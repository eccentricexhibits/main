"""Fit an orthographic camera per turntable photo: hand-picked eye centres + mask silhouette vs. black backdrop."""
import sys, json, numpy as np, trimesh
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as Rot

mask_path, photo_dir, out = sys.argv[1:4]
ONLY = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
prev = json.load(open(out)) if ONLY else {}
mesh = trimesh.load(mask_path)
rng = np.random.default_rng(0)
Vs = mesh.vertices[rng.choice(len(mesh.vertices), 40000, replace=False)]
EYES = np.array([[-31, 125, 65.], [30, 125, 65.]])           # char-right, char-left eye fronts (model mm)
PICKS = {1: [(549, 703), (771, 703)], 8: [(535, 684), (745, 717)],
         19: [(557, 646), (673, 721)], 31: [(597, 636), (597, 722)]}
TURN = {1: 0, 8: -21, 19: -54, 31: -85}                      # rough turntable angle for initialisation (deg)

def project(p, P):
    R = Rot.from_rotvec(p[:3]).as_matrix(); s = p[3]
    q = P @ R.T
    return np.c_[s * q[:, 0] + p[4], -s * q[:, 1] + p[5]], q[:, 2]

def silhouette(p, shape):
    uv, _ = project(p, Vs)
    m = np.zeros(shape, bool); ij = np.round(uv).astype(int)
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < shape[1]) & (ij[:, 1] >= 0) & (ij[:, 1] < shape[0])
    m[ij[ok, 1], ij[ok, 0]] = True
    return ndi.binary_closing(ndi.binary_dilation(m, iterations=2), iterations=3), (~ok).mean()

res = dict(prev)
for fr, picks in PICKS.items():
    if ONLY and fr not in ONLY:
        continue
    img = np.asarray(Image.open(f'{photo_dir}/cow_frame-{fr}.jpg').convert('RGB'))
    fg = ndi.binary_opening(img.max(-1) > 28, iterations=2)
    fg = ndi.binary_fill_holes(fg)
    dist_bg = ndi.distance_transform_edt(fg)          # distance inside foreground to background
    dist_out = ndi.distance_transform_edt(~fg)        # distance outside foreground
    e = np.array(picks, float)
    def cost(p):
        uv, _ = project(p, EYES)
        c_eye = ((uv - e) ** 2).sum(1).mean()
        sil, off = silhouette(p, fg.shape)
        b = sil & ~ndi.binary_erosion(sil)
        # rendered mask must stay on the foreground; its outline should hug the foreground edge
        c_out = (dist_out[sil] ** 2).mean()
        c_edge = np.minimum(dist_bg[b], 25).mean()
        # photos were all shot at the same distance, so keep the scale near the front view's
        return c_eye + 3 * c_out + 0.5 * c_edge ** 2 + 1e4 * off + 2e4 * (p[3] - 3.72) ** 2
    th = np.radians(TURN[fr])
    R0 = Rot.from_euler('y', th) * Rot.from_euler('x', 0.0)
    s0 = 3.64
    mid = e.mean(0)
    best = None
    inits = [Rot.from_euler('y', th) * Rot.from_euler('x', np.radians(pitch)) for pitch in (-15, 0, 15)]
    if str(fr - 12) in prev:  # continue the turntable from the previous fitted frame (3 deg/frame)
        inits.append(Rot.from_euler('y', -36, degrees=True) * Rot.from_rotvec(prev[str(fr - 12)][:3]))
    for R in inits:
        p0 = np.r_[R.as_rotvec(), s0, 0, 0]
        uv, _ = project(p0, EYES); p0[4:6] = mid - uv.mean(0)
        r = minimize(cost, p0, method='Powell', options={'maxiter': 6000, 'xtol': 1e-3, 'ftol': 1e-4})
        if best is None or r.fun < best.fun: best = r
    p = best.x
    uv, _ = project(p, EYES)
    sil, _ = silhouette(p, fg.shape)
    print(fr, 'cost %.1f' % best.fun, 'eye err px', np.linalg.norm(uv - e, axis=1).round(1),
          'outside fg %.3f' % ((sil & ~fg).sum() / max(sil.sum(), 1)), 'scale %.3f' % p[3],
          'euler(yxz deg)', Rot.from_rotvec(p[:3]).as_euler('yxz', degrees=True).round(1))
    res[fr] = p.tolist()
json.dump(res, open(out, 'w'), indent=1)
