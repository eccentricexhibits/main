"""Cycles check render of the LOW glove with its baked maps (colour, tangent normal, roughness).
usage: python3 bl_preview_baked.py <work.blend> <bake_dir> <size> <out.png> [samples=16] [res=700]
Shots: back of hand, thumb side, 3/4 from above, hoof close-up. Blender frame: Z up, back of hand = -Y."""
import sys, os, math, bpy
from mathutils import Vector
BL, BD, SZ, OUT = sys.argv[1:5]; SAMP = int(sys.argv[5]) if len(sys.argv) > 5 else 16; RES = int(sys.argv[6]) if len(sys.argv) > 6 else 700
bpy.ops.wm.open_mainfile(filepath=BL)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMP
sc.render.resolution_x = sc.render.resolution_y = RES; sc.render.film_transparent = False
hc = bpy.data.collections.get("HIGH")
if hc: hc.hide_render = True
m = bpy.data.materials.new("Glove_baked_preview"); m.use_nodes = True; nt = m.node_tree
b = nt.nodes["Principled BSDF"]; b.inputs["Metallic"].default_value = 0
def tex(kind, noncolor):
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(BD, f"glove_{kind}_{SZ}.png"))
    if noncolor: n.image.colorspace_settings.name = "Non-Color"
    return n
nt.links.new(tex("color", False).outputs[0], b.inputs["Base Color"])
nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(tex("normal", True).outputs[0], nm.inputs["Color"]); nt.links.new(nm.outputs[0], b.inputs["Normal"])
if os.path.exists(os.path.join(BD, f"glove_roughness_{SZ}.png")):
    nt.links.new(tex("roughness", True).outputs[0], b.inputs["Roughness"])
for n in ("Glove_Palm", "Toe_IndexMiddle", "Toe_RingLittle"):
    o = bpy.data.objects[n]
    for i in range(len(o.data.materials)): o.data.materials[i] = m
    for p in o.data.polygons: p.use_smooth = True
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.92, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
key = bpy.data.objects.new("key", bpy.data.lights.new("key", "SUN")); key.data.energy = 3.0; sc.collection.objects.link(key)
key.rotation_euler = (math.radians(50), math.radians(10), math.radians(-30))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
shots = [("back", Vector((0, -1, 0)), Vector((0, 0, 0.49)), 0.62), ("thumb", Vector((1, 0, 0)), Vector((0, 0, 0.49)), 0.62),
         ("q34", Vector((0.6, -0.7, 0.5)), Vector((0, 0, 0.5)), 0.66), ("hoof", Vector((0.15, -1, 0.2)), Vector((-0.06, 0, 0.78)), 0.3)]
from PIL import Image
tiles = []
for name, d, tgt, scale in shots:
    d.normalize(); cam.location = tgt + d * 3; cam.data.ortho_scale = scale
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    path = OUT.replace(".png", f"_{name}.png"); sc.render.filepath = path; bpy.ops.render.render(write_still=True); tiles.append(path)
ims = [Image.open(p).convert("RGB") for p in tiles]
sheet = Image.new("RGB", (RES * len(ims), RES)); [sheet.paste(im, (RES * i, 0)) for i, im in enumerate(ims)]; sheet.save(OUT)
print("saved", OUT)
