+++
title="Sentrux vs Terraphim: Two Approaches to AI Code Quality Evaluation"
description="A technical comparison of Sentrux's structural analysis engine and Terraphim's semantic evaluation toolkit for measuring AI agent contributions to a codebase"
date=2026-04-29

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "code-quality", "AI-agents", "evaluation", "comparison", "sentrux"]
[extra]
toc = true
comments = true
+++

As AI agents write more and more production code, the question shifts from "can the agent write code?" to "can we verify the code is good?" Two tools tackle this from opposite ends: Sentrux measures structural health, Terraphim measures semantic completeness. Neither is complete without the other.

<!-- more -->

## The Problem They Both Solve

An AI agent that generates 500 lines of syntactically correct Rust can still degrade a codebase. It might introduce tight coupling, leave behind unimplemented stubs, create circular dependencies, or raise the cyclomatic complexity past any reasonable threshold. Standard CI pipelines catch compilation errors and failing tests. They do not catch architectural erosion.

Both Sentrux and the Terraphim evaluation toolkit are designed to close that gap. They just do so from fundamentally different perspectives.

---

## Sentrux: Structural Analysis

[Sentrux](https://github.com/sentrux/sentrux) (v0.5.7, MIT, 27.7k lines of Rust) is a real-time structural analysis engine. It parses source code into an AST using tree-sitter, builds a dependency graph, and computes a quality signal from 0 to 10,000.

### Five Root Cause Metrics

Sentrux computes a geometric mean across five orthogonal dimensions:

| Metric | What it captures |
|---|---|
| **Modularity** | Fan-in and fan-out between modules; god file detection |
| **Acyclicity** | Circular dependency count and which files participate |
| **Depth** | Maximum dependency chain length; instability score |
| **Equality** | Cyclomatic complexity distribution (Gini coefficient); large files |
| **Redundancy** | Dead functions; duplicate code groups |

These are structural facts derived from the AST and dependency graph, not text patterns. Sentrux does not care what the code says; it cares how it connects.

### How It Works with Agents

Sentrux ships a native MCP server with nine tools. The intended agent workflow is:

```
sentrux.scan("/path/to/project")
  -> { quality_signal: 7342, files: 139, bottleneck: "modularity" }

sentrux.session_start()
  -> baseline saved

... agent writes code ...

sentrux.session_end()
  -> { pass: false, signal_before: 7342, signal_after: 6891,
       summary: "Quality degraded during this session" }
```

The agent gets a precise numeric verdict with a named bottleneck. It can iterate: check the bottleneck, fix it, call `rescan`, repeat.

### The GUI

Sentrux includes a live treemap built with egui and wgpu. Files are sized by metric contribution and glow when modified. Dependency edges are drawn between coupled files. A file system watcher (notify) feeds changes over crossbeam-channel to the renderer in real time. The same process that runs the GUI hosts the MCP server, so you can watch architectural changes happen as the agent works.

### Language Support

52 languages via tree-sitter plugins. Each plugin is a `plugin.toml` and a `tags.scm` query file. No Rust required to add a language.

---

## Terraphim Evaluation Toolkit: Semantic Completeness

The Terraphim approach lives across two production crates in [terraphim-ai](https://github.com/terraphim/terraphim-ai): `terraphim_codebase_eval` and `terraphim_negative_contribution`. These are not a conceptual framework or a shell script wrapper; they are typed Rust libraries integrated into the agent review pipeline.

### The Manifest System (`terraphim_codebase_eval`)

The evaluation manifest is a TOML file that describes a before/after comparison at the git SHA level:

```toml
[[haystacks]]
id = "baseline"
path = "/srv/repo"
commit_sha = "abc123"
state = "baseline"

[[haystacks]]
id = "candidate"
path = "/srv/repo"
commit_sha = "def456"
state = "candidate"

[[roles]]
role_id = "code-reviewer"
description = "Reviews for bugs and maintainability"
term_sets = ["bug-patterns", "code-smells"]

[roles.scoring_weights]
search_score = 1.0
graph_density = 0.8
entity_count = 1.0

[[queries]]
query_text = "highlight potential bugs"
role_id = "code-reviewer"
expected_signal = "increase"
confidence_threshold = 0.6

[thresholds]
improved_pct = 10.0
degraded_pct = 5.0
critical_test_failures = 0
```

Roles define the evaluation perspective. Each role carries named term sets (Aho-Corasick dictionaries built from domain knowledge graphs) and per-dimension scoring weights. Queries specify what to search for and in which direction the score should move. The manifest is validated for referential integrity before execution: any query that references a non-existent role is rejected at load time, not at runtime.

The verdict logic is explicit: if the weighted score increases by more than `improved_pct`, the contribution is classified as Improved; if it drops by more than `degraded_pct`, it is Degraded; any new test failure triggers immediate Degraded regardless of scores.

### The EDM Scanner (`terraphim_negative_contribution`)

The Explicit Deferral Marker (EDM) scanner answers a specific and critical question: did the agent ship stubs as production code?

It uses the Aho-Corasick automata to detect markers in Rust source that indicate deferred implementation:

- `todo!()`
- `unimplemented!()`
- `panic!("not implemented")`
- `panic!("TODO")`

The scanner is production-only by design. It automatically skips:

- `tests/`, `examples/`, `benches/` directories
- `build.rs`
- Files ending in `_test.rs`
- Any file containing `#[test]` or `#[cfg(test)]`

Suppression is available per-line: `// terraphim: allow(stub)` silences the finding on that line only. Every finding carries a file path, line number, severity, category, confidence (0.95), and a suggestion drawn from the thesaurus URL metadata.

The scanner outputs a `ReviewAgentOutput` struct consumed directly by the Terraphim review pipeline. An agent that ships one `todo!()` in production code fails the gate.

---

## Side-by-Side Comparison

| Dimension | Sentrux | Terraphim EDM Scanner | Terraphim Manifest Eval |
|---|---|---|---|
| **Core mechanism** | tree-sitter AST + dependency graph | Aho-Corasick on EDM pattern thesaurus | Aho-Corasick on domain KG + weighted scoring |
| **What it measures** | Architecture: coupling, cycles, complexity | Incomplete implementations in production code | Semantic quality delta between two git SHAs |
| **Language scope** | 52 languages | Rust only (production files) | Any language with KG term sets |
| **Unit of comparison** | Quality signal delta within a session | Pass/fail per file | Before/after manifest with role-weighted scores |
| **Agent integration** | MCP server (9 tools, session lifecycle) | `ReviewAgentOutput` struct in review pipeline | `EvaluationManifest` loaded per evaluation run |
| **False positive risk** | Low (graph-structural, not text) | Very low (exact stub patterns, test exclusions) | Medium (depends on KG quality) |
| **Customisation** | `rules.toml` (layer boundaries, thresholds) | `// terraphim: allow(stub)` suppression | KG term sets, role weights, query direction |
| **Live feedback** | Yes (file watcher, treemap, MCP) | No (batch scan) | No (batch manifest) |
| **Verdict granularity** | Named bottleneck + per-metric breakdown | Finding list with file:line and suggestion | Improved / Degraded / Neutral with percentage |

---

## Where They Complement Each Other

These tools are not alternatives. They operate at different layers of the quality stack:

**Sentrux** answers: *Is the architecture getting worse?*

**Terraphim EDM Scanner** answers: *Did the agent leave stubs in production code?*

**Terraphim Manifest Eval** answers: *Did the agent improve or degrade domain-specific semantic quality across these two commits?*

A complete agent quality gate combines all three:

1. `sentrux session_start` before the agent begins work
2. Agent writes code
3. `sentrux session_end` to verify no structural degradation
4. Terraphim EDM scan to verify no stubs shipped to production
5. Terraphim manifest eval (optional, for domain-specific semantic coverage) comparing the baseline and candidate SHAs

If any gate fails, the contribution is blocked. The agent gets specific, actionable feedback: a named structural bottleneck from Sentrux, a file and line number from the EDM scanner, or a percentage degradation from the manifest evaluator.

---

## Choosing Your Starting Point

If you are instrumenting an AI agent pipeline today, start with the Terraphim EDM scanner. It requires no configuration beyond pointing it at your Rust source. It has a binary pass/fail verdict, zero false positives on well-written production code, and integrates directly into the existing `ReviewAgentOutput` pipeline.

Add Sentrux when you want continuous architectural visibility. The MCP integration means the agent can self-correct in real time rather than discovering structural problems only at gate check.

Add the Terraphim manifest evaluation when you have a domain knowledge graph and want to verify that the agent's changes improve semantic coverage in your specific domain, not just compile and pass tests.

Together, they give you three independent quality signals that a capable agent must satisfy simultaneously: structural soundness, implementation completeness, and semantic improvement.

---

## Further Reading

- [Teaching AI Agents to Learn from Mistakes](/posts/teaching-ai-agents-to-learn-from-mistakes/)
- [Why Graph Embeddings Matter](/posts/why-graph-embeddings-matter/)
- [Guarding OpenCode with DCG](/posts/guarding-opencode-with-dcg/)
- Sentrux repository: [github.com/sentrux/sentrux](https://github.com/sentrux/sentrux)
- Terraphim AI: [github.com/terraphim/terraphim-ai](https://github.com/terraphim/terraphim-ai)
