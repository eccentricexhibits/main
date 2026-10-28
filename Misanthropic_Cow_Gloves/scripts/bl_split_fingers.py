"""Split the cleaned high-poly glove the way the real costume moves: two rigid finger pairs that part like a
Vulcan salute, between the middle and ring fingers, pivoting at the finger web.

  Glove_Palm            palm, thumb and cuff, cut flat at the web (optionally with a hidden stub, see STUB)
  Toe_IndexMiddle       thumb side (+X): terry finger compartment + its hoof cap, one rigid object
  Toe_RingLittle        little-finger side (-X)
Both toes: closed solids, flat inner walls along the cleft (paint above the hoof base, terry below), origin
(pivot) at the web on the cleft line, mid-thickness; parented to the palm. Spread = rotate about local Y,
curl = local X.

usage: python3 bl_split_fingers.py <glove_high.blend> <flat.npz (V)> <planes.json> <out.blend> [web_drop_mm=20] [stub_mm=0]
web_drop_mm: how far below the hoof base (the paint edge) the finger web / pivot sits.
stub_mm: optional palm stub reaching up inside the fingers (3 mm smaller). Not needed for spreading: with the
pivot at the web, the bottom of each toe swings down into the palm. A stub that crosses the deep crease
under the cleft folds when shrunk and pokes out between the toes, so the default is 0.
Blender frame: Z up, back of hand = -Y, thumb = +X.
"""
import sys, json, bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix

BL, FLAT, PJ, OUT = sys.argv[1:5]
DROP = float(sys.argv[5]) if len(sys.argv) > 5 else 20.0
STUB = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
bpy.ops.wm.open_mainfile(filepath=BL)
P = json.load(open(PJ))
MM = 1 / 254
src = bpy.data.objects["Glove_HIGH"]; me = src.data
V = np.load(FLAT)["V"].astype(np.float32); assert len(V) == len(me.vertices)
me.vertices.foreach_set("co", V.ravel()); me.update()

base_co, base_no = Vector(P["base_co"]), Vector(P["base_no"]).normalized()
cleft_co, cleft_no = Vector(P["cleft_co"]), Vector(P["cleft_no"]).normalized()
web_co = base_co - base_no * (DROP * MM)                 # knuckle/web plane: parallel to the hoof base
hx0, hx1 = P["hand_x"]

def mat(name, rgb, rough):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = 0.0
    return m
M_WALL = mat("Hoof_InnerWall", (0.02, 0.02, 0.022), 0.55)
M_TERRY_IN = mat("Terry_Inner", (0.75, 0.72, 0.63), 0.9)

def copy_obj(name):
    o = src.copy(); o.data = src.data.copy(); o.name = name; o.data.name = name
    bpy.context.collection.objects.link(o); return o

def mat_index(o, m):
    if m.name not in [x.name for x in o.data.materials if x]: o.data.materials.append(m)
    return [x.name if x else "" for x in o.data.materials].index(m.name)

def cut(o, co, no, keep_positive, cap_mat, split_cap_at=None, skip_x_above=None):
    """Cut o by a plane, keep one side, fill the opening flat. The cap gets cap_mat; if split_cap_at is
    given (co, no, mat_above), cap faces above that plane get mat_above instead. skip_x_above: leave every
    face whose centre lies beyond this x (the thumb) out of the cut."""
    bm = bmesh.new(); bm.from_mesh(o.data)
    faces = [f for f in bm.faces if skip_x_above is None or f.calc_center_median().x <= skip_x_above]
    geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + faces
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=co, plane_no=no,
                           clear_inner=keep_positive, clear_outer=not keep_positive)
    bnd = [e for e in bm.edges if e.is_boundary]
    cap = [f for f in bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd)["geom"]
           if isinstance(f, bmesh.types.BMFace)]
    left = [e for e in bm.edges if e.is_boundary]
    if left:
        cap += [f for f in bmesh.ops.holes_fill(bm, edges=left, sides=0)["faces"]]
    mi = mat_index(o, cap_mat)
    for f in cap: f.material_index = mi
    if split_cap_at:
        sco, sno, smat = split_cap_at
        geom = list({v for f in cap for v in f.verts}) + list({e for f in cap for e in f.edges}) + cap
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=sco, plane_no=sno)
        mi2 = mat_index(o, smat)
        for f in bm.faces:
            if f.material_index == mi and (f.calc_center_median() - sco).dot(sno) > 0: f.material_index = mi2
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(o.data); bm.free(); o.data.update()

def keep_largest(o):
    """Drop loose pieces (e.g. the thumb tip, which rises just above the web plane)."""
    bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    seen, comps = set(), []
    for f in bm.faces:
        if f.index in seen: continue
        stack, comp = [f], []
        seen.add(f.index)
        while stack:
            g = stack.pop(); comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); stack.append(h)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    drop = [f for c in comps[1:] for f in c]
    bmesh.ops.delete(bm, geom=drop, context='FACES')
    bm.to_mesh(o.data); bm.free(); o.data.update()
    return len(comps), len(drop)

def nonmanifold(o):
    bm = bmesh.new(); bm.from_mesh(o.data); n = sum(1 for e in bm.edges if not e.is_manifold); bm.free(); return n

# --- palm: cut at the web plane (+ optional stub, pulled 3 mm inward, feathered over 5 mm, so it hides
#     inside the fingers). The thumb (beyond the hand's edge) is never moved.
palm = copy_obj("Glove_Palm")
cut(palm, web_co + base_no * (STUB * MM), base_no, keep_positive=False, cap_mat=M_TERRY_IN,
    skip_x_above=hx1 + 0.003)                             # the thumb tip rises above the web plane: keep it
if STUB > 0:
    bm = bmesh.new(); bm.from_mesh(palm.data); bm.normal_update(); moves = []
    for v in bm.verts:
        if v.co.x > hx1 + 0.003: continue                 # thumb
        hgt = (v.co - web_co).dot(base_no)
        if hgt > -2 * MM:
            t = min(1.0, (hgt + 2 * MM) / (5 * MM)); moves.append((v, v.normal * (3 * MM * t * t * (3 - 2 * t))))
    for v, d in moves: v.co -= d
    bm.to_mesh(palm.data); bm.free(); palm.data.update()

# --- fingers: everything above the web plane, split along the cleft; inner walls are paint above the hoof
#     base and terry below it
fing = copy_obj("Fingers_tmp")
cut(fing, web_co, base_no, keep_positive=True, cap_mat=M_TERRY_IN)
toe_a = copy_obj("Toe_IndexMiddle"); toe_a.data = fing.data.copy()
toe_b = copy_obj("Toe_RingLittle"); toe_b.data = fing.data.copy()
for t, side in ((toe_a, True), (toe_b, False)):            # +X = thumb side
    cut(t, cleft_co, cleft_no, keep_positive=side, cap_mat=M_TERRY_IN, split_cap_at=(base_co, base_no, M_WALL))
    print(t.name, "pieces before cleanup / faces dropped:", keep_largest(t))
bpy.data.objects.remove(fing); bpy.data.objects.remove(src)

# --- pivot: the web on the cleft line, at the hand's mid-thickness there
pv = np.empty(len(palm.data.vertices) * 3, np.float32); palm.data.vertices.foreach_get("co", pv); pv = pv.reshape(-1, 3)
d_web = (pv - np.array(web_co)) @ np.array(base_no)
ring = pv[(np.abs(d_web) < 3 * MM) & (pv[:, 0] < hx1)]
ym = float((ring[:, 1].min() + ring[:, 1].max()) / 2)
# point on both planes with y = ym: solve for x, z
A = np.array([[cleft_no.x, cleft_no.z], [base_no.x, base_no.z]])
b = np.array([cleft_no.dot(cleft_co) - cleft_no.y * ym, base_no.dot(web_co) - base_no.y * ym])
px, pz = np.linalg.solve(A, b); pivot = Vector((float(px), ym, float(pz)))

def set_origin(o, p):
    o.data.transform(Matrix.Translation(-p)); o.location = p
cuff = pv[pv[:, 2] < pv[:, 2].min() + 5 * MM]
set_origin(palm, Vector((float(cuff[:, 0].mean()), float(cuff[:, 1].mean()), float(pv[:, 2].min()))))
for t in (toe_a, toe_b): set_origin(t, pivot)
bpy.context.view_layer.update()            # matrix_world must reflect the new origins before parenting
for t in (toe_a, toe_b):
    t.parent = palm; t.matrix_parent_inverse = palm.matrix_world.inverted()
bpy.context.view_layer.update()

for o in (palm, toe_a, toe_b):
    vv = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", vv); vv = vv.reshape(-1, 3)
    print(f"{o.name}: {len(o.data.polygons):,} faces, non-manifold edges {nonmanifold(o)}, origin {[round(c, 4) for c in o.matrix_world.translation]}, size {np.round(np.ptp(vv, 0) * 25.4, 1)} cm")
print(f"web/pivot {DROP:.0f} mm below the hoof base, {float((pivot.z) / MM / 10):.1f} cm above the cuff bottom")
json.dump(dict(pivot=list(pivot), web_drop_mm=DROP, stub_mm=STUB), open(OUT.replace(".blend", "_pivot.json"), "w"))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
