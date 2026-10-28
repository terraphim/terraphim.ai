+++
title="KG Concepts Before Code, Checklists After"
date=2026-10-28
[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "coding-agent", "knowledge-graph", "checklists", "hooks"]
[extra]
toc = true
+++

The [Graph Embeddings for Checklists](/posts/graph-embeddings-checklists/) article
shows how a knowledge graph acts as an enumerable checklist around an LLM call:
`terraphim-grep` before it, `terraphim-agent hook` and learning after it. This
how-to applies the same loop to `terraphim-agent code` — the bounded coding loop —
on the simplest possible concept: **`npm install` must become `bun add`**.

Every command below was run while writing this article; the outputs are real.

<!-- more -->

## TL;DR

Declare the concept once (`kg/*.md` or `.terraphim/rewrite/*.md` with
`synonyms::`), let the hook find `npm install` in a proposed tool call and
prescribe `bun add`, run `code` inside the policy gate, then validate the
produced work with `validate --checklist`. The checklist guards the write and
judges the result — the model is never trusted to police itself.

## Declare the Concept

One file, written once, compiled into the role's automaton. From this site's own
`.terraphim/rewrite/bun install.md`:

```text
# bun add

Install dependencies using Bun package manager.

synonyms:: npm install, yarn install, pnpm install, npm i, yarn add, pnpm add
```

## Before `code`: The Hook Checks the Action

An agent proposing `npm install` hits the checklist first — `pre-tool-use` with
`--rewrite` (opt-in so a stray substring can't silently mutate a destructive
command):

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"npm install react"}}' \
  | terraphim-agent hook --hook-type pre-tool-use --rewrite \
      --role "Terraphim Engineer" --json
```

```json
{
    "tool_input": {
        "command": "bun install react"
    },
    "tool_name": "Bash"
}
```

The concept fired: `npm install` in, `bun install` out — a checklist line
executed *before* the tool call runs, with a named edge (`bun install.md`) to
audit.

## Inside `code`: The Loop Is Gated

`code run` puts the model inside a bounded loop — every tool call is
policy-decided, audited to JSONL, and the run is exit-coded for callers:

```bash
TERRAPHIM_CODE_MODEL=auto \
  terraphim-agent code run "Create a Cargo.toml and src/main.rs that prints Hello from terraphim"
```

```text
- **Cargo.toml** — package `terraphim` v0.1.0, edition 2021, no dependencies
- **src/main.rs** — `fn main()` printing `Hello from terraphim`

Verified with `cargo run`, which compiled cleanly and output:

    Hello from terraphim
```

The hook and the gate compose: the KG checklist shapes what commands the agent
may propose, the deny-first policy decides whether a call runs at all, and the
audit JSONL records both decisions. Sessions persist as transcripts plus
`TurnStep` checkpoints, so `code resume` replays context and reads persisted
steps back.

## After `code`: The Checklist Judges the Result

The same graph that prescribed `bun` judges the output — `code_review` is a KG
checklist, not a prompt suggestion:

```bash
echo "no tests, unwrap() everywhere" \
  | terraphim-agent validate --checklist code_review
```

```text
Checklist 'code_review' Validation for role 'AI Dark Factory Author':
  Passed: false
  Score: 0/5
  Missing items:
    ✗ tests
    ✗ documentation
    ✗ error_handling
    ✗ security
    ✗ performance
```

Zero-inflated honesty applies here too: if the produced work mentions none of
the checklist items, the report says so with the missing set enumerated — the
same "honest empty case" property `terraphim-grep` shows on retrieval.

## The Loop

```text
declare kg/*.md ──► hook pre-tool-use (npm install → bun add)
                              │
                    code run — gated, audited, resumable
                              │
            validate --checklist code_review — the verdict
                              │
              learn/correct — feed misses back into synonyms
```

## Honest Notes

- `hook --rewrite` is opt-in (`--rewrite` flag, default off): findings are
  always emitted; the *substitution* is explicit. Without `--rewrite` the same
  run returns the input unchanged with the finding attached.
- `terraphim-agent replace` in this build reports `changed: true` while
  returning the input unchanged — the findings-based `hook` path above is the
  contract to rely on (this caveat is carried from the checklists post, which
  documented it first).
- `auto` on `terraphim-llm-proxy` resolves through the measured dynamic pool
  with a static `MiniMax-M3` fall-through, so a gated-out pool degrades to a
  healthy lane rather than failing — fixed during this session (the pool's
  eligibility gates had evicted every candidate while the static fallback was
  absent; `auto` answered with a generic 400). A dead member in the pool
  (`kimi-for-coding-highspeed`, subscription 403) still costs probe traffic.
- Roles resolve from the device-settings config; tests and CI can inject a
  thesaurus directly via `TERRAPHIM_CODE_AUTOMATA_PATH` rather than registering
  a role.

## The Demo

Two `fframes` renders of real captures back this article — every terminal
line is a real command output captured while writing it.

<video controls playsinline preload="metadata" poster="/demos/kg-concepts-code-checklists/terraphim-spec-graph-gate-code-checklist-poster.png" style="width:100%;height:auto;max-width:100%;border-radius:12px" aria-label="A real spec checked by the knowledge graph, gated during code, then scored by a checklist">
  <source src="/demos/kg-concepts-code-checklists/terraphim-spec-graph-gate-code-checklist.mp4" type="video/mp4">
  <a href="/demos/kg-concepts-code-checklists/terraphim-spec-graph-gate-code-checklist.mp4">Download the video</a>.
</video>

The joined storyline (`spec → graph → gate → surface → code → checklist`): a
real `spec.md`, `terraphim-grep` firing `validation gate` on the context, the
gate denying two shell calls by rule name, the tools/commands/policy surface,
a verified `cargo run` output, and the `0/5` checklist verdict on
spec-violating code.

<video controls playsinline preload="metadata" poster="/demos/kg-concepts-code-checklists/terraphim-engineered-issue-poster.png" style="width:100%;height:auto;max-width:100%;border-radius:12px" aria-label="A real terraphim-clients issue driven through disciplined engineering phases">
  <source src="/demos/kg-concepts-code-checklists/terraphim-engineered-issue.mp4" type="video/mp4">
  <a href="/demos/kg-concepts-code-checklists/terraphim-engineered-issue.mp4">Download the video</a>.
</video>

The disciplined-engineering cut (`issue → research → design → impl → verify →
validate`): real issue [#431](https://git.terraphim.cloud/terraphim/terraphim-clients/issues/431)
through the `disciplined-*` phases — the `rg` finding, the design decision,
real commits, `fmt`/`blaze` verification, and the checklist verdict.
