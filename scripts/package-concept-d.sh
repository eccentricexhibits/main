#!/usr/bin/env bash
# Builds a standalone handoff zip of Concept D ("Spotlight") only, into handoff-zips/ (ignored by git):
# the files D needs to render and rebuild, its 8 PNG frames, a D-only review PDF, the D handoff notes and the
# brand, copy and design sources behind it. The PNGs and PDF are rebuilt inside the staged copy, which proves the
# package is self-contained; the PNGs must match the approved ones in exports/.
#   bash scripts/package-concept-d.sh
set -euo pipefail
cd "$(dirname "$0")/.."
NAME=remarkable-2027-concept-d
OUT=handoff-zips
STAGE="$OUT/stage/$NAME"
LIMIT_MB=25
rm -rf "$OUT/stage" "$OUT/$NAME.zip" && mkdir -p "$STAGE"

FILES=(
  package.json package-lock.json .gitignore
  scripts/export.mjs scripts/pages.mjs
  brand/tokens.css fonts/Karbon-Regular.otf fonts/Karbon-Medium.otf fonts/Karbon-Semibold.otf
  content/copy.json content/COPY-CHANGES.md
  mockups/shared/render.js mockups/shared/base.css
  mockups/concept-d/concept.js mockups/concept-d/concept.css
  mockups/concept-d/index.html mockups/concept-d/agenda.html mockups/concept-d/speakers.html mockups/concept-d/faq.html
  # Every asset D's pages load (collected by rendering all four pages at both widths), plus the colour logo for the PDF cover
  assets/brand-elements/vector-arrow-magenta.svg assets/brand-elements/vector-arrow-extended-magenta.svg
  # The home page with the previous ("stage") hero, kept on file
  exports/archive/concept-d-home-desktop-stage-hero.png exports/archive/concept-d-home-mobile-stage-hero.png
  assets/logos/logo-bilingual-knockout-white.png assets/logos/logo-bilingual-colour.png
  assets/funders/canada.png assets/funders/ontario.png assets/funders/cifar.png
  assets/social-icons/x-white.png assets/social-icons/bluesky-white.png
  assets/speakers/stock-headshot-0{1,2,3,4,5,6}.jpg
  assets/photos-2026/{attendees-group-photo,audience-listening,auditorium-crowd,auditorium-fireside-screens}.jpg
  assets/photos-2026/{auditorium-wide-stage,executive-breakfast-networking,executive-breakfast-panel}.jpg
  assets/photos-2026/{networking-hallway,posters-conversation,registration-desk,stage-fireside-chat,workshop-room}.jpg
  assets/photos-2026/{stage-remarkable-backdrop,speaker-at-podium,posters-discussion}.jpg
  sources/Vector_BrandGuidelines_6.29.26.pdf sources/Remarkable_2027_Current_Website_copy.docx
  sources/concept-d-design   # (the AI Summit 2026 page reference stays in the full package, to keep this zip under 25 MB)
)
for f in "${FILES[@]}"; do
  [ -e "$f" ] || { echo "!! missing $f"; exit 1; }
  mkdir -p "$STAGE/$(dirname "$f")" && cp -R "$f" "$STAGE/$f"
done
cp handoff/concept-d/HANDOFF.md handoff/concept-d/CLAUDE.md "$STAGE/"

# Rebuild the frames and the D-only review PDF inside the package, then check them against the approved PNGs
ln -s "$PWD/node_modules" "$STAGE/node_modules"
if ! log=$(cd "$STAGE" && node scripts/export.mjs 2>&1); then echo "$log" | grep -v '^ok'; echo "!! export failed inside the package"; exit 1; fi
rm "$STAGE/node_modules"
for png in exports/concept-d-*.png; do
  cmp -s "$png" "$STAGE/$png" || { echo "!! $png differs when rebuilt inside the package"; exit 1; }
done
[ "$(ls "$STAGE"/exports/*.png | wc -l)" -eq 8 ] || { echo "!! expected 8 PNG frames"; exit 1; }

(cd "$OUT/stage" && zip -q -r -X "../$NAME.zip" "$NAME")
rm -rf "$OUT/stage"
mb=$(( $(stat -c %s "$OUT/$NAME.zip") / 1048576 ))
flag=ok; [ "$mb" -lt "$LIMIT_MB" ] || flag="!! over ${LIMIT_MB} MB"
printf '%s  %s  %s MB  %s files\n' "$flag" "$OUT/$NAME.zip" "$mb" "$(zipinfo -1 "$OUT/$NAME.zip" | grep -vc '/$')"
