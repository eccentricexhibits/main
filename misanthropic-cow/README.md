# The Misanthropic Cow, v10

v10 rebuilds the body and the rig of the 3D Misanthropic Cow. The body follows the proportions from the original 2012 Hasselblad shoot. The rig fixes the Chicken Dance problems in v09: the "wings" that grew under the armpits, and the hands that came loose from the sleeves.

The second v10 pass (this one) adds four more things:
- the head rebuilt from the mask-and-hood photos, with the fur horn tube restored;
- toned-down shag;
- clipping fixes at the arms and teats;
- light baked physics.

| File | What it is |
|---|---|
| `models/Misanthropic_Cow_v10.glb` | Static master. 639k triangles, real-world scale in metres, all textures embedded. |
| `models/Misanthropic_Cow_v10_ChickenDance.glb` | Same model with a 40-joint skin and the 12-second Chicken Dance (30 fps), including baked physics. |
| `reviews/` | Turntable and close-up renders, the before/after sheet, the head-vs-photo sheet, the pose review sheet, the dance video and the validation JSON. |
| `viewer/` | A three.js web viewer that plays the dance, with camera presets and a clay toggle. |
| `pipeline/` | The Python sources that generate everything above. |

Both GLBs pass the Khronos glTF Validator with 0 errors and 0 warnings.

## What changed from v09

**Proportions.** The proportions were measured from the 2012 shoot photos:
- belly width is about 2× the mask width;
- muzzle-to-crotch is about 3 mask heights;
- the crotch is at 46 % of standing height.

The wearer is built at about 1.60 m. v09 had scaled the whole figure to fit an oversized mask, which gave it broad, square shoulders and a short barrel torso. v10 instead scales the scanned mask to 0.75 (about 0.21 m wide). The body has narrow, sloped shoulders and a long, round padded belly that hangs to the crotch. Pink satin panties show under the belly, as in shots 0077, 0120 and 0191.

**Head.** The mask-and-hood photos (`IMG_2003`–`2034`) were used for the head:
- **Mask over the hood.** The papier-mâché mask covers the whole front of the fur hood. The hood is shaped so that at the mask's back plane it is 92 % of the mask's outline. The mask therefore overhangs the fur all round, and the hood swells out behind it into a large rounded back. The hood narrows toward the crown and drapes onto the shoulders.
- **Horn tube.** The fur-covered cardboard tube that joins the horns runs across the top again, seated on the mask's top edge. Each scanned horn rides on one of its ends, in its original scan position relative to the tube. v09's rectangular "crown block" was a stand-in for this tube.
- **Mask colour.** The white paint in the mask photo gets a lift. The eyes, the muzzle and the weathered grey wash keep their colour.

**Udder, shag and leggings.**
- The udder is two large, soft pink cups. Each has one teat hanging forward over the belly and one pointing out and down.
- The black shag follows the patch layout in the photos:
  - upper chest and shoulder on the wearer's right;
  - low belly;
  - both elbows;
  - upper back right and lower back left.
- The shag is mostly in the texture now: streaked, clumped long pile with edges that break into hanging tufts. On top of that sit sparse clumps of 5 short strands (1.6–3.6 cm). Each patch belongs to one garment piece only, so no patch spills across a sleeve seam.
- The leggings use smaller, irregular painted white spots.
- The hoof caps are glossy black, as in every photo. v08 had them mid grey-teal.

**Wings under the armpits (fixed).** v09 split the arm from the torso with x-coordinate thresholds. Raising the elbows dragged a strip of torso flank along with the upper arm. v10 builds the sleeves as separate tubes set into the shoulder, the way the costume is sewn. The torso keeps its own complete surface, and a clavicle bone carries the top of the shoulder.

**Hands that don't connect (fixed).** Each glove tucks 3.5 cm up inside its sleeve end. The sleeve and the glove are weighted by the same function of position along the forearm, so they move as one. In the wing pose the fists follow the forearm instead of being bent 90° at the wrist. v08's flared cuff ring and its halo strands were removed, because at this scale they z-fought with the sleeve.

**Clipping (fixed).**
- Each elbow swings around its shoulder-wrist line to stay clear of the udder cups and torso. The swing is chosen frame by frame from a collision cost and kept continuous with a Viterbi pass, then smoothed around the loop.
- Half-rotation helper joints at the sleeve head and the elbow keep both joints full when they bend.
- The torso just around each sleeve head follows the arm slightly.
- The belly's fullest point was lowered 2.7 cm and the bottom teats angled forward. This gives the teats clearance at rest, matching the dip under the cups in shots 0120 and 0071.

**Light physics (new, baked).** glTF has no live physics, so damped springs are simulated over three loops of the dance and the last loop is baked into the bones. It plays in any glTF viewer and loops seamlessly.
- **Teats:** each teat swings on its own bone and collides with the belly, peaking at about 20° and averaging about 5°.
- **Shag patches:** six spring bones drag the strand tips, with up to about 4 cm of lag at the elbows.
- **Belly and cups:** they jiggle; the cups are kept from sinking into the belly.

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

The Chicken Dance runs 3 s per phase, with four moves in each:
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
python render_dance.py   ../build/rigged.pkl video ../reviews/Chicken_Dance_v10.mp4
python compare_v09.py <handoff>/project/dist/assets/cow-dance-test.glb \
                      <handoff>/project/dist/assets/dance-matrices.bin ../reviews/v09_same_metrics.json
```

Add `--quick` to `build_v10.py` for a half-resolution build that takes about 2.5 minutes. The full build takes about 6 minutes; most of that time goes to solving the elbow paths and simulating the physics. Proportions live in `design.py` as signed-distance primitives. Shag patch and spot placement is in `textures.py`, skin weights are in `rig.py`, and the choreography is in `anim.py`.

The web copies in `viewer/` were made with gltfpack 0.22:
- `cow-meshopt.glb` uses `-cc -kn -km -ke` (full detail).
- `cow-plain.glb` uses `-kn -km -ke -si 0.4` (a simplified fallback). The page also accepts base64 copies (`cow-meshopt.b64.txt`, `cow-plain.b64.txt`) for hosts that only serve text; make them with `base64 -w0`.

To view them locally, run `python3 -m http.server` inside `viewer/` and open the page. three.js loads from the jsDelivr CDN.

## Known limits

- The proportions come from photos at an assumed 1.6 m height. Nothing was measured from the costume.
- The side-jaw photo projection on the mask is still stretched in pure side views, as in v09.
- The black shag is a texture plus a few strand clumps, not a simulated groom.
- The physics is baked springs, not live simulation. Only the teats collide with anything (the belly).
- There's no cloth simulation. The suit deforms by skinning only.
- The elbow stretch noted above remains.
