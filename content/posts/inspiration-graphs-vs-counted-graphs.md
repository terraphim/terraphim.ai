+++
title="Inspiration Graphs and Counted Graphs: What FIG-MAC Says About Graph Embeddings"
date=2026-11-27

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "graph-embeddings", "knowledge-graph", "research", "hybrid-retrieval", "explainability"]

[extra]
toc = true
comments = true
+++

A new paper builds a knowledge graph from 26,917 research papers, learns graph embeddings over it, and reports that graph traversal finds more varied sources than vector search. Terraphim also calls what it does "graph embeddings", but almost every design choice goes the other way. Putting the two side by side shows what each approach buys, what it costs, and the one thing our graph cannot do yet.

<!-- more -->

## The paper

[FIG-MAC: A Fine-grained Inspiration Graph Empowered Multi-Agent Collaboration for Automated Scientific Hypothesis Generation](https://arxiv.org/abs/2611.33563) (Chen et al., Huazhong Agricultural University, submitted 25 November 2026) tries to get LLM agents to propose research hypotheses that are new but still grounded in the literature. It has three parts:

1. **A typed graph.** Each paper becomes a PAP node with RQ (research question) and SOL (solution) nodes under it. Cross-paper edges are `related` or `inspired`. An `inspired` edge runs from a solution in one paper to a research question in another, and means the first was a precursor of the second, even without a citation between them. A fine-tuned Qwen model extracts the nodes, and a fine-tuned Qwen3-8B classifies the candidate edges.
2. **Learned embeddings and hybrid retrieval.** A relational graph convolutional network (RGCN, 256 dimensions, DistMult decoder) scores edges. Each query runs dense vector search and graph traversal side by side. Multi-hop "inspiration chains" are ranked by a weighted mix of cosine similarity and two learned edge confidences, and a beam search keeps the best chains.
3. **An agent team.** Innovators draft, three reviewers score, a quality controller decides when to stop.

The result that matters for retrieval is the ablation in Table 5. With every backbone tested (Mixtral-8x7b, LLaMA3.1-70b, Qwen-Max), graph-only retrieval beat vector-only retrieval on the paper's raw novelty and source diversity scores, and the hybrid of the two beat both. With Qwen-Max and the multi-agent setup, source diversity was 0.298 for graph only, 0.182 for vectors only and 0.650 for the hybrid.

## What Terraphim does instead

The mechanism is on the [graph embeddings reference](/docs/graph-embeddings/) and the [interactive explainer](/docs/graph-embeddings-interactive/). Here is the short version, read from `terraphim_rolegraph` in terraphim-core at commit 84a496a:

- **Nodes are concepts you write down.** A role's thesaurus maps every synonym to a normalised concept id. It compiles to an Aho-Corasick automaton (leftmost-longest, case-insensitive).
- **Edges are counted adjacency.** When a document is indexed, each consecutive pair of matched concepts updates one directed edge. The edge keeps a per-document count of that pair, and the node's rank goes up by one per pair update. (Correction, 27 November: these counts are not exact. A document's first occurrence is stored as 1 or 2 depending on insertion order, and removal does not fully undo node rank; see [Counts That Are Really Length](/posts/counts-that-are-really-length/).)
- **A score is a sum you can recompute.** For each query concept, `query_graph` walks the concept's edges and adds `node.rank + edge.rank + document count` to each document on them. There are no weights, no vectors and no training.
- **When nothing matches, the graph says so.** If the automaton finds no concept, a TF-IDF trigger index over concept descriptions can step in, with a 0.3 relevance cut-off. Otherwise the result is empty, not a nearest neighbour.

That is why [Why Graph Embeddings Matter](/posts/why-graph-embeddings-matter/) can say a new concept is a text edit and a rebuild, not a retraining run.

## Side by side

| | FIG-MAC | Terraphim rolegraph |
|---|---|---|
| Node | Entity an LLM extracts (paper, question, solution) | Concept from a thesaurus a person writes |
| Edge | Typed and directed: `has_rq`, `has_sol`, `related`, `inspired` | Default role graph: directed adjacency, counted per document, no type. The optional `medical` feature adds typed edges loaded from curated ontologies |
| Embedding | Learned 256-d RGCN vectors, plus 1536-d text vectors | Integer counts on nodes and edges |
| Multi-hop | Scored chains, returned as evidence | A yes-or-no connectivity check |
| Cost of a new concept | Re-extract, re-classify, retrain | Edit a markdown file, rebuild the automaton |
| Why a result came back | A chain of named entities, with learned confidences | A sum of named counts |
| Query with unknown words | Dense search still returns neighbours | Empty, unless the trigger fallback fires |

No benchmark covers both systems, so this table compares designs, not results.

## What the paper gets right that we should take

**Edges that mean something.** In the default role graph, an edge records that two concepts appeared next to each other. It cannot record that a solution came before a question, or that one method refines another. FIG's `inspired` edge carries that meaning, and it is why their chains read as an argument rather than a list.

Terraphim already has typed edges in one place. The optional `medical` feature adds a `MedicalRoleGraph` that stores typed, directed relations such as `IsA`, `Treats`, `Causes` and `Contraindicates`, loaded from curated sources (PrimeKG and SNOMED CT). Those types are specific to medicine, and `query_graph` does not use them when it ranks documents. That points to a route with no classifier: generalise the medical edge types so a role's thesaurus can declare relations such as `refines` or `contradicts` between two concepts. The type would then come from the same reviewed text file as the synonyms and stay explainable.

**Links between documents that share no words.** Two of our documents are linked only through the thesaurus. If two papers describe the same idea in different vocabulary, they stay apart until someone writes the synonym down. FIG's classifier closes that gap automatically, at the price of a learned decision nobody can recompute. That is the real trade: recall from inference, or explanations from counting.

**Paths as evidence.** `is_all_terms_connected_by_path` already searches for a walk that connects all the query's concepts. It treats our directed edges as undirected and returns only true or false. If it returned the walk, with the counts on each edge, an agent would get a chain it could cite, without any learning.

**Score the sources as well as the answer.** FIG's provenance-adjusted novelty penalises a hypothesis for being too similar to the sources it was built from and rewards diversity among those sources. That is a cheap check on whether an answer just restates its context, and it belongs next to grounding checks in an evaluation harness.

## What the paper does not show

The numbers are a v1 preprint's, and some caveats affect how far they generalise:

- **The judge is the generator.** Qwen-Max is the primary backbone and also gives the 1 to 10 quality scores. The subjective margins over the best baseline are 0.1 to 0.3 points.
- **The human study does not rank methods.** Five PhD students made 200 assessments of 100 questions, but the table reports no per-method breakdown, so the claim that the human ranking matches the LLM ranking is not shown.
- **The diversity metric partly measures the mechanism.** Source diversity is the average dissimilarity among the retrieved sources. Traversing cross-domain edges retrieves dissimilar sources by construction, so part of the graph's advantage is built into the metric.
- **No repeated-run variance, no cost, no release.** The system-result tables report no repeated runs or run-to-run spread. Runtime, token and call counts are not given. No code or data has been released.
- **One equation does not match its table.** Computing raw novelty (HD × CI / CD) from the Table 2 means gives 0.92 for FIG-MAC against 0.684 reported. Averaging the ratio per hypothesis could explain the gap, but the paper does not say whether it does that.

None of this makes the graph result wrong. It means the result supports "typed graph traversal brings in varied sources for hypothesis generation", not "graphs beat vectors" in general.

## Where that leaves "not a vector problem"

In [Graph Embeddings for Checklists](/posts/graph-embeddings-checklists/) we argued that a checklist is not a vector problem: it is a fixed set of items that must be enumerated, and an automaton does that exactly. FIG-MAC is the opposite kind of problem. Hypothesis generation needs neighbours you did not list, and dense search provides them. The paper's own ablation agrees with both points: graph traversal alone beat vectors alone in every backbone, and the best results came from combining them.

So for Terraphim the lesson is about the graph rather than the vectors. Keep the counting, because counting is what makes a score auditable. Generalise the typed edges the medical graph already has into relation types any role can declare, and return the paths we already compute. That narrows the gap with a learned typed graph without giving up the property that every number can be traced to a line in a file.

## Sources

- Chen et al., [arXiv:2611.33563v1](https://arxiv.org/abs/2611.33563), sections 3.1 to 4.3 and Tables 2 to 5. Numbers are quoted from the paper; the HD × CI / CD recomputation is ours.
- `terraphim_rolegraph` in terraphim-core at 84a496a: `query_graph`, `add_or_update_document`, `find_matching_node_ids_with_fallback`, `is_all_terms_connected_by_path`.
