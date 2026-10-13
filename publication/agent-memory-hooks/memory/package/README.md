# Harbour: save a lesson and find it next time

This public example captures an actual instruction, recovers it in new processes,
and retrieves it through an explicit project knowledge graph. It uses
terraphim-agent **1.21.20**. Earlier 1.21.19 cannot capture supplied lesson text.

## Requirements

- Python 3.9 or later and `rg` (ripgrep) on PATH; the local Markdown KG loader uses it.
- The released `terraphim-agent` for your platform. Download it and SHA256SUMS from:
  https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.20
- Verify the archive against the release's SHA256SUMS before extracting it.
  `released-binaries.json` also pins the extracted binaries accepted by this example.
- No model-provider account is needed for this memory walkthrough. There is no
  generated answer and no coding-host execution in this example.

## Run every check

From this extracted folder, substituting your real binary path:

```sh
python3 reproduce.py --agent /path/to/terraphim-agent --output ./harbour-run
```

The output folder must not exist. The script checks the binary's exact version
and hash, prepares public input and scoped settings, then starts ten independent
CLI processes. It never changes HOME or installs hooks. It writes only inside
that new output folder. If any command or assertion fails, it exits nonzero.

Expected result: `verification.json` says PASS, with qualification
`released-binary`. One exact saved lesson is retrieved for `validate brief` by
Brief Reviewer. The unrelated query, Finance Reviewer and separate empty store
return zero. `memory apply` previews proposed context; it executes nothing.

Inspect `outputs/*.stdout.json` for actual CLI responses, `execution-receipts.json`
for argv/stdout/stderr/exit codes and `data/terraphim/evolution/cli-agent.json`
for the persisted store. `recorded/` contains the publication's observed outputs;
your identifiers and timestamps will naturally differ.

## Walk through the commands yourself

Use another fresh folder. Preparation does not capture memory:

```sh
python3 reproduce.py --agent /path/to/terraphim-agent --output ./manual-run --prepare-only
cd manual-run/fixture
export TERRAPHIM_DEFAULT_DATA_PATH="$(cd .. && pwd)/data"
export TERRAPHIM_SETTINGS_PATH="$(cd .. && pwd)/settings"
```

Put the same verified binary on PATH, or replace `terraphim-agent` below with its
full path. Check `terraphim-agent --version` reports 1.21.20, then run:

```sh
terraphim-agent --format json memory capture --file lesson.md --provenance-tag harbour-public-brief-v1
terraphim-agent --format json memory list
terraphim-agent --format json memory show MEMORY_ID_FROM_CAPTURE
terraphim-agent memory export --format json --output memories.json
terraphim-agent --config ../config.json memory retrieve 'validate brief' --role 'Brief Reviewer' --format json
terraphim-agent --config ../config.json memory retrieve 'volcanic eruption' --role 'Brief Reviewer' --format json
terraphim-agent --config ../config.json memory retrieve 'validate brief' --role 'Finance Reviewer' --format json
```

Every command exits; the next invocation reads the saved file in a new process.
The knowledge graph is in `fixture/kg/`. Its `synonyms::` definitions are explicit,
reviewable terminology. Saving a memory does not automatically create concepts
or copy the item to the separate learning-corrections store.

## Scope and interpretation

Roles filter graph retrieval; they do not enforce confidentiality. Separate data
roots select separate stores, and ordinary filesystem permissions still apply.
The lesson is preserved as supplied, so review your own notes before sharing or
exporting them. This sample contains no private data or credentials. Graph
retrieval depends on concept co-occurrence; the note deliberately connects Brief
validation with Project brief. No token savings or host execution are claimed.

The `--candidate` switch is only for engineering checks and labels results
`candidate-only`; those results do not qualify as released-binary evidence.
