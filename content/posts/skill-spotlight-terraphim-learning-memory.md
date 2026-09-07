+++
title="Skill Spotlight: Terraphim Learning Memory as Orchestration Guidance"
date=2026-09-07
draft=true

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "agent-memory", "knowledge-graph", "provenance", "agent-skills"]

[extra]
toc = true
comments = true
+++

`terraphim-learning-memory` is orchestration guidance that starts with capability discovery and routes writes to owning Terraphim components; it is not evidence of a shipped memory runtime.
<!-- evidence: MEM-002 -->

That distinction is the point of this draft: useful memory practice starts by checking what the installed tool can actually do.

<!-- more -->

## Release status first

`terraphim-grep` and `terraphim-learning-memory` are source-branch release candidates on open, unmerged stacked pull requests #65 and #66.
<!-- evidence: CAT-005 -->

The installed `terraphim-agent` 1.21.13 has no `memory` namespace.
<!-- evidence: MEM-001 -->

Do not read the candidate skill as an announcement of a released memory command. Before publication, replace `RELEASE_COMMIT` in the [candidate source link](https://github.com/terraphim/terraphim-skills/blob/RELEASE_COMMIT/skills/terraphim-learning-memory/SKILL.md) and confirm the package appears on the live catalogue.

## What the guide asks an agent to do

`terraphim-learning-memory` instructs an agent to retrieve, assess, verify, capture, and revisit durable evidence through available Terraphim components.
<!-- evidence: SKL-049 -->

The practical boundary is capability discovery. An agent checks installed help before selecting a command, then uses the component that owns the information: failed-command learning, session history, local role knowledge, or a project knowledge graph. A successful route message is not treated as proof that content was stored.
<!-- evidence: MEM-004 -->

This makes the guide an orchestration layer over capabilities that may differ between installations. It also keeps temporary task progress out of long-lived knowledge unless there is a durable, sourced fact to preserve.
<!-- evidence: MEM-008 -->

## Deterministic before recursive

The learning-memory guidance assigns builds and tests to implementation or verification, and makes deterministic KG extraction the default with RLM optional only for long, genuinely novel material.
<!-- evidence: MEM-003 -->

That means a normal “remember this” request should not trigger a broad build or recursive decomposition. Build results can become evidence, but the memory guide does not own compilation. Likewise, deterministic extraction remains the normal route for knowledge-graph material; RLM is a bounded fallback rather than the default.
<!-- evidence: MEM-005 -->

## What would justify stronger wording

Publication can call this a released skill only after PRs #65 and #66 merge, the package is published, and its live catalogue and install route are checked.
<!-- evidence: MEM-006 -->

Claims about a `memory` runtime need separate evidence from a released binary whose help exposes that namespace, followed by exercised capture, read-back, correction, retirement, and failure behaviour. Until then, the accurate description is narrower: this candidate teaches capability-aware memory orchestration across existing Terraphim components.
<!-- evidence: MEM-007 -->

Repository: [terraphim/terraphim-skills](https://github.com/terraphim/terraphim-skills). Candidate source: [reviewed skill revision](https://github.com/terraphim/terraphim-skills/blob/RELEASE_COMMIT/skills/terraphim-learning-memory/SKILL.md).

Editorial source gate: replace `RELEASE_COMMIT` after the stacked pull requests merge and the GitHub mirror contains the reviewed commit.
