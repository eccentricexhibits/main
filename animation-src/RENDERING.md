# Diagonal Arrow Transition — rendering the masters

The transition is generated from `scene-builder.js`, a seeded, fully
deterministic scene description (6878 × 1080, 6.00 s, travel angle 67.93°,
gradient #B659F0 → #48C0D9, transparent background, full cover at exactly
3.00 s). The web mock-up (`../arrow-transition-mockup.html`) and the frame
renderer both consume this same module, so a local render reproduces the
approved preview frame-for-frame.

## 1. Render the PNG sequence (the alpha master)

Requires Node 18+.

```sh
cd animation-src
npm install @resvg/resvg-js
node render-svg.js 0 360 frames        # 360 frames = 60 FPS x 6 s
```

Each frame is a lossless 6878×1080 RGBA PNG (`frames/frame_0000.png` …
`frame_0359.png`). Rendering is CPU-bound (~1 min/frame/core); split the
range across processes to parallelize, e.g. four workers:

```sh
node render-svg.js 0 90 frames & node render-svg.js 90 180 frames &
node render-svg.js 180 270 frames & node render-svg.js 270 360 frames & wait
```

The renderer is deterministic: the same frame range always produces
byte-identical output, so partial/resumed renders are safe.

## 2. Encode delivery formats (both keep the alpha channel)

ProRes 4444 — the editing master for Premiere / After Effects / Resolve:

```sh
ffmpeg -framerate 60 -i frames/frame_%04d.png \
  -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -vendor apl0 \
  arrow-transition-6878x1080-60fps-prores4444.mov
```

VP9 WebM — compact, plays with transparency in Chrome/Edge/OBS
(a copy is checked in at the repo root):

```sh
ffmpeg -framerate 60 -i frames/frame_%04d.png \
  -c:v libvpx-vp9 -pix_fmt yuva420p -crf 30 -b:v 0 \
  -deadline good -cpu-used 3 -row-mt 1 -auto-alt-ref 0 \
  arrow-transition-6878x1080-60fps-alpha.webm
```

Note: to decode the WebM's alpha with ffmpeg, force the libvpx decoder:
`ffmpeg -c:v libvpx-vp9 -i arrow-transition-...-alpha.webm ...`

## 3. The cut point

The canvas is 100 % covered (zero fully-transparent pixels, verified at
full resolution) at **frame 180 = 3.000 s** — fade the incoming scene in
there. A diagonal light sweep peaks on that same frame as a flourish.
