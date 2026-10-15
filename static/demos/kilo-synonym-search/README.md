# Search the words you meant

This supplier brief says **Risk**. Its author saved **Concern** as an alternative
in Terraphim Editor, then exported the graph and clean Markdown. The graph connects
both words to the same concept. The clean brief contains no literal Concern.

## Reproduce the search

Install [terraphim-grep 1.21.20](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.20),
extract this ZIP and open a terminal in its `kilo-synonym-search` directory.

```sh
terraphim-grep --version
terraphim-grep Concern --thesaurus knowledge-graph.json --paths corpus -n 3 --search-only --json
terraphim-grep Concern --thesaurus knowledge-graph.json --paths corpus -n 3 --answer --json
```

The first command returns three passages at lines 3, 5 and 7, with `answer: null`.
The second adds a generated answer and source citations. Synthesis uses your
configured model provider; its wording can vary. Compare the passages and cited
lines with the supplied source, rather than expecting identical generated prose.
Search only `corpus`, so the annotated document and saved results are excluded.

`annotated.md` reopens in Terraphim Editor with Risk/Concern alternatives. The
online editor is at https://terraphim.ai/editor/ . The released VS Code extension
is at https://marketplace.visualstudio.com/items?itemName=applied-knowledge-systems.terraphim-it .

## What the clip shows

The 44-second silent, captioned clip reopens an actual saved Kilo session and
its source document. Its label says **Saved-run replay**. It preserves the
recorded versions: Kilo 7.8.8, editor 0.1.3, terraphim-grep 1.21.20 and Continue's
search MCP adapter 0.1.1. The tool calls ran on 14 October 2026; this replay was
captured on 15 October. It is not a fresh execution or a Kilo catalog install.

The saved retrieval and synthesis calls used the same graph and returned the
same three source passages. `without-synthesis.json` and `with-synthesis.json`
contain the actual CLI output fields, extracted unchanged from their saved
execution envelopes. `manifest.json` records their provenance and file hashes.
The video has captions and no narration; the main website story retains its
British English narration.

For Kilo configuration, see https://terraphim-skills.md/docs/kilo/ . The four
candidate skills are still under marketplace review. The editor, CLI and MCP
adapter are separate installations. This example does not claim a released
Kilo catalog entry, an Obsidian/Logseq plugin, or all-host feature qualification.
