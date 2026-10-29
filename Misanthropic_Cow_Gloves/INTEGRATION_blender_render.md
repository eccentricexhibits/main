# Hoof gloves → Misanthropic Cow character: integration note (Blender, Cycles render)

**For:** the assistant (or person) building the full Misanthropic Cow character in Blender.
**What it is:** the character's costume gloves: cream terry mittens whose two finger pairs end in black painted hoof
caps and can spread apart like a Vulcan salute. Finished, real-size, textured, with a terry displacement version for
Cycles. Everything below was tested by appending the gloves into a fresh character file with a hand rig (Blender 5.2.3).

---

## 1. Which file

From the glove handoff **Part 4 BLENDS_LIVE** (`09_final/blend_live/`):

| File | Use it for |
|---|---|
| `Glove_pair_live_displace.blend` | **Cycles renders (recommended).** Terry loops are real geometry at render time: fuzzy outline, loop shadows. |
| `Glove_pair_live.blend` | EEVEE or quick previews: same look, with the terry as bump only. |
| `textures/` (10 files) | Used by both. **Must stay next to the .blend** (paths are relative). |

Both files were saved with **Blender 5.2.3**; open them with 5.2 or newer. (Not Blender? Use `Glove_pair.glb` from
Part 2 instead; no displacement.)

## 2. What's inside

Six objects, no rig, one shared material `Glove_Terry_Hoof_live`:

| Object | Parent | What it is |
|---|---|---|
| `Glove_L_Palm` | – | Palm, thumb and cuff of the left glove. **Origin = centre of the bottom of the cuff.** |
| `Glove_L_Toe_IndexMiddle` | `Glove_L_Palm` | Index + middle finger compartment with its hoof cap. |
| `Glove_L_Toe_RingLittle` | `Glove_L_Palm` | Ring + little finger compartment with its hoof cap. |
| `Glove_R_*` (same three) | `Glove_R_Palm` | The right glove: **a mirror image** of the left (palm shows scale −1, −1, −1 with rotation 180° X; that is just how Blender displays a mirror). |

- **Real size, metres:** 24.7 cm from cuff to hoof tip, ~12 cm wide at the thumb. Build the character at real size
  too. The cow mask scan in the glove handoff (`01_references/scale_sources/cowMask1.stl`) is in **millimetres**:
  import it with scale 0.001.
- **Rest pose:** fingers point +Z, back of the hand faces −Y, left thumb toward +X. Left glove at x = −0.12 m, right at
  +0.12 m, cuffs at z = 0.
- **Animation:** each finger pair pivots at the finger web, **13.9 cm above the cuff**.
  - **Spread:** rotate about the toe's **local Y**: `Toe_IndexMiddle` **+θ**, `Toe_RingLittle` **−θ**. The **same signs on
    both gloves**; the mirror takes care of the right one. 12° each opens the tips from 0.6 cm to 4.8 cm apart.
  - **Curl:** rotate about **local X**.

## 3. Steps

1. **Copy the folder** `blend_live/` (the .blend files + `textures/`) into the character project, e.g.
   `<character project>/assets/gloves/`.
2. **Save the character .blend** before appending, so the texture paths can be stored relative to it.
3. **Append** the six objects: File → Append → `Glove_pair_live_displace.blend` → `Object` → select the six
   `Glove_*` objects. Then File → External Data → **Make Paths Relative**.
4. **Place each glove** by moving and rotating **only its palm object** (the finger pairs follow). Put the cuff at the
   wrist. The cuff is closed, so it sits over the hand; the bodysuit's fur sleeve should cover the cuff, as on the real
   costume.
5. **Attach to the hand:** select the palm, then the armature, Pose Mode, select the hand bone, **Ctrl+P → Bone**. No rig
   yet? Parent the palm to the forearm object or an Empty instead.
6. **Render with Cycles** (Render Properties → Render Engine → Cycles). Displacement appears only in final renders and
   in the Rendered viewport. Budget about **6 GB of RAM** for the two gloves at render time.

Same steps as a script (tested; adjust the path, rig and bone names, and the placement matrices):

```python
import bpy, math
from mathutils import Matrix
GLOVES = "//assets/gloves/Glove_pair_live_displace.blend"   # relative to the SAVED character .blend
rig = bpy.data.objects["Rig"]                                   # your armature
names = ["Glove_L_Palm", "Glove_L_Toe_IndexMiddle", "Glove_L_Toe_RingLittle",
         "Glove_R_Palm", "Glove_R_Toe_IndexMiddle", "Glove_R_Toe_RingLittle"]
col = bpy.data.collections.new("Gloves"); bpy.context.scene.collection.children.link(col)
with bpy.data.libraries.load(bpy.path.abspath(GLOVES), link=False, relative=True) as (src, dst):
    dst.objects = [n for n in src.objects if n in names]
for o in dst.objects: col.objects.link(o)
bpy.ops.file.make_paths_relative()
G = {o.name: o for o in dst.objects}

def attach(palm, bone, world_matrix):
    palm.matrix_world = world_matrix          # place: translation + rotation only (keep the right glove's mirror)
    bpy.context.view_layer.update(); keep = palm.matrix_world.copy()
    palm.parent = rig; palm.parent_type = "BONE"; palm.parent_bone = bone
    bpy.context.view_layer.update(); palm.matrix_world = keep   # parent without moving it

# example: cuff at the wrist, fingers along +X (left hand) / -X (right hand), back of the hand up
attach(G["Glove_L_Palm"], "hand.L", Matrix.Translation((0.35, 0, 1.0))
       @ Matrix.Rotation(math.radians(-90), 4, "Y") @ Matrix.Rotation(math.radians(90), 4, "Z"))
attach(G["Glove_R_Palm"], "hand.R", Matrix.Translation((-0.35, 0, 1.0))
       @ Matrix.Rotation(math.radians(90), 4, "Y") @ Matrix.Rotation(math.radians(-90), 4, "Z")
       @ Matrix.Diagonal((-1, 1, 1, 1)))      # the right glove stays a mirror image
bpy.context.scene.render.engine = "CYCLES"
```

## 4. Don'ts

- **Don't Apply scale or rotation (Ctrl+A) to any glove object.** The right glove would turn inside out, and the
  terry and brush-stroke textures are projected from each object's own coordinates, so applying would change their
  size and turn the hoof strokes sideways. Need a different size? Scale a parent (Empty or bone), never apply.
- **Don't join** the glove meshes with each other or with the body: the finger pairs must stay separate to animate.
- **Don't delete or reorder the `terry_displace` Subdivision modifier** (keep it last in each stack); it makes the
  micro-polygons the displacement needs. Don't switch it to Catmull-Clark: that would round off the hoof edges.
- **Don't rename or move** files inside `textures/`.

## 5. Known quirks (expected, not bugs)

- On a closed glove, the terry is a little smoother in a ~6 mm band across the knuckle line: the displacement fades
  out where the finger pairs meet the palm, so they can spread without cracks.
- The baked ambient occlusion was made with the fingers closed: when spread, the inner walls look slightly dark.
- The inner walls of the finger pairs are flat (the real hooves were hollow cardboard caps).

## 6. Checks after integrating

```python
import bpy, os, math
print([i.name for i in bpy.data.images if i.filepath and not os.path.exists(bpy.path.abspath(i.filepath))])  # want []
for side in "LR":                                   # spread test: both gloves should open
    bpy.data.objects[f"Glove_{side}_Toe_IndexMiddle"].rotation_euler.y = math.radians(12)
    bpy.data.objects[f"Glove_{side}_Toe_RingLittle"].rotation_euler.y = math.radians(-12)
```

Then render a close-up of each hand in Cycles: cream terry with visible loops, black hooves with long base-to-tip
brush strokes, and both gloves following the hand bones when posed. Reset the toe rotations to 0 afterwards.
