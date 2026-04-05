+++
title = "Hooks System"
description = "Pre and post tool-use hooks for AI coding assistants -- capture failures, inject knowledge, automate learning"
date = 2026-04-05
weight = 5

[taxonomies]
categories = ["Capabilities"]
tags = ["hooks", "ai-assistant", "learning", "security", "claude-code"]

[extra]
toc = true
waypoint = "WP-005"
icon = "fa-solid fa-code-branch"
+++

## Two-Stage Runtime Validation

Terraphim implements a **two-stage runtime validation system** for AI-assisted development workflows. Every tool execution and LLM generation passes through hooks that provide both safety and intelligence enhancement.

### Stage 1: Guard Stage

The guard stage prevents dangerous operations before any processing occurs:

- **Blocks** bypass flags like `--no-verify` in git operations
- **Validates** commands against security patterns (injection prevention, resource limits)
- **Logs** all decisions with reasons for audit trails

### Stage 2: Replacement Stage

The replacement stage enhances text using knowledge graph patterns:

- **Applies** role-based knowledge graph replacements to commands and text
- **Validates** semantic connectivity and coherence
- **Transforms** using thesaurus and autocomplete for terminology consistency

## Learning from Mistakes

Failed commands are automatically captured by post-tool-use hooks. When a bash command fails, Terraphim records the failure for later review. Over time, you build a searchable history of what went wrong and how it was corrected.

```bash
# Review captured learnings
terraphim-agent learn list

# Query by pattern
terraphim-agent learn query "npm"

# Add a correction
terraphim-agent learn correct <id> "use bun instead"
```

This turns individual debugging sessions into institutional knowledge that persists across conversations and team members.

## Hook Types

Terraphim supports hooks at four points in the AI workflow:

| Hook | Purpose |
|------|---------|
| **Pre-LLM** | Validate prompts before generation; block, modify, or require human confirmation |
| **Post-LLM** | Validate responses; catch harmful content, enforce formatting |
| **Pre-Tool** | Validate commands before execution; security checks, injection prevention |
| **Post-Tool** | Monitor results; track performance, capture failures for learning |

## Configuration

Hooks are configured via TOML and environment variables, with sensible defaults:

- **Fail-open in development** -- hooks that crash do not block your work
- **Fail-closed in production** -- strict validation when it matters
- **Configurable timeouts** -- hooks that take too long are bypassed gracefully

## Deep Dives

- [Teaching AI Coding Agents with Knowledge Graph Hooks](/posts/teaching-ai-agents-with-knowledge-graphs/) -- How Aho-Corasick automata intercept and transform AI agent commands
- [Teaching AI Agents to Learn from Their Mistakes](/posts/teaching-ai-agents-to-learn-from-mistakes/) -- Turning agent failures into institutional memory
- [MCP Server Integration](/capabilities/mcp-server/)
