New interactive page on terraphim.ai: a graph embedding here is not a point in a vector space but a node plus its directed edges and integer counters — and the page proves it by running the actual Rust terraphim_rolegraph crate, compiled to WebAssembly, in your browser. Nothing is staged or ported: the counters you watch increment are the same code paths the Rust tests exercise.

Type text and watch Aho-Corasick matching return concept ids in a single pass ('raft quorum consensus' -> #1 raft, #6 quorum, #2 consensus). Index eight documents step by step and watch adjacent matches become directed edges — 10 concepts, 23 edges, including the title-match self-loop that Rust's Document::to_string() semantics predict. Query 'consensus' and read the ledger: doc-membership earns 19 as node 7 + edge 1 + doc 2 + node 7 + edge 1 + doc 1 — every point of the sum is a named node, a named edge and a count.

The comparison is honest in both directions: 'byzantine fault tolerance' hits no thesaurus term and the graph returns an empty set while the illustrative vector panel still gives a fuzzy score; adding a synonym triggers a real automaton rebuild measured in single-digit milliseconds. The page compares node2vec, GCN, TransE, Cleora and API vector DBs across training, update cost, explainability, determinism and memory, and references the hybrid retrieval that is already implemented (TriggerIndex TF-IDF fallback via query_graph_with_trigger_fallback, and search_sessions_hybrid fusing BM25 with knowledge-graph boosts).

https://terraphim.ai/docs/graph-embeddings-interactive/

What would you index first on a graph you can watch being built?
