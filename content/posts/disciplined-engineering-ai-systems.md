+++
title="Disciplined Engineering: How We Build AI Systems That Actually Work"
date=2026-04-17

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "ai", "engineering", "v-model", "developer-tools", "coding-agents", "discipline"]
[extra]
toc = true
comments = true
+++

AI coding agents ship code fast. But fast is not the same as correct. We built a V-model skill framework that gives AI agents the engineering discipline they lack, and you can install it in 30 seconds.

<!-- more -->

## The Vibe Coding Problem

A new pattern has taken hold in AI-assisted development. Developers describe what they want, the agent writes code, tests pass, the PR gets merged. It feels productive. It is productive -- until it is not.

Every AI-generated PR we review at Zestic AI shows the same failure modes. Scope creep: the agent "improves" code it was never asked to touch. No traceability: you cannot trace the final implementation back to the original requirements. Knowledge loss: context from one session vanishes by the next. The industry calls this "vibe coding" and it produces systems that are fast to build and expensive to maintain.

The missing piece is not better models. It is engineering discipline. The agent shipped code, but nobody verified it does what was actually asked for.

## The V-Model Walkthrough

The V-model is a software engineering lifecycle that maps each planning phase on the left to a corresponding testing phase on the right. The left side asks "what should we build?" and the right side asks "did we build it correctly?" We adapted it for AI agent development with five phases plus a critical half-phase most frameworks skip entirely.

```
Phase 1: Research      <-->  Phase 5: Validation
Phase 2: Design        <-->  Phase 4: Verification
Phase 2.5: Specification
Phase 3: Implementation
```

**Phase 1: Research.** Before writing a single line of code, understand the problem. Read existing code, check for prior art, understand why the current approach exists before replacing it. This is where most AI agents fail -- they read a task description and start coding immediately.

**Phase 2: Design.** Design is about deciding what NOT to do. The output includes file changes, function signatures, test strategy, and an explicit NOT-doing list. AI agents will cheerfully refactor surrounding code, add error handling for impossible scenarios, and create abstractions for one-time operations. The design phase draws the boundary.

**Phase 2.5: Deep Specification.** This is the phase most frameworks skip entirely, and the one that saves the most time. It is a structured specification interview across ten dimensions, designed to surface hidden assumptions before they become production incidents.

The ten dimensions:

1. **Concurrency and race conditions**: "Two users edit the same record simultaneously. Last-write-wins, first-write-wins, or conflict detection?"
2. **Failure modes and recovery**: "The third-party API is down. Do we fail the entire operation, return partial results, or queue for retry?"
3. **Edge cases and boundaries**: "The input contains 10 million records. Does the algorithm still work? What is the memory bound?"
4. **User mental models**: "Users see 'pending' status. They refresh 10 times. Is there feedback about progress, or just waiting?"
5. **Scale and performance**: "This query joins 3 tables. At 1M rows each, what is the expected latency? Index strategy?"
6. **Security and privacy**: "This endpoint returns user data. Who can call it? What authorisation checks exist?"
7. **Integration effects**: "This creates a new entity. Does search index update? Notifications fire? Analytics track it?"
8. **Migration and compatibility**: "Existing users have data in the old format. Migration strategy during rollout?"
9. **Accessibility and internationalisation**: "Keyboard-only users -- is every action reachable without a mouse?"
10. **Operational concerns**: "User reports 'it is not working'. What logs and traces do we need to debug?"

The interview is convergence-based. It keeps asking questions until the answers stop revealing new information -- specifically, until two consecutive rounds yield no new concerns. This is not a single pass. It is a loop:

```
while has_new_concerns or dimensions_covered < 6:
    questions = generate_from_unexplored_areas(previous_answers)
    answers = ask_user(questions)
    new_concerns = analyse_for_novelty(answers)
    if no_new_concerns_for_2_rounds:
        offer_to_conclude()
```

In practice, spending two hours in Phase 2.5 saves roughly two days of debugging. The maths is not close. Every "what if?" surfaced here is a production incident that never happens.

**Phase 3: Implementation.** Now, and only now, the agent writes code. Each step has tests written alongside. An execution log tracks what was done and why. No changes outside the scope defined in Phase 2.

**Phase 4: Verification.** Did we build it according to the design? Unit and integration tests run against the design specification. A traceability matrix links requirements to tests. If a design flaw surfaces, it loops back to Phase 2.

**Phase 5: Validation.** Did we build what was actually asked for? System testing against non-functional requirements, user acceptance, formal sign-off. If a requirements gap appears, it loops back to Phase 1. Research validates against Validation. Design verifies against Verification. The symmetry is the point.

## Terraphim Skills: The V-Model as Executable Code

Philosophy without enforcement is just documentation nobody reads. We encoded every phase of the V-model as executable skills in [terraphim-skills](https://github.com/terraphim/terraphim-skills), a skill pack for AI coding agents. 37 skills cover the full lifecycle.

Install in 30 seconds:

```bash
npx skills add terraphim/terraphim-skills
```

This works across Claude Code, Cursor, Codex, Copilot, VS Code, Gemini CLI, Amp, Goose, Letta, and OpenCode. One install, every agent gains access to every skill.

| Skill | Phase | What It Does |
| --- | --- | --- |
| `disciplined-research` | 1 | Forces problem exploration before solutions |
| `disciplined-design` | 2 | Produces implementation plan with NOT-doing list |
| `disciplined-specification` | 2.5 | Conducts deep specification interview (10 dimensions) |
| `disciplined-implementation` | 3 | Builds with tests at each step, execution log |
| `disciplined-verification` | 4 | Verifies output against design specification |
| `disciplined-validation` | 5 | Validates against original requirements |
| `quality-gate` | 3 to 4 | Code review and traceability check |
| `git-safety-guard` | All | Blocks destructive git commands before execution |
| `terraphim-hooks` | All | Knowledge graph text replacement (Aho-Corasick) |
| `session-search` | All | Search past sessions for prior art and context |

Start with `disciplined-research` on your next task. Watch how it changes the agent's approach: instead of jumping to code, it explores the problem space, identifies risks, and produces a research document you can review before any implementation begins.

## Guard Rails: Preventing the Worst Mistakes

Discipline is not just about process. It is also about preventing catastrophic errors in real time.

### Git Safety Guard

The `git-safety-guard` skill intercepts destructive git operations before they execute. `git reset --hard` -- uncommitted work gone. `git push --force` -- team history destroyed. `git branch -D` -- branch deleted without merge check. `git checkout -- .` -- local changes discarded silently.

The guard uses regex pattern matching with an allowlist. `git checkout -b feature` passes through (creating a branch is safe). `git checkout -- src/` gets blocked (discarding changes is not). Safe operations add zero friction. The guard is fail-open: if `terraphim-agent` is unavailable, commands pass through. Development is never blocked by the safety system itself.

### Destructive Command Guard for OpenCode

For OpenCode users, we integrated Jeffrey Emanuel's [Destructive Command Guard (dcg)](https://github.com/Dicklesworthstone/destructive_command_guard) -- a Rust binary with SIMD-accelerated pattern matching and 49+ security packs. We wrote a plugin that wires dcg into OpenCode's `tool.execute.before` hook for sub-millisecond interception of all bash commands. Full architecture and code in the dedicated post: [Guarding OpenCode with Destructive Command Guard](/posts/guarding-opencode-with-dcg/).

Both guards exist because of a real incident. On 17 December 2025, an AI agent ran `git checkout -- .` and destroyed a day of uncommitted work. We built mechanical enforcement the same week. Instructions are suggestions. Guards are guarantees.

---

*Next: *[*The 30% Problem: Why AI Agent Harnesses Ignore Code Intelligence Research*](/posts/the-30-percent-problem/)* examines the research findings that motivated each phase of this framework.*

*Previously: *[*Teaching AI Agents with Knowledge Graph Hooks*](/posts/teaching-ai-agents-with-knowledge-graphs/)* and *[*Teaching AI Agents to Learn from Their Mistakes*](/posts/teaching-ai-agents-to-learn-from-mistakes/)*.*

*Source: *[*terraphim/terraphim-skills on GitHub*](https://github.com/terraphim/terraphim-skills)
