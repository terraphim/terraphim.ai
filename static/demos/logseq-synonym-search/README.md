# Find the garden decisions with Logseq and Terraphim

Your project brief says **Risk**. You remember **Concern**. This example keeps the relationship in a concept note and uses the same exported graph as the [Terraphim Editor walkthrough](https://terraphim.ai/how-tos/synonym-search/) to find the decisions.

## Open the example

1. Extract the ZIP.
2. In Logseq 2.0, open the graph menu → **Import existing notes** → **File to DB graph**. Select the included `graph` folder and name the new graph **Terraphim garden demo**. This import was checked in Logseq 2.0.2. A Logseq version that supports file graphs can open this Markdown graph folder directly.
3. Open **Start here**, then **Risk**. Its `synonyms:: Risk, Concern` property belongs to the concept note. The native `alias:: Concern` property also gives that page another name inside Logseq.
4. Search for **Concern search** and choose **Open in sidebar** to see the saved command-line passages beside the concept and embedded project brief.

5. To explore the note connections, open **Graph view**, choose **Graph settings → All pages**, and select **Community garden launch**. Increase **Link distance** and zoom in to read the labels. The arrows show Logseq page links. The supplied Terraphim graph separately connects the words in the Risk synonym property.

The three examples are concrete decisions: a backup supplier for late timber, a covered area for rain, and a reserve list for volunteer cancellations.

## Run the search

Install [terraphim-grep 1.21.19](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.19), then open a terminal in the extracted `graph` folder:

```sh
terraphim-grep concern --thesaurus baseline-role.json --paths pages/Projects -C 2 --json --search-only
terraphim-grep concern --thesaurus knowledge-graph.json --paths pages/Projects -C 2 --json --search-only
```

The first command returns **0 passages**. The second returns **3 passages** from `Community garden launch.md`, at lines 3, 5 and 7. Search targets only `pages/Projects`: the Risk concept note and saved results cannot supply a literal hit. The project brief never contains the word “concern”.

If you see “No git repository found”, the search still works: Git-based exclusion rules are simply unavailable in the extracted folder.

`evidence/before-sharing.json` and `evidence/with-synonym.json` contain the actual saved outputs. `evidence/verification.json` records the commands and binary identity; `manifest.json` lists the download checksums.

## How the files connect

- `graph/pages/Risk.md`: the concept, native page alias and Terraphim synonym property.
- `graph/pages/Projects/Community garden launch.md`: the source brief, written as Logseq blocks with links to Risk.
- `graph/pages/Concern search.md`: saved CLI results only.
- `graph/knowledge-graph.json`: the graph exported by Terraphim Editor, unchanged from the website example.
- `graph/baseline-role.json`: a baseline without the authored Risk/Concern relationship.

These commands read the included Markdown files. Logseq 2.0 imports a copy into its database; use the original extracted folder for the CLI commands. The supplied JSON graph matches the synonym property in Risk.md. This example shares it explicitly with `--thesaurus`.

Local retrieval needs no model provider. The main website video also demonstrates optional synthesis with `--answer`; this Logseq example focuses on opening the notes and reproducing retrieval.
