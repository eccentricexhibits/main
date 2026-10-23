# Remarkable 2027 — Rounded panels

A four-page Vector Institute event mockup prepared for Swoogo implementation. The handoff records the status of the sample content and unfinished destinations.

## Open the design

Unzip the package and open `dist/index.html` in a browser. Home, Agenda, Speakers and FAQ work from the local folder. Keep all folders together. No install, build or server is required.

## Visual direction

The October 23, 2026 revision rebuilds the layout as a system of rounded rectangles: inset gradient opening panels, grey section panels, white cards and pill controls on one radius scale. Pixels follow one rule: they appear only where the official arrow cuts through a photo, and the photo breaks apart along the cut, on the home hero, every inner-page banner and the recap. See `HANDOFF.md` for details.


The hero keeps its diagonal photo split and official extended Vector arrow, with the tip touching the section top. All typography now uses the supplied Karbon family, including body text and controls.

The opening backgrounds use a warmer middle crop of the official #EB088A to #313CFF gradient. Mixed colours appear only in these opening backgrounds. Other text, symbols and surfaces use white, grey, black, magenta or cobalt. The correct block-based Pixel Design is extracted directly from the supplied symbol PDF and used at a more prominent scale.

Agenda, Speakers and FAQ place the event name above the page title, with date and venue below. FAQ topic headings use the supplied compact Vector arrow in magenta. Visible editorial notes are removed so the pages read as a cohesive mockup.

## Files

- `dist/index.html`, `agenda.html`, `speakers.html`, `faq.html`: page entry points.
- `dist/styles.css`: responsive rounded-panel layout and colour treatment.
- `dist/brand/tokens.css`: brand colours, radius scale and supplied Karbon face declarations.
- `dist/fonts/`: supplied OTFs and matching WOFF versions.
- `dist/assets/brand-elements/vector-pixel-design.svg`: exact 34-cell block design from the supplied PDF.
- `dist/assets/brand-elements/vector-arrow-compact.svg`: compact official arrow from the supplied PDF.
- `dist/render.js`: shared renderer, arrow geometry, pixel seam and interactions.
- `dist/content/copy.json`: authoritative event copy.
- `dist/content/copy.js`: generated offline copy.
- `tools/sync-copy.py`: regenerates copy.js after JSON edits.
- `HANDOFF.md`: design decisions and Swoogo implementation notes.
- `design-preview.jpg`, `faq-preview.jpg`: current desktop screenshots.

## Interactions

Four-page navigation, mobile menu with Escape dismissal, keyboard day tabs, featured-session deep links, speaker-profile links, a manual nine-photo carousel, FAQ topic links and disclosures, email contact and back-to-top navigation.

## Content status

The existing 2027 speaker and session content remains sample material. Registration, virtual attendance, French, recap playback and institutional/social destinations still need final connections. This status is recorded here and in the handoff rather than displayed as editorial notes inside the mockup.
