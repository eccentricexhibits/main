# Event Floor Maps — Vector Institute at Design Exchange

Guest-facing wayfinding maps for the Design Exchange (234 Bay Street, Toronto),
built from the venue's own blueprints and set in the Vector Institute brand.

Five sheets:

| Sheet | Size | What it covers |
| --- | --- | --- |
| `gallery-event-map` | 24 × 16 in | Level 3 as a guest-facing **event map** — flat colour-blocked spaces, numbered pins, north up |
| `level-1-lobby` | 24 × 36 in | Arrival, check-in, coat check, washrooms, Grand Staircase |
| `level-2-trading-floor` | 24 × 36 in | The immersive projection theatre and its three screen walls |
| `level-3-gallery` | 24 × 36 in | Exhibition hall, Gallery Boardroom (Patty Watt Room), washrooms |
| `building-overview` | 24 × 36 in | How the three levels connect — every vertical route in the building |

Each sheet ships as `.pdf` (press-ready), `.svg` (vector, fonts embedded) and
`.png` (2×, for slides and screens). `dist/index.html` is a single-file viewer
with all five and download links.

## Two drawing styles

The four 24 × 36 in sheets are **plan sheets**: they carry the venue's own wall
poché with colour washed over it, and keep the blueprint's orientation. They
are the reference drawing — good for staff, production and anyone comparing
against DX's own documents.

`gallery-event-map` is an **event map**: the poché is thrown away and the floor
is rebuilt as flat filled shapes, one tone per category, with white gaps
between rooms and numbered pins keyed to a panel. Geometry still comes from the
blueprint, so the simplification stays dimensionally true — but nothing is drawn
that a guest does not need. This is the style to extend to the other levels.

## Design decisions

**One colour key, learned once.** Colour is semantic and constant across all
three levels, so a guest who reads the key on one sign can read every other
sign: magenta = the headline event space, cobalt = elevators, violet = stairs
and escalators, turquoise = washrooms, tangerine = coat check / food, lime =
secondary rooms. Glyph colours are picked per background to clear 4.5:1
contrast — dark glyphs on turquoise, tangerine and lime; white on the rest.

**The three things people actually ask for** are given the most weight: where
the show is, where the washrooms are, and how to get between floors. Hence the
standing "Getting between floors" panel on every sheet, the explicit *no
washrooms on Level 2* warning, and the overview sheet.

**North is not up on the venue's drawings.** The north arrow on every DX sheet
points to the *right* of the page. The four plan sheets keep that orientation
and label it; the event map rotates the plan 90° counter-clockwise so north is
up, which also matches the orientation of the event team's own 3D gallery
renders.

**The base plan is real.** Wall geometry is extracted from the vector content
of the venue's blueprints rather than traced, so room shapes, door swings,
stair runs and lift shafts are dimensionally correct. Scale is 4.5 pt = 1 ft-0 in
(the blueprints are 1/16" = 1'-0").

## Building

```bash
python3 src/extract_walls.py    # blueprints -> geometry/f{1,2,3}.json
python3 src/build.py            # geometry + content -> dist/
```

`extract_walls.py` needs the source blueprint PDFs; `geometry/*.json` is
committed so `build.py` runs standalone. Requires `pymupdf` and `playwright`
(Chromium is used for PNG rasterising and PDF printing).

- `src/mapdata.py` — content for the four plan sheets: zones, pins, labels,
  callouts, palette. Edit this to move a label or retitle a room.
- `src/gallery_data.py` — content for the Gallery event map, same idea.
- `src/build.py` — SVG assembly, icon set, sheet layout, output. Running it
  also builds the event map and the viewer.
- `src/build_gallery.py` — the event-map renderer, on its own if you want to
  iterate on just that sheet.

## Sources

- `Floor 1/2/3 — Floor Plan.pdf` — DX blueprints (geometry, room names, scale)
- `DX_Tech_Deck_01.01.2026` — projection surfaces: the Trading Floor's three
  walls (~45 ft × 270 ft, 6872 × 1080 px), the Gallery's projection and LED
  walls, and the Gallery Boardroom name
- `BrandGuidelines_QuickReference` — Vector Institute palette and Karbon type
- Venue access details (Bay Street and TD Concourse entrances) from
  designexchangetoronto.com and AccessTO

## Known assumptions

- **Entrances.** The venue publishes Lobby access "from Bay Street and the TD
  Concourse", and the blueprint shows escalators down to the concourse in the
  north-west plus a link corridor along the north edge. The sheets mark the
  arrival zone and the escalators rather than asserting a specific street door —
  worth confirming with DX before print, along with which door your guests are
  actually routed through on the night.
- **Screen wall names — resolved.** The tech deck's "South / West Domino /
  North" naming looked like it contradicted the blueprint, but that was an
  artefact of assuming north was up. Read with north to the page-right, the
  deck's compass names land exactly on the blueprint's geometry, on both the
  Trading Floor and the Gallery. The sheets still label the Trading Floor walls
  by position, which is unambiguous either way.
- **Gallery vendor tables.** The event map shows the vendor rows from the event
  team's own "Vector – Gallery – Vendor Tables" plan (Floor 3 reference images).
  They are drawn as indicative bands of tables, not surveyed positions, and
  should be re-checked against the final floor plan.
- **The Gallery LED wall** (1920 × 1080) is specified in the tech deck but not
  sited on any drawing, so the event map lists it without pinning it to a wall.
- Back-of-house rooms (Eatertainment offices, storage, staff washrooms off the
  Level 1 east corridor) are deliberately left untinted so guests read them as
  "not for me".
