Graph embeddings you can watch being built

A Terraphim graph embedding is not a point in a vector space. It is a node plus its directed edges and a set of integer counters — synonyms that map to the concept, and the concepts that appear next to it. That is easier to show than to say, so the new page on terraphim.ai shows it: the actual Rust terraphim_rolegraph crate, compiled to WebAssembly, running the algorithm in your browser. Nothing on screen is staged or ported — the counters you watch increment are the same code paths the crate's own tests exercise.

Type into the matcher and a real Aho-Corasick automaton scans the text in a single pass, returning concept ids: 'raft quorum consensus' fires #1 raft, #6 quorum, #2 consensus. Index the eight-document corpus one click at a time and adjacent matches become directed edges while node and edge counters increment — 10 concepts, 23 edges at the end, including a title-match self-loop that falls out of Rust's Document::to_string() semantics rather than any special-casing.

Query 'consensus' and the ledger decomposes the winner: doc-membership earns 19 as node 7 + edge 1 + doc 2, plus node 7 + edge 1 + doc 1 through a second edge. Every point of the sum is a named node, a named edge and an inspectable count. That is the explainability argument made concrete.

The honesty runs both ways. 'byzantine fault tolerance' hits no thesaurus term, and the graph returns an empty set while the illustrative vector panel still produces fuzzy scores — the failure modes are the teaching point. Add a synonym and the automaton rebuild is measured live in single-digit milliseconds, against the cost column of a retraining pipeline.

The comparison table covers node2vec, GCN, TransE, Cleora and API vector databases across training, update cost, explainability, determinism and memory — and points at the hybrid retrieval that already exists in the codebase: query_graph_with_trigger_fallback (TF-IDF trigger index) and search_sessions_hybrid (BM25 fused with knowledge-graph boosts).

https://terraphim.ai/docs/graph-embeddings-interactive/
