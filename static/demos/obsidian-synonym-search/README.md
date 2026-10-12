# Obsidian synonym-search example

Captured from the installed Obsidian 1.14.4 on 12 October 2026 in an isolated demo vault. No personal notes or community plugins were used.

Open `vault` as a folder in Obsidian. `Notes/Risk.md` owns the raw `synonyms:: Risk, Concern` property and embeds the source brief, `Notes/Projects/Community garden launch.md`. `Search results/Concern search.md` contains saved output from the released terraphim-grep 1.21.19 binary; it does not define synonyms and is not an Obsidian search extension.

The graph and brief are byte-identical to the [published editor demo exports](https://terraphim.ai/how-tos/synonym-search/). The **project brief** has no literal “concern”; the separate **Risk concept note** deliberately contains it as a synonym property. The property agrees with the exported graph. This example supplies that graph explicitly; it does not claim that saving an Obsidian note automatically rebuilds it.

Search targets the project brief only. It excludes the concept definition, generated JSON and saved result note, so none can supply a literal query hit. `evidence/` contains the actual outputs, binary/input hashes and assertions.

From the vault directory, with terraphim-grep 1.21.19 on your PATH:

```sh
terraphim-grep concern --thesaurus "Knowledge graph/baseline-role.json" --paths "Notes/Projects" -C 2 --json --search-only
terraphim-grep concern --thesaurus "Knowledge graph/knowledge-graph.json" --paths "Notes/Projects" -C 2 --json --search-only
```

Outside a Git checkout, this released CLI may print “No git repository found”. The two commands still complete successfully: the baseline returns zero passages and the synonym graph returns three.

The corrected native screenshot is `screenshots/03-synonyms-in-knowledge-note.jpg`: `Risk.md` owns the actual property and embeds the brief, beside the results-only note. The captured accessibility tree is retained in `evidence/native-note-and-results.txt`. Earlier screenshots are preserved under `publication/synonym-search/archive/before-obsidian-note-synonyms-20261012/` and excluded from the corrected bundle.

Terraphim’s custom `synonyms::` convention uses Logseq-compatible Markdown property syntax. Obsidian’s native note aliases use YAML `aliases`; automatic alias import or vault synchronisation is not part of this example.

The original narrated video already compares retrieval and optional synthesis. This additional Obsidian capture reruns local retrieval only; it does not claim a new synthesis run. Jason Fried’s [Write_On video](https://x.com/jasonfried/status/2105403067793584590) inspired the editor work.
