use terraphim_automata::load_thesaurus_from_json;
use terraphim_rolegraph::{RoleGraph, magic_pair, magic_unpair};
use terraphim_types::{Document, NormalizedTerm, NormalizedTermValue, RoleName};
use wasm_bindgen::prelude::*;

#[wasm_bindgen(start)]
pub fn init() {
    console_error_panic_hook::set_once();
    wasm_logger::init(wasm_logger::Config::default());
    log::info!("Terraphim RoleGraph WASM bindings initialized");
}

/// Live `terraphim_rolegraph` `RoleGraph` exposed to JavaScript.
///
/// All matching, indexing and scoring run the real Rust code paths —
/// Aho-Corasick `LeftmostLongest` matching with
/// `ascii_case_insensitive(true)`, `magic_pair` directed edges and
/// `node.rank + edge.rank + doc_hash` ranking.
#[wasm_bindgen]
pub struct RoleGraphWasm {
    inner: RoleGraph,
    /// Pattern index -> node id, mirroring `build_aho_corasick` which
    /// lays patterns out in thesaurus iteration order
    /// (`aho_corasick_values` itself is crate-private).
    pattern_ids: Vec<u64>,
}

fn pattern_ids_for(inner: &RoleGraph) -> Vec<u64> {
    inner.thesaurus.into_iter().map(|(_, nt)| nt.id).collect()
}

#[wasm_bindgen]
impl RoleGraphWasm {
    /// Build a graph from a thesaurus JSON string
    /// (`{"name": ..., "data": {synonym: {id, nterm}}}`).
    #[wasm_bindgen(constructor)]
    pub fn new(thesaurus_json: &str) -> Result<RoleGraphWasm, JsValue> {
        let thesaurus = load_thesaurus_from_json(thesaurus_json)
            .map_err(|e| JsValue::from_str(&format!("thesaurus: {e}")))?;
        let inner = RoleGraph::new_sync(RoleName::new("explainer"), thesaurus)
            .map_err(|e| JsValue::from_str(&format!("rolegraph: {e}")))?;
        let pattern_ids = pattern_ids_for(&inner);
        Ok(RoleGraphWasm { inner, pattern_ids })
    }

    /// Index a document (title + body are matched, mirroring
    /// `Document::to_string()`). Returns JSON: ordered matched node ids.
    pub fn insert_document(
        &mut self,
        doc_id: &str,
        title: &str,
        body: &str,
    ) -> Result<String, JsValue> {
        let doc = Document {
            id: doc_id.to_string(),
            title: title.to_string(),
            body: body.to_string(),
            ..Default::default()
        };
        let matched = self.inner.find_matching_node_ids(&doc.to_string());
        self.inner.insert_document(doc_id, doc);
        serde_json::to_string(&matched)
            .map_err(|e| JsValue::from_str(&format!("serialise: {e}")))
    }

    pub fn remove_document(&mut self, doc_id: &str) -> bool {
        self.inner.remove_document(doc_id)
    }

    /// All LeftmostLongest matches with byte spans:
    /// `[{id, nterm, start, end}]`.
    pub fn find_matches(&self, text: &str) -> Result<String, JsValue> {
        let out: Vec<serde_json::Value> = self
            .inner
            .ac
            .find_iter(text)
            .map(|m| {
                let id = self.pattern_ids[m.pattern()];
                let nterm = self
                    .inner
                    .ac_reverse_nterm
                    .get(&id)
                    .map(|v| v.to_string())
                    .unwrap_or_default();
                serde_json::json!({
                    "id": id,
                    "nterm": nterm,
                    "start": m.start(),
                    "end": m.end(),
                })
            })
            .collect();
        serde_json::to_string(&out).map_err(|e| JsValue::from_str(&format!("serialise: {e}")))
    }

    /// Ordered matched node ids only (`[u64]`).
    pub fn find_node_ids(&self, text: &str) -> Result<String, JsValue> {
        serde_json::to_string(&self.inner.find_matching_node_ids(text))
            .map_err(|e| JsValue::from_str(&format!("serialise: {e}")))
    }

    /// Ranked results plus per-(node, edge) contribution ledger.
    /// Ranks come from `query_graph` verbatim; contributions are
    /// reconstructed from the public graph state under the same rule.
    pub fn query(&self, q: &str) -> Result<String, JsValue> {
        let results = self
            .inner
            .query_graph(q, None, None)
            .map_err(|e| JsValue::from_str(&format!("query: {e}")))?;
        let ser = self.inner.to_serializable();
        let qids = self.inner.find_matching_node_ids(q);

        let out: Vec<serde_json::Value> = results
            .into_iter()
            .map(|(doc_id, idx)| {
                let mut contributions = vec![];
                for &nid in &qids {
                    let Some(node) = ser.nodes.get(&nid) else {
                        continue;
                    };
                    for eid in &node.connected_with {
                        let Some(edge) = ser.edges.get(eid) else {
                            continue;
                        };
                        if let Some(doc_rank) = edge.doc_hash.get(&doc_id) {
                            let (a, b) = magic_unpair(*eid);
                            contributions.push(serde_json::json!({
                                "node_id": nid,
                                "nterm": ser
                                    .ac_reverse_nterm
                                    .get(&nid)
                                    .map(|v| v.to_string())
                                    .unwrap_or_default(),
                                "node_rank": node.rank,
                                "edge_id": eid,
                                "pair": [a, b],
                                "edge_rank": edge.rank,
                                "doc_rank": doc_rank,
                                "total": node.rank + edge.rank + doc_rank,
                            }));
                        }
                    }
                }
                contributions.sort_by_key(|c| {
                    (
                        u64::MAX - c["total"].as_u64().unwrap_or(0),
                        c["edge_id"].as_u64().unwrap_or(0),
                    )
                });
                serde_json::json!({
                    "doc": doc_id,
                    "rank": idx.rank,
                    "contributions": contributions,
                })
            })
            .collect();
        serde_json::to_string(&out).map_err(|e| JsValue::from_str(&format!("serialise: {e}")))
    }

    /// `{nodes, edges, documents, thesaurus_terms}`
    pub fn stats(&self) -> Result<String, JsValue> {
        serde_json::to_string(&serde_json::json!({
            "nodes": self.inner.get_node_count(),
            "edges": self.inner.get_edge_count(),
            "documents": self.inner.get_document_count(),
            "thesaurus_terms": self.inner.thesaurus.len(),
        }))
        .map_err(|e| JsValue::from_str(&format!("serialise: {e}")))
    }

    /// Full graph snapshot for rendering:
    /// `{nodes: [{id, rank}], edges: [{id, a, b, rank, doc_hash}]}`.
    pub fn snapshot(&self) -> Result<String, JsValue> {
        let ser = self.inner.to_serializable();
        let nodes: Vec<_> = ser
            .nodes
            .values()
            .map(|n| serde_json::json!({"id": n.id, "rank": n.rank}))
            .collect();
        let edges: Vec<_> = ser
            .edges
            .values()
            .map(|e| {
                let (a, b) = magic_unpair(e.id);
                serde_json::json!({
                    "id": e.id,
                    "a": a,
                    "b": b,
                    "rank": e.rank,
                    "doc_hash": e.doc_hash,
                })
            })
            .collect();
        serde_json::to_string(&serde_json::json!({"nodes": nodes, "edges": edges}))
            .map_err(|e| JsValue::from_str(&format!("serialise: {e}")))
    }

    /// `{node_id: nterm}` display map.
    pub fn nterms(&self) -> Result<String, JsValue> {
        let map: std::collections::BTreeMap<String, String> = self
            .inner
            .ac_reverse_nterm
            .iter()
            .map(|(id, v)| (id.to_string(), v.to_string()))
            .collect();
        serde_json::to_string(&map).map_err(|e| JsValue::from_str(&format!("serialise: {e}")))
    }

    /// Add a synonym under an existing concept and rebuild the
    /// automaton — the real `rebuild_automata` path. Rebuild cost is
    /// measured caller-side.
    pub fn add_synonym(
        &mut self,
        synonym: &str,
        concept_id: u64,
        nterm: &str,
    ) -> Result<(), JsValue> {
        self.inner.thesaurus.insert(
            NormalizedTermValue::new(synonym.to_string()),
            NormalizedTerm::new(concept_id, NormalizedTermValue::new(nterm.to_string())),
        );
        self.inner
            .rebuild_automata()
            .map_err(|e| JsValue::from_str(&format!("rebuild: {e}")))?;
        self.pattern_ids = pattern_ids_for(&self.inner);
        Ok(())
    }
}

/// Cantor pairing used for edge ids — exported so the renderer can
/// map (a, b) pairs to edge ids without re-implementing it.
#[wasm_bindgen]
pub fn magic_pair_js(x: u64, y: u64) -> u64 {
    magic_pair(x, y)
}

#[wasm_bindgen]
pub fn magic_unpair_js(z: u64) -> Vec<u64> {
    let (a, b) = magic_unpair(z);
    vec![a, b]
}

#[wasm_bindgen]
pub fn version() -> String {
    format!("terraphim_rolegraph v{}", env!("CARGO_PKG_VERSION"))
}
