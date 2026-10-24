+++
title = "Terraphim Proxy — Refund Policy"
description = "How refunds work for direct-download purchases of Terraphim Proxy."
weight = 30
template = "page.html"
render = true
+++

**Effective upon launch of direct-download sales.**

This policy covers **direct downloads purchased on terraphim.ai**.
Purchases made through the Mac App Store are refunded by Apple under the
[Apple Media Services Terms and Conditions](https://www.apple.com/legal/internet-services/itunes/); Apple,
not Terraphim, decides those refunds.

## The short version

**Within 14 days of purchase you can get a full refund provided no
release has been downloaded. Once your account has downloaded a release,
the sale is final — unless the proxy does not function.**

This is the same shape as Steam's rule for games: a refund is available
while the product is untouched, and the usage measurement is what makes
the rule fair to enforce. Steam measures playtime; we measure the moment
our service first serves the download.

## Why we do it this way

A signed application bundle cannot be returned once it is copied to your
Mac — there is no undo. The download is the honest line between
"bought but not taken" and "taken", and it is a line we can measure: the
service records the first time it serves a release download request to
your account, and that record is the only thing the refund rule
consults.

We considered the alternative — a blanket 14-day window — and rejected
it, because it would let anyone buy, download every release, and refund.
That pattern subsidises itself out of the purchase price of everyone
else.

## What you get back

| Situation | Outcome |
| --- | --- |
| Within 14 days of purchase, **no release downloaded** | Full refund, no questions asked |
| **Any release downloaded**, proxy functioning as documented | Final sale — no refund |
| **Any release downloaded**, proxy does not function | Full refund — see *When the proxy does not function* below |
| More than 14 days after purchase, no download | Not automatic. Ask anyway — see *Outside the rules* below. |

*"Downloaded" is counted when our service begins delivering the release
to your account — the request is recorded when delivery starts, not when
the bytes finish. A failed or interrupted delivery does not count as a
completed download for refund purposes (see *Downloads were broken*
below), and where the record is ambiguous we treat it in your favour.*

Refunds go back to the original payment method through Stripe. Card
refunds usually appear within 5–10 business days, depending on your bank
— that part is outside our control.

When a refund is issued, download access ends: the entitlement is
revoked and release downloads stop working.

## When the proxy does not function

"Not functioning" means the software itself is defective — for example:

- The app fails to install or launch on a supported macOS version.
- The embedded proxy does not bind its port or does not forward requests
  to a correctly configured provider.
- A documented feature — routing, remaps, synonyms, dashboard,
  autostart — is absent or broken in the release you downloaded.

It does not cover upstream problems outside our control: a provider
outage, an exhausted provider quota, a network block on your side, or a
model behaving unexpectedly. Those are the provider's service, not ours.

Because the app collects no telemetry, we cannot see the failure
ourselves — when you report a defect we may ask for the app version, your
macOS version, and the error or behaviour you see. If the software
genuinely does not work, we will refund it. You should not have to argue
the point.

## How to ask

Email **[engineering@terraphim.ai](mailto:engineering@terraphim.ai)**
with the email address on the account you purchased with. For a defect
claim, include the app version and macOS version.

We aim to process refund requests within **3 business days**.

## Outside the rules

Outside the automatic cases a refund is at our discretion, but the door
is not closed. We will look seriously at:

- **You were charged twice**, or charged without completing a purchase.
  Always refunded.
- **Downloads were broken** — the entitlement was granted but releases
  would not download. Our fault; refunded.
- **A release was withdrawn** after you bought it for that version
  specifically.

## What we record

To make this policy enforceable we keep a server-side record, tied to
your purchase account, of **when our service first serves a release
download request to you** — the version, the asset and the time. That is
the entire record — the app itself collects no telemetry and reports
nothing back. Purchase and download records are covered in the
[Privacy policy](/terraphim-llm-proxy/privacy/).

## Your statutory rights

If you are a consumer in the UK or EU you have a legal right to cancel a
distance contract within 14 days. For digital content that right is lost
once downloading begins **if** you asked for immediate access and
acknowledged losing the right — which is why checkout asks you to
confirm exactly that before a download becomes available.

Nothing in this policy affects your statutory rights.

## Fair use

We will refuse refunds where the pattern is clearly abusive — for
example repeatedly purchasing, downloading, and refunding, or
redistributing downloaded releases. Because downloads are recorded we
can see this pattern; purchase of a licence does not transfer
redistribution rights.

## Changes

We may change this policy. Any change applies to purchases made after
the change, never retrospectively. Material changes will be notified by
email or through the site.
