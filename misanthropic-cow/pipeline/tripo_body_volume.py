"""One-off conversion of the owner's Tripo model of the costume ("cow costume 3d model", made from four
approved generated views) into the body asset of round 19: assets/tripo_body.npz.

The Tripo mesh is one closed surface with the udder cups, teats, black shag lumps and the tail bow fused
into it, and a fine noise over its fur.  This script:
  1. places it in the model's frame (hood crown at 1.639 m, knees on the v10 knees);
  2. fills the shag lumps, cups, teats and bow with a smooth membrane spanning their rims, so the plain
     suit underneath remains (they are rebuilt separately: strands, v10 cups, the bowtie);
  3. turns the cleaned surface into a signed-distance volume on a 4 mm grid, smoothed (sigma 6 mm);
  4. fits the arms (shoulder pivot, elbow, wrist, hand tip and a radius profile) and the legs;
  5. makes a second volume for the torso with the arms cut away beyond the shoulders and the armpits
     closed, since the sleeves are separate garments;
  6. records the markings: each shag lump's footprint on the filled suit (centre, axes, half-extents)
     and each white spot painted on Tripo's leggings, which follow the approved generated views.
Everything is stored in the Tripo model's own heights; tripo_body.py maps them to the photo proportions.

usage: python tripo_body_volume.py <cow_costume_3d_model.obj> <cow_costume_3d_model_basecolor.jpg> <out.npz>
"""
import sys
import json
import numpy as np
import scipy.sparse as sp
from scipy import ndimage
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import splu
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SCALE, DZ = 1.639 / 0.948, 0.0730        # Tripo units -> metres (hood crown), and the knee alignment in z
H = .004                                 # grid step (m)
SMOOTH = 1.5                             # gaussian sigma (voxels) over the signed distance
CAP = .10                                # length of the shoulder cap the torso keeps along the upper arm (m)


def read_obj(path):
    v, vt, fv, ft = [], [], [], []
    with open(path) as fh:
        for line in fh:
            c = line[:2]
            if c == 'v ':
                v.append(line[2:])
            elif c == 'vt':
                vt.append(line[3:])
            elif c == 'f ':
                a = line[2:].split()
                fv.append([int(s.split('/')[0]) for s in a]); ft.append([int(s.split('/')[1]) for s in a])
    V = np.array(' '.join(v).split(), np.float64).reshape(-1, 3)
    UV = np.array(' '.join(vt).split(), np.float64).reshape(-1, 2)
    return V, UV, np.array(fv, np.int64) - 1, np.array(ft, np.int64) - 1


def vertex_colours(V, UV, F, FT, tex):
    th, tw = tex.shape[:2]
    col = np.zeros((len(V), 3)); cnt = np.zeros(len(V))
    for k in range(3):
        uv = UV[FT[:, k]]
        c = tex[np.clip(((1 - uv[:, 1]) * th).astype(int), 0, th - 1), np.clip((uv[:, 0] * tw).astype(int), 0, tw - 1)]
        np.add.at(col, F[:, k], c); np.add.at(cnt, F[:, k], 1)
    return col / np.maximum(cnt, 1)[:, None]


def fill_mask(V, F, C, A):
    """Shag lumps (black islands not reaching the legs or the mask), the udder cups and teats, and the bow."""
    x, y, z = V.T
    r, g, b = C.T
    black = C.mean(1) < 60
    pink = (r > 150) & (r - g > 30) & (r - b > 10)
    gold = (r > 150) & (g > 100) & (b < 90) & (r - b > 80)
    nb, lab = connected_components(A[black][:, black], directed=False)
    bi = np.flatnonzero(black)
    lump = np.zeros(len(V), bool)
    for k in range(nb):
        idx = bi[lab == k]
        if len(idx) < 30 or y[idx].min() < .55 or y[idx].mean() > 1.42 or np.abs(x[idx]).mean() > .44:
            continue                       # legs and slippers, the mask's paint, the hooves
        lump[idx] = True
    mask = lump | (pink & (y > .95) & (y < 1.40) & (np.abs(x) < .33) & (z > -.02)) | (gold & (z < 0))
    for _ in range(2):
        mask |= A @ mask.astype(float) > 0
    return mask


def membrane(V, A, mask):
    """Each filled vertex becomes the average of its neighbours, then the seam is relaxed."""
    deg = np.asarray(A.sum(1)).ravel()
    mi, fi = np.flatnonzero(mask), np.flatnonzero(~mask)
    lu = splu((sp.diags(deg[mi]) - A[mi][:, mi]).tocsc())
    rhs = A[mi][:, fi] @ V[fi]
    Vn = V.copy()
    Vn[mi] = np.column_stack([lu.solve(rhs[:, k]) for k in range(3)])
    ring = mask | (A @ mask.astype(float) > 0)
    ring |= A @ ring.astype(float) > 0
    for _ in range(30):
        Vn[ring] = .5 * Vn[ring] + .5 * ((A @ Vn) / deg[:, None])[ring]
    return Vn


def occupancy(V, F, lo, shape):
    P = np.vstack([V, V[F].mean(1)] + [.5 * (V[F[:, a]] + V[F[:, b]]) for a, b in ((0, 1), (1, 2), (2, 0))])
    ijk = np.rint((P - lo) / H).astype(int)
    shell = np.zeros(shape, bool)
    shell[ijk[:, 0], ijk[:, 1], ijk[:, 2]] = True
    return ndimage.binary_fill_holes(ndimage.binary_closing(shell, iterations=1))


def signed(inside):
    sd = (ndimage.distance_transform_edt(~inside) - ndimage.distance_transform_edt(inside)) * H
    return ndimage.gaussian_filter(sd, SMOOTH)


def sample(sd, lo, p):
    q = ((np.atleast_2d(p) - lo) / H).T
    return ndimage.map_coordinates(sd, q, order=1, mode='nearest')


def fit_arm(V, s):
    """Shoulder pivot, elbow, wrist and hooves' tip for one arm (s = +1 character left)."""
    x, y, z = V.T
    cen = []
    for yy in np.arange(.98, .855, -.02):                 # below the armpit the arm stands clear of the body
        a = V[(np.abs(y - yy) < .006) & (s * x > .24)]
        a = a[s * a[:, 0] > s * a[:, 0].max() - .20]
        cen.append(a.mean(0))
    cen = np.array(cen)
    c0 = cen.mean(0); d = np.linalg.svd(cen - c0)[2][0]
    d = d if d[1] < 0 else -d                              # pointing down the arm
    wrist = c0 + d * ((.86 - c0[1]) / d[1])
    elbow = c0 + d * ((1.03 - c0[1]) / d[1])
    shoulder = np.array([s * .19, 1.275, -.030])
    tip = V[(s * x > .3) & (y < .80)]
    tip = tip[np.argmin(tip[:, 1])]
    return shoulder, elbow, wrist, tip


def arm_radius(sd, lo, pts, s, n=40):
    """Radius of the sleeve along shoulder -> elbow -> wrist, from rays cast round the axis (outer side)."""
    seg = [(pts[0], pts[1]), (pts[1], pts[2])]
    lens = [np.linalg.norm(b - a) for a, b in seg]
    t = np.linspace(0, sum(lens), n); out = []
    for tt in t:
        k = 0 if tt <= lens[0] else 1
        a, b = seg[k]; u = (b - a) / np.linalg.norm(b - a)
        c = a + u * (tt - (0 if k == 0 else lens[0]))
        e1 = np.cross(u, [0, 0, 1.]); e1 /= np.linalg.norm(e1); e2 = np.cross(u, e1)
        hits = []
        for ang in np.linspace(0, 2 * np.pi, 24, endpoint=False):
            dr = np.cos(ang) * e1 + np.sin(ang) * e2
            if s * dr[0] < -.3:                            # towards the body: fused near the armpit
                continue
            rr = np.linspace(0, .16, 161)
            v = sample(sd, lo, c + rr[:, None] * dr)
            j = np.flatnonzero(v > 0)
            hits.append(rr[j[0]] if len(j) else .16)
        out.append(np.percentile(hits, 40))
    return t, np.array(out)


def markings(V, Vn, C, A, arms):
    """Shag patches from the lumps' footprints (where the fill put them on the suit) and the white spots
    painted on the leggings, as (centre, axes, half-extents) in Tripo's heights; 'piece' says whether a
    patch is on the torso or a sleeve."""
    x, y, z = V.T
    L, sat = C.mean(1), C.max(1) - C.min(1)

    def islands(sel, minsize):
        nb, lab = connected_components(A[sel][:, sel], directed=False)
        idx = np.flatnonzero(sel)
        return [idx[lab == k] for k in range(nb) if (lab == k).sum() >= minsize]

    def ellipse(P):
        c = P.mean(0)
        U = np.linalg.svd(P - c, full_matrices=False)[2]          # rows: main axes; the last is the normal
        q = (P - c) @ U.T
        return c, U, [(np.percentile(q[:, k], 96) - np.percentile(q[:, k], 4)) / 2 for k in range(2)]

    def piece(c):
        for s, side in ((1, 'L'), (-1, 'R')):
            sh, el, wr, tip = arms[s]
            du = (el - sh) / np.linalg.norm(el - sh)
            if (c - sh) @ du > CAP and np.linalg.norm(np.cross(c - sh, du)) < .12:
                return 'sleeve_' + side
        return 'torso'

    patches, spots = [], []
    for idx in islands(L < 60, 30):
        if y[idx].min() < .55 or y[idx].mean() > 1.42 or np.abs(x[idx]).mean() > .44:
            continue
        c, U, r = ellipse(Vn[idx])
        patches.append({'piece': piece(V[idx].mean(0)), 'c': c.tolist(), 'axes': U.tolist(), 'r': r, 'n': int(len(idx))})
    legs = (L > 120) & (sat < 45) & (y > .16) & (y < .64) & (np.abs(x) < .26)
    for idx in islands(legs, 25):
        c, U, r = ellipse(V[idx])
        spots.append({'c': c.tolist(), 'axes': U.tolist(), 'r': r, 'n': int(len(idx))})
    return {'patches': patches, 'spots': spots}


def seg_dist(p, a, b):
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ab), axis=1), t


def main(obj, tex_path, out):
    V, UV, F, FT = read_obj(obj)
    V = V * SCALE; V[:, 2] += DZ
    C = vertex_colours(V, UV, F, FT, np.asarray(Image.open(tex_path).convert('RGB'), np.float64))
    n = len(V)
    E = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    A = sp.coo_matrix((np.ones(len(E)), (E[:, 0], E[:, 1])), shape=(n, n)).tocsr()
    A = ((A + A.T) > 0).astype(np.float64)
    mask = fill_mask(V, F, C, A)
    Vn = membrane(V, A, mask)
    lo = Vn.min(0) - .03
    shape = np.ceil((Vn.max(0) + .03 - lo) / H).astype(int) + 1
    inside = occupancy(Vn, F, lo, shape)
    body = signed(inside)
    arms = {s: fit_arm(Vn, s) for s in (1, -1)}
    radius = {s: arm_radius(body, lo, arms[s], s) for s in (1, -1)}
    # torso: cut the arms away beyond the shoulder pivot (with a margin round the sleeve), close the armpits
    g = np.stack(np.meshgrid(*[lo[k] + H * np.arange(shape[k]) for k in range(3)], indexing='ij'), -1).reshape(-1, 3)
    # The torso keeps a short cap over each shoulder (CAP along the upper arm, like the round-17 shoulder cap);
    # the sleeve's head turns inside it.  Near the body the cut hugs the sleeve; past the armpit and round the
    # mitten it is generous, so no scraps of the Tripo arm or hand are left on the torso.
    cut = np.zeros(len(g), bool)
    for s, (sh, el, wr, tip) in arms.items():
        t, r = radius[s]
        du = (el - sh) / np.linalg.norm(el - sh)
        along = (g - sh) @ du
        L1 = np.linalg.norm(el - sh)
        for a, b, t0, t1 in ((sh, el, 0., L1), (el, wr, L1, t[-1]), (wr, tip, t[-1], t[-1])):
            dd, tt = seg_dist(g, a, b)
            rr = np.interp(t0 + (t1 - t0) * tt, t, r)
            margin = np.where(along < .20, .02, .045)
            if a is wr:
                rr, margin = .08, .03
            cut |= (along > CAP) & (dd < rr + margin)
    torso_in = inside & ~cut.reshape(shape)
    box = np.zeros(shape, bool)                            # close the armpits only, so nothing else gets bridged
    ii = lambda v, k: int(np.clip(round((v - lo[k]) / H), 0, shape[k] - 1))
    for s in (1, -1):
        xa, xb = sorted((ii(s * .16, 0), ii(s * .36, 0)))
        box[xa:xb, ii(.98, 1):ii(1.30, 1), :] = True
    ball = ndimage.generate_binary_structure(3, 1)
    closed = ndimage.binary_closing(torso_in, structure=ball, iterations=4)
    torso_in = np.where(box, closed, torso_in)
    torso = signed(torso_in)
    q = lambda a: np.clip(np.rint(a / 1e-4), -32000, 32000).astype(np.int16)
    legs = {}
    for s in (1, -1):
        legs[s] = {}
        for nm, yy in (('ankle', .15), ('knee', .44), ('hip_band', .55)):
            sl = Vn[(np.abs(Vn[:, 1] - yy) < .005) & (s * Vn[:, 0] > .005) & (s * Vn[:, 0] < .30)]
            legs[s][nm] = sl.mean(0)
    gold = (C[:, 0] > 150) & (C[:, 1] > 100) & (C[:, 2] < 90) & (C[:, 0] - C[:, 2] > 80) & (V[:, 2] < 0)
    np.savez_compressed(
        out, body=q(body), torso=q(torso), origin=lo, h=H, scale_m=1e-4,
        arm_L=np.array(arms[1]), arm_R=np.array(arms[-1]),
        arm_t_L=radius[1][0], arm_r_L=radius[1][1], arm_t_R=radius[-1][0], arm_r_R=radius[-1][1],
        leg_L=np.array([legs[1][k] for k in ('hip_band', 'knee', 'ankle')]),
        leg_R=np.array([legs[-1][k] for k in ('hip_band', 'knee', 'ankle')]),
        bow=V[gold].mean(0), crotch=.635, belly_bottom=.790, shoulder=1.300,
        markings=json.dumps(markings(V, Vn, C, A, arms)))
    print('grid', shape, 'filled vertices', int(mask.sum()))
    for s in (1, -1):
        print('arm', s, np.round(arms[s], 3).tolist(), 'radius', np.round(radius[s][1][[0, 10, 20, 30, 39]], 3))


if __name__ == '__main__':
    main(*sys.argv[1:4])
