#!/usr/bin/env bash
# Rebuild the RoleGraph WASM bundle vendored into
# static/explainers/graph-embeddings/wasm/.
#
# The wrapper crate (./rolegraph-wasm/) lives in the terraphim-core
# workspace as crates/terraphim_rolegraph/wasm/ — this script copies the
# vendored source into a core checkout, builds both targets with
# wasm-pack and copies the artefacts back. Build provenance (core
# commit, tool versions, artefact hashes) is recorded in
# scripts/explainer/wasm-manifest.json.
#
# Usage: ./scripts/explainer/build-wasm.sh /path/to/terraphim-core
set -euo pipefail

CORE="${1:?path to a terraphim-core checkout}"
SITE="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$CORE/crates/terraphim_rolegraph/wasm"

CORE_COMMIT="$(git -C "$CORE" rev-parse HEAD)"
CORE_DIRTY="$(git -C "$CORE" status --porcelain -- crates/terraphim_rolegraph crates/terraphim_automata crates/terraphim_types | head -5)"
if [[ -n "$CORE_DIRTY" ]]; then
  echo "warning: terraphim-core checkout has uncommitted changes under the algorithm crates:" >&2
  echo "$CORE_DIRTY" >&2
fi

# The rolegraph Cargo.toml target-gates tokio/automata features for
# wasm32; this vendored copy assumes that change is present.
mkdir -p "$DEST"
cp -R "$SITE/scripts/explainer/rolegraph-wasm/"* "$DEST/"

(cd "$DEST" && wasm-pack build --target web --out-dir pkg-web --release)
(cd "$DEST" && wasm-pack build --target nodejs --out-dir pkg-node --release)

cp "$DEST/pkg-web/terraphim_rolegraph_wasm.js" \
   "$DEST/pkg-web/terraphim_rolegraph_wasm_bg.wasm" \
   "$DEST/pkg-web/terraphim_rolegraph_wasm.d.ts" \
   "$SITE/static/explainers/graph-embeddings/wasm/"
cp "$DEST/pkg-node/terraphim_rolegraph_wasm.js" \
   "$DEST/pkg-node/terraphim_rolegraph_wasm_bg.wasm" \
   "$SITE/scripts/explainer/wasm-node/"

WASM_SHA="$(shasum -a 256 "$DEST/pkg-web/terraphim_rolegraph_wasm_bg.wasm" | awk '{print $1}')"
RUSTC="$(rustc --version)"
WASM_PACK="$(wasm-pack --version | awk '{print $2}')"

cat > "$SITE/scripts/explainer/wasm-manifest.json" <<EOF
{
  "core_commit": "$CORE_COMMIT",
  "built_at": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "rustc": "$RUSTC",
  "wasm_pack": "$WASM_PACK",
  "wasm_sha256": "$WASM_SHA",
  "note": "terraphim_rolegraph must have the wasm32 target-gated tokio/automata deps"
}
EOF

echo "Rebuilt (core $CORE_COMMIT, wasm sha256 ${WASM_SHA:0:12}...)."
echo "Re-run: node scripts/explainer/check.js"
