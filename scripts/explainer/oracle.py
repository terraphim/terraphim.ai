#!/usr/bin/env python3
"""Independent oracle for the graph-embeddings explainer.

Mirrors crates/terraphim_rolegraph/src/lib.rs (terraphim-core) line for line:
  - build_aho_corasick: LeftmostLongest, ascii_case_insensitive
  - insert_document: find_matching_node_ids -> tuple_windows -> add_or_update_document
  - init_or_update_edge: Edge::new(rank=1, doc_hash={doc:1}); repeat ->
    *doc_hash.entry(doc).or_insert(1) += 1   (quirk preserved)
  - init_or_update_node: Node::new(rank=1) else node.rank += 1
  - query_graph: for each matched node, for each edge in connected_with,
    for each (doc, r) in doc_hash: total = node.rank + edge.rank + r

Usage: python3 oracle.py <corpus.json> [goldens_out.json]
"""
import json, sys, re

def magic_pair(x, y):
    return x * x + x + y if x >= y else y * y + x

def magic_unpair(z):
    q = int(z ** 0.5)
    l = z - q * q
    return (l, q) if l < q else (q, l - q)

def ascii_fold(s):
    # aho_corasick ascii_case_insensitive(true): only A-Z folds, not Unicode.
    return s.translate({c: c + 32 for c in range(ord("A"), ord("Z") + 1)})

class AhoLite:
    """Leftmost-longest, ASCII case-insensitive multi-pattern scan."""
    def __init__(self, data):
        self.patterns = sorted(
            [(ascii_fold(k), v["id"]) for k, v in data.items()], key=lambda p: -len(p[0])
        )
        self.nterm = {v["id"]: v["nterm"] for v in data.values()}

    def find_matches(self, text):
        t = ascii_fold(text)
        out, i, n = [], 0, len(t)
        while i < n:
            for pat, cid in self.patterns:
                if t.startswith(pat, i):
                    out.append({"start": i, "end": i + len(pat), "id": cid})
                    i += len(pat)
                    break
            else:
                i += 1
        return out

class RoleGraphLite:
    def __init__(self, thesaurus):
        self.ac = AhoLite(thesaurus["data"])
        self.nodes = {}   # id -> {"rank": int, "connected_with": set}
        self.edges = {}   # magic_pair id -> {"id","rank","doc_hash":{doc:count}}
        self.documents = {}

    def find_node_ids(self, text):
        return [m["id"] for m in self.ac.find_matches(text)]

    def insert_document(self, doc_id, text, title=None):
        self.remove_document_contributions(doc_id)
        self.documents[doc_id] = {"id": doc_id, "title": title or doc_id}
        matches = self.find_node_ids(text)
        for a, b in zip(matches, matches[1:]):
            self.add_or_update_document(doc_id, a, b)

    def remove_document_contributions(self, doc_id):
        affected = [eid for eid, e in self.edges.items() if doc_id in e["doc_hash"]]
        for eid in affected:
            e = self.edges[eid]
            del e["doc_hash"][doc_id]
            edge_removed = not e["doc_hash"]
            if edge_removed:
                del self.edges[eid]
            a, b = magic_unpair(eid)
            for endpoint in (a, b):
                node = self.nodes.get(endpoint)
                if node is None:
                    continue
                node["rank"] = max(0, node["rank"] - 1)
                if edge_removed:
                    node["connected_with"].discard(eid)
                if node["rank"] == 0 and not node["connected_with"]:
                    del self.nodes[endpoint]
        self.documents.pop(doc_id, None)

    def add_or_update_document(self, doc_id, x, y):
        eid = magic_pair(x, y)
        if eid in self.edges:
            e = self.edges[eid]
            e["doc_hash"][doc_id] = e["doc_hash"].get(doc_id, 1) + 1
        else:
            self.edges[eid] = {"id": eid, "rank": 1, "doc_hash": {doc_id: 1}}
        for nid in (x, y):
            if nid in self.nodes:
                self.nodes[nid]["rank"] += 1
                self.nodes[nid]["connected_with"].add(eid)
            else:
                self.nodes[nid] = {"rank": 1, "connected_with": {eid}}

    def query_graph(self, q, offset=0, limit=None):
        node_ids = self.find_node_ids(q)
        results = {}
        for nid in node_ids:
            node = self.nodes.get(nid)
            if node is None:
                continue
            for eid in node["connected_with"]:
                edge = self.edges.get(eid)
                if edge is None:
                    continue
                for doc_id, doc_rank in edge["doc_hash"].items():
                    total = node["rank"] + edge["rank"] + doc_rank
                    entry = results.setdefault(doc_id, {"id": doc_id, "rank": 0,
                                                        "contributions": []})
                    entry["rank"] += total
                    entry["contributions"].append({
                        "node_id": nid, "edge_id": eid,
                        "node_rank": node["rank"], "edge_rank": edge["rank"],
                        "doc_rank": doc_rank, "total": total,
                    })
        ranked = sorted(results.values(), key=lambda r: (-r["rank"], r["id"]))
        ranked = ranked[offset:]
        return ranked[:limit] if limit is not None else ranked

def main():
    corpus = json.load(open(sys.argv[1]))
    g = RoleGraphLite(corpus["thesaurus"])
    for doc in corpus["documents"]:
        g.insert_document(doc["id"], doc["text"], doc.get("title"))
    goldens = {
        "nodes": {str(k): v["rank"] for k, v in g.nodes.items()},
        "edges": {str(eid): {"pair": list(magic_unpair(eid)),
                             "rank": e["rank"],
                             "doc_hash": e["doc_hash"]}
                  for eid, e in g.edges.items()},
        "queries": {q: [{"id": r["id"], "rank": r["rank"],
                         "contributions": r["contributions"]}
                        for r in g.query_graph(q)]
                    for q in corpus["queries"]},
    }
    out = json.dumps(goldens, indent=2, sort_keys=True)
    if len(sys.argv) > 2:
        open(sys.argv[2], "w").write(out + "\n")
    else:
        print(out)

if __name__ == "__main__":
    main()
