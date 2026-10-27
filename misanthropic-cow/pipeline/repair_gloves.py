"""One-off repair of assets/gloves_tripo.glb: rebuild each glove as one closed surface.

tripo_gloves.py reduced the Tripo gloves before welding the Tripo mesh's split seams, so each piece
was reduced on its own and their edges no longer met: each glove came out with ~300 hairline cracks
(over 6,000 open edges) that opened wider as the hand moved and showed as dark lines on the mitten.
The Tripo OBJ is not in the handoff, so this repairs the asset itself:
  1. sample the glove's surface densely (keeping each sample's texture coordinates);
  2. on a 0.5 mm grid, mark everything within EPS of the surface as wall, flood-fill the outside,
     and treat the rest as the glove's inside, which closes every gap narrower than about 2 x EPS;
  3. take the surface of that solid (marching cubes), move it back in by EPS to the original size,
     smooth away the grid steps and reduce it to the original triangle count;
  4. unwrap it again and bake its colour and roughness from the old surface's textures.
The gloves keep their frame, size and shape (within a fraction of a millimetre) and gloves_tripo.json
is unchanged.

usage: python repair_gloves.py ../assets/gloves_tripo.glb ../assets/gloves_tripo.glb
"""
import sys
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree
import sdf as S
import render as R
import textures as T
import glb as G

EPS = .0009            # gaps narrower than about twice this are closed
H = .0005              # grid spacing
TEX = 2048
SAMPLES = 2_500_000


def surface_samples(v, f, uv, n, rng):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    area = .5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    fi = np.r_[np.arange(len(f)), rng.choice(len(f), n, p=area / area.sum())]     # every face at least once
    r1, r2 = rng.random(len(fi)), rng.random(len(fi))
    s1 = np.sqrt(r1)
    bc = np.stack([1 - s1, s1 * (1 - r2), s1 * r2], 1)
    return np.einsum('ij,ijk->ik', bc, v[f[fi]]), np.einsum('ij,ijk->ik', bc, uv[f[fi]])


def closed_surface(v, f, pts):
    from skimage.measure import marching_cubes
    lo = v.min(0) - .004
    shape = np.ceil((v.max(0) + .004 - lo) / H).astype(int) + 1
    tree = cKDTree(pts)
    d = np.empty(int(np.prod(shape)), np.float32)
    ii = np.arange(len(d))
    for s in range(0, len(d), 2_000_000):                         # distance to the surface, in chunks
        k = ii[s:s + 2_000_000]
        g = np.stack(np.unravel_index(k, shape), 1) * H + lo
        d[k] = np.minimum(tree.query(g, distance_upper_bound=.004)[0], .004)
    d = d.reshape(shape)
    wall = d < EPS
    lab, _ = ndimage.label(~wall)
    border = np.unique(np.r_[lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(),
                             lab[:, :, 0].ravel(), lab[:, :, -1].ravel()])
    outside = np.isin(lab, border[border > 0])
    phi = np.where(outside | wall, d - EPS, -d)
    vv, ff, _, _ = marching_cubes(phi, 0., spacing=(H, H, H))
    vv = vv + lo
    vv, ff = S.largest_component(vv, ff.astype(np.int64))
    # face the outside: positive enclosed volume
    vol = np.einsum('ij,ij->i', vv[ff[:, 0]], np.cross(vv[ff[:, 1]], vv[ff[:, 2]])).sum()
    if vol < 0:
        ff = ff[:, ::-1]
    vv = vv - S.vertex_normals(vv, ff) * EPS                       # back to the original size
    vv = S.taubin(vv, ff, 6)
    return vv, ff


def main(src, out):
    import xatlas
    rng = np.random.default_rng(5)
    m = G.read(src)
    imgs = {}
    for p in m.parts:
        v, f, uv = p['v'].astype(float), p['f'].astype(np.int64), p['uv'].astype(float)
        mat = m.materials[p['material']]
        pb = mat['pbrMetallicRoughness']
        maps = [G.image_array(m, pb['baseColorTexture']['image']).astype(np.float32) / 255,
                G.image_array(m, pb['metallicRoughnessTexture']['image']).astype(np.float32) / 255]
        pts, puv = surface_samples(v, f, uv, SAMPLES, rng)
        vv, ff = closed_surface(v, f, pts)
        vv, ff = S.decimate(vv, ff, len(f))
        vv, ff = S.clean(vv, ff)
        vmap, fi, uvl = xatlas.parametrize(vv.astype(np.float32), ff.astype(np.uint32))
        v2 = vv[vmap]
        pos, cover = R.bake(fi, uvl, v2, TEX, TEX)
        idx = np.nonzero(cover)
        _, near = cKDTree(pts).query(pos[idx])
        baked = []
        for img in maps:
            o = np.zeros((TEX, TEX, 3), np.float32)
            o[idx] = T.sample(img, puv[near])
            baked.append(T.dilate(o, cover))
        imgs[p['name']] = (T.to_jpeg(baked[0], 90), T.to_jpeg(baked[1], 92))
        pb['baseColorTexture']['image'] = m.add_image(imgs[p['name']][0])
        pb['metallicRoughnessTexture']['image'] = m.add_image(imgs[p['name']][1])
        p.update(v=v2.astype(np.float32), n=S.vertex_normals(v2, fi).astype(np.float32), f=fi.astype(np.int32),
                 uv=uvl.astype(np.float32), uv1=None, ao=None)
        q = np.round(v2 / 1e-6).astype(np.int64)
        _, inv = np.unique(q, axis=0, return_inverse=True); fw = inv.ravel()[fi]
        E = np.sort(np.vstack([fw[:, [0, 1]], fw[:, [1, 2]], fw[:, [2, 0]]]), 1)
        _, cnt = np.unique(E, axis=0, return_counts=True)
        print(p['name'], 'triangles', len(fi), 'open edges', int((cnt == 1).sum()),
              'bounds', v2.min(0).round(3), v2.max(0).round(3), 'was', v.min(0).round(3), v.max(0).round(3), flush=True)
    # keep only the images still referenced
    used = sorted({mm['pbrMetallicRoughness'][k]['image'] for mm in m.materials for k in ('baseColorTexture', 'metallicRoughnessTexture')
                   if k in mm.get('pbrMetallicRoughness', {})})
    remap = {o: i for i, o in enumerate(used)}
    m.images = [m.images[o] for o in used]
    for mm in m.materials:
        for k in ('baseColorTexture', 'metallicRoughnessTexture'):
            if k in mm.get('pbrMetallicRoughness', {}):
                mm['pbrMetallicRoughness'][k]['image'] = remap[mm['pbrMetallicRoughness'][k]['image']]
    G.write(m, out)


if __name__ == '__main__':
    main(*sys.argv[1:3])
