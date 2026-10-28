# The Misanthropic Cow: Hoof Gloves 3D Model, Project Status

**Status: DONE (v2). Full handoff: `HANDOFF_gloves.md`.**

Process: `3D_Model_Pipeline_PLAYBOOK` (photos → ChatGPT multiview → Tripo → cleanup in Blender `bpy`).
Worked example followed: the Misanthropic Cow slippers.

## Decisions (from intake, 28 Oct 2026)

| Question | Answer |
|---|---|
| Route | No re-shoot. AI multiview from the existing 16 photos (playbook stages 2–5). |
| Pose | Worn (filled), fingers straight, hoof **closed**. |
| Hoof parts | **Both hoof toes kept as separate objects** so they can be animated individually. Mitten body = one mesh. No armature. |
| Hoof finish | Satin black with grey brush-streak wear (studio photos), not the glossy green-black of the "Alt Image". |
| Pair | Model the LEFT glove; the right glove is the mirror (X scale −1). |

## Ground truth (see `01_references/DESIGN_KEY.png`)

Cream looped-terry mitten with a separate terry thumb (no hoof on it). The four fingers sit in two
compartments, each capped by a hard black toe cap: together a cloven hoof. Closed, the toes meet along a
straight cleft and their tips meet in one point. Thin raised rim on the toe edges. Plain open cuff, no fur
(the white fur in the photos is the bodysuit sleeve).

## Real-world size (measured, ±5 %)

From the mask scan (`01_references/scale_sources/cowMask1.stl`, mm) and the overhead photo of the gloves beside
the mask (`gloves_with_mask_2.jpg`); see `01_references/SCALE_measured_on_photo2.jpg` and `scripts/measure_scale.py`.

| | Left-hand glove | Right-hand glove |
|---|---|---|
| Cuff → hoof tip | 24.7 cm | 24.7 cm |
| Terry, cuff → hoof base | 15.8 cm | 16.0 cm |
| Hoof toe caps (base → tip) | 8.5 / 9.0 cm | 9.4 / 8.3 cm |
| Width at the wrist, laid flat | ~8 cm | ~8.6 cm |

Thumb ≈ 4.5–5 cm. Hoof ≈ 36 % of the length. The empty gloves lie flat, so the widths are half-circumferences;
worn they are narrower (~8–9 cm) and ~4–5 cm thick.

How: sphere fits to the scan's bead eyes give 56.9 mm centre to centre. Photo 2 is the same Nikon D800 / 24 mm
frame as the EXIF-tagged flat-lay photo, so the eye beads' pixel spacing gives the camera height (~44 cm above
the mat), and each part is scaled at its own height. Cross-checks: the beads measure 22.7 mm in the photo vs
23 mm in the scan, and the mat comes out 598 mm wide (a standard 24 in / 610 mm cutting mat).

## Estimated, not measured

- Side profile of the hoof (slim wedge as thick as the hand, tapering to the tip): no photo shows it
  straight on. It is an assumption; check it in Step 1 of the kit.
- Palm side assumed to mirror the back of the hand (true for a sewn mitten).

## Stage tracker

| Stage | Status |
|---|---|
| 0 Intake | done |
| 1 References, design key, brief | done: `01_references/`, `01_design_brief.md`; real size measured (see above) |
| 2 ChatGPT multiview kit | done: `02_chatgpt_kit/` (5 step zips + fix-ups). Guide page with copy buttons is published as a private artifact. **User runs Steps 1–5.** |
| 2b Approved views | done: `02_approved_views/` (front, little-finger side, thumb side; all round 1, no fixes needed). Hoof 35–36 % of the height in all three; side views mirror each other (silhouette IoU 0.80, the thumb accounts for most of the difference). |
| 3 Normalise Tripo inputs | done: `03_tripo_inputs/` (palm view = mirrored front). Slots: Left = thumb side (the object's own left, same convention as the slippers), Right = little-finger side. |
| 4 Evaluate Tripo model | done: `04_tripo_v1_evaluation/`. Tripo v1 = `furry_glove_3d_model` (OBJ 186 MB, kept with the user; too big for the repo). 1.86 M triangles, one connected piece, no twist. Silhouette vs input views IoU 0.92–0.94. Hoof 37 % of length (real 36 %), wrist 8.3–8.9 cm, hand 5.3–5.8 cm thick (estimate was 4–5). Problems: metallic 0.92 on the hoof (must be 0); bead-like bumps down both side seams of the terry (invented, flatten); cuff is a closed flat cap; hoof toes fused (cleft groove only 6–9 mm deep each side of a 50 mm hoof). Scale: model is 0.972 units tall → 1 unit ≈ 25.4 cm. User approved v1 (cuff stays closed, thickness as is). |
| 6 Cleanup + split | done (high-poly), `05_cleanup_and_split/`. Mesh is watertight after welding. Side-seam and cuff beads flattened (`flatten_seams.py`: feathered band where the broad surface faces sideways, terry only, 2 passes, max move 1.4 mm). Metallic 0. Split (`fit_hoof_planes.py` → `bl_split_fingers.py`), revised after user feedback: the real hooves were glued onto the finger pairs, so each moving part is a finger pair (terry compartment + hoof cap) that parts from the middle/ring web like a Vulcan salute. Planes: hoof base through the paint edge (64.6 % height, 6.9° tilt, 4 mm residual); cleft through the groove bottom (2.9 mm residual); web plane parallel to the base, 20 mm below it, where the modelled crease under the cleft fades out. Parts: `Glove_Palm` (palm, thumb, cuff; cut flat at the web, thumb left whole), `Toe_IndexMiddle` (+X, 11.1 cm) and `Toe_RingLittle` (−X, 10.8 cm): closed solids, flat inner walls (paint above the hoof base, terry below), pivot on the web at mid-thickness (13.9 cm above the cuff), parented to the palm. Spread = local Y, curl = local X. Test file `Glove_L_split_test_lowres.glb`. (First attempt, hooves only with the pivot at the hoof base: `scripts/superseded/bl_split_hoof.py`.) **Waiting for the user's OK on the split before optimising/texturing.** |
| 5 Round 2 if needed | – |
| 6 Cleanup + split hoof toes into separate objects with knuckle pivots | – |
| 7 Optimise | done: `06_optimise_uv_bake/`. 100k triangles per glove (palm 60k, each toe 20k): silhouette mismatch 0.06 %, shading difference 3.0/255 vs the full mesh (150k and 64k also tested). `bl_optimize_parts.py`, `compare_glove_lods.py`. |
| 8 UVs + bakes | done. One shared 4K atlas for the three parts (64 islands, 63.9 % coverage; `bl_unwrap_parts.py`), colour + tangent normal baked from the full mesh (`bl_bake_parts.py`), cap-edge sharp edges, cut walls painted into the maps (`bl_fix_cap_texels.py`), roughness derived from colour. |
| v1 delivery | `07_deliverables_v1/`: `Glove_pair.glb` (6.3 MB, both gloves, right = mirrored node sharing the meshes), `Glove_L.glb`, `Glove_pair.blend` + `textures/` (relative paths, moved-copy tested). Real size: 24.7 cm tall, metres, Z-up in Blender; left cuff at x −0.12 m, right at +0.12 m; toe pivots 13.9 cm above the cuff. Surface = Tripo's own texture, cleaned (playbook route 9a). |
| 9 Surface | done (slipper look, 9c). Tiles `08_fabric_tiles/` (raw + prepared), live material `bl_glove_material.py` (tiles in each part's own coordinates; strokes follow the toes), AO normalised ×0.5, final 4K bakes. Live vs baked match (`09_final/renders/check_live_top_vs_baked_bottom.jpg`). |
| 10–11 Deliver + handoff | done: `09_final/` (GLB pair 14.5 MB, baked .blend, live .blend, renders) and `HANDOFF_gloves.md`. Handoff parts (each < 29 MB) sent as zips in the chat. `07_deliverables_v1/` is superseded. |
| 10–11 Deliver pair, package for handoff (<29 MB per file) | – |

## Plan for the separate hoof toes (stage 6)

Tripo returns one fused mesh. After cleanup: segment the black hoof by baked colour plus position, cut it
off the mitten, split it at the cleft into two toe objects, give each a thickness and an open back, and set
each pivot at its knuckle line. The mitten's finger ends are closed under the caps so nothing is hollow when
a toe rotates. If Tripo's hoof geometry is poor, rebuild the two caps in Blender, fitted to Tripo's
silhouette (they are simple rigid shells).

## Files

- `01_references/`: white-background cut-outs (`REF_A–C`), detail crops (`DETAIL_1–5`), `DESIGN_KEY.png`
- `01_design_brief.md`: the brief pasted into every prompt
- `02_chatgpt_kit/`: one zip per step (PROMPT.txt + images numbered in attach order), `FIX_UP_PROMPTS.zip`,
  `guide_page.html` (offline copy of the guide)
- `scripts/`: `prep_refs_gloves.py` (rembg `birefnet-general` cut-outs; run one job per process, see the
  docstring), `design_key_gloves.py`, `kit_content.py` (all prompt text), `build_kit.py`, `build_page.py`
