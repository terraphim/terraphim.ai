+++
title = "Releases"
description = "Latest Terraphim AI releases and changelog"
date = 2026-07-08
sort_by = "date"
paginate_by = 10
+++

# Releases

Stay up-to-date with the latest Terraphim AI releases.

## Latest Release: v1.21.14

**Released:** 11 September 2026

[GitHub Releases](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.14) | [Release Notes](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.14)

### Self-Update (recommended)

If you already have a Terraphim client installed, update it with a single command — no GitHub credentials, no rate limiting:

```bash
terraphim-agent update
terraphim-grep update
```

The self-update backend is served from our R2 bucket (`downloads.terraphim.ai`) with Ed25519 signature verification. GitHub Releases is an automatic fallback if R2 is unreachable.

### Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash
```

### Direct Downloads

Binaries are distributed via Cloudflare R2 with zero-egress CDN. Browse the manifests:

- [terraphim-agent manifest](https://downloads.terraphim.ai/terraphim-agent/stable.json)
- [terraphim-grep manifest](https://downloads.terraphim.ai/terraphim-grep/stable.json)
- [terraphim-cli manifest](https://downloads.terraphim.ai/terraphim-cli/stable.json)

Download the latest archive for your platform directly:

```bash
curl -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-1.21.14-x86_64-unknown-linux-gnu.tar.gz"
tar -xzf terraphim-agent-1.21.14-*.tar.gz
sudo mv terraphim-agent /usr/local/bin/
```

### Available Binaries

v1.21.14 ships across three client tools:

- **`terraphim-agent`** — full CLI + REPL + TUI
- **`terraphim-grep`** — intelligent hybrid search with RLM fallback
- **`terraphim-cli`** — lightweight command-line toolkit

Platforms:

| Platform | Agent | Grep | CLI |
|---|---|---|---|
| Linux x86_64 (GNU) | ✓ | ✓ | ✓ |
| Linux x86_64 (MUSL) | ✓ | ✓ | ✓ |
| Linux ARM64 (MUSL) | ✓ | ✓ | ✓ |
| macOS Apple Silicon | ✓ | ✓ | ✓ |
| macOS Intel | ✓ | ✓ | ✓ |
| macOS Universal | ✓ | ✓ | — |
| Windows x64 | ✓ | ✓ | ✓ |

All Linux and macOS archives are **Ed25519-signed** and verified on install by the self-updater. macOS universal binaries are additionally **notarised** by Apple.

### What's New in v1.21.14

**`terraphim-agent` de-monolithization (issue #211)**
- `main.rs` slimmed from 6,842 → 5,638 LOC (−17.6%): extracted `cli_helpers`, `cli_schema`, and `robot_dispatch` modules
- All fifteen `run_offline_command` handler arms extracted — dispatch is now a pure function

**Workspace**
- `terraphim_types` 1.21.0 → 1.22.1 across all member crates
- Registry policy documented in the `[patch.crates-io]` block

**Verification**
- fmt / `clippy --workspace --all-targets -D warnings` / `cargo build --workspace` all clean
- 582 terraphim-agent tests pass (489 lib + 93 bin)

### From v1.21.9 (July 2026)

- R2 binary distribution with Ed25519/zipsign archive signing — unsigned archives are a hard failure
- Self-update robustness: install-path fix, atomic-rename install, `TERRAPHIM_UPDATE_BACKEND=r2|github` override

### Installation

{{< tabs >}}
{{< tab "Self-update" >}}
```bash
# Already have terraphim-agent?  Update in-place.
terraphim-agent update
terraphim-grep update
```
{{< /tab >}}
{{< tab "Universal installer" >}}
```bash
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash
```
{{< /tab >}}
{{< tab "Cargo" >}}
```bash
cargo install terraphim_agent --features repl-full
```
{{< /tab >}}
{{< tab "Homebrew" >}}
```bash
brew tap terraphim/terraphim && brew install terraphim-agent
```
{{< /tab >}}
{{< /tabs >}}

[Installation Guide](/docs/installation)

## All Releases

View complete release history on [GitHub Releases (terraphim-clients)](https://github.com/terraphim/terraphim-clients/releases).

## Release Channels

### Stable

Stable releases are recommended for production use. They are thoroughly tested and signed. The self-updater fetches signed archives from `downloads.terraphim.ai` by default.

**Latest Stable:** v1.21.14

### Development

Development releases contain the latest features and improvements. Use these for testing.

Check the [main branch](https://github.com/terraphim/terraphim-clients) for development builds.

## Upgrade Guide

### From Any Version to Latest

```bash
# Self-update (recommended, no GitHub token needed)
terraphim-agent update

# Or via the universal installer
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash
```

### Configuration Compatibility

Terraphim maintains backward compatibility for configuration files across minor versions. Major version bumps may require configuration updates.

## Verify Your Installation

```bash
terraphim-agent --version
terraphim-agent check-update
```

## Security & Integrity

- Every archive is **Ed25519-signed** with zipsign. The self-updater verifies the signature before installing; tampered or unsigned archives are rejected.
- Archives are served over **TLS 1.2+** from Cloudflare's CDN.
- Public keys are embedded in the binary at compile time; no runtime key-download trust-on-first-use.
- See [ADR-001](https://github.com/terraphim/terraphim-clients/blob/main/adr/ADR-001.md) for the key rotation design.

## Beta Testing

Want to test new features before they're released?

Join our [Discord server](https://discord.gg/VPJXB6BGuY) and look for #beta-testing channel. Beta testers get early access to new features and help shape the product.

## Need Help?

If you encounter issues with a release:

1. Search [existing issues](https://github.com/terraphim/terraphim-clients/issues)
2. [Create a new issue](https://github.com/terraphim/terraphim-clients/issues/new)
3. Join [Discord community](https://discord.gg/VPJXB6BGuY) for support

## Previous Releases

**v1.21.9** (6 July 2026) — the first release distributed via R2 with Ed25519 signing. Binaries on [GitHub](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.9) and R2.

**v1.20.5** (14 June 2026) — the final release distributed exclusively through GitHub Releases before the R2 migration. v1.20.5 binaries remain available on [GitHub](https://github.com/terraphim/terraphim-ai/releases/tag/v1.20.5). From v1.21.9 onward, all releases are published to both GitHub and R2.
