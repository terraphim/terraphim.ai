# Research: Interactive Visual Explainer for Terraphim Graph Embeddings

**Status**: Draft
**Canonical Path**: `docs/plans/research-graph-embeddings-explainer.md`
**Change Slug**: `graph-embeddings-explainer`
**Author**: Devin
**Date**: 2026-10-20
**Reviewers**: Alex

## Executive Summary

Terraphim's marketing site explains graph embeddings in two prose pages
(`content/capabilities/graph-embeddings.md`, `content/docs/graph-embeddings.md`)
and several posts, but there is no page where a visitor can *see* the mechanism
work. This change adds an interactive explainer page that animates the real
indexing and query algorithms — Aho-Corasick matching, consecutive-concept edge
formation, integer rank accumulation — and contrasts it with dense vector
embeddings and traditional learned graph embeddings (DeepWalk/node2vec,
GCN/GraphSAGE, TransE, Cleora). The algorithm is small enough to re-implement
faithfully in ~200 lines of dependency-free JavaScript, so every number on the
page is computed live, not staged.

## Essential Questions Check

| Question | Answer | Evidence |
|----------|--------|----------|
| Energising? | Yes | Graph embeddings are Terraphim's core differentiator; the site already invests in explaining them (3+ pages, a blog campaign) |
| Leverages strengths? | Yes | The whole algorithm fits in a browser — no GPU, no API — which is itself the product claim |
| Meets real need? | Yes | Current pages are text-only; readers cannot inspect *why* a document ranks. An interactive walkthrough closes that gap |

**Proceed**: Yes — 3/3 YES.

## Problem Statement

### Description

`docs/graph-embeddings.md` describes the scoring rule
(`node.rank + edge.rank + document_rank`) and the query pipeline in prose and
ASCII art. A first-time reader still has to simulate the algorithm in their
head. The comparison with alternatives is a static table. The request: a
visual, interactive page that (a) teaches how Terraphim graph embeddings work,
and (b) compares them with more traditional graph embeddings.

### Impact

- Site visitors evaluating Terraphim for explainable/on-device search.
- The promotion campaign already running (posts, how-tos) — an interactive
  artifact is a stronger landing target than prose.

### Success Criteria

- A reader can step through indexing and querying and state the scoring rule
  unprompted.
- Every number shown is computed by running the actual algorithm in the page
  (verified against an oracle derived from the Rust source).
- The page honestly shows both directions of the trade-off: vectors retrieve
  *something* for out-of-vocabulary terms; the graph retrieves nothing.
- `zola build` passes; page works on desktop and mobile, with reduced-motion
  fallback.

## Current State Analysis

### Existing Implementation

| Component | Location | Purpose |
|-----------|----------|---------|
| `RoleGraph` | `terraphim-core/crates/terraphim_rolegraph/src/lib.rs` | Index + query algorithm |
| `Node`/`Edge`/`Thesaurus` | `terraphim-core/crates/terraphim_types/src/graph.rs` | Graph primitives |
| `TriggerIndex` | `terraphim-core/crates/terraphim_rolegraph_core/src/trigger_index.rs` | TF-IDF fallback when AC finds nothing |
| AC automaton build | `terraphim_rolegraph/src/lib.rs:188` | `MatchKind::LeftmostLongest`, `ascii_case_insensitive` |
| Analysis doc | `terraphim-ai/docs/src/scorers/graph-embedding-analysis.md` | Terraphim vs Cleora comparison (in-repo) |
| Prose docs | `content/docs/graph-embeddings.md`, `content/capabilities/graph-embeddings.md` | Current explanations |
| Blog context | `content/posts/why-graph-embeddings-matter.md`, `sub-millisecond-context-knowledge-graphs.md` | Published numbers and framing |
| WASM build | `static/editor/rolegraph/` | `terraphim_rolegraph_browser` already compiled for the editor |
| Demo assets | `static/demos/synonym-search/baseline-role.json` | A real, small `thesaurus.json` (22 terms, 8 concepts) |

### The Algorithm (verified from source)

**Construction** (`RoleGraph::new_sync` → `build_aho_corasick`,
`lib.rs:188-207`): for every `(key, NormalizedTerm{id, value})` in the
thesaurus, push `key` as a pattern and `id` as the payload into an
Aho-Corasick automaton with `LeftmostLongest` matching and case-insensitive
ASCII. `ac_reverse_nterm` maps `id → nterm` for display.

**Indexing** (`insert_document`, `lib.rs:922-932`):
1. `find_matching_node_ids(doc.to_string())` — one AC scan → ordered concept-ID
   sequence (duplicates kept).
2. `tuple_windows()` over that sequence → consecutive directed pairs `(a, b)`.
3. `add_or_update_document(doc_id, a, b)`:
   - `edge_id = magic_pair(a, b)` — Cantor-style pairing (`lib.rs:1270`):
     `x>=y → x²+x+y`, `x<y → y²+x`. Directed: `pair(1,2)=5`, `pair(2,1)=7`.
   - `init_or_update_edge`: `Edge::new(id, doc)` with `rank=1`,
     `doc_hash={doc:1}`; on repeat, `doc_hash[doc] += 1`
     (`edge.rank` itself is never incremented in the current code — a real
     quirk worth knowing; the doc page describes edge.rank as a document
     count but the implementation keeps it at 1).
   - `init_or_update_node` for `a` and `b`: new node `rank=1`,
     else `node.rank += 1`; node's `connected_with` records the edge.
4. Re-inserting the same `document_id` first removes all its contributions
   (`remove_document_contributions`) — replace semantics, idempotent.

**Query** (`query_graph`, `lib.rs:455-544`):
1. AC-scan the query → matched node IDs.
2. For each node in the graph → for each `edge_id` in `node.connected_with`
   → for each `(doc_id, doc_rank)` in `edge.doc_hash`:
   `total = node.rank + edge.rank + doc_rank`, accumulated per document.
3. Sort by rank desc, tie-break document id asc; apply offset/limit.
4. `query_graph_with_trigger_fallback`: if AC finds no nodes, the TF-IDF
   `TriggerIndex` (over trigger descriptions) supplies candidate nodes;
   pinned nodes are always included when enabled.

### Data Flow

```
thesaurus.json ──► AC automaton (built once)
documents    ──► AC scan ──► [c1, c2, c3 …] ──► pairs (c1,c2),(c2,c3)… ──► edges+counts
query        ──► AC scan ──► matched nodes ──► their edges ──► doc_hash ──► Σ ranks ──► sorted docs
```

### Published claims to stay consistent with

- "1.4 million patterns matched in under one millisecond, under 4 GB RAM"
  (`why-graph-embeddings-matter.md`)
- "5–10 ns per KG inference step"; "20 ms to rebuild a role's graph"
- "15–20 MB RAM for a typical graph" (`capabilities/graph-embeddings.md`)

## Constraints

### Technical Constraints

- Zola static site, no JS build step — vanilla ES-module JS + SVG/Canvas only;
  no npm/React unless justified.
- `base.html` exposes `{% block custom_js %}` for page-specific scripts.
- WarpDrive theme: dark canvas (`#0a0c14` theme-colour), amber accent
  `oklch(0.72 0.16 70)` (CSS var names still say `--warp-blue`), Space
  Grotesk/Onest/JetBrains Mono fonts, FontAwesome icons (no emoji — project
  rule).
- British English in all copy (project rule).
- Issue terraphim/terraphim.ai#6: `zola build` fails on Zola 0.23.6 locally
  (macros call in `page.html`); CI pins 0.22.1. Verification may hit this —
  it is pre-existing, not ours to fix silently; note it.

### Business Constraints

- Page must not overclaim: simulated vector-side latencies must be labelled
  illustrative; the Terraphim side computes real values.

## Vital Few (Essentialism)

| Constraint | Why It's Vital | Evidence |
|------------|----------------|----------|
| Real algorithm in-page, not staged animation | The product claim is "deterministic, auditable"; a fake demo would contradict it | `interactive-visualization-creator` rule #9 (real algorithms, not fake data) |
| Honest trade-off visible | Credibility: the graph fails on OOV terms; vectors answer anyway | `math-explainer` ME-HOOK (the honest failure) |
| Static-host friendly | Cloudflare Pages, no server | `wrangler.toml` |

### Eliminated from Scope

| Eliminated Item | Why Eliminated |
|-----------------|----------------|
| Using the real WASM `terraphim_rolegraph_browser` | Adds async init + worker complexity for zero pedagogical gain over a faithful JS port of a 40-line algorithm; revisited only if JS port diverges |
| Narrated video (franken_manim) | User asked for an interactive page, not a video; the video skill supplies method (facts, storyboard, gates), not the deliverable |
| Three.js/WebGL | <50 nodes → SVG is simpler and more accessible |
| Editing the existing prose pages | Keep them stable; link to the new page instead |

## Dependencies

### External Dependencies

| Dependency | Version | Risk | Alternative |
|------------|---------|------|-------------|
| None (vanilla JS) | — | — | — |

### Prior Art

- `docs/src/scorers/graph-embedding-analysis.md` (terraphim-ai): Terraphim vs
  Cleora table — reuse its comparison dimensions.
- `static/demos/synonym-search/baseline-role.json`: real thesaurus JSON shape
  `{name, data: {term → {id, nterm, display_value?}}}`.
- `graph_embeddings_tutorial.rs` example in terraphim-core — walking example.

## Risks and Unknowns

### Known Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `zola build` fails on 0.23.6 (issue #6) | High | Blocks local verification only | Verify with available tooling; flag in PR; do not silently "fix" theme |
| JS port diverges from Rust semantics | Medium | Page teaches wrong algorithm | Oracle-check: port both `insert_document`/`query_graph` in Python, generate golden vectors, assert JS output matches |
| Dense-embedding side seen as strawman | Medium | Credibility loss | Label simulated latencies; show vectors *winning* on OOV terms |
| Mobile interaction cramped | Medium | Poor UX | Tap targets ≥44px, stacked panels, no hover-required flows |

### Open Questions

1. Placement: new `docs/` page vs new `explainers/` section — **decision
   deferred to design; default `docs/`** (least new IA).
2. Dataset: reuse `baseline-role.json` (real, already published) vs craft a
   systems-engineering mini-thesaurus matching the docs' raft/consensus
   example — **default: raft/consensus-style KG for continuity with
   `docs/graph-embeddings.md`**, data file in the same thesaurus JSON shape.

### Assumptions Explicitly Stated

| Assumption | Basis | Risk if Wrong | Verified? |
|------------|-------|---------------|-----------|
| Page embeds HTML/JS via a dedicated template + `custom_js` block | `base.html` tail | Falls back to inline `<script>` in markdown | Yes |
| Small hand-rolled AC in JS can reproduce LeftmostLongest results | aho-corasick crate semantics | Use longest-match scan instead (identical output on small input) | Design will pin exact matching semantics |

### Multiple Interpretations Considered

| Interpretation | Implications | Chosen? |
|----------------|--------------|---------|
| "Visual explanation" = video explainer via franken_manim | Weeks of render work; not interactive | Rejected — user explicitly wants an interactive page |
| Interactive page embedded in the site | One new content page + static JS assets | Chosen |
| Upgrade existing docs page in place | Fewer files, but mixes long prose with interactive blocks | Rejected — new page, cross-linked |

## Research Findings

### Key Insights

1. The entire Terraphim "embedding" is two integer counters and a pairing
   function — explainable enough to run live in the browser. The demo *is*
   the algorithm.
2. `edge.rank` is constant 1 in current code (only `doc_hash` per-doc counts
   grow); the explainer should show `doc_hash` counts honestly rather than
   repeat the prose's looser description.
3. Edges are *directed* (Cantor pairing of ordered consecutive matches) —
   "co-occurrence" is really "adjacency in matched-term order". This is a
   distinctive, teachable detail.
4. The strongest contrast with traditional graph embeddings (node2vec etc.)
   is *when* computation happens: they amortise a training pass into vectors;
   Terraphim does all its work at index time in counters and nothing at
   query time but lookup and sum.

### Comparative landscape (for content accuracy)

| Family | Mechanism | Vector? | Training | Update cost | Explainability |
|--------|-----------|---------|----------|-------------|----------------|
| Dense text embeddings (BERT/OpenAI) | Transformer → R^d | Yes | Heavy | Re-embed corpus | None |
| DeepWalk / node2vec | Random walks + skip-gram | Yes | Walks + SGD | Re-walk + retrain | None |
| GCN / GraphSAGE | Neural message passing | Yes | GPU training | Retrain | Low |
| TransE / RotatE (KGE) | Relational vector algebra | Yes | Embedding opt. | Retrain | Low |
| Cleora | Iterative averaging over adjacency | Yes | Cheap (CPU) | Re-embed | Medium |
| **Terraphim RoleGraph** | AC match → consecutive-pair edges → integer counts | **No** | **None** | **O(1) per doc** | **Full trace** |

## Recommendations

### Proceed/No-Proceed

Proceed. The change is one content page, one template, three static assets —
small, reversible, high explanatory value.

### Scope Recommendations

- One page, ~5 interactive scenes + a comparison table + honest-limits
  section. No framework. No video.
- Cross-link from `docs/graph-embeddings.md` and
  `capabilities/graph-embeddings.md` (one line each).

## Next Steps

1. Design doc (Phase 2): scene-by-scene interaction spec, file changes,
   oracle/test strategy.
2. Human approval gate.
3. Implement + `zola build` verify + Gitea issue tracking.

## Appendix

### Reference Materials

- `terraphim-core/crates/terraphim_rolegraph/src/lib.rs` (algorithm)
- `terraphim-core/crates/terraphim_types/src/graph.rs` (Node/Edge/Thesaurus)
- `terraphim-ai/docs/src/scorers/graph-embedding-analysis.md` (Cleora comparison)
- `content/docs/graph-embeddings.md`, `content/posts/why-graph-embeddings-matter.md`
- `static/demos/synonym-search/baseline-role.json` (thesaurus JSON shape)
- Skills: `interactive-visualization-creator`, `terraphim-essentialist-design`,
  `math-explainer-videos…` (method: oracle-checked numbers, honest hook)

### The exact scoring path (source-verified)

```text
insert_document(doc):
    matches = ac.find_iter(doc.text) -> [id…]          # LeftmostLongest
    for (a, b) in consecutive(matches):
        e = magic_pair(a, b)                          # directed edge id
        edge[e].doc_hash[doc] += 1                    # per-doc pair count
        node[a].rank += 1 ; node[b].rank += 1

query_graph(q):
    for id in ac.find_iter(q):
        for e in node[id].connected_with:
            for (doc, r) in edge[e].doc_hash:
                score[doc] += node[id].rank + edge[e].rank + r
    sort desc by score, asc by doc_id
```
