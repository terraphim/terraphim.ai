+++
title="Stop Paying the Cold-Start Tax: Agentic Memory for Teams Running 42 Agents Nightly"
date=2026-07-01

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "ai", "agentic-engineering", "memory", "adf", "knowledge-graph", "developer-tools"]
[extra]
toc = true
comments = true
+++

We run forty-two AI agents in our Dark Factory every night. Every one of them used to wake up with amnesia, rediscovering facts we already knew, paying the same token bill twice. Here is what we built to stop paying it -- and the eight-stage frame, named by memco.ai, that finally made the story legible. As of July 2026, the whole pipeline ships as a single `terraphim-agent memory` CLI namespace.

> Builds on [Teaching AI Agents to Learn from Their Mistakes](/posts/teaching-ai-agents-to-learn-from-mistakes/) and [Knowledge Graph Hooks](/posts/teaching-ai-agents-with-knowledge-graphs/). Maps both into a single lifecycle.

<!-- more -->

## The cold-start tax is a line item, not a metaphor

Last Tuesday an ADF agent spent fourteen thousand tokens working out that our project uses `bun`, not `npm`. We had captured that correction three months ago. The correction was sitting in `~/.config/terraphim/`, two directories away from where the agent was looking, in a file the agent did not know to read.

memco.ai calls this the **cold-start tax**: every agent run begins from zero, paying full token cost for facts the team already owns. They name it well. "Context is rented. Memory is owned." Read their [field guide](https://www.memco.ai/field-guide); it is short and it is right.

The tax compounds. With forty-two agents running through the night against the same repository, the same rediscovery happens forty-two times. Most teams cope by buying bigger context windows. We tried that. Bigger windows do not pay the tax; they just stretch the receipt.

## The second run is the signal

The number that actually matters is the delta between run one and run two of the same task. If memory works, run two costs less. If memory fails, run two costs the same as run one and your "AI strategy" is a slot machine with extra steps.

Here are five tasks from our last seven days of ADF activity, retried within twenty-four hours after a hook-captured correction landed:

| Gitea issue | Run 1 input tokens | Run 2 input tokens | Delta |
|---|---|---|---|
| #1873 | 47,200 | 31,800 | -32.6% |
| #1862 | 28,400 | 19,100 | -32.7% |
| #1879 | 81,000 | 63,500 | -21.6% |
| #1858 | 33,900 | 28,200 | -16.8% |
| #1850 | 52,100 | 47,400 | -9.0% |

Median: 21.6%. Best: 32.7%. Worst: 9%. The 9% case is a fair tell -- that issue's correction sat in a project KG the second-run agent did not consult. We patched the role scope; next attempt should join the others.

The new `second-run` subcommand reads ADF artefacts and computes this delta automatically:

```bash
$ terraphim-agent memory second-run --issue 1899
{
  "gitea_issue": 1899,
  "runs_compared": 4,
  "delta": {
    "tokens_saved": 8400,
    "retries_avoided": 1,
    "wall_time_delta_seconds": -45.2,
    "interpretation": "improved (fewer tokens in later run)"
  }
}
```

We had this data and we were not looking at it. That is the marketing failure underneath the engineering one.

## Eight stages, all green: the lifecycle in our stack

memco names eight stages of an agentic memory lifecycle. We checked our stack against it. All eight are now wired behind a single CLI namespace.

| Stage | What memco names | CLI command | Status |
|---|---|---|---|
| 1. Capture | Record the lesson | `terraphim-agent memory capture --provenance-tag <TAG>` | Shipped |
| 2. Distill | Synthesise into a shape worth keeping | `memory distill` | Shipped |
| 3. Scope | Attribute the right role / project | `memory scope --role <ROLE> --check` | Shipped |
| 4. Provenance | Trace it back to where it came from | `memory provenance` | Shipped |
| 5. Retrieve | Find it again when it matters | `memory retrieve <QUERY>` | Shipped |
| 6. Apply | Inject it into the next run | `memory apply --prompt <TEXT>` | Shipped |
| 7. Validate | Check the lesson is still true | `memory validate` | Shipped |
| 8. Retire | Demote the lessons that have aged out | `memory retire --lesson-id <ID>` | Shipped |
| -- | Diagnostic | Full reliability readout | `memory rubric --project <PATH>` | Shipped |
| -- | Inspection | Browse the evolution store | `memory list`, `memory show`, `memory export` | Shipped |

The implementation lives in [terraphim-clients PR #61](https://git.terraphim.cloud/terraphim/terraphim-clients/pulls/61). Thirteen subcommands, ~1200 lines of Rust, built on `terraphim_agent_evolution` from the terraphim registry. No new crates. No new schemas. Pure consolidation.

## The Memory Reliability Rubric: a ten-minute readout

The rubric subcommand scores every captured memory on six dimensions and produces a markdown diagnostic in under a second:

1. **Faithfulness** -- does the memory accurately describe what happened?
2. **Scope** -- is the role and project boundary correct?
3. **Provenance** -- can we trace this memory to a session, commit, or hook event?
4. **Actionability** -- does the memory tell the next agent what to do, or only what happened?
5. **Decay** -- is the memory still current, or has the codebase moved past it?
6. **Risk** -- does applying this memory introduce a new failure mode (brittle text substitution, false confidence)?

Example output against a project with two captured items:

```
$ terraphim-agent memory rubric --project ~/project

# Memory Reliability Rubric Report

| Dimension    | Score | Status        |
|-------------|-------|---------------|
| Faithfulness | 0.65 | Adequate      |
| Scope       | 0.30 | Needs attention |
| Provenance  | 0.90 | Good          |
| Actionability | 0.40 | Adequate    |
| Decay        | 1.00 | Good          |
| Risk         | 0.40 | Needs attention |

Composite score: 0.59 / 1.00

## Top 3 Items Needing Attention

1. **ab12cd** (composite: 0.57) -- Memory item captured via CLI with provenance: test
2. **ef34gh** (composite: 0.60) -- Potential risk pattern detected in content

## Recommended Retirements

- **ef34gh**: contains high-risk command pattern (risk: 0.70)
```

## Public commons vs permissioned memory

Not every lesson belongs to the world. We split memory into two buckets, with a policy file at the repo root:

**Public commons memory** lives in the [terraphim-skills](https://github.com/terraphim/terraphim-skills) repository and as KG terms published via Gitea wiki. Apache-2.0, no PII, no secrets. Anyone can clone, anyone can contribute.

**Permissioned memory** lives in per-project KGs, per-agent corrections, and session transcripts. It stays in `~/.config/terraphim/evolution/cli-agent.json` or per-repo `.terraphim/`. Never leaves the device without an explicit publication step. A scope check in the capture path warns when a permissioned item is about to land in a public location.

This split is what makes the open-source story work without burning operational secrets. It is documented in `MEMORY_POLICY.md` at the terraphim-clients repo root.

## Try it

Install:

```bash
# Build from source (terraphim-clients repo)
git clone https://git.terraphim.cloud/terraphim/terraphim-clients.git
cd terraphim-clients
cargo build --release -p terraphim_agent

# Capture a memory item
terraphim-agent memory capture --provenance-tag "session-abc123"

# Browse the store
terraphim-agent memory list

# Run the reliability rubric
terraphim-agent memory rubric --project ./my-project

# Check second-run acceleration
terraphim-agent memory second-run --issue 1234

# Export as JSON
terraphim-agent memory export --format json --output memory-dump.json
```

The full `memory` namespace is shipping in [terraphim-clients PR #61](https://git.terraphim.cloud/terraphim/terraphim-clients/pulls/61). The feature request is [terraphim-ai#1899](https://git.terraphim.cloud/terraphim/terraphim-ai/issues/1899). Thirteen subcommands, one CLI surface, zero new crates.

## What memco got right, and what we are adding

memco named the category and wrote the field guide. That is real work and we are crediting them for the vocabulary throughout this post. What we are adding is the engineering substrate: a working eight-stage pipeline in Rust with 13 CLI subcommands, a six-dimension rubric you can run on your own code, a second-run acceleration signal measured from production ADF data, and a forty-two-agent fleet that has been paying the tax in production for long enough to measure the relief.

The cold-start tax is real. The second-run signal is measurable. The lifecycle exists in a single CLI namespace today. Read the field guide. Then check your own stack against the eight stages. If you are missing more than two, you are paying tax you do not need to pay.

---

*Discuss on [Twitter](https://twitter.com/terraphim_ai) or open an issue at [git.terraphim.cloud/terraphim/terraphim-ai](https://git.terraphim.cloud/terraphim/terraphim-ai). The Gitea feature request for the consolidated CLI is [#1899](https://git.terraphim.cloud/terraphim/terraphim-ai/issues/1899). PR: [terraphim-clients#61](https://git.terraphim.cloud/terraphim/terraphim-clients/pulls/61).*
