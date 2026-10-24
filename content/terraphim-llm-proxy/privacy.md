+++
title = "Terraphim Proxy — Privacy Policy"
description = "Privacy policy for the Terraphim Proxy desktop application (cloud.terraphim.desktop)"
date = 2026-10-24
weight = 10

[taxonomies]
categories = ["Legal"]

[extra]
toc = false
+++

**Effective date: 24 October 2026.** Applies to the Terraphim Proxy macOS
application (`cloud.terraphim.desktop`), distributed via the Mac App
Store and direct download.

## The short version

The Terraphim Proxy **application** collects **no data whatsoever**. There
is no account system, no telemetry, no analytics, no crash reporting, and
no third-party tracking SDK in the app. Your credentials never leave your
Mac except inside the requests you deliberately send to the LLM providers
you configured.

Buying a direct download does create a small server-side record — kept by
the Terraphim Skills marketplace, not by the app — described under
*Purchases* below.

## What stays on your device

- **API keys and OAuth tokens** are stored exclusively in the macOS
  Keychain — never in configuration files, never transmitted to
  Terraphim Proxy or any third party.
- **Settings** (provider choices, route pins, keyword remaps and
  synonyms) are stored as a plain file inside the app's sandbox
  container on your Mac.
- **Prompts and completions** pass through the embedded proxy in memory
  and are forwarded only to the upstream providers you configured.
  Terraphim Proxy does not log, persist or transmit them elsewhere.
- **Metrics** shown in the operator dashboard are computed in-process
  and served only on loopback (`127.0.0.1`) listeners bound to your
  machine.

## What leaves your device

Only the requests you send through the proxy, to the LLM providers you
chose — over TLS, bearing the credentials those providers issued to
you. Their handling of that traffic is governed by their own privacy
policies (z.ai, OpenRouter, Groq, Cerebras, Kimi, MiniMax, DeepSeek,
OpenAI, xAI, or any other provider you configure).

## Purchases

**Mac App Store.** The app is a one-time purchase processed entirely by
Apple's App Store. Apple — not Terraphim Proxy — receives and processes
your payment information. The app contains no in-app purchases, no
subscription checks and no licence servers.

**Direct download.** Direct-download purchases are processed by Stripe
via the Terraphim Skills marketplace (`api.terraphim-skills.md`). Stripe
— not Terraphim — receives and processes your payment information. The
marketplace stores the email address on your account, the fact of the
purchase, and which releases you have downloaded; those records are used
solely for entitlement checks and refund adjudication, as described in
the [Refund policy](/terraphim-llm-proxy/refunds/). The application
itself still collects nothing — this record lives entirely on the
marketplace side.

## Permissions the app requests

| Entitlement | Why |
|---|---|
| `app-sandbox` | The app runs sandboxed. |
| `files.user-selected.read-write` | Only files you explicitly choose (e.g. settings export). |
| `network.client` | Outbound calls to your configured LLM providers. |
| `network.server` | Loopback-only listeners for the local proxy endpoint and the dashboard's metrics feed. |

## Contact

Questions, corrections or requests: open an issue on
[GitHub](https://github.com/terraphim/terraphim-ai/issues) or write to
the maintainers via the repository.

If this policy changes, the updated version is published at this URL
before the change ships.
