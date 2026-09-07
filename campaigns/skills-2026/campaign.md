# Evidence-backed skills campaign

## Objective

Publish a phased, source-linked account of what the 54 candidate skills instruct agents to do. Do not imply that instruction guarantees an outcome. Keep four evidence classes separate:

1. documented workflow guidance;
2. source-branch release candidate;
3. independently exercised runtime behaviour;
4. currently live marketplace availability.

The live marketplace remains authoritative for availability. The source branch is authoritative only for candidate content.

## Stop conditions

No platform announcement or Zola post leaves draft while any applicable condition remains:

- candidate and live catalogue counts differ without an explicit limitation;
- a promoted skill is unmerged or unavailable through the claimed route;
- installer copy implies complete packages while `scripts/skills.sh` downloads only `SKILL.md`;
- package validation is presented as runtime proof;
- a claim lacks a stable evidence ID, reviewed source range, and reproduction result;
- `learning-capture` or `gitea-issue-to-pr` appears as a recommendation before its blockers close;
- source links do not resolve to an immutable public commit;
- a platform's current self-promotion, flair, tag, account, or generated-content rules have not been checked by the human publisher.

## Phase 0: remediate and release

1. After explicit approval, merge stacked PRs #65 and #66 in order, then mirror the release commit to GitHub.
2. Fix or explicitly constrain the guidance-file installer.
3. Fix `learning-capture`: secret redaction, no payload re-emission, accurate storage discovery, accurate host activation, adversarial tests, and security review.
4. Fix `gitea-issue-to-pr`: fail-closed gates, validation verdict enforcement, structured remote read-backs, shell-safe values, portable configuration, and executable failure-path tests.
5. Publish candidate packages, verify each live page and install route, and rerun the ledger commands at the release commit.

If phase 0 is incomplete, publication remains paused. Drafts may be reviewed internally.

## Phase 1: initial five

Publish the overview first, then one spotlight no more frequently than every three days:

1. `terraphim-learning-memory`: present as capability-aware orchestration guidance, not a shipped memory namespace.
2. `terraphim-grep`: separate the unmerged skill package from locally exercised `terraphim-grep` 1.21.13 behaviour.
3. `learning-capture`: publish only after LRN-001 and LRN-002 close; until then retain the blocked audit draft.
4. `gitea-issue-to-pr`: publish only after GIT-001 through GIT-004 close; until then retain the blocked audit draft.
5. `issue-to-pr-core`: present only as a written tracker-neutral contract unless adapter conformance has separate runtime evidence.

Do not turn the sequence into five near-identical launch posts. Each spotlight must lead with a distinct workflow, limitation, and verification task.

## Phase 2: remaining 49

Begin only after phase 1 feedback is incorporated. Publish one grouped article per week, with individual spotlights only where readers ask for them.

| Week after phase 1 | Theme | Seven skills |
|---|---|---|
| 1 | Discovery and planning | `acceptance-testing`, `disciplined-research`, `disciplined-quality-evaluation`, `disciplined-design`, `disciplined-specification`, `disciplined-implementation`, `disciplined-verification` |
| 2 | Verification and review | `disciplined-validation`, `testing`, `requirements-traceability`, `quality-gate`, `code-review`, `structural-pr-review`, `ubs-scanner` |
| 3 | Rust engineering | `rust-development`, `rust-performance`, `rust-observability`, `rust-ci-cd`, `rust-fleet-standard`, `security-audit`, `debugging` |
| 4 | Knowledge and agent orchestration | `local-knowledge`, `session-search`, `kg-rlm-ingest`, `terraphim-hooks`, `terraphim-rlm`, `deterministic-rlm-review`, `adf-orchestrate` |
| 5 | Trackers and collaboration | `gitea-pagerank-workflow`, `linear-issue-to-pr`, `linear-ticket-writer`, `terraphim-linear`, `open-source-contribution`, `community-engagement`, `git-safety-guard` |
| 6 | Research and communication | `documentation`, `md-book`, `grounded-content-writer`, `technical-book-writer`, `deep-research`, `repeatable-demo-video`, `judge` |
| 7 | Architecture and delivery tools | `ai-config-management`, `architecture`, `devops`, `gpui-components`, `implementation`, `quickwit-log-search`, `visual-testing` |

The seven groups contain all 49 skills not covered in phase 1. Recount against `scripts/skills.sh` before scheduling.

## Proof protocol

For every material sentence:

1. Assign a stable ID before drafting.
2. Copy the exact public wording into `evidence.md`.
3. Record the primary source path and line range at the reviewed revision.
4. Record the exact command, exit status, and meaningful result for executable claims.
5. Mark the claim `proved`, `documented`, or `blocked`.
6. Add `<!-- evidence: ID -->` immediately after the sentence in Zola content.
7. Classify it as guidance, candidate, runtime, or live availability.
8. Re-run executable evidence after any source or release change.
9. Remove or narrow a claim when evidence weakens. Never broaden it to save copy.

Package signatures, manifests, static validators, and installer structure belong to package evidence. Runtime claims require an exercised released binary or workflow. Availability requires a check against the live marketplace, not a branch or PR.

## Editorial rules

- Use British English and plain technical language.
- Use no emoji, prose em dashes, inflated adjectives, or outcome guarantees.
- Do not claim performance, adoption, production use, reliability, security, or effectiveness without dedicated evidence.
- Say what a skill instructs an agent to do.
- Link public copy to immutable GitHub paths. Use an obvious editorial placeholder until the commit is public.
- Keep blocked findings visible. A valid signature does not cancel a security or workflow defect.
- Require a human technical and platform review before changing `draft=true`.

## Platform anti-spam controls

### Reddit

- Use one substantive post per community, not repeated link drops.
- For r/opensource, use Promotional flair, disclose maintainer affiliation, and recheck current self-promotion rules.
- Do not post the same copy to r/TerraphimAI and r/opensource on the same day.
- Answer questions directly and do not manufacture engagement.

### Hacker News

- Submit only the title and link specified in `platform-drafts.md`.
- Use a regular submission for the catalogue article; Show HN excludes blog posts and lists.
- Comments and replies must be personally written. Do not use generated comments.
- Do not repost after a weak reception unless there is a material new release.

### Lobsters

- Confirm account eligibility before submission.
- Use `show` and `vibecoding` only if they still fit current tag guidance.
- Avoid near-duplicate submissions and disclose maintainer context in any permitted description.
- Require the account holder to provide meaningful human authorship, not a cursory approval of generated copy.

## Measurement and pause rule

Track referral visits, catalogue-page visits, documentation corrections, reproduction reports, and substantive questions. Do not infer workflow effectiveness from clicks. Pause the next wave when reviewers find an unsupported claim, a broken reproduction, a package mismatch, or repeated platform complaints. Correct the source, ledger, and every affected draft before resuming.
