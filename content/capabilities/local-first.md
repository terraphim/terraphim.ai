+++
title = "Local-First Architecture"
description = "Your data never leaves your machine — all indexing, searching, and graph traversal happens entirely on-device"
date = 2026-04-05
weight = 1

[taxonomies]
categories = ["Capabilities"]
tags = ["privacy", "local-first", "offline", "architecture"]

[extra]
toc = true
waypoint = "WP-001"
icon = "fa-solid fa-shield-halved"
+++

## Privacy by Architecture, Not by Policy

Terraphim AI is not "privacy-respecting" because of a terms-of-service promise. It is private because the architecture makes data exfiltration structurally impossible. All indexing, searching, and knowledge graph traversal happens entirely on your device. There is no cloud dependency, no telemetry, no analytics phone-home.

## Design Principles

The search architecture is deliberately non-neural and offline-first:

| Principle | What It Means |
|-----------|---------------|
| **Offline-first** | No network calls or LLM inference required at search time |
| **Deterministic** | Same query plus same corpus equals same results, always |
| **Explainable** | Every score decomposes into frequency counts, field weights, or set overlaps |
| **Low footprint** | Approximately 15-20 MB RAM for a typical knowledge graph; no GPU, no float vectors |
| **Graph-native** | Explicit edges and nodes encode domain relationships, not latent geometry |

## No Account Required

There is no sign-up, no API key, no subscription. You install Terraphim and it works. Your search history, your knowledge graphs, your indexed documents — all of it stays on your machine under your control.

## How It Compares

Traditional enterprise search tools upload your data to cloud servers, process it with proprietary models, and return results through APIs that require authentication and ongoing payment. Terraphim inverts this model entirely:

- **Data stays on device** — not uploaded, not cached remotely, not used for training
- **Works offline** — full functionality without an internet connection
- **Zero telemetry** — no usage tracking, no analytics, no fingerprinting
- **No vendor lock-in** — open source, standard formats, portable knowledge graphs

## Deployment Options

Terraphim runs wherever you need it: as a native desktop application, a WebAssembly module in your browser, a CLI tool, or a TUI (terminal user interface). For teams that need shared access, Terraphim Private Cloud uses AWS Firecracker microVMs to give each user a dedicated virtual machine with their own TLS certificate — keeping data isolated even in multi-tenant deployments.

## Learn More

- [Installation guide](/docs/installation)
- [Quickstart](/docs/quickstart)
- [Rust/WASM Performance](/capabilities/rust-wasm/)
