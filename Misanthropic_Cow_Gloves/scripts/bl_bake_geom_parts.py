"""Per-texel world position + part id for the shared glove atlas (for the material masks).

usage: python3 bl_bake_geom_parts.py <work_uv.blend> <out_dir> <size>
Writes geom_position_<size>.npy (H x W x 4: xyz in Blender world units, alpha = 1 where a part covers the
texel) and geom_part_<size>.npy (0 = none, 1 = palm, 2 = index-middle toe, 3 = ring-little toe). Row 0 = top
of the UV square (v = 1). Bakes are EMIT bakes of the Geometry node, one part at a time; each texel is kept only from the part whose UV
faces cover it (bake_atlas.py), so one part's margin cannot overwrite another's texels.
"""
import sys, os, bpy, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bake_atlas import uv_ownership, Atlas
BL, OUT, SIZE = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BL)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 1
hc = bpy.data.collections.get("HIGH")
if hc:
    for o in list(hc.objects): bpy.data.objects.remove(o)
names = ("Glove_Palm", "Toe_IndexMiddle", "Toe_RingLittle")
mat = bpy.data.materials.new("geom"); mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
geo = nt.nodes.new("ShaderNodeNewGeometry"); val = nt.nodes.new("ShaderNodeRGB"); img_node = nt.nodes.new("ShaderNodeTexImage")
nt.links.new(em.outputs[0], out.inputs["Surface"])
for n in names:
    o = bpy.data.objects[n]
    if not o.data.materials: o.data.materials.append(mat)
    for i in range(len(o.data.materials)): o.data.materials[i] = mat
bk = sc.render.bake; bk.use_selected_to_active = False; bk.margin = 4; bk.margin_type = "EXTEND"
owners = uv_ownership([bpy.data.objects[n] for n in names], SIZE)   # each texel from its own part only (bake_atlas.py)
res = {}
for kind in ("position", "part"):
    img = bpy.data.images.new(kind, SIZE, SIZE, alpha=True, float_buffer=True, is_data=True)
    img.colorspace_settings.name = "Non-Color"; img_node.image = img; nt.nodes.active = img_node
    if kind == "position": nt.links.new(geo.outputs["Position"], em.inputs["Color"])
    else: nt.links.new(val.outputs[0], em.inputs["Color"])
    acc = Atlas(SIZE, owners)
    for i, n in enumerate(names):
        if kind == "part": val.outputs[0].default_value = (i + 1, 0, 0, 1)
        for o in sc.objects: o.select_set(False)
        o = bpy.data.objects[n]; o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.bake(type="EMIT", use_clear=True); acc.add(i, img)
    res[kind] = acc.finish(4)[::-1].copy()
cov = res["position"][..., 3] > 0.5
np.save(os.path.join(OUT, f"geom_position_{SIZE}.npy"), res["position"])
np.save(os.path.join(OUT, f"geom_part_{SIZE}.npy"), np.where(cov, np.rint(res["part"][..., 0]), 0).astype(np.uint8))
print("baked; coverage incl. margin", round(cov.mean() * 100, 1), "%")
