# Vector Institute — “Convergence”

A three-minute generative animation for the DX Trading Floor immersive room,
built from the official Vector brand assets.

**Canvas:** 6878 × 1080 · **Duration:** 180 s · **Loop:** seamless (verified
pixel-identical at the seam) · **Palette:** primary magenta → violet → cobalt
gradient.

---

## Preview it in a browser

Open **`dist/preview.html`** — it is fully self-contained, so it works straight
off disk with no server. Controls include a scrub bar, phase jump buttons, a
venue overlay showing every projector region, a loop-seam test, and a preview
resolution selector.

To rebuild it after changing the scene:

```bash
npm install
node tools/build-preview.js
```

For live development with module reloading, serve `src/` instead:

```bash
npx http-server src -p 8099   # then open http://127.0.0.1:8099/preview.html
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
nothing is re-encoded. On four cores a full 180 s / 30 fps master takes roughly
20 minutes and lands around 190 MB.

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

The composition is a continuous field, so it survives the corner wraps. Hero
elements are steered away from the grills, and the Vector icon resolves on the
west wall — centred in the viewer's eye-line and clear of every obstruction.

## The piece

A single sustained field rather than a sequence of movements. Brand marks drift
up and to the right along the arrow axis at **67.93°**, carrying motion trails,
and leave through the top of the frame. Nothing about the look changes over the
three minutes — density, palette and rate hold steady, so the room never
"cuts" to a different design.

Rate is deliberately slow for the scale of the projection: whole laps per loop
give **30 px/s** for the far field up to **91 px/s** for the nearest marks. A
mark takes between 13 and 38 seconds to cross the height of the frame.

Depth drives everything together — near marks are larger, brighter and faster;
far marks are small, dim and slow — which is what keeps the field readable
rather than flat.

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
tools/render.js     parallel full-resolution render and encode
tools/still.js      single-frame renders for quick checks
```

`src/scene.js` drives both the preview and the final render, so what is
approved in the browser is exactly what gets encoded.

The Vector logo is not currently in the piece: a logo reveal is by definition a
change of design, which the single-sustained-field direction rules out. The
icon geometry is still available as `LOGO_ICON` in `src/brand.js` if it should
come back.
