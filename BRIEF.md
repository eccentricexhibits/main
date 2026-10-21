# Remarkable 2027: Build brief for three home-page mockups

You are building **three internal design concepts** for the home page of the Remarkable 2027 registration site. Remarkable is the Vector Institute's annual AI conference. The final site will be built on Swoogo by Swoogo's team, so these mockups are **design visualizations, not production code**. They need to look polished and realistic at desktop and mobile widths, because two reviewers (Danielle and Marcie) will pick one direction from them.

Everything you need is in this folder. Read this whole file before writing code.

---

## 1. Deliverables

Build 9 frames: 3 concepts × (desktop page, mobile page, email banner). Export them as PNGs, then gather them into one review PDF.

```
mockups/
  shared/            # shared CSS (imports ../../brand/tokens.css), shared JS that renders copy.json
  concept-a/index.html   # responsive home page
  concept-a/banner.html  # 1478 x 300 email banner
  concept-b/index.html
  concept-b/banner.html
  concept-c/index.html
  concept-c/banner.html
exports/
  concept-a-desktop.png   # 1440px wide, full page
  concept-a-mobile.png    # 390px wide, full page
  concept-a-banner.png    # 1478 x 300 exactly
  ... (same for b, c)
  remarkable-2027-concepts-review.pdf   # cover page + 9 frames, in order A, B, C
scripts/
  export.mjs (or export.py)  # Playwright: serves the folder, screenshots every frame, builds the PDF
```

- Use plain HTML/CSS (vanilla JS is fine). No framework or build step is needed. Load the copy from `content/copy.json` (or inline it identically in all three).
- Use Playwright for the screenshots. If it isn't installed, run `npm i -D playwright && npx playwright install chromium` (or the Python equivalent).
- Run a local server for screenshots (e.g. `npx http-server` or `python -m http.server`) so the JSON and images load.
- Each page shows a small fixed label in the top-left corner: "Concept A — internal draft — placeholder copy" (11px, grey, semi-transparent white pill). Hide this label in the banner exports.
- The review PDF gets a cover page with a title ("Remarkable 2027 — Registration site concepts — internal draft — Oct 23, 2026"). It also gets a one-line rationale per concept (see section 4) at the top of each concept's first frame.

---

## 2. Event facts (use exactly)

- **Remarkable 2027**: Thursday–Friday, **February 18–19, 2027**
- **Hilton Toronto**, 145 Richmond St W, Toronto, ON
- Day 1: full day of keynotes and research talks. Day 2: half day of workshops, lightning talks and posters
- In-person attendance is by invitation; there is also a public virtual livestream
- **Do not** write "Now in its X year" or "10th anniversary" copy. Instead, reserve a visible empty slot for a 10th-anniversary mark that a separate agency will supply. Draw it as a dashed outline with the tiny label "10th anniversary mark".

All placeholder copy lives in `content/copy.json`. Use it verbatim and don't invent statistics, names or quotes.

---

## 3. Shared page structure (identical in all three concepts, same order)

1. **Nav bar**: Vector bilingual logo (left); links Home · Agenda · Speakers · Venue · FAQ · Partners · Log in; a **Register** pill button (right, magenta). On mobile, collapse to a hamburger icon plus the Register button.
2. **Hero**: eyebrow, event name, tagline, dates | venue, two CTAs (Register in person = primary magenta; Join virtually = secondary outline), small print, and the 10th-anniversary slot.
3. **Intro**: one paragraph, max-width ~720px.
4. **Stats band**: 4 figures plus caption. Numbers must be solid colour, **never gradient**.
5. **Two days at a glance**: two cards (Day 1, Day 2), each with label, date, length, title and body.
6. **Featured speakers**: 6 **circular** headshots with name (bold), title and org.
7. **Themes**: 3 blocks.
8. **Recap video**: a 16:9 thumbnail with rounded corners and a play button (static, no autoplay).
9. **Funders**: Canada, Ontario and CIFAR logos at equal height. Use `filter: brightness(0) invert(1)` for white versions on dark or gradient backgrounds.
10. **Footer**: knockout logo, Ontario credit line, contact, hashtag, social links, legal text (small), copyright.

Responsive targets: 1440 desktop (content max 1200px) and 390 mobile. On mobile, cards stack and speakers form a 2-column grid.

---

## 4. The three concepts (each must look clearly different; don't mix motifs between them)

### Concept A: "Gradient Stage" (continuity)
*Rationale line: "Continuity — the 2026 stage look, rebuilt in the new magenta-to-cobalt brand gradient."*
- **Hero:** full-bleed horizontal magenta-to-cobalt gradient (`--vi-gradient`, or `assets/backgrounds/gradient-magenta-cobalt-1.png` as a background image). A faint 2026 **"AI" letterform** (`assets/brand-elements/ai-letterform-2026.png`) sits at ~10–15% opacity, large, behind and to the right. Content goes in a centred **overlay box** (white at 20% opacity, 24px radius, per brand p.38). Inside the box: knockout logo, a letter-spaced wordmark **R E M A R K A B L E** (letter-spacing ~0.5em, white), "2027" beneath, then dates | venue and the CTAs. The anniversary slot is a dashed circle badge at the box's top-right corner.
- Stats band: solid **cobalt** background with white numbers.
- Day cards: white 20% overlay cards on a second gradient band, or white cards on grey.
- Speakers: circles with 4px white keylines on a gradient band.
- Plus-sign pattern (`plus-pattern-2026.png`) allowed at low opacity in the corners of gradient bands only.
- **Banner:** gradient, knockout logo top-left, letter-spaced wordmark plus dates centred (closest to the 2026 banners in `reference/2026-email-banner-*.png`).

### Concept B: "Arrow Split" (the splashiest, photo-led)
*Rationale line: "Momentum — the brand arrow cuts through real Remarkable photos; the most energetic option."*
- **Hero:** gradient background. Text sits on the left (~45%): eyebrow, big headline "Where AI possibilities come to life." in white, then event name, dates | venue, and the CTAs. On the right (~55%) is a **split-screen of two 2026 photos** (e.g. `stage-fireside-chat.jpg` and `networking-crowd.jpg`) separated by a large magenta **extended vector arrow** (`vector-arrow-extended-magenta.svg`) as the divider, following brand pp.39–40. Photos keep rounded corners where they aren't full-bleed. The anniversary slot is a dashed lockup area under the headline.
- Stats band: white background with **magenta** numbers.
- Day cards: photo-topped cards (`stage-remarkable-backdrop.jpg`, `posters-discussion.jpg`) with rounded corners, on white.
- Speakers: circles with a gradient keyline (CSS ring using `--vi-gradient-shape`) on white.
- Use the magenta pixel pattern (`pixel-pattern-magenta.svg`) once, on a gradient area, never under a photo.
- **Banner:** gradient on the left with headline and dates; on the right, a photo strip with the arrow divider.

### Concept C: "Open Canvas" (light, editorial, modern)
*Rationale line: "Modern editorial — white space and bold type, with colour used only as an accent."*
- **Hero:** white background. A very large heading-font headline "Remarkable" (~120px desktop, black text is fine here), with "2027" on a **gradient band** behind it (a gradient rectangle behind large headline text, which is allowed; the text itself stays white or black, never gradient-filled). Tagline, dates | venue and the CTAs follow below. A thin magenta-to-cobalt **gradient divider line** separates the elements (brand p.37). There is one rounded photo on the right (`speaker-at-podium.jpg` or `workshop-speaker-smiling.jpg`), and the magenta pixel pattern breaks out of the top-right corner (not overlapping the photo). The anniversary slot is a large dashed square beside "2027".
- Stats band: grey `#E9E8E8` background, black numbers, a gradient rule above.
- Day cards: a two-column typographic layout with a gradient vertical divider and no card boxes.
- Speakers: circles with thin black keylines, magenta names.
- Generous white space throughout (section padding ≥ 96px desktop).
- **Banner:** white background, bold headline left, gradient underline, magenta pixel pattern on the right edge, colour logo.

---

## 5. Brand rules (hard constraints; check each one before exporting)

Source: Vector Brand Guidelines 2026. Page images are in `reference/brand-guide-pXX.jpg`.

1. **Logo:** always the **bilingual** lockup (Vector Institute | Institut Vecteur). Use `logo-bilingual-colour.png` on white and `logo-bilingual-knockout-white.png` on gradient or photo. Keep clear space ≥ the arrow height. Never stretch, recolour, rotate or add effects.
2. **Colours:** only the tokens in `brand/tokens.css`. Magenta + cobalt lead. Use **max 2 colours and 1–2 graphic elements per section**.
3. **Black:** black is for text; avoid large black backgrounds (the client asked for this). The footer may use a cobalt or gradient background instead.
4. **Gradients:** magenta → cobalt, **one direction (horizontal) across all three pages and banners**. Use them only as backgrounds behind large headlines and bands. **Never** apply gradients to body text, numbers or arrows next to other colours, never lay them over photos, and never put them inside patterns.
5. **Overlay box on gradient:** white 20% opacity, 24px radius.
6. **Type:** headings in `--font-heading` (Karbon → Open Sans 600 fallback); subheads Open Sans 700; body Open Sans 400, ≥ 16px on desktop.
7. **Images:** rounded corners on placed images (16px); **no** rounding on full-bleed images. Speaker portraits are **circular**.
8. **Patterns:** pixel and plus patterns may be cropped and rotated **only in 90° steps**, and never sit under photos.
9. **Arrows:** gradient arrows only on white or as an image separator. Don't recolour the arrow SVGs.
10. **No stars, sparkles or glow effects** (explicit client feedback), and no drop shadows or bevels.
11. **Accessibility (AODA/WCAG AA):** text contrast ≥ 4.5:1 for body (check white on magenta; use it only for large text ≥ 24px or bold ≥ 19px), alt text on every image, semantic headings, visible focus states, no flashing or autoplay.

---

## 6. Assets in this folder

| Path | What it is |
|---|---|
| `assets/logos/logo-bilingual-colour.png` | Bilingual logo, black + magenta arrow, transparent (derived from the official knockout PNG) |
| `assets/logos/logo-bilingual-knockout-white.png` | Bilingual logo, all white, transparent |
| `assets/brand-elements/vector-arrow-*.svg` | Vector arrow (short): magenta and gradient (vector, from the brand guide p.23) |
| `assets/brand-elements/vector-arrow-extended-*.svg` | Extended arrow for split-image treatments: magenta and gradient |
| `assets/brand-elements/fastlane-arrow-*.svg` | Fastlane arrow: magenta and gradient (FastLane programme only; avoid unless needed) |
| `assets/brand-elements/pixel-pattern-magenta.svg`, `-cobalt.svg` | Branded pixel pattern (p.24) |
| `assets/brand-elements/plus-pattern-2026.png` | 2026 plus-sign scatter pattern (transparent) |
| `assets/brand-elements/ai-letterform-2026.png` | 2026 giant "AI" letterform (Concept A only) |
| `assets/backgrounds/gradient-magenta-cobalt-1..5.png` | Official magenta/cobalt gradient backgrounds (≈1021px wide; scale up with `background-size: cover`, which is fine for soft gradients) |
| `assets/backgrounds/gradient-2026-magenta-violet-plain.png` | Plain 2026 gradient (old palette; reference only) |
| `assets/photos-2026/*.jpg` | 19 Remarkable 2026 event photos (≤2000px) |
| `assets/speakers/*` | 6 speaker headshots (2026 stand-ins) |
| `assets/funders/*` | Canada, Ontario, CIFAR logos |
| `assets/social-icons/*` | X and Bluesky (white). Draw LinkedIn and YouTube as simple inline SVG icons |
| `reference/` | Brand guide pages, 2026 banners, slides, badge, recap pages: for visual reference only, don't embed |

The SVG arrows and patterns were cropped from the brand guide PDF and keep their original page coordinates in the `viewBox`. Scale them with CSS width/height, and check how they render.

---

## 7. Process

1. Read `brand/tokens.css`, `content/copy.json`, and look at `reference/brand-guide-p33.jpg` to `p41.jpg` and `reference/2026-*.png`.
2. Build the shared skeleton (structure, copy rendering, responsive grid) once, then style each concept on top of it.
3. Export the screenshots. **Open every PNG and look at it** (desktop, mobile, banner). Fix overlaps, cut-off text, low contrast, broken images, and anything that breaks section 5.
4. Self-review against the checklist below, then build the PDF.

## 8. Acceptance checklist

- [ ] 9 PNGs plus 1 PDF in `exports/`; banners exactly 1478 × 300
- [ ] Every page shows the 10 sections in order, with identical copy across concepts
- [ ] Dates read "February 18–19, 2027" everywhere; venue reads "Hilton Toronto"
- [ ] Bilingual logo on every frame
- [ ] One gradient direction everywhere; no gradient on text, numbers or photos
- [ ] No stars, sparkles, glows or shadows; no large black fills
- [ ] Circular speaker photos; rounded placed photos
- [ ] Mobile frames have no horizontal scroll and readable 16px body text
- [ ] The three concepts are clearly distinct at a glance
- [ ] The 10th-anniversary slot is visible in each hero and banner
- [ ] Concept label visible on page frames, hidden on banners

When done, report back with the file list and one sentence per concept on anything that deviates from this brief.
