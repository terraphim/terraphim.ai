# Editor website candidate

The `/editor/` bundle is a hash-admitted preview candidate, not full source-video acceptance. Its immutable source identity and qualification are recorded in `static/editor/release.json`; the independent manifest digest is pinned in the deployment workflow.

Before deployment, verify both source assets and Zola output with that independent digest:

```bash
python3 -m unittest discover -s scripts -p test_import_editor.py -v
python3 scripts/import-editor.py --verify --destination static/editor --manifest-sha256 f9b04aabeafb9c304ad192635bd5c586da961e798e96c73df012084ca9662cdf
zola build
python3 scripts/import-editor.py --verify --destination public/editor --manifest-sha256 f9b04aabeafb9c304ad192635bd5c586da961e798e96c73df012084ca9662cdf
```

Use Zola 0.22.1, matching deployment. A different installed Zola version is not the deployment build.

Import a replacement into a fresh directory using `scripts/import-editor.py --source BUILD --manifest MANIFEST --manifest-sha256 APPROVED_DIGEST --destination NEW_DIRECTORY`. Review source identity, runtime closure and browser output evidence before changing the independent pin. Never derive the expected digest from the mutable deployed receipt during verification.

The current bundle was staged from the clean editor demo snapshot `8659ccf2967518585ec20dd8962a2ca4413126ad`. Confirm that this source is admitted to the editor release chain before promoting this website candidate. Deployment and HTTPS/browser acceptance are separate gates. Safari dragging and complete 41-requirement acceptance remain unresolved. A stock Zed capability preview is not custom visual parity; the fork is outside this change.

The how-to uses authored public input and an existing shared KG. New alternatives are document-scoped synonyms. The paired grep synthesis demonstration requires the clients candidate with synonym retrieval, semantic coverage and explicit `--answer` fixes; an older installed binary may behave differently. Configured provider synthesis may send public retrieved text outside the device.
