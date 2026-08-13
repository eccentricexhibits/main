# Review — Design Exchange event floor maps

A full check of the floor-map set built on branch
`claude/design-exchange-floor-maps-0icdz3` (generator under `floor-maps/`),
verified against the venue source material in `eccentricexhibits/floorplan`
(blueprints, tech deck, reference images) and the shipped "Claude Code -"
PDFs in that bundle. Review only — no fixes applied.

## What checks out

- **Orientation.** All three blueprints' north arrows point page-right,
  confirming HANDOFF §4.1. Every compass claim on the four event maps was
  re-derived independently and holds: entrances east, Grand Staircase
  south-east, Domino screen west, north/south projection walls, all washroom
  and stair placements. The tech deck's compass wall names land on the
  blueprint geometry under the north-right reading, as §4.3 says.
- **Reproducibility.** Rebuilding all seven sheets from source produced PNGs
  bit-identical to the committed `dist/` — source, geometry and outputs are
  in sync.
- **Tech-deck numbers.** 6872 × 1080 (2239/1679/2239 walls), 7015 × 1080
  (3242 · 400 · 307 · 3066, east run 46'-0"), LED wall 1920 × 1080, lobby
  totem 1080 × 1920 with 980 × 1820 safe area, PNG stills only — all match
  the deck.
- **Blueprint labels.** Coat check (+ storage), women's/men's/universal
  washrooms, kitchen, Bridge Over, Patty Watt Room, freight elev., Grand
  Staircase — all sit inside the zones the data modules define.

## 1. Print-critical — every PDF renders the artwork at 75% size

All seven PDFs (committed `dist/` and the shipped bundle) have the artwork
in the top-left 75% of the page: 18 × 12 in on the 24 × 16 sheets,
18 × 27 in on the 24 × 36 sheets, with blank margin right and bottom.
Cause: the SVG is 1728 CSS px wide, Chromium prints CSS px at 96/in
(= 18 in), but `page.pdf()` declares a 24 in page. Affects `render()` in
both `event_map.py` and `build.py`. Fix: pass `scale=96/72` to
`page.pdf()` (or style the SVG in physical units), then re-export the
bundle PDFs. PNGs and SVGs are unaffected.

## 2. Content errors on the 24 × 36 plan sheets (`mapdata.py`)

Fossils of the earlier "north is up" assumption — corrected on the event
maps, not on the plan sheets:

- **L1 entrance pinned on the wrong side.** Pin at (392, 205) = page-top =
  west, inside the Eatertainment office area. The real door clusters (67"
  clear widths) are on the page-bottom = east edge, where the event map
  pins them.
- **L1 "Grand Staircase in the south-west corner"** (connections text) —
  it is the south-east corner. Same wording in `make_artifact.py`'s
  description for this sheet.
- **L2 wrong stair labelled "Grand Staircase — down to Lobby".** The
  labelled pin (275, 575) is the mid-hall stair (the one inferred to go up
  to the Gallery — HANDOFF §9.2). The actual Grand Staircase is the
  south-east corner stair (blueprint "DN" at 152.7, 635.9; registers with
  L1's "Grand Staircase to Traiding Floor" label). That stair is drawn but
  unlabelled.
- **L3 claims a universal washroom** (zone sub-label, accessible pin,
  legend row). The L3 blueprint has women's and men's only; the universal
  washroom is on L1. The event maps and overview card state this correctly,
  so the set contradicts itself on an accessibility fact.
- **L3 sites the LED wall** (south edge of hall). Its position is
  unconfirmed (HANDOFF §9.3); the event map deliberately lists it without
  pinning.
- **All three plan sheets tint the freight shaft as a passenger elevator**
  (cobalt, passenger pin, "Elevator — All levels" legend). Event maps
  correctly mark freight crew-only.

## 3. Factual slip on the current event maps

Trading Floor key row 9: Domino screen "**1655** × 630 px". The venue's own
template (`DX_TradingFloor_Immersive_Template-scaled_fullSize.png` and the
deck surface map) says **1653** × 630. HANDOFF §4.5 carries the same 1655.

## 4. Consistency and hygiene

- **Bundle staleness.** `Claude Code - Event Map - Level 3 - Gallery.pdf`
  in `eccentricexhibits/floorplan` differs visibly (~6% of pixels) from the
  current build — freight badge colour, plan framing. The other six match.
  Re-export after the PDF fix regardless.
- **Freight category inconsistent** across event maps: `gallery_data.py`
  uses `cat="service"` (tangerine); trading/lobby use `plant` (grey), which
  `mapstyle.py`'s comment says is the freight category.
- **Elevator counts don't reconcile.** Overview key: "two locations on each
  floor"; L1/L2 keys: both elevators "serve every level"; but L3 (sheet and
  blueprint core — verified: one passenger shaft plus freight) shows one
  passenger elevator. Cannot all be true. Suggest adding to HANDOFF §9 as
  an open question for the venue rather than guessing.
- **README miscount**: "The four 24 × 36 in sheets are plan sheets" — there
  are three (and four 24 × 16 event-style sheets).
- Cosmetic: Trading key rows 10–11 and Gallery row 10 show numbered chips
  that appear nowhere on the plan (swatch-identified only). L1 plan text
  "leave coats at the east wall" is loose — the coat check is one room in
  from the north-east corner.

## Deliberately not re-derived

Per HANDOFF §4/§9: vendor rows, the 350-seat grid (352 marks labelled 350
is a documented compromise), and trading-wall pixel extents were left as
traced. The deck's compass wall names were verified, not "fixed".
