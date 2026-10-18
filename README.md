# Terraphim website

This repository builds [terraphim.ai](https://terraphim.ai), the Terraphim
project website, with [Zola](https://www.getzola.org/). It includes product
guides, release information and the browser editor preview.

## Current downloads

Verified release links as of 18 October 2026. Core services and CLI clients have
separate releases.

| Component | Release | Use |
| --- | --- | --- |
| Core project | [v1.21.3](https://github.com/terraphim/terraphim-ai/releases/tag/v1.21.3) | Stable core/source release |
| CLI clients | [v1.21.22](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.22) | Stable `terraphim-grep`, agent and client tools |
| Terraphim Editor | [v0.1.0-rc.4](https://github.com/terraphim/terraphim-editor/releases/tag/v0.1.0-rc.4) | Browser editor prerelease |
| VS Code extension | [0.1.7](https://github.com/terraphim/terraphim-ai/releases/tag/terraphim_vscode-v0.1.7) | Prerelease VSIX for compatible editors |
| Cursor plugin | [v0.2.7](https://github.com/terraphim/terraphim-cursor-plugin/releases/tag/v0.2.7) | Native Cursor plugin; separate from the VSIX catalogue |
| Stock Zed extension | [v0.2.1](https://github.com/terraphim/zed-terraphim/releases/tag/v0.2.1) | GitHub download; official Zed catalogue submission remains pending |
| Continue integration | [0.1.1](https://github.com/terraphim/terraphim-ai/releases/tag/terraphim_continue-v0.1.1) | Continue integration package |

For future stable releases, use [latest core
downloads](https://github.com/terraphim/terraphim-ai/releases/latest) or [latest
CLI client
downloads](https://github.com/terraphim/terraphim-clients/releases/latest). Use
the explicit version links above for prereleases.

### From wording alternatives to search

[Try the browser editor](https://terraphim.ai/editor/): add **Concern** as an
alternative to **Risk**, save the annotated Markdown, then export its knowledge
graph. Authored groups use `synonyms:: Risk, Concern`. Supply the exported graph
explicitly to the released `terraphim-grep` client to retrieve related passages.
Sharing does not silently change the active role; optional synthesis is a
separate operation.

Follow the [saved-output
walkthrough](https://terraphim.ai/how-tos/synonym-search/) for the exact search
commands and example files.

For agent CLI examples, use the [client agent
README](https://github.com/terraphim/terraphim-clients/blob/main/crates/terraphim_agent/README.md)
and [memory capture
guide](https://github.com/terraphim/terraphim-clients/blob/main/docs/memory-capture.md).
The stock Zed extension has its own supported LSP capabilities; it is separate
from the Zed fork.

## Build and preview

Install Zola, then run from this repository:

```sh
zola build
zola serve
```

`zola build` writes the site to `public/`. `zola serve` starts the local
development server. See [AGENTS.md](AGENTS.md) for the site structure and
deployment notes.
