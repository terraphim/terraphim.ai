# Implementation Plan: Interactive Graph Embeddings Explainer

**Status**: Draft
**Canonical Path**: `docs/plans/design-graph-embeddings-explainer.md`
**Change Slug**: `graph-embeddings-explainer`
**Research**: `docs/plans/research-graph-embeddings-explainer.md`
**Author**: Devin
**Date**: 2026-10-20
**Estimated Effort**: 1 day

## Overview

### Summary

Add `/docs/graph-embeddings-interactive/` — a single Zola page that runs the
real RoleGraph indexing and query algorithm in the browser (faithful
dependency-free JS port), visualises it on an SVG graph, and contrasts it
with dense vector embeddings and traditional learned graph embeddings
(node2vec/DeepWalk, GCN, TransE, Cleora).

### Approach

- One content page (`docs` section) using a new thin template that extends
  `base.html` and loads the explainer bundle via `{% block custom_js %}`.
- The algorithm is ported 1:1 from `terraphim_rolegraph/src/lib.rs`
  (AC LeftmostLongest match → `tuple_windows` pairs → `magic_pair` edge IDs →
  `doc_hash` counts → sum-of-ranks scoring). A Python oracle mirrors the Rust
  source and emits golden vectors; a Node/browser-less test asserts the JS
  output equals the oracle on the bundled corpus.
- Illustrative (simulated) vector-side panels are clearly labelled as such.

### Scope

**In Scope:**
- Interactive explainer page with 5 scenes (see Scenes below)
- Comparison table (three families) + honest-limits section
- Cross-links from the two existing graph-embeddings pages
- Golden-vector oracle + JS conformance check

**Out of Scope:**
- Video render, WASM build changes, theme changes, nav changes
- Fixes to pre-existing zola 0.23.6 template incompatibility (issue #6)

**Avoid At All Cost** (5/25):
- A JS framework or build pipeline — fatal for a static page
- Fake/staged numbers on the Terraphim side
- Full AC trie/fail-link visualisation — too much machinery for the payoff;
  the matcher is shown as a scanning cursor + matched spans instead
- Persisting user input, accounts, comments — not needed
- Rewriting existing prose pages

## Architecture

### Component Diagram

```
content/docs/graph-embeddings-interactive.md   (front-matter + scene scaffolding HTML + prose)
templates/explainer.html                       (extends base.html; article chrome + custom_js block)
static/explainers/graph-embeddings/
    explainer.css          (scene layout, SVG styling, WarpDrive-consistent palette)
    explainer.js           (ES module: engine + scene controllers)
    corpus.json            (thesaurus {term→{id,nterm}} + 8 mini documents)
scripts/explainer/
    oracle.py              (1:1 port of Rust insert_document/query_graph)
    goldens.json           (expected node/edge/doc counts + query rankings)
    check.js               (loads explainer.js engine in Node, asserts == goldens)
```

### Data Flow

```
corpus.json ──► engine.js (RoleGraphLite) ──► scene renderers (SVG + DOM)
oracle.py ──► goldens.json ──► check.js asserts JS engine output identical
```

## Key Design Decisions

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| JS port of algorithm, not WASM | Faithful + inspectable + zero init complexity; algorithm is ~80 lines | terraphim_rolegraph_browser WASM (heavier, less readable for teaching) |
| SVG for the graph | <50 elements; accessible; CSS-animatable | Canvas/WebGL |
| Directed edges shown honestly | `magic_pair` is order-sensitive — this is a real, teachable detail | "Undirected co-occurrence" simplification (inaccurate) |
| `edge.rank` shown as constant 1; per-doc count via `doc_hash` | Matches code, not the looser prose | Repeating the docs-page description literally |
| Deterministic hand-tuned layout for curated nodes; circle placement for user-added | Force layout adds jitter nondeterminism | Force-directed layout |
| Curated thesaurus: distributed-systems terms | Continuity with `docs/graph-embeddings.md` raft/consensus example | baseline-role.json café/decision set (whimsical, off-topic) |

## Scenes (interaction spec)

All scenes share one `RoleGraphLite` instance so the user sees state persist.

1. **Two worlds** — side-by-side toggle. Left: "dense vector" panel — dots in
   a 2-D field, query dot, dashed cosine-radius ring, a doc highlights with
   caption "score 0.83 — nothing else to see". Right: graph panel — the same
   corpus as nodes/edges; clicking a result reveals *the path* and the sum.
   Honest moment: type an out-of-thesaurus term — graph returns nothing,
   vector side still returns nearest neighbours. Label on left panel:
   "illustrative simulation".
2. **The matcher** — text input; as the user types, a cursor scans left to
   right, matched spans highlight and tag with their concept id/nterm;
   LeftmostLongest shown by a `judgment` vs `judgment call`-style overlap in
   the corpus thesaurus (e.g. `leader` vs `leader election`).
3. **Indexing** — a document queue; "Index next" / "Index all" buttons +
   free-text "index your own sentence". Each step: matched sequence renders
   as chips; consecutive pairs animate into the graph as directed edges;
   node counters and the `doc_hash` ledger tick up. Replace semantics demo:
   "re-index doc 3" shows contributions removed then re-added.
4. **Query** — query input; matched nodes pulse; for each result a ledger
   lists every contribution `node.rank + edge.rank + doc.rank` with
   expandable provenance (which edge, which document count). Ranked list
   re-sorts live.
5. **When does the work happen?** — pipeline comparison. Three columns:
   Terraphim (build thesaurus → index: counters → query: sum) vs
   node2vec-family (walks → skip-gram → vectors → ANN) vs dense API
   (upload corpus → embed call → index → per-query embed+ANN). Interactive:
   "add a synonym" — Terraphim column flashes "rebuilt in ~ms" (real, graph
   rebuilt live); others show a spinner labelled "re-embed required
   (illustrative)". Timing chips cite published numbers with source note.
6. **Recap + honest limits** — table from research §Comparative landscape;
   bullet list: OOV blindness, coarse ties, frequency bias, no smoothing
   beyond thesaurus, TF-IDF trigger fallback exists to soften (1).

## API Design

### `corpus.json` shape (mirrors real thesaurus JSON)

```json
{
  "thesaurus": {
    "name": "Systems Engineer",
    "data": { "raft": {"id": 1, "nterm": "raft"}, "consensus": {"id": 2, "nterm": "consensus"} }
  },
  "documents": [ {"id": "doc-1", "text": "…"} ]
}
```

### `engine.js` (exported from explainer.js for testing)

```js
export function magicPair(x, y)           // exact port of lib.rs:1270
export function magicUnpair(z)            // exact port of lib.rs:1276
export class AhoLite {
  constructor(thesaurusData)              // patterns = keys, payload = id
  findMatches(text)                       // -> [{start, end, id, nterm}]
                                          // LeftmostLongest, ASCII case-insensitive
}
export class RoleGraphLite {
  constructor(thesaurus)
  insertDocument(docId, text)             // replace semantics like Rust
  removeDocument(docId)                   // idempotent
  queryGraph(q, {offset, limit})          // -> [{docId, score, contributions[]}]
  stats()                                 // {nodes, edges, documents}
}
```

`contributions[]` entries: `{nodeId, nterm, edgeId, pair:[a,b], docRank, nodeRank, edgeRank}` — powers the provenance ledger (the explainability story the vectors cannot tell).

### `explainer.js` scene controllers

```js
initScenes(root)         // wires scenes 1–5 against one RoleGraphLite
renderGraph(svg, graph, highlights)  // nodes/edges/counters
renderLedger(el, contributions)      // score arithmetic per doc
```

## Test Strategy

| Test | Location | Purpose |
|------|----------|---------|
| `oracle.py` golden generation | `scripts/explainer/oracle.py` | Independent re-derivation of index/query results from the Rust algorithm spec |
| `check.js` conformance | `scripts/explainer/check.js` | `node --experimental-… check.js`: asserts engine output == `goldens.json` (nodes, edges, per-doc scores, ranking order, directed-edge IDs, OOV empty result) |
| `magic_pair` round-trip | `check.js` | `magicUnpair(magicPair(a,b)) == (a,b)` for corpus ids |
| LeftmostLongest | `check.js` | overlapping pattern case from corpus |
| Manual UX pass | browser | reduced-motion, mobile widths, keyboard nav |

No mocks (project rule) — the check runs the real engine on the real corpus.

## Implementation Steps

1. **Engine + corpus + oracle**: `corpus.json`, `explainer.js` engine part,
   `oracle.py`, `goldens.json`, `check.js` — conformance green first.
2. **Template + page scaffold**: `templates/explainer.html`,
   `content/docs/graph-embeddings-interactive.md` skeleton, `explainer.css`.
3. **Scenes 2–4** (matcher, indexing, query) — the core teaching loop.
4. **Scenes 1, 5, 6** (worlds toggle, pipeline compare, recap).
5. **Cross-links** into the two existing pages; `zola build`; fix anything
   attributable to us; report issue #6 status honestly.
6. **Gitea issue + commit** (`Refs #N`).

## Rollback Plan

Page is additive; revert the commit. Delete `content/docs/graph-embeddings-interactive.md`
and `static/explainers/graph-embeddings/` if pulled.

## Expected Lifecycle Artefacts

| Artefact | Path | Required? |
|----------|------|-----------|
| Research | `docs/plans/research-graph-embeddings-explainer.md` | Done |
| Design | this file | Yes |
| Verification | manual checklist in commit/PR body | Yes |
| Validation | `zola build` + interactive smoke | Yes |

## Simplicity Check

**What if this could be easy?** It is: markdown page + static JS + one
template. No new dependencies, no build step. The only "clever" part — the JS
port — is constrained to be a line-by-line translation of ~80 lines of Rust.

## Open Items

| Item | Status | Owner |
|------|--------|-------|
| Page placement `docs/` vs new section | Defaulted to `docs/` | Alex to veto |
| Zola 0.23.6 local build (issue #6) | Pre-existing; verify and report | — |

## Approval

- [ ] Technical review complete
- [ ] Human approval received
