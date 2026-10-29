# The Misanthropic Cow — Hoof Gloves 3D Model: Project Handoff

**Prepared:** 28 October 2026 · **Owner:** the user (character creator of *The Misanthropic Cow*)
**Read this first.** It is written so a fresh assistant (or person) can pick up exactly where this session stopped.
Process: `3D_Model_Pipeline_PLAYBOOK` (the slipper project's playbook). This project is a second worked example.

**Handoff parts** (each under 29 MB so it can be attached to a chat): **Part 1 CONTEXT** (this file, status, renders,
references, prompt kits, tiles, scripts) · **Part 2 FINAL_GLB** (`Glove_pair.glb`) · **Part 3 BLEND_BAKED** (baked
.blend + `textures/`) · **Part 4 BLENDS_LIVE** (live-material .blend and its displacement variant + `textures/`) ·
**Part 5 SOURCES** (the cleaned, split full-detail mesh). Start with Part 1.
Everything except Part 5 is also in the repo folder `Misanthropic_Cow_Gloves/`.

---

## 1. Goal

A clean, animatable 3D model of the character's **costume gloves** (a pair), from the real prop (now gone).
Tools as for the slippers: ChatGPT for images, Tripo AI multiview for the base mesh, Blender (`bpy`) for the rest.

**Current status: DONE (v4 = v2 "slipper look" with the terry smoothed at 20 mm).** Optional polish in section 8.

---

## 2. The real glove (ground truth — see `01_references/DESIGN_KEY.png`)

| # | Part | Notes |
|---|---|---|
| 1 | Cream looped **terry** mitten | Like a towel / fluffy sock. Plain, no fur cuff (the white fur in the photos is the bodysuit sleeve). |
| 2 | Separate **thumb** | Terry only, **no hoof**. |
| 3 | Fingers in **two compartments** | Index+middle, ring+little. |
| 4 | Black **cloven hoof** | Two hard painted-cardboard caps glued onto the two finger pairs. Closed: straight cleft, tips meet. |
| 5 | **Long brush strokes** | Satin black paint with grey drag streaks, strokes running base to tip. Thin raised rim along the edges. |
| 6 | Straight paint edge | The caps start at a clean straight cut. |
| 7 | Plain closed cuff | (Kept closed on the model: the fur sleeve covers it.) |

**Movement (user's spec):** the glove parts like a Vulcan salute, between the middle and ring fingers, from the finger
web; the caps move with their finger pairs (they were glued on).

**Measured size** (`01_references/SCALE_measured_on_photo2.jpg`, `scripts/measure_scale.py`): 24.7 cm cuff to hoof tip,
toe caps 8.3–9.4 cm, thumb ~4.5–5 cm, hand ~8–9 cm wide worn. Method: sphere fits to the bead eyes of the mask scan
(`01_references/scale_sources/cowMask1.stl`, mm; 56.9 mm apart) + the overhead photo's EXIF lens (Nikon D800, 24 mm,
proven to be the same frame by template match) → camera height → per-height scale. Cross-checks: beads 22.7 vs 23 mm;
the mat comes out 598 mm (a 24 in cutting mat). ±5 %.

---

## 3. What happened (short history — so mistakes aren't repeated)

1. **References** (`prep_refs_gloves.py`): rembg `birefnet-general` cut-outs. `isnet-general-use` failed on cream terry
   (it kept only the black hooves). Run one cut-out per process (birefnet ran out of 16 GB memory when several shared one).
   A lilac ribbon over the hoof was **inpainted before** segmenting; masking it out afterwards cut a false notch.
2. **ChatGPT views** (`02_chatgpt_kit/`): front (edited from the flat-lay photo), little-finger side, thumb side — all
   approved on the first try; palm = mirrored front. The hoof was asked for CLOSED on purpose (splitting is done in 3D).
3. **Tripo slots:** the first kit had Left/Right swapped. Convention (as for the slippers): **Left = the object's own
   left** = the side on the viewer's right in the front view (here the thumb side). The model came out untwisted.
4. **Tripo v1** (`04_tripo_v1_evaluation/`): 1.86 M triangles, watertight after welding, silhouette vs inputs IoU
   0.92–0.94, hoof 37 % of the length (real 36 %). Problems: metallic 0.92 on the hoof (→ 0); **bead-like bumps invented
   along the side seams and cuff** (where Tripo fused its front and back views); closed flat cuff; toes fused (cleft groove
   only 6–9 mm deep each side of a 50 mm hoof).
5. **Seam beads** flattened (`flatten_seams.py`): feathered band where the broad surface faces sideways, terry only (the
   hoof's real beaded rim kept), 2 passes, max move 1.4 mm.
6. **Split, first attempt (superseded):** hooves only, pivot at the hoof base. The user corrected it: the caps were glued
   on, so the whole finger pair moves. **Final split** (`fit_hoof_planes.py` → `bl_split_fingers.py`): base plane through
   the paint edge (64.6 % height, 6.9° tilt), cleft plane through the groove bottom, web plane 20 mm below the base (where
   the modelled crease fades). Lessons: a palm "stub" reaching into the fingers folded in the deep crease and poked out
   (now no stub — the toes swing *into* the palm when they spread); the web cut must skip the thumb (its tip rises above
   the web plane); call `view_layer.update()` before parenting or the children land offset by the parent's origin.
7. **Optimisation** (`06_optimise_uv_bake/`): 100k triangles per glove (palm 60k, toes 20k each); silhouette change
   0.06 % (150k and 64k also tested).
8. **UVs:** plain smart-project gave ~1,800 islands; ~1.5 % of faces sat in 1–4-face islands smaller than a texel and
   baked as **black/white specks**. Fix (`bl_unwrap_parts.py`): smart-project on smoothed proxies only proposes charts,
   islands under 40 faces are merged into neighbours, seams between charts, angle-based unwrap → 64 islands, 64 % coverage.
9. **Bakes:** coplanar cut walls bake badly (grey, glassy) → painted into the maps directly. Cap edges marked sharp so no
   shading line shows where palm and toes meet. Tripo's roughness map did not survive the OBJ import.
10. **v1 delivery** (`07_deliverables_v1/`, superseded): Tripo's own texture, cleaned (playbook route 9a).
11. **v2 "slipper look"** (route 9c, current final): ChatGPT tiles for terry and for the hoof paint with long vertical
    strokes (swatches rotated so strokes run base to tip). Regions from geometry, not colour: paint = finger-pair texels
    above the hoof base plane. Paint darkened (gamma 1.3; it read charcoal). AO normalised (open surfaces = 1) and used at
    50 % (at 60 % un-normalised it greyed the terry by ~20 %). Terry warmed slightly (blue ×0.95).
12. **Terry smoothing, v3 → v4** (user: "the glove looks a tad too lumpy"): Tripo's terry surface was bumpy
    (lumps of a few mm all over the palm, thumb and cuff, deep pits on the finger compartments just above the web).
    `smooth_terry_unsplit.py` low-passes the whole high-poly glove **before the split** (between steps 6 and 7 of
    section 6): result 2·S(V) − S(S(V)) with S = Laplacian diffusion over the radius, so lumps go but the shape keeps
    its size; the painted hoof (above the paint edge, 1–4 mm feather) and the closed cuff bottom are pinned.
    v3 used 10 mm (terry moved 0.45 mm mean, max 2.4 mm; broad folds kept). The user pointed out that the folds are
    Tripo's guesses too; 10/20/30 mm were compared in clay (`05_cleanup_and_split/terry_smoothing_10_20_30mm_clay.jpg`)
    and **20 mm was chosen (v4, current final)**: terry moved 0.9 mm mean, max 5.7 mm; most folds gone, proportions
    kept (width incl. thumb 11.8 cm vs 12.0). 30 mm (1.6 / 9.7 mm) slimmed the thumb and made the cuff edge wobble
    (pinned bottom vs sides moving in). The crease between the finger compartments and the hoof are unchanged. Then
    everything from the split on was re-run (v4: 76 UV islands, 64 % coverage). Lesson: smoothing
    the already split parts (`scripts/superseded/bl_smooth_terry.py`) has to pin the cut walls at the web, so the
    pits right above the web survive; smooth before splitting. Before/after: `09_final/renders/before_after_terry_smoothing.jpg`,
    clay: `05_cleanup_and_split/terry_smoothing_clay_before_after.jpg`.
13. **White specks on the hoof (fixed in v4):** two causes. (a) Bake margins: the parts were baked one after another
    into ONE image, so a later part's 16 px margin overwrote an earlier part's texels wherever islands sit close (v4's
    layout put a ring-little terry island ~20 px from the index-middle hoof island → cream patches on the hoof). Now
    every bake (`bl_bake_parts.py`, `bl_bake_geom_parts.py`, `bl_glove_material.py`) bakes each part into a cleared
    image, keeps only the texels that part's own UV faces cover, and adds the margin once at the end
    (`scripts/bake_atlas.py`). (b) The ChatGPT paint tile had ~290 small cream lint flecks; `prep_tiles_glove.py` now
    inpaints isolated bright dots (> 100 above a 7 px median), keeping the grey drag streaks; seam unchanged.
14. **Terry displacement (optional, Cycles renders):** `Glove_pair_live_displace.blend` turns the terry loops into
    real geometry so the outline is fuzzy and loops cast tiny shadows (bump alone keeps the outline smooth). Simple-type
    adaptive subdivision (shape not rounded), micro-polygons 0.3 mm on the object, terry height map displaced 1.2 mm
    (full range), softened by 0.12 mm first. Tried and rejected: 1 px screen-space dicing (a 3 cm close-up ran out of
    16 GB); the raw height at 1.5 mm (detail finer than the micro-polygons became spikes: burr-like outline, dark
    slivers); softening 0.3 mm (about the loop size: patchy nubs). Mask (`bl_make_displace_mask.py`): terry only, 0 on
    the hoof and the cut walls, fading in over 3 mm (3D distance) from the wall edges so the palm and toes, which project
    the tile from different origins, still meet exactly; islands padded so UV seams don't dip. Comparison:
    `09_final/renders/terry_bump_vs_displacement.jpg` (A bump, B raw 1.5 mm, C softened 0.3 mm, D = delivered).

---

## 4. The final deliverable (v4)

| File (`09_final/`) | What it is |
|---|---|
| `glb/Glove_pair.glb` (15.0 MB) | Both gloves, baked 4K maps (JPEG): base colour (AO included), roughness, tangent normal (OpenGL/Blender convention), metallic 0. Right glove = the same meshes on mirrored nodes. |
| `blend_baked/Glove_pair_baked.blend` + `textures/` | The same, in Blender, textures external and relative. |
| `blend_live/Glove_pair_live.blend` + `textures/` | The **live** material `Glove_Terry_Hoof_live`: tiles at full resolution, mask-driven. Best for renders/edits. Keep `textures/` next to the .blend. |
| `blend_live/Glove_pair_live_displace.blend` | Same, plus **true displacement** of the terry loops (Cycles only; fuzzy outline, real loop shadows). ~1.6 M micro-triangles per glove at render time, ~6 GB peak memory and slower to render than the bump version (four 800 px close-ups at 32 samples: ~2.3 min on CPU). Viewport and EEVEE show the plain mesh. Uses `textures/displace_mask.png` and `height_terry_displace.png`. |
| `renders/` | Final pair (also with displacement), close-ups (hoof strokes, terry, spread), live-vs-baked check, region map, before/after the terry smoothing, bump vs displacement. |

**Specs**
- Objects per glove: `Glove_L_Palm` (root; palm, thumb, cuff) with children `Glove_L_Toe_IndexMiddle` and
  `Glove_L_Toe_RingLittle` (each = terry finger compartment + hoof cap). Same for `Glove_R_*`.
- **Animate:** rotate a toe about its **local Y** to spread (Vulcan-salute V), **local X** to curl. Pivot = the
  middle/ring finger web, mid-thickness, **13.9 cm above the cuff** (20 mm below the hoof base).
- 100,000 triangles per glove (palm 60k, each toe 20k). One shared 4K UV atlas for all three parts.
- **Units/axes:** real size in **metres**, 24.7 cm tall. Blender: Z up, back of the hand toward −Y, thumb of the left
  glove toward +X; left glove's cuff centre at x = −0.12 m, right at +0.12 m. glTF: Y up, back of the hand toward +Z.
- **Live material:** tiles box-projected from each part's own object coordinates (terry 4 cm, paint 6 cm), so the strokes
  follow a toe when it moves; `mask_paint.png` (UV, lossless) switches terry → paint; tile height bumped on top of the
  baked detail normal from the full (smoothed) mesh (it carries the hoof's stroke grooves and the broad terry folds); AO multiplied
  at 0.5. Roughness: terry 0.92, paint 0.50 (black) to 0.72 (grey drag streaks).

---

## 5. Known issues / open items

1. **AO was baked with the toes closed.** When spread, the inner walls and the web look slightly darker than lit
   surfaces would. Re-bake AO in the spread pose if a spread pose is the hero shot.
2. **Inner walls are flat** (the real caps were hollow cardboard). At grazing angles they mirror the room and read grey.
3. **Proportions follow the AI views** where no photo shows them: hand thickness 5.3–5.8 cm (estimate was 4–5), the
   hoof's side profile, the palm mirroring the back of the hand.
4. The thumb is part of the palm (not separately animatable). The cuff is closed.
5. The terry tile has a faint mirrored repeat (ChatGPT made it seamless that way); not visible at normal distance.
6. Where the palm meets the toes the meshes are separate; with flat clay shading a hairline can show. Hidden in the
   textured renders.
7. `Glove_pair.glb` uses 4K JPEG maps (15 MB). For real-time use, drop to 2K.
8. Displacement version: the terry fades to flat over 3 mm each side of where the toes meet the palm (so they don't
   crack apart), which reads as a faint smoother band across the knuckle line on a closed glove. A shorter fade
   (`bl_make_displace_mask.py ... 1.5`) narrows it. Displacement is not in the GLB (glTF has no displacement).

---

## 6. How to reproduce / continue (pipeline)

Environment: Linux container, CPU only, 16 GB RAM, Python 3.13.
`pip install bpy==5.2.3 trimesh rtree pymeshlab networkx freetype-py imageio pyglet "PyOpenGL>=3.1.9" scipy opencv-python-headless pillow "rembg[cpu]"`
then `pip install --no-deps pyrender` (its old networkx pin fails to build). `apt-get install libegl1 libgl1 libopengl0 unar`.
`bl_*.py` run with plain `python3`; everything else with `python3 -I`. Blender frame: Z up, back of hand −Y, thumb +X.

1. `prep_refs_gloves.py photos refs [job]` (one job per process) → `design_key_gloves.py refs refs`
2. `kit_content.py` (all prompt text) → `build_kit.py refs out` → `build_page.py out`
3. `normalize_glove_views.py out front.png side_little.png side_thumb.png` (palm = mirrored front)
4. `render_model.py model.obj dir` · `measure_tripo_glove.py model_dir` · `compare_to_views.py model.obj tripo_inputs out.jpg`
5. `bl_import_weld.py model.obj glove_high.blend` → `bl_dump_mesh.py glove_high.blend Glove_HIGH high.npz basecolor.jpg`
6. `flatten_seams.py high.npz flat.npz 2` → `fit_hoof_planes.py high.npz flat.npz planes.json`
   → `smooth_terry_unsplit.py high.npz flat.npz planes.json smooth.npz 20` (terry smoothing radius, mm; v4 = 20)
7. `bl_split_fingers.py glove_high.blend smooth.npz planes.json split.blend 20 0` (web drop mm, palm stub mm)
8. `bl_optimize_parts.py split.blend work.blend low.glb 60000 20000 high.glb` · `compare_glove_lods.py`
9. `bl_unwrap_parts.py work.blend planes.json 66 uv.png` (keep a copy: the pre-bake file names the cap materials)
10. `bl_bake_parts.py work.blend bake_dir 4096 2` → `bl_fix_cap_texels.py work_uv.blend planes.json maps_dir`
11. `bl_bake_geom_parts.py work_uv.blend geom 4096` → `make_masks_glove.py geom planes.json masks 4096`
12. `prep_tiles_glove.py raw_tiles tiles`
13. `bl_glove_material.py work.blend tiles mask_paint.png glove_normal.jpg out 2048 12 ao_only` → denoise (2× bilateral),
    normalise (÷ 90th percentile), upscale to 4K, gamma 0.8 → `bl_glove_material.py ... out 4096 4 ao_4096.png`
14. `bl_export_pair.py work.blend maps out 24.7` (real size, mirrored right glove, GLB + baked .blend)
15. `bl_glove_material.py Glove_pair.blend ... live:ao_4096.png` → `bl_lean_live.py Glove_live.blend out Glove_pair_live.blend`
16. Displacement variant: `bl_make_displace_mask.py work_uv.blend geom mask_paint.png displace_mask.png 3` →
    `bl_terry_displace.py Glove_pair_live.blend displace_mask.png Glove_pair_live_displace.blend 1.2 mm:0.3 0.12`
    (height mm, dicing, softening mm); check with `bl_render_displace_check.py`.
17. Checks: `bl_render_pair.py`, `bl_render_live.py`, `bl_preview_baked.py`, `glb_check_hierarchy.py`; surface shape
    without textures: `bl_clay.py work.blend out_prefix` (whole glove) and `bl_clay_web.py work.blend out.png` (web close-ups).

Bake timings (CPU, 4K): selected-to-active colour/normal/roughness ~50–60 s each at 2 samples; final material bakes
~85 s each at 4 samples; AO 2K/12 samples ~50 s. 1.86 M-triangle `trimesh.split()` runs out of memory — use the
scipy connected-components count in `measure_tripo_glove.py`.

---

## 7. Package contents

- **Part 1 CONTEXT:** this file, `PROJECT_STATUS.md`, `01_references/` (design key, cut-outs, details, scale image and
  `scale_sources/` incl. the mask scan `cowMask1.stl`, mm), `02_chatgpt_kit/` (guide page; the step zips are left out —
  rebuild them with `build_kit.py`), `02_approved_views/`, `03_tripo_inputs/`, `04_tripo_v1_evaluation/`,
  `05_cleanup_and_split/`, `06_optimise_uv_bake/`, `08_fabric_tiles/` (raw ChatGPT tiles; the prepared ones are in
  Part 4's `blend_live/textures/` or rebuild with `prep_tiles_glove.py`), `09_final/renders/`, `scripts/`.
- **Part 2 FINAL_GLB:** `Glove_pair.glb`.
- **Part 3 BLEND_BAKED:** `blend_baked/` with its `textures/`.
- **Part 4 BLENDS_LIVE:** `blend_live/` (live and displacement .blend files) with its `textures/`.
- **Part 5 SOURCES:** `high_full.glb` — the cleaned (seam beads flattened, terry smoothed), split full-detail parts
  (`Glove_Palm_HIGH`, `Toe_*_HIGH`, model units: 0.97 tall), for re-baking.
- Not included (with the user, too large): the Tripo download `furry_glove_3d_model` (OBJ 186 MB + maps).

---

## 8. Suggested next steps (pick any)

- Place on the character: parent each `Glove_*_Palm` to the forearm/hand bone; key the toes' local Y/X rotations.
- Re-bake AO in a spread pose for spread hero shots (issue 1).
- Real-time LOD: 2K maps, 50k triangles per glove (re-run step 8 with lower budgets, then 9–14).
- Hollow the cuff if an arm must go inside.
- More or less terry smoothing: re-run `smooth_terry_unsplit.py` with another radius (10 mm keeps Tripo's folds, 30 mm
  removes them but slims the thumb; protect the thumb and let the cuff bottom move in if you go that far),
  then steps 7–17.
