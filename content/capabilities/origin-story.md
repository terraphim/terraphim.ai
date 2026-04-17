+++
title = "Origin Story"
description = "From science fiction to The Pattern to Terraphim AI — a decade of rethinking search from the ground up"
date = 2026-04-17
weight = 7

[taxonomies]
categories = ["Capabilities"]
tags = ["history", "the-pattern", "redis", "kaggle", "oxford", "incose", "science-fiction", "relict"]

[extra]
toc = true
waypoint = "WP-007"
icon = "fa-solid fa-rocket"
+++

## Inspired by Science Fiction

The name *Terraphim* comes from the [Relict series][relict] of science fiction novels by [Vasiliy Golovachev](https://en.wikipedia.org/wiki/Vasili_Golovachov). In Golovachev's universe a Terraphim is an artificial intelligence that lives inside a spacesuit — part of an exocortex — or inside your house or vehicle, designed to help you with your tasks. You carry it with you.

Similar companions are now familiar across modern science fiction. Destiny 2 has [Ghost][ghost], a small floating AI bound to its Guardian. Star Wars Jedi: Survivor has [BD-1][bd-1], a droid riding on Cal Kestis's back. Same pattern: a compact, mobile, personal intelligence that augments rather than replaces.

That image — small, local, loyal, always with you — drives the engineering choices in the rest of this page. Terraphim runs on your hardware, codifies knowledge as compact graphs rather than heavyweight models, and never ships your data across a boundary. The sci-fi premise is the brief; what follows is how we built it.

[bd-1]: https://starwars.fandom.com/wiki/BD-1
[ghost]: https://www.destinypedia.com/Ghost
[relict]: https://www.goodreads.com/en/book/show/196710046

## From Kaggle to Nanosecond Inference

Terraphim AI did not start as a product. It started as a frustration with how slowly machine learning pipelines process data.

The project's predecessor, **The Pattern**, grew out of participation in two Kaggle data science competitions. The original ML pipeline could not finish processing data in six days. The Pattern processed the same data for training in six hours and achieved under two-millisecond inference. That hundredfold improvement was not a hardware upgrade — it was a fundamental rethinking of how search and retrieval should work.

## Redis Hackathon Platinum Winner

The Pattern was awarded **Platinum Winner** at the Redis Hackathon, outperforming Nvidia's ML pipeline for BERT QA inference on CPU. The prize confirmed that external experts recognised the approach as genuinely innovative, not merely a clever optimisation.

The results were presented and discussed at a **public lecture at Oxford University, Green Templeton College**, bringing academic scrutiny to the architecture that would become Terraphim AI.

## The Breakthrough: Graph Embeddings Without Attention

Traditional search systems rely on dense vector embeddings and attention mechanisms that are expensive, opaque, and non-deterministic. Terraphim took a different path.

**Terraphim Graph Embeddings** maintain the position of terms in a sentence without requiring traditional training techniques like attention. Users can specify synonyms manually and rebuild graph embeddings for a role within 20 milliseconds. This allows matching terms in different languages to the same concept without running language detection, and eliminates the need for stop-word dictionaries entirely.

By rethinking from the ground up, Terraphim AI achieves pipeline processing in hundreds of milliseconds and knowledge-graph-based inference in **5 to 10 nanoseconds**.

## Validated by INCOSE

The methodology has been validated within the **INCOSE** (International Council on Systems Engineering) community for the Systems Engineering Handbook v.4 and the Systems Engineering Digital Process Model v.1. It was recognised as a valid low-effort substitution for formal model-based systems engineering — particularly valuable for brownfield systems engineering, reverse-engineering, and professional certification.

## Why Search is Broken

Research consistently shows the problem Terraphim exists to solve:

- 88% of employees feel demoralised when they cannot find the information they need (Coveo 2023)
- Workers spend 1.8 hours daily searching for information (McKinsey)
- Traditional enterprise search addresses only 20% of actual business search use cases
- 25% of all webpages that existed between 2013 and 2023 are no longer accessible (Pew Research 2024)

Terraphim's answer: deterministic, privacy-first, knowledge-graph-powered search that runs entirely on your hardware.

## Three Differentiators

1. **Privacy-first**: Rather than transferring data across boundaries, Terraphim codifies and moves knowledge graphs. Runs in your browser via WebAssembly.
2. **Action-oriented ontologies**: Focused on required outcomes, not exhaustive recognition. Compact knowledge representations following YAGNI principles.
3. **Role-based knowledge lenses**: Separate knowledge graphs per role, with user control over modifications.

## Learn More

- [Join the discussion on Discourse](https://terraphim.discourse.group/)
- [Quickstart guide](/docs/quickstart)
- [Knowledge Graph Engine](/capabilities/knowledge-graph/)
