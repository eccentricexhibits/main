"""SUPERSEDED by smooth_terry_unsplit.py: smoothing the split parts must pin the cut walls at the web, so the
deep pits just above the web survive. Kept for reference.

Smooth the lumpy terry (user request), leaving the painted hoof untouched.

usage: python3 bl_smooth_terry.py <work_uv.blend> <planes.json> <out.blend> <radius_mm>

1. On each full-detail part (<part>_HIGH): low-pass smoothing of the TERRY only, with a
   per-vertex weight that is 0 on the hoof (finger-pair vertices above the hoof base plane, feathered over the
   1-4 mm below it), on the flat cut caps and on the closed cuff bottom (feathered over ~5 mm on the palm, ~2 mm on
   the toes), 1 elsewhere.
   radius_mm sets how large a lump gets smoothed away. Smoothing S = plain Laplacian diffusion over ~radius
   ((radius / mean edge)^2 iterations); the result is 2*S(V) - S(S(V)), which removes lumps smaller than the radius
   but restores the shrinkage of the overall shape to second order. (Taubin lambda/mu smoothing was tried first:
   its pass band keeps lumps this size, it moved the surface only 0.1-0.25 mm.)
2. Each low-poly part is snapped onto its smoothed HIGH surface (Shrinkwrap, nearest surface point), with the same
   weights, so topology, UVs, mask and pivots are unchanged.
Run on the pre-bake work file (it still names the cap materials).
"""
import sys, json, time, bpy
import numpy as np, scipy.sparse as sp

BL, PJ, OUT, RAD = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=BL)
bpy.context.view_layer.update()                     # stored matrix_world can be stale (identity) until evaluated
P = json.load(open(PJ)); bc, bn = np.array(P["base_co"]), np.array(P["base_no"]); bn /= np.linalg.norm(bn)
names = ("Glove_Palm", "Toe_IndexMiddle", "Toe_RingLittle")
for o in bpy.data.objects: o.hide_set(False); o.hide_viewport = False
hcol = bpy.data.collections.get("HIGH")
if hcol: hcol.hide_viewport = False

def arrays(o):
    me = o.data; n = len(me.vertices)
    V = np.empty(n * 3, np.float64); me.vertices.foreach_get("co", V); V = V.reshape(-1, 3)
    E = np.empty(len(me.edges) * 2, np.int64); me.edges.foreach_get("vertices", E); E = E.reshape(-1, 2)
    mw = np.array(o.matrix_world)
    return V, E, mw

def weights(o, V, E, mw, MM):
    """1 = smooth freely, 0 = keep (hoof paint, cut caps, cuff bottom), feathered on the mesh graph."""
    me = o.data; n = len(V); W = V @ mw[:3, :3].T + mw[:3, 3]
    mats = [m.name if m else "" for m in me.materials]; capi = [i for i, nm in enumerate(mats) if nm in ("Hoof_InnerWall", "Terry_Inner")]
    mi = np.empty(len(me.polygons), np.int64); me.polygons.foreach_get("material_index", mi)
    nrm = np.empty(len(me.polygons) * 3); me.polygons.foreach_get("normal", nrm); nrm = nrm.reshape(-1, 3) @ mw[:3, :3].T
    cen = np.empty(len(me.polygons) * 3); me.polygons.foreach_get("center", cen); cen = cen.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
    pinf = np.isin(mi, capi)
    if o.name.startswith("Glove_Palm"):
        pinf |= (nrm[:, 2] < -0.9) & (cen[:, 2] < W[:, 2].min() + 4 * MM)
    lt = np.empty(len(me.polygons), np.int64); me.polygons.foreach_get("loop_total", lt)
    lv = np.empty(len(me.loops), np.int64); me.loops.foreach_get("vertex_index", lv)
    pinv = np.zeros(n, bool); pinv[lv[np.repeat(pinf, lt)]] = True
    w = (~pinv).astype(np.float64)
    if not o.name.startswith("Glove_Palm"):                       # hoof: no smoothing above (and just below) the paint edge
        d = (W - bc) @ bn
        t = np.clip((-d - 1 * MM) / (3 * MM), 0, 1); w *= t * t * (3 - 2 * t)
    # feather the pins along the surface (graph diffusion): ~5 mm on the palm, ~2 mm on the short toe terry band
    # (20 mm between the web cut and the hoof; a wide feather would pin all of it)
    fe = 5 if o.name.startswith("Glove_Palm") else 2
    A = sp.coo_matrix((np.ones(len(E) * 2), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr()
    Wn = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
    el = np.linalg.norm(W[E[:, 0]] - W[E[:, 1]], axis=1).mean()
    for _ in range(int((fe * MM / el) ** 2 / 2) + 1):
        w = np.minimum(w, Wn @ w)
    return w, Wn, el

def lowpass(V, Wn, w, iters):
    def S(X):
        for _ in range(iters): X = 0.5 * X + 0.5 * (Wn @ X)
        return X
    s1 = S(V); s2 = S(s1)
    return V + w[:, None] * ((2 * s1 - s2) - V)

MM = None
for n in names:
    hi = bpy.data.objects[n + "_HIGH"]; V, E, mw = arrays(hi)
    if MM is None:                                                  # model units per mm (glove = 247 mm tall)
        zs = []
        for x in names:
            Vx, _, mx = arrays(bpy.data.objects[x]); zs.append((Vx @ mx[:3, :3].T + mx[:3, 3])[:, 2])
        zs = np.concatenate(zs); MM = (zs.max() - zs.min()) / 247.0
    w, Wn, el = weights(hi, V, E, mw, MM)
    it = max(1, int(round((RAD * MM / el) ** 2)))
    V2 = lowpass(V, Wn, w, it)
    mv = np.linalg.norm(V2 - V, axis=1) / MM
    hi.data.vertices.foreach_set("co", V2.astype(np.float32).ravel()); hi.data.update()
    print(f"{n}_HIGH: {it} diffusion iterations (edge {el/MM:.2f} mm), moved mean {mv[w > 0.5].mean():.2f} mm, max {mv.max():.2f} mm", flush=True)
    lo = bpy.data.objects[n]; VL, EL, mwl = arrays(lo); wl, _, _ = weights(lo, VL, EL, mwl, MM)
    vg = lo.vertex_groups.new(name="snap")
    q = np.round(wl, 2)
    for x in np.unique(q[q > 0]): vg.add(np.nonzero(q == x)[0].tolist(), float(x), "REPLACE")
    mod = lo.modifiers.new("snap", "SHRINKWRAP"); mod.target = hi; mod.wrap_method = "NEAREST_SURFACEPOINT"; mod.vertex_group = "snap"
    with bpy.context.temp_override(object=lo, active_object=lo, selected_objects=[lo]):
        bpy.ops.object.modifier_apply(modifier="snap")
    lo.vertex_groups.remove(lo.vertex_groups["snap"])      # (the old Python handle is stale after modifier_apply)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT, round(time.time() - t0, 1), "s")
