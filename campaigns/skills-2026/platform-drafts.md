# Platform announcement drafts

Every section is editorial material only.

## r/TerraphimAI

**DO NOT PUBLISH until the campaign gates pass.**

**Proposed title:** A source-audited catalogue of 54 Terraphim agent workflow guides

**Draft:**

We have prepared a 54-skill release candidate and audited its claims against the source. The candidate list and marketplace metadata contain the same 54 names, but the live marketplace still reports 47 active skills. We will not call the additional entries live until publication and install checks pass.

The first five write-ups cover Terraphim Grep, learning-memory orchestration, learning capture, the Gitea issue-to-PR profile, and its tracker-neutral core. Two are unmerged candidates, two have release-blocking findings, and the core is documented only as a written contract. The accompanying evidence ledger separates package checks from independently exercised runtime behaviour.

Catalogue: <CATALOGUE_URL>

Source and evidence: <REPOSITORY_URL>

If you review it, please challenge a specific claim or reproduction command. We will update the ledger rather than argue from intent.

**Evidence:** CAT-001, CAT-004, CAT-005, CAT-006, MEM-001, GRP-001, LRN-001, GIT-001, CORE-001.

**Gate:** promoted entries are live, links resolve to a public commit, blocked skills are fixed or omitted, and subreddit rules are rechecked immediately before posting.

## r/opensource

**DO NOT PUBLISH until the campaign gates pass. Recheck whether Promotional flair is still required.**

**Proposed title:** We audited the claims in a 54-guide coding-agent workflow catalogue

**Draft:**

Affiliation disclosure: I maintain Terraphim Skills.

We have a 54-entry source-branch candidate for coding-agent workflow guidance. Rather than treating a valid manifest as proof that a workflow works, we built a claim ledger that records source lines, reproduction commands, status, and publication gates.

The audit found useful limits. The live service still reports 47 active skills. The shell installer downloads only `SKILL.md`, so it is a guidance-file installer rather than a complete manifest package installer. Learning capture and one Gitea workflow remain blocked by security, fail-closed, portability, and verification issues. They will not be recommended until those findings are fixed and retested.

Catalogue: <CATALOGUE_URL>

Repository: <REPOSITORY_URL>

Feedback on the evidence format and reproducibility would be useful.

**Evidence:** CAT-001, CAT-004, CAT-006, CAT-007, LRN-001, LRN-002, GIT-001 to GIT-004, PUB-001.

**Gate:** check current flair and self-promotion rules, disclose affiliation, avoid same-day duplicate posts, and publish only after release and blocker gates pass.

## Hacker News

**DO NOT PUBLISH until the campaign gates pass.**

HN submission must be title and link only. The catalogue article is reading material, so submit it as a regular story rather than Show HN:

**Title:** 54 Agent Workflow Guides in the Release Candidate

**URL:** <CATALOGUE_URL>

Do not add generated submission text. Comments and replies must be personally written because Hacker News prohibits generated or AI-edited comments. The person posting must read the linked material, disclose relevant affiliation when appropriate, and answer from direct knowledge.

**Evidence:** PUB-002.

**Gate:** public catalogue reflects the announced release, source links resolve, blocked skills are fixed or excluded, and a human writes every comment or reply.

## Lobsters

**DO NOT PUBLISH until the campaign gates pass.**

**Proposed title:** Terraphim Skills: evidence-traced workflow guides for coding agents

**URL:** <CATALOGUE_URL>

**Tags:** `show`, `vibecoding`

**Optional description, only if the submission form permits it:**

An overview of a workflow-guide catalogue with a public claim ledger. Package integrity, documented guidance, exercised binary behaviour, and live availability are reported separately.

**Evidence:** CAT-006, PUB-003, and the proof protocol in `campaign.md`.

**Account eligibility gate:** confirm the submitting account is eligible to create a story, the project and link satisfy current Lobsters rules, and `show` plus `vibecoding` remain the appropriate tags. Do not seek an invitation or create an account solely to run the campaign.

**Gate:** all shared publication gates pass, an eligible account holder substantially reviews and adopts the article and submission as their own work, and it is not posted as a near-duplicate of another recent Lobsters story.
