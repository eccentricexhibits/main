REMARKABLE 2027 — EDITORIAL, FIVE REFINEMENTS (builds on "Four Corrections")

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

FONTS: as before, fonts are not included. Keep your existing Source/dist/fonts folder
(Karbon-Regular/Medium/Semibold/Bold .woff) in place.

PREVIEW: open OPEN_INTERACTIVE_PREVIEW.html (keep it next to the Source folder so it finds the fonts),
or open Source/dist/index.html. Rebuild the preview after edits with:
  cd Source && python3 tools/export-mockup.py --output ../OPEN_INTERACTIVE_PREVIEW.html
