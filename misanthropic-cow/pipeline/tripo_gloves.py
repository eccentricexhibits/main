"""One-off conversion: cut the two hoof gloves out of the owner's Tripo model of the glove photo
(the mask and both gloves lying on a mat) and save them as a compact asset (assets/gloves_tripo.glb)
that gloves.py places on the hands.

Each glove is a long cream terry mitten with a thumb and two glossy black hoof halves over the
fingertips, chipped to show red card on the left glove and green on the right.  This script:
  1. scales the Tripo mesh so the horn span matches the v10 mask (x 0.653);
  2. splits it into pieces and keeps the two gloves (red chips = left glove, green = right);
  3. finds each glove's own frame from its shape: u along the hand toward the hoof tips, a across
     the palm toward the thumb, w out of the palm (left and right gloves are mirror images);
  4. moves it into that frame, with the hoof tips at u = U_TIP and the wrist end of the mitten
     centred on the arm;
  5. reduces it to ~40k triangles, unwraps it with xatlas and bakes its colour and roughness from
     the 8K / 4K Tripo maps by nearest point on the full-resolution surface;
  6. touches up the colour: the photo's lighting left the cream terry grey-green, so the terry is
     white-balanced back to cream (the black hooves and their chips are barely changed).

A JSON file beside the asset (gloves_tripo.json) records, per glove, where the hoof halves start
(u); gloves.py uses it for the hoof bone and finds the thumb from the mesh itself.

usage: python tripo_gloves.py "<hands model>/cow_head_3d_model.obj" "<hands model>" ../assets/gloves_tripo.glb
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
from tripo_slippers import load_obj

Image.MAX_IMAGE_PIXELS = None
SCALE = .653           # Tripo units -> metres (horn tip to horn tip = v10's 0.243 m)
U_TIP = .200           # hoof tips this far past the wrist joint, as in the v10 gloves
TEX = 2048
CREAM = (.86, .83, .76)  # the terry's colour in the close-up photos


def pieces(v, f):
    key = np.round(v * 1e5).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel(); fw = inv[f]; n = inv.max() + 1
    A = coo_matrix((np.ones(3 * len(fw)), (np.r_[fw[:, 0], fw[:, 1], fw[:, 2]], np.r_[fw[:, 1], fw[:, 2], fw[:, 0]])), shape=(n, n))
    _, lab = connected_components(A, directed=False)
    return lab[fw[:, 0]]


def sample(img, uv):
    H, W = img.shape[:2]
    return img[np.clip(((1 - uv[:, 1] % 1) * (H - 1)).astype(int), 0, H - 1), np.clip(((uv[:, 0] % 1) * (W - 1)).astype(int), 0, W - 1)]


def is_hoof(c):
    """Black lacquer or a coloured chip (not cream terry)."""
    return (c.max(1) < .25) | ((c.max(1) - c.min(1)) > .3)


def glove_frame(p, c, side):
    m = p.mean(0); X = p - m
    e1 = np.linalg.eigh(X.T @ X)[1][:, 2]
    dark = is_hoof(c)
    if (p[dark].mean(0) - m) @ e1 < 0:
        e1 = -e1
    q = X - np.outer(X @ e1, e1)
    e2 = np.linalg.eigh(q[~dark].T @ q[~dark])[1][:, 2]
    u, l = X @ e1, X @ e2
    mid = (~dark) & (u > np.percentile(u, 25)) & (u < np.percentile(u[dark], 5))
    if l[mid].max() + l[mid].min() < 0:          # the thumb side reaches further out
        e2 = -e2
    e2 = e2 - e1 * (e2 @ e1); e2 /= np.linalg.norm(e2)
    w = np.cross(e1, e2) * (1 if side == 'L' else -1)
    return m, e1, e2, w


def bake(v_lo, f_lo, uv_lo, v_hi, uv_hi, maps):
    pos, cover = R.bake(f_lo, uv_lo, v_lo, TEX, TEX)
    idx = np.nonzero(cover)
    _, near = cKDTree(v_hi).query(pos[idx])
    out = []
    for img in maps:
        o = np.zeros((TEX, TEX, img.shape[2]), np.float32)
        o[idx] = sample(img, uv_hi[near])
        out.append(T.dilate(o, cover))
    return out


def main(obj, folder, out):
    import xatlas
    v, uv, f = load_obj(obj)
    v = v * SCALE
    col = np.asarray(Image.open(f'{folder}/cow_head_3d_model_basecolor.jpg').convert('RGB')).astype(np.float32) / 255
    rough = np.asarray(Image.open(f'{folder}/cow_head_3d_model_roughness.png').convert('L')).astype(np.float32)[..., None] / 255
    vcol = sample(col, uv)
    lab = pieces(v, f)
    sizes = np.bincount(lab)
    gloves = []
    for c in np.argsort(-sizes)[:3]:
        vi = np.unique(f[lab == c])
        if abs(v[vi, 0].mean()) > .05:
            cc = vcol[vi]
            red = ((cc[:, 0] > .45) & (cc[:, 1] < .25) & (cc[:, 2] < .25)).sum()
            grn = ((cc[:, 1] > .35) & (cc[:, 0] < .25) & (cc[:, 2] < .3)).sum()
            gloves.append(('L' if red > grn else 'R', c))
    assert sorted(s for s, _ in gloves) == ['L', 'R'], gloves
    m = G.Model()
    extras = {}
    for side, c in sorted(gloves):
        ff = f[lab == c]
        vi = np.unique(ff); rm = -np.ones(len(v), np.int64); rm[vi] = np.arange(len(vi))
        p, cc, uh, fh = v[vi], vcol[vi], uv[vi], rm[ff]
        o, e1, e2, w = glove_frame(p, cc, side)
        X = p - o
        loc = np.stack([X @ e1, X @ e2, X @ w], 1)
        loc[:, 0] += U_TIP - loc[:, 0].max()
        terry = ~is_hoof(cc)
        wrist = terry & (loc[:, 0] > -.04) & (loc[:, 0] < .02)
        loc[:, 1:] -= loc[wrist, 1:].mean(0)                      # mitten centred on the arm at the wrist
        dark = is_hoof(cc)
        hoof_u = float(np.percentile(loc[dark, 0], 3))
        extras[side] = {'hoof_u': hoof_u}
        vl, fl_ = S.decimate(loc, fh, 40000)
        vmap, fi, uvl = xatlas.parametrize(vl.astype(np.float32), fl_.astype(np.uint32))
        vl2 = vl[vmap]
        cimg, rimg = bake(vl2, fi, uvl, loc, uh, [col, rough])
        # touch-up: the photo's lighting left the cream terry grey-green; white-balance it to cream
        flat = cimg.reshape(-1, 3)
        terry_px = (flat.max(1) - flat.min(1) < .12) & (flat.mean(1) > .35)
        gain = np.clip(np.array(CREAM) / np.median(flat[terry_px], 0), .8, 1.5)
        cimg = np.clip(cimg * gain, 0, 1)
        rr = np.clip(rimg[..., 0], .30, 1.)
        mr = np.dstack([np.zeros_like(rr), rr, np.zeros_like(rr)])
        ic = m.add_image(T.to_jpeg(cimg, 90), 'image/jpeg')
        ir = m.add_image(T.to_jpeg(mr, 92), 'image/jpeg')
        mat = m.add_material({'name': f'Glove_{side}_terry_mitten_and_black_hoof_caps', 'pbrMetallicRoughness': {
            'baseColorTexture': {'image': ic, 'texCoord': 0}, 'metallicRoughnessTexture': {'image': ir, 'texCoord': 0},
            'metallicFactor': 0, 'roughnessFactor': 1}})
        m.parts.append({'name': f'Glove_{side}_tripo', 'v': vl2.astype(np.float32), 'n': S.vertex_normals(vl2, fi).astype(np.float32),
                        'f': fi.astype(np.int32), 'uv': uvl.astype(np.float32), 'uv1': None, 'ao': None, 'material': mat})
        print(side, 'triangles', len(fi), 'local bounds', vl2.min(0).round(3), vl2.max(0).round(3), extras[side], flush=True)
    G.write(m, out)
    import json
    json.dump({'frame': 'u along the hand (wrist joint at 0), a toward the thumb, w out of the palm; metres', 'gloves': extras},
              open(out[:-4] + '.json', 'w'), indent=2)


if __name__ == '__main__':
    main(*sys.argv[1:4])
