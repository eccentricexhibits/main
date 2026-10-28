"""Unwrap the three LOW glove parts into ONE shared UV atlas (one texture set per glove), with region
texel weighting and tight packing (playbook stage 8).

usage: python3 bl_unwrap_parts.py <work.blend> <planes.json> [angle_deg=66] [uv_plot.png]
Weights: painted hoof 1.3, terry 1.0, toe inner walls (seen when the toes spread) 0.6,
cuff bottom 0.3, palm top at the web (hidden) 0.25.

The decimated terry is bumpy, so neighbouring faces point in quite different directions and smart-project
cuts hundreds of sliver islands (narrower than a texel, they bake neighbours' colours as specks). So the
unwrap runs on smoothed copies of the parts (same topology, bumps relaxed) and the UVs are copied back
loop-for-loop onto the real meshes; the bumps are 1-2 mm on a 25 cm glove, so the stretch is negligible.
Smart-project still pulls ~1.5 % of the faces out into 1-4-face islands, leaving holes in the big charts;
those faces are smaller than a texel and bake as margin colour (black specks on the terry, white on the
hoof). So smart-project only proposes the charts: every island under MIN_FACES faces is merged into the
neighbouring chart it shares most edges with, seams are marked between charts only, and each chart is
unwrapped with the angle-based unwrapper (no holes, no slivers).
"""
import sys, json, math, time, bpy
import numpy as np
from mathutils import Vector
from bpy_extras import mesh_utils

BL, PJ = sys.argv[1:3]; ANG = float(sys.argv[3]) if len(sys.argv) > 3 else 66.0
PLOT = sys.argv[4] if len(sys.argv) > 4 else None
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=BL)
P = json.load(open(PJ)); base_co, base_no = Vector(P["base_co"]), Vector(P["base_no"]).normalized()
MM = 1 / 254
real = [bpy.data.objects[n] for n in ("Glove_Palm", "Toe_IndexMiddle", "Toe_RingLittle")]
SMOOTH_IT = 30
parts = []
for o in real:                                   # smoothed stand-ins with identical topology
    c = o.copy(); c.data = o.data.copy(); c.name = o.name + "_uvproxy"; bpy.context.scene.collection.objects.link(c)
    c.parent = None; c.matrix_world = o.matrix_world.copy()
    mod = c.modifiers.new("sm", "LAPLACIANSMOOTH"); mod.iterations = SMOOTH_IT; mod.lambda_factor = 0.5
    mod.use_volume_preserve = True; mod.use_normalized = True
    with bpy.context.temp_override(object=c, active_object=c, selected_objects=[c]):
        bpy.ops.object.modifier_apply(modifier="sm")
    parts.append(c)

for o in bpy.data.objects: o.select_set(False)
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(ANG), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.object.mode_set(mode="OBJECT")

import bmesh
MIN_FACES = 40
for o in parts:
    me = o.data; chart = np.full(len(me.polygons), -1, np.int64)
    for k, isl in enumerate(mesh_utils.mesh_linked_uv_islands(me)): chart[isl] = k
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    nb = [[g.index for e in f.edges for g in e.link_faces if g.index != f.index] for f in bm.faces]
    for _ in range(20):                                    # fold small islands into their largest neighbour
        sizes = np.bincount(chart); small = sizes[chart] < MIN_FACES
        if not small.any(): break
        for fi in np.nonzero(small)[0]:
            ids = [chart[g] for g in nb[fi] if sizes[chart[g]] >= MIN_FACES]
            if ids: chart[fi] = max(set(ids), key=ids.count)
        # small islands with no big neighbour yet: merge into any neighbour
        sizes = np.bincount(chart)
        for fi in np.nonzero(sizes[chart] < MIN_FACES)[0]:
            ids = [chart[g] for g in nb[fi]]
            if ids: chart[fi] = max(set(ids), key=lambda c: sizes[c])
    for e in bm.edges:
        lf = e.link_faces
        e.seam = bool(len(lf) != 2 or chart[lf[0].index] != chart[lf[1].index])
    bm.to_mesh(me); bm.free()
    print(o.name, "charts:", len(set(chart.tolist())), flush=True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.unwrap(method="ANGLE_BASED", fill_holes=True, correct_aspect=True, margin=0.0)
bpy.ops.object.mode_set(mode="OBJECT")

counts = {}
for o in parts:
    me = o.data; mw = o.matrix_world; mats = [m.name if m else "" for m in me.materials]
    name = o.name.replace("_uvproxy", "")
    zmin = min((mw @ v.co).z for v in me.vertices)
    islands = mesh_utils.mesh_linked_uv_islands(me); uvl = me.uv_layers.active.data
    for isl in islands:
        a = 0.0; c = Vector((0, 0, 0)); n = Vector((0, 0, 0)); cap = 0.0
        for pi in isl:
            p = me.polygons[pi]; a += p.area; c += (mw @ p.center) * p.area; n += (mw.to_3x3() @ p.normal) * p.area
            if mats[p.material_index] in ("Hoof_InnerWall", "Terry_Inner"): cap += p.area
        if a == 0: continue
        c /= a; n.normalize()
        if cap > 0.5 * a:
            s = 0.25 if name == "Glove_Palm" else 0.6           # palm top at the web is never seen
        elif name == "Glove_Palm" and n.z < -0.8 and c.z < zmin + 6 * MM:
            s = 0.3                                                # closed cuff bottom
        elif name != "Glove_Palm" and (c - base_co).dot(base_no) > 0:
            s = 1.3                                                # painted hoof
        else:
            s = 1.0
        counts[s] = counts.get(s, 0) + 1
        if s == 1.0: continue
        loops = [li for pi in isl for li in me.polygons[pi].loop_indices]
        cu = sum((uvl[li].uv for li in loops), Vector((0, 0))) / len(loops)
        for li in loops: uvl[li].uv = cu + (uvl[li].uv - cu) * s
print("islands by weight:", dict(sorted(counts.items())), f"{time.time()-t0:.0f}s", flush=True)

bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.pack_islands(shape_method="CONCAVE", margin_method="FRACTION", margin=0.001, rotate=True, scale=True)
bpy.ops.object.mode_set(mode="OBJECT")
for o, c in zip(real, parts):                    # copy the UVs back onto the real meshes, then drop the proxies
    uv = np.empty(len(c.data.loops) * 2, np.float32); c.data.uv_layers.active.data.foreach_get("uv", uv)
    o.data.uv_layers.active.data.foreach_set("uv", uv); o.data.update()
    bpy.data.objects.remove(c)
parts = real
bpy.ops.wm.save_as_mainfile(filepath=BL)

# coverage + plot (each part tinted, shaded by normal)
area = 0.0; img = None
if PLOT:
    from PIL import Image, ImageDraw
    S = 2048; img = Image.new("RGB", (S, S), (20, 20, 24)); d = ImageDraw.Draw(img)
import collections
nisl = sum(len(mesh_utils.mesh_linked_uv_islands(o.data)) for o in parts); print("islands after copy-back:", nisl)
tint = {"Glove_Palm": (1.0, 0.95, 0.8), "Toe_IndexMiddle": (1.0, 0.6, 0.55), "Toe_RingLittle": (0.55, 0.7, 1.0)}
for o in parts:
    me = o.data; uv = np.empty(len(me.loops) * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    for p in me.polygons:
        a = uv[list(p.loop_indices)]
        area += abs(sum(a[i][0] * a[(i + 1) % len(a)][1] - a[(i + 1) % len(a)][0] * a[i][1] for i in range(len(a)))) / 2
        if img:
            k = 0.55 + 0.45 * p.normal.z * 0.5 + 0.2; tc = tint[o.name]
            d.polygon([(u * S, (1 - v) * S) for u, v in a], fill=tuple(int(255 * min(1, max(0, k * c))) for c in tc))
if img: img.save(PLOT)
print(f"UV coverage {area*100:.1f}%  ({time.time()-t0:.0f}s)")
