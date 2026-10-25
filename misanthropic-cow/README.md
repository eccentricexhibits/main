# The Misanthropic Cow, v10

v10 rebuilds the body and the rig of the 3D Misanthropic Cow. The body follows the proportions from the original 2012 Hasselblad shoot. The rig fixes the Chicken Dance problems in v09: the "wings" that grew under the armpits, and the hands that came loose from the sleeves.

| File | What it is |
|---|---|
| `models/Misanthropic_Cow_v10.glb` | Static master. 659k triangles, real-world scale in metres, all textures embedded. |
| `models/Misanthropic_Cow_v10_ChickenDance.glb` | Same model with a 26-joint skin and the 12-second Chicken Dance (30 fps). |
| `reviews/` | Turntable and close-up renders, the before/after sheet, the pose review sheet, the dance video and the validation JSON. |
| `viewer/` | A three.js web viewer that plays the dance, with camera presets and a clay toggle. |
| `pipeline/` | The Python sources that generate everything above. |

Both GLBs pass the Khronos glTF Validator with 0 errors and 0 warnings.

## What changed from v09

**Proportions.** The proportions were measured from the 2012 shoot photos:
- belly width is about 2× the mask width;
- muzzle-to-crotch is about 3 mask heights;
- the crotch is at 46 % of standing height.

The wearer is built at about 1.60 m. v09 had scaled the whole figure to fit an oversized mask, which gave it broad, square shoulders and a short barrel torso. v10 instead scales the scanned mask to 0.75 (about 0.21 m wide). The body has narrow, sloped shoulders and a long, round padded belly that hangs to the crotch. Pink satin panties show under the belly, as in shots 0077, 0120 and 0191.

**Head.** The scanned mask, its photo textures and the horns are kept from v09. The mask now sits recessed in the opening of a fur hood. The hood narrows above the brow, as in the photos, and has a crown tuft. Each horn is slid along its own axis until its root is buried in the hood. The rectangular crown block from v09 is gone. The mask photo gets a mild brightness lift; the weathered grey wash on the mask is real and is kept.

**Udder, shag and leggings.**
- The udder is two large, soft pink cups. Each has one teat hanging forward over the belly and one pointing out and down.
- Long black shag strands follow the patch layout in the photos:
  - upper chest and shoulder on the wearer's right;
  - low belly;
  - both elbows;
  - upper back right and lower back left.
- The leggings use smaller, irregular painted white spots.
- The hoof caps are glossy black, as in every photo. v08 had them mid grey-teal.

**Wings under the armpits (fixed).** v09 split the arm from the torso with x-coordinate thresholds. Raising the elbows dragged a strip of torso flank along with the upper arm. v10 builds the sleeves as separate tubes set into the shoulder, the way the costume is sewn. The torso keeps its own complete surface, and a clavicle bone carries the top of the shoulder.

**Hands that don't connect (fixed).** Each glove tucks 3.5 cm up inside its sleeve end. The sleeve and the glove are weighted by the same function of position along the forearm, so they move as one. In the wing pose the fists follow the forearm instead of being bent 90° at the wrist. v08's flared cuff ring and its halo strands were removed, because at this scale they z-fought with the sleeve.

## Measured over the dance

| Check | v09 | v10 |
|---|---|---|
| Torso edge stretch, 99.9th percentile, worst frame | 4.08× | 1.40× |
| Sleeve edge stretch, 99.9th percentile, worst frame | 12.85× | 2.95× |
| Sleeve end to glove distance, at rest and at the worst frame | not measured | 16.0 mm and 16.1 mm |
| Glove into body, 99.5th percentile | not measured | 0 mm in all four phases |
| Clap contact gap | not measured | 0.3 mm |
| Loop seam error | 0 | 0 |
| Planted-foot drift | ~0 | 0.05 mm |

Most of the remaining sleeve stretch is on the outside of the elbow at the top of each wing flap. That is the usual limit of linear-blend skinning on a sharply bent elbow. The full numbers are in `reviews/validation_v10.json`. `reviews/v09_same_metrics.json` has the same metric run on the v09 rig.

## The rig

There are 26 joints:
- **Spine and head:** Hips, Spine, Belly, Chest, Neck, Head.
- **Each side:** Shoulder (clavicle), UpperArm, Forearm, Hand, HoofFingers, Thumb, Thigh, Shin and Foot.
- **Udder:** one Udder bone per cup.

Belly and udder bones get a damped-spring jiggle that is baked into the animation. Bind rotations are identity, and all inverse bind matrices are translations.

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
python render_reviews.py ../build/rigged.pkl ../reviews <geometry-v09.glb> <shoot photos...>
python render_dance.py   ../build/rigged.pkl video ../reviews/Chicken_Dance_v10.mp4
python compare_v09.py <handoff>/project/dist/assets/cow-dance-test.glb \
                      <handoff>/project/dist/assets/dance-matrices.bin ../reviews/v09_same_metrics.json
```

Add `--quick` to `build_v10.py` for a half-resolution build that takes about 45 s. Proportions live in `design.py` as signed-distance primitives. Shag patch and spot placement is in `textures.py`, skin weights are in `rig.py`, and the choreography is in `anim.py`.

The web copies in `viewer/` were made with gltfpack 0.22:
- `cow-meshopt.glb` uses `-cc -kn -km -ke` (full detail).
- `cow-plain.glb` uses `-kn -km -ke -si 0.45` (a simplified fallback).

To view them locally, run `python3 -m http.server` inside `viewer/` and open the page. three.js loads from the jsDelivr CDN.

## Known limits

- The proportions come from photos at an assumed 1.6 m height. Nothing was measured from the costume.
- The side-jaw photo projection on the mask is still stretched in pure side views, as in v09.
- The black shag is ribbon strands, not a simulated groom.
- There's no cloth simulation. The suit deforms by skinning only.
- The elbow stretch noted above remains.
