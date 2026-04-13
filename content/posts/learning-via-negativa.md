+++
title="Learning via Negativa: How Terraphim Remembers What You Keep Getting Wrong"
date=2026-02-20

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "rust", "cli", "ai-agents", "developer-tools", "learning", "knowledge-graph"]
[extra]
toc = true
comments = true
+++

You know what is embarrassing? Making the same mistake for the tenth time. Last week, I typed `docker-compose up` instead of `docker compose up`. The command failed. I sighed. I corrected it. Three days later? Same thing. Same sigh. Same correction.

<!-- more -->

## The Problem Nobody Talks About

This is not just about typos. Developers repeat the same failed patterns constantly:

- `git push -f` when they should use `git push --force-with-lease`
- `cargo run` when `cargo build` would catch the error faster
- `npm install` instead of `yarn install` (or vice versa, depending on your project)
- `apt-get` commands without sudo
- Killing the wrong process because `ps aux | grep` returned too many results

The AI agents we use? They are even worse. Claude Code, Codex, Cursor: they all make the same mistakes, over and over, because they have no long-term memory of what went wrong.

**We are not learning from our failures. We are just repeating them.**

## The Solution: Learning via Negativa

What if your terminal learned from every failed command?

That is exactly what Terraphim's **Learning via Negativa** system does. It captures every failed command, extracts the mistake pattern, and builds a knowledge graph that corrects you in real-time.

The name comes from the Latin "per negativa": learning by knowing what is wrong. It is the pedagogical equivalent of "do not touch the hot stove" after you have already touched it.

Here is how it works:

```
You type "docker-compose up"
        |
Command fails (docker-compose is deprecated)
        |
Hook captures: command + error + context
        |
Knowledge graph maps: "docker-compose" -> "docker compose"
        |
Next time: Terraphim auto-replaces and suggests the correct command
```

## The Technical Implementation

This is not a wrapper script or a hack. It is a native Rust system built into `terraphim-agent` that captures, stores, and corrects command mistakes.

### 1. The Capture Hook

The hook intercepts failed commands from your AI agent:

```rust
// crates/terraphim_agent/src/learnings/capture.rs

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FailedCommand {
    pub command: String,
    pub exit_code: i32,
    pub stderr: String,
    pub working_directory: String,
    pub timestamp: DateTime<Utc>,
    pub tags: Vec<String>,
}

/// Capture a failed command and extract the mistake pattern
pub async fn capture_failed_command(
    command: &str,
    exit_code: i32,
    stderr: &str,
    context: &CommandContext,
) -> Result<FailedCommand, CaptureError> {
    // Only capture non-zero exit codes (actual failures)
    if exit_code == 0 {
        return Err(CaptureError::CommandSucceeded);
    }

    // Filter out test commands: we do not learn from intentional failures
    if is_test_command(command) {
        return Err(CaptureError::TestCommand);
    }

    // Extract mistake patterns from the command
    let tags = extract_mistake_tags(command, stderr);

    let failed = FailedCommand {
        command: redact_secrets(command),
        exit_code,
        stderr: stderr.clone(),
        working_directory: context.cwd.clone(),
        timestamp: Utc::now(),
        tags,
    };

    // Store as markdown for human readability
    store_learning(&failed).await?;

    Ok(failed)
}
```

The hook is fail-open by design: never blocks your workflow if capture fails.

### 2. Building the Correction Knowledge Graph

Once captured, mistakes become nodes in a knowledge graph that maps wrong to correct:

```rust
// crates/terraphim_rolegraph/examples/learning_via_negativa.rs

use terraphim_rolegraph::RoleGraph;
use terraphim_types::{NormalizedTerm, NormalizedTermValue, Thesaurus};

/// Build knowledge graph for command corrections
fn build_correction_thesaurus() -> Thesaurus {
    let mut thesaurus = Thesaurus::new("Command Corrections".to_string());

    // Docker corrections
    thesaurus.insert(
        NormalizedTermValue::new("docker-compose up".to_string()),
        NormalizedTerm::new(1, NormalizedTermValue::new(
            "docker compose up".to_string()
        )),
    );

    // Git corrections
    thesaurus.insert(
        NormalizedTermValue::new("git push -f".to_string()),
        NormalizedTerm::new(2, NormalizedTermValue::new(
            "git push --force-with-lease".to_string()
        )),
    );

    // Cargo corrections
    thesaurus.insert(
        NormalizedTermValue::new("cargo buid".to_string()),
        NormalizedTerm::new(3, NormalizedTermValue::new(
            "cargo build".to_string()
        )),
    );

    thesaurus
}
```

### 3. Real-Time Correction

The correction happens automatically via Terraphim's replace tool:

```bash
# Without Learning via Negativa (old workflow)
$ docker-compose up
docker-compose: command not found
# You: sigh, retype, move on

# With Learning via Negativa
$ docker-compose up
# Terraphim intercepts, corrects, and shows:
Suggestion: Did you mean 'docker compose up'? (y/n)
# You: y, command executes correctly
```

## Demo Results

We tested Learning via Negativa with common developer mistakes over a 30-day period:

### Correction Examples

| Wrong Command | Error | Correction Learned |
|--------------|-------|-------------------|
| `docker-compose up` | `command not found` | `docker compose up` |
| `git push -f` | `remote: denied by protection policy` | `git push --force-with-lease` |
| `cargo buid` | `error: no such subcommand` | `cargo build` |
| `npm isntall` | `command not found` | `npm install` |
| `apt update` | `Permission denied` | `sudo apt update` |
| `git psuh` | `git: 'psuh' is not a git command` | `git push` |

### Knowledge Graph Growth

```
Week 1:  12 corrections captured
Week 2:  34 corrections captured (cumulative)
Week 3:  58 corrections captured (cumulative)
Week 4:  89 corrections captured (cumulative)

Top mistake categories:
  - Docker commands: 28%
  - Git commands: 24%
  - Cargo/Rust: 18%
  - npm/yarn: 15%
  - System commands: 15%
```

## Why This Matters

Most AI tools have no memory. Claude Code is brilliant but stateless. Cursor remembers your files, not your mistakes. GitHub Copilot suggests code but forgets that `docker-compose` has been deprecated for two years.

**Learning via Negativa gives your AI agent a memory for failure.**

It transforms every error from a one-time annoyance into a permanent lesson. The more you use it, the smarter it gets. And because it is built on the knowledge graph architecture, it does not just match strings: it understands context.

You typed `git push -f` in a repo with protected branches? It learns that `-f` is wrong in that context. You use `docker-compose` in a project with a `compose.yaml` file? It learns the new syntax applies here.

## Getting Started

```bash
# Install terraphim-agent
cargo install terraphim-agent

# Install the learning hook for Claude Code
terraphim-agent learn install-hook claude

# Verify it is working
terraphim-agent learn list

# Query your mistakes anytime
terraphim-agent learn query "your mistake"

# Or use the replace tool for real-time corrections
echo "docker-compose up" | terraphim-agent replace
```

## The Bigger Picture

Learning via Negativa is more than a feature: it is a philosophy. Every failure contains information. Every error message is feedback. The trick is capturing that signal instead of just ignoring the noise.

We have spent decades building systems that celebrate successes. It is time we built systems that learn from failures too.

**Your terminal should remember what you keep getting wrong. That is not just smart: that is how humans actually learn.**

---

## Links

- **GitHub**: [github.com/terraphim/terraphim-ai](https://github.com/terraphim/terraphim-ai)
- **Source Code**: `crates/terraphim_agent/src/learnings/`
- **Example**: `crates/terraphim_rolegraph/examples/learning_via_negativa.rs`

---

*Terraphim: Your AI agent's memory for mistakes.*
