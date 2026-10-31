"""The owner's four approved generated views of the costume (references/approved_views: front, back, left
and right side), as the round-19 reference for the body's outline, the belly, the cups, the briefs and all
the markings.  The owner: "Gemini is guaranteed correct".

Each view is mapped into model coordinates.  Vertically it is piecewise linear: the floor -> 0, the crotch
-> 0.747 m (the leg length of the original photos, which the model keeps) and the horn tip -> 1.696 m.
Horizontally it is scaled like the torso (crotch to horn tip) about the leg axis.  The camera of each view
looks along one model axis, so a model point's pixel follows directly.

project_patches / project_spots paint the black shag and the leggings' white spots straight from the views:
each surface point samples every view that faces it and can see it (a depth map of the model per view), and
the views are blended by how squarely they face the point (sharply, so a marking isn't ghosted
from a neighbouring view).  The leggings are matched row by row, leg by
leg, so a spot keeps its place across the leg although the model's legs are not exactly the drawing's.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

DIR = Path(__file__).resolve().parent.parent / 'references' / 'approved_views'
CROTCH, HORN = .747, 1.696
# name: (file, top row, crotch row, floor row, leg-axis column, model horizontal axis, sign, camera direction)
VIEWS = {
    'front': ('front.png', 83, 748, 1233, 421, 0, 1, (0, 0, 1.)),
    'back': ('back.png', 72, 870, 1458, 507, 0, -1, (0, 0, -1.)),
    'left': ('left.png', 54, 727, 1220, 477, 2, -1, (1., 0, 0)),
    'right': ('right.jpg', 58, 729, 1221, 401, 2, 1, (-1., 0, 0)),
}
# the generated pictures' hands hang beside the thighs in the side views; their pale mittens are not spots
HANDS = {'left': ((-.06, .14), (.66, .88)), 'right': ((-.06, .14), (.66, .88))}

_cache = {}


class View:
    def __init__(self, name):
        f, self.top, self.crotch, self.floor, self.axis, self.hax, self.sign, cam = VIEWS[name]
        self.name, self.cam = name, np.array(cam)
        self.rgb = np.asarray(Image.open(DIR / f).convert('RGB')).astype(np.float32)
        self.h, self.w = self.rgb.shape[:2]
        self.k = (HORN - CROTCH) / (self.crotch - self.top)          # metres per pixel
        L = self.rgb.mean(-1)
        sat = self.rgb.max(-1) - self.rgb.min(-1)
        fg = ~((L > 246) & (sat < 10))
        self.fg = ndimage.binary_opening(ndimage.binary_fill_holes(ndimage.binary_closing(fg, iterations=2)), iterations=2)
        self.L, self.sat = L, sat

    def row(self, y):
        return np.interp(y, [0, CROTCH, HORN], [self.floor, self.crotch, self.top])

    def y(self, row):
        return np.interp(-np.asarray(row, float), [-self.floor, -self.crotch, -self.top], [0, CROTCH, HORN])

    def col(self, hz):
        return self.axis + self.sign * np.asarray(hz) / self.k

    def hz(self, col):
        return self.sign * (np.asarray(col, float) - self.axis) * self.k

    def pixel(self, p):
        return self.row(p[..., 1]), self.col(p[..., self.hax])

    def depth(self, p):
        return p @ self.cam                                      # larger is nearer the camera


def view(name):
    if name not in _cache:
        _cache[name] = View(name)
    return _cache[name]


def _runs(row_mask, min_len=4):
    xs = np.flatnonzero(row_mask)
    if len(xs) == 0:
        return []
    parts = np.split(xs, np.flatnonzero(np.diff(xs) > 2) + 1)
    return [(int(p.min()), int(p.max())) for p in parts if len(p) >= min_len]


# ------------------------------------------------------------------------------------------- outlines
def profiles(ys):
    """Per height: the figure's front and back in the side views (mean of left and right) and the torso's
    half-width in the front and back views (the run through the body's axis)."""
    out = {}
    fr, bk = [], []
    for name in ('left', 'right'):
        v = view(name)
        f_, b_ = [], []
        for y in ys:
            rr = _runs(v.fg[int(round(v.row(y)))])
            a, b = max(rr, key=lambda t: t[1] - t[0]) if rr else (np.nan, np.nan)
            h = sorted([float(v.hz(a)), float(v.hz(b))])
            b_.append(h[0]); f_.append(h[1])
        fr.append(f_); bk.append(b_)
    out['front'], out['back'] = np.nanmean(fr, 0), np.nanmean(bk, 0)
    hw = []
    for name in ('front', 'back'):
        v = view(name)
        w_ = []
        for y in ys:
            rr = _runs(v.fg[int(round(v.row(y)))])
            c = [t for t in rr if t[0] - 3 <= v.axis <= t[1] + 3]
            w_.append(abs(float(v.hz(c[0][1]) - v.hz(c[0][0]))) / 2 if c else np.nan)
        hw.append(w_)
    out['halfwidth'] = np.nanmean(hw, 0)
    return out


# --------------------------------------------------------------------------------------- projection
def _bilinear(img, r, c):
    return ndimage.map_coordinates(img, [np.asarray(r).ravel(), np.asarray(c).ravel()], order=1, mode='constant', cval=0).reshape(np.shape(r))


class Occluders:
    """Depth maps of the model seen from each view (splatted surface points on a 3 mm grid), so a point
    hidden behind an arm, a cup or the belly does not take that view's colour."""
    def __init__(self, points, cell=.003):
        self.cell, self.maps = cell, {}
        for name in VIEWS:
            v = view(name)
            r, c = v.pixel(points)
            d = v.depth(points)
            i, j = (r * v.k / cell).astype(int), (c * v.k / cell).astype(int)
            ok = (i >= 0) & (j >= 0)
            i, j, d = i[ok], j[ok], d[ok]
            m = np.full((i.max() + 2, j.max() + 2), -np.inf, np.float32)
            np.maximum.at(m, (i, j), d)
            m = ndimage.maximum_filter(m, 3)                  # close the gaps between splatted points
            self.maps[name] = m

    def visible(self, name, p, tol=.012):
        v = view(name)
        r, c = v.pixel(p)
        i, j = (r * v.k / self.cell).astype(int), (c * v.k / self.cell).astype(int)
        m = self.maps[name]
        ok = (i >= 0) & (j >= 0) & (i < m.shape[0]) & (j < m.shape[1])
        out = np.zeros(len(p), bool)
        out[ok] = v.depth(p[ok]) >= m[i[ok], j[ok]] - tol
        return out


def _blend(p, n, occ, sample, views):
    acc, wsum = np.zeros(len(p)), np.zeros(len(p))
    for name in views:
        v = view(name)
        w = np.clip(n @ v.cam, 0, 1) ** 6                 # the view facing the point most squarely dominates
        w = w * occ.visible(name, p)
        sel = w > 1e-4
        if not sel.any():
            continue
        acc[sel] += w[sel] * sample(name, p[sel])
        wsum[sel] += w[sel]
    return np.where(wsum > 1e-4, acc / np.maximum(wsum, 1e-9), 0.)


MIN_PATCH_PX = 150        # dark specks smaller than this in a view are fur shadows, not shag


def _patch_image(name):
    """The view's black shag: dark areas big enough to be a patch, not the leggings, the hooves or the mask's
    own paint, softened at the edge."""
    key = ('patch', name)
    if key not in _cache:
        v = view(name)
        dark = (v.L < 80) & v.fg
        lab, n = ndimage.label(dark)
        keep = np.zeros(n + 1, bool)
        for k, sl in enumerate(ndimage.find_objects(lab), 1):
            rows, cols = np.nonzero(lab[sl] == k)
            if len(rows) < MIN_PATCH_PX:
                continue
            yc = float(v.y(rows.mean() + sl[0].start))
            hc = float(v.hz(cols.mean() + sl[1].start))
            ylo = float(v.y(rows.max() + sl[0].start))
            if ylo < .70:                                   # reaches the legs: leggings, socks, slippers
                continue
            if yc < .90 and abs(hc) > .30 and v.hax == 0:    # the hooves at the hands
                continue
            if yc > 1.42:                                   # the mask's paint
                continue
            keep[k] = True
        m = keep[lab].astype(np.float32)
        _cache[key] = ndimage.gaussian_filter(m, 2.0)
    return _cache[key]


def project_patches(p, n, occ):
    """How black (0..1) the shag is at suit points p (normals n), from the four views."""
    def sample(name, q):
        v = view(name)
        r, c = v.pixel(q)
        return _bilinear(_patch_image(name), r, c)
    return np.clip((_blend(p, n, occ, sample, VIEWS) - .25) / .5, 0, 1)


def _leg_rows(name):
    """Per image row, the legs' extents as arrays (rows x 2 legs x [start, end] columns, NaN where unknown):
    front/back hold both legs, image-left first, split at the body's axis; the side views hold the leg in
    slot 0.  Each extent runs between the outermost dark (legging) pixels, so spots don't break it."""
    key = ('legs', name)
    if key not in _cache:
        v = view(name)
        dark = (v.L < 90) & v.fg
        if name in HANDS:
            (z0, z1), (y0, y1) = HANDS[name]
            c0, c1 = sorted([v.col(z0), v.col(z1)])
            dark[int(v.row(y1)):int(v.row(y0)), int(c0):int(c1)] = False
        out = np.full((v.h, 2, 2), np.nan)
        for r in range(int(v.row(.78)), int(v.row(.03))):
            xs = np.flatnonzero(dark[r])
            if name in ('front', 'back'):
                for k, part in enumerate((xs[xs < v.axis], xs[xs >= v.axis])):
                    if len(part) > 10:
                        out[r, k] = part.min(), part.max()
            elif len(xs) > 10:
                out[r, 0] = xs.min(), xs.max()
        _cache[key] = out
    return _cache[key]


def _spot_image(name):
    key = ('spot', name)
    if key not in _cache:
        v = view(name)
        white = ((v.L > 140) & (v.sat < 70)).astype(np.float32)
        white[:int(v.row(.745))] = 0                        # the briefs' lace above the leg line is not paint
        white[int(v.row(.19)):] = 0                         # nor the slippers below the socks' cuffs
        if name in HANDS:
            (z0, z1), (y0, y1) = HANDS[name]
            c0, c1 = sorted([v.col(z0), v.col(z1)])
            white[int(v.row(y1)):int(v.row(y0)), int(c0):int(c1)] = 0
        _cache[key] = ndimage.gaussian_filter(white, 2.0)
    return _cache[key]


def project_spots(p, n, occ, leg_extent):
    """How white (0..1) the paint is at leggings points p (normals n).  leg_extent[(view, side)] = (ys, lo, hi):
    the model leg's extent along the view's horizontal axis by height, for matching rows across the leg."""
    def sample(name, q):
        v = view(name)
        rows = np.clip(np.rint(v.row(q[:, 1])).astype(int), 0, v.h - 1)
        segs = _leg_rows(name)[rows]                            # n x 2 legs x 2
        side = np.where(q[:, 0] > 0, 1, -1)
        if name in ('front', 'back'):
            first = (side < 0) == (v.sign > 0)                  # front: image-left is the character's right leg
            seg = np.where(first[:, None], segs[:, 0], segs[:, 1])
        else:
            seg = segs[:, 0]
        lo, hi = np.zeros(len(q)), np.zeros(len(q))
        for sd in (1, -1):
            m = side == sd
            if (name, sd) in leg_extent and m.any():
                ys, l_, h_ = leg_extent[(name, sd)]
                lo[m], hi[m] = np.interp(q[m, 1], ys, l_), np.interp(q[m, 1], ys, h_)
        ok = np.isfinite(seg).all(1) & (hi - lo > 1e-3)
        u = np.clip((q[:, v.hax] - lo) / np.maximum(hi - lo, 1e-9), 0, 1)
        if v.sign < 0:
            u = 1 - u
        col = seg[:, 0] + u * (seg[:, 1] - seg[:, 0])
        ok &= (q[:, 1] > .20) & (q[:, 1] < .735)             # between the socks' cuffs and the briefs
        out = np.zeros(len(q))
        fade = np.clip((.735 - q[ok, 1]) / .02, 0, 1)         # a spot running up under the briefs fades out
        out[ok] = _bilinear(_spot_image(name), rows[ok], col[ok]) * fade
        return out
    res = np.zeros(len(p))
    for sd, sv in ((1, 'left'), (-1, 'right')):            # a side view only sees its own leg
        m = (p[:, 0] > 0) if sd > 0 else (p[:, 0] <= 0)
        if m.any():
            res[m] = _blend(p[m], n[m], occ, sample, ('front', 'back', sv))
    return np.clip((res - .3) / .4, 0, 1)
