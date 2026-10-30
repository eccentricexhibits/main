"""Stages 10-11: deliverables from the live fabric .blend.

python3 -I bl_export_cow.py <Cow_fabric_live.blend> <fabric_dir> <out_dir> [slipper_tex=2048]

1. <out>/Misanthropic_Cow.glb: the whole figure with the baked maps (JPEG), metallic 0, AO as glTF occlusion.
   Objects: Cow_body (body with the mask, socks, cord tail, horns, wire tuft), Slipper_L, Slipper_R (and Cow_mask
   with face=scan)
   (the finished slipper pair; their maps reduced to slipper_tex to keep the file under 29 MB). glTF axes (+Y up).
2. <out>/live/Cow_fabric_live.blend + live/textures/: the live fabric materials with every texture external and
   relative (//textures/...): tiles 2K JPG, heights 1K JPG, mix masks PNG (must stay lossless), detail normals JPG,
   slipper maps JPG. Keep the textures folder next to the .blend.
Prints every file's size.
"""
import sys, os, shutil
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bl_cow_common import baked_material  # noqa: E402

SRC, FAB, OUT = sys.argv[1:4]
SLIP = int(sys.argv[4]) if len(sys.argv) > 4 else 2048
os.makedirs(f"{OUT}/live/textures", exist_ok=True)
MB = lambda p: os.path.getsize(p) / 1e6

# ---------- 2. lean live .blend (first, from the untouched live file) ----------
bpy.ops.wm.open_mainfile(filepath=SRC)
bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)   # e.g. the Tripo colour material
for im in list(bpy.data.images):
    if im.users == 0 or im.type != "IMAGE": continue           # (the bake targets are unused after the bakes)
    base = os.path.splitext(bpy.path.basename(im.filepath or im.name))[0] or im.name
    data = im.colorspace_settings.name == "Non-Color"
    if base.startswith("mix_"):
        dst, fmt, size = f"{base}.png", "PNG", None
    elif base.endswith("_height"):
        dst, fmt, size = f"{base}.jpg", "JPEG", 1024
    elif base.startswith(("cow_normal", "mask_normal")):
        dst, fmt, size = f"{base}.jpg", "JPEG", None
    elif base.startswith("TILE_"):
        dst, fmt, size = f"{base}.jpg", "JPEG", 2048
    else:                                                     # slipper maps packed in the file
        dst, fmt, size = f"slipper_{base.replace('_4096', '')}.jpg", "JPEG", SLIP
    if size and max(im.size) > size: im.scale(size, size)
    sc = bpy.context.scene; sc.render.image_settings.file_format = fmt
    if fmt == "JPEG": sc.render.image_settings.quality = 90
    im.save_render(f"{OUT}/live/textures/{dst}", scene=sc)
    if im.packed_file: im.unpack(method="REMOVE")
    im.filepath = os.path.abspath(f"{OUT}/live/textures/{dst}"); im.source = "FILE"   # made //textures/... on save
    if data: im.colorspace_settings.name = "Non-Color"
    im.reload()
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/live/Cow_fabric_live.blend", compress=True)
bpy.ops.file.make_paths_relative()                           # now that the file has its final location
bpy.ops.wm.save_mainfile(compress=True)
bpy.ops.wm.open_mainfile(filepath=f"{OUT}/live/Cow_fabric_live.blend")
imgs = [im for im in bpy.data.images if im.type == "IMAGE" and im.source == "FILE"]
missing = [im.filepath for im in imgs if not os.path.exists(bpy.path.abspath(im.filepath))]
absolute = [im.filepath for im in imgs if not im.filepath.startswith("//")]
print(f"live .blend reopened: {len(imgs)} images, missing files {missing or 'none'}, non-relative paths {absolute or 'none'}", flush=True)
tex_mb = sum(MB(f"{OUT}/live/textures/{f}") for f in os.listdir(f"{OUT}/live/textures"))
print(f"live .blend {MB(f'{OUT}/live/Cow_fabric_live.blend'):.1f} MB + textures {tex_mb:.1f} MB ({len(os.listdir(f'{OUT}/live/textures'))} files)", flush=True)

# ---------- 1. baked GLB ----------
bpy.ops.wm.open_mainfile(filepath=SRC)
for ob, tag, size, ao in [(bpy.data.objects["Cow_LOW"], "Cow", 4096, 2048)] + ([(bpy.data.objects["Mask_LOW"], "Mask", 2048, 1024)] if "Mask_LOW" in bpy.data.objects else []):
    maps = {k: bpy.data.images.load(f"{FAB}/{tag}_{k}_{n}.png") for k, n in (("basecolor", size), ("roughness", size), ("normal", size), ("ao", ao))}
    ob.data.materials.clear(); ob.data.materials.append(baked_material(f"{tag}_baked", maps))
bpy.data.objects["Cow_LOW"].name = "Cow_body"
if "Mask_LOW" in bpy.data.objects: bpy.data.objects["Mask_LOW"].name = "Cow_mask"
for ob in bpy.data.objects:
    if ob.name.startswith("Slipper"):
        for m in ob.data.materials:
            for n in m.node_tree.nodes:
                if n.type == "TEX_IMAGE" and n.image and max(n.image.size) > SLIP: n.image.scale(SLIP, SLIP)
glb = f"{OUT}/Misanthropic_Cow.glb"
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_image_format="JPEG", export_jpeg_quality=88,
                          export_yup=True, export_apply=True, export_materials="EXPORT", use_selection=False)
print(f"GLB {MB(glb):.1f} MB -> {glb}", flush=True)
