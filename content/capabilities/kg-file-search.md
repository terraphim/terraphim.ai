+++
title = "KG-Boosted File Search"
description = "File search augmented with knowledge graph context -- find files by semantic relationship, not just name"
date = 2026-04-05
weight = 6

[taxonomies]
categories = ["Capabilities"]
tags = ["search", "knowledge-graph", "semantic", "role-based"]

[extra]
toc = true
waypoint = "WP-006"
icon = "fa-solid fa-magnifying-glass-chart"
+++

## Beyond Keyword Matching

Traditional file search finds files by name or by text content. Terraphim's KG-boosted file search finds files by their **semantic relationship** to your domain concepts and role-specific vocabulary.

When you search for "requirements validation", Terraphim does not just grep for those words. It traverses your knowledge graph to find documents connected to those concepts through synonyms, co-occurrence edges, and domain relationships. A document titled "acceptance criteria review" surfaces because the knowledge graph knows these concepts are related in a systems engineering context.

## Multi-Source Search

Terraphim searches across multiple sources simultaneously:

- **Local filesystem** -- Markdown files, code, documentation
- **Knowledge repositories** -- Obsidian vaults, Logseq graphs
- **Shared servers** -- Atomic Server for team knowledge
- **Code search** -- GitHub, StackOverflow, and other configured haystacks

Results from all sources are unified, deduplicated, and ranked using a single knowledge graph.

## Intelligent Deduplication

When searching across multiple haystacks, the same document often appears in different sources. Terraphim handles duplicates intelligently, merging results and preserving the highest-ranked version rather than showing the same content multiple times.

## Role-Specific Relevance

The same search query produces different rankings for different roles:

- A **systems engineer** searching "testing" sees verification and validation documents first
- A **project manager** searching "testing" sees schedule and resource allocation documents
- A **quality analyst** searching "testing" sees compliance and audit documents

Each role's knowledge graph contains domain-specific concepts and synonyms that reshape how results are scored and ordered.

## Context Collections

Terraphim organises searchable content into context collections -- curated sets of documents, taxonomies, and vocabulary that define a domain. Collections can be shared across a team or customised per user, providing consistent search relevance without centralised configuration.

## Integration with AI Assistants

Through the MCP server, KG-boosted file search is available directly in your AI coding assistant. When Claude Code searches for files, it uses your knowledge graph to find semantically relevant results, not just filename matches.

## Learn More

- [Knowledge Graph Engine](/capabilities/knowledge-graph/)
- [MCP Server Integration](/capabilities/mcp-server/)
- [Quickstart guide](/docs/quickstart)
