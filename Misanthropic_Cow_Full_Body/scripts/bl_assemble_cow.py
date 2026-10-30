"""Assemble the swapped cow in Blender (bpy) at real size, metres, Z up, front -Y, own left +X.

python3 -I bl_assemble_cow.py <swaps_dir> <tripo_basecolor.jpg> <slippers.glb> <out.blend>

Objects (all *_HIGH: full detail, before stage 7):
  Cow_body_HIGH      Tripo body after the swaps (welded; Tripo UVs and colour texture kept for region masks)
  Mask_scan_HIGH     the real mask scan's relief + rim skirt (only with face=scan; with face=tripo the face is Tripo's)
  Horn_long_L_HIGH, Horn_short_R_HIGH, Horn_wires_R_HIGH   scan-guided horns and wire tuft
  Socks_HIGH         black-sock feet
  Tail_cord_HIGH     the white cord from the bow
  Slipper_L, Slipper_R   the finished slipper pair (150k each, own baked material), placed at real size
"""
import sys, json
import numpy as np, bpy, bmesh
from mathutils import Matrix

SW, TEX, GLB, OUT = sys.argv[1:5]
info = json.load(open(f"{SW}/swaps.json"))
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.unit_settings.system = "METRIC"; scn.unit_settings.scale_length = 1.0


def simple_mat(name, rgb, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = 0
    return m


def mesh_obj(name, V, F, mat=None):
    me = bpy.data.meshes.new(name); me.from_pydata(V.tolist(), [], F.tolist()); me.validate(); me.update()
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    if mat: me.materials.append(mat)
    for p in me.polygons: p.use_smooth = True
    return ob


# body with per-loop UVs, then weld (loop UVs survive the weld)
d = np.load(f"{SW}/body.npz"); V, F, UV = d["v"].astype(float), d["f"].astype(int), d["uv"]
body_mat = bpy.data.materials.new("Tripo_colour"); body_mat.use_nodes = True
nt = body_mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
img = nt.nodes.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(TEX); img.image.name = "tripo_basecolor"
nt.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0; bsdf.inputs["Roughness"].default_value = 0.85
body = mesh_obj("Cow_body_HIGH", V, F, body_mat)
me = body.data
uvl = me.uv_layers.new(name="tripo_uv")
li = np.empty(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", li)
uvl.data.foreach_set("uv", UV[li].ravel())
bm = bmesh.new(); bm.from_mesh(me); n0 = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(me); bm.free()
print(f"body: welded {n0 - len(me.vertices):,} seam duplicates -> {len(me.vertices):,} verts, {len(me.polygons):,} faces")

import trimesh  # noqa: E402  (ply loading)
parts = [("Mask_scan_HIGH", "mask_shell", (0.92, 0.91, 0.88), 0.6), ("Horn_long_L_HIGH", "horn_long", (0.93, 0.78, 0.25), 0.45),
         ("Horn_short_R_HIGH", "horn_short", (0.93, 0.78, 0.25), 0.45), ("Horn_wires_R_HIGH", "horn_wires", (0.35, 0.35, 0.37), 0.35),
         ("Socks_HIGH", "socks", (0.03, 0.03, 0.035), 0.8), ("Tail_cord_HIGH", "tail", (0.9, 0.9, 0.88), 0.7)]
import os  # noqa: E402
for name, fn, rgb, rough in parts:
    if not os.path.exists(f"{SW}/{fn}.ply"): print(f"{name}: none (face=tripo)"); continue
    m = trimesh.load(f"{SW}/{fn}.ply", process=False)
    mesh_obj(name, np.asarray(m.vertices), np.asarray(m.faces), simple_mat(name.replace("_HIGH", ""), rgb, rough))
    print(f"{name}: {len(m.faces):,} faces")

# slippers: import the GLB, keep mesh A with its baked material; two objects, the right one mirrored
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=GLB)
new = [o for o in bpy.data.objects if o not in before]
src = [o for o in new if o.type == "MESH"][0]
sme = src.data
for o in new: bpy.data.objects.remove(o, do_unlink=True)
for side, sg in (("L", 1), ("R", -1)):
    ob = bpy.data.objects.new(f"Slipper_{side}", sme); scn.collection.objects.link(ob)
    off = info["slippers"][side]["offset_m"]
    ob.matrix_world = Matrix.Translation(off) @ Matrix.Diagonal((sg * 0.275, 0.275, 0.275, 1))
print("slippers:", len(sme.polygons), "faces each, material", [m.name for m in sme.materials])

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
