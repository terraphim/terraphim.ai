+++
title = "Terraphim Proxy"
description = "One menu-bar proxy for every LLM provider — intelligent graph-embedding routing, Keychain credentials, and a live operator dashboard"
weight = 20
sort_by = "weight"

[extra]
toc = true
+++

**Terraphim Proxy** is a menu-bar app for macOS that turns all of your AI
provider subscriptions and API keys into a single, intelligent,
OpenAI-compatible endpoint on your machine.

## Bring your own providers

Add z.ai, OpenRouter, Groq, Cerebras, Kimi, MiniMax or DeepSeek with an
API key, or sign in to OpenAI Codex and xAI with OAuth — no keys to
paste. Credentials and tokens live in the macOS Keychain, never in
config files.

## Route by intent, not by model name

Terraphim Proxy builds a knowledge graph over your prompt — graph-embedding
keyword detection recognises requests to review, explain, plan, search
or debug — then picks the model you pinned for that scenario. Remap any
keyword to a different capability and define your own synonyms; changes
apply to the running proxy instantly, no restart.

## Watch it work

A dedicated operator dashboard shows the live route chain, per-provider
latency, token throughput and cache hits. Start and stop the proxy,
switch the default route (auto, fastest, cheapest or any provider pin)
straight from the menu bar.

## Your keys, your costs

A single one-time purchase unlocks the app — no subscription, no seat
limits, no renewal. Upstream usage is billed by your own providers at
their rates; Terraphim Proxy never marks up a token. Intelligent scenario
routing sends each prompt to the cheapest model that can handle it —
published routing research shows cost reductions of over 2x at ~95% of
flagship quality — so the app pays for itself out of saved tokens.
Every listener is loopback-only; nothing leaves your machine except the
requests you send to your providers.

<div class="proxy-buy">
  <div class="proxy-buy-actions">
    <button type="button" class="btn btn-primary" id="proxy-buy-btn">
      <i class="fa-solid fa-cart-shopping" aria-hidden="true"></i>
      Buy — $15
    </button>
    <a class="btn btn-ghost" href="/terraphim-llm-proxy/download/">
      <i class="fa-solid fa-download" aria-hidden="true"></i>
      Downloads
    </a>
  </div>
  <p id="proxy-buy-status" role="status" aria-live="polite" class="proxy-buy-status"></p>
  <p class="proxy-buy-caption">One-time purchase &middot; macOS &middot; <a href="/terraphim-llm-proxy/refunds/">Refund policy</a></p>
</div>
<style>
.proxy-buy-actions { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; margin-bottom: 0.5rem; }
.proxy-buy-status { font-size: 0.85rem; color: var(--text-dim); margin: 0.5rem 0 0; }
.proxy-buy-status:empty { margin: 0; }
.proxy-buy-caption { font-size: 0.8rem; color: var(--text-dim); margin: 0.25rem 0 0; }
</style>
<script src="/js/proxy-buy.js"></script>

## Links

- [Downloads](/terraphim-llm-proxy/download/)
- [Privacy policy](/terraphim-llm-proxy/privacy/)
- [Refund policy](/terraphim-llm-proxy/refunds/)
- [Support — GitHub issues](https://github.com/terraphim/terraphim-ai/issues)
- [Source — terraphim-llm-proxy](https://github.com/terraphim/terraphim-llm-proxy)
