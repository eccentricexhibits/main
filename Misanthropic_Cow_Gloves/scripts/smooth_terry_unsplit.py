"""Smooth the lumpy terry on the whole (not yet split) high-poly glove, leaving the painted hoof untouched
(user request: "the glove looks a tad too lumpy"). Runs between flatten_seams.py and bl_split_fingers.py.

usage: python3 -I smooth_terry_unsplit.py <high.npz (F)> <flat.npz (V)> <planes.json> <out.npz> [radius_mm=10]
Writes out.npz with V (smoothed positions, same vertex order) and w (smoothing weight per vertex), so it drops in
for flat.npz in bl_split_fingers.py.

Weight per vertex: 0 on the hoof (finger vertices above the hoof base plane, feathered over the 1-4 mm below it;
the thumb is never pinned) and on the closed cuff bottom (feathered ~5 mm), 1 elsewhere.
Smoothing S = plain Laplacian diffusion over ~radius ((radius / mean edge)^2 iterations); the result is
2*S(V) - S(S(V)): lumps smaller than the radius go, the overall shape keeps its size (shrinkage is undone to
second order). Taubin lambda/mu smoothing was tried first and was too weak at this scale.
Done before the split on purpose: smoothing the split parts has to pin the cut walls at the web, and the deep
pits just above the web then survive.
"""
import sys, json, numpy as np, scipy.sparse as sp
HI, FL, PJ, OUT = sys.argv[1:5]; RAD = float(sys.argv[5]) if len(sys.argv) > 5 else 10.0
MM = 1 / 254                                                    # model units per mm (glove 0.972 = 24.7 cm)
F = np.load(HI)["F"].astype(np.int64); V = np.load(FL)["V"].astype(np.float64); n = len(V)
P = json.load(open(PJ)); bc, bn = np.array(P["base_co"]), np.array(P["base_no"]); bn /= np.linalg.norm(bn)
hx1 = P["hand_x"][1]

E = np.unique(np.sort(np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]], axis=1), axis=0)
A = sp.coo_matrix((np.ones(len(E) * 2), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr()
Wn = sp.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
el = np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1).mean()

# hoof: no smoothing above the paint edge (fingers only; the thumb sits beyond hand_x)
d = (V - bc) @ bn
t = np.clip((-d - 1 * MM) / (3 * MM), 0, 1); w = np.where(V[:, 0] <= hx1 + 3 * MM, t * t * (3 - 2 * t), 1.0)
# cuff bottom (flat closed cap)
fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]); fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12
fc = V[F].mean(1); cuff = (fn[:, 2] < -0.9) & (fc[:, 2] < V[:, 2].min() + 4 * MM)
cuffv = np.zeros(n, bool); cuffv[F[cuff].ravel()] = True; w[cuffv] = 0
wc = (~cuffv).astype(np.float64)                                # feather the cuff pin ~5 mm along the surface
for _ in range(int((5 * MM / el) ** 2 / 2) + 1): wc = np.minimum(wc, Wn @ wc)
w = np.minimum(w, wc)

it = max(1, int(round((RAD * MM / el) ** 2)))
def S(X):
    for _ in range(it): X = 0.5 * X + 0.5 * (Wn @ X)
    return X
s1 = S(V); s2 = S(s1)
V2 = V + w[:, None] * ((2 * s1 - s2) - V)
mv = np.linalg.norm(V2 - V, axis=1) / MM
print(f"{n} vertices, edge {el / MM:.2f} mm, {it} iterations; terry moved mean {mv[w > 0.5].mean():.2f} mm, "
      f"p99 {np.percentile(mv[w > 0.5], 99):.2f}, max {mv.max():.2f} mm; hoof max move {mv[w == 0].max():.3f} mm")
np.savez(OUT, V=V2.astype(np.float32), w=w.astype(np.float32))
