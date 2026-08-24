# Arrow field — 2-minute loops

Two components, both **arrows only**: no ground gradient, no grain, no logo formation, no
speaker cards. Full resolution 6878 × 1080, transparent, exact 2-minute loops.

| Folder | Arrow speed | Loop |
| --- | --- | --- |
| `1x/` | the approved speed, unchanged | 2:00 |
| `0.5x/` | half the approved speed | 2:00 |

Both are built the same way as `../ambient-layer/`: six plates stacked back to front, each
with a **linear** position keyframe at 0:00 and 2:00, opacities as tabled. Sequence 2:00
long. Everything in the Premiere notes there still applies — Scale 100%, both Temporal and
Spatial Interpolation set to Linear, straight alpha, still-image default duration.

## What had to shift, and what did not

A loop closes only when the field has travelled a whole lattice vector, so

    loop distance = speed x duration

Cutting six minutes to two divides the loop distance by three; halving the speed as well
divides it by six. The **arrangement** has to repeat on that shorter distance. Nothing else
changes — not the arrow sizes, not the density, not the colours, not the layer opacities,
and in `1x/` not the speed.

The wrong way to do that is to shrink every tile, which is where I started: it satisfies
the loop but adds a horizontal and a vertical repeat, and squeezes the cell until one arrow
fits in it. The field turns into wallpaper.

The right way: the tile does not have to be a small rectangle, it has to be a **lattice**
containing the travel vector — and the second lattice vector is free to stay long. The
fundamental cell keeps its full area and its full complement of arrows, and the pattern
echoes only along the direction of travel.

| | 6-minute build | `1x/` | `0.5x/` |
| --- | --- | --- | --- |
| Arrow speed | 3.88–9.98 px/s | identical | half |
| Arrows on screen, layer 6 | 20 | 20 | 20 |
| Arrow sizes | 48–235 px | identical | identical |
| Echo along travel, layer 6 | 3,593 px | 1,198 px | 599 px |
| Echo horizontally / vertically | none | none | none |

The echo along the travel direction is the one real cost and it cannot be avoided — a
shorter loop distance *means* a shorter repeat. `0.5x/` has it twice as tight as `1x/`,
which is the honest trade for half the speed in the same two minutes. It is the thing to
look at on the actual wall before committing.

### Speeds are within 3% except where they are exact

Travel per loop has to land on whole pixels, so tile widths are snapped to a multiple of
15r. Layers 4 and 6 — the two most visible — come out exact in both builds; the rest move
by at most 2.9% (`1x/`) or 4.0% (`0.5x/`).

## `1x/` — approved speed, 2-minute loop

| Layer | Plate | Opacity | Position at 0:00 | Position at 2:00 |
| --- | --- | --- | --- | --- |
| 1 (bottom) | `layer1_plate_7362x1828.png` | 10% | 3349.0, 762.0 | 3529.0, 318.0 |
| 2 | `layer2_plate_7506x2016.png` | 16% | 3334.0, 799.0 | 3544.0, 281.0 |
| 3 | `layer3_plate_7687x2263.png` | 25% | 3311.5, 854.5 | 3566.5, 225.5 |
| 4 | `layer4_plate_7976x2662.png` | 42% | 3274.0, 947.0 | 3604.0, 133.0 |
| 5 | `layer5_plate_8305x3101.png` | 68% | 3236.5, 1039.5 | 3641.5, 40.5 |
| 6 (top) | `layer6_plate_8690x3552.png` | 100% | 3214.0, 1095.0 | 3664.0, −15.0 |

## `0.5x/` — half speed, 2-minute loop

| Layer | Plate | Opacity | Position at 0:00 | Position at 2:00 |
| --- | --- | --- | --- | --- |
| 1 (bottom) | `layer1_plate_7272x1606.png` | 10% | 3394.0, 651.0 | 3484.0, 429.0 |
| 2 | `layer2_plate_7401x1757.png` | 16% | 3386.5, 669.5 | 3491.5, 410.5 |
| 3 | `layer3_plate_7552x1930.png` | 25% | 3379.0, 688.0 | 3499.0, 392.0 |
| 4 | `layer4_plate_7811x2255.png` | 42% | 3356.5, 743.5 | 3521.5, 336.5 |
| 5 | `layer5_plate_8095x2583.png` | 68% | 3341.5, 780.5 | 3536.5, 299.5 |
| 6 (top) | `layer6_plate_8465x2997.png` | 100% | 3326.5, 817.5 | 3551.5, 262.5 |

Positions are Premiere / After Effects **Position** values — where the clip's anchor point
lands, and the anchor defaults to the clip's **centre**. Entering top-left coordinates
instead shifts every plate left by half its own width and leaves the field stopping about
46% across the frame. `layers.json` in each folder carries the top-left equivalents.

The 2:00 keyframe sits one frame past the last frame, which is correct — set the export
out-point at 2:00 so it is not included.

## Verification

**The loop is bit-exact in both.** Composited from the delivered plates, the frame at 0:00
and the frame at 2:00 are identical — max difference 0.000 on every channel.

That took three attempts, and the first two passed tests that were worthless:

- Comparing t=0 with t=120 proves nothing. A CSS animation repeats its transform every
  duration by definition, so those two frames are trivially identical whatever the
  geometry does. Comparing t=5 with t=125 has the same flaw.
- The real test is whether the field is unchanged when translated by one loop's travel.
  Run that way, the first build was wrong: replicas of an arrow were each drawing their own
  size and opacity jitter, so copies that had to be identical were not.
- With that fixed the geometry was right but the raster was not quite — Chromium's blur is
  not position-independent, so an arrow and its twin differed by up to 45/255 on their
  glow, on under 1% of pixels. `tools/periodise.py` collapses each orbit of pixels onto one
  value, which touches at most 1.9% of pixels by a few levels and makes the loop exact.

Also verified:

- **Plates reproduce the render**: mean 0.16/255 (`1x/`) and 0.18/255 (`0.5x/`) against
  browser-rendered full-resolution frames — the same figure as the six-minute plates, and
  the same cause, resampling filter difference on arrow edges at fractional offsets.
- **Speed measured off the built animation**: `0.5x/` layers 4 and 6 come out at exactly
  half, 3.6598 and 4.9906 px/s against 7.3196 and 9.9812.
- **The approved six-minute field is untouched** — all six of its plates regenerated after
  every change here and checksummed byte-identical against the committed ones.

## Regenerating

```sh
node animation/tools/export-plates.js --rate 1   --secs 120 --out DIR
node animation/tools/export-plates.js --rate 0.5 --secs 120 --out DIR
python3 animation/tools/periodise.py DIR
```

The periodise step is not optional — without it the loop is close but not exact. `?rate=`
and `?secs=` do the same on the render surface, and `export.js --rate 0.5 --secs 120`
renders frames from it.

`--rate S --secs T` requires `360 / (S x T)` to be a whole number, because the pattern has
to repeat a whole number of times per loop. 1x and 0.5x over 120 s give 3 and 6.
