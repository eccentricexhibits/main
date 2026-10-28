"""Lean, portable copy of the live-material .blend: every used image copied to <out>/textures/, paths set absolute
to the new folder, saved, then made relative and saved again (playbook stage 11; setting //relative paths before
the first save resolves them against the OLD location and breaks them). Unused images/materials are purged.
usage: python3 bl_lean_live.py <in.blend> <out_dir> <out_name.blend>"""
import sys, os, shutil, bpy
B, OUT, NAME = sys.argv[1:4]
tex = os.path.join(OUT, "textures"); os.makedirs(tex, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=B)
used = set()
for m in bpy.data.materials:
    if m.users and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image: used.add(n.image.name)
for im in list(bpy.data.images):
    if im.name not in used: bpy.data.images.remove(im)
for m in list(bpy.data.materials):
    if not m.users: bpy.data.materials.remove(m)
bpy.data.orphans_purge(do_recursive=True)
names = {"tile_terry.jpg", "tile_paint.jpg", "height_terry.jpg", "height_paint.jpg", "rough_paint.jpg"}
for im in bpy.data.images:
    if not im.filepath: continue
    src = bpy.path.abspath(im.filepath); base = os.path.basename(src)
    if base.startswith("ao_"):                                   # AO: 2K JPEG is plenty
        from PIL import Image
        dst = os.path.join(tex, "ao_2048.jpg"); Image.open(src).convert("L").resize((2048, 2048)).save(dst, quality=92)
    else:
        dst = os.path.join(tex, base); shutil.copy(src, dst)
    im.filepath = dst; im.reload()
path = os.path.join(OUT, NAME)
bpy.ops.wm.save_as_mainfile(filepath=path)
bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_as_mainfile(filepath=path)
if os.path.exists(path + "1"): os.remove(path + "1")
for f in sorted(os.listdir(tex)): print("  textures/" + f, round(os.path.getsize(os.path.join(tex, f)) / 1e6, 2), "MB")
print(NAME, round(os.path.getsize(path) / 1e6, 1), "MB")
