# Remarkable 2027 — Rounded panels handoff

Updated October 23, 2026. Builds on the October 22, 2026 Karbon and pixels revision, from the supplied event package, brand guide, recap reference, Karbon Font archive and Symbol Compilation for Swoogo PDF.

## Current revision: rounded panels

1. **One rounded-rectangle system.** Every surface is a rounded panel, card or pill. The radius scale is in `brand/tokens.css`: 40 px for opening panels, section panels and the footer; 28 px for cards; 20 px for placed images and inner tiles. Nested shapes use outer radius minus padding so the corners stay concentric. On mobile the scale steps down to 28/22/16 px.
2. **Inset opening panels.** The home hero and the inner-page banners are rounded gradient panels inset 16 px from the viewport (10 px on mobile). The diagonal photo split, extended arrow and top-anchored arrow tip are unchanged; the split now starts at 50% and the copy column is sized from the measured split (`--copy-max`).
3. **Event details as glass pills.** Date and venue sit inside the opening panels as frosted pills (white 16% fill, after the brand guide's overlay box), replacing the separate strip under the hero. On mobile they stack as grey pills under the actions.
4. **Pixel Design drawn inline.** `render.js` draws the exact 34 cells of `vector-pixel-design.svg` as inline SVG, so each use takes `currentColor` (white on gradients and cobalt, magenta or cobalt elsewhere). Cells reveal bottom-left to top-right when they scroll into view; with reduced motion they appear immediately. A three-cell step from the same grid marks intro cards and stat tiles.
5. **Section treatments.** Intro paragraphs become grey cards with a cobalt closing banner. Statistics sit in white tiles on a grey panel. Day cards carry an inset photo, a magenta or cobalt day badge and a whole-card link to that day of the agenda. Speakers sit in white cards on a grey panel with rounded-square portraits. The recap uses a full-bleed rounded photo with a frosted heading card. Funder logos sit on white tiles. The footer is a single inset grey panel with a white contact card.
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
