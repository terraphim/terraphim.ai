# Findings: graph-embeddings-for-checklists article

Captured 2026-10-20. All commands run and outputs verified in-session.

## Tool versions

- `terraphim-grep 1.21.22`, `terraphim-agent 1.21.22` at `~/.grok/bin/`
- `gtr` at `~/.local/bin/gtr`, `zola` at `/opt/homebrew/bin/zola`
- Gitea `terraphim/terraphim.ai` reachable; issue #5 created + labelled `status/in-progress`

## Global KG assets (the article's subject matter)

- `~/.config/terraphim/thesaurus.json` — role "Terraphim Engineer", 219 entries.
  Checklist-adjacent terms present: `judge-checklist`, `quality gate`, `quality check`.
- `~/.config/terraphim/kg/` — concepts incl. `hook.md`, `judge-checklist.md`,
  `validation gate.md`, `grounding gate.md`, `gated lifecycle.md`,
  `vector embeddings.md`, `KLS quality framework.md`.
- `hook.md` nterm definition (quotable): "A function the runtime calls at a
  fixed point (before or after a model call or tool use) that can validate,
  refuse, log, transform or capture; the enforcement layer of context
  engineering."
- `judge-checklist.md` — "Required elements in a judge verdict response";
  synonyms: scores, reasoning, improvements, verdict, semantic score,
  pragmatic score, syntactic score, average score, task_id, model, timestamp.
- `~/.config/terraphim/rewrite/` — "Command Rewriter" role KG, 9 rules:
  bun/bunx/bun run/bun install, uv/uv add/uv sync, docker compose, Terraphim AI.
- `~/.config/terraphim/embedded_config.json` — only role is "Personal Assistant".
- Roles in `~/.config/terraphim/roles/`: default, fpf-all, fpf-architect,
  fpf-engmgr, fpf-hce, fpf-researcher, fpf-syseng, rust-engineer, tai-dev.

## Verified pre-LLM demonstration (terraphim-grep, role + concept)

Query "quality gate" over this repo with the Terraphim Engineer thesaurus:

```
terraphim-grep "quality gate" --haystack all --paths . \
  --thesaurus ~/.config/terraphim/thesaurus.json -n 8 -C 1 --json
```

- `search_latency_ms: 53`, `chunks_returned: 8`, `kg_hits: 8`
- Concept expansion returned: accept, accepted, escalate, fail, improve,
  judge-verdicts, needs improvement, pass — synonyms the user never typed.
- Hits found in `.github/workflows/*.yml`, `campaigns/skills-2026/*` — files
  containing none of the literal query words (matched via synonyms `fail`,
  `curl --fail`, etc.). This is the checklist story in miniature: the graph
  enumerates the vocabulary a reviewer would check for.

Counter-example (control): `terraphim-grep "checklist"` same flags →
`kg_hits: 0`, `chunks: 4` plain lexical hits, `sufficiency: SearchOnly`,
`kg confidence 0.00`. Shows the mechanism is honest about when the graph
does not cover a term — useful honesty caveat for the article.

## Verified post-LLM demonstration (terraphim-agent hook = findings checklist)

```
echo '{"tool_name":"Bash","tool_input":{"command":"npm install react"}}' \
  | terraphim-agent hook --hook-type pre-tool-use --json
```

Output (run from `~/.config/terraphim` so the rewrite KG resolves):

```json
{"tool_input":{"command":"npm install react"},"tool_name":"Bash",
 "validations":{"findings":[{"matched_term":"npm install",
 "suggested_replacement":"bun install"}],"has_findings":true}}
```

Key point for the article: in 1.21.22 the hook does NOT silently rewrite —
it returns a machine-readable findings list (matched term → suggested
replacement). That IS a checklist: enumerated, deterministic, auditable.

Hook types available: pre-tool-use, post-tool-use, pre-commit,
prepare-commit-msg; `--with-guard` defaults true for pre-tool-use only.

## Caveats — validated and reported (terraphim-clients)

1. **CONFIRMED BUG → terraphim-clients#401.** `terraphim-agent replace`
   counts matches (`replacements:1, changed:true`) but `result`/stdout is
   byte-identical to `original` — the substitution never lands. Reproduced
   via stdin, arg form, `--role "Terraphim Engineer"`, `--boundary word`;
   `suggest "Claude Code"` confirms the term is in the graph (sim 1.00).
   The `hook` findings path is the working contract.
2. **CONFIRMED BUG → terraphim-clients#402.** `sessions search` works (19
   results for "checklist") but emits **8999 WARN lines**, all
   `missing field 'uuid'` from `terraphim_session_analyzer::parser` on
   unrecognised newer Claude Code JSONL event types (`atis-latch`,
   `cost-state`). One WARN per line hides real warnings.
3. **CONFIRMED → terraphim-clients#403.** `search` on role
   "Terraphim Engineer" returns nothing because fff's file picker requires
   a git root: `~/.config/terraphim/docs/src` exists but is not under git,
   so zero results + one WARN. A content haystack should not need git.
   (Control: `--role "Personal Assistant"` returned real results — the
   search path itself works when the haystack resolves.)

## learn / sessions

- `terraphim-agent learn query "checklist"` returns global learnings
  (exit-1 commands) incl. prior gtr/gh CLI failures — evidence the store works.
- `terraphim-agent sessions search` emits 8999 `uuid` WARNs — filed as
  terraphim-clients#402.
- `terraphim-agent search` returns results for roles whose haystacks
  resolve (Personal Assistant worked); Terraphim Engineer role's haystack
  is a non-git dir — filed as terraphim-clients#403.

## Related published posts to link (internal cross-links)

- /posts/why-graph-embeddings-matter/ — numbers: 1.4M patterns <1ms,
  5-10ns per inference step, 20ms thesaurus rebuild
- /posts/sub-millisecond-context-knowledge-graphs/
- /posts/native-hook-support/ — verified hooks workflow
- /posts/teaching-ai-agents-with-knowledge-graphs/ — npm→bun demo post
- /posts/teaching-ai-agents-to-learn-from-mistakes/ + learning-via-negativa
- /posts/guarding-opencode-with-dcg/ — guard precedent
- /posts/skill-spotlight-terraphim-grep/ + skill-spotlight-learning-capture
- /docs/graph-embeddings/ reference page, /how-tos/command-rewriting-howto/

## Repo conventions for the post

- Location: `content/posts/<slug>.md`; suggested slug
  `graph-embeddings-checklists`
- Frontmatter: TOML `+++`, `title`, `date=2026-10-20`, `[taxonomies]`
  categories/tags, `[extra] toc=true, comments=true` (match existing posts)
- `<!-- more -->` separator after intro paragraph
- British English, no emoji, no em-dashes in prose (de-slopify pass)
- `zola build` must pass; `public/` is gitignored
- Git flow seen in log: `post/<slug>` branches, PRs merged on GitHub
  (origin is github.com:terraphim/terraphim.ai); Gitea tracks the task

## Public-artefact audit (added in second pass)

- `docs/src/kg/` in terraphim-ai is public on BOTH github/main and
  gitea origin/main; `docs/src/kg/checklists/` holds code_review.md and
  security.md (already public, cited in the post).
- The article's 219-entry `~/.config/terraphim/thesaurus.json` is private
  config; `terraphim_server/fixtures/haystack/Engineer_thesaurus.json` in
  terraphim-ai is a different 42-entry fixture (0 common terms).
- Resolution: committed `.terraphim/` to terraphim.ai — `kg/` (9 public-safe
  concept files copied verbatim from the working KG), `rewrite/` (9 hook
  checklist files verbatim), `thesaurus.json` (39 entries, role name
  "Terraphim Engineer"), README with regenerate script.
- Reproduction verified: `.terraphim/thesaurus.json` gives kg_hits 8 and the
  identical 8-concept expansion on "quality gate"; "checklist" control still
  honestly reports kg_hits 0.
- Accuracy fix: real `bun install.md` heading is `# bun add` (was quoted
  as `# bun install`); article corrected to quote the file verbatim.
- terraphim-ai has dual remotes: origin=gitea, github=github. gitea main is
  337 commits ahead of github main (73 the other way) — divergence predates
  this work; flagged, not addressed here.

## Skill mapping (jsm = jeffreys-skills.md + terraphim stack)

jsm: planning, de-slopify, session-search, structural-pr-review (PR phase),
quality-gate (optional final check).
terraphim: terraphim-grep, terraphim-grep-offline, terraphim-hooks,
terraphim-agent-learn, terraphim-agent-memory, local-knowledge,
gitea-pagerank-workflow.
