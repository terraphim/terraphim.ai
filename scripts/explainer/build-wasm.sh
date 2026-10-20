#!/usr/bin/env bash
# Rebuild the RoleGraph WASM bundle vendored into
# static/explainers/graph-embeddings/wasm/.
#
# The wrapper crate (./rolegraph-wasm/) lives in the terraphim-core
# workspace as crates/terraphim_rolegraph/wasm/ — this script copies the
# vendored source into a core checkout, builds both targets with
# wasm-pack and copies the artefacts back.
#
# Usage: ./scripts/explainer/build-wasm.sh /path/to/terraphim-core
set -euo pipefail

CORE="${1:?path to a terraphim-core checkout}"
SITE="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$CORE/crates/terraphim_rolegraph/wasm"

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

echo "Rebuilt. Re-run: node scripts/explainer/check.js"
