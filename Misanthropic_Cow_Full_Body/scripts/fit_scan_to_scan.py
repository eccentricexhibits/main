"""Fit the face relief of one mask scan onto another (rigid + uniform scale ICP) to compare their units.

python3 -I fit_scan_to_scan.py <ref.stl|obj> <moving.stl|obj> <out.npy>
  ref:    cowMask1.stl from the mask project (millimetres, checked against a photo by the glove project);
          lies face-up: the face looks toward +Z.
  moving: cowMask.obj (2014); stands upright: Z up, the face looks toward -Y.
Only front-facing surface points are used (the scans' filled backs and extruded sides are not real mask).
Prints the scale moving -> ref: 1.0 means the OBJ is in millimetres too.
"""
import sys, itertools
import numpy as np, trimesh
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation as Rot


def front_points(m, view, frac, n, rng):
    """Surface samples whose normal faces `view` and that lie in the front `frac` of the depth along it."""
    p, fi = trimesh.sample.sample_surface_even(m, n * 6, seed=1)
    nr = m.face_normals[fi]
    d = p @ view
    keep = (nr @ view > 0.25) & (d > d.min() + (1 - frac) * (d.max() - d.min()))
    p = p[keep]
    return p[rng.choice(len(p), min(n, len(p)), replace=False)]


def icp(A, B, R, s, t, iters=80, trim=80, fix_scale=False):
    """Move A (scaled, rotated) onto B. Returns R, s, t, median and p90 residual (A->B)."""
    tree = cKDTree(B)
    for _ in range(iters):
        X = s * A @ R.T + t
        d, i = tree.query(X)
        k = d < np.percentile(d, trim)
        P, Q = A[k], B[i[k]]
        mp, mq = P.mean(0), Q.mean(0); Pc, Qc = P - mp, Q - mq
        U, sig, Wt = np.linalg.svd(Pc.T @ Qc)
        D = np.eye(3); D[2, 2] = np.sign(np.linalg.det(Wt.T @ U.T))
        R = Wt.T @ D @ U.T
        if not fix_scale: s = np.trace(np.diag(sig) @ D) / (Pc ** 2).sum()
        t = mq - s * mp @ R.T
    d = tree.query(s * A @ R.T + t)[0]
    return R, s, t, np.median(d), np.percentile(d, 90)


if __name__ == "__main__":
    ref = trimesh.load(sys.argv[1], force="mesh"); mov = trimesh.load(sys.argv[2], force="mesh")
    rng = np.random.default_rng(0)
    B = front_points(ref, np.array([0, 0, 1.0]), 0.55, 6000, rng)
    A = front_points(mov, np.array([0, -1.0, 0]), 0.55, 6000, rng)
    # base turn: the OBJ's face direction (-Y) onto the STL's (+Z); then try spins about the face axis
    base = Rot.from_rotvec([np.pi / 2, 0, 0])   # -Y -> +Z
    # Free-scale ICP collapses onto a patch, so: rigid ICP at each fixed scale, scored both ways
    # (OBJ->STL and STL->OBJ medians), then a final free-scale polish from the best start.
    tB = cKDTree(B)
    best = None
    for s0 in np.arange(0.7, 1.41, 0.05):
        for spin in range(0, 360, 45):
            R0 = (Rot.from_rotvec([0, 0, np.radians(spin)]) * base).as_matrix()
            t0 = B.mean(0) - s0 * A.mean(0) @ R0.T
            R, s, t, med, p90 = icp(A, B, R0, s0, t0, iters=25, fix_scale=True)
            back = np.median(cKDTree(s * A @ R.T + t).query(B)[0])
            score = med + back
            if best is None or score < best[0]: best = (score, R, s, t, med, back)
        print(f"scale {s0:.2f}: best so far score {best[0]:.2f} at scale {best[2]:.2f}")
    _, R, s, t, med, back = best
    # refine the scale finely around the best (rigid ICP per scale)
    for s0 in np.arange(s - 0.08, s + 0.081, 0.01):
        R1, _, t1, m1, _ = icp(A, B, R, s0, t, iters=30, fix_scale=True)
        b1 = np.median(cKDTree(s0 * A @ R1.T + t1).query(B)[0])
        if m1 + b1 < med + back: R, s, t, med, back = R1, s0, t1, m1, b1
    print(f"BEST: scale OBJ->STL {s:.3f}; median OBJ->STL {med:.2f} mm, STL->OBJ {back:.2f} mm")
    np.save(sys.argv[3], {"R": R, "s": s, "t": t})
