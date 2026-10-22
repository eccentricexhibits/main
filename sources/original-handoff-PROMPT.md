You're a senior web designer working in code. I need three distinct, polished home-page design concepts for "Remarkable 2027", the Vector Institute's annual AI conference (Feb 18–19, 2027, Hilton Toronto). The concepts go to my manager on Friday for internal review, and she'll pick one direction. Swoogo will later rebuild the chosen one on their platform, so these are high-fidelity visual mockups, not production code. They have to look like a real, finished event site at desktop and mobile widths.

This folder is your entire brief:
- BRIEF.md: the full spec (deliverables, page structure, the three concepts, brand rules, checklist). Read all of it before you write any code.
- brand/tokens.css: the only colours, gradients and fonts you may use
- content/copy.json: placeholder copy; use it verbatim in all three concepts
- assets/: logos, brand arrows and patterns, gradient backgrounds, 2026 event photos, speaker headshots, funder logos
- reference/: brand-guide pages and last year's materials; look at them, don't embed them

How I'd like you to work:
1. Read BRIEF.md and look at reference/brand-guide-p33.jpg to p41.jpg and reference/2026-*.png. Then tell me in a few lines how you'll make A, B and C look clearly different. Stop and wait for my OK.
2. Build one shared skeleton (all 10 sections, copy loaded from copy.json, responsive at 1440 and 390). Screenshot it at desktop width and show me.
3. Style Concept A, export it, look at the PNGs yourself and fix anything off. Show me before moving on to B, then C.
4. Build the three 1478×300 email banners. Then write the Playwright export script that produces the 9 PNGs plus the review PDF in /exports.

Non-negotiables (details in BRIEF.md section 5):
- Bilingual Vector logo on every frame
- Magenta→cobalt gradient in one horizontal direction everywhere, as a background only: never on text, numbers or photos
- No stars, sparkles, glows or drop shadows; no large black backgrounds
- Circular speaker photos; rounded corners on placed (not full-bleed) photos
- Max 2 colours and 1–2 graphic elements per section
- Don't invent copy, stats or "anniversary" wording. Leave the dashed 10th-anniversary slot empty
- WCAG AA contrast, alt text on every image, nothing that autoplays or flashes

Quality bar: each concept should hold up next to a top-tier conference site. Use confident type hierarchy, generous spacing and real photos used well, and make sure all three are distinguishable at a thumbnail glance. Before you call anything done, open every exported PNG and check it against the BRIEF.md section 8 checklist: no overlapping or clipped text, no broken images, no horizontal scroll on mobile.

When finished, give me the list of files in /exports, one sentence per concept on its strongest idea, and anything you had to deviate from or couldn't do.
