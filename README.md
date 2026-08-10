# Vector Institute — AI Summit 2026

Immersive wall content and print for the DX Trading Floor, built from the
official Vector brand assets.

**Canvas:** 6878 × 1080 · **Palette:** secondary violet → turquoise on deep
violet · **Deliverables:**

| Piece | Length | What it is |
| --- | --- | --- |
| **Convergence** | 3:00, seamless | the sustained room loop |
| **Convergence (dark)** | 3:00, seamless | the same loop with the walls receded, for use under a presentation |
| **Arrival** | 0:12, one shot | arrows gathering into the Vector logo, for the cue before a keynote |
| Name badges | — | four categories, layered PDF |

## What changed after the concept review

Concept B was chosen as the foundation, with a revised colour direction. The
nine items from the feedback and where each one lives:

| # | Item | Where |
| --- | --- | --- |
| 1 | Background to deep violet flowing into almost black | `ROOM` in `src/brand.js`, `drawBackground` in `src/scene.js` |
| 2 | Arrows on a violet → turquoise gradient | `GRADIENT_ENV` in `src/brand.js` |
| 3 | Arrows-into-logo motion piece | `src/logo-moment.js` |
| 4 | Speaker names on the walls | `drawSpeaker` in `src/scene.js` |
| 5 | Magenta is wayfinding only, not the room | `GRADIENT_WAYFINDING`, unused by the scene |
| 6 | Dark state for presentations | `stateFactors` in `src/scene.js` |
| 7 | Badge colour system | `CATEGORIES` in `tools/badges.py` |
| 8 | Badges smooth, large format textured | `tools/badges.py` — the mark field is gone from the badge |
| 9 | Concept C badge layout on the confirmed colours | `tools/badges.py` |

Two notes on the brief, neither of which changes the work:

- The rationale given for the arrow gradient reads *violet = Academia,
  turquoise = Industry*. The guidelines (p13) assign them the other way round:
  Industry `#8A25C9`, Academic Institutions `#48C0D9`. The pairing and its
  direction across the room are unaffected.
- Magenta is out of the room's palette, but the Vector mark itself keeps its
  magenta arrow in the **Arrival** piece. The mark is the mark; repainting it
  would be the brand error, not the restraint.

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
| `dist/preview.html` | Current — violet → turquoise, dark state, Arrival piece |
| `dist/preview-v3.html` | v3 — magenta → cobalt palette, pre-feedback |
| `dist/preview-v2.html` | v2 — everything on the 67.93° axis, no funnel |
| `dist/preview-v1.html` | v1 — five-phase arc, horizontal flow, logo reveal |

To rebuild any earlier version from git:

```bash
tools/build-archive.sh <commit> <name> "<banner text>"
tools/build-archive.sh 84271cc v1 "Version 1 — phase arc, horizontal flow"
tools/build-archive.sh 061d85b v2 "Version 2 — all-diagonal flow, no funnel"
tools/build-archive.sh f1c2656 v3 "Version 3 — magenta/cobalt, pre-feedback"
```

## Render the final file

```bash
node tools/render.js                      # Convergence, 6878x1080, 30 fps, CRF 16
node tools/render.js --dark               # the presentation state
node tools/render.js --moment             # Arrival, the arrows-into-logo piece
node tools/render.js --speaker "Glenda Crisp|President & CEO,|Vector Institute"
node tools/render.js --fps 60 --crf 14    # higher frame rate / quality
node tools/render.js --walls              # also cut one file per projector
node tools/render.js --duration 10        # short test render
```

Options: `--fps --crf --gop --duration --workers --out --walls --pix-fmt --dark
--moment --speaker`. Output names itself from the mode, so the three masters do
not overwrite each other.

Frames are rendered at full resolution across worker processes, piped as raw
RGBA into per-segment ffmpeg encoders, then concatenated with a stream copy so
nothing is re-encoded. On four cores a full 180 s / 30 fps master takes about
25–35 minutes. The master delivered before the concept review (yuv444p, CRF 16)
was **475 MB** at 21.1 Mbps and measured **42.1 dB** against the raw render; the
revised piece is darker overall, so expect a smaller file at the same CRF.

### Colour conversion

`-colorspace bt709` only *labels* the stream — ffmpeg's automatic RGB→YUV
conversion still uses BT.601. Tagging alone therefore produces a file converted
with one matrix and played back with another: a systematic colour shift, worth
about 4.8 dB of error against the source, and most visible on exactly the
saturated violet and turquoise this piece is built from.

The renderer converts explicitly instead:

```
scale=in_range=full:in_color_matrix=bt709:out_range=tv:out_color_matrix=bt709
```

plus `-color_range tv` so the tags match the data. Canvas gives full-range RGB;
video convention is limited-range YUV.

### Bloom is sized in scene units

The bloom taps are a fixed fraction of the 6878x1080 **scene**, never of the
backing store. Sizing them off the backing store makes the blur a constant
number of *device* pixels — which is a different fraction of the artwork at
every render resolution. A quarter-size preview then carries four times the
bloom radius of the full-resolution master, so the master arrives with visibly
less glow, softer trails and less shimmer than the preview it was approved on.

This is the one place where "the preview is exactly what gets encoded" can
quietly stop being true, because nothing else in the scene is expressed in
device pixels.

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

Two things in the room *are* placed against that geometry rather than floating
in the field:

- **Speaker names** sit at x 1452 and x 4742. The grills rule out x 430–1376 and
  x 5481–6426, and the template forbids text below y 538; those are the two
  clear blocks left, and both happen to fall on the stage side of their wall.
  The field is dense everywhere by design, so each name carries a soft scrim —
  waiting for a quiet patch would mean a mark drifting through and taking a word
  with it.
- **The Arrival lockup** is centred on the domino screen (x 2633–4243,
  y 0–628), the brightest and flattest surface in the room and the one the
  audience is already facing.

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

Colour runs violet on the south wall to turquoise on the north, meeting across
the west wall — the same place the perspective funnel converges, so the two
audiences the pairing stands for come together in the middle of the room. The
ground is deep violet at the foot of the frame falling away to almost black at
the top and through the centre, which is what keeps the walls off the speaker
and off the domino screen.

Nothing about the look changes over the three minutes — density, palette and
rate hold steady, so the room never "cuts" to a different design.

### The dark state

The room has two jobs: it is the piece during the reception, and it has to get
out of the way while someone is presenting. That is one continuous control
(`--dark`, or the slider in the preview), not a second edit of the scene — mark
alpha, the violet in the ground and the bloom strength all come down together
while the geometry stays put, so the room can be cross-faded live from the desk
and nothing moves when it changes.

### Arrival

Twelve seconds, one shot, for the cue before a keynote. It opens on the same
field, same axis, same speeds as the loop, so it can be cut to live without the
room appearing to change. Then the arrows leave the travel axis and assemble the
mark: each one is given a target sampled from *inside* the icon's own outline —
by rasterising the official paths and reading back the covered pixels, so the
notch between the V and the arrow is real and nothing drifts if the artwork is
updated — and the solid lockup resolves on top once the shape has closed. It
ends on a hold rather than a loop.

Depth drives everything together: near marks are larger, brighter and faster;
far marks are small, dim and slow. That is what keeps the field readable rather
than flat.

## Brand compliance

- Colour is sampled exclusively from the secondary violet → turquoise gradient
  (`GRADIENT_ENV` in `src/brand.js`), with brighter "glow" partners for emissive
  marks matched to the supplied reference frames. The violet glow is kept on the
  blue side of the hue deliberately: brightening violet the obvious way takes it
  toward pink, and once the additive bloom stacks a few marks the south wall
  reads magenta — the one colour that is meant to stay outside the room.
- **Nothing is rotated.** Both official arrow paths are used verbatim, and
  pixels and pluses are drawn axis-aligned exactly as the official patterns are
  constructed. Only position, scale, opacity and gradient fill vary.
- The complete **plus and pixel cluster patterns** drift through the field as
  whole units alongside individual marks, so the real pattern stays
  recognisable and not just its constituent marks. Cluster geometry is lifted
  verbatim from the supplied symbol artwork (`PLUS_CLUSTER`, `PIXEL_CLUSTER`).
- Individual marks keep official proportions — a plain grid square for the
  pixel, and a plus whose bar is 20.6 % of its width.

## Name badges

Four category badges, built on the artboard from the updated working file
(`Concept_3_badges_fixed_2.pdf`):

```bash
python3 tools/badges.py            # -> out/badges/vector-badge-*.pdf + -all.pdf
python3 tools/verify-badges.py     # contrast + layer checks
```

| | |
| --- | --- |
| Page (artboard) | 5.8125 x 7.5 in — 418.5 x 540 pt |
| Bleed | 4.0625 x 5.75 in, placed at (63, 63) |
| Trim (tag edge) | 3.8125 x 5.5 in, 18 pt corner radius |
| Safe area | 3.4375 x 4.75 in |
| Slots | dual, 45 x 11.25 pt |

The layout is the one that came out of the Concept C review — category gradient
across the top on a slant, lower two thirds in near-black, name set large on the
black — carrying the confirmed colour system and the Concept A finish.

The mark field runs across the whole card at low opacity. It is drawn twice
against the *same* geometry — once in the ground colour clipped to the colour
panel, once in the category gradient clipped to everything below it — so a mark
straddling the panel edge reads as one continuous shape that changes ink where
the ground changes, rather than as two marks that happen to meet.

The arrows are a **lattice**, not a scatter: one pitch, half-dropped rows, and
jitter small enough that the repeat still reads. Only opacity and a few skipped
cells break it up. That is what lets the arrow count come down without the card
looking sparse — a scatter at this density reads as leftovers, a tile reads as a
pattern.

Two things hold the field back where it would cost something. A clear-space
falloff fades marks to a twelfth of their opacity under the lockup, which is the
one element with no fallback if it goes soft. The band the name and body copy
occupy runs at a third of the field's opacity, easing back to full over 26 pt
either side.

Marks below the panel are lifted most of the way toward white before they are
used. Straight pairing colours arrive with wildly different weight at badge scale
— Lime sits at 0.86 relative luminance and Cobalt at 0.11 — so one category's
field would shout and another's disappear.

The panel's light also falls off into the black over about forty points, and that
spill carries the panel's own gradient rather than a single colour: violet under
the violet end, turquoise under the turquoise end. Its fade runs perpendicular to
the slanted edge, not straight down — a vertical fade starts at one *y* across
the whole width, which on a 26 pt slant means it begins 26 pt inside the panel at
the right-hand end.

Note this puts texture back on the badge, against the review's "smooth gradients
on badges, textured for large format". It is much lighter than the version that
note was written about, and held off the type, but it is a deliberate departure
worth naming when these go back for sign-off.

| Category | Gradient | Chip | Chip ink |
| --- | --- | --- | --- |
| Student | Violet → Turquoise | Turquoise | black, 9.8:1 |
| Employer | Violet → Tangerine | Tangerine | black, 10.1:1 |
| Partner | Cobalt → Lime | Lime | black, 17.3:1 |
| Vector Institute Staff | Magenta → Cobalt | Cobalt | white, 6.5:1 |

Type is sized against the safe width rather than to a preset scale: the name runs
at up to **36 pt** (a 14-character surname still only fills 73 % of the 248 pt
safe line), body lines at 13 pt, chip label at 13 pt.

Eight layers as real PDF optional content groups, vector artwork throughout, live
Karbon text, with the die-line on the top layer for reference.

### The logo is set in white

Every confirmed pairing now *leads* with a dark colour, which retires the black
lockup the previous colour system needed. White clears the 3:1 graphics floor on
all four lead colours — 6.6:1 on Violet, 6.5:1 on Cobalt, 4.3:1 on Magenta — so
the set stays consistent. Straight max-contrast would flip Magenta to black
(4.9:1 against white's 4.3:1), and one black lockup in a set of four reads as a
mistake at a lanyard's distance; `reverse_or_black` prefers white and only drops
to black if it actually fails. Chip label ink is picked the same way, by
measurement.

### The contrast check measures the worst patch, not the average

With a mark field behind the type the mean is the wrong test: a field that
averages out fine can still put one bright plus under a letter, and that is
exactly where legibility goes. `tools/verify-badges.py` tiles each ink area at
about the size of a stroke and reports the worst tile alongside the mean. On the
current set the mean runs 17–19:1 on the name and the worst tile 10.7:1 — still
clear of the 4.5:1 floor, but a third of the headroom the average implies.

### Five traps, all hit once

**PyMuPDF's rasteriser ignores optional-content state.** It renders every layer
regardless of what is switched off, so it will report that layers "work" on a
file that has none. `tools/verify-badges.py` renders through PDFium instead and
asserts that switching a layer off actually changes the pixels.

**PDFium caches by filename.** The verifier reused one scratch path, so every
layer comparison was quietly comparing a file with itself and passing. Each
render now writes a fresh path.

**Switching a layer off in a source PDF does nothing once you place it.**
Illustrator writes layers as marked-content sections in the page stream
(`/OC /MC0 BDC … EMC`), and `show_pdf_page` copies the stream verbatim — the
optional-content state belongs to the source document, not to the operators. The
first attempt at carrying the die-line across brought the *old badge artwork*
with it, on top, hiding three layers underneath. `guides_pdf` now cuts the guides
section out of the stream instead. This is the second time a top layer has hidden
a whole badge design; probing only a couple of layers is how it survives, so the
verifier now probes every one.

**Contrast needs sRGB to linear conversion first.** Skipping it understates
contrast on saturated darks by roughly two times — plain Cobalt reads 0.28
naively against a true 0.11.

**The ink value in a contrast check is relative luminance, not an RGB
component.** rgb(.03,.01,.06) is 0.0014, not 0.03; using the latter reported a
passing chip as a failure.

## Layout

```
src/brand.js          palette, venue geometry, official shape and logo paths
src/scene.js          Convergence — one deterministic function of loop time
src/logo-moment.js    Arrival — the arrows-into-logo piece
src/preview.html      browser preview shell
src/preview-main.js   preview controls
tools/build-preview.js  bundles the preview into one self-contained file
tools/build-archive.sh  rebuilds an earlier version from git into dist/
tools/render.js       parallel full-resolution render and encode
tools/still.js        single-frame renders for quick checks
tools/moment-still.js frames from Arrival
tools/badges.py       layered name badge PDFs
tools/verify-badges.py  badge contrast and layer checks
```

`src/scene.js` drives both the preview and the final render, so what is approved
in the browser is exactly what gets encoded. `src/logo-moment.js` reuses its
background, palette, axis and state control, so the two pieces cannot drift
apart.

The Vector logo does not appear in the sustained loop — a logo reveal is by
definition a change of design, which the single-sustained-field direction rules
out. It has its own piece instead.
