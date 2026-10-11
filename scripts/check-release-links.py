#!/usr/bin/env python3
"""Verify that the release download URLs advertised by the site resolve.

The site publishes download links against the public release channel
(downloads.terraphim.ai). This check reads the version the site advertises, then
confirms the channel manifests serve that version and that every asset the site
links to is present on the channel with a non-trivial size.

It is the release half of CI: build validation proves the site compiles, this
proves the site does not advertise downloads that do not exist.

The channel is fronted by Cloudflare bot management, which rejects generic
clients, so requests carry a descriptive User-Agent.

Exit codes:
  0  every advertised URL resolved
  1  an advertised URL is missing or unusable
  2  the channel could not be reached
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

CHANNEL_BASE = os.environ.get("TERRAPHIM_CHANNEL_BASE", "https://downloads.terraphim.ai")
USER_AGENT = "terraphim-site-release-check/1.0 (release validation)"

# Targets the site offers downloads for, and how the site names them.
TARGETS = {
    "x86_64-unknown-linux-gnu": "linux-x86_64",
    "aarch64-unknown-linux-musl": "linux-aarch64",
    "x86_64-apple-darwin": "macos-x86_64",
    "aarch64-apple-darwin": "macos-aarch64",
    "x86_64-pc-windows-msvc": "windows-x86_64",
}

CLI_BINARIES = ("terraphim-agent", "terraphim-cli", "terraphim-grep")
MIN_ASSET_BYTES = 100_000

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"


def read_site_version() -> str:
    """Return the release version the site advertises in config.toml."""
    text = CONFIG.read_text(encoding="utf-8")
    match = re.search(r'^release_version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        print("::error::config.toml has no extra.release_version")
        sys.exit(1)
    return match.group(1)


def fetch(url: str, limit: int = 64 * 1024 * 1024) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read(limit)


def head_size(url: str) -> int | None:
    """Return Content-Length for a URL, or None when unavailable."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            length = response.headers.get("Content-Length")
            return int(length) if length else None
    except urllib.error.HTTPError:
        return None


def manifest_for(binary: str) -> dict:
    url = f"{CHANNEL_BASE}/{binary}/stable-v2.json"
    try:
        return json.loads(fetch(url))
    except urllib.error.HTTPError as error:
        print(f"::error::manifest {url} returned HTTP {error.code}")
        sys.exit(2)
    except (urllib.error.URLError, ValueError, TimeoutError) as error:
        print(f"::error::manifest {url} unreachable: {error}")
        sys.exit(2)


def main() -> int:
    version = read_site_version()
    print(f"Site advertises release {version}")

    failures: list[str] = []

    for binary in CLI_BINARIES:
        manifest = manifest_for(binary)
        channel_version = manifest.get("version", "")
        if channel_version != version:
            failures.append(
                f"{binary}: channel serves {channel_version!r} but the site advertises {version!r}"
            )
            continue

        assets = manifest.get("assets", {})
        for target, label in TARGETS.items():
            asset = assets.get(target)
            if not asset:
                failures.append(f"{binary}: channel manifest has no asset for {target}")
                continue

            # The manifest path is relative to the channel root and already
            # includes the binary name, e.g. "terraphim-agent/terraphim-agent-...".
            url = f"{CHANNEL_BASE}/{asset['path'].lstrip('/')}"
            size = head_size(url)
            if size is None:
                failures.append(f"{binary} {label}: {url} did not resolve")
            elif size < MIN_ASSET_BYTES:
                failures.append(f"{binary} {label}: {url} is only {size} bytes")

        print(f"{binary}: checked {len(TARGETS)} advertised targets against {CHANNEL_BASE}")

    if failures:
        for failure in failures:
            print(f"::error::{failure}")
        return 1

    print(f"All advertised downloads for release {version} resolve on {CHANNEL_BASE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())