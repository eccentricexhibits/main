"""Round 19 body: the shape of the owner's Tripo model of the costume, at the photo proportions.

assets/tripo_body.npz (made once by tripo_body_volume.py) holds the cleaned Tripo body as signed-distance
volumes in the Tripo model's own heights, its arm and leg landmarks and the sleeve radius profile.  This
module maps it to the model:
  - the torso keeps Tripo's widths and contours (shoulders, chest, belly, back); vertically it is mapped so
    the bottom of the belly lands at the photo height (0.84 m at the front) while the shoulders stay put;
  - the legs keep Tripo's shape but are as long as the original photos show: the crotch at 0.747 m;
  - the sleeves are tubes along Tripo's arm axes with Tripo's radius profile (its A-pose is the rest pose),
    set into a short shoulder cap that the torso keeps.
The head (mask, horns, snug hood), udder cups, gloves and slippers stay the owner's own assets.
"""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage

ASSET = Path(__file__).resolve().parent.parent / 'assets' / 'tripo_body.npz'
_d = np.load(ASSET)
_H, _LO, _SC = float(_d['h']), _d['origin'], float(_d['scale_m'])
_BODY = _d['body'].astype(np.float32) * _SC
_TORSO = _d['torso'].astype(np.float32) * _SC

# vertical maps, Tripo height -> model height (both monotonic, piecewise linear)
CROTCH, BELLY, SHOULDER = float(_d['crotch']), float(_d['belly_bottom']), float(_d['shoulder'])
TORSO_SRC = np.array([-1., BELLY, SHOULDER, 3.])
BELLY_DST = .815          # the bottom of the belly in the approved views (round 18's photo reading was 0.84)
TORSO_DST = np.array([-1. + BELLY_DST - BELLY, BELLY_DST, SHOULDER, 3.])     # shoulders unchanged
ANKLE_SRC, ANKLE_DST = .14, .092
WAIST_SRC = .90


def torso_y(y):
    return np.interp(y, TORSO_SRC, TORSO_DST)


LEG_SRC = np.array([-1., ANKLE_SRC, CROTCH, WAIST_SRC, SHOULDER, 3.])
LEG_DST = np.array([ANKLE_DST - (ANKLE_SRC + 1.), ANKLE_DST, .747, float(torso_y(WAIST_SRC)), SHOULDER, 3.])


def leg_y(y):
    return np.interp(y, LEG_SRC, LEG_DST)


def _sample(vol, p, src_y):
    q = np.stack([p[..., 0], src_y, p[..., 2]], -1)
    ijk = (q - _LO) / _H
    flat = ijk.reshape(-1, 3).T
    out = ndimage.map_coordinates(vol, flat, order=1, mode='nearest')
    return out.reshape(p.shape[:-1])


def torso_sdf(p):
    """Tripo's torso (arms cut away beyond the shoulder caps), in model heights."""
    return _sample(_TORSO, p, np.interp(p[..., 1], TORSO_DST, TORSO_SRC))


THIGH_FULL = .30          # the thighs are this much wider at the crotch than Tripo's, fading out by the knee


def thigh_scale(y):
    """Original shot 0077: each thigh is ~19.6 cm wide just below the crotch, Tripo's 14.2 cm (knees and calves
    match), so the thighs are widened about the legs' axes: fully at the crotch, not at all at the knee, and
    not above the crotch (the hips keep Tripo's width)."""
    knee, crotch = float(leg_y(.44)), .747
    up = np.clip((y - knee) / (crotch - knee), 0, 1)
    down = np.clip((crotch + .04 - y) / .04, 0, 1)
    return 1 + THIGH_FULL * up * up * (3 - 2 * up) * down * down * (3 - 2 * down)


def body_legs_sdf(p):
    """Tripo's whole body, with the legs' height map and fuller thighs (used for the legs and hips).  The
    widening maps each side about its leg's axis and blends to no change at the centre line, so the two
    sides meet without a seam."""
    y = p[..., 1]
    k = thigh_scale(y)
    hip_x = float(np.mean([abs(LEG[s][0][0]) for s in (1, -1)]))
    hip_z = float(np.mean([LEG[s][0][2] for s in (1, -1)]))
    ax = np.abs(p[..., 0])
    w = np.clip(ax / .05, 0, 1); w = w * w * (3 - 2 * w)
    q = p.copy()
    q[..., 0] = np.sign(p[..., 0]) * (ax / k + hip_x * (1 - 1 / k) * w)
    q[..., 2] = hip_z + (p[..., 2] - hip_z) / k
    return _sample(_BODY, q, np.interp(y, LEG_DST, LEG_SRC)) * k


# ---------------------------------------------------------------- fit to the approved views
# The torso is reshaped height by height so its outline matches the approved views: front and back from the
# side views, width from the front and back views.  Under the cups the chest sits where the views' cups are
# sewn on (their back), and above the shoulders and below the hem the torso keeps Tripo's shape.
FIT_Y = np.round(np.arange(.70, 1.50, .01), 3)
FLUFF = .012              # the views' outline is the fur's (and the shag's) tips, about this far out
CHEST_FRONT = [(1.14, .14), (1.17, .118), (1.30, .115), (1.33, .15)]


def _model_profile(ys):
    xs, zs = np.arange(-.30, .301, .005), np.arange(-.35, .45, .005)
    X, Z = np.meshgrid(xs, zs, indexing='ij')
    out = []
    for y in ys:
        p = np.stack([X, np.full_like(X, y), Z], -1)
        inside = torso_sdf(p) < 0
        if not inside.any():
            out.append((np.nan, np.nan, np.nan)); continue
        zi, xi = Z[inside], X[inside]
        out.append((zi.max(), zi.min(), np.abs(xi).max()))
    return np.array(out)


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _fit():
    import approved_views as AV
    from scipy.ndimage import gaussian_filter1d
    ys = FIT_Y
    g = AV.profiles(ys)
    m = _model_profile(ys)
    front_t = g['front'] - FLUFF
    chest = np.interp(ys, [c[0] for c in CHEST_FRONT], [c[1] for c in CHEST_FRONT])
    under_cups = (ys >= 1.14) & (ys <= 1.33)
    front_t = np.where(under_cups, chest, front_t)
    back_t = g['back'] - FLUFF * .5
    width_t = g['halfwidth'] - FLUFF * .5
    a = (front_t - back_t) / (m[:, 0] - m[:, 1])
    b = back_t - a * m[:, 1]
    c = np.clip(width_t / m[:, 2], .85, 1.15)
    # where the fit applies: the torso from the hem to the neck (z), the belly below the armpits (x)
    wz = _smoothstep(.76, .80, ys) * (1 - _smoothstep(1.36, 1.42, ys))
    wx = _smoothstep(.76, .80, ys) * (1 - _smoothstep(1.08, 1.13, ys))     # above, the views' arms join the body
    a = np.where(np.isfinite(a), a, 1); b = np.where(np.isfinite(b), b, 0); c = np.where(np.isfinite(c), c, 1)
    a, b, c = 1 + (a - 1) * wz, b * wz, 1 + (c - 1) * wx
    return gaussian_filter1d(a, 2), gaussian_filter1d(b, 2), gaussian_filter1d(c, 2)


_FIT = None


def fitted_torso_sdf(p):
    """Tripo's torso reshaped to the approved views' outline (z = a(y) z0 + b(y), x = c(y) x0)."""
    global _FIT
    if _FIT is None:
        _FIT = _fit()
    a, b, c = (np.interp(p[..., 1], FIT_Y, f) for f in _FIT)
    q = p.copy()
    q[..., 0] = p[..., 0] / c
    q[..., 2] = (p[..., 2] - b) / a
    return torso_sdf(q) * np.minimum(a, c)


def back_z(y, x=0.):
    """Where the back of the torso is at height y (for seating the back-fat roll and the bow)."""
    z = np.linspace(.1, -.35, 451)
    p = np.stack([np.full_like(z, x), np.full_like(z, y), z], -1)
    d = fitted_torso_sdf(p)
    j = np.flatnonzero(d > 0)
    return float(z[j[0]]) if len(j) else -.2


def front_z(x, y):
    z = np.linspace(-.05, .45, 501)[::-1]
    p = np.stack([np.full_like(z, x), np.full_like(z, y), z], -1)
    d = fitted_torso_sdf(p)
    j = np.flatnonzero(d < 0)
    return float(z[j[0]]) if len(j) else .2


ARM = {1: _d['arm_L'], -1: _d['arm_R']}                        # shoulder pivot, elbow, wrist, hooves' tip
ARM_T = {1: _d['arm_t_L'], -1: _d['arm_t_R']}
ARM_R = {1: _d['arm_r_L'], -1: _d['arm_r_R']}
LEG = {1: _d['leg_L'], -1: _d['leg_R']}                        # hip band, knee, ankle (Tripo heights)
MARKINGS = json.loads(str(_d['markings']))                    # shag lumps and leggings spots (Tripo heights)
BOW = np.array(_d['bow'], float)
BOW[1] = float(torso_y(BOW[1]))


def arm_points(s):
    sh, el, wr, _ = ARM[s]
    return np.array(sh, float), np.array(el, float), np.array(wr, float)


def _seg(p, a, b):
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(p - (a + t[..., None] * ab), axis=-1), t


def sleeve_sdf(p, s, wrist_cut=True):
    """A tube along Tripo's arm with its radius profile, ending flat at the wrist (the glove's cuff
    tucks inside)."""
    sh, el, wr = arm_points(s)
    t, r = ARM_T[s], ARM_R[s]
    L1 = np.linalg.norm(el - sh)
    d1, t1 = _seg(p, sh, el)
    d2, t2 = _seg(p, el, wr)
    a = d1 - np.interp(t1 * L1, t, r)
    b = d2 - np.interp(L1 + t2 * (t[-1] - L1), t, r)
    k = .02
    h = np.clip(.5 + .5 * (b - a) / k, 0, 1)
    d = b * (1 - h) + a * h - k * h * (1 - h)
    if wrist_cut:
        u = (wr - el) / np.linalg.norm(wr - el)
        plane = (p - (wr - .004 * u)) @ u
        k2 = .012
        h2 = np.clip(.5 - .5 * (plane - d) / k2, 0, 1)
        d = plane * (1 - h2) + d * h2 + k2 * h2 * (1 - h2)
    return d


def leg_points(s):
    """Hip, knee and ankle joint positions in model heights (the hip joint keeps round 18's height)."""
    hip_band, knee, ankle = (np.array(v, float) for v in LEG[s])
    return (np.array([s * .086, .893, -.020]),
            np.array([knee[0], float(leg_y(knee[1])), knee[2]]),
            np.array([ankle[0], ANKLE_DST, ankle[2]]))
