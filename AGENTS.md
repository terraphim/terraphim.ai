# Agent Notes: terraphim.ai

## What this repo is
A [Zola](https://www.getzola.org/) static site for https://terraphim.ai. No root `Cargo.toml` or `package.json` — the `crates/` directory holds app config, not buildable Rust crates.

## Daily commands
- `zola build` — outputs to `public/` (gitignored). Should complete in ~40ms.
- `zola serve` — local dev server.
- `./scripts/update-release.sh` — fetches the latest GitHub release via `gh` and updates version strings across `config.toml`, content, and theme files. Run before `zola build` when a new release drops.

## Deploy
- Target: Cloudflare Pages.
- Config: `wrangler.toml` (`pages_build_output_dir = "public"`).
- Command: `wrangler pages deploy public/`
- Credentials live in `.env.1password` — **never commit**.

## Version conventions
- `config.toml` has *two* version fields:
  - `extra.version` — dev version (shown in nav badge).
  - `extra.release_version` — stable version (used in download URLs and JS platform detection).
- `scripts/update-release.sh` only mutates `release_version`.

## Theme architecture
- Active theme: `WarpDrive` (defined in `config.toml`).
- Theme files: `themes/WarpDrive/templates/`, `themes/WarpDrive/static/`, `themes/WarpDrive/sass/`.
- Local template overrides go in `templates/` (currently has a few macros and old backups).
- Homepage is `themes/WarpDrive/templates/index.html` (large, ~36 KB); base layout is `base.html`.

## Cleanup to know about
- Old `DeepThought` theme still exists in `themes/DeepThought/`.
- `templates/*.deepthought-bak` are leftover backups and safe to delete.
- `public/` is gitignored but may contain stale build output locally.

## Content structure
- `content/_index.md` — homepage frontmatter.
- `content/capabilities/` — feature pages linked from homepage waypoint cards.
- `content/docs/` — installation, quickstart.
- `content/posts/` — blog posts (no longer in nav, accessible via `/posts/`).
- `content/releases.md` — release notes.

## Editing constraints
- The WarpDrive theme uses an OKLCH colour system. Accent colour is amber (`oklch(0.72 0.16 70)`). CSS variable names still say `--warp-blue` but values are amber.
- Platform detection JS reads `data-version` from the install section and constructs GitHub asset URLs — keep `release_version` in sync with actual GitHub releases.

## Graph-embeddings explainer (`/docs/graph-embeddings-interactive/`)
- The Terraphim side runs the **real `terraphim_rolegraph` crate compiled to WASM** — `static/explainers/graph-embeddings/wasm/` (wasm-pack `web` target). `engine.js` is only a JSON adapter; never reimplement algorithm logic in JS.
- Wrapper crate source: `scripts/explainer/rolegraph-wasm/` (canonical home: `crates/terraphim_rolegraph/wasm/` in terraphim-core). Rebuild: `./scripts/explainer/build-wasm.sh /path/to/terraphim-core`.
- `terraphim_rolegraph`'s Cargo.toml target-gates `tokio = "full"` and automata's `tokio-runtime`/`remote-loading` to non-wasm targets — required for wasm32.
- Conformance: `node scripts/explainer/check.js` diffs the nodejs wasm build (`scripts/explainer/wasm-node/`) against `scripts/explainer/goldens.json` from `scripts/explainer/oracle.py` — regenerate goldens after corpus changes.
- The crate matches `Document::to_string()` = `title + body`; titles that contain thesaurus terms contribute nodes/edges (self-loops are normal).
