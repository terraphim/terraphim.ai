/* Terraphim Proxy — entitlement-gated release downloads.
   Renders the public release catalogue on /terraphim-llm-proxy/download/
   and gates artefact fetches behind a Bearer JWT; 402 means the account
   has not purchased. Contract (api.terraphim-skills.md):
     GET /api/products/terraphim-proxy/releases
         -> [{version, asset_name, size_bytes, sha256, published_at}]
            (a wrapped {"releases": [...]} shape is tolerated)
     GET /api/products/terraphim-proxy/releases/{version}/{asset}
         -> artefact bytes + X-SHA256 header; 402 {"error":"purchase_required"}.

   Sign-in is a round trip: links carry ?return_to=<this page>, the OAuth
   callback lands back here with the JWT in the fragment (#token=<jwt>),
   which captureToken() moves into localStorage and strips from the
   address bar. Requires /js/proxy-helpers.js loaded first. */
(function () {
  'use strict';
  var H = window.ProxyHelpers;
  var banner = document.getElementById('proxy-dl-banner');
  var notice = document.getElementById('proxy-dl-notice');
  var wrap = document.getElementById('proxy-dl-wrap');
  if (!H || !notice || !wrap) { return; }

  var BUY_URL = '/terraphim-llm-proxy/#your-keys-your-costs';

  /* Move a JWT handed back in the URL fragment (or, forward-compat, the
     query) into localStorage, then scrub it from the address bar and
     history — a JWT must never linger in either. */
  function captureToken() {
    var tok = H.tokenFromLocation(window.location);
    if (!tok) { return; }
    try { localStorage.setItem('terraphim_token', tok); } catch (e) { return; }
    try {
      var q = new URLSearchParams(window.location.search);
      q.delete('token');
      var qs = q.toString();
      var hash = H.stripTokenFromHash(window.location.hash);
      var clean = window.location.origin + window.location.pathname +
        (qs ? '?' + qs : '') + (hash ? '#' + hash : '');
      history.replaceState(null, '', clean);
    } catch (e) { /* replaceState unavailable — token is stored anyway */ }
  }

  function getToken() {
    try { return localStorage.getItem('terraphim_token'); } catch (e) { return null; }
  }

  function signInHref() {
    var back = window.location.origin + window.location.pathname + window.location.search;
    return H.signInUrl(back);
  }

  captureToken();

  /* ?checkout=success comes back from Stripe. Only claim the purchase is
     confirmed when a token is present — anyone can forge the parameter,
     so signed-out visitors get neutral wording instead. */
  try {
    if (new URLSearchParams(window.location.search).get('checkout') === 'success' && banner) {
      if (!getToken()) {
        banner.innerHTML =
          '<i class="fa-solid fa-circle-info" aria-hidden="true"></i> ' +
          'Checkout completed — sign in below to confirm download access.';
      }
      banner.hidden = false;
    }
  } catch (e) { /* malformed query — ignore */ }

  function signInPrompt() {
    notice.innerHTML =
      '<p class="proxy-dl-callout"><i class="fa-solid fa-right-to-bracket" aria-hidden="true"></i> ' +
      '<a href="' + signInHref() + '">Sign in with GitHub</a> using the account you purchased ' +
      'with to download releases. No licence yet? ' +
      '<a href="' + BUY_URL + '">Buy Terraphim Proxy — $15</a>.</p>';
  }

  function purchaseRequired() {
    notice.innerHTML =
      '<p class="proxy-dl-callout warn"><i class="fa-solid fa-lock" aria-hidden="true"></i> ' +
      'Purchase required — this account has not bought Terraphim Proxy. ' +
      '<a href="' + BUY_URL + '">Buy a licence</a> to unlock downloads, or ' +
      '<a href="' + signInHref() + '">sign in with a different account</a>.</p>';
  }

  if (!getToken()) { signInPrompt(); }

  fetch(H.API + '/api/products/terraphim-proxy/releases', {
    headers: { 'Accept': 'application/json' }
  })
    .then(function (res) {
      if (!res.ok) { throw new Error('releases ' + res.status); }
      return res.json();
    })
    .then(function (data) {
      var releases = H.normaliseReleases(data);
      if (!releases.length) {
        wrap.innerHTML = '<p class="proxy-dl-muted">No releases are published yet.</p>';
        return;
      }
      renderTable(releases);
    })
    .catch(function () {
      wrap.innerHTML =
        '<p class="proxy-dl-muted">Releases are unavailable right now — please try again later.</p>';
    });

  function renderTable(releases) {
    var hasToken = !!getToken();
    var rows = [];
    for (var i = 0; i < releases.length; i++) {
      var r = releases[i] || {};
      var sha = r.sha256 || '';
      var shaCell = sha
        ? '<code class="proxy-dl-sha" title="' + H.esc(sha) + '">' + H.esc(sha.slice(0, 12)) + '…</code>'
        : '—';
      var action = hasToken
        ? '<button type="button" class="btn btn-primary btn-sm" data-i="' + i + '">' +
          '<i class="fa-solid fa-download" aria-hidden="true"></i> Download</button>'
        : '<a class="btn btn-ghost btn-sm" href="' + signInHref() + '">' +
          '<i class="fa-solid fa-right-to-bracket" aria-hidden="true"></i> Sign in</a>';
      rows.push(
        '<tr>' +
        '<td>' + H.esc(r.version || '—') + '</td>' +
        '<td><code>' + H.esc(r.asset_name || '—') + '</code></td>' +
        '<td>' + H.esc(H.fmtDate(r.published_at)) + '</td>' +
        '<td>' + H.esc(H.humanSize(r.size_bytes)) + '</td>' +
        '<td>' + shaCell + '</td>' +
        '<td>' + action + '<div class="proxy-dl-row-status"></div></td>' +
        '</tr>'
      );
    }
    wrap.innerHTML =
      '<table class="proxy-dl-table"><thead><tr>' +
      '<th>Version</th><th>Asset</th><th>Released</th><th>Size</th><th>SHA-256</th><th></th>' +
      '</tr></thead><tbody>' + rows.join('') + '</tbody></table>';
    var btns = wrap.querySelectorAll('button[data-i]');
    for (var j = 0; j < btns.length; j++) {
      (function (btn) {
        btn.addEventListener('click', function () {
          downloadRelease(releases[Number(btn.getAttribute('data-i'))], btn);
        });
      })(btns[j]);
    }
  }

  function downloadRelease(rel, btn) {
    var token = getToken();
    var rs = btn.parentNode.querySelector('.proxy-dl-row-status');
    if (!token) { signInPrompt(); return; }
    btn.disabled = true;
    rs.innerHTML =
      '<span class="proxy-dl-muted"><i class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> downloading…</span>';
    fetch(H.downloadUrl(rel.version, rel.asset_name), {
      headers: { 'Authorization': 'Bearer ' + token }
    })
      .then(function (res) {
        if (res.status === 401) {
          rs.innerHTML = '';
          signInPrompt();
          throw { handled: true };
        }
        if (res.status === 402) {
          rs.innerHTML = '';
          purchaseRequired();
          throw { handled: true };
        }
        if (!res.ok) { throw new Error('download ' + res.status); }
        var sha = res.headers.get('X-SHA256');
        return res.blob().then(function (blob) { return { blob: blob, sha: sha }; });
      })
      .then(function (result) {
        if (!result) { return; }
        var objectUrl = URL.createObjectURL(result.blob);
        var a = document.createElement('a');
        a.href = objectUrl;
        a.download = rel.asset_name || 'terraphim-proxy.dmg';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(function () { URL.revokeObjectURL(objectUrl); }, 5000);
        rs.innerHTML = result.sha
          ? '<span class="proxy-dl-ok"><i class="fa-solid fa-circle-check" aria-hidden="true"></i> ' +
            'Saved. SHA-256: <code title="' + H.esc(result.sha) + '">' + H.esc(result.sha) + '</code> ' +
            '— verify with <code>shasum -a 256</code></span>'
          : '<span class="proxy-dl-ok"><i class="fa-solid fa-circle-check" aria-hidden="true"></i> ' +
            'Saved ' + H.esc(rel.asset_name || 'artefact') + '.</span>';
      })
      .catch(function (err) {
        if (err && err.handled) { return; }
        rs.innerHTML =
          '<span class="proxy-dl-err"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i> ' +
          'Download failed — please try again.</span>';
      })
      .finally(function () { btn.disabled = false; });
  }
})();
