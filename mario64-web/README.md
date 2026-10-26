# Mario 64 Playground

A small browser game built around Mario as he exists in *Super Mario 64*: his real model,
textures, all 209 animations, his voice clips, and a JavaScript port of the game's own
movement code (walking, running, triple jumps, long jumps, backflips, side flips, wall
kicks, ground pounds, dives, ledge grabs, slides, punches and kicks).

**No Nintendo data is included in this repository.** When the page opens it asks for your
own ROM of *Super Mario 64 (US)*. Everything (model, textures, animations, voice) is decoded
from that file inside your browser; nothing is uploaded anywhere. The ROM can optionally be
remembered in your browser's local storage (IndexedDB) so you don't have to pick it again.

## Playing

The page uses ES modules, so serve the folder over HTTP rather than opening the file
directly:

```sh
cd mario64-web
python3 -m http.server 8000
# open http://localhost:8000
```

It also works from any static host (for example GitHub Pages).

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
