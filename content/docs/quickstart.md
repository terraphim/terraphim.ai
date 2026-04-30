+++
title = "Quickstart"
description = "Get started with Terraphim AI in 5 minutes"
date = 2026-01-27
updated = 2026-05-01

[extra]
toc = true
+++

# Quickstart Guide

Get up and running with Terraphim AI in just 5 minutes. The agent works offline by default -- no server required.

## Step 1: Install

Choose your preferred installation method:

### Option A: Universal Installer (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/terraphim/terraphim-ai/main/scripts/install.sh | bash
```

### Option B: Homebrew (macOS/Linux)

```bash
brew tap terraphim/terraphim && brew install terraphim-ai
```

### Option C: Cargo

```bash
cargo install terraphim_agent --features repl-full
```

[More installation options](/docs/installation)

## Step 2: Launch the REPL

```bash
terraphim-agent repl
```

You will see:

```
============================================================
Terraphim TUI REPL
============================================================
Type /help for help, /quit to exit
Mode: Offline Mode | Current Role: AI Engineer

AI Engineer>
```

The REPL runs offline by default. No server or network connection required.

## Step 3: First Search

Search your knowledge graph:

```
AI Engineer> /search knowledge graph
```

Results are displayed in a ranked table with title and file path.

## Step 4: Explore REPL Commands

Here are the most useful commands to get started:

| Command | Description |
|---------|-------------|
| `/search "query"` | Search knowledge graph with role context |
| `/autocomplete "query"` | Autocomplete terms from the thesaurus |
| `/extract "text"` | Extract matching paragraphs |
| `/find "text"` | Find exact matches in indexed documents |
| `/replace "text"` | Replace matches using thesaurus mappings |
| `/thesaurus` | Show loaded thesaurus entries |
| `/graph` | Visualise knowledge graph (ASCII) |
| `/role list` | List available roles |
| `/role select <name>` | Switch to a different role |
| `/config show` | Display current configuration |
| `/help` | Show all available commands |
| `/quit` | Exit the REPL |

## CLI Subcommands

For scripting and automation, use subcommands directly:

```bash
# Search from the command line
terraphim-agent search "knowledge graph" --limit 5

# List roles
terraphim-agent roles list

# Show configuration
terraphim-agent config show

# Visualise knowledge graph (ASCII)
terraphim-agent graph --top-k 10
```

## Session Search

Import and search your AI coding assistant history (Claude Code, Cursor, Aider):

```bash
# Check available sources
terraphim-agent sessions sources

# Import sessions
terraphim-agent sessions import

# Search across sessions
terraphim-agent sessions search "rust async error"
```

## Learning Capture

Terraphim captures failed commands and their corrections for future reference:

```bash
# List captured learnings
terraphim-agent learn list

# Query by pattern
terraphim-agent learn query "npm"

# Compile corrections into a thesaurus
terraphim-agent learn compile
```

See the blog post [Teaching AI Agents to Learn from Their Mistakes](/posts/teaching-ai-agents-to-learn-from-mistakes) for a worked example.

## Onboarding Wizard

On first run, the interactive wizard helps you configure:

1. **Role selection** -- choose a role (AI Engineer, Log Analyst, etc.)
2. **Haystack path** -- where your documents live
3. **Knowledge graph** -- remote automata or local markdown files
4. **LLM provider** -- Ollama (local) or OpenRouter (cloud)

You can re-run the wizard at any time with `terraphim-agent onboard`.

## Next Steps

- [Installation Guide](/docs/installation) -- More installation options and troubleshooting
- [Configuration Guide](/docs/terraphim_config) -- Customise Terraphim to your needs
- [Contribution Guide](/docs/contribution) -- Contribute to Terraphim development
- [Discord Community](https://discord.gg/VPJXB6BGuY) -- Join our Discord for support
- [Discourse Forum](https://terraphim.discourse.group) -- Community discussions and Q&A

## Getting Help

If you run into issues:

1. Search existing [GitHub issues](https://github.com/terraphim/terraphim-ai/issues)
2. [Create a new issue](https://github.com/terraphim/terraphim-ai/issues/new)
3. Join [Discord community](https://discord.gg/VPJXB6BGuY) for support
4. Visit [Discourse forum](https://terraphim.discourse.group) for discussions
