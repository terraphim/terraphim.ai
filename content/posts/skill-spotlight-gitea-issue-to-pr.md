+++
title="Skill Spotlight Audit: Gitea Issue to PR Remains Blocked"
date=2026-09-07
draft=true

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "Gitea", "pull-requests", "workflow-security", "agent-skills"]

[extra]
toc = true
comments = true
+++

`gitea-issue-to-pr` is blocked because its Grok workflow logs failed tests, traceability, or review but still advances to validation and PR creation, and it does not gate PR creation on the validation verdict.
<!-- evidence: GIT-001 -->

This draft records why the current adapter should not be recommended, even though its written profile describes stronger gates.

<!-- more -->

## The intended profile

`gitea-issue-to-pr` instructs an agent to apply a Gitea tracker profile to the shared issue-to-PR contract.
<!-- evidence: SKL-019 -->

The profile text asks for repository identity checks, issue read-back, scoped branch delivery, pull-request verification, and an explicit stop before merge. The problem is not the intended contract. The problem is that the packaged Grok workflow does not enforce all of those boundaries itself.
<!-- evidence: GIT-007 -->

## Delivery can continue after failed gates

The workflow collects booleans for tests, traceability, and review. When one is false, it logs a warning and continues. It then invokes validation, records only the validation summary, and advances to the PR phase without reading validation's `passed` field.
<!-- evidence: GIT-005 -->

The release gate is fail-closed behaviour: every required negative or missing verdict must stop commit, push, comment, and PR creation. Executable tests must cover each failure path.
<!-- evidence: GIT-008 -->

## Remote state is delegated, not verified

The Grok workflow trusts remote postconditions reported by its PR agent instead of independently reading Gitea state.
<!-- evidence: GIT-002 -->

Prompting an agent to re-read a pull request is not equivalent to a structured workflow read-back. The workflow must fetch and compare owner, repository, head SHA, base, state, comment, and merged status before it reports completion.
<!-- evidence: GIT-006 -->

## Shell and portability blockers

The Grok workflow interpolates issue-derived owner, repository, index, title, base, and branch values into shell command text without a strict allow-list or shell-safe encoding.
<!-- evidence: GIT-003 -->

The `gitea-issue-to-pr` package includes a host-specific `http://bigbox:3456/v1` proxy configuration.
<!-- evidence: GIT-004 -->

The first finding requires validated identifiers, argument-safe command construction, and malicious-input tests. The second requires removing the private hostname from the package and documenting user-supplied endpoints instead.

## Static checks do not close these findings

Local checks passed for all checked-in signatures and manifests, all 54 TSM package validations, the strict Claude marketplace validation, and the issue-to-PR adapter validator; these checks establish package integrity and documentation structure, not runtime behaviour.
<!-- evidence: CAT-006 -->

The adapter validator can show that expected files and contract text are present. It does not prove fail-closed execution, safe interpolation, or independent remote verification.
<!-- evidence: CAT-009 -->

This post must stay in draft until GIT-001 through GIT-004 close and the corrected workflow is exercised.

Repository: [terraphim/terraphim-skills](https://github.com/terraphim/terraphim-skills). Reviewed source: [skill revision](https://github.com/terraphim/terraphim-skills/blob/RELEASE_COMMIT/skills/gitea-issue-to-pr/SKILL.md).

Publication rule: replace `RELEASE_COMMIT` only after the corrected workflow and its evidence are present in that revision.
