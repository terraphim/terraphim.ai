+++
title = "Different words. The same idea."
description = "Create a wording alternative, share its knowledge graph, and find related decisions with terraphim-grep."
date = 2026-10-11
[taxonomies]
categories = ["How-tos"]
tags = ["editor", "knowledge-graph", "search"]
+++

Your project brief says **risk**. Later, you search for **concern**. Terraphim connects the two so a change of wording does not hide the decisions you need.

<video controls preload="metadata" playsinline poster="/demos/synonym-search/poster.jpg" style="width:100%;max-width:1100px" aria-label="Create an alternative, share its graph, and search with it — 80 seconds"><source src="/demos/synonym-search/synonym-search-story.mp4" type="video/mp4"><track kind="captions" src="/demos/synonym-search/captions.vtt" srclang="en" label="English">[Watch the 80-second story](/demos/synonym-search/synonym-search-story.mp4)</video>

[Try Terraphim Editor](/editor/) · [Read the narration](/demos/synonym-search/transcript.txt)

## Choose the words that fit

In our community garden brief, timber might arrive late. The team has decided to keep a backup supplier. Add **Concern** as an alternative to **Risk**, then swap between them. The other wording stays attached to the document.

## Share what those words mean

Open **Knowledge graph** from the Markdown export menu. The editor shows **Risk ↔ Concern** and its actual definition:

```text
synonyms:: Risk, Concern
```

Download the graph and the clean text. This explicitly shares the document's authored synonym groups as a Terraphim thesaurus; it does not silently change your active role. The saved example contains **Risk**, with no literal occurrence of **Concern**.

## Find the decisions using either word

Use the graph downloaded from that editing session:

```sh
terraphim-grep concern --thesaurus knowledge-graph.json --paths corpus -C 2 --json
```

The actual result contains three risk passages and their related decisions, with file and line locations. No generated answer is requested.

Add `--answer` to the same command for synthesis:

```sh
terraphim-grep concern --thesaurus knowledge-graph.json --paths corpus -C 2 --json --answer
```

The video shows the generated summary and its references to the same three passages. Decisions remain decisions: the source does not establish whether they have been carried out. Check the evidence alongside any generated answer.

Editing and local search use your local data. Optional synthesis sends the retrieved passages to your configured model provider.

## Try the exact files

- [The graph downloaded in the recording](/demos/synonym-search/knowledge-graph.json)
- [The clean project brief](/demos/synonym-search/project-brief.md) — place it in a `corpus` directory
- [Saved Markdown with alternatives](/demos/synonym-search/annotated.md)
- [Actual result without synthesis](/demos/synonym-search/without-synthesis.json)
- [Actual result with synthesis](/demos/synonym-search/with-synthesis.json)

The community garden brief is authored public sample input. The alternatives, downloaded graph, retrieved passages and generated answer are actual outputs. The command-line section displays those JSON fields in a readable presentation; it is not a separate Terraphim interface. The voice is synthetic British English (Emma). Setup is omitted, and the recorded interaction runs at its original speed. [Recording details and file identities](/demos/synonym-search/manifest.json).

This is a preview of the new export and search flow. It uses the [editor graph-sharing candidate](https://git.terraphim.cloud/terraphim/terraphim-editor/pulls/131) and the [grep synonym/synthesis candidate](https://git.terraphim.cloud/terraphim/terraphim-clients/pulls/385); older installed binaries may differ. A fresh synthesis run may produce different wording.

[Earlier browser and Zed host walkthroughs](/how-tos/knowledge-work-editor/) retain their own recorded versions and limitations. This focused story does not qualify all 41 source-video requirements. The Zed fork remains separate.
