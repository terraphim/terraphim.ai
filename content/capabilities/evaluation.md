+++
title = "Automata Evaluation"
description = "Measure classification accuracy with precision, recall, F1 against ground truth"
date = 2026-04-16
weight = 11

[taxonomies]
categories = ["Capabilities"]
tags = ["evaluation", "automata", "testing", "quality"]

[extra]
toc = true
icon = "fa-solid fa-chart-line"
+++

The evaluation framework measures how accurately the Aho-Corasick automata classify terms in
real documents. Give it a JSON file of hand-labeled documents and it returns micro-averaged
precision, recall, and F1, a per-term breakdown, and a list of terms that consistently
produce false positives.

## When to use it

- After changing a thesaurus, to verify the automata still behave as expected.
- To find patterns that match too broadly (systematic false positives).
- To quantify recall gaps before adding new synonyms.

## Ground-truth file format

```json
[
  {
    "id": "doc1",
    "text": "tokio powers async rust applications",
    "expected_terms": [
      { "term": "tokio",  "category": null },
      { "term": "rust",   "category": null },
      { "term": "async",  "category": null }
    ]
  }
]
```

Each `term` must match the normalized term value (`nterm`) stored in the thesaurus.

## Running an evaluation

```rust
use terraphim_automata::evaluation::{evaluate, load_ground_truth};

let docs = load_ground_truth(Path::new("ground_truth.json"))?;
let result = evaluate(&docs, thesaurus);

println!("F1: {:.2}", result.overall.f1);
for report in &result.per_term {
    println!("  {} precision={:.2} recall={:.2}",
        report.term, report.metrics.precision, report.metrics.recall);
}
for err in &result.systematic_errors {
    println!("  SYSTEMATIC FP: {} in {} documents", err.term, err.false_positive_count);
}
```

## How metrics are computed

Metrics are **micro-averaged**: true positives, false positives, and false negatives are
summed across all documents before dividing.

A term is flagged as a `SystematicError` when it appears as a false positive in 2 or more
documents. Matching is case-insensitive; each term is counted at most once per document.

Source: `crates/terraphim_automata/src/evaluation.rs`
