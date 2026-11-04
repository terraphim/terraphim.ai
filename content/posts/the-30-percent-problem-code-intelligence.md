+++
title="The 30% Problem: What Code Intelligence Research Tells Agent Builders"
date=2026-11-04

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "ai", "engineering", "coding-agents", "code-intelligence", "research"]

[extra]
toc = true
comments = true
+++

A 300-page survey of code intelligence is full of findings that most agent harnesses do not act on. Our rough estimate is that they use about 30% of it. That number is a judgement, not a measurement, but the gap behind it is real, and some of the popular shortcuts built on this research do not survive a reading of the paper.

<!-- more -->

## The source

[From Code Foundation Models to Agents and Applications](https://arxiv.org/abs/2511.18538) (Yang et al., submitted November 2025) surveys the lifecycle of code models: data curation, pre-training, fine-tuning, reinforcement learning and autonomous agents. It also reports its own experiments, and it names the gap between academic benchmarks and real software development as a central problem.

The 30% in our title is our own estimate of how much of this reaches production harnesses. The survey does not state it, nobody has measured it, and you should treat it as shorthand.

## Code does not scale like one thing

Section 8.2 fits Chinchilla-style scaling laws to seven programming languages. The exponents measure how sensitive loss is to model size and to training data. The last column is the fitted lower bound on loss.

| Language | Model size exponent | Data exponent | Irreducible loss |
|----------|---------------------|---------------|------------------|
| Python | 0.221 | 1.217 | 0.566 |
| Java | 0.447 | 1.129 | 0.397 |
| JavaScript | 0.692 | 1.247 | 0.554 |
| TypeScript | 0.439 | 1.303 | 0.518 |
| C# | 0.321 | 1.350 | 0.288 |
| Go | 0.845 | 1.149 | 0.414 |
| Rust | 0.643 | 1.297 | 0.397 |

Two cautions before anyone builds on this table.

**These are pre-training results.** They describe how to spend compute when training a model. They do not give a context window for each language, so a claim such as "Go needs 32k tokens and Python plateaus at 16k" cannot be sourced to them. If you want a context budget per language, measure one on your own tasks.

**Read the numbers, not only the summary.** The surrounding prose says interpreted languages have larger exponents, with Python highest. The fitted values in the table are more mixed: Python has the lowest model size exponent and Go the highest. The irreducible loss ordering does match the prose, from C# at 0.288 to Python at 0.566.

The practical recommendations from that section are about training: allocate tokens by language rather than uniformly, pair syntactically similar languages such as Java with C#, and treat multilingual pre-training as the default.

What an agent builder can fairly take away is narrower and still useful. Languages differ measurably, so a single setting tuned on one language deserves suspicion when it is applied to another.

## More context is not the same as more understanding

The survey is direct about long inputs. Even with expanded windows, general models "do not robustly exploit very long inputs": performance degrades when the relevant information sits in the middle of the context, and repository-level benchmarks "reveal persistent difficulties in cross-file dependency tracking and global reasoning".

That is the finding we think harnesses underuse. A larger window helps only if the right material is in it and the model can use it. Choosing what goes in matters at least as much as how much fits, which is why we spend our effort on [knowledge graph retrieval](/capabilities/knowledge-graph/) rather than on filling the window.

## Verifiable rewards help, within limits

Reinforcement Learning with Verifiable Rewards (RLVR) trains models on deterministic pass or fail feedback from test cases or compilers. The survey credits it with developing structured reasoning, self-verification and error correction.

It also sets a limit. RLVR "primarily sharpens the model's existing capabilities", so high-quality earlier training remains a prerequisite.

This is a training result too, but in our view the lesson carries over to how agents are run. Feedback from a compiler or a type checker does not depend on the agent's opinion of its own work. Tests written by the same agent that wrote the code can pass while missing what was asked, and that is the pattern we keep finding in review.

## What the gap costs

[GitClear's 2025 report](https://www.gitclear.com/ai_assistant_code_quality_2025_research) analysed 211 million changed lines. Lines classified as copied or pasted rose from 8.3% to 12.3% between 2021 and 2024, and the report's headline describes 4x growth in code clones. That is one dataset, and it shows correlation over a period of rapid AI adoption rather than proof of cause. It is still the kind of signal a team should track in its own repositories.

## What we do about it

None of this needs a new model. Our response is a discipline around the models we already have:

- **Verify against something independent.** Compilers, type checkers and requirements written before the code, rather than the agent's own tests alone.
- **Curate context.** Retrieve by concept through a knowledge graph, rather than assume that a larger window will sort itself out.
- **Work at repository level.** Trace each change back to its requirement and its design, because cross-file reasoning is where the research says models still struggle.
- **Measure on your own code.** Treat any published number, including ours, as a hypothesis to test on your own tasks.

The method is set out in [Disciplined Engineering: How We Build AI Systems That Actually Work](/posts/disciplined-engineering-ai-systems/), and the skills that encode it are in the [Terraphim Skills marketplace](https://terraphim-skills.md).

## References

- Yang et al., [From Code Foundation Models to Agents and Applications](https://arxiv.org/abs/2511.18538), arXiv:2511.18538. See section 8.2 and Table 24 for scaling laws, and section 4 for RLVR.
- GitClear, [AI Copilot Code Quality: 2025 Data Suggests 4x Growth in Code Clones](https://www.gitclear.com/ai_assistant_code_quality_2025_research).
