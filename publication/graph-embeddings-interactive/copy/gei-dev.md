*Originally published at [terraphim.ai](https://terraphim.ai/docs/graph-embeddings-interactive/) — where this article is fully interactive.*

# Graph Embeddings You Can Watch Being Built

A graph embedding does not have to be a vector. In Terraphim it is a node plus its directed edges and a set of integer counters: the synonyms that map to the concept, and the concepts that appear next to it in real text. That claim is easy to make and hard to feel, so we built a page that proves it — the actual Rust `terraphim_rolegraph` crate, compiled to WebAssembly, running the algorithm in your browser. Nothing on screen is staged or reimplemented; the counters you watch increment are the same code paths the crate's own tests exercise.

## What the page does

**Live Aho-Corasick matching.** Type any sentence into the matcher and a real automaton — compiled from a 19-term thesaurus — scans it in a single pass and reports concept ids. `raft quorum consensus` fires `#1 raft`, `#6 quorum`, `#2 consensus`. The matching is case-folding and leftmost-longest, exactly as the Rust crate configures it.

**Step-by-step indexing.** Index the eight-document corpus one click at a time. Each document is matched, adjacent concept matches become directed edges, and node and edge counters increment. The end state — 10 concepts, 23 directed edges — includes a `raft → raft` self-loop that falls out of `Document::to_string()` matching titles as well as bodies. No special-casing; that is what the Rust code does, so that is what the page shows.

**A query ledger you can audit.** Query `consensus` and the winner, `doc-membership`, earns 19 points decomposed as `node 7 + edge 1 + doc 2` through one edge plus `node 7 + edge 1 + doc 1` through another. Every point of the sum is a named node, a named edge and an inspectable document count. That is the explainability argument for symbolic retrieval made concrete: there is no answer to "why 0.87" for a dense vector, and a complete answer here.

**Honest failure.** `byzantine fault tolerance` matches no thesaurus term and the graph returns an empty set — displayed as such — while the illustrative vector panel next to it still produces fuzzy similarity scores. The contrast is the lesson: dense retrieval always answers, symbolic retrieval tells you when it does not know.

**Real rebuild cost.** Add a synonym — say `leader selection` — and the page calls the crate's `thesaurus.insert` plus `rebuild_automata`, measuring the result live (single-digit milliseconds on an M-series laptop). Set against the "update the embedding" column for node2vec, GCN or a hosted vector index, this is the cost-of-change argument.

## The honest comparison

The page includes a side-by-side table across training requirements, update cost, explainability, determinism and memory footprint for learned graph embeddings (node2vec, GCN, TransE, Cleora), dense text embeddings behind an API and vector database, and Terraphim's graph. It does not pretend the symbolic graph wins everywhere: it is blind to out-of-vocabulary terms, its ranks reflect frequency rather than importance, and its reach is one hop of adjacency.

Those gaps have engineered answers that already exist in the codebase rather than proposals: `query_graph_with_trigger_fallback` backs the graph with a TF-IDF trigger index as an opt-in fallback, and `search_sessions_hybrid` fuses BM25 full-text scoring with knowledge-graph concept boosts for session search.

## Try it

Everything above is one click away at [terraphim.ai/docs/graph-embeddings-interactive/](https://terraphim.ai/docs/graph-embeddings-interactive/). The WASM build, its provenance manifest and a conformance suite that cross-checks the browser output against an independent oracle are all in the site's repository.

What would you index first on a graph you can watch being built?
