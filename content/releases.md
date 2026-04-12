+++
title = "Releases"
description = "Latest Terraphim AI releases and changelog"
date = 2026-04-03
sort_by = "date"
paginate_by = 10
+++

# Releases

Stay up-to-date with the latest Terraphim AI releases.

## Latest Release: v1.16.31

**Released:** 7 April 2026

[Download from GitHub](https://github.com/terraphim/terraphim-ai/releases/latest) | [GitHub Releases](https://github.com/terraphim/terraphim-ai/releases)

### Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash
```

### Available Binaries

v1.15.0 ships pre-built binaries for 7 platforms:

- **macOS**: Apple Silicon (ARM64), Intel (x64), Universal
- **Linux**: x86_64 (GNU), x86_64 (MUSL), ARM64 (MUSL), ARMv7 (MUSL)
- **Windows**: x64
- **Debian packages**: amd64

Three binaries in each release:
- `terraphim-agent` -- Interactive TUI/REPL with knowledge graph search
- `terraphim-cli` -- CLI for automation, scripting, and JSON output
- `terraphim_server` -- HTTP REST API server

### Installation

Choose your preferred method:

```bash
# Universal installer (recommended)
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash

# Homebrew
brew tap terraphim/terraphim && brew install terraphim-ai

# Cargo
cargo install terraphim-agent
cargo install terraphim-cli
```

[Installation Guide](/docs/installation)

## All Releases

View complete release history on [GitHub Releases](https://github.com/terraphim/terraphim-ai/releases).

## Release Channels

### Stable

Stable releases are recommended for production use. They have been thoroughly tested and are the most reliable version.

**Latest Stable:** v1.16.31

### Development

Development releases contain the latest features and improvements but may have more bugs. Use these for testing new features.

Check the [main branch](https://github.com/terraphim/terraphim-ai/tree/main) for development builds.

## Upgrade Guide

### From Any Version to Latest

```bash
# Universal installer (recommended)
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash

# Cargo
cargo install terraphim-agent --force
cargo install terraphim-cli --force
```

### Configuration Compatibility

Terraphim maintains backward compatibility for configuration files across minor versions. Major version bumps (e.g., 1.x to 2.0) may require configuration updates.

## Verify Your Installation

After installation or upgrade, verify your version:

```bash
terraphim-agent --version
terraphim-cli --version
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
