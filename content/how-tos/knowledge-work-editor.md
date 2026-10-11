+++
title = "Write and search with the same knowledge graph"
description = "Try Terraphim Editor, then inspect search results with and without synthesis."
date = 2026-10-11
+++

[Try Terraphim Editor](/editor/)

Keep alternatives attached to words, sentences and paragraphs. Ghost a passage without losing it, stash notes in Overflow, and use the Lab to inspect possible cuts. The editor runs as WebAssembly in your browser with a bundled local knowledge graph.

This is a preview. The complete source-video requirements are still being qualified; Safari dragging and some visual/native cases remain unresolved. Keyboard pull from Overflow is available. The browser demo does not imply full custom visual parity in the stock Zed extension.

## Start with a public brief

Paste this supplied example into the editor. It is sample input, not generated output:

```markdown
# Public research workspace

Decision: launch a local-first research workspace for the delivery team.

The decision owner will review the brief before the pilot begins.

Risk: inconsistent terminology makes prior decisions hard to locate.

Use the project brief to align the team and keep the decision record clear.
```

Turn on Write_On using the word counter. Explore alternatives for “decision”, add your own wording, and compare it in context. Ghost/revive a passage, stash a note in Overflow and inspect the Lab. Save the result and reopen the actual file to check the choices and annotations.

## Save your work and use it in search

Save keeps the Markdown, alternatives, ghosts and Overflow together. Clean Markdown export includes active text and omits ghosts, Overflow and the annotation block. Chrome can offer a file handle; Firefox and Safari use a download. Check the actual browser dialog and downloaded file.

Download the [same bundled KG](/editor/roles/default.json) and inspect the [editor build identity](/editor/release.json). Newly authored alternatives register as document-scoped synonyms; they do not silently change this shared KG.

Move the chosen saved or clean-exported file into a dedicated local corpus folder. Keep evidence logs and other copies outside that folder. With `terraphim-grep` installed, set paths for that public corpus and downloaded KG:

```bash
terraphim-grep "decision" --thesaurus ./default.json --paths ./public-corpus --json
terraphim-grep "decision" --thesaurus ./default.json --paths ./public-corpus --json --answer
```

The first command returns search evidence without enabling synthesis. The second asks for an answer when sufficient evidence and a configured provider are available. Keep the query, corpus and KG unchanged to compare them. Add the same `--role-config` path to both commands if configuring a provider through a role. Check the generated answer against the returned source lines; a missing answer or provider error is not a successful synthesis.

Writing and local search do not require sending your document to an LLM. Synthesis may send retrieved content to the configured provider. Use public sample content for the demo and inspect the provider configuration before enabling `--answer`.
