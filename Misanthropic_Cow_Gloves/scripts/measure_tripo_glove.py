"""Measure a Tripo glove model (OBJ + basecolor/metallic/roughness maps) against the real glove.
usage: python3 -I measure_tripo_glove.py <model_dir_with_obj> [real_length_cm]"""
import sys, os, glob
import numpy as np, trimesh
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
D = sys.argv[1]; REAL = float(sys.argv[2]) if len(sys.argv) > 2 else 24.7
obj = glob.glob(os.path.join(D, "*.obj"))[0]
m = trimesh.load(obj, process=False, force="mesh")
V = m.vertices; F = m.faces
lo, hi = m.bounds; L = hi[1] - lo[1]; cm = REAL / L
print(f"triangles {len(F):,}  vertices {len(V):,}  extent X {hi[0]-lo[0]:.3f} Y {L:.3f} Z {hi[2]-lo[2]:.3f}  (1 unit = {cm:.1f} cm)")

# per-vertex base colour from the UV map
bc = np.asarray(Image.open(glob.glob(os.path.join(D, "*basecolor*"))[0]).convert("RGB"))
uv = m.visual.uv; H, W = bc.shape[:2]
px = np.clip((uv[:, 0] % 1) * (W - 1), 0, W - 1).astype(int); py = np.clip((1 - uv[:, 1] % 1) * (H - 1), 0, H - 1).astype(int)
col = bc[py, px].astype(float); lum = col.mean(1); dark = lum < 90
y = (V[:, 1] - lo[1]) / L
hoof_lo = np.percentile(y[dark], 1); print(f"hoof (dark) from {100*hoof_lo:.0f}% height up -> hoof = top {100*(1-hoof_lo):.0f}% of length (real ~36%)")

# width (X, excluding the thumb side beyond the hoof width) and thickness (Z) along the height
def band(f, w=0.01):
    s = np.abs(y - f) < w; return V[s]
hx = band(0.85); x0, x1 = hx[:, 0].min(), hx[:, 0].max()
print(f"hoof width at 85%: {(x1-x0)*cm:.1f} cm")
for f in (0.05, 0.25, 0.45, 0.6, 0.7, 0.85, 0.95):
    b = band(f); bx = b[(b[:, 0] > x0 - 0.02) & (b[:, 0] < x1 + 0.02)] if f > 0.3 else b
    print(f"  at {int(f*100):>2}%: width {np.ptp(b[:,0])*cm:5.1f} cm (all incl. thumb)  thickness {np.ptp(b[:,2])*cm:4.1f} cm")
# the thumb: vertices beyond the wrist's X range (at 25 % height) between 30 and 75 % height
wb = band(0.25); wx0, wx1 = wb[:, 0].min(), wb[:, 0].max()
thumb = V[((V[:, 0] > wx1 + 0.01) | (V[:, 0] < wx0 - 0.01)) & (y > 0.3) & (y < 0.75)]
if len(thumb):
    ty = (thumb[:, 1] - lo[1]) / L
    print(f"thumb: tip at {100*ty.max():.0f}% height, sticks out {max(thumb[:,0].max()-wx1, wx0-thumb[:,0].min())*cm:.1f} cm beyond the wrist line")

# cleft depth: ray casts across the hoof from the front (-Z rays) and the back (+Z rays)
for f in (0.7, 0.8, 0.9):
    yy = lo[1] + f * L; xs = np.linspace(x0, x1, 81)
    out = []
    for z0, dz in ((hi[2] + 0.1, -1.0), (lo[2] - 0.1, 1.0)):
        o = np.c_[xs, np.full_like(xs, yy), np.full_like(xs, z0)]
        loc, idx, _ = m.ray.intersects_location(o, np.tile([0, 0, dz], (len(o), 1)), multiple_hits=False)
        z = np.full(len(xs), np.nan); z[idx] = loc[:, 2] * -dz      # height above the respective side
        out.append((np.nanmax(z) - np.nanmin(z[30:51])) * cm * 10)
    print(f"cleft at {int(f*100)}% height: groove depth front {out[0]:.1f} mm, back {out[1]:.1f} mm, hoof thickness {np.ptp(band(f)[:,2])*cm*10:.0f} mm")

for name in ("metallic", "roughness"):
    p = glob.glob(os.path.join(D, f"*{name}*"))
    if p:
        a = np.asarray(Image.open(p[0]).convert("L")).astype(float) / 255
        h, w = a.shape
        sel = a[np.clip((1 - uv[:, 1] % 1) * (h - 1), 0, h - 1).astype(int), np.clip((uv[:, 0] % 1) * (w - 1), 0, w - 1).astype(int)]
        print(f"{name}: mean {sel.mean():.3f}  p50 {np.percentile(sel,50):.3f}  p95 {np.percentile(sel,95):.3f}  max {sel.max():.3f}  | hoof mean {sel[dark].mean():.3f}  terry mean {sel[~dark].mean():.3f}")

# connected components on position-welded vertices (Tripo splits vertices at UV seams); light on RAM
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
_, inv = np.unique(np.round(V, 6), axis=0, return_inverse=True); inv = inv.ravel()
f = inv[F]; e = np.r_[f[:, [0, 1]], f[:, [1, 2]]]
n = inv.max() + 1
k, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)), directed=False)
sizes = np.bincount(lab[f[:, 0]], minlength=k)
print(f"connected components: {k}, faces in largest {sizes.max():,} ({100*sizes.max()/len(F):.2f}%), others total {len(F)-sizes.max():,}")
