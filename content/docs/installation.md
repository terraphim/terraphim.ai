+++
title = "Installation"
description = "Install Terraphim AI on Linux, macOS, or Windows using your preferred method"
date = 2026-01-27
+++

# Installation

Choose the installation method that best suits your needs and platform.

## Quick Install (Recommended)

The universal installer detects your platform, resolves the current release
from the release channel, verifies the download's SHA-256, and unpacks it into
`~/.local/bin`.

```bash
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash
```

Options:

```bash
# Also install the CLI and grep tools
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash --with-cli --with-grep

# Install somewhere else
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash --install-dir /usr/local/bin

# Require a specific version (fails if the channel serves a different one)
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash --version 1.21.16
```

The installer publishes these exit codes: `0` success, `1` usage error,
`2` manifest unreachable, `3` requested version unavailable, `4` download
failed, `5` checksum mismatch, `6` installation failed.

## Package Managers

### Homebrew (macOS/Linux)

```bash
brew tap terraphim/terraphim && brew install terraphim-agent
```

The tap also carries `terraphim-grep`. There is no `terraphim-ai` formula.

### Cargo (Rust)

```bash
# Install agent with interactive REPL and full features
cargo install terraphim_agent --features repl-full
```

## Platform-Specific Guides

### Linux

#### Binary Download

Archives are served from `downloads.terraphim.ai`. Substitute the release you
want for `1.21.16`, or read the current version from the
[manifest](https://downloads.terraphim.ai/terraphim-agent/stable-v2.json).

```bash
VERSION=1.21.16

# x86_64 (GNU)
curl -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-${VERSION}-x86_64-unknown-linux-gnu.tar.gz"
tar -xzf "terraphim-agent-${VERSION}-x86_64-unknown-linux-gnu.tar.gz"
sudo mv terraphim-agent /usr/local/bin/

# x86_64 (MUSL / static)
curl -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-${VERSION}-x86_64-unknown-linux-musl.tar.gz"

# ARM64 (MUSL)
curl -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-${VERSION}-aarch64-unknown-linux-musl.tar.gz"
```

Verify the download against the digest in the manifest before installing:

```bash
curl -fsSL https://downloads.terraphim.ai/terraphim-agent/stable-v2.json \
  | python3 -c 'import json,sys; m=json.load(sys.stdin); print(m["version"]); print(m["assets"]["x86_64-unknown-linux-gnu"]["sha256"])'
sha256sum "terraphim-agent-${VERSION}-x86_64-unknown-linux-gnu.tar.gz"
```

#### Build from Source

```bash
git clone https://github.com/terraphim/terraphim-clients.git
cd terraphim-clients

cargo build --release -p terraphim_agent --bin terraphim-agent

sudo cp target/release/terraphim-agent /usr/local/bin/
```

### macOS

#### Binary Download

```bash
VERSION=1.21.16

# Apple Silicon (ARM64)
curl -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-${VERSION}-aarch64-apple-darwin.tar.gz"
tar -xzf "terraphim-agent-${VERSION}-aarch64-apple-darwin.tar.gz"
sudo mv terraphim-agent /usr/local/bin/

# Intel (x86_64)
curl -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-${VERSION}-x86_64-apple-darwin.tar.gz"

# Universal (runs on both)
curl -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-${VERSION}-universal-apple-darwin.tar.gz"
```

macOS builds are signed and notarised by Apple; the self-updater verifies an
Ed25519 signature over every archive before installing it.

#### Build from Source

Requires Xcode command line tools.

```bash
git clone https://github.com/terraphim/terraphim-clients.git
cd terraphim-clients
cargo build --release -p terraphim_agent --bin terraphim-agent
sudo cp target/release/terraphim-agent /usr/local/bin/
```

### Windows

#### Binary Download

```powershell
$VERSION = "1.21.16"
curl.exe -fsSLO "https://downloads.terraphim.ai/terraphim-agent/terraphim-agent-$VERSION-x86_64-pc-windows-msvc.zip"
```

Extract the zip and add the directory to your PATH.

#### Build from Source

Requires [Rust for Windows](https://rustup.rs/).

```powershell
git clone https://github.com/terraphim/terraphim-clients.git
cd terraphim-clients
cargo build --release -p terraphim_agent --bin terraphim-agent
# Binary will be in target\release\
```

## Server and Library Bindings

The commands above install the client tools (`terraphim-agent`,
`terraphim-grep`, `terraphim-cli`). The server and the language bindings have
their own release paths:

### Terraphim server

The server is built and released from
[terraphim-ai](https://github.com/terraphim/terraphim-ai). Build it from
source, or use the container images published to the GitHub Container
Registry.

### npm (Node.js / Bun)

The `@terraphim/autocomplete` package provides NAPI bindings for autocomplete and knowledge graph functions.

```bash
npm install @terraphim/autocomplete
```

### Python (PyPI)

The `terraphim-automata` package provides PyO3 bindings for text matching and autocomplete.

```bash
pip install terraphim-automata
```

### Browser Extensions

Two browser extensions are available for developer-mode installation:

- **Terraphim Sidebar** — knowledge graph search panel
- **Terraphim Autocomplete** — autocomplete suggestions in text fields

Install from source:

```bash
git clone https://github.com/terraphim/terraphim-ai.git
cd terraphim-ai/browser_extensions
```

Then load unpacked in Chrome at `chrome://extensions` (enable Developer Mode). Coming to the Chrome Web Store soon.

See [browser_extensions/INSTALL.md](https://github.com/terraphim/terraphim-ai/tree/main/browser_extensions) for detailed instructions.

## Verification

After installation, verify that Terraphim is working:

```bash
# Check version
terraphim-agent --version
# terraphim-agent 1.21.16

# Confirm the updater can see the channel
terraphim-agent check-update

# Start the REPL
terraphim-agent repl
```

## Troubleshooting

### Permission Denied

If you get a permission denied error, make the binary executable:

```bash
chmod +x /usr/local/bin/terraphim-agent
```

### Command Not Found

Ensure that the installation directory is in your PATH. The universal
installer adds `~/.local/bin` to your shell profile:

```bash
# For bash
echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.zshrc
source ~/.zshrc
```

### Checksum Mismatch

The installer exits with code `5` if the downloaded archive does not match the
digest in the release manifest. Re-run the install; if it fails again, please
open an issue rather than using `--skip-verify`.

### Rust Version Issues

Ensure that you have a recent Rust version:

```bash
rustc --version  # Should be 1.85.0 or later
rustup update stable
```

## Next Steps

- [Quickstart Guide](/docs/quickstart) — Get up and running in 5 minutes
- [Configuration Guide](/docs/terraphim_config) — Customise Terraphim to your needs
- [Discord Community](https://discord.gg/VPJXB6BGuY) — Join our Discord for support
- [Discourse Forum](https://terraphim.discourse.group) — Community discussions and Q&A