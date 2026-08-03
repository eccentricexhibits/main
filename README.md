# Vector Institute — “Convergence”

A three-minute generative animation for the DX Trading Floor immersive room,
built from the official Vector brand assets.

**Canvas:** 6878 × 1080 · **Duration:** 180 s · **Loop:** seamless (verified
pixel-identical at the seam) · **Palette:** primary magenta → violet → cobalt
gradient.

---

## Preview it in a browser

Open **`dist/preview.html`** — it is fully self-contained, so it works straight
off disk with no server. Controls include a scrub track, a venue overlay
showing every projector region, a loop-seam test, and a preview resolution
selector.

To rebuild it after changing the scene:

```bash
npm install
node tools/build-preview.js
```

For live development with module reloading, serve `src/` instead:

```bash
npx http-server src -p 8099   # then open http://127.0.0.1:8099/preview.html
```

### Earlier versions

Every cut of the piece stays viewable, not just recoverable. `dist/` holds a
standalone preview per version, each with a banner so it cannot be mistaken for
the current one:

| File | Version |
| --- | --- |
| `dist/preview.html` | Current — funnelled left-to-right field, arrows on the 67.93° axis |
| `dist/preview-v2.html` | v2 — everything on the 67.93° axis, no funnel |
| `dist/preview-v1.html` | v1 — five-phase arc, horizontal flow, logo reveal |

To rebuild any earlier version from git:

```bash
tools/build-archive.sh <commit> <name> "<banner text>"
tools/build-archive.sh 84271cc v1 "Version 1 — phase arc, horizontal flow"
tools/build-archive.sh 061d85b v2 "Version 2 — all-diagonal flow, no funnel"
```

## Render the final file

```bash
node tools/render.js                      # 6878x1080, 30 fps, H.264 CRF 16
node tools/render.js --fps 60 --crf 14    # higher frame rate / quality
node tools/render.js --walls              # also cut one file per projector
node tools/render.js --duration 10        # short test render
```

Options: `--fps --crf --gop --duration --workers --out --walls`.

Frames are rendered at full resolution across worker processes, piped as raw
RGBA into per-segment ffmpeg encoders, then concatenated with a stream copy so
nothing is re-encoded. On four cores a full 180 s / 30 fps master takes about
26 minutes and lands at **554 MB** (24.6 Mbps).

### Colour conversion

`-colorspace bt709` only *labels* the stream — ffmpeg's automatic RGB→YUV
conversion still uses BT.601. Tagging alone therefore produces a file converted
with one matrix and played back with another: a systematic colour shift, worth
about 4.8 dB of error against the source, and most visible on exactly the
saturated magenta and cobalt this piece is built from.

The renderer converts explicitly instead:

```
scale=in_range=full:in_color_matrix=bt709:out_range=tv:out_color_matrix=bt709
```

plus `-color_range tv` so the tags match the data. Canvas gives full-range RGB;
video convention is limited-range YUV.

### Pixel format

Measured on 24 representative frames against the raw render, with the colour
conversion correct in both cases:

| Encode | PSNR | Size (3 min) |
| --- | --- | --- |
| yuv420p CRF 16 | 36.6 dB | ~520 MB |
| **yuv444p CRF 16** | **41.7 dB** | **~428 MB** |

Saturated, hard-edged brand colour on near-black is the worst case for 4:2:0,
and the encoder spends bits on the resulting residual — so 4:4:4 is both higher
quality *and* smaller here.

It is not the default only because H.264 High 4:4:4 Predictive decodes in
software (VLC, Resolume, ffmpeg-based media servers) but not on every hardware
decoder. Choose by what the venue plays back on:

```bash
node tools/render.js --pix-fmt yuv444p    # better and smaller, software playback
node tools/render.js                      # yuv420p, universally compatible
```

An earlier measurement in this repo claimed 4:4:4 gained 4.8 dB over 4:2:0.
That was wrong: the test encode was self-consistent while the real render was
mis-tagged, so a colour-matrix error was misattributed to chroma subsampling.
The figures above are like-for-like.

---

## The venue

The template is **not** three equal panels. Region bounds were measured from
`DX_TradingFloor_Immersive_Template-scaled_fullSize.png` and live in
`VENUE` in `src/brand.js`:

| Region | x range | width |
| --- | --- | --- |
| South wall | 0 – 2239 | 2239 |
| West-faced corner | 2239 – 2501 | 262 |
| South-faced corner | 2501 – 2596 | 95 |
| **West wall** (viewer's eye-line) | 2596 – 4277 | 1681 |
| South-faced corner | 4277 – 4371 | 94 |
| West-faced corner | 4371 – 4634 | 263 |
| North wall | 4634 – 6878 | 2244 |

Other physical constraints carried in the same file:

- **Cube line at y = 674** on the south and north walls — below it the surface
  is a physical cube, not flat wall.
- **Speaker grills** at y 358–488, x 430–1376 (south) and x 5481–6426 (north).
- **Draped fabric** at the outer edges of both cubes.
- **Domino screen** on the west wall, x 2633–4243, y 0–628.
- Template marks everything below y = 538 as “background graphics only, no
  text”.

The composition is a continuous field with no fixed focal point, so it survives
the corner wraps and the cube line without anything important being cut in half
or lost behind a grill.

## The piece

A single sustained field rather than a sequence of movements. Two flows run at
once:

- **The mark field travels left to right** along a band that funnels toward a
  vanishing point on the west wall. One perspective factor drives element size,
  band height and trail length together, so marks are large at the outer walls
  and converge to a small, tight throat in the middle of the room — the read
  from the reference mockups. Horizontal motion trails, carried by roughly the
  nearest quarter of marks, draw the eye across the throat even where the marks
  themselves are tiny. Rate is **47–93 px/s**.
- **Arrows travel on their own axis**, up and to the right at **67.93°**,
  leaving through the top of the frame at **30–91 px/s**. They sit in the same
  perspective as the field, so they too are large at the walls and small through
  the middle.

Nothing about the look changes over the three minutes — density, palette and
rate hold steady, so the room never "cuts" to a different design.

Depth drives everything together: near marks are larger, brighter and faster;
far marks are small, dim and slow. That is what keeps the field readable rather
than flat.

## Brand compliance

- Colour is sampled exclusively from the primary magenta → cobalt gradient
  (`GRADIENT` in `src/brand.js`), with brighter "glow" partners for emissive
  marks matched to the supplied reference frames.
- **Nothing is rotated.** Both official arrow paths are used verbatim, and
  pixels and pluses are drawn axis-aligned exactly as the official patterns are
  constructed. Only position, scale, opacity and gradient fill vary.
- The complete **plus and pixel cluster patterns** drift through the field as
  whole units alongside individual marks, so the real pattern stays
  recognisable and not just its constituent marks. Cluster geometry is lifted
  verbatim from the supplied symbol artwork (`PLUS_CLUSTER`, `PIXEL_CLUSTER`).
- Individual marks keep official proportions — a plain grid square for the
  pixel, and a plus whose bar is 20.6 % of its width.

## Layout

```
src/brand.js        palette, venue geometry, official shape paths
src/scene.js        the renderer — one deterministic function of loop time
src/preview.html    browser preview shell
src/preview-main.js preview controls
tools/build-preview.js  bundles the preview into one self-contained file
tools/build-archive.sh  rebuilds an earlier version from git into dist/
tools/render.js     parallel full-resolution render and encode
tools/still.js      single-frame renders for quick checks
```

`src/scene.js` drives both the preview and the final render, so what is
approved in the browser is exactly what gets encoded.

The Vector logo is not currently in the piece: a logo reveal is by definition a
change of design, which the single-sustained-field direction rules out. The
icon geometry is still available as `LOGO_ICON` in `src/brand.js` if it should
come back.
