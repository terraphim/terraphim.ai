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

## Try the exact files

- [The graph downloaded in the recording](/demos/synonym-search/knowledge-graph.json)
- [The clean project brief](/demos/synonym-search/project-brief.md) — place it in a `corpus` directory
- [Saved Markdown with alternatives](/demos/synonym-search/annotated.md)
- [Actual result without synthesis](/demos/synonym-search/without-synthesis.json)
- [Actual result with synthesis](/demos/synonym-search/with-synthesis.json)
- [Download the complete example ZIP](/demos/synonym-search/synonym-search-example.zip), including a step-by-step README
- [English subtitles (SRT)](/demos/synonym-search/captions.srt)

The community garden brief is authored public sample input. The alternatives, downloaded graph, retrieved passages and generated answer are actual outputs. The command-line section displays those JSON fields in a readable presentation; it is not a separate Terraphim interface. The voice is synthetic British English (Emma). Setup is omitted, and the recorded interaction runs at its original speed. [Recording details and file identities](/demos/synonym-search/manifest.json).

## Reproduce it with released builds

The recording preserves its original candidate-build identities. The same flow was separately verified on 12 October 2026 using the published [Editor v0.1.0-rc.1 prerelease](https://github.com/terraphim/terraphim-editor/releases/tag/v0.1.0-rc.1) and [terraphim-grep v1.21.19](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.19). The editor is still an RC; the video is not a claim that every host or feature is fully qualified.

Download the example ZIP, extract it, and follow `README.md`. It uses the same graph and clean brief as the recording. Verify `terraphim-grep --version` before running the two commands above. The release includes macOS and Linux builds; Windows is not claimed by this example.

Inspect the separate released-binary outputs: [before sharing the synonym graph](/demos/synonym-search/released-before-sharing.json), [without synthesis](/demos/synonym-search/released-without-synthesis.json), and [with synthesis](/demos/synonym-search/released-with-synthesis.json). The baseline used the editor's default role, which lacks the authored synonym: zero passages became three when the exported graph was supplied. The paired modes retrieved the same passages. [Released-build identities, commands and file checksums](/demos/synonym-search/reproduction.json) distinguish this verification from the original recording. A fresh synthesis run may produce different wording.

[Earlier browser and Zed host walkthroughs](/how-tos/knowledge-work-editor/) retain their own recorded versions and limitations. This focused story does not qualify all 41 source-video requirements. The Zed fork remains separate.
