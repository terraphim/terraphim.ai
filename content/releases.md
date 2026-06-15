+++
title = "Releases"
description = "Latest Terraphim AI releases and changelog"
date = 2026-04-03
sort_by = "date"
paginate_by = 10
+++

# Releases

Stay up-to-date with the latest Terraphim AI releases.

## Latest Release: v1.20.5

**Released:** 14 June 2026

[Download from GitHub](https://github.com/terraphim/terraphim-ai/releases/tag/v1.20.5) | [GitHub Releases](https://github.com/terraphim/terraphim-ai/releases)

### Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash
```

### Available Binaries

v1.20.5 ships **53 release assets** across server and client tooling:

- **Server** (`terraphim_server`): macOS universal (signed & notarized), Linux GNU/MUSL, Windows, Debian `.deb`
- **Clients** (`terraphim-agent`, `terraphim-cli`, `terraphim-grep`): macOS, Linux GNU/MUSL, Windows
- **Docker**: multi-arch images for Ubuntu 20.04 and 22.04 (`ghcr.io/terraphim/terraphim-server`)
- **Checksums**: `checksums.txt` for integrity verification

Platforms:

- **macOS**: Apple Silicon (ARM64), Intel (x64), Universal
- **Linux**: x86_64 (GNU), x86_64 (MUSL), ARM64 (MUSL)
- **Windows**: x64
- **Debian packages**: `terraphim-server` amd64

### New in This Release

**Polyrepo release pipeline**
- Client binaries built from [terraphim-clients](https://github.com/terraphim/terraphim-clients) and attached to the main release
- Comprehensive GitHub Actions release: server matrix, Docker, Debian packages, macOS notarization, Homebrew tap update

**Server & infrastructure**
- `terraphim_service` 1.20.5 from the Terraphim cargo registry (openrouter fix)
- MUSL cross-compilation for x86_64 and aarch64 Linux
- Docker images published for `linux/amd64` and `linux/arm64`

**Developer experience**
- `terraphim-agent` REPL, `terraphim-cli` toolkit, and `terraphim-grep` hybrid search on all major platforms
- Homebrew formulas updated via automated release workflow

### Installation

Choose your preferred method:

```bash
# Universal installer (recommended)
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash

# Homebrew
brew tap terraphim/terraphim && brew install terraphim-server terraphim-agent

# Cargo
cargo install terraphim_agent --features repl-full
```

[Installation Guide](/docs/installation)

## All Releases

View complete release history on [GitHub Releases](https://github.com/terraphim/terraphim-ai/releases).

## Release Channels

### Stable

Stable releases are recommended for production use. They have been thoroughly tested and are the most reliable version.

**Latest Stable:** v1.20.5

### Development

Development releases contain the latest features and improvements but may have more bugs. Use these for testing new features.

Check the [main branch](https://github.com/terraphim/terraphim-ai/tree/main) for development builds.

## Upgrade Guide

### From Any Version to Latest

```bash
# Universal installer (recommended)
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash

# Cargo
cargo install terraphim_agent --features repl-full --force
```

### Configuration Compatibility

Terraphim maintains backward compatibility for configuration files across minor versions. Major version bumps (e.g., 1.x to 2.0) may require configuration updates.

## Verify Your Installation

After installation or upgrade, verify your version:

```bash
terraphim-agent --version
```

## Beta Testing

Want to test new features before they're released?

Join our [Discord server](https://discord.gg/VPJXB6BGuY) and look for #beta-testing channel. Beta testers get early access to new features and help shape product.

## Security Updates

Security updates are released as soon as they're available. Stay informed by:

- Watching the [repository](https://github.com/terraphim/terraphim-ai/watchers)
- Subscribing to [security advisories](https://github.com/terraphim/terraphim-ai/security/advisories)
- Following [@alex_mikhalev](https://twitter.com/alex_mikhalev) on Twitter

## Need Help?

If you encounter issues with a release:

1. Search [existing issues](https://github.com/terraphim/terraphim-ai/issues)
2. [Create a new issue](https://github.com/terraphim/terraphim-ai/issues/new)
3. Join [Discord community](https://discord.gg/VPJXB6BGuY) for support
4. Visit [Discourse forum](https://terraphim.discourse.group) for discussions