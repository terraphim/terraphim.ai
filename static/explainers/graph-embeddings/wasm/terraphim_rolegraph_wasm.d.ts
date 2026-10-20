/* tslint:disable */
/* eslint-disable */

/**
 * Live `terraphim_rolegraph` `RoleGraph` exposed to JavaScript.
 *
 * All matching, indexing and scoring run the real Rust code paths —
 * Aho-Corasick `LeftmostLongest` matching with
 * `ascii_case_insensitive(true)`, `magic_pair` directed edges and
 * `node.rank + edge.rank + doc_hash` ranking.
 */
export class RoleGraphWasm {
    free(): void;
    [Symbol.dispose](): void;
    /**
     * Add a synonym under an existing concept and rebuild the
     * automaton — the real `rebuild_automata` path. Rebuild cost is
     * measured caller-side.
     */
    add_synonym(synonym: string, concept_id: bigint, nterm: string): void;
    /**
     * All LeftmostLongest matches with byte spans:
     * `[{id, nterm, start, end}]`.
     */
    find_matches(text: string): string;
    /**
     * Ordered matched node ids only (`[u64]`).
     */
    find_node_ids(text: string): string;
    /**
     * Index a document (title + body are matched, mirroring
     * `Document::to_string()`). Returns JSON: ordered matched node ids.
     */
    insert_document(doc_id: string, title: string, body: string): string;
    /**
     * Build a graph from a thesaurus JSON string
     * (`{"name": ..., "data": {synonym: {id, nterm}}}`).
     */
    constructor(thesaurus_json: string);
    /**
     * `{node_id: nterm}` display map.
     */
    nterms(): string;
    /**
     * Ranked results plus per-(node, edge) contribution ledger.
     * Ranks come from `query_graph` verbatim; contributions are
     * reconstructed from the public graph state under the same rule.
     */
    query(q: string): string;
    remove_document(doc_id: string): boolean;
    /**
     * Full graph snapshot for rendering:
     * `{nodes: [{id, rank}], edges: [{id, a, b, rank, doc_hash}]}`.
     */
    snapshot(): string;
    /**
     * `{nodes, edges, documents, thesaurus_terms}`
     */
    stats(): string;
}

export function init(): void;

/**
 * Cantor pairing used for edge ids — exported so the renderer can
 * map (a, b) pairs to edge ids without re-implementing it.
 */
export function magic_pair_js(x: bigint, y: bigint): bigint;

export function magic_unpair_js(z: bigint): BigUint64Array;

export function version(): string;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
    readonly memory: WebAssembly.Memory;
    readonly __wbg_rolegraphwasm_free: (a: number, b: number) => void;
    readonly init: () => void;
    readonly magic_pair_js: (a: bigint, b: bigint) => bigint;
    readonly magic_unpair_js: (a: bigint) => [number, number];
    readonly rolegraphwasm_add_synonym: (a: number, b: number, c: number, d: bigint, e: number, f: number) => [number, number];
    readonly rolegraphwasm_find_matches: (a: number, b: number, c: number) => [number, number, number, number];
    readonly rolegraphwasm_find_node_ids: (a: number, b: number, c: number) => [number, number, number, number];
    readonly rolegraphwasm_insert_document: (a: number, b: number, c: number, d: number, e: number, f: number, g: number) => [number, number, number, number];
    readonly rolegraphwasm_new: (a: number, b: number) => [number, number, number];
    readonly rolegraphwasm_nterms: (a: number) => [number, number, number, number];
    readonly rolegraphwasm_query: (a: number, b: number, c: number) => [number, number, number, number];
    readonly rolegraphwasm_remove_document: (a: number, b: number, c: number) => number;
    readonly rolegraphwasm_snapshot: (a: number) => [number, number, number, number];
    readonly rolegraphwasm_stats: (a: number) => [number, number, number, number];
    readonly version: () => [number, number];
    readonly __wbindgen_free: (a: number, b: number, c: number) => void;
    readonly __wbindgen_exn_store: (a: number) => void;
    readonly __externref_table_alloc: () => number;
    readonly __wbindgen_externrefs: WebAssembly.Table;
    readonly __wbindgen_malloc: (a: number, b: number) => number;
    readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
    readonly __externref_table_dealloc: (a: number) => void;
    readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;

/**
 * Instantiates the given `module`, which can either be bytes or
 * a precompiled `WebAssembly.Module`.
 *
 * @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
 *
 * @returns {InitOutput}
 */
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
 * If `module_or_path` is {RequestInfo} or {URL}, makes a request and
 * for everything else, calls `WebAssembly.instantiate` directly.
 *
 * @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
 *
 * @returns {Promise<InitOutput>}
 */
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
