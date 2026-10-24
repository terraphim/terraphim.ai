/* Terraphim Proxy — buy button.
   Wires #proxy-buy-btn on /terraphim-llm-proxy/ to the Terraphim Skills
   marketplace checkout. Contract: GET /api/billing/checkout?product=…
   with a Bearer JWT returns {"url": "<stripe checkout url>"}.

   Sign-in is a round trip: the link carries ?return_to=<this page>, the
   OAuth callback lands back here with the JWT in the fragment
   (#token=<jwt>), which captureToken() below moves into localStorage and
   strips from the address bar. Requires /js/proxy-helpers.js loaded first. */
(function () {
  'use strict';
  var H = window.ProxyHelpers;
  var btn = document.getElementById('proxy-buy-btn');
  var status = document.getElementById('proxy-buy-status');
  if (!H || !btn || !status) { return; }

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

  function showSignIn(note) {
    status.innerHTML = note +
      ' <a href="' + signInHref() + '">Sign in with GitHub</a>, then try again.';
  }

  captureToken();

  btn.addEventListener('click', function () {
    var token = getToken();
    if (!token) {
      showSignIn('Purchasing needs a Terraphim account.');
      return;
    }
    btn.disabled = true;
    status.textContent = 'Preparing checkout…';
    fetch(H.API + '/api/billing/checkout?product=terraphim-proxy', {
      headers: { 'Authorization': 'Bearer ' + token }
    })
    .then(function (res) {
      if (res.status === 401) {
        showSignIn('Your session has expired —');
        btn.disabled = false;
        return null;
      }
      if (!res.ok) { throw new Error('checkout ' + res.status); }
      return res.json();
    })
    .then(function (data) {
      if (!data) { return; }
      if (data.url) { window.location.href = data.url; return; }
      throw new Error('checkout returned no url');
    })
    .catch(function () {
      status.textContent = 'Checkout is unavailable right now — please try again later.';
      btn.disabled = false;
    });
  });
})();
