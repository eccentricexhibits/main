#!/usr/bin/env bash
# Builds upload-sized zips of the whole Remarkable 2027 package into handoff-zips/ (ignored by git),
# for moving the project into a Claude chat window (about 30 MB per upload). See HANDOFF.md section 9.
#   bash scripts/package-handoff.sh
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=handoff-zips
LIMIT_MB=25
# Replace only this script's numbered zips; other packages in $OUT (e.g. the Concept D zip) stay
mkdir -p "$OUT" && rm -f "$OUT"/remarkable-2027-[0-9]*.zip

# Only files tracked by git, so nothing local or generated-but-uncommitted slips in.
tracked() { git ls-files -- "$@"; }
pack() { # pack <zip name> <paths...>
  local name="$1"; shift
  tracked "$@" | zip -q -X "$OUT/remarkable-2027-$name.zip" -@
}

pack 1-core HANDOFF.md CLAUDE.md BRIEF.md package.json package-lock.json .gitignore \
  brand content fonts assets mockups scripts reference handoff
pack 2-review-pdfs exports/remarkable-2027-concepts-review.pdf exports/wireframe
# PNG frames in two zips (all four concepts in one would pass 25 MB)
pack 3a-exports-png-a-b 'exports/concept-[ab]-*.png'
pack 3b-exports-png-c-d 'exports/concept-[cd]-*.png' exports/archive
pack 4-sources sources
# Everything else tracked at the repo root: the requester's earlier uploads
git ls-files | grep -v -e '^\(assets\|brand\|content\|fonts\|mockups\|scripts\|reference\|handoff\|sources\|exports\)/' \
  -e '^\(HANDOFF\|CLAUDE\|BRIEF\)\.md$' -e '^package' -e '^\.gitignore$' \
  | zip -q -X "$OUT/remarkable-2027-5-earlier-uploads.zip" -@

# Every tracked file must be in exactly one zip
total=$(git ls-files | wc -l)
packed=$(for z in "$OUT"/remarkable-2027-[0-9]*.zip; do zipinfo -1 "$z"; done | sort | uniq | wc -l)
[ "$total" -eq "$packed" ] || { echo "!! $packed of $total tracked files packed"; exit 1; }

for z in "$OUT"/remarkable-2027-[0-9]*.zip; do
  mb=$(( $(stat -c %s "$z") / 1048576 ))
  flag=ok; [ "$mb" -lt "$LIMIT_MB" ] || flag="!! over ${LIMIT_MB} MB"
  printf '%-4s %-48s %3s MB  %4s files\n' "$flag" "$(basename "$z")" "$mb" "$(zipinfo -1 "$z" | wc -l)"
done
echo "All $total tracked files packed into $OUT/"
