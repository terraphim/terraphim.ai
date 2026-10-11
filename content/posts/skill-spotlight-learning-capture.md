+++
title="Skill Spotlight Audit: Why Learning Capture Is Not Ready to Recommend"
date=2026-09-07
draft=true

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "learning", "hooks", "security", "agent-skills"]

[extra]
toc = true
comments = true
+++

`learning-capture` is blocked because `terraphim-agent` 1.21.13 redacts captured error output but stores the parsed command and full command chain without applying the same redaction; generated and documented hook wrappers also echo the original hook payload after invoking the CLI.
<!-- evidence: LRN-001 -->

Do not enable the workflow from this draft. The useful idea needs a safer implementation and accurate activation guidance first.

<!-- more -->

## Intended workflow

`learning-capture` instructs an agent to capture and query failed-command records, but activation is blocked pending safety and accuracy fixes.
<!-- evidence: SKL-028 -->

The intended loop is straightforward: retain a failed command with context, add a verified correction, and query that record before repeating similar work. The current package documentation, however, makes the capture boundary too broad for a recommendation.
<!-- evidence: LRN-006 -->

## Security blocker

The record format contains the failed command and redacted stderr or stdout. In version 1.21.13, command and chain fields bypass the error-output redaction. The documented and generated wrappers read the full hook input, forward it to `terraphim-agent learn hook`, and then echo the original input again.
<!-- evidence: LRN-003 -->

Commands and tool output can contain tokens, credentials, personal data, internal URLs, or other restricted values. A fail-open hook does not solve persistence or re-emission risk. The release gate therefore requires redaction before storage, removal of original-payload re-emission, adversarial secret fixtures, and an independent security review.
<!-- evidence: LRN-004 -->

## Accuracy blocker

`learning-capture` must not be recommended for activation because its install-hook activation and storage documentation are not accurate across the claimed hosts.
<!-- evidence: LRN-002 -->

The current text presents Claude Code, Codex, and OpenCode installation commands and one fixed Linux-style storage path. The publication gate is an end-to-end check on every named host: install, activate, cause a controlled non-secret failure, locate the resulting record, query it, add a correction, and verify read-back. Documentation then needs to match the observed host-specific behaviour.
<!-- evidence: LRN-005 -->

## Why a signed package is not enough

The community change passed 45 Python tests, 73% aggregate branch coverage, six Bun tests, signed-manifest and installer-policy validation, TSM validation for all four community skills, and an isolated install of four skills with zero skipped.
<!-- evidence: CAT-006 -->

Those community distribution checks do not resolve this premium package's runtime and security blockers.

A valid digest can prove that downloaded bytes match reviewed bytes. It cannot prove that those bytes redact secrets, activate on every claimed host, or store data where the guide says.
<!-- evidence: CAT-008 -->

This spotlight stays an audit draft until those runtime and security gates pass.

Repository: [terraphim/terraphim-skills](https://github.com/terraphim/terraphim-skills). Reviewed source: [skill revision](https://github.com/terraphim/terraphim-skills/blob/RELEASE_COMMIT/skills/learning-capture/SKILL.md).

Publication rule: replace `RELEASE_COMMIT`, do not turn this into setup guidance, and do not include an activation command until LRN-001 and LRN-002 are closed with executable evidence.
