"""Clay close-ups of the web (where the finger pairs meet the palm), 4 views: back, palm, thumb side, little-finger side.
usage: python3 bl_clay_web.py <work.blend> <out.png>"""
import sys, math, bpy
from mathutils import Vector
B, OUT = sys.argv[1:3]
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
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 12
sc.render.resolution_x, sc.render.resolution_y = 700, 700
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = 4.0; sc.collection.objects.link(l)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 85
bpy.context.view_layer.update()
zs = [(o.matrix_world @ v.co).z for o in parts for v in o.data.vertices]; H = max(zs) - min(zs)
tgt = Vector((-0.01, 0, min(zs) + 0.57 * H)); outs = []
for name, d, sun in (("back", (0, -1, 0.1), (75, 0, 60)), ("palm", (0, 1, 0.1), (75, 0, -120)),
                     ("thumb", (1, 0, 0.1), (70, 0, 150)), ("little", (-1, 0, 0.1), (70, 0, -30))):
    d = Vector(d).normalized(); cam.location = tgt + d * H * 1.3; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    l.rotation_euler = tuple(math.radians(a) for a in sun)
    p = f"{OUT[:-4]}_{name}.png"; sc.render.filepath = p; bpy.ops.render.render(write_still=True); outs.append(p)
print("saved", outs)
