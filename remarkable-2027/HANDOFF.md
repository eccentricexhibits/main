# Remarkable 2027 event site: design handoff

Design mockups for the Vector Institute's **Remarkable 2027** registration site (February 18–19, 2027,
Hilton Toronto). Four pages (Home, Agenda, Speakers, FAQ), desktop and mobile. This is "version 1", the
direction the client approved, revised to their October 28 feedback (see section 4).

These are working HTML/CSS mockups for review and for the Swoogo build team. They are not production code.

Last updated: October 28, 2026.

---

## 1. Start here

| To… | Open |
|---|---|
| Click through every page and view | `OPEN_INTERACTIVE_PREVIEW.html` (keep it next to the `Source` folder so it finds the fonts) |
| See static images | `Mockups/PNG/` (8 full-page PNGs) or `Mockups/Remarkable_2027_Mockups.pdf` |
| Read what changed and why | `CHANGELOG.md` |
| Edit the design | `Source/dist/editorial-event-identity.css` (all visual refinements) and `Source/dist/app.js` (page markup) |

The interactive preview switches between **Desktop** and **Mobile**. Width choices are 1280 / 1440 / 1600 px for desktop and 320 / 390 / 430 px for mobile. The Section menu
jumps to each part of the current page.

---

## 2. Package contents

```
HANDOFF.md                      this file
CHANGELOG.md                    every revision round, in order
OPEN_INTERACTIVE_PREVIEW.html   self-contained desktop/mobile viewer (fonts load from Source/dist/fonts)
Mockups/
  PNG/                          remarkable-2027-<page>-<view>.png, desktop 1440 px wide, mobile 390 px wide
  Remarkable_2027_Mockups.pdf   the same 8 frames with a cover page
Source/
  dist/                         the four live pages and everything they load
    index.html, agenda.html, speakers.html, faq.html
    styles.css                  base Editorial Complete layout (unchanged)
    gradient-panels.css         people / closing panels, agenda controls (unchanged)
    mobile.css                  phone layout, 600 px and below (unchanged)
    editorial-event-identity.css   the event-identity layer: every refinement since Four Corrections
    app.js                      renders header, page content, footer and dialogs from content/copy.js
    content/copy.json, copy.js  all page copy (keep the two in sync); COPY-CHANGES.md records sources
    assets/                     logos, the official Vector plus symbol, photos, speaker portraits, funders
    fonts/                      Karbon Regular / Medium / Semibold / Bold (.woff), licensed, see section 7
    mobile.html                 older phone-frame review page (optional; superseded by the preview)
  tools/
    export-mockup.py            rebuilds OPEN_INTERACTIVE_PREVIEW.html from dist
    mockup/                     the preview's shell (viewer.html / .css / .js)
Source Artwork/                 the supplied "Remarkable AI" gradient PDFs the people section is built from
```

---

## 3. The design at a glance

**Palette.** Magenta `#EB088A`, cobalt `#313CFF`, event ink `#09060E`, white, grey `#E9E8E8`. The event
gradient (`--event-glow`) runs magenta → `#B317AB` → `#6720AA` → cobalt.

**Type.** Karbon throughout. Headings and labels use Medium (500); Semibold (600) accents on the nav
Register button, the hero kicker, the ribbon text, the photo label and the closing Register button.

**One graphic device: the Vector plus.** Remarkable uses the plus signs, so the pages use no Vector arrows
or pixel symbol. The official plus cluster (`assets/brand-elements/vector-plus-symbol.svg`, from "Vector
Official Plus Symbol.svg") appears in the hero, the three inner-page headers and the closing panel; a
single official plus (`vector-plus-single.svg`) marks text links and the Home day rows, and is the
favicon. The Vector arrow survives only inside the Vector Institute logo.

**Buttons.** Calls to action (Register, Register now, the dialog buttons) carry no icon: label only,
centred, at 22–26 px.

**Black sections.** The header, the Agenda / Speakers / FAQ title panels and the footer are black, each
closed or opened by a 4 px event-gradient rule. On the inner pages the header and title panel read as one
black block.

**Home.**
- Hero: oversized "Remarkable", magenta "2027.", date, tagline and Register now; the magenta plus
  cluster sits on the photo's top-left corner, its top aligned with the photo's top edge; tracked
  "R E M A R K A B L E / THE COMMUNITY · 2026" label on the photo. On phones the cluster sits beside
  "2027.".
- People section ("Brilliant minds. Big conversations."): the "Remarkable AI" artwork. The gradient is
  CSS; the AI letterforms and the wide plus field are PNGs exported from the supplied PDFs, blended with
  `lighten` (letterforms 85%, pluses 80%). Speaker cards are white text on 25% white glass, with a soft
  shadow behind the small lines.
- Closing panel ("Be part of what comes next."): the flat Remarkable AI gradient (no AI letters or
  pluses in the background), 25% glass panel, one white Register now button, white plus cluster.
- Venue section: "Hilton Toronto, Toronto, Ontario" only; the street address goes out with registration
  confirmations, not on the public site.

**Agenda / Speakers / FAQ title panels.** Eyebrow in magenta, large headline, and the same plus cluster on
all three pages, with a lighter offset copy (17% magenta) behind it, right-aligned and vertically
centred.

**Speakers page.** Portrait rings use a magenta-weighted gradient (magenta for the first 40%, then into
cobalt).

**Alignment.** Large letters (R, S, G, B and the day numbers' 0) carry built-in side space, so the big
headings are pulled left by small `em` amounts to share the exact left edge of the labels and body text
(within 0.5 px at 1440 and 390 px). Right-hand elements (ornaments, plus icons, toggles) sit flush with the
content edge.

**Shared sizes.**
- "See where the conversation goes.", "Right at the heart of it." and "Be part of what comes next." share
  one size scale: 76 / 68 / 62 / 58 px, then 46–58 px on phones.
- "Remarkable 2026 by the numbers" matches the "Remarkable 2026 in photos" eyebrow.
- One glass value, `--panel-fill: rgba(255,255,255,.25)`, drives the speaker cards and the closing panel.

---

## 4. October 28 client feedback (implemented)

- Moving forward with version 1 (the main design). The alternate split-arrow header was retired; it
  remains in the project's Git history if needed.
- Arrows removed from all CTA buttons, with larger button type.
- The hero arrow is replaced by the plus cluster, partly over the image.
- Speakers and FAQ headers use the same plus cluster as Agenda, so one device carries through.
- Every other Vector arrow (text links, Home day rows, Agenda day tabs, back-to-top, favicon) is replaced
  by a plus or removed. Standard interface glyphs stay: the gallery's ← →, the FAQ topic ↓ and the recap
  play ▶.
- The closing panel's grainy background is replaced by the flat Remarkable AI gradient.
- The venue's street address is removed from the venue section and the FAQ; the FAQ now says the address
  and directions come with the registration confirmation email.

---

## 5. Run and rebuild

- **View the live pages:** from `Source/`, run `python3 -m http.server 8080 --directory dist` and open
  `http://localhost:8080/index.html`. Use a local server rather than opening the files directly: from
  `file://`, Chrome blocks the CSS masks that draw the plus symbols, so they don't appear.
  The interactive preview is not affected (its assets are embedded).
- **Rebuild the preview after editing `dist`:**
  ```
  cd Source
  python3 tools/export-mockup.py --output ../OPEN_INTERACTIVE_PREVIEW.html
  ```
- **PNG mockups:** captured with Playwright (Chromium) at device scale 1 with reduced motion. Each page is
  scrolled once so every lazy image loads, then captured full-page.

---

## 6. Swoogo implementation notes

- **Stylesheet order:** load on every page in this order: `styles.css` → `gradient-panels.css` →
  `mobile.css` → `editorial-event-identity.css`. The last file overrides the others by order, so keep it
  last.
- **Scripts and assets:** load `content/copy.js` then `app.js`. Upload `assets/` and `fonts/` and update
  paths to the hosted URLs (CSS `url()` values and the image paths in `app.js` / `copy.json`).
- **Breakpoints:** 1750, 1200, 1000, 860 and 600 px (phone layout at 600 px and below), plus a 360 px
  refinement.
- **Header:** static (scrolls away). The Agenda day tabs are not sticky.
- **Behaviour:** reduced-motion preferences are respected; dialogs are native modal dialogs (focus stays
  inside, Escape closes).

---

## 7. Fonts and licensing

- **Fonts:** this package includes Karbon Regular, Medium, Semibold and Bold as `.woff`, converted from the
  `.otf` files supplied by the requester. Karbon is a licensed commercial typeface. Check that the Vector
  Institute's licence covers web embedding on the event site before deploying, and do not redistribute the
  font files outside the project.
- **Not in GitHub:** the GitHub copy of this project omits `Source/dist/fonts/`. To restore it, drop the
  four `.woff` files back in.

---

## 8. Content status: confirm before launch

- **Speakers:** the six speakers (names, titles, organizations, bios, sessions) are fictitious, and the
  portraits are stock headshots. No 2027 speakers are confirmed.
- **Agenda:** session times, titles, rooms and named people are sample content.
- **FAQ:** answers reuse confirmed facts (invitation-only in person, public livestream, Hilton Toronto,
  recorded, English only), but process details and the accessibility answer are placeholders.
- **Registration:** buttons open an informational dialog with an email contact, not a live form. Connect
  the approved registration, livestream and recap-video destinations.
- **Facts carried forward:** dates, venue, 2026 statistics and photos come from the supplied source.
- **Copy sources:** `Source/dist/content/COPY-CHANGES.md` records where every line came from.

---

## 9. Accessibility notes

- **Speaker cards:** white text on the 25% glass measures about 4.0–4.5:1 on most of each card and about
  3.6:1 at the far left of the first card, where the gradient is hottest pink. The small lines carry a soft
  shadow. For strict WCAG AA on small text, lower `--panel-fill` to about 0.12, or shift the gradient's
  pink corner.
- **Already in place:** focus states are visible, dialogs are labelled, decorative artwork is
  `aria-hidden`, and photos have alt text.
