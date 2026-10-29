# The Misanthropic Cow: full-body 3D model

Follows `3D_Model_Pipeline_PLAYBOOK` (the slipper project's playbook). This folder holds stages 0–2: reference prep, design key, brief and the ChatGPT four-view kit.

## Decisions (Stage 0 intake)

| Question | Answer |
|---|---|
| Re-shoot the real costume? | No. The AI route uses only the existing 92 photos. |
| Beige briefs part of the look? | Yes. They're worn over the spotted leggings. |
| Feet | Slippers drawn into the images, so Tripo models them with the body. |
| Use / pose | Rigged and animated, so the views use an **A-pose** (arms ~45° out, clear of the belly). |
| Body proportions | From the **original photo shoot** wearer (`Original Cow Photo Shoot (Proper Body Proportions)`). |

## How the proportions were fixed

No photo shows the whole costume uncovered on the original wearer. `reference/PROPORTION_BASE_original_wearer.png` combines two shots from that session:
- **Body:** shot 4 of 8, standing, front on.
- **Head:** shot 3 of 8, which uses the same camera distance and backdrop.

Each was cut out against a fitted backdrop colour model (GrabCut) and white-balanced on the white fur. The head was scaled ×0.91 so the udder-cup widths match, then aligned on the top and centre of the cups. The raised arms were removed. ChatGPT redraws them in an A-pose.

Measured on that composite, as fractions of floor-to-horn-tip height (all estimated from photos, not measured on the costume):

| Landmark | Height | Width |
|---|---|---|
| Horn tips | 100 % | |
| Bottom of the snout, top of the udder cups | ~85 % | head (hood) ~10–11 % |
| Udder cups | 73–85 % | ~25 % together |
| Belly, widest point | ~60 % | ~28 % (the widest part of the body) |
| Fur hem | ~52 % | |
| Crotch (bottom of the briefs) | ~46 % | hips ~22 % |
| Legs | | ~9 % each at the thigh |

## Horns (confirmed by the user)

The horns deliberately don't match:
- **Wearer's right horn:** short, ending in a tuft of twisted bare wire. The wire is intentional.
- **Wearer's left horn:** a long crescent with a pointed tip.

Later photos show the long horn's tip broken off. That's damage, so the horns are drawn from the original shoot (`DETAIL_3`, `DETAIL_3b`).

## Assumptions to confirm

- The thin white cord hanging from the gold bow is the **tail**.
- The black patches follow the original shoot. They shifted between wearers.

## Contents

- `kit/STEP_1 … STEP_5*.zip`: one package per ChatGPT step. Each has a `PROMPT.txt` and the images to attach, numbered in attach order. `STEP_1` also has `README_START_HERE.txt`, and `STEP_5` has `TRIPO_UPLOAD.txt`.
- `kit/FIX_UP_PROMPTS.zip`: fixes for the usual failure modes, plus every detail crop.
- `reference/DESIGN_KEY_check_every_view_against_this.png`: 16 numbered features. Check every generated view against it.
- `DESIGN_BRIEF.md`: the authoritative parts list and NEVER ADD list.
- `scripts/`:
  - `prep_refs_cow.py`: white-balanced, square reference and detail crops.
  - `proportion_base_composite.py`: the composite.
  - `design_key_cow.py` + `design_key_marks.py`: the design key.
  - `kit_content_cow.py`: all prompt text, the single source of truth.
  - `build_kit_cow.py`: builds the zips.

## Rebuild

The photos come from the user's `Full_Cow_Tripo.part1–4.rar` archive, extracted to `<photos>`:

```bash
python3 -I scripts/prep_refs_cow.py <photos> <playbook_dir> refs
python3 -I scripts/proportion_base_composite.py "<photos>/Original Cow Photo Shoot (Proper Body Proportions)" work   # then copy work/PROPORTION_BASE_original_wearer.png into refs/
python3 -I scripts/design_key_cow.py refs refs/DESIGN_KEY_check_every_view_against_this.png
python3 -I scripts/build_kit_cow.py refs out
```

## Next stages (playbook stage numbers)

3. Normalise the four approved views for Tripo.
4. Evaluate the Tripo model: turnaround renders and measurements.
5. Round 2 if needed.

After that: clean-up, decimation, UVs and bakes, and the surface. The surface is probably 9c: material regions plus fabric tiles for the white fur, black shag, pink fleece, beige satin, black leggings and the mask.
