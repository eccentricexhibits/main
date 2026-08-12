# Handoff — Design Exchange event floor maps

Written so another session (or another person) can pick this up and make
changes without re-deriving what took the most work to establish. Read
section 4 before you touch any coordinates — it is the part that is not obvious from
the code, and getting it wrong silently produces plausible-looking but wrong
maps.

---

## 1. What exists

Guest-facing wayfinding maps for a Vector Institute event at the Design
Exchange, 234 Bay Street, Toronto. Built from the venue's own blueprints and
tech deck, set in the Vector brand (Karbon, brand palette).

Seven sheets, in two styles:

| Sheet key | Size | Style | Covers |
| --- | --- | --- | --- |
| `lobby-event-map` | 24 × 16 in | event map | Level 1 — arrival, check-in, coat check |
| `trading-floor-event-map` | 24 × 16 in | event map | Level 2 — immersive theatre |
| `gallery-event-map` | 24 × 16 in | event map | Level 3 — exhibition hall, boardroom |
| `building-overview` | 24 × 16 in | section | "Getting Around" — vertical routes |
| `level-1-lobby` | 24 × 36 in | plan sheet | Level 1, reference drawing |
| `level-2-trading-floor` | 24 × 36 in | plan sheet | Level 2, reference drawing |
| `level-3-gallery` | 24 × 36 in | plan sheet | Level 3, reference drawing |

Each ships as `.pdf` (press), `.svg` (vector, fonts embedded) and `.png` (2×).
All in `floor-maps/dist/`.

**Two styles, on purpose.** The four 24 × 16 sheets are the current work: the
venue's real wall geometry with room floors tinted by category, numbered pins
keyed to a card, north up. The three 24 × 36 sheets are the earlier reference
drawings — blueprint poché with colour washed over it, kept in the blueprint's
own orientation. They are still built and still valid, but the event maps are
the direction the client chose. If asked to retire the plan sheets, delete the
`FLOORS` loop in `src/build.py:main()` and the sheets in `src/make_artifact.py`.

---

## 2. Where it lives

Two repositories are involved — do not confuse them:

```
handoff bundle   eccentricexhibits/floorplan
                 the finished PDFs, the venue source PDFs and this report

generator source eccentricexhibits/main
                 branch  claude/design-exchange-floor-maps-0icdz3
                 dir     floor-maps/
```

The bundle is what to read and review. The generator is what to edit if you
need to *change* a sheet — see the note at the end of section 2a. If the source
has since been moved into `floorplan`, look for `src/` and `geometry/` there
first.

```
floor-maps/
├── README.md               project docs
├── HANDOFF.md              this file
├── geometry/f1.json        wall vectors extracted from the Floor 1 blueprint
├── geometry/f2.json          "  Floor 2
├── geometry/f3.json          "  Floor 3
├── dist/                   all output + artifact.html + index.html
└── src/
    ├── mapstyle.py         shared palette + wall tones  ← change a colour here
    ├── event_map.py        the event-map renderer (all four 24×16 sheets)
    ├── lobby_data.py       Level 1 content
    ├── trading_data.py     Level 2 content
    ├── gallery_data.py     Level 3 content
    ├── overview_data.py    Getting Around content
    ├── build_overview_map.py   draws the section (not a plan — own body code)
    ├── build_lobby.py / build_trading.py / build_gallery.py   one sheet each
    ├── build.py            builds everything + the viewer; also holds the
    │                       older plan-sheet renderer and shared helpers
    ├── mapdata.py          content for the three 24×36 plan sheets only
    ├── extract_walls.py    blueprint PDFs → geometry/f*.json
    └── make_artifact.py    single-file shareable page → dist/artifact.html
```

Brand assets sit in the **repo root**, not in `floor-maps/`:
`Karbon-Regular.otf`, `Karbon-Semibold.otf`, `Official Vector Logo.svg`.

---

## 2a. If you were handed files instead of the repo

**Filename mapping.** This report names sheets by their repo key. If the files
arrived with the handoff naming, they map across like this:

| Handoff filename | Repo key | What it is |
| --- | --- | --- |
| Claude Code - Event Map - Level 1 - Lobby | `lobby-event-map` | current style |
| Claude Code - Event Map - Level 2 - Trading Floor | `trading-floor-event-map` | current style |
| Claude Code - Event Map - Level 3 - Gallery | `gallery-event-map` | current style |
| Claude Code - Building Overview | `building-overview` | current style; the sheet is titled **Getting Around** and is a section, not a plan |
| Claude Code - Reference Map - Level 1 | `level-1-lobby` | 24 × 36 plan sheet |
| Claude Code - Reference Map - Level 2 | `level-2-trading-floor` | 24 × 36 plan sheet |
| Claude Code - Reference Map - Level 3 | `level-3-gallery` | 24 × 36 plan sheet |

Everything prefixed **"Claude Code -"** is generated output from this project.
Everything prefixed **"Venue Supplied Plans"** is source material from Design
Exchange:

| Handoff filename | Original | Trust it for |
| --- | --- | --- |
| Venue Supplied Plans (From Blueprints - Accurate Layout) - Level 1/2/3 | `Floor 1/2/3 — Floor Plan.pdf` | **everything** — wall geometry, dimensions, room names, the north arrow. This is the authority |
| Venue Supplied Plans (... + 3D Mockups) - Level 1 | `Floor 1 — Reference Images.pdf` | "Vector – Lobby" — a sparse lobby plan plus renders |
| Venue Supplied Plans (... + 3D Mockups) - Level 2 | `Floor 2 — Reference Images.pdf` | **"Vector – 350px Theater Style" — a full 350-seat theatre layout for the Trading Floor** |
| Venue Supplied Plans (... + 3D Mockups) - Level 3 | `Floor 3 — Reference Images.pdf` | "Vector – Gallery – Vendor Tables" — the vendor layout |
| Design Exchange - Tech Deck | `DX_Tech_Deck_01.01.2026_LR.pdf` | projection surfaces, LED sign, lighting and audio inventory |

**All three reference files carry an event layout, not just renders.** Each is a
Visrez document by Alicia Black: page 1 is a layout plan, pages 2–3 are 3D views
of it. Every page is a raster image — there is no vector geometry to extract, so
anything taken from them is traced by eye against the blueprint, not measured.
Do not treat them as dimensioned drawings; do not dismiss them as decoration
either.

They are named per level for what they actually contain, because the three
differ a lot in usefulness:

- **Level 1** — "Vector – Lobby". Mostly bare architecture with a little
  furniture. Nothing was taken from it.
- **Level 2** — "Vector – 350px Theater Style". A **350-seat theatre layout**,
  two blocks with a centre aisle and stage elements along both long walls. The
  seating is drawn on the Trading Floor sheet; the stage elements are not,
  since what they are is not stated on any drawing.
- **Level 3** — "Vector – Gallery – Vendor Tables". The vendor layout, and the
  source of the vendor rows on the Gallery sheet. It also confirmed the
  north-up orientation the whole set uses.

**Which format to upload — PDF.** It wins on every axis at once:

| | vector | model can *see* it | text extractable | size (this set) |
| --- | --- | --- | --- | --- |
| **PDF** | yes | yes — pages render as images | yes | **117–336 KB** |
| PNG | no | yes | no | 350–580 KB |
| SVG | yes | no — read as text | yes | 225–332 KB |

PDF is the only format that is simultaneously the press master, scalable, and
directly viewable by a model — and here it is also the *smallest* of the three.
It keeps live text too (~1,900 extractable characters per sheet), so a session
can search for a label rather than squint at it. Headings set with letter
spacing extract with gaps between characters, which is cosmetic.

PNG is a fine fallback if something in the chain will not take PDF, but it is
larger and carries no text. SVG is worth uploading only when a human will open
it in Illustrator — read as text it is 75–86% base64-encoded Karbon, and a
model cannot see the rendered result from it at all.

**The bigger point: these sheets are generated, not drawn.** Editing an SVG or
PDF by hand produces a change that the next `python3 src/build.py` silently
throws away. If the goal is *changes* rather than *review*, the highest-value
upload is not an image format at all — it is `src/`, `geometry/` and the brand
assets, so the new session edits the data module and rebuilds. Use the image
formats for looking, the source for changing.

**Minimum useful upload set:**

1. This report
2. The four event-map **PDFs** (and the plan-sheet PDFs if those are in scope)
3. `Floor 1 / 2 / 3 — Floor Plan.pdf` — **the most important omission to avoid.**
   Without them nothing in section 4 can be verified, no coordinate can be
   checked, and geometry cannot be regenerated
4. `DX_Tech_Deck` — the projection and signage specs
5. `Floor 3 — Reference Images.pdf` — needed for any vendor-table change

**To rebuild rather than hand-edit**, you need `geometry/f1–f3.json`
(~143 KB total), the whole of `src/`, and the brand assets named in section 2.
Cloning the generator repo is easier than assembling those by hand. If you
cannot reach it, say so rather than hand-editing an exported PDF or SVG — the
edit will not survive the next build.

---

## 3. Rebuilding

```bash
cd floor-maps
python3 src/build.py              # everything: 7 sheets + dist/index.html
python3 src/build_lobby.py        # or one sheet at a time while iterating
python3 src/build_trading.py
python3 src/build_gallery.py
python3 src/build_overview_map.py
python3 src/make_artifact.py      # rebuild dist/artifact.html after any change
```

Needs `pymupdf` and `playwright`. Chromium does the PNG rasterising and PDF
printing; the path is hardcoded at `event_map.CHROME` (imported from
`build.py`) as `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` — **update
that constant on a different machine.** There is no numpy or PIL in this
environment; image inspection was done with pymupdf `Pixmap.pixel()`.

`extract_walls.py` needs the source blueprint PDFs. `geometry/*.json` is
committed, so everything else runs standalone without them.

---

## 4. Six things that took real work — read before editing coordinates

### 4.1 North is to the RIGHT on every DX blueprint, not up

The north arrow on all three DX sheets is a circle with a tick pointing to the
**right of the page**. So the blueprints are drawn 90° off north-up. Every
event map rotates the plan 90° counter-clockwise to put north up.

The mapping you need whenever you read a coordinate off a blueprint:

```
blueprint +x  →  NORTH        blueprint page-top    →  WEST
blueprint +y  →  EAST         blueprint page-bottom →  EAST
                              blueprint page-left   →  SOUTH
                              blueprint page-right  →  NORTH
```

This is genuinely counter-intuitive when reading the data files. On Level 1 the
escalators sit at the page's **left** edge but land in the **south-west** of the
finished map; the coat check reads page-bottom-right but is **north-east**.

An earlier version of these sheets claimed "north is up" and was wrong. The
three 24 × 36 plan sheets now say "north is to the right" and draw their arrow
pointing right, because they keep the blueprint's orientation.

### 4.2 The rotation, in code

Data files store **blueprint PDF points**. The renderer converts:

```python
P(x, y) = (MX + (y - FRAME[1]) * S,        # u — increases EAST
           MY + (FRAME[2] - x) * S)        # v — increases SOUTH
```

The same rotation is expressed as an SVG matrix (`event_map.PLAN_XF`) so the
blueprint's own path data can be dropped in untouched:

```
matrix(0, -S, S, 0, MX - S*FRAME[1], MY + S*FRAME[2])
```

Scale is `4.5 pt = 1 ft-0 in` on every DX sheet (they are all 1/16" = 1'-0").
`S` is computed per sheet to fit `FRAME` into the panel — you never set it.

### 4.3 The tech deck's compass names are correct — once you know 4.1

The deck names projection walls "south wall", "east wall", "west Domino" and so
on. Those look like they contradict the blueprints, and an earlier version of
this work called that out as a venue error. It was not. Read with north to the
page-right, the deck's naming lands exactly on the blueprint geometry, on both
the Trading Floor and the Gallery. **The deck was right; the north assumption
was wrong.** Do not "fix" the deck's naming.

### 4.4 Gallery projection — confirmed geometry

Tech deck p.13–14 (the sidebar on those pages reads TRADING FLOOR, which is a
copy-paste slip in the deck itself; the TOC and the template links both say
Gallery). Surface is 7015 × 1080 px:

```
south run 3242 | gap 400 | corner 307 | east run 3066   = 7015
full south wall 3949 = 3242 + 400 + 307
```

The east run measures **46'-0"** on the drawing, which pins the surface at
~66.7 px/ft; the south run then lands on the **full height of the core's south
face**. The two runs wrap the hall's inside corner — the same corner
photographed on deck p.13. This is drawn on the sheet as a heavy magenta
polyline `(236,362) → (236,626) → (443,626)`.

### 4.5 Trading Floor projection — which wall is which, but no pixel extents

Deck p.7–8. Three walls, ~45 ft tall, ~270 ft total, delivered as one
6872 × 1080 px file:

```
north wall 2239 × 1080   (long wall, hall's north side — top of the map)
west wall  1679 × 1080   (short wall, carries the Domino screen 1655 × 630)
south wall 2239 × 1080   (long wall, hall's south side — bottom of the map)
```

**Do not divide these pixel widths along the walls.** Each long wall is a built
form — the deck shows a "cube" with draped areas either side — so the pixels do
not map onto the structural walls in proportion (2239/1679 = 1.33, but the
walls are 105 ft / 57 ft = 1.84). Marking which wall is which is solid;
drawing precise extents would be false precision. The exact numbers live in the
sheet's AV card instead.

### 4.6 The levels do not register against each other

Each DX blueprint was drawn as its own sheet with its own page origin. The
"freight elev." label sits at page-x ≈ 97 on Floors 1–2 but page-x ≈ 454 on
Floor 3 — they cannot both be right in a shared coordinate system. **Never
assume a shaft on one floor is at the same plan position on another.**

This is why the Getting Around sheet is a *section*, not a stacked plan: what
can be stated confidently is what each route **connects**, not where it sits.

---

## 5. Architecture

### Render pipeline (event maps)

`event_map.build(data_module)` →

1. `configure(mod)` — fits `FRAME` to the panel, computes `S`, `MX`, `MY`, `PLAN_XF`
2. `header()` — black band, logo, title, level chip
3. `plan()` — **the drawing order is the whole trick**:
   1. `PLATE` rect filled with the `staff` tone (so anything unnamed recedes)
   2. `ZONES` — room floors, tinted, **no strokes**
   3. `base_plan()` — the blueprint's own glazing, poché, wall edges, detail
   4. `overheads()`, `small_labels()`, `furniture()`, `routes()`, `surfaces()`
   5. `titles()`, `features()` — the numbered pin layer, always on top
4. `meta_strip()` — scale bar, north arrow, note
5. `right_column()` — key card, notes cards, footer
6. `svg_wrap()` → `render()` — Chromium screenshot + `page.pdf()`

**Zones are drawn *under* the poché.** That is deliberate: the simplified
rectangles in the data files never have to line up exactly with the real walls,
because the walls are painted on top and mask any overshoot. Do not "fix" a
zone that overshoots slightly — check the render first.

### Mass vs. wall

`is_mass()` decides whether a poché path is a solid block (service core,
adjoining structure → `MASS_FILL`) or a run of wall (→ near-white `WALL_FILL`).
It tests bbox area **and** the polygon's own area as a fraction of that box
(> 0.55). Bounding box alone is not enough: a long diagonal wall has a huge box
while enclosing almost nothing, which is exactly the Floor 1 case that broke an
earlier version.

`path_points()` parses the path properly because these paths use `H` and `V`
commands carrying a **single** coordinate — you cannot pair the numbers off two
at a time.

### The Getting Around sheet

`build_overview_map.py` draws its own body (level bands + transit-style lanes)
but borrows `header()`, `right_column()`, `badge()`, `chip()`, `svg_wrap()` and
`emit()` from `event_map` via `configure_chrome()`, which binds `G` without
trying to fit a plan. That is how the set stays one design.

---

## 6. Data schema

A floor data module needs these; everything else is optional.

### Required

```python
FRAME = (x0, y0, x1, y1)   # blueprint extent to draw (usually the geo bbox, trimmed)
PLATE = (x0, y0, x1, y1)   # gets the base "staff" tone
ZONES  = [dict(key=..., cat=..., pts=[(x,y), ...])]
TITLES = [dict(at=(x,y), size=, text=, sub=, sub_size=, num=, max_chars=, colour=)]
FEATURES = [dict(num=, cat=, icon=, at=(x,y), label=, side=, size=)]
KEY    = [dict(num=, cat=, label=, sub=, + one of: icon= / swatch=True /
                rule=True / dash=True / table=True)]
CARDS  = [dict(title=, accent=, body=)  or  dict(title=, accent=, rows=[(l,r)], note=)]
SHEET  = dict(key=, geometry="f2.json", level=, title=, tagline=,
              footer_left=, footer_right=, scale_note=)
from mapstyle import *      # brings in the palette + rect()
```

### Optional

| Name | Draws |
| --- | --- |
| `SMALL_LABELS` | quiet in-plan captions — `dict(at, text, size, rot)` |
| `RUNS` | repeated furniture — `dict(axis="x"/"y", const, lo, hi, n, len, depth)` |
| `GRIDS` | a lattice of furniture, e.g. seating — `dict(x0, x1, nx, y0, y1, ny, w, d)` |
| `RUN_LABELS` | labels for those — `dict(at, text, rot)` |
| `BLOCKS` | one-off furniture — `dict(box=(x0,y0,x1,y1))` |
| `ROUTES` + `ROUTE_LABEL` | dashed wayfinding lines — list of point lists |
| `SURFACES` | projection/screen walls — `dict(path, num, label, label_at, rot, w, glow, size)` |
| `OVERHEAD` | things crossing above the floor — `dict(box, label, label_at, rot)` |

### Vocabulary

```
cat (zone / badge category)
  hall      the headline event space (magenta)
  board     a second event room (deeper magenta)
  washroom  turquoise        stair     violet        elevator  cobalt
  service   tangerine        lounge    lime          plant     grey, crew-only
  staff     grey             corridor  near-white (FILL only, no ACCENT)

icon   accessible, coat, elevator, entrance, escalator, food, info,
       stairs, theatre, washroom          (defined in build.py ICONS)

side   "above" | "below" | "left" | "right"   — where a pin's label pill sits
```

Numbers may repeat: two pins with `num=5` both point at key row 5 (used for
paired fire stairs and elevators).

---

## 7. Common edits

**Change a category colour everywhere** → `src/mapstyle.py`, `FILL` / `ACCENT`.
Check `GLYPH_ON` has an entry for any new accent, or badges lose contrast.

**Rename a room / retitle a sheet** → the floor's data module, `TITLES` or
`SHEET`. No rendering code involved.

**Move a pin** → `FEATURES[n]["at"]`, in blueprint points. Read the coordinate
off the blueprint PDF with pymupdf `get_text("words")` rather than guessing.

**Fix a label collision** → change `side` first; move the anchor only if that
fails. The renderer does not detect overlaps — you have to look at the PNG.

**Add a key row** → append to `KEY`. Watch for the warning
`! right column overruns the sheet by N pt` — the fix is usually shortening a
card body so it wraps to fewer lines, not shrinking type.

**Add a whole floor** → copy a data module, point `SHEET["geometry"]` at the
right `geometry/f*.json`, set `FRAME`, describe the floor, add a
`build_*.py` wrapper, register it in `build.py:main()` and
`make_artifact.py:SHEETS`. No renderer changes needed.

**Update the shareable page** → `python3 src/make_artifact.py`, then republish
`dist/artifact.html` to the existing artifact URL (do not create a new one).

---

## 8. Pitfalls already hit — do not reintroduce

- **Flat colour blocks instead of real walls.** The first Gallery draft threw
  the poché away entirely. The client asked for the architecture back. Keep the
  blueprint linework; colour the floors *under* it.
- **`is_mass()` on bbox area alone** — greys out diagonal walls. See §5.
- **Naive path number-pairing** — `H`/`V` carry one coordinate. See §5.
- **Chip placement on rotated labels** — offset along the rotated axis (in `y`),
  not sideways, or the chip flies off the plan.
- **`data:` URI downloads in the artifact.** Artifacts render in a sandboxed
  iframe; without `allow-downloads` a `data:` URI download is **silently
  swallowed — it does not throw**, so there is nothing to catch and no way to
  detect it from the page. `make_artifact.py` rebuilds files as Blobs in JS and
  always shows a visible GitHub fallback. Do not "simplify" it back to
  `<a download href="data:...">`.
- **Don't embed each PNG twice** — the download reads it back off the `<img>`.
  That halved the page size.

---

## 9. Open questions for the venue

1. **Which Lobby door do guests use?** DX publishes access "from Bay Street and
   the TD Concourse". The plan shows two door clusters on the east side; both
   are pinned as entrances, and the key says to confirm routing.
2. **Is the Level 2 in-hall stair the one to the Gallery?** It is the only
   interior stair in the hall, and Level 3's centre stair does come down to
   Level 2 — but the two sheets place them ~15 ft apart, and per §4.6 the
   drawings do not register, so this is inference, not fact.
3. **Where is the Gallery LED wall (1920 × 1080)?** Specified in the deck, not
   sited on any drawing. Listed in the AV card, deliberately not pinned.
4. **Are the small Level 1 washrooms behind the office block public?** Treated
   as staff — single-fixture rooms behind the BOH corridor, while the plainly
   labelled public ones are the large stall blocks.
5. **Is the 350-seat theatre layout final?** It is now drawn on the Trading
   Floor sheet (`GRIDS` in `trading_data.py`), traced from "Vector – 350px
   Theater Style". 22 rows of 16 in two blocks with a centre cross-aisle. That
   is 352 marks against a stated 350, so a row is presumably two short — the
   sheet says 350. Re-check if the configuration changes.
6. **Vendor tables** on the Gallery sheet are traced from the event team's own
   "Vector – Gallery – Vendor Tables" plan. Indicative, not surveyed — re-check
   against the final layout.

---

## 10. Source material

| File | Used for |
| --- | --- |
| `Floor 1 / 2 / 3 — Floor Plan.pdf` | wall geometry, room names, dimensions, scale, north arrow |
| `Floor 3 — Reference Images.pdf` | the event team's vendor-table plan + 3D renders; also confirmed the north-up orientation choice |
| `Floor 1 / 2 — Reference Images.pdf` | 3D renders, sanity checks |
| `DX_Tech_Deck_01.01.2026_LR.pdf` | projection surfaces (p.7–8 Trading Floor, p.13–14 Gallery), Lobby LED sign (p.17), lighting/audio inventory (p.10–11) |
| `BrandGuidelines_QuickReference` | Vector palette, Karbon |
| designexchangetoronto.com, AccessTO | venue access, entrances |

Useful venue facts already extracted: Trading Floor ceiling **40'-0"**
unobstructed, hall **106'-2" × 57'-8"**; Gallery ceiling **12 ft**; Gallery
Boardroom (Patty Watt Room) **35'-9" × 22'-10"** with a 13'-3" screen; Lobby LED
sign is a **free-standing totem**, 1080 × 1920, PNG stills only, no video.
