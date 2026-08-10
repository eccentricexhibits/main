# Handoff — rebuilding the diagonal arrow loop from scratch

Everything a fresh session needs to reproduce this piece without re-deriving it. The
short version: the maths is all in `arrow-field.js`, but the *reasons* are here, and
several of them are non-obvious enough that a rebuild would otherwise get them wrong.

---

## 1. The brief, as given

> A 6878 × 1080 pixel animation of our official arrow travelling diagonally upwards
> (slope +2.467; angle 67.93° above the horizontal). Many arrows in a tiling pattern,
> with different opacities, overlapping each other on different layers. Background
> purple `#8A25C9`. The arrows feature a gradient transition which switches colours
> along the same slope as the arrow's movement direction — the bottom left part of the
> arrow `#B659F0`, the upper right portion `#48C0D9`. The brightest arrow fully opaque.
> The arrows must not move too quickly; this is for a large scale installation. Three
> minutes long, seamlessly looping. Keep it as a web mock-up until final approval to
> export as a video file.

Reference material supplied: `Arrow_Example.mp4` (an earlier version of the same piece,
1300 × 204 — see §3) and `Vector Official - Arrow Regular.svg`.

---

## 2. The single most important discovery

**The arrow does not get rotated.** Its own shaft already runs at the specified angle.

The polygon in `Vector Official - Arrow Regular.svg` has a shaft edge from
`(208.02, 137.79)` to `(68.91, 480.94)`:

```
Δ = (−139.11, +343.15)      slope = 343.15 / 139.11 = 2.46674
```

That is where the client's `2.467` came from. So the artwork's axis and the direction of
travel are the same line, and the field slides *along* the arrow rather than across it.
Any rebuild that applies a rotation transform is wrong.

`37 / 15 = 2.46667` is used throughout as the exact rational form — it matches the
measured slope to 5 decimal places and, crucially, lets tile dimensions stay whole
numbers (see §5).

Arrow geometry constants, all needed:

| | |
| --- | --- |
| viewBox | `0 0 422.98 600` |
| bbox | exactly x ∈ [0, 422.98], y ∈ [0, 600] — the extreme points touch all four edges |
| aspect (w/h) | 0.70497 |
| filled area | 86,605.4 units² → **fill fraction 0.3413** of the bbox |
| travel unit vector | `(0.375702, −0.926733)` (screen coords, y down) |

---

## 3. What was measured off the reference clip

The reference is 1300 × 204 — **exactly 1/5.29 of 6878 × 1080**, same aspect ratio. So it
is the same deliverable at reduced scale, and its numbers transfer directly.

| Measurement | Method | Result |
| --- | --- | --- |
| Background | modal pixel colour | `#810DC2` (note: *not* the `#8A25C9` now specified) |
| Travel | block-match frames 10 s apart | (11, −27) px → slope 2.4545, **15.4 px/s** at full scale |
| Ink coverage | fraction of pixels differing from bg at thresholds 12/25/40/60 | **0.145 / 0.119 / 0.102 / 0.075** |
| Tone split | luminance of non-bg pixels vs bg | **27% of arrow pixels are darker than the ground** |
| Arrow sizes | visual, on a 2× crop | ~60 px to ~300 px tall at full scale |

Those four coverage numbers are the density target — they are how this build was tuned,
and they are far more reliable than counting arrows by eye. Current build measures
**0.141 / 0.121 / 0.104 / 0.085**.

The 27% dark-pixel figure is the one thing the current build deliberately does *not*
reproduce: the specified gradient over a purple ground can only ever read lighter than
the ground. Flagged to the client as an open question (§9).

---

## 4. Environment gotchas

These cost real time to discover:

- **`apt-get install ffmpeg` fails** in this container (404s on universe packages).
  Use `pip install imageio-ffmpeg`, then
  `python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`.
- **Playwright's bundled ffmpeg cannot decode H.264** — it is compiled with almost
  everything disabled (VP8/webm only). It will not open the reference mp4.
- **Headless Chromium cannot decode H.264 either**, so playing the reference in a page
  and screenshotting it does not work.
- Playwright lives at `/opt/node22/lib/node_modules/playwright`; Chromium is at
  `/opt/pw-browsers`. Never run `playwright install`.
- No `PIL`, no `cv2`, no `scipy`. `numpy` is present. PNGs are decoded for analysis by
  piping through ffmpeg and reading width/height straight out of the PNG IHDR chunk —
  see `load()` in `analyze.py`.

---

## 5. How the seamless loop works, and the constraint it imposes

Each layer is **one element** carrying a repeating background tile of `TW × TH` px,
animated with `transform: translate3d()`. Fix `TH / TW = 37 / 15`. Then the vector
`(TW, −TH)` is simultaneously:

1. parallel to the travel direction, and
2. a lattice vector of the repeating tiling.

Translating a layer by `(TW, −TH)` therefore maps the pattern onto itself. The frame at
t = 180 s is *the same image* as t = 0 s — no crossfade, nothing to hide.

**The constraint that shapes the whole design:** the smallest lattice vector along the
travel axis is `(TW, −TH)`, with length `|(TW, −TH)| = 2.6617 × TW`. Nothing smaller
exists — you cannot use `(TW/2, −TH/2)`, it is not a lattice vector. So:

```
loop distance = 2.6617 × TW          speed = 2.6617 × TW / 180
```

**Tile width alone sets a layer's speed.** A slow layer is forced to have a narrow tile,
which means less unique pattern before it repeats. That tension drives every number in
the layer table: slow layers get denser small arrows (repetition reads as texture), fast
layers get bigger tiles and bigger arrows.

The escape hatch: the six tile widths are mutually non-commensurate, so although each
layer repeats, the **composite** has no repeat period the eye can find across 6878 px.

Sub-constraints:

- `TW` must be a multiple of 15 so `TH = TW / 15 × 37` is a whole number. Fractional
  tile sizes produce visible seams in a repeated background.
- Element geometry, so the layer still covers the stage at both ends of its travel:
  `left = −TW − M`, `top = −M`, `width = 6878 + TW + 2M`, `height = 1080 + TH + 2M`,
  with `M = 16`. Getting this wrong shows as a bare purple wedge sliding in from an edge.

### Tile contents

- Arrow positions come from **blue-noise sampling on the tile's torus** (dart throwing
  with wrap-around distance, radius relaxed on failure). A jittered grid was rejected —
  with only 2 columns per tile it reads as vertical banding.
- Any arrow whose bbox crosses a tile edge is **drawn again on the opposite side** (the
  3 × 3 neighbour loop in `buildTile`). Without this, arrows get clipped at seams.
- Per-arrow size jitter ×[0.70, 1.35] and opacity jitter ×[0.72, 1.00] on top of the
  layer values. The size jitter matters: it breaks up the "every arrow in this layer is
  identical" signature that makes tiling visible.
- Seeded PRNG (mulberry32, seed 20260810) so the field is byte-identical on every load
  and every export run.

---

## 6. The gradient maths

Per-arrow gradient, `#B659F0` at the lower-left end → `#48C0D9` at the upper-right end,
with the colour bands perpendicular to the travel axis.

It is defined in **objectBoundingBox units**, which works uniformly for every arrow
because all arrows share one bbox aspect and none are rotated. But oBB applies a
*non-uniform* stretch (422.98 × 600), so you cannot simply map user-space points into
oBB — the perpendicularity has to survive the stretch.

Solve for the gradient vector `g = (gx, gy)` in oBB units such that the user-space band
normal `(gx / 422.98, gy / 600)` is parallel to `(15, −37)`:

```
gy = gx · (600 / 422.98) · (−37 / 15) = −3.49879 · gx
```

Then pick the magnitude and origin so the gradient runs from the box corner furthest
down-axis to the one furthest up-axis. Result:

```
x1 = −0.26424   y1 =  0.92444
x2 =  0.07551   y2 = −0.26422
```

`gradientEndpoints()` in `arrow-field.js` derives these from `RISE`/`RUN` rather than
hard-coding them, so changing the angle keeps the gradient aligned.

---

## 7. The layer table

| Layer | Tile | Arrow h | Opacity | Per tile | On screen | Speed | Loop travel |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 525 × 1295 | 48 px | 0.10 | 10 | 109 | 7.8 px/s | 1,397 px |
| 2 | 645 × 1591 | 68 px | 0.16 | 12 | 87 | 9.5 px/s | 1,717 px |
| 3 | 750 × 1850 | 92 px | 0.25 | 12 | 64 | 11.1 px/s | 1,996 px |
| 4 | 990 × 2442 | 130 px | 0.42 | 14 | 43 | 14.6 px/s | 2,635 px |
| 5 | 1200 × 2960 | 175 px | 0.68 | 14 | 29 | 17.7 px/s | 3,194 px |
| 6 | 1350 × 3330 | 235 px | 1.00 | 12 | 20 | 20.0 px/s | 3,593 px |

~352 arrows on screen. Layer 6 is fully opaque, satisfying "the brightest arrow should be
fully opaque". Composite speed sits either side of the reference's 15.4 px/s.

To predict the ink a config will produce before rendering it:

```
coverage ≈ Σ (onScreen · 0.3413 · 0.70497 · h²) · E[s²] / (6878 · 1080)
```

with `E[s²] = 1.0857` for the ×[0.70, 1.35] size jitter. Accurate to within about 10%.

---

## 8. Verifying a rebuild

```sh
node animation/build.js
VERIFY_SCALE=1 node animation/verify.js 0 10 90 180
python3 animation/analyze.py
```

Expected:

- `travel vector is exactly 15:37 (slope 2.4667, 67.93 deg) on every layer`
- `loop seam t=180 vs t=0: max channel diff 0` — **exactly zero**, across all 7,428,240 px
- coverage within ~0.01 of 0.141 / 0.121 / 0.104 / 0.085

**Check the seam at `VERIFY_SCALE=1` only.** A scaled screenshot lands layers on half
pixels and reports anti-aliasing noise as a mismatch — an isolated layer at 0.25 scale
showed a "max diff 117" that was entirely an artefact of the downscale.

Independent angle check on one layer (phase correlation fails here — a periodic field has
many equal correlation peaks, so use direct block matching over a short interval):

```sh
VERIFY_SCALE=1 node animation/verify.js --layer 6 0 5
```

Layer 6 moves (38, −92) px in 5 s against a predicted (37.5, −92.5) — inside one-pixel
quantisation.

---

## 9. Open decisions, not yet answered by the client

1. **Frame rate and codec for export.** 180 s divides evenly at 24, 25, 30, 60. Playback
   hardware determines ProRes 422 HQ vs HAP vs H.264. `export-frames.js` is written and
   tested but deliberately not run.
2. **Dark arrows.** The reference gets 27% of its arrow pixels *darker* than the ground;
   the specified palette cannot do that at any opacity. Offered to add layers below the
   ground value if wanted.
3. The reference's ground was `#810DC2`; the brief specifies `#8A25C9`. Built to the
   brief.

---

## 10. Rebuilding in a fresh Claude Code session

If the files survive, it is just `node animation/build.js` — the engine is the source of
truth and the two HTML deliverables are generated from it.

If you are starting over from nothing, this prompt carries the whole design:

> Build a 6878 × 1080 seamlessly looping 3-minute web animation: a tiled field of the
> arrow in `Vector Official - Arrow Regular.svg` drifting up-right on a `#8A25C9` ground.
>
> Do not rotate the arrow — its own shaft edge, `(208.02,137.79)`→`(68.91,480.94)`, runs
> at slope 2.4667 (= 37/15, 67.93°), which is the travel direction.
>
> Each arrow is filled with a linear gradient `#B659F0` → `#48C0D9` running along that
> same axis, defined in objectBoundingBox units with endpoints
> `x1=−0.26424 y1=0.92444 x2=0.07551 y2=−0.26422` (derived so the bands stay
> perpendicular to travel after the non-uniform bbox stretch).
>
> Six parallax layers. Each is one div with a repeating SVG-data-URI background tile of
> `TW × TH` where `TH/TW = 37/15` and `TW` is a multiple of 15, animated
> `translate3d(0,0,0)` → `translate3d(TW, −TH, 0)` over 180 s linear infinite. That
> translation is a lattice vector of the tiling, so the loop is pixel-exact. Layer speed
> is forced to `2.6617 × TW / 180` px/s. Use `TW` = 525, 645, 750, 990, 1200, 1350 with
> arrow heights 48, 68, 92, 130, 175, 235 px, opacities 0.10, 0.16, 0.25, 0.42, 0.68,
> 1.00, and 10, 12, 12, 14, 14, 12 arrows per tile. Size the elements
> `6878 + TW + 32` × `1080 + TH + 32` at `left: −TW − 16, top: −16`.
>
> Place arrows by blue-noise sampling on the tile torus with a seeded PRNG, redraw any
> arrow that crosses a tile edge on the opposite side, and jitter per-arrow size ×[0.70,
> 1.35] and opacity ×[0.72, 1.00].
>
> Target ink coverage 0.145 / 0.119 / 0.102 / 0.075 at difference thresholds 12/25/40/60
> against the ground. Verify the loop by screenshotting t=0 and t=180 at full 1:1
> resolution and diffing — it must be exactly zero.
>
> Deliver as a self-contained web mock-up with scrub and a loop-point check; do not
> export video.
