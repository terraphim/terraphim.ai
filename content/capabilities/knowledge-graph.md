+++
title = "Knowledge Graph Engine"
description = "Build and traverse interconnected knowledge graphs with Aho-Corasick multi-pattern matching"
date = 2026-04-05
weight = 2

[taxonomies]
categories = ["Capabilities"]
tags = ["knowledge-graph", "aho-corasick", "ontology", "semantic-search"]

[extra]
toc = true
waypoint = "WP-002"
icon = "fa-solid fa-diagram-project"
+++

## Thousands of Patterns in a Single Pass

At the heart of Terraphim is a knowledge graph engine that uses **Aho-Corasick finite state automata** for multi-pattern matching. Unlike traditional keyword search, Aho-Corasick matches thousands of patterns simultaneously in O(n) time relative to the text length — regardless of how many patterns are in the graph.

## How It Works

The search pipeline operates in stages:

1. **Lexical Extraction** — Aho-Corasick automaton matches all thesaurus terms simultaneously, with case-insensitive, leftmost-longest matching
2. **Graph Traversal** — Matched nodes are traversed through the RoleGraph, accumulating node rank, edge rank, and document rank
3. **Statistical Ranking** — Pluggable scorers (BM25, BM25F, BM25+, TF-IDF, Jaccard, QueryRatio) rank results
4. **Similarity Re-ranking** — Optional fuzzy matching via Levenshtein, Jaro, or Jaro-Winkler distance

## Role-Based Knowledge Graphs

Each Terraphim role has its own separate knowledge graph containing concepts relevant to that domain, with all synonyms. A systems engineer, a project manager, and a quality analyst each see the same documents ranked differently based on their role's knowledge graph.

Knowledge graphs are built from industry standards, reference process models, handbooks, and curated taxonomies. Terraphim imports these sources and produces a graph following the SIPOC pattern — concepts at the input and output of processes, with activity names linking them.

## Dynamic Ontology

Terraphim's Dynamic Ontology enables schema-first knowledge graph construction:

- **Two-layer architecture**: Curated schema combined with an ontology catalogue
- **Normalisation**: Aho-Corasick plus fuzzy matching — no vector embeddings needed
- **Coverage governance**: Quality signals to judge extraction quality
- **Grounding metadata**: Canonical URIs for interoperability

## Synonym Control and Multilingual Matching

Users specify synonyms manually and rebuild graph embeddings within 20 milliseconds. This allows matching terms in different languages to the same concept without running language detection. There is no need for a stop-word dictionary — "The Pattern" matches exactly as a project name, even though "The" would normally be filtered as a stop word.

## Learn More

- [Graph Embeddings documentation](/docs/graph-embeddings)
- [Teaching AI Agents with Knowledge Graph Hooks](/posts/teaching-ai-agents-with-knowledge-graphs/)
- [KG-Boosted File Search](/capabilities/kg-file-search/)
- [Discussion on Discourse](https://terraphim.discourse.group/)
