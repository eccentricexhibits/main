# Remarkable 2027 mockups

Read `HANDOFF.md` in full before doing anything. It describes the project, every decision made after
`BRIEF.md` (and overrides the brief where they differ), how to rebuild the exports, and the open items.

- All copy lives in `content/copy.json`; log copy changes in `content/COPY-CHANGES.md`.
- Use only the colours, gradients and fonts in `brand/tokens.css`; brand rules are in `BRIEF.md` section 5 and `HANDOFF.md` section 5.
- After changing anything, re-export (`npm run export` or `node scripts/export.mjs <frame-prefix>`) and open the PNGs to check them.
