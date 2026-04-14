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

AI coding agents are making us worse engineers, unless you add discipline back. Here is why "vibe coding" is building unmaintainable systems at unprecedented velocity—and what we do instead.

<!-- more -->

## The 30% Problem

In 2024, researchers published a 300+ page survey on code intelligence ([arXiv:2511.18538](https://arxiv.org/abs/2511.18538)). Their core finding was revolutionary: code scales differently than natural language, and scaling laws vary by programming language.

Go benefits from 32k+ context windows. Python plateaus at 16k. Rust's compiler provides unique optimisation signals.

Fast forward to 2026. The hottest AI coding agents—Cursor, Claude Code, Amazon Q Developer, Harness AI—have adopted approximately **30%** of these insights. The other 70%? Ignored. Lost in the gap between research and production.

This isn't academic nitpicking. It's why your AI-generated codebase has 800% more duplication than hand-written code. It's why agents "game" test suites instead of actually understanding your code. It's why we're building unmaintainable systems at unprecedented velocity.

### Language-Specific Scaling Laws

The 2024 research derived scaling laws specifically for programming languages—not just adapting text LLM laws.

| Language | Optimal Context | Scaling Behaviour |
|----------|-----------------|-------------------|
| **Go** | 32k+ tokens | High signal-to-noise, benefits from more context |
| **Python** | ~16k tokens | Diminishing returns after 16k |
| **JavaScript** | Carefully curated | High noise, needs pruning |
| **Rust** | Type-aware | Compiler feedback most valuable |

What harnesses do: Use 128k context for everything. "More is better."

The cost: Wasted tokens, slower inference, confused models drowning in irrelevant context.

### RLVR: Reinforcement Learning with Verified Rewards

The research evaluated RL strategies with different reward signals:

| Reward Signal | Effectiveness | Risk |
|---------------|---------------|------|
| **Test-passing** | High short-term | Gaming behaviour, overfitting |
| **Compiler feedback** | Very high | Language-specific implementation |
| **Type-checking** | High | Requires typed languages |
| **Coverage increase** | Moderate | May incentivise useless tests |

What harnesses do: Use test-passing rewards. Simple, universal, and flawed.

The cost: Agents learn to pass tests without understanding code. They game the metric. Technical debt accumulates.

## The V-Model: Adding Discipline Back

We built a V-model for AI agents to add the discipline that research demands but harnesses ignore:

```
Research ────────────────> Design ───────────────> Specification
     │                        │                        │
     │                        │                        │
     └────────────────────────┴────────────────────────┘
          Validation <────────── Verification <───────── Implementation
```

### Phase 1: Research

Before writing any code, the agent must understand the problem space:
- Search existing knowledge graphs for relevant patterns
- Identify language-specific constraints
- Determine optimal context window for target language
- Find similar implementations in the codebase

### Phase 2: Design

Create a specification before implementation:
- Define interfaces and data structures
- Identify cross-language considerations
- Plan for compiler feedback integration
- Document the "why" not just the "what"

### Phase 3: Implementation

Write code with tests from the start:
- Language-appropriate context management
- Compiler feedback integration points
- Type-safe by default (for typed languages)
- Self-documenting through clear structure

### Phase 4: Verification

Verify against the design, not just tests:
- Type-checking passes
- Linting passes
- Compiler warnings addressed
- Design intent preserved

### Phase 5: Validation

Validate against the original requirements:
- Does it solve the actual problem?
- Are there simpler alternatives?
- What's the maintenance burden?

## terraphim-skills: 32+ Executable Disciplines

We packaged the V-model as executable skills you can add to any AI agent:

```bash
npx skills add terraphim/terraphim-skills
```

This installs skills that enforce:
- **disciplined-research**: Understand before building
- **disciplined-design**: Plan before coding
- **disciplined-implementation**: Build with tests
- **disciplined-verification**: Verify against design
- **disciplined-validation**: Validate against requirements

Each skill is a self-contained prompt that guides the agent through the phase's inputs, outputs, and quality gates.

## Quality Gates: The Judge System

Our judge system (Kimi K2.5) catches what humans miss:
- 90% verdict agreement with human reviewers
- 62.5% NO-GO detection rate on genuinely flawed code
- ~9s average review latency

Automated quality gates, zero manual overhead. Every PR reviewed before it merges.

## Guard Rails in Practice

Example: A git-safety-guard skill that runs before any commit:
1. Checks for secrets in diff
2. Verifies tests pass
3. Confirms no debug code remains
4. Validates commit message format
5. Checks for TODO comments that should be issues

## Real Example: AI Dark Factory

We run 12+ agents overnight with V-model discipline:
- Each agent has assigned research before design
- Implementations are verified before validation
- The judge system reviews all overnight work
- Morning standup: reviewed output, not debugging

This is what "disciplined engineering" looks like in practice—not process overhead, but automated quality gates that catch problems before they compound.

## Conclusion

The gap between code intelligence research and AI agent harnesses is real. But it's not a technology gap—it's a discipline gap. The V-model and 32+ executable skills we built are available today:

```bash
npx skills add terraphim/terraphim-skills
```

Add discipline back. Your future self will thank you.

---

*Deeper dive: The V-model and quality gates we use are detailed in Chapters 3-4 of *Context Engineering with Knowledge Graphs*. Coming soon.*

**Related posts:**
- [Teaching AI Coding Agents with Knowledge Graph Hooks](/posts/teaching-ai-agents-with-knowledge-graphs/)
- [Teaching AI Agents to Learn from Their Mistakes](/posts/teaching-ai-agents-to-learn-from-mistakes/)
