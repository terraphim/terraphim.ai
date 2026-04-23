+++
title="Building a Front-End Developer Agent with Knowledge Graphs and Code Search"
date=2026-04-23

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "walkthrough", "knowledge-graph", "grepapp", "Svelte", "SvelteKit", "TypeScript", "agent"]
[extra]
toc = true
comments = true
+++

We have published a comprehensive walkthrough showing how to build a specialised front-end developer agent using Terraphim's knowledge graph system, dual haystacks, and deterministic search. This post walks through the key concepts and links to the full guide.

<!-- more -->

## Why a Front-End Developer Agent?

Front-end development spans a vast surface area: CSS layout, accessibility, TypeScript types, Svelte reactivity, build tooling, performance, testing, and more. When you search for "how do I make this accessible?" or "what's the SvelteKit pattern for form validation?", you want answers that understand your domain -- not generic web search results.

Terraphim's deterministic knowledge graph approach means every search result is grounded in concepts you define, ranked by relevance, and fully reproducible. No hallucination, no non-deterministic LLM output.

## What the Agent Does

The front-end developer agent combines three capabilities:

1. **Knowledge Graph**: 18 concept files covering responsive design, accessibility, Svelte/SvelteKit patterns, TypeScript, CSS layout, state management, build tools, testing, performance, and more. Each concept has synonyms that resolve deterministically via Aho-Corasick matching.

2. **Local Search (Ripgrep)**: Searches your project files -- `.svelte`, `.ts`, `.css`, `.md` -- using the knowledge graph to boost conceptually relevant files.

3. **Global Code Search (GrepApp)**: Searches millions of public GitHub repositories for TypeScript code patterns via the grep.app API, filtered to TypeScript for modern front-end relevance.

Results from both haystacks are merged and ranked using TerraphimGraph, a hybrid scoring algorithm that combines knowledge graph concept matching with TF-IDF rescoring. In testing, a query for "svelte component" returned 13 results with TerraphimGraph versus 1 result with the simpler BM25Plus scorer. The 18 concept files with 358 synonyms actively influence ranking, not just display.

## The Knowledge Graph

Each concept is a Markdown file with a heading, description, and synonym list:

```markdown
# Svelte Patterns

Svelte-specific patterns for building reactive, compiled frontend
applications using runes, stores, and SvelteKit conventions.

synonyms:: Svelte, SvelteKit, rune, $state, $derived, $effect,
$props, bind, each block, await block, load function, +page.svelte
```

When you search for `$derived` or `+page.svelte`, the Aho-Corasick automaton matches it to the "Svelte Patterns" concept in O(n+m) time. The matching is case-insensitive and leftmost-longest, so "CSS grid" matches as one term rather than two separate words.

If no exact match exists, a TF-IDF fallback kicks in using `trigger::` directives for semantic similarity.

## Hybrid Scoring: Why TerraphimGraph

Terraphim offers multiple relevance functions. For a knowledge-graph-backed agent, `terraphim-graph` is strictly superior to the simpler `bm25plus`:

| Aspect | BM25Plus | TerraphimGraph |
|--------|----------|----------------|
| KG concepts affect ranking | No (display only) | Yes (graph + TF-IDF hybrid) |
| Term co-occurrence | Not used | Boosts related documents |
| KG link insertion | Disabled | Enabled in results |
| TF-IDF rescoring | Not applied | 30% weight boost |

TerraphimGraph uses a two-pass scoring system. Pass 1 builds a co-occurrence graph from Aho-Corasick matches and ranks documents by `total_rank = node_rank + edge_rank + document_rank`. Pass 2 applies TF-IDF rescoring at 30% weight. Documents containing co-occurring concepts (e.g., "svelte" + "component" + "state management") score higher than those matching only one term.

## Svelte and SvelteKit Focus

The knowledge graph is tuned for Svelte/SvelteKit development with TypeScript:

- **Svelte Patterns**: Runes (`$state`, `$derived`, `$effect`), stores, components, transitions
- **SvelteKit Routing**: `+page.svelte`, `+page.ts`, `+layout.svelte`, form actions, load functions
- **TypeScript**: Interfaces, generics, type guards, `satisfies` operator
- **CSS Custom Properties**: Design tokens, oklch colour values, dark mode theming
- **Forms and Validation**: SvelteKit form actions, zod schemas, superforms

The GrepApp haystack is filtered to `language: "typescript"` rather than JavaScript, reflecting the modern Svelte/SvelteKit ecosystem.

## Quick Start

```bash
# Build the agent
git clone https://github.com/terraphim/terraphim-ai.git
cd terraphim-ai
cargo build --release
# Enable GrepApp haystack support
cargo build --release -p terraphim_middleware --features grepapp
cargo install --path crates/terraphim_agent

# Set up the front-end developer role
terraphim-agent setup --template frontend-engineer --path ~/projects

# Search across local files and GitHub
terraphim-agent search "flexbox responsive layout"
```

## Architecture in Brief

```
Query: "flexbox responsive layout"
    |
    v
[Auto-route] -> Front-End Developer role
    |
    v
[Aho-Corasick] -> CSS Layout + Responsive Design concepts
    |
    v
[Ripgrep]       [GrepApp (TypeScript)]
    |                |
    v                v
[TerraphimGraph hybrid scoring:
  Pass 1: KG graph ranking (node + edge co-occurrence)
  Pass 2: TF-IDF rescoring (30% weight boost)]
              |
              v
      Ranked results
```

## MCP Integration with AI Coding Agents

The `terraphim_mcp_server` binary exposes all knowledge graph tools via the Model Context Protocol, so any MCP-compatible AI coding agent can use your front-end developer KG during coding sessions.

**opencode** (`~/.config/opencode/opencode.json`):

```json
{
  "mcp": {
    "terraphim": {
      "type": "local",
      "command": ["~/.cargo/bin/terraphim_mcp_server"],
      "environment": { "TERRAPHIM_DATA_PATH": "~/.terraphim" }
    }
  }
}
```

**Claude Code** (`~/.claude.json`):

```json
{
  "mcpServers": {
    "terraphim": {
      "type": "stdio",
      "command": "~/.cargo/bin/terraphim_mcp_server",
      "env": { "RUST_LOG": "error" }
    }
  }
}
```

After configuration, the AI agent gains access to 18 MCP tools: `search`, `autocomplete_terms`, `replace_matches`, `terraphim_find_files`, `terraphim_grep`, and more. Queries auto-route to the Front-End Developer role when front-end terms are detected.

For Cursor, Windsurf, or any HTTP-based MCP client, start the SSE server: `terraphim_mcp_server --sse --bind 127.0.0.1:8000`.

## Read the Full Walkthrough

The complete step-by-step guide covers:

- Building terraphim-agent with GrepApp support
- Understanding the knowledge graph architecture
- Creating 18 front-end concept files
- Configuring the role with dual haystacks
- Using search, autocomplete, replace, and validate commands
- Integrating with opencode and Claude Code via MCP
- Adding new concepts to the knowledge graph
- Troubleshooting common issues

Read it at: [`docs/walkthroughs/frontend-developer-agent.md`](https://github.com/terraphim/terraphim-ai/blob/main/docs/walkthroughs/frontend-developer-agent.md)

## What Comes Next

This walkthrough demonstrates the deterministic, KG-first approach. Natural extensions include:

- **LLM chat**: Enable Ollama for conversational search over the same knowledge graph
- **MCP server**: Expose the agent to Claude Code or Cursor via Model Context Protocol
- **More roles**: The same pattern applies to any domain -- React specialists, DevOps engineers, data scientists

The knowledge graph pattern is universal: define concepts, add synonyms, point at haystacks, and search. No training, no fine-tuning, no API keys for the deterministic path.
