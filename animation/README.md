# Official arrow — diagonal travel loop

A 6878 × 1080 field of the official arrow travelling up and to the right along its own
axis, as a seamless three-minute loop. Currently a **web mock-up**, held for approval
before anything is encoded to video.

| | |
| --- | --- |
| Canvas | 6878 × 1080 px |
| Duration | 180.000 s, seamless (last frame is pixel-identical to the first) |
| Ground | `#8A25C9` |
| Arrow fill | linear gradient `#B659F0` (lower left) → `#48C0D9` (upper right), axis parallel to travel, applied per arrow |
| Travel | slope +2.4667 (run 15 : rise 37), 67.93° above horizontal |
| Speed | 7.8 – 20.0 px/s across six depth layers |
| Field | ~352 arrows on screen, ~14% ink coverage |
| Artwork | `Vector Official - Arrow Regular.svg`, unmodified and unrotated |

## Files

| File | What it is |
| --- | --- |
| `arrow-animation-mockup.html` | The review page — viewer, transport, scrub, loop-point check, spec sheet. Self-contained. |
| `arrow-animation-render.html` | Bare 6878 × 1080 surface with a `seek(seconds)` hook. The export source. |
| `arrow-field.js` | The engine. Single source of truth for geometry, colour and layer config. |
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
t = 180 s is the frame at t = 0 s, with nothing to cross-fade. Tile widths are multiples
of 15 so `TH` stays a whole number; fractional tile sizes produce visible seams.

One consequence worth knowing: loop distance is `|(TW, −TH)| = 2.6617 × TW`, so **tile
width alone sets a layer's speed**. Wider tile → faster layer and more unique pattern
before it repeats. The six layers use mutually non-commensurate widths, so the composite
has no repeat period the eye can find across 6878 px even though each layer repeats.

Arrows are placed by blue-noise sampling on the tile's torus, and any arrow straddling a
tile edge is drawn again on the opposite side, so tiles butt cleanly.

## Verifying

```sh
node animation/build.js
VERIFY_SCALE=1 node animation/verify.js 0 10 90 180
python3 animation/analyze.py
```

`analyze.py` reports ink coverage per frame, confirms t = 180 matches t = 0, and
recovers the travel vector by matching frames.

**Check the seam at `VERIFY_SCALE=1` only.** A scaled screenshot lands layers on half
pixels and reports anti-aliasing noise as a mismatch. At 1:1 the difference across all
7,428,240 pixels is exactly zero.

`--layer N` isolates one layer, which is how the travel angle was measured
independently of the other five:

```sh
VERIFY_SCALE=1 node animation/verify.js --layer 6 0 5
```

Layer 6 moves (38, −92) px over 5 s against a predicted (37.5, −92.5) — inside the
one-pixel quantisation of an integer match.

## Exporting (after approval)

```sh
node animation/export-frames.js --fps 30 --out /tmp/frames
ffmpeg -framerate 30 -i /tmp/frames/f_%05d.png -c:v prores_ks -profile:v 3 arrow-loop.mov
```

Frames are seeked explicitly rather than screen-captured, so none are dropped or
duplicated. 180 s divides evenly at 24, 25, 30 and 60 fps.

## Tuning

Everything adjustable lives in `CONFIG` at the top of `arrow-field.js`: per-layer tile
width (speed), arrow height, opacity, and arrows per tile, plus the global size and
opacity jitter ranges. Density was matched to the client's reference clip by ink
coverage — the reference sits at 0.145 / 0.119 / 0.102 / 0.075 at difference thresholds
12 / 25 / 40 / 60, and this field sits at 0.143 / 0.122 / 0.103 / 0.084.
