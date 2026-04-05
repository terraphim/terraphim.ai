+++
title = "Graph Embeddings"
description = "Understanding Terraphim's unique graph-based embedding system"
date = 2026-04-04
+++

# Graph Embeddings

Terraphim uses a fundamentally different approach to semantic search compared to traditional vector embeddings. Instead of dense numerical vectors, Terraphim leverages **graph structure embeddings** where ranking is determined by the number of synonyms and related concepts connected to a query term in the knowledge graph.

## What are Graph Embeddings in Terraphim?

Unlike vector embeddings that represent concepts as points in a high-dimensional semantic space, Terraphim represents concepts as nodes in a **knowledge graph**. Each node is a normalized term, and edges represent co-occurrence relationships between terms found in documents.

The key insight is that **rank is defined by the number of synonyms connected to a concept**. When you search for a term, Terraphim expands your query to include all synonyms and related concepts from the knowledge graph, then traverses the graph to find documents that mention these connected concepts.

### Graph Structure

```
    "raft" ----(edge)---- "consensus"
       |                    |
    (edge)               (edge)
       |                    |
    "leader" ----(edge)---- "election"
```

When you search for "consensus algorithms", the graph traverses from the matched node to connected nodes, finding documents that mention related concepts like "raft", "leader election", and so on.

## How It Works

The Terraphim Graph (scorer) uses unique graph embeddings with the following ranking algorithm:

```
total_rank = node.rank + edge.rank + document_rank
```

Where:
- **node.rank**: Number of connections to other concepts in the graph
- **edge.rank**: Number of documents containing both connected concepts
- **document.rank**: Base ranking score of the document

### Query Expansion

When you search, Terraphim:
1. Matches your query terms against the thesaurus (normalized terms and synonyms)
2. Expands the query to include all connected synonyms and related concepts
3. Traverses the graph to find documents containing these terms
4. Ranks documents by aggregating scores from multiple graph paths
5. Returns results with explainable match reasons

## Technical Details

### Core Implementation

The graph embedding system is implemented in `crates/terraphim_rolegraph/src/lib.rs`:

- **RoleGraph**: The core data structure representing concepts and their relationships
- **TriggerIndex**: TF-IDF fallback for semantic search when exact matches aren't found
- **Node/Edge**: Graph primitives representing concepts and their connections

### Symbolic Embeddings

For domain-specific embeddings (e.g., medical), the `SymbolicEmbeddingIndex` in `crates/terraphim_rolegraph/src/medical.rs` builds embeddings from IS-A hierarchies, allowing for hierarchical concept relationships.

### Configuration

The system is configured via `config/atomic_graph_embeddings_config.json`:

```json
{
  "roles": {
    "Atomic Graph Embeddings": {
      "relevance_function": "terraphim-graph"
    }
  }
}
```

The `terraphim-graph` relevance function enables graph-based ranking.

## Use Cases

### Semantic Search with Relationship Awareness

Graph embeddings excel when content relationships matter more than simple keyword matching:

- **Finding related concepts automatically**: Search for "distributed systems" also returns results about "consensus", "raft", "CAP theorem"
- **Role-based search**: Domain-specific knowledge graphs for engineers, medical professionals, etc.
- **Explainable results**: Each result shows which graph paths led to the match

### Example: Learning Assistant

With a learning knowledge graph:
- Search "active recall" returns notes about "spaced repetition", "flashcards", "memory"
- Search "consensus algorithms" returns notes about "raft", "paxos", "leader election"
- Results are ranked by graph connectivity, not just keyword density

## Comparison with Vector Embeddings

### Why Graph Embeddings?

| Feature | Vector Embeddings | Graph Embeddings |
|---------|----------------|----------------|
| Representation | Dense vectors | Graph structure |
| Explainability | Black box | Full traceability |
| Queries expand | Implicit via distance | Explicit via synonyms |
| Relationship capture | Learns patterns | Encodes relationships |
| Domain adaptation | Requires retraining | Add to thesaurus |

### The Transparency Advantage

Unlike vector embeddings where you don't know WHY a document matched, Terraphim's graph embeddings show:

1. **Which terms matched**: The exact thesaurus entries that triggered
2. **Graph paths**: The path from query term through the graph to the document
3. **Ranking breakdown**: How node.rank + edge.rank + document_rank was computed

This makes results fully auditable and debuggable.

## Example Usage

### CLI Search

```bash
# Search with the Engineer role
terraphim-agent search "graph embeddings" --role engineer
```

This returns results for:
- "graph embeddings" (exact match)
- "terraphim-graph" (synonym)
- "knowledge graph based embeddings" (related concept)
- "symbolic embeddings" (connected concept)

### Programmatic Usage

```rust
use terraphim_rolegraph::RoleGraph;
use terraphim_types::{Thesaurus, RoleName};

// Create rolegraph with domain knowledge
let thesaurus = build_domain_thesaurus();
let role_name = RoleName::new("Engineer");
let mut graph = RoleGraph::new(role_name, thesaurus).await?;

// Index documents
for doc in documents {
    graph.insert_document(&doc.id, doc);
}

// Query - automatically expands to synonyms
let results = graph.query_graph("distributed systems", None, Some(10))?;
```

### Configuration

Enable graph embeddings in your config:

```json
{
  "roles": {
    "Your Role": {
      "relevance_function": "terraphim-graph",
      "kg": {
        "knowledge_graph_local": {
          "path": "./docs/your-domain"
        }
      }
    }
  }
}
```

## Next Steps

- [Quickstart Guide](/docs/quickstart) - Get started with Terraphim
- [Configuration Guide](/docs/terraphim_config) - Configure roles and knowledge graphs
- [Installation Guide](/docs/installation) - Install Terraphim on your system