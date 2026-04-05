+++
title="Teaching AI Agents to Learn from Their Mistakes"
date=2026-04-05

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "ai", "learning", "hooks", "knowledge-graph", "claude-code", "developer-tools"]
[extra]
toc = true
comments = true
+++

AI coding agents make the same mistakes over and over. We built a learning system that captures failures, stores corrections, and feeds them back into future sessions -- turning every error into institutional memory.

<!-- more -->

## The Problem: Groundhog Day for AI Agents

Every AI coding agent session starts from zero. Claude Code runs `npm install`, gets corrected, switches to `bun` -- and tomorrow does it again. A force-push to main gets blocked, the agent learns why, then forgets by next session.

In our previous post on [Knowledge Graph Hooks](/posts/teaching-ai-agents-with-knowledge-graphs/), we showed how Aho-Corasick automata can intercept and transform agent commands in real time. But interception is reactive. What if the agent could *remember* its past failures and avoid repeating them?

## The Solution: Terraphim Learning Capture

Terraphim's learning system operates as a closed loop with three stages:

```
Failed Command --> PostToolUse Hook --> Learning Store --> Query at Session Start
```

### Stage 1: Automatic Capture

A PostToolUse hook fires after every tool execution in Claude Code. When a command exits with a non-zero status, the hook calls `terraphim-agent learn hook`, which persists the failure as a structured markdown file:

```yaml
---
id: 6b99a8924fad4f2aaeadf5450e76730c
command: npm install react
exit_code: 127
source: Global
captured_at: 2026-04-04T18:43:07+00:00
---
```

The hook is fail-open -- if `terraphim-agent` is unavailable, it exits silently. Development is never blocked.

### Stage 2: Human Corrections

Raw failures are useful, but corrections make them actionable. Any developer (or the agent itself) can attach a correction:

```bash
$ terraphim-agent learn correct <id> --correction "Use 'bun add react' instead"
```

The learning file is updated in place:

```yaml
---
id: 6b99a8924fad4f2aaeadf5450e76730c
command: npm install react
exit_code: 127
correction: "Use 'bun add react' instead"
---
```

### Stage 3: Query Before Repeating

At the start of a session, or when encountering a familiar error, the agent queries the learning store:

```bash
$ terraphim-agent learn query "npm"

Learnings matching 'npm'.
  [G] [cmd] npm install lodash (exit: 1)
     Correction: Use 'bun add lodash' instead. Terraphim hooks enforce bun over npm.
  [G] [cmd] npm install react (exit: 127)
     Correction: Use bun instead of npm/yarn/pnpm. 'bun add react' or 'bun install'.
```

The agent sees past mistakes with their corrections before taking action. No more Groundhog Day.

## How the Hook Works

The PostToolUse hook is a shell script that receives JSON from Claude Code on stdin after every Bash tool call:

```bash
#!/bin/bash
set -euo pipefail

# Find terraphim-agent binary
AGENT="$HOME/.cargo/bin/terraphim-agent"
[ -x "$AGENT" ] || exit 0  # Fail-open

# Read tool result from stdin
INPUT=$(cat)

# Capture failures as learnings
$AGENT learn hook --format claude <<< "$INPUT" 2>/dev/null || true
```

The `learn hook` subcommand parses the Claude Code tool result format, extracts the command and exit code, and writes a learning file only when the exit code is non-zero.

### What Gets Captured

| Signal | Captured? | Example |
|--------|-----------|---------|
| Non-zero exit code | Yes | `npm install` (exit 127) |
| Force push attempts | Yes | `git push --force origin main` (exit 1) |
| Compilation errors | Yes | `cargo build` (exit 101) |
| Successful commands | No | Only failures are stored |
| Duplicate failures | Deduplicated | Same command + exit code within a session |

## Real Evidence: What Our Agents Have Learnt

Here is actual data from our production learning store, accumulated across weeks of development sessions:

**Package manager enforcement** -- 3 npm entries, all corrected to bun:
```
[G] [cmd] npm install lodash (exit: 1)
   Correction: Use 'bun add lodash' instead.
[G] [cmd] npm install react (exit: 127)
   Correction: Use bun instead of npm/yarn/pnpm.
```

**Git safety** -- 29 push failures captured, including one critical correction:
```
[G] [cmd] git push --force origin main (exit: 1)
   Correction: NEVER force push to main. Use feature branches and PRs.
```

These corrections are not just documentation. They are queryable institutional memory that agents consult before repeating the same mistakes.

## Integration with Knowledge Graph Hooks

The learning system complements the [Knowledge Graph Hooks](/posts/teaching-ai-agents-with-knowledge-graphs/) we described previously. Together they form two layers of defence:

| Layer | Mechanism | Timing |
|-------|-----------|--------|
| **Prevention** | KG hooks intercept `npm install` and replace with `bun install` | Before execution |
| **Learning** | PostToolUse hook captures failures that slip through | After execution |

If a new pattern appears that the knowledge graph does not cover, the learning system captures it. A developer adds a correction. Optionally, the pattern gets promoted to a knowledge graph entry for permanent interception.

```
New failure captured --> Correction added --> Pattern promoted to KG --> Hook intercepts automatically
```

## The Learning Store

Learning files are stored as markdown in `~/Library/Application Support/terraphim/learnings/` (macOS) or `~/.local/share/terraphim/learnings/` (Linux). Each file is a standalone document:

```markdown
---
id: 1c8a4548-1434-a346-cd641131202a
command: git push --force origin main
exit_code: 1
source: Global
captured_at: 2026-04-02T15:31:20+00:00
correction: NEVER force push to main. Use feature branches and PRs.
---

## Command

`git push --force origin main`

## Error Output

```
rejected
```

## Suggested Correction

`NEVER force push to main. Use feature branches and PRs.`
```

Being plain markdown, these files are:
- **Human-readable** -- developers can browse and edit directly
- **Version-controllable** -- share learnings across a team via git
- **Portable** -- copy between machines or agents

## CLI Reference

```bash
# List recent learnings
terraphim-agent learn list

# Query by pattern (full-text search)
terraphim-agent learn query "pattern"

# Add correction to a learning
terraphim-agent learn correct <id> --correction "what to do instead"

# Hook mode (called by PostToolUse, reads JSON from stdin)
terraphim-agent learn hook --format claude
```

## Setting It Up

### 1. Install the PostToolUse hook

Create `~/.claude/hooks/post_tool_use.sh`:

```bash
#!/bin/bash
set -euo pipefail
AGENT="$HOME/.cargo/bin/terraphim-agent"
[ -x "$AGENT" ] || exit 0
INPUT=$(cat)
$AGENT learn hook --format claude <<< "$INPUT" 2>/dev/null || true
```

### 2. Register in Claude Code settings

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/post_tool_use.sh"
      }]
    }]
  }
}
```

### 3. Start using it

Failed commands are captured automatically. Query them with `terraphim-agent learn query`.

## What Comes Next

The learning system is the foundation for richer agent memory:

- **Cross-agent sharing** -- learnings from one agent become available to all agents on the team
- **Automatic promotion** -- when a correction appears N times, auto-generate a KG entry
- **Session search integration** -- `terraphim-agent sessions search` already indexes learnings alongside session transcripts
- **Confidence scoring** -- weight corrections by frequency and recency

The goal is not to make agents perfect on the first try. It is to make them incapable of making the same mistake twice.

## Conclusion

AI coding agents are powerful but amnesiac. Every session starts fresh, every mistake is rediscovered. Terraphim's learning capture system closes this gap with a simple, fail-open hook that turns failures into institutional memory.

The pattern is straightforward: capture failures automatically, attach corrections manually, query before acting. No training required, no model fine-tuning, no prompt engineering beyond what you already do.

Your agents will still make mistakes. They just will not make the *same* mistakes.

## Resources

- [Terraphim AI Repository](https://github.com/terraphim/terraphim-ai)
- [Knowledge Graph Hooks Post](/posts/teaching-ai-agents-with-knowledge-graphs/)
- [Claude Code Skills Plugin](https://github.com/terraphim/terraphim-claude-skills)
- [Hook Installation Guide](https://docs.terraphim.ai/hooks/)
