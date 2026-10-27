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

FONTS: as before, fonts are not included. Keep your existing Source/dist/fonts folder
(Karbon-Regular/Medium/Semibold/Bold .woff) in place.

PREVIEW: open OPEN_INTERACTIVE_PREVIEW.html (keep it next to the Source folder so it finds the fonts),
or open Source/dist/index.html. Rebuild the preview after edits with:
  cd Source && python3 tools/export-mockup.py --output ../OPEN_INTERACTIVE_PREVIEW.html
