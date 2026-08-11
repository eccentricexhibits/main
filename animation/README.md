# Official arrow — diagonal travel loop

A 6878 × 1080 field of the official arrow travelling up and to the right along its own
axis, as a seamless six-minute loop, with a once-per-loop transition that converges the
field into the Vector logo on the Domino screen. Built to the DX Trading Floor immersive
template. Currently a **web mock-up**, held for approval before anything is encoded to
video.

| | |
| --- | --- |
| Canvas | 6878 × 1080 px |
| Duration | 360.000 s, seamless (last frame is pixel-identical to the first) |
| Ground | vertical gradient, `#13071A` top → `#3B1056` bottom, with 3% grain to dither the ramp |
| Arrow fill | linear gradient `#8A25C9` (lower left) → `#48C0D9` (upper right), axis parallel to travel, applied per arrow |
| Logo magenta | `#EB088A` — the brand value, which overrides the EPS's approximate CMYK→RGB conversion |
| Travel | slope +2.4667 (run 15 : rise 37), 67.93° above horizontal |
| Speed | 3.9 – 10.0 px/s across six depth layers |
| Field | ~352 arrows on screen, each with a soft halo and a light trail |
| Artwork | `Vector Official - Arrow Regular.svg`, unmodified and unrotated |
| Venue | DX Trading Floor — 7 panels, cube band from y 674, Domino screen 1653 × 630 |
| Transition | 4:00 → 4:26.5, once per loop; 365 arrows converge, 235 of them form the mark |

## Files

| File | What it is |
| --- | --- |
| `arrow-animation-mockup.html` | The review page — viewer, transport, scrub, loop-point check, spec sheet. Self-contained. |
| `arrow-animation-render.html` | Bare 6878 × 1080 surface with a `seek(seconds)` hook. The export source. |
| `arrow-field.js` | The ambient engine. Single source of truth for geometry, colour and layer config. |
| `arrow-transition.js` | The logo event — sweep, gather, reveal, resolve, hold, release. |
| `venue.js` | Panel geometry measured off the venue template. |
| `assets/vector-logo-horizontal.svg` | The bilingual lockup, converted from the supplied EPS. |
| `assets/mark-points.js` | The mark sampled onto a grid — generated, do not hand-edit. |
| `tools/eps-to-svg.py` | Recovers the logo artwork from the Illustrator EPS. |
| `tools/sample-mark.js` | Regenerates `mark-points.js` at a given grid spacing. |
| `templates/` | Page shells with an `__ENGINE__` slot. |
| `build.js` | Inlines the engine (and the Karbon faces) into the two self-contained pages. |
| `verify.js` / `analyze.py` | Render frames headlessly and check the loop, angle and density. |
| `export-frames.js` | Frame-accurate PNG export. Not run yet. |
| `HANDOFF.md` | Why every number is what it is — read this before changing anything, or before rebuilding elsewhere. |

Rebuild after editing `arrow-field.js` or anything in `templates/`:

```sh
node animation/build.js
```

## How the seamless loop works

Every layer is one element carrying a repeating background tile of `TW × TH` px, with
`TH / TW` fixed at `37 / 15`. That makes the vector `(TW, −TH)`:

1. point exactly along the travel direction, and
2. a lattice vector of the tiling.

So translating a layer by `(TW, −TH)` lands the pattern back on itself — the frame at
t = 360 s is the frame at t = 0 s, with nothing to cross-fade. Tile widths are multiples
of 15 so `TH` stays a whole number; fractional tile sizes produce visible seams.

One consequence worth knowing: loop distance is `|(TW, −TH)| = 2.6617 × TW`, so **tile
width and duration together set a layer's speed** — `2.6617 × TW / duration`. Wider tile
→ faster layer and more unique pattern before it repeats; a longer loop slows everything
proportionally without touching the pattern (which is exactly how the six-minute version
halved the speed of the three-minute one). The six layers use mutually non-commensurate widths, so the composite
has no repeat period the eye can find across 6878 px even though each layer repeats.

Arrows are placed by blue-noise sampling on the tile's torus, and any arrow straddling a
tile edge is drawn again on the opposite side, so tiles butt cleanly.

## The transition

Once per loop the ambient field steps aside and the wall resolves into the logo:

| Phase | Length | What happens |
| --- | --- | --- |
| sweep | 7 s | Ambient fades down. Arrows drop in from off the top and bottom edges, round a corner into a horizontal lane, and cruise toward the centre — nose-first, so they face where they are going. |
| gather | 4 s | Each arrow swoops out of its lane onto a point sampled from the Vector mark, straightening back up as it lands and shrinking from ambient scale to ~14 px. Arrows with no point to fill dissolve. |
| reveal | 2.5 s | The crisp mark fades in over the arrows; the arrows fade out. |
| resolve | 2 s | The mark eases into its slot in the full bilingual lockup as the wordmark fades in beside it. |
| hold | 5 s | The finished logo sits at 70% of the Domino screen's width. |
| release | 6 s | Logo out, ambient field back. |

Every journey is three moves — drop in, cruise, swoop — evaluated by `positionAt(p, d)`
as a single closed-form function of distance travelled. Heading comes from a finite
difference along that same function rather than a hand-derived tangent per leg, which is
what keeps a three-segment path from needing three separate rotation cases.

Two details make it work:

- **Journeys are laid out backwards.** Each arrow's arrival time is what gets spread
  across the window; its entry point falls out of that. Speeds come out near-uniform
  without being pinned, and the wall keeps feeding the centre instead of draining.
- **There is no gate.** An arrow leaves its lane when it comes within its own randomised
  distance (420–860 px) of its destination, and vertical position is a function of that
  distance rather than of elapsed time. A single shared turn-in point — which is what an
  explicit gate is — stacks arrows into a vertical column down the wall before they fly
  to the mark.
- **Rotation is temporary.** Arrows follow their flight path — nose down on the way in,
  along the lane on the cruise, banking through the swoop — and straighten back to brand
  orientation over the last quarter of the swoop, so the mark is always built out of
  upright arrows.
- **Only the arrows that land carry the logo's colours.** They are white or magenta from
  the moment they enter; the ones destined to dissolve stay in the ambient palette. Mark
  points are split left/right between the two streams so they do not reach across each
  other, but a quarter are swapped over — a strict split sends every magenta arrow down
  one side, since they all sit on the mark's right, and the two streams then read as two
  differently coloured flocks.
- **It is a pure function of t.** No integration, no accumulated state — `draw(t)` gives
  the same pixels at any time, which is what keeps the whole loop seekable and therefore
  exportable frame by frame. The particle canvas is cleared and inert outside the event,
  so t = 0 and t = 360 stay pixel-identical.

`TRANSITION.finish` picks how the reveal resolves: `settle` (default) forms the mark
large and eases it into the lockup, `inPlace` forms it at lockup size and just fades the
lockup over the top, `markOnly` stops at the crisp mark and never brings in the wordmark.

## Regenerating the logo assets

```sh
python3 animation/tools/eps-to-svg.py <the-lockup>.eps \
  animation/assets/vector-logo-horizontal.svg --magenta '#EB088A'
node animation/tools/sample-mark.js --spacing 3.6
node animation/build.js
```

The EPS is an AI11 EPS whose page content is plain PostScript using Illustrator's short
operators (`mo`/`li`/`cv`/`cp`, `cmyk`, `f`), so the artwork comes out exactly, with no
rasterising and no Ghostscript — which is not available in this container. Smaller
`--spacing` means more, finer arrows in the formed mark.

`--magenta` replaces every non-white fill with the given value. CMYK→RGB out of an EPS is
only ever an approximation — this file converts to `#FF0FF1` — so the brand's own sRGB
value is what ships.

## Verifying

```sh
node animation/build.js
VERIFY_SCALE=1 node animation/verify.js 0 60 180 360
python3 animation/analyze.py
```

`analyze.py` reports ink coverage per frame, confirms the last frame matches t = 0, and
recovers the travel vector by matching frames. Coverage is measured against `plate.png`,
a render of the background and grain with no arrows, so the vertical ground gradient does
not count as ink.

**Check the seam at `VERIFY_SCALE=1` only.** A scaled screenshot lands layers on half
pixels and reports anti-aliasing noise as a mismatch. At 1:1 the difference across all
7,428,240 pixels is exactly zero.

`--layer N` isolates one layer, which is how the travel angle was measured
independently of the other five:

```sh
VERIFY_SCALE=1 node animation/verify.js --layer 6 0 10
```

Layer 6 moves (37.5, −92.5) px per 10 s at the six-minute duration. Phase correlation is
unreliable on a periodic field — it finds many equal peaks — so measure with direct block
matching over a short interval.

## Exporting (after approval)

```sh
node animation/export-frames.js --fps 30 --out /tmp/frames
ffmpeg -framerate 30 -i /tmp/frames/f_%05d.png -c:v prores_ks -profile:v 3 arrow-loop.mov
```

Frames are seeked explicitly rather than screen-captured, so none are dropped or
duplicated. 360 s divides evenly at 24, 25, 30 and 60 fps — 10,800 frames at 30.

## Tuning

Everything adjustable lives in `CONFIG` at the top of `arrow-field.js`: duration,
background gradient, arrow gradient, per-layer tile width (speed), arrow height, opacity
and arrows per tile, the global size and opacity jitter ranges, and the glow, trail and
grain settings.

Density was originally matched to the client's reference clip by ink coverage. That
comparison is now only indicative — the reference was measured against a flat purple
ground, and this piece sits on a dark gradient, so the same arrows register far more
contrast.

Setting `glow.opacity` or `trail.opacity` to 0 drops those elements from the tile
entirely rather than drawing them invisibly, and `dither: 0` removes the grain layer.

**Effects are declared in the arrow's own coordinates**, inside the reused `<g id="s">`,
so each `<use>`'s scale carries the blur with it and a 48 px arrow gets proportionally
the same halo as a 235 px one. Note that the trail reaches well outside the arrow's
bounding box, so tile culling and edge duplication work off `spriteBox()` — the union of
arrow, trail and blur bleed. Using the arrow's own bbox there would clip glow at seams.
