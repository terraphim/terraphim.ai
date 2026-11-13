"""Replay published checklist commands with the exact advertised release binary."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from scripts.test_checklist_publication import (
    ARTICLES,
    article_command_fixture_bindings,
    released_commands_in_help,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts/tests/fixtures/terraphim-agent-v1.21.22"
IDENTITY = json.loads((FIXTURE / "identity.json").read_text())
ARTICLE_CONFIG_SNIPPET_SHA256 = (
    "5fa6f6da63164c3573c2214c576f29ae7e0bf56ea5a3b9bb23168ceba331c937"
)
DOWNLOAD_STEP_BODY_SHA256 = (
    "193ae1625b66502c3acf7351c7043d76a485a4d0ea8a176c56375bca4009158d"
)
RIPGREP_VERSION = "14.1.1"
RIPGREP_ARCHIVE = "ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz"
RIPGREP_URL = (
    "https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/"
    "ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz"
)
RIPGREP_ARCHIVE_SHA256 = (
    "4cf9f2741e6c465ffdb7c26f38056a59e2a2544b51f7cc128ef28337eeae4d8e"
)
RIPGREP_STEP_BODY_SHA256 = (
    "877d29d89f0c3d60ddba05e60d6ff424b2e3bc080f789d37207276ab6b19b5c8"
)


def require_live_binary(environ):
    if environ.get("TERRAPHIM_PUBLICATION_LIVE_REQUIRED") != "1":
        raise RuntimeError("TERRAPHIM_PUBLICATION_LIVE_REQUIRED must equal 1")
    value = environ.get("TERRAPHIM_AGENT_BIN")
    if not value:
        raise RuntimeError("TERRAPHIM_AGENT_BIN is required for live publication replay")
    binary = Path(value).resolve()
    if not binary.is_file():
        raise RuntimeError(f"TERRAPHIM_AGENT_BIN is not a file: {binary}")
    return binary


def verify_binary_sha(binary, expected):
    actual = hashlib.sha256(binary.read_bytes()).hexdigest()
    if actual != expected:
        raise AssertionError(
            f"binary SHA-256 mismatch: expected {expected}, received {actual}"
        )


def verify_fixture_sha(data, expected, name):
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise AssertionError(
            f"{name} SHA-256 mismatch: expected {expected}, received {actual}"
        )


def require_help_commands(help_bytes, required):
    released = released_commands_in_help(help_bytes.decode("utf-8"))
    missing = required - released
    if missing:
        raise AssertionError(f"released help is missing: {', '.join(sorted(missing))}")
    return released


def assert_process_result(
    actual_exit, actual_stdout, expected_exit, expected_stdout, stderr=b"", label=""
):
    if actual_exit != expected_exit:
        raise AssertionError(
            f"[{label}] exit mismatch: expected {expected_exit}, "
            f"received {actual_exit}; "
            f"stderr: {stderr.decode('utf-8', errors='replace')!r}"
        )
    if actual_stdout != expected_stdout:
        raise AssertionError(
            f"[{label}] stdout byte mismatch: expected {expected_stdout!r}, "
            f"received {actual_stdout!r}; "
            f"stderr: {stderr.decode('utf-8', errors='replace')!r}"
        )


def assert_article_provenance(pages, identity):
    actual = {
        article: article_command_fixture_bindings(page)
        for article, page in pages.items()
    }
    if actual != identity["articleCommandFixtures"]:
        raise AssertionError("article command input, role, type, or flag drifted")


def extract_article_config_snippet(article):
    match = re.search(
        r"```bash\n.*?^python3 - <<'PY'\n(.*?)\n^PY\n```",
        article,
        flags=re.DOTALL | re.MULTILINE,
    )
    if match is None:
        raise AssertionError("article lacks the allowlisted Python role-config heredoc")
    snippet = match.group(1) + "\n"
    verify_fixture_sha(
        snippet.encode(), ARTICLE_CONFIG_SNIPPET_SHA256, "article role-config snippet"
    )
    return snippet


def validate_role_config(config):
    data = json.loads(config.read_text()) if isinstance(config, Path) else config
    if set(data.get("roles", {})) != {"Command Rewriter"}:
        raise AssertionError("article role config must define only Command Rewriter")
    if data.get("default_role") != "Command Rewriter":
        raise AssertionError("article role config default role drifted")
    if data.get("selected_role") != "Command Rewriter":
        raise AssertionError("article role config selected role drifted")
    role = data["roles"]["Command Rewriter"]
    if role.get("name") != "Command Rewriter" or role.get("shortname") != "rewriter":
        raise AssertionError("article role identity drifted")
    local = role.get("kg", {}).get("knowledge_graph_local", {})
    expected_path = str((ROOT / ".terraphim/rewrite").resolve())
    if local.get("input_type") != "markdown" or local.get("path") != expected_path:
        raise AssertionError("article role graph input type or path drifted")
    return data


def execute_article_role_config(article, scratch, environment):
    scratch = scratch.resolve()
    if not scratch.is_relative_to(ROOT.resolve()):
        raise AssertionError("article role config scratch directory must be in workspace")
    snippet = extract_article_config_snippet(article)
    config = scratch / "rewrite-role.json"
    isolated_environment = dict(environment)
    isolated_environment["TERRAPHIM_REWRITE_CONFIG"] = str(config)
    run = subprocess.run(
        [sys.executable, "-c", snippet],
        cwd=ROOT,
        env=isolated_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if run.returncode != 0:
        raise AssertionError(f"article role-config snippet failed: {run.stderr!r}")
    if not config.is_file():
        raise AssertionError("article role-config snippet did not create its config")
    validate_role_config(config)
    return config


def _workflow_step(workflow, name):
    marker = f"      - name: {name}"
    lines = workflow.splitlines()
    try:
        start = lines.index(marker)
    except ValueError as error:
        raise AssertionError(f"workflow lacks required step: {name}") from error
    end = start + 1
    while end < len(lines) and not lines[end].startswith("      - name: "):
        if lines[end] and not lines[end].startswith("        "):
            break
        end += 1
    return "\n".join(lines[start:end])


def assert_live_workflow_steps(workflow, later_markers):
    download = _workflow_step(
        workflow, "Download checksum-verified terraphim-agent v1.21.22"
    )
    replay = _workflow_step(workflow, "Replay published terraphim-agent commands")
    download_lines = download.splitlines()
    expected_download_header = [
        "      - name: Download checksum-verified terraphim-agent v1.21.22",
        "        shell: bash",
        "        run: |",
    ]
    if download_lines[:3] != expected_download_header:
        raise AssertionError("Download step header is not the canonical shape")
    body_lines = download_lines[3:]
    if not body_lines or any(
        line and not line.startswith("          ") for line in body_lines
    ):
        raise AssertionError("Download step contains a non-script top-level field")
    normalized_body = "\n".join(
        line[10:] if line else "" for line in body_lines
    ) + "\n"
    actual_body_sha = hashlib.sha256(normalized_body.encode()).hexdigest()
    if actual_body_sha != DOWNLOAD_STEP_BODY_SHA256:
        raise AssertionError(
            "Download step body SHA-256 mismatch: "
            f"expected {DOWNLOAD_STEP_BODY_SHA256}, received {actual_body_sha}"
        )
    expected_replay = [
        "      - name: Replay published terraphim-agent commands",
        "        run: python3 -m unittest scripts.test_checklist_publication_live -v",
    ]
    if replay.splitlines() != expected_replay:
        raise AssertionError("Replay step is not the exact canonical two-line shape")
    download_at = workflow.index(download)
    replay_at = workflow.index(replay)
    if download_at >= replay_at:
        raise AssertionError("Download step must precede Replay step")
    for marker in later_markers:
        if replay_at >= workflow.index(marker):
            raise AssertionError(f"Replay step must precede {marker}")


def assert_ripgrep_workflow_step(workflow, identity, later_markers):
    expected_identity = {
        "ripgrepVersion": RIPGREP_VERSION,
        "ripgrepArchive": RIPGREP_ARCHIVE,
        "ripgrepUrl": RIPGREP_URL,
        "ripgrepArchiveSha256": RIPGREP_ARCHIVE_SHA256,
    }
    actual_identity = {
        key: identity.get(key) for key in expected_identity
    }
    if actual_identity != expected_identity:
        raise AssertionError(
            "ripgrep identity digest or release metadata drifted: "
            f"expected {expected_identity}, received {actual_identity}"
        )
    expected_environment = (
        f"  RIPGREP_PUBLICATION_URL: {RIPGREP_URL}",
        "  RIPGREP_PUBLICATION_ARCHIVE_SHA256: " + RIPGREP_ARCHIVE_SHA256,
    )
    for line in expected_environment:
        if workflow.splitlines().count(line) != 1:
            raise AssertionError(f"ripgrep workflow digest environment drifted: {line}")

    install = _workflow_step(
        workflow, "Install checksum-verified ripgrep 14.1.1"
    )
    install_lines = install.splitlines()
    expected_header = [
        "      - name: Install checksum-verified ripgrep 14.1.1",
        "        shell: bash",
        "        run: |",
    ]
    if install_lines[:3] != expected_header:
        raise AssertionError("ripgrep step header is not the canonical shape")
    body_lines = install_lines[3:]
    if not body_lines or any(
        line and not line.startswith("          ") for line in body_lines
    ):
        raise AssertionError("ripgrep step contains a non-script top-level field")
    normalized_body = "\n".join(
        line[10:] if line else "" for line in body_lines
    ) + "\n"
    actual_body_sha = hashlib.sha256(normalized_body.encode()).hexdigest()
    if actual_body_sha != RIPGREP_STEP_BODY_SHA256:
        raise AssertionError(
            "ripgrep step body SHA-256 mismatch: "
            f"expected {RIPGREP_STEP_BODY_SHA256}, received {actual_body_sha}"
        )

    replay = _workflow_step(workflow, "Replay published terraphim-agent commands")
    install_at = workflow.index(install)
    replay_at = workflow.index(replay)
    if install_at >= replay_at:
        raise AssertionError("ripgrep step must precede Replay step")
    for marker in later_markers:
        if install_at >= workflow.index(marker):
            raise AssertionError(f"ripgrep step must precede {marker}")


def _binding_command(binary, config, binding):
    command = [str(binary)]
    if binding["config"] is not None:
        if binding["config"] != "$TERRAPHIM_REWRITE_CONFIG":
            raise AssertionError(f"unexpected article config: {binding['config']}")
        command.extend(("--config", str(config)))
    if binding["subcommand"] == "hook":
        command.extend(("hook", "--hook-type", binding["hookType"]))
        if binding["rewrite"]:
            command.append("--rewrite")
        command.extend(("--role", binding["role"], "--json"))
    elif binding["subcommand"] == "validate":
        command.extend(("validate", "--checklist", binding["checklist"], "--json"))
    else:
        raise AssertionError(f"unsupported live subcommand: {binding['subcommand']}")
    return command


def replay_published_commands(binary, identity, base_environment=None):
    verify_binary_sha(binary, identity["binarySha256"])
    pages = {path.name: path.read_text() for path in ARTICLES}
    assert_article_provenance(pages, identity)

    with tempfile.TemporaryDirectory(prefix=".publication-live-", dir=ROOT) as root:
        isolated = Path(root)
        environment = dict(
            os.environ if base_environment is None else base_environment
        )
        for variable, directory in (
            ("TMPDIR", "tmp"),
            ("XDG_CACHE_HOME", "cache"),
            ("XDG_CONFIG_HOME", "config"),
            ("XDG_DATA_HOME", "data"),
            ("XDG_STATE_HOME", "state"),
        ):
            path = isolated / directory
            path.mkdir()
            environment[variable] = str(path)

        graph_article = pages["graph-embeddings-checklists.md"]
        config = execute_article_role_config(graph_article, isolated, environment)

        help_fixture = (FIXTURE / "help.raw.txt").read_bytes()
        verify_fixture_sha(
            help_fixture, identity["helpRawSha256"], "help.raw.txt"
        )

        help_run = subprocess.run(
            [str(binary), "--help"],
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        assert_process_result(
            help_run.returncode,
            help_run.stdout,
            0,
            help_fixture,
            help_run.stderr,
        )
        released = require_help_commands(help_run.stdout, {"hook", "validate"})
        if "code" in released:
            raise AssertionError("released help unexpectedly exposes code")

        for article in sorted(identity["articleCommandFixtures"]):
            for binding in identity["articleCommandFixtures"][article]:
                raw_fixture = (FIXTURE / binding["rawFixture"]).read_bytes()
                if hashlib.sha256(raw_fixture).hexdigest() != binding["rawSha256"]:
                    raise AssertionError(f"raw fixture hash drift: {binding['rawFixture']}")
                run = subprocess.run(
                    _binding_command(binary, config, binding),
                    cwd=ROOT,
                    env=environment,
                    input=(binding["stdin"] + "\n").encode(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                assert_process_result(
                    run.returncode,
                    run.stdout,
                    binding["exitCode"],
                    raw_fixture,
                    run.stderr,
                    label=f"{article} {binding['subcommand']} "
                    f"{'rewrite' if binding.get('rewrite') else 'no-rewrite'}",
                )


class LiveReplayContractTests(unittest.TestCase):
    def test_help_fixture_sha_is_independently_guarded(self):
        with self.assertRaisesRegex(AssertionError, "help.raw.txt SHA-256"):
            verify_fixture_sha(b"not the captured help\n", "0" * 64, "help.raw.txt")

    def test_article_python_snippet_creates_the_replayed_role_config(self):
        article = (ROOT / "content/posts/graph-embeddings-checklists.md").read_text()
        with tempfile.TemporaryDirectory(prefix=".article-config-test-", dir=ROOT) as root:
            config = execute_article_role_config(article, Path(root), dict(os.environ))
            validate_role_config(config)

    def test_article_config_input_type_and_role_drift_are_rejected(self):
        article = (ROOT / "content/posts/graph-embeddings-checklists.md").read_text()
        mutations = (
            ('"input_type": "markdown"', '"input_type": "json"'),
            ('"name": "Command Rewriter"', '"name": "Missing Role"'),
        )
        for old, new in mutations:
            with self.subTest(mutation=new):
                self.assertIn(old, article)
                with tempfile.TemporaryDirectory(
                    prefix=".article-config-mutation-", dir=ROOT
                ) as root:
                    with self.assertRaises(AssertionError):
                        execute_article_role_config(
                            article.replace(old, new, 1), Path(root), dict(os.environ)
                        )

    def test_generated_role_config_schema_rejects_semantic_drift_directly(self):
        article = (ROOT / "content/posts/graph-embeddings-checklists.md").read_text()
        with tempfile.TemporaryDirectory(prefix=".role-schema-test-", dir=ROOT) as root:
            config_path = execute_article_role_config(
                article, Path(root), dict(os.environ)
            )
            generated = json.loads(config_path.read_text())
        mutations = (
            (
                "input type",
                lambda config: config["roles"]["Command Rewriter"]["kg"][
                    "knowledge_graph_local"
                ].__setitem__("input_type", "json"),
            ),
            (
                "role name",
                lambda config: config["roles"]["Command Rewriter"].__setitem__(
                    "name", "Missing Role"
                ),
            ),
            (
                "rewrite path",
                lambda config: config["roles"]["Command Rewriter"]["kg"][
                    "knowledge_graph_local"
                ].__setitem__("path", str((ROOT / ".terraphim/kg").resolve())),
            ),
        )
        for label, mutate in mutations:
            with self.subTest(mutation=label):
                changed = json.loads(json.dumps(generated))
                mutate(changed)
                with self.assertRaises(AssertionError):
                    validate_role_config(changed)

    def test_workflows_verify_and_replay_release_before_build_or_secrets(self):
        required = (
            "https://downloads.terraphim.ai/terraphim-agent/"
            "terraphim-agent-1.21.22-x86_64-unknown-linux-musl.tar.gz",
            IDENTITY["archiveSha256"],
            IDENTITY["binarySha256"],
            "TERRAPHIM_AGENT_BIN=",
            "TERRAPHIM_PUBLICATION_LIVE_REQUIRED=1",
            "python3 -m unittest scripts.test_checklist_publication_live -v",
        )
        for relative, later_markers in (
            (
                ".github/workflows/validate.yml",
                ("Install Zola", "python3 -m unittest discover", "Build site"),
            ),
            (
                ".github/workflows/deploy.yml",
                (
                    "Install Zola",
                    "python3 -m unittest discover",
                    "Build site",
                    "Load secrets from 1Password",
                    "- name: Deploy to Cloudflare Pages",
                ),
            ),
        ):
            workflow = (ROOT / relative).read_text()
            with self.subTest(workflow=relative):
                for value in required:
                    self.assertIn(value, workflow)
                replay_at = workflow.index(
                    "python3 -m unittest scripts.test_checklist_publication_live -v"
                )
                for marker in later_markers:
                    self.assertLess(replay_at, workflow.index(marker))
                assert_live_workflow_steps(workflow, later_markers)

    def test_workflows_install_verified_ripgrep_before_replay(self):
        for relative, later_markers in (
            (
                ".github/workflows/validate.yml",
                ("Install Zola", "python3 -m unittest discover", "Build site"),
            ),
            (
                ".github/workflows/deploy.yml",
                (
                    "Install Zola",
                    "python3 -m unittest discover",
                    "Build site",
                    "Load secrets from 1Password",
                    "- name: Deploy to Cloudflare Pages",
                ),
            ),
        ):
            workflow = (ROOT / relative).read_text()
            with self.subTest(workflow=relative):
                assert_ripgrep_workflow_step(workflow, IDENTITY, later_markers)

    def test_ripgrep_workflow_step_rejects_missing_bypasses_and_digest_drift(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text()
        step_name = "Install checksum-verified ripgrep 14.1.1"
        mutations = (
            (
                "      - name: Install checksum-verified ripgrep 14.1.1\n"
                "        shell: bash",
                "      - name: Install checksum-verified ripgrep 14.1.1\n"
                "        if: false\n"
                "        shell: bash",
            ),
            (
                "      - name: Install checksum-verified ripgrep 14.1.1\n"
                "        shell: bash",
                "      - name: Install checksum-verified ripgrep 14.1.1\n"
                "        continue-on-error: true\n"
                "        shell: bash",
            ),
        )
        self.assertIn(f"      - name: {step_name}", workflow)
        missing = workflow.replace(_workflow_step(workflow, step_name) + "\n", "", 1)
        with self.assertRaisesRegex(AssertionError, "ripgrep|workflow lacks"):
            assert_ripgrep_workflow_step(missing, IDENTITY, ())
        for old, new in mutations:
            with self.subTest(mutation=new):
                self.assertIn(old, workflow)
                with self.assertRaises(AssertionError):
                    assert_ripgrep_workflow_step(
                        workflow.replace(old, new, 1), IDENTITY, ()
                    )
        wrong_workflow_digest = workflow.replace(
            IDENTITY["ripgrepArchiveSha256"], "0" * 64, 1
        )
        with self.assertRaisesRegex(AssertionError, "ripgrep.*SHA-256|digest"):
            assert_ripgrep_workflow_step(wrong_workflow_digest, IDENTITY, ())
        wrong_identity = json.loads(json.dumps(IDENTITY))
        wrong_identity["ripgrepArchiveSha256"] = "0" * 64
        with self.assertRaisesRegex(AssertionError, "ripgrep.*SHA-256|digest"):
            assert_ripgrep_workflow_step(workflow, wrong_identity, ())

    def test_workflow_steps_reject_conditional_or_continue_on_error_bypasses(self):
        for relative in (
            ".github/workflows/validate.yml",
            ".github/workflows/deploy.yml",
        ):
            workflow = (ROOT / relative).read_text()
            mutations = (
                (
                    "      - name: Download checksum-verified terraphim-agent v1.21.22\n"
                    "        shell: bash",
                    "      - name: Download checksum-verified terraphim-agent v1.21.22\n"
                    "        if: false\n"
                    "        shell: bash",
                ),
                (
                    "      - name: Replay published terraphim-agent commands\n"
                    "        run:",
                    "      - name: Replay published terraphim-agent commands\n"
                    "        continue-on-error: true\n"
                    "        run:",
                ),
                (
                    "      - name: Download checksum-verified terraphim-agent v1.21.22\n"
                    "        shell: bash",
                    "      - name: Download checksum-verified terraphim-agent v1.21.22\n"
                    '        "if": false\n'
                    "        shell: bash",
                ),
                (
                    "      - name: Download checksum-verified terraphim-agent v1.21.22\n"
                    "        shell: bash",
                    "      - name: Download checksum-verified terraphim-agent v1.21.22\n"
                    "        if : false\n"
                    "        shell: bash",
                ),
                (
                    "      - name: Download checksum-verified terraphim-agent v1.21.22\n"
                    "        shell: bash",
                    "      - name: Download checksum-verified terraphim-agent v1.21.22\n"
                    '        "continue-on-error": true\n'
                    "        shell: bash",
                ),
                (
                    "run: python3 -m unittest scripts.test_checklist_publication_live -v",
                    "run: python3 -m unittest scripts.test_checklist_publication_live -v || true",
                ),
                (
                    "| sha256sum --check --strict -",
                    "| sha256sum --check --strict - || true",
                ),
            )
            for old, new in mutations:
                with self.subTest(workflow=relative, mutation=new):
                    self.assertIn(old, workflow)
                    with self.assertRaises(AssertionError):
                        assert_live_workflow_steps(workflow.replace(old, new, 1), ())

    def test_required_mode_rejects_missing_binary_environment(self):
        with self.assertRaisesRegex(RuntimeError, "TERRAPHIM_AGENT_BIN"):
            require_live_binary({"TERRAPHIM_PUBLICATION_LIVE_REQUIRED": "1"})

    def test_wrong_binary_sha_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "binary SHA-256"):
            verify_binary_sha(Path(__file__), "0" * 64)

    def test_released_help_must_expose_every_replayed_command(self):
        help_without_hook = b"Commands:\n  validate  Validate text\n\nOptions:\n"
        with self.assertRaisesRegex(AssertionError, "hook"):
            require_help_commands(help_without_hook, {"hook", "validate"})

    def test_stdout_comparison_is_exact_bytes(self):
        with self.assertRaisesRegex(AssertionError, "stdout"):
            assert_process_result(0, b"different\n", 0, b"expected\n")

    def test_failure_reports_the_child_stderr_and_the_binding_label(self):
        with self.assertRaises(AssertionError) as caught:
            assert_process_result(
                1,
                b"",
                0,
                b"expected\n",
                b"boom: role graph missing\n",
                label="kg article validate",
            )
        message = str(caught.exception)
        self.assertIn("kg article validate", message)
        self.assertIn("boom: role graph missing", message)

    def test_role_input_and_flag_drift_are_rejected(self):
        pages = {path.name: path.read_text() for path in ARTICLES}
        graph = "graph-embeddings-checklists.md"
        mutations = (
            (
                'echo \'{"tool_name":"Bash","tool_input":{"command":"npm install react"}}\'',
                'echo \'{"tool_name":"Bash","tool_input":{"command":"printf safe"}}\'',
            ),
            ('--role "Command Rewriter"', '--role "Missing Role"'),
            (
                "hook --hook-type pre-tool-use --rewrite",
                "hook --hook-type pre-tool-use",
            ),
        )
        for old, new in mutations:
            with self.subTest(mutation=new):
                mutated = dict(pages)
                mutated[graph] = pages[graph].replace(old, new, 1)
                with self.assertRaises(AssertionError):
                    assert_article_provenance(mutated, IDENTITY)


class LivePublicationReplayTests(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("TERRAPHIM_PUBLICATION_LIVE_REQUIRED") == "1",
        "live publication replay is enabled explicitly in publication CI",
    )
    def test_checksum_verified_release_replays_published_commands(self):
        binary = require_live_binary(os.environ)
        replay_published_commands(binary, IDENTITY)

    @unittest.skipUnless(
        os.environ.get("TERRAPHIM_PUBLICATION_LIVE_REQUIRED") == "1",
        "live publication replay is enabled explicitly in publication CI",
    )
    def test_missing_ripgrep_fails_with_local_kg_diagnostic(self):
        binary = require_live_binary(os.environ)
        with tempfile.TemporaryDirectory(prefix=".no-rg-path-", dir=ROOT) as root:
            environment = dict(os.environ)
            environment["PATH"] = root
            with self.assertRaises(AssertionError) as caught:
                replay_published_commands(binary, IDENTITY, environment)
        message = str(caught.exception)
        self.assertIn(
            "Failed to build thesaurus from local KG for role Command Rewriter",
            message,
        )
        self.assertIn("No such file or directory", message)


if __name__ == "__main__":
    unittest.main()
