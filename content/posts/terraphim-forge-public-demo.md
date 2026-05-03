+++
title="Try Terraphim Forge: public demo open at demo.terraphim-forge.com"
date=2026-05-03
[taxonomies]
categories = ["Product"]
tags = ["terraphim-forge", "gitea", "firecracker", "cargo-registry", "demo", "self-hosted"]
[extra]
toc = true
comments = true
+++

We just opened the public demo of **Terraphim Forge** at [demo.terraphim-forge.com](https://demo.terraphim-forge.com). It is a free, anonymous, self-serve instance of our Gitea fork running on Firecracker microVMs. Sign up, push code, publish a Cargo crate, run our PageRank-based issue triage tool. Everything resets at 04:00 UTC daily, so bring nothing irreplaceable.

<!-- more -->

## What it is

Terraphim Forge is a pay-first SaaS that hands a paying customer their own Gitea-on-Firecracker microVM at `<their-id>.terraphim-forge.com` within ~30 seconds of completing checkout. The persistent paid tiers will go on the price page later this week; the public demo is what you can try right now without paying anything.

The demo is one VM, public-facing, with anonymous registration enabled. Four canonical repositories are seeded on every refresh:

- [`terraphim/gitea`](https://demo.terraphim-forge.com/terraphim/gitea) -- our Gitea fork (the binary that runs inside every customer VM)
- [`terraphim/gitea-robot`](https://demo.terraphim-forge.com/terraphim/gitea-robot) -- the `gtr` CLI for PageRank-driven issue triage
- [`terraphim/terraphim-skills`](https://demo.terraphim-forge.com/terraphim/terraphim-skills) -- skill packages that drive our agent workflows
- [`terraphim/terraphim-ai`](https://demo.terraphim-forge.com/terraphim/terraphim-ai) -- the main Terraphim platform repo (read-only, archived; ~390 MB)

You can fork any of them into your demo account, push to your forks, and use the platform exactly as a paying customer would.

## What you can actually do on it

### Push code, including LFS

```sh
# Sign up at https://demo.terraphim-forge.com/user/sign_up first.
git clone https://demo.terraphim-forge.com/<you>/<repo>
cd <repo>
git lfs track '*.bin'
git add .gitattributes some.bin && git commit -m "with LFS"
git push
```

LFS objects land in our SeaweedFS-backed S3 store; the demo bucket gets wiped at 04:00 UTC along with the VM, so do not use this for anything you care about.

### Publish a Cargo crate to the per-user registry

Every demo user gets their own Cargo registry endpoint at `/api/packages/<your-user>/cargo`. Generate a Personal Access Token in the Gitea UI (Settings -> Applications, scopes `read:package`, `write:package`), then:

```sh
mkdir my-crate && cd my-crate
cargo init --lib
# minimal Cargo.toml: name, version, edition, license
cargo publish --registry-url \
    "https://demo.terraphim-forge.com/api/packages/<you>/cargo" \
    --token "Bearer <your-pat>"
```

The `.crate` lands in SeaweedFS, becomes downloadable from the sparse index. We verified the round-trip end-to-end (publish, sparse-index lookup, presigned-URL download, sha256 match) on a freshly-provisioned VM the day we opened the demo.

### Run gitea-robot against the demo

`gtr` is our PageRank-based issue triage tool. It scores issues by how many other issues they unblock, so you fix the high-leverage ones first.

```sh
git clone https://demo.terraphim-forge.com/terraphim/gitea-robot
cd gitea-robot
bun install
export GITEA_URL=https://demo.terraphim-forge.com
export GITEA_TOKEN=<your-pat>
./bin/gtr triage --owner <you> --repo <your-repo>
./bin/gtr ready --owner <you> --repo <your-repo>
./bin/gtr graph --owner <you> --repo <your-repo>
```

Read-only browsing of `terraphim/gitea-robot` works without a login.

## The catch

> The demo resets every day at 04:00 UTC. Your repos, your packages, your account, the admin password -- all gone, all replaced. We rebuild from a known-good golden rootfs, re-mirror the four seeded repos from canonical Gitea, and rotate the admin password from 1Password.

This is deliberate. Twenty-four-hour lifetime makes the demo a poor target for spam, persistence-style abuse, or content-takedown drama. It also keeps the surface honest: you can never end up trusting a piece of state that turns out to have been there for six months by accident.

If you want a Forge that does not reset, that is the paid tier; the price page goes up later this week.

## How it is built

Each demo session and each paying customer gets their own [Firecracker](https://firecracker-microvm.github.io/) microVM. Boot time is ~330 ms total (network configure, drive attach, kernel boot, instance start). The full pay-first chain -- landing -> Stripe checkout -> webhook -> microVM provisioned -> admin user created -> Caddy route added -> customer logged in and pushing code -- runs in ~30 seconds end-to-end.

A few of the load-bearing engineering decisions:

**Per-VM rootfs (copy-on-write).** Firecracker exposes the host file as a raw `virtio-blk` device with no isolation. Two VMs sharing the same path with `is_read_only: false` will silently corrupt each other's ext4+SQLite. We copy the golden image to `/var/lib/firecracker/images/instances/<vm_id>.rootfs` before `add_drive` so each VM gets its own private writable disk. Cleanup happens automatically on stop.

**`forge.fqdn=` kernel arg.** Each VM boots with `forge.fqdn=<user>.terraphim-forge.com` in `/proc/cmdline`. A systemd `ExecStartPre` hook in the rootfs reads it and patches `app.ini` so Gitea's `DOMAIN` and `ROOT_URL` are right before the daemon starts. Without it, every public URL would be `https://localhost/` and the customer experience would be broken in ways that take a while to track down.

**Stable demo password from 1Password.** The refresh job reads `op://TerraphimPlatform/forge-demo/password` every cycle and applies it to the freshly-provisioned admin user via `gitea admin user change-password`. No more lost demo creds.

**Caddy on-demand TLS.** Each customer subdomain gets its own ACME cert on first request; Caddy reuses it across daily refreshes since the SAN does not change.

**SeaweedFS for everything that is not git.** LFS, packages (Cargo registry, generic uploads), and repo archives all go to a SeaweedFS S3 bucket. Same bucket survives demo refreshes (we wipe per-user namespaces, not the whole bucket).

The VM image build (`gitea-vm-image`) and the control plane (`firecracker-rust`) are both Rust. The control plane is `fcctl-web` + `fcctl-core`, the latter is the Firecracker driver and the former is the Stripe-aware web service that wires customer signup to VM provisioning.

## Where it is going

Short term:

- **Paid persistent tiers** at fixed monthly pricing -- one VM that does not reset, plus larger sizes.
- **Cargo registry as a first-class product** -- not just per-customer, but team registries with shared tokens and crate visibility controls.
- **Closed-source git mirrors** -- pull a private repo from another forge into your Forge VM, get all of Gitea's Actions, Issues, Wiki on top of it.

Medium term:

- **Multi-region**. Right now the demo and customer VMs all run on one bigbox in Falkenstein.
- **GitHub Actions runner integration** -- bring your own runner, point it at your Forge.

If you want a particular integration, ping us on the demo (open an issue in any repo there) or send us a note on social — we will be opening a public Forge tracker as the source repos go public.

## Source code

The Rust control plane is being prepared for public release; the source repository will be opened up alongside this demo over the next few days. The four canonical repositories are currently visible *on the demo itself* (see the links earlier in this post), and a fork of our Gitea fork is one of them, so you can already read the patches we run by signing up on the demo and browsing `terraphim/gitea`.

When the public release lands, the URLs will be:

- Control plane: `github.com/terraphim/firecracker-rust`
- VM image build: `git.terraphim.cloud/terraphim/gitea-vm-image`
- Ops scripts (refresh, seed, systemd units): `git.terraphim.cloud/terraphim/terraphim-forge`
- Our Gitea fork: `git.terraphim.cloud/terraphim/gitea`

Follow [@terraphim_ai](https://twitter.com/terraphim_ai) for the public-release announcement.

## Try it

[demo.terraphim-forge.com](https://demo.terraphim-forge.com)

If you break it, we will see it in the next refresh and fix it. If you build something cool on it, tag [@terraphim_ai](https://twitter.com/terraphim_ai) and we will boost it.
