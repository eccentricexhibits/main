"""Body design for the Misanthropic Cow v10, at real-world scale (metres).

Proportions follow the original 2012 Hasselblad shoot (MisCow_original2012HasselbladShoot_*):
a petite wearer (~1.60 m barefoot), narrow sloped shoulders, a long round padded belly that
hangs to the crotch over pink satin panties, two large pink udder cups on the chest and
black leggings with painted white spots.  Measured ratios from the photos:
  belly width ~= 2.0 x mask width; muzzle-bottom -> crotch ~= 3 x mask height;
  crotch ~= 46 % of standing height (wearer without mask, shot 0077).
Axes: +Y up, +Z forward (the way the character faces), +X = the character's LEFT.
The broken horn with exposed wire is on the character's RIGHT (-X), as in the photos.
"""
import numpy as np
import sdf as S

SIDES = (1, -1)          # +1 = character's left (+X), -1 = character's right (-X)


def arm_points(s, d=None):
    d = d or {}
    sh = np.array([s * .172, 1.335, -.032])
    up_angle = np.deg2rad(d.get('arm_abduction', 17.0))
    elbow = sh + .275 * np.array([s * np.sin(up_angle), -np.cos(up_angle), .07])
    fa = np.deg2rad(d.get('forearm_abduction', 11.0))
    wrist = elbow + .232 * np.array([s * np.sin(fa), -np.cos(fa), .30])
    return sh, elbow, wrist


J = {
    'Hips': np.array([0, .925, -.025]),
    'Spine': np.array([0, 1.06, -.035]),
    'Chest': np.array([0, 1.22, -.035]),
    'Neck': np.array([0, 1.395, -.035]),
    'Head': np.array([0, 1.465, -.020]),
}
for s, side in [(1, 'L'), (-1, 'R')]:
    sh, el, wr = arm_points(s)
    J[f'Shoulder_{side}'] = np.array([s * .035, 1.37, -.010])   # clavicle root
    J[f'UpperArm_{side}'] = sh
    J[f'Forearm_{side}'] = el
    J[f'Hand_{side}'] = wr
    J[f'Thigh_{side}'] = np.array([s * .086, .855, -.020])
    J[f'Shin_{side}'] = np.array([s * .094, .470, -.002])
    J[f'Foot_{side}'] = np.array([s * .100, .092, -.022])

HEAD_CENTER = np.array([0, 1.525, -.005])
MASK_SCALE = .75           # scanned mask -> real size (0.21 m wide)
MASK_OLD_ANCHOR = np.array([0, 1.73, .070])     # eye height on the mask's back plane (v09 units)
MASK_NEW_ANCHOR = np.array([0, 1.512, .080])



def mask_transform(v):
    return (v - MASK_OLD_ANCHOR) * MASK_SCALE + MASK_NEW_ANCHOR


def hood_only(p):
    return suit_parts(p)['hood']


def root_horn(v, depth=.014):
    """Slide a horn along its own root axis so its root is buried `depth` inside the hood."""
    side = np.sign(v[:, 0].mean())
    ax = np.abs(v[:, 0])
    root = v[ax < ax.min() + .012].mean(0)
    out_dir = v.mean(0) - root
    out_dir[1] *= .5
    out_dir /= np.linalg.norm(out_dir)
    lo, hi = -.15, .15       # find t with the root on the surface: hood(root + t*out_dir) == 0
    for _ in range(40):
        t = .5 * (lo + hi)
        if hood_only(root + t * out_dir) < 0:
            lo = t
        else:
            hi = t
    return v + (t - depth) * out_dir


# ------------------------------------------------------------------ fur suit + hood
def suit_parts(p):
    """Return dict of component SDFs (used for both the surface and skin-weight membership)."""
    out = {}
    chest = S.ellipsoid(p, (0, 1.19, -.028), (.163, .205, .128))
    shoulders = S.capsule(p, (-.145, 1.318, -.036), (.145, 1.318, -.036), .062)
    neck = S.round_cone(p, (0, 1.30, -.034), (0, 1.47, -.015), .078, .066)
    belly = S.ellipsoid(p, (0, .932, .055), (.226, .204, .220))
    back = S.ellipsoid(p, (0, .99, -.045), (.186, .225, .148))
    torso = S.smin(chest, shoulders, .07)
    torso = S.smin(torso, back, .09)
    torso = S.smin(torso, belly, .10)
    torso = S.smin(torso, neck, .05)
    # hem: lower at the front under the belly, higher at the back
    z = p[..., 2]
    hem = .808 + .030 * np.clip((.05 - z) / .25, 0, 1)
    torso = S.smax(torso, hem - p[..., 1], .025)
    out['torso'] = torso
    for s, side in [(1, 'L'), (-1, 'R')]:
        sh, el, wr = arm_points(s)
        upper = S.round_cone(p, sh, el, .070, .060)
        fore = S.round_cone(p, el, wr, .059, .048)
        arm = S.smin(upper, fore, .025)
        d = (wr - el) / np.linalg.norm(wr - el)
        arm = S.smax(arm, S.plane(p, wr - .004 * d, d), .012)
        out['arm_' + side] = arm
    # hood: loose fur hood over the head, crown tuft between the horns, face opening
    # the hood narrows above the brow so the horns stand proud of it, as in the photos
    taper = 1 - .30 * np.clip((p[..., 1] - 1.53) / .13, 0, 1) ** 1.5
    q = p.copy(); q[..., 0] = p[..., 0] / taper
    hood = S.ellipsoid(q, HEAD_CENTER + [0, 0, .018], (.127, .143, .140)) * (.5 + .5 * taper)
    tuft = S.ellipsoid(p, (0, 1.648, .036), (.074, .040, .060))
    hood = S.smin(hood, tuft, .035)
    hood = S.smin(hood, neck, .05)
    cavity = S.ellipsoid(p, (0, 1.490, .205), (.092, .114, .128))
    hood = S.smax(hood, -cavity, .012)
    out['hood'] = hood
    return out


def suit_sdf(p):
    """Torso + hood only.  Sleeves are separate tubes set into the shoulder (as the costume is sewn),
    so the chest side never fuses with the inner arm -- that fusion is what webbed into 'wings'."""
    c = suit_parts(p)
    return S.smin(c['torso'], c['hood'], .03)


def sleeve_sdf(p, side):
    return suit_parts(p)['arm_' + side]


def body_sdf(p):
    c = suit_parts(p)
    return np.minimum(S.smin(c['torso'], c['hood'], .03), np.minimum(c['arm_L'], c['arm_R']))


# ------------------------------------------------------------------ leggings
def legging_parts(p):
    out = {}
    pelvis = S.ellipsoid(p, (0, .885, -.030), (.178, .128, .128))
    for s, side in [(1, 'L'), (-1, 'R')]:
        hip, knee, ankle = J[f'Thigh_{side}'], J[f'Shin_{side}'], J[f'Foot_{side}']
        thigh = S.round_cone(p, hip + [s * .006, .03, 0], knee, .104, .066)
        shin = S.round_cone(p, knee, ankle + [0, -.03, 0], .063, .040)
        calf = S.ellipsoid(p, (s * .098, .330, -.030), (.060, .110, .062))
        butt = S.ellipsoid(p, (s * .078, .800, -.068), (.102, .105, .092))
        leg = S.smin(S.smin(thigh, shin, .03), calf, .045)
        out['leg_' + side] = leg
        pelvis = S.smin(pelvis, butt, .05)
    out['pelvis'] = pelvis
    return out


def legging_sdf(p):
    c = legging_parts(p)
    d = S.smin(c['pelvis'], c['leg_L'], .045)
    d = S.smin(d, c['leg_R'], .045)
    d = np.minimum(d, np.minimum(c['leg_L'], c['leg_R']))
    d = S.smax(d, p[..., 1] - 1.02, .02)     # top hidden inside the suit
    d = S.smax(d, .060 - p[..., 1], .01)     # ends inside the slippers
    return d


# ------------------------------------------------------------------ udder cups
CUP_C = {s: np.array([s * .100, 1.170, .090]) for s in SIDES}
CUP_R = np.array([.106, .110, .130])


def cup_sdf_one(p, s):
    a = S.ellipsoid(p, CUP_C[s], CUP_R)
    b = S.ellipsoid(p, CUP_C[s] + [s * .006, -.045, .018], (.094, .072, .108))   # sagging lower fullness
    return S.smin(a, b, .05)


def teat_specs(s):
    """(direction from cup centre to the base, teat pointing direction) per teat."""
    return [
        (np.array([s * -.28, -1.0, 1.05]), np.array([s * .06, -1.0, .78])),   # bottom, hangs forward/down over the belly
        (np.array([s * 1.0, -.62, .45]), np.array([s * .85, -.55, .18])),   # outer, points out and down
    ]


def surface_point(fn, origin, direction, tmax=.3):
    d = direction / np.linalg.norm(direction)
    t0, t1 = 0.0, tmax
    for _ in range(50):
        tm = .5 * (t0 + t1)
        if fn(origin + d * tm) < 0:
            t0 = tm
        else:
            t1 = tm
    return origin + d * t0


def teats(s):
    out = []
    for base_dir, point in teat_specs(s):
        base = surface_point(lambda q: cup_sdf_one(q, s), CUP_C[s] + [0, -.02, .02], base_dir)
        d = point / np.linalg.norm(point)
        out.append((base - .012 * d, base + .060 * d))
    return out


TEATS = {s: teats(s) for s in SIDES}


def udder_sdf(p):
    d = np.full(p.shape[:-1], 1e3)
    for s in SIDES:
        c = cup_sdf_one(p, s)
        for a, b in TEATS[s]:
            c = S.smin(c, S.round_cone(p, a, b, .0155, .0115), .014)
        d = np.minimum(d, c)
    return d
