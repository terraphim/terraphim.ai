+++
title = "Installation"
description = "Install Terraphim AI on Linux, macOS, or Windows using your preferred method"
date = 2026-01-27
+++

# Installation

Choose the installation method that best suits your needs and platform.

## Quick Install (Recommended)

The universal installer automatically detects your platform and installs the appropriate version.

```bash
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash
```

## Package Managers

### Homebrew (macOS/Linux)

```bash
brew tap terraphim/terraphim && brew install terraphim-ai
```

This installs `terraphim-agent`, `terraphim-cli`, and `terraphim_server`.

### Cargo (Rust)

Install using Cargo, Rust's package manager.

```bash
# Install agent with interactive TUI
cargo install terraphim-agent

# Install CLI for automation
cargo install terraphim-cli
```

### Debian/Ubuntu

Download the `.deb` package from the latest release:

```bash
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent_1.16.31-1_amd64.deb
sudo dpkg -i terraphim-agent_1.16.31-1_amd64.deb
```

## Platform-Specific Guides

### Linux

#### Binary Download

Download the latest release from GitHub:

```bash
# x86_64 (GNU)
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent-1.16.31-x86_64-unknown-linux-gnu.tar.gz
tar -xzf terraphim-agent-1.16.31-x86_64-unknown-linux-gnu.tar.gz
sudo mv terraphim-agent terraphim-cli terraphim_server /usr/local/bin/

# x86_64 (MUSL / static)
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent-1.16.31-x86_64-unknown-linux-musl.tar.gz

# ARM64 (MUSL)
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent-1.16.31-aarch64-unknown-linux-musl.tar.gz

# ARMv7 (MUSL)
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent-1.16.31-armv7-unknown-linux-musleabihf.tar.gz
```

#### Build from Source

```bash
# Clone the repository
git clone https://github.com/terraphim/terraphim-ai.git
cd terraphim-ai

# Build all binaries
cargo build --release

# Install
sudo cp target/release/terraphim_server /usr/local/bin/
sudo cp target/release/terraphim-agent /usr/local/bin/
sudo cp target/release/terraphim-cli /usr/local/bin/
```

### macOS

#### Binary Download

```bash
# Apple Silicon (ARM64)
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent-1.16.31-aarch64-apple-darwin.tar.gz
tar -xzf terraphim-agent-1.16.31-aarch64-apple-darwin.tar.gz
sudo mv terraphim-agent terraphim-cli terraphim_server /usr/local/bin/

# Intel (x86_64)
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent-1.16.31-x86_64-apple-darwin.tar.gz

# Universal (Fat binary)
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent-1.16.31-universal-apple-darwin.tar.gz
```

#### Build from Source

Requires Xcode command line tools.

```bash
git clone https://github.com/terraphim/terraphim-ai.git
cd terraphim-ai
cargo build --release
sudo cp target/release/terraphim_server /usr/local/bin/
sudo cp target/release/terraphim-agent /usr/local/bin/
sudo cp target/release/terraphim-cli /usr/local/bin/
```

### Windows

#### Binary Download

```powershell
# Download and extract
curl -LO https://github.com/terraphim/terraphim-ai/releases/latest/download/terraphim-agent-1.16.31-x86_64-pc-windows-msvc.zip
```

Extract the zip and add the directory to your PATH.

- [Download for Windows x64](https://github.com/terraphim/terraphim-ai/releases/latest)

#### Build from Source

Requires [Rust for Windows](https://rustup.rs/).

```powershell
git clone https://github.com/terraphim/terraphim-ai.git
cd terraphim-ai
cargo build --release
# Binaries will be in target\release\
```

## Library Bindings

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

- **Terraphim Sidebar** -- knowledge graph search panel
- **Terraphim Autocomplete** -- autocomplete suggestions in text fields

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
# terraphim-agent 1.16.31

terraphim-cli --version
# terraphim-cli 1.16.31

# Start the server
terraphim_server

# In another terminal, use the agent
terraphim-agent
```

## Troubleshooting

### Permission Denied

If you get a permission denied error, make the binary executable:

```bash
chmod +x /usr/local/bin/terraphim_server
chmod +x /usr/local/bin/terraphim-agent
chmod +x /usr/local/bin/terraphim-cli
```

### Command Not Found

Ensure that the installation directory is in your PATH:

```bash
# For bash
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.zshrc
source ~/.zshrc
```

### Rust Version Issues

Ensure that you have a recent Rust version:

```bash
rustc --version  # Should be 1.75.0 or later
rustup update stable
```

## Next Steps

- [Quickstart Guide](/docs/quickstart) -- Get up and running in 5 minutes
- [Configuration Guide](/docs/terraphim_config) -- Customise Terraphim to your needs
- [Discord Community](https://discord.gg/VPJXB6BGuY) -- Join our Discord for support
- [Discourse Forum](https://terraphim.discourse.group) -- Community discussions and Q&A
