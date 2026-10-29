"""Displacement mask for the terry (UV atlas, 1 = displace, 0 = keep the surface where it is).

usage: python3 bl_make_displace_mask.py <work_uv.blend> <geom_dir> <mask_paint.png> <out.png> [feather_mm=3] [size=4096]
0 on the painted hoof (mask_paint) and on the flat cut walls (Hoof_InnerWall / Terry_Inner faces, so run on the
pre-bake work file that still names them). Ramps from 0 to 1 over feather_mm of 3D distance from the walls' outer
edges: the palm and the toes project the terry tile from different origins, so at the web their displacements
differ; fading both to 0 at the shared cut edge keeps the parts meeting without cracks.
"""
import sys, os, bpy, numpy as np, cv2
from PIL import Image
from scipy.spatial import cKDTree
BL, G, MP, OUT = sys.argv[1:5]
FE = float(sys.argv[5]) if len(sys.argv) > 5 else 3.0; SIZE = int(sys.argv[6]) if len(sys.argv) > 6 else 4096
bpy.ops.wm.open_mainfile(filepath=BL); bpy.context.view_layer.update()
names = ("Glove_Palm", "Toe_IndexMiddle", "Toe_RingLittle")
pos = np.load(os.path.join(G, f"geom_position_{SIZE}.npy"))                 # rows top first (v = 1), world units
cov = pos[..., 3] > 0.5
zs = np.concatenate([[(bpy.data.objects[n].matrix_world @ v.co).z for v in bpy.data.objects[n].data.vertices] for n in names])
MM = (zs.max() - zs.min()) / 247.0                                          # units per mm (glove 247 mm tall)

wall = np.zeros((SIZE, SIZE), np.uint8); pts = []
for n in names:
    o = bpy.data.objects[n]; me = o.data; mw = np.array(o.matrix_world)
    mats = [m.name if m else "" for m in me.materials]; capi = [i for i, nm in enumerate(mats) if nm in ("Hoof_InnerWall", "Terry_Inner")]
    mi = np.empty(len(me.polygons), np.int64); me.polygons.foreach_get("material_index", mi); cap = np.isin(mi, capi)
    uv = np.empty(len(me.loops) * 2); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    for p in me.polygons:                                                   # wall texels
        if cap[p.index]:
            q = uv[list(p.loop_indices)]; q = np.column_stack([q[:, 0] * SIZE - 0.5, (1 - q[:, 1]) * SIZE - 0.5])
            cv2.fillPoly(wall, [np.round(q * 16).astype(np.int32)], 1, shift=4)
    V = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", V); V = V.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
    ef = {}                                                                 # edges between wall and outer faces
    for p in me.polygons:
        for ek in p.edge_keys: ef.setdefault(ek, set()).add(bool(cap[p.index]))
    for (a, b), s in ef.items():
        if len(s) == 2:
            k = max(2, int(np.linalg.norm(V[a] - V[b]) / (0.3 * MM)) + 1)
            pts.append(V[a] + np.linspace(0, 1, k)[:, None] * (V[b] - V[a]))
pts = np.concatenate(pts); print(f"wall edge samples: {len(pts)}", flush=True)

paint = np.asarray(Image.open(MP).convert("L")).astype(np.float32) / 255
terry = cov & (paint < 0.5) & (wall == 0)
d = np.full((SIZE, SIZE), np.inf, np.float32)
d[terry] = cKDTree(pts).query(pos[terry][:, :3], k=1, workers=-1)[0] / MM
t = np.clip((d - 0.5) / (FE - 0.5), 0, 1); m = t * t * (3 - 2 * t)
m = m * (1 - paint)                                                         # soft at the paint edge (1-2 px)
m[~terry] = 0
m = cv2.GaussianBlur(m, (0, 0), 0.7) * terry                                # no hard texel steps
# pad every island outward with its own edge values (like a bake margin): with linear filtering, island edges
# would otherwise blend with the empty 0 texels and the displacement would dip along every UV seam
from scipy import ndimage as nd
_, (iy, ix) = nd.distance_transform_edt(~cov, return_indices=True)
m = np.where(cov, m, m[iy, ix])
Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).save(OUT)
print(f"saved {OUT}: displaced texels {((m > 0.5) & cov).sum() / max(cov.sum(), 1) * 100:.1f} % of covered, feather {FE} mm")
