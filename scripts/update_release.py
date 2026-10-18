#!/usr/bin/env python3
"""Release updater: discover admitted release/channel inputs and update
precisely scoped active fields and managed README regions.

Standard library only. See docs/release-link-updater.md for the input
authorities, failure modes and review model.

Exit codes: 0 success-or-unchanged, 1 drift in --check mode,
2 rejected inputs, 3 operational failure.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_REJECTED = 2
EXIT_OPERATIONAL = 3

API_BASE = "https://api.github.com"
CHANNEL_BASE = "https://downloads.terraphim.ai"
USER_AGENT = "terraphim-release-updater/1 (+https://terraphim.ai)"

REQUEST_TIMEOUT_S = 30
MAX_ATTEMPTS = 3
RETRY_AFTER_CAP_S = 120
DISCOVERY_BUDGET_S = 300

README_MARKER_START = "<!-- terraphim-downloads:start -->"
README_MARKER_END = "<!-- terraphim-downloads:end -->"
README_HEADING = "## Current downloads"

MONTHS = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)


class RejectedInput(Exception):
    """Inputs are malformed, ambiguous, conflicting or unsafe to admit."""


class OperationalFailure(Exception):
    """I/O, network exhaustion or other operational failure."""


class TargetRepository(Enum):
    WEBSITE = "website"
    TERRAPHIM_AI = "terraphim-ai"
    TERRAPHIM_CLIENTS = "terraphim-clients"


TARGET_REPO_NAMES = {
    TargetRepository.WEBSITE: "terraphim/terraphim.ai",
    TargetRepository.TERRAPHIM_AI: "terraphim/terraphim-ai",
    TargetRepository.TERRAPHIM_CLIENTS: "terraphim/terraphim-clients",
}


# ---------------------------------------------------------------------------
# Versions


@dataclass(frozen=True, order=False)
class Version:
    major: int
    minor: int
    patch: int
    prerelease: tuple  # tuple of identifiers, empty = stable

    @staticmethod
    def parse(text: str) -> Optional["Version"]:
        m = re.match(r"^v?(\d{1,10})\.(\d{1,10})\.(\d{1,10})(?:-([0-9A-Za-z.-]+))?$", text)
        if not m:
            return None
        pre = tuple(m.group(4).split(".")) if m.group(4) else ()
        return Version(int(m.group(1)), int(m.group(2)), int(m.group(3)), pre)

    def _key(self):
        # semver precedence: stable > prerelease; numeric identifiers < alnum
        pre_key = tuple(
            (0, int(p)) if p.isdigit() else (1, p) for p in self.prerelease
        )
        stable_flag = 1 if not self.prerelease else 0
        return (self.major, self.minor, self.patch, stable_flag, pre_key)

    def __lt__(self, other: "Version") -> bool:
        return self._key() < other._key()

    def __le__(self, other: "Version") -> bool:
        return self._key() <= other._key()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Version) and self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return base + ("-" + ".".join(self.prerelease) if self.prerelease else "")


# ---------------------------------------------------------------------------
# Component selectors (closed seven-row table)


@dataclass(frozen=True)
class ComponentSelector:
    name: str
    repository: str
    tag_prefix: str          # tag must start with this prefix
    allow_prerelease: bool
    display_strip_v: bool    # render "0.1.7" rather than "v0.1.7"


COMPONENTS: tuple = (
    ComponentSelector("core", "terraphim/terraphim-ai", "", False, False),
    ComponentSelector("clients", "terraphim/terraphim-clients", "", False, False),
    ComponentSelector("editor", "terraphim/terraphim-editor", "", True, False),
    ComponentSelector("vscode", "terraphim/terraphim-ai", "terraphim_vscode-", True, True),
    ComponentSelector("cursor", "terraphim/terraphim-cursor-plugin", "", False, False),
    ComponentSelector("zed", "terraphim/zed-terraphim", "", False, False),
    ComponentSelector("continue", "terraphim/terraphim-ai", "terraphim_continue-", False, True),
)

# clients channel gate: expected target sets per binary manifest
CHANNEL_TARGETS = {
    "terraphim-agent": {
        "aarch64-apple-darwin", "aarch64-unknown-linux-musl",
        "universal-apple-darwin", "x86_64-apple-darwin",
        "x86_64-unknown-linux-gnu", "x86_64-unknown-linux-musl",
    },
    "terraphim-cli": {
        "aarch64-apple-darwin", "aarch64-unknown-linux-musl",
        "x86_64-apple-darwin", "x86_64-unknown-linux-gnu",
        "x86_64-unknown-linux-musl",
    },
    "terraphim-grep": {
        "aarch64-apple-darwin", "aarch64-unknown-linux-musl",
        "universal-apple-darwin", "x86_64-apple-darwin",
        "x86_64-unknown-linux-gnu", "x86_64-unknown-linux-musl",
    },
}


# ---------------------------------------------------------------------------
# Snapshot types


@dataclass(frozen=True)
class ComponentRelease:
    component: str
    repository: str
    tag: str
    version: Version
    prerelease: bool
    published_at: str
    url: str
    asset_names: tuple
    api_url: str


@dataclass(frozen=True)
class ChannelManifest:
    binary: str
    version: str
    released_at: str
    notes_url: str
    targets: tuple
    descriptors: dict
    raw_digest: str


@dataclass(frozen=True)
class ReleaseSnapshot:
    checked_at: str
    components: dict           # component name -> ComponentRelease (admitted only)
    channels: dict             # binary -> ChannelManifest
    input_digests: dict        # source label -> sha256 of raw input
    skipped: dict = field(default_factory=dict)  # component -> skip reason


@dataclass(frozen=True)
class PlannedFile:
    path: str
    original_sha256: str
    proposed_sha256: str
    proposed_bytes: bytes


@dataclass(frozen=True)
class UpdatePlan:
    target: str
    checked_at: str
    admitted: dict             # component -> tag
    files: tuple               # tuple[PlannedFile]

    @property
    def changed(self) -> bool:
        return any(f.original_sha256 != f.proposed_sha256 for f in self.files)


@dataclass(frozen=True)
class CurrentVersions:
    # component -> Version currently displayed in this repository
    displayed: dict


# ---------------------------------------------------------------------------
# HTTP (bounded retries, Retry-After honoured)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects: following them would forward the Authorization
    header to whatever host the redirect names."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def _request_headers(url: str, token: Optional[str]) -> dict:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    host = urllib.parse.urlsplit(url).hostname or ""
    if token and host.endswith(".github.com") or token and host == "github.com":
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _http_get_json(url: str, token: Optional[str], deadline: float) -> Any:
    last_err: Optional[Exception] = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise OperationalFailure(f"discovery budget exhausted before {url}")
        req = urllib.request.Request(url, headers=_request_headers(url, token))
        try:
            with _OPENER.open(req, timeout=min(REQUEST_TIMEOUT_S, remaining)) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            retryable = e.code == 429 or 500 <= e.code < 600
            if not retryable or attempt == MAX_ATTEMPTS:
                raise OperationalFailure(f"GET {url} failed: HTTP {e.code}") from e
            wait = min(RETRY_AFTER_CAP_S, float(e.headers.get("Retry-After") or 2 ** attempt))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            if attempt == MAX_ATTEMPTS:
                raise OperationalFailure(f"GET {url} failed: {e}") from e
            wait = min(RETRY_AFTER_CAP_S, 2 ** attempt)
        time.sleep(min(wait, max(0.0, deadline - time.monotonic())))
    raise OperationalFailure(f"GET {url} failed: {last_err}")


def collect_snapshot(timeout_seconds: int = DISCOVERY_BUDGET_S,
                     token: Optional[str] = None,
                     fetcher: Optional[Callable] = None) -> ReleaseSnapshot:
    """Collect live GitHub release/channel inputs. `fetcher` injects a
    transport for deterministic tests; production uses _http_get_json."""
    deadline = time.monotonic() + timeout_seconds
    token = token or os.environ.get("GITHUB_TOKEN")
    get = fetcher or (lambda url: _http_get_json(url, token, deadline))

    repos = sorted({c.repository for c in COMPONENTS})
    raw_releases: dict = {}
    digests: dict = {}
    for repo in repos:
        url = f"{API_BASE}/repos/{repo}/releases?per_page=30"
        body = get(url)
        raw_releases[repo] = body
        digests[f"releases:{repo}"] = hashlib.sha256(
            json.dumps(body, sort_keys=True).encode()).hexdigest()

    channels: dict = {}
    for binary in CHANNEL_TARGETS:
        url = f"{CHANNEL_BASE}/{binary}/stable-v2.json"
        body = get(url)
        digests[f"channel:{binary}"] = hashlib.sha256(
            json.dumps(body, sort_keys=True).encode()).hexdigest()
        channels[binary] = _parse_channel(binary, body)

    components, skipped = _admit_components(raw_releases, channels)
    return ReleaseSnapshot(
        checked_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        components=components, channels=channels, input_digests=digests,
        skipped=skipped)


def _parse_channel(binary: str, body: dict) -> ChannelManifest:
    if not isinstance(body, dict):
        raise RejectedInput(f"clients channel {binary} manifest is not an object")
    version = body.get("version")
    released_at = body.get("released_at") or body.get("releasedAt") or ""
    notes = body.get("notes_url") or body.get("notesURL") or ""
    targets = tuple(sorted((body.get("targets") or body.get("assets", {}).keys())))
    descriptors = body.get("assets") or body.get("archive_descriptors") or {}
    return ChannelManifest(
        binary=binary, version=str(version or ""), released_at=str(released_at),
        notes_url=str(notes), targets=targets, descriptors=descriptors,
        raw_digest=hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest())


def _release_to_component(sel: ComponentSelector, rel: dict) -> Optional[ComponentRelease]:
    if not isinstance(rel, dict):
        return None
    tag = rel.get("tag_name") or ""
    if not tag.startswith(sel.tag_prefix):
        return None
    if sel.tag_prefix == "" and tag.startswith("terraphim_"):
        return None  # unprefixed selectors exclude component-prefixed tags
    suffix = tag[len(sel.tag_prefix):]
    version = Version.parse(suffix)
    if version is None:
        return None
    if rel.get("draft"):
        return None
    if rel.get("prerelease") and not sel.allow_prerelease:
        return None
    published = str(rel.get("published_at") or "")
    try:
        datetime.fromisoformat(published.replace("Z", "+00:00"))
    except ValueError:
        return None  # malformed metadata: unadmitted rather than crash later
    url = str(rel.get("html_url") or "")
    if url != f"https://github.com/{sel.repository}/releases/tag/{tag}":
        return None  # untrusted link target: never interpolated into output
    return ComponentRelease(
        component=sel.name, repository=sel.repository, tag=tag, version=version,
        prerelease=bool(rel.get("prerelease")),
        published_at=published,
        url=url,
        asset_names=tuple(sorted(a.get("name", "") for a in rel.get("assets", []))),
        api_url=rel.get("url") or "")


def _admit_components(raw_releases: dict, channels: dict) -> tuple:
    admitted: dict = {}
    skipped: dict = {}
    for sel in COMPONENTS:
        candidates = [
            c for c in (
                _release_to_component(sel, r)
                for r in raw_releases.get(sel.repository, [])
            ) if c is not None
        ]
        if not candidates:
            continue  # component unadmitted; per-component proposals continue
        candidates.sort(key=lambda c: (c.version, c.published_at))
        top = candidates[-1]
        ties = [c for c in candidates if c.version == top.version]
        if len({(c.tag, c.published_at, tuple(c.asset_names)) for c in ties}) > 1:
            raise RejectedInput(
                f"conflicting same-version metadata for {sel.name}")
        if sel.name == "clients":
            try:
                _check_channel_gate(top, channels)
            except RejectedInput as e:
                skipped["clients"] = str(e)
                continue
        admitted[sel.name] = top
    return admitted, skipped


def _check_channel_gate(clients: ComponentRelease, channels: dict) -> None:
    ver = str(clients.version)
    for binary, expected in CHANNEL_TARGETS.items():
        ch = channels.get(binary)
        if ch is None:
            raise RejectedInput(f"clients channel manifest missing: {binary}")
        if ch.version != ver:
            raise RejectedInput(
                f"clients channel {binary} version {ch.version!r} != release {ver!r}")
        if clients.tag not in ch.notes_url:
            raise RejectedInput(
                f"clients channel {binary} notesURL does not reference {clients.tag}")
        actual = set(ch.targets)
        if any("windows" in t for t in actual):
            raise RejectedInput(f"clients channel {binary} admits a native Windows target")
        if actual != expected:
            raise RejectedInput(
                f"clients channel {binary} target set mismatch: "
                f"missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
        for t in actual:
            d = ch.descriptors.get(t)
            if not isinstance(d, dict) or not (d.get("url") or d.get("path")) or \
                    not (d.get("sha256") or d.get("digest")) or not d.get("size"):
                raise RejectedInput(
                    f"clients channel {binary} target {t} lacks url/digest/size")


# ---------------------------------------------------------------------------
# Snapshot (de)serialisation


def snapshot_to_dict(snap: ReleaseSnapshot) -> dict:
    return {
        "checked_at": snap.checked_at,
        "components": {n: dataclasses.asdict(c) | {"version": str(c.version)}
                       for n, c in snap.components.items()},
        "channels": {b: dataclasses.asdict(m) for b, m in snap.channels.items()},
        "input_digests": snap.input_digests,
        "skipped": snap.skipped,
    }


def load_snapshot(path: Path) -> ReleaseSnapshot:
    """Load a recorded snapshot. Two shapes accepted:
    - native snapshot_to_dict output, or
    - the research packet shape {repositories: {repo: [releases]}, channels: {}}.
    """
    body = json.loads(Path(path).read_text(encoding="utf-8"))
    if "components" in body and isinstance(body["components"], dict) and \
            all("tag" in v for v in body["components"].values()):
        components = {
            n: ComponentRelease(
                component=n, repository=c["repository"], tag=c["tag"],
                version=Version.parse(c["version"].lstrip("v")),
                prerelease=bool(c["prerelease"]), published_at=c["published_at"],
                url=c["url"], asset_names=tuple(c.get("asset_names", ())),
                api_url=c.get("api_url", ""))
            for n, c in body["components"].items()
        }
        channels = {b: _parse_channel(b, m) for b, m in body.get("channels", {}).items()}
        return ReleaseSnapshot(checked_at=body.get("checked_at", ""),
                               components=components, channels=channels,
                               input_digests=body.get("input_digests", {}),
                               skipped=body.get("skipped", {}))

    # research packet shape: per-repository release lists + channel bodies
    raw_releases = body.get("repositories", {})
    channels = {b: _parse_channel(b, m) for b, m in body.get("channels", {}).items()}
    components, skipped = _admit_components(raw_releases, channels)
    return ReleaseSnapshot(checked_at=body.get("checked_at", ""),
                           components=components, channels=channels,
                           input_digests={}, skipped=skipped)


# ---------------------------------------------------------------------------
# Current state parsing


def _read(root: Path, rel: str) -> Optional[bytes]:
    p = Path(root) / rel
    return p.read_bytes() if p.is_file() else None


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


_RELEASE_LINK = re.compile(
    r"github\.com/([^/\s]+/[^/\s]+)/releases/tag/([^)\s]+)")


def _match_component(repository: str, tag: str):
    """Selector whose repo and tag-prefix both match; None otherwise."""
    for sel in COMPONENTS:
        if sel.repository != repository:
            continue
        if not tag.startswith(sel.tag_prefix):
            continue
        if sel.tag_prefix == "" and tag.startswith("terraphim_"):
            continue
        v = Version.parse(tag[len(sel.tag_prefix):].lstrip("v"))
        if v is not None:
            return sel, v
    return None


def parse_current_readme(readme: bytes) -> dict:
    """component -> Version currently displayed in the README downloads block."""
    text = readme.decode("utf-8")
    out: dict = {}
    row_re = re.compile(r"^\|[^|]*\|\s*\[[^\]]*\]\(([^)]*)\)", re.M)
    for m in row_re.finditer(text):
        link = _RELEASE_LINK.search(m.group(1))
        if not link:
            continue
        matched = _match_component(link.group(1), link.group(2))
        if matched and matched[0].name not in out:
            out[matched[0].name] = matched[1]
    return out


def parse_current_config(config: bytes) -> Optional[Version]:
    m = re.search(rb'(?m)^release_version = "([^"]+)"', config)
    return Version.parse(m.group(1).decode()) if m else None


def current_versions(root: Path, target: TargetRepository) -> CurrentVersions:
    displayed: dict = {}
    readme = _read(root, "README.md")
    if readme:
        displayed.update(parse_current_readme(readme))
    if target is TargetRepository.WEBSITE:
        config = _read(root, "config.toml")
        if config:
            v = parse_current_config(config)
            if v:
                displayed["clients"] = v
    return CurrentVersions(displayed=displayed)


# ---------------------------------------------------------------------------
# Validation


def validate_snapshot(snapshot: ReleaseSnapshot, current: CurrentVersions) -> None:
    for name, rel in snapshot.components.items():
        cur = current.displayed.get(name)
        if cur is not None and rel.version < cur:
            raise RejectedInput(
                f"{name}: admitted {rel.version} is a downgrade of displayed {cur}")


# ---------------------------------------------------------------------------
# Rendering: website active fields


@dataclass(frozen=True)
class Slot:
    name: str
    pattern: re.Pattern  # one capture group = the value slot to rewrite
    min_count: int
    max_count: Optional[int]
    value: str            # rendered replacement for the captured group


def _apply_slots(text: str, slots: list, filename: str) -> str:
    for slot in slots:
        matches = list(slot.pattern.finditer(text))
        if not (slot.min_count <= len(matches) <= (slot.max_count or 10**6)):
            raise RejectedInput(
                f"{filename}: anchor {slot.name} matched {len(matches)} times, "
                f"expected {slot.min_count}..{slot.max_count}")
        def repl(m, _v=slot.value):
            return m.group(0)[:m.start(1) - m.start(0)] + _v + m.group(0)[m.end(1) - m.start(0):]
        text = slot.pattern.sub(repl, text)
    return text


def _semver() -> str:
    return r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?"


def _pretty_date(published_at: str) -> str:
    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    return f"{dt.day} {MONTHS[dt.month - 1]} {dt.year}"


def _website_fields(root: Path, clients: ComponentRelease) -> list:
    """(path, proposed_bytes) for the clients-version-driven site fields."""
    ver = str(clients.version)
    date = _pretty_date(clients.published_at)
    sv = _semver()
    out = []

    config = _read(root, "config.toml")
    if config is not None:
        text = config.decode()
        new = _apply_slots(text, [Slot(
            "release_version",
            re.compile(r'(?m)^release_version = "(' + sv + r')"'),
            1, 1, ver)], "config.toml")
        out.append(("config.toml", new.encode()))

    releases = _read(root, "content/releases.md")
    if releases is not None:
        text = releases.decode()
        parts = re.split(r"(?m)^(## Previous Release[^\n]*)$", text, maxsplit=1)
        if len(parts) != 3:
            raise RejectedInput(
                "content/releases.md: expected exactly one '## Previous Release' boundary")
        active, boundary, history = parts
        active = _apply_slots(active, [
            Slot("latest_heading",
                 re.compile(r"(?m)^## Latest Release: v(" + sv + r")$"), 1, 1, ver),
            Slot("released_date",
                 re.compile(r"(?m)^\*\*Released:\*\* (.+)$"), 1, 1, date),
            Slot("latest_stable",
                 re.compile(r"\*\*Latest Stable:\*\* v(" + sv + r")"), 1, 1, ver),
            Slot("release_tag_links",
                 re.compile(
                     r"https://github\.com/terraphim/terraphim-clients/releases/tag/v("
                     + sv + r")"), 1, None, ver),
            Slot("agent_archive_examples",
                 re.compile(r"terraphim-agent-(" + sv + r")-"), 0, None, ver),
            Slot("version_prose",
                 re.compile(r"v(" + sv + r")(?= ships across)"), 0, None, ver),
        ], "content/releases.md")
        out.append(("content/releases.md", (active + boundary + history).encode()))

    install = _read(root, "content/docs/installation.md")
    if install is not None:
        text = install.decode()
        new = _apply_slots(text, [
            Slot("installer_version_flag",
                 re.compile(r"install\.sh \| bash --version (" + sv + r")"), 0, 1, ver),
            Slot("version_assignment",
                 re.compile(r"(?m)^VERSION=(" + sv + r")$"), 0, None, ver),
            Slot("backtick_version",
                 re.compile(r"`(" + sv + r")`"), 0, None, ver),
            Slot("agent_version_output",
                 re.compile(r"(?m)^# terraphim-agent (" + sv + r")$"), 0, 1, ver),
        ], "content/docs/installation.md")
        out.append(("content/docs/installation.md", new.encode()))

    index = _read(root, "themes/WarpDrive/templates/index.html")
    if index is not None:
        text = index.decode()
        new = _apply_slots(text, [
            Slot("default_fallbacks",
                 re.compile(r"release_version \| default\(value=['\"]([^'\"]+)['\"]\)"),
                 1, None, ver),
        ], "index.html")
        out.append(("themes/WarpDrive/templates/index.html", new.encode()))

    site_js = _read(root, "themes/WarpDrive/static/js/site.js")
    if site_js is not None:
        text = site_js.decode()
        new = _apply_slots(text, [
            Slot("js_fallback",
                 re.compile(r"data-version'\) \|\| '([^']+)'"), 1, 1, ver),
        ], "site.js")
        out.append(("themes/WarpDrive/static/js/site.js", new.encode()))

    # quickstart.md: declared allowed path, no managed slots currently
    return out


# ---------------------------------------------------------------------------
# Rendering: README managed region


ROW_LABELS = (
    ("Core project", "core", "Stable core/source release"),
    ("CLI clients", "clients",
     "Stable `terraphim-grep`, agent and client tools"),
    ("Terraphim Editor", "editor", "Browser editor prerelease"),
    ("VS Code extension", "vscode", "Prerelease VSIX for compatible editors"),
    ("Cursor plugin", "cursor",
     "Native Cursor plugin; separate from the VSIX catalogue"),
    ("Stock Zed extension", "zed",
     "GitHub download; official Zed catalogue submission remains pending"),
    ("Continue integration", "continue", "Continue integration package"),
)


def render_downloads_region(snapshot: ReleaseSnapshot,
                            existing_rows: Optional[dict] = None) -> str:
    c = snapshot.components
    checked = datetime.fromisoformat(
        snapshot.checked_at.replace("Z", "+00:00")) if snapshot.checked_at \
        else datetime.now(timezone.utc)
    date = f"{checked.day} {MONTHS[checked.month - 1]} {checked.year}"
    existing_rows = existing_rows or {}

    def disp(sel: ComponentSelector) -> str:
        v = str(c[sel.name].version)
        return v if sel.display_strip_v else "v" + v

    lines = [
        README_MARKER_START,
        f"Verified release links as of {date}. Core services and CLI clients have",
        "separate releases.",
        "",
        "| Component | Release | Use |",
        "| --- | --- | --- |",
    ]
    for label, name, desc in ROW_LABELS:
        sel = next(s for s in COMPONENTS if s.name == name)
        if name not in c:
            if label not in existing_rows:
                raise RejectedInput(
                    f"{name}: unadmitted and no existing row to preserve")
            lines.append(existing_rows[label])
            continue
        lines.append(f"| {label} | [{disp(sel)}]({c[name].url}) | {desc} |")
    lines.append(README_MARKER_END)
    return "\n".join(lines)


def _existing_rows(block: str) -> dict:
    rows = {}
    for line in block.splitlines():
        m = re.match(r"^\| ([^|]+) \| ", line)
        if m and m.group(1).strip() not in ("Component", "---"):
            rows[m.group(1).strip()] = line
    return rows


def _readme_region(readme: bytes, snapshot: ReleaseSnapshot) -> bytes:
    """Return proposed README bytes with the managed region regenerated.
    Unadmitted components keep their existing row bytes."""
    text = readme.decode("utf-8")
    start_n = text.count(README_MARKER_START)
    end_n = text.count(README_MARKER_END)
    if start_n != end_n or start_n > 1:
        raise RejectedInput("README.md: duplicate or unbalanced downloads markers")
    if start_n == 1 and \
            text.index(README_MARKER_END) < text.index(README_MARKER_START):
        raise RejectedInput("README.md: downloads END marker precedes START")

    if start_n == 0:
        # Pre-migration: exactly one Current downloads heading whose block
        # matches the known structure (verified line + 7-row table).
        headings = re.findall(r"(?m)^## Current downloads\s*$", text)
        if len(headings) != 1:
            raise RejectedInput(
                "README.md: markers absent and '## Current downloads' heading "
                f"found {len(headings)} times")
        head_pos = text.index(README_HEADING)
        tail = text[head_pos:]
        next_head = re.search(r"(?m)^##{1,3} ", tail[len(README_HEADING):])
        block_end = len(text) if next_head is None else \
            head_pos + len(README_HEADING) + next_head.start()
        block = text[head_pos:block_end]
        if "Verified release links as of" not in block or \
                block.count("\n|") < 7 or "| Component | Release | Use |" not in block:
            raise RejectedInput(
                "README.md: markers absent and downloads block does not match "
                "the known seven-row structure; refusing to guess region")
        # Migration: markers wrap intro line + table; trailing paragraph stays out.
        rendered = render_downloads_region(snapshot, _existing_rows(block))
        table_end = block.rindex("\n|")
        table_end = block.index("\n", table_end + 2)
        insert_at = head_pos + table_end + 1
        inner_start = head_pos + len(README_HEADING)
        proposed = text[:inner_start] + "\n" + rendered + text[insert_at:]
        return proposed.encode()

    # Marked file: regenerate strictly between the markers.
    s = text.index(README_MARKER_START) + len(README_MARKER_START)
    e = text.index(README_MARKER_END)
    inner_current = text[s:e]
    rendered = render_downloads_region(snapshot, _existing_rows(inner_current))
    new_inner = rendered[rendered.index(README_MARKER_START) + len(README_MARKER_START):
                         rendered.index(README_MARKER_END)]
    return (text[:s] + new_inner + text[e:]).encode()


# ---------------------------------------------------------------------------
# Plan / apply


ALLOWED_PATHS = {
    TargetRepository.WEBSITE: {
        "config.toml", "content/releases.md", "content/docs/installation.md",
        "content/docs/quickstart.md", "themes/WarpDrive/templates/index.html",
        "themes/WarpDrive/static/js/site.js", "README.md",
    },
    TargetRepository.TERRAPHIM_AI: {"README.md"},
    TargetRepository.TERRAPHIM_CLIENTS: {"README.md"},
}


def plan_updates(root: Path, target: TargetRepository,
                 snapshot: ReleaseSnapshot) -> UpdatePlan:
    root = Path(root)
    current = current_versions(root, target)
    validate_snapshot(snapshot, current)

    proposed: list = []
    if target is TargetRepository.WEBSITE and "clients" in snapshot.components:
        proposed.extend(_website_fields(root, snapshot.components["clients"]))
    elif target is TargetRepository.WEBSITE:
        # clients unadmitted: website version fields stay; README still updates
        pass

    readme = _read(root, "README.md")
    if readme is not None:
        proposed.append(("README.md", _readme_region(readme, snapshot)))

    files = []
    for rel_path, new_bytes in proposed:
        if rel_path not in ALLOWED_PATHS[target]:
            raise RejectedInput(f"plan contains disallowed path {rel_path}")
        old = _read(root, rel_path)
        if old is None:
            raise RejectedInput(f"missing required file {rel_path}")
        files.append(PlannedFile(
            path=rel_path, original_sha256=_sha(old),
            proposed_sha256=_sha(new_bytes), proposed_bytes=new_bytes))

    return UpdatePlan(
        target=target.value, checked_at=snapshot.checked_at,
        admitted={n: c.tag for n, c in snapshot.components.items()},
        files=tuple(files))


def apply_plan(plan: UpdatePlan, root: Path,
               _replace: Callable = os.replace) -> dict:
    """Verify original hashes, stage via temp+os.replace, restore on failure.
    `_replace` injects a fault seam for tests; production uses os.replace."""
    root = Path(root)
    staged: list = []    # (path, temp_path, original_bytes) not yet swapped in
    replaced: list = []  # paths already swapped in, need restore on failure
    try:
        for f in plan.files:
            p = root / f.path
            current = p.read_bytes()
            if _sha(current) != f.original_sha256:
                raise OperationalFailure(
                    f"{f.path}: original hash mismatch; refusing to overwrite")
            if f.proposed_sha256 == f.original_sha256:
                continue  # byte-identical: no write needed
            fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".relupd-")
            os.fchmod(fd, p.stat().st_mode)  # mkstemp is 0600; keep the mode
            with os.fdopen(fd, "wb") as fh:
                fh.write(f.proposed_bytes)
            staged.append((p, tmp, current))
        for p, tmp, _ in staged:
            _replace(tmp, str(p))
            replaced.append(p)
    except Exception as e:
        orig = {p: b for p, _, b in staged}
        for p in replaced:
            p.write_bytes(orig[p])
        raise OperationalFailure(f"apply failed, originals restored: {e}") from e
    finally:
        for _, tmp, _ in staged:
            if Path(tmp).exists():
                os.unlink(tmp)
    return {
        "receiptType": "update",
        "target": plan.target,
        "checked_at": plan.checked_at,
        "admitted": plan.admitted,
        "outcome": "applied" if plan.changed else "unchanged",
        "files": [{"path": f.path,
                   "status": "unchanged" if f.original_sha256 == f.proposed_sha256
                            else "applied"}
                  for f in plan.files],
    }


# ---------------------------------------------------------------------------
# CLI


def _cmd(args: argparse.Namespace) -> int:
    try:
        if args.snapshot:
            snap = load_snapshot(Path(args.snapshot))
        else:
            snap = collect_snapshot(timeout_seconds=args.timeout)
        if args.snapshot_out:
            Path(args.snapshot_out).write_text(
                json.dumps(snapshot_to_dict(snap), indent=2) + "\n")
        target = TargetRepository(args.target)
        root = Path(args.root or ".").resolve()
        plan = plan_updates(root, target, snap)

        receipt = {
            "receiptType": "discovery",
            "target": target.value,
            "checked_at": snap.checked_at,
            "admitted": plan.admitted,
            "input_digests": snap.input_digests,
            "skipped": snap.skipped,
            "files": [{"path": f.path, "original_sha256": f.original_sha256,
                       "proposed_sha256": f.proposed_sha256,
                       "changed": f.original_sha256 != f.proposed_sha256}
                      for f in plan.files],
            "outcome": "drift" if plan.changed else "unchanged",
        }
        if args.receipt:
            Path(args.receipt).write_text(json.dumps(receipt, indent=2) + "\n")

        if args.check:
            for f in plan.files:
                if f.original_sha256 != f.proposed_sha256:
                    print(f"drift: {f.path}")
            if plan.changed:
                return EXIT_DRIFT
            print("no drift")
            return EXIT_OK

        out = apply_plan(plan, root)
        if args.receipt:
            Path(args.receipt).write_text(json.dumps(out, indent=2) + "\n")
        for f in out["files"]:
            print(f"{f['status']}: {f['path']}")
        print(out["outcome"])
        return EXIT_OK
    except RejectedInput as e:
        print(f"rejected: {e}", file=sys.stderr)
        return EXIT_REJECTED
    except OperationalFailure as e:
        print(f"operational failure: {e}", file=sys.stderr)
        return EXIT_OPERATIONAL
    except (OSError, json.JSONDecodeError, KeyError,
            ValueError, AttributeError, TypeError) as e:
        # malformed upstream data or structural surprises are operational
        # failures (exit 3), never silent drift (exit 1) or tracebacks
        print(f"operational failure: {e}", file=sys.stderr)
        return EXIT_OPERATIONAL


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report drift without writing; exit 1 on drift")
    ap.add_argument("--snapshot", help="recorded ReleaseSnapshot JSON")
    ap.add_argument("--snapshot-out",
                    help="write the collected snapshot JSON here")
    ap.add_argument("--receipt", help="write run receipt JSON here")
    ap.add_argument("--target", choices=[t.value for t in TargetRepository],
                    default=TargetRepository.WEBSITE.value)
    ap.add_argument("--root", help="repository checkout root (default: cwd)")
    ap.add_argument("--timeout", type=int, default=DISCOVERY_BUDGET_S,
                    help="total discovery budget seconds")
    return _cmd(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
