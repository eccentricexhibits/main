# Remarkable 2027 — Rounded panels handoff

Updated October 23, 2026 (rounded panels, arrow seam, then official-pattern tapestry and colour). Builds on the October 22, 2026 Karbon and pixels revision, from the supplied event package, brand guide, recap reference, Karbon Font archive and Symbol Compilation for Swoogo PDF.

## Current revision: official-pattern tapestry and colour

Scope is the four Swoogo pages (Home, Agenda, Speakers, FAQ) on desktop and mobile. The email-banner fields left in `copy.json` from earlier concepts are untouched and unused.

1. **Only the official Pixel Design.** Every pixel shape on the pages is now a whole copy of the Pixel Design in the Symbol Compilation for Swoogo PDF: the same 34 cells in the same arrangement, only scaled and coloured. Copies are never rotated, mirrored, cropped or broken apart, never overlap each other and never cross the cut where they would be seen. (Page 11 of the brand guide shows the pattern mirrored; the Swoogo PDF orientation is used.) The generated cells from the previous revision are gone.
2. **Tapestry along the arrow.** The arrow-seam rule stays: pixels appear only where the arrow cuts a photo. A seeded stream of small copies hugs the cut and thins out away from it. Most are white, with turquoise and tangerine accents; white copies fade slightly with distance. On the photo side, about a quarter of the copies are knocked out of the photo to show the colour field. One larger tangerine copy sits over the top of the photo, away from the people in it. Copies may tuck under the arrow but never sit on copy text or the arrowhead.
3. **More brand colour.** Turquoise (#48C0D9) and tangerine (#FF9E00) join magenta and cobalt:
   - in the pixel tapestries (brand guide p.11 shows the pattern in every brand colour);
   - in the four statistics tiles: magenta, cobalt, turquoise and tangerine, with black or white text chosen for at least 4.5:1 contrast;
   - as session-format dots on the agenda: magenta for main-stage formats, cobalt for talks, turquoise for workshops and posters, tangerine for arrivals, breaks, meals and the reception.
   Mixed gradient colours remain confined to the opening panels.
4. **Banner photos** are framed from the left (`object-position: 25% 50%`) so people sit farther from the cut.

The tapestry is drawn by `buildSeam` and `paintSeam` in `render.js`. `PIXEL_CELLS` holds the 34 cells from `vector-pixel-design.svg`; `TAPESTRY` holds the art-directed copy; the stream is seeded (`seededRandom(2027)`), so it is identical on every visit and rescales with the panel. Each seam panel declares `data-palette` for its copy colours.

## Previous revision: the arrow seam

The pixel motif now follows one rule taken from the brand references, where pixels always travel with arrows: **pixels appear only where the official arrow cuts through a photo, and the photo breaks apart along that cut.** The free-standing pixel clusters, stair-step markers and heading accents are gone.

- **Where it appears.** Three places share the same construction of colour field, photo, arrow and pixel seam: the home hero (gradient), every inner-page banner (gradient, with a page photo: Agenda `stage-fireside-chat.jpg`, Speakers `audience-listening.jpg`, FAQ `registration-desk.jpg`) and the recap block (cobalt). Content sections between them stay clean.
- **How the cells behaved (replaced).** All cells sat on one square grid sized from the panel height (12-24 px). On the photo side, cells within about three cells of the arrow are knocked out of the image and show the colour field through it. On the open side, broken-off cells thin out with distance and favour steps up and to the right, like the Pixel Design and the arrow. Cells near the cut take colours sampled from the photo; farther out they become fading white. Cells keep 14 px clear of all copy, buttons and the photo caption. Cell choice is seeded by grid position, so the pattern is stable and redraws without reshuffling on resize.
- **Motion.** Cells grow outward from the cut over about one second the first time each panel scrolls into view. With reduced motion they appear immediately.
- **Mobile.** The hero and recap keep the photo, so the full seam runs on phones. Inner-page banners hide their photo on phones and keep the small top-right arrow, so only the white broken-off cells remain beside it.
- **Implementation.** `render.js` draws each seam on a `<canvas class="seam-pixels">` between the photo and the arrow (`buildSeam`, `paintSeam`, `wireSeams`). Each seam panel declares its split position (`data-split`) and colour field (`data-field`, either a gradient's two stops or a solid colour). Photo colours are taken by drawing the image into a small canvas, so the effect never reads pixel data and works from the local folder. In Swoogo, keep the photo, canvas and arrow stacking order and the shared arrow geometry.
- **Official symbol.** `assets/brand-elements/vector-pixel-design.svg` is kept in the package but no longer placed on the pages; the seam carries the motif instead.

## Rounded panels (October 23, 2026)

1. **One rounded-rectangle system.** Every surface is a rounded panel, card or pill. The radius scale is in `brand/tokens.css`: 40 px for opening panels, section panels and the footer; 28 px for cards; 20 px for placed images and inner tiles. Nested shapes use outer radius minus padding so the corners stay concentric. On mobile the scale steps down to 28/22/16 px.
2. **Inset opening panels.** The home hero and the inner-page banners are rounded gradient panels inset 16 px from the viewport (10 px on mobile). The diagonal photo split, extended arrow and top-anchored arrow tip are unchanged; the split now starts at 50% and the copy column is sized from the measured split (`--copy-max`).
3. **Event details as glass pills.** Date and venue sit inside the opening panels as frosted pills (white 16% fill, after the brand guide's overlay box), replacing the separate strip under the hero. On mobile they stack as grey pills under the actions.
4. **Pixel Design.** First drawn as inline clusters throughout; replaced by the arrow seam above.
5. **Section treatments.** Intro paragraphs become grey cards with a cobalt closing banner. Statistics sit in white tiles on a grey panel. Day cards carry an inset photo, a magenta or cobalt day badge and a whole-card link to that day of the agenda. Speakers sit in white cards on a grey panel with rounded-square portraits. The recap is a cobalt panel cut by the arrow (see the arrow seam above). Funder logos sit on white tiles. The footer is a single inset grey panel with a white contact card.
6. **Inner pages.** Agenda day tabs are a segmented control. Featured sessions, program sessions, speaker profiles and FAQ items are all rounded cards. Livestream labels are magenta pills. The FAQ topics list is a sticky rounded card on desktop and a pill row on smaller screens. Only the first FAQ in each topic now opens by default.
7. **Palette note.** Large quiet panels use `--vi-grey-light` (#F4F3F3), a 50% tint of brand grey #E9E8E8, so cards and white tiles can sit on it. Everything else stays white, grey, black, magenta or cobalt, and mixed gradient colours remain confined to the opening panels.

No event copy changed in this revision; `content/copy.json` and `copy.js` are untouched.

## Previous revision: Karbon and pixels

1. **Karbon throughout.** Earlier headings used Karbon while body text and controls used Open Sans. All visible type now uses the supplied Karbon family: Regular (400), Medium (500), Semibold (600) and Bold (700+). The supplied OTFs are preserved, with matching WOFF versions for browser loading. No synthetic font weight is needed.
2. **Correct, larger pixel symbols.** The earlier motif was the Plus Design. The new `vector-pixel-design.svg` preserves the exact 34 rectangles and arrangement of the PDF’s Pixel Design. White opening accents and magenta/cobalt content accents are larger and fully opaque. Small-screen layouts keep symbols where there is clear space.
3. **Official gradient crop.** The opening backgrounds use the 25%-60% portion of the #EB088A to #313CFF sRGB gradient. The warm-biased midpoint is 42.5%; rounded endpoint colours are #BD15A7 and #7B27D0. These mixed colours are used only behind opening sections. Text and graphics elsewhere use white, grey, black, magenta or cobalt. The footer is grey with a full-colour logo.
4. **Cohesive mockup copy.** The internal-preview strip, sample-program note, stock/fictitious speaker notices, video-source note and destination tooltips are removed from the rendered pages. Recap artwork retains its play affordance. Accessible portrait descriptions now use the speaker names.
5. **FAQ arrows.** Each topic heading uses the exact compact Vector arrow extracted from the supplied PDF, coloured #EB088A, replacing 01-04. Decorative arrows have empty alternative text.
6. **Better event-detail hierarchy.** The event name is an eyebrow above each page title. Date and venue sit beneath the title with simple white calendar/location icons. Mobile details stack without crossing the large arrow.

The diagonal hero, top-aligned opening arrows, compact speaker announcement, large statistics, portrait grid, featured-session cards and manual gallery remain.

## Hero geometry

`wireArrowGeometry()` measures the hero and calculates the photo’s clip edge and the extended arrow position from the original SVG geometry. ResizeObserver, viewport changes and font readiness keep both aligned. Preserve the SVG viewBox and shared calculations in Swoogo.

On mobile, the diagonal split remains while actions and invitation text sit in a white band below it. Opening arrow tips stay at `top: 0`; the path itself begins at the top of its viewBox. All official arrow shapes retain their aspect ratio.

## Copy and content status

Only four JSON fields change in this revision: `speakers_note` and `agenda_page.note` are emptied; `speakers_page.intro` loses its editorial second sentence; and `ui.video_placeholder` becomes a concise accessible video label. Event descriptions, names, biographies, sixteen sessions, ten FAQ answers, dates, venue, statistics, nine gallery photos, funders and legal copy are unchanged.

The speaker identities, organizations, biographies and sessions are still the supplied fictitious sample content; portraits remain stock images. Removing their visible editorial notes does not turn them into confirmed event content. Final copy comes from Nadia, according to the original handoff.

Registration, virtual attendance, French-language, recap playback and institutional/social destinations remain visual placeholders. Email contact and internal page interactions work. Replace/connect the final content and destinations when implementing the approved design in Swoogo.

## Swoogo implementation

1. Map Home, Agenda, Speakers and FAQ to the corresponding event pages.
2. Upload the supplied Karbon web fonts and brand SVGs; preserve the face-to-weight mapping in `brand/tokens.css`.
3. Preserve the shared layout, opening-gradient crop, top arrow anchor and diagonal hero calculations.
4. Keep mixed gradient colours confined to opening backgrounds. Use the specified brand palette for all other elements.
5. Keep featured-card links paired with their correct session and day.
6. Connect the final event destinations and recap video, then verify the approved event copy.

## Copy updates

Edit `dist/content/copy.json`, then run `python3 tools/sync-copy.py` to regenerate its offline companion. There is no build step.

## Verification

Browser review of the rounded-panels revision covers 1440 px desktop, 768 px tablet, 390 px and 320 px mobile. All four pages fit without horizontal page overflow, use Karbon and show no editorial placeholder notes. Opening arrow tips remain exactly at the section top. FAQ arrows, new event-detail hierarchy and prominent pixel motifs are visually reviewed. Day switching (click, arrow keys and session deep links), gallery paging, mobile-menu Escape dismissal and the pixel reveal pass.

Source checks verify one main heading per page, unique IDs, local assets, featured-session destinations, the four intended JSON edits and synchronized offline copy. The four supplied OTFs match the archive byte-for-byte, their WOFF glyph outlines match, and the pixel SVG contains the exact 34 cells extracted from the PDF.
