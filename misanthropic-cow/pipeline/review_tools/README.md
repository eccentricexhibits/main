# Review and build tools (rounds 19–24)

The tools used to build and check rounds 19–24, the static Tripo-based body that does not have a rig yet. Run them from `pipeline/`, passing `.` as the pipeline directory.

| Tool | What it does |
|---|---|
| `build_static.py` | Builds the static model, with no rig or animations. This is the build behind rounds 19–24. `COW_ARM_RAISE=70` gives the arms-raised pose, and `COW_MARKINGS_CACHE` shares the markings between the two poses. Run it with `--quick` for a half-resolution build of about 2 minutes; the full build takes about 12 minutes. |
| `pair_sheet.py` | Puts each model view beside the matching approved Gemini view (front, left, right and back) at the image's own scale, with a silhouette overlay. |
| `spot_cmp.py` | Overlays the leggings' white spots on Gemini's, view by view: green for both, red for the model only and blue for Gemini only. |
| `head_cmp.py` | Shows any region of a view beside the same region of the Gemini view, for example the head, waist or udders. |
| `problems.py` | Renders six fixed close-ups: head, lower torso and lower legs, each from the front and side. |
| `profile_cmp.py` | Prints the silhouette extents per height for the model and for Gemini. |
| `sdf_vs_gemini.py` | Draws the outlines of the design's SDF parts on the Gemini views without meshing, for fast shape checks. |
| `gemini_measure.py` | Measures the approved views in model metres: floor at 0, crotch at 0.747 m, horn tip at 1.696 m. |
| `rig_bench.py` | Round 38: `build_v10.py` in separate steps that each save their result, so a run that is stopped can carry on where it was: `assemble` (the model with skin weights), `bake` (any clips), `validate` (`validate.py` per clip), `glb` (the rigged GLB), `rigged` (the `rigged.pkl` that `render_dance.py` reads), `sheet` (clip sheets) and `pose` (frames straight from the pose solver, without the springs, for quick weight and pose checks). It builds the round 37 body, since `design.BODY_SOURCE` is `'tripo'`. |
| `test_viewer.js` | Runs a headless Chromium (SwiftShader) test of the viewer. Under SwiftShader it takes 30–45 minutes. It covers opening on the newest round with Idle selected, picking rounds 17, 18 and 25 together, side by side and overlaid, the Chicken Dance's own controls, Arms raised, every lighting rig and the backdrops. |

Example:

```bash
cd pipeline
REBUILD=../../Rebuild_Inputs/project COW_MARKINGS_CACHE=/tmp/marks.pkl python review_tools/build_static.py . ../build/r24.glb
REBUILD=../../Rebuild_Inputs/project COW_MARKINGS_CACHE=/tmp/marks.pkl COW_ARM_RAISE=70 python review_tools/build_static.py . ../build/r24_arms_raised.glb
python review_tools/pair_sheet.py . ../build/r24.glb ../references/approved_views pairs.jpg "Round 24"
```

`pair_sheet.py`, `spot_cmp.py` and `head_cmp.py` take the Gemini views under their original file names. In the handoff package these are in `Reference_Photos/approved_gemini_views`. Otherwise, make a folder from `references/approved_views` with:
- `1_FRONT_approved.png`, a copy of `front.png`;
- `2_BACK_approved.png`, a copy of `back.png`;
- `3_SIDE_facing_left_approved.png`, a copy of `left.png`;
- `Gemini_Generated_Image_f4u2n8f4u2n8f4u2.jpg`, a copy of `right.jpg`.
