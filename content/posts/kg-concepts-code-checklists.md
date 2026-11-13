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
how-to applies the released pieces to the simplest possible concept:
**`npm install` must become `bun add`**. It also identifies the bounded
`terraphim-agent code` loop accurately as an unreleased proposal.

The hook and validation commands below were reproduced with released
`terraphim-agent` v1.21.22. The `code` footage predates release qualification
and is retained as a source-only demo, not as an installable command.

<!-- more -->

## TL;DR

Declare the concept once (`kg/*.md` or `.terraphim/rewrite/*.md` with
`synonyms::`), let the hook find `npm install` in a proposed tool call and
prescribe `bun add`, then inspect lexical checklist coverage with
`validate --checklist`. This is not a quality authorization: a lexical matcher
does not execute tests, review code, or approve a merge or deployment.

## Declare the Concept

One file, written once, compiled into the role's automaton. From this site's own
`.terraphim/rewrite/bun install.md`:

```text
# bun add

Install dependencies using Bun package manager.

synonyms:: npm install, yarn install, pnpm install, npm i, yarn add, pnpm add
```

## Before `code`: The Hook Checks the Action

An agent proposing `npm install` hits the rewrite graph first. Use the complete
`Command Rewriter` role setup in the [checklists article](/posts/graph-embeddings-checklists/),
which points `knowledge_graph_local.path` at `.terraphim/rewrite`, then run
`pre-tool-use` with explicit `--rewrite`:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"npm install react"}}' \
  | terraphim-agent --config "$TERRAPHIM_REWRITE_CONFIG" \
      hook --hook-type pre-tool-use --rewrite \
      --role "Command Rewriter" --json
```

```json
{"tool_input":{"command":"bun add react"},"tool_name":"Bash"}
```

The concept fired: `npm install` in, `bun add` out — a rewrite rule
executed *before* the tool call runs, with a named edge (`bun install.md`) to
audit.

## `code run`: Unreleased Source-Only Demo

Released v1.21.22 has no `code` subcommand: its exact top-level help omits it,
and asking for `terraphim-agent code --help` exits 2 with “unrecognized
subcommand 'code'”. `code run`, `code resume`, and `code doctor` remain in open
[Gitea PR #432](https://git.terraphim.cloud/terraphim/terraphim-clients/pulls/432).
Do not copy a `code run` command from the demo and expect an installed v1.21.22
binary to execute it.

The source-only capture showed a proposed bounded loop producing:

```text
- **Cargo.toml** — package `terraphim` v0.1.0, edition 2021, no dependencies
- **src/main.rs** — `fn main()` printing `Hello from terraphim`

Verified with `cargo run`, which compiled cleanly and output:

    Hello from terraphim
```

Those policy, audit, transcript, and resume claims describe the open PR's demo,
not released behavior. They become public CLI instructions only after a reviewed
release exposes the subcommand in its pinned help.

## After `code`: The Checklist Judges the Result

The released `code_review` checklist reports lexical coverage. It does not judge
whether code is correct or safe:

```bash
echo "no tests; no documentation; no error handling; no security; no performance" \
  | terraphim-agent validate --checklist code_review --json
```

Formatted for reading (the separately pinned raw stdout is one line):

```json
{"checklist_name":"code_review","passed":false,"total_items":5,
 "satisfied":[],
 "missing":["tests","documentation","error_handling","security","performance"]}
```

The measured result is `passed=false`, a score of `0/5`; the human form says
`Passed: false`, and the command nevertheless exits 0. Shell automation must
parse the result's `passed` field (`result.passed` in a consumer) rather than
treating process success as checklist success. Conversely, matching words is
only lexical coverage: even a positive `passed` value is not a quality
authorization. Real authorization still requires executed tests, independent
review, and exact-head CI.

## The Loop

```text
declare kg/*.md ──► hook pre-tool-use (npm install → bun add)
                              │
              code run — unreleased PR #432 demo
                              │
            validate --checklist code_review — the verdict
                              │
              learn/correct — feed misses back into synonyms
```

## Honest Notes

- `hook --rewrite` is opt-in (`--rewrite` flag, default off). On v1.21.22 the
  no-rewrite response preserves the input and emits a warning; it does not
  return `validations.findings` for this role-only setup.
- `terraphim-agent replace` in this build reports `changed: true` while
  returning the input unchanged. Verify the returned command itself rather
  than relying on a change flag or an optional findings object.
- The role's rewrite graph and the global learn/validation KG are distinct in
  v1.21.22. Register the role explicitly as shown; do not infer validation
  findings from a successful replacement.

## Historical PR-only Demo

Two `fframes` renders preserve the original captures. Their `code` sequences
are explicitly historical source-only evidence, not v1.21.22 release evidence.

<video controls playsinline preload="metadata" poster="/demos/kg-concepts-code-checklists/terraphim-spec-graph-gate-code-checklist-poster.png" style="width:100%;height:auto;max-width:100%;border-radius:12px" aria-label="A real spec checked by the knowledge graph, gated during code, then scored by a checklist">
  <source src="/demos/kg-concepts-code-checklists/terraphim-spec-graph-gate-code-checklist.mp4" type="video/mp4">
  <a href="/demos/kg-concepts-code-checklists/terraphim-spec-graph-gate-code-checklist.mp4">Download the video</a>.
</video>

The historical PR #432 capture joined the storyline (`spec → graph → gate →
surface → code → checklist`): it showed a real `spec.md`, `terraphim-grep`
firing `validation gate` on the context, the proposed PR-only gate denying two
shell calls by rule name, the proposed tools/commands/policy surface, a
historical `cargo run` output, and the `0/5` checklist verdict on spec-violating
code. Those gated tool calls and policy surfaces are not released v1.21.22
features.

<video controls playsinline preload="metadata" poster="/demos/kg-concepts-code-checklists/terraphim-engineered-issue-poster.png" style="width:100%;height:auto;max-width:100%;border-radius:12px" aria-label="A real terraphim-clients issue driven through disciplined engineering phases">
  <source src="/demos/kg-concepts-code-checklists/terraphim-engineered-issue.mp4" type="video/mp4">
  <a href="/demos/kg-concepts-code-checklists/terraphim-engineered-issue.mp4">Download the video</a>.
</video>

The disciplined-engineering cut (`issue → research → design → impl → verify →
validate`): real issue #431
through the `disciplined-*` phases — the `rg` finding, the design decision,
real commits, `fmt`/`blaze` verification, and the checklist verdict.
