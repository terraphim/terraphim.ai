+++
title="Setting Up a Frontend Developer Role in Terraphim"
date=2026-05-02
[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "walkthrough", "knowledge-graph", "frontend", "Svelte", "TypeScript", "agent"]
[extra]
toc = true
comments = true
+++

This guide documents the step-by-step process for setting up a Frontend Developer role in Terraphim, including knowledge graph validation, MCP server configuration, and integration with OpenCode.

<!-- more -->

## Prerequisites

- Rust toolchain (for building MCP server)
- terraphim-agent installed
- OpenCode or Claude Code as the AI coding agent
- Basic familiarity with Svelte/SvelteKit and TypeScript

## Step 1: Validate the Frontend Knowledge Graph

Before deploying the knowledge graph, validate each concept file to ensure proper structure:

```bash
# Knowledge graph source location
KG_SOURCE="/home/alex/projects/terraphim/terraphim-ai/data/kg/frontend"

# Validate each file has required structure
for f in "$KG_SOURCE"/*.md; do
  echo "=== $(basename "$f") ==="
  head -5 "$f"
  echo
done
```

**Validation criteria**:
- Valid markdown with `# Heading`
- Has `synonyms::` line with 3+ terms
- Description is 2+ sentences

The frontend KG ships with 18 concept files covering:

| Domain | Files |
|--------|-------|
| Svelte/SvelteKit | svelte-patterns.md, component-design.md |
| CSS | css-layout.md, css-custom-properties.md, visual-design.md |
| TypeScript | typescript.md |
| Accessibility | accessibility.md |
| Performance | performance.md |
| Testing | testing-frontend.md |
| State Management | state-management.md |
| Forms | forms-validation.md |
| APIs | api-integration.md |
| Browser APIs | browser-apis.md |
| Build Tools | build-tools.md |
| DX | developer-experience.md |
| Package Management | package-management.md |
| Responsive Design | responsive-design.md |
| Interaction | interaction-patterns.md |

**Total: 316 synonyms across 18 concepts**

## Step 2: Copy Knowledge Graph to User Config

```bash
# Create directory
mkdir -p ~/.config/terraphim/kg/frontend

# Copy validated KG
cp -r /home/alex/projects/terraphim/terraphim-ai/data/kg/frontend/* \
  ~/.config/terraphim/kg/frontend/

# Verify
ls ~/.config/terraphim/kg/frontend/
```

## Step 3: Configure Settings

Add role configuration path to `settings.toml`:

```toml
# ~/.config/terraphim/settings.toml
server_hostname = "127.0.0.1:8000"
api_endpoint = "http://localhost:8000/api"
initialized = "${TERRAPHIM_INITIALIZED:-false}"
default_data_path = "${TERRAPHIM_DATA_PATH:-${HOME}/.terraphim}"
default_role = "AI Engineer"
role_config = "/home/alex/.config/terraphim/embedded_config.json"
```

## Step 4: Configure the Frontend Developer Role

Add the role to `embedded_config.json`:

```json
{
  "roles": {
    "Frontend Developer": {
      "shortname": "fedev",
      "name": "Frontend Developer",
      "relevance_function": "terraphim-graph",
      "terraphim_it": true,
      "theme": "yeti",
      "kg": {
        "automata_path": null,
        "knowledge_graph_local": {
          "input_type": "markdown",
          "path": "/home/alex/.config/terraphim/kg/frontend"
        },
        "public": false,
        "publish": false
      },
      "haystacks": [
        {
          "location": "/home/alex/projects/frontend-test",
          "service": "Ripgrep",
          "read_only": true,
          "fetch_content": false,
          "extra_parameters": {}
        }
      ],
      "llm_enabled": false
    }
  }
}
```

**Key configuration choices**:

| Setting | Value | Rationale |
|---------|-------|-----------|
| `relevance_function` | `terraphim-graph` | Hybrid KG + TF-IDF scoring |
| `terraphim_it` | `true` | Enables text replacement via synonyms |
| `llm_enabled` | `false` | Deterministic search only |
| `haystacks[0]` | Ripgrep | Local project file search |

## Step 5: Build terraphim_mcp_server

For FFF-based file finding (fuzzy path + content search with KG scoring):

```bash
cd ~/projects/terraphim/terraphim-ai
cargo build --release -p terraphim_mcp_server
cp target/release/terraphim_mcp_server ~/.cargo/bin/
```

For GrepApp support (GitHub code search):

```bash
cargo build --release -p terraphim_middleware --features grepapp
cargo build --release -p terraphim_mcp_server
```

## Step 6: Register MCP in OpenCode

Add to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "terraphim": {
      "type": "local",
      "command": ["/home/alex/.cargo/bin/terraphim_mcp_server"],
      "environment": {
        "TERRAPHIM_DATA_PATH": "~/.terraphim"
      }
    }
  }
}
```

## Step 7: Create Fresh Svelte Project

```bash
cd ~/projects
bunx sv create frontend-test --template minimal --types ts --no-install

cd frontend-test
bun install
bun run build
```

## Step 8: Verify Integration

```bash
# Reload config
terraphim-agent config reload

# List roles
terraphim-agent roles list

# Test search
terraphim-agent search --role "Frontend Developer" --limit 5 "aria"
```

**Expected output**:
```
[103] README
    /home/alex/projects/frontend-test/node_modules/aria-query/README.md
    # ARIA Query
...
```

## Understanding Haystack Types

### Ripgrep Haystack

Standard content search using ripgrep:

```json
{
  "location": "/path/to/project",
  "service": "Ripgrep",
  "read_only": true,
  "extra_parameters": {}
}
```

**Pros**: Fast, exhaustive content search, regex support
**Cons**: No concept understanding, no frecency

### FFF (Fuzzy File Finder)

Not a haystack - provides MCP tools for fuzzy file finding and KG-scored content search:

```bash
# MCP tools provided by terraphim_mcp_server:
# - terraphim_find_files: Fuzzy path search with KG boost
# - terraphim_grep: Content search with KG-ordered files
# - terraphim_multi_grep: Multi-pattern Aho-Corasick search
```

**Pros**: Frecency (frequency + recency), KG path scoring
**Cons**: Different interface than haystack search

### GrepApp Haystack

GitHub code search via grep.app API:

```json
{
  "location": "https://grep.app",
  "service": "GrepApp",
  "extra_parameters": { "language": "typescript" }
}
```

**Pros**: Searches millions of public GitHub repos
**Cons**: Requires `--features grepapp` build, rate limits

## Architecture: Flow A vs Flow B

### Flow A: Ripgrep Haystack

```
Query → terraphim search → Ripgrep haystack → KG-boosted ranking
```

### Flow B: FFF Tools

```
Query → terraphim_find_files/grep → FFF (fuzzy + frecency) → KG path scoring
```

## Next Steps

1. **Create navigation component**: Use terraphim search to find accessibility patterns
2. **Iterate with WCAG audit**: Find missing aria-label, fix, re-audit
3. **Add GrepApp**: Build with `--features grepapp` for GitHub code search

## Troubleshooting

### "Role not found"

```bash
terraphim-agent config reload
terraphim-agent roles list
```

### "GrepApp haystack support not enabled"

GrepApp requires building terraphim_middleware with `--features grepapp`:

```bash
cargo build --release -p terraphim_middleware --features grepapp
cargo build --release -p terraphim_mcp_server
```

### Search returns no results

Check haystack location exists:

```bash
ls -la /home/alex/projects/frontend-test
```

## Related Documentation

- [Frontend Developer Agent Walkthrough](https://github.com/terraphim/terraphim-ai/blob/main/docs/walkthroughs/frontend-developer-agent.md)
- [FFF Search Integration](https://github.com/terraphim/terraphim-ai/blob/main/docs/capabilities/fff-search-integration.md)
- [MCP Integration Guide](https://github.com/terraphim/terraphim-ai/blob/main/docs/src/howto/mcp-integration-claude-opencode.md)
