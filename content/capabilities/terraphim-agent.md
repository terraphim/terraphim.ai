+++
title = "terraphim-agent CLI"
description = "Search-first AI agent with knowledge-graph context, session memory, and failure capture"
date = 2026-04-15
weight = 10

[taxonomies]
categories = ["Capability"]
tags = ["agent", "cli", "ai-agents", "learning"]

[extra]
toc = true
+++

`terraphim-agent` is a command-line AI agent that searches before it answers. It runs
local knowledge graph queries, imports session history from Claude Code and Cursor,
captures failed commands via post-tool-use hooks, and surfaces past corrections when
you encounter a recurring error.

Install it with one command:

```bash
cargo install terraphim-agent
```

## What it does

- **Session search**: query across imported Claude Code and Cursor session logs.
- **Knowledge-graph search**: match queries against role-configured Aho-Corasick automata.
- **Learning capture**: the `learn` subcommand records failed commands and their corrections.
- **Command rewriting**: pre-tool-use hooks rewrite `npm install` to `bun add`,
  `pip install` to `uv add`, etc. via a thesaurus.

See the [command rewriting how-to](/how-tos/command-rewriting-howto) and the blog post
[Teaching AI Agents to Learn from Their Mistakes](/posts/teaching-ai-agents-to-learn-from-mistakes)
for worked examples.
