# Ambient field — 2-minute loops at four speeds

The venue caps a video at 2 minutes, so these are exact 120-second loops. Same six-plate
build as `../ambient-layer/`, same full resolution, same transparency — only the tile
geometry and the loop length differ.

## The constraint, which is geometry rather than preference

**Loop distance = speed × duration.** The field only lands back on itself after travelling
exactly one tile, so once the loop length is fixed at 120 s, **tile size is proportional to
speed**. There is no way to choose them independently:

| Speed | Tile size | Arrows per tile | Density vs approved | Verdict |
| --- | --- | --- | --- | --- |
| 3x | 525–1350 px — today's exactly | 10–14 | 1.00 | identical to what you approved |
| 2x | 345–900 px | 4–6 | 0.92–0.98 | holds up |
| 1x | 180–450 px | 1–2 | 0.72–1.29 | reads as a lattice |
| 0.5x | 90–225 px | 1 (forced) | 2.6–3.4 | not usable as-is |

Slower means a shorter loop distance means a smaller tile. A third of the width is a ninth
of the area, so the tile holds a ninth of the arrows. Below roughly two arrows per tile the
placement stops reading as scattered and starts reading as a repeating grid — and at 0.5x
the count cannot go below one, so the field also ends up about three times denser than
intended. That is why the bottom two rows are marked the way they are.

**3x is free.** Its plates are byte-identical to the six in `../ambient-layer/` — a
2-minute 3x loop is literally the approved field played three times as fast, not a
re-render. Verified by checksum.

## Getting a slow field inside 2 minutes anyway

If 1x or 0.5x is what the venue actually wants, the tile route is the wrong one and there
are two better ones:

1. **Hide the wrap in a fade.** If the piece has any moment where the arrows reach zero
   opacity — the way the field clears out under the logo event in the six-minute show —
   the loop can wrap there invisibly, and the constraint disappears entirely. Any speed
   then works with today's full-size tiles. This is the clean answer if a 2-minute cut
   includes an event.
2. **Cross-dissolve the loop.** Build 121.5 s at true 1x or 0.5x with the full-size tiles,
   then overlap the last 1.5 s onto the first and cross-dissolve. The field is
   statistically uniform, so the dissolve reads as a brief flutter in density rather than a
   jump. Not pixel-exact, but it keeps the approved texture, which the small-tile versions
   do not.

Worth asking the venue whether the 2-minute cap is hard before either — the six-minute
build already exists and needs nothing.

## Build tables

### 0.5x — `0.5x/plates/`

| Layer | Plate | Opacity | Position at 0:00 | Position at 2:00 |
| --- | --- | --- | --- | --- |
| 1 (bottom) | `layer1_plate_7000x1334.png` | 10% | 3394.0, 651.0 | 3484.0, 429.0 |
| 2 | `layer2_plate_7015x1371.png` | 16% | 3386.5, 669.5 | 3491.5, 410.5 |
| 3 | `layer3_plate_7030x1408.png` | 25% | 3379.0, 688.0 | 3499.0, 392.0 |
| 4 | `layer4_plate_7075x1519.png` | 42% | 3356.5, 743.5 | 3521.5, 336.5 |
| 5 | `layer5_plate_7105x1593.png` | 68% | 3341.5, 780.5 | 3536.5, 299.5 |
| 6 (top) | `layer6_plate_7135x1667.png` | 100% | 3326.5, 817.5 | 3551.5, 262.5 |

Tiles 90–225 px, 7000×1334 to 7135×1667 plates, 1.7 MB.

### 1x — `1x/plates/`

| Layer | Plate | Opacity | Position at 0:00 | Position at 2:00 |
| --- | --- | --- | --- | --- |
| 1 (bottom) | `layer1_plate_7090x1556.png` | 10% | 3349.0, 762.0 | 3529.0, 318.0 |
| 2 | `layer2_plate_7120x1630.png` | 16% | 3334.0, 799.0 | 3544.0, 281.0 |
| 3 | `layer3_plate_7165x1741.png` | 25% | 3311.5, 854.5 | 3566.5, 225.5 |
| 4 | `layer4_plate_7240x1926.png` | 42% | 3274.0, 947.0 | 3604.0, 133.0 |
| 5 | `layer5_plate_7315x2111.png` | 68% | 3236.5, 1039.5 | 3641.5, 40.5 |
| 6 (top) | `layer6_plate_7360x2222.png` | 100% | 3214.0, 1095.0 | 3664.0, −15.0 |

Tiles 180–450 px, 7090×1556 to 7360×2222 plates, 1.4 MB.

### 2x — `2x/plates/`

| Layer | Plate | Opacity | Position at 0:00 | Position at 2:00 |
| --- | --- | --- | --- | --- |
| 1 (bottom) | `layer1_plate_7255x1963.png` | 10% | 3266.5, 965.5 | 3611.5, 114.5 |
| 2 | `layer2_plate_7345x2185.png` | 16% | 3221.5, 1076.5 | 3656.5, 3.5 |
| 3 | `layer3_plate_7405x2333.png` | 25% | 3191.5, 1150.5 | 3686.5, −70.5 |
| 4 | `layer4_plate_7570x2740.png` | 42% | 3109.0, 1354.0 | 3769.0, −274.0 |
| 5 | `layer5_plate_7705x3073.png` | 68% | 3041.5, 1520.5 | 3836.5, −440.5 |
| 6 (top) | `layer6_plate_7810x3332.png` | 100% | 2989.0, 1650.0 | 3889.0, −570.0 |

Tiles 345–900 px, 7255×1963 to 7810×3332 plates, 3.0 MB.

### 3x — `3x/plates/`

| Layer | Plate | Opacity | Position at 0:00 | Position at 2:00 |
| --- | --- | --- | --- | --- |
| 1 (bottom) | `layer1_plate_7435x2407.png` | 10% | 3176.5, 1187.5 | 3701.5, −107.5 |
| 2 | `layer2_plate_7555x2703.png` | 16% | 3116.5, 1335.5 | 3761.5, −255.5 |
| 3 | `layer3_plate_7660x2962.png` | 25% | 3064.0, 1465.0 | 3814.0, −385.0 |
| 4 | `layer4_plate_7900x3554.png` | 42% | 2944.0, 1761.0 | 3934.0, −681.0 |
| 5 | `layer5_plate_8110x4072.png` | 68% | 2839.0, 2020.0 | 4039.0, −940.0 |
| 6 (top) | `layer6_plate_8260x4442.png` | 100% | 2764.0, 2205.0 | 4114.0, −1125.0 |

Tiles 525–1350 px, 7435×2407 to 8260×4442 plates, 5.1 MB.

## How to build

Exactly as `../ambient-layer/README.md` describes — six plates, stacked in order, linear
position keyframes, opacities as tabled — with two changes: the sequence is **2:00** long,
and the second keyframe sits at **2:00** instead of 6:00.

Positions are Premiere / After Effects **Position** values: where the clip's anchor point
lands, and the anchor defaults to the clip's **centre**. `layers.json` in each folder
carries the top-left equivalents alongside them.

All the Premiere specifics still apply: Scale 100%, both Temporal and Spatial Interpolation
set to Linear, still-image default duration, straight alpha.

## Verification

Each of the four was rendered at t=0 and t=120 and compared: **0 differing pixels** on
every channel across all 7,428,240, so all four loop exactly.

The 3x plates were checksummed against the six already delivered in `../ambient-layer/` —
all six byte-identical.

## Regenerating

```sh
node animation/tools/export-plates.js --speed 2 --loop 120 --out DIR
```

`--speed` is relative to the shipped field and `--loop` is the loop length in seconds; the
tile geometry follows from the two. The same switches work on the render surface as
`?speed=2&loop=120`, so a variant can be previewed before its plates are cut.
