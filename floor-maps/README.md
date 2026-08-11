# Event Floor Maps — Vector Institute at Design Exchange

Guest-facing wayfinding maps for the Design Exchange (234 Bay Street, Toronto),
built from the venue's own blueprints and set in the Vector Institute brand.

Four sheets, each 24 × 36 in portrait:

| Sheet | What it covers |
| --- | --- |
| `level-1-lobby` | Arrival, check-in, coat check, washrooms, Grand Staircase |
| `level-2-trading-floor` | The immersive projection theatre and its three screen walls |
| `level-3-gallery` | Exhibition hall, Gallery Boardroom (Patty Watt Room), washrooms |
| `building-overview` | How the three levels connect — every vertical route in the building |

Each sheet ships as `.pdf` (press-ready), `.svg` (vector, fonts embedded) and
`.png` (2×, for slides and screens). `dist/index.html` is a single-file viewer
with all four and download links.

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

- `src/mapdata.py` — all content: zones, pins, labels, callouts, palette.
  Edit this to move a label or retitle a room; no rendering code involved.
- `src/build.py` — SVG assembly, icon set, sheet layout, output.

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
- **Screen wall names.** The tech deck names the Trading Floor surfaces
  "South / West Domino / North", which does not line up with the blueprint's
  north arrow. The sheets label them by position instead — the Domino screen on
  the short far wall, projection walls down both long sides — which matches the
  deck's own pixel dimensions (2239 / 1679 / 2239 px against 76 ft / 58 ft / 76 ft).
- Back-of-house rooms (Eatertainment offices, storage, staff washrooms off the
  Level 1 east corridor) are deliberately left untinted so guests read them as
  "not for me".
