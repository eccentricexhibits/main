"""Close-up check renders of the live material (no material replacement).
usage: python3 bl_render_live.py <Glove_live.blend> <out.png> [samples=32] [spread_deg=15]
Shots: whole glove (back of hand), hoof close-up (strokes), terry close-up, spread 3/4."""
import sys, math, bpy
from mathutils import Vector
from PIL import Image
B, OUT = sys.argv[1:3]; SA = int(sys.argv[3]) if len(sys.argv) > 3 else 32; SP = float(sys.argv[4]) if len(sys.argv) > 4 else 15
bpy.ops.wm.open_mainfile(filepath=B)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SA
sc.render.resolution_x = sc.render.resolution_y = 800
parts = [o for o in bpy.data.objects if o.type == "MESH"]
zs = [(o.matrix_world @ v.co).z for o in parts for v in o.data.vertices]; H = max(zs) - min(zs); z0 = min(zs)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.92, 0.94, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.5
for rot, e in (((50, 10, -35), 3.2), ((70, 0, 140), 1.0)):
    l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = e; sc.collection.objects.link(l)
    l.rotation_euler = tuple(math.radians(a) for a in rot)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = "ORTHO"
cx = sum((o.matrix_world @ v.co).x for o in parts[:1] for v in o.data.vertices) / len(parts[0].data.vertices)
toes = [o for o in parts if "Toe_" in o.name]
shots = [("glove", 0, Vector((0.1, -1, 0.15)), Vector((cx, 0, z0 + 0.5 * H)), 1.05 * H),
         ("hoof strokes", 0, Vector((0.25, -1, 0.1)), Vector((cx - 0.06 * H, 0, z0 + 0.8 * H)), 0.32 * H),
         ("terry", 0, Vector((-0.2, -1, 0.1)), Vector((cx, 0, z0 + 0.3 * H)), 0.28 * H),
         ("spread", SP, Vector((0.5, -0.8, 0.4)), Vector((cx, 0, z0 + 0.6 * H)), 0.85 * H)]
paths = []
for name, sp, d, tgt, scale in shots:
    for t in toes:
        t.rotation_euler.y = math.radians(sp if "Index" in t.name else -sp) * (1 if t.matrix_world.to_scale().x * t.parent.matrix_world.to_scale().x > 0 else -1) if t.parent else 0
    d.normalize(); cam.location = tgt + d * 3 * H; cam.data.ortho_scale = scale
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    p = OUT.replace(".png", f"_{name.replace(' ', '_')}.png"); sc.render.filepath = p; bpy.ops.render.render(write_still=True); paths.append(p)
ims = [Image.open(p).convert("RGB").resize((600, 600)) for p in paths]
sheet = Image.new("RGB", (600 * len(ims), 600)); [sheet.paste(im, (600 * i, 0)) for i, im in enumerate(ims)]; sheet.save(OUT)
print("saved", OUT)
