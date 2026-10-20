# Task Plan: Article — Graph Embeddings for Checklists

Goal: publish `content/posts/graph-embeddings-checklists.md` on terraphim.ai
demonstrating how graph embeddings (nterm/synonym automaton) turn checklists
from prose into executable gates around the LLM call: terraphim-grep retrieval
before the call, terraphim-agent hooks + learn/memory after it.

Tracking: Gitea terraphim/terraphim.ai#5 (labelled status/in-progress).
Evidence gathered so far: docs_dev/findings.md.
Interpretation: "jsm skills" = jeffreys-skills.md catalogue; "our skills" =
terraphim skill stack.

## The article's thesis

A checklist is an enumerated set of terms that must be checked. Vector
embeddings cannot enumerate a set — they return fuzzy neighbours. A
Terraphim knowledge graph can: the nterm is the checklist head, the synonyms
are the items, and the Aho-Corasick automaton either matches each item or
reports that it did not. Same machinery drives both halves of the loop:

- Before the LLM call — `terraphim-grep --thesaurus <role>` expands the task
  vocabulary into concept synonyms and retrieves grounded chunks. The
  checklist question is "does the prompt contain the right evidence?"
- After the LLM call — `terraphim-agent hook` returns a findings list
  (matched_term → suggested_replacement), `learn` captures failures and
  corrections, `memory` stores authored lessons, hooks (PostToolUse /
  prepare-commit-msg) apply the gate automatically.

The workflow that produces the article IS the demonstration: real commands,
real JSON, captured in findings.md.

## Article outline (technical-leadership voice, UK English, no emoji)

1. Hook: checklists are the one artefact agents can verify deterministically;
   stop asking the model whether it followed the checklist and start matching
   the checklist's vocabulary.
2. Why a graph and not a vector index: enumeration beats similarity.
   Explainability — every hit names its edge.
3. Phase A, before the LLM call: `terraphim-grep "quality gate" --thesaurus
   ~/.config/terraphim/thesaurus.json` → kg_hits 8, 53 ms, concept expansion
   to accept/fail/escalate/judge-verdicts; control run ("checklist",
   kg_hits 0) shows honest empty-KG behaviour.
4. Phase B, after the LLM call: `terraphim-agent hook --hook-type
   pre-tool-use` JSON findings for `npm install` → `bun install`; rewrite KG
   markdown files as the checklist source of truth; PostToolUse learning
   capture and `memory retrieve` closing the loop.
5. The lifecycle: declare synonyms → build thesaurus → retrieve → draft →
   findings gate → capture corrections → the checklist compiles again.
6. Numbers and honesty section: reuse verified figures (1.4M patterns <1 ms,
   20 ms rebuild) plus this session's 53 ms/8 kg_hits; note the
   `replace`/`changed:true` quirk and how the findings contract is the
   stable API.
7. Cross-links to why-graph-embeddings-matter, native-hook-support,
   teaching-* posts, /docs/graph-embeddings/, command-rewriting-howto.

## Phases

### Phase 1 — Track and frame (DONE)
- [x] date, tool versions, Gitea issue #5 created + in-progress
- [x] load jsm + terraphim skills
- [x] run pre-LLM terraphim-grep demos; capture JSON to findings.md
- [x] run post-LLM hook demo; identify findings-checklist contract

### Phase 2 — Draft (the LLM call this article describes)
- [x] `git checkout -b task/5-graph-embeddings-checklists`
- [x] Write `content/posts/graph-embeddings-checklists.md`
      (frontmatter matching existing posts, `<!-- more -->`, UK English)
- [x] Every command block in the post = a command actually executed this
      session; real output pasted, no invented numbers

### Phase 3 — Post-LLM checklist gate (the article's own gate)
- [x] de-slopify pass: trimmed 4 em-dashes to colon/semicolon/parens;
      3 remain (consistent with published post style)
- [x] `terraphim-agent hook` findings over the whole article: 10 findings,
      all inside quoted KG/demo blocks — zero instructional commands flagged
- [x] Verify each internal link resolves (9/9 files found under content/)
- [x] Frontmatter check: title/date/taxonomies/toc/comments present
- [x] `zola build` clean — NOTE: brew zola 0.23.6 fails on theme; CI pins
      0.22.1 which builds cleanly (50 pages). Used /tmp/zola 0.22.1.
- [x] `learn correction add`: replace→hook findings (tool-preference)
      saved as correction-ac438fe65b974e25837d3e5f0d200a99
- [x] `memory capture` verified: 2714c769-7ac9-4334-be19-842c9e03dbb1
      (hook-findings-over-replace lesson, provenance terraphim.ai-issue-5-article)

### Phase 4 — Ship
- [ ] Commit `Refs #5`, push branch, `gh pr create` (origin is GitHub)
- [ ] `gtr comment` progress + PR URL on issue #5
- [ ] Optional: structural-pr-review / quality-gate before merge; close #5
      after merge. Deploy is via Cloudflare Pages pipeline — not manual.

## Errors encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| gtr edit-issue label | status/in-progress missing | created label via API, retried |
| gtr edit-issue flag | --add-assignees unsupported | skipped assignee (flag absent in this gtr build) |
| terraphim-agent replace | changed:true but identical result | recorded as learn correction + memory; article centred on hook findings |
| zola build 0.23.6 | macros:: in extending templates fails | parity with CI's pinned zola 0.22.1 (/tmp/zola) — theme left unchanged |
