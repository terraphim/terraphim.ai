/* Terraphim Proxy — pure helpers shared by the buy and download pages.
   UMD-style export: attaches to window.ProxyHelpers in the browser and
   exports the same object via module.exports so `node --test` can load it
   without a DOM or any npm dependencies. */
(function (root, factory) {
  var api = factory();
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
  root.ProxyHelpers = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var API = 'https://api.terraphim-skills.md';

  /* HTML-escape a value for interpolation into element markup or an
     attribute — quotes included so it is safe inside title="…" too. */
  function esc(s) {
    return String(s === null || s === undefined ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /* Human-readable byte count: 16457327 -> "15.7 MB". */
  function humanSize(bytes) {
    var n = Number(bytes);
    if (!isFinite(n) || n < 0) { return '—'; }
    var units = ['B', 'KB', 'MB', 'GB'];
    var i = 0;
    while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
    return (i === 0 ? String(n) : n.toFixed(1)) + ' ' + units[i];
  }

  /* en-GB short date for an ISO timestamp; invalid input passes through
     so a surprising-but-non-empty server value is shown rather than lost. */
  function fmtDate(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) { return iso || '—'; }
    return d.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  /* Accept both the bare array and the {"releases": [...]} wrapped shape. */
  function normaliseReleases(data) {
    if (Array.isArray(data)) { return data; }
    if (data && Array.isArray(data.releases)) { return data.releases; }
    return [];
  }

  /* Bearer-gated artefact endpoint for one release asset. */
  function downloadUrl(version, asset) {
    return API + '/api/products/terraphim-proxy/releases/' +
      encodeURIComponent(version) + '/' + encodeURIComponent(asset);
  }

  /* GitHub OAuth entry point carrying an absolute return_to so the token
     is handed back to this origin (server-side allowlist includes
     https://terraphim.ai). */
  function signInUrl(returnTo) {
    return API + '/api/auth/signin/github?return_to=' + encodeURIComponent(returnTo);
  }

  /* Extract the JWT the OAuth callback hands back in the fragment
     (#token=<jwt>, possibly alongside other params) or, forward-compat,
     in the query (?token=<jwt>). `loc` is a {hash, search} pair — pass
     window.location at runtime, plain strings in tests. Hash wins. */
  function tokenFromLocation(loc) {
    var hash = (loc && loc.hash) || '';
    var hm = hash.match(/(?:^#|[#&])token=([^&]+)/);
    if (hm) { return decodeURIComponent(hm[1]); }
    var search = (loc && loc.search) || '';
    var qm = search.match(/[?&]token=([^&]+)/);
    if (qm) { return decodeURIComponent(qm[1]); }
    return null;
  }

  /* Remove only the token= param from a location.hash, preserving other
     params and plain anchors. Returns the bare fragment (no leading #). */
  function stripTokenFromHash(hash) {
    var h = (hash || '').replace(/(^#|&)token=[^&]*/g, '$1');
    return h.replace(/^[#&]+/, '').replace(/&+$/, '');
  }

  return {
    API: API,
    esc: esc,
    humanSize: humanSize,
    fmtDate: fmtDate,
    normaliseReleases: normaliseReleases,
    downloadUrl: downloadUrl,
    signInUrl: signInUrl,
    tokenFromLocation: tokenFromLocation,
    stripTokenFromHash: stripTokenFromHash
  };
});
