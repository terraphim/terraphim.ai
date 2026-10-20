+++
title = "Graph Embeddings, Explained Interactively"
description = "Watch Terraphim's graph embeddings work — live Aho-Corasick matching, co-occurrence edges and integer rank — and compare them honestly with vector embeddings and traditional graph embeddings"
date = 2026-10-20
template = "explainer.html"

[taxonomies]
categories = ["Documentation"]
tags = ["graph-embeddings", "knowledge-graph", "aho-corasick", "interactive", "explainer"]

[extra]
toc = true
+++

Most pages about embeddings show you a picture of some dots and ask you to trust the maths.
This one is different: **the Terraphim side of every demo below runs the real algorithm** —
the actual `terraphim_rolegraph` Rust crate, compiled to WebAssembly and executing in your
browser — on a real thesaurus and corpus. Nothing is staged or ported: the counters you watch
increment are the same code paths the Rust tests exercise.

<div class="tge-note">
<strong>How to read this page.</strong> Each scene has controls. Press buttons, type queries,
index your own sentence. If a number is on screen, it was computed in your browser a moment
ago. Where the comparison side is simulated rather than real, it says so on the panel.
<span class="tge-kbd-hint">Esc clears highlights and ledgers; your indexed data stays.</span>
</div>

## Two retrieval worlds, one question

The same eight documents, two retrieval systems. On the left, the classic picture: every
document is a point in a high-dimensional space; a query lands as another point; similarity
is distance. On the right, the Terraphim graph: every concept is a node; documents feed
co-occurrence counters; a query lights up a path.

Run a query — including `byzantine fault tolerance`, which is deliberately absent from the
thesaurus — and watch what each side does with it.

<div class="tge-scene" id="scene-worlds">
  <div class="tge-controls" id="tge-q-presets">
    <input type="text" id="tge-q" value="consensus" aria-label="Query for both systems">
    <button class="tge-btn primary" id="tge-q-run"><i class="fa-solid fa-play" aria-hidden="true"></i> Run</button>
    <button class="tge-btn" data-q="consensus">consensus</button>
    <button class="tge-btn" data-q="leader election">leader election</button>
    <button class="tge-btn" data-q="raft consensus">raft consensus</button>
    <button class="tge-btn" data-q="byzantine fault tolerance">byzantine fault tolerance</button>
  </div>
  <div class="tge-split wide-right">
    <div class="tge-panel">
      <h4>Dense vectors <span class="tge-tag sim">illustrative</span></h4>
      <svg id="vec-svg" class="tge-graph" viewBox="0 0 360 260" role="img" aria-label="Simulated dense embedding space"></svg>
      <p class="tge-caption">Every dot is a document. The ring is a cosine-similarity radius.
      You get a score — 0.98, 0.87, 0.76 — and nothing else. There is no answer to
      <em>why</em> this document matched.</p>
    </div>
    <div class="tge-panel">
      <h4>Terraphim RoleGraph <span class="tge-tag real">real algorithm</span></h4>
      <svg id="world-graph-svg" class="tge-graph" viewBox="0 0 820 520" role="img" aria-label="Live Terraphim knowledge graph"></svg>
      <p class="tge-caption">Nodes are concepts; numbers inside are <code>node.rank</code> —
      co-occurrence counts. Lit nodes and edges are the ones the query actually traversed.</p>
    </div>
  </div>
  <div id="tge-why" class="tge-note" aria-live="polite"></div>
</div>

## Scene one: how the text is read

Before anything is a graph, there is a dictionary. The role's **thesaurus** maps synonyms to
normalised concepts — `leader election` and `election` are the same node, id 3. At startup the
thesaurus compiles into an Aho-Corasick automaton: a finite-state machine that scans text in a
single pass, regardless of how many patterns it holds.

Watch it read. The matcher runs **leftmost-longest**, case-insensitive: at each position it
takes the longest pattern that fits, then jumps past it. Type anything — the highlights and the
concept sequence update live.

<div class="tge-scene" id="scene-matcher">
  <h3>Aho-Corasick matching <span class="tge-tag real">real algorithm</span></h3>
  <div class="tge-controls">
    <input type="text" id="tge-matcher-input" aria-label="Text to scan with the Aho-Corasick automaton">
  </div>
  <div class="tge-text" id="tge-matcher-text"></div>
  <div class="tge-chips" id="tge-matcher-chips" role="status" aria-live="polite" aria-atomic="true"></div>
  <p class="tge-caption">Try <span class="tge-mono">a consensus algorithm</span> vs
  <span class="tge-mono">a consensus</span>: <code>consensus algorithm</code> wins as one match,
  not two. That is LeftmostLongest. Overlapping terms collapse into a single concept id —
  and that ordered sequence of ids is all the indexer sees.</p>
</div>

## Scene two: indexing — where the "embedding" is built

Here is the whole trick, and it is smaller than you expect. When a document is indexed:

1. The automaton scans it once, producing the matched concept sequence you saw above.
   (The crate matches `title + body` — `Document::to_string()` — which is why "Raft notes"
   adds a `raft → raft` self-loop: the title itself matches.)
2. Each **consecutive pair** `(a, b)` becomes a directed edge `magic_pair(a, b)` — an integer
   key computed by a Cantor-style pairing function, so `(raft → consensus)` and
   `(consensus → raft)` are different edges.
3. `node.rank += 1` for both endpoints; `edge.doc_hash[doc] += 1` counts how often that pair
   appeared in that document.

That is the embedding. **What a concept "is" here: a node plus its edges in conceptual
space** — the synonyms that map to it and the concepts that appear next to it — not a point
in a vector space. Press "Index next" a few times and watch the graph accrete; then index
your own sentence (only thesaurus terms count).

<div class="tge-scene" id="scene-indexer">
  <h3>Build the graph <span class="tge-tag real">real algorithm</span></h3>
  <div class="tge-controls">
    <button class="tge-btn primary" id="tge-index-next"><i class="fa-solid fa-forward-step" aria-hidden="true"></i> Index next</button>
    <button class="tge-btn" id="tge-index-all"><i class="fa-solid fa-forward" aria-hidden="true"></i> Index all</button>
    <button class="tge-btn" id="tge-index-reset"><i class="fa-solid fa-rotate-left" aria-hidden="true"></i> Reset</button>
    <span class="tge-chip" id="tge-stats" aria-live="polite"></span>
  </div>
  <div class="tge-queue" id="tge-queue"></div>
  <div id="tge-index-matches"></div>
  <div class="tge-controls">
    <input type="text" id="tge-own-text" placeholder="Index your own sentence — try mentioning raft, quorum, leader…" aria-label="Index your own sentence">
    <button class="tge-btn" id="tge-index-own"><i class="fa-solid fa-plus" aria-hidden="true"></i> Index it</button>
  </div>
  <svg id="main-graph-svg" class="tge-graph" viewBox="0 0 820 520" role="img" aria-label="Main knowledge graph view"></svg>
  <p class="tge-caption">Edge thickness ∝ total document count on that pair. Loops are real:
  <code>partition tolerance → partition tolerance</code> and <code>leader → leader</code> appear
  when the same concept is matched twice in a row. Re-indexing removes a document's
  contributions before re-counting — replace semantics. Honest caveat: removal decrements
  node rank once per <em>edge</em>, while insertion counts once per pair <em>occurrence</em>,
  so a document that repeats the same directed pair leaves a small rank residual on re-index.
  That is the Rust implementation's real behaviour, running live — not smoothed over.</p>
</div>

## Scene three: asking a question

Querying is the mirror image. The automaton matches the query terms to node ids; for each
matched node, the engine walks its edges; for every document on each edge it adds:

<pre class="tge-mono">score += node.rank + edge.rank + doc_hash[doc]</pre>

Documents are sorted by the sum. And because every point of the sum comes from a named node,
a named edge and a count you can inspect, the ranking is **auditable** — click a query and read
the ledger. This is the part a cosine score cannot give you.

<div class="tge-scene" id="scene-query">
  <h3>Query the graph <span class="tge-tag real">real algorithm</span></h3>
  <div class="tge-controls" id="tge-query-presets">
    <input type="text" id="tge-query-input" value="consensus" aria-label="Graph query">
    <button class="tge-btn primary" id="tge-query-run"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i> Query</button>
    <button class="tge-btn" data-q="consensus">consensus</button>
    <button class="tge-btn" data-q="leader election">leader election</button>
    <button class="tge-btn" data-q="raft">raft</button>
    <button class="tge-btn" data-q="quorum">quorum</button>
    <button class="tge-btn" data-q="byzantine fault tolerance">byzantine fault tolerance</button>
  </div>
  <div id="tge-results" aria-live="polite"></div>
</div>

## Scene four: when does the work happen?

The deepest difference is not the data structure — it is **where computation lives**.

Traditional graph embeddings — DeepWalk, node2vec, GraphSAGE, TransE, Cleora — front-load
everything: random walks or message passing produce dense vectors once, then queries are cheap
ANN lookups. Adding a term means re-walking and re-training. Terraphim inverts this: all the
work is tiny counters at index time; a query is a lookup and a sum.

Add a synonym right now. The Terraphim column measures the real rebuild time in your browser.

<div class="tge-scene" id="scene-pipeline">
  <h3>Cost of change</h3>
  <div class="tge-controls">
    <input type="text" id="tge-syn-input" placeholder="new synonym, e.g. leader selection" aria-label="New synonym to add to the thesaurus">
    <button class="tge-btn primary" id="tge-syn-add"><i class="fa-solid fa-bolt" aria-hidden="true"></i> Add synonym</button>
    <div id="tge-syn-result" aria-live="polite"></div>
  </div>
  <div class="tge-cols">
    <div class="tge-col">
      <h5>Terraphim RoleGraph</h5>
      <div class="tge-step free" id="tge-syn-flash"><i class="fa-solid fa-pen" aria-hidden="true"></i>Edit thesaurus → rebuild automaton<span class="tge-time" id="tge-syn-time">~ms</span></div>
      <div class="tge-step"><i class="fa-solid fa-file-import" aria-hidden="true"></i>Index doc: one AC scan + counter increments<span class="tge-time">µs</span></div>
      <div class="tge-step free"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>Query: match + traverse + integer sum<span class="tge-time">sub-ms</span></div>
      <div class="tge-step free"><i class="fa-solid fa-scale-balanced" aria-hidden="true"></i>Answer to "why?": full provenance<span class="tge-time">free</span></div>
    </div>
    <div class="tge-col">
      <h5>Learned graph embeddings <span class="tge-tag sim">node2vec / GCN / TransE / Cleora</span></h5>
      <div class="tge-step cost"><i class="fa-solid fa-shoe-prints" aria-hidden="true"></i>Random walks / message passing<span class="tge-time">corpus pass</span></div>
      <div class="tge-step cost"><i class="fa-solid fa-brain" aria-hidden="true"></i>Skip-gram / gradient training<span class="tge-time">minutes–hours</span></div>
      <div class="tge-step"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>Query: cosine vs ANN index<span class="tge-time">ms</span></div>
      <div class="tge-step cost"><i class="fa-solid fa-rotate" aria-hidden="true"></i>New term → re-embed affected subgraph<span class="tge-time">retrain</span></div>
    </div>
    <div class="tge-col">
      <h5>Dense text embeddings <span class="tge-tag sim">API + vector DB</span></h5>
      <div class="tge-step cost"><i class="fa-solid fa-cloud-arrow-up" aria-hidden="true"></i>Embed every document via API<span class="tge-time">50–500 ms/doc</span></div>
      <div class="tge-step cost"><i class="fa-solid fa-database" aria-hidden="true"></i>Build ANN index (HNSW)<span class="tge-time">build pass</span></div>
      <div class="tge-step"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>Query: embed query + ANN scan<span class="tge-time">5–50 ms + API</span></div>
      <div class="tge-step cost"><i class="fa-solid fa-rotate" aria-hidden="true"></i>New vocabulary → re-embed corpus<span class="tge-time">retrain/index</span></div>
    </div>
  </div>
  <p class="tge-caption">Timings on the Terraphim column are measured live in this page; the other
  columns are indicative ranges consistent with published measurements, shown for comparison.</p>
</div>

## The honest comparison

| Aspect | Learned graph embeddings (node2vec, GCN, TransE, Cleora) | Dense text embeddings (API + vector DB) | Terraphim graph embeddings |
|---|---|---|---|
| What a concept "is" | A point in ℝᵈ learned from walks/adjacency | A point in ℝᵈ learned from text | A node + its edges + integer counters |
| Training | Walks + SGD / iterative propagation | Pre-trained model; per-doc embed call | None — counters at index time |
| Query mechanism | Vector → ANN cosine | Vector → ANN cosine | AC match → traverse → integer sum |
| Multi-hop semantics | Yes — walks/message passing | Indirect | Neighbourhood only (1 hop) |
| Unseen vocabulary | Degrades silently | Generalises (that's the point) | Returns nothing — honestly |
| Update cost | Re-embed affected subgraph | Re-embed document | Edit thesaurus, ~ms rebuild |
| Explainability | Vector distance only | Vector distance only | Every contribution named and countable |
| Memory / hardware | Float32 × nodes × dims | ANN index + API | ints; 15–20 MB typical; runs on a Pi |
| Determinism | Seed-dependent | Model/version dependent | Same input → same output, always |

## Where the graph loses — honestly

- **Out-of-vocabulary blindness.** If it is not in the thesaurus, it does not exist. The
  `byzantine fault tolerance` query above returns an empty set while the vector panel cheerfully
  returns neighbours. Domain coverage is an authoring problem, not a learning problem.
- **Frequency bias.** `node.rank` counts co-occurrences, not importance. Popular concepts
  dominate. Hybrid search already exists to soften this and is implemented, not proposed:
  `query_graph_with_trigger_fallback` falls back to a `TriggerIndex` (TF-IDF over trigger
  descriptions) inside the rolegraph itself — exposed in the editor bridge as the
  `fallback` query mode — and `search_sessions_hybrid` in `terraphim_sessions` fuses BM25
  scores with knowledge-graph boosts.
- **One hop.** The graph captures adjacency, not transitive similarity. Two concepts that never
  sit next to each other in a document stay unlinked, however related they are.
- **Coarse ties.** Integer sums collide; ties break on document id. It is explainable, not subtle.

## From page to code

Every label above maps to a real symbol:

- `RoleGraph::new_sync` → builds the automaton (`MatchKind::LeftmostLongest`, case-insensitive)
- `insert_document` → `find_matching_node_ids` → `tuple_windows` → `add_or_update_document`
- `magic_pair` / `magic_unpair` → directed edge ids
- `query_graph` → the `node.rank + edge.rank + doc_hash` sum and sort you watched
- `remove_document_contributions` → the replace semantics that made re-indexing idempotent

One honest detail the prose docs gloss over: `edge.rank` is currently always 1 — the real
per-document count lives in `edge.doc_hash`, which is why the ledger above shows the
document count rather than an edge rank. This page shows the code, not the approximation.

The reference text lives at [Graph Embeddings](/docs/graph-embeddings/); the short version of
*why it matters* is in [Why Graph Embeddings Matter](/posts/why-graph-embeddings-matter/).
