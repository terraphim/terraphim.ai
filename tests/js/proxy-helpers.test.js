/* Tests for the pure helpers shared by the Terraphim Proxy buy/download
   pages (static/js/proxy-helpers.js). Node built-ins only — no npm deps,
   no DOM mocks: the helpers are pure functions over strings/values. */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const H = require('../../static/js/proxy-helpers.js');

test('esc neutralises a script-tag payload', () => {
  const out = H.esc('<script>alert("x")</script>');
  assert.equal(out, '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;');
  assert.ok(!out.includes('<') && !out.includes('>'));
});

test('esc neutralises attribute-injection payloads', () => {
  const out = H.esc('"><img src=x onerror=alert(1)>');
  assert.equal(out, '&quot;&gt;&lt;img src=x onerror=alert(1)&gt;');
  // Safe inside a double-quoted title attribute.
  assert.ok(!out.includes('"') && !out.includes('<'));
});

test('esc handles apostrophes, ampersands and non-strings', () => {
  assert.equal(H.esc("o'neil & <b>"), 'o&#39;neil &amp; &lt;b&gt;');
  assert.equal(H.esc(42), '42');
  assert.equal(H.esc(null), '');
  assert.equal(H.esc(undefined), '');
  // Ampersand must be escaped first — already-escaped input stays safe.
  assert.equal(H.esc('&lt;'), '&amp;lt;');
});

test('normaliseReleases accepts the bare array shape', () => {
  const list = [{ version: '0.1.45' }];
  assert.equal(H.normaliseReleases(list), list);
});

test('normaliseReleases accepts the wrapped {releases: [...]} shape', () => {
  const list = [{ version: '0.1.45' }];
  assert.deepEqual(H.normaliseReleases({ releases: list }), list);
});

test('normaliseReleases returns [] for every other shape', () => {
  assert.deepEqual(H.normaliseReleases(null), []);
  assert.deepEqual(H.normaliseReleases(undefined), []);
  assert.deepEqual(H.normaliseReleases({}), []);
  assert.deepEqual(H.normaliseReleases({ releases: 'nope' }), []);
  assert.deepEqual(H.normaliseReleases('[]'), []);
});

test('downloadUrl encodes version and asset path segments', () => {
  assert.equal(
    H.downloadUrl('0.1.45', 'Terraphim-Proxy-0.1.45-arm64.dmg'),
    'https://api.terraphim-skills.md/api/products/terraphim-proxy/releases/0.1.45/Terraphim-Proxy-0.1.45-arm64.dmg'
  );
  // A version containing '+' or '/' must not corrupt the path.
  const url = H.downloadUrl('1.0.0-beta+exp', 'a/b.dmg');
  assert.ok(url.endsWith('/releases/1.0.0-beta%2Bexp/a%2Fb.dmg'));
});

test('signInUrl carries an encoded absolute return_to', () => {
  const back = 'https://terraphim.ai/terraphim-llm-proxy/download/?checkout=success';
  const url = H.signInUrl(back);
  assert.equal(
    url,
    'https://api.terraphim-skills.md/auth/oauth/github?return_to=' +
      encodeURIComponent(back)
  );
});

test('humanSize formats byte counts', () => {
  assert.equal(H.humanSize(0), '0 B');
  assert.equal(H.humanSize(512), '512 B');
  assert.equal(H.humanSize(1024), '1.0 KB');
  assert.equal(H.humanSize(16457327), '15.7 MB');
  assert.equal(H.humanSize(3 * 1024 * 1024 * 1024), '3.0 GB');
  // Beyond GB stays pinned to the last unit.
  assert.equal(H.humanSize(5 * 1024 * 1024 * 1024 * 1024), '5120.0 GB');
});

test('humanSize rejects invalid input', () => {
  assert.equal(H.humanSize(-1), '—');
  assert.equal(H.humanSize('not-a-number'), '—');
  assert.equal(H.humanSize(null), '0 B'); // Number(null) is 0 — a real size.
  assert.equal(H.humanSize(undefined), '—');
});

test('fmtDate renders en-GB short dates and tolerates junk', () => {
  assert.equal(H.fmtDate('2026-10-24T15:21:00Z'), '24 Oct 2026');
  assert.equal(H.fmtDate(''), '—');
  assert.equal(H.fmtDate(undefined), '—');
  // Invalid-but-non-empty input passes through unchanged.
  assert.equal(H.fmtDate('soon'), 'soon');
});

test('tokenFromLocation reads #token=<jwt> from the fragment', () => {
  assert.equal(H.tokenFromLocation({ hash: '#token=abc.def-ghi', search: '' }), 'abc.def-ghi');
  assert.equal(
    H.tokenFromLocation({ hash: '#checkout=done&token=zzz', search: '' }),
    'zzz'
  );
});

test('tokenFromLocation reads ?token=<jwt> from the query', () => {
  assert.equal(H.tokenFromLocation({ hash: '', search: '?token=qq' }), 'qq');
  assert.equal(H.tokenFromLocation({ hash: '', search: '?a=1&token=qq' }), 'qq');
  // Fragment wins over query when both are present.
  assert.equal(
    H.tokenFromLocation({ hash: '#token=frag', search: '?token=query' }),
    'frag'
  );
});

test('tokenFromLocation returns null without a token', () => {
  assert.equal(H.tokenFromLocation({ hash: '', search: '' }), null);
  assert.equal(H.tokenFromLocation({ hash: '#section', search: '?checkout=success' }), null);
  assert.equal(H.tokenFromLocation(null), null);
  assert.equal(H.tokenFromLocation(undefined), null);
  // A lookalike param name is not a token.
  assert.equal(H.tokenFromLocation({ hash: '#mytoken=x', search: '' }), null);
});

test('stripTokenFromHash removes only the token param', () => {
  assert.equal(H.stripTokenFromHash('#token=abc'), '');
  assert.equal(H.stripTokenFromHash('#token=abc&checkout=done'), 'checkout=done');
  assert.equal(H.stripTokenFromHash('#checkout=done&token=abc'), 'checkout=done');
  assert.equal(H.stripTokenFromHash('#your-keys-your-costs'), 'your-keys-your-costs');
  assert.equal(H.stripTokenFromHash(''), '');
});
