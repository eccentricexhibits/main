"""Close-ups that show bump vs true displacement on the terry (left glove).
usage: python3 bl_render_displace_check.py <Glove_pair_live[_displace].blend> <out.png> [samples=32] [spread_deg=15]
Shots: terry under raking light, the little-finger-side outline against the background, the web with the finger
pairs spread (cracks would show here), and the whole glove."""
import sys, math, bpy
from mathutils import Vector
from PIL import Image
B, OUT = sys.argv[1:3]; SA = int(sys.argv[3]) if len(sys.argv) > 3 else 32; SP = float(sys.argv[4]) if len(sys.argv) > 4 else 15
bpy.ops.wm.open_mainfile(filepath=B)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SA
sc.render.resolution_x = sc.render.resolution_y = 800
left = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Glove_L")]
palm = next(o for o in left if "Palm" in o.name); toes = [o for o in left if "Toe_" in o.name]
W = [palm.matrix_world @ v.co for v in palm.data.vertices]
z0 = min(p.z for p in W); H = max((t.matrix_world @ v.co).z for t in toes for v in t.data.vertices) - z0
cx = sum(p.x for p in W) / len(W)
band = [p for p in W if abs(p.z - (z0 + 0.35 * H)) < 0.01 * H]; xmin = min(p.x for p in band)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.92, 0.94, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.35
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3.5; sc.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = "ORTHO"
shots = [("terry_raking", 0, Vector((-0.1, -1, 0.05)), Vector((cx, 0, z0 + 0.3 * H)), 0.13 * H, (10, 0, 75)),
         ("outline", 0, Vector((0, -1, 0.02)), Vector((xmin, 0, z0 + 0.35 * H)), 0.10 * H, (55, 0, -40)),
         ("web_spread", SP, Vector((0.15, -1, 0.35)), Vector((cx - 0.02 * H, 0, z0 + 0.58 * H)), 0.22 * H, (50, 10, -35)),
         ("glove", 0, Vector((0.1, -1, 0.15)), Vector((cx, 0, z0 + 0.5 * H)), 1.05 * H, (50, 10, -35))]
paths = []
for name, sp, d, tgt, scale, srot in shots:
    for t in toes: t.rotation_euler.y = math.radians(sp if "Index" in t.name else -sp)
    d.normalize(); cam.location = tgt + d * 3 * H; cam.data.ortho_scale = scale
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); sun.rotation_euler = tuple(math.radians(a) for a in srot)
    p = OUT.replace(".png", f"_{name}.png"); sc.render.filepath = p; bpy.ops.render.render(write_still=True); paths.append(p)
ims = [Image.open(p).convert("RGB").resize((600, 600)) for p in paths]
sheet = Image.new("RGB", (600 * len(ims), 600)); [sheet.paste(im, (600 * i, 0)) for i, im in enumerate(ims)]; sheet.save(OUT)
print("saved", OUT)
