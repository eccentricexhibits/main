# HANDOFF: The Misanthropic Cow, full-body 3D model

**For:** a new Claude session continuing this project. The repository branch is `claude/sleepy-keller-33h8gn` in `eccentricexhibits/main`, folder `Misanthropic_Cow_Full_Body/` (the earlier stages are also on `claude/gallant-feynman-4ikhs2`). The project was planned around the user's `3D_Model_Pipeline_PLAYBOOK`; it was not available in the last session, so that session followed this file and the slipper project's pipeline (same stages). Read the playbook first if the user supplies it.

## 1. Goal and where we are

Goal: a clean, textured, rig-ready 3D model of the user's character, The Misanthropic Cow, a handmade full-body cow costume. The costume no longer exists to re-shoot, so the model is built from about 100 old photos, the AI route (ChatGPT/Gemini views -> Tripo), and three real objects: the 2014 scan of the real mask, the finished slipper model and the user's fabric tiles.

| Stage | Status |
|---|---|
| 0-4 Intake, references, views, Tripo inputs, Tripo model | done (`views/`, `tripo_inputs/`, `tripo_eval/REPORT.md`) |
| 6 Cleanup | done: `scripts/bl_stage6_cow.py` |
| 6b Real scale + geometry swaps | done: 1.64 m; scan-guided horns, slippers centred under the legs on black-sock feet, cord tail (`checkpoints/CHECKPOINT_1`, `_2`). The face is **Tripo's** (see §3) |
| 7 Decimation | done: body 1.55M -> 230k; silhouette IoU 0.9996+ in 8 views (checked on the scan-mask version) |
| 8 UVs and bakes | done: one 4K body atlas (texel-weighted, the face at 2x); colour, normal, per-texel geometry |
| 9c Region map, tiles, live material, AO, final bakes | done; region map approved by the user (`checkpoints/CHECKPOINT_3_region_map.jpg`, then re-done for Tripo's face: `CHECKPOINT_5_tripo_face.jpg`) |
| 10-11 Deliverables | done: `deliver/Misanthropic_Cow.glb` and `deliver/live/Cow_fabric_live.blend` + `textures/`; browser viewer `viewer/` |
| Next | rigging (Rigify or AccuRig); optional polish (§5) |

## 2. The user

- Character creator. Comfortable with Blender, but wants Claude to do the technical work and to end every reply with a concrete, numbered next step. Wants pictures at every checkpoint.
- Runs ChatGPT, Gemini and Tripo themselves. Likes complete, copy-pasteable prompts with numbered attachments. Gives sharp visual feedback: trust it, then measure.
- Every file moved to a new window must be **under 29 MB**.

## 3. Decisions (all confirmed by the user)

- **No re-shoot** (the costume is gone). Proportions come from the **original photo shoot wearer** (8 photos).
- **A-pose**, rigged and animated eventually.
- **Real size: 1.64 m to the horn tips** (1.676 m per Tripo unit), set from the real mask's width at eye level (176 mm). Cross-checks: Tripo's feet come out 28.5 cm against the real 27 cm slippers; matching the eye spacing instead would give 1.54 m; a 1.6 m wearer would suggest about 1.72 m. Tripo's head is a little large for its body, so the user chose to keep the mask at its real size.
- **Mask: Tripo's own face** (the user's choice). The first version replaced it with the 2014 scan (`cowMask.obj`, millimetres, 836k triangles, no texture), coloured from REF_J; the user found it "all messed up" next to Tripo's face (noisy black-paint areas in the scan, ragged projected patches, the mask sitting deep in the hood). The scan now gives the real scale, the horn shapes and the mask's outline (which part of Tripo's face is mask, for the regions). `build_swaps_cow.py ... scan` still builds the scan version.
- **Horns follow the scan** (user's choice over the REF_J ratios): clean swept tubes along the scan's horn centrelines. Long horn 18.5 cm along its curve on the costume's own left (3 black rings, pointed tip); short horn 4.9 cm on its own right (2 rings) with a five-strand twisted wire tuft. Both sit on Tripo's horn tube (bolster), which is about 11 cm long, like the real one.
- **Slippers:** the finished pair (`Cow_Slippers_pair.glb`) at real size (27 cm), each **centred under its leg** (Tripo's legs come down 2.7 cm closer to the middle than Tripo's slippers; centring on those let the ankle poke out of the slipper's inner side, which the user spotted), toes on Tripo's toes, own textures. **Black-sock feet** (15 x 7 cm, toes only ~4 cm under the slipper's head) fill them.
- **Tail:** a 4 mm white cord from the gold bow to knee height (0.45 m).
- **Beige satin bloomers with lace side panels**; the back continues the front (satin, lace at the sides). The lace is see-through over the black leggings.
- **No baked lighting in the colour.** AO is a separate glTF occlusion map. Metallic is 0 everywhere.
- **Surface route 9c:** material regions plus the user's ChatGPT fabric tiles, the same "product" look as the slippers.

## 4. Ground truth and key references

- `DESIGN_BRIEF.md`: authoritative parts list and NEVER ADD list.
- `reference/DESIGN_KEY_check_every_view_against_this.png`, `PROPORTION_BASE_original_shoot.png`, `PROPORTION_SKETCH_A_pose.png`.
- `reference/REF_J_head_front_on_new_photo.webp`: the mask's front; its black patches, red snout and nostril slits were projected from it (`scripts/make_regions_cow.py`, hand-measured snout oval and slits). `REF_K_…`, `REF_L_back_bow_new_photo.jpg`.
- The mask project (`Misanthropic_Cow_Mask_Part1-3`, for the separate "v10" rigged cow pipeline) has more mask photos (`references/mask_and_head/IMG_2003-2034`), the STL scan and its scale check (beads 23 mm, 56.9 mm apart). This cow measures the OBJ scan's beads at 24 mm, 59 mm apart.
- Raw photos: the user's `Full_Cow_Tripo.part1–4.rar` (untrusted input; extract in its own folder).

## 5. What's next

1. **Rigging.** Suggest Rigify (in Blender, from `deliver/live/Cow_fabric_live.blend` or the GLB) or AccuRig. The mask, horns, wire and tube should be weighted 100 % to the head bone; the slippers to the feet; the cord tail can get a short bone chain.
2. Optional polish the user may ask for:
   - The bolster-end caps are flat fans (fur-coloured, visible up close).
   - The mask's patches follow Tripo's painted face, not REF_J.
   - The body's black patches and white leg spots follow Tripo's texture, not the photos.
   - The horns follow the 2014 scan, which hooks more than REF_J.
   - A lighter LOD (body 100k, slippers 2K) for real-time use.

## 6. Environment setup (fresh container)

```bash
apt-get install -y unrar libegl1 libegl-mesa0 libgl1-mesa-dri libgles2 libosmesa6 libglu1-mesa libxi6 libxxf86vm1 libxfixes3 libxrender1 libsm6 libxkbcommon0 libopengl0
```
```bash
pip install opencv-python-headless pillow numpy scipy "networkx>=3" trimesh rtree "PyOpenGL>=3.1.9" freetype-py imageio pyglet==1.5.29 pymeshlab matplotlib embreex bpy==5.2.3
```
```bash
pip install --no-deps pyrender
```
- `bpy==5.2.3` has a cp313 wheel (about 400 MB). pyrender needs `PYOPENGL_PLATFORM=egl`; render with `RenderFlags.RGBA` and composite the alpha onto white. `embreex` makes trimesh's ray casting fast.
- Run scripts with `python3 -I` (they add their own folder to `sys.path` for the shared helpers).
- Blender's bake alpha is 1 everywhere: compute texel coverage from the UV triangles instead (`make_regions_cow.py`).
- `pkill -f <script>` from the same shell kills that shell too (its command line contains the pattern); use `pgrep` + `kill`.

## 7. Scripts (`scripts/`) and the order they run in

Inputs: `<x>` = extracted uploads (Tripo OBJ, `cowMask.obj`, slipper `Cow_Slippers_pair.glb`, the 10 `TILE_*.png`), `<w>` = a work folder.

| # | Script | What it does |
|---|---|---|
| 1 | `bl_stage6_cow.py <tripo.obj> <w>/cow_high.blend` | Import, Z up, metallic 0 |
| 2 | `fit_mask_scan_cow.py <cowMask.obj> <tripo npz> <w>/maskfit` | Scan units (eye beads), scale from the mask width, pose fit onto Tripo's face -> `fit.json` |
| 3 | `prep_tiles_cow.py <tiles> fabric_tiles/real_fabric_crops <w>/tiles_ready` | Seam/light/brightness checks, seamless tiles, heights, colour fixes, gold satin, glossy black paint, lace opacity |
| 4 | `horns_from_scan_cow.py <cowMask.obj> <w>/horns` | Scan-guided horns and wire tuft |
| 5 | `build_swaps_cow.py … <w>/swaps` | Mask on, Tripo face/horns/feet off (capped), socks, slipper placement, cord tail |
| 6 | `bl_assemble_cow.py <w>/swaps <tripo basecolor> <slippers.glb> <w>/cow_swapped.blend` | All parts in one .blend, metres |
| 7 | `bl_decimate_cow.py <w>/cow_swapped.blend <w>/cow_low.blend <w>/ply` | Region-weighted decimation; `compare_lod_cow.py` checks it |
| 8 | `bl_uv_cow.py <w>/cow_low.blend <w>/cow_uv.blend` | Joins the LOW parts (face attribute `part`), texel-weighted atlases |
| 9 | `bl_bake_cow.py <w>/cow_uv.blend <w>/bake` | Colour, normal, per-texel position/normal/part; UV'd OBJs |
| 10 | `make_regions_cow.py <w>/bake … <w>/swaps/swaps.json … REF_J <w>/regions` | Region classes; the mask from Tripo's colours inside the scan's outline (`swaps/mask_footprint.npz`); `render_regions_cow.py` draws the map |
| 11 | `make_mix_masks_cow.py <w>/regions <w>/mix` | Soft sequential mix factors |
| 12 | `bl_fabric_cow.py <w>/bake/cow_baked_work.blend <w>/tiles_ready <w>/mix <w>/bake <w>/fabric` | Live materials, AO, final bakes (about 12 min on CPU) |
| 13 | `render_compare_cow.py`, `bl_export_cow.py <w>/fabric/Cow_fabric_live.blend <w>/fabric deliver` | Live vs baked; GLB + lean live .blend |
| 14 | `bl_export_web_cow.py deliver/Misanthropic_Cow.glb <viewer>` | Lighter GLBs for the browser viewer (`viewer/README.md`) |

Helpers: `geom_cow.py` (tube sweep), `bl_cow_common.py` (baked material with glTF occlusion), `render_clay_views.py`, `fit_scan_to_scan.py` (OBJ vs STL check; free-scale ICP collapses, see §8). Earlier stages: `prep_refs_cow.py`, `proportion_*`, `design_key_*`, `kit_*`, `fix_*_view.py`, `normalize_views_cow.py`, `render_model_cow.py`, `compare_silhouettes_cow.py`, `prep_fabric_crops_cow.py`, `build_tile_kit_cow.py`.

Numbers worth keeping are in `checkpoints/`: `mask_scan_fit.json`, `swaps.json` (scale, slipper placement, horn shifts, bolster ends, tail), `horns.json`, `tile_report.json`, `regions.json`.

## 8. Lessons (worth adding to the playbook)

1. **Image-model guardrails.** ChatGPT blocked the costume ("nudity/sexuality") because of underwear and breast-like words and photos. Neutral wording ("udder" with "nubs", "bloomers", "the costume's own left"), no close-ups of the udder and underwear, cropped props, the user's censored front, and a new chat after any refusal fixed it. Gemini allowed what ChatGPT refused.
2. **Gemini re-renders the whole image on every edit**; ChatGPT's Select tool stays closer. Do AI fixes first and deterministic fixes last. Deterministic edits beat AI edits for size, position and colour.
3. **Measure with a rigid ruler** (the mask width, eye beads). Reference photos must match the side they're used for.
4. **Free-scale ICP shrinks** onto a patch of the target (scan vs scan, and scan vs an AI face). Hold the scale from a measured landmark and let ICP set only the pose; test scales on a grid when needed.
5. **A real scan beats AI geometry for a rigid part.** Deleting the AI face inside the scan's outline and capping the hole worked; pushing the AI surface behind the scan left spikes and an AI snout under the real chin.
6. **AI meshes are split at UV seams**: weld by position before finding boundary loops (sock rings, caps).
7. **Black paint scans noisily** (the mask's black patches are rough in the scan); the geometry still fits.
8. **Photo projection needs hand-checked landmarks** where shadows merge shapes (the nostril slits merge into the snout's shadow).
9. **Show the user the textured result early.** The scanned mask passed the region-map check but looked wrong once textured; a quick textured render of a swapped part before the full pipeline would have caught it.
10. **Place props under the AI body's limbs, not where the AI drew its own props**: Tripo's slippers were 2.7 cm off its legs.

## 9. Package map

| Folder or file | Contents |
|---|---|
| `HANDOFF.md`, `README.md`, `DESIGN_BRIEF.md` | Docs |
| `scripts/` | Every script above |
| `checkpoints/` | Checkpoint pictures 1-4 and the measured numbers |
| `deliver/Misanthropic_Cow.glb` | The finished figure (§10) |
| `deliver/live/` | `Cow_fabric_live.blend` + `textures/` (keep them together) |
| `views/`, `reference/`, `tripo_inputs/`, `tripo_eval/`, `prompts/`, `fabric_tiles/`, `kit/` | Earlier stages |

Not in the repo: the Tripo OBJ (the user's RAR, 194 MB), the mask scan (`cowMask.rar`), the raw photos, and the work .blends (rebuild with §7).

## 10. The deliverable

`deliver/Misanthropic_Cow.glb`: glTF, +Y up, metres, the face toward +Z, the costume's own left at +X; 1.648 m tall.

| Object | Triangles | Maps |
|---|---|---|
| `Cow_body` (body with the mask, socks, cord tail, horns, wire tuft) | 242k | 4K base colour, roughness, normal; 2K occlusion |
| `Slipper_L`, `Slipper_R` (one mesh, mirrored) | 150k each | the slippers' own maps at 2K |

Metallic 0 everywhere; JPEG maps; the occlusion maps are separate (no lighting in the colour).
`deliver/live/Cow_fabric_live.blend`: the live fabric material `Cow_Fabric` (mask classes included): tiles box-projected at real size (fur and shag 10 cm, fleece, satin, lace, plaster 8 cm, leggings, paint, knit 6 cm, snout 5 cm), mix masks (PNG, keep lossless), detail normals, see-through lace. Textures are relative (`//textures/...`).
