"""Model clean horns and the wire tuft that follow the real horns in the 2014 mask scan.

python3 -I horns_from_scan_cow.py <cowMask.obj> <out_dir>

Scan frame (millimetres): Z up, the face looks toward -Y, the costume's own left is +X.
- Long horn (own left, +X): a separate piece in the scan. Its centreline comes from geodesic distance
  bins (root -> tip), its radius from the mean distance of each bin's vertices to the bin centre.
- Short horn (own right, -X): fused with the horn tube, so its centreline is the straight axis read
  off orthographic renders; the radius is the median distance of the scan's vertices around it.
- Wires: five thin twisted strands rising from the short horn's tip and curling outward, following the
  scan's four strands (they rise about 45 mm and curl out over the horn).
Each horn is swept as a smooth closed tube (parallel-transport frames, smoothed radius, rounded root,
pointed tip on the long horn per the brief). Writes horn_long.ply, horn_short.ply, horn_wires.ply (scan mm)
and horns.json (centrelines, radii, the black ring positions as fractions of length).
"""
import sys, os, json
import numpy as np, trimesh, networkx as nx
from scipy.ndimage import gaussian_filter1d
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom_cow import sweep  # noqa: E402

SCAN, OUT = sys.argv[1:3]
os.makedirs(OUT, exist_ok=True)
def resample(C, r, n):
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]
    u = np.linspace(0, s[-1], n)
    return np.c_[[np.interp(u, s, C[:, k]) for k in range(3)]].T, np.interp(u, s, r), s[-1]


scan = trimesh.load(SCAN, force="mesh", process=False)
sv = np.asarray(scan.vertices); sf = np.asarray(scan.faces)

# ---------- long horn: the separate piece above the slab on +X ----------
top = trimesh.Trimesh(sv, sf[sv[sf][:, :, 2].max(1) > 195], process=False)
parts = sorted(top.split(only_watertight=False), key=lambda p: -len(p.faces))
lh = [p for p in parts if p.bounds[0][0] > 20][0]
lh.merge_vertices()
g = nx.Graph(); e = lh.edges_unique
g.add_weighted_edges_from(np.c_[e, lh.edges_unique_length])
v = np.asarray(lh.vertices)
root_seed = int(np.argmin(v[:, 0] + 0.5 * (v[:, 2] - 195)))        # innermost, lowest point = the root
dist = nx.single_source_dijkstra_path_length(g, root_seed)
idx = np.array(list(dist.keys()), dtype=int); dd = np.array(list(dist.values()), dtype=float)
tip = idx[np.argmax(dd)]
nb = 40
bins = np.linspace(0, dd.max(), nb + 1)
C, R = [], []
for i in range(nb):
    k = idx[(dd >= bins[i]) & (dd < bins[i + 1])]
    if len(k) < 20: continue
    c = v[k].mean(0); C.append(c); R.append(np.linalg.norm(v[k] - c, axis=1).mean())
C, R = np.array(C), np.array(R)
# geodesic bins at the very root and tip are caps, not cross-sections: drop them, extend the line
C, R = C[2:-1], R[2:-1]
C = np.c_[[gaussian_filter1d(C[:, k], 1.5, mode="nearest") for k in range(3)]].T
R = gaussian_filter1d(R, 2.0, mode="nearest")
C, R, L_long = resample(C, R, 90)
taper = np.clip((np.linspace(0, 1, 90) - 0.86) / 0.14, 0, 1)        # brief: an intact, smooth, pointed tip
R = R * (1 - 0.88 * taper ** 1.4)
# push the root 12 mm back along the root direction so it seats into the tube
d0 = C[0] - C[3]; d0 /= np.linalg.norm(d0)
C = np.vstack([C[0] + d0 * 12, C]); R = np.r_[R[0], R]
horn_long = sweep(C, R)
horn_long.export(f"{OUT}/horn_long.ply")
print(f"long horn: length {L_long:.0f} mm, root radius {R[1]:.1f}, mid {R[len(R)//2]:.1f}; root {C[1].round(1)}, tip {C[-1].round(1)}")

# ---------- short horn: straight axis read from the renders ----------
A0, A1 = np.array([-42.0, 0.5, 253.0]), np.array([-90.0, 0.5, 264.0])
ax = (A1 - A0) / np.linalg.norm(A1 - A0); Ls = np.linalg.norm(A1 - A0)
near = sv[(sv[:, 0] < -36) & (sv[:, 2] > 215)]
q = (near - A0) @ ax; rad = np.linalg.norm(near - A0 - q[:, None] * ax, axis=1)
ts = np.linspace(0.04, 0.96, 24) * Ls
Rs = []
for t_ in ts:
    k = (np.abs(q - t_) < 2.0) & (rad < 30)
    Rs.append(np.median(rad[k]) if k.sum() > 20 else np.nan)
Rs = np.array(Rs); Rs = np.interp(ts, ts[~np.isnan(Rs)], Rs[~np.isnan(Rs)])
Rs = gaussian_filter1d(Rs, 1.5, mode="nearest")
Cs = A0 + ts[:, None] * ax
Cs = np.vstack([A0 - ax * 12, Cs]); Rs = np.r_[Rs[0], Rs]
horn_short = sweep(Cs, Rs, cap_tip=True)
horn_short.export(f"{OUT}/horn_short.ply")
print(f"short horn: length {Ls:.0f} mm, root radius {Rs[1]:.1f}, end radius {Rs[-1]:.1f}")

# ---------- wire tuft: five twisted strands from the short horn's end ----------
rng = np.random.default_rng(7)
end = Cs[-1]; up = np.array([0, 0, 1.0])
out_dir = ax.copy()
wires = []
for w in range(5):
    phi = 2 * np.pi * w / 5 + rng.uniform(-0.3, 0.3)
    side = np.cross(ax, up); side /= np.linalg.norm(side)
    start = end - ax * 3 + (np.cos(phi) * side + np.sin(phi) * up) * Rs[-1] * 0.55
    n = 60; u = np.linspace(0, 1, n)
    height = 42 + rng.uniform(-6, 8); reach = 26 + rng.uniform(-6, 6)
    # rise, then curl outward and over (as in the scan), with a slow twist about the tuft's axis
    path = start + up[None] * (height * np.sin(u * np.pi * 0.62)[:, None] / np.sin(np.pi * 0.62)) \
        + out_dir[None] * (reach * u[:, None] ** 1.8) \
        + side[None] * (3.0 * np.sin(u * 3 * np.pi + phi))[:, None] \
        + np.cross(out_dir, side)[None] * (2.0 * np.cos(u * 3 * np.pi + phi))[:, None]
    wires.append(sweep(path, np.full(n, 0.8), sides=8))
trimesh.util.concatenate(wires).export(f"{OUT}/horn_wires.ply")

json.dump({"units": "mm, scan frame", "long_horn": {"length": L_long, "root": C[1].tolist(), "tip": C[-1].tolist(),
           "rings_at_fraction": [0.30, 0.48, 0.66], "ring_width_mm": 5},
           "short_horn": {"length": Ls, "root": Cs[1].tolist(), "end": Cs[-1].tolist(), "rings_at_fraction": [0.35, 0.70], "ring_width_mm": 5},
           "long_centreline": C.tolist(), "short_centreline": Cs.tolist()}, open(f"{OUT}/horns.json", "w"), indent=1)
print("wrote", OUT)
