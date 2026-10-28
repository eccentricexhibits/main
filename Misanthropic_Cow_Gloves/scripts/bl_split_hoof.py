"""Split the cleaned high-poly glove into three objects for animation:
  Glove_Mitten          terry mitten; its finger end continues ~2 cm up inside the toes, 3 mm smaller,
                        so no hole shows when a toe opens
  Hoof_Toe_IndexMiddle  thumb-side toe (+X), closed solid with a flat inner (cleft) wall
  Hoof_Toe_RingLittle   little-finger-side toe (-X)
Both toes have their origin (pivot) at the bottom of the cleft on the hoof base, mid-thickness, and are
parented to the mitten. Cut faces get their own materials (Hoof_InnerWall / Terry_Inner).

usage: python3 bl_split_hoof.py <glove_high.blend> <flat.npz (V)> <planes.json> <out.blend>
Blender frame: Z up, back of hand = -Y, thumb = +X.
"""
import sys, json, bpy, bmesh
import numpy as np
from mathutils import Vector

BL, FLAT, PJ, OUT = sys.argv[1:5]
bpy.ops.wm.open_mainfile(filepath=BL)
P = json.load(open(PJ))
MM = 1 / 254
src = bpy.data.objects["Glove_HIGH"]; me = src.data
V = np.load(FLAT)["V"].astype(np.float32)
assert len(V) == len(me.vertices)
me.vertices.foreach_set("co", V.ravel()); me.update()

base_co, base_no = Vector(P["base_co"]), Vector(P["base_no"]).normalized()
cleft_co, cleft_no = Vector(P["cleft_co"]), Vector(P["cleft_no"]).normalized()
pivot = Vector(P["pivot"])

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

def cut(o, co, no, keep_positive, wall_mat):
    """Cut o by a plane, keep one side, fill the opening flat, give the cap its own material."""
    bm = bmesh.new(); bm.from_mesh(o.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=co, plane_no=no,
                           clear_inner=keep_positive, clear_outer=not keep_positive)
    bnd = [e for e in bm.edges if e.is_boundary]
    res = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd)
    if wall_mat.name not in [m.name for m in o.data.materials if m]:
        o.data.materials.append(wall_mat)
    mi = [m.name if m else "" for m in o.data.materials].index(wall_mat.name)
    for f in res["geom"]:
        if isinstance(f, bmesh.types.BMFace): f.material_index = mi
    left = [e for e in bm.edges if e.is_boundary]          # any tiny gap the fill missed
    if left:
        bmesh.ops.holes_fill(bm, edges=left, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    nb = len([e for e in bm.edges if not e.is_manifold])
    bm.to_mesh(o.data); bm.free(); o.data.update()
    return nb

# --- mitten: cut 2 cm above the hoof base, then shrink everything above the base 3 mm inward (feathered
#     over 5 mm) so the finger end sits inside the toes. Cutting first keeps the cap a clean flat loop.
mit = copy_obj("Glove_Mitten")
open_mit = cut(mit, base_co + base_no * (20 * MM), base_no, keep_positive=False, wall_mat=M_TERRY_IN)
bm = bmesh.new(); bm.from_mesh(mit.data); bm.normal_update()
moves = []
for v in bm.verts:
    hgt = (v.co - base_co).dot(base_no)
    if hgt > -2 * MM:
        t = min(1.0, (hgt + 2 * MM) / (5 * MM)); moves.append((v, v.normal * (3 * MM * t * t * (3 - 2 * t))))
for v, d in moves: v.co -= d
bm.to_mesh(mit.data); bm.free(); mit.data.update()

# --- hoof: everything above the base plane, then split along the cleft
hoof = copy_obj("Hoof_tmp")
open_hoof = cut(hoof, base_co, base_no, keep_positive=True, wall_mat=M_WALL)
toe_a = copy_obj("Hoof_Toe_IndexMiddle"); toe_a.data = hoof.data.copy()
toe_b = copy_obj("Hoof_Toe_RingLittle"); toe_b.data = hoof.data.copy()
open_a = cut(toe_a, cleft_co, cleft_no, keep_positive=True, wall_mat=M_WALL)     # +X = thumb side
open_b = cut(toe_b, cleft_co, cleft_no, keep_positive=False, wall_mat=M_WALL)
bpy.data.objects.remove(hoof); bpy.data.objects.remove(src)
print("non-manifold edges after cuts: mitten", open_mit, "| toe A", open_a, "| toe B", open_b)

# --- origins: toes at the cleft base (pivot); mitten at the cuff's bottom centre
def set_origin(o, p):
    o.data.transform(__import__("mathutils").Matrix.Translation(-p)); o.location = p
mv = np.empty(len(mit.data.vertices) * 3, np.float32); mit.data.vertices.foreach_get("co", mv); mv = mv.reshape(-1, 3)
cuff = mv[mv[:, 2] < mv[:, 2].min() + 5 * MM]
set_origin(mit, Vector((float(cuff[:, 0].mean()), float(cuff[:, 1].mean()), float(mv[:, 2].min()))))
for t in (toe_a, toe_b):
    set_origin(t, pivot)
bpy.context.view_layer.update()            # matrix_world must reflect the new origins before parenting
for t in (toe_a, toe_b):
    t.parent = mit; t.matrix_parent_inverse = mit.matrix_world.inverted()
bpy.context.view_layer.update()

for o in (mit, toe_a, toe_b):
    vv = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", vv); vv = vv.reshape(-1, 3)
    print(f"{o.name}: {len(o.data.polygons):,} faces, origin {[round(c, 4) for c in o.location]}, size {np.round(np.ptp(vv, 0) * 25.4, 1)} cm")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
