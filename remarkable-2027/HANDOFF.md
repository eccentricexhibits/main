# Remarkable 2027 event site: design handoff

Design mockups for the Vector Institute's **Remarkable 2027** registration site (February 18–19, 2027,
Hilton Toronto). Four pages (Home, Agenda, Speakers, FAQ), desktop and mobile, with an alternate header
design for the Agenda, Speakers and FAQ pages.

These are working HTML/CSS mockups for review and for the Swoogo build team. They are not production code.

Last updated: October 27, 2026.

---

## 1. Start here

| To… | Open |
|---|---|
| Click through every page and view | `OPEN_INTERACTIVE_PREVIEW.html` (keep it next to the `Source` folder so it finds the fonts) |
| See static images | `Mockups/PNG/` (14 full-page PNGs) or `Mockups/Remarkable_2027_Mockups.pdf` |
| Read what changed and why | `CHANGELOG.md` |
| Edit the design | `Source/dist/editorial-event-identity.css` (all visual refinements) and `Source/dist/app.js` (page markup) |

The interactive preview has four view buttons:

- **Desktop** and **Mobile**: the main design.
- **Desktop Alt** and **Mobile Alt**: the same pages with the alternate header on Agenda, Speakers and FAQ
  (see section 4). Home is identical in both.

Width choices are 1280 / 1440 / 1600 px for desktop and 320 / 390 / 430 px for mobile. The Section menu
jumps to each part of the current page.

---

## 2. Package contents

```
HANDOFF.md                      this file
CHANGELOG.md                    every revision round, in order
OPEN_INTERACTIVE_PREVIEW.html   self-contained desktop/mobile viewer (fonts load from Source/dist/fonts)
Mockups/
  PNG/                          remarkable-2027-<page>-<view>.png, desktop 1440 px wide, mobile 390 px wide
  Remarkable_2027_Mockups.pdf   the same 14 frames with a cover page
Source/
  dist/                         the four live pages and everything they load
    index.html, agenda.html, speakers.html, faq.html
    styles.css                  base Editorial Complete layout (unchanged)
    gradient-panels.css         people / closing panels, agenda controls (unchanged)
    mobile.css                  phone layout, 600 px and below (unchanged)
    editorial-event-identity.css   the event-identity layer: every refinement since Four Corrections
    app.js                      renders header, page content, footer and dialogs from content/copy.js
    content/copy.json, copy.js  all page copy (keep the two in sync); COPY-CHANGES.md records sources
    assets/                     logos, Vector arrows and pixel symbol, photos, speaker portraits, funders
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

**Black sections.** The header, the Agenda / Speakers / FAQ title panels and the footer are black, each
closed or opened by a 4 px event-gradient rule. On the inner pages the header and title panel read as one
black block.

**Home.**
- Hero: oversized "Remarkable", magenta "2027.", date, tagline and Register now; the Vector arrow just
  covers the photo's top-left corner; tracked "R E M A R K A B L E / THE COMMUNITY · 2026" label on the
  photo.
- People section ("Brilliant minds. Big conversations."): the "Remarkable AI" artwork. The gradient is
  CSS; the AI letterforms and the wide plus field are PNGs exported from the supplied PDFs, blended with
  `lighten` (letterforms 85%, pluses 80%). Speaker cards are white text on 25% white glass, with a soft
  shadow behind the small lines.
- Closing panel ("Be part of what comes next."): textured gradient, 25% glass panel, one white Register
  now button, full white pixel symbol.

**Agenda / Speakers / FAQ title panels (main design).** Eyebrow in magenta, large headline, and one
ornament per page (plus pattern, pixel symbol, Vector arrow), each with a lighter offset copy (17%
magenta) behind it. The three ornaments share one bounding size and sit right-aligned and vertically
centred.

**Speakers page.** Portrait rings use a magenta-weighted gradient (magenta for the first 40%, then into
cobalt).

**Alignment.** Large letters (R, S, G, B and the day numbers' 0) carry built-in side space, so the big
headings are pulled left by small `em` amounts to share the exact left edge of the labels and body text
(within 0.5 px at 1440 and 390 px). Right-hand elements (ornaments, arrows, toggles, the closing pixel
symbol) sit flush with the content edge.

**Shared sizes.**
- "See where the conversation goes.", "Right at the heart of it." and "Be part of what comes next." share
  one size scale: 76 / 68 / 62 / 58 px, then 46–58 px on phones.
- "Remarkable 2026 by the numbers" matches the "Remarkable 2026 in photos" eyebrow.
- One glass value, `--panel-fill: rgba(255,255,255,.25)`, drives the speaker cards and the closing panel.

---

## 4. Alternate header (Desktop Alt / Mobile Alt)

Adapted from the Classy Black (Concept D) mockup.

- **Desktop:** a 2026 photo fills the right side of the title panel, cut along the shaft of the long Vector
  arrow (`assets/brand-elements/vector-arrow-extended.svg`, never rotated). The arrow's tip touches the
  "Remarkable 2027" rule and its tail runs off the bottom. The split starts at 44% of the content width.
- **Mobile:** no split; the photo sits under the headline and fades in from black.
- **Photos:** Agenda `stage-remarkable-backdrop.jpg`, Speakers `speaker-at-podium.jpg`, FAQ
  `posters-discussion.jpg`.
- **How it works:** `app.js` draws the split as an inline SVG sized to the panel's real proportions, on
  load and on every resize, so the arrow is never cropped. Each photo is framed on a focal point:
  `HERO_PHOTOS` in `app.js`, where `fx` / `fy` work like CSS `object-position` and `phone` sets the mobile
  crop.
- **Turning it on:** in the preview, use the Alt buttons. On the live pages, add `?hero=split` (e.g.
  `agenda.html?hero=split`), or add the class `alt-hero` to `<html>`.

---

## 5. Run and rebuild

- **View the live pages:** from `Source/`, run `python3 -m http.server 8080 --directory dist` and open
  `http://localhost:8080/index.html`. Use a local server rather than opening the files directly: from
  `file://`, Chrome blocks the CSS masks that draw the Vector arrows and pixel symbol, so they don't appear.
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
- **FAQ:** answers reuse confirmed facts (invitation-only in person, public livestream, Hilton address,
  recorded, English only), but process details, directions and the accessibility answer are placeholders.
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
