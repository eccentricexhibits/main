"""Step 2: assemble the head in the model frame (mm, Y up, face toward +Z).

- Mask: the cleaned scan field, resampled into the model frame.
- Hood: the fur cowl behind the mask (not in the 2014 scan; proportions from the turntable photos).
- Horn bar: fur-wrapped log on top of the head, horns at each end (rebuilt; the scanned horns were partial).
"""
import sys, numpy as np, trimesh
from scipy import ndimage as ndi
from skimage import measure
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from frames import scan_to_model_matrix

field_path, sym_path, out_dir = sys.argv[1:4]
rng = np.random.default_rng(7)
PITCH = 1.0

def grid(lo, hi):
    ax = [np.arange(l, h + PITCH, PITCH) for l, h in zip(lo, hi)]
    return ax, np.stack(np.meshgrid(*ax, indexing='ij'), -1).astype(np.float32)

def noise(shape, sigma):
    n = ndi.gaussian_filter(rng.standard_normal(shape).astype(np.float32), sigma, mode='wrap')
    return n / n.std()

def to_mesh(f, ax, level=0.5):
    v, fa, _, _ = measure.marching_cubes(f, level, spacing=(PITCH,) * 3)
    v += np.array([a[0] for a in ax])
    return trimesh.Trimesh(v, fa[:, ::-1])

def occ(sdf):  # signed distance (mm, negative inside) -> soft occupancy
    return np.clip(0.5 - sdf / (2 * PITCH), 0, 1)

def smin(a, b, k):  # polynomial smooth union of two SDFs
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)

# ---------------- mask + hood ----------------
ax, P = grid((-118, -45, -135), (118, 262, 108))
X, Y, Z = P[..., 0], P[..., 1], P[..., 2]

d = np.load(field_path); f_scan = d['f'].astype(np.float32); T = d['T']
A = scan_to_model_matrix(np.load(sym_path))
Ainv = np.linalg.inv(A)
Ps = P.reshape(-1, 3) @ Ainv[:3, :3].T + Ainv[:3, 3]
idx = ((Ps - T[:3, 3]) / np.diag(T)[:3]).T
f_mask = ndi.map_coordinates(f_scan, idx, order=1, cval=0).reshape(X.shape)

# hood: ellipsoid cowl sized so its section at the rim plane (Z=0) is just wider than the mask rim
c, r = np.array([0, 112, -32.]), np.array([100, 118, 88.])
q = (P - c) / r
ell = (np.linalg.norm(q, axis=-1) - 1) * r.min()
neck = np.maximum(np.sqrt((X / 72) ** 2 + ((Z + 30) / 66) ** 2) * 66 - 66, np.maximum(-30 - Y, Y - 120))
hood = smin(ell, neck, 25)
hood = np.maximum(hood, -24 - Y)  # flat neck opening (closed) where the head meets the body
hood += 3.0 * noise(X.shape, 14) + 0.35 * noise(X.shape, 2.0)  # soft plush folds; fine fuzz is left to shading
hood = np.maximum(hood, -24 - Y)  # keep the neck opening flat after the noise
# the cowl stays behind the mask rim (rolling over at its edge so it peeks out around the mask);
# below the chin it comes forward as a furry throat tucked under the snout
hood = -smin(-hood, -(Z - 6 - 0.9 * np.maximum(0, 45 - Y)), 8)
f_hood = occ(hood)

f = np.maximum(f_mask, f_hood)
body = to_mesh(ndi.gaussian_filter(f, 0.7), ax)
body = max(body.split(only_watertight=False), key=lambda m: len(m.faces))
# label: which field produced the surface here
vi = ((body.vertices - np.array([a[0] for a in ax])) / PITCH).T
fm = ndi.map_coordinates(f_mask, vi, order=1); fh = ndi.map_coordinates(f_hood, vi, order=1)
body.vertex_attributes['is_mask'] = (fm >= fh).astype(np.float32)

# ---------------- horn bar ----------------
BAR_C, BAR_R, BAR_HALF = np.array([0, 238, -6.]), 30.0, 56.0
ax2, P2 = grid((-70, 200, -50), (70, 285, 35))
L = P2 - BAR_C
rad = np.sqrt(L[..., 1] ** 2 + L[..., 2] ** 2)
dx, dr = np.abs(L[..., 0]) - (BAR_HALF - 10), rad - (BAR_R - 10)  # rounded cylinder, 10mm edge radius
bar = np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dr, 0) ** 2) + np.minimum(np.maximum(dx, dr), 0) - 10
bar += 1.6 * noise(bar.shape, 8) + 0.3 * noise(bar.shape, 2.0)
hornbar = to_mesh(occ(bar), ax2)
hornbar = max(hornbar.split(only_watertight=False), key=lambda m: len(m.faces))

# ---------------- horns ----------------
def tube(C, R, nseg):
    """Open tube along polyline C with per-point radius R (parallel-transport frames)."""
    D = np.gradient(C, axis=0); D /= np.linalg.norm(D, axis=1, keepdims=True)
    Nv = np.cross(D[0], [0.3, 0.2, 1.]); Nv /= np.linalg.norm(Nv); V = []
    ang = np.linspace(0, 2 * np.pi, nseg, endpoint=False)
    for k in range(len(C)):
        Nv = Nv - D[k] * (Nv @ D[k]); Nv /= np.linalg.norm(Nv); B = np.cross(D[k], Nv)
        V += [C[k] + R[k] * (np.cos(a) * Nv + np.sin(a) * B) for a in ang]
    F = [[k * nseg + a, k * nseg + (a + 1) % nseg, (k + 1) * nseg + (a + 1) % nseg] for k in range(len(C) - 1) for a in range(nseg)]
    F += [[k * nseg + a, (k + 1) * nseg + (a + 1) % nseg, (k + 1) * nseg + a] for k in range(len(C) - 1) for a in range(nseg)]
    return trimesh.Trimesh(np.array(V), np.array(F), process=False)

def horn(side):
    """Tapered tube along a quadratic Bezier from inside the bar end, outward then up."""
    P0, P1, P2_ = np.array([44, 0, 0.]), np.array([84, 0, 0.]), np.array([92, 30, 6.])
    t = np.linspace(0, 1, 90)[:, None]
    C = (1 - t) ** 2 * P0 + 2 * (1 - t) * t * P1 + t ** 2 * P2_
    D = 2 * (1 - t) * (P1 - P0) + 2 * t * (P2_ - P1); D /= np.linalg.norm(D, axis=1, keepdims=True)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]; u = s / s[-1]
    R = 17 - 6 * u ** 1.4
    # parallel-transport frame
    Nv = np.cross(D[0], [0, 0, 1.]); Nv /= np.linalg.norm(Nv); frames = []
    for k in range(len(C)):
        Nv = Nv - D[k] * (Nv @ D[k]); Nv /= np.linalg.norm(Nv); frames.append((Nv.copy(), np.cross(D[k], Nv)))
    nseg = 40; ang = np.linspace(0, 2 * np.pi, nseg, endpoint=False)
    verts = [C[k] + R[k] * (np.cos(a) * frames[k][0] + np.sin(a) * frames[k][1]) for k in range(len(C)) for a in ang]
    uu = [u[k] for k in range(len(C)) for a in ang]
    # hemispherical tip cap
    tip_rings = 10
    for j in range(1, tip_rings):
        phi = j / tip_rings * np.pi / 2
        for a in ang:
            verts.append(C[-1] + D[-1] * R[-1] * np.sin(phi) + R[-1] * np.cos(phi) * (np.cos(a) * frames[-1][0] + np.sin(a) * frames[-1][1]))
            uu.append(1.0)
    verts.append(C[-1] + D[-1] * R[-1]); uu.append(1.0)
    verts = np.array(verts); rings = len(C) + tip_rings - 1
    F = []
    for k in range(rings - 1):
        for a in range(nseg):
            i0, i1 = k * nseg + a, k * nseg + (a + 1) % nseg
            F += [[i0, i1, i1 + nseg], [i0, i1 + nseg, i0 + nseg]]
    tip = len(verts) - 1; base = (rings - 1) * nseg
    F += [[base + a, base + (a + 1) % nseg, tip] for a in range(nseg)]
    F += [[(a + 1) % nseg, a, len(verts)] for a in range(nseg)]  # flat cap hidden inside the bar
    verts = np.vstack([verts, C[0]]); uu.append(0.0)
    verts = verts + BAR_C
    m = trimesh.Trimesh(verts, np.array(F), process=False)
    m.vertex_attributes['u'] = np.array(uu, np.float32)
    if side < 0:
        m.vertices[:, 0] *= -1; m.faces = m.faces[:, ::-1]
    return m, (C[-1] + D[-1] * R[-1] * 0.6 + BAR_C) * [side, 1, 1], D[-1] * [side, 1, 1]

horn_L, tipL, dirL = horn(+1)   # character's left = +X
horn_R, tipR, dirR = horn(-1)

def wire_bundle(tip, direction, n=4, length=34):
    """Twisted bare wire poking out of a horn tip (character's right horn in the photos)."""
    parts = []
    up = np.array([0, 1., 0]); side = np.cross(direction, up); side /= np.linalg.norm(side)
    for k in range(n):
        t = np.linspace(0, 1, 60)[:, None]
        ph = 2 * np.pi * k / n
        ctr = tip + direction * (t * length) + up * (12 * t ** 2) + side * (-6 * t ** 2)
        off = 1.6 * (np.cos(ph + 9 * t) * side + np.sin(ph + 9 * t) * np.cross(direction, side))
        path = (ctr + off).reshape(-1, 3)
        parts.append(tube(path, np.full(len(path), 0.55), 6))
    return trimesh.util.concatenate(parts)

wire = wire_bundle(tipR, dirR)

np.save(f'{out_dir}/body_is_mask.npy', body.vertex_attributes['is_mask'])
body.export(f'{out_dir}/body_hi.ply')
hornbar.export(f'{out_dir}/hornbar.ply')
for name, m in (('horn_L', horn_L), ('horn_R', horn_R)):
    m.export(f'{out_dir}/{name}.ply'); np.save(f'{out_dir}/{name}_u.npy', m.vertex_attributes['u'])
wire.export(f'{out_dir}/wire_R.ply')
print('body', len(body.faces), 'bar', len(hornbar.faces), 'horn', len(horn_L.faces), 'wire', len(wire.faces))
