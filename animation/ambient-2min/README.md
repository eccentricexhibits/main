# Ambient field — 2-minute loop, unchanged arrow speed

The venue caps a video at 2 minutes. This is the same field as the six-minute build, with
the arrows moving at **exactly the same speed** — only the loop is shorter. Same
resolution, same transparency, same density, same arrow sizes.

## What had to change, and what did not

Nothing about the motion. A shorter loop means the field has to land back on itself after
a shorter distance, so what changes is the *placement*: the arrangement now repeats along
the travel direction every third of a tile instead of every whole tile.

The obvious way to do that — shrink every tile to a third — is wrong, and was my first
answer. It satisfies the loop but throws in two repeats nobody asked for, one horizontal
and one vertical, and shrinks the cell so far that only one arrow fits in it. That is what
turns the field into wallpaper. `other-speeds/1x/` is that version, kept for comparison.

The right way: a tile does not have to be a small rectangle. It has to be a **lattice**
containing the travel vector, and the second lattice vector is free to stay long. So the
fundamental cell keeps exactly the area it has today and holds exactly as many arrows —
the pattern simply echoes along the direction of travel and nowhere else.

| | Six-minute build | This 2-minute build |
| --- | --- | --- |
| Arrow speed | 3.88–9.98 px/s | **identical** |
| Arrows on screen per layer | 20–109 | **identical** |
| Arrow sizes | 48–235 px | identical |
| Cell area (arrows per cell) | 10–14 | identical |
| Repeats along travel | every 3,593 px (layer 6) | every 1,198 px |
| Repeats horizontally / vertically | none within the frame | none within the frame |

The echo along the travel direction is the one genuine cost, and it is not avoidable: a
shorter loop *means* a shorter repeat distance. Everything else is preserved.

### One small adjustment

Travel per loop is a third of a tile and has to land on a whole pixel, so four of the six
tile widths were nudged to the nearest multiple of 45. That shifts those layers' speeds by
at most 2.9%, and **layers 4 and 6 — the two most visible — are exactly unchanged**.

| Layer | Tile width | Speed change |
| --- | --- | --- |
| 1 | 525 → 540 | +2.9% |
| 2 | 645 → 630 | −2.3% |
| 3 | 750 → 765 | +2.0% |
| 4 | 990 → 990 | none |
| 5 | 1200 → 1215 | +1.2% |
| 6 | 1350 → 1350 | none |

## The build

Identical to the six-minute build in `../ambient-layer/README.md` — six plates stacked in
order, **linear** position keyframes, opacities as tabled — with the sequence **2:00** long
and the second keyframe at **2:00**.

| Layer | Plate | Opacity | Position at 0:00 | Position at 2:00 |
| --- | --- | --- | --- | --- |
| 1 (bottom) | `layer1_plate_7090x1556.png` | 10% | 3349.0, 762.0 | 3529.0, 318.0 |
| 2 | `layer2_plate_7120x1630.png` | 16% | 3334.0, 799.0 | 3544.0, 281.0 |
| 3 | `layer3_plate_7165x1741.png` | 25% | 3311.5, 854.5 | 3566.5, 225.5 |
| 4 | `layer4_plate_7240x1926.png` | 42% | 3274.0, 947.0 | 3604.0, 133.0 |
| 5 | `layer5_plate_7315x2111.png` | 68% | 3236.5, 1039.5 | 3641.5, 40.5 |
| 6 (top) | `layer6_plate_7360x2222.png` | 100% | 3214.0, 1095.0 | 3664.0, −15.0 |

These are Premiere / After Effects **Position** values — where the clip's anchor point
lands, and the anchor defaults to the clip's **centre**. Entering top-left coordinates here
shifts every plate left by half its own width and leaves the field stopping about 46%
across the frame.

Top-left equivalents, for anything that positions by corner:

| Layer | Top-left at 0:00 | Top-left at 2:00 | Plate | Travel per loop |
| --- | --- | --- | --- | --- |
| 1 | −196, −16 | −16, −460 | 7090 × 1556 | 180, −444 |
| 2 | −226, −16 | −16, −534 | 7120 × 1630 | 210, −518 |
| 3 | −271, −16 | −16, −645 | 7165 × 1741 | 255, −629 |
| 4 | −346, −16 | −16, −830 | 7240 × 1926 | 330, −814 |
| 5 | −421, −16 | −16, −1015 | 7315 × 2111 | 405, −999 |
| 6 | −466, −16 | −16, −1126 | 7360 × 2222 | 450, −1110 |

All the Premiere specifics still apply: Scale 100%, both Temporal and Spatial Interpolation
set to Linear, still-image default duration, straight alpha. The 2:00 keyframe sits one
frame past the last frame, which is correct — set the export out-point at 2:00 so it is not
included.

## Verification

- **The loop is exact, tested across the wrap rather than at it.** Seeking to exactly the
  loop length lands back on iteration zero and proves nothing, so the test compares t=5
  against t=125 and t=37 against t=157 — genuinely different iterations. Both: **0
  differing pixels** on every channel across all 7,428,240.
- **Speed is unchanged.** Measured off the built animation, per-layer speeds match the
  six-minute build to four decimal places on layers 4 and 6 and within 2.9% elsewhere, and
  on-screen arrow counts are identical layer for layer.
- **The plates reconstruct the render**, mean visible error 0.21/255 — the same figure as
  the six-minute plates, and the same cause: resampling filter difference on arrow edges at
  fractional offsets.
- **The shipped six-minute field is untouched.** All six of its plates were regenerated
  after these engine changes and checksummed against the committed ones — byte-identical.

## Other loop lengths

The divisor is a parameter, so any whole fraction of six minutes is available:

| Divisor | Loop | Echo along travel (layer 6) |
| --- | --- | --- |
| 2 | 3:00 | every 1,797 px |
| **3** | **2:00** | **every 1,198 px** |
| 4 | 1:30 | every 898 px |
| 6 | 1:00 | every 599 px |

3 is the one that fits the cap with the longest possible repeat distance, which is why it
is the build here. Ask if a shorter file is ever needed and I will cut the plates for it.

## Regenerating

```sh
node animation/tools/export-plates.js --short 3 --out DIR
```

`?short=3` does the same on the render surface, and `export.js --short 3` renders frames
from it. `--short` takes a whole number only — a loop 2.5 times shorter is not a loop.

## `other-speeds/`

The earlier round, built when I misread the brief as wanting different arrow speeds. All
four are exact 2-minute loops, but they change the motion: `3x/` is the approved field
played three times as fast (its plates are byte-identical to `../ambient-layer/`), `2x/`
holds up, and `1x/` and `0.5x/` are the shrunken-tile versions this build replaces.
