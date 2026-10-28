"""Flatten the bead-like bumps Tripo invented along the glove's side seams and cuff edge.

The beads sit on the line where Tripo fused its front and back views, i.e. where the (heavily smoothed)
surface normal is perpendicular to the front direction (Blender -Y). Within a feathered band around that
line, on terry only (the hoof's beaded rim is a real feature and is kept), and in a band at the bottom of
the cuff, each vertex is moved back onto a smoothed surface along its normal.

usage: python3 -I flatten_seams.py <high.npz from bl_dump_mesh> <out.npz> [passes=2]   (writes V_new + weights)
"""
import sys, numpy as np, scipy.sparse as sp
d = np.load(sys.argv[1]); V = d["V"].astype(np.float64); F = d["F"]; C = d["C"].astype(float)
n = len(V); MM = 1 / 254                       # 1 mm in model units (model 0.972 tall = 24.7 cm)
e = np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]; e = np.r_[e, e[:, ::-1]]
A = sp.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)).tocsr(); A.data[:] = 1
W = sp.diags(1 / np.asarray(A.sum(1)).ravel()) @ A
def smooth(X, it):
    for _ in range(it): X = 0.5 * X + 0.5 * (W @ X)
    return X
def normals(X):
    fn = np.cross(X[F[:, 1]] - X[F[:, 0]], X[F[:, 2]] - X[F[:, 0]]); vn = np.zeros_like(X)
    for k in range(3): np.add.at(vn, F[:, k], fn)
    return vn / (np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12)
PASSES = int(sys.argv[3]) if len(sys.argv) > 3 else 2
vbig = normals(smooth(V, 1500))                       # broad shape: decides where the side seam is
lum = C.mean(1); terry = smooth((lum >= 110).astype(float), 40)          # feathered terry mask
ss = lambda x, a, b: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
seam = 1 - ss(np.abs(vbig[:, 1]), 0.18, 0.40)                           # side-facing band
cuff = 1 - ss(V[:, 2], 8 * MM, 15 * MM)                                 # bottom ~8-15 mm of the cuff
w = smooth(np.clip(np.maximum(seam, cuff) * ss(terry, 0.35, 0.8), 0, 1), 15)   # soft edges, no visible step
V0 = V.copy()
for p in range(PASSES):                               # each pass: move vertices back onto a smoothed surface
    Vs = smooth(V, 150); vn = normals(Vs)             # (beads are ~3-4 mm across)
    h = ((V - Vs) * vn).sum(1)
    V = V - (w * h)[:, None] * vn
Vn = V
moved = np.linalg.norm(Vn - V0, axis=1) / MM
print(f"passes {PASSES}; vertices in band (w>0.5): {np.mean(w>0.5)*100:.1f}%  | moved: mean {moved[w>0.5].mean():.2f} mm, p99 {np.percentile(moved,99):.2f} mm, max {moved.max():.2f} mm")
np.savez(sys.argv[2], V=Vn.astype(np.float32), w=w.astype(np.float32))
