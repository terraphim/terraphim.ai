+++
title = "Terraphim Proxy — Downloads"
description = "Signed macOS releases of Terraphim Proxy for licensed customers."
weight = 40
template = "page.html"
render = true
+++

Signed macOS builds of Terraphim Proxy, served from the Terraphim Skills
marketplace. Downloads are tied to the account you purchased with — sign
in below with that account, then pick a release. Every artefact is listed
with its SHA-256 so you can verify the download before opening it.

<div id="proxy-download">
  <div id="proxy-dl-banner" class="proxy-dl-banner" role="status" hidden>
    <i class="fa-solid fa-circle-check" aria-hidden="true"></i>
    Purchase confirmed — your downloads are below.
  </div>
  <div id="proxy-dl-notice" aria-live="polite"></div>
  <div id="proxy-dl-wrap">
    <p class="proxy-dl-muted"><i class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Loading releases…</p>
  </div>
</div>
<style>
#proxy-download .proxy-dl-banner {
  border: 1px solid var(--green-dim);
  border-radius: var(--radius-lg);
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  color: var(--green);
}
#proxy-download .proxy-dl-callout {
  border: 1px solid var(--border-bright);
  border-radius: var(--radius-lg);
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  background: oklch(0.72 0.16 70 / 0.06);
}
#proxy-download .proxy-dl-callout.warn { border-color: var(--amber-dim); }
#proxy-download .proxy-dl-muted { color: var(--text-dim); }
#proxy-download .proxy-dl-row-status { margin-top: 0.4rem; font-size: 0.8rem; line-height: 1.5; }
#proxy-download .proxy-dl-row-status code { overflow-wrap: anywhere; }
#proxy-download .proxy-dl-ok { color: var(--green); }
#proxy-download .proxy-dl-err { color: var(--red); }
#proxy-download .proxy-dl-sha { font-size: 0.75rem; }
#proxy-download .proxy-dl-table td code { overflow-wrap: anywhere; }
</style>
<script src="/js/proxy-helpers.js"></script>
<script src="/js/proxy-download.js"></script>
