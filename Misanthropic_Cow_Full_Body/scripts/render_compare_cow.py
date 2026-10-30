"""Live fabric material vs baked maps, same Cycles cameras (front, back, head 3/4, hand + bloomers).

python3 -I render_compare_cow.py <Cow_fabric_live.blend> <fabric_dir> <out.jpg> [size=900] [samples=48]
"""
import sys, os, math
import bpy
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bl_cow_common import baked_material  # noqa: E402

SRC, FAB, OUT = sys.argv[1:4]
SIZE = int(sys.argv[4]) if len(sys.argv) > 4 else 900
SAMPLES = int(sys.argv[5]) if len(sys.argv) > 5 else 48
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = SIZE; sc.render.film_transparent = False
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.9, 0.92, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
for name, rot, e in (("key", (math.radians(50), 0, math.radians(-35)), 3.0), ("fill", (math.radians(65), 0, math.radians(140)), 1.0)):
    ld = bpy.data.lights.new(name, "SUN"); ld.energy = e; lo = bpy.data.objects.new(name, ld); lo.rotation_euler = rot; sc.collection.objects.link(lo)
cam_d = bpy.data.cameras.new("cam"); cam_d.type = "ORTHO"; cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
VIEWS = [("front", (0, 0, 0.83), (0, -1, 0), 1.76), ("back", (0, 0, 0.83), (0, 1, 0), 1.76),
         ("head 3/4", (0.0, -0.05, 1.45), (0.55, -1, 0.12), 0.36), ("hand + bloomers", (0.25, -0.05, 0.82), (0.35, -1, 0.05), 0.5)]


def shoot(tag):
    paths = []
    for name, c, d, ortho in VIEWS:
        d = Vector(d).normalized(); c = Vector(c)
        cam.location = c + d * 4; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); cam_d.ortho_scale = ortho
        p = f"{os.path.dirname(OUT)}/_cmp_{tag}_{name.replace(' ', '_').replace('/', '')}.png"
        sc.render.filepath = p; bpy.ops.render.render(write_still=True); paths.append((name, p))
        print(tag, name, flush=True)
    return paths


live = shoot("live")
for ob, tag, size, ao in [(bpy.data.objects["Cow_LOW"], "Cow", 4096, 2048)] + ([(bpy.data.objects["Mask_LOW"], "Mask", 2048, 1024)] if "Mask_LOW" in bpy.data.objects else []):
    maps = {k: bpy.data.images.load(f"{FAB}/{tag}_{k}_{n}.png") for k, n in (("basecolor", size), ("roughness", size), ("normal", size), ("ao", ao))}
    ob.data.materials.clear(); ob.data.materials.append(baked_material(f"{tag}_baked", maps))
baked = shoot("baked")

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
sheet = Image.new("RGB", (SIZE * len(VIEWS), SIZE * 2 + 40), "white"); dr = ImageDraw.Draw(sheet); f = ImageFont.load_default(26)
for row, (label, paths) in enumerate((("LIVE material", live), ("BAKED maps (GLB)", baked))):
    for i, (name, p) in enumerate(paths):
        sheet.paste(Image.open(p).convert("RGB"), (i * SIZE, 40 + row * SIZE))
        dr.text((i * SIZE + 10, 46 + row * SIZE), f"{label}: {name}", fill=(0, 0, 0), font=f)
dr.text((10, 6), "Live vs baked, same cameras (Cycles). AO is a separate occlusion map, not in the colour.", fill=(0, 0, 0), font=f)
sheet.save(OUT, quality=88); print("wrote", OUT)
