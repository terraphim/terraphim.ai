# What the model requested, and what actually ran

This example extends the existing project-local OpenCode adapter with a linked execution record. The released **terraphim-agent v1.21.19** still compiles and applies the correction. The included **adapter v2.0.0** records the evidence and updates the host's mutable input. **OpenCode 2.0.20 executes the command.** The new adapter is supplied as source in this example; it is not represented as part of the earlier binary release.

## Run the example

Requirements: Python 3, Node.js, OpenCode 2.0.20, a checksum-verified `terraphim-agent` from [clients v1.21.19](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.19), and an already authenticated coding model. The verified Apple Silicon binary has SHA-256 `78542870b76e2a90fa7b2a767ba7fd6126b32304a925feb83e16db01faf0f4d1`. Check the release archive against its published `SHA256SUMS` before extracting it.

```sh
python3 reproduce.py \
  --agent /absolute/path/to/terraphim-agent \
  --model kimi-code-plan-global/k3 \
  --output /absolute/path/to/a-new-harbour-run
node verify.mjs /absolute/path/to/a-new-harbour-run
```

Use a fresh output directory. The script fails if the host does not perform the expected commands. Global hooks and Terraphim stores are unchanged. Only the fictional public Harbour brief and commands are sent to the configured coding model; no fallback provider or paid API is selected automatically.

The baseline calls `python3 validate-brief.py --chek`, which exits 2. The actual after-tool event becomes a saved learning. The example then adds an explicitly checked tool-preference mapping to `--check`, compiles it with the existing Terraphim CLI, and exports its `synonyms::` Markdown. Recording a suggested correction with `learn correct` alone does not activate it; there is no built-in human-approval gate here.

A fresh OpenCode process requests the same typo. Terraphim returns the corrected command; the adapter applies it; OpenCode executes it and the validator writes an output bound to that execution.

## Inspect one execution

Each shell call receives an `execution_id` UUID and a folder:

```text
evidence/executions/<execution_id>/
  receipt.json           original/applied/executed input, host IDs, result and hashes
  config.json            selected role points to this execution's graph snapshot
  compiled-rules.json    exact graph used (present when a graph is configured)
  validation.json        actual successful validator output, with execution_id
```

`receipt.json` contains the host session, message and tool-call IDs; original request; matching compiled rule ID and rule-set SHA-256; applied input; the actual after-tool input; exit code and combined shell output; and the output file's path, execution ID, byte length and SHA-256. The SHA identifies the rule-set version, rather than inventing a semantic version for generated data. Rule ID alone is not globally unique.

The adapter attributes the fixture's exact whole-command mapping by checking the compiled rule against the actual CLI return. Unsupported or ambiguous rewrite attribution fails. It does not claim general substring/multiple-rule provenance for all Terraphim integrations.

`verify.mjs` cross-checks the receipts against actual native before/after events and rehashes the saved graph and artifact. Successful output must have the same execution ID and JSON content as the tool's reported output. Missing files, old-run IDs, changed bytes, mismatched commands and unmatched host calls fail verification. The recorder rejects concurrent fixture calls so an output cannot be attributed to a different pending command. Interrupted calls remain incomplete; blocked/error calls do not receive an executed-command claim.

Read `evidence/verification.json`, `evidence/identities.json`, `evidence/host-events.jsonl` and each execution receipt. `evidence/baseline-host.jsonl` and `corrected-host.jsonl` retain the host transcript, including any difference between the model's requested command and execution.

## Scope

This is a public fixture and an evidence trail, not a tamper-proof attestation or general secret-redaction service. The released agent has documented redaction limitations in command/cwd/passthrough fields, so use fictional input. OpenCode supplies combined output; the adapter does not invent separate stdout/stderr streams. Only the two validator commands are permitted by the included host configuration.
