+++
title = "Terraphim Editor"
description = "Intelligent editing with alternative suggestions powered by knowledge graphs and roles."
date = 2026-10-11
weight = 10

[taxonomies]
categories = ["Capabilities"]
tags = ["editor", "knowledge-graph", "role-based", "wasm"]

[extra]
toc = true
waypoint = "WP-010"
icon = "fa-solid fa-pen-to-square"
+++

## Intelligent editing with your knowledge graph

Terraphim Editor brings knowledge-graph alternative suggestions into your writing. Use role-specific concepts and synonyms to compare wording in context, choose an alternative, and keep other options attached to the text. Roles provide the vocabulary for your domain; the online preview starts with a bundled local knowledge graph.

[Try the intelligent editor preview](/editor/)

## Keep your decisions and alternatives

Attach alternatives to words, sentences and paragraphs. Save an annotated Markdown document and reopen it with those choices preserved. Newly authored alternatives register as document-scoped synonyms using `synonyms::` syntax; download them through Knowledge graph to use that exact vocabulary in terraphim-grep. Sharing is explicit and does not silently alter your active role.

Ghost passages to retain them outside clean export, set notes aside in Overflow, and inspect possible cuts in the Lab. KG-protected Trim preserves matched concepts and their original spelling, including supported Unicode normalization.

The editor runs as WebAssembly in your browser. Editing with the bundled graph does not require an LLM or sending your document to a provider.

## See actual saved outputs

[Watch the 80-second alternative-to-search story](/how-tos/synonym-search/): create Concern as an alternative to Risk, share the graph and find related decisions, with and without synthesis.

[Earlier captioned browser and extension walkthroughs](/how-tos/knowledge-work-editor/): Chrome, Safari, Firefox and the existing Zed extension, followed by search with the same shared KG, with and without synthesis. Each video identifies its recorded scope; the current browser build includes the later Unicode normalization repair.

This is a preview. Complete acceptance against all 41 source-video requirements remains open, including Safari dragging and some visual/native cases. The existing Zed extension demonstrates its supported capabilities; the separate Zed fork is outside this publication.

## Explore related capabilities

- [Knowledge Graph Engine](/capabilities/knowledge-graph/)
- [KG-Boosted File Search](/capabilities/kg-file-search/)
