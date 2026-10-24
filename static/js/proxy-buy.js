/* Terraphim Proxy — buy button.
   Wires #proxy-buy-btn on /terraphim-llm-proxy/ to the Terraphim Skills
   marketplace checkout. Contract: GET /api/billing/checkout?product=…
   with a Bearer JWT returns {"url": "<stripe checkout url>"}. */
(function () {
  'use strict';
  var API = 'https://api.terraphim-skills.md';
  var btn = document.getElementById('proxy-buy-btn');
  var status = document.getElementById('proxy-buy-status');
  if (!btn || !status) { return; }

  function getToken() {
    try { return localStorage.getItem('terraphim_token'); } catch (e) { return null; }
  }

  function showSignIn(note) {
    status.innerHTML = note +
      ' <a href="' + API + '/auth/oauth/github">Sign in with GitHub</a>, then try again.';
  }

  btn.addEventListener('click', function () {
    var token = getToken();
    if (!token) {
      showSignIn('Purchasing needs a Terraphim account.');
      return;
    }
    btn.disabled = true;
    status.textContent = 'Preparing checkout…';
    fetch(API + '/api/billing/checkout?product=terraphim-proxy', {
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
