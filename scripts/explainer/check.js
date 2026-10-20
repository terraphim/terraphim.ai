#!/usr/bin/env node
/* Conformance check: WASM (real terraphim_rolegraph crate) output ==
 * Python oracle goldens. Runs the compiled crate through the same
 * adapter the page uses — no mocks.
 * Usage: node check.js
 */
"use strict";

const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..", "..");
const staticDir = path.join(root, "static", "explainers", "graph-embeddings");
const engine = require(path.join(staticDir, "engine.js"));
const wasmPkg = require(path.join(__dirname, "wasm-node", "terraphim_rolegraph_wasm.js"));
const corpus = JSON.parse(fs.readFileSync(path.join(staticDir, "corpus.json"), "utf8"));
const goldens = JSON.parse(fs.readFileSync(path.join(__dirname, "goldens.json"), "utf8"));

let failures = 0;
function eq(name, actual, expected) {
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  if (a === e) {
    console.log(`  ok   ${name}`);
  } else {
    failures += 1;
    console.log(`  FAIL ${name}\n       expected ${e}\n       actual   ${a}`);
  }
}

async function main() {
  await engine.init(wasmPkg);

  // magic_pair round-trip
  {
    let ok = true;
    for (let x = 0; x < 64; x++) {
      for (let y = 0; y < 64; y++) {
        const [a, b] = engine.magicUnpair(engine.magicPair(x, y));
        if (a !== x || b !== y) ok = false;
      }
    }
    eq("magic_pair round-trip 64x64", ok, true);
    eq("magic_pair(1,2)", engine.magicPair(1, 2), 5);
    eq("magic_pair(2,1)", engine.magicPair(2, 1), 7); // directed
  }

  // index the corpus
  const g = new engine.RoleGraph(corpus.thesaurus);
  for (const doc of corpus.documents) {
    g.insertDocument(doc.id, doc.text, doc.title);
  }

  // node ranks
  {
    const actual = {};
    for (const [id, n] of g.nodes) actual[String(id)] = n.rank;
    eq("node ranks", actual, goldens.nodes);
  }

  // edges
  {
    const sortDeep = (v) =>
      Array.isArray(v)
        ? v.map(sortDeep)
        : v && typeof v === "object"
          ? Object.fromEntries(
              Object.keys(v).sort().map((k) => [k, sortDeep(v[k])])
            )
          : v;
    const actual = {};
    for (const [eid, e] of g.edges) {
      actual[String(eid)] = {
        pair: engine.magicUnpair(eid),
        rank: e.rank,
        doc_hash: Object.fromEntries(e.docHash),
      };
    }
    eq("edges", sortDeep(actual), sortDeep(goldens.edges));
  }

  // queries — rank order and totals (contribution detail checked for shape)
  for (const q of corpus.queries) {
    const actual = g.queryGraph(q).map((r) => ({ id: r.id, rank: r.rank }));
    const expected = goldens.queries[q].map((r) => ({ id: r.id, rank: r.rank }));
    eq(`query "${q}"`, actual, expected);
  }

  // contribution detail for "consensus"
  {
    const actual = g.queryGraph("consensus").map((r) => ({
      id: r.id,
      contributions: r.contributions,
    }));
    const expected = goldens.queries["consensus"].map((r) => ({
      id: r.id,
      contributions: r.contributions.map((c) => ({
        nodeId: c.node_id,
        edgeId: c.edge_id,
        nodeRank: c.node_rank,
        edgeRank: c.edge_rank,
        docRank: c.doc_rank,
        total: c.total,
      })),
    }));
    const norm = (rs) =>
      rs.map((r) => ({
        id: r.id,
        contributions: r.contributions
          .map((c) =>
            [c.nodeId, c.edgeId, c.nodeRank, c.edgeRank, c.docRank, c.total].join(":")
          )
          .sort(),
      }));
    eq('contributions "consensus"', norm(actual), norm(expected));
  }

  // re-index idempotency: re-insert doc-raft, graph must be identical
  {
    const snap = () =>
      JSON.stringify([
        [...g.nodes.entries()].map(([k, v]) => [k, v.rank]).sort(),
        [...g.edges.entries()].map(([k, v]) => [k, Object.fromEntries(v.docHash)]).sort(),
      ]);
    const before = snap();
    const doc = corpus.documents.find((d) => d.id === "doc-raft");
    g.insertDocument(doc.id, doc.text, doc.title);
    eq("re-index idempotent", snap(), before);
  }

  // LeftmostLongest: "consensus algorithm" beats "consensus"
  {
    const m = g.ac.findMatches("a consensus algorithm chooses a leader");
    eq("LeftmostLongest span", m.map((x) => x.id), [2, 4]);
    eq("LeftmostLongest covers 19 chars", [m[0].start, m[0].end], [2, 21]);
  }

  // Spans are UTF-16 code-unit offsets (JS slice indices), not UTF-8
  // bytes — the real crate returns byte offsets, the wrapper converts.
  {
    const m = g.ac.findMatches("😀 raft");
    // 😀 = 2 UTF-16 units + 1 space => raft at [3, 7)
    eq("UTF-16 span: emoji before match", m.map((x) => [x.start, x.end]), [[3, 7]]);
    const m2 = g.ac.findMatches("café quorum"); // é = 1 UTF-16 unit
    eq("UTF-16 span: accented text", m2.map((x) => x.id), [6]);
    eq("UTF-16 span: accented offsets", [m2[0].start, m2[0].end], [5, 11]);
  }

  // OOV honest failure
  eq("OOV returns empty", g.queryGraph("kubernetes docker swarm"), []);

  // ASCII-only case folding (aho_corasick ascii_case_insensitive):
  // "CAFÉ" must NOT match pattern "café" — É is not ASCII.
  {
    const ac = new engine.RoleGraph({
      name: "fold-test",
      data: {
        "café": { id: 50, nterm: "café" },
        state: { id: 51, nterm: "state" },
      },
    });
    eq("ASCII fold: CAFÉ does not match café", ac.ac.findMatches("CAFÉ"), []);
    eq("ASCII fold: STATE matches state", ac.ac.findMatches("STATE").map((m) => m.id), [51]);
  }

  // Rust parity: removal decrements once per EDGE while insertion increments
  // per pair OCCURRENCE (lib.rs:946-981 vs 996-1007). A doc repeating a directed
  // pair keeps residual node rank on re-index — not idempotent in that case.
  {
    const r1 = new engine.RoleGraph(corpus.thesaurus);
    r1.insertDocument("rep", "raft consensus raft consensus");
    const before = r1.nodes.get(1).rank; // 3
    r1.insertDocument("rep", "raft consensus raft consensus");
    eq("repeated-edge re-index parity (residual +1)", r1.nodes.get(1).rank, before + 1);
  }

  console.log(failures === 0 ? "\nALL CHECKS PASSED" : `\n${failures} FAILURES`);
  process.exit(failures === 0 ? 0 : 1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
