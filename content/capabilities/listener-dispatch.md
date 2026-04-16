+++
title = "Gitea Agent Dispatch"
description = "Execute terraphim-agent commands from Gitea issue mentions with multi-layer security"
date = 2026-04-16
weight = 12

[taxonomies]
categories = ["Capabilities"]
tags = ["gitea", "agent", "dispatch", "security", "automation"]

[extra]
toc = true
icon = "fa-solid fa-robot"
+++

The listener dispatch feature lets you run `terraphim-agent` subcommands by mentioning the
agent in a Gitea issue or comment. The result is posted back as a formatted markdown comment.

## Triggering a command

Mention the agent in a Gitea comment with a subcommand and arguments:

```
@adf:worker search "knowledge graph" --role engineer
@adf:worker evaluate --role engineer
@adf:worker learn list
```

The listener parses the text after `@adf:`, validates it through three security layers, runs
the command, and posts the output back to the same issue.

## Security

Three checks must all pass before the process is spawned:

**1. Shell metacharacter rejection** — Input containing `|`, `;`, `&`, `` ` ``, `$`, `(`,
`)`, `<`, or `>` is rejected immediately. No shell is involved in execution, but this
prevents confusion if the input is ever logged or replayed.

**2. Subcommand allowlist / denylist** — Only known safe subcommands are permitted.
Denied subcommands (`listen`, `repl`, `interactive`, `setup`, `update`, `sessions`)
are blocked even if added to `extra_allowed_subcommands`.

**3. CommandGuard** — A pattern-based guard runs on the full command string before
process spawn. It blocks destructive patterns such as `git reset --hard`.

## Configuration

Enable dispatch in your listener config JSON:

```json
{
  "identity": { "agent_name": "worker" },
  "gitea": {
    "base_url": "https://git.terraphim.cloud",
    "owner": "terraphim",
    "repo": "terraphim-ai"
  },
  "dispatch": {
    "timeout_secs": 300,
    "max_output_bytes": 48000,
    "specialist_routes": {
      "evaluate": "eval-bot"
    }
  }
}
```

`specialist_routes` routes specific subcommands to a named agent rather than running locally.

## Output

The comment posted back to Gitea includes the exit code, elapsed time, stdout in a code
block, and stderr in a collapsible section. Output is capped at 48 KB. Commands that exceed
5 minutes are killed and marked `**TIMED OUT**`.

The `--robot` flag is always appended, so output is machine-readable JSON regardless of the
user's default format.

Source: `crates/terraphim_agent/src/shell_dispatch.rs`, `crates/terraphim_agent/src/listener.rs`
