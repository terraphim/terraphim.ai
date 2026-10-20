/* engine.js — thin adapter over the compiled terraphim_rolegraph crate.
 *
 * The algorithm itself runs in WebAssembly built from the real Rust crate
 * (crates/terraphim_rolegraph/wasm): Aho-Corasick LeftmostLongest matching
 * with ascii_case_insensitive(true), magic_pair directed edges, and
 * node.rank + edge.rank + doc_hash ranking. This file only translates
 * JSON strings to JS objects and keeps a Map-shaped surface for
 * explainer.js. No algorithm is reimplemented here.
 */
const TGEngine = (() => {
  "use strict";

  const GLUE = "/explainers/graph-embeddings/wasm/terraphim_rolegraph_wasm.js";
  let wasm = null;

  // In the browser: dynamic-import the wasm-pack `web` bundle. In Node
  // (conformance checks): pass the pre-required `nodejs` pkg as `mod`.
  async function init(mod) {
    if (!wasm) {
      wasm = mod || (await import(GLUE));
      if (!mod) await wasm.default();
    }
    return wasm;
  }

  const magicPair = (x, y) => Number(wasm.magic_pair_js(BigInt(x), BigInt(y)));
  const magicUnpair = (z) => [...wasm.magic_unpair_js(BigInt(z))].map(Number);

  class RoleGraph {
    constructor(thesaurusObj) {
      if (!wasm) throw new Error("await TGEngine.init() before constructing");
      this._g = new wasm.RoleGraphWasm(JSON.stringify(thesaurusObj));
    }

    // Matcher surface: spans + id -> nterm map, live from the crate.
    get ac() {
      return {
        findMatches: (text) => JSON.parse(this._g.find_matches(text)),
        nterm: JSON.parse(this._g.nterms()),
      };
    }

    findNodeIds(text) {
      return JSON.parse(this._g.find_node_ids(text));
    }

    insertDocument(docId, text, title) {
      return JSON.parse(this._g.insert_document(docId, title || docId, text));
    }

    removeDocument(docId) {
      return this._g.remove_document(docId);
    }

    queryGraph(q) {
      return JSON.parse(this._g.query(q)).map((r) => ({
        id: r.doc,
        rank: r.rank,
        contributions: r.contributions.map((c) => ({
          nodeId: Number(c.node_id),
          nterm: c.nterm,
          nodeRank: c.node_rank,
          edgeId: Number(c.edge_id),
          pair: c.pair.map(Number),
          edgeRank: c.edge_rank,
          docRank: c.doc_rank,
          total: c.total,
        })),
      }));
    }

    stats() {
      const s = JSON.parse(this._g.stats());
      return {
        nodes: s.nodes,
        edges: s.edges,
        documents: s.documents,
        thesaurus: s.thesaurus_terms,
      };
    }

    get nodes() {
      return new Map(
        JSON.parse(this._g.snapshot()).nodes.map((n) => [n.id, n])
      );
    }

    get edges() {
      return new Map(
        JSON.parse(this._g.snapshot()).edges.map((e) => [
          e.id,
          { id: e.id, rank: e.rank, docHash: new Map(Object.entries(e.doc_hash)) },
        ])
      );
    }

    // Real rebuild_automata path: insert into the thesaurus, rebuild.
    addSynonym(synonym, conceptId, nterm) {
      this._g.add_synonym(synonym, BigInt(conceptId), nterm);
    }
  }

  return { init, magicPair, magicUnpair, RoleGraph };
})();

if (typeof window !== "undefined") window.TGEngine = TGEngine;
if (typeof module !== "undefined" && module.exports) module.exports = TGEngine;
