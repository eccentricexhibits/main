"""Package the optimised glove as a real-size PAIR (GLB + lean .blend) with baked maps.

usage: python3 bl_export_pair.py <work.blend> <maps_dir> <out_dir> [height_cm=24.7]
maps_dir holds glove_color.jpg, glove_normal.jpg, glove_roughness.jpg (shared atlas).
- Scales the glove to real size (metres; the cuff-to-tip height = height_cm).
- Left glove: Glove_L_Palm (root, origin at the cuff bottom) with children Glove_L_Toe_IndexMiddle and
  Glove_L_Toe_RingLittle (pivot at the middle/ring web). Right glove: the same meshes on mirrored nodes
  (X scale -1), placed beside it. Spread = rotate a toe about its local Y axis, curl = local X.
- Writes Glove_pair.glb, Glove_L.glb and Glove_pair.blend (+ textures/ next to it, relative paths).
"""
import sys, os, shutil, bpy
from mathutils import Vector, Matrix

BL, MAPS, OUT = sys.argv[1:4]; H_CM = float(sys.argv[4]) if len(sys.argv) > 4 else 24.7
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BL)
hc = bpy.data.collections.get("HIGH")
if hc:
    for o in list(hc.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(hc)
palm, ta, tb = (bpy.data.objects[n] for n in ("Glove_Palm", "Toe_IndexMiddle", "Toe_RingLittle"))

# real size: scale everything about the world origin, keeping parenting intact
zs = [(o.matrix_world @ v.co).z for o in (palm, ta, tb) for v in o.data.vertices]
k = (H_CM / 100) / (max(zs) - min(zs))
S = Matrix.Diagonal((k, k, k, 1))
for o in (palm, ta, tb):
    o.data.transform(Matrix.Diagonal((k, k, k, 1)))
bpy.context.view_layer.update()
mw = {o: o.matrix_world.copy() for o in (palm, ta, tb)}
for o in (palm, ta, tb):
    t = mw[o].to_translation() * k
    o.parent = None; o.matrix_world = Matrix.Translation(t)
bpy.context.view_layer.update()
for o in (ta, tb):
    o.parent = palm; o.matrix_parent_inverse = palm.matrix_world.inverted()
# left glove's cuff centre at x = -0.12 m, right glove mirrored at +0.12 m
palm.location = Vector((-0.12, 0.0, 0.0))
bpy.context.view_layer.update()

# material with the baked atlas
tex_dir = os.path.join(OUT, "textures"); os.makedirs(tex_dir, exist_ok=True)
for f in ("glove_color.jpg", "glove_normal.jpg", "glove_roughness.jpg"):
    shutil.copy(os.path.join(MAPS, f), os.path.join(tex_dir, f))
m = bpy.data.materials.new("Glove_Terry_Hoof"); m.use_nodes = True; nt = m.node_tree
b = nt.nodes["Principled BSDF"]; b.inputs["Metallic"].default_value = 0.0
def tex(f, noncolor):
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(tex_dir, f))
    if noncolor: n.image.colorspace_settings.name = "Non-Color"
    return n
nt.links.new(tex("glove_color.jpg", False).outputs[0], b.inputs["Base Color"])
nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(tex("glove_normal.jpg", True).outputs[0], nm.inputs["Color"])
nt.links.new(nm.outputs[0], b.inputs["Normal"])
nt.links.new(tex("glove_roughness.jpg", True).outputs[0], b.inputs["Roughness"])
for o in (palm, ta, tb):
    o.data.materials.clear(); o.data.materials.append(m)

names = {palm: "Glove_L_Palm", ta: "Glove_L_Toe_IndexMiddle", tb: "Glove_L_Toe_RingLittle"}
for o, n in names.items(): o.name = n; o.data.name = n.replace("Glove_L_", "Glove_")
# right glove: linked duplicates on a mirrored root
dup = {}
for o in (palm, ta, tb):
    d = o.copy(); bpy.context.scene.collection.objects.link(d); d.name = o.name.replace("_L_", "_R_"); dup[o] = d
for o in (ta, tb):
    dup[o].parent = dup[palm]; dup[o].matrix_parent_inverse = o.matrix_parent_inverse.copy()
rp = dup[palm]; rp.parent = None
rp.matrix_world = Matrix.Diagonal((-1, 1, 1, 1)) @ palm.matrix_world             # mirror across x = 0
bpy.context.view_layer.update()

def export(path, objs):
    for o in bpy.data.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, use_selection=True, export_format="GLB", export_image_format="JPEG", export_apply=False)
export(os.path.join(OUT, "Glove_pair.glb"), [palm, ta, tb, rp, dup[ta], dup[tb]])
export(os.path.join(OUT, "Glove_L.glb"), [palm, ta, tb])
# lean .blend with external, relative textures (absolute -> save -> make relative -> save; see playbook 11)
blend = os.path.join(OUT, "Glove_pair.blend")
for im in list(bpy.data.images):                      # leftover Tripo maps and old bake images
    if im.name not in ("glove_color.jpg", "glove_normal.jpg", "glove_roughness.jpg"): bpy.data.images.remove(im)
for mt in list(bpy.data.materials):
    if mt.name != "Glove_Terry_Hoof": bpy.data.materials.remove(mt)
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_as_mainfile(filepath=blend)
if os.path.exists(blend + "1"): os.remove(blend + "1")
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if os.path.isfile(p): print(f, round(os.path.getsize(p) / 1e6, 1), "MB")
print("height", H_CM, "cm; scale factor", round(k, 4))
