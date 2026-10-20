/* Terraphim RoleGraph — faithful JavaScript port for the interactive explainer.
 *
 * Mirrors terraphim-core/crates/terraphim_rolegraph/src/lib.rs:
 *   - Aho-Corasick matching semantics: LeftmostLongest + ASCII case-insensitive
 *   - insert_document: matched node ids -> consecutive pairs -> edges/counts
 *   - magic_pair: Cantor-style directed pairing for edge ids
 *   - query_graph: sum of node.rank + edge.rank + per-document rank
 * including the or_insert-then-increment quirk in init_or_update_edge.
 *
 * Loads as a classic script: window.TGEngine in the browser,
 * module.exports in Node for the conformance check.
 */
(function () {
  "use strict";

  // lib.rs:1270 — pub fn magic_pair(x: u64, y: u64) -> u64
  function magicPair(x, y) {
    return x >= y ? x * x + x + y : y * y + x;
  }

  // lib.rs:1276 — pub fn magic_unpair(z: u64) -> (u64, u64)
  function magicUnpair(z) {
    const q = Math.floor(Math.sqrt(z));
    const l = z - q * q;
    return l < q ? [l, q] : [q, l - q];
  }

  // Leftmost-longest, ASCII case-insensitive multi-pattern scan.
  // Equivalent output to aho_corasick with MatchKind::LeftmostLongest:
  // at each leftmost position, the longest pattern that matches wins;
  // scanning resumes after the matched span.
  class AhoLite {
    constructor(thesaurusData) {
      this.patterns = Object.entries(thesaurusData)
        .map(([k, v]) => [k.toLowerCase(), v.id])
        .sort((a, b) => b[0].length - a[0].length);
      this.nterm = {};
      for (const v of Object.values(thesaurusData)) {
        this.nterm[v.id] = v.nterm;
      }
    }

    findMatches(text) {
      const t = text.toLowerCase();
      const out = [];
      let i = 0;
      while (i < t.length) {
        let hit = null;
        for (const [pat, id] of this.patterns) {
          if (t.startsWith(pat, i)) {
            hit = { start: i, end: i + pat.length, id: id };
            break; // patterns sorted longest-first == LeftmostLongest
          }
        }
        if (hit) {
          out.push(hit);
          i = hit.end;
        } else {
          i += 1;
        }
      }
      return out;
    }
  }

  class RoleGraphLite {
    constructor(thesaurus) {
      this.thesaurus = thesaurus;
      this.ac = new AhoLite(thesaurus.data);
      this.nodes = new Map(); // id -> {rank, connectedWith:Set}
      this.edges = new Map(); // edgeId -> {id, rank, docHash:Map<docId,count>}
      this.documents = new Map(); // docId -> {id, title}
    }

    findNodeIds(text) {
      return this.ac.findMatches(text).map((m) => m.id);
    }

    // lib.rs:922 — replace semantics: remove old contributions first
    insertDocument(docId, text, title) {
      this.removeDocumentContributions(docId);
      this.documents.set(docId, { id: docId, title: title || docId });
      const matches = this.findNodeIds(text);
      for (let k = 0; k + 1 < matches.length; k++) {
        this.addOrUpdateDocument(docId, matches[k], matches[k + 1]);
      }
      return matches;
    }

    // lib.rs:946 — idempotent removal
    removeDocumentContributions(docId) {
      const affected = [];
      for (const [eid, edge] of this.edges) {
        if (edge.docHash.has(docId)) affected.push(eid);
      }
      for (const eid of affected) {
        const edge = this.edges.get(eid);
        edge.docHash.delete(docId);
        const edgeRemoved = edge.docHash.size === 0;
        if (edgeRemoved) this.edges.delete(eid);
        const [a, b] = magicUnpair(eid);
        for (const endpoint of [a, b]) {
          const node = this.nodes.get(endpoint);
          if (!node) continue;
          node.rank = Math.max(0, node.rank - 1);
          if (edgeRemoved) node.connectedWith.delete(eid);
          if (node.rank === 0 && node.connectedWith.size === 0) {
            this.nodes.delete(endpoint);
          }
        }
      }
      this.documents.delete(docId);
    }

    // lib.rs:989-1008 — init_or_update_edge + init_or_update_node
    addOrUpdateDocument(docId, x, y) {
      const eid = magicPair(x, y);
      if (this.edges.has(eid)) {
        const edge = this.edges.get(eid);
        // Rust: *edge.doc_hash.entry(doc).or_insert(1) += 1
        edge.docHash.set(docId, (edge.docHash.get(docId) ?? 1) + 1);
      } else {
        this.edges.set(eid, {
          id: eid,
          rank: 1,
          docHash: new Map([[docId, 1]]),
        });
      }
      for (const nid of [x, y]) {
        if (this.nodes.has(nid)) {
          const node = this.nodes.get(nid);
          node.rank += 1;
          node.connectedWith.add(eid);
        } else {
          this.nodes.set(nid, { rank: 1, connectedWith: new Set([eid]) });
        }
      }
    }

    // lib.rs:455 — query_graph with per-contribution provenance
    queryGraph(q, { offset = 0, limit = null } = {}) {
      const nodeIds = this.findNodeIds(q);
      const results = new Map();
      for (const nid of nodeIds) {
        const node = this.nodes.get(nid);
        if (!node) continue;
        for (const eid of node.connectedWith) {
          const edge = this.edges.get(eid);
          if (!edge) continue;
          const [a, b] = magicUnpair(eid);
          for (const [docId, docRank] of edge.docHash) {
            const total = node.rank + edge.rank + docRank;
            let entry = results.get(docId);
            if (!entry) {
              entry = { id: docId, rank: 0, contributions: [] };
              results.set(docId, entry);
            }
            entry.rank += total;
            entry.contributions.push({
              nodeId: nid,
              nterm: this.ac.nterm[nid] || String(nid),
              edgeId: eid,
              pair: [a, b],
              nodeRank: node.rank,
              edgeRank: edge.rank,
              docRank: docRank,
              total: total,
            });
          }
        }
      }
      const ranked = [...results.values()].sort(
        (x, y) => y.rank - x.rank || (x.id < y.id ? -1 : 1)
      );
      const sliced = ranked.slice(offset);
      return limit == null ? sliced : sliced.slice(0, limit);
    }

    stats() {
      return {
        nodes: this.nodes.size,
        edges: this.edges.size,
        documents: this.documents.size,
        thesaurus: this.ac.patterns.length,
      };
    }
  }

  const TGEngine = { magicPair, magicUnpair, AhoLite, RoleGraphLite };
  if (typeof module !== "undefined" && module.exports) {
    module.exports = TGEngine;
  }
  if (typeof window !== "undefined") {
    window.TGEngine = TGEngine;
  }
})();
