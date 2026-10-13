#!/usr/bin/env python3
"""Recover an authored lesson using a verified released Terraphim agent."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New directory for this run")
    parser.add_argument("--candidate", action="store_true", help="Engineering check only; never release evidence")
    parser.add_argument("--prepare-only", action="store_true", help="Prepare an isolated run for the manual walkthrough without capturing a lesson")
    args = parser.parse_args()
    agent = args.agent.resolve(strict=True)
    binary_hash = hashlib.sha256(agent.read_bytes()).hexdigest()
    version = subprocess.check_output([str(agent), "--version"], text=True).strip()
    if version != "terraphim-agent 1.21.20":
        raise SystemExit(f"Expected terraphim-agent 1.21.20, got {version}")
    if not args.candidate:
        identities = json.loads((BASE / "released-binaries.json").read_text())
        if binary_hash not in [item["binarySha256"] for item in identities["binaries"]]:
            raise SystemExit("Binary checksum is not in this example's verified release identities")
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    shutil.copytree(BASE / "fixture", root / "fixture")
    fixture = root / "fixture"
    for name in ("settings", "data", "empty-data", "dashmap", "sqlite", "outputs"):
        (root / name).mkdir()

    def role(name, key):
        return dict(shortname=key, name=name, relevance_function="terraphim-graph",
                    terraphim_it=True, theme="lumen", kg=dict(automata_path=None,
                    knowledge_graph_local=dict(input_type="markdown", path=str(fixture / "kg" / key)),
                    public=False, publish=False), haystacks=[], llm_provider=None,
                    llm_auto_summarize=False, extra={})

    config = dict(id="Server", global_shortcut="Ctrl+Shift+T",
                  roles={"Brief Reviewer": role("Brief Reviewer", "brief"),
                         "Finance Reviewer": role("Finance Reviewer", "finance")},
                  default_role="Brief Reviewer", selected_role="Brief Reviewer")
    (root / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    quoted = lambda path: json.dumps(str(path))
    (root / "settings/settings.toml").write_text(f'''server_hostname = "127.0.0.1:8000"
api_endpoint = "http://localhost:8000/api"
initialized = "true"
default_data_path = {quoted(root / 'data')}
role_config = {quoted(root / 'config.json')}
[profiles.dashmap]
type = "dashmap"
root = {quoted(root / 'dashmap')}
[profiles.sqlite]
type = "sqlite"
datadir = {quoted(root / 'sqlite')}
connection_string = {quoted(root / 'sqlite/terraphim.db')}
table = "terraphim_kv"
''')
    if args.prepare_only:
        print(f"Prepared {root}. No memory captured. See README.md for the scoped manual commands.")
        return
    records = []

    def run(label, command, store="data"):
        env = os.environ.copy()
        for key in ("GH_TOKEN", "GITHUB_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"):
            env.pop(key, None)
        env["TERRAPHIM_DEFAULT_DATA_PATH"] = str(root / store)
        env["TERRAPHIM_SETTINGS_PATH"] = str(root / "settings")
        argv = [str(agent), "--format", "json", "--config", str(root / "config.json"), *command]
        start = time.monotonic()
        process = subprocess.run(argv, cwd=fixture, env=env, text=True, capture_output=True, timeout=90)
        record = dict(label=label, argv=argv, store=store, exitCode=process.returncode,
                      stdout=process.stdout, stderr=process.stderr,
                      seconds=round(time.monotonic() - start, 3),
                      utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        records.append(record)
        (root / "outputs" / (label + ".stdout.json")).write_text(process.stdout)
        (root / "outputs" / (label + ".stderr.txt")).write_text(process.stderr)
        (root / "execution-receipts.json").write_text(json.dumps(records, indent=2) + "\n")
        if process.returncode:
            raise RuntimeError(f"{label} failed: {process.stderr}")
        return json.loads(process.stdout)

    baseline = run("before-capture", ["memory", "list"])
    captured = run("capture", ["memory", "capture", "--file", "lesson.md", "--provenance-tag", "harbour-public-brief-v1"])
    memory_id = captured["memory_id"]
    shown = run("reopened", ["memory", "show", memory_id, "--json"])
    listed = run("listed", ["memory", "list"])
    exported = run("exported", ["memory", "export", "--format", "json"])
    positive = run("retrieved", ["memory", "retrieve", "validate brief", "--role", "Brief Reviewer", "--format", "json"])
    negative = run("unrelated-query", ["memory", "retrieve", "volcanic eruption", "--role", "Brief Reviewer", "--format", "json"])
    other_role = run("other-role", ["memory", "retrieve", "validate brief", "--role", "Finance Reviewer", "--format", "json"])
    empty = run("separate-store", ["memory", "retrieve", "validate brief", "--role", "Brief Reviewer", "--format", "json"], "empty-data")
    preview = run("context-preview", ["memory", "apply", "--role", "Brief Reviewer", "--prompt", "validate brief"])
    lesson = (fixture / "lesson.md").read_text()
    checks = dict(emptyBaseline=baseline["count"] == 0,
                  exactNewProcessReadback=shown["memory_item"]["content"] == lesson,
                  listPersistence=listed["count"] == 1,
                  exactExport=any(item["content"] == lesson for item in exported["memory_items"]),
                  conceptRetrieval=positive["count"] == 1 and positive["items"][0]["id"] == memory_id and positive["items"][0]["content"] == lesson,
                  unrelatedQuery=negative["count"] == 0, otherRole=other_role["count"] == 0,
                  separateStore=empty["count"] == 0,
                  proposedContext=preview["retrieved_items"] == 1 and preview["injected_bytes"] > 0)
    result = dict(status="PASS" if all(checks.values()) else "FAIL", checks=checks,
                  qualification="candidate-only" if args.candidate else "released-binary",
                  binaryVersion=version, binarySha256=binary_hash, memoryId=memory_id,
                  lesson=lesson, processCount=len(records),
                  note="Every command is a fresh process. Roles filter retrieval; they are not access-control boundaries. Apply is a preview, not execution.")
    (root / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
