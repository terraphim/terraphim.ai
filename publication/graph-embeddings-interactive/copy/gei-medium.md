*Originally published at [terraphim.ai](https://terraphim.ai/docs/graph-embeddings-interactive/) — where this article is fully interactive.*

# Graph Embeddings You Can Watch Being Built

A graph embedding does not have to be a vector. In Terraphim it is a node plus its directed edges and a set of integer counters: the synonyms that map to the concept, and the concepts that appear next to it in real text. That claim is easy to make and hard to feel, so we built a page that proves it — the actual Rust `terraphim_rolegraph` crate, compiled to WebAssembly, running the algorithm in your browser. Nothing on screen is staged or reimplemented; the counters you watch increment are the same code paths the crate's own tests exercise.

**Live Aho-Corasick matching.** Type any sentence and a real automaton compiled from a 19-term thesaurus scans it in a single pass, reporting concept ids. `raft quorum consensus` fires `#1 raft`, `#6 quorum`, `#2 consensus`.

**Step-by-step indexing.** Index the eight-document corpus one click at a time. Adjacent concept matches become directed edges; node and edge counters increment. The end state — 10 concepts, 23 directed edges — includes a `raft → raft` self-loop that falls out of `Document::to_string()` matching titles as well as bodies.

**A query ledger you can audit.** Query `consensus` and `doc-membership` earns 19 points decomposed as `node 7 + edge 1 + doc 2` plus `node 7 + edge 1 + doc 1` through a second edge. Every point of the sum is a named node, a named edge and an inspectable count.

**Honest failure.** `byzantine fault tolerance` matches no thesaurus term and the graph returns an empty set while the illustrative vector panel still scores. Dense retrieval always answers; symbolic retrieval tells you when it does not know.

**Real rebuild cost.** Add a synonym and the crate's `rebuild_automata` runs and is timed live in single-digit milliseconds — the cost-of-change argument against retraining pipelines.

The page compares node2vec, GCN, TransE, Cleora and API vector databases across training, update cost, explainability, determinism and memory — and references the hybrid retrieval already implemented: `query_graph_with_trigger_fallback` (a TF-IDF trigger index) and `search_sessions_hybrid` (BM25 fused with knowledge-graph boosts).

Try it: https://terraphim.ai/docs/graph-embeddings-interactive/
