"""Bake each <part>_HIGH onto its LOW part into ONE shared atlas: base colour, tangent normal, roughness.

usage: python3 bl_bake_parts.py <work.blend> <out_dir> <size> <samples> [passes=color,normal,roughness]
Each LOW part keeps its material slots (so face material indices survive) but every slot gets the same
bake material whose active image node is the shared atlas. Each part is baked (selected-to-active from its own
HIGH mesh) into a cleared image and only the texels its own UV faces cover are kept; the margin is added once at
the end (bake_atlas.py). Baking all parts into one image let a later part's margin overwrite an earlier part's
texels where islands sit close together.
"""
import sys, os, time, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bake_atlas import uv_ownership, Atlas

BL, OUT, SIZE, SAMPLES = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
PASSES = sys.argv[5].split(",") if len(sys.argv) > 5 else ["color", "normal", "roughness"]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BL)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
names = ("Glove_Palm", "Toe_IndexMiddle", "Toe_RingLittle")
hc = bpy.data.collections["HIGH"]; hc.hide_viewport = False; hc.hide_render = False
for o in hc.objects: o.hide_set(False); o.hide_render = False; o.hide_viewport = False
for img in bpy.data.images:
    if img.source == "FILE" and not os.path.exists(bpy.path.abspath(img.filepath)):
        print("WARNING missing texture:", img.filepath)

# smooth shading, with the edges around the cut caps marked sharp so the outer surface's normals ignore the
# caps (otherwise a shading line shows where the palm meets the toes)
import bmesh
for n in names:
    lo = bpy.data.objects[n]; mats = [m.name if m else "" for m in lo.data.materials]
    capi = {i for i, nm in enumerate(mats) if nm in ("Hoof_InnerWall", "Terry_Inner")}
    if not capi: continue
    bm = bmesh.new(); bm.from_mesh(lo.data); ns = 0
    for f in bm.faces: f.smooth = True
    for e in bm.edges:
        lf = e.link_faces
        if len(lf) == 2 and ((lf[0].material_index in capi) != (lf[1].material_index in capi)):
            e.smooth = False; ns += 1
    bm.to_mesh(lo.data); bm.free(); print(n, "sharp cap edges:", ns)

bake = bpy.data.materials.get("Glove_bake") or bpy.data.materials.new("Glove_bake")
bake.use_nodes = True; nt = bake.node_tree
for n in list(nt.nodes):
    if n.type == "TEX_IMAGE": nt.nodes.remove(n)
img_node = nt.nodes.new("ShaderNodeTexImage"); nt.nodes.active = img_node
for n in names:
    lo = bpy.data.objects[n]
    if not lo.data.materials: lo.data.materials.append(bake)
    for i in range(len(lo.data.materials)): lo.data.materials[i] = bake

bk = sc.render.bake
bk.use_selected_to_active = True; bk.cage_extrusion = 0.012; bk.max_ray_distance = 0.03
MARGIN = 16 if SIZE >= 4096 else 8
bk.margin = MARGIN; bk.margin_type = "EXTEND"
owners = uv_ownership([bpy.data.objects[n] for n in names], SIZE)

for kind in PASSES:
    t = time.time(); noncolor = kind != "color"
    img = bpy.data.images.new(f"glove_{kind}", SIZE, SIZE, alpha=False, float_buffer=False, is_data=noncolor)
    if noncolor: img.colorspace_settings.name = "Non-Color"
    img_node.image = img; acc = Atlas(SIZE, owners)
    for i, n in enumerate(names):
        lo, hi = bpy.data.objects[n], bpy.data.objects[n + "_HIGH"]
        for o in bpy.data.objects: o.select_set(False)
        hi.select_set(True); lo.select_set(True); bpy.context.view_layer.objects.active = lo
        clear = True
        if kind == "color":
            bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, use_clear=clear)
        elif kind == "normal":
            bk.normal_space = "TANGENT"; bpy.ops.object.bake(type="NORMAL", use_clear=clear)
        elif kind == "roughness":
            bpy.ops.object.bake(type="ROUGHNESS", use_clear=clear)
        acc.add(i, img)
    acc.finish(MARGIN); acc.write(img)
    path = os.path.join(OUT, f"glove_{kind}_{SIZE}.png")
    img.filepath_raw = path; img.file_format = "PNG"; img.save()
    print(kind, "baked", round(time.time() - t, 1), "s ->", path, flush=True)
bpy.ops.wm.save_as_mainfile(filepath=BL)
