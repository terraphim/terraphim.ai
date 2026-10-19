# release-update fixtures

Deterministic regression inputs for `scripts/tests/test_update_release.py`.

- `source/` — real files copied verbatim from the merged public source heads:
  website `d1e348d061f103356708e346cdc19c9bd849fc70`,
  terraphim-ai `7f731abc8342ec04216598d4bf59efad2e11c2a9`,
  terraphim-clients `fe0e5a6012cc79fdc4c295e9a0820bcd8935767d`.
- `snapshot/` — captured real GitHub release API responses and stable-v2
  channel manifests from 2026-10-18 (research packet
  `release-updater-cicd-research-20261018`), plus two derived variants
  (`incomplete-channels.json` simulates a partial channel rollout;
  `downgrade.json` simulates an older clients release).

These are recorded inputs for deterministic tests. They are not live
verification; actual CI/CD behaviour is proven separately by real runs.
