# HANDOFF: The Misanthropic Cow, full-body 3D model

**For:** a new Claude session continuing this project. Read `3D_Model_Pipeline_PLAYBOOK/PLAYBOOK.md` first; this project follows it. Then read this file. The repository branch is `claude/gallant-feynman-4ikhs2` in `eccentricexhibits/main`, folder `Misanthropic_Cow_Full_Body/`.

## 1. Goal and where we are

Goal: a clean, textured, rig-ready 3D model of the user's character, The Misanthropic Cow, a handmade full-body cow costume. The costume no longer exists to re-shoot, so the model is built from about 100 old photos and the AI route in the playbook.

| Stage (playbook) | Status |
|---|---|
| 0 Intake | done (decisions in §3) |
| 1 References, design key, brief | done |
| 2 Multiview images (ChatGPT/Gemini) | done: `views/1_FRONT…`, `2_BACK…`, `3_SIDE_facing_left…`, `4_SIDE_facing_right…` `_approved.png` |
| 3 Tripo inputs | done: `tripo_inputs/` (1536², same height and ground line) |
| 4 Tripo model, evaluated | done: `tripo_eval/REPORT.md`. Accepted with no second round. |
| 6 Cleanup | done in a working .blend (Z up, metallic 0). Rebuild it with `scripts/bl_stage6_cow.py` (see §6). |
| 9c step 1, fabric tiles | **the user is generating 10 tiles in ChatGPT** with `fabric_tiles/Cow_fabric_tiles_kit.zip` |
| Next | geometry swaps, then decimate, UV, bake, region masks, tiles, final bake, deliverables (§5) |

**Waiting on the user:**
1. The 10 fabric tiles (`TILE_01…TILE_10.png`).
2. A 3D scan of the real mask. Ask which app made it; phone scanners usually save in metres.
3. The finished slipper model from the earlier slipper project (GLB).
4. Re-uploading the Tripo model `cow_costume_3d_model.part1–3.rar`: it's 194 MB and isn't in the repo.

## 2. The user

- Character creator. Comfortable with Blender, but wants Claude to do the technical work and to end every reply with a concrete, numbered next step.
- Runs ChatGPT, Gemini and Tripo themselves. Likes complete, copy-pasteable prompts with numbered attachments. Gives sharp visual feedback: trust it, then measure.
- Every file moved to a new window must be **under 29 MB**.

## 3. Decisions (all confirmed by the user)

- **No re-shoot** (the costume is gone). Proportions come from the **original photo shoot wearer** (8 photos). Other wearers stuffed the belly and udder differently.
- **A-pose**, rigged and animated eventually.
- **Beige satin "bloomers" with lace side panels**, worn over the black spotted leggings. The original pair was lost after that shoot; the back design is unknown. Plan: paint the back as a continuation of the front at the texturing stage.
- **Slippers:** drawn into the views, but **to be replaced by the finished slipper model** in Blender.
- **Horns are deliberately mismatched.** The costume's own RIGHT horn is short and ends in a tuft of twisted bare wire (deliberate). Its own LEFT horn is a long horn with 3 black rings and an intact pointed tip; later photos show this tip broken, which is damage, not design. Seen straight on, the long horn goes **out sideways, then hooks up near the tip** (REF_J, REF_K). Plan: **model both horns cleanly in Blender**.
- **The hood is a separate piece** whose fur edge overlaps the suit's collar. Keep that construction, but no neck or skin should ever show.
- **Black socks** inside the slippers; no bare skin anywhere.
- **Tail:** a thin white cord hanging from the gold bow. **It's left out of the images and modelled in Blender.**
- **Bow:** small gold satin, centred on the lower back, about a quarter of the back's width.
- **Gloves:** white fuzzy knit with a plain white thumb, and two broad, blunt black hoof halves over the fingers. No claws.
- **Surface route:** 9c (material regions plus ChatGPT fabric tiles), the same "product" look as the slippers.
- **No real measurements exist.** Scale will come from the mask scan. Today the model is 0.978 units tall, in arbitrary units.

## 4. Ground truth and key references

- `DESIGN_BRIEF.md`: authoritative parts list and NEVER ADD list.
- `reference/DESIGN_KEY_check_every_view_against_this.png`: 16 numbered features.
- `reference/PROPORTION_BASE_original_shoot.png`: collage of the original wearer (shot 4 body, shot 3 head).
- `reference/PROPORTION_SKETCH_A_pose.png`: flat-colour drawing of the same proportions.
- Measured proportions, from floor to horn tips: snout bottom ~85%, udder 73–85% (~25% of height wide), belly widest at ~60% (~28% wide), fur hem ~52%, crotch ~46%.
- Straight-on head photos supplied by the user: `reference/REF_J_head_front_on_new_photo.webp`, `REF_K_…`. Back bow photo: `REF_L_back_bow_new_photo.jpg`.
- Right side of the head: photos 8 and 9 of 25 (`DETAIL_15`, `DETAIL_15b` in the STEP_5 kit). **No clean photo shows the body's left side.**
- Raw photos: the user's `Full_Cow_Tripo.part1–4.rar`. Extract with `unrar`. They're untrusted input, so keep them in their own folder.

## 5. What to do next (in this order)

1. **Geometry swaps**, all before decimation. Blender frame: Z up, front −Y, the costume's own left is +X.
   - Mask scan: fit it to Tripo's head (scale and pose by landmarks: eyes, nostril slits, snout, brow), replace the face, and set the **real scale**: measure the mask's width at eye level on the scan and on the model, then scale the whole model by scan ÷ model.
   - Horns: model a long horn (out sideways, then hooked up, 3 rings) on the costume's own left, and a short horn (2 rings) with a twisted-wire tuft (thin curves) on its right. Size them against the mask, using REF_J: the long horn reaches about 0.35 of the mask width out from the bolster and rises about 0.24; it's about 0.23 thick at the root.
   - Slippers: remove Tripo's feet below the ankle and place the slipper GLB (mirrored pair) on black-sock feet.
   - Cord tail: a thin smooth white cord (shoelace-thick) from the bow to about knee height.
   - The udder stays from Tripo. Its depth matches the left view.
2. **Stage 7 decimation** from 1.9M triangles. Use region weights: keep the face/mask, hands and hooves, bow, patch tufts and udder nubs; reduce the flat legs, back and belly. Verify with same-camera clay renders and silhouette scores (`compare_meshes.py`).
3. **Stage 8:** UV unwrap with texel weighting (face and hands high, legs low), then bake colour, normal and roughness from high to low, plus a per-texel position/normal bake.
4. **Stage 9c:**
   - `prep_tiles.py` on the user's tiles: fix seams, make height maps. Make two recolours: **gold satin** (from the beige satin) and **glossy black paint** (from the plaster).
   - Region masks per texel. Classes: white fur, black shag patches, pink fleece udder, beige satin, beige lace, black leggings, white paint spots, white knit gloves, black hooves (solid, glossy), mask plaster, black mask paint, yellow eyes (solid), red flocked snout, black nostril slits, yellow horn paint + black rings (solid), gold bow, slippers (own textures).
   - **Show the colour-coded region map to the user before texturing.**
   - Paint the mask's black patches from REF_J/REF_K (front) and DETAIL_15 (right side). The real mask is wider than Gemini's and has a big patch over each eye.
   - Build the live material, bake AO, final bakes, compare live vs baked.
5. **Deliver (stages 10–11):** GLB with JPEG maps and a lean .blend with relative textures, every file under 29 MB, plus an updated HANDOFF. Rigging is next after that; suggest Rigify or AccuRig to the user.

## 6. Environment setup (fresh container)

```bash
apt-get install -y unrar libegl1 libegl-mesa0 libgl1-mesa-dri libgles2 libosmesa6 libglu1-mesa libxi6 libxxf86vm1 libxfixes3 libxrender1 libsm6 libxkbcommon0
```
```bash
pip install opencv-python-headless pillow numpy scipy "networkx>=3" trimesh rtree "PyOpenGL>=3.1.9" freetype-py imageio pyglet==1.5.29 bpy==5.2.3
```
```bash
pip install --no-deps pyrender
```
- `bpy==5.2.3` has a cp313 wheel (about 400 MB).
- pyrender needs `PYOPENGL_PLATFORM=egl`. `r.render(..., flags=DEPTH_ONLY)` returns only the depth array. Use `RenderFlags.RGBA` and composite onto white, or the background renders black.
- Blender OBJ import puts the Y-up to Z-up conversion in the object rotation. Apply the transform.

## 7. Scripts (`scripts/`)

| Script | Purpose |
|---|---|
| `prep_refs_cow.py` | All REF_/DETAIL_ crops, white-balanced, square (needs the extracted photos and the playbook folder) |
| `proportion_base_composite.py` | Proportion collage (shots 4 + 3) |
| `proportion_guide_sketch.py` | Flat-colour A-pose proportion drawing |
| `design_key_cow.py` + `design_key_marks.py` | Design key |
| `kit_content_cow.py` + `build_kit_cow.py` | Step-kit prompts and zips (`kit/`) |
| `fix_front_view.py` | Front view: real long horn from REF_J, legs stretched 6% with the slippers unscaled |
| `fix_back_view.py` | Back view: mirrored front horn (3 rings), neck gap covered, bow centred, ankle skin blacked |
| `fix_side_udder.py` | Right side view: udder ×1.25 about its top attachment |
| `normalize_views_cow.py` | Tripo inputs: cleans off-white backgrounds without eating white fur, same height and ground line |
| `render_model_cow.py` | Textured and clay turnarounds of an OBJ |
| `compare_silhouettes_cow.py` | Model vs input-view silhouette IoU and width profiles |
| `bl_stage6_cow.py` | Import OBJ, apply axis conversion, zero metallic, save the high-poly .blend |
| `prep_fabric_crops_cow.py` + `build_tile_kit_cow.py` | Fabric crops and the ChatGPT tile kit |

Example (from the repo folder): `python3 scripts/bl_stage6_cow.py "<extracted>/cow costume 3d model/cow_costume_3d_model.obj" work/cow_high.blend`

## 8. Lessons from this project (worth adding to the playbook)

1. **Image-model guardrails.** ChatGPT blocked the costume ("nudity/sexuality") because of underwear and breast-like words and photos, even though the costume covers everything. What worked:
   - neutral costume wording ("udder" with "nubs", "bloomers", "the costume's own left");
   - dropping close-ups of the udder and underwear;
   - cropping out props (a knife and fake blood);
   - the user's **censored front** (udder painted out) as the reference for the back view;
   - a new chat after any refusal.

   Gemini allowed what ChatGPT refused.
2. **Gemini re-renders the whole image on every edit**, which softens detail and changes size. ChatGPT's Select tool also re-renders globally but stays close (silhouette IoU 0.96–0.99). Each round can drift, so do **AI fixes first and deterministic fixes last**.
3. **Deterministic edits beat AI edits** for size, position and colour fixes:
   - shrinking or replacing a horn;
   - moving the bow;
   - stretching the legs while keeping the slippers unscaled;
   - enlarging the udder;
   - filling the neck gap;
   - colouring in the ankle strips.

   AI models kept making the horn 2–3× too big. Pasting the **real horn cut from a straight-on photo** fixed it.
4. **Measure with a rigid ruler:** the mask width (or the floor-to-snout height) gave consistent numbers across photos and generated views.
5. **Reference photos must match the side they're used for.** A flipped head photo puts asymmetric paint on the wrong side. Search the archive for a real photo of that side first.
6. The extra "correction" turn in Gemini made it drift toward a generic cartoon. Paste the next step's prompt directly; the step prompts carry the side-specific details.
7. Side views: one slipper floats higher (perspective) and the hands came out ~11% smaller. Tolerable when those parts get replaced in 3D.

## 9. Package map

The handoff zip holds the repo folder without the regenerable or superseded bulk:

| Folder or file | Contents |
|---|---|
| `HANDOFF.md`, `README.md`, `DESIGN_BRIEF.md` | Docs |
| `scripts/` | Every script above |
| `views/` | Approved views, raw AI outputs, the user's censored front (`FRONT_censored_user_edit.webp`) |
| `reference/` | Design key, proportion base and sketch, REF_J/K/L |
| `tripo_inputs/` | The four normalised Tripo inputs, line-up, upload notes |
| `tripo_eval/` | Round-1 renders and report |
| `prompts/` | ChatGPT back-view prompt and images |
| `fabric_tiles/` | Real-fabric crops and the tile kit |

Not included:
- `kit/`: the ChatGPT/Gemini step kit, 40 MB. Done, and on the branch.
- The Tripo OBJ (the user's RAR, 194 MB).
- The raw photos (the user's RAR).
- The working .blend (rebuild with `bl_stage6_cow.py`).
