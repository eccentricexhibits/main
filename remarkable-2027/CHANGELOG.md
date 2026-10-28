# Changelog

Every revision round since the "Four Corrections" handoff, oldest first. Later rounds sometimes reverse
earlier ones (for example, the round-1 Semibold section numbers and the dark photo-label plate were later
removed); `HANDOFF.md` describes the current design.

```
REMARKABLE 2027 — EDITORIAL, FIVE REFINEMENTS + ROUND 2 (builds on "Four Corrections")

All edits live in Source/dist/editorial-event-identity.css, plus one markup change in
Source/dist/app.js (hero photo label). styles.css, gradient-panels.css and mobile.css are unchanged.

1) Font weights: the Karbon Semibold (600) accents from the earlier event-branding layer are back:
   nav Register button, "Vector Institute presents / Hilton Toronto" kicker, section-label numbers,
   the gradient ribbon text, and the attendance-bar titles.
2) Stray gradient line removed: the header had become position:static, so its gradient rule was
   positioned against the browser window and floated across the page at the bottom of the first
   screen. The header is now position:relative (still scrolls away, not sticky), so the rule sits
   directly under the black header on Home. On Agenda/Speakers/FAQ the header and title panel are
   one black block, so only the panel's lower gradient rule and the footer rule remain.
3) Agenda / Speakers / FAQ title panels: more space below the headline (and slightly smaller
   headlines); the plus / pixel / arrow ornaments share one bounding size on every tab and are
   vertically centred at the right; THE PROGRAM / THE PEOPLE / FREQUENTLY ASKED QUESTIONS are magenta.
4) Home: the large arrow moved left so it only just covers the photo's upper-left corner.
   (It sits a little further onto the photo below 1000px wide, where the text column runs up to it.)
5) Home: the photo label uses the earlier mockup's design: dark translucent plate,
   tracked "R E M A R K A B L E" over "THE COMMUNITY · 2026".

ROUND 2
- Agenda: the Day 01 / Day 02 tabs no longer stick to the top while scrolling.
- Home: the photo is cropped from the left (narrower) so the arrow still covers its corner
  but has clear space from the 2027 / date / tagline text at every desktop width.
- Home: section numbers 01-04 already share the headings' left edge (measured within 1px);
  "Brilliant minds." is nudged left because the large "B" has extra built-in space.
- Home: "Register now" label is larger (23px desktop, 20px phone).
- Agenda / Speakers / FAQ: larger ornaments (about 260px at 1440px wide) and a larger offset
  for the lighter shadow shape (22/24px desktop, 15/16px tablet, 8/9px phone).
- Home: the dark plate behind the photo label is removed; the text sits on the photo with a soft shadow.
- FAQ: the arrow is already the official Vector "Arrow Regular" shape (kept as is).
- Bold text: weights in the CSS are unchanged; headings use Karbon Medium (500). Without the
  Medium font file they fall back to Regular and look unbolded, so keep Karbon-Medium.woff in fonts/.

ROUND 3
- Closing panel ("Be part of what comes next."): one white "Register now" button replaces the
  two-option bar; it opens the registration dialog, which still offers in-person and virtual.
- Gradient rules around the black sections are thinner (6px -> 4px).
- Shadow shapes on Agenda / Speakers / FAQ are lighter (24% -> 17% opacity).
- "2027" in the Agenda / Speakers / FAQ "Remarkable 2027" line is the brand magenta (#EB088A).
- "Remarkable 2026 by the numbers" is magenta.
- Optical left alignment: large letters (R, S, G, B and the 0 of the day numbers) have built-in
  side space, so the big "Remarkable", "2027.", hero date, day numbers, "Remarkable 2027" line,
  "Speakers." / "Good questions." and "Right at the heart of it." are pulled left to share the
  exact left edge of the small labels (checked to within 0.5px at 1440 and 390px).
- Home people section uses the new "Remarkable AI" artwork: the gradient is rebuilt in CSS, and the
  AI letterforms and plus field (assets/brand-elements/remarkable-ai-symbol.png and
  remarkable-plus-field.png, exported from the supplied PDFs) sit along the bottom edge, blended
  with "lighten" as in the artwork. Extra space below the cards keeps the letterforms visible.

ROUND 4
- Right edges checked on every page at 1440 and 390px. Fixed: closing pixel motif now sits fully
  inside the panel (no longer clipped); FAQ arrow (narrower than the other ornaments) now right-aligns
  in its box; Home day arrows and Agenda session "+" icons sit flush with the content edge;
  "HILTON TORONTO" compensates for its trailing letter-spacing; mobile hero arrow flush right.
- "Remarkable 2026 by the numbers": uppercase, same size/tracking as "Remarkable 2026 in photos".
- Speakers page (and speaker pop-up) portraits: magenta-to-cobalt gradient ring.
- "Be part of what comes next." now uses the same size scale as "See where the conversation goes."
  and "Right at the heart of it." (76 / 68 / 62 / 58px, and 46-58px on phones; the three now match at
  every width). Button, padding and pixel motif were scaled down to suit.
- FAQ topic list: the 01-04 numbers sit on the same baseline as their labels (desktop and mobile).

ROUND 5
- Speakers page portrait rings: more magenta (solid magenta for the first 40%, then into cobalt).
- People section: plus field replaced with the wider 3600pt artwork (same placement, centred on the
  original), so the pluses run edge to edge.
- Mobile ribbon: "World-class research." / "Real-world impact." centred.
- Section numbers 01-04 now use the same weight as their labels (they already matched in size,
  letter-spacing and baseline).

ROUND 6
- People section plus field: alt-colour wider artwork, blended with "lighten" at 80% (the original
  was 70%).

ROUND 7: ALTERNATE INNER-PAGE HEADER (from the Classy Black / Concept D mockup)
- Preview: four view buttons, Desktop / Mobile / Desktop Alt / Mobile Alt. The Alt views switch the
  Agenda, Speakers and FAQ black sections to the alternate header; everything else is identical.
- Desktop Alt: a 2026 photo fills the right side of the black section, cut along the shaft of the
  long Vector arrow (assets/brand-elements/vector-arrow-extended.svg, unrotated), with the arrow's tip
  touching the "Remarkable 2027" rule and its tail running off the bottom. The SVG is redrawn at the
  area's real proportions (on load and on resize), so the arrow is never cropped.
- Mobile Alt: no split; the same photo sits under the title and fades in from black.
- Photos (copied from the Concept D package): Agenda stage-remarkable-backdrop.jpg, Speakers
  speaker-at-podium.jpg, FAQ posters-discussion.jpg.
- The split starts at 44% of the content width, and each photo is framed on a focal
  point (HERO_PHOTOS fx/fy in app.js) so its subject stays in view as the area changes shape.
- Live pages: add ?hero=split to agenda.html, speakers.html or faq.html to see the alternate header.

ROUND 8
- Home people section: speaker card text (session, name, role, organisation, View profile link and
  its underline and +) is white, with a soft shadow behind the smaller lines.
- One glass fill (--panel-fill, 25% white; was 32%) for the speaker cards and the closing
  "Be part of what comes next." panel, so they match.

FONTS: as before, fonts are not included. Keep your existing Source/dist/fonts folder
(Karbon-Regular/Medium/Semibold/Bold .woff) in place.

PREVIEW: open OPEN_INTERACTIVE_PREVIEW.html (keep it next to the Source folder so it finds the fonts),
or open Source/dist/index.html. Rebuild the preview after edits with:
  cd Source && python3 tools/export-mockup.py --output ../OPEN_INTERACTIVE_PREVIEW.html

ROUND 9: CLIENT FEEDBACK (October 28, 2026)
- Version 1 (main design) chosen; the alternate split-arrow header, its viewer buttons, PNGs and the three
  photos it used are removed.
- CTA buttons: no arrows; label centred; larger type (nav 22px, Register now 26px desktop / 22px phone,
  dialog buttons 22px).
- One graphic device, the official Vector plus symbol ("Vector Official Plus Symbol.svg"), replaces the
  hand-drawn plus pattern, the pixel symbol and every Vector arrow:
  hero plus cluster over the photo's corner (magenta on the page, white on the photo; beside "2027." on
  phones); the same cluster on the Agenda, Speakers and FAQ headers; white cluster in the closing panel;
  a single plus on text links and the Home day rows; plus favicon. Arrows removed from the Agenda day tabs
  and back-to-top.
- Hero photo returns to full width (the crop that made room for the arrow is gone).
- Closing panel background: the flat Remarkable AI gradient replaces the grainy gradient-flow texture.
- Venue street address removed from the venue section and FAQ (it goes out with registration
  confirmations); see Source/dist/content/COPY-CHANGES.md.

ROUND 10
- Hero plus cluster: all magenta (no white where it crosses the photo), moved down and right, clear of
  the "2027." / date text.
- "Remarkable 2026 by the numbers" and "Remarkable 2026 in photos" use the same tracking as the 01-04
  section labels on phones (they already matched on desktop).
```
