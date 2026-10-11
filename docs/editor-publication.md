# Editor website candidate

The `/editor/` bundle is a hash-admitted preview candidate, not full source-video acceptance. Its immutable source identity and qualification are recorded in `static/editor/release.json`; the independent manifest digest is pinned in the deployment workflow.

Before deployment, verify both source assets and Zola output with that independent digest:

```bash
python3 -m unittest discover -s scripts -p test_import_editor.py -v
python3 scripts/import-editor.py --verify --destination static/editor --manifest-sha256 e972d1c779cca709ff1a1c8e0b0c543b855d82d7e6fa26fbf14414f84c6fb1d0
zola build
python3 scripts/import-editor.py --verify --destination public/editor --manifest-sha256 e972d1c779cca709ff1a1c8e0b0c543b855d82d7e6fa26fbf14414f84c6fb1d0
```

Use Zola 0.22.1, matching deployment. A different installed Zola version is not the deployment build.

Import a replacement into a fresh directory using `scripts/import-editor.py --source BUILD --manifest MANIFEST --manifest-sha256 APPROVED_DIGEST --destination NEW_DIRECTORY`. Review source identity, runtime closure and browser output evidence before changing the independent pin. Never derive the expected digest from the mutable deployed receipt during verification.

The current bundle was staged from clean editor commit `4050ac9a35e1255ebc3f1d7cd50eb0dd97059730`, including the Unicode KG-protected Trim repair and reviewed document-synonym export. Confirm that this source is admitted to the editor release chain before promoting this website candidate. Deployment and HTTPS/browser acceptance are separate gates. Safari dragging and complete 41-requirement acceptance remain unresolved. A stock Zed capability preview is not custom visual parity; the fork is outside this change.

The new synonym-search how-to uses authored public input, then creates Concern as an alternative to Risk and downloads the actual document synonym graph. The CLI consumes those exact downloaded bytes. The older host walkthroughs retain their existing shared-KG demonstration and recorded limitations. The paired grep synthesis demonstration requires the clients candidate with synonym retrieval, semantic coverage and explicit `--answer` fixes; an older installed binary may behave differently. Configured provider synthesis may send public retrieved text outside the device.

## Public walkthrough media

Six reviewed public MP4 files are served under `/demos/knowledge-work/`. `manifest.json` pins their SHA-256 digests, recorded editor source and editing disclosures. Raw Safari and Zed recordings are excluded. `scripts/test_publication_media.py` verifies the actual publication bytes and required links/disclosures. The homepage links both the editor preview and the walkthrough.

The recorded browser candidate remains `e2ee3ff9f6133cd67cd15533109c8020c20a0cdf`; the later pointer and Unicode normalization repairs are not silently relabelled as recorded. Publication is a public preview, not stable editor/extension release or complete 41-requirement qualification. All eight publication tests, Zola0.22.1 and verification of all132 source/output editor assets passed before publication.

Unicode repair verification:110 native library tests, six original protection tests, eight Unicode regressions, strict native/WASM Clippy, real Chrome Trim reduction, Done ghosts, exact annotated save/reopen and undo/redo. Existing Terraphim normalized term and matcher types are reused; NFC and original grapheme boundary mapping are added. Greek sigma variants are equivalent; general full case folding and Straße/STRASSE transliteration are not claimed. Exact original spelling is retained.

The paced-v2 media edition adds burned-in explanatory text outside the app image and replaces idle-heavy walkthroughs with disclosed chronological cuts and1.5–3× speed changes. Overview77s, Chrome44s, Firefox49s, Safari45s, Zed60s, grep21s. Original footage, source identity and qualification limits remain unchanged. The manifest records every retained source range and output caption interval.

## Focused synonym-search story

The 80-second story at `/how-tos/synonym-search/` supersedes the previous overview as the homepage demo. It records editor `4050ac9a35e1255ebc3f1d7cd50eb0dd97059730` and clients `f0410af`, with natural-rate British female synthetic narration. Editor-created graph and clean text are actual downloads; identical chunks are verified with synthesis off/on. CLI JSON fields are presented readably with original strings retained. See `/demos/synonym-search/manifest.json` for the media and artifact identities.
