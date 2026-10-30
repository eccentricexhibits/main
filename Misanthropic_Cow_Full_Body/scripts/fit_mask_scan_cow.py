"""Fit the real mask scan (cowMask.obj, 2014, millimetres) onto the Tripo cow's face and derive the
cow's real-world scale.

python3 -I fit_mask_scan_cow.py <cowMask.obj> <tripo_blender_frame.npz> <out_dir>

Both meshes in the Blender frame: Z up, the face looks toward -Y, the costume's own left is +X.
The scan is a closed block: the real mask relief sits in front of a flat slab (front plane near y = 0),
with the horn tube and horns on top. Only the relief in front of the slab is used here.

Steps
1. Eye beads: sphere fits on the scan (centres, diameters).
2. Start: Tripo eye centres (measured on an orthographic textured render) matched to the scan's,
   scale from the mask width at eye level (scan 176 mm; Tripo 0.105 units -> 1.676 m per unit).
3. Trimmed ICP, Tripo face points -> scan relief, then a check the other way. Free-scale ICP shrinks
   (1.50 m per unit: the AI face is not the scan's shape, p90 16 mm), so the scale is held at the
   mask-width value and ICP only sets the pose. The free-scale result is still reported.
Writes fit.json: the scan-mm -> Tripo-units transform, the cow scale (m per Tripo unit), residuals.
"""
import sys, json, os
import numpy as np, trimesh
from scipy.spatial import cKDTree
from scipy.optimize import least_squares

SCAN, NPZ, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
SLAB_FRONT_Y = -2.0         # scan: relief is everything in front of this (mm)
SCAN_EYES0 = [(-30.6, 125.6), (30.5, 124.5)]      # rough (x, z) from the front render
TRIPO_EYES_XZ = [(-0.02125, 0.8543), (0.01625, 0.8550)]   # from tripo_head_tex_front.png (4000 px/unit)


def sphere(p):
    r = lambda q: np.linalg.norm(p - q[:3], axis=1) - q[3]
    s = least_squares(r, np.r_[p.mean(0) + [0, 8, 0], 10], loss="soft_l1", f_scale=0.5)
    return s.x, float(np.median(np.abs(r(s.x))))


scan = trimesh.load(SCAN, force="mesh", process=False)
sv = np.asarray(scan.vertices)
eyes = []
for x0, z0 in SCAN_EYES0:
    sel = sv[np.hypot(sv[:, 0] - x0, sv[:, 2] - z0) < 16]
    q, res = sphere(sel[sel[:, 1] < sel[:, 1].min() + 8])
    eyes.append(q); print(f"scan eye: centre {q[:3].round(1)} diameter {2*q[3]:.1f} mm (fit residual {res:.2f})")
eye_mid_s = (eyes[0][:3] + eyes[1][:3]) / 2
eye_gap_s = float(np.linalg.norm(eyes[0][:3] - eyes[1][:3]))
print(f"scan eye spacing {eye_gap_s:.1f} mm")

# scan relief samples (front of the slab, below the slab top, no horns/tube)
p, fi = trimesh.sample.sample_surface_even(scan, 200000, seed=2)
n = scan.face_normals[fi]
rel = p[(p[:, 1] < SLAB_FRONT_Y) & (p[:, 2] < 212) & (n[:, 1] < 0.2)]
print("scan relief samples", len(rel), "x", rel[:, 0].min().round(1), rel[:, 0].max().round(1), "z", rel[:, 2].min().round(1), rel[:, 2].max().round(1))

d = np.load(NPZ); tv, tf = d["v"], d["f"]
keep = tv[tf][:, :, 2].min(1) > 0.78
head = trimesh.Trimesh(tv, tf[keep], process=False)
# Tripo eye centres: front-most hit at the measured (x, z), pushed back by the scan bead radius
te = []
for x, z in TRIPO_EYES_XZ:
    loc, _, _ = head.ray.intersects_location([[x, -1, z]], [[0, 1, 0]], multiple_hits=False)
    te.append(np.array([x, loc[0, 1], z]))
eye_mid_t = (te[0] + te[1]) / 2
print("tripo eye front points", np.round(te, 4).tolist(), "spacing", round(float(np.linalg.norm(te[0] - te[1])), 4))

tp, tfi = trimesh.sample.sample_surface_even(head, 200000, seed=3)
tn = head.face_normals[tfi]
# the mask area of the Tripo head: front-facing, in front of the hood edge
face_t = tp[(tn[:, 1] < -0.2) & (np.abs(tp[:, 0] - eye_mid_t[0]) < 0.054) & (tp[:, 2] > 0.80) & (tp[:, 2] < 0.925) & (tp[:, 1] < eye_mid_t[1] + 0.045)]
print("tripo face samples", len(face_t))

# map Tripo units -> scan mm: X_s = s * R @ X_t + t
s = 0.176 / 0.105 * 1000      # mm per Tripo unit from the mask width
R = np.eye(3)
t = eye_mid_s + np.array([0, -12.0, 0]) - s * eye_mid_t     # eye fronts sit ~12 mm in front of the bead centres
tree = cKDTree(rel)
FIX = s
for it in range(160):
    if it == 80: s_free = s; s = FIX; R = np.eye(3); t = eye_mid_s + np.array([0, -12.0, 0]) - s * eye_mid_t
    Xs = s * face_t @ R.T + t
    dd, ii = tree.query(Xs)
    k = dd < np.percentile(dd, 75)
    P, Q = face_t[k], rel[ii[k]]
    mp, mq = P.mean(0), Q.mean(0); Pc, Qc = P - mp, Q - mq
    U, sig, Wt = np.linalg.svd(Pc.T @ Qc)
    D = np.eye(3); D[2, 2] = np.sign(np.linalg.det(Wt.T @ U.T))
    R = Wt.T @ D @ U.T
    if it < 80: s = np.trace(np.diag(sig) @ D) / (Pc ** 2).sum()
    t = mq - s * mp @ R.T
Xs = s * face_t @ R.T + t
d1 = tree.query(Xs)[0]
inv_mask = (np.abs(rel[:, 0] - eye_mid_s[0]) < 0.054 * s) & (rel[:, 2] > (0.80 * s + t[2])) & (rel[:, 2] < (0.925 * s + t[2]))
d2 = cKDTree(Xs).query(rel[inv_mask])[0]
ang = np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
print(f"free-scale ICP would give {s_free:.1f} mm per unit (height {0.97849 * s_free / 1000:.3f} m)")
print(f"ICP: {s:.1f} mm per Tripo unit (cow height {0.97849 * s / 1000:.3f} m), rotation {ang:.1f} deg")
print(f"     Tripo->scan median {np.median(d1):.1f} mm, p90 {np.percentile(d1, 90):.1f}; scan->Tripo median {np.median(d2):.1f}, p90 {np.percentile(d2, 90):.1f}")
# inverse: scan mm -> Tripo units
Ri = R.T; si = 1 / s; ti = -si * (t @ R)
json.dump({
    "scan_units": "millimetres",
    "scan_eye_beads_mm": [{"centre": e[:3].round(2).tolist(), "diameter": round(2 * e[3], 2)} for e in eyes],
    "scan_eye_spacing_mm": round(eye_gap_s, 2),
    "mm_per_tripo_unit_used": round(s, 2),
    "mm_per_tripo_unit_free_scale_icp": round(s_free, 2),
    "mm_per_tripo_unit_mask_width": round(0.176 / 0.105 * 1000, 2),
    "mm_per_tripo_unit_eye_spacing": round(eye_gap_s / float(np.linalg.norm(te[0] - te[1])), 2),
    "icp_rotation_deg": round(float(ang), 2),
    "icp_residual_mm": {"tripo_to_scan_median": round(float(np.median(d1)), 2), "tripo_to_scan_p90": round(float(np.percentile(d1, 90)), 2),
                        "scan_to_tripo_median": round(float(np.median(d2)), 2), "scan_to_tripo_p90": round(float(np.percentile(d2, 90)), 2)},
    "scan_mm_to_tripo_units": {"R": Ri.tolist(), "s": si, "t": ti.tolist(), "formula": "X_tripo = s * R @ X_scan + t"},
}, open(os.path.join(OUT, "fit.json"), "w"), indent=1)
print("wrote", os.path.join(OUT, "fit.json"))
