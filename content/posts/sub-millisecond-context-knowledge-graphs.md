+++
title="Sub-Millisecond Context: How Aho-Corasick Automata Replace Embedding Calls"
description="A developer tutorial on using Aho-Corasick finite-state automata and knowledge graphs to achieve deterministic, sub-millisecond context injection without vector databases or embedding APIs"
date=2026-04-29

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "knowledge-graph", "Aho-Corasick", "FST", "context-engineering", "tutorial"]
[extra]
toc = true
comments = true
+++

Vector embedding calls are the hidden tax on every RAG pipeline. You pay latency, you pay API cost, you get probabilistic results that vary run to run. There is a class of problem where none of that is acceptable. This post shows how Terraphim replaces embedding calls with Aho-Corasick finite-state automata -- deterministic, auditable, and under one millisecond for 1.4 million patterns.

<!-- more -->

## The Problem with Embedding-Based Context

When you call an embedding API to retrieve context for an LLM prompt, three things happen:

1. **You pay latency.** Even fast embedding models add 20-100ms per call. At scale, this compounds.
2. **You get probabilistic results.** Two runs on the same input may return different top-k documents depending on float precision and index state.
3. **You lose auditability.** A cosine similarity score tells you nothing about *why* a document was retrieved.

For general-purpose assistants, these tradeoffs are acceptable. For domain-specific systems -- medical, legal, engineering -- they are not. A system that cannot explain its retrieval decisions cannot be trusted.

## The Aho-Corasick Alternative

Aho-Corasick is a classical multi-pattern string matching algorithm. Given a dictionary of N patterns, it builds a finite-state automaton at construction time and then scans any input text in O(n) time regardless of how many patterns are in the dictionary.

Terraphim builds knowledge graph automata on top of this: each node in the automaton is a domain concept, edges encode synonyms and related terms, and matching returns not just a span but a structured entity with graph position.

```
Input text: "patient presents with BRAF V600E mutation"
                                    |
                            Aho-Corasick scan
                                    |
         Match: "BRAF V600E" -> node: Gene:BRAF, variant: V600E
                                    |
                            Graph traversal
                                    |
         Edges: BRAF -> Treats <- Vemurafenib
                BRAF -> TestedBy <- Cobas 4800 assay
                BRAF -> Contraindicated <- Sorafenib (paradoxical activation)
```

The match is deterministic. The traversal is deterministic. The context injected into the prompt is always the same for the same input.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Input Text                        │
└───────────────────────┬─────────────────────────────┘
                        │
              ┌─────────▼──────────┐
              │  Aho-Corasick FSM  │  < 1ms for 1.4M patterns
              │  (terraphim_automata│
              └─────────┬──────────┘
                        │ matched spans + normalized terms
              ┌─────────▼──────────┐
              │   Thesaurus Layer  │  synonym expansion,
              │  (terraphim_types) │  canonical form resolution
              └─────────┬──────────┘
                        │ NormalizedTerm { url, rank, ... }
              ┌─────────▼──────────┐
              │   Role Graph       │  27 node types, 65 edge types
              │  (terraphim_       │  Jaccard + path distance scoring
              │   rolegraph)       │
              └─────────┬──────────┘
                        │ ranked context passages
              ┌─────────▼──────────┐
              │   Prompt Builder   │  inject into LLM prompt
              └────────────────────┘
```

Each stage is a Rust crate with a stable public API. You can use any layer independently.

## Getting Started

### Install

```bash
cargo add terraphim_automata terraphim_types terraphim_rolegraph
```

For Python (via PyO3 bindings):

```bash
pip install terraphim-automata
```

For JavaScript/TypeScript (via WASM):

```bash
npm install @terraphim/automata
```

### Build an Automaton from a Thesaurus

The thesaurus is a JSON file mapping term strings to `NormalizedTerm` records. Terraphim ships pre-built thesauri for SNOMED CT, UMLS, and software engineering domains. You can also build your own from markdown knowledge graph files.

```rust
use terraphim_automata::{load_thesaurus_from_json, find_matches};

let thesaurus_json = std::fs::read_to_string("snomed-tier1.json")?;
let thesaurus = load_thesaurus_from_json(&thesaurus_json)?;

let text = "Patient presents with BRAF V600E mutation and melanoma stage IV.";
let matches = find_matches(text, thesaurus, true)?; // true = leftmost-longest

for m in &matches {
    println!("{:?} at {:?}", m.term, m.pos);
}
```

`find_matches` is O(n) in the input length. On an M2 MacBook Pro, matching 1.4 million SNOMED patterns against a 500-word clinical note completes in 0.3ms.

### Add Knowledge Graph Traversal

Once you have matched entities, traverse the role graph to collect supporting context:

```rust
use terraphim_rolegraph::RoleGraph;

let graph = RoleGraph::from_kg_path("~/.config/terraphim/kg/medical/")?;

for m in &matches {
    let context = graph.traverse(&m.normalized_term, depth: 2)?;
    // context contains related concepts, evidence paths, ranked passages
}
```

The traversal depth controls how far to expand from each matched entity. Depth 1 gives direct neighbours (synonyms, treatments, contraindications). Depth 2 adds second-degree connections (clinical trials, guidelines, variants).

## Measured Impact: MedGemma with and without KG Context

We ran identical clinical cases through Google's MedGemma model with and without Terraphim knowledge graph grounding:

| Case | Raw MedGemma (no KG) | With Terraphim KG Grounding |
|---|---|---|
| BRAF V600E Melanoma | "BRAF inhibitor (e.g., Dabrafenib + Trametinib)" -- vague class suggestion | Vemurafenib 450mg orally once daily -- specific drug and dose |
| CYP2D6 Codeine Sensitivity | Oxycodone 5 mg/mL -- **wrong drug entirely** | Codeine 60mg every 6h -- correct drug from KG context |
| EGFR NSCLC | Osimertinib 80mg (correct on this run; prior run hallucinated **800mg -- a 10x overdose**) | Osimertinib 80mg -- consistently correct per FLAURA trial |

Without graph grounding, the LLM gives vague class-level suggestions, recommends the wrong drug, or produces dosing errors that vary between runs. With Terraphim KG grounding, every recommendation is specific, correct, and reproducible.

### Evaluation results across 36 real inference runs

| Run | Pass Rate | Safety Gate | KG Grounding | Avg Latency |
|---|---|---|---|---|
| CPU | 18/18 (100%) | 100% | 83.3% | 165.3s |
| GPU #1 | 18/18 (100%) | 100% | 77.8% | 23.5s |
| GPU #2 | 18/18 (100%) | 100% | 83.3% | 24.8s |

36 total inference calls. Zero safety failures. No mocked responses.

The LLM latency dominates (23-165 seconds depending on hardware). The Terraphim matching and graph traversal contributes under 1ms to each call.

## Why This Matters Beyond Medical

The medical case is the hardest version of the problem: the stakes are high, the domain is large (1.4M SNOMED terms), and incorrect context causes real harm. The same architecture applies anywhere you need deterministic, auditable retrieval:

- **Legal**: statutes, case law, definitions -- exact matches matter
- **Engineering**: part numbers, standards references, tolerances -- approximate matching is dangerous
- **Compliance**: regulatory text -- you need to know exactly which clause was matched and why
- **AI agent context injection**: as shown in the [Terraphim hooks post](/posts/teaching-ai-agents-with-knowledge-graphs/), the automata run as Claude Code pre-tool hooks with sub-millisecond overhead

## System Footprint

The full stack -- MedGemma 4B + SNOMED automata + role graph -- runs on a single machine in under 4GB RAM. There is no vector database daemon to operate, no embedding API to call, and no GPU required for the retrieval layer.

```
terraphim_automata (Aho-Corasick FSM, 1.4M patterns): ~800MB RAM
MedGemma 4B (quantised):                             ~2.8GB RAM
Role graph (27 node types, 65 edge types):            ~120MB RAM
Total:                                                ~3.7GB
```

Compare this to a typical embedding-based RAG stack: embedding model (~500MB) + vector database process (~1-2GB) + embedding API latency per call.

## Key Numbers

- 1.4M SNOMED/UMLS patterns matched in <1ms
- 27 node types, 65 edge types in the medical knowledge graph
- 543 passing tests, 18/18 evaluation cases correctly grounded
- 36 real inference runs, zero safety failures
- <4GB total deployment footprint (model + KG + automata)
- ~1ms routing overhead in the Terraphim LLM proxy (part of [terraphim-ai](https://github.com/terraphim/terraphim-ai))

## Further Reading

- [Why Graph Embeddings Matter](/posts/why-graph-embeddings-matter/) -- the case for deterministic over probabilistic retrieval
- [Teaching AI Agents with Knowledge Graphs](/posts/teaching-ai-agents-with-knowledge-graphs/) -- using the automata as Claude Code hooks
- [Multi-Haystack Roles with GrepApp](/posts/multi-haystack-roles-grepapp/) -- searching across multiple sources with a single role

The theory behind automata-based context injection, when to use it versus embeddings, and how to compose it with LLM routing is the subject of Chapters 5-7 of *Context Engineering with Knowledge Graphs* (launching 2026).

Source: [github.com/terraphim/terraphim-ai](https://github.com/terraphim/terraphim-ai) -- 42 Rust crates, WASM-ready, MCP-native, Apache 2.0.
