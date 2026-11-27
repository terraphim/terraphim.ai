+++
title="Facts, Style and Named Concepts: What FOF-80M Says About Graph Embeddings"
date=2026-11-27

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "graph-embeddings", "text-embeddings", "factuality", "research", "explainability"]

[extra]
toc = true
comments = true
+++

Give an embedding model a sentence, a wordy rewrite that keeps every fact, and a near-copy that changes one fact. The model picks the near-copy as closer almost every time. A new paper measures this, trains a small model to resist it, and is candid about what that costs. Terraphim answers the same question, "are these two texts the same?", in a very different way. Here is what each approach catches, what it misses, and a bug we found in our own code while checking.

<!-- more -->

## The paper

[Focus On Facts: Stylistically Invariant and Factually Sensitive Text Embeddings](https://arxiv.org/abs/2611.33250) (Maximus Adeola, University of Maryland, Baltimore County; NeurIPS 2026 LP4FM workshop) opens with this example:

- **Anchor:** "We present ab initio calculations of the electronic energy loss of charged particles moving outside a magnesium surface."
- **Fact-altered near-copy:** the same sentence, with *beryllium* in place of *magnesium*.
- **Fact-preserving rewrite:** "In this highly detailed scientific work, we put forward a set of comprehensive ab initio calculations pertaining to the electronic energy loss experienced by charged particles as they travel in close proximity to, but outside of, a magnesium surface."

The paper builds **FOF-Bench**, 83,263 triplets like this from Wikipedia, arXiv, PubMed, ROCStories and ReClor. An LLM wrote both the rewrites and the near-copies. Each near-copy has exactly one alteration: a swapped entity, a changed number, a reversed direction or condition, a different quantifier, swapped cause and effect, or reordered events.

On the 8,327 test triplets, the base model (F2LLM-v2-80M) ranks the near-copy above the rewrite **99.58%** of the time. Fine-tuning it with a contrastive loss gives **FOF-80M**, with these results:

- **Ordering.** The rewrite now wins 29.37% of the time, and 98.5% of per-triplet margins move the right way.
- **Mean separation** turns positive, from -0.1650 to +0.0329.
- **Style invariance.** Cross-style similarity on the DiSC style-transfer set rises from 0.79 to 0.96.

The author is clear that the problem is not solved, and lists the costs:

- **Retrieval.** Style-agnostic R-precision falls from 98.84% to 88.36%.
- **Entailment.** SNLI probe accuracy drops from 71% to 53%.
- **Summaries.** Correlation with human consistency ratings on SummEval falls from 0.21 to 0.02.

The model learns to treat *missing* facts as *different* facts. That makes a faithful summary look wrong. It also lets shared named entities outweigh a fabricated relation between them. The paper calls the result a "soft factual fingerprint", not a factuality metric. The [dataset](https://huggingface.co/datasets/MaxDevv/FOF-Bench) and [model](https://huggingface.co/MaxDevv/FOF-80M) are public.

## A bag of words fails the same way

We ran one cheap check on the released test split. Token-set Jaccard similarity, which knows nothing beyond which words appear, prefers the rewrite in **3 of 8,327 triplets (0.04%)**, with no ties. The base embedding's 0.42% sits right next to that floor. The base model's failure is the surface-overlap shortcut, as the paper says.

The same data shows how small the change is. An anchor and its near-copy differ by a median of **two** distinct words. In **15.7%** of triplets they use exactly the same set of words, and the alteration is a reordering.

Two more things turned up in the release:

- **Malformed rows.** 246 of the test positives are JSON objects rather than text. Some carry the generator's own planning notes.
- **Longer rewrites than asked for.** The rewrites were meant to be 1.5 to 5 times the anchor's length. In practice 46% are longer than that.

Neither changes the headline, but both make the paper's "synthetic data quality" caveat concrete.

## How Terraphim decides two texts are the same

Terraphim's [graph embeddings](/docs/graph-embeddings/) do not learn similarity. A role's thesaurus declares it:

- **Synonyms map to one concept id.** The thesaurus compiles to an Aho-Corasick automaton.
- **Matching returns ids in order.** Matching a text returns the ordered list of concept ids it contains.
- **Indexing counts directed pairs.** Each consecutive pair of concepts becomes a directed edge in the graph.
- **Ranking is a sum.** `query_graph` adds integer counts. There are no vectors and no training.

We ran the paper's example through `terraphim_rolegraph` at terraphim-core commit 84a496a. The thesaurus was one we wrote for the test, holding *ab initio*, *electronic energy loss*, *charged particles*, *magnesium*, *beryllium* and *surface*:

| Text | Concept ids |
|---|---|
| Anchor | `[1, 2, 3, 4, 6]` |
| 39-word rewrite | `[1, 2, 3, 4, 6]` |
| Near-copy | `[1, 2, 3, 5, 6]` |

The rewrite collapses onto the anchor exactly, because the words that carry style are not concepts. The near-copy differs in one position, and we can name it: magnesium (4) became beryllium (5). That is the behaviour FOF-80M is trained towards, and here it is exact rather than soft.

It is exact **only for words in the thesaurus**:

- **Unlisted entities.** Take the two elements out of the thesaurus and the anchor and near-copy produce identical sequences.
- **Numbers and negation.** "Three points from safety" against "four points", or "beat" against "did not beat", look the same to the graph.
- **Order swaps.** "Smoking causes lung cancer" and "lung cancer causes smoking" do produce two different directed edges. But a query for *smoking* ranks both documents equally, because ranking does not use direction today.

| Alteration in FOF-Bench | Terraphim's generic graph |
|---|---|
| Entity swap | Caught, and named, if both entities are concepts |
| Numeric change, negation, quantifier | Not seen |
| Cause and effect, event order | Stored as edge direction, not used in ranking |

## Where each approach is strong

**FOF-80M** generalises. It needs no thesaurus and catches some substitutions in any domain. But it ranks only 29% of hard cases correctly. Its scores are compressed into a narrow high band, and it does worse at retrieval than the model it started from.

**Terraphim** is exact and explainable inside its vocabulary, and blind outside it. Two of the paper's failure modes are worth comparing directly.

- **Omission.** FOF-80M penalises a summary for leaving facts out. Terraphim's query-to-document scoring is directional: a document that contains some of the query's concepts still ranks, and missing ones simply add nothing. That is the entailment-shaped behaviour the paper's model loses.
- **Entity overpowering.** In the paper's example, a summary uses the right footballers and club but invents a claim about one of them. FOF-80M scores it 0.89. A concept graph would rank it high too, because every entity matches. Neither approach catches a false relation between correct entities. That needs typed relations, which we discussed in [Inspiration Graphs and Counted Graphs](/posts/inspiration-graphs-vs-counted-graphs/).

## A bug in our own similarity

Terraphim has a second, hierarchy-based similarity behind the `medical` feature. It works over IS-A ancestor and descendant sets, for example to find related drugs or diseases. We built a tiny hierarchy (element, then alkaline earth metal, then magnesium and beryllium; carbon directly under element) and asked it the paper's question:

| Pair | Similarity |
|---|---|
| magnesium, magnesium | 1.0 |
| magnesium, beryllium | **1.0** |
| magnesium, carbon | 0.5 |
| magnesium, alkaline earth metal (its parent) | 0.325 |

Two sibling concepts score exactly as identical, and a concept's own parent scores below an unrelated cousin. There are two causes:

- **The overlap term.** Siblings with the same ancestors have identical sets, so the Jaccard part is 1.0.
- **The path estimate.** It rounds the common ancestor's depth up to the siblings' own depth, so the path length comes out as zero instead of two.

In a medical role, a sibling swap is exactly the dangerous substitution: one drug for another in the same class. The existing test checked that siblings beat distant nodes, not that siblings fall below identity. The fix is tracked in terraphim-core#119 with the reproduction. Generic search does not use this similarity.

## What we take from it

- **A concept diff for answer checking.** Because the automaton returns ordered concept ids, a judge can compare a source and an answer and report "magnesium became beryllium" by name, with no model call. It covers only what the thesaurus covers, which is the point: it is exact where it applies and says nothing where it does not.
- **FOF-Bench's shape as a regression test.** If we add a dense fallback lane, it should not rank one-fact near-copies above paraphrases. Note that the dataset licence is non-commercial.
- **Not FOF-80M itself, for search.** By the paper's own tables it retrieves, entails and judges summaries worse than its base.

The broader lesson matches the one from FIG-MAC. Learned similarity buys generality and pays in calibration and explanation. Declared similarity buys exactness and an honest "no match", and pays in coverage. The interesting work is in making the declared side cover more: typed relations, numbers and negation as first-class concepts, without giving up the ability to point at the exact concept that changed.

*The probes and the bag-of-words check are small scripts run against terraphim-core 84a496a and the public FOF-Bench test split. The paper is CC BY 4.0. Figures quoted are from its tables or from our own runs, as marked.*
