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
        white = ((v.L > 95) & (v.sat < 70)).astype(np.float32)          # paint in shade is mid grey; the leggings are under 40
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


# ------------------------------------------------------------------------------------ spots as decals
# Round 20: each painted spot is taken whole from the view that sees it most squarely and laid onto the leg as a
# decal: around the spot's centre the leg is unwrapped (arc length round the leg, height up it) and the view's
# picture is mapped on with the linear map the view has there.  A spot seen at a glancing angle in its view is
# so un-foreshortened properly instead of being smeared across the side of the leg, and every spot keeps the
# drawing's own brushed outline.
MIN_SPOT_PX = 40


def _leg_pixel(name, q, leg_extent):
    """Image (row, col) of leggings points q in view name, matching the model's leg to the drawing's leg row by
    row; ok marks points with a match."""
    v = view(name)
    rf = v.row(q[:, 1])
    rows = np.clip(np.rint(rf).astype(int), 0, v.h - 1)
    segs = _leg_rows(name)[rows]
    side = np.where(q[:, 0] > 0, 1, -1)
    if name in ('front', 'back'):
        first = (side < 0) == (v.sign > 0)
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
    u = (q[:, v.hax] - lo) / np.maximum(hi - lo, 1e-9)
    if v.sign < 0:
        u = 1 - u
    col = seg[:, 0] + u * (seg[:, 1] - seg[:, 0])
    return rf, col, ok


def _leg_axis(pts):
    """Per side, the leg's centre (x, z) by height, for unwrapping round the leg."""
    out = {}
    ys = np.arange(.15, .80, .02)
    for sd in (1, -1):
        q = pts[pts[:, 0] * sd > 0]
        cx, cz = [], []
        for y in ys:
            s = q[np.abs(q[:, 1] - y) < .012]
            cx.append(s[:, 0].mean() if len(s) else np.nan); cz.append(s[:, 2].mean() if len(s) else np.nan)
        cx, cz = np.array(cx), np.array(cz)
        ok = np.isfinite(cx)
        out[sd] = (ys[ok], cx[ok], cz[ok])
    return out


def _unwrap(q, c, axis):
    """(u, v) of points q relative to centre c: arc length round the leg (counter-clockwise seen from above) and
    height."""
    ys, cx, cz = axis
    ax, az = np.interp(q[:, 1], ys, cx), np.interp(q[:, 1], ys, cz)
    a0x, a0z = np.interp(c[1], ys, cx), np.interp(c[1], ys, cz)
    ang = np.arctan2(q[:, 2] - az, q[:, 0] - ax)
    ang0 = np.arctan2(c[2] - a0z, c[0] - a0x)
    r0 = np.hypot(c[2] - a0z, c[0] - a0x)
    da = (ang - ang0 + np.pi) % (2 * np.pi) - np.pi
    return r0 * da, q[:, 1] - c[1]


def _spot_labels(name):
    """Connected spots of a view, only inside the drawing's legs (the white backdrop beside them is not paint)."""
    key = ('spotlab', name)
    if key not in _cache:
        v = view(name)
        segs = _leg_rows(name)
        legs = np.zeros((v.h, v.w), bool)
        for r in range(v.h):
            for k in range(2):
                a, b = segs[r, k]
                if np.isfinite(a) and np.isfinite(b):
                    legs[r, int(a):int(b) + 1] = True
        legs = ndimage.binary_dilation(legs, iterations=3)
        # the backdrop seen between the legs (and between near and far leg in the side views) is not paint
        bg = ndimage.binary_dilation((v.L > 246) & (v.sat < 10), iterations=2)
        img = _spot_image(name) * legs * ~bg
        lab, nl = ndimage.label(img > .35)
        _cache[key] = (img.astype(np.float32), lab, nl)
    return _cache[key]


def spot_decals(pts, nrm, occ, leg_extent):
    """Find every spot in the four views, place it on the leg, and keep each spot once (from the view facing it
    most squarely).  pts/nrm: leggings surface samples."""
    axes = _leg_axis(pts)
    found = []
    for name in ('front', 'back', 'left', 'right'):
        v = view(name)
        img, lab, nl = _spot_labels(name)
        if not nl:
            continue
        sel = np.ones(len(pts), bool)
        if name == 'left':
            sel = pts[:, 0] > 0
        elif name == 'right':
            sel = pts[:, 0] <= 0
        q, nq = pts[sel], nrm[sel]
        face = nq @ v.cam
        vis = occ.visible(name, q) & (face > .15)
        rf, col, ok = _leg_pixel(name, q, leg_extent)
        ok &= vis & (q[:, 1] > .20) & (q[:, 1] < .735)
        col = np.where(ok, col, 0.)
        ri, ci = np.clip(np.rint(rf).astype(int), 0, v.h - 1), np.clip(np.rint(col).astype(int), 0, v.w - 1)
        hit = np.where(ok, lab[ri, ci], 0)
        sizes = ndimage.sum(np.ones_like(img), lab, np.arange(1, nl + 1))
        for i in range(1, nl + 1):
            if sizes[i - 1] < MIN_SPOT_PX:
                continue
            sl = ndimage.find_objects((lab == i).astype(int))[0]
            bh, bw = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if sizes[i - 1] / (bh * bw) < .22 and max(bh, bw) > 25:     # a thin sliver (an edge highlight), not paint
                continue
            f = np.flatnonzero(hit == i)
            if len(f) < 4:
                continue
            w = face[f] ** 2
            c = (w[:, None] * q[f]).sum(0) / w.sum()
            c = q[f][np.argmin(np.linalg.norm(q[f] - c, axis=1))]          # on the surface
            nc = (w[:, None] * nq[f]).sum(0); nc /= np.linalg.norm(nc)
            sd = 1 if c[0] > 0 else -1
            # the view's linear map at the centre: d(row, col) / d(u, v), u round the leg, v up it
            axis = axes[sd]
            a0x, a0z = np.interp(c[1], axis[0], axis[1]), np.interp(c[1], axis[0], axis[2])
            radial = np.array([c[0] - a0x, 0, c[2] - a0z]); radial /= np.linalg.norm(radial)
            t1 = np.array([-radial[2], 0, radial[0]])                       # counter-clockwise seen from above
            e = .004
            r0, c0, _ = _leg_pixel(name, c[None], leg_extent)
            r1, c1, _ = _leg_pixel(name, (c + e * t1)[None], leg_extent)
            r2, c2, _ = _leg_pixel(name, (c + [0, e, 0])[None], leg_extent)
            J = np.array([[r1[0] - r0[0], r2[0] - r0[0]], [c1[0] - c0[0], c2[0] - c0[0]]]) / e
            full = 1 / v.k
            gs = J[1, 0]
            if abs(gs) < .35 * full:                                        # at most ~3x un-foreshortening
                J[1, 0] = np.sign(gs if gs != 0 else 1) * .35 * full
            J[1, 1] = np.clip(J[1, 1], -.4 * full, .4 * full)               # little shear where the legs widen
            ys_, xs_ = np.nonzero(lab == i)
            reach = np.hypot((ys_ - r0[0]).max() - (ys_ - r0[0]).min(), (xs_ - c0[0]).max() - (xs_ - c0[0]).min()) * v.k
            found.append(dict(view=name, label=i, c=c, n=nc, side=sd, face=float(np.median(face[f])), row=r0[0], col=c0[0],
                              J=J, reach=float(np.clip(reach * 1.3 / max(abs(J[1, 0]) / full, .35), .03, .13)), area=sizes[i - 1] * v.k ** 2))
    # one decal per spot: drop a spot already taken from a view that faces it more squarely
    found.sort(key=lambda d: -d['face'])
    keep = []
    for d in found:
        if any(k['side'] == d['side'] and np.linalg.norm(k['c'] - d['c']) < .5 * min(k['reach'], d['reach'], .06) for k in keep):
            continue
        keep.append(d)
    for d in keep:
        d['axis'] = axes[d['side']]
        img, lab, _ = _spot_labels(d['view'])
        own = ndimage.binary_dilation(lab == d['label'], iterations=4)
        d['img'] = (img * own).astype(np.float32)
    return keep


def paint_decals(p, n, decals):
    """How white (0..1) the paint is at points p from the spot decals."""
    out = np.zeros(len(p))
    for d in decals:
        side = (p[:, 0] > 0) if d['side'] > 0 else (p[:, 0] <= 0)
        near = side & (np.linalg.norm(p - d['c'], axis=1) < d['reach']) & (n @ d['n'] > -.2)
        near &= (p[:, 1] > .20) & (p[:, 1] < .745)
        if not near.any():
            continue
        u, w = _unwrap(p[near], d['c'], d['axis'])
        r = d['row'] + d['J'][0, 0] * u + d['J'][0, 1] * w
        c = d['col'] + d['J'][1, 0] * u + d['J'][1, 1] * w
        val = _bilinear(d['img'], r, c)
        fade = np.clip((.735 - p[near, 1]) / .02, 0, 1)
        out[near] = np.maximum(out[near], val * fade)
    return np.clip((out - .3) / .4, 0, 1)
