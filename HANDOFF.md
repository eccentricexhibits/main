# AI Summit 2026 — immersive room handoff

Everything needed to render, play back, change or take over the DX Trading Floor
immersive content. Written for three readers: the AV team running the room, the
designer who picks this up next, and whoever has to answer "why is it like
that?" in six months.

The companion document is `README.md`, which covers the same ground in more
depth and from the code's side. This file is the operational one.

---

## 1. Deliverables and status

| Piece | Spec | Status |
| --- | --- | --- |
| **Convergence** | 6878 × 1080, 3:00, seamless loop | source complete, **not rendered** |
| **Convergence (dark)** | same, walls receded for presentations | source complete, **not rendered** |
| **Arrival** | 6878 × 1080, 0:12, one shot | source complete, **not rendered** |
| **Name badges** | 4 categories, layered PDF, 5.8125 × 7.5 in artboard | delivered |
| **Browser preview** | `dist/preview.html`, self-contained | delivered |
| **This document** | `dist/handoff.html` (live), `dist/AI-Summit-2026-handoff.pdf`, `HANDOFF.md` | — |

**Read this before anything else.** No video master has been rendered from the
current cut. The only master ever delivered — 475 MB, H.264 4:4:4, split into 17
parts — is the **pre-feedback v3** piece on the magenta → cobalt palette. The
concept review replaced that palette, so **that file is superseded and must not
go to the venue.** It is still viewable as `dist/preview-v3.html`.

Rendering is a single command per piece and takes 25–35 minutes each on four
cores (see §5). It has deliberately not been run yet because of §2.

---

## 2. Three things to settle before rendering

**1. Pixel format — this one blocks the render.** Measured like-for-like on this
content, 4:4:4 is both higher quality *and* smaller than 4:2:0:

| Encode | PSNR vs source | Size (3 min) |
| --- | --- | --- |
| yuv420p CRF 16 | 36.6 dB | ~520 MB |
| **yuv444p CRF 16** | **41.7 dB** | **~428 MB** |

Saturated brand colour on near-black is the worst case for chroma subsampling,
so the encoder spends bits on the residual. The catch is that H.264 High 4:4:4
Predictive decodes in software (VLC, Resolume, ffmpeg-based media servers) but
not on every hardware decoder. **Ask the venue what the playback machine is.** If
there is any doubt, render 4:2:0 — it is the default and it is universally safe.

**2. Speaker names are baked into the render, not live text.** Each name needs
its own file. Before rendering, the production needs: the speaker list, their
role lines, and whether names ride the loop all evening or only around their own
session. If names change on the night there is no way to update them without a
re-render, so if that is a risk, run the room without names and put them on the
domino screen instead.

**3. Two items carried from the concept review, both needing sign-off:**

- The Vector mark in **Arrival** keeps its magenta arrow. Magenta is out of the
  room's *palette*, but the mark is the mark — repainting it would be the brand
  error rather than the restraint. If marketing wants it gone, the all-white
  knockout lockup is also official and it is a one-line change.
- The **badges carry texture**, against the review's "smooth gradients on
  badges, textured for large format". It is much lighter than the version that
  note was written about and it is held off the type, but it is a deliberate
  departure and was requested after the review.

---

## 3. Playback spec

| | |
| --- | --- |
| Resolution | 6878 × 1080 |
| Frame rate | 30 fps (`--fps 60` available) |
| Codec | H.264 High, CRF 16, `preset slow` |
| Pixel format | yuv420p default, yuv444p optional — see §2 |
| Colour | BT.709 primaries / transfer / matrix, **limited range** |
| GOP | 30 frames (1 s), fixed, scene-cut detection off |
| Audio | none |

The short fixed GOP is deliberate: it keeps seeking and loop restarts snappy on
venue playback hardware, and it guarantees every segment opens on a keyframe.

**Convergence loops seamlessly.** The loop has been verified pixel-identical at
the seam — frame at t=0 and frame at t=180 differ by zero bytes. No crossfade is
needed or wanted; a crossfade will visibly soften the one frame it touches.

**Arrival does not loop.** It ends on a hold, which is there so it can sit under
an introduction and be cut away from on a cue. Looping it will snap the lockup
back to an empty room.

**Per-projector files** can be cut from the master with `--walls`, giving one
file per wall (2239, 1681 and 2244 px wide). Only do this if the media server
cannot window a single 6878-wide source — the corners are part of the composition
and a single source keeps them in register for free.

---

## 4. Running the room

### The two room states

**Show state** is the piece: full brightness, for the reception and the breaks.

**Dark state** is for when someone is presenting. The walls recede so they are
not competing with what is on the screen behind the stage. Mark brightness drops
to 24 %, the violet in the ground to 30 %, and bloom to 26 %.

They are two files, but they are **frame-for-frame identical in geometry** —
same scene, same deterministic seeds, same timeline. A cross-dissolve between
the two at matching timecode reads as a lighting change rather than a cut. If
the media server can hold both in sync, that is the nicest way to run it. If it
cannot, a hard cut on a beat is fine; nothing moves except brightness.

### Cue outline

| Cue | File | Notes |
| --- | --- | --- |
| Doors / reception | Convergence (show) | loops indefinitely |
| ~12 s before a keynote walks on | Arrival | holds on the lockup at 0:12 |
| Speaker on stage | Convergence (dark) | cut or dissolve from the Arrival hold |
| Session ends | Convergence (show) | |

Arrival opens on the same field, the same axis and the same speeds as the loop,
so cutting into it from Convergence does not show a jump. Its timeline:

| Time | What happens |
| --- | --- |
| 0:00 – 0:03 | the field, indistinguishable from the loop |
| 0:03 – 0:07.2 | arrows leave the travel axis and gather on the west wall |
| 0:07.2 – 0:08.6 | the solid lockup resolves out of the swarm |
| 0:08.6 – 0:10 | the wordmark arrives |
| 0:10 – 0:12 | hold |

### Wayfinding

**Magenta is the wayfinding colour** — signs and directional arrows throughout
the venue. It is deliberately kept out of the immersive content so the two do
not compete. The primary magenta → cobalt gradient is still in the palette
module (`GRADIENT_WAYFINDING` in `src/brand.js`) for the print pieces.

---

## 5. Rebuilding from source

### Requirements

- **Node 18+** — `npm install` (canvas, esbuild, ffmpeg-static, playwright)
- **Python 3.11+** for the badges — `cairosvg pymupdf pikepdf pypdfium2 numpy
  pillow`
- **Karbon-Semibold.otf** and **Karbon-Regular.otf** in the repository root.
  They are licensed fonts and are committed here; check that is acceptable
  before this repo goes anywhere public.

ffmpeg comes from `ffmpeg-static`, so there is nothing to install system-wide.

> On a machine with more than one Python, install the packages into the same
> interpreter you invoke — more than one `python3` on `PATH` is the most common
> reason `tools/badges.py` fails on a fresh machine. Every command in this
> section was verified end to end on a clean clone.

### Commands

```bash
npm install

node tools/build-preview.js            # rebuild dist/preview.html
node tools/render.js                   # Convergence, show state
node tools/render.js --dark            # Convergence, dark state
node tools/render.js --moment          # Arrival
node tools/render.js --pix-fmt yuv444p # see section 2
node tools/render.js --walls           # also cut per-projector files
node tools/render.js --duration 10     # short test render
node tools/render.js --speaker "Glenda Crisp|President & CEO,|Vector Institute"

python3 tools/badges.py                # the four badge PDFs plus a combined one
python3 tools/verify-badges.py         # contrast + layer checks, must pass
python3 tools/handoff-pdf.py           # this document as a PDF
python3 tools/build-handoff.py         # this document as a live web page
```

Output names itself from the mode, so the three masters do not overwrite each
other:

| Command | Output |
| --- | --- |
| `node tools/render.js` | `out/vector-convergence-6878x1080.mp4` |
| `node tools/render.js --dark` | `out/vector-convergence-dark-6878x1080.mp4` |
| `node tools/render.js --moment` | `out/vector-arrival-6878x1080.mp4` |
| `python3 tools/badges.py` | `out/badges/vector-badge-*.pdf` + `-all.pdf` |
| `python3 tools/handoff-pdf.py` | `dist/AI-Summit-2026-handoff.pdf` |
| `python3 tools/build-handoff.py` | `dist/handoff.html` |

Full option list: `--fps --crf --gop --duration --workers --out --walls
--pix-fmt --dark --moment --speaker`.

`out/` is gitignored — everything in it regenerates. The badge build is
deterministic: a rerun on a clean clone reproduces the same PDFs.

### Expected cost

About 25–35 minutes per 3-minute master on four cores. Frames render at full
resolution across worker processes, pipe as raw RGBA into per-segment ffmpeg
encoders, and are concatenated with a stream copy so nothing is re-encoded.

### Previewing

Two self-contained pages, both of which open straight off disk with no server:

- **`dist/handoff.html`** — this document with the room running live at the top
  of it and the badge set below. The one to send to someone who needs to *see*
  the design rather than read about it.
- **`dist/preview.html`** — the working review tool. Same player, no prose.

Both carry each piece, a scrub track, the venue overlay, the room-state slider,
speaker-name fields and a loop-seam test. **The preview is exactly what gets
encoded**: the same scene functions drive the page and the renderer.

Earlier cuts stay viewable rather than merely recoverable:

| File | Version |
| --- | --- |
| `dist/preview.html` | current |
| `dist/preview-v3.html` | magenta → cobalt, pre-feedback |
| `dist/preview-v2.html` | all-diagonal flow, no funnel |
| `dist/preview-v1.html` | five-phase arc, horizontal flow |

---

## 6. The venue, and what can go where

The template is **not** three equal panels. All bounds were measured from
`DX_TradingFloor_Immersive_Template-scaled_fullSize.png` and live in `VENUE` in
`src/brand.js`.

| Region | x range | Width |
| --- | --- | --- |
| South wall | 0 – 2239 | 2239 |
| West-faced corner | 2239 – 2501 | 262 |
| South-faced corner | 2501 – 2596 | 95 |
| **West wall** (audience eye-line) | 2596 – 4277 | 1681 |
| South-faced corner | 4277 – 4371 | 94 |
| West-faced corner | 4371 – 4634 | 263 |
| North wall | 4634 – 6878 | 2244 |

Hard constraints:

- **Speaker grills** at y 358–488, x 430–1376 (south) and x 5481–6426 (north).
  Artwork behind them reads as texture at best. Nothing load-bearing here.
- **No text below y = 538** — the template marks everything below that line as
  background graphics only.
- **Cube line at y = 674** on the south and north walls. Below it the surface is
  a physical cube, not flat wall.
- **Draped fabric** at the outer edges of both cubes — soft, non-flat surfaces.
- **Domino screen** on the west wall, x 2633–4243, y 0–628. Flattest and
  brightest surface in the room; the Arrival lockup is centred on it.

Those constraints are what place the **speaker names** at x 1452 and x 4742 —
the grills and the no-text line leave exactly one clear block per side wall, and
both happen to fall on the stage side, so the names read close to the eye-line.

The composition is otherwise a continuous field with no fixed focal point, so it
survives the corner wraps and the cube line without anything important being cut
in half.

---

## 7. Things that will bite whoever edits this

Each of these was hit once. Longer write-ups are in `README.md`.

**Bloom must be sized in scene units, never off the backing store.** Sizing it
off the backing store makes the blur a constant number of *device* pixels, which
is a different fraction of the artwork at every render resolution — a
quarter-size preview then carries four times the bloom radius of the master, and
the master arrives with visibly less glow than the preview it was approved on.
This is the one place where "the preview is what gets encoded" can quietly stop
being true.

**`-colorspace bt709` only labels the stream.** ffmpeg's automatic RGB→YUV
conversion still uses BT.601, so tagging alone produces a file converted with one
matrix and played back with another — about 4.8 dB of error, worst on exactly the
saturated violet and turquoise this piece is built from. The renderer converts
explicitly with a `scale=…bt709…` filter plus `-color_range tv`.

**Additive marks on a violet ground walk toward magenta.** The ground pre-loads
the blue channel, so once blue pins at 255 every further addition only moves red
and green. At the loop's mark sizes it never gets far enough to see; at Arrival's
it turned the south wall pink. Arrival therefore composites normally and lets the
bloom supply the glow; the loop keeps its additive field.

**PyMuPDF's rasteriser ignores optional-content state** — it will report that
layers "work" on a file that has none. The badge verifier renders through PDFium.

**PDFium caches by filename.** Reusing one scratch path made every layer
comparison silently compare a file with itself.

**Switching a layer off in a source PDF does nothing once you place it.**
Illustrator writes layers as marked-content sections in the page stream, and
`show_pdf_page` copies the stream verbatim. The first attempt at carrying the
die-line across brought the old badge artwork with it, on top, hiding three
layers underneath.

---

## 8. Decisions log — don't "fix" these

- **Nothing rotates.** Both official arrow paths are used verbatim, and pixels
  and pluses are drawn axis-aligned exactly as the official patterns are
  constructed. Only position, scale, opacity and fill vary. This was an explicit
  constraint from the outset.
- **Magenta is wayfinding only**, and the violet glow stop is kept on the blue
  side of the hue for the reason in §7.
- **The Vector mark keeps its magenta arrow** in Arrival. See §2.
- **The logo does not appear in the sustained loop.** A logo reveal is by
  definition a change of design, which the single-sustained-field direction
  rules out. It has its own piece instead.
- **The badge mark field uses a different seed per side.** Marks on the colour
  panel are darker than their ground; marks on the black are lighter than
  theirs. Run one mark across the boundary and its polarity inverts half-way
  through, and the edge becomes the loudest thing on the card. Two independent
  fields meeting at a clean line is what reads as continuous — building one
  field across both, which sounds more seamless, is what makes the seam.
- **Badge mark opacity is solved, not set.** A fixed opacity gives a mark on Lime
  nearly three times the contrast of the same mark on Cobalt.
- **The badge logo is white on all four categories.** Every confirmed pairing
  leads with a dark colour, and white clears the 3:1 graphics floor on all of
  them. Straight max-contrast would flip Magenta to black, and one black lockup
  in a set of four reads as a mistake at a lanyard's distance.

### One correction to carry forward

An earlier note in this project flagged the perspective funnel's vanishing point
as possibly misplaced — sitting at the canvas centre rather than the centre of
the west wall. That was wrong, and it needs no action: the throat is at x 3439
and the west wall's centre is at x 3436.5, a difference of **2.5 px in 6878**.

---

## 9. File map

```
src/brand.js           palette, venue geometry, official shape and logo paths
src/scene.js           Convergence — one deterministic function of loop time
src/logo-moment.js     Arrival — the arrows-into-logo piece
src/preview.html       browser preview shell
src/preview-main.js    preview controls
src/handoff.html       browser handoff shell
src/handoff-main.js    handoff player

tools/render.js        parallel full-resolution render and encode
tools/build-preview.js bundles the preview into one self-contained file
tools/build-archive.sh rebuilds an earlier version from git into dist/
tools/still.js         single-frame renders for quick checks
tools/moment-still.js  frames from Arrival
tools/badges.py        layered name badge PDFs
tools/verify-badges.py badge contrast and layer checks
tools/handoff-pdf.py   renders HANDOFF.md to a print-ready PDF
tools/build-handoff.py bundles HANDOFF.md + the live player into one HTML file
tools/rejoin-windows.bat  reassembles a split master on Windows

HANDOFF.md             this document — the operational one, and the source
                       for both the PDF and the web version
README.md              the same ground from the code's side

Official Vector Logo.svg, Vector Official - Arrow {Regular,Long}.svg,
Vector Official {Pixel,Plus} Symbol.svg      supplied brand artwork
Karbon-{Regular,Semibold}.otf                supplied fonts
BrandGuidelines_QuickReference_10_31_25.pdf  supplied guidelines
DX_TradingFloor_Immersive_Template-scaled_fullSize.png   venue template
Concept_3_badges_fixed_2.pdf                 badge artboard and die-line
Feedback.docx                                the concept review
AI_Summit_2026_Presentation_DRAFT.pdf        the concept presentation
```

`src/scene.js` drives both the preview and the final render.
`src/logo-moment.js` reuses its background, palette, axis and state control, so
the two pieces cannot drift apart.

---

*Repository:* `eccentricexhibits/main`, branch
`claude/brand-animation-3wall-d2pcnv`. <!--STAMP-->
