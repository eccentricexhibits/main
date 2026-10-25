# The Misanthropic Cow, v10

v10 rebuilds the body and the rig of the 3D Misanthropic Cow. The body follows the proportions from the original 2012 Hasselblad shoot. The rig fixes the Chicken Dance problems in v09: the "wings" that grew under the armpits, and the hands that came loose from the sleeves.

Later v10 passes added:
- the head rebuilt from the mask and hood photos;
- the shag rebuilt on the user's own swatch and tuft sheet;
- clipping fixes at the arms and teats;
- light baked physics;
- a rounded belly underside;
- an animation library: Idle, Walk, Run, Sneak, Jumping Jacks, Look Around and the Chicken Dance.

| File | What it is |
|---|---|
| `models/Misanthropic_Cow_v10.glb` | Static master in the default (rest) pose. 626k triangles, real-world scale in metres, all textures embedded. |
| `models/Misanthropic_Cow_v10_Animated.glb` | Same model with a 40-joint skin and seven looping animations at 30 fps, all with baked physics. |
| `reviews/` | Turntable and close-up renders, the before/after sheet, the head-vs-photo sheet, the animation sheet, the dance pose sheet, the showcase video and the validation JSON. |
| `viewer/` | A three.js web viewer with an animation picker, a Default pose button, camera presets and a clay toggle. |
| `textures/` | The user-supplied black shag swatch and tuft sheet. |
| `pipeline/` | The Python sources that generate everything above. |

Both GLBs pass the Khronos glTF Validator with 0 errors and 0 warnings.

## What changed from v09

**Proportions.** The proportions were measured from the 2012 shoot photos:
- belly width is about 2× the mask width;
- muzzle-to-crotch is about 3 mask heights;
- the crotch is at 46 % of standing height.

The wearer is built at about 1.60 m. v09 had scaled the whole figure to fit an oversized mask, which gave it broad, square shoulders and a short barrel torso. v10 instead scales the scanned mask to 0.75 (about 0.21 m wide). The body has narrow, sloped shoulders and a long, round padded belly that hangs to the crotch. Pink satin panties show under the belly, as in shots 0077, 0120 and 0191.

**Head.** The head is built as the costume is worn, following the mask and hood photos (`IMG_2003`–`2034`, `0006`, `0013`, `0014`, `Nathan 32`). There are three separate pieces:
- **Hood.** A snug fur balaclava, about 2 cm of fur over a 1.6 m wearer's head. Its neck tucks into the torso garment's neckline, which stops at the base of the neck. The head is skinned only to the Head and Neck bones, so it turns freely without dragging the torso up into a hump.
- **Mask.** The scanned papier-mâché mask covers the hood's whole front.
- **Tube and horns.** The fur-covered cardboard tube that joins the horns belongs to the mask and rests on the mask's top edge. The scanned horns ride on its ends in their original positions relative to it.

The white paint in the mask photo gets a lift; the eyes, the muzzle and the weathered grey wash keep their colour.

**Udder, shag and leggings.**
- The udder is two large, soft pink cups. Each has one teat hanging forward over the belly and one pointing out and down.
- The black shag follows the patch layout in the photos:
  - upper chest and shoulder on the wearer's right;
  - low belly;
  - both elbows;
  - upper back right and lower back left.
- The shag uses the user's black shag swatch (`textures/black_shag_tile.jpg`) as its base, with edges that break into hanging tufts.
- On top of the base sit hanging tuft cards (4–6 cm): alpha-cut tufts from the user's tuft sheet (`textures/black_shag_tufts_sheet.png`). The white background becomes transparency, and each card uses one of the 12 tufts.
- Each patch belongs to one garment piece only, so no patch spills across a sleeve seam.
- The leggings use smaller, irregular painted white spots.
- The belly's underside is a shallow bowl with a soft edge, so it reads round from below instead of sliced flat.
- The hoof caps are glossy black, as in every photo. v08 had them mid grey-teal.

**Wings under the armpits (fixed).** v09 split the arm from the torso with x-coordinate thresholds. Raising the elbows dragged a strip of torso flank along with the upper arm. v10 builds the sleeves as separate tubes set into the shoulder, the way the costume is sewn. The torso keeps its own complete surface, and a clavicle bone carries the top of the shoulder.

**Hands that don't connect (fixed).** Each glove tucks 3.5 cm up inside its sleeve end. The sleeve and the glove are weighted by the same function of position along the forearm, so they move as one. In the wing pose the fists follow the forearm instead of being bent 90° at the wrist. v08's flared cuff ring and its halo strands were removed, because at this scale they z-fought with the sleeve.

**Clipping (fixed).**
- Each elbow swings around its shoulder-wrist line to stay clear of the udder cups and torso. The swing is chosen frame by frame from a collision cost and kept continuous with a Viterbi pass, then smoothed around the loop.
- Half-rotation helper joints at the sleeve head and the elbow keep both joints full when they bend.
- The torso just around each sleeve head follows the arm slightly.
- The belly's fullest point was lowered 2.7 cm and the bottom teats angled forward. This gives the teats clearance at rest, matching the dip under the cups in shots 0120 and 0071.

**Light physics (baked).** glTF has no live physics, so damped springs are simulated over three loops of each animation and the last loop is baked into the bones. It plays in any glTF viewer and every animation loops seamlessly.
- **Teats:** each teat swings on its own bone and collides with the belly. In the dance it peaks at about 20° and averages about 5°.
- **Shag patches:** six spring bones drag the tuft tips, with up to about 4 cm of lag at the elbows.
- **Belly and cups:** they jiggle; the cups are kept from sinking into the belly.

## Animations

All seven animations loop seamlessly and play in place, with no root travel.

| Animation | Length | What it does |
|---|---|---|
| Idle | 4.0 s | Breathing, a small weight shift, and the arms relaxed at the sides. |
| Walk | 1.12 s cycle | 36 cm stride; heel strike and toe-off; hips sway and roll; the arms swing opposite the legs, clear of the belly. |
| Run | 0.72 s cycle | Flight phase, high knee lift, forward lean, bent pumping arms. |
| Sneak | 2.6 s cycle | Cartoon tiptoe: crouched, high knees, pointed toes, hooves dangling in front of the chest, head scanning side to side. |
| Jumping Jacks | 4.0 s (4 jacks) | Airborne between the open and closed positions; arms overhead; knees bend on landing. |
| Look Around | 6.0 s | Looks left and then right with the near-side hoof shading the eyes, leans in to peer, looks up, then settles. |
| Chicken Dance | 12.0 s | Beaks, Wings, Wiggle, Claps (3 s each, four moves each). |

The **default pose** is the rest pose: arms relaxed and down at the sides. In the viewer the Default pose button resets the skeleton to it, and the static master is exported in it.

### Animation clipping

All depths are the 99.5th percentile over every frame.

| Animation | Arms into cups or torso | Teats into belly | Gloves into body | Lowest slipper point |
|---|---|---|---|---|
| Idle | 0.6 mm | 0 mm | 0 mm | 6.0 mm above floor |
| Walk | 1.7 mm | 0 mm | 0 mm | 1.2 mm above floor |
| Run | 0 mm | 0.8 mm | 0 mm | 1.4 mm above floor |
| Sneak | 0 mm | 0 mm | 0 mm | 2.6 mm above floor |
| Jumping Jacks | 0 mm | 0 mm | 0 mm | 6.0 mm above floor |
| Look Around | 8.6 mm | 0 mm | 0 mm | 6.0 mm above floor |
| Chicken Dance | 0 mm | 2.4 mm | 0 mm | 6.0 mm above floor |

The Look Around figure is the relaxed arm pressing into the plush chest side while the body twists.

In every animation the gloves stay tucked into the sleeves: the sleeve-to-glove distance never changes by more than 1.3 mm.

## Measured over the dance

| Check | v09 | v10 |
|---|---|---|
| Arms and gloves into the udder cups or torso, 99.5th percentile | not measured | 0 mm in all four phases |
| Teats into the belly, 99.5th percentile | not measured | 0 mm, except 2.4 mm at the bottom of the Wiggle squat |
| Torso edge stretch, 99.9th percentile, worst frame | 4.08× | 1.74× |
| Sleeve edge stretch, 99.9th percentile, worst frame | 12.85× | 2.79× |
| Sleeve end to glove distance, at rest and at the worst frame | not measured | 15.8 mm and 16.1 mm |
| Glove into body, 99.5th percentile | not measured | 0 mm in all four phases |
| Clap contact gap | not measured | 0.3 mm |
| Loop seam error | 0 | 0 |
| Planted-foot drift | ~0 | 0.05 mm |

Most of the remaining sleeve stretch is on the outside of the elbow at the top of each wing flap. That is the usual limit of linear-blend skinning on a sharply bent elbow. The torso stretch is higher than in the first v10 pass (1.40×) because the shoulder now follows the arm a little; that trade removes the poke-through at the sleeve head. The full numbers are in `reviews/validation_v10.json`. `reviews/v09_same_metrics.json` has the same metric run on the v09 rig.

## The rig

There are 40 joints:
- **Spine and head:** Hips, Spine, Belly, Chest, Neck, Head.
- **Each side:** Shoulder (clavicle), UpperArm, Forearm, Hand, HoofFingers, Thumb, Thigh, Shin and Foot.
- **Udder:** one Udder bone per cup.
- **Helpers:** UpperArmRoot and Elbow on each side. Each takes half its joint's rotation.
- **Teats:** four bones (Teat_L/R_bottom, Teat_L/R_outer).
- **Shag:** six patch bones (Shag_chest_R, Shag_belly, Shag_back_upper_R, Shag_back_lower_L, Shag_elbow_L, Shag_elbow_R).

The teat, shag, belly and udder bones carry the baked physics. If you use the rig in a game engine, those 12 bones are the ones to put live spring or "jiggle" components on; the dance clip then only needs the body bones. Bind rotations are identity, and all inverse bind matrices are translations.

The solver is shared by all the animations:
- **Arms:** IK or FK, with the elbow swivel for collision avoidance.
- **Legs:** foot IK with heel and toe contact.
- **Helpers:** the half-rotation joints.
- **Physics:** the baked springs.

Each animation is a small class in `clips.py`. The Chicken Dance is in `anim.py` and runs 3 s per phase, with four moves in each:
- **Beaks:** the hoof "beaks" snap open and shut in front of the chest.
- **Wings:** fists at the chest corners while the elbows flap.
- **Wiggle:** knees bend and the hips swish.
- **Claps:** four claps above the udder.

## Orientation and naming

- +Y is up and +Z is the way the character faces. The model is in metres.
- **+X is the character's left.** Bone and mesh names now use the character's own left and right.
- v09 named some parts by screen side. Its "Left" glove was the character's right. The broken horn with the exposed wire is on the character's right (-X), which matches the photos.

## Rebuilding

You need Python 3.12 or later with `numpy scipy pillow scikit-image vtk`, plus `g++` and `ffmpeg`. The pipeline reuses two things from the v09 handoff:
- the review GLB, which supplies the mask scan, horns, gloves and slippers;
- the `textures-v09` folder, which supplies the fur, shag and cotton swatches.

```bash
cd pipeline
python build_v10.py <handoff>/project/dist/assets/geometry-v09.glb \
                    <handoff>/project/model-source/textures-v09  ../build
python render_reviews.py ../build/rigged.pkl ../reviews <geometry-v09.glb> <shoot photos...> --head=<head photo folder>
python render_dance.py   ../build/rigged.pkl showcase ../reviews/Misanthropic_Cow_v10_Animations.mp4
python render_dance.py   ../build/rigged.pkl sheet    ../reviews/Animation_Clips_v10.jpg
python compare_v09.py <handoff>/project/dist/assets/cow-dance-test.glb \
                      <handoff>/project/dist/assets/dance-matrices.bin ../reviews/v09_same_metrics.json
```

Add `--quick` to `build_v10.py` for a half-resolution build that takes about 3 minutes. The full build takes about 8 minutes; most of that time goes to solving the elbow paths and simulating the physics for all seven animations. `preview_clips.py` poses a few frames of each animation in seconds, for working on the choreography.

Where things live:
- `design.py`: proportions, as signed-distance primitives;
- `textures.py`: shag patch and spot placement;
- `rig.py`: skin weights;
- `anim.py` and `clips.py`: the choreography.

The web copies in `viewer/` were made with gltfpack 0.22:
- `cow-meshopt.glb` uses `-cc -kn -km -ke` (full detail).
- `cow-plain.glb` uses `-kn -km -ke -si 0.4` (a simplified fallback). The page also accepts base64 copies (`cow-meshopt.b64.txt`, `cow-plain.b64.txt`) for hosts that only serve text; make them with `base64 -w0`.

To view them locally, run `python3 -m http.server` inside `viewer/` and open the page. three.js loads from the jsDelivr CDN.

## Known limits

- The proportions come from photos at an assumed 1.6 m height. Nothing was measured from the costume.
- The side-jaw photo projection on the mask is still stretched in pure side views, as in v09.
- The black shag is a texture plus alpha-cut tuft cards, not a simulated groom. Better tuft images would improve it directly.
- The physics is baked springs, not live simulation. Only the teats collide with anything (the belly).
- Locomotion plays in place; feet slide back during stance like a treadmill, so add root motion in your engine.
- There's no cloth simulation. The suit deforms by skinning only.
- The elbow stretch noted above remains.
