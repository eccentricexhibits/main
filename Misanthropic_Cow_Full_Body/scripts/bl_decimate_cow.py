"""Stage 7: region-weighted decimation of the swapped cow (after the slipper project's bl_adaptive.py).

python3 -I bl_decimate_cow.py <cow_swapped.blend> <out.blend> <ply_dir> [body_target=200000] [mask_target=60000]

Decimate-modifier semantics (verified in the slipper project): with a vertex group and invert=False only the
weighted vertices are simplified. So the flat regions get their own pass first, then one global pass.
Regions on the body come from the Tripo colour under each vertex (sampled through the UVs) plus position:
  kept detail: black shag patches and tufts, black hooves (dark above the bloomers), pink udder and nubs, gold bow, hands
  flat (pass 1, keep 10 %): the legs below the bloomers (leggings and their paint spots), the plain back, the plain belly front
Writes *_LOW objects next to the *_HIGH ones (slippers are already optimised at 150k and are left alone),
and PLY copies of HIGH and LOW for the comparison renders.
"""
import sys, time, os
import numpy as np, bpy

SRC, OUT, PLY = sys.argv[1:4]
BODY_T = int(sys.argv[4]) if len(sys.argv) > 4 else 200000
MASK_T = int(sys.argv[5]) if len(sys.argv) > 5 else 60000
os.makedirs(PLY, exist_ok=True)
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=SRC)


def tris(o): return len(o.data.polygons)


def vco(o):
    a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); return a.reshape(-1, 3)


def copy_low(hi):
    lo = hi.copy(); lo.data = hi.data.copy(); lo.name = hi.name.replace("_HIGH", "_LOW"); lo.data.name = lo.name
    bpy.context.scene.collection.objects.link(lo); return lo


def decimate(lo, target_total, vidx=None):
    for g in list(lo.vertex_groups): lo.vertex_groups.remove(g)
    mod = lo.modifiers.new("dec", "DECIMATE"); mod.decimate_type = "COLLAPSE"; mod.use_collapse_triangulate = True
    mod.ratio = max(min(target_total / tris(lo), 1.0), 0.0001)
    if vidx is not None:
        vg = lo.vertex_groups.new(name="simplify"); vg.add(vidx.tolist(), 1.0, "REPLACE")
        mod.vertex_group = "simplify"; mod.vertex_group_factor = 1.0; mod.invert_vertex_group = False
    for o in bpy.context.scene.objects: o.select_set(False)
    bpy.context.view_layer.objects.active = lo; lo.select_set(True)
    bpy.ops.object.modifier_apply(modifier="dec")
    for g in list(lo.vertex_groups): lo.vertex_groups.remove(g)


def vertex_colours(o):
    """Tripo base colour under each vertex (first loop's UV), 0..1."""
    img = bpy.data.images["tripo_basecolor"]; w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    me = o.data
    li = np.empty(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", li)
    uv = np.empty(len(me.loops) * 2, np.float32); me.uv_layers["tripo_uv"].data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    first = np.full(len(me.vertices), -1); first[li[::-1]] = np.arange(len(li))[::-1]
    u = uv[first]
    return px[np.clip((u[:, 1] * (h - 1)).astype(int), 0, h - 1), np.clip((u[:, 0] * (w - 1)).astype(int), 0, w - 1), :3]


def regions(co, c):
    x, y, z = co.T; r, g, b = c.T; L = c.mean(1)
    dark = (L < 0.27) & (z > 0.76)          # below the bloomers dark is the leggings, not shag
    pink = (r > 0.75) & (g > 0.45) & (g < 0.82) & (b > 0.5) & (r - g > 0.12)
    gold = (r > 0.47) & (g > 0.31) & (b < 0.75 * g) & (r - b > 0.16)
    hands = (np.abs(x) > 0.36) & (z < 1.05)
    keep = dark | pink | gold | hands
    legs = (z < 0.74) & ~hands
    back = (y > 0.06) & (z > 0.88) & (z < 1.30) & ~keep
    belly = (y < -0.12) & (z > 0.86) & (z < 1.15) & ~keep
    return {"flat": legs | back | belly, "detail": keep, "legs": legs, "back": back, "belly": belly}


body = bpy.data.objects["Cow_body_HIGH"]; lo = copy_low(body)
col = vertex_colours(lo); R = regions(vco(lo), col)
print(f"body {tris(lo):,} tris; vertex counts " + ", ".join(f"{k} {v.sum():,}" for k, v in R.items()), flush=True)
nf = R["flat"].sum() / len(R["flat"])
decimate(lo, tris(lo) - int(tris(lo) * nf * 0.90), np.nonzero(R["flat"])[0])
print(f"after the flat pass: {tris(lo):,} tris ({time.time() - t0:.0f}s)", flush=True)
decimate(lo, BODY_T)
print(f"body LOW: {tris(lo):,} tris ({time.time() - t0:.0f}s)", flush=True)

mask = bpy.data.objects.get("Mask_scan_HIGH")
if mask:
    ml = copy_low(mask); decimate(ml, MASK_T); print(f"mask LOW: {tris(ml):,} tris", flush=True)
for n in ("Horn_long_L", "Horn_short_R", "Horn_wires_R", "Socks", "Tail_cord"):
    hi = bpy.data.objects[f"{n}_HIGH"]; l = copy_low(hi)
    if tris(l) > 3000: decimate(l, max(3000, tris(l) // 2))
    print(f"{n} LOW: {tris(l):,} tris")

bpy.ops.wm.save_as_mainfile(filepath=OUT)


def export_ply(o, path):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); me = ev.to_mesh()
    M = np.array(o.matrix_world)
    V = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", V); V = V.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
    me.calc_loop_triangles()
    T = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get("vertices", T); T = T.reshape(-1, 3)
    if np.linalg.det(M[:3, :3]) < 0: T = T[:, ::-1]
    with open(path, "wb") as fh:
        fh.write(f"ply\nformat binary_little_endian 1.0\nelement vertex {len(V)}\nproperty float x\nproperty float y\nproperty float z\n"
                 f"element face {len(T)}\nproperty list uchar int vertex_indices\nend_header\n".encode())
        fh.write(V.astype("<f4").tobytes())
        rec = np.zeros(len(T), dtype=[("n", "u1"), ("i", "<i4", 3)]); rec["n"] = 3; rec["i"] = T; fh.write(rec.tobytes())
    ev.to_mesh_clear()


total_lo = 0
for o in bpy.context.scene.objects:
    if o.type != "MESH": continue
    export_ply(o, f"{PLY}/{o.name}.ply")
    if not o.name.endswith("_HIGH"): total_lo += tris(o)
print(f"total LOW scene: {total_lo:,} tris (slippers included); saved {OUT} in {time.time() - t0:.0f}s")
