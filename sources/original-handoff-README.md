# Remarkable 2027 mockup handoff package

This package lets Claude Code build the three home-page concepts (A Gradient Stage, B Arrow Split, C Open Canvas) due Friday, Oct 23.

## How to use

1. Unzip this folder and open it as the working directory in Claude Code.
2. Paste the contents of `PROMPT.md` (the full handoff prompt). The short version below also works.

```
Read BRIEF.md in full, then build the three Remarkable 2027 home-page mockup
concepts it describes. Use only the assets, tokens and copy in this folder.
Follow the brand rules in section 5 as hard constraints. Export the 9 frames and
the review PDF to /exports with a Playwright script, then open every PNG and
check it against the acceptance checklist in section 8, fixing problems before
you finish. Start by showing me the shared skeleton at desktop width before
styling the concepts.
```

## What's inside

| Folder | Contents |
|---|---|
| `BRIEF.md` | The full build spec: deliverables, page structure, the three concepts, brand rules, checklist |
| `brand/tokens.css` | Brand colours, gradient, overlay, type and spacing as CSS variables |
| `content/copy.json` | Placeholder copy (same in all three concepts) |
| `assets/` | Logos, arrows, patterns, gradient backgrounds, 19 event photos, 6 speaker headshots, funder logos |
| `reference/` | Brand guide pages, 2026 banners, slides, badge, recap pages (look, don't embed) |

## Before you start: optional files to add

- **Karbon webfont files** (`.woff2`, Medium + Semibold) in a `/fonts` folder, if Vector's licence allows web use. Uncomment the `@font-face` block in `brand/tokens.css`. Without them, headings use Open Sans Semibold.
- **Official logo SVGs** from Marketing. The PNGs included were derived from the 2026 slide deck and are fine for mockups, not for production.
- **Hilton Toronto venue photos**, if you have them. They're not needed for Friday.

Not needed: the original .docx/.pptx/.pdf files. Everything useful from them has been extracted here.
