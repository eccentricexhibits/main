"""Fit the two cutting planes for splitting the hoof (Blender frame: Z up, back of hand -Y, thumb +X).
- BASE plane: through the edge where black paint meets cream terry (least squares, outliers dropped),
  restricted to the hand (the thumb is excluded).
- CLEFT plane: through the bottom of the cleft groove, found front (-Y) and back (+Y) at several heights.
usage: python3 -I fit_hoof_planes.py <high.npz (V,F,C)> <flat.npz (V)> <planes.json>"""
import sys, json, numpy as np, trimesh
d = np.load(sys.argv[1]); F = d["F"]; C = d["C"].astype(float); V = np.load(sys.argv[2])["V"].astype(float)
MM = 1 / 254; L = V[:, 2].max()
# hoof mask: paint (incl. its grey highlights) is far darker than the cream terry; smooth it on the mesh
# graph so stray dark/light texels don't create false edges, then keep the main black region only
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
n_ = len(V); e_ = np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]; e_ = np.r_[e_, e_[:, ::-1]]
Aj = sp.coo_matrix((np.ones(len(e_)), (e_[:, 0], e_[:, 1])), shape=(n_, n_)).tocsr(); Aj.data[:] = 1
Wn = sp.diags(1 / np.asarray(Aj.sum(1)).ravel()) @ Aj
x = (C.mean(1) < 150).astype(float)
for _ in range(30): x = 0.5 * x + 0.5 * (Wn @ x)
dark = x > 0.5
sub = Aj[dark][:, dark]; k, lab = connected_components(sub, directed=False)
main = np.bincount(lab).argmax(); idx = np.where(dark)[0]; dark = np.zeros(n_, bool); dark[idx[lab == main]] = True
print(f"hoof mask: {dark.mean()*100:.1f}% of vertices, lowest at {V[dark,2].min()/V[:,2].max()*100:.0f}% height")
# hand x-range at the wrist, to tell the thumb apart
wr = V[np.abs(V[:, 2] - 0.25 * L) < 0.01]; hx0, hx1 = wr[:, 0].min(), wr[:, 0].max()
thumb = (V[:, 0] > hx1 + 0.005) & (V[:, 2] > 0.3 * L) & (V[:, 2] < 0.8 * L)
print(f"wrist x {hx0:.3f}..{hx1:.3f}; thumb top at {V[thumb,2].max()/L*100:.0f}% height" if thumb.any() else "no thumb found")
# boundary vertices: on an edge between a dark and a light vertex
e = np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]; b = e[dark[e[:, 0]] != dark[e[:, 1]]]
ub = np.unique(b); P = V[ub]; P = P[(P[:, 2] > 0.45 * L) & ~thumb[ub]]
for _ in range(4):                                   # z = a x + b y + c, drop >2 sigma outliers
    A = np.c_[P[:, 0], P[:, 1], np.ones(len(P))]; coef, *_ = np.linalg.lstsq(A, P[:, 2], rcond=None)
    r = P[:, 2] - A @ coef; P = P[np.abs(r) < 2 * r.std() + 1e-9]
n = np.array([-coef[0], -coef[1], 1.0]); n /= np.linalg.norm(n); c0 = np.array([0, 0, coef[2]])
print(f"base plane: z = {coef[0]:.3f} x + {coef[1]:.3f} y + {coef[2]:.4f}  (tilt {np.degrees(np.arccos(n[2])):.1f} deg; mean height {P[:,2].mean()/L*100:.1f}%; residual {r.std()/MM:.1f} mm; {len(P)} pts)")
# cleft groove bottom: cast rays front->back and back->front across the hoof at several heights
m = trimesh.Trimesh(V, F, process=False)
G = []
for f in np.linspace(0.68, 0.9, 12):
    z = f * L; hoofrow = V[(np.abs(V[:, 2] - z) < 0.004) & dark]
    x0, x1 = hoofrow[:, 0].min(), hoofrow[:, 0].max(); xs = np.linspace(x0 + 0.3 * (x1 - x0), x1 - 0.3 * (x1 - x0), 61)
    for y0, dy in ((-1.0, 1.0), (1.0, -1.0)):
        o = np.c_[xs, np.full_like(xs, y0), np.full_like(xs, z)]
        loc, idx, _ = m.ray.intersects_location(o, np.tile([0, dy, 0], (len(o), 1)), multiple_hits=False)
        if len(loc) < 20: continue
        depth = loc[:, 1] * dy                       # how far the ray travelled in: largest = groove bottom
        k = np.argmax(depth); G.append(loc[k])
G = np.array(G)
# plane containing the groove points: x = p y + q z + s
A = np.c_[G[:, 1], G[:, 2], np.ones(len(G))]; cf, *_ = np.linalg.lstsq(A, G[:, 0], rcond=None)
rc = G[:, 0] - A @ cf
nc = np.array([1.0, -cf[0], -cf[1]]); nc /= np.linalg.norm(nc); cc = np.array([cf[2], 0, 0])
print(f"cleft plane: x = {cf[0]:.3f} y + {cf[1]:.3f} z + {cf[2]:.4f}  ({len(G)} groove points, residual {rc.std()/MM:.1f} mm, max {np.abs(rc).max()/MM:.1f} mm)")
# pivot: where the cleft plane meets the base plane, at the hoof's mid-thickness
yb = V[(np.abs(V[:, 2] - c0[2]) < 0.006) & ~thumb][:, 1]; ym = (yb.min() + yb.max()) / 2
# solve x = cf0*ym + cf1*z + cf2 ; z = coef0*x + coef1*ym + coef2
M = np.array([[1, -cf[1]], [-coef[0], 1]]); rhs = np.array([cf[0] * ym + cf[2], coef[1] * ym + coef[2]])
px, pz = np.linalg.solve(M, rhs)
json.dump(dict(base_co=c0.tolist(), base_no=n.tolist(), cleft_co=cc.tolist(), cleft_no=nc.tolist(),
               pivot=[float(px), float(ym), float(pz)], hand_x=[float(hx0), float(hx1)], height=float(L)), open(sys.argv[3], "w"), indent=1)
print("pivot", np.round([px, ym, pz], 4))
