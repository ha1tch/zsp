#!/usr/bin/env bash
# release.sh - zsp release hygiene automation, adapted from zenimate's
# scripts/release.sh for a static site rather than a compiled Go binary.
#
# Single-pass release preparation:
#   1. Validate the VERSION string and the matching CHANGELOG entry
#   2. Regenerate zsp_site/ from scratch (VERSION is read live by
#      build_site.py — there is no separate constant to sync, unlike
#      zenimate's pkg/version/version.go)
#   3. Verify the rebuild: no stray .md cross-links, expected page count
#   4. Stage a versioned checkpoint zip under dist/
#
# It never tags or pushes: cutting the git tag is the human's trigger.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VER="$(tr -d ' \t\r\n' < VERSION)"
echo "==> Releasing zsp v${VER}"

# 1. Validate version format (semver MAJOR.MINOR.PATCH) and CHANGELOG entry.
if [[ ! "$VER" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
	echo "release: VERSION '$VER' is not MAJOR.MINOR.PATCH" >&2
	exit 1
fi
if ! grep -q "^## \[${VER}\]" CHANGELOG.md; then
	echo "release: no CHANGELOG.md entry for [${VER}]" >&2
	exit 1
fi

# 2. Regenerate the site. build_site.py reads VERSION directly, so this
#    step is also the sync step.
echo "==> tools/build_site.py"
rm -rf zsp_site
python3 tools/build_site.py

# 3. Verify: no leftover .md cross-links, and a sane page count.
echo "==> checking for stray .md links"
BAD_LINKS="$(grep -rno 'href="[^"]*\.md"' zsp_site/projects/*/index.html zsp_site/projects/*/docs/*.html 2>/dev/null \
   | grep -v 'README\.md' || true)"
if [[ -n "$BAD_LINKS" ]]; then
	echo "release: unexpected .md links survived rendering:" >&2
	echo "$BAD_LINKS" >&2
	exit 1
fi

PAGE_COUNT="$(find zsp_site -name '*.html' | wc -l)"
echo "==> ${PAGE_COUNT} HTML pages generated"
if [[ "$PAGE_COUNT" -lt 30 ]]; then
	echo "release: page count (${PAGE_COUNT}) looks too low — check the build" >&2
	exit 1
fi

# 4. Checkpoint zip of the generated site (not the whole repo — zsp_site/
#    is the publishable artefact).
mkdir -p dist
ZIP="dist/zsp-site-v${VER}.zip"
rm -f "$ZIP"
echo "==> staging checkpoint $ZIP"
zip -q -r "$ZIP" zsp_site

echo "==> Done. Artefacts in dist/:"
ls -la dist/
echo
echo "Next: review, then 'git tag v${VER}' to trigger the release."
