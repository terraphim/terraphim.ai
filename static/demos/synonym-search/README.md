# Different words. The same idea.

Source: https://terraphim.ai/how-tos/synonym-search/

This kit contains the actual graph and clean brief exported in the 80-second
recording, and separate evidence from released builds. The brief is public sample
input. The graph and search results are actual outputs.

## Reproduce local retrieval

1. Download terraphim-grep v1.21.19 for your macOS or Linux architecture:
   https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.19
   Check the archive against that release's SHA256SUMS, then extract it and put
   terraphim-grep on PATH. No Windows build is claimed by this kit.
2. In this extracted directory, run:

```sh
terraphim-grep --version
mkdir -p corpus
cp project-brief.md corpus/project-brief.md
terraphim-grep concern --thesaurus baseline-role.json --paths corpus -C 2 --search-only --json
terraphim-grep concern --thesaurus knowledge-graph.json --paths corpus -C 2 --search-only --json
```

The first search uses the editor's default role, which lacks this authored
synonym. It returns zero passages. The exported graph connects Risk and Concern;
the second search returns three Risk passages even though Concern is absent
from the clean brief. `released-before-sharing.json` and
`released-without-synthesis.json` contain those actual outputs.

## Compare optional synthesis

Configure a model provider using the client release documentation. Then run:

```sh
terraphim-grep concern --thesaurus knowledge-graph.json --paths corpus -C 2 --json --answer
```

Optional synthesis sends the retrieved passages to your configured model
provider and may incur provider charges. The released verification used
DeepSeek (deepseek-v4-flash-0731). No credentials are included. Generated wording
can vary. Compare the chunks and citations, not an exact answer string:
`released-with-synthesis.json` has the same three chunks as the search-only run.
Decisions in the source do not prove that the actions have been completed.

## Recreate the editor export

Use https://terraphim.ai/editor/ or the published v0.1.0-rc.1 editor prerelease:
https://github.com/terraphim/terraphim-editor/releases/tag/v0.1.0-rc.1

Open the brief, add Concern as an alternative to Risk, swap between them, and
retain Risk in the final text. Choose Knowledge graph from the Markdown export
menu. The definition is `synonyms:: Risk, Concern`. Export the graph and clean
text, then use your exported filenames in the commands above. This explicitly
shares document synonyms; it does not silently update the active role.
`annotated.md` preserves the alternatives for reopening.

## Provenance

- `manifest.json`, `without-synthesis.json`, and `with-synthesis.json` describe
  the original candidate-build recording. They have not been relabelled as
  released-binary evidence.
- `reproduction.json` and the `released-*.json` files describe the separate
  v0.1.0-rc.1 / v1.21.19 verification on 12 October 2026.
- `captions.vtt`, `captions.srt`, and `transcript.txt` accompany the original video.
  The British female narration is synthetic (Emma, Kokoro).
- Video and poster are available on the source page; they are not in this ZIP.

This focused flow does not qualify all 41 requirements or every extension.
The Zed fork remains separate.
