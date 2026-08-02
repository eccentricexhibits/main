#!/usr/bin/env bash
# Rebuild an earlier cut of the piece from git into a standalone preview file,
# so old directions stay viewable next to the current one rather than only
# being recoverable as source.
#
#   tools/build-archive.sh <commit> <name> "<banner text>"
#
# Example:
#   tools/build-archive.sh 84271cc v1 "Version 1 — phase arc, horizontal flow"
set -euo pipefail

COMMIT="${1:?usage: build-archive.sh <commit> <name> <banner>}"
NAME="${2:?usage: build-archive.sh <commit> <name> <banner>}"
BANNER="${3:-Archived version $NAME}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/src"
for f in brand.js scene.js preview.html preview-main.js; do
  git -C "$ROOT" show "$COMMIT:src/$f" > "$TMP/src/$f"
done

node "$ROOT/tools/build-preview.js" \
  --src "$TMP/src" \
  --out "$ROOT/dist/preview-$NAME.html" \
  --banner "$BANNER"
