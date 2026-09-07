+++
title="Skill Spotlight: Reading Issue to PR Core as a Contract"
date=2026-09-07
draft=true

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "issue-tracking", "pull-requests", "verification", "agent-skills"]

[extra]
toc = true
comments = true
+++

`issue-to-pr-core` passes as a written tracker-neutral contract; this does not prove that every adapter conforms at runtime.
<!-- evidence: CORE-001 -->

That boundary matters because a careful contract can coexist with an adapter that fails to enforce it.

<!-- more -->

## What the core is for

`issue-to-pr-core` instructs an agent to use a tracker-neutral issue-to-PR contract with risk routing, evidence, review, and explicit delivery gates.
<!-- evidence: SKL-025 -->

Tracker profiles are expected to supply issue identity, forge operations, and read-backs. The core remains the written location for mode selection, acceptance evidence, review convergence, and optional delivery operations.
<!-- evidence: CORE-002 -->

This is a contract description. It is not a statement that a Linear, Gitea, Grok, Claude, or OpenCode adapter executes every clause correctly.
<!-- evidence: CORE-003 -->

## The useful review questions

Reviewers can apply the contract as a checklist:

1. Was repository and issue identity resolved before mutation?
2. Does each acceptance criterion map to implementation and an executed check?
3. Did a failed required gate stop delivery?
4. Were remote mutations read back through the tracker or forge?
5. Were merge and live validation left off unless explicitly requested?

These questions come from the written preflight, acceptance-evidence, delivery, and tracker-profile sections. Passing the static adapter validator confirms the expected contract text and package relationships are present; it does not answer the runtime questions.
<!-- evidence: CORE-004 -->

## Why the distinction is practical

The current Gitea spotlight demonstrates the separation. Its profile delegates to the core, while its Grok workflow has independent blockers around failed gates, remote postconditions, shell values, and host-specific configuration. A claim that “the adapter follows the core” would therefore be broader than the evidence.
<!-- evidence: CORE-005 -->

The accurate publication language stays narrow: the core is a reviewed, signed written contract, and adapter conformance requires separate failure-path and postcondition tests.
<!-- evidence: CORE-006 -->

## Publication gate

Before stronger claims are made, each adapter needs independent tests for rejected inputs, required-gate failures, remote read-backs, `no_commit`, `no_pr`, and opt-in operations. Results should name the adapter revision and quote meaningful assertions rather than relying on an agent summary.

Repository: [terraphim/terraphim-skills](https://github.com/terraphim/terraphim-skills). Reviewed source: [contract revision](https://github.com/terraphim/terraphim-skills/blob/RELEASE_COMMIT/skills/issue-to-pr-core/SKILL.md).

Publication rule: replace `RELEASE_COMMIT` with the immutable revision covered by the final adapter evidence.
