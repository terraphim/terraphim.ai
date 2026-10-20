# Handover: Graph Embeddings for Checklists — publication and promotion

**Date**: 2026-10-20
**UTC Time**: 12:50 UTC
**Change Slug**: graph-embeddings-checklists
**Branch**: `task/5-graph-embeddings-checklists` (merged to `main` via PR #45, merge SHA `6532de6`)
**Tracking**: Gitea `terraphim.ai#5` (article, closed), `terraphim.ai#7` (promotion, closed)
**Upstream issues filed**: `terraphim-clients#401`, `#402`, `#403`; `terraphim.ai#6`

## Progress Summary

- Completed work:
  - Article authored, reviewed (stand-in claude-sonnet structural review, 4/5, no P0/P1), merged and deployed to https://terraphim.ai/posts/graph-embeddings-checklists/ (HTTP 200).
  - All referenced code artefacts made public: `.terraphim/` in this repo (9 KG concepts, 9 rewrite rules, 39-entry thesaurus, README with reproduce commands); `docs/src/kg/checklists/` confirmed public in terraphim-ai.
  - Promotion complete across all in-scope channels; every placement verified by live readback; receipts in `publication/graph-embeddings-checklists/published/`; ledger in `campaign.json`.
- Current implementation state:
  - Working tree: `HANDOVER.md` carries a pre-existing uncommitted edit from 2026-04-16 (unrelated to this work; left untouched). `copy/` committed at `2b9a8f8`.
  - No known broken state in this repo.

## Publication Map (verified 2026-10-20, BST)

| Channel | URL | Receipt |
|---|---|---|
| Article | https://terraphim.ai/posts/graph-embeddings-checklists/ | live, 200 |
| X Article | https://x.com/alex_mikhalev/status/2112517998372077811 | `published/x-thread.json` |
| X thread root | https://x.com/alex_mikhalev/status/2112515759293510135 | 6 posts chained; post 6 renders full chain |
| Discourse | https://terraphim.discourse.group/t/graph-embeddings-for-checklists/30 | `published/discourse.json` |
| Discord | AKS `#terraphim` 13:17 | `published/discord.json` |
| GitHub Discussion | https://github.com/orgs/terraphim/discussions/29 | gh API |
| DEV | https://dev.to/alexmikhalev/graph-embeddings-for-checklists-lgc | `published/dev.json`, canonical verified |
| Medium | https://alexmikhalev.medium.com/graph-embeddings-for-checklists-7820299a4af7 | `published/medium.json`, canonical verified |
| Mastodon | https://mastodon.social/@alexmikhalev/117473209576093723 | `published/mastodon.json` |
| Reddit | https://www.reddit.com/r/TerraphimAI/comments/1xaqpct/graph_embeddings_for_checklists/ | `published/reddit.json` |

Boundaries kept: LinkedIn draft-only (copy prepared), YouTube skipped (no asset), r/rust parked, Brand X skipped, no paid promotion.

## Artifact Index

- Plan/evidence: `docs_dev/task_plan.md`, `docs_dev/findings.md`
- Article: `content/posts/graph-embeddings-checklists.md`
- Public graph: `.terraphim/` (kg, rewrite, thesaurus.json, README)
- Campaign: `publication/graph-embeddings-checklists/` (copy/, published/, campaign.json)
- Review: PR #45 comment (claude-sonnet stand-in structural review)
- Deploy: Cloudflare Pages run `39417737786` (39s, success)

## Current State

- Known-good: live article, 9 verified placements, canonical links on DEV/Medium point to terraphim.ai.
- Partially working: `terraphim-agent replace` reports `changed:true` without substituting (terraphim-clients#401, article works around via hook findings); sessions search WARN spam (#402); non-git haystack silence (#403).
- Risky or broken: local environment notes — brew terraphim-agent/grep are 1.21.18 but shadowed by `~/.grok/bin` 1.21.22 release artefacts (verified byte-identical); SSH git pushes intermittently hang (HTTPS push works); Zola 0.23.6 breaks WarpDrive build while CI pins 0.22.1 (terraphim.ai#6).

## Resume Procedure

1. `git log --oneline -3` — expect `2b9a8f8` at tip of task branch; `main` has merge `6532de6`.
2. `curl -sI https://terraphim.ai/posts/graph-embeddings-checklists/ | head -1` — expect 200.
3. `cat publication/graph-embeddings-checklists/campaign.json` — full channel ledger.
4. To reproduce the article's demo: `terraphim-grep "quality gate" --haystack all --paths . --thesaurus .terraphim/thesaurus.json -n 8 -C 1 --json` — expect 8 concepts.

## Next Steps

1. Optional: publish LinkedIn (draft ready in `copy/gec-channels.json`) — requires explicit authorisation per prior boundary.
2. Optional: monitor upstream issues #401–#403 for fixes; update article caveat when `replace` is fixed.
3. Optional: fix terraphim.ai#6 (Zola 0.23.6 compat) if brew CI moves past 0.22.1.
4. Optional: refresh the stale `HANDOVER.md` working-tree edit or revert it.

## Open Questions and Risks

- X browser publication leaves stray `(Needs title)` drafts if title entry fails — check X Articles drafts before concluding a session is clean (two were deleted this campaign).
- Medium import can concatenate URL with placeholder text in the import field — always read back the field value before clicking Import.
- Postiz remains running with zero configured social providers; all social posting went through Kimi WebBridge authenticated browser sessions.

## Notes for the Next Session

- Kimi WebBridge daemon on `http://127.0.0.1:10086` drives the real logged-in browser (X `@alex_mikhalev`, Medium, DEV `alexmikhalev`, mastodon.social `alexmikhalev`, Reddit, Discord, Discourse all authenticated).
- For React/DraftJS/ProseMirror editors (X, Medium import, Reddit, Mastodon): `evaluate` fill is discarded on re-render — use focus + CDP `Input.insertText` (trusted input path). Reddit title lives in `POST-COMPOSER-TITLE` shadow root; use the native setter + input events.
- X reply composer: the resolved reply button targets the wrong focal article under load; scope the selector to the focal tweet's article element, then verify the saved parent ID on each post before chaining the next.
- Gitea `gtr` works when `~/.config/terraphim/gitea.env` is sourced; gh API works for GitHub Discussions via the repository discussion categories query (not `Organization.discussionCategories`).
