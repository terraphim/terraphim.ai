+++
title="Terraphim Skills: 54 Agent Workflow Guides in the Release Candidate"
date=2026-09-07
draft=true

[taxonomies]
categories = ["Announcements"]
tags = ["Terraphim", "agent-skills", "developer-tools", "evidence", "workflows"]

[extra]
toc = true
comments = true
+++

The source-branch release candidate contains 54 skill names in `scripts/skills.sh`, and the marketplace candidate lists the same 54 names.
<!-- evidence: CAT-001 -->

The live marketplace currently reports 47 active skills, not 54.
<!-- evidence: CAT-004 -->

This draft describes the candidate catalogue without presenting every candidate as released or installable.

<!-- more -->

## How to read this catalogue

Each of those 54 candidate skills has a `SKILL.md` and a `skill.toml`.
<!-- evidence: CAT-002 -->

The candidate marketplace metadata version is 1.6.1.
<!-- evidence: CAT-003 -->

Local checks passed for all checked-in signatures and manifests, all 54 TSM package validations, the strict Claude marketplace validation, and the issue-to-PR adapter validator; these checks establish package integrity and documentation structure, not runtime behaviour.
<!-- evidence: CAT-006 -->

The descriptions below say what each guide instructs an agent to do. They do not guarantee that the agent will complete the task, produce a correct result, or satisfy a deployment environment. The [repository](https://github.com/terraphim/terraphim-skills) is the public project link. Before publication, replace `RELEASE_COMMIT` in the [reviewed source link](https://github.com/terraphim/terraphim-skills/tree/RELEASE_COMMIT) with the immutable release commit.

## Research, specification, and phased delivery

- `acceptance-testing` instructs an agent to turn requirements into acceptance criteria, test cases, test data, and a sign-off checklist.
<!-- evidence: SKL-001 -->
- `disciplined-research` instructs an agent to map the existing system, constraints, risks, and exclusions before design.
<!-- evidence: SKL-014 -->
- `disciplined-quality-evaluation` instructs an agent to assess research or design documents with the six-dimension KLS framework before phase transitions.
<!-- evidence: SKL-013 -->
- `disciplined-design` instructs an agent to turn approved research into a file-level implementation plan with signatures, tests, and sequencing.
<!-- evidence: SKL-011 -->
- `disciplined-specification` instructs an agent to refine implementation details, edge cases, and trade-offs through a structured interview.
<!-- evidence: SKL-015 -->
- `disciplined-implementation` instructs an agent to execute an approved plan step by step with tests and reviewable changes.
<!-- evidence: SKL-012 -->
- `disciplined-verification` instructs an agent to verify implementation against design with tests, coverage evidence, and traceability.
<!-- evidence: SKL-017 -->
- `disciplined-validation` instructs an agent to validate a system against original requirements and gather structured acceptance evidence.
<!-- evidence: SKL-016 -->

## Review, evidence, and safety

- `code-review` instructs an agent to review Rust and WebAssembly code for correctness, security, performance, and maintainability findings.
<!-- evidence: SKL-005 -->
- `deterministic-rlm-review` instructs an agent to run capability-routed review perspectives and reconcile severity-ranked findings.
<!-- evidence: SKL-009 -->
- `quality-gate` instructs an agent to assemble review, security, performance-risk, traceability, acceptance, and relevant visual evidence for a change.
<!-- evidence: SKL-034 -->
- `requirements-traceability` instructs an agent to map requirements through design, implementation, tests, and evidence, then flag gaps.
<!-- evidence: SKL-037 -->
- `security-audit` instructs an agent to review Rust and WebAssembly input handling, unsafe code, defaults, and relevant OWASP risks.
<!-- evidence: SKL-043 -->
- `structural-pr-review` instructs an agent to produce a severity-ranked pull-request review with file overviews, confidence, and an architecture diagram.
<!-- evidence: SKL-045 -->
- `ubs-scanner` instructs an agent to run Ultimate Bug Scanner and incorporate its findings into a quality-gate workflow.
<!-- evidence: SKL-053 -->
- `git-safety-guard` instructs an agent to configure a fail-open pre-tool guard for selected destructive Git and filesystem commands.
<!-- evidence: SKL-021 -->

## Rust and application engineering

- `architecture` instructs an agent to design Rust and WebAssembly architecture, APIs, modules, and decision records without implementing code.
<!-- evidence: SKL-004 -->
- `implementation` instructs an agent to implement an approved design with tests, documentation, and lint checks.
<!-- evidence: SKL-024 -->
- `testing` instructs an agent to write and run unit, integration, property-based, and benchmark tests and analyse failures.
<!-- evidence: SKL-052 -->
- `debugging` instructs an agent to reproduce and diagnose Rust failures, use logging or profiling, and remove temporary debug changes.
<!-- evidence: SKL-007 -->
- `rust-development` instructs an agent to apply idiomatic Rust patterns for async code, errors, traits, safety, and performance.
<!-- evidence: SKL-039 -->
- `rust-performance` instructs an agent to profile and optimise Rust code with benchmarks, memory analysis, SIMD, and zero-copy techniques.
<!-- evidence: SKL-042 -->
- `rust-observability` instructs an agent to configure tracing, OpenTelemetry, Prometheus metrics, request context, and environment-specific logging for Rust services.
<!-- evidence: SKL-041 -->
- `rust-ci-cd` instructs an agent to configure Rust CI/CD checks, dependency policy, coverage, benchmark, and release workflows.
<!-- evidence: SKL-038 -->
- `rust-fleet-standard` instructs an agent to apply the repository's shared Rust build, validation, issue-flow, and knowledge-stack conventions.
<!-- evidence: SKL-040 -->
- `gpui-components` instructs an agent to generate GPUI components using Zed-style rendering, state, completion, and theming patterns.
<!-- evidence: SKL-022 -->
- `visual-testing` instructs an agent to define screenshot coverage, rendering stabilisation, baseline management, and CI checks for UI changes.
<!-- evidence: SKL-054 -->

## Knowledge, search, and agent orchestration

- `terraphim-grep` instructs an agent to use local search first, scope paths, request JSON when needed, and make LLM synthesis explicit.
<!-- evidence: SKL-047 -->
- `terraphim-learning-memory` instructs an agent to retrieve, assess, verify, capture, and revisit durable evidence through available Terraphim components.
<!-- evidence: SKL-049 -->
- `learning-capture` instructs an agent to capture and query failed-command records, but activation is blocked pending safety and accuracy fixes.
<!-- evidence: SKL-028 -->
- `local-knowledge` instructs an agent to search configured personal notes and role documentation through Terraphim.
<!-- evidence: SKL-031 -->
- `session-search` instructs an agent to search imported coding-assistant session history for previous conversations and decisions.
<!-- evidence: SKL-044 -->
- `kg-rlm-ingest` instructs an agent to distil sourced material into role-scoped knowledge-graph notes, using deterministic extraction before optional RLM work.
<!-- evidence: SKL-027 -->
- `terraphim-hooks` instructs an agent to configure knowledge-graph-based text replacement for supported command and commit hooks.
<!-- evidence: SKL-048 -->
- `terraphim-rlm` instructs an agent to route multi-step, multi-file work through budgeted recursive decomposition and reconciliation tools.
<!-- evidence: SKL-051 -->
- `adf-orchestrate` instructs an agent to dispatch, monitor, or cancel approved asynchronous ADF work on a user-controlled server.
<!-- evidence: SKL-002 -->

## Issues, pull requests, and collaboration

- `issue-to-pr-core` instructs an agent to use a tracker-neutral issue-to-PR contract with risk routing, evidence, review, and explicit delivery gates.
<!-- evidence: SKL-025 -->
- `gitea-issue-to-pr` instructs an agent to apply a Gitea tracker profile to the shared issue-to-PR contract.
<!-- evidence: SKL-019 -->
- `linear-issue-to-pr` instructs an agent to take a Linear issue through a phased engineering and pull-request workflow.
<!-- evidence: SKL-029 -->
- `gitea-pagerank-workflow` instructs an agent to prioritise and manage Gitea issues and dependencies with `gtr`.
<!-- evidence: SKL-020 -->
- `terraphim-linear` instructs an agent to fetch and inspect Linear issues through semantic aliases or structured output.
<!-- evidence: SKL-050 -->
- `linear-ticket-writer` instructs an agent to draft structured Linear tickets with lifecycle, priority, state, and estimate fields.
<!-- evidence: SKL-030 -->
- `open-source-contribution` instructs an agent to prepare issues and pull requests that follow a project's contribution conventions.
<!-- evidence: SKL-033 -->
- `community-engagement` instructs an agent to support contributors, discussions, release notes, and open-source community practice.
<!-- evidence: SKL-006 -->

## Documentation, research, and communication

- `documentation` instructs an agent to write Rust API, README, architecture, and contributor documentation in the project's style.
<!-- evidence: SKL-018 -->
- `md-book` instructs an agent to work with the MD-Book documentation generator, including highlighting, live reload, search, and templates.
<!-- evidence: SKL-032 -->
- `grounded-content-writer` instructs an agent to attach citations to material claims and recheck numbers against their sources.
<!-- evidence: SKL-023 -->
- `technical-book-writer` instructs an agent to structure a long technical explanation with progressive concepts, diagrams, and chapter files.
<!-- evidence: SKL-046 -->
- `deep-research` instructs an agent to route bounded or open research across file-only and externally enhanced modes, then reconcile evidence.
<!-- evidence: SKL-008 -->
- `repeatable-demo-video` instructs an agent to create scripted terminal or browser recordings as repeatable review evidence.
<!-- evidence: SKL-036 -->
- `judge` instructs an agent to assess outputs with semantic, pragmatic, and syntactic dimensions and record structured verdicts.
<!-- evidence: SKL-026 -->

## Operations and delivery tools

- `ai-config-management` instructs an agent to specify configuration control, semantic governance, drift detection, traceability, and change control for AI artefacts.
<!-- evidence: SKL-003 -->
- `devops` instructs an agent to work on Rust CI/CD, containers, deployment automation, and infrastructure as code.
<!-- evidence: SKL-010 -->
- `quickwit-log-search` instructs an agent to investigate logs and incidents with Quickwit using one of three index-discovery modes.
<!-- evidence: SKL-035 -->

## Release boundaries

`terraphim-grep` and `terraphim-learning-memory` are source-branch release candidates on open, unmerged stacked pull requests #65 and #66.
<!-- evidence: CAT-005 -->

`scripts/skills.sh` is a guidance-file installer: it downloads only each skill's `SKILL.md`, not every file declared by that skill's manifest.
<!-- evidence: CAT-007 -->

`learning-capture` and `gitea-issue-to-pr` remain blocked in this campaign. Their spotlight drafts explain the findings and the checks required before either can be recommended.
<!-- evidence: CAT-010 -->
