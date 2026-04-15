+++
title = "Multi-Haystack Search"
description = "One agent, many haystacks — search local files, Confluence, Jira, Discourse, email, and global code via grepapp"
date = 2026-04-15
weight = 10

[taxonomies]
categories = ["Capability"]
tags = ["haystack", "search", "grepapp", "code-search"]

[extra]
toc = true
+++

Terraphim roles can be configured with multiple haystacks — named sources of content.
A single query fans out across every haystack attached to the role and the results come
back ranked by the role's knowledge graph.

Haystack adapters available today:

- **Local files** — any directory tree, reindexed on change
- **Confluence** — pages in a space
- **Jira** — issues and comments
- **Discourse** — forum threads
- **Email** — IMAP mailboxes
- **grepapp** — global code search across public repositories
- **Atomic Data** — typed resources in an Atomic Server store

See the release post [Introducing Multi-Haystack Roles: Local + Global Code Search](/posts/multi-haystack-roles-grepapp)
for a walkthrough of combining a local haystack with grepapp to search both your code and
the world's code in one query.
