+++
title = "Releases"
description = "Latest Terraphim AI releases and changelog"
date = 2026-07-08
sort_by = "date"
paginate_by = 10
+++

# Releases

Stay up-to-date with the latest Terraphim AI releases.

## Latest Release: v1.21.16

**Released:** 25 September 2026

[GitHub Releases](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.16) | [Release Notes](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.16)

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

- [terraphim-agent manifest](https://downloads.terraphim.ai/terraphim-agent/stable-v2.json)
- [terraphim-grep manifest](https://downloads.terraphim.ai/terraphim-grep/stable-v2.json)
- [terraphim-cli manifest](https://downloads.terraphim.ai/terraphim-cli/stable-v2.json)

The `stable-v2.json` manifests carry the version, release date and a SHA-256
digest plus size for every published archive. The older `stable.json` pointers
are still served for pre-1.21.15 clients.

Download the latest archive for your platform directly:

```bash
curl -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-1.21.16-x86_64-unknown-linux-gnu.tar.gz"
tar -xzf terraphim-agent-1.21.16-*.tar.gz
sudo mv terraphim-agent /usr/local/bin/
```

### Available Binaries

v1.21.16 ships across three client tools:

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

### What's New

**Public install path corrected**
- The universal installer now resolves release versions from the channel manifests rather than from version-less GitHub assets, so it installs the current release instead of an older one
- Downloads are verified against the manifest's SHA-256 before anything is unpacked, and a mismatch aborts the install
- Archives are unpacked from a staging directory; the destination is only written once the bytes are verified and the expected binary is present

**Version reporting and exit codes**
- The installer reports a specific exit code per failure (unreachable manifest, unavailable version, failed download, checksum mismatch)

**Release integrity**
- `stable-v2.json` manifests publish a SHA-256 digest and byte size for every archive
- Archive signing (Ed25519 / zipsign) continues to apply to every `.tar.gz`

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

**Latest Stable:** v1.21.16

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

## Previous Release: v1.20.5

**Released:** 14 June 2026

The final release distributed exclusively through GitHub Releases before the R2 migration. v1.20.5 binaries remain available on [GitHub](https://github.com/terraphim/terraphim-ai/releases/tag/v1.20.5) and will continue to be served as the GitHub fallback. From v1.21.9 onward, all releases are published to both GitHub and R2.
