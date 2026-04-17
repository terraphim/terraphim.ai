+++
title="Personal Assistant Role: One Search Across Email and Notes"
date=2026-04-17

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "personal-assistant", "jmap", "obsidian", "knowledge-graph", "fastmail"]

[extra]
toc = true
comments = true
+++

Most "personal AI" tools split your context across silos: one search box for email, another for notes, a third for your chat history. Terraphim treats every source as a haystack on the same role, so a single query crosses all of them. This post shows how to wire up the two most common personal sources -- email via JMAP and notes in an Obsidian vault -- under a new Personal Assistant role.

<!-- more -->

## Why a unified role matters

The mental tax of personal search is not the typing. It is the *deciding*. "Did I read that in an email or write it in a note?" Each silo you skip is a context switch with no useful payload. Once Terraphim is the front door for both surfaces, the question collapses to "where is the thing about X" and the role's `terraphim-graph` ranking serves whichever source actually has the strongest signal.

The Personal Assistant role uses two haystacks under one role:

- **Obsidian vault** indexed by the `Ripgrep` service. Plain markdown, sub-millisecond local search, no daemon.
- **Fastmail mailbox** indexed by the `Jmap` service ([RFC 8620/8621](https://www.rfc-editor.org/rfc/rfc8620)). One HTTPS round trip per query, server-side full-text against your real mailbox, results returned with `jmap:///email/<id>` URLs you can paste back into a mail client.

Ranking is the same `terraphim-graph` scoring as every other Terraphim role: an Aho-Corasick automaton built from the Obsidian vault contributes synonyms specific to your project vocabulary, then both haystacks share the same rank ladder. Notes and email interleave by relevance, not by source.

## What you get

- A single command: `terraphim-agent-pa search "<query>"` returns mixed hits ordered by rank.
- Determinism. Every match traces back to a concrete edge in your knowledge graph -- no opaque embedding score.
- Privacy. The Obsidian vault never leaves disk; the JMAP query goes directly to your mail provider with your token. No Terraphim cloud component sits in the path.
- Composition. The role is just a JSON entry in `~/.config/terraphim/embedded_config.json`. Add another haystack tomorrow (calendar, contacts, browser history) and the same query sweeps it too.

A 4 GB process on your laptop holds the whole working set; queries return in single-digit milliseconds for the local side and a few hundred for the remote JMAP round trip.

## Wiring sketch

The role config is roughly thirty lines of JSON: two haystacks, one knowledge-graph pointer, no LLM. The Fastmail token is *not* in the config -- it is injected at runtime via `op run` from 1Password into the `JMAP_ACCESS_TOKEN` environment variable, so the secret never lands on disk:

```bash
exec op run --account my.1password.com \
  --env-file=<(echo 'JMAP_ACCESS_TOKEN=op://VAULT/ITEM/credential') \
  -- /Users/alex/.cargo/bin/terraphim-agent "$@"
```

Wrap that in `~/bin/terraphim-agent-pa`, `chmod +x`, and the JMAP haystack lights up only for queries that ask for it. The other roles keep using the bare `terraphim-agent` and never pay for the 1Password unlock.

## Why graph embeddings make this practical

The reason a unified role works at all -- not just for two haystacks but for any reasonable number -- is that Terraphim's graph-embeddings layer is sub-millisecond and deterministic. There is no per-query embedding API call to amortise across sources, no vector database to keep in sync, no opaque ranker that has to be retrained when you add a new haystack. The matching is byte-level Aho-Corasick traversal of an automaton built once at role-load time. We wrote up the engine in detail at [Why Graph Embeddings Matter](/posts/why-graph-embeddings-matter/); this Personal Assistant role is one application of that engine.

## Try it

The end-to-end how-to is in the docs: install the prerequisites, add the JSON snippet, write the wrapper, run three verification queries.

**Read the how-to: [Personal Assistant Role on docs.terraphim.ai](https://docs.terraphim.ai/howto/personal-assistant-role.html)**

One caveat worth surfacing up front: the published `terraphim-agent` on crates.io does not yet ship with the JMAP haystack (the `haystack_jmap` dependency is not published either). For email search you need to build from local source with `cargo build --release -p terraphim_agent --features jmap`. The how-to walks through the two Cargo.toml edits required.

## What is next

Personal Assistant is the smallest useful instance of "Terraphim as the front door for everything I read." Calendar (CalDAV), contacts (CardDAV), browser bookmarks, RSS, and AI session logs are all natural follow-ups -- each is a single haystack entry on the same role. The pattern composes; the cost stays linear in haystacks, not quadratic in cross-source queries.

If you want the underlying engine, start with [Why Graph Embeddings Matter](/posts/why-graph-embeddings-matter/). If you want to wire knowledge-graph hooks into your AI coding agent on the same machine, [Teaching AI Coding Agents with Knowledge Graph Hooks](/posts/teaching-ai-agents-with-knowledge-graphs/) covers that side of the same engine.
