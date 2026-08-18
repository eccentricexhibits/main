# Handoff — rebuilding the diagonal arrow loop from scratch

Everything a fresh session needs to reproduce this piece without re-deriving it. The
short version: the maths is all in `arrow-field.js`, but the *reasons* are here, and
several of them are non-obvious enough that a rebuild would otherwise get them wrong.

---

## 1. The brief, as given

> A 6878 × 1080 pixel animation of our official arrow travelling diagonally upwards
> (slope +2.467; angle 67.93° above the horizontal). Many arrows in a tiling pattern,
> with different opacities, overlapping each other on different layers. The arrows
> feature a gradient transition which switches colours along the same slope as the
> arrow's movement direction — the bottom left part of the arrow `#8A25C9`, the upper
> right portion `#48C0D9`. The brightest arrow fully opaque. The arrows must not move
> too quickly; this is for a large scale installation. Seamlessly looping. Keep it as a
> web mock-up until final approval to export as a video file.
>
> Background: a top-to-bottom gradient — nearly-black purple at the top, dark purple at
> the bottom. Add a subtle glow to the arrows, and some very subtle, tasteful light
> trails.

Revision after the first review: **duration 3 min → 6 min** (halving every speed), the
arrows' lower-left gradient stop **`#B659F0` → `#8A25C9`**, the flat `#8A25C9` ground
replaced by the vertical gradient above, and the glow and trails added.

Second revision — the logo transition:

> Add a flashy transition, to the venue's specifications (official template supplied).
> Arrows move horizontally across the north/south cube and the north/south wall to the
> centre portion. These move separately and do not cross vertically until they meet the
> centre. The many arrows then transform into the Vector logo in the centre, positioned
> on the Domino screen, filling about 70% of that area — tiny arrows forming the shape of
> the Vector arrow, most white and a few magenta, since there is less magenta surface
> area in the logo than white. Afterwards the proper Vector logo fades in over top.

Reference material supplied: `Arrow_Example.mp4` (an earlier version of the same piece,
1300 × 204 — see §3), `Vector Official - Arrow Regular.svg`,
`DX_TradingFloor_Immersive_Template-scaled_fullSize.png` (the venue template),
`Canada_Arrow.mp4` (a dotted-shape morph showing the intended particle effect), and the
bilingual horizontal lockup as an Illustrator EPS.

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
| Background | modal pixel colour | `#810DC2` (the reference predates both the flat `#8A25C9` and the current gradient) |
| Travel | block-match frames 10 s apart | (11, −27) px → slope 2.4545, **15.4 px/s** at full scale |
| Ink coverage | fraction of pixels differing from bg at thresholds 12/25/40/60 | **0.145 / 0.119 / 0.102 / 0.075** |
| Tone split | luminance of non-bg pixels vs bg | **27% of arrow pixels are darker than the ground** |
| Arrow sizes | visual, on a 2× crop | ~60 px to ~300 px tall at full scale |

Those four coverage numbers were the density target while the ground was flat purple,
and they are far more reliable than counting arrows by eye. They are **no longer directly
comparable**: the ground is now a dark gradient, so the same arrows register far more
contrast, and glow and trails add a lot of faint ink. Coverage is now measured against
`plate.png` — a render of the background and grain with no arrows — rather than a flat
colour constant.

The 27% dark-pixel figure stopped being a problem with the dark ground: low-opacity
arrows over a near-black top now read as dark silhouettes on their own.

---

## 3b. The venue, and the logo artwork

The venue template is itself exactly **6878 × 1080** — the canvas was already right. Panel
boundaries in `venue.js` are the template's rule centres, detected by thresholding the
image and finding columns that are mostly white:

    seams  0, 2241, 2503, 2598, 4278, 4373, 4636, 6878
    cube band starts at y = 674 and is 406 tall

The labelled "Above cube 2239 × 684" is ten rows taller than 1080 − 406, so upper-band
artwork carries ten rows of bleed behind the cube's top edge.

**The EPS parses directly.** It is an AI11 EPS whose page content is plain PostScript
using Illustrator's short operators — `mo`/`li`/`cv`/`cp` for paths, `cmyk` for colour,
`f` to fill. `tools/eps-to-svg.py` walks those tokens and rebuilds the artwork exactly.
No Ghostscript in this container, and none needed. Two things to know:

- Illustrator emits `1 -1 scale 0 -H translate` at the top of the page, which puts the
  path coordinates into a y-down space with the origin top-left — already SVG's
  convention, so the numbers transfer unchanged.
- The first path is the white "V", the second the magenta arrow, and the rest is the
  wordmark. That z-order is what lets the converter split `#mark` from `#wordmark`.

That split also settles a question the brief left open. The mark is **white plus
magenta** — which is exactly the "most of them white, a few magenta" the client
described, and confirms the particles form the mark rather than the whole lockup. The
sampled grid comes out about 27% magenta.

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
t = 360 s is *the same image* as t = 0 s — no crossfade, nothing to hide.

**The constraint that shapes the whole design:** the smallest lattice vector along the
travel axis is `(TW, −TH)`, with length `|(TW, −TH)| = 2.6617 × TW`. Nothing smaller
exists — you cannot use `(TW/2, −TH/2)`, it is not a lattice vector. So:

```
loop distance = 2.6617 × TW          speed = 2.6617 × TW / duration
```

**Tile width and duration together set a layer's speed**, and loop distance is fixed by
the tile alone. Two consequences:

- "Slow it down by 50%" is a one-line change. Doubling the duration to 360 s halves every
  speed and leaves the pattern, the tiles and the loop distances untouched.
- At a *fixed* duration, a slow layer is forced to have a narrow tile, which means less
  unique pattern before it repeats. That tension drives every number in the layer table:
  slow layers get denser small arrows (repetition reads as texture), fast layers get
  bigger tiles and bigger arrows.

The escape hatch: the six tile widths are mutually non-commensurate, so although each
layer repeats, the **composite** has no repeat period the eye can find across 6878 px.

Sub-constraints:

- `TW` must be a multiple of 15 so `TH = TW / 15 × 37` is a whole number. Fractional
  tile sizes produce visible seams in a repeated background.
- Element geometry, so the layer still covers the stage at both ends of its travel:
  `left = −TW − M`, `top = −M`, `width = 6878 + TW + 2M`, `height = 1080 + TH + 2M`,
  with `M = 16`. Getting this wrong shows as a bare ground-coloured wedge sliding in from
  an edge.

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

### Glow and trails

Both live inside the reused `<g id="s">`, declared in the **arrow's own coordinates**, so
each `<use>`'s scale carries the blur along and a 48 px arrow gets proportionally the same
halo as a 235 px one. Structure, back to front: trail path → blurred copy of the arrow at
`glow.opacity` → sharp arrow.

The trail is a tapered quad running back down the travel axis from the shaft's end cap
`(67.58, 484.26)`–`(113.86, 600)`, so it continues the line of the arrow instead of
crossing it. It fades to zero alpha at the far end via a three-stop gradient.

**The trap:** the trail reaches far outside the arrow's bounding box, and blur bleeds
past both. Tile culling and edge duplication must work off `spriteBox()` — the union of
arrow, trail and 3σ of blur — not the arrow's bbox, or glow gets clipped at tile seams.

Trail strength needs restraint. The first pass at `opacity 0.42, length 1.15` read as
prominent purple streaks and made the field look like rain; `0.20 / 0.90` is the
"very subtle" the client asked for.

### Background grain

The ground gradient spans only ~60 values of blue across 1080 px — about one step every
18 rows, which is exactly where 8-bit banding shows on a large LED wall. A static
`feTurbulence` tile (`stitchTiles="stitch"`, desaturated, alpha forced to 1) sits above
the background and below the arrows at 3% with `mix-blend-mode: overlay`, giving roughly
±0.5 of a value — enough to dissolve the steps. Measured: no row-to-row step ≥ 0.9
anywhere in the ramp. `dither: 0` removes it.

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
| 1 | 525 × 1295 | 48 px | 0.10 | 10 | 109 | 3.9 px/s | 1,397 px |
| 2 | 645 × 1591 | 68 px | 0.16 | 12 | 87 | 4.8 px/s | 1,717 px |
| 3 | 750 × 1850 | 92 px | 0.25 | 12 | 64 | 5.5 px/s | 1,996 px |
| 4 | 990 × 2442 | 130 px | 0.42 | 14 | 43 | 7.3 px/s | 2,635 px |
| 5 | 1200 × 2960 | 175 px | 0.68 | 14 | 29 | 8.9 px/s | 3,194 px |
| 6 | 1350 × 3330 | 235 px | 1.00 | 12 | 20 | 10.0 px/s | 3,593 px |

~352 arrows on screen. Layer 6 is fully opaque, satisfying "the brightest arrow should be
fully opaque". Speeds are half the reference clip's 15.4 px/s and below, as asked.

To predict the ink a config will produce before rendering it:

```
coverage ≈ Σ (onScreen · 0.3413 · 0.70497 · h²) · E[s²] / (6878 · 1080)
```

with `E[s²] = 1.0857` for the ×[0.70, 1.35] size jitter. Accurate to within about 10%.

---

## 8. Verifying a rebuild

```sh
node animation/build.js
VERIFY_SCALE=1 node animation/verify.js 0 60 360
python3 animation/analyze.py
```

**Rebuild before verifying.** `verify.js` loads the *built* HTML, so editing
`arrow-field.js` and re-running verify without `build.js` silently measures the old
version. This produced a baffling round of "coverage 0.017 / 0.401" numbers once.

Expected:

- `travel vector is exactly 15:37 (slope 2.4667, 67.93 deg) on every layer`
- `loop seam t360 vs t=0: max channel diff 0` — **exactly zero**, across all 7,428,240 px
- coverage around 0.24 / 0.19 / 0.16 / 0.13 against the bare plate

**Check the seam at `VERIFY_SCALE=1` only.** A scaled screenshot lands layers on half
pixels and reports anti-aliasing noise as a mismatch — an isolated layer at 0.25 scale
showed a "max diff 117" that was entirely an artefact of the downscale.

Independent angle check on one layer (phase correlation fails here — a periodic field has
many equal correlation peaks, so use direct block matching over a short interval):

```sh
VERIFY_SCALE=1 node animation/verify.js --layer 6 0 5
```

At the six-minute duration layer 6 moves (37.5, −92.5) px per 10 s. Phase correlation is
useless here — a periodic field gives many equal peaks — so use direct block matching over
a short interval.

### The transition

Timeline, particle behaviour and the two non-obvious decisions are documented in
`README.md`. The parts that would be easy to get wrong on a rebuild:

- **The sweep must be a conveyor.** Arrows laid out only *inside* their band all reach
  the centre at once and the far ends of the wall are bare within a few seconds. Lay them
  over a run ~1.9× the band width, at close to a single speed, and fade each one in as it
  crosses the outer edge.
- **Entry is from the top and bottom edges**, not the sides: drop in, round a corner
  into a horizontal lane, cruise, swoop. `positionAt(p, d)` evaluates the whole
  three-part path in closed form from distance travelled, and the heading is a finite
  difference along it — deriving a tangent per leg by hand is where this gets fiddly and
  starts to snag at the joins.
- **Lanes span the full height** and each arrow enters from whichever edge is nearer.
  Splitting lanes into a top group and a bottom group leaves a bare stripe across the
  middle of the wall.
- **Give every arrow its own numbers.** Corner radius, swoop distance, cruise length,
  lane wander, speed multiplier and the exponent shaping its acceleration are all drawn
  per arrow. With one shared set the swarm reads as stiff no matter how good the path
  shape is; the cruise also needs a shallow sine wander, because ruler-straight travel is
  what makes a flock look mechanical.
- **Cruise length is capped by the wall, not by a constant.** `cruise` is clamped to
  `target.x − 60` (or the mirror on the north side) so entries spread right out to both
  edges. A fixed maximum bunches every entry into the middle third.
- **Particles start at ambient scale and shrink.** The first pass ran them at 7–15 px
  throughout; against 48–235 px ambient arrows they read as dust and the handoff looked
  like a cross-fade to a different piece. Starting at 34–120 px and shrinking to ~10 px
  during the gather makes the field look like it turns and condenses.
- **Do not use a gate at all.** The first version funnelled every arrow to a fixed x on
  each side before flying it to the mark, which stacked them into two vertical columns
  down the wall. Jittering that x by ±150 px was not enough. What works: no gate, and an
  arrow leaves its lane when it comes within its *own* randomised distance (420–860 px)
  of its destination — vertical position keyed to remaining distance, not to elapsed
  time. Nothing then shares a turn-in point.
- **Rotation is temporary.** Arrows turn to fly nose-first along their path — which also
  fixes north-side arrows appearing to travel backwards — and straighten back to brand
  orientation over the last quarter of the swoop, so the mark is always assembled from
  upright arrows. Tangent angle is closed-form: with y keyed to remaining distance by a
  smoothstep, dy/dx = rise · 6s(1−s) / swoop.
- **Nothing may integrate.** Every particle's position is a closed-form function of t.
  That is what keeps `seek()` exact and the export frame-accurate — and it is why the
  canvas can be cleared and skipped entirely outside the event, leaving t = 0 and t = 360
  pixel-identical.

### The speaker cards

- **The card covers the whole wall panel** and centres its content. The wipe is then just
  the arrow's progress across the panel, so the reveal edge tracks the arrow for free —
  no working out where the arrow meets the artwork. It also guarantees the portrait and
  type stay off the cube band and the draped returns.
- **Minifying SVG by stripping newlines welds attributes together.** `build.js` used
  `.replace(/\n\s*/g, '')`, which turned `font-family="..."\n text-anchor="..."` into
  `font-family="..."text-anchor="..."` — the data URI then failed to decode and the image
  reported `complete: true, naturalWidth: 0`. Collapse to a single space, not to nothing.
- **The wipe arrow is the client's own horizontal artwork**, not the brand arrow rotated.
  It is stored with `fill="currentColor"` so `TRANSITION.magenta` stays the single source
  of the colour, and its aspect is read from its own viewBox at mount.
- **The render page needs the font too.** The cards are set in Karbon; inlining it only in
  the review page would export type in a fallback face.

### Performance

The review page measures ~13 fps ambient and ~19 fps during the transition in this
container, which has no GPU and rasterises in software. Earlier builds measured ~5 fps;
wrapping the drifting layers in `.af-ambient` for the fade promoted them to a composited
layer, which helped. Either way the figure tracks the environment, not the design — it
was identical with the glow and trails switched off and identical on the build before
them. Real-time smoothness needs
checking on the actual playback machine; the exported video sidesteps it entirely, since
export seeks each frame rather than capturing in real time.

### Exporting the piece as separate layers

The client assembles the show layer by layer in an edit, so the surface can be split and
each part exported on its own clock. Two switches do it, on the render surface as query
parameters and on `export.js` as flags: `ambient=0` drops the six drifting tile layers and
the grain but keeps the logo event, and `speakers=0` drops the speaker cards. Combined
with `alpha=0` — the ground at zero opacity, i.e. no ground at all — that yields the logo
formation alone over transparency.

`bare=1` looks like it should do the same job and does not: it empties `layers` too, but
the transition only mounts when there are layers, so `bare=1` takes the event with it.
`ambient=0` sets `keepTransition`, which is the flag the mount condition in
`arrow-field.js` also accepts.

Because every layer is seeked from the same master clock, the parts drop onto a timeline
in sync with no matching to do — a frame exported at t=252 is the same instant in every
layer. Export the formation from 239 rather than 240 so the layer opens on a second of
empty transparent frames, which makes the start position visible in the edit.

Isolated, the formation is far cheaper than the whole surface: ~1.7 fps capture and
~170 KB a frame through most of it, against ~0.5 fps and ~2.7 MB with everything on. The
sweep, 240–247 s, is the costly stretch — every particle on screen trailing — peaking near
1.9 MB a frame.

---

## 9. Open decisions, not yet answered by the client

1. **Frame rate and codec for export.** 360 s divides evenly at 24, 25, 30, 60 — 10,800
   frames at 30. Playback hardware determines ProRes 422 HQ vs HAP vs H.264.
   `export-frames.js` is written and tested but deliberately not run.
2. **Grain.** Added unprompted, at 3%, because the ground gradient is a banding risk on
   large hardware. `dither: 0` removes it if the client would rather not have it.
3. **"Speed up the overall animation" was read as the transition**, not the six-minute
   loop — the ambient speed was set deliberately two rounds earlier and the rest of that
   round's notes were all about the event. The transition went 45 s → 26.5 s. Flagged to
   the client.
4. **How the reveal resolves.** The brief asks for the logo at 70% of the Domino screen
   *and* for arrows to form the mark; at 70% width the mark inside the lockup is only
   ~219 px, too small to read as built from arrows. The default `settle` forms the mark
   large and eases it into the lockup. `TRANSITION.finish` switches to `inPlace` (literal
   reading) or `markOnly`. Put to the client, unanswered at time of writing.
5. **Arrow orientation during the sweep.** Arrows now rotate to fly nose-first, which the
   client sanctioned when asking for a more dynamic swoop. They are upright whenever they
   matter — at fade-in, and once landed in the mark.

---

## 10. Rebuilding in a fresh Claude Code session

If the files survive, it is just `node animation/build.js` — the engine is the source of
truth and the two HTML deliverables are generated from it.

If you are starting over from nothing, this prompt carries the whole design:

> Build a 6878 × 1080 seamlessly looping 6-minute web animation: a tiled field of the
> arrow in `Vector Official - Arrow Regular.svg` drifting up-right on a ground that is a
> vertical gradient from `#13071A` at the top to `#3B1056` at the bottom.
>
> Do not rotate the arrow — its own shaft edge, `(208.02,137.79)`→`(68.91,480.94)`, runs
> at slope 2.4667 (= 37/15, 67.93°), which is the travel direction.
>
> Each arrow is filled with a linear gradient `#8A25C9` → `#48C0D9` running along that
> same axis, defined in objectBoundingBox units with endpoints
> `x1=−0.26424 y1=0.92444 x2=0.07551 y2=−0.26422` (derived so the bands stay
> perpendicular to travel after the non-uniform bbox stretch).
>
> Six parallax layers. Each is one div with a repeating SVG-data-URI background tile of
> `TW × TH` where `TH/TW = 37/15` and `TW` is a multiple of 15, animated
> `translate3d(0,0,0)` → `translate3d(TW, −TH, 0)` over 360 s linear infinite. That
> translation is a lattice vector of the tiling, so the loop is pixel-exact. Layer speed
> is forced to `2.6617 × TW / 360` px/s. Use `TW` = 525, 645, 750, 990, 1200, 1350 with
> arrow heights 48, 68, 92, 130, 175, 235 px, opacities 0.10, 0.16, 0.25, 0.42, 0.68,
> 1.00, and 10, 12, 12, 14, 14, 12 arrows per tile. Size the elements
> `6878 + TW + 32` × `1080 + TH + 32` at `left: −TW − 16, top: −16`.
>
> Place arrows by blue-noise sampling on the tile torus with a seeded PRNG, redraw any
> arrow that crosses a tile edge on the opposite side, and jitter per-arrow size ×[0.70,
> 1.35] and opacity ×[0.72, 1.00].
>
> The logo's magenta is `#EB088A` — the brand's sRGB value, not the EPS's CMYK
> conversion, which comes out as `#FF0FF1`.
>
> Give each arrow a soft halo (blurred copy of itself at 0.5 alpha, blur 0.055 × arrow
> height) and a light trail: a tapered quad running back down the travel axis from the
> shaft end cap `(67.58,484.26)`–`(113.86,600)`, 0.90 × arrow height long, tapering to
> 0.28, fading to zero alpha, at 0.20 alpha and blur 0.04. Declare both inside the reused
> group in the arrow's own coordinates so the use scale carries them. Cull and duplicate
> tiles against the union of arrow + trail + 3σ blur, not the arrow bbox.
>
> Lay a static seamless `feTurbulence` grain over the background at 3% with
> `mix-blend-mode: overlay` to dither the ground ramp against 8-bit banding.
>
> Verify the loop by screenshotting t=0 and t=360 at full 1:1 resolution and diffing — it
> must be exactly zero.
>
> Deliver as a self-contained web mock-up with scrub and a loop-point check; do not
> export video.
