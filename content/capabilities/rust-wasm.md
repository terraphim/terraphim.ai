+++
title = "Rust/WASM Performance"
description = "Written in Rust, compiled to WebAssembly — sub-millisecond search latency at near-native speed"
date = 2026-04-05
weight = 4

[taxonomies]
categories = ["Capabilities"]
tags = ["rust", "wasm", "performance", "benchmarks"]

[extra]
toc = true
waypoint = "WP-004"
icon = "fa-brands fa-rust"
+++

## Near-Native Speed, Everywhere

Terraphim AI is written in Rust and compiles to WebAssembly. This is not a marketing choice — it is a performance requirement. Knowledge graph inference runs in **5 to 10 nanoseconds**. Pipeline processing completes in hundreds of milliseconds. Search queries resolve in sub-millisecond time.

## Why Rust

Rust provides **memory safety without garbage collection**, **zero-cost abstractions**, and **thread safety** guaranteed at compile time. For a system that builds and traverses knowledge graphs with thousands of nodes and edges, these guarantees translate directly into reliable performance without unexpected pauses or memory leaks.

## Why WebAssembly

WebAssembly allows the same Rust codebase to run:

- **In your browser** — no installation required, instant access
- **On your desktop** — native performance as a standalone application
- **On your server** — same code, same results, different deployment target
- **On mobile** — lightweight enough for devices with limited resources

One codebase, compiled to multiple targets, with no performance compromise.

## Performance Numbers

The journey from The Pattern to Terraphim AI tells the performance story:

| Metric | Traditional ML Pipeline | The Pattern | Terraphim AI |
|--------|------------------------|-------------|--------------|
| Data processing for training | 6 days | 6 hours | Hundreds of milliseconds |
| Inference latency | Seconds | Under 2 ms | 5-10 nanoseconds |
| RAM footprint | Gigabytes | Hundreds of MB | 15-20 MB |
| GPU required | Yes | No | No |

## Benchmarking

Terraphim includes a comprehensive benchmarking framework covering:

- Knowledge graph construction time
- Search indexing throughput
- Query evaluation latency
- Aho-Corasick pattern matching speed
- End-to-end performance across all components

All benchmarks run on standard hardware — no GPU, no specialised accelerator.

## Low Footprint

A typical Terraphim knowledge graph occupies approximately 15-20 MB of RAM. There are no float vectors, no dense embeddings, no GPU memory allocation. This means Terraphim runs comfortably on a laptop, a Raspberry Pi, or a modest cloud instance.

## Learn More

- [Local-First Architecture](/capabilities/local-first/)
- [Knowledge Graph Engine](/capabilities/knowledge-graph/)
- [Installation guide](/docs/installation)
