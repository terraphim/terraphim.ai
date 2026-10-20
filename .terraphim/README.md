# .terraphim — project knowledge graph

Project-local Terraphim assets for this site, referenced by
`content/posts/graph-embeddings-checklists.md`.

## Layout

- `kg/` — concept markdown for the search demo. Each file: heading is the
  normalised term, `synonyms::` line lists the surface forms the checklist
  must catch (e.g. `validation gate` carries `quality gate`; `judge-verdicts`
  carries `accept`, `fail`, `escalate`, `pass`, ...).
- `rewrite/` — the "Command Rewriter" hook checklist demonstrated in the
  post (`bun add`, `bunx`, `uv`, `docker compose`, ...). The quoted file
  `bun install.md` lives here verbatim.
- `thesaurus.json` — compiled from `kg/`; role name "Terraphim Engineer"
  (public 39-entry subset of the author's working role).

## Reproduce

```bash
terraphim-grep "quality gate" --haystack all --paths . \
  --thesaurus .terraphim/thesaurus.json -n 8 -C 1 --json
# expect: kg_hits 8, concepts: accept, accepted, escalate, fail,
#         improve, judge-verdicts, needs improvement, pass

terraphim-grep "checklist" --haystack all --paths . \
  --thesaurus .terraphim/thesaurus.json -n 5 -C 1 --json
# expect: kg_hits 0 (honest "not covered" case)
```

For the hook findings demo, point your agent's Command Rewriter role at
`rewrite/` (see the rewrite role's `knowledge_graph_local.path` in your
terraphim config) and run:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"npm install react"}}' \
  | terraphim-agent hook --hook-type pre-tool-use --json
```

## Regenerate the thesaurus

```bash
python3 - <<'PY'
import os, json, glob
data, cid = {}, 100
for f in sorted(glob.glob(".terraphim/kg/*.md")):
    nterm = os.path.splitext(os.path.basename(f))[0]
    txt = open(f, encoding="utf-8").read()
    syn = next((l.split("::",1)[1] for l in txt.splitlines()
                if l.strip().lower().startswith("synonyms::")), "")
    for t in dict.fromkeys([nterm] + [s.strip().lower() for s in syn.split(",") if s.strip()]):
        data.setdefault(t.lower(), {"id": cid, "nterm": nterm})
    cid += 1
json.dump({"name": "Terraphim Engineer", "data": data}, open(".terraphim/thesaurus.json","w"), indent=2)
PY
```

See also: `docs/src/kg/checklists/` in terraphim/terraphim-ai for the
published checklist concepts (code review, security).
