# Evidence-backed skills campaign

## Objective

Publish a phased, source-linked account of what the 54 marketplace candidate skills instruct agents to do, while leading release announcements with the four free community skills. Do not imply that instruction guarantees an outcome. Keep four evidence classes separate:

1. documented workflow guidance;
2. source-branch release candidate;
3. independently exercised runtime behaviour;
4. currently live marketplace availability.

The live marketplace remains authoritative for availability. The source branch is authoritative only for candidate content.

## Stop conditions

No platform announcement or Zola post leaves draft while any applicable condition remains:

- candidate and live catalogue counts differ without an explicit limitation;
- a promoted skill is unmerged or unavailable through the claimed route;
- installer copy implies that `scripts/skills.sh` exposes core or premium packages, or admits a community package that requires unsigned or omitted companion files;
- package validation is presented as runtime proof;
- a claim lacks a stable evidence ID, reviewed source range, and reproduction result;
- `learning-capture` or `gitea-issue-to-pr` appears as a recommendation before its blockers close;
- source links do not resolve to an immutable public commit;
- a platform's current self-promotion, flair, tag, account, or generated-content rules have not been checked by the human publisher.

## Phase 0: remediate and release

1. After explicit approval, merge stacked PRs #65, #66, and #72 in order, then mirror the release commit to GitHub.
2. Verify the public shell installer exposes exactly the four signed community packages and installs each package completely.
3. Publish the four community packages, verify each live page and install route, and rerun the ledger commands at the release commit.

If phase 0 is incomplete, publication remains paused. Drafts may be reviewed internally.

The premium audit drafts have independent gates. `learning-capture` requires secret redaction, no payload re-emission, accurate storage discovery and host activation, adversarial tests, and security review. `gitea-issue-to-pr` requires fail-closed gates, validation-verdict enforcement, structured remote read-backs, shell-safe values, portable configuration, and executable failure-path tests. These findings do not block the community release when the affected premium packages are omitted from recommendation and installer copy.

## Phase 1: community release

Publish the overview first, then one community spotlight no more frequently than every three days:

1. `terraphim-learning-memory`: present session retrieval as built-in while distinguishing the guide from an unavailable `memory` namespace.
2. `terraphim-grep`: separate the unmerged skill package from locally exercised `terraphim-grep` 1.21.13 behaviour.
3. `local-knowledge`: present the validated direct, structured, read-only retrieval workflow and its privacy boundary.
4. `kg-rlm-ingest`: present deterministic-first extraction and the authorised write plus retrieval boundary; do not imply that production knowledge was mutated during validation.

Do not turn the sequence into near-identical launch posts. Each spotlight must lead with a distinct workflow, limitation, and verification task. The `learning-capture`, `gitea-issue-to-pr`, and `issue-to-pr-core` drafts remain internal premium catalogue audits, not community-installer announcements.

## Phase 2: broader marketplace catalogue

Begin only after phase 1 feedback is incorporated. Build the schedule from marketplace metadata and manifest tiers, excluding the four community packages already covered. Publish one grouped article per week, with individual spotlights only where readers ask for them. Never present a core or premium package as available through `scripts/skills.sh`.

Suggested themes are discovery and planning, verification and review, Rust engineering, advanced knowledge and orchestration, trackers and collaboration, research and communication, and architecture and delivery. Recount the non-community set against `.claude-plugin/marketplace.json` before scheduling.

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
