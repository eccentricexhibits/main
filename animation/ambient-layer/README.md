# Ambient arrow field — the whole 6-minute loop, full resolution, in 7 MB

The drifting arrows on their own: no ground gradient, no grain, no logo event. Full
resolution, transparent, and **frame-rate independent** — it plays at 120 fps, 60 fps or
anything else because it is not a frame sequence.

## Why this is not a PNG sequence

A 360-second loop at 120 fps is **43,200 frames**. Measured at full size with alpha, this
layer costs **1.94 MB a frame and captures at 0.67 fps**, so the sequence you asked for
would be **~84 GB and about 18 hours of render**. The container has 26 GB of disk, and
GitHub takes 100 MB a file. It cannot be produced or delivered from here in any format —
the frame count is the problem, so dropping to 60 fps or to a lossless movie does not
rescue it.

What makes that acceptable rather than a compromise: **this layer does not need frames.**
Each of the six layers is a single seamlessly repeating tile, `background-repeat`, sliding
in a straight line at constant speed. There is no per-arrow animation, no fade, no
twinkle — one linear `translate3d` per layer over the full 360 s, and nothing else. Six
static images and six position keyframes reproduce the entire six minutes exactly, at any
frame rate you like.

That also settles the fast/slow question for free. The venue's slow version is not a
re-render — it is the same six keyframes with a longer duration.

## The build

Stack the six plates in order, layer 1 at the back, and give each a **linear** position
keyframe from its start to its end over the loop length. That is the whole animation.

### Premiere Pro / After Effects — position by centre

Both applications position a clip by its **anchor point**, which defaults to the **centre**
of the clip, not its top-left corner. Use these numbers directly in Motion > Position:

| Layer | Plate | Opacity | Position at 0:00 | Position at 6:00 |
| --- | --- | --- | --- | --- |
| 1 (bottom) | `layer1_plate_7435x2407.png` | 10% | 3176.5, 1187.5 | 3701.5, −107.5 |
| 2 | `layer2_plate_7555x2703.png` | 16% | 3116.5, 1335.5 | 3761.5, −255.5 |
| 3 | `layer3_plate_7660x2962.png` | 25% | 3064.0, 1465.0 | 3814.0, −385.0 |
| 4 | `layer4_plate_7900x3554.png` | 42% | 2944.0, 1761.0 | 3934.0, −681.0 |
| 5 | `layer5_plate_8110x4072.png` | 68% | 2839.0, 2020.0 | 4039.0, −940.0 |
| 6 (top) | `layer6_plate_8260x4442.png` | 100% | 2764.0, 2205.0 | 4114.0, −1125.0 |

If the arrows end up crowded into the left of the frame with black to the right, this is
why: top-left coordinates were entered where centre coordinates were wanted, which shifts
each plate left by half its own width. The symptom is distinctive — the field stops at
about 46% across.

### The same thing as top-left coordinates

For any tool that positions by the top-left corner (CSS, canvas, most compositing code):

| Layer | Top-left at 0:00 | Top-left at 6:00 | Plate | Tile | Arrow height |
| --- | --- | --- | --- | --- | --- |
| 1 | −541, −16 | −16, −1311 | 7435 × 2407 | 525 × 1295 | 48 px |
| 2 | −661, −16 | −16, −1607 | 7555 × 2703 | 645 × 1591 | 68 px |
| 3 | −766, −16 | −16, −1866 | 7660 × 2962 | 750 × 1850 | 92 px |
| 4 | −1006, −16 | −16, −2458 | 7900 × 3554 | 990 × 2442 | 130 px |
| 5 | −1216, −16 | −16, −2976 | 8110 × 4072 | 1200 × 2960 | 175 px |
| 6 | −1366, −16 | −16, −3346 | 8260 × 4442 | 1350 × 3330 | 235 px |

Centre = top-left + half the plate size. Either way each layer travels exactly one tile —
right by `tileW`, up by `tileH` — which is what makes the loop seamless.

### Premiere specifics

- **Scale must be 100%.** The plates are larger than the sequence, so if Preferences >
  Media > Default Media Scaling is set to *Scale to Frame Size* or *Set to Frame Size*,
  Premiere shrinks them to fit and the arrows come out miniature. Set it to *None* before
  importing, or reset Scale to 100 on each clip afterwards.
- **Both interpolations must be linear.** Right-click each keyframe: *Temporal
  Interpolation > Linear* and *Spatial Interpolation > Linear*. Premiere's spatial default
  is Auto Bézier, which can ease the motion — and any easing breaks the loop, because
  velocity has to match across the seam as well as position.
- **Still-image duration.** The default is 5 seconds. Set Preferences > Timeline > Still
  Image Default Duration to 6:00 before importing, or stretch each clip afterwards.
- **The 6:00 keyframe sits one frame past the last frame**, which is correct. At 120 fps a
  360-second sequence runs frames 0–43199, and 00:06:00:00 is frame 43200. Put the keyframe
  there and export up to but not including it. If Premiere will not place a keyframe past
  the clip end, extend the clips a few frames beyond 6:00 and set the export out-point at
  6:00.
- **Alpha.** Right-click > Modify > Interpret Footage > Alpha Channel: *Use Alpha Channel*,
  with *Ignore Alpha* off and premultiply off. The plates are straight alpha.

### Checklist

- Sequence 6878 × 1080, 6:00 long, at whatever frame rate you are working in.
- Six plates, Scale 100%, no smoothing.
- Linear position keyframes at 0:00 and 6:00, values as tabled.
- Layer opacities as tabled.
- Frame 0 and frame 6:00 are identical, so the last frame before the wrap is 6:00 minus one
  frame.

## The fade under the logo event

The field does not simply run behind the logo formation — in the approved animation it
clears out of the way and comes back. Put a single opacity animation on the group holding
all six plates, all segments linear:

| Time | Opacity |
| --- | --- |
| 0:00 → 4:00.000 | 100% |
| 4:03.850 | 0% |
| 4:26.700 | 0% |
| 4:32.700 | 100% |
| → 6:00 | 100% |

Measured off the built animation rather than read off the config. `../ASSEMBLY.md` has the
whole stack and where this sits in it.

## Speed variants

Change nothing but the comp duration and where the second keyframe sits:

- **Current speed** — second keyframe at 6:00.
- **Half speed (slow backup)** — 12:00 comp, second keyframe at 12:00. Still seamless,
  still full resolution, no re-render.
- **Any other speed** — move the keyframe. The loop stays seamless at every duration
  because both keyframes sit on lattice positions.

This is the honest way to get the fast and slow versions the venue wants: one build,
one number.

## `tiles/`

The same six layers as single tiles rather than pre-tiled plates — 2 MB total instead of
5 MB. Use these if you would rather tile in the editor (After Effects' Motion Tile, or a
repeating fill) than move a large image. The plates are simpler and are what the table
above describes; the tiles are here because they are the actual source artwork and some
pipelines prefer them.

Tile sizes are in the filenames. Each tile is `tileW × tileH` where `tileH = tileW × 37/15`
— that ratio is the whole trick behind the seamless loop. `(tileW, −tileH)` is
simultaneously the travel direction and a vector of the tiling lattice, so after one tile
of travel the field lands exactly on itself.

`layers.json` carries all of it in machine-readable form.

## Verification

- **The loop is pixel-exact.** Rendered at t=0 and t=360 in this exact mode — ambient
  only, transparent — the two frames differ by **0 on every channel across all 7,428,240
  pixels**.
- **The plates reconstruct the rendered animation.** Compositing them per the table and
  comparing against browser-rendered full-resolution frames at t = 0, 72, 137.5, 240, 300,
  359.5 and 360: mean visible error **0.2 / 255**. Where offsets land on whole pixels the
  match is essentially exact; the residual is confined to arrow edges at fractional
  offsets and is resampling filter difference — my check used bilinear, Chromium uses its
  own — not a difference in the artwork. Your editor applies its own filter at fractional
  positions exactly as the browser does.
- Plates carry a real alpha channel, unpremultiplied.

## Regenerating

The ambient field with no logo event is `--event 0`:

```sh
node animation/export.js --fps 60 --from 0 --to 360 --scale 1 --alpha 0 --event 0 --seq DIR
```

Be aware of what that costs — see the top of this file. `--event 0` has to skip the event
at the mount rather than hide it afterwards: mounting the event also installs the
keyframes that fade this whole field to nothing for the 33 seconds the event owns, which
would otherwise punch a hole in an ambient-only export.

The plates and tiles themselves come from the layer geometry in `arrow-field.js`
(`CONFIG.layers`, `overscan: 16`); plate size is `6878 + tileW + 32` by `1080 + tileH + 32`,
which is exactly the element the engine builds.

## If you do want frames

A short span at full resolution is affordable — roughly 4 seconds of 120 fps fits in a
1 GB delivery. Say the word and name the span. The full loop is not deliverable as frames
from here at any resolution or frame rate.
