+++
title="Counts That Are Really Length: What a Proposition Paper Says About Graph Scores"
date=2026-11-27

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "graph-embeddings", "evaluation", "research", "explainability", "grounding"]

[extra]
toc = true
comments = true
+++

A new paper tests three kinds of method on two questions about sentences, and finds that the symbolic counters look predictive only because longer sentences have bigger counts. Terraphim's graph score is a count too. Checking our own code against the paper's test turned up a score term that grows with a concept's distinct neighbours, which is a plausible route for length to leak in, and two counting defects, which we have filed.

<!-- more -->

## The paper, and what it does not say

[Verifiable but Not Predictable: What Sentence Embeddings Know About Propositional Decomposition](https://arxiv.org/abs/2611.33668) (Li, Wu and Cui, Technological and Higher Education Institute of Hong Kong, submitted 25 November 2026, CC BY 4.0) is about splitting sentences into propositions, the small self-contained claims that retrieval and fact-checking pipelines work with. It builds no graph and uses no graph embeddings. It asks two quality-control questions:

1. **Verify.** Given a sentence and a candidate proposition, does the proposition belong to the sentence?
2. **Predict.** Before splitting, how many propositions should the sentence yield?

The answers, on 539 test sentences from English Wikipedia (PropSegmEnt):

- **A learned entailment judge verifies well.** A fine-tuned mDeBERTa-v3 natural language inference (NLI) model gets 92.8% accuracy and an AUC of 0.977. Its errors are structured: definitional statements that are true given the surrounding document, but not entailed by the sentence alone, have a 43% false-positive rate against 11.7% for other negatives. (The abstract calls these most of the errors; the section 5.1 figures put them at roughly 46 of 285.) Cosine similarity between embeddings cannot do this job: it saturates at about 0.7 for members and non-members alike.
- **Symbolic counters only measure length.** Token count, an idea-density counter (CPIDR) and a predicate counter all correlate with the human counts. Once sentence length is controlled, all three drop to zero or below.
- **A linear probe on dense embeddings keeps real signal.** After length is controlled, its correlation with human counts is 0.40 to 0.49, and it survives INT4 quantisation and truncation to 256 dimensions.

So this is not a paper that favours counted symbolic structure over vectors. If anything it shows the opposite for counting. Its value for us is the method it uses to catch a count that is really length.

## The test: three lenses

The paper's central warning is in Table 2. Raw token count correlates with the human proposition count at 0.810, better than two of the three embedding probes. Taken at face value, the simplest possible counter wins.

The paper does not take it at face value. Every predictor is scored three ways:

1. **Raw rank correlation** with the human count.
2. **Length-partialled correlation.** Both the prediction and the human count are regressed on token count, and the residuals are correlated. This asks whether there is any information beyond length.
3. **Same-length pair accuracy.** Over 2,341 pairs of test sentences with the same token count but different human counts, how often does the predictor order them correctly? Chance is 50%.

Token count scores 0.810, then -0.042, then undefined, because it can never break a tie between sentences of equal length. The idea-density counter scores 0.659, then -0.179, then 41.6%: worse than a coin when length cannot help. The paper's own phrase for the first number is that "raw correlation would have lied."

## Terraphim's score is a count

The mechanism is on the [graph embeddings reference](/docs/graph-embeddings/) and the [interactive explainer](/docs/graph-embeddings-interactive/). Read from `terraphim_rolegraph` in terraphim-core at commit 84a496a:

- Indexing a document matches its concepts with an Aho-Corasick automaton and links each consecutive pair with a directed edge. The edge keeps a per-document count.
- `query_graph` walks every edge of each matched concept and, for each document on that edge, adds `node.rank + edge.rank + count`.
- `edge.rank` is set to 1 when the edge is created and never changes, so it adds a constant 1 per edge.

Put those together for a one-concept query. A document's score is k × (node.rank + 1) plus the sum of its counts, where k is the number of distinct edges between that concept and the concepts matched next to it in that document. node.rank is the same for every document, so each extra distinct neighbour adds node.rank + 1 plus its count. Unmatched text does not change k. A single mention has at most two neighbours, so k grows when the concept is mentioned more often next to different concepts, which longer documents give more room for. That last step is a hypothesis, not something we measured.

We ran one toy case in a scratch test. Two documents each mention `alpha` once. `alpha beta` scores 5. `gamma alpha beta delta epsilon` scores 11. The second gives `alpha` two matched neighbours instead of one.

That shows the score is coupled to neighbourhood size. It does not show that neighbourhood size tracks document length in a real corpus, and it does not show that our ranking reduces to length. That needs the paper's second and third lenses against relevance judgements, which this check did not have. Correlating score with length on its own would be half the test, and the paper's retracted pilot is a reminder of what half a test produces.

## Two counting defects

Writing the toy test also exposed two bugs, now filed as terraphim-core#120 on our Gitea:

1. **The first count depends on insertion order.** The document that creates an edge is stored with count 1. Every later document's first occurrence of the same pair is stored as 2. Two documents with identical text, `alpha beta`, scored 4 and 5.
2. **Removal leaks node rank.** Insertion adds 1 to a node's rank per pair occurrence; removal subtracts 1 per edge. A document that repeats a pair leaves residue: in our test the rank went from 1 to 6 on insert and back to 4, not 1, on removal. The interactive explainer already noted this one. The first defect had not been noted anywhere we could find.

Our [FIG-MAC comparison](/posts/inspiration-graphs-vs-counted-graphs/) this morning said the edge "counts that pair's occurrences per document". That was inexact, and the post now says so. The reference page also defined `node.rank` and `edge.rank` in ways the code does not match; this change corrects it.

## What we are taking from the paper

**The three lenses become the acceptance test for ranking changes.** We already have open hypotheses for the role graph: weight concepts by inverse document frequency, link all concept pairs in a document instead of adjacent ones. Each will be reported on raw correlation with relevance, correlation after partialling out document length, and accuracy on same-length document pairs. A change that moves only the first number is length in disguise. The insertion-order defect gets fixed first, or no ranking change can be pinned.

**Verification needs an entailment judge, not overlap.** The paper's split maps onto grounding, the question of whether a cited source supports a claim. Concept overlap is no more a faithfulness test than a cosine threshold is, and the paper names the cosine version as an over-claim. The shape that works in the paper is a cheap screen to route, then a discriminative judge per claim, with the context-true class reported separately.

**Keep the automaton for what it actually does.** The automaton answers whether a declared term occurs. That is exact and recomputable, and it is what our [checklist argument](/posts/graph-embeddings-checklists/) relies on. It is not the paper's verification task, and the paper offers no evidence either way about it.

## Caveats on the paper

- **One dataset, one domain.** English Wikipedia only. ESG transfer is planned, not run.
- **A paragraph that does not match its table.** Section 6.2 attributes the ceiling comparison to the 22M-parameter MiniLM probe, but the paired difference (+0.032) and the MAE (1.53) match the Qwen3 0.6B row. The difference for MiniLM would be 0.092.
- **A caption that does not match the text.** The Figure 3 caption says definitional negatives "drive 43% of the false positives". Section 5.1 says they have a 43% false-positive rate, and only that reading fits the totals.
- **No code.** The paper says it releases derived statistics. No repository is linked.

None of these touch the main finding: the symbolic counters' length-controlled point estimates are at or below zero under every reading, and only CPIDR's interval lies wholly below zero.

## Sources

- Li, Wu and Cui, [arXiv:2611.33668v1](https://arxiv.org/abs/2611.33668), sections 3 to 7 and Tables 1 to 4, read from the v1 PDF. Numbers are quoted from the paper. The 0.092 recomputation is ours.
- `terraphim_rolegraph` in terraphim-core at 84a496a: `query_graph`, `init_or_update_edge`, `init_or_update_node`, `remove_document_contributions`. The scratch test and its output are recorded in terraphim-core#120.
