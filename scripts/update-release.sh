#!/usr/bin/env bash
# Fetch the latest GitHub release and update all version references site-wide.
# Run before `zola build` to keep release links current.
#
# Files updated:
#   config.toml              - release_version
#   content/releases.md      - version headings and date
#   content/docs/installation.md - download URLs and version comments
#   content/docs/quickstart.md   - version strings in example output
#   themes/WarpDrive/templates/index.html - default() fallbacks
#   themes/WarpDrive/static/js/site.js    - JS fallback version
#
# Usage: ./scripts/update-release.sh
# Requires: gh (GitHub CLI), sed

set -euo pipefail

REPO="terraphim/terraphim-ai"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG="$ROOT_DIR/config.toml"
RELEASES_MD="$ROOT_DIR/content/releases.md"
INSTALL_MD="$ROOT_DIR/content/docs/installation.md"
QUICKSTART_MD="$ROOT_DIR/content/docs/quickstart.md"
INDEX_HTML="$ROOT_DIR/themes/WarpDrive/templates/index.html"
SITE_JS="$ROOT_DIR/themes/WarpDrive/static/js/site.js"

# Fetch latest release from GitHub
LATEST=$(gh api "repos/$REPO/releases/latest" --jq '.tag_name' 2>/dev/null)
if [ -z "$LATEST" ]; then
  echo "ERROR: Could not fetch latest release from GitHub" >&2
  exit 1
fi

# Strip leading 'v' for the version number
VERSION="${LATEST#v}"
RELEASE_DATE=$(gh api "repos/$REPO/releases/latest" --jq '.published_at[:10]' 2>/dev/null)
RELEASE_DATE_PRETTY=$(date -j -f "%Y-%m-%d" "$RELEASE_DATE" "+%-d %B %Y" 2>/dev/null || echo "$RELEASE_DATE")

# Read current version from config.toml
CURRENT=$(grep '^release_version' "$CONFIG" | sed 's/.*= *"\(.*\)"/\1/')

if [ "$CURRENT" = "$VERSION" ]; then
  echo "Already at latest: v$VERSION"
  exit 0
fi

echo "Updating release: v$CURRENT -> v$VERSION (released $RELEASE_DATE_PRETTY)"

# Update config.toml
sed -i '' "s/^release_version = \".*\"/release_version = \"$VERSION\"/" "$CONFIG"

# Update releases.md: version references and date
sed -i '' "s/Latest Release: v[0-9][0-9.]*/Latest Release: v$VERSION/" "$RELEASES_MD"
sed -i '' "s/Latest Stable:\*\* v[0-9][0-9.]*/Latest Stable:** v$VERSION/" "$RELEASES_MD"
sed -i '' "s/\*\*Released:\*\* .*/\*\*Released:\*\* $RELEASE_DATE_PRETTY/" "$RELEASES_MD"

# Update installation.md and quickstart.md: replace old version in download URLs and comments
for f in "$INSTALL_MD" "$QUICKSTART_MD" "$RELEASES_MD"; do
  if [ -f "$f" ]; then
    sed -i '' "s/$CURRENT/$VERSION/g" "$f"
  fi
done

# Update index.html template: default() fallback values
if [ -f "$INDEX_HTML" ]; then
  sed -i '' "s/$CURRENT/$VERSION/g" "$INDEX_HTML"
fi

# Update site.js: JS fallback version
if [ -f "$SITE_JS" ]; then
  sed -i '' "s/$CURRENT/$VERSION/g" "$SITE_JS"
fi

echo "Updated all version references: v$CURRENT -> v$VERSION"
