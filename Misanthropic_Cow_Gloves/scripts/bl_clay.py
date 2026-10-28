"""Clay render (no textures) of the low-poly glove parts, for judging the surface shape.
usage: python3 bl_clay.py <work.blend> <out_prefix> [samples=24]
Writes <out_prefix>_back.png (back of hand, raking light) and <out_prefix>_side.png (thumb side)."""
import sys, math, bpy
from mathutils import Vector
B, OUT = sys.argv[1:3]; SA = int(sys.argv[3]) if len(sys.argv) > 3 else 24
bpy.ops.wm.open_mainfile(filepath=B)
hc = bpy.data.collections.get("HIGH")
if hc:
    for o in list(hc.objects): bpy.data.objects.remove(o)
parts = [o for o in bpy.data.objects if o.type == "MESH"]
clay = bpy.data.materials.new("clay"); clay.use_nodes = True
bs = clay.node_tree.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = (0.62, 0.6, 0.57, 1); bs.inputs["Roughness"].default_value = 0.55
for o in parts:
    o.data.materials.clear(); o.data.materials.append(clay)
    for p in o.data.polygons: p.use_smooth = True
for o in bpy.data.objects:
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SA
sc.render.resolution_x, sc.render.resolution_y = 900, 1200
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = 4.0; sc.collection.objects.link(l)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 85
zs = [(o.matrix_world @ v.co).z for o in parts for v in o.data.vertices]; H = max(zs) - min(zs)
tgt = Vector((0, 0, min(zs) + 0.5 * H))
for name, d, sun in (("back", Vector((0.0, -1, 0.05)), (75, 0, 60)), ("side", Vector((1, -0.25, 0.05)), (70, 0, 150))):
    d.normalize(); cam.location = tgt + d * H * 3.0; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    l.rotation_euler = tuple(math.radians(a) for a in sun)
    sc.render.filepath = f"{OUT}_{name}.png"; bpy.ops.render.render(write_still=True)
print("saved", OUT)
