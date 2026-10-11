/**
 * Browser binding with one owned session per instance; no DOM dependency.
 */
export class TerraphimHostSession {
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        TerraphimHostSessionFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_terraphimhostsession_free(ptr, 0);
    }
    /**
     * Commit exact host output after the native text transaction.
     * @param {number} id
     * @param {number} revision
     * @param {string} source
     * @returns {string}
     */
    acknowledge(id, revision, source) {
        let deferred3_0;
        let deferred3_1;
        try {
            const ptr0 = passStringToWasm0(source, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len0 = WASM_VECTOR_LEN;
            const ret = wasm.terraphimhostsession_acknowledge(this.__wbg_ptr, id, revision, ptr0, len0);
            var ptr2 = ret[0];
            var len2 = ret[1];
            if (ret[3]) {
                ptr2 = 0; len2 = 0;
                throw takeFromExternrefTable0(ret[2]);
            }
            deferred3_0 = ptr2;
            deferred3_1 = len2;
            return getStringFromWasm0(ptr2, len2);
        } finally {
            wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
        }
    }
    /**
     * Open a host resource with exact source and revision.
     * @param {string} resource
     * @param {string} session
     * @param {number} revision
     * @param {string} source
     */
    constructor(resource, session, revision, source) {
        const ptr0 = passStringToWasm0(resource, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(session, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ptr2 = passStringToWasm0(source, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len2 = WASM_VECTOR_LEN;
        const ret = wasm.terraphimhostsession_new(ptr0, len0, ptr1, len1, revision, ptr2, len2);
        if (ret[2]) {
            throw takeFromExternrefTable0(ret[1]);
        }
        this.__wbg_ptr = ret[0];
        TerraphimHostSessionFinalization.register(this, this.__wbg_ptr, this);
        return this;
    }
    /**
     * Stage a protocol command; committed source stays unchanged.
     * @param {string} message
     * @returns {string}
     */
    propose(message) {
        let deferred3_0;
        let deferred3_1;
        try {
            const ptr0 = passStringToWasm0(message, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len0 = WASM_VECTOR_LEN;
            const ret = wasm.terraphimhostsession_propose(this.__wbg_ptr, ptr0, len0);
            var ptr2 = ret[0];
            var len2 = ret[1];
            if (ret[3]) {
                ptr2 = 0; len2 = 0;
                throw takeFromExternrefTable0(ret[2]);
            }
            deferred3_0 = ptr2;
            deferred3_1 = len2;
            return getStringFromWasm0(ptr2, len2);
        } finally {
            wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
        }
    }
    /**
     * Invalidate a named staged operation.
     * @param {number} id
     */
    reject(id) {
        const ret = wasm.terraphimhostsession_reject(this.__wbg_ptr, id);
        if (ret[1]) {
            throw takeFromExternrefTable0(ret[0]);
        }
    }
    /**
     * Current source and render projection, encoded as protocol JSON.
     * @returns {string}
     */
    snapshot() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.terraphimhostsession_snapshot(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * Adopt actual external edits or native undo/redo.
     * @param {number} revision
     * @param {string} source
     * @returns {string}
     */
    synchronize(revision, source) {
        let deferred3_0;
        let deferred3_1;
        try {
            const ptr0 = passStringToWasm0(source, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len0 = WASM_VECTOR_LEN;
            const ret = wasm.terraphimhostsession_synchronize(this.__wbg_ptr, revision, ptr0, len0);
            var ptr2 = ret[0];
            var len2 = ret[1];
            if (ret[3]) {
                ptr2 = 0; len2 = 0;
                throw takeFromExternrefTable0(ret[2]);
            }
            deferred3_0 = ptr2;
            deferred3_1 = len2;
            return getStringFromWasm0(ptr2, len2);
        } finally {
            wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
        }
    }
    /**
     * Query committed authored KG synonyms, encoded as JSON.
     * @param {string} span_id
     * @param {string} text
     * @returns {string}
     */
    synonyms_for(span_id, text) {
        let deferred3_0;
        let deferred3_1;
        try {
            const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len0 = WASM_VECTOR_LEN;
            const ptr1 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            const ret = wasm.terraphimhostsession_synonyms_for(this.__wbg_ptr, ptr0, len0, ptr1, len1);
            deferred3_0 = ret[0];
            deferred3_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
        }
    }
}
if (Symbol.dispose) TerraphimHostSession.prototype[Symbol.dispose] = TerraphimHostSession.prototype.free;

/**
 * @param {string} token
 * @returns {any}
 */
export function abort_document_history_transaction(token) {
    const ptr0 = passStringToWasm0(token, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.abort_document_history_transaction(ptr0, len0);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Appends alternative `text` from `source` to span `span_id`. Returns the
 * change, or `null` if the span already has that text; throws on error.
 * @param {string} span_id
 * @param {string} text
 * @param {string} source
 * @returns {any}
 */
export function alt_add(span_id, text, source) {
    const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ptr2 = passStringToWasm0(source, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len2 = WASM_VECTOR_LEN;
    const ret = wasm.alt_add(ptr0, len0, ptr1, len1, ptr2, len2);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * "AI alternatives for selection" through every provider, in the shape of
 * the #10 panel operations so `MarkdownEditor.alternativeOp(
 * 'append_alternatives', start, end, supplied)` records it as one undo step.
 * `supplied` is the JSON the host's awaited providers produced (see
 * [`parse_supplied`]); `""` for none. Returns the change, `null` when
 * nothing new was left to add, and throws, changing nothing, when there is
 * nothing to offer for the selection or another span overlaps it.
 * @param {number} start
 * @param {number} end
 * @param {string} supplied
 * @returns {any}
 */
export function alt_append_alternatives(start, end, supplied) {
    const ptr0 = passStringToWasm0(supplied, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.alt_append_alternatives(start, end, ptr0, len0);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Creates a span of `kind` (`"word"`, `"sentence"`, `"paragraph"`) over
 * `start..end` (UTF-16) with its first alternative `text` from `source`
 * (`"human"` or `"ai"`). Returns the change (see [`AltChange::to_json`]);
 * throws, changing nothing, for an invalid or overlapping range, empty text
 * or text equal to the original.
 * @param {string} kind
 * @param {number} start
 * @param {number} end
 * @param {string} text
 * @param {string} source
 * @returns {any}
 */
export function alt_create_span(kind, start, end, text, source) {
    const ptr0 = passStringToWasm0(kind, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ptr2 = passStringToWasm0(source, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len2 = WASM_VECTOR_LEN;
    const ret = wasm.alt_create_span(ptr0, len0, start, end, ptr1, len1, ptr2, len2);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Replaces the text of alternative `index` of span `span_id`. Returns the
 * change (with the body edit when it was the active one), or `null` when the
 * text is unchanged; throws on error.
 * @param {string} span_id
 * @param {number} index
 * @param {string} text
 * @returns {any}
 */
export function alt_edit(span_id, index, text) {
    const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ret = wasm.alt_edit(ptr0, len0, index, ptr1, len1);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * "AI alternatives for selection" (R-8.6, see [`kg_append`]), in the shape
 * of the #10 panel operations so `MarkdownEditor.alternativeOp('kg_append',
 * start, end)` records it as one undo step: returns the change (see
 * `AltChange::to_json`), `null` when the span already offers every synonym,
 * and throws, changing nothing, when there is no KG term at the selection
 * or another span overlaps it.
 * @param {number} start
 * @param {number} end
 * @returns {any}
 */
export function alt_kg_append(start, end) {
    const ret = wasm.alt_kg_append(start, end);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Moves alternative `from` of span `span_id` to position `to`. Returns the
 * change, or `null` when `from == to`; throws on error.
 * @param {string} span_id
 * @param {number} from
 * @param {number} to
 * @returns {any}
 */
export function alt_move(span_id, from, to) {
    const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.alt_move(ptr0, len0, from, to);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Removes alternative `index` of span `span_id`. Returns the change (its
 * `after` is `null` when the span was removed); throws on error.
 * @param {string} span_id
 * @param {number} index
 * @returns {any}
 */
export function alt_remove(span_id, index) {
    const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.alt_remove(ptr0, len0, index);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Replays a recorded panel operation (see [`DocumentSession::alt_restore`]):
 * `target_json` is the span snapshot to put back, or `"null"` to leave the
 * span out. Returns `{ detached, reattached, setAside, warning, notice, ... }`;
 * throws, changing nothing, when the replay does not fit.
 * @param {string} span_id
 * @param {string} target_json
 * @param {number} start
 * @param {number} deleted_len
 * @param {string} inserted
 * @returns {any}
 */
export function alt_restore(span_id, target_json, start, deleted_len, inserted) {
    const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(target_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ptr2 = passStringToWasm0(inserted, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len2 = WASM_VECTOR_LEN;
    const ret = wasm.alt_restore(ptr0, len0, ptr1, len1, start, deleted_len, ptr2, len2);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * The provider ids in the order they are asked, as a JSON array.
 * @returns {any}
 */
export function alternatives_provider_ids() {
    const ret = wasm.alternatives_provider_ids();
    return ret;
}

/**
 * Registers a host provider `id` (default model `model`) after the ones
 * already there, so its answers can be supplied to
 * [`alt_append_alternatives`]. Re-registering keeps its place; the
 * `thesaurus` id is reserved and throws.
 * @param {string} id
 * @param {string} model
 */
export function alternatives_provider_register(id, model) {
    const ptr0 = passStringToWasm0(id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(model, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ret = wasm.alternatives_provider_register(ptr0, len0, ptr1, len1);
    if (ret[1]) {
        throw takeFromExternrefTable0(ret[0]);
    }
}

/**
 * Removes the provider `id`; `false` when there was none.
 * @param {string} id
 * @returns {boolean}
 */
export function alternatives_provider_unregister(id) {
    const ptr0 = passStringToWasm0(id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.alternatives_provider_unregister(ptr0, len0);
    return ret !== 0;
}

/**
 * Mirrors a surface edit (`start`, `deletedLength`, `insertedText`, UTF-16)
 * in the model. Returns `{ detached, detachedGhosts, reattached, setAside, warning, notice }`; throws
 * if the edit does not fit the model, in which case call
 * [`sync_document_body`].
 * @param {number} start
 * @param {number} deleted_len
 * @param {string} inserted
 * @returns {any}
 */
export function apply_edit(start, deleted_len, inserted) {
    const ptr0 = passStringToWasm0(inserted, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.apply_edit(start, deleted_len, ptr0, len0);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * @param {string} expected_body
 * @param {string} target_body
 * @param {string} operations_json
 * @returns {any}
 */
export function begin_document_history_replay(expected_body, target_body, operations_json) {
    const ptr0 = passStringToWasm0(expected_body, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(target_body, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ptr2 = passStringToWasm0(operations_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len2 = WASM_VECTOR_LEN;
    const ret = wasm.begin_document_history_replay(ptr0, len0, ptr1, len1, ptr2, len2);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * @param {string} expected_body
 * @param {string} level
 * @param {string} kept_json
 * @returns {any}
 */
export function begin_trim_ghost_transaction(expected_body, level, kept_json) {
    const ptr0 = passStringToWasm0(expected_body, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(level, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ptr2 = passStringToWasm0(kept_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len2 = WASM_VECTOR_LEN;
    const ret = wasm.begin_trim_ghost_transaction(ptr0, len0, ptr1, len1, ptr2, len2);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * `{ spans, ghosts, overflow, setAside: { spans, ghosts }, preservedBlock,
 * kg }` of the current document, in UTF-16 offsets. `kg` holds the derived
 * knowledge-graph spans (issue #13, see [`crate::kg::KgSpan::to_json`]);
 * they are never saved.
 * @returns {any}
 */
export function document_annotations() {
    const ret = wasm.document_annotations();
    return ret;
}

/**
 * The body as the model holds it (should always equal the surface text).
 * @returns {string}
 */
export function document_body() {
    let deferred1_0;
    let deferred1_1;
    try {
        const ret = wasm.document_body();
        deferred1_0 = ret[0];
        deferred1_1 = ret[1];
        return getStringFromWasm0(ret[0], ret[1]);
    } finally {
        wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
    }
}

/**
 * `{ words, chars }` of the body, ghosted text included.
 * @returns {any}
 */
export function document_counts() {
    const ret = wasm.document_counts();
    return ret;
}

/**
 * The overflow (stash) text of the current document.
 * @returns {string}
 */
export function document_overflow() {
    let deferred1_0;
    let deferred1_1;
    try {
        const ret = wasm.document_overflow();
        deferred1_0 = ret[0];
        deferred1_1 = ret[1];
        return getStringFromWasm0(ret[0], ret[1]);
    } finally {
        wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
    }
}

/**
 * Query the current browser document's scoped authored KG synonym concept.
 * @param {string} span_id
 * @param {string} text
 * @returns {string}
 */
export function document_synonyms(span_id, text) {
    let deferred3_0;
    let deferred3_1;
    try {
        const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ret = wasm.document_synonyms(ptr0, len0, ptr1, len1);
        deferred3_0 = ret[0];
        deferred3_1 = ret[1];
        return getStringFromWasm0(ret[0], ret[1]);
    } finally {
        wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
    }
}

/**
 * The current document as clean Markdown: active alternatives, no ghosted
 * text, no overflow, no block.
 * @returns {string}
 */
export function export_document() {
    let deferred1_0;
    let deferred1_1;
    try {
        const ret = wasm.export_document();
        deferred1_0 = ret[0];
        deferred1_1 = ret[1];
        return getStringFromWasm0(ret[0], ret[1]);
    } finally {
        wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
    }
}

/**
 * Downloadable Terraphim graph of the current document's authored synonyms.
 *
 * # Errors
 * Refuses malformed annotations and ambiguous cross-group terms.
 * @returns {string}
 */
export function export_knowledge_graph() {
    let deferred2_0;
    let deferred2_1;
    try {
        const ret = wasm.export_knowledge_graph();
        var ptr1 = ret[0];
        var len1 = ret[1];
        if (ret[3]) {
            ptr1 = 0; len1 = 0;
            throw takeFromExternrefTable0(ret[2]);
        }
        deferred2_0 = ptr1;
        deferred2_1 = len1;
        return getStringFromWasm0(ptr1, len1);
    } finally {
        wasm.__wbindgen_free(deferred2_0, deferred2_1, 1);
    }
}

/**
 * @param {string} token
 * @returns {any}
 */
export function finish_document_history_transaction(token) {
    const ptr0 = passStringToWasm0(token, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.finish_document_history_transaction(ptr0, len0);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Render a pending (debounced) preview immediately.
 *
 * Call this before reading the preview for save, export or tests. Returns
 * `true` if a render was pending and has now run, `false` if the preview was
 * already up to date (or no editor is initialised). From JavaScript in the
 * Trunk build this is `window.wasmBindings.flush_preview()`.
 * @returns {boolean}
 */
export function flush_preview() {
    const ret = wasm.flush_preview();
    return ret !== 0;
}

/**
 * Ghosts `start..end` (UTF-16 offsets into the body) in the current
 * document. Returns `{ ok: true, id, annotations }` with the updated
 * annotations (as [`document_annotations`]), or `{ ok: false, error, kind }`
 * with the document unchanged. Never throws.
 * @param {number} start
 * @param {number} end
 * @returns {any}
 */
export function ghost_range(start, end) {
    const ret = wasm.ghost_range(start, end);
    return ret;
}

/**
 * LF source for a DOM presentation, with rebased annotations and untouched
 * malformed block bytes. Native persisted source remains owned by its host.
 *
 * # Errors
 * Refuses overflowing annotation coordinates.
 * @param {string} source
 * @returns {string}
 */
export function host_presentation_source(source) {
    let deferred3_0;
    let deferred3_1;
    try {
        const ptr0 = passStringToWasm0(source, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.host_presentation_source(ptr0, len0);
        var ptr2 = ret[0];
        var len2 = ret[1];
        if (ret[3]) {
            ptr2 = 0; len2 = 0;
            throw takeFromExternrefTable0(ret[2]);
        }
        deferred3_0 = ptr2;
        deferred3_1 = len2;
        return getStringFromWasm0(ptr2, len2);
    } finally {
        wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
    }
}

/**
 * Forgets the thesaurus: no KG spans until the next load.
 */
export function kg_clear_thesaurus() {
    wasm.kg_clear_thesaurus();
}

/**
 * Publish a prepared role and return its summary as JSON text.
 * @param {string} token
 * @returns {string}
 */
export function kg_commit_prepared_role(token) {
    let deferred3_0;
    let deferred3_1;
    try {
        const ptr0 = passStringToWasm0(token, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.kg_commit_prepared_role(ptr0, len0);
        var ptr2 = ret[0];
        var len2 = ret[1];
        if (ret[3]) {
            ptr2 = 0; len2 = 0;
            throw takeFromExternrefTable0(ret[2]);
        }
        deferred3_0 = ptr2;
        deferred3_1 = len2;
        return getStringFromWasm0(ptr2, len2);
    } finally {
        wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
    }
}

/**
 * Discard a prepared role; active state is untouched.
 * @param {string} token
 */
export function kg_discard_prepared_role(token) {
    const ptr0 = passStringToWasm0(token, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    wasm.kg_discard_prepared_role(ptr0, len0);
}

/**
 * The derived KG spans of the open document (see [`KgSpan::to_json`]).
 * `document_annotations` returns the same list as its `kg` field.
 * @returns {any}
 */
export function kg_document_spans() {
    const ret = wasm.kg_document_spans();
    return ret;
}

/**
 * Loads a thesaurus JSON for KG alternatives, replacing the current one.
 * Returns `{ name, concepts, skipped }`; throws (keeping the previous
 * thesaurus) if the JSON is not a thesaurus.
 * @param {string} json
 * @returns {any}
 */
export function kg_load_thesaurus(json) {
    const ptr0 = passStringToWasm0(json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.kg_load_thesaurus(ptr0, len0);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * The KG term at the selection `start..end` with its alternatives, or
 * `null` (see [`kg_lookup`]). Read-only.
 * @param {number} start
 * @param {number} end
 * @returns {any}
 */
export function kg_lookup_selection(start, end) {
    const ret = wasm.kg_lookup_selection(start, end);
    return ret;
}

/**
 * Prepare local role JSON without replacing the current KG engine.
 * @param {string} json
 * @returns {string}
 */
export function kg_prepare_role(json) {
    let deferred3_0;
    let deferred3_1;
    try {
        const ptr0 = passStringToWasm0(json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.kg_prepare_role(ptr0, len0);
        var ptr2 = ret[0];
        var len2 = ret[1];
        if (ret[3]) {
            ptr2 = 0; len2 = 0;
            throw takeFromExternrefTable0(ret[2]);
        }
        deferred3_0 = ptr2;
        deferred3_1 = len2;
        return getStringFromWasm0(ptr2, len2);
    } finally {
        wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
    }
}

/**
 * Read-only active role snapshot for the Worker coordinator.
 * @returns {string}
 */
export function kg_role_snapshot_json() {
    let deferred1_0;
    let deferred1_1;
    try {
        const ret = wasm.kg_role_snapshot_json();
        deferred1_0 = ret[0];
        deferred1_1 = ret[1];
        return getStringFromWasm0(ret[0], ret[1]);
    } finally {
        wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
    }
}

/**
 * Replace the single opt-in browser role observer; `None` unregisters it.
 * Called synchronously, with no arguments, only after successful load, clear,
 * or prepared commit. Read the authoritative snapshot inside the callback.
 * @param {Function | null} [listener]
 */
export function kg_set_role_change_listener(listener) {
    wasm.kg_set_role_change_listener(isLikeNone(listener) ? 0 : addToExternrefTable0(listener));
}

/**
 * Makes alternative `index` of KG span `span_id` the text. Returns the same
 * shape as `set_active_alternative` (`{ span, from, to, edit, range, ... }`,
 * `edit` the exact UTF-16 change made to the body, or `null`); throws,
 * changing nothing, for an unknown span, an invalid index or an edit that
 * would change a block span's text.
 * @param {string} span_id
 * @param {number} index
 * @returns {any}
 */
export function kg_swap_alternative(span_id, index) {
    const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.kg_swap_alternative(ptr0, len0, index);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * `[{ id, label }]` of the six Lab actions, in popover order.
 * @returns {any}
 */
export function lab_actions() {
    const ret = wasm.lab_actions();
    return ret;
}

/**
 * Runs Lab action `action` (an id from [`lab_actions`]) over the current
 * document body and returns `[{ kind, start, end, score, reason, proposal }]`
 * in UTF-16 offsets. Throws for an unknown action id. Never changes text.
 * @param {string} action
 * @returns {any}
 */
export function lab_mark(action) {
    const ptr0 = passStringToWasm0(action, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.lab_mark(ptr0, len0);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Render the editor markup into `root` with `initial` as the open document
 * and wire the live preview to the surface inside `root` (issue #77).
 *
 * This is the entry point of the embeddable wrapper; [`run`] uses it for
 * `#app`. Every lookup is scoped to `root`, so markup elsewhere on the page
 * is never touched. `root` gains the `te-app` class, which the Write_On
 * layout rules key on. There is one document session and one preview per
 * module instance, so mounting replaces the previous editor: one editor
 * per page (see docs/design/embedding.md).
 * @param {Element} root
 * @param {string} initial
 */
export function mount_editor(root, initial) {
    const ptr0 = passStringToWasm0(initial, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.mount_editor(root, ptr0, len0);
    if (ret[1]) {
        throw takeFromExternrefTable0(ret[0]);
    }
}

/**
 * Moves the body text `start..end` to `to` (UTF-16 code units; `to` is an
 * insertion point in the pre-move body, outside the range), carrying the
 * spans and ghosts inside the range. Returns
 * `{ detached, detachedGhosts, reattached, setAside, warning, notice }` like [`apply_edit`];
 * throws (changing nothing) if the range or destination is invalid or the
 * move would split a span or ghost.
 *
 * `MarkdownEditor.moveRange` calls this and then updates the editing surface
 * without mirroring the change through [`apply_edit`].
 * @param {number} start
 * @param {number} end
 * @param {number} to
 * @returns {any}
 */
export function move_document_range(start, end, to) {
    const ret = wasm.move_document_range(start, end, to);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Opens a `.md` source as the current document and returns
 * `{ body, warning, unresolved }`: put `body` on the editing surface and
 * show `warning` (a string or `null`) as a non-blocking notice.
 * @param {string} source
 * @returns {any}
 */
export function open_document(source) {
    const ptr0 = passStringToWasm0(source, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.open_document(ptr0, len0);
    return ret;
}

/**
 * The text a pull back (R-6.4, a copy) inserts at `at` (UTF-16) and where:
 * the overflow range `from..to` (UTF-16; when empty, the line at `from`),
 * separated as terraphim-lsp separates it. Returns `{ start, text }` and
 * changes nothing; throws when there is nothing to pull back or for an
 * invalid offset or range. `TeOverflowPanel.pullBack` inserts `text` at
 * `start` through the normal edit path.
 * @param {number} at
 * @param {number} from
 * @param {number} to
 * @returns {any}
 */
export function overflow_pull_back_text(at, from, to) {
    const ret = wasm.overflow_pull_back_text(at, from, to);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Synchronous model preflight for one issued receipt, before JS cursor/surface
 * movement. Whole mixed replay groups require controller-level clone preflight.
 * @param {string} change_json
 * @param {boolean} undo
 */
export function preflight_document_ghost_change(change_json, undo) {
    const ptr0 = passStringToWasm0(change_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.preflight_document_ghost_change(ptr0, len0, undo);
    if (ret[1]) {
        throw takeFromExternrefTable0(ret[0]);
    }
}

/**
 * Current preview debounce delay in milliseconds.
 * @returns {number}
 */
export function preview_delay() {
    const ret = wasm.preview_delay();
    return ret >>> 0;
}

/**
 * Whether a debounced preview render is scheduled but has not yet run.
 * @returns {boolean}
 */
export function preview_pending() {
    const ret = wasm.preview_pending();
    return ret !== 0;
}

/**
 * Number of preview renders triggered by edits since the last [`run`].
 * The initial render on load is part of the template and is not counted.
 * Intended for diagnostics and tests.
 * @returns {number}
 */
export function preview_render_count() {
    const ret = wasm.preview_render_count();
    return ret >>> 0;
}

/**
 * @param {string} token
 * @param {string} source
 * @returns {any}
 */
export function recover_document_history_transaction(token, source) {
    const ptr0 = passStringToWasm0(token, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(source, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ret = wasm.recover_document_history_transaction(ptr0, len0, ptr1, len1);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Convert Markdown to HTML with the `markdown` crate.
 *
 * Exported so that JavaScript (and the browser benchmarks) use exactly the
 * same conversion as the live preview.
 * @param {string} input
 * @returns {string}
 */
export function render_markdown(input) {
    let deferred3_0;
    let deferred3_1;
    try {
        const ptr0 = passStringToWasm0(input, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.render_markdown(ptr0, len0);
        var ptr2 = ret[0];
        var len2 = ret[1];
        if (ret[3]) {
            ptr2 = 0; len2 = 0;
            throw takeFromExternrefTable0(ret[2]);
        }
        deferred3_0 = ptr2;
        deferred3_1 = len2;
        return getStringFromWasm0(ptr2, len2);
    } finally {
        wasm.__wbindgen_free(deferred3_0, deferred3_1, 1);
    }
}

/**
 * Replays an issued receipt, never arbitrary promotion ranges. Protected
 * promotion is wired by Lab separately, not exposed as a JS bypass here.
 * @param {string} change_json
 * @param {boolean} undo
 * @returns {any}
 */
export function replay_document_ghost_change(change_json, undo) {
    const ptr0 = passStringToWasm0(change_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.replay_document_ghost_change(ptr0, len0, undo);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Replays a recorded overflow change `from` -> `to` (undo or redo of a
 * stash) onto the current overflow, keeping text typed in the panel since
 * (see [`rebase_overflow`]). Returns `{ ok: true, overflow, applied }`
 * (`applied: false` when an undo could not find the stashed text intact at
 * its recorded position and left the overflow unchanged) or
 * `{ ok: false, error, kind }`. Never throws.
 * @param {string} from
 * @param {string} to
 * @returns {any}
 */
export function replay_document_overflow(from, to) {
    const ptr0 = passStringToWasm0(from, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(to, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ret = wasm.replay_document_overflow(ptr0, len0, ptr1, len1);
    return ret;
}

/**
 * Revives `start..end` (UTF-16 offsets into the body) in the current
 * document. Returns `{ ok: true, changed, annotations }`, or
 * `{ ok: false, error, kind }` with the document unchanged. Never throws.
 * @param {number} start
 * @param {number} end
 * @returns {any}
 */
export function revive_range(start, end) {
    const ret = wasm.revive_range(start, end);
    return ret;
}

/**
 * Render the full-page editor, with the welcome text, into `#app`.
 *
 * Errors when the page has no element with id `app`.
 */
export function run() {
    const ret = wasm.run();
    if (ret[1]) {
        throw takeFromExternrefTable0(ret[0]);
    }
}

/**
 * The current document as `.md` text: body plus annotation block, set-aside
 * annotations included.
 * @returns {string}
 */
export function save_document() {
    let deferred1_0;
    let deferred1_1;
    try {
        const ret = wasm.save_document();
        deferred1_0 = ret[0];
        deferred1_1 = ret[1];
        return getStringFromWasm0(ret[0], ret[1]);
    } finally {
        wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
    }
}

/**
 * Makes alternative `index` of span `span_id` active (R-2.4): the span's
 * text is swapped and a preceding "a"/"an" fixed up (R-2.6) in the model.
 * Returns `{ span, from, to, edit, range, detached, reattached, setAside,
 * warning, notice }`, where `edit` (`{ start, deletedLength, deletedText,
 * insertedText }` in UTF-16 code units, or `null` when `index` was already
 * active) is the exact change made to the body and `range` (`{ start, end }`)
 * is the span's text afterwards. Throws, changing nothing,
 * for an unknown span, an invalid index or a stale anchor.
 *
 * `MarkdownEditor.swapAlternative` calls this and then applies `edit` to
 * the editing surface without mirroring it through [`apply_edit`].
 * @param {string} span_id
 * @param {number} index
 * @returns {any}
 */
export function set_active_alternative(span_id, index) {
    const ptr0 = passStringToWasm0(span_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.set_active_alternative(ptr0, len0, index);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Replaces the overflow text (what the Overflow panel holds). Returns
 * `{ ok: true, overflow }`, or `{ ok: false, error, kind }` (kind
 * `"preserved-block"`) with nothing changed. Never throws.
 * @param {string} text
 * @returns {any}
 */
export function set_document_overflow(text) {
    const ptr0 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.set_document_overflow(ptr0, len0);
    return ret;
}

/**
 * Set the preview debounce delay in milliseconds; `0` renders synchronously
 * on every `input`. Applies to renders scheduled after the call; a render
 * already pending keeps its original deadline. [`run`] resets the delay to
 * [`DEFAULT_PREVIEW_DELAY_MS`]. Does nothing if no editor is initialised.
 * @param {number} ms
 */
export function set_preview_delay(ms) {
    wasm.set_preview_delay(ms);
}

/**
 * Module start: render the full-page editor into `#app` (the Trunk build).
 *
 * Does nothing on a page that embeds the editor through the
 * `TeraphimEditor` wrapper (`public/js/terraphim-editor.js`): the wrapper
 * sets `window.TE_EMBED = true` before it instantiates the module and then
 * calls [`mount_editor`] on its own container, so a host page that happens
 * to have an element with id `app` is never taken over. A page without
 * `#app` is also left alone, so instantiating the module never fails for
 * want of one (a failing start function would reject the glue's `init()`).
 */
export function start() {
    wasm.start();
}

/**
 * Stashes the body text `start..end` (UTF-16) in the overflow: removed
 * from the body through the normal edit path and appended to the overflow
 * (R-6.3). Returns `{ edit, overflow: { before, after }, detached,
 * detachedGhosts, reattached, setAside, warning, notice }`; throws,
 * changing nothing, for an empty or invalid range or while a malformed
 * block is preserved.
 *
 * `MarkdownEditor.stashRange` calls this and then applies `edit` to the
 * editing surface without mirroring it through [`apply_edit`].
 * @param {number} start
 * @param {number} end
 * @returns {any}
 */
export function stash_document_range(start, end) {
    const ret = wasm.stash_document_range(start, end);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Replaces the model body with `text` if it differs and re-anchors; returns
 * `{ changed, unresolved, notice }` (`notice` as for [`apply_edit`]).
 * @param {string} text
 * @returns {any}
 */
export function sync_document_body(text) {
    const ptr0 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.sync_document_body(ptr0, len0);
    return ret;
}

/**
 * Explicit-selection kind inference through shared Rust boundaries/counter.
 * @param {string} text
 * @returns {string}
 */
export function text_infer_kind(text) {
    let deferred2_0;
    let deferred2_1;
    try {
        const ptr0 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.text_infer_kind(ptr0, len0);
        deferred2_0 = ret[0];
        deferred2_1 = ret[1];
        return getStringFromWasm0(ret[0], ret[1]);
    } finally {
        wasm.__wbindgen_free(deferred2_0, deferred2_1, 1);
    }
}

/**
 * Shared automatic targeting; coordinates and return object are UTF-16.
 * @param {string} text
 * @param {number} utf16
 * @param {string} kind
 * @returns {any}
 */
export function text_range_at(text, utf16, kind) {
    const ptr0 = passStringToWasm0(text, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(kind, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ret = wasm.text_range_at(ptr0, len0, utf16, ptr1, len1);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * The typed edits "Make the cuts" applies at `level` with `kept` kept:
 * `{ text, edits: [{ start, end, insert, kind }] }` on the current body's
 * UTF-16 offsets. Throws for a stale plan; never changes text itself.
 * @param {string} level
 * @param {string} kept
 * @returns {any}
 */
export function trim_make_cuts(level, kept) {
    const ptr0 = passStringToWasm0(level, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(kept, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ret = wasm.trim_make_cuts(ptr0, len0, ptr1, len1);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Computes the trim plan for the current document body and returns
 * `{ totalWords, levels, cuts }` (UTF-16 offsets). Align the model with the
 * surface first. Never changes text.
 * @returns {any}
 */
export function trim_plan_json() {
    const ret = wasm.trim_plan_json();
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * The status card for trim level `level` (`"slight"`, ...) with the cut
 * ids in `kept` (a JSON array) kept, plus the active pieces to fade. Throws
 * for an unknown level, bad ids, no plan or a stale plan.
 * @param {string} level
 * @param {string} kept
 * @returns {any}
 */
export function trim_status(level, kept) {
    const ptr0 = passStringToWasm0(level, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ptr1 = passStringToWasm0(kept, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len1 = WASM_VECTOR_LEN;
    const ret = wasm.trim_status(ptr0, len0, ptr1, len1);
    if (ret[2]) {
        throw takeFromExternrefTable0(ret[1]);
    }
    return takeFromExternrefTable0(ret[0]);
}

/**
 * Forget the editor wired by the last [`mount_editor`]: cancel a pending
 * preview render and drop the references to its nodes, so a destroyed
 * embed leaves no timer behind. The surface's `input` listener stays on the
 * (removed) surface and does nothing once the state is gone.
 */
export function unmount_editor() {
    wasm.unmount_editor();
}
function __wbg_get_imports() {
    const import0 = {
        __proto__: null,
        __wbg___wbindgen_is_falsy_16bd49b68658263e: function(arg0) {
            const ret = !arg0;
            return ret;
        },
        __wbg___wbindgen_is_undefined_8865fb403f8fe9d8: function(arg0) {
            const ret = arg0 === undefined;
            return ret;
        },
        __wbg___wbindgen_rethrow_cb2e88c6b2a16733: function(arg0) {
            throw arg0;
        },
        __wbg___wbindgen_throw_41e9ee4f547fc59a: function(arg0, arg1) {
            throw new Error(getStringFromWasm0(arg0, arg1));
        },
        __wbg__wbg_cb_unref_dcc1a90847f04c41: function(arg0) {
            arg0._wbg_cb_unref();
        },
        __wbg_addEventListener_4d0db17c671ea324: function() { return handleError(function (arg0, arg1, arg2, arg3) {
            arg0.addEventListener(getStringFromWasm0(arg1, arg2), arg3);
        }, arguments); },
        __wbg_add_9ceab44da1353b80: function() { return handleError(function (arg0, arg1, arg2) {
            arg0.add(getStringFromWasm0(arg1, arg2));
        }, arguments); },
        __wbg_call_6137034ef55c9d0f: function() { return handleError(function (arg0, arg1) {
            const ret = arg0.call(arg1);
            return ret;
        }, arguments); },
        __wbg_classList_8a097a4837412bf6: function(arg0) {
            const ret = arg0.classList;
            return ret;
        },
        __wbg_clearTimeout_c7bc4c3c7a7774af: function(arg0, arg1) {
            arg0.clearTimeout(arg1);
        },
        __wbg_document_9854e03c05fc8834: function(arg0) {
            const ret = arg0.document;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_error_757e9472f8410341: function(arg0, arg1) {
            let deferred0_0;
            let deferred0_1;
            try {
                deferred0_0 = arg0;
                deferred0_1 = arg1;
                console.error(getStringFromWasm0(arg0, arg1));
            } finally {
                wasm.__wbindgen_free(deferred0_0, deferred0_1, 1);
            }
        },
        __wbg_error_c9cf3fc2064683a9: function(arg0) {
            console.error(arg0);
        },
        __wbg_getElementById_cc94972b404e4eaa: function(arg0, arg1, arg2) {
            const ret = arg0.getElementById(getStringFromWasm0(arg1, arg2));
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_getRandomValues_a608c4436c19407a: function() { return handleError(function (arg0, arg1) {
            globalThis.crypto.getRandomValues(getArrayU8FromWasm0(arg0, arg1));
        }, arguments); },
        __wbg_get_31af05bd4842a84f: function() { return handleError(function (arg0, arg1) {
            const ret = Reflect.get(arg0, arg1);
            return ret;
        }, arguments); },
        __wbg_instanceof_Window_82d71df4eddf88bc: function(arg0) {
            let result;
            try {
                result = arg0 instanceof Window;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_new_227d7c05414eb861: function() {
            const ret = new Error();
            return ret;
        },
        __wbg_parse_0fc53dead14b3b42: function() { return handleError(function (arg0, arg1) {
            const ret = JSON.parse(getStringFromWasm0(arg0, arg1));
            return ret;
        }, arguments); },
        __wbg_querySelector_49877e2a9e3f670b: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.querySelector(getStringFromWasm0(arg1, arg2));
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_setTimeout_db7bbc18a17e152a: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.setTimeout(arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_set_innerHTML_7af59a832a09a074: function(arg0, arg1, arg2) {
            arg0.innerHTML = getStringFromWasm0(arg1, arg2);
        },
        __wbg_stack_3b0d974bbf31e44f: function(arg0, arg1) {
            const ret = arg1.stack;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_static_accessor_GLOBAL_266715b9d96ba635: function() {
            const ret = typeof global === 'undefined' ? null : global;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_GLOBAL_THIS_10fb7dc1ae063179: function() {
            const ret = typeof globalThis === 'undefined' ? null : globalThis;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_SELF_0b583911f537483a: function() {
            const ret = typeof self === 'undefined' ? null : self;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_WINDOW_d7f903d1508cbdc4: function() {
            const ret = typeof window === 'undefined' ? null : window;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_textContent_acd42c63564a445e: function(arg0, arg1) {
            const ret = arg1.textContent;
            var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            var len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbindgen_generic_0000000000000001: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("Event")], shim_idx: 79, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen_b0ba9b6703635be___convert__closures_____invoke___web_sys_aad0de371f77e982___features__gen_Event__Event______true_);
            return ret;
        },
        __wbindgen_generic_0000000000000002: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [], shim_idx: 81, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen_b0ba9b6703635be___convert__closures_____invoke_______true_);
            return ret;
        },
        __wbindgen_generic_0000000000000003: function(arg0, arg1) {
            // Cast intrinsic for `Ref(String) -> Externref`.
            const ret = getStringFromWasm0(arg0, arg1);
            return ret;
        },
        __wbindgen_init_externref_table: function() {
            const table = wasm.__wbindgen_externrefs;
            const offset = table.grow(4);
            table.set(0, undefined);
            table.set(offset + 0, undefined);
            table.set(offset + 1, null);
            table.set(offset + 2, true);
            table.set(offset + 3, false);
        },
    };
    return {
        __proto__: null,
        "./terraphim-editor_bg.js": import0,
    };
}

function wasm_bindgen_b0ba9b6703635be___convert__closures_____invoke_______true_(arg0, arg1) {
    wasm.wasm_bindgen_b0ba9b6703635be___convert__closures_____invoke_______true_(arg0, arg1);
}

function wasm_bindgen_b0ba9b6703635be___convert__closures_____invoke___web_sys_aad0de371f77e982___features__gen_Event__Event______true_(arg0, arg1, arg2) {
    wasm.wasm_bindgen_b0ba9b6703635be___convert__closures_____invoke___web_sys_aad0de371f77e982___features__gen_Event__Event______true_(arg0, arg1, arg2);
}

const TerraphimHostSessionFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_terraphimhostsession_free(ptr, 1));

function addToExternrefTable0(obj) {
    const idx = wasm.__externref_table_alloc();
    wasm.__wbindgen_externrefs.set(idx, obj);
    return idx;
}

const CLOSURE_DTORS = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(state => wasm.__wbindgen_destroy_closure(state.a, state.b));

function getArrayU8FromWasm0(ptr, len) {
    ptr = ptr >>> 0;
    return getUint8ArrayMemory0().subarray(ptr / 1, ptr / 1 + len);
}

let cachedDataViewMemory0 = null;
function getDataViewMemory0() {
    if (cachedDataViewMemory0 === null || cachedDataViewMemory0.buffer.detached === true || (cachedDataViewMemory0.buffer.detached === undefined && cachedDataViewMemory0.buffer !== wasm.memory.buffer)) {
        cachedDataViewMemory0 = new DataView(wasm.memory.buffer);
    }
    return cachedDataViewMemory0;
}

function getStringFromWasm0(ptr, len) {
    return decodeText(ptr >>> 0, len);
}

let cachedUint8ArrayMemory0 = null;
function getUint8ArrayMemory0() {
    if (cachedUint8ArrayMemory0 === null || cachedUint8ArrayMemory0.byteLength === 0) {
        cachedUint8ArrayMemory0 = new Uint8Array(wasm.memory.buffer);
    }
    return cachedUint8ArrayMemory0;
}

function handleError(f, args) {
    try {
        return f.apply(this, args);
    } catch (e) {
        const idx = addToExternrefTable0(e);
        wasm.__wbindgen_exn_store(idx);
    }
}

function isLikeNone(x) {
    return x === undefined || x === null;
}

function makeMutClosure(arg0, arg1, f) {
    const state = { a: arg0, b: arg1, cnt: 1 };
    const real = (...args) => {

        // First up with a closure we increment the internal reference
        // count. This ensures that the Rust closure environment won't
        // be deallocated while we're invoking it.
        state.cnt++;
        const a = state.a;
        state.a = 0;
        try {
            return f(a, state.b, ...args);
        } finally {
            state.a = a;
            real._wbg_cb_unref();
        }
    };
    real._wbg_cb_unref = () => {
        if (--state.cnt === 0) {
            wasm.__wbindgen_destroy_closure(state.a, state.b);
            state.a = 0;
            CLOSURE_DTORS.unregister(state);
        }
    };
    CLOSURE_DTORS.register(real, state, state);
    return real;
}

function passStringToWasm0(arg, malloc, realloc) {
    if (realloc === undefined) {
        const buf = cachedTextEncoder.encode(arg);
        const ptr = malloc(buf.length, 1) >>> 0;
        getUint8ArrayMemory0().subarray(ptr, ptr + buf.length).set(buf);
        WASM_VECTOR_LEN = buf.length;
        return ptr;
    }

    let len = arg.length;
    let ptr = malloc(len, 1) >>> 0;

    const mem = getUint8ArrayMemory0();

    let offset = 0;

    for (; offset < len; offset++) {
        const code = arg.charCodeAt(offset);
        if (code > 0x7F) break;
        mem[ptr + offset] = code;
    }
    if (offset !== len) {
        if (offset !== 0) {
            arg = arg.slice(offset);
        }
        ptr = realloc(ptr, len, len = offset + arg.length * 3, 1) >>> 0;
        const view = getUint8ArrayMemory0().subarray(ptr + offset, ptr + len);
        const ret = cachedTextEncoder.encodeInto(arg, view);

        offset += ret.written;
        ptr = realloc(ptr, len, offset, 1) >>> 0;
    }

    WASM_VECTOR_LEN = offset;
    return ptr;
}

function takeFromExternrefTable0(idx) {
    const value = wasm.__wbindgen_externrefs.get(idx);
    wasm.__externref_table_dealloc(idx);
    return value;
}

let cachedTextDecoder = new TextDecoder('utf-8', { ignoreBOM: true, fatal: true });
cachedTextDecoder.decode();
const MAX_SAFARI_DECODE_BYTES = 2146435072;
let numBytesDecoded = 0;
function decodeText(ptr, len) {
    numBytesDecoded += len;
    if (numBytesDecoded >= MAX_SAFARI_DECODE_BYTES) {
        cachedTextDecoder = new TextDecoder('utf-8', { ignoreBOM: true, fatal: true });
        cachedTextDecoder.decode();
        numBytesDecoded = len;
    }
    return cachedTextDecoder.decode(getUint8ArrayMemory0().subarray(ptr, ptr + len));
}

const cachedTextEncoder = new TextEncoder();

if (!('encodeInto' in cachedTextEncoder)) {
    cachedTextEncoder.encodeInto = function (arg, view) {
        const buf = cachedTextEncoder.encode(arg);
        view.set(buf);
        return {
            read: arg.length,
            written: buf.length
        };
    };
}

let WASM_VECTOR_LEN = 0;

let wasmModule, wasmInstance, wasm;
function __wbg_finalize_init(instance, module) {
    wasmInstance = instance;
    wasm = instance.exports;
    wasmModule = module;
    cachedDataViewMemory0 = null;
    cachedUint8ArrayMemory0 = null;
    wasm.__wbindgen_start();
    return wasm;
}

async function __wbg_load(module, imports) {
    if (typeof Response === 'function' && module instanceof Response) {
        if (!module.ok) {
            throw new Error(`failed to fetch Wasm: ${module.status} ${module.statusText} fetching '${module.url}'`);
        }

        if (typeof WebAssembly.instantiateStreaming === 'function') {
            try {
                return await WebAssembly.instantiateStreaming(module, imports);
            } catch (e) {
                const validResponse = expectedResponseType(module.type);

                if (validResponse && module.headers.get('Content-Type') !== 'application/wasm') {
                    console.warn("`WebAssembly.instantiateStreaming` failed because your server does not serve Wasm with `application/wasm` MIME type. Falling back to `WebAssembly.instantiate` which is slower. Original error:\n", e);

                } else { throw e; }
            }
        }

        const bytes = await module.arrayBuffer();
        return await WebAssembly.instantiate(bytes, imports);
    } else {
        const instance = await WebAssembly.instantiate(module, imports);

        if (instance instanceof WebAssembly.Instance) {
            return { instance, module };
        } else {
            return instance;
        }
    }

    function expectedResponseType(type) {
        switch (type) {
            case 'basic': case 'cors': case 'default': return true;
        }
        return false;
    }
}

function initSync(module) {
    if (wasm !== undefined) return wasm;


    if (module !== undefined) {
        if (Object.getPrototypeOf(module) === Object.prototype) {
            ({module} = module)
        } else {
            console.warn('using deprecated parameters for `initSync()`; pass a single object instead')
        }
    }

    const imports = __wbg_get_imports();
    if (!(module instanceof WebAssembly.Module)) {
        module = new WebAssembly.Module(module);
    }
    const instance = new WebAssembly.Instance(module, imports);
    return __wbg_finalize_init(instance, module);
}

async function __wbg_init(module_or_path) {
    if (wasm !== undefined) return wasm;


    if (module_or_path !== undefined) {
        if (Object.getPrototypeOf(module_or_path) === Object.prototype) {
            ({module_or_path} = module_or_path)
        } else {
            console.warn('using deprecated parameters for the initialization function; pass a single object instead')
        }
    }

    if (module_or_path === undefined) {
        module_or_path = new URL('terraphim-editor_bg.wasm', import.meta.url);
    }
    const imports = __wbg_get_imports();

    if (typeof module_or_path === 'string' || (typeof Request === 'function' && module_or_path instanceof Request) || (typeof URL === 'function' && module_or_path instanceof URL)) {
        module_or_path = fetch(module_or_path);
    }

    const { instance, module } = await __wbg_load(await module_or_path, imports);

    return __wbg_finalize_init(instance, module);
}

export { initSync, __wbg_init as default };
