#!/usr/bin/env python3
"""Import hash-admitted editor assets into a new website directory; never deploy."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"symlink forbidden: {part}")
    return path


def validated_manifest(raw):
    """Validate identity and every relative asset path before accessing files."""
    data = json.loads(raw)
    if data.get("schema") != 1 or not re.fullmatch(r"[a-f0-9]{40}", data.get("sourceHead", "")):
        raise ValueError("invalid source manifest identity")
    assets = data.get("assets")
    if not isinstance(assets, dict) or not {"index.html", "roles/default.json", "vendor/manifest.json"} <= assets.keys():
        raise ValueError("missing required editor assets")
    for name, expected in assets.items():
        if (not isinstance(name, str) or not name or "\\" in name
                or PurePosixPath(name).is_absolute() or any(p in ("", ".", "..") for p in name.split("/"))
                or name in ("release.json", "assets-manifest.json")):
            raise ValueError("unsafe or reserved asset path")
        if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
            raise ValueError("invalid asset digest")
    return data, assets


def stage(source, manifest, expected_sha, destination):
    """Verify every byte before creating a new app tree; preserve existing trees."""
    source, manifest, destination = map(lambda p: Path(os.path.abspath(p)), (source, manifest, destination))
    safe(source)
    safe(manifest)
    safe(destination)
    if destination.exists():
        raise ValueError("destination already exists; use a fresh staging directory")
    raw = manifest.read_bytes()
    if not re.fullmatch(r"[a-f0-9]{64}", expected_sha) or sha(raw) != expected_sha:
        raise ValueError("manifest does not match independently admitted SHA256")
    data, assets = validated_manifest(raw)
    payloads = {}
    for name, expected in assets.items():
        payload = safe(source / name).read_bytes()
        if not isinstance(expected, str) or sha(payload) != expected:
            raise ValueError(f"asset hash mismatch: {name}")
        payloads[name] = payload
    # Payloads are immutable snapshots of the verified reads, not later source copies.
    destination.parent.mkdir(parents=True, exist_ok=True)
    safe(destination.parent)
    temporary = Path(tempfile.mkdtemp(prefix=".editor-stage-", dir=destination.parent))
    try:
        for name, payload in payloads.items():
            path = temporary / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        (temporary / "assets-manifest.json").write_bytes(raw)
        (temporary / "release.json").write_text(json.dumps({
            "schema": 1, "sourceHead": data["sourceHead"], "manifestSha256": expected_sha,
            "assets": len(payloads), "fullParityAccepted": False,
            "qualification": "HASH-ADMITTED CANDIDATE; browser/deployment acceptance required",
        }, indent=2) + "\n")
        safe(destination)
        if destination.exists():
            raise ValueError("destination appeared during staging")
        temporary.rename(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def verify(destination, expected_sha):
    """Recheck imported bytes before site build/deploy without changing them."""
    destination = safe(Path(os.path.abspath(destination)))
    receipt = json.loads(safe(destination / "release.json").read_text())
    raw = safe(destination / "assets-manifest.json").read_bytes()
    if (not isinstance(expected_sha, str) or not re.fullmatch(r"[a-f0-9]{64}", expected_sha)
            or sha(raw) != expected_sha or receipt["manifestSha256"] != expected_sha):
        raise ValueError("imported manifest identity changed")
    data, assets = validated_manifest(raw)
    if (receipt.get("schema") != 1 or receipt.get("sourceHead") != data["sourceHead"]
            or receipt.get("assets") != len(assets) or receipt.get("fullParityAccepted") is not False):
        raise ValueError("receipt does not describe the admitted candidate")
    expected_paths = set(assets) | {"release.json", "assets-manifest.json"}
    actual_paths = set()
    for parent, directories, files in os.walk(destination, followlinks=False):
        for name in directories + files:
            safe(Path(parent) / name)
        for name in files:
            actual_paths.add((Path(parent) / name).relative_to(destination).as_posix())
    if actual_paths != expected_paths:
        raise ValueError("imported tree contains missing or unadmitted files")
    for name, expected in assets.items():
        if sha(safe(destination / name).read_bytes()) != expected:
            raise ValueError(f"imported asset changed: {name}")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--destination", type=Path, default=Path("static/editor"))
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify(args.destination, args.manifest_sha256), indent=2))
    else:
        if not all((args.source, args.manifest, args.manifest_sha256)):
            parser.error("import requires --source, --manifest and --manifest-sha256")
        stage(args.source, args.manifest, args.manifest_sha256, args.destination)
        print(f"Imported admitted candidate into {args.destination}; no deployment performed")


if __name__ == "__main__":
    main()
