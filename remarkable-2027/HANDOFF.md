# Remarkable 2027 — Karbon and pixels handoff

Updated October 22, 2026 from the supplied event package, brand guide, recap reference, Karbon Font archive and Symbol Compilation for Swoogo PDF.

## Current revision

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

Browser review covers desktop, 768 px tablet and mobile down to 320 px. All four pages fit without horizontal page overflow, use Karbon and show no editorial placeholder notes. Opening arrow tips remain exactly at the section top. FAQ arrows, new event-detail hierarchy and prominent pixel motifs are visually reviewed. Day switching and mobile-menu Escape dismissal pass.

Source checks verify one main heading per page, unique IDs, local assets, featured-session destinations, the four intended JSON edits and synchronized offline copy. The four supplied OTFs match the archive byte-for-byte, their WOFF glyph outlines match, and the pixel SVG contains the exact 34 cells extracted from the PDF.
