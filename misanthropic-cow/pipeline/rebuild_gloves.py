"""One-off rebuild of the hoof gloves as clean, smooth solids (round 14).

The Tripo gloves came out of tripo_gloves.py with saw-tooth spikes along their edges, and gloves.py
then bent their cuffs to fit the sleeves (pulling the cuff in and flaring the wrist vertex by vertex),
which folded the surface over itself into ragged frills at the wrist.  This rebuilds each glove from
the closed Tripo glove (assets/gloves_tripo_closed.glb, made by repair_gloves.py) in the hand's own
frame (u along the hand from the wrist joint, a toward the thumb, w out of the palm):
  1. the Tripo glove becomes a signed distance field on a 0.6 mm grid, smoothed a little
     (Gaussian, SMOOTH) to take off the spikes while keeping its shape, thumb and hoof halves;
  2. at the wrist it eases in to the sleeve opening's width, so it never pokes through the sleeve;
  3. inside the sleeve it ends in a clean round cuff that fills the sleeve to 8 mm inside its
     surface (so the hand doesn't float in the opening), flattened on the palm side so the claps
     still meet palm to palm; cuff and hand join in one smooth blend;
  4. the result is meshed evenly (about 40k triangles), unwrapped, and its colour and roughness
     baked from the Tripo glove's textures by nearest point.
gloves.py only places the result on the hands; gloves_tripo.json is unchanged.

usage: python rebuild_gloves.py ../assets/gloves_tripo_closed.glb ../assets/gloves_tripo.glb
"""
import sys
import numpy as np
from scipy import ndimage
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
import sdf as S
import render as R
import textures as T
import glb as G
import garments as Gm
import design as D
import gloves as GL

H = .0006              # grid spacing
SMOOTH = .0012         # Gaussian smoothing of the distance field (metres)
SLEEVE_CLEAR = .008    # the cuff stays this far inside the sleeve's surface
PALM_W = .017          # the cuff's palm side is flat here, level with the Tripo palm at the wrist
TEX = 2048
SAMPLES = 2_500_000


def signed_field(v, f, uv, rng):
    """Signed distance of a closed mesh on a grid (negative inside), plus dense surface samples."""
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    area = .5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    fi = np.r_[np.arange(len(f)), rng.choice(len(f), SAMPLES, p=area / area.sum())]
    r1, r2 = rng.random(len(fi)), rng.random(len(fi))
    s1 = np.sqrt(r1)
    bc = np.stack([1 - s1, s1 * (1 - r2), s1 * r2], 1)
    pts = np.einsum('ij,ijk->ik', bc, v[f[fi]]); puv = np.einsum('ij,ijk->ik', bc, uv[f[fi]])
    lo = v.min(0) - .012; lo[0] = -.105                      # room for the cuff inside the sleeve
    hi = v.max(0) + .012
    shape = np.ceil((hi - lo) / H).astype(int) + 1
    # exact distance to the surface samples near the surface; a grid distance transform further out
    near = .003
    tree = cKDTree(pts)
    d = np.empty(int(np.prod(shape)), np.float32)
    ii = np.arange(len(d))
    for s in range(0, len(d), 2_000_000):
        k = ii[s:s + 2_000_000]
        g = np.stack(np.unravel_index(k, shape), 1) * H + lo
        d[k] = np.minimum(tree.query(g, distance_upper_bound=near)[0], near)
    d = d.reshape(shape)
    lab, _ = ndimage.label(d >= .0006)
    border = np.unique(np.r_[lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(),
                             lab[:, :, 0].ravel(), lab[:, :, -1].ravel()])
    outside = np.isin(lab, border[border > 0])
    far = np.where(outside, ndimage.distance_transform_edt(outside), -ndimage.distance_transform_edt(~outside)) * H
    sd = np.where(outside, d, -d)
    return np.where(d < near, sd, far).astype(np.float32), lo, shape, pts, puv


def design_field(phi, lo, shape, side):
    """Smooth the glove, ease its wrist into the sleeve opening and give it a clean cuff inside."""
    phi = ndimage.gaussian_filter(phi, SMOOTH / H)
    axes = [lo[k] + H * np.arange(shape[k]) for k in range(3)]
    U, A, W = np.meshgrid(*axes, indexing='ij')
    rho = np.hypot(A, W)
    # the wrist eases in to fit the sleeve opening (4.4 cm, so 4 mm clear of its rim) and widens again
    # over the back of the hand
    R_wrist = .040 + .048 * np.clip((U - .004) / .03, 0, 1) ** 2
    hand = S.smax(phi, rho - R_wrist, .006)
    hand = S.smax(hand, -.001 - U, .006)                      # the Tripo cuff ends at the sleeve opening
    # the cuff: fills the sleeve to SLEEVE_CLEAR inside its surface, palm side flat, closed inside the sleeve
    o, d, aa, pn = GL.hand_frame(side)
    # clearance from the sleeve's side wall only: near the opening, use the sleeve's cross-section 3 cm up,
    # so the closed end of the sleeve's field doesn't hold the cuff back from the hand
    Uw = np.minimum(U, -.03)
    world = (o + Uw[..., None] * d + A[..., None] * aa + W[..., None] * pn).reshape(-1, 3)
    inside = np.concatenate([D.sleeve_sdf(world[s:s + 1_000_000], side) for s in range(0, len(world), 1_000_000)])
    inside = inside.reshape(U.shape)
    # a little more room toward the opening, where the sleeve's rim curls in
    cuff = S.smax(inside + SLEEVE_CLEAR + .005 * np.clip((U + .03) / .03, 0, 1), W - PALM_W, .008)
    cuff = S.smax(cuff, U - .006, .006)                       # reaches just past the sleeve's end
    cuff = S.smax(cuff, -(U + .085), .008)                    # closed 8.5 cm up the sleeve
    return S.smin(hand, cuff, .012), axes


def main(src, out):
    import xatlas
    rng = np.random.default_rng(5)
    m = G.read(src)
    for p in m.parts:
        side = p['name'].split('_')[1]
        v, f, uv = p['v'].astype(float), p['f'].astype(np.int64), p['uv'].astype(float)
        mat = m.materials[p['material']]
        pb = mat['pbrMetallicRoughness']
        maps = [G.image_array(m, pb['baseColorTexture']['image']).astype(np.float32) / 255,
                G.image_array(m, pb['metallicRoughnessTexture']['image']).astype(np.float32) / 255]
        phi, lo, shape, pts, puv = signed_field(v, f, uv, rng)
        phi, axes = design_field(phi, lo, shape, side)
        fn = RegularGridInterpolator(axes, phi, bounds_error=False, fill_value=.02)
        vv, ff = Gm.mesh_from(fn, lo + H, lo + H * (np.array(shape) - 2), .0009, 40000, smooth=4)
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
        pb['baseColorTexture']['image'] = m.add_image(T.to_jpeg(baked[0], 90))
        pb['metallicRoughnessTexture']['image'] = m.add_image(T.to_jpeg(baked[1], 92))
        p.update(v=v2.astype(np.float32), n=S.vertex_normals(v2, fi).astype(np.float32), f=fi.astype(np.int32),
                 uv=uvl.astype(np.float32), uv1=None, ao=None)
        q = np.round(v2 / 1e-6).astype(np.int64)
        _, inv = np.unique(q, axis=0, return_inverse=True); fw = inv.ravel()[fi]
        E = np.sort(np.vstack([fw[:, [0, 1]], fw[:, [1, 2]], fw[:, [2, 0]]]), 1)
        _, cnt = np.unique(E, axis=0, return_counts=True)
        print(p['name'], 'triangles', len(fi), 'open edges', int((cnt == 1).sum()),
              'bounds', v2.min(0).round(3), v2.max(0).round(3), flush=True)
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
