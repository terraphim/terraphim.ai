+++
title="System Operator Demo: A Logseq Knowledge Graph Drives Enterprise MBSE Search"
date=2026-04-17

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "system-operator", "logseq", "knowledge-graph", "mbse", "systems-engineering"]

[extra]
toc = true
comments = true
+++

Terraphim's [System Operator role](https://github.com/terraphim/system-operator) is the demo we point people at when they want to see a real Logseq knowledge graph drive search. 1,347 Logseq pages, 52 of them carrying explicit `synonyms::` lines, covering Model-Based Systems Engineering vocabulary -- requirements, architecture, verification, validation, life cycle concepts. This post walks the demo end-to-end and shows the piece people miss: the KG is doing real work, not just re-ranking text matches.

<!-- more -->

## What the demo is

The `terraphim/system-operator` repository on GitHub is a **Logseq vault** -- flat folder of markdown files under `pages/`, one page per concept, with Logseq's bullet-tree syntax for structure and Terraphim-format `synonyms::` lines for the knowledge-graph layer. Two things make it a useful demo rather than a toy:

1. **Real MBSE vocabulary.** The synonyms are not invented; they track the INCOSE Systems Engineering Handbook v.4, the V-Model, and SEMP conventions. When you type `RFP`, the automaton normalises it to `acquisition need` because that is what the handbook calls it.
2. **Real scale.** 1,347 markdown files is enough to expose cold-start behaviour (~5-10 seconds to index on a laptop) without being so large it obscures the ranking signal.

## Run it

There is an automated setup script in the repo. As of today it clones to a durable path under `~/.config/terraphim/system_operator` instead of `/tmp`, so the vault survives a reboot:

```bash
./scripts/setup_system_operator.sh
```

Then either drive the role via the server --

```bash
cargo run --bin terraphim_server -- \
  --config terraphim_server/default/system_operator_config.json
curl "http://127.0.0.1:8000/documents/search?q=RFP&role=System%20Operator&limit=5"
```

-- or via the `terraphim-agent` CLI after adding the role entry to `~/.config/terraphim/embedded_config.json`:

```bash
terraphim-agent config reload
terraphim-agent search --role "System Operator" --limit 5 "RFP"
```

The full config snippet and the `embedded_config.json` entry are in the [`README_SYSTEM_OPERATOR.md`](https://github.com/terraphim/terraphim-ai/blob/main/terraphim_server/README_SYSTEM_OPERATOR.md).

## The piece people miss

Search-over-notes tools usually describe ranking in terms of "it uses a knowledge graph". That sentence hides a lot. Is the graph actually consulted at query time? Is it just a post-hoc re-ranker on top of BM25? Does it expand synonyms? On what vocabulary?

Terraphim exposes the answer directly. `validate --connectivity` prints which words in your query the automaton matched and what canonical terms they normalised to:

```
$ terraphim-agent validate --role "System Operator" --connectivity \
    "RFP business analysis life cycle model business requirements documentation tree"

Connectivity Check for role 'System Operator':
  Connected: false
  Matched terms: ["acquisition need", "business or mission analysis",
                  "business requirements", "documentation tree",
                  "life cycle concepts"]
```

Five query fragments, five canonical matches. `RFP` collapsed to `acquisition need` (its synonym, from `Acquisition need.md` in the vault). `business analysis` collapsed to `business or mission analysis` (INCOSE terminology). `life cycle model` collapsed to `life cycle concepts`. None of this is text matching -- the word `RFP` does not appear in the canonical page body; it lives in the `synonyms::` line.

Once a query is normalised, the ranker walks the graph. A document that mentions `acquisition need` directly outranks one that mentions it through three synonym hops, and both outrank a document that mentions none of the canonical terms at all. Ranks come back with concrete integer scores -- `[13]` on a top result, not an opaque 0.87 cosine.

## How it compares to the Personal Assistant role

We [wrote up the Personal Assistant role yesterday](/posts/personal-assistant-role-jmap-obsidian/): a private per-user role that indexes a Fastmail mailbox plus an Obsidian vault. Same engine, same ranker, different haystacks. The knowledge graph there is a small `kg/` folder inside the user's vault with 14 synonym files covering personal vocabulary (`bun` with `npm`/`yarn`/`pnpm` synonyms, `odilo`, `invoice`, `meeting`).

The two roles expose the same pattern at two scales:

| | System Operator | Personal Assistant |
| --- | --- | --- |
| KG size | 52 synonym files, 1,300-concept vocabulary | 14 synonym files, ~30-concept personal vocabulary |
| Haystacks | 1 (Logseq repo) | 2 (Obsidian vault + Fastmail JMAP) |
| Source | Public GitHub repo | Private user files and mailbox |
| Audience | Demos, onboarding, public showcase | One user |
| Lifetime | Frozen per release | Edited daily, rebuilt in 20 ms per edit |

Both use `terraphim-graph` ranking. Both build an Aho-Corasick automaton once at role-load time. Both run in a 4 GB process on a laptop with no cloud round-trip. The only interesting difference is the vocabulary, which is exactly the separation of concerns a knowledge-graph-first design is supposed to deliver.

## Why this matters for teams evaluating MBSE tooling

If you are evaluating Terraphim for a systems engineering group, the System Operator role is the honest starting point. It runs on a laptop against a public vault; you can check that every synonym mapping traces back to a concrete page; you can diff the `pages/` folder against the INCOSE handbook and argue about terminology. When your team's own vocabulary diverges (every organisation's does), you clone the repo, edit `synonyms::` lines, and the graph rebuilds in 20 milliseconds without a retraining step.

The expensive part of enterprise search is not the ranker. It is the vocabulary. A deterministic graph makes the vocabulary an asset you curate, not a black box you tune.

## Try it

```bash
git clone https://github.com/terraphim/terraphim-ai
cd terraphim-ai
./scripts/setup_system_operator.sh
cargo run --bin terraphim_server -- \
  --config terraphim_server/default/system_operator_config.json
```

Or cut to the CLI if you already have `terraphim-agent` installed -- the `embedded_config.json` snippet is in the [README](https://github.com/terraphim/terraphim-ai/blob/main/terraphim_server/README_SYSTEM_OPERATOR.md).

For the underlying engine, start with [Why Graph Embeddings Matter](/posts/why-graph-embeddings-matter/). For the personal-productivity analogue, see the [Personal Assistant role post](/posts/personal-assistant-role-jmap-obsidian/).
