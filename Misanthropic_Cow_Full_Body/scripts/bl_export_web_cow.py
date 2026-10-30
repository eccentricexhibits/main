"""Lighter GLBs for the browser viewer (each file under 15 MB), from the finished Misanthropic_Cow.glb.

python3 -I bl_export_web_cow.py <Misanthropic_Cow.glb> <out_dir>

Writes cow_body.glb (body, socks, tail, horns, wire; 2K maps, 1K occlusion), cow_mask.glb (2K colour, 1K others)
and cow_slippers.glb (both slippers; 1K maps). Same frame as the full GLB (+Y up, metres).
"""
import sys, os
import bpy

SRC, OUT = sys.argv[1:3]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
LIMIT = {"Cow_body": {"default": 2048, "ao": 1024}, "Cow_mask": {"default": 1024, "basecolor": 2048},
         "Slipper_L": {"default": 1024}, "Slipper_R": {"default": 1024}}
done = set()
for ob in bpy.data.objects:
    if ob.type != "MESH": continue
    lim = LIMIT.get(ob.name, {"default": 1024})
    for m in ob.data.materials:
        for n in m.node_tree.nodes:
            if n.type != "TEX_IMAGE" or not n.image or n.image.name in done: continue
            key = next((k for k in lim if k in n.image.name.lower()), "default")
            s = lim[key]
            if max(n.image.size) > s: n.image.scale(s, s)
            done.add(n.image.name)
for fn, names in (("cow_body", ["Cow_body"]), ("cow_mask", ["Cow_mask"]), ("cow_slippers", ["Slipper_L", "Slipper_R"])):
    for o in bpy.data.objects: o.select_set(o.name in names)
    path = f"{OUT}/{fn}.glb"
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_image_format="JPEG",
                              export_jpeg_quality=85, export_yup=True, export_apply=True, export_materials="EXPORT")
    print(f"{fn}.glb {os.path.getsize(path) / 1e6:.1f} MB")
