/* Graph embeddings explainer — scene controllers.
 * One shared RoleGraphLite instance; every number on the Terraphim side is
 * computed live by engine.js (a faithful port of terraphim_rolegraph).
 * The "dense vectors" panel is a labelled illustrative simulation.
 */
(function () {
  "use strict";

  const { magicPair, magicUnpair, AhoLite, RoleGraphLite } = window.TGEngine;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (sel, el) => (el || document).querySelector(sel);
  const $$ = (sel, el) => [...(el || document).querySelectorAll(sel)];
  const esc = (s) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const escAttr = (s) => esc(s).replace(/"/g, "&quot;").replace(/'/g, "&#39;");

  // Deterministic hand-tuned layout (id -> [x,y]) in a 820x520 viewBox.
  const POS = {
    1: [215, 105], 2: [330, 265], 3: [450, 115], 4: [565, 265],
    5: [335, 415], 6: [565, 415], 7: [145, 300], 8: [105, 160],
    9: [705, 140], 10: [445, 490],
  };
  const posFor = (id) => POS[id] || [
    410 + 190 * Math.cos(id * 2.399), 280 + 160 * Math.sin(id * 2.399),
  ];

  let corpus, graph, ntermOf;

  function rebuildGraph() {
    graph = new RoleGraphLite(corpus.thesaurus);
    ntermOf = graph.ac.nterm;
    for (const d of corpus.documents) {
      if (d.indexed) graph.insertDocument(d.id, d.text, d.title);
    }
  }

  /* ---------- shared SVG renderer ---------- */

  const SVGNS = "http://www.w3.org/2000/svg";
  function el(name, attrs, parent) {
    const e = document.createElementNS(SVGNS, name);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  // Directed edge path: curve offset perpendicular so both directions show.
  function edgePath(a, b, self) {
    const [x1, y1] = posFor(a);
    const [x2, y2] = posFor(b);
    if (self) {
      const r = 26;
      return `M ${x1} ${y1 - 16} C ${x1 - r * 1.6} ${y1 - r * 2.4}, ${x1 + r * 1.6} ${y1 - r * 2.4}, ${x1 + 14} ${y1 - 14}`;
    }
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    const dx = x2 - x1, dy = y2 - y1;
    const len = Math.hypot(dx, dy) || 1;
    const off = Math.min(24, len * 0.18);
    const cx = mx - (dy / len) * off, cy = my + (dx / len) * off;
    return `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;
  }

  function renderGraph(svg, { litNodes = new Set(), litEdges = new Set(), dimOthers = false, newNodes = new Set() } = {}) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const defs = el("defs", {}, svg);
    const marker = el("marker", {
      id: svg.id + "-arrow", viewBox: "0 0 10 10", refX: 9, refY: 5,
      markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse",
    }, defs);
    el("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: "var(--text-muted)" }, marker);

    const edgeLayer = el("g", {}, svg);
    const nodeLayer = el("g", {}, svg);

    for (const [eid, edge] of graph.edges) {
      const [a, b] = magicUnpair(eid);
      const weight = [...edge.docHash.values()].reduce((s, v) => s + v, 0);
      const lit = litEdges.has(eid);
      const p = el("path", {
        d: edgePath(a, b, a === b),
        class: "tge-edge" + (lit ? " lit" : dimOthers ? " dim" : ""),
        "stroke-width": 1 + Math.min(4, weight * 0.9),
        "marker-end": `url(#${svg.id}-arrow)`,
        "data-edge": eid,
      }, edgeLayer);
      if (lit) {
        const mid = edgePathMid(a, b, a === b);
        el("text", { x: mid[0], y: mid[1] - 6, class: "tge-edge-label", "text-anchor": "middle" }, edgeLayer)
          .textContent = `×${weight}`;
      }
    }

    for (const [id, node] of graph.nodes) {
      const [x, y] = posFor(id);
      const lit = litNodes.has(id);
      const gnode = el("g", {
        class: "tge-node" + (lit ? " lit" : dimOthers ? " dim" : "") + (newNodes.has(id) ? " new" : ""),
        transform: `translate(${x} ${y})`, "data-node": id,
      }, nodeLayer);
      const r = 13 + 1.6 * Math.sqrt(node.rank);
      el("circle", { r: r }, gnode);
      const label = el("text", { y: -r - 6 }, gnode);
      label.textContent = ntermOf[id] || `#${id}`;
      el("text", { y: 4, class: "tge-rank" }, gnode).textContent = node.rank;
    }
  }

  function edgePathMid(a, b, self) {
    const [x1, y1] = posFor(a);
    if (self) return [x1, y1 - 46];
    const [x2, y2] = posFor(b);
    return [(x1 + x2) / 2 - (y2 - y1) * 0.12, (y1 + y2) / 2 + (x2 - x1) * 0.12];
  }

  // Ported from sx-map-canvas edge painting: a "packet" travels each touched
  // edge so the counter increment is *seen*, not just stated. Overlay a cloned
  // path and march a dash along it via WAAPI stroke-dashoffset; skipped under
  // prefers-reduced-motion.
  function flowEdges(svg, eids) {
    if (reduced) return;
    eids.forEach((eid, i) => {
      const base = svg.querySelector(`path[data-edge="${eid}"]`);
      if (!base || !base.animate) return;
      const packet = base.cloneNode(false);
      packet.removeAttribute("marker-end");
      packet.removeAttribute("data-edge");
      packet.setAttribute("class", "tge-packet");
      packet.setAttribute("aria-hidden", "true");
      base.parentNode.appendChild(packet);
      const len = packet.getTotalLength();
      packet.style.strokeDasharray = `16 ${len}`;
      packet.style.strokeDashoffset = String(len);
      packet.animate(
        [{ strokeDashoffset: len }, { strokeDashoffset: -16 }],
        { duration: 750, delay: i * 90, easing: "cubic-bezier(0.23,1,0.32,1)", fill: "forwards" }
      ).onfinish = () => packet.remove();
    });
  }

  /* ---------- Scene 1: two worlds ---------- */

  // Deterministic fake vector layout, labelled illustrative.
  function hash(s) {
    let h = 2166136261;
    for (const c of s) { h ^= c.charCodeAt(0); h = (h * 16777619) >>> 0; }
    return h;
  }
  const vpos = {};
  function vecPos(id) {
    if (!vpos[id]) {
      const h1 = hash(id), h2 = hash(id + ":y");
      vpos[id] = [30 + (h1 % 300), 30 + (h2 % 200)];
    }
    return vpos[id];
  }
  function fakeNearest(q, k) {
    const hq = hash(q);
    return corpus.documents
      .map((d) => ({ id: d.id, dist: Math.abs(((hash(d.id) ^ hq) % 997) / 997) + (hq % 13) / 1000 }))
      .sort((a, b) => a.dist - b.dist)
      .slice(0, k);
  }

  function renderVecPanel(svg, query) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const near = new Set(fakeNearest(query, 4).map((d) => d.id));
    const qx = 30 + (hash(query) % 300), qy = 30 + (hash(query + ":q") % 200);
    el("circle", { cx: qx, cy: qy, r: 105, class: "tge-ring" }, svg);
    for (const d of corpus.documents) {
      const [x, y] = vecPos(d.id);
      const lit = near.has(d.id);
      const c = el("circle", { cx: x, cy: y, r: lit ? 8 : 5.5, class: "tge-dot" + (lit ? " lit" : "") }, svg);
      el("title", {}, c).textContent = d.id;
      if (lit) {
        el("text", { x: x + 10, y: y - 8, class: "tge-sim-label" }, svg)
          .textContent = (0.98 - 0.11 * fakeNearest(query, 4).findIndex((n) => n.id === d.id)).toFixed(2);
      }
    }
    el("circle", { cx: qx, cy: qy, r: 7, class: "tge-dot query" }, svg);
    el("text", { x: qx + 10, y: qy + 4, class: "tge-sim-label" }, svg).textContent = "query";
  }

  function runWorldsQuery() {
    const q = $("#tge-q").value.trim() || "consensus";
    renderVecPanel($("#vec-svg"), q);
    const results = graph.queryGraph(q);
    const litNodes = new Set(graph.findNodeIds(q));
    const litEdges = new Set();
    for (const r of results) for (const c of r.contributions) litEdges.add(c.edgeId);
    renderGraph($("#world-graph-svg"), { litNodes, litEdges, dimOthers: true });
    const why = $("#tge-why");
    if (results.length === 0) {
      why.innerHTML = litNodes.size === 0
        ? `<strong>Nothing.</strong> “${esc(q)}” matches no thesaurus term —
           the graph returns an empty set. The vector side still returns nearest neighbours:
           useful, and worth being honest about.`
        : `<strong>Matched, but no results yet.</strong> “${esc(q)}” maps to real concepts —
           the index is just empty. Scroll down, index the corpus, come back.`;
      why.className = "tge-note red";
    } else {
      const top = results[0];
      why.innerHTML = `<strong>${esc(top.id)}</strong> wins with score <b>${top.rank}</b> —
        and every point of it is explained below: which node, which edge, which count.`;
      why.className = "tge-note green";
    }
  }

  /* ---------- Scene 2: matcher ---------- */

  function renderMatcher() {
    const text = $("#tge-matcher-input").value;
    const matches = graph.ac.findMatches(text);
    const out = $("#tge-matcher-text");
    if (!text) { out.innerHTML = '<span class="tge-kbd-hint">Type above — matched spans highlight and map to concept ids.</span>'; $("#tge-matcher-chips").innerHTML = ""; return; }
    let html = "", last = 0;
    for (const m of matches) {
      html += esc(text.slice(last, m.start));
      html += `<mark title="→ #${m.id} ${escAttr(ntermOf[m.id] || "")}">${esc(text.slice(m.start, m.end))}</mark>`;
      last = m.end;
    }
    html += esc(text.slice(last));
    out.innerHTML = html + '<span class="tge-cursor" aria-hidden="true"></span>';
    // Single-pass sweep: re-inserting the element restarts the CSS animation.
    if (!reduced) {
      out.appendChild(Object.assign(document.createElement("span"), { className: "tge-cursor-scan" }));
    }
    $("#tge-matcher-chips").innerHTML = matches.length
      ? matches.map((m, i) =>
          `<span class="tge-chip${i < matches.length - 1 ? " arrow" : ""}"><b>#${m.id}</b> ${esc(ntermOf[m.id] || "")}</span>`
        ).join("")
      : '<span class="tge-chip">no matches — this text adds nothing to the graph</span>';
    return matches;
  }

  /* ---------- Scene 3: indexer ---------- */

  function renderQueue() {
    const q = $("#tge-queue");
    q.innerHTML = corpus.documents.map((d) => `
      <div class="tge-docrow ${d.indexed ? "indexed" : ""}" data-doc="${esc(d.id)}">
        <span class="tge-docid">${esc(d.id)}</span>
        <span class="tge-doctext">${esc(d.title)} — ${esc(d.text)}</span>
      </div>`).join("");
  }

  function indexDoc(docId, text, title) {
    const matches = graph.insertDocument(docId, text, title);
    const pairs = [];
    for (let i = 0; i + 1 < matches.length; i++) pairs.push([matches[i], matches[i + 1]]);
    return { matches, pairs };
  }

  function chipsFor(matches) {
    return matches.map((id, i) =>
      `<span class="tge-chip${i < matches.length - 1 ? " arrow" : ""}"><b>#${id}</b> ${esc(ntermOf[id] || "")}</span>`
    ).join("");
  }

  function indexNext() {
    const next = corpus.documents.find((d) => !d.indexed);
    if (!next) return;
    next.indexed = true;
    const { matches, pairs } = indexDoc(next.id, next.text, next.title);
    const touched = pairs.map(([a, b]) => magicPair(a, b));
    $("#tge-index-matches").innerHTML =
      `<div class="tge-mono" style="font-size:.8rem;color:var(--text-dim)">matched sequence for ${esc(next.id)}</div>` +
      `<div class="tge-chips">${chipsFor(matches)}</div>` +
      `<div class="tge-mono" style="font-size:.8rem;color:var(--text-dim);margin-top:.4rem">` +
      `→ ${pairs.length} directed edge${pairs.length === 1 ? "" : "s"}: ` +
      pairs.map(([a, b]) => `(${esc(ntermOf[a] || a)} → ${esc(ntermOf[b] || b)})`).join(", ") + `</div>`;
    renderQueue();
    renderGraph($("#main-graph-svg"), { newNodes: new Set(matches) });
    flowEdges($("#main-graph-svg"), touched);
    renderStats();
    markQueueRow(next.id);
  }

  function markQueueRow(id) {
    const row = $(`.tge-docrow[data-doc="${CSS.escape(id)}"]`);
    if (row) { row.classList.add("indexed", "active"); }
  }

  function renderStats() {
    const s = graph.stats();
    $("#tge-stats").textContent =
      `${s.nodes} concepts · ${s.edges} directed edges · ${s.documents} documents · ${s.thesaurus} thesaurus terms`;
  }

  /* ---------- Scene 4: query ---------- */

  function runQuery(q) {
    const results = graph.queryGraph(q);
    const litNodes = new Set(graph.findNodeIds(q));
    const litEdges = new Set();
    for (const r of results) for (const c of r.contributions) litEdges.add(c.edgeId);
    renderGraph($("#main-graph-svg"), { litNodes, litEdges, dimOthers: results.length > 0 });
    const el_ = $("#tge-results");
    if (results.length === 0) {
      el_.innerHTML = `<div class="tge-note red"><b>Empty.</b> “${esc(q)}” hits no thesaurus term. Honest failure —
        no fuzzy fallback here (the TF-IDF trigger index is a separate opt-in layer).</div>`;
      return;
    }
    el_.innerHTML = `<table class="tge-ledger"><thead><tr>
        <th>document</th><th>score</th><th>how it was earned</th></tr></thead><tbody>` +
      results.map((r, i) => `<tr class="${i === 0 ? "top" : ""}">
        <td>${esc(r.id)}</td>
        <td class="tge-sum">${r.rank}</td>
        <td>${r.contributions.map((c) =>
          `<div class="tge-contrib"><code>${esc(c.nterm)}</code> via edge
           <code>${esc(ntermOf[c.pair[0]] || c.pair[0])}→${esc(ntermOf[c.pair[1]] || c.pair[1])}</code>:
           node ${c.nodeRank} + edge ${c.edgeRank} + doc ${c.docRank} = <b>${c.total}</b></div>`
        ).join("")}</td></tr>`).join("") +
      "</tbody></table>";
  }

  /* ---------- Scene 5: pipeline ---------- */

  function addSynonym() {
    const input = $("#tge-syn-input").value.trim().toLowerCase();
    const out = $("#tge-syn-result");
    if (!input) return;
    if (corpus.thesaurus.data[input]) {
      out.innerHTML = `<span class="tge-chip">“${esc(input)}” is already a thesaurus term — pick another.</span>`;
      return;
    }
    const t0 = performance.now();
    corpus.thesaurus.data[input] = { id: 4, nterm: "leader" };
    graph.ac = new AhoLite(corpus.thesaurus.data);
    ntermOf = graph.ac.nterm;
    const ms = (performance.now() - t0).toFixed(2);
    $("#tge-syn-time").textContent = `${ms} ms (measured)`;
    out.innerHTML =
      `<span class="tge-chip"><b>rebuilt</b> automaton in ${ms} ms — “${esc(input)}” now maps to
       <b>leader</b>. Try it in the matcher or as a query.</span>`;
    $("#tge-syn-flash").classList.add("flash");
    renderStats();
    renderGraph($("#main-graph-svg"), {});
  }

  /* ---------- wiring ---------- */

  async function init() {
    const res = await fetch("/explainers/graph-embeddings/corpus.json");
    corpus = await res.json();
    // Start fully indexed — scene 1 must show a live graph. The indexer
    // scene lets visitors reset and rebuild step by step.
    corpus.documents.forEach((d) => (d.indexed = true));
    rebuildGraph();
    renderStats();
    renderQueue();
    renderGraph($("#main-graph-svg"), {});
    renderGraph($("#world-graph-svg"), {});
    renderVecPanel($("#vec-svg"), "consensus");

    $("#tge-q-run").addEventListener("click", runWorldsQuery);
    $("#tge-q").addEventListener("keydown", (e) => { if (e.key === "Enter") runWorldsQuery(); });
    $$("#tge-q-presets [data-q]").forEach((b) =>
      b.addEventListener("click", () => { $("#tge-q").value = b.dataset.q; runWorldsQuery(); }));

    $("#tge-matcher-input").addEventListener("input", renderMatcher);
    $("#tge-matcher-input").value = "Raft is a consensus algorithm — the leader election picks a leader.";
    renderMatcher();

    $("#tge-index-next").addEventListener("click", indexNext);
    $("#tge-index-all").addEventListener("click", () => { while (corpus.documents.some((d) => !d.indexed)) indexNext(); });
    $("#tge-index-reset").addEventListener("click", () => {
      corpus.documents.forEach((d) => (d.indexed = false));
      rebuildGraph(); renderQueue(); renderStats();
      renderGraph($("#main-graph-svg"), {});
      $("#tge-index-matches").innerHTML = "";
      $("#tge-results").innerHTML = "";
    });
    $("#tge-index-own").addEventListener("click", () => {
      const text = $("#tge-own-text").value.trim();
      if (!text) return;
      const id = "your-doc";
      const existing = corpus.documents.find((d) => d.id === id);
      if (existing) { existing.text = text; existing.indexed = true; }
      else corpus.documents.push({ id, title: "Your sentence", text, indexed: true });
      const { matches, pairs } = indexDoc(id, text, "Your sentence");
      const touched = pairs.map(([a, b]) => magicPair(a, b));
      $("#tge-index-matches").innerHTML =
        `<div class="tge-mono" style="font-size:.8rem;color:var(--text-dim)">your sentence</div>` +
        `<div class="tge-chips">${matches.length ? chipsFor(matches) : '<span class="tge-chip">no thesaurus terms — nothing indexed</span>'}</div>`;
      renderQueue(); renderGraph($("#main-graph-svg"), { newNodes: new Set(matches) });
      flowEdges($("#main-graph-svg"), touched); renderStats();
      markQueueRow(id);
    });

    $$("#tge-query-presets [data-q]").forEach((b) =>
      b.addEventListener("click", () => { $("#tge-query-input").value = b.dataset.q; runQuery(b.dataset.q); }));
    $("#tge-query-run").addEventListener("click", () => runQuery($("#tge-query-input").value));
    $("#tge-query-input").addEventListener("keydown", (e) => { if (e.key === "Enter") runQuery(e.target.value); });

    $("#tge-syn-add").addEventListener("click", addSynonym);

    // Esc clears transient view state (highlights, ledgers) — indexed data is kept.
    document.addEventListener("keydown", (e) => {
      if (e.key !== "Escape" || e.target.matches("input, textarea")) return;
      $("#tge-results").innerHTML = "";
      $("#tge-index-matches").innerHTML = "";
      $("#tge-why").innerHTML = "";
      renderGraph($("#main-graph-svg"), {});
      renderGraph($("#world-graph-svg"), {});
    });

    // Lazy init: scenes animate only when near the viewport.
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((es) => {
        es.forEach((e) => e.target.classList.toggle("in-view", e.isIntersecting));
      }, { rootMargin: "100px" });
      $$(".tge-scene").forEach((s) => io.observe(s));
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
