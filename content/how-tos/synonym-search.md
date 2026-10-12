+++
title = "Different words. The same idea."
description = "Create a wording alternative, share its knowledge graph, and find related decisions with terraphim-grep."
date = 2026-10-11
[taxonomies]
categories = ["How-tos"]
tags = ["editor", "knowledge-graph", "search"]
[extra]
social_image = "/demos/synonym-search/poster.jpg"
+++

Your project brief says **risk**. Later, you search for **concern**. Terraphim connects the two so a change of wording does not hide the decisions you need.

The inspiration came from [Jason Fried’s original Write_On video](https://x.com/jasonfried/status/2105403067793584590) and its idea of “alternative control”. It prompted Alex Mikhalev to return to Terraphim Editor, a Rust/WebAssembly project he had abandoned two years earlier, with a clear purpose: connect wording alternatives to a reusable knowledge graph and carry that meaning into search.

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
terraphim-grep concern --thesaurus knowledge-graph.json --paths corpus -C 2 --search-only --json
```

The actual result contains three risk passages and their related decisions, with file and line locations. No generated answer is requested.

Replace `--search-only` with `--answer` for synthesis:

```sh
terraphim-grep concern --thesaurus knowledge-graph.json --paths corpus -C 2 --json --answer
```

The video shows the generated summary and its references to the same three passages. Decisions remain decisions: the source does not establish whether they have been carried out. Check the evidence alongside any generated answer.

Editing and local search use your local data. Optional synthesis sends the retrieved passages to your configured model provider.

## Try it with an Obsidian vault

Keep the words that describe a concept in the note that owns it. In this example, **Risk.md** contains the actual `synonyms:: Risk, Concern` property and embeds the community garden brief. The separate brief still says **risk**, never **concern**. The search-results note contains saved passages, with no synonym definition.

<figure><a href="/demos/obsidian-synonym-search/screenshots/03-synonyms-in-knowledge-note.jpg"><img src="/demos/obsidian-synonym-search/screenshots/03-synonyms-in-knowledge-note.jpg" alt="Obsidian with synonyms in the Risk knowledge note on the left and saved terraphim-grep results on the right: zero baseline passages, then three with the exported graph." width="2048" height="1600" loading="lazy" style="width:100%;height:auto"></a><figcaption>Captured in Obsidian 1.14.4. The knowledge note owns the synonyms; Obsidian displays saved CLI results.</figcaption></figure>

[Download the Obsidian demo vault ZIP](/demos/obsidian-synonym-search/obsidian-synonym-search-example.zip). Extract it, open the included `obsidian-demo/vault` folder as an Obsidian vault, and open `Notes/Risk.md`. Open `Search results/Concern search.md` alongside it to inspect the saved output. No community plugins are required.

To reproduce the retrieval, install [terraphim-grep v1.21.19](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.19), open a terminal in the extracted `vault` directory, and run:

```sh
terraphim-grep concern --thesaurus "Knowledge graph/baseline-role.json" --paths "Notes/Projects" -C 2 --json --search-only
terraphim-grep concern --thesaurus "Knowledge graph/knowledge-graph.json" --paths "Notes/Projects" -C 2 --json --search-only
```

The released binary returned **zero passages** with the baseline graph and **three exact risk-and-decision passages** with the exported graph, at lines 7, 10 and 13. The commands search only the project brief directory, excluding the concept definition and saved results. Inspect the [baseline output](/demos/obsidian-synonym-search/evidence/before-sharing.json), [synonym output](/demos/obsidian-synonym-search/evidence/with-synonym.json), [execution receipt](/demos/obsidian-synonym-search/evidence/verification.json) and [file checksums](/demos/obsidian-synonym-search/manifest.json).

Terraphim’s `synonyms::` convention uses Logseq-compatible Markdown property syntax. Obsidian’s native aliases use YAML `aliases`. This example supplies the same graph exported by the editor explicitly: saving a note does not automatically rebuild the graph or synchronise the vault. Search runs in the CLI; Obsidian displays the notes and saved results. The capture reruns local retrieval only; the video above shows the separate synthesis comparison.

## Try it yourself

1. [Download the complete example ZIP](/demos/synonym-search/synonym-search-example.zip). It includes the project brief, synonym graph and a step-by-step README.
2. [Install terraphim-grep](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.19) for macOS or Linux.
3. Extract the ZIP and follow the README to search the brief, first without the synonym relationship and then with it. Add `--answer` when you want a summary alongside the source passages.

Searching for **concern** returns no passages before the graph is shared. With the graph, it finds all three **risk** passages and their related decisions. Compare the saved results [before sharing](/demos/synonym-search/released-before-sharing.json), [with the synonym graph](/demos/synonym-search/released-without-synthesis.json), and [with a generated summary](/demos/synonym-search/released-with-synthesis.json).

Then try the same steps with a pair of words from your own project notes.

## Explore the files

- [Synonym graph](/demos/synonym-search/knowledge-graph.json)
- [Project brief](/demos/synonym-search/project-brief.md) — the sample text searched in the demo
- [Markdown with wording alternatives](/demos/synonym-search/annotated.md) — reopen it in the editor
- [Recorded search results](/demos/synonym-search/without-synthesis.json)
- [Recorded summary and references](/demos/synonym-search/with-synthesis.json)
- [English subtitles (SRT)](/demos/synonym-search/captions.srt)

The video uses a sample project brief and synthetic British English narration. The graph and search results are saved outputs from the demonstrated workflow. [Recording details](/demos/synonym-search/manifest.json) and [versions, commands and file checksums](/demos/synonym-search/reproduction.json) are available with the downloads.

[Explore more editor walkthroughs](/how-tos/knowledge-work-editor/).
