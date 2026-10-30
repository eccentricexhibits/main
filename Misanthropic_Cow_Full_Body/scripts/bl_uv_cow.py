"""Stage 8a: UVs for the LOW cow, with texel-density weighting (after the slipper project's bl_unwrap.py).

python3 -I bl_uv_cow.py <cow_low.blend> <out.blend> [angle=66]

- Cow_LOW: the LOW body, socks, tail, horns and wire tuft joined into one object (one 4K atlas). Each face keeps
  its source in the FACE attribute "part" (0 body, 1 socks, 2 tail, 3 long horn, 4 short horn, 5 wires).
- Mask_LOW: the scanned mask on its own atlas (2K), so the face gets far more texels.
Texel weights (island scale before packing): hands and hooves 1.6, udder 1.3, head and hood 1.2, plain back 0.85,
legs 0.7, socks 0.5, tail 0.8, everything else 1.0. The Tripo UVs are removed from the LOW (the colour bake reads
the HIGH's own UVs).
"""
import sys, time, math
import numpy as np, bpy
from mathutils import Vector
from bpy_extras import mesh_utils

SRC, OUT = sys.argv[1:3]
ANGLE = float(sys.argv[3]) if len(sys.argv) > 3 else 66.0
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=SRC)
scn = bpy.context.scene
PARTS = [("Cow_body_LOW", 0), ("Socks_LOW", 1), ("Tail_cord_LOW", 2), ("Horn_long_L_LOW", 3), ("Horn_short_R_LOW", 4), ("Horn_wires_R_LOW", 5)]

for name, pid in PARTS:
    me = bpy.data.objects[name].data
    for uv in list(me.uv_layers): me.uv_layers.remove(uv)
    a = me.attributes.new("part", "INT", "FACE"); a.data.foreach_set("value", np.full(len(me.polygons), pid, np.int32))
for o in scn.objects: o.select_set(False)
objs = [bpy.data.objects[n] for n, _ in PARTS]
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
bpy.ops.object.join()
cow = bpy.context.view_layer.objects.active; cow.name = "Cow_LOW"; cow.data.name = "Cow_LOW"
mask = bpy.data.objects["Mask_scan_LOW"]; mask.name = "Mask_LOW"; mask.data.name = "Mask_LOW"
print(f"joined Cow_LOW: {len(cow.data.polygons):,} faces; Mask_LOW {len(mask.data.polygons):,}", flush=True)


def weight(c, n, part):
    if part == 1: return 0.5
    if part == 2: return 0.8
    if part >= 3: return 1.0
    if abs(c.x) > 0.36 and c.z < 1.05: return 1.6
    if c.y < -0.08 and 1.18 < c.z < 1.38 and abs(c.x) < 0.2: return 1.3
    if c.z > 1.30: return 1.2
    if c.z < 0.74: return 0.7
    if c.y > 0.06 and 0.88 < c.z < 1.30: return 0.85
    return 1.0


def unwrap(ob, weighted):
    for o in scn.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    me = ob.data
    if not me.uv_layers: me.uv_layers.new(name="UVMap")
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(ANGLE), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    print(f"{ob.name}: smart project {time.time() - t0:.0f}s", flush=True)
    if weighted:
        islands = mesh_utils.mesh_linked_uv_islands(me)
        part = np.empty(len(me.polygons), np.int32); me.attributes["part"].data.foreach_get("value", part)
        uvl = me.uv_layers.active.data
        uv = np.empty(len(me.loops) * 2, np.float32); uvl.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
        cen = np.empty(len(me.polygons) * 3, np.float32); me.polygons.foreach_get("center", cen); cen = cen.reshape(-1, 3)
        nor = np.empty(len(me.polygons) * 3, np.float32); me.polygons.foreach_get("normal", nor); nor = nor.reshape(-1, 3)
        area = np.empty(len(me.polygons), np.float32); me.polygons.foreach_get("area", area)
        ls = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get("loop_start", ls)
        lt = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get("loop_total", lt)
        for isl in islands:
            isl = np.asarray(isl); a = area[isl].sum()
            if a == 0: continue
            c = Vector((cen[isl] * area[isl, None]).sum(0) / a); n = Vector((nor[isl] * area[isl, None]).sum(0))
            s = weight(c, n, int(np.bincount(part[isl]).argmax()))
            if s == 1.0: continue
            li = np.concatenate([np.arange(ls[p], ls[p] + lt[p]) for p in isl])
            cu = uv[li].mean(0); uv[li] = cu + (uv[li] - cu) * s
        uvl.foreach_set("uv", uv.ravel())
        print(f"{ob.name}: weighted {len(islands):,} islands {time.time() - t0:.0f}s", flush=True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(shape_method="CONCAVE", margin_method="FRACTION", margin=0.0012, rotate=True, scale=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    uv = np.empty(len(me.loops) * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", uv)
    print(f"{ob.name}: packed {time.time() - t0:.0f}s, uv range {uv.min():.3f}..{uv.max():.3f}", flush=True)


unwrap(cow, True)
unwrap(mask, False)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT, f"{time.time() - t0:.0f}s")
