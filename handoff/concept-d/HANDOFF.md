# Remarkable 2027, Concept D "Spotlight": handoff

This package holds **one** design concept for the Remarkable 2027 registration site, Concept D ("Spotlight"),
and everything needed to review, discuss or rebuild it. It was cut from a larger project with four concepts
(A, B, C and D); A–C and their material aren't included. Read this file in full before changing anything.

Last updated: October 22, 2026.

---

## 1. What this is

**Remarkable 2027** is the Vector Institute's annual AI conference: **February 18–19, 2027, Hilton Toronto**,
145 Richmond St W, Toronto. Day 1 is a full day of keynotes and research talks; Day 2 is a half day of workshops,
lightning talks and posters. In-person attendance is by invitation; a virtual livestream is open to everyone.

Two reviewers, Danielle and Marcie, choose a direction; Swoogo's team then rebuilds it on their platform. These
are **design mockups, not production code**: plain HTML/CSS, rendered to PNG and PDF with Playwright.

**Concept D, Spotlight** (bold contrast): a black stage. The home page opens on a split screen: REMARKABLE over a
magenta 2027 on the left, and a 2026 photo on the right cut along the long magenta arrow; a
magenta-to-cobalt gradient rule closes each black band; a grey "program" band holds the two days and the
speakers; a black band holds the recap video and the photo carousel. The Agenda, Speakers and FAQ headers are a
split screen: a photo on the right half, cut along the extended magenta arrow (brand guide p. 6).

### Status: refined with the requester, awaiting review

- Four pages (**Home, Agenda, Speakers, FAQ**) at **1440 px desktop and 390 px mobile**: 8 PNG frames in
  `exports/`, plus `exports/remarkable-2027-concepts-review.pdf` (a cover and the 8 frames).
- These four pages are the whole scope. Email banners and other formats are out of scope.

---

## 2. Folder map

| Path | What it is |
|---|---|
| `HANDOFF.md` | This file. |
| `brand/tokens.css` | The only colours, gradients and fonts allowed, plus the Karbon `@font-face` rules. |
| `content/copy.json` | All copy. Never hard-code copy in the concept. It also holds keys used only by the other concepts (`banner`, `hero.anniversary_slot`, `hero.anniversary_mark`); leave them. |
| `content/COPY-CHANGES.md` | Where every line of copy came from, every edit, and what is placeholder or fictitious. It covers all four concepts. |
| `assets/` | Only what D uses: the white Vector logo (and the colour one for the PDF cover), the magenta Vector arrow and the extended arrow, 15 photos from 2026, 6 stock speaker portraits, funder logos, social icons. |
| `fonts/` | Karbon Regular, Medium and Semibold (D uses Semibold). |
| `mockups/shared/render.js` | The renderer: loads `copy.json` and builds the nav, page content and footer for `<body data-page="home\|agenda\|speakers\|faq">`. |
| `mockups/shared/base.css` | Shared structure, grids and responsive rules. |
| `mockups/concept-d/` | `concept.js` (hero and page-header markup, options), `concept.css` (all of D's styling) and four generated page shells. |
| `scripts/export.mjs` | Serves the folder, screenshots every frame, checks for broken images, missing alt text and horizontal overflow, and builds the review PDF. |
| `scripts/pages.mjs` | Rewrites the four page shells. |
| `exports/` | Generated PNGs and the review PDF. Regenerate rather than edit. `exports/archive/` holds the home page with the previous ("stage") hero. |
| `sources/Vector_BrandGuidelines_6.29.26.pdf` | The Vector brand guide. |
| `sources/Remarkable_2027_Current_Website_copy.docx` | The reg-site copy doc the copy came from (it still holds the 2026 text). |
| `sources/concept-d-design/` | The design from a separate AI chat that D was adapted from (full-page PNG, page text, HTML/CSS/JS). Background only; see section 4. |

---

## 3. How to run

```bash
npm install                                   # playwright 1.56.1 + pdf-lib
npx playwright install chromium               # only if Chromium isn't already available
npm run export                                # the 8 PNGs + exports/remarkable-2027-concepts-review.pdf
node scripts/export.mjs concept-d-home        # just the home page, both widths
```

To look at a page in a browser, serve this folder (the pages fetch `content/copy.json` and use `../../` paths):
`python3 -m http.server 8000`, then open `http://localhost:8000/mockups/concept-d/index.html`. Open Sans loads
from Google Fonts, so rendering needs network access.

The export prints `ok` or `!!` per frame and exits non-zero on any broken image, missing alt text or horizontal
overflow. Still **open every PNG and look at it**: the checks don't catch overlapping or badly wrapped text.

---

## 4. Decisions behind D (made with the requester)

**Shared with the other concepts**
1. **Left-aligned** text throughout. In D nothing is indented: intros line up with their titles.
2. **Nav:** Home · Agenda · Speakers · FAQ, an **EN | FR** switch, and **Register**.
3. **Structure follows the AI Summit 2026 Swoogo page** (in the full four-concept package, `sources/`): full-width sections in one content column, a speaker
   list with photo left and details right, a full footer (contact line, socials, Vector links, privacy text).
4. **Copy comes from the reg-site doc**, edited only to make it true for 2027 (no "Nth year" or anniversary
   wording). Every edit is in `content/COPY-CHANGES.md`. Final copy comes from Nadia.
5. **Home sections, in order:** hero, intro, 2026 stats, the two days, featured speakers, recap video, photo
   carousel (nine photos, moved only by the arrow buttons or scrolling, never automatically), funders, footer.
6. **No 2027 speakers or sessions are confirmed:** every speaker, company, bio and session is **fictitious**.
   Portraits are the requester's **stock headshots**; first names match the gender shown in each portrait
   (Hannah, Arjun, David, Mei, Marcus, Amara). Bios refer to speakers by name, never by pronoun.
7. **Karbon Semibold** for every heading; Open Sans for body text (18 px desktop, 16 px mobile; nothing under
   14 px except the footer's legal text).
8. **No on-page notices** (requester's request, so the mockups read as real pages; the requester tells reviewers in
   the covering email): the "fictitious speakers / stock portraits" notes, the agenda's "sample program" note and
   the top-left review label ("Concept X — internal draft — placeholder copy") are gone from every concept, and the
   review PDF's cover no longer says "placeholder copy" or that content is fictitious. The content is still
   fictitious (speakers, companies, sessions) and the portraits are stock images: never send frames outside the
   team without saying so.

**D itself**
9. **Origin:** the requester liked a design made in a separate AI chat (`sources/concept-d-design/`), but not
   its font sizes, rewritten copy or single long page. D keeps its **look** and follows the shared **layout**:
   - Kept: black nav and hero, the oversized uppercase REMARKABLE with a magenta "2027", the rounded hero photo
     with the magenta arrow on its corner, gradient rules under black bands, Karbon headings with tight
     tracking, square-cornered magenta buttons with black labels and a north-east arrow, underlined text-link
     secondary buttons, the grey program band (photo left, days right), stats with dividers and a magenta "+",
     a black photo band, magenta plus/minus FAQ icons and a black footer.
   - Replaced: every line of copy (all from `copy.json`), the page structure (four pages), the speakers (the
     chat had "to be announced"), the photos (the chat had a three-photo grid and no recap video), the footer,
     and the type sizes (the chat had 12–15 px body text and 8–11 px captions).
   - Removed: "Celebrating 10 years of Vector", the arrow's drop shadow, the closing gradient "Be part of what
     comes next" band and the When/Where labels (copy that isn't ours), the "01 / …" section eyebrows, photo
     captions, and the registration and gallery pop-ups. Photos use the brand's 16 px corners, not 8 px.
10. **Refinements from the requester's review:**
   - REMARKABLE and 2027 are **one size (145 px), side by side on one baseline**, filling the 1200 px column
     (stacked on mobile).
   - **The hero fits one 1440 × 900 screen** (nav, hero and gradient rule end at 893 px): 96 px between the
     wordmark and the tagline/photo, a 116 px arrow, a 312 px photo (the height of the tagline column beside
     it).
   - Button labels are **optically centred**, with the arrow on the same centre line.
   - **No 10th-anniversary mark** in D, and **no Hilton logo** (both tried, then removed at the requester's
     request).
   - "Remarkable 2026 by the numbers" is a **section heading** (40 px desktop / 28 px mobile).
   - Home speakers row: 48 px between columns (24 px on mobile).
   - **Home hero is a split screen** (adapted from the requester's separate "Karbon and pixels" mockup, in D's
     colours): text on black on the left (eyebrow; "Remarkable" at 112 px over a much larger magenta "2027" (180 px),
     matching the proportions the requester preferred in that mockup; the
     tagline; the buttons; the small print). From the centre to the right
     edge a 2026 photo is cut along the extended magenta arrow, whose tip touches the top of the section. The
     dates and venue sit in a row below, then the gradient rule. Phones: no split; the photo fades in from black
     below the text, as on the inner pages. Not taken from that mockup: its purple gradient background, white pill
     buttons, all-Karbon body text, the "Remarkable 2026" photo tag and (at the requester's request) its pixel
     symbol.
   - **The previous hero is kept on file:** the full-width REMARKABLE 2027 above the tagline and a rounded photo
     with the arrow on its corner. `const D_HERO = "stage"` in `concept.js` brings it back (checked
     pixel-identical to the archived PNGs in `exports/archive/`).
   - The agenda shows **one day at a time**: Day 2 is in the page but hidden until its tab is clicked.
   - **Inner-page headers (Agenda, Speakers, FAQ) are a split screen** on desktop, after brand guide p. 6 ("Brand
     Narrative"): black with the title and intro on the left, a 2026 photo on the right cut along the extended
     magenta arrow, whose tip touches the top edge of the section and whose tail runs off the bottom. The split
     starts 60 px left of centre. Photos: Agenda, a speaker in front of the Remarkable backdrop; Speakers, a speaker
     at the Vector podium; FAQ, attendees talking at a poster (none of them used in B's headers).
   - **On phones there is no split:** the photo sits below the text and fades in from black (a black-to-clear
     fade over the photo's top 42%), so the title and intro read on black and flow into the image.

---

## 5. Brand rules

The rules come from the brand guide (`sources/Vector_BrandGuidelines_6.29.26.pdf`).

**Met:** the bilingual logo on every frame; only colours from `brand/tokens.css` (magenta `#EB088A`, cobalt
`#313CFF`, grey `#E9E8E8`, black, white); one gradient, always horizontal magenta→cobalt and never on text,
numbers or photos; no stars, sparkles, glows or drop shadows; circular speaker photos; 16 px rounded corners on
placed photos; the Vector arrow is the official magenta file, never recoloured; alt text on every meaningful
image; nothing autoplays.

**Deliberate deviations:**

| Deviation | Why |
|---|---|
| Large black fills: nav, hero, page headers, the recap and photo band, footer | Goes against earlier client feedback against large black areas. Kept because the requester chose this design; raise it with Danielle and Marcie. |
| Magenta buttons have black labels | Black on magenta is 4.9:1 and passes AA at any size (white on magenta is only 4.3:1). It's the design's look. |
| Phone headers fade the photo in from black | A black-to-clear fade over the top of the photo, so the header text sits on black and flows into the image (requester's request). It isn't the brand gradient, which stays off photos. |
| Small accent text (session times, session labels, Livestreamed tags) is cobalt, not magenta | Magenta is 4.26:1 on white, which fails AA for small text; cobalt is 6.5:1. |

Magenta "2027" on black is 4.9:1; secondary grey text on black (`#bdbdbd`) is 11:1.

---

## 6. How D is built (details that are easy to break)

**Shared renderer**
- `render.js` builds every page from `copy.json`. The concept supplies `window.CONCEPT` in `concept.js`: `letter`,
  `navLogo` ("knockout"), `agendaTabs` (true), `hero(copy, helpers)`, `pageHeader(copy, page, helpers)` and
  `after(copy, page)`.
- When fonts and images have loaded, the page sets `<html data-ready="true">`; the export waits for it.
- There is no review label in the top-left: `frame_label` in `copy.json` is empty so the pages read as real ones.
  Restore "Concept {X} — internal draft — placeholder copy" to bring it back.
- **Agenda tabs** (`agendaTabs`): real `role="tab"` buttons; the other day's panel has `hidden`. Click or the
  left/right arrow keys switch days. The export shows Day 1.

**D (`mockups/concept-d/`)**
- **Home hero (`heroSplit`):** a 700 px band; `.d-sh__split` runs from 100 px left of centre to the right edge and
  holds `arrowSplit` with `H: 700`, `seam: 70` and `touchTop: true` (`D_SPLIT`). `after()` redraws the frame at the
  region's real proportions (820 × 700 at 1440, 1100 × 700 at 2000) and again on resize, so the arrow keeps its
  full height and nothing is cropped at any width. Measured at 1440 and 2000 wide: the hero (details row and
  gradient rule included) ends at 896 px, the arrow's tip is on the section's top row, and the arrow stays 211 px
  clear of "Remarkable". On phones `.d-sh__split` is hidden and `.d-sh__fade` shows the photo below
  the text. The previous hero is `heroStage`, selected by `D_HERO`; its CSS (`.d-hero`, `.d-masthead`, `.d-arrow`)
  is kept. Its notes: REMARKABLE and 2027 at 145 px, measured to fill the 1200 px column, trailing letter-spacing
  cancelled; the photo was 312 px so it fit 1440 × 900.
- **Phone buttons:** D overrides the shared full-width mobile buttons: on phones they keep their natural width,
  stacked and left-aligned, with the arrow beside the label (still 48 px tall). The shared stretch suits A–C's
  boxed buttons; next to D's text-link "Join virtually" it made "Register in person" look oversized.
- **Buttons:** Karbon sits high in its line box, so `.btn` has 5 px of top padding and its arrow (`::after`) is
  lifted 2.5 px. Measured: capitals and arrow both centre within 0.5 px of the button's centre.
- **Arrow (stage hero, kept):** `assets/brand-elements/vector-arrow-magenta.svg`, over the photo's top-right corner at `top: -40px`.
- **Split headers:** `pageHeader` calls the shared `arrowSplit` with a 780 × 480 frame, `seam: 160` and `touchTop: true`, in `.d-split`, which runs from
  60 px left of centre to the right edge, above the gradient rule (`left: calc(50% - 60px)`), so at 1440 px the
  frame is exactly 780 × 480 and nothing is cropped. `touchTop` lifts the arrow by its file's built-in top padding
  (2.4% of its height) so the tip touches the section's top edge, makes it 8% taller than the frame so the tail
  still runs off the bottom, and shifts it so the shaft stays on the photo's edge. Measured at 1440: tip on the
  top row, tail across the bottom row, shaft about 70 px clear of the text. Photos and crops are in
  `D_PAGE_PHOTOS` (`align` for the desktop crop, `phone` for the phone crop); change `seam` and the photos,
  never the coordinates. Header text is capped at 620 px. On phones `.d-split` is hidden and `.d-fade` (an
  `<img>` of the same photo, 320 px tall, pulled 40 px up under the text) shows instead, with a black-to-clear
  fade over its top.
  The photo is clipped to a line parallel to the arrow's shaft, measured from `vector-arrow-extended-magenta.svg`
  (it leans right 0.4017 per unit of height).
- **`after()`** adds the photo to the grey days band and wraps a trailing "+" on stats in a magenta span; neither
  is in the shared markup.
- The speakers teaser continues the grey band; its divider is a `::before` on the container so it matches the
  content width.

---

## 7. Notes for the Swoogo build

- **Interactions:** the agenda's Day 1 / Day 2 tabs switch the visible day; the photo carousel moves only on its
  arrow buttons or by scrolling; FAQ items are open/close disclosures (all shown open in the mockup). Nothing
  autoplays; the recap video is a static thumbnail with a play button.
- **Placeholders:** Register, Join virtually, EN | FR, social and footer links point nowhere yet.
- **Fonts:** Karbon is self-hosted from `fonts/`; Open Sans comes from Google Fonts.

---

## 8. Open items before anything leaves the team

1. **The pages carry no notice that content is fictitious** (section 4). Say so in the covering message, and
   replace the speakers, companies and sessions before anything is public.
2. **Black fills:** confirm with Danielle and Marcie that they're acceptable (section 5).
3. **Fictitious company and university names** (Lumenfold AI, Halcyon Labs, Northbridge Financial Group, Lakeview
   Institute of Technology, Cobalt Ridge Materials, Meridian Health Network, plus the panellists' companies on the
   agenda) haven't been checked against real organizations.
4. **Stock portraits:** confirm the licence covers this use.
5. **Final copy** comes from Nadia. FAQ answers to confirm: the Osgoode-station directions, the accessibility
   answer, and the registration-email steps.
6. **Karbon web licence:** confirm it. If web use isn't licensed, delete the three `@font-face` lines in
   `brand/tokens.css`; headings then fall back to Open Sans 600, as the brand guide allows. Re-measure the
   masthead afterwards (section 6).
7. **Funders** (Canada, Ontario, CIFAR) are carried over from 2026; confirm them for 2027.

---

## 9. Starting prompt for a new Claude session

```
You're picking up Concept D ("Spotlight") of the Remarkable 2027 registration-site mockups for the
Vector Institute. Everything is in this folder. Read HANDOFF.md in full first.
Keep all copy in content/copy.json and log changes in content/COPY-CHANGES.md. Use only the colours,
gradients and fonts in brand/tokens.css.
After any change, re-export with Playwright (npm run export, or node scripts/export.mjs <frame-prefix>),
open the PNGs and check them against HANDOFF.md sections 5 and 6 before calling anything done.
What I'd like to do next: <describe the next task>
```
