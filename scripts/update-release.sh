#!/usr/bin/env bash
# Update release links across managed site fields and the README downloads
# region. Delegates to scripts/update_release.py (Python standard library);
# the exit status is propagated unchanged.
#
# Files updated (active fields only; history and development version are
# preserved):
#   config.toml              - release_version
#   content/releases.md      - active Latest Release heading/date/links/examples
#   content/docs/installation.md - active download URLs and version examples
#   content/docs/quickstart.md   - active version strings in examples (none today)
#   themes/WarpDrive/templates/index.html - default() fallbacks
#   themes/WarpDrive/static/js/site.js    - JS fallback version
#   README.md                - managed downloads region (marker-guarded)
#
# Usage: ./scripts/update-release.sh [--check] [--snapshot F] [--receipt F]
#          [--target website|terraphim-ai|terraphim-clients] [--root DIR]
#          [--timeout SECONDS]
# Requires: python3. Optional: gh/GITHUB_TOKEN for authenticated API reads.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/update_release.py" "$@"
