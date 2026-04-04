# Handover: terraphim.ai Website Overhaul

**Date:** 2026-04-04
**Branch:** `main` (at `/Users/alex/projects/terraphim/terraphim.ai/`)
**Build status:** `zola build` passes (37ms, 10 pages, 2 sections)

## What Was Done

The website was migrated from the DeepThought theme (old, inside terraphim-ai monorepo) to the WarpDrive theme (new, standalone repo). All content was then updated to reflect the actual state of the project.

### 1. Theme Migration
- Replaced DeepThought theme with WarpDrive theme
- Old DeepThought templates backed up as `*.deepthought-bak`
- Removed `.gitmodules` (was tracking DeepThought submodule)
- Added `wrangler.toml` for Cloudflare Pages deployment
- Added `.env.1password` for Cloudflare credentials via 1Password

### 2. Navigation Menu
**Before:** Home, Posts, Docs, Tags, Categories, Donate
**After:** Home, Releases, Quickstart, Docs, Install, Blog, Donate

### 3. Download Buttons Fixed
- Added `release_version = "1.15.0"` to `config.toml` (separate from dev `version = "1.16.0"`)
- Hero download button links to `releases/tag/v1.15.0`
- Platform detection JS reads `data-version` from the install section, constructs direct GitHub asset URLs
- "All platforms" list has 8 direct download links to specific release assets
- Platform detection confirmed working (macOS ARM64 detected, correct `.tar.gz` URL)

### 4. Install Section Rewrite
Two groups instead of six equal tabs:
- **Install the Application:** Quick Install (curl), Homebrew (`brew tap terraphim/terraphim && brew install terraphim-ai`), Cargo, Windows (WSL + .zip link)
- **Library Bindings:** npm (`@terraphim/autocomplete`), Python (`terraphim-automata`), Browser Extension (developer mode, coming to Chrome Web Store)

### 5. Content Updates
- `content/releases.md` -- v1.15.0, correct asset names, removed broken changelog/migration links
- `content/docs/quickstart.md` -- v1.15.0, fixed Homebrew (was "Coming Soon"), fixed `terraphim_server` binary name
- `content/docs/installation.md` -- correct binary URLs, added Debian/npm/PyPI/browser extension sections
- Deploy section -- desktop links to `terraphim-ai-desktop` repo, added HTTP Server card

### 6. Discourse Integration
- Added `discourse = "terraphim.discourse.group"` to `config.toml` social config
- Added Discourse icon/link to footer social links macro (`macros.html`)
- Added Discourse links in releases.md, quickstart.md, installation.md

## What Needs Doing

### Not Yet Committed
All changes are uncommitted. The diff is large because the entire theme changed. Files to stage:

**Modified (tracked):**
- `config.toml` -- new theme config, nav, release_version, discourse
- `content/_index.md` -- simplified for WarpDrive
- `.gitignore` -- deleted (needs decision: create new one?)
- `.gitmodules` -- deleted (DeepThought submodule removed)
- `netlify.toml` -- deleted (moved to Cloudflare Pages)
- `templates/base.html`, `templates/index.html`, `templates/page.html` -- deleted (replaced by theme)

**New (untracked):**
- `themes/WarpDrive/` -- entire new theme
- `content/releases.md`, `content/docs/quickstart.md`, `content/docs/installation.md` -- new/rewritten
- `content/posts/teaching-ai-agents-with-knowledge-graphs.md` -- blog post
- `wrangler.toml` -- Cloudflare Pages config
- `.env.1password` -- 1Password refs for deploy (DO NOT commit)
- `public/` -- build output (should be .gitignored)

**Backup files to decide on:**
- `templates/base.html.deepthought-bak` etc. -- can be deleted if DeepThought is no longer needed

### Remaining Tasks
1. **Create `.gitignore`** -- at minimum: `public/`, `.DS_Store`, `.env`, `*.deepthought-bak`
2. **Commit and push** -- stage all changes, commit with descriptive message
3. **Cloudflare Pages deployment** -- verify `wrangler.toml` works with `wrangler pages deploy public/`
4. **Verify external docs link** -- `https://docs.terraphim.ai` is in the nav; confirm it resolves
5. **Consider removing DeepThought backups** -- `templates/*.deepthought-bak` and `themes/DeepThought/`
6. **Landing page content review** -- user indicated wanting "solid information"; may want further iteration on hero copy, capabilities descriptions, or adding use-case examples

## Key Files

| File | Purpose |
|------|---------|
| `config.toml` | Site config, nav, version, social links |
| `themes/WarpDrive/templates/index.html` | Homepage (hero, capabilities, comparison, systems, roles, deploy, install) |
| `themes/WarpDrive/templates/base.html` | Base layout (nav, footer, search modal) |
| `themes/WarpDrive/templates/macros.html` | Social links, page meta, tags |
| `themes/WarpDrive/static/js/site.js` | Platform detection, scroll gauge, search, copy buttons |
| `themes/WarpDrive/static/css/warp.css` | Full theme CSS (~2150 lines) |
| `content/releases.md` | Releases page |
| `content/docs/quickstart.md` | Quickstart guide |
| `content/docs/installation.md` | Full installation guide |

## Architecture Notes

- **Static site generator:** Zola (Rust-based, fast, single binary)
- **Theme:** WarpDrive (custom, dark sci-fi aesthetic)
- **Deployment:** Cloudflare Pages via `wrangler.toml`
- **Search:** Elasticlunr.js (built-in Zola search index)
- **Versioning:** `config.extra.version` (dev, shown in nav badge) vs `config.extra.release_version` (stable, used in download URLs)
- **Platform detection:** JS in `site.js` reads `navigator.userAgentData.platform`, maps to GitHub release asset filenames, populates banner with direct download link
