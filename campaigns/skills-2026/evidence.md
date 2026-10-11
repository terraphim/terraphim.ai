# Evidence ledger: skills campaign 2026

Review basis: `/Users/alex/projects/terraphim/terraphim-skills` at `fe4dd603451b8912e69598579b299f2fd128c071` on branch `task/71-community-only-installer`, reviewed 2026-09-07. Absolute paths are intentional in this internal ledger. Public copy must use a stable GitHub commit path or an editorial placeholder.

## Claim states

- **proved**: directly supported by reviewed source and an executed check.
- **documented**: the skill instructs an agent to follow the stated workflow; runtime outcomes are not implied.
- **blocked**: the claim or package must not be promoted until its gate passes.

Package validation establishes integrity and structure. It does not establish that a workflow produces its intended runtime outcome.

## Catalogue and release claims

### CAT-001

- **Exact claim:** The source-branch marketplace candidate lists 54 skill packages.
- **Status:** proved
- **Primary source:** `/Users/alex/projects/terraphim/terraphim-skills/.claude-plugin/marketplace.json:11-1198`
- **Verification:**

  ```text
  $ jq -r '.plugins[].name' .claude-plugin/marketplace.json | wc -l | tr -d ' '
  54
  ```

- **Publication gate:** retain the count only while marketplace metadata still contains 54 unique packages at the publication revision.

### CAT-002

- **Exact claim:** Each of those 54 marketplace candidate skills has a `SKILL.md` and a `skill.toml`.
- **Status:** proved
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/*/SKILL.md:1-10`; `/Users/alex/projects/terraphim/terraphim-skills/skills/*/skill.toml:1-24`
- **Verification:** iterating over `jq -r '.plugins[].name' .claude-plugin/marketplace.json` and checking `skills/$skill/SKILL.md` plus `skills/$skill/skill.toml` returned no missing paths and exit 0.
- **Publication gate:** rerun against the publication revision.

### CAT-003

- **Exact claim:** The candidate marketplace metadata version is 1.6.1.
- **Status:** proved
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/.claude-plugin/marketplace.json:7-10`; `/Users/alex/projects/terraphim/terraphim-skills/scripts/skills.sh:79-80`
- **Verification:** `jq -r '.metadata.version' .claude-plugin/marketplace.json` returned `1.6.1`; `rg -n '^echo "Terraphim Engineering Skills v1.6.1"$' scripts/skills.sh` returned the matching version line.
- **Publication gate:** confirm the version has not changed before publication.

### CAT-004

- **Exact claim:** The live marketplace currently reports 47 active skills, not 54.
- **Status:** proved
- **Primary source:** `https://terraphim-skills.md`, fetched 2026-09-07
- **Verification:** `curl -fsSL https://terraphim-skills.md | rg -o '47 production-grade skills|View all 47 skills'` returned both `47 production-grade skills` and `View all 47 skills` with exit 0.
- **Publication gate:** replace this claim only after the live marketplace itself reports the new count.

### CAT-005

- **Exact claim:** The four community packages are source-branch release candidates on open, unmerged stacked pull requests #65, #66, and #72.
- **Status:** proved
- **Primary sources:** Gitea PRs #65, #66, and #72; `/Users/alex/projects/terraphim/terraphim-skills/scripts/skills.sh:10-15`
- **Verification:** `gtr view-pull` returned `state:"open"` and `merged:false` for all three stacked PRs; #72 is based on #66 and contains the four-entry community installer plus the `local-knowledge` and `kg-rlm-ingest` community changes.
- **Publication gate:** all three PRs merged in order, mirrored to a stable public GitHub commit, packages published, and public install routes verified.

### CAT-006

- **Exact claim:** The community change passed 45 Python tests, 73% aggregate branch coverage, six Bun tests, signed-manifest and installer-policy validation, TSM validation for all four community skills, and an isolated install of four skills with zero skipped.
- **Status:** proved
- **Primary source:** `/Users/alex/projects/terraphim/terraphim-skills/docs/validation/validation-report-community-knowledge-skills.md:101-116`
- **Verification:** the report records 45 passing Python tests, 73% aggregate branch coverage, six passing Bun tests, passing trust-chain checks, four passing TSM validations, and `Four installed, zero skipped` in an isolated destination.
- **Publication gate:** rerun the checks at the release commit and keep package, documentation, and runtime claims separate.

### CAT-007

- **Exact claim:** The community shell installer downloads one `SKILL.md` per selected skill; every current community manifest signs only that standalone file, so the four-skill install does not omit a required community package file.
- **Status:** proved
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/scripts/skills.sh:38-75`; `/Users/alex/projects/terraphim/terraphim-skills/docs/validation/validation-report-community-knowledge-skills.md:23-35`
- **Verification:** signed-manifest validation and an isolated install confirmed that all four current community packages contain the required standalone `SKILL.md` and no omitted companion file.
- **Publication gate:** keep the shell route community-only; extend it to manifest-declared files before admitting any future multi-file community package.

### CAT-008

- **Exact claim:** A valid digest can prove that downloaded bytes match reviewed bytes. It cannot prove that those bytes redact secrets, activate on every claimed host, or store data where the guide says.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/docs/signed-skill-manifests.md:3-15`; CAT-006; LRN-001; LRN-002
- **Verification:** trust-chain documentation and blocker review.
- **Publication gate:** keep integrity and runtime wording separate.

### CAT-009

- **Exact claim:** The adapter validator can show that expected files and contract text are present. It does not prove fail-closed execution, safe interpolation, or independent remote verification.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/scripts/validate-command-adapters.py:280-368`; GIT-001 to GIT-003
- **Verification:** validator returned 23/23; workflow source review found runtime enforcement gaps.
- **Publication gate:** add executable adapter tests before making runtime conformance claims.

### CAT-010

- **Exact claim:** `learning-capture` and `gitea-issue-to-pr` remain blocked in this campaign. Their spotlight drafts explain the findings and the checks required before either can be recommended.
- **Status:** blocked
- **Primary sources:** LRN-001; LRN-002; GIT-001 to GIT-004
- **Verification:** source and threat review recorded in those entries.
- **Publication gate:** close every referenced blocker.

### CAT-011

- **Exact claim:** `scripts/skills.sh` exposes exactly four free community skills: `kg-rlm-ingest`, `local-knowledge`, `terraphim-grep`, and `terraphim-learning-memory`; core and premium packages remain in the 54-entry marketplace catalogue and are not exposed through that installer.
- **Status:** proved
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/scripts/skills.sh:10-15`; `/Users/alex/projects/terraphim/terraphim-skills/README.md:8-34`; `/Users/alex/projects/terraphim/terraphim-skills/scripts/validate-optional-augmentation.py`
- **Verification:** `bash scripts/skills.sh --list` returned the four names; the validator derived expected membership from signed manifests with `tier = "community"` and rejected missing, additional, or duplicate entries.
- **Publication gate:** merge PR #72 and verify the public installer returns the same four names.

## Community and blocked spotlight claims

### MEM-001

- **Exact claim:** The installed `terraphim-agent` 1.21.13 has no `memory` namespace.
- **Status:** proved
- **Primary source:** installed CLI help on 2026-09-07
- **Verification:** `terraphim-agent --version; terraphim-agent memory --help` returned `terraphim-agent 1.21.13`, `error: unrecognized subcommand 'memory'`, and exit 2.
- **Publication gate:** retain this limitation until a released binary's help exposes and runtime checks exercise the namespace.

### MEM-002

- **Exact claim:** `terraphim-learning-memory` is orchestration guidance that starts with capability discovery and routes writes to owning Terraphim components; it is not evidence of a shipped memory runtime.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:31-62`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:64-80`
- **Verification:** source review; MEM-001 confirms the installed CLI limitation.
- **Publication gate:** present it as guidance until the package is published and any runtime namespace is separately released and exercised.

### MEM-003

- **Exact claim:** The learning-memory guidance assigns builds and tests to implementation or verification, and makes deterministic KG extraction the default with RLM optional only for long, genuinely novel material.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:174-180`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:227-231`
- **Verification:** source review.
- **Publication gate:** preserve these boundaries through review and release.

### MEM-004

- **Exact claim:** The practical boundary is capability discovery. An agent checks installed help before selecting a command, then uses the component that owns the information: failed-command learning, session history, local role knowledge, or a project knowledge graph. A successful route message is not treated as proof that content was stored.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:31-62`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:64-80`
- **Verification:** source review.
- **Publication gate:** keep command selection conditional on installed help.

### MEM-005

- **Exact claim:** That means a normal “remember this” request should not trigger a broad build or recursive decomposition. Build results can become evidence, but the memory guide does not own compilation. Likewise, deterministic extraction remains the normal route for knowledge-graph material; RLM is a bounded fallback rather than the default.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:174-180`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:227-231`
- **Verification:** source review.
- **Publication gate:** preserve deterministic-first and build-ownership wording.

### MEM-006

- **Exact claim:** Publication can call this a released skill only after PRs #65, #66, and #72 merge, the package is published, and its live catalogue and install route are checked.
- **Status:** blocked
- **Primary source:** CAT-005
- **Verification:** current PR and live catalogue checks under CAT-004 and CAT-005.
- **Publication gate:** the claim itself states the gate.

### MEM-007

- **Exact claim:** Claims about a `memory` runtime need separate evidence from a released binary whose help exposes that namespace, followed by exercised capture, read-back, correction, retirement, and failure behaviour. Until then, the accurate description is narrower: this candidate teaches capability-aware memory orchestration across existing Terraphim components.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:31-62`; installed CLI result under MEM-001
- **Verification:** source review and `terraphim-agent memory --help` exit 2.
- **Publication gate:** runtime namespace release plus the listed behavioural checks.

### MEM-008

- **Exact claim:** This makes the guide an orchestration layer over capabilities that may differ between installations. It also keeps temporary task progress out of long-lived knowledge unless there is a durable, sourced fact to preserve.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:31-80`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:109-123`
- **Verification:** source review.
- **Publication gate:** no additional gate beyond MEM-006.

### MEM-009

- **Exact claim:** Session history is built into this community workflow. The released CLI exposes `sources`, `list`, `search`, and `stats`; live validation found matching prior work while also surfacing parser warnings that callers must not hide.
- **Status:** proved
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:83-133`; `/Users/alex/projects/terraphim/terraphim-skills/docs/validation/validation-report-community-knowledge-skills.md:37-49`
- **Verification:** `terraphim-agent sessions --help` exposed the four subcommands and `terraphim-agent sessions search "local-knowledge kg-rlm-ingest community skill validation" --limit 10` returned matching sessions with parser warnings for unsupported records.
- **Publication gate:** retain the installed version and warning boundary; do not invent `sessions import`, `sessions show`, or export commands.

### LKG-001

- **Exact claim:** The community `local-knowledge` guide uses the current direct CLI to discover roles and configured paths, perform structured read-only search, cite results, and inspect response data rather than trusting an empty-search exit status.
- **Status:** proved
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/local-knowledge/SKILL.md:25-132`; `/Users/alex/projects/terraphim/terraphim-skills/docs/validation/validation-report-community-knowledge-skills.md:37-49`
- **Verification:** live checks on `terraphim-agent 1.21.13` returned 16 roles, role-specific KG and haystack configuration, and one structured local result with concept and total-match metadata. A separate empty query returned exit 0 and `success:true`, so the guide checks `.data.results` and `.data.total_matches`.
- **Publication gate:** merge PR #72 and rerun against the release binary and public package.

### KGI-001

- **Exact claim:** The community `kg-rlm-ingest` guide discovers the configured role path, extracts and deduplicates concepts deterministically, requires an authorised safe edit, refreshes the role cache, and accepts success only after retrieval of the intended note; validation stopped before mutating production knowledge.
- **Status:** proved
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/kg-rlm-ingest/SKILL.md:39-197`; `/Users/alex/projects/terraphim/terraphim-skills/docs/validation/validation-report-community-knowledge-skills.md:71-85`
- **Verification:** live CLI checks established role/path discovery, deterministic extraction, structured deduplication search, and role-scoped cache refresh. The write protocol was validated up to the explicit production-authorisation boundary; no production knowledge note was changed.
- **Publication gate:** merge PR #72; every real ingestion still requires authorised path inspection, write, cache refresh, and retrieval.

### GRP-001

- **Exact claim:** The locally installed `terraphim-grep` 1.21.13 independently exercised search-only mode, JSON output, directory path scoping, and rejection of conflicting LLM flags.
- **Status:** proved
- **Primary sources:** installed binary; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-grep/SKILL.md:12-22`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-grep/SKILL.md:81-138`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-grep/SKILL.md:185-203`
- **Verification:**
  - `terraphim-grep --version` returned `terraphim-grep 1.21.13`.
  - `terraphim-grep 'CORE_PATH' --search-only --haystack code --json --paths scripts/ | jq '{chunk_count:(.chunks|length), answer, sufficiency}'` returned `chunk_count: 4`, `answer: null`, `sufficiency: "SearchOnly"`.
  - the same query scoped to `skills/` returned 0 chunks, confirming directory scope changed the result set.
  - `terraphim-grep 'CORE_PATH' --search-only --answer` returned exit 2 and `the argument '--search-only' cannot be used with '--answer'`.
- **Publication gate:** describe this only as exercised binary behaviour, not as proof that the unmerged skill package is released.

### GRP-002

- **Exact claim:** The `terraphim-grep` skill package is not yet merged or published.
- **Status:** blocked
- **Primary source:** CAT-005
- **Verification:** PR #65 returned open and unmerged; live marketplace remains at 47 skills under CAT-004.
- **Publication gate:** merge PR #65, publish the package, and verify its live catalogue page and install route.

### GRP-003

- **Exact claim:** The guide begins with capability detection, recommends narrow identifier searches, and separates local retrieval from optional synthesis. It also tells an agent to preserve path scope when falling back to another search tool.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-grep/SKILL.md:24-66`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-grep/SKILL.md:185-203`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-grep/SKILL.md:242-251`
- **Verification:** source review.
- **Publication gate:** merge and publish under GRP-002.

### GRP-004

- **Exact claim:** The runtime check used installed version 1.21.13. A search-only JSON query scoped to `scripts/` returned four chunks, a null answer, and `SearchOnly` sufficiency. The same query scoped to `skills/` returned no chunks. Combining `--search-only` with `--answer` exited with code 2 and reported that the arguments conflict.
- **Status:** proved
- **Primary source:** installed binary results under GRP-001
- **Verification:** exact commands and results are recorded under GRP-001.
- **Publication gate:** retain the tested version and options in public wording.

### LRN-001

- **Exact claim:** `learning-capture` is blocked because `terraphim-agent` 1.21.13 redacts captured error output but stores the parsed command and full command chain without applying the same redaction; generated and documented hook wrappers also echo the original hook payload after invoking the CLI.
- **Status:** blocked
- **Primary sources:** `terraphim-clients` tag `v1.21.13`, `crates/terraphim_agent/src/learnings/capture.rs:970-1000`; `crates/terraphim_agent/src/learnings/install.rs:51-115`; `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:68-92`
- **Verification:** `git show v1.21.13:crates/terraphim_agent/src/learnings/capture.rs` shows `redact_secrets(error_output)` but passes `actual_command.clone()` and `chain.clone()` into `CapturedLearning` without redaction. `git show v1.21.13:crates/terraphim_agent/src/learnings/install.rs` and the skill's manual wrapper each show a final `echo "$INPUT"`.
- **Publication gate:** redact secrets before persistence, stop re-emitting the original payload, add adversarial secret tests, and obtain an independent security review.

### LRN-002

- **Exact claim:** `learning-capture` must not be recommended for activation because its install-hook activation and storage documentation are not accurate across the claimed hosts.
- **Status:** blocked
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:56-92`; `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:179-192`
- **Verification:** source review against installed `terraphim-agent learn --help` and observed macOS capture location; documentation assumes a single Linux storage path and lists host activation without demonstrated end-to-end results.
- **Publication gate:** test installation, activation, capture, read-back, and storage discovery on every named host, then update the documentation to match.

### LRN-003

- **Exact claim:** The record format contains the failed command and redacted stderr or stdout. In version 1.21.13, command and chain fields bypass the error-output redaction. The documented and generated wrappers read the full hook input, forward it to `terraphim-agent learn hook`, and then echo the original input again.
- **Status:** blocked
- **Primary sources:** `terraphim-clients` tag `v1.21.13`, `crates/terraphim_agent/src/learnings/capture.rs:970-1000`; `crates/terraphim_agent/src/learnings/install.rs:51-115`; `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:68-92`; `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:108-133`
- **Verification:** immutable tag source and skill source review.
- **Publication gate:** LRN-001.

### LRN-004

- **Exact claim:** Commands and tool output can contain tokens, credentials, personal data, internal URLs, or other restricted values. A fail-open hook does not solve persistence or re-emission risk. The release gate therefore requires redaction before storage, removal of original-payload re-emission, adversarial secret fixtures, and an independent security review.
- **Status:** blocked
- **Primary sources:** LRN-001 and LRN-003.
- **Verification:** threat review of the versioned implementation and documented data flow.
- **Publication gate:** the claim states the required controls.

### LRN-005

- **Exact claim:** The current text presents Claude Code, Codex, and OpenCode installation commands and one fixed Linux-style storage path. The publication gate is an end-to-end check on every named host: install, activate, cause a controlled non-secret failure, locate the resulting record, query it, add a correction, and verify read-back. Documentation then needs to match the observed host-specific behaviour.
- **Status:** blocked
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:56-106`; `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:179-192`
- **Verification:** source review; no complete cross-host evidence is present.
- **Publication gate:** the claim states the required test sequence.

### LRN-006

- **Exact claim:** The intended loop is straightforward: retain a failed command with context, add a verified correction, and query that record before repeating similar work. The current package documentation, however, makes the capture boundary too broad for a recommendation.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:94-167`; blocker LRN-001
- **Verification:** source and threat review.
- **Publication gate:** LRN-001 and LRN-002.

### GIT-001

- **Exact claim:** `gitea-issue-to-pr` is blocked because its Grok workflow logs failed tests, traceability, or review but still advances to validation and PR creation, and it does not gate PR creation on the validation verdict.
- **Status:** blocked
- **Primary source:** `/Users/alex/projects/terraphim/terraphim-skills/.grok/workflows/gitea-to-pr.rhai:543-580`
- **Verification:** source review shows the failure branch only calls `log`, then execution enters `phase("Validate")` and `phase("PR")`; the validation `passed` field is never read.
- **Publication gate:** make every required failure stop delivery and cover each failure path with executable workflow tests.

### GIT-002

- **Exact claim:** The Grok workflow trusts remote postconditions reported by its PR agent instead of independently reading Gitea state.
- **Status:** blocked
- **Primary source:** `/Users/alex/projects/terraphim/terraphim-skills/.grok/workflows/gitea-to-pr.rhai:580-639`
- **Verification:** source review shows read-back instructions inside a prompt, followed by direct trust in `pr.output` fields.
- **Publication gate:** perform structured read-backs in the workflow and compare repository, SHA, branch, PR, comment, and merged state before completion.

### GIT-003

- **Exact claim:** The Grok workflow interpolates issue-derived owner, repository, index, title, base, and branch values into shell command text without a strict allow-list or shell-safe encoding.
- **Status:** blocked
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/.grok/workflows/gitea-to-pr.rhai:47-80`; `/Users/alex/projects/terraphim/terraphim-skills/.grok/workflows/gitea-to-pr.rhai:193-219`; `/Users/alex/projects/terraphim/terraphim-skills/.grok/workflows/gitea-to-pr.rhai:591-605`
- **Verification:** source review shows trimming and substring parsing but no character validation before command construction.
- **Publication gate:** validate identifiers, keep titles and bodies out of shell interpolation, and add malicious-input tests.

### GIT-004

- **Exact claim:** The `gitea-issue-to-pr` package includes a host-specific `http://bigbox:3456/v1` proxy configuration.
- **Status:** blocked
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/gitea-issue-to-pr/grok-proxy-models.toml:1-29`; `/Users/alex/projects/terraphim/terraphim-skills/skills/gitea-issue-to-pr/skill.toml:14-19`
- **Verification:** source review found the URL three times and confirmed the file is manifest-declared.
- **Publication gate:** remove host-specific configuration from the package and document user-supplied endpoints without a private hostname.

### GIT-005

- **Exact claim:** The workflow collects booleans for tests, traceability, and review. When one is false, it logs a warning and continues. It then invokes validation, records only the validation summary, and advances to the PR phase without reading validation's `passed` field.
- **Status:** blocked
- **Primary source:** `/Users/alex/projects/terraphim/terraphim-skills/.grok/workflows/gitea-to-pr.rhai:543-580`
- **Verification:** source review.
- **Publication gate:** GIT-001.

### GIT-006

- **Exact claim:** Prompting an agent to re-read a pull request is not equivalent to a structured workflow read-back. The workflow must fetch and compare owner, repository, head SHA, base, state, comment, and merged status before it reports completion.
- **Status:** blocked
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/.grok/workflows/gitea-to-pr.rhai:580-639`; `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:207-224`
- **Verification:** source review.
- **Publication gate:** GIT-002.

### GIT-007

- **Exact claim:** The profile text asks for repository identity checks, issue read-back, scoped branch delivery, pull-request verification, and an explicit stop before merge. The problem is not the intended contract. The problem is that the packaged Grok workflow does not enforce all of those boundaries itself.
- **Status:** blocked
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/gitea-issue-to-pr/SKILL.md:34-85`; GIT-001 to GIT-004
- **Verification:** profile and adapter source review.
- **Publication gate:** all four adapter blockers.

### GIT-008

- **Exact claim:** The release gate is fail-closed behaviour: every required negative or missing verdict must stop commit, push, comment, and PR creation. Executable tests must cover each failure path.
- **Status:** blocked
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:159-176`; `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:195-224`
- **Verification:** required remediation derived from GIT-001.
- **Publication gate:** executable workflow tests pass for every listed path.

### CORE-001

- **Exact claim:** `issue-to-pr-core` passes as a written tracker-neutral contract; this does not prove that every adapter conforms at runtime.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:17-45`; `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:159-176`; `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:249-259`
- **Verification:** `python3 scripts/validate-command-adapters.py` returned 23/23, which is a static contract and package check.
- **Publication gate:** describe it only as a contract until each adapter has independent failure-path and postcondition tests.

### CORE-002

- **Exact claim:** Tracker profiles are expected to supply issue identity, forge operations, and read-backs. The core remains the written location for mode selection, acceptance evidence, review convergence, and optional delivery operations.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:17-45`; `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:249-259`
- **Verification:** source review.
- **Publication gate:** CORE-001.

### CORE-003

- **Exact claim:** This is a contract description. It is not a statement that a Linear, Gitea, Grok, Claude, or OpenCode adapter executes every clause correctly.
- **Status:** documented
- **Primary source:** CORE-001
- **Verification:** static validation only; no all-adapter runtime evidence reviewed.
- **Publication gate:** adapter-specific conformance evidence.

### CORE-004

- **Exact claim:** These questions come from the written preflight, acceptance-evidence, delivery, and tracker-profile sections. Passing the static adapter validator confirms the expected contract text and package relationships are present; it does not answer the runtime questions.
- **Status:** documented
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:61-80`; `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:159-176`; `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:207-224`; `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:249-259`
- **Verification:** adapter validator returned 23/23; runtime conformance was not exercised.
- **Publication gate:** CORE-001.

### CORE-005

- **Exact claim:** The current Gitea spotlight demonstrates the separation. Its profile delegates to the core, while its Grok workflow has independent blockers around failed gates, remote postconditions, shell values, and host-specific configuration. A claim that “the adapter follows the core” would therefore be broader than the evidence.
- **Status:** blocked
- **Primary sources:** GIT-001 to GIT-004; `/Users/alex/projects/terraphim/terraphim-skills/skills/gitea-issue-to-pr/SKILL.md:13-16`
- **Verification:** source review.
- **Publication gate:** GIT-001 to GIT-004.

### CORE-006

- **Exact claim:** The accurate publication language stays narrow: the core is a reviewed, signed written contract, and adapter conformance requires separate failure-path and postcondition tests.
- **Status:** documented
- **Primary sources:** CORE-001; CAT-006
- **Verification:** static validators passed; no all-adapter runtime evidence reviewed.
- **Publication gate:** preserve the limitation or add adapter-specific runtime evidence.

## Site and platform evidence

### SITE-001

- **Exact claim:** All six Zola post drafts parse and render when draft content is included.
- **Status:** proved
- **Primary sources:** `/Users/alex/projects/terraphim/terraphim.ai/content/posts/terraphim-skills-54-agent-workflows.md`; the five `skill-spotlight-*.md` files listed in `campaign.md`
- **Verification:** `zola check --drafts --skip-external-links` returned `50 pages (2 orphan), 4 sections` and exit 0. `zola build --drafts` returned `Creating 50 pages (2 orphan) and 4 sections` and exit 0. The two orphan warnings predate this campaign.
- **Publication gate:** repeat without `--drafts` only after all content and release gates pass.

### PUB-001

- **Exact claim:** Reddit prohibits repeated or unsolicited mass engagement and identifies mass-posting repetitive promotional content as potential spam.
- **Status:** proved
- **Primary source:** `https://support.reddithelp.com/hc/en-us/articles/360043504051-Spam`, updated 2026-05-19 and fetched 2026-09-07
- **Verification:** the policy text contains both statements and directs posters to check community-specific rules.
- **Publication gate:** a human must recheck each target community's current rules immediately before posting and must not post near-duplicate submissions.

### PUB-002

- **Exact claim:** Hacker News excludes blog posts, lists, and other reading material from Show HN, asks submitters to retain the original title except for stated corrections, and prohibits generated or AI-edited comments.
- **Status:** proved
- **Primary sources:** `https://news.ycombinator.com/showhn.html`; `https://news.ycombinator.com/newsguidelines.html`, fetched 2026-09-07
- **Verification:** Show HN guidance says those materials are off-topic and should be regular submissions. Submission guidance asks for the original title unless it is misleading or linkbait, with limited stated edits. Comment guidance says, “Don't post generated text or AI-edited text.”
- **Publication gate:** submit the catalogue article as a regular story, not Show HN. Every comment and reply must be written personally.

### PUB-003

- **Exact claim:** Lobsters limits self-promotion, restricts new accounts from `show` and `vibecoding`, and treats promotional content or content without meaningful human authorship as potential spam.
- **Status:** proved
- **Primary sources:** `https://lobste.rs/about`; `https://lobste.rs/tags`, fetched 2026-09-07
- **Verification:** the About page states the less-than-one-quarter self-promotion rule, the 70-day new-user restrictions, and the spam flag criteria. The tag catalogue defines `show` for projects and `vibecoding` for using AI/LLM coding tools.
- **Publication gate:** an established eligible account holder must substantially review and adopt the article and submission as their own work before deciding whether to submit.

## Catalogue description ledger

Each sentence below is an instruction summary, not an outcome guarantee. Sources are the named skill's frontmatter in the reviewed source branch. Recheck wording whenever frontmatter changes.

| ID | Exact claim | Status | Primary source and line range |
|---|---|---|---|
| SKL-001 | `acceptance-testing` instructs an agent to turn requirements into acceptance criteria, test cases, test data, and a sign-off checklist. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/acceptance-testing/SKILL.md:1-10` |
| SKL-002 | `adf-orchestrate` instructs an agent to dispatch, monitor, or cancel approved asynchronous ADF work on a user-controlled server. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/adf-orchestrate/SKILL.md:1-10` |
| SKL-003 | `ai-config-management` instructs an agent to specify configuration control, semantic governance, drift detection, traceability, and change control for AI artefacts. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/ai-config-management/SKILL.md:1-10` |
| SKL-004 | `architecture` instructs an agent to design Rust and WebAssembly architecture, APIs, modules, and decision records without implementing code. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/architecture/SKILL.md:1-10` |
| SKL-005 | `code-review` instructs an agent to review Rust and WebAssembly code for correctness, security, performance, and maintainability findings. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/code-review/SKILL.md:1-10` |
| SKL-006 | `community-engagement` instructs an agent to support contributors, discussions, release notes, and open-source community practice. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/community-engagement/SKILL.md:1-10` |
| SKL-007 | `debugging` instructs an agent to reproduce and diagnose Rust failures, use logging or profiling, and remove temporary debug changes. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/debugging/SKILL.md:1-10` |
| SKL-008 | `deep-research` instructs an agent to route bounded or open research across file-only and externally enhanced modes, then reconcile evidence. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/deep-research/SKILL.md:1-10` |
| SKL-009 | `deterministic-rlm-review` instructs an agent to run capability-routed review perspectives and reconcile severity-ranked findings. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/deterministic-rlm-review/SKILL.md:1-10` |
| SKL-010 | `devops` instructs an agent to work on Rust CI/CD, containers, deployment automation, and infrastructure as code. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/devops/SKILL.md:1-10` |
| SKL-011 | `disciplined-design` instructs an agent to turn approved research into a file-level implementation plan with signatures, tests, and sequencing. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/disciplined-design/SKILL.md:1-10` |
| SKL-012 | `disciplined-implementation` instructs an agent to execute an approved plan step by step with tests and reviewable changes. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/disciplined-implementation/SKILL.md:1-10` |
| SKL-013 | `disciplined-quality-evaluation` instructs an agent to assess research or design documents with the six-dimension KLS framework before phase transitions. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/disciplined-quality-evaluation/SKILL.md:1-10` |
| SKL-014 | `disciplined-research` instructs an agent to map the existing system, constraints, risks, and exclusions before design. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/disciplined-research/SKILL.md:1-10` |
| SKL-015 | `disciplined-specification` instructs an agent to refine implementation details, edge cases, and trade-offs through a structured interview. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/disciplined-specification/SKILL.md:1-10` |
| SKL-016 | `disciplined-validation` instructs an agent to validate a system against original requirements and gather structured acceptance evidence. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/disciplined-validation/SKILL.md:1-10` |
| SKL-017 | `disciplined-verification` instructs an agent to verify implementation against design with tests, coverage evidence, and traceability. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/disciplined-verification/SKILL.md:1-10` |
| SKL-018 | `documentation` instructs an agent to write Rust API, README, architecture, and contributor documentation in the project's style. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/documentation/SKILL.md:1-10` |
| SKL-019 | `gitea-issue-to-pr` instructs an agent to apply a Gitea tracker profile to the shared issue-to-PR contract. | blocked | `/Users/alex/projects/terraphim/terraphim-skills/skills/gitea-issue-to-pr/SKILL.md:1-16`; see GIT-001 to GIT-004 |
| SKL-020 | `gitea-pagerank-workflow` instructs an agent to prioritise and manage Gitea issues and dependencies with `gtr`. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/gitea-pagerank-workflow/SKILL.md:1-10` |
| SKL-021 | `git-safety-guard` instructs an agent to configure a fail-open pre-tool guard for selected destructive Git and filesystem commands. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/git-safety-guard/SKILL.md:1-10` |
| SKL-022 | `gpui-components` instructs an agent to generate GPUI components using Zed-style rendering, state, completion, and theming patterns. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/gpui-components/SKILL.md:1-10` |
| SKL-023 | `grounded-content-writer` instructs an agent to attach citations to material claims and recheck numbers against their sources. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/grounded-content-writer/SKILL.md:1-10` |
| SKL-024 | `implementation` instructs an agent to implement an approved design with tests, documentation, and lint checks. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/implementation/SKILL.md:1-10` |
| SKL-025 | `issue-to-pr-core` instructs an agent to use a tracker-neutral issue-to-PR contract with risk routing, evidence, review, and explicit delivery gates. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/issue-to-pr-core/SKILL.md:1-21`; see CORE-001 |
| SKL-026 | `judge` instructs an agent to assess outputs with semantic, pragmatic, and syntactic dimensions and record structured verdicts. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/judge/SKILL.md:1-10` |
| SKL-027 | `kg-rlm-ingest` instructs an agent to distil sourced material into role-scoped knowledge-graph notes, using deterministic extraction before optional RLM work and requiring retrieval after every authorised write. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/kg-rlm-ingest/SKILL.md:1-35`; `/Users/alex/projects/terraphim/terraphim-skills/skills/kg-rlm-ingest/SKILL.md:142-160` |
| SKL-028 | `learning-capture` instructs an agent to capture and query failed-command records, but activation is blocked pending safety and accuracy fixes. | blocked | `/Users/alex/projects/terraphim/terraphim-skills/skills/learning-capture/SKILL.md:1-17`; see LRN-001 and LRN-002 |
| SKL-029 | `linear-issue-to-pr` instructs an agent to take a Linear issue through a phased engineering and pull-request workflow. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/linear-issue-to-pr/SKILL.md:1-10` |
| SKL-030 | `linear-ticket-writer` instructs an agent to draft structured Linear tickets with lifecycle, priority, state, and estimate fields. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/linear-ticket-writer/SKILL.md:1-10` |
| SKL-031 | `local-knowledge` instructs an agent to discover configured roles and paths, search local knowledge through structured direct commands, cite results, and remain read-only. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/local-knowledge/SKILL.md:1-23`; `/Users/alex/projects/terraphim/terraphim-skills/skills/local-knowledge/SKILL.md:41-81` |
| SKL-032 | `md-book` instructs an agent to work with the MD-Book documentation generator, including highlighting, live reload, search, and templates. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/md-book/SKILL.md:1-10` |
| SKL-033 | `open-source-contribution` instructs an agent to prepare issues and pull requests that follow a project's contribution conventions. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/open-source-contribution/SKILL.md:1-10` |
| SKL-034 | `quality-gate` instructs an agent to assemble review, security, performance-risk, traceability, acceptance, and relevant visual evidence for a change. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/quality-gate/SKILL.md:1-10` |
| SKL-035 | `quickwit-log-search` instructs an agent to investigate logs and incidents with Quickwit using one of three index-discovery modes. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/quickwit-log-search/SKILL.md:1-10` |
| SKL-036 | `repeatable-demo-video` instructs an agent to create scripted terminal or browser recordings as repeatable review evidence. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/repeatable-demo-video/SKILL.md:1-10` |
| SKL-037 | `requirements-traceability` instructs an agent to map requirements through design, implementation, tests, and evidence, then flag gaps. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/requirements-traceability/SKILL.md:1-10` |
| SKL-038 | `rust-ci-cd` instructs an agent to configure Rust CI/CD checks, dependency policy, coverage, benchmark, and release workflows. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/rust-ci-cd/SKILL.md:1-10` |
| SKL-039 | `rust-development` instructs an agent to apply idiomatic Rust patterns for async code, errors, traits, safety, and performance. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/rust-development/SKILL.md:1-10` |
| SKL-040 | `rust-fleet-standard` instructs an agent to apply the repository's shared Rust build, validation, issue-flow, and knowledge-stack conventions. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/rust-fleet-standard/SKILL.md:1-10` |
| SKL-041 | `rust-observability` instructs an agent to configure tracing, OpenTelemetry, Prometheus metrics, request context, and environment-specific logging for Rust services. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/rust-observability/SKILL.md:1-10` |
| SKL-042 | `rust-performance` instructs an agent to profile and optimise Rust code with benchmarks, memory analysis, SIMD, and zero-copy techniques. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/rust-performance/SKILL.md:1-10` |
| SKL-043 | `security-audit` instructs an agent to review Rust and WebAssembly input handling, unsafe code, defaults, and relevant OWASP risks. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/security-audit/SKILL.md:1-10` |
| SKL-044 | `session-search` instructs an agent to search imported coding-assistant session history for previous conversations and decisions. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/session-search/SKILL.md:1-10` |
| SKL-045 | `structural-pr-review` instructs an agent to produce a severity-ranked pull-request review with file overviews, confidence, and an architecture diagram. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/structural-pr-review/SKILL.md:1-10` |
| SKL-046 | `technical-book-writer` instructs an agent to structure a long technical explanation with progressive concepts, diagrams, and chapter files. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/technical-book-writer/SKILL.md:1-10` |
| SKL-047 | `terraphim-grep` instructs an agent to use local search first, scope paths, request JSON when needed, and make LLM synthesis explicit. | blocked | `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-grep/SKILL.md:1-22`; see GRP-001 and GRP-002 |
| SKL-048 | `terraphim-hooks` instructs an agent to configure knowledge-graph-based text replacement for supported command and commit hooks. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-hooks/SKILL.md:1-10` |
| SKL-049 | `terraphim-learning-memory` instructs an agent to retrieve, assess, verify, capture, and revisit durable evidence, with source session search built into the workflow. | blocked | `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:1-29`; `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-learning-memory/SKILL.md:83-133`; see MEM-001 to MEM-003 and CAT-005 |
| SKL-050 | `terraphim-linear` instructs an agent to fetch and inspect Linear issues through semantic aliases or structured output. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-linear/SKILL.md:1-10` |
| SKL-051 | `terraphim-rlm` instructs an agent to route multi-step, multi-file work through budgeted recursive decomposition and reconciliation tools. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/terraphim-rlm/SKILL.md:1-10` |
| SKL-052 | `testing` instructs an agent to write and run unit, integration, property-based, and benchmark tests and analyse failures. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/testing/SKILL.md:1-10` |
| SKL-053 | `ubs-scanner` instructs an agent to run Ultimate Bug Scanner and incorporate its findings into a quality-gate workflow. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/ubs-scanner/SKILL.md:1-10` |
| SKL-054 | `visual-testing` instructs an agent to define screenshot coverage, rendering stabilisation, baseline management, and CI checks for UI changes. | documented | `/Users/alex/projects/terraphim/terraphim-skills/skills/visual-testing/SKILL.md:1-10` |

## Shared publication gate

Before any announcement leaves draft:

1. Rerun CAT-001, CAT-002, CAT-006, CAT-007, CAT-011, and all relevant runtime checks at the exact release commit.
2. Keep `scripts/skills.sh` community-only and verify that every admitted community package remains complete through that route.
3. Confirm live catalogue count and each promoted package page through the public service.
4. Merge and publish all three stacked community pull requests before describing the four skills as released.
5. Keep `learning-capture` and `gitea-issue-to-pr` out of recommendation copy until every blocker closes.
6. Run a human editorial review for claim wording, source links, platform rules, and affiliation disclosure.
