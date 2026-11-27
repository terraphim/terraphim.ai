+++
title="Ontologies, Lexical Graphs and the Missing Exact Lookup"
date=2026-11-27
description="AWS's Context Ontology Accelerator serves agents from two graphs: a formal ontology induced from tables and a lexical graph built from documents. Its own docs name the gaps between them. Here is where a deterministic concept layer fits, with a run on real Terraphim code, including the two places COA is ahead of us."

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "knowledge-graph", "ontology", "ai-agents", "mcp", "semantic-layer"]

[extra]
toc = true
comments = true
+++

AWS has published the Context Ontology Accelerator (COA), an Apache-2.0 semantic context layer that runs in your own AWS account and serves AI agents through MCP. It builds context with two techniques. One is a formal ontology induced from your tables. The other is a lexical knowledge graph built from your documents. Its documentation is unusually candid about where the two fall short, and several of those gaps fall where a deterministic concept layer such as Terraphim's fits.

This post reads COA at version 0.3.11 (commit `5dd33d7`). It names the gaps in COA's own words and shows what our graph does with them, on a small demo against real code. It also covers the two places where COA already does better than we do.

<!-- more -->

## Two techniques, three tiers

COA answers a question in tiers, and each tier falls through to the next on a miss:

- **Tier 1, governed metrics.** It matches a metric by name or synonym and runs the metric's pre-written SQL. No LLM is called.
- **Tier 2, structured queries.** It writes SQL, or SPARQL that Ontop translates to SQL, from the ontology. Only classes backed by a real table are used.
- **Tier 3, knowledge retrieval.** It runs GraphRAG over the document graph, and a model writes the answer.

The first two tiers stand on technique one. Induction reads the approved table and column metadata and proposes OWL classes with R2RML mappings. Grounding against an ontology such as FIBO or Schema.org uses embeddings and, by default, an LLM reranker. A data steward accepts the proposal before anything is live.

Tier 3 stands on technique two. An LLM extracts entities, topics and statements from the documents into Amazon Neptune, and embeddings go to OpenSearch.

An opt-in "bridge" strategy then copies meanings found in documents onto the table columns.

Six MCP tools expose all of this to agents: `list_metrics`, `describe_schema`, `query`, `translate_sparql`, `rag_retrieval` and `graph_traversal`. Cedar policies authorise every MCP tool call against the user the agent acts for, not the agent, and fail closed.

## Where COA says it falls short

Four gaps, each quoted or paraphrased from COA's own documentation:

1. **No exact lookup from a variant to its class.** A steward can add business variants as `skos:altLabel`, but they are only embedded with the class. In COA's own words: "There is no exact lookup from a variant to its class yet, so a question using `顧客離脱` is not guaranteed to find the class whose preferred Japanese label is `解約`."
2. **Links between the two sides are kept, not followed.** A grounding link from an induced class to a graph class stays in the ontology, "but neither engine follows it". One engine answers each question, and SQL and graph results are not combined.
3. **The default Tier 3 ignores the formal ontology.** The default GraphRAG strategy reads only the document graph. Its topic and entity nodes come from extraction, "not the accepted, formally-typed ontology".
4. **The bridge picks tables by name.** It considers at most 60 tables by default, "the first in name order", and only then finds out which ones have document evidence.

## What a concept layer adds

Terraphim compiles markdown knowledge-graph files into a thesaurus that maps each synonym to a concept. One Aho-Corasick automaton matches all of them in a single pass over the text, choosing the longest match. A role graph then counts which concepts appear next to each other in documents. It is deterministic, it runs locally, and every match comes with the term and its byte position.

Here is how that meets each COA technique. These are proposals: none is built, and none is measured against a COA deployment.

**On the ontology side**, compile a thesaurus from COA's published vocabulary. The graph API returns each class's labels and `altLabels`, the ontology downloads as Turtle, and metrics carry their own synonyms. Make the class or metric the concept, and its IRI the link.

An agent can then resolve a user's wording to a class before it calls `query`, with no model in the loop. That covers gap 1 on the agent side. The agent can also narrow `describe_schema` to the classes it needs. When the question also asks for a filter, the agent can pass it as `options.dimensions`, the channel COA documents for keeping a metric answer deterministic.

**On the lexical-graph side**, the entity names an LLM extracts vary: "attrition", "customer churn", "顧客離脱". A thesaurus maps them all to one concept, which gives graph traversal an exact starting point next to the vector hit.

Co-occurrence offers a cheap candidate list for the bridge. A document concept and a column concept that appear in the same paragraph are worth reading first, instead of the first 60 tables in name order (gap 4). The candidate carries no type and no definition, so COA's model and steward still make the decision.

## The run

We wrote a small program against terraphim-core main at commit `b1f8389`, built it from a fresh target directory, and ran it. Four knowledge-graph files mirror COA's documentation examples:

- a churn class with the Japanese labels `解約` and `顧客離脱`;
- a `total_revenue` metric;
- a `net_revenue` metric that deliberately shares the synonym `revenue`;
- an `order_status` column.

One glossary sentence we wrote mentions both a cancellation and the order status. This is the output:

```text
thesaurus entries: 16
COLLISION synonym="revenue" won="total_revenue" lost="net_revenue"
Q: 先月の顧客離脱率は？
   "顧客離脱"->churn @(9, 21)
Q: What was turnover last quarter?
   "turnover"->total_revenue @(9, 17)
Q: What was attrition for Gold loyalty customers?
   "attrition"->churn @(9, 18)
Q: How many cancellations did the Gold tier have?
   (no concept)
Q: Show revenue by order status
   "revenue"->total_revenue @(5, 12); "order status"->order_status @(16, 28)
graph nodes=2 edges=1
connected("attrition by order status") = true
connected("turnover and attrition") = false
```

The Japanese variant resolves to its concept inside an unspaced sentence. The word-boundary check counts only ASCII letters and digits as word characters, so CJK text matches where it must. That is COA's gap 1, on its own example.

The bridge edge exists only because we wrote a sentence containing both terms. It shows the mechanism and proves nothing about real documents.

## Where COA is ahead

Two lines of that output are failures, and in both COA behaves better.

**Plurals.** "cancellations" finds nothing, because our matcher rejects a match that sits inside a longer word. COA's Tier 1 has a fuzzy fallback (a similarity of at least 0.88) for typos and plurals. Our fuzzy search exists only in the autocomplete index, not in the matcher.

**Shared synonyms.** "revenue" resolves silently to `total_revenue`. Our build now reports the collision, but only on main: the fix merged on 27 November 2026 and is not in a published release yet. At query time the thesaurus still holds one winner per synonym. COA's Tier 1 declines when more than one metric matches, which is the right behaviour for numbers people act on.

COA also does something we do not do at all. After a metric match, Tier 1 strips the matched words and a closed stop-word list, and checks whether anything is left. In "total revenue for the Gold tier", the words "Gold tier" are left over, so Tier 1 declines to give the unfiltered total and hands the governed formula to Tier 2. Our matcher already returns positions, so the leftover text is computable, but no API returns it.

## What we take away

COA and Terraphim are not competitors. COA has governance we lack: steward review, formal OWL with R2RML, typed links such as `skos:closeMatch` against `skos:relatedMatch`, and fail-closed authorisation. Terraphim offers a deterministic vocabulary layer that can sit on the agent side or run as a build step. It fills the exact-lookup gap that COA names.

We are taking three ideas back into Terraphim:

- report the residual, meaning the words a match did not cover;
- decline on ambiguity at match time, not only at build time;
- type the links between concepts.

The longer architecture argument, with the layering we propose, is in the companion paper on [Reference Architecture for AI](https://reference-architecture.ai/posts/a-deterministic-concept-layer-beside-ontology-and-lexical-graph/). For how our graph counts and ranks, see [Inspiration Graphs and Counted Graphs](/posts/inspiration-graphs-vs-counted-graphs/).
