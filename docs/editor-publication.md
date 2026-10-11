# Editor website candidate

The `/editor/` bundle is a hash-admitted preview candidate, not full source-video acceptance. Its immutable source identity and qualification are recorded in `static/editor/release.json`; the independent manifest digest is pinned in the deployment workflow.

Before deployment, verify both source assets and Zola output with that independent digest:

```bash
python3 -m unittest discover -s scripts -p test_import_editor.py -v
python3 scripts/import-editor.py --verify --destination static/editor --manifest-sha256 3e0510de27b93c5aed5018058b55bd82798ad7ed535fd1c25812aef5a0aadc03
zola build
python3 scripts/import-editor.py --verify --destination public/editor --manifest-sha256 3e0510de27b93c5aed5018058b55bd82798ad7ed535fd1c25812aef5a0aadc03
```

Use Zola 0.22.1, matching deployment. A different installed Zola version is not the deployment build.

Import a replacement into a fresh directory using `scripts/import-editor.py --source BUILD --manifest MANIFEST --manifest-sha256 APPROVED_DIGEST --destination NEW_DIRECTORY`. Review source identity, runtime closure and browser output evidence before changing the independent pin. Never derive the expected digest from the mutable deployed receipt during verification.

The current bundle was staged from clean editor commit `949b5252e89814ed294c1a238cef726663873a76`, including the independently reviewed Unicode KG-protected Trim repair. Confirm that this source is admitted to the editor release chain before promoting this website candidate. Deployment and HTTPS/browser acceptance are separate gates. Safari dragging and complete 41-requirement acceptance remain unresolved. A stock Zed capability preview is not custom visual parity; the fork is outside this change.

The how-to uses authored public input and an existing shared KG. New alternatives are document-scoped synonyms. The paired grep synthesis demonstration requires the clients candidate with synonym retrieval, semantic coverage and explicit `--answer` fixes; an older installed binary may behave differently. Configured provider synthesis may send public retrieved text outside the device.

## Public walkthrough media

Six reviewed public MP4 files are served under `/demos/knowledge-work/`. `manifest.json` pins their SHA-256 digests, recorded editor source and editing disclosures. Raw Safari and Zed recordings are excluded. `scripts/test_publication_media.py` verifies the actual publication bytes and required links/disclosures. The homepage links both the editor preview and the walkthrough.

The recorded browser candidate remains `e2ee3ff9f6133cd67cd15533109c8020c20a0cdf`; the later pointer and Unicode normalization repairs are not silently relabelled as recorded. Publication is a public preview, not stable editor/extension release or complete 41-requirement qualification. All eight publication tests, Zola0.22.1 and verification of all132 source/output editor assets passed before publication.

Unicode repair verification:110 native library tests, six original protection tests, eight Unicode regressions, strict native/WASM Clippy, real Chrome Trim reduction, Done ghosts, exact annotated save/reopen and undo/redo. Existing Terraphim normalized term and matcher types are reused; NFC and original grapheme boundary mapping are added. Greek sigma variants are equivalent; general full case folding and Straße/STRASSE transliteration are not claimed. Exact original spelling is retained.

The paced-v2 media edition adds burned-in explanatory text outside the app image and replaces idle-heavy walkthroughs with disclosed chronological cuts and1.5–3× speed changes. Overview77s, Chrome44s, Firefox49s, Safari45s, Zed60s, grep21s. Original footage, source identity and qualification limits remain unchanged. The manifest records every retained source range and output caption interval.
