+++
title = "Graph Embeddings"
description = "Deterministic graph-based embeddings via Aho-Corasick and RoleGraph -- no neural vectors, no GPUs"
date = 2026-04-15
weight = 10

[taxonomies]
categories = ["Capability"]
tags = ["graph-embeddings", "aho-corasick", "knowledge-graph", "search"]

[extra]
toc = true
+++

Terraphim uses **graph embeddings** instead of neural vector embeddings. Terms and concepts
are represented as nodes in a role-specific knowledge graph, with relationships encoded as
edges. Matching a query against a graph is deterministic, auditable, and fast.

See the [full design note](/docs/graph-embeddings) for how RoleGraph composes
Aho-Corasick matching with PageRank ordering to produce ranked results in
sub-millisecond time, without any floating-point vector math.

## Why graph embeddings

- **Deterministic**: same query, same graph, same result. No stochastic retrieval.
- **Explainable**: every matched node traces back to a term in the thesaurus.
- **Efficient**: 15-20 MB RAM for a typical graph, no GPU required.
- **Domain-adapted**: each role has its own vocabulary and relationships.

This is a fundamentally different model from dense vector retrieval. It is what makes
Terraphim run on a laptop, a Raspberry Pi, or inside a browser extension.
