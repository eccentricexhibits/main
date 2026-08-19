# Assembling the show from its layers

You are building this layer by layer rather than taking one flat render, so this is the
spec for how the pieces sit together: what each layer is, where it comes from, and — the
part that is easy to miss — how they interact. Two of the layers are not independent, and
getting that wrong is the difference between the assembly matching the approved animation
and not.

Comp: **6878 × 1080**, **6:00** (360 s) long, looping. Frame rate is yours to pick; see
the note at the end.

## The stack, back to front

| # | Layer | Source | Runs |
| --- | --- | --- | --- |
| 1 | Ground gradient | see below — flat artwork, no motion | whole loop |
| 2 | Ambient arrow field | `ambient-layer/` — six plates, keyframed | whole loop, **fades under the event** |
| 3 | Logo formation | `logo-layer/` — PNG sequence | 3:59 → 4:33 |
| 4 | Speaker cards | not yet exported | 4:17.5 → 4:26.7 |

## 1 — Ground gradient

A vertical linear gradient, top to bottom, static for the whole loop:

- top `#13071A`
- bottom `#3B1056`

Make this in the edit rather than importing it — a 6878 × 1080 gradient is a few
keystrokes and stays clean, where an 8-bit PNG of it will band on a screen this size.

**Add grain over it at about 3%.** That is not decoration; it dithers the ramp. A gradient
this wide and this dark bands visibly on large hardware, and the grain has to be applied
*after* the gradient is at its final values — which is exactly why the transparent exports
have no grain baked in. Any fine monochrome noise at low opacity will do.

## 2 — Ambient arrow field

Six plates from `ambient-layer/plates/`, stacked in order, each with a **linear** position
keyframe at 0:00 and 6:00:

| Layer | Plate | Opacity | Position at 0:00 | Position at 6:00 |
| --- | --- | --- | --- | --- |
| 2a (back) | `layer1_plate_7435x2407.png` | 10% | −541, −16 | −16, −1311 |
| 2b | `layer2_plate_7555x2703.png` | 16% | −661, −16 | −16, −1607 |
| 2c | `layer3_plate_7660x2962.png` | 25% | −766, −16 | −16, −1866 |
| 2d | `layer4_plate_7900x3554.png` | 42% | −1006, −16 | −16, −2458 |
| 2e | `layer5_plate_8110x4072.png` | 68% | −1216, −16 | −16, −2976 |
| 2f (front) | `layer6_plate_8260x4442.png` | 100% | −1366, −16 | −16, −3346 |

Positions are the plate's **top-left corner** in the comp, +y downward. No scaling, no
easing — easing breaks the loop, because velocity has to match across the seam as well as
position. Full detail and the verification are in `ambient-layer/README.md`.

### The part that is easy to miss

**The ambient field fades out under the logo event.** In the approved animation it does not
sit behind the logo — it clears out of the way and comes back. Put this on a group holding
all six plates, as a single opacity animation, all segments **linear**:

| Time | Opacity |
| --- | --- |
| 0:00 → 4:00.000 | 100% |
| 4:03.850 | 0% |
| 4:26.700 | 0% |
| 4:32.700 | 100% |
| → 6:00 | 100% |

In seconds, if that is easier to key: 100% at 240.000, 0% at 243.850, 0% at 266.700, 100%
at 272.700. Measured off the built animation, not read off the config.

If you skip this, the arrow field keeps drifting behind the logo formation and the whole
event reads as cluttered — it is the single biggest difference between an assembly that
matches and one that does not.

## 3 — Logo formation

The PNG sequence in `logo-layer/`, imported at **60 fps**. Frame 0 sits at **t = 239.000 s
(3:59:00)** in the comp, and the sequence runs to 273.000 s. The first 60 frames are
deliberately empty so you can see the layer land in the right place.

Straight (unpremultiplied) alpha, normal blend, no scaling.

Beats, if you need to trim or cut around them:

| Beat | Time | Frame in sequence |
| --- | --- | --- |
| Sweep begins | 240.000 | 60 |
| Sweep ends | 247.000 | 480 |
| Gather ends | 251.000 | 720 |
| Logo revealed | 253.500 | 870 |
| Logo resolved | 255.500 | 990 |
| Release begins | 266.700 | 1662 |
| Fully faded | 272.700 | 2022 |

## 4 — Speaker cards

Not yet exported as a layer. They run 4:17.5 → 4:26.7 (260.7 → 266.7 s), on the north and
south wall panels only. Ask and I will export them the same way — full size, transparent,
on the same clock.

## Frame rate, and the fast/slow versions

Layers 1 and 2 are frame-rate independent: a gradient and six linear position keyframes
render at whatever rate the comp is set to. Layer 3 is a 60 fps sequence, so in a 120 fps
comp it holds each frame for two — which is correct, not a defect. The formation was
approved at that speed and nothing in it moves fast enough to want more.

For the venue's slow backup, the honest build is **not** a re-render and **not** a
frame-rate trick:

- **Current speed** — 6:00 comp, ambient second keyframe at 6:00.
- **Half speed** — 12:00 comp, ambient second keyframe at 12:00. Still seamless, still
  full resolution. Move the event layers to wherever you want them on the longer timeline.

The loop stays seamless at any duration because both ambient keyframes sit on lattice
positions. That is a property of the tile geometry, not of the frame rate.

## Checking the assembly

The loop is seamless by construction, so the test is simple: the last frame of the comp
and the first frame should be identical. For the ambient field alone this was verified to
be exact — 0 difference on every channel across all 7,428,240 pixels. If your build shows
a jump at the wrap, the usual cause is easing on the ambient keyframes, or a comp duration
that is not exactly 360 s.
