+++
title="Guarding OpenCode with Destructive Command Guard"
date=2026-04-17

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "ai", "opencode", "developer-tools", "rust", "safety", "coding-agents"]
[extra]
toc = true
comments = true
+++

AI coding assistants are fast, productive, and occasionally catastrophic. One misplaced `rm -rf`, one accidental `git reset --hard`, and hours of uncommitted work vanish.

Jeffrey Emanuel ([@Dicklesworthstone](https://github.com/Dicklesworthstone)) built [Destructive Command Guard (dcg)](https://github.com/Dicklesworthstone/destructive_command_guard): a Rust binary with SIMD-accelerated pattern matching, 49+ security packs, and a fail-open design. It is one of the best tools to come out of the AI agent safety space, and it solved a problem we had been fighting with regex hacks.

This post shows how we integrated dcg with [OpenCode](https://opencode.ai) using its plugin hook system, so destructive commands are intercepted *before* they run.

<!-- more -->

## The Problem

AI agents do not type commands into a terminal. They invoke tools programmatically, and they do not always get it right:

- "Cleaning up build artifacts" becomes `rm -rf ./src` (one-character typo)
- "Resetting to last commit" becomes `git reset --hard` (uncommitted work gone)
- "Force pushing the fix" becomes `git push --force` (team history destroyed)

You need a safety net that operates between the agent and your shell.

## The Architecture

OpenCode v1.4+ exposes a plugin hook system. Hooks are top-level keys on the `Hooks` interface:

```ts
interface Hooks {
  "tool.execute.before"?: (input, output) => Promise<void>;
  "tool.execute.after"?:  (input, output) => Promise<void>;
}
```

The `"tool.execute.before"` hook fires before every tool call. It receives the tool name and arguments, and can throw an error to abort execution. This is exactly where a command guard belongs.

DCG is Jeffrey's Rust binary that reads a JSON payload from stdin and exits `0` (allow) or `2` (block). Our contribution was the plugin that wires dcg into OpenCode's hook system:

```
OpenCode agent
    |
    | calls bash tool: "rm -rf ./build"
    v
"tool.execute.before" hook
    |
    | spawns: echo '{"tool":"bash","args":{"command":"rm -rf ./build"}}' | dcg
    v
dcg (Rust, SIMD-accelerated pattern matching)
    |
    | exit code 2 + reason on stderr
    v
hook throws Error --> command never executes
```

## The Plugin

The complete plugin is roughly 60 lines:

```javascript
import { spawn } from 'child_process';

const callDcgHook = (toolCall) => {
  return new Promise((resolve, reject) => {
    const dcg = spawn('dcg', [], {
      env: { ...process.env, DCG_FORMAT: 'json' }
    });

    let stdout = '';
    let stderr = '';

    dcg.stdout.on('data', (data) => { stdout += data.toString(); });
    dcg.stderr.on('data', (data) => { stderr += data.toString(); });

    dcg.on('close', (code) => {
      if (code === 0) {
        try { resolve(JSON.parse(stdout)); }
        catch { resolve({ allowed: true }); }
      } else {
        reject(new Error(stderr || 'dcg blocked command'));
      }
    });

    dcg.stdin.write(JSON.stringify(toolCall));
    dcg.stdin.end();
  });
};

export const DcgGuard = async ({ client }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== 'bash') return;

      const toolCall = {
        tool: 'bash',
        args: { command: output.args.command }
      };

      try {
        await callDcgHook(toolCall);
      } catch (error) {
        throw new Error(
          `dcg blocked destructive command: ${output.args.command}\n\n` +
          `${error.message}\n\n` +
          `This command was blocked to protect your system.`
        );
      }
    }
  };
};
```

## What Got Fixed: A Subtle API Mismatch

The original plugin used a nested structure:

```javascript
return {
  tool: {
    execute: {
      before: async (input, output) => { ... }
    }
  }
};
```

This looks intuitive but is wrong. In OpenCode's plugin API, `tool` is reserved for registering *new tools* (each needing a `description`, `args`, and `execute` function). The hook `"tool.execute.before"` is a **top-level dotted key** on the `Hooks` object, not a nested path.

The fix:

```javascript
return {
  "tool.execute.before": async (input, output) => { ... }
};
```

This distinction matters. OpenCode iterates over `tool` entries expecting `ToolDefinition` objects. When it found `{ before: ... }` instead, it called `.execute(args, ctx)` on it, which was `undefined`. Hence the error: `def.execute is not a function`.

## What DCG Blocks

| Category | Examples |
|----------|----------|
| Git history destruction | `git reset --hard`, `git push --force`, `git branch -D` |
| Uncommitted work loss | `git checkout — .`, `git restore file`, `git clean -f` |
| Stash destruction | `git stash drop`, `git stash clear` |
| Filesystem damage | `rm -rf` outside `/tmp` |
| Database operations | `DROP TABLE`, `FLUSHALL` (via packs) |
| Container destruction | `docker system prune`, `docker-compose down --volumes` |
| Infrastructure | `terraform destroy`, `kubectl delete namespace` |

Safe operations pass through silently: `git status`, `git add`, `git commit`, `git push` (without `--force`), `git stash`, `git checkout -b`, and all non-destructive commands.

## Key Design Decisions

**Default-allow.** Unrecognised commands pass through. DCG blocks only *known* dangerous patterns. This prevents false positives from blocking legitimate work.

**Whitelist-first.** Safe patterns (like `git checkout -b`) are checked *before* destructive patterns. Explicitly safe commands are never accidentally blocked.

**Sub-millisecond latency.** Jeffrey's implementation uses SIMD-accelerated substring search via Rust's `memchr` crate. Commands without "git" or "rm" bypass regex matching entirely. The guard adds no perceptible delay.

**Fail-open.** If dcg crashes or produces unexpected output, the plugin catches the error and defaults to allowing the command. A broken guard should never break your workflow. A safety system that slows down the developer will be disabled by the third day. A safety system that is invisible will run forever.

## Extending with Packs

DCG ships with a modular pack system. Enable additional protection categories in `~/.config/dcg/config.toml`:

```toml
[packs]
enabled = [
    "database.postgresql",
    "containers.docker",
    "kubernetes",
    "cloud.aws",
]
```

Or via environment variable:

```bash
export DCG_PACKS="containers.docker,kubernetes"
```

## Installation

```bash
# 1. Install dcg
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/master/install.sh" | bash

# 2. Install the plugin
mkdir -p ~/.config/opencode/plugin
curl -fsSL https://raw.githubusercontent.com/jms830/opencode-dcg-plugin/main/plugin/dcg-guard.js \
  -o ~/.config/opencode/plugin/dcg-guard.js

# 3. Restart OpenCode
```

## Conclusion

The OpenCode plugin API's `"tool.execute.before"` hook is a clean interception point for safety guards. Combined with Jeffrey Emanuel's dcg and its fast pattern matching, you get protection against destructive commands with zero workflow friction. The plugin is small, the guard is fast, and the safety net catches the mistakes that matter.

Instructions are suggestions. Guards are guarantees.

---

*DCG is built by [Jeffrey Emanuel](https://github.com/Dicklesworthstone) — see his [destructive_command_guard](https://github.com/Dicklesworthstone/destructive_command_guard) repository and the broader [agentic coding flywheel](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup) ecosystem for more agent safety tooling.*

*This post is part of the [Disciplined Engineering](/posts/disciplined-engineering-ai-systems/) series. See also: [Teaching AI Agents with Knowledge Graph Hooks](/posts/teaching-ai-agents-with-knowledge-graphs/) and [Teaching AI Agents to Learn from Their Mistakes](/posts/teaching-ai-agents-to-learn-from-mistakes/).*

*Source: [DCG plugin gist](https://gist.github.com/bc7cc0f237bdb2a6fade347aba203acb) and [opencode-dcg-plugin repository](https://github.com/jms830/opencode-dcg-plugin)*
