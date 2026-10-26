"""One-off conversion: cut the cow slippers out of the Tripo "Shy Cow" model and save them as a compact
asset (assets/slippers_shy_cow.glb) that assets.py places on the feet.

The owner judged Shy Cow's slippers the right ones: low knitted cow-head slippers on a fuzzy black
rim, with the black sock rising out of the opening (the costume is tights with black socks, pushed
into slippers).  This script:
  1. scales the Tripo mesh to the v10 figure (slipper sole to horn tip = 1.70 m) and finds each
     slipper's ankle axis from the leg just above it;
  2. removes the sock and leg (faces near the ankle axis above the opening) and keeps every
     substantial fragment (Tripo meshes come in pieces);
  3. moves each slipper into its own frame: ankle axis at the origin, sole at y = 0, toe along +z;
  4. reduces it to ~30k triangles, unwraps it with xatlas and bakes its colour from the 8K Tripo
     texture by nearest point on the full-resolution surface.

usage: python tripo_slippers.py "<Shy Cow folder>/cow_mascot_3d_model.obj" "<...>/cow_mascot_3d_model_basecolor.jpg" ../assets/slippers_shy_cow.glb
Needs xatlas (pip install xatlas) in addition to the pipeline's requirements.
"""
import sys
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import sdf as S
import render as R
import textures as T
import glb as G

Image.MAX_IMAGE_PIXELS = None
SCALE = 1.734          # Tripo units -> metres (Shy Cow's horn tip at the v10 horn-tip height)
TEX = 2048


def load_obj(path):
    V, Tt, F = [], [], []
    with open(path) as fh:
        for line in fh:
            c = line[:2]
            if c == 'v ':
                V.append(line[2:])
            elif c == 'vt':
                Tt.append(line[3:])
            elif c == 'f ':
                F.append(line[2:].replace('/', ' '))
    v = np.array(' '.join(V).split(), np.float32).reshape(-1, 3)
    t = np.array(' '.join(Tt).split(), np.float32).reshape(-1, 2)
    per = len(F[0].split()) // 3
    ff = np.array(' '.join(F).split(), np.int64).reshape(len(F), 3, per) - 1
    key = ff[:, :, 0] * (len(t) + 1) + ff[:, :, 1]
    uk, inv = np.unique(key.ravel(), return_inverse=True)
    return v[uk // (len(t) + 1)], t[uk % (len(t) + 1)], inv.reshape(-1, 3).astype(np.int64)


def cut(v, uv, f, s):
    """Faces of one slipper (s = +1 left, -1 right), sock and leg removed."""
    c = v[f].mean(1)
    leg = v[(v[:, 0] * s > 0) & (np.abs(v[:, 1] - .22) < .01)]
    ax = np.array([leg[:, 0].mean(), leg[:, 2].mean()])
    rr = np.linalg.norm(c[:, [0, 2]] - ax, axis=1)
    keep = (c[:, 0] * s > 0) & (c[:, 1] < .20) & ~((c[:, 1] > .085) & (rr < .055))
    ff = f[keep]
    used = np.unique(ff); rm = -np.ones(len(v), np.int64); rm[used] = np.arange(len(used))
    vv, ff, uu = v[used], rm[ff], uv[used]
    n = len(vv)
    A = coo_matrix((np.ones(3 * len(ff)), (np.r_[ff[:, 0], ff[:, 1], ff[:, 2]], np.r_[ff[:, 1], ff[:, 2], ff[:, 0]])), shape=(n, n))
    k, lab = connected_components(A, directed=False)
    sizes = np.bincount(lab[ff[:, 0]], minlength=k)
    ff = ff[sizes[lab[ff[:, 0]]] > 500]
    used = np.unique(ff); rm = -np.ones(n, np.int64); rm[used] = np.arange(len(used))
    return vv[used], rm[ff], uu[used], ax


def to_local(v, ax):
    """Ankle axis to the origin, sole to y = 0, toe along +z (from the footprint's long axis)."""
    p = v - np.array([ax[0], 0, ax[1]])
    p[:, 1] -= p[:, 1].min()
    foot = p[p[:, 1] < .03][:, [0, 2]]
    X = foot - foot.mean(0)
    w, V = np.linalg.eigh(X.T @ X)
    d = V[:, 1]
    if (foot.mean(0) - 0) @ d < 0:          # the toe end is the one farther from the ankle
        d = -d
    ang = np.arctan2(d[0], d[1])
    c, s_ = np.cos(-ang), np.sin(-ang)
    Ry = np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
    return p @ Ry.T


def bake_colour(v_lo, f_lo, uv_lo, v_hi, uv_hi, tex):
    pos, cover = R.bake(f_lo, uv_lo, v_lo, TEX, TEX)
    tree = cKDTree(v_hi)
    H, W = tex.shape[:2]
    idx = np.nonzero(cover)
    _, near = tree.query(pos[idx])
    u = uv_hi[near]
    px = np.clip((u[:, 0] % 1) * (W - 1), 0, W - 1).astype(int)
    py = np.clip((1 - u[:, 1] % 1) * (H - 1), 0, H - 1).astype(int)
    img = np.zeros((TEX, TEX, 3), np.float32)
    img[idx] = tex[py, px]
    return T.dilate(img, cover)


def main(obj, tex_path, out):
    import xatlas
    v, uv, f = load_obj(obj)
    v = v * SCALE
    tex = np.asarray(Image.open(tex_path).convert('RGB')).astype(np.float32) / 255
    m = G.Model()
    m.add_material({'name': 'Slipper_knitted_cow_head', 'pbrMetallicRoughness': {'metallicFactor': 0, 'roughnessFactor': .9}})
    for s, side in [(1, 'L'), (-1, 'R')]:
        vh, fh, uh, ax = cut(v, uv, f, s)
        vh = to_local(vh, ax)
        vl, fl = S.decimate(vh, fh, 30000)
        vmap, fi, uvl = xatlas.parametrize(vl.astype(np.float32), fl.astype(np.uint32))
        vl2 = vl[vmap]
        img = bake_colour(vl2, fi, uvl, vh, uh, tex)
        im = m.add_image(T.to_jpeg(img, 90), 'image/jpeg')
        mat = m.add_material({'name': f'Slipper_{side}_knitted_cow_head', 'pbrMetallicRoughness': {
            'baseColorTexture': {'image': im, 'texCoord': 0}, 'metallicFactor': 0, 'roughnessFactor': .9},
            'doubleSided': True})
        m.parts.append({'name': f'Slipper_{side}_shy_cow', 'v': vl2.astype(np.float32),
                        'n': S.vertex_normals(vl2, fi).astype(np.float32), 'f': fi.astype(np.int32),
                        'uv': uvl.astype(np.float32), 'uv1': None, 'ao': None, 'material': mat})   # baked in this same uv space
        print(side, 'triangles', len(fi), 'bounds', vl2.min(0).round(3), vl2.max(0).round(3), flush=True)
    m.materials = m.materials[1:]
    for p in m.parts:
        p['material'] -= 1
    G.write(m, out)


if __name__ == '__main__':
    main(*sys.argv[1:4])
