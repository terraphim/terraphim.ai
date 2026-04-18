+++
title="Plug Terraphim Search into Claude Code and opencode (CLI First, MCP When You Need It)"
date=2026-04-18

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "claude-code", "opencode", "mcp", "knowledge-graph", "developer-tools", "integration"]

[extra]
toc = true
comments = true
+++

Your AI coding agent already has a knowledge graph. It is just not yours yet. The model knows GitHub, Stack Overflow, and the public training corpus -- it has no idea that in your project `npm` should be `bun`, that `RFP` is shorthand for `acquisition need`, or that the email about the Stripe receipt for the Obsidian licence lives in your Fastmail mailbox. This post shows the smallest path to fixing that for both [Claude Code](https://claude.com/claude-code) and [opencode](https://opencode.ai), using [Terraphim](https://terraphim.ai) and the three roles we have published over the last week (Terraphim Engineer, [Personal Assistant](/posts/personal-assistant-role-jmap-obsidian/), [System Operator](/posts/system-operator-logseq-knowledge-graph/)).

Two paths. CLI first.

<!-- more -->

## What "integrate" means here

The host -- Claude Code or opencode -- needs a way to ask your role-aware Terraphim setup a question and get back ranked, source-attributed results. The model decides when to ask. The role decides which haystacks to search. Terraphim's `terraphim-graph` ranker decides which results come back first.

Concrete example. You are working in opencode and you type:

```
/tsearch "System Operator" RFP
```

The slash command runs against the System Operator role. The role's knowledge graph normalises `RFP` to its INCOSE-canonical form `acquisition need`. The Aho-Corasick matcher walks the role's haystack (1,347 Logseq pages from the [terraphim/system-operator](https://github.com/terraphim/system-operator) repository). The top hit comes back ranked 13 -- `Acquisition need.md` -- with the `synonyms::` line that mapped your query to it visible in the snippet. The model now has the right page in its context window and can answer your follow-up without a hallucinated INCOSE handbook reference.

This works in both hosts because both speak the same two integration languages: shell-out slash commands and MCP servers. We are going to use both.

## Path A -- CLI via slash command

### Why this is the recommended starting point

`terraphim-agent` already exists, takes `--role` and `--limit`, and writes ranked results to stdout. There is nothing to build. Both Claude Code and opencode let slash commands shell out via Bash. So a two-line command file is the entire integration.

### One file, two hosts

Drop this at `~/.claude/commands/tsearch.md` (and an identical copy at `~/.config/opencode/command/tsearch.md` -- both hosts read the same frontmatter shape):

```markdown
---
description: Terraphim search across configured roles. Usage: /tsearch [role] <query>
allowed-tools: Bash(terraphim-agent search:*), Bash(terraphim-agent-pa search:*)
---
Run `terraphim-agent search --role "<role>" --limit 5 "<query>"` (or
`terraphim-agent-pa search ...` if the role is "Personal Assistant" and
the query needs the JMAP haystack). Return the top results as a numbered
list with title, source path/URL, and a 120-char snippet.
```

That is it. The `allowed-tools` line auto-approves the two CLI invocations so the model does not have to ask permission per call. Restart the host (or reload commands) and `/tsearch` is live.

### Why fast enough

`terraphim-agent` reads its persisted role state at start (low milliseconds), runs the query against the role's haystacks, and returns. For a typical knowledge-graph query against the Terraphim Engineer role on a laptop, the round trip from slash command to formatted output is well under a second. The agent already has the typed CLI -- `--role`, `--limit`, `--format json` -- so there is nothing the MCP layer adds for the search-only flow.

### Three example queries

```
/tsearch "Terraphim Engineer" rolegraph
/tsearch "System Operator" RFP
/tsearch "Personal Assistant" invoice    # uses terraphim-agent-pa wrapper for JMAP
```

The Personal Assistant case is the most interesting because it crosses surfaces -- Obsidian notes interleave with `jmap:///email/<id>` URLs from your Fastmail mailbox, ranked by the same `terraphim-graph` scoring. The wrapper script injects `JMAP_ACCESS_TOKEN` from 1Password at call time so the secret never lands on disk; the bare `terraphim-agent` continues to work for the other five roles without paying the unlock cost.

## Path B -- MCP server (when you want typed tools)

The CLI path is enough for search. If you want the model to call `search` as a first-class tool with structured JSON parameters -- alongside `autocomplete_terms`, `autocomplete_with_snippets`, four flavours of fuzzy autocomplete, `build_autocomplete_index`, and `update_config_tool` -- that is what `terraphim_mcp_server` exposes. It reads the same `~/.config/terraphim/embedded_config.json`, so the role list is identical.

### Build and install

```bash
cd ~/projects/terraphim/terraphim-ai
cargo build --release -p terraphim_mcp_server --features jmap
cp target/release/terraphim_mcp_server ~/.cargo/bin/terraphim_mcp_server
```

For the Personal Assistant role, mirror the existing `terraphim-agent-pa` wrapper at `~/bin/terraphim_mcp_server-pa` so the JMAP token flows through `op run` instead of being baked into config.

### Register

opencode -- add to `~/.config/opencode/opencode.json` under `mcp`:

```jsonc
"terraphim":    { "type": "local", "command": ["/Users/alex/.cargo/bin/terraphim_mcp_server"] },
"terraphim-pa": { "type": "local", "command": ["/Users/alex/bin/terraphim_mcp_server-pa"] }
```

Claude Code -- one shell command per server:

```bash
claude mcp add terraphim    /Users/alex/.cargo/bin/terraphim_mcp_server
claude mcp add terraphim-pa /Users/alex/bin/terraphim_mcp_server-pa
claude mcp list      # both should show as Connected
```

The model now sees `mcp__terraphim__search` and `mcp__terraphim_pa__search` (plus the autocomplete tools) in its tool list.

## SessionStart primer (both paths)

Slash commands and MCP tools are useless if the model does not know the roles exist. Extend the SessionStart hook in `~/.claude/settings.json` to print a one-screen role index when each session starts:

```bash
printf '\n--- Terraphim search via /tsearch [role] <query> ---\n'
printf '  Terraphim Engineer  (Rust/agent KG)\n'
printf '  Personal Assistant  (Obsidian + Fastmail JMAP, use terraphim-agent-pa for email)\n'
printf '  System Operator     (INCOSE/MBSE Logseq KG)\n'
printf '  Context Engineering Author, Rust Engineer, Default\n'
```

Equivalent hook in opencode. Cost: one screen of context per session. Benefit: the model picks the right role on the first try instead of guessing.

## When to pick which path

| | CLI (Path A) | MCP (Path B) |
| --- | --- | --- |
| New binaries | None | `terraphim_mcp_server` plus wrapper |
| Cold start | ~50-200 ms per call | ~10-50 ms per call (long-lived process) |
| Tools exposed | `search` only | `search` + 4 autocomplete + `build_autocomplete_index` + `update_config_tool` |
| Works in any host | Yes -- anything that runs a slash command | Only hosts that speak MCP |
| Token handling | `terraphim-agent-pa` wrapper | `terraphim_mcp_server-pa` wrapper |

For the search-across-roles flow, CLI is enough. Add MCP when the model needs autocomplete-as-you-type, when you want it to manage role configuration without leaving the conversation, or when you are using a host where the typed-tool surface matters more than the cold-start cost.

You do not have to choose. Wire both. The slash command above defaults to CLI and falls back to MCP if the binary is missing -- the two paths coexist cleanly because they read the same role config.

## Why this is the right shape

Most "AI assistant + knowledge base" integrations end up tightly coupled to a specific host. Vendor X's plugin marketplace, Vendor Y's tool format. Terraphim takes the opposite stance: the role configuration lives in your filesystem, the haystacks live in your filesystem (or your mailbox), the ranker runs in a process you own, and the integration with the AI host is the thinnest possible shim -- a slash command or an MCP server, both of which are commodity surfaces.

Yesterday the Personal Assistant role was a private setup on one laptop. Today it is callable from inside two different AI coding hosts via a one-file slash command. Tomorrow you can add Cursor or Aider with the same two-line wrapper because the integration surface is `terraphim-agent search`, not `vendor-specific-tool-protocol-v3`.

The expensive part of context engineering is not the ranker. It is the vocabulary in the knowledge graph and the haystacks the role can reach. The integration layer should not be allowed to compete for that budget. CLI-first keeps it small.

## Try it

```bash
# Build (or install the published crate when JMAP feature lands on crates.io)
cd ~/projects/terraphim/terraphim-ai
cargo install --path crates/terraphim_agent --features jmap

# Configure roles -- copy the snippets from the how-tos linked below
$EDITOR ~/.config/terraphim/embedded_config.json

# Install the slash command
mkdir -p ~/.claude/commands ~/.config/opencode/command
cp ~/projects/terraphim/terraphim-ai/docs/src/howto/mcp-integration-claude-opencode.md \
   /tmp/tsearch.md  # adapt to your slash command file shape

# Reload roles
terraphim-agent config reload

# Try
terraphim-agent search --role "Terraphim Engineer" --limit 3 "rolegraph"
```

Step-by-step in the docs: [Plug Terraphim Search into Claude Code and opencode](https://docs.terraphim.ai/howto/mcp-integration-claude-opencode.html).

For the underlying engine, start with [Why Graph Embeddings Matter](/posts/why-graph-embeddings-matter/). For the two roles this integration most cleanly exposes, see [Personal Assistant](/posts/personal-assistant-role-jmap-obsidian/) and [System Operator](/posts/system-operator-logseq-knowledge-graph/).
