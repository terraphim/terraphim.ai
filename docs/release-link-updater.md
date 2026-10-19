# Release link updater

`scripts/update-release.sh` keeps the site's advertised release links and the
three repository READMEs' "Current downloads" tables in step with the actual
published releases. It delegates to `scripts/update_release.py` (Python
standard library only) and propagates its exit status.

Fixes terraphim/terraphim.ai#33: the previous implementation fetched
`releases/latest` on terraphim-ai (which resolves to the older **core**
release, not the clients release), rewrote every `**Released:**` date including
historical blocks, and could not maintain the READMEs at all.

## Input authorities

| Row | Source of truth | Selector |
| --- | --- | --- |
| Core project | `terraphim/terraphim-ai` releases | newest non-draft, non-prerelease unprefixed `v*` tag |
| CLI clients | `terraphim/terraphim-clients` releases **plus** all three stable-v2 channel manifests | newest stable `v*` whose version every manifest agrees on |
| Terraphim Editor | `terraphim/terraphim-editor` releases | newest non-draft `v*` in the series (stable or prerelease) |
| VS Code extension | `terraphim/terraphim-ai` releases | newest non-draft `terraphim_vscode-v*` |
| Cursor plugin | `terraphim/terraphim-cursor-plugin` releases | newest non-draft, non-prerelease `v*` |
| Stock Zed extension | `terraphim/zed-terraphim` releases | newest non-draft, non-prerelease `v*` |
| Continue integration | `terraphim/terraphim-ai` releases | newest non-draft `terraphim_continue-v*` |

The clients row is admitted only when the GitHub release and all three
stable-v2 manifests (`terraphim-agent`, `terraphim-cli`, `terraphim-grep` on
`downloads.terraphim.ai`) agree on the version, reference the release in
`notes_url`, and carry complete archive descriptors for the expected target
set. A partial rollout skips only the clients row; the other six rows still
update in the same run. Manifest hashes are availability/size metadata, not
signature verification — the unchanged `check-release-links.py` remains the
independent link checker.

The displayed client date is the GitHub release `published_at` UTC calendar
date. Historical release blocks are never rewritten. A discovered version
lower than the displayed one is rejected — a deliberate rollback is a normal
reviewed change.

## What it writes

**Website (this repository):** `config.toml` `extra.release_version` (never
`extra.version`), the active block of `content/releases.md` (the `## Previous
Release` boundary and everything after it is opaque preserved bytes), the
version slots in `content/docs/installation.md`,
`themes/WarpDrive/templates/index.html` `default()` fallbacks, the
`themes/WarpDrive/static/js/site.js` fallback literal, and the README managed
region. `content/docs/quickstart.md` is a declared allowed path with no
managed slots today.

**terraphim-ai and terraphim-clients:** the README managed region only.

Every managed field is located by an explicit structural anchor; zero or
multiple matches fail the file before any write. No global substitution of
version-shaped strings — literals like `pre-1.21.15` and `rustc 1.85.0`
requirements are outside the anchors and are preserved.

## README managed region

The downloads block is bounded by a single marker pair:

```text
<!-- terraphim-downloads:start -->
<!-- terraphim-downloads:end -->
```

The first generated update inserts the markers around the existing
"Current downloads" block when it matches the known seven-row structure.
Afterwards the region between the markers is regenerated from the admitted
snapshot; anything outside is byte-preserved. Marker-free files whose block
does not match the expected structure, and files with duplicate or unbalanced
markers, are refused.

## Usage

```bash
# Apply in the current checkout (live discovery)
./scripts/update-release.sh

# Report drift without writing (exit 1 on drift, 0 when clean)
./scripts/update-release.sh --check

# Replay a recorded snapshot (deterministic; used by tests and receipts)
./scripts/update-release.sh --snapshot snapshot.json --receipt receipt.json

# Target another repository checkout
./scripts/update-release.sh --target terraphim-ai --root ../terraphim-ai
```

Exit codes: `0` success or already-current, `1` drift found in `--check`,
`2` rejected inputs (conflicting metadata, downgrades, incomplete channels
blocking a required field, anchor/marker violations), `3` operational failure
(network exhaustion, I/O, hash conflict at apply time).

Discovery budget: 30 s per request, up to 3 attempts on 5xx/429 honouring
`Retry-After` (capped 120 s), 300 s total. `GITHUB_TOKEN` is used for API
reads when present; anonymous reads work for public repositories. Release
metadata is data only — never executed.

## Automation model

Each repository runs its own updater workflow with its own `GITHUB_TOKEN` and
proposes a normal reviewed pull request on branch `bot/release-updater`
(commit via GraphQL `createCommitOnBranch`; the PR is reused across runs).
Generated commits in terraphim-clients must read back `verified` before the
PR is touched — an unverified signature is a visible failure, never a silent
unsigned fallback.

If the update branch was changed by an unexpected actor or its head moved,
the writer refuses and comments on the PR; a human resolves it. It never
force-pushes or resets other people's changes.

`scripts/release_update_pr.py` implements the proposal step;
`scripts/release-update-receipt.schema.json` defines the discovery, update
and proposal receipts emitted as CI artifacts.

## Tests

```bash
python3 scripts/tests/test_update_release.py
python3 scripts/tests/test_release_update_pr.py
```

Fixtures under `scripts/tests/fixtures/release-update/` are real files copied
from merged source heads and real captured release/channel responses. They
are recorded inputs for deterministic tests — not live verification. Actual
CI/CD behaviour is proven by real workflow runs as a separate gate.

## Failure and rollback

- Disable only the updater workflow to stop future proposals; receipts are
  retained as run artifacts.
- Erroneous unmerged PRs are closed, not force-pushed.
- Merged output is repaired by a normal reviewed revert/fix.
- A failed repository is reported independently; success in one repository
  does not imply the others completed.
