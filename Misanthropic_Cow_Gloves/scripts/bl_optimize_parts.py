"""Region-weighted decimation of the three glove parts (playbook stage 7).

usage: python3 bl_optimize_parts.py <split.blend> <out.blend> <out_low.glb> <palm_tris> <toe_tris> [out_high.glb]

For each part (Glove_Palm, Toe_IndexMiddle, Toe_RingLittle) the full-detail mesh is kept as <name>_HIGH
(collection "HIGH", hidden; the bake source) and a copy is simplified into <name>_LOW, which takes the
part's name, origin and parenting. Passes on the LOW copy:
  1. hidden flat faces: interior vertices of the cut caps (Hoof_InnerWall / Terry_Inner) and of the
     closed cuff bottom keep 3 % of their faces,
  2. one global pass down to the part's triangle budget.
Decimate-modifier semantics (verified in the slipper project): with a vertex group and invert=False only
the weighted vertices are simplified.
"""
import sys, time, bpy
import numpy as np

BL, OUT, OUT_GLB = sys.argv[1:4]; PALM, TOE = int(sys.argv[4]), int(sys.argv[5])
OUT_HIGH = sys.argv[6] if len(sys.argv) > 6 else None
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=BL)
MM = 1 / 254
budget = {"Glove_Palm": PALM, "Toe_IndexMiddle": TOE, "Toe_RingLittle": TOE}
hc = bpy.data.collections.new("HIGH"); bpy.context.scene.collection.children.link(hc)

def tris(o): return len(o.data.polygons)

def decimate(o, target, verts=None):
    for g in list(o.vertex_groups): o.vertex_groups.remove(g)
    mod = o.modifiers.new("dec", "DECIMATE"); mod.decimate_type = "COLLAPSE"; mod.use_collapse_triangulate = True
    mod.ratio = max(min(target / tris(o), 1.0), 0.0001)
    if verts is not None:
        vg = o.vertex_groups.new(name="simplify"); vg.add(verts, 1.0, "REPLACE")
        mod.vertex_group = "simplify"; mod.vertex_group_factor = 1.0; mod.invert_vertex_group = False
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]):
        bpy.ops.object.modifier_apply(modifier="dec")
    for g in list(o.vertex_groups): o.vertex_groups.remove(g)

def hidden_flat_verts(o):
    """Vertices used only by cap faces (cut walls) or by the flat cuff bottom."""
    me = o.data; mats = [m.name if m else "" for m in me.materials]
    cap_mi = {i for i, n in enumerate(mats) if n in ("Hoof_InnerWall", "Terry_Inner")}
    nF = len(me.polygons)
    mi = np.empty(nF, np.int32); me.polygons.foreach_get("material_index", mi)
    nrm = np.empty(nF * 3, np.float32); me.polygons.foreach_get("normal", nrm); nrm = nrm.reshape(-1, 3)
    cen = np.empty(nF * 3, np.float32); me.polygons.foreach_get("center", cen); cen = cen.reshape(-1, 3)
    wz = (np.array(o.matrix_world)[:3, :3] @ cen.T).T[:, 2] + o.matrix_world.translation.z
    hidden = np.isin(mi, list(cap_mi))
    if o.name.startswith("Glove_Palm"):
        hidden |= (nrm[:, 2] < -0.9) & (wz < wz.min() + 4 * MM)          # closed cuff bottom
    # faces can be triangles or quads (bisect splits triangles): go through the loops
    lt = np.empty(nF, np.int32); me.polygons.foreach_get("loop_total", lt)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", lv)
    face_of_loop = np.repeat(np.arange(nF), lt)          # polygons' loops are stored consecutively
    vis = np.zeros(len(me.vertices), bool); vis[lv[~hidden[face_of_loop]]] = True
    hid = np.zeros(len(me.vertices), bool); hid[lv[hidden[face_of_loop]]] = True
    return np.nonzero(hid & ~vis)[0].tolist(), int(hidden.sum())

lows = {}
for name in budget:
    hi = bpy.data.objects[name]
    lo = hi.copy(); lo.data = hi.data.copy()
    bpy.context.scene.collection.objects.link(lo)
    hi.name = name + "_HIGH"; hi.data.name = name + "_HIGH"
    for c in list(hi.users_collection): c.objects.unlink(hi)
    hc.objects.link(hi)
    lo.name = name; lo.data.name = name
    lows[name] = lo
# re-point parenting of the LOW toes to the LOW palm (copies kept the HIGH palm as parent)
bpy.context.view_layer.update()
for n in ("Toe_IndexMiddle", "Toe_RingLittle"):
    lo = lows[n]; mw = lo.matrix_world.copy(); lo.parent = lows["Glove_Palm"]; lo.matrix_world = mw
hc.hide_render = True; hc.hide_viewport = True
bpy.context.view_layer.update()

for name, lo in lows.items():
    n0 = tris(lo)
    hv, nh = hidden_flat_verts(lo)
    if hv:
        decimate(lo, n0 - int(nh * 0.97), hv)
    n1 = tris(lo)
    decimate(lo, budget[name])
    print(f"{name}: {n0:,} -> hidden flat faces {nh:,} reduced -> {n1:,} -> final {tris(lo):,}  ({time.time()-t0:.0f}s)", flush=True)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
for o in bpy.data.objects: o.select_set(False)
for o in lows.values(): o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT_GLB, use_selection=True, export_format="GLB", export_materials="NONE")
if OUT_HIGH:
    hc.hide_viewport = False; bpy.context.view_layer.update()
    for o in bpy.data.objects: o.select_set(False)
    for o in hc.objects: o.hide_set(False); o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=OUT_HIGH, use_selection=True, export_format="GLB", export_materials="NONE")
print("saved", OUT, OUT_GLB, OUT_HIGH or "", f"{time.time()-t0:.0f}s")
