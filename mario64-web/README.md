# Misanthropic Cow 64

A small browser game starring **The Misanthropic Cow**, moving with Mario's physics and
animations from *Super Mario 64*. Mario himself is still selectable from the pause menu.

There are two cows, picked from the pause menu (and in the animation viewer):

- **Cow 64** (default): a low-poly (about 3,000 triangles), Mario-proportioned version with a
  big head, chunky body and short legs, drawn at 1.2x Mario's size. Each body part is a rigid
  mesh built in the local frame of one of Mario's 20 animated parts, the way Mario's own N64
  model is built, so every Mario animation fits it exactly. That includes the punch/kick
  scaling and the floor-aligned crawling and sliding. Its face is the real mask from the
  detailed model, rendered into a texture when the game loads; without the detailed model it
  falls back to a drawn face. The geometry comes from code (`src/render/lowPolyCow.js`), with
  no image files.
- **Detailed cow**: the original 3D model with its own skeleton, described below.

## The detailed cow

- Model: `assets/misanthropic_cow.glb` (not committed; see below), a game-ready copy of
  *Misanthropic_Cow_v11_FirstPass_Animated.glb*. Triangles were cut from 620k to 133k (the
  scanned mask keeps the most detail, the alpha-card fur is untouched), textures capped at
  1024 px and the geometry meshopt-compressed: 35 MB down to 5.9 MB. The skeleton and all 18
  clips are unchanged.
- Animation (`src/render/cowModel.js`): idling, walking, sneaking and running use the cow's
  own clips (Idle, Look Around, Walk, Sneak, Run), sped up to match the ground speed. It
  switches to Depressed Walk and Exasperated when health is low, and does the Chicken Dance
  after getting the star. Every other move (jumps, flips, punches, dives, ledge grabs,
  slides, sleeping...) uses Mario's animation from the ROM, retargeted onto the cow's
  skeleton at runtime: the arms are re-aimed from Mario's A-pose to the cow's resting pose,
  and root motion is scaled to the cow's longer legs. Clips cross-fade over 0.14 s.
- Physics tweak: the cow's top speed is 78% of Mario's (about 24 instead of 32 units per
  frame) so its run cycle doesn't look frantic. Everything else is Mario's original
  physics. Triple jumps and long jumps still work: a long jump covers about 1,370 units,
  and the level's widest gap is 950.
- Mario's voice clips are off by default when playing as the cow (pause menu to enable).
- The animation viewer can show any of Mario's 209 animations on the cow, plus the cow's
  own clips.

The model file is deliberately not committed while this repository is public. To run the
cow version from source, copy the optimized GLB to `assets/misanthropic_cow.glb`; without
it the game falls back to Mario. `npm run build` embeds it into the standalone files in
`dist/` (which are git-ignored for the same reason).

## About the engine

The game is built around Mario as he exists in *Super Mario 64*: his real model,
textures, all 209 animations, his voice clips, and a JavaScript port of the game's own
movement code (walking, running, triple jumps, long jumps, backflips, side flips, wall
kicks, ground pounds, dives, ledge grabs, slides, punches and kicks).

**No Nintendo data is included in this repository.** When the page opens it asks for your
own ROM of *Super Mario 64 (US)*. Everything (model, textures, animations, voice) is decoded
from that file inside your browser; nothing is uploaded anywhere. The ROM can optionally be
remembered in your browser's local storage (IndexedDB) so you don't have to pick it again.

## Playing

**Easiest:** double-click `dist/mario64-playground.html` (built locally with `npm run build`). It is a single
self-contained file (code, styles and Three.js inlined) that runs straight from disk, no
server needed. `dist/mario64-viewer.html` is the matching animation viewer.

To work on the source, serve the folder over HTTP (the unbundled pages use ES modules,
which browsers won't load from `file://`):

```sh
cd mario64-web
python3 -m http.server 8000
# open http://localhost:8000
```

It also works from any static host (for example GitHub Pages).

After changing the source, rebuild the standalone files with `npm install && npm run build`.
The physics tests run with `ROM=path/to/sm64.z64 node tests/physics/run.mjs`.

| Action | Keyboard | Gamepad |
| --- | --- | --- |
| Move | WASD (hold Ctrl to walk) | Left stick |
| Jump (A) | Space or K | A / Cross |
| Punch, dive, kick (B) | J or X | B, X / Circle, Square |
| Crouch, ground pound, long jump (Z) | Shift or L | LT / RT / LB |
| Camera | Drag the mouse, Q/E or arrow keys, mouse wheel, R/F | Right stick, D-pad |
| Pause | Esc | Start |

Touch controls appear automatically on phones and tablets.

**Goal:** collect the 8 red coins scattered around the playground, then grab the Power
Star that appears on top of the central tower. Your time is shown when you get it.

`viewer.html` is an animation browser that plays any of Mario's 209 animations with
selectable eyes, hands and cap.

## How it works

| Piece | File | What it does |
| --- | --- | --- |
| ROM loader | `src/rom/rom.js` | Normalises .z64/.v64/.n64 byte order, checks the SHA-1, maps ROM segments |
| MIO0 | `src/rom/mio0.js` | Decompresses Nintendo's MIO0 asset banks |
| Geo layouts | `src/rom/geo.js` | Parses the scene-graph bytecode that arranges Mario's 20 animated body parts |
| Display lists | `src/rom/f3d.js` | Interprets Fast3D graphics commands into triangle batches, lights, combiner settings and decoded textures |
| Animations | `src/rom/anims.js` | Reads the animation bank (per-bone rotation tracks + root translation) |
| Voice | `src/rom/audio.js` | Reads the sound banks and decodes Mario's VADPCM voice samples |
| Rendering | `src/render/` | Builds Three.js meshes, emulates the N64 colour combiner in a shader, ports the geo callbacks (blinking, hand poses, punch scaling, torso tilt) |
| Physics | `src/mario/`, `src/engine/` | JavaScript port of `mario.c`, `mario_step.c`, the action files and surface collision from the SM64 decompilation, running at the original 30 Hz |
| Game | `src/game/`, `src/main.js` | Playground level, follow camera, input, HUD, red coins and star |

The physics and data formats follow the community decompilation of Super Mario 64
(github.com/n64decomp/sm64). Three.js r170 (MIT) is vendored in `vendor/`.

Only the unmodified US ROM (SHA-1 `9bef1128717f958171a4afac3ed78ee2bb4e86ce`) is
supported, because asset locations differ between releases.

Super Mario 64 and Mario are trademarks of Nintendo. This is an unofficial fan project.
