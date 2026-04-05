+++
title = "MCP Server Integration"
description = "Native Model Context Protocol server connecting AI assistants to local knowledge graphs"
date = 2026-04-05
weight = 3

[taxonomies]
categories = ["Capabilities"]
tags = ["mcp", "ai-assistant", "claude", "context-engineering"]

[extra]
toc = true
waypoint = "WP-003"
icon = "fa-solid fa-plug"
+++

## Connect Your AI Assistant to Local Knowledge

Terraphim includes a native **Model Context Protocol (MCP) server** that exposes your local knowledge graphs to AI coding assistants like Claude Code, Claude Desktop, and other MCP-compatible tools. Your AI assistant gains domain-specific context without your data leaving your machine.

## Available MCP Tools

### Paragraph Extraction

Extract paragraphs from text starting at matched terms, with precise line numbers. Useful for referencing function definitions, getting context around specific patterns, or building documentation with accurate line references.

### Knowledge Graph Search

Semantic search that returns full document context with file paths. Unlike plain text search, this leverages your role-based knowledge graph to find documents by their conceptual relationship to your query, not just keyword overlap.

### Token Tracking

Monitor token usage across your AI assistant sessions. Track how much context is being consumed and optimise your prompts based on actual usage data.

## Role-Based Context Enrichment

Different roles need different context. A systems engineer asking about "requirements" needs different search results from a quality analyst asking the same word. Terraphim's MCP server routes queries through the active role's knowledge graph, ensuring your AI assistant receives context that matches your current domain.

## How It Differs from Cloud Solutions

Typical AI assistant integrations send your files and context to cloud APIs. Terraphim's MCP server runs locally:

- **No data upload** -- your files, code, and documents stay on your machine
- **No API key** -- no third-party service required for the knowledge graph layer
- **No latency** -- knowledge graph queries resolve in nanoseconds, not network round trips
- **Full control** -- you decide which knowledge graphs are active and what context your AI sees

## Integration with Claude Code

Terraphim works as a Claude Code MCP server, providing knowledge-graph-boosted file search, concept extraction, and role-based context enrichment directly within your development workflow.

## Learn More

- [Terraphim Configuration](/docs/terraphim_config)
- [Knowledge Graph Engine](/capabilities/knowledge-graph/)
- [Hooks System](/capabilities/hooks/)
