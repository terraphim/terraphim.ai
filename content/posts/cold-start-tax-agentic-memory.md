+++
title="A project lesson your coding agent can find next time"
date=2026-07-01
updated=2026-10-13
description="Save an actual project instruction, recover it in a new process, and retrieve it through a small knowledge graph. Includes a narrated demo and reproducible example."

[taxonomies]
categories = ["Technical"]
tags = ["Terraphim", "ai", "agentic-engineering", "memory", "knowledge-graph", "developer-tools"]
[extra]
toc = true
comments = true
+++

You explain the project's validation command. The session ends. Next time, the agent needs the same explanation. Keeping the instruction somewhere is useful only if the next run can find the right instruction again.

This walkthrough saves one lesson from a fictional project, opens it in a new process, and retrieves it through a small knowledge graph. You can inspect the exact saved text and repeat the same checks with the downloadable example.

<!-- more -->

<video controls playsinline preload="metadata" poster="/demos/agent-memory/screenshots/poster.jpg" style="width:100%;height:auto;max-width:100%;border-radius:12px" aria-label="Save and retrieve a Harbour project lesson with Terraphim agent">
  <source src="/demos/agent-memory/agent-memory.mp4" type="video/mp4">
  <track kind="captions" src="/demos/agent-memory/captions.vtt" srclang="en" label="English" default>
  Your browser does not support embedded video. <a href="/demos/agent-memory/agent-memory.mp4">Download the video</a>.
</video>

[Download the Harbour example](/demos/agent-memory/harbour-memory-example.zip) · [Read the transcript](/demos/agent-memory/transcript.txt)

## Start with an instruction worth keeping

Harbour is a small public project brief. It records a decision, a risk and an owner. Before publication, its validator checks that all three fields are present. The instruction we want the next session to remember is deliberately specific:

```text
Validate the Harbour project brief with python3 validate-brief.py --check.
Keep the source decisions in brief.md intact.
```

That gives a future agent an action and a boundary. “Remember to be careful” would be much harder to use. The example also includes the brief and validator, so the instruction has something concrete to refer to.

The first step is to save this actual text. Download and extract the example, then install [terraphim-agent v1.21.20](https://github.com/terraphim/terraphim-clients/releases/tag/v1.21.20). From the example folder, prepare a new, isolated run before entering the manual commands below:

```sh
python3 reproduce.py --agent /path/to/terraphim-agent \
  --output ./harbour-run --prepare-only
cd harbour-run/fixture
export TERRAPHIM_DEFAULT_DATA_PATH="$(cd .. && pwd)/data"
export TERRAPHIM_SETTINGS_PATH="$(cd .. && pwd)/settings"
```

Use your actual binary path in the first command and put that same verified binary on your PATH for the remaining commands. Preparation creates the role configuration, settings and `lesson.md`; it has not captured anything yet. To run all checks automatically instead, omit `--prepare-only` and choose a fresh output folder.

```sh
terraphim-agent --format json memory capture \
  --file lesson.md \
  --provenance-tag harbour-public-brief-v1
```

Capture returns a memory identifier. We use that identifier to inspect the saved item, rather than treating a successful exit code as the whole result. The saved content is the lesson itself, and the provenance tag identifies which public example supplied it.

`--content` accepts a short instruction directly. `--file` is convenient for a multiline note. Both preserve the supplied text. Missing, blank, unreadable or conflicting inputs fail without creating a substitute placeholder.

## End the process, then open the memory

Each command in the demonstration starts a new process. After capture exits, `memory show` opens the saved identifier. `memory list` finds the item, and `memory export` includes the same instruction in JSON.

```sh
terraphim-agent --format json memory show MEMORY_ID
terraphim-agent --format json memory list
terraphim-agent memory export --format json --output memories.json
```

Replace `MEMORY_ID` with the identifier returned by capture. The reproduction script does this automatically and checks that the reopened and exported text exactly matches `lesson.md`.

![A new process displays the exact saved Harbour instruction and its provenance tag](/demos/agent-memory/screenshots/saved-lesson.jpg)

The store has an explicit location. The example sets `TERRAPHIM_DEFAULT_DATA_PATH` to a new folder for that run; the evolution file lives beneath `terraphim/evolution/cli-agent.json`. A second empty folder supplies the independent-store check. This keeps the demonstration separate from your existing memory files.

Without an explicit data root, the agent retains its usual platform configuration-directory location. Changing the root selects another store; it does not silently migrate or merge your previous one.

## Teach the role the words used by the project

Knowing an identifier is useful for inspection. Day to day, you are more likely to ask a question such as “validate brief”. The **Brief Reviewer** role supplies the terminology for that question.

Its small graph has a **Brief validation** concept:

```markdown
# Brief validation
synonyms:: validate brief, brief validation, --check
```

A second concept describes the **Project brief**, including `brief.md`. Both definitions are ordinary Markdown in the download. The saved instruction mentions these concepts, connecting an action with the document it applies to.

The `synonyms::` property makes the relationship visible: “validate brief” and `--check` are labels for the same concept in this project. You can review or change that relationship. Saving a memory does not invent new terminology or update every other role automatically.

This is the same explicit-knowledge principle used in the [editor-to-search example](/how-tos/synonym-search/): record the relationship, then use the configured graph to find relevant work. Here the searched material is an authored memory item.

## Retrieve the instruction, then check the empty cases

With the example's role configuration loaded, this query retrieves the stored lesson:

```sh
terraphim-agent --config ../config.json memory retrieve 'validate brief' \
  --role 'Brief Reviewer' --format json
```

The result includes the original text, its memory identifier, the provenance tag and a matched concept. It is a retrieved instruction, not a generated paraphrase. The viewer can compare it directly with the file that was captured.

![The Brief Reviewer retrieves one saved lesson while unrelated-query, other-role and empty-store controls return zero](/demos/agent-memory/screenshots/retrieval-controls.jpg)

The accompanying controls matter just as much. “Volcanic eruption” returns no memory. The **Finance Reviewer** role, which has budget and grant concepts, does not match the validation query. The same useful query against a separate empty store also returns nothing.

Those observations distinguish useful retrieval from a command that always prints the latest note. Roles shape which concepts are recognised. They are not an access-control system: use separate stores and ordinary filesystem permissions where separation is required.

## What happens inside the CLI

The agent stores the lesson using Terraphim's existing evolution types. During retrieval, the role's thesaurus matches terms, and the role graph ranks memory items by their concept relationships. There is no lexical fallback when a question matches none of the configured concepts.

This graph uses co-occurrence edges, so the example intentionally connects validation with the project brief. A single isolated concept is not enough to assume the same retrieval behavior. Keep the graph and the note inspectable, and test the questions people will actually ask.

`memory apply` can preview proposed context for a prompt. That preview does not execute a command or prove a coding host consumed it. The separate hooks walkthrough will follow the instruction into actual execution. Captured memories and reviewed learning corrections also use different stores; neither is an automatic copy of the other.

## Try the next run yourself

The ZIP contains the public brief, validator, lesson, Markdown concepts, reproduction script and saved outputs. Follow its README to verify the released binary, create an isolated run and compare the positive and negative results. The script checks the saved content, rather than relying on expected screenshots.

[Download and reproduce the memory example](/demos/agent-memory/harbour-memory-example.zip). You can also inspect the [saved outputs and verification manifest](/demos/agent-memory/manifest.json).

The useful result here is modest and concrete: an instruction survives the process that captured it, and the intended project terminology can find it again. Measuring whether that saves tokens or improves later decisions needs a separate experiment.

*Updated 13 October 2026 with a reproducible walkthrough. The broader memory-lifecycle vocabulary was inspired by [memco.ai's field guide](https://www.memco.ai/field-guide). The video uses synthetic British female narration and readable views of actual CLI outputs. The Harbour fixture is public sample data.*
