# Remarkable 2027 registration-site mockups: handoff

This file is written for whoever picks up the project next (a person or another Claude session). Read it in full
before changing anything. It records what was built, every decision made with the requester after the original
brief, and how to rebuild the exports. Where this file and `BRIEF.md` disagree, **this file wins**: the brief is the
starting point, and the decisions below came later from the requester.

Last updated: October 22, 2026 (stock portraits and matching names; anniversary mark in Concept A; Karbon
Semibold headings; scope narrowed to the four pages; Concept D added and refined).

---

## 1. What this is

Four high-fidelity visual concepts for the registration site of **Remarkable 2027**, the Vector Institute's annual
AI conference (**February 18–19, 2027, Hilton Toronto**, 145 Richmond St W). Two reviewers, Danielle and Marcie,
pick one direction; Swoogo's team then rebuilds the chosen one on their platform. These are **design mockups, not
production code**: plain HTML/CSS rendered to PNG and PDF with Playwright.

| Concept | Strongest idea |
|---|---|
| **A, Gradient Stage** (continuity) | The 2026 stage look rebuilt in the new gradient: a full-height hero with the letter-spaced R E M A R K A B L E / 2 0 2 7 in a 20% white overlay box over a faint "AI" letterform, then one long gradient "stage" band for the day cards and speakers. |
| **B, Arrow Split** (the splashiest) | The brand's extended magenta arrow cuts diagonally through two real 2026 photos, with the photo edges following the arrow's exact angle (brand guide pp. 39–40). |
| **C, Open Canvas** (editorial) | Mostly white with a huge black "Remarkable", "2027" on a gradient band, thin gradient rules and magenta accents; colour is used only as an accent. |
| **D, Spotlight** (bold contrast) | A black stage: an oversized REMARKABLE 2027 ("2027" in magenta) spanning the column, a rounded 2026 photo with the magenta Vector arrow breaking out of its corner, a gradient rule, a grey program band and a black photo band. Adapted from a design made in a separate AI chat (decision 15). |

### Status: complete, awaiting review

- All four concepts are built across **four pages** (Home, Agenda, Speakers, FAQ) at **1440 px desktop and 390 px
  mobile**. These four pages are the only deliverables now (decision 14).
- `exports/` holds 32 page PNGs and `remarkable-2027-concepts-review.pdf` (cover plus 32 frames, A, B, C, D). The three
  `concept-*-banner.png` files are from the earlier scope and are no longer updated.
- `exports/wireframe/` holds a greyscale wireframe of the four pages, its review page and a 5-page PDF, made for
  the manager to sign off the structure before visual design. The review page was also published as a private
  Claude artifact (https://claude.ai/artifact/5uVSWQSJ6K96EySJwGZi54); only its owner can open or share it.
- Git branch: `claude/wonderful-ritchie-ox7y3z` in `eccentricexhibits/main` (continues
  `claude/remarkable-2027-homepage-pvevfp`, where A–C were built).

---

## 2. Folder map

| Path | What it is |
|---|---|
| `BRIEF.md` | The original build brief (deliverables, three concepts, brand rules, checklist). Read with section 4 below. |
| `HANDOFF.md` | This file. |
| `brand/tokens.css` | The only colours, gradients and fonts allowed. The Karbon `@font-face` block is enabled (see section 7). |
| `content/copy.json` | All copy, shared by every concept and page. Never hard-code copy in a concept. |
| `content/COPY-CHANGES.md` | Where every line of copy came from, every edit to the source doc, and what is placeholder or fictitious. |
| `assets/` | Logos (including the 10th-anniversary mark), brand arrows and patterns, gradient backgrounds, 19 photos from 2026, 6 stock speaker headshots, funder logos, social icons. Funder PNGs were trimmed of transparent padding so they sit at equal height. |
| `fonts/` | Karbon Regular, Medium and Semibold OTF, used by the mockups. The full family is in `sources/Karbon_Font_full_family.zip`. |
| `mockups/shared/render.js` | The one renderer: loads `copy.json` and builds the nav, page content and footer for `<body data-page="home|agenda|speakers|faq">`. |
| `mockups/shared/base.css` | Shared structure, grids and responsive rules for every concept. |
| `mockups/shared/banner.js` | Fills banner copy from `copy.json` (banners are parked, see decision 14). |
| `mockups/concept-{a,b,c,d}/` | `concept.js` (hero and page-header markup, options), `concept.css` (all styling), four generated page shells, and (A–C only) a parked `banner.html`. |
| `mockups/skeleton/` | The unstyled shared structure. |
| `mockups/wireframe/` | The greyscale wireframe concept: images become crossed boxes, sections get numbered markers. |
| `scripts/export.mjs` | Serves the repo, screenshots every frame, checks for broken images, missing alt text and horizontal overflow, and builds the review PDF. |
| `scripts/pages.mjs` | Writes the four page shells into every `mockups/*/` folder that has a `concept.js`. |
| `scripts/wireframe-pdf.mjs` | Builds the wireframe PDF from `exports/wireframe/index.html`. |
| `scripts/package-handoff.sh` | Builds upload-sized zips of this whole package (section 9). |
| `scripts/package-concept-d.sh` | Builds a standalone zip of Concept D only (section 9). |
| `handoff/concept-d/` | The `HANDOFF.md` and `CLAUDE.md` that go into the Concept D package. Update them with any change to D. |
| `exports/` | Generated PNGs and PDFs. Regenerate rather than edit. |
| `reference/` | Brand-guide pages 13–41 and 2026 materials (banners, slides, badges, recap pages) as images. Look, don't embed. |
| `sources/` | The original files: Vector Brand Guidelines PDF (6.29.26), the 2026 event-recap PDF, the reg-site copy doc, the AI Summit 2026 Swoogo page, the full Karbon family, the original handoff README and prompt, the agency's 10th-anniversary mark preview, and `concept-d-design/` (the AI-chat design D was adapted from: full-page PNG, page text, HTML/CSS/JS; its photos, fonts and the 5 MB standalone HTML were left out). |
| Repo root PDFs, PNGs, SVGs | Earlier uploads by the requester (brand quick-reference PDF, "Frame" and badge images, official logo and arrow SVGs). Not used by the mockups; kept as they were. |

---

## 3. How to run

```bash
npm install                                   # playwright 1.56.1 + pdf-lib
npx playwright install chromium               # only if Chromium isn't already available
npm run export                                # all 32 page PNGs + exports/remarkable-2027-concepts-review.pdf
node scripts/export.mjs concept-b             # only frames whose name starts with "concept-b"
node scripts/export.mjs concept-a-home        # e.g. just Concept A's home page, both widths
node scripts/export.mjs skeleton              # unstyled skeleton preview
OUT_DIR=exports/wireframe node scripts/export.mjs wireframe && node scripts/wireframe-pdf.mjs
node scripts/pages.mjs                        # after adding a new concept folder
```

To look at a page in a browser, serve the **repo root** (the pages fetch `content/copy.json` and use `../../`
paths): `python3 -m http.server 8000`, then open `http://localhost:8000/mockups/concept-a/index.html`.
Open Sans loads from Google Fonts, so rendering needs network access.

The export prints `ok` or `!!` per frame and lists any broken image, missing alt text or horizontal overflow. It
exits non-zero if anything is wrong. Still **open every PNG and look at it**: the checks don't catch overlapping
text or a pattern running under a paragraph, and both happened during this build.

---

## 4. Decisions made with the requester after the brief (these override BRIEF.md)

In the order they were made:

1. **Left-aligned layout.** All text is left-aligned, as on vectorinstitute.ai. The intro is set in by a slight tab
   (`--lead-indent`: 64 px desktop, 16 px mobile). The live site couldn't be fetched from the build environment,
   so the indent is an estimate from the requester's description.
2. **Nav:** Home · Agenda · Speakers · FAQ, then an **EN | FR** switch and the **Register** button. Venue,
   Partners and Log in were removed.
3. **Themes section removed.** The 2026 themes now appear only as research-talk tracks on the agenda.
4. **Structure follows the AI Summit 2026 Swoogo page** (`sources/AI_Summit_2026_Website_Reference.zip`):
   full-width sections stacked in one content column, a speaker list with photo left and details right, and a
   fuller footer (contact line, "Find us on socials", Vector site links, privacy text). Swoogo can rebuild this
   structure directly. Not copied from it: its black footer (the client rejected large black areas), its 14 px
   body text (below the 16 px minimum) and its centred hero.
5. **Copy comes from the reg-site doc** (`sources/Remarkable_2027_Current_Website_copy.docx`), which still holds
   the 2026 text. It was edited only to make it true for 2027 and to drop year-count wording such as "Now in its
   third year". Every edit is in `content/COPY-CHANGES.md`.
6. **Four pages** instead of one: Home, Agenda, Speakers and FAQ, all styled in every concept.
7. **Photo carousel** on Home ("Remarkable 2026 in photos"): nine photos, moved only by the arrow buttons or
   scrolling, never automatically. **EN | FR switch** in the nav.
8. **No 2027 speakers or sessions are confirmed**, so every speaker, company, bio and agenda session is
   **fictitious**. Their portraits are the requester's **stock headshots**
   (`assets/speakers/stock-headshot-01…06.jpg`, in speaker order); the 2026 headshots of real people that stood in
   before were removed. At the requester's request the first names match the gender shown in each portrait
   (Hannah, Arjun, David, Mei, Marcus, Amara); surnames, roles and bios are unchanged. Bios refer to speakers by
   name, never by pronoun.
9. **Concept A got a "splashier" pass** after Danielle asked for something splashier: a full-height hero, a
   larger wordmark, the "AI" letterform enlarged to fill the hero, and the day cards moved onto the gradient. B is
   still the brief's designated "splashiest" option.
10. **Karbon** (supplied by the requester) is used for all headings, and Open Sans for body text.
11. **Wireframe first:** a greyscale wireframe went to the manager before the visual concepts (`exports/wireframe/`).
12. **10th-anniversary mark placed in Concept A** (hero and banner). The agency's preview file
    (`sources/vector-10th-anniversary-preview.png`, black "10" with a magenta arrow on white) was cut out to a
    transparent PNG, `assets/logos/anniversary-10-years-colour.png`, and set full colour on a white disc. B and C
    still show the dashed placeholder slot.
13. **Karbon Semibold (600) for every heading**, replacing Karbon Medium (the brand guide's default) at the
    requester's request. `--weight-heading` in `brand/tokens.css` drives it; A's letter-spaced wordmark and page
    titles, which were Regular, now use it too. Small all-caps labels (eyebrows, stats caption, funders title) stay
    in Open Sans Bold.
14. **Scope: the four pages only** (Home, Agenda, Speakers, FAQ) for every concept from now on. Email banners and
    other formats are out of scope: they're left out of `npm run export` and the review PDF. Their HTML is kept and
    can still be rendered by name (`node scripts/export.mjs concept-a-banner`).
15. **Concept D, Spotlight**, added from a design the requester had made in a separate AI chat
    (`sources/concept-d-design/`). The requester liked its look but not its font sizes, rewritten copy or single
    long page, so D keeps the **look** and follows our **layout**:
    - Kept: black nav and hero, the oversized uppercase REMARKABLE with a magenta "2027", the rounded hero photo
      with the magenta Vector arrow on its top-right corner, the gradient rule under black bands, Karbon headings
      with tight tracking, square-cornered magenta buttons with black labels and a north-east arrow, underlined
      text-link secondary buttons, the grey program band (photo left, days right), stats with dividers and a
      magenta "+", a black photo band, magenta plus/minus FAQ icons and a black footer.
    - Replaced with ours: every line of copy (all from `copy.json`; nothing from the chat's rewrite), the four
      pages and their section order, the six speakers (the chat had "to be announced"), the recap video and the
      nine-photo carousel (the chat had a three-photo grid), the full footer, our photos and logo files, and the
      type sizes (the chat set body text at 12–15 px and captions at 8–11 px; D uses the shared 18/16 px body
      and 14 px minimum for labels).
    - Removed: "Celebrating 10 years of Vector" (anniversary wording; the agency's mark sits on a white disc
      instead, as in A), the arrow's drop shadow, the closing gradient "Be part of what comes next" band and the
      When/Where labels (copy that isn't ours), the "01 / …" section eyebrows, photo captions, and the
      registration and gallery pop-ups. Placed photos use the brand's 16 px corners, not the chat's 8 px.
16. **Concept D refinements** (requester's review):
    - REMARKABLE and 2027 are one size (145 px), side by side on one baseline, filling the 1200 px column
      (stacked on mobile, as before).
    - Button labels are optically centred (see section 6), with the arrow on the same centre line.
    - The 10th-anniversary mark is **removed from D** (A still shows it).
    - The "Remarkable 2026 by the numbers" caption is a section heading: Karbon Semibold, 40 px desktop / 28 px
      mobile, sentence case, black (it was a small cobalt all-caps label).
    - The agenda shows **one day at a time**: Day 2 is in the page but hidden until its tab is clicked
      (`agendaTabs: true`; A–C still show both days and can switch it on the same way).
    - The intro paragraph under each inner-page title (Agenda, Speakers, FAQ), and the day description on the
      agenda, have no indent, so they line up with the titles.
    - A Hilton logo was tried beside "Hilton Toronto" and then removed at the requester's request (the SVG is in
      git history, commit 9d21eca, as `assets/logos/hilton-white.svg`).
    - The hero was opened up after it felt cramped under the full-width wordmark: more space above and below the
      wordmark (96 px to the tagline and photo) and a smaller arrow (116 px). The wordmark keeps its size.
    - **The hero fits one 1440 × 900 screen**: nav, hero and gradient rule end at 893 px. The photo is 312 px tall
      (the height of the tagline column beside it) and the details row has 24/32 px padding. Re-measure if any
      hero copy or spacing changes.
    - Home speakers row: 48 px between columns (24 px on mobile) and 20 px names, so neighbouring names and titles
      don't run together.
    - **Inner-page headers (Agenda, Speakers, FAQ) are a split screen** on desktop, after brand guide p. 6 ("Brand
      Narrative"): black with the title and intro on the left, a 2026 photo on the right cut along the extended
      magenta arrow, whose tip touches the top edge of the section and whose tail runs off the bottom. The split
      starts 60 px left of centre. Photos: Agenda, a speaker in front of the Remarkable backdrop; Speakers, a speaker
      at the Vector podium; FAQ, attendees talking at a poster (none of them used in B's headers).
    - **On phones there is no split:** the photo sits below the text and fades in from black (a black-to-clear
      fade over the photo's top 42%), so the title and intro read on black and flow into the image.

17. **No on-page notices** (requester's request, so the mockups read as real pages; the requester tells reviewers in
    the covering email): the "fictitious speakers / stock portraits" notes, the agenda's "sample program" note and
    the top-left review label ("Concept X — internal draft — placeholder copy") are gone from every concept, and the
    review PDF's cover no longer says "placeholder copy" or that content is fictitious. The content is still
    fictitious (speakers, companies, sessions) and the portraits are stock images: never send frames outside the
    team without saying so.
---

## 5. Brand rules: how they are met, and the deliberate deviations

The rules are in `BRIEF.md` section 5 and in the brand guide (`sources/Vector_BrandGuidelines_6.29.26.pdf`, page
images in `reference/`).

**Met everywhere:** the bilingual logo on every frame; only colours from `brand/tokens.css`; no stars, sparkles,
glows or drop shadows; no large black fills; circular speaker photos; 16 px rounded corners on placed photos, none
on full-bleed ones; patterns never under photos; arrows never recoloured; the gradient never on text, numbers or
photos; alt text on every image; nothing autoplays.

**Deliberate deviations (agreed or forced by other rules):**

| Deviation | Why |
|---|---|
| Every gradient is the CSS `--vi-gradient` (90°), not the supplied swirl PNGs | The swirl PNGs run in mixed directions; the brief requires one horizontal direction everywhere. |
| B's speaker rings use the horizontal gradient, not the diagonal `--vi-gradient-shape` | The same one-direction rule. Agreed with the requester at the start. |
| C's day columns: a horizontal gradient rule above both columns and a thin grey line between them, instead of the brief's "gradient vertical divider" | A gradient running down a vertical line would be a second direction. The brief contradicts itself here. |
| A's "AI" letterform is shown as a white silhouette at 12% | The PNG carries its own vertical gradient. The 2026 slides also showed it as a light shape. |
| A's 10th-anniversary mark sits on a white disc, not directly on the gradient | The mark is black and magenta; its arrow vanishes into the magenta end of the gradient. The disc keeps the agency's colours instead of recolouring the mark. A white knockout version would need the agency's sign-off. |
| D uses large black fills (nav, hero, page headers, the recap and photo band, footer) | Goes against the earlier client feedback against large black areas. Kept because the requester chose this design; raise it with Danielle and Marcie. |
| D's magenta buttons have black labels | Black on magenta is 4.9:1 and passes AA at any size (white is 4.3:1). It's the design's look. |
| A's hero box doesn't repeat the logo | The nav logo sits on the gradient directly above; two logos within about 200 px looked wrong. |
| Hero primary buttons on a gradient are white with magenta text (A and B) | A magenta button disappears into the magenta end of the gradient. |
| A's day cards are solid white on the gradient, not 20% white overlay cards | White body text on a 20% overlay reaches only about 3.8:1 at the magenta end, which fails AA. |
| B's hero gradient runs magenta→cobalt across the text panel only (0–58%) | So the magenta pixel pattern sits on cobalt and shows up. Still the same horizontal gradient. |
| D's phone headers fade the photo in from black | A black-to-clear fade over the top of the photo, so the header text sits on black and flows into the image (requester's request). It isn't the brand gradient, which stays off photos. |
| Small accent text (session labels, Livestreamed tags) is cobalt, not magenta | Magenta is 4.26:1 on white, which fails AA for small text. Cobalt is 6.5:1. |
| Patterns are left out on phone widths where no corner is free of text (A's hero and page headers; B's hero and page headers) | They would run under text. |
| The page has 9 sections instead of the brief's 10 | Themes was removed at the requester's request. |

**Contrast facts that drove these choices:**
- White on magenta `#EB088A` is about **4.3:1**, so white text on magenta must be large: bold and at least 19 px,
  or at least 24 px. Every button label is 19 px bold for this reason.
- White on the gradient passes 4.5:1 everywhere right of about 5% across. Content starts at 120 px of 1440, so
  normal white text on the gradient is fine.
- White on a 20% white overlay on the gradient is about **3.8–4.6:1**, so only large text goes inside overlay
  boxes.

---

## 6. How each concept is built (details that are easy to break)

**Shared**
- `render.js` builds everything from `copy.json`. A concept supplies `window.CONCEPT` in its `concept.js`:
  `letter`, optional `label`, `navLogo` ("colour" or "knockout"), `hero(copy, helpers)`,
  `pageHeader(copy, page, helpers)`, `dayPhotos` and `after()`. Helpers include `logo`, `anniversarySlot`, `ctas`,
  `meta`, `esc`, `photoAlt` and `ROOT`.
- When fonts and images have loaded, the page sets `<html data-ready="true">`, and the export waits for it.
  `data-broken` lists any image that failed to load.
- **Arrow split** (`arrowSplit` helper): photos clipped to diagonals parallel to the extended magenta arrow's shaft,
  with the official arrow laid over the seam. It was B's `split()`; it moved to `render.js` so D's page headers
  could use it too (B's frames were checked pixel-identical after the move). The geometry notes under B below
  still apply. Option `touchTop` (D only) lifts the arrow so its tip touches the frame's top edge; B doesn't use it.
- **The 10th-anniversary slot** (`anniversarySlot`) is a dashed outline labelled only "10th anniversary mark", still
  used by B and C. `anniversaryMark` places the agency's mark (path and alt text in `copy.json` →
  `hero.anniversary_mark`) on a white disc; A uses it. Never add anniversary or "Nth year" wording to the copy.
- The fixed review label in the top-left shows only when there is label text: the concepts' `frame_label` in
  `copy.json` is empty (decision 17), so only the wireframe (its own `label`) shows one. Restore the text
  "Concept {X} — internal draft — placeholder copy" to bring it back.

**A, Gradient Stage** (`mockups/concept-a/`)
- The nav sits on the gradient with the white knockout logo.
- The anniversary disc is 176 px on desktop (108 px on mobile) and overlaps the hero box's top-right corner. It sits
  at `top: -88px` so it clears the last "E" of the Semibold wordmark; on mobile the eyebrow has 64 px below it so
  the disc doesn't touch it.
- The "AI" letterform is positioned with `translate(-44%, -50%)`, because the glyphs sit 44% of the way across
  the PNG.
- **The plus-pattern PNG holds two clusters:** left at x 0–1072, y 554–963, and right at x 1428–2500, y 538–970
  (in a 2500 × 1406 image). Each corner box shows exactly one cluster, scaled by `--s`, so it can't drift under
  text. It appears only in the corners of gradient bands.

**B, Arrow Split** (`mockups/concept-b/`)
- **The arrow geometry was measured from `vector-arrow-extended-magenta.svg`:** the shaft leans right by
  **K = 0.4017** per unit of height. At a rendered height of 1, the width is 0.5244 and the shaft's centre line is
  at x = 0.080 + K × (0.9 − y).
- `arrowSplit` (in `render.js`) draws the photos clipped to lines parallel to the shaft, places the arrow 1.05× the
  frame height so its tail runs off the bottom, and lines the shaft up with the seam. Change `seam` and the photo
  widths there; don't hand-edit coordinates.
- The banner uses the same maths, written out in `banner.html`.

**C, Open Canvas** (`mockups/concept-c/`)
- The hero lockup is a CSS grid: `max-content max-content 1fr`, with the `<h1>` set to `display: contents`, so
  the dashed square sits right next to "2027".
- The pixel pattern sits above the photo's top edge, never on it.
- Desktop sections have 128 px of vertical padding.

**D, Spotlight** (`mockups/concept-d/`)
- Inner-page headers: `arrowSplit` with a 780 × 480 frame, `seam: 160` and `touchTop: true`, in `.d-split`, which runs from
  60 px left of centre to the right edge, above the gradient rule (`left: calc(50% - 60px)`), so at 1440 px the
  frame is exactly 780 × 480 and nothing is cropped. `touchTop` lifts the arrow by its file's built-in top padding
  (2.4% of its height) so the tip touches the section's top edge, makes it 8% taller than the frame so the tail
  still runs off the bottom, and shifts it so the shaft stays on the photo's edge. Measured at 1440: tip on the
  top row, tail across the bottom row, shaft about 70 px clear of the text. Photos and crops are in
  `D_PAGE_PHOTOS` (`align` for the desktop crop, `phone` for the phone crop); change `seam` and the photos,
  never the coordinates. Header text is capped at 620 px. On phones `.d-split` is hidden and `.d-fade` (an
  `<img>` of the same photo, 320 px tall, pulled 40 px up under the text) shows instead, with a black-to-clear
  fade over its top.
- The hero's `<h1>` is a flex row: REMARKABLE and 2027 share one font size (145 px, measured to fill the 1200 px
  column; 8.4vw on tablet), with the trailing letter-spacing after "2027" cancelled so it ends on the column edge.
  If the copy or tracking changes, re-measure; it must not exceed the column.
- Buttons: Karbon sits high in its line box, so `.btn` has 5 px of top padding and its arrow (`::after`) is lifted
  2.5 px. Measured: capitals and arrow both centre within 0.5 px of the button's centre.
- The arrow is `assets/brand-elements/vector-arrow-magenta.svg` (the same geometry as the chat's arrow), placed
  over the photo's top-right corner at `top: -48px`.
- Agenda tabs (`agendaTabs` in `render.js`): real `role="tab"` buttons; the other day's panel has `hidden`.
  Click or the left/right arrow keys switch days. The export shows Day 1.
- `after()` in `concept.js` adds the photo to the grey days band and wraps a trailing "+" on stats in a magenta
  span; neither is in the shared markup.
- The speakers teaser continues the grey band; its divider is a `::before` on the container so it matches the
  content width.

**Two CSS gotchas hit during the build**
- The wireframe PDF script hides panels with a doubled class (`.pdf-hide.pdf-hide`), because the review page's
  own `!important` rule was more specific.
- The review PDF embeds JPEG copies of the frames. With lossless PNGs it was 27 MB; now it's about 13 MB. The
  PNGs in `exports/` stay lossless.

---

## 7. Open items before anything leaves the team

1. **The pages carry no notice that content is fictitious** (decision 17). Whoever sends frames must say so in the
   covering message, and replace the speakers, companies and sessions before anything is public.
2. **Portraits:** done. Stock headshots replaced the 2026 portraits in every concept. Confirm the stock licence
   covers this use.
3. **Fictitious company and university names** (Lumenfold AI, Halcyon Labs, Northbridge Financial Group, Lakeview
   Institute of Technology, Cobalt Ridge Materials, Meridian Health Network, plus the panellists' companies on the
   agenda) haven't been checked against real organizations.
4. **Final copy** comes from Nadia. FAQ answers to confirm: the Osgoode-station directions, the accessibility
   answer, and the registration-email steps.
5. **Karbon web licence:** confirm it. If web use isn't licensed, delete the three `@font-face` lines in
   `brand/tokens.css`; headings then fall back to Open Sans 600, as the brand guide allows.
6. **The intro indent** is estimated; compare it with vectorinstitute.ai.
7. **The 10th-anniversary mark:** placed in Concept A from the agency's *preview* file (700 px); removed from D
   at the requester's request. Swap in the final
   artwork (ideally SVG) when it arrives, confirm a minimum size with the agency ("YEARS | ANS" is about 9 px
   tall on mobile), and place it in B and C if they stay in play.
8. **Danielle and Marcie** choose a direction from the four concepts. The chosen concept then goes to Swoogo with the PNGs, this file and
   `content/COPY-CHANGES.md`.

---

## 8. Starting prompt for the next Claude session

```
You're picking up the Remarkable 2027 registration-site mockups for the Vector Institute.
Everything is in this folder. Read HANDOFF.md in full first, then BRIEF.md. HANDOFF.md
records every decision made after the brief and overrides it where they differ.
Look at reference/brand-guide-p33.jpg to p41.jpg and a few PNGs in exports/ before changing
anything. Keep all copy in content/copy.json and log changes in content/COPY-CHANGES.md.
After any change, re-export with Playwright (npm run export, or node scripts/export.mjs
<frame-prefix>), open the PNGs and check them against BRIEF.md section 8 and HANDOFF.md
section 5 before calling anything done.
What I'd like to do next: <describe the next task>
```

---

## 9. Moving this package

- **To another Claude Code session:** open this repository on the branch `claude/wonderful-ritchie-ox7y3z`.
  Everything is committed, and `CLAUDE.md` points the session to this file.
- **To a Claude chat window (about 30 MB per upload):** run `bash scripts/package-handoff.sh`. It writes six zips
  of under 25 MB each into `handoff-zips/` (ignored by git):

  | Zip | Contents | Upload when |
  |---|---|---|
  | `1-core` | HANDOFF, BRIEF, brand, content, fonts, assets, mockups, scripts, reference, the Concept D handoff notes, package files | Always. Enough to understand and rebuild everything. |
  | `2-review-pdfs` | Concepts review PDF and the wireframe folder | To review or discuss the designs |
  | `3a-exports-png-a-b` | PNG frames of Concepts A and B (plus their parked banners) | To inspect those frames |
  | `3b-exports-png-c-d` | PNG frames of Concepts C and D (plus C's parked banner) | To inspect those frames |
  | `4-sources` | Brand guidelines, recap PDF, copy doc, AI Summit page, full Karbon family, anniversary-mark preview, the AI-chat design D came from | For brand, copy or Concept D background questions |
  | `5-earlier-uploads` | The requester's earlier repo-root files | Only if those materials matter |

- **Concept D on its own:** run `bash scripts/package-concept-d.sh`. It writes
  `handoff-zips/remarkable-2027-concept-d.zip` (about 20 MB): only the files D needs, its 8 PNGs, a D-only review
  PDF, the brand guide, copy doc, AI Summit page and the AI-chat design D came from, with its own `HANDOFF.md`
  and `CLAUDE.md` from `handoff/concept-d/`. The script rebuilds the PNGs and PDF inside the staged package and
  fails unless the PNGs match `exports/`, so the zip is proven to rebuild on its own. `export.mjs` exports only
  the concepts present in `mockups/`, which is what lets a single-concept package build its own PDF.
