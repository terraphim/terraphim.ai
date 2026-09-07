+++
title="Skill Spotlight: Terraphim Grep, with Package and Runtime Evidence Kept Separate"
date=2026-09-07
draft=true

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "search", "knowledge-graph", "developer-tools", "agent-skills"]

[extra]
toc = true
comments = true
+++

The `terraphim-grep` skill package is not yet merged or published.
<!-- evidence: GRP-002 -->

The locally installed `terraphim-grep` 1.21.13 independently exercised search-only mode, JSON output, directory path scoping, and rejection of conflicting LLM flags.
<!-- evidence: GRP-001 -->

These are two different facts. This draft keeps them separate.

<!-- more -->

## What the candidate guide covers

`terraphim-grep` instructs an agent to use local search first, scope paths, request JSON when needed, and make LLM synthesis explicit.
<!-- evidence: SKL-047 -->

The guide begins with capability detection, recommends narrow identifier searches, and separates local retrieval from optional synthesis. It also tells an agent to preserve path scope when falling back to another search tool.
<!-- evidence: GRP-003 -->

That is documented workflow guidance. It does not show that the package is available in the live marketplace.

## What was exercised

The runtime check used installed version 1.21.13. A search-only JSON query scoped to `scripts/` returned four chunks, a null answer, and `SearchOnly` sufficiency. The same query scoped to `skills/` returned no chunks. Combining `--search-only` with `--answer` exited with code 2 and reported that the arguments conflict.
<!-- evidence: GRP-004 -->

They do not support speed, reliability, adoption, or package-availability claims.

## Publication boundary

The four community packages are source-branch release candidates on open, unmerged stacked pull requests #65, #66, and #72.
<!-- evidence: CAT-005 -->

`scripts/skills.sh` exposes exactly four free community skills: `kg-rlm-ingest`, `local-knowledge`, `terraphim-grep`, and `terraphim-learning-memory`; core and premium packages remain in the 54-entry marketplace catalogue and are not exposed through that installer.
<!-- evidence: CAT-011 -->

The live marketplace currently reports 47 active skills, not 54.
<!-- evidence: CAT-004 -->

Before changing this post from draft, merge the stacked PRs through #72, publish the skill package, verify its public catalogue page and community install route, and replace `RELEASE_COMMIT` in the source link below. Runtime examples should continue to state the binary version that produced them.

Repository: [terraphim/terraphim-skills](https://github.com/terraphim/terraphim-skills). Candidate source: [reviewed skill revision](https://github.com/terraphim/terraphim-skills/blob/RELEASE_COMMIT/skills/terraphim-grep/SKILL.md).
