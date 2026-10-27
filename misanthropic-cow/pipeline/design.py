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
    sh = np.array([s * .170, 1.308, -.032])
    up_angle = np.deg2rad(d.get('arm_abduction', 20.0))
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
# The mask, its horn tube and horns move as one rigid piece.  MASK_SEAT pushes that piece back
# onto the hood so its rim sits on the cheeks instead of floating in front of the face.
MASK_SEAT = np.array([0, 0, -.025])
MASK_NEW_ANCHOR = np.array([0, 1.512, .080]) + MASK_SEAT



def mask_transform(v):
    return (v - MASK_OLD_ANCHOR) * MASK_SCALE + MASK_NEW_ANCHOR


# The fur-covered cardboard tube that joins the two horns across the top of the head
# (v09's "crown block" stood in for it). Horns keep their scanned positions at its ends.
TUBE_C_SCAN = np.array([0, 1.6325, .0615]) + MASK_SEAT     # where the scanned horns expect the tube
# The tube sits directly on the mask's arched top edge, as in the photos of the mask with its horns:
# its underside rests on the rim at the crown (y 1.597), within a few mm of where the scanned horns put it
TUBE_C = np.array([0, 1.629, .070]) + MASK_SEAT
HORN_SHIFT = TUBE_C - TUBE_C_SCAN
TUBE_HALF, TUBE_R = .066, .037
MASK_BACK_Z = .080 + MASK_SEAT[2]     # the scanned mask shell's back plane (its rim) after mask_transform
# Outline of the mask rim in the XY plane, as a polar radius around MASK_RIM_C (Fourier fit of the
# scanned shell's outermost rim points, rms error 1.3 mm): [a0, cos1, sin1, cos2, sin2, ...]
MASK_RIM_C = np.array([0, 1.4775])
MASK_RIM_F = [.1115, .0007, .0055, -.0076, .0014, -.001, -.0024, -.0025, .0003, -.0007, -.0058, -.0015, .0005]


def mask_rim_radius(theta):
    r = np.full_like(theta, MASK_RIM_F[0])
    for k in range(1, (len(MASK_RIM_F) - 1) // 2 + 1):
        r += MASK_RIM_F[2 * k - 1] * np.cos(k * theta) + MASK_RIM_F[2 * k] * np.sin(k * theta)
    return r


def hood_face(p):
    """The hood's padded face opening: fills the mask's outline so the rim rests on fur all the way
    round.  Just inside the rim it is 2 mm inside the outline; its rounded front edge tucks ~3 mm into
    the shell, well clear of the inner wall; behind the rim it tapers back into the head."""
    q = p[..., :2] - MASK_RIM_C
    r = np.linalg.norm(q, axis=-1)
    R = mask_rim_radius(np.arctan2(q[..., 1], q[..., 0]))
    u = (MASK_BACK_Z + .003) - p[..., 2]            # depth behind the front face of the fill
    front = np.clip(1 - u / .009, 0, 1)
    back = np.clip((u - .009) / .075, 0, 1)
    inset = .002 + .012 * front ** 2 + .055 * back ** 2
    d = r - (R - inset)
    return np.maximum(d, np.maximum(-u, u - .09))


# ------------------------------------------------------------------ fur suit + hood
BACK_ROLL_Y = .925       # the back-fat roll over the panty waistband

def torso_sdf(p):
    return suit_parts(p, torso_only=True)['torso']


def suit_parts(p, torso_only=False):
    """Return dict of component SDFs (used for both the surface and skin-weight membership)."""
    out = {}
    chest = S.ellipsoid(p, (0, 1.19, -.028), (.163, .205, .128))
    shoulders = S.capsule(p, (-.145, 1.318, -.036), (.145, 1.318, -.036), .062)
    neck = S.round_cone(p, (0, 1.30, -.034), (0, 1.43, -.030), .080, .070)
    belly = S.ellipsoid(p, (0, .888, .072), (.236, .212, .234))     # full and low, as in Blue Shirt
    back = S.ellipsoid(p, (0, .99, -.045), (.186, .225, .148))
    torso = S.smin(chest, shoulders, .07)
    torso = S.smin(torso, back, .09)
    torso = S.smin(torso, belly, .15)          # a soft, round join where the belly meets the sides
    torso = S.smin(torso, neck, .05)
    # neckline: the torso garment stops at the base of the neck; the hood's neck tucks inside it
    torso = S.smax(torso, p[..., 1] - 1.405, .02)
    # underside: a shallow bowl (lowest under the front of the belly, rising to the sides and back),
    # with a soft fillet, so the padded belly reads round from below instead of sliced flat
    x, z = p[..., 0], p[..., 2]
    # a little back fat: a padded roll across the lower back that bulges out and overhangs the
    # panty waistband as a lip, rather than the back ending flat (owner's note)
    roll = S.ellipsoid(p, (0, BACK_ROLL_Y, -.128), (.170, .052, .082))
    torso = S.smin(torso, roll, .035)
    # the hem rises gently round the sides, so the bottom of the belly stays round instead of being sliced
    # off on a diagonal (owner's note); at the back it ends where it did, tucked under the roll
    hem = .768 + 1.3 * x * x + 1.15 * (z - .12) ** 2 - .016 * np.clip((-.06 - z) / .08, 0, 1)
    torso = S.smax(torso, hem - p[..., 1], .08)
    out['torso'] = torso          # the trunk: what the arms are kept clear of
    if torso_only:
        return out
    out['torso'] = with_deltoids(p, torso)
    for s, side in [(1, 'L'), (-1, 'R')]:
        sh, el, wr = arm_points(s)
        # its round head turns inside the shoulder cap (3 mm inside it); the upper arm is nearly the
        # cap's width, so the sleeve leaves the cap at a shallow angle instead of a crease
        upper = S.round_cone(p, sh, el, .061, .058)
        fore = S.round_cone(p, el, wr, .059, .048)
        arm = S.smin(upper, fore, .025)
        d = (wr - el) / np.linalg.norm(wr - el)
        arm = S.smax(arm, S.plane(p, wr - .004 * d, d), .012)
        out['arm_' + side] = arm
    # hood: a separate snug fur balaclava worn on the head (photos 0006/0013), ~2 cm of fur over a
    # 1.6 m wearer's head, with a neck that tucks into the torso's neckline.  The mask covers its front.
    head = S.ellipsoid(p, (0, 1.519, -.012), (.090, .118, .099))     # back of the head 2 cm flatter
    hood_neck = S.round_cone(p, (0, 1.355, -.030), (0, 1.47, -.022), .060, .064)
    hood = S.smin(head, hood_neck, .04)
    hood = S.smin(hood, hood_face(p), .03)
    hood = S.smax(hood, p[..., 2] - (MASK_BACK_Z + .003), .004)   # ends just inside the mask shell
    # the fur-covered tube that carries the horns is part of the mask, resting on its top edge
    out['tube'] = S.round_cylinder_x(p, TUBE_C, TUBE_HALF, TUBE_R, .012)
    out['hood'] = hood
    return out


def deltoid(p, s):
    """Padded shoulder: the torso garment rounds over the top and outside of the sleeve head, so
    the arm grows out of the body rather than plugging into it.  It is a ball centred on the
    shoulder pivot and the sleeve head is a smaller ball on the same centre, so however the arm
    swings, the sleeve turns inside the cap like a ball in a socket and never pokes through it.
    Only the outer half: the armpit side stays open so it cannot web."""
    sh, el, _ = arm_points(s)
    du = (el - sh) / np.linalg.norm(el - sh)
    out_dir = s * np.array([-du[1], du[0], 0.])      # perpendicular to the arm, outward/up
    out_dir = out_dir / np.linalg.norm(out_dir)
    cap = S.sphere(p, sh, .064)
    return S.smax(cap, -((p - sh) @ out_dir + .015), .025)


def with_deltoids(p, torso):
    for s in SIDES:
        torso = S.smin(torso, deltoid(p, s), .045)
    return torso


def suit_sdf(p):
    """The torso garment only (with its shoulder caps).  Sleeves are separate tubes set into the
    shoulder (as the costume is sewn), so the chest never fuses with the inner arm; the hood and the
    horn tube are separate too."""
    return with_deltoids(p, torso_sdf(p))


def hood_sdf(p):
    return suit_parts(p)['hood']


def tube_sdf(p):
    return suit_parts(p)['tube']


def sleeve_sdf(p, side):
    return suit_parts(p)['arm_' + side]


def body_sdf(p):
    c = suit_parts(p)
    return np.minimum.reduce([c['torso'], c['hood'], c['tube'], c['arm_L'], c['arm_R']])


# ------------------------------------------------------------------ leggings
THIGH_OUT, THIGH_R = .024, .096
def legging_parts(p):
    out = {}
    pelvis = S.ellipsoid(p, (0, .885, -.030), (.192, .130, .130))    # wide hips (Blue Shirt)
    for s, side in [(1, 'L'), (-1, 'R')]:
        hip, knee, ankle = J[f'Thigh_{side}'], J[f'Shin_{side}'], J[f'Foot_{side}']
        # the thigh's axis sits 2.4 cm out from the hip joint and it is slimmer at the top, so the hips keep
        # their width while the inner thighs part below the crotch (owner's note: more separation)
        thigh = S.round_cone(p, hip + [s * THIGH_OUT, .03, 0], knee, THIGH_R, .066)
        shin = S.round_cone(p, knee, ankle + [0, -.03, 0], .063, .040)
        calf = S.ellipsoid(p, (s * .098, .330, -.030), (.060, .110, .062))
        butt = S.ellipsoid(p, (s * .084, .800, -.068), (.106, .105, .092))
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
# Udder cups: big stuffed-cloth pillows that hang low on the chest and press together in the middle,
# as in the Blue Shirt reference (shoot 0120); each about 22 cm across, as in the photo.  The two are hand-made and not identical: the
# character's left cup is a little larger and sits a little lower and further out than the right.
CUP_C = {1: np.array([.100, 1.130, .100]), -1: np.array([-.096, 1.138, .097])}
CUP_R = {1: np.array([.112, .114, .142]), -1: np.array([.108, .110, .138])}
CUP_SAG = {1: (np.array([.006, -.040, .060]), np.array([.094, .080, .112])),
           -1: (np.array([-.004, -.036, .056]), np.array([.090, .076, .108]))}


def cup_sdf_one(p, s):
    """A pillow wider than it is tall, its stuffing settled into a lobe that hangs forward and down,
    so seen from the side the cup is a teardrop with the bottom teat at its lower front tip."""
    a = S.ellipsoid(p, CUP_C[s], CUP_R[s])
    off, r = CUP_SAG[s]
    b = S.ellipsoid(p, CUP_C[s] + off, r)
    return S.smin(a, b, .06)


def teat_specs(s):
    """(direction from cup centre to the base, teat pointing direction) per teat: one under each cup
    hanging forward and down, one on the outer side pointing out and down.  Sewn on by hand, so the
    two sides do not mirror each other."""
    if s == 1:
        return [(np.array([-.22, -.70, 1.70]), np.array([.06, -.60, .92])),
                (np.array([1.0, -.50, .62]), np.array([.90, -.45, .32]))]
    return [(np.array([.12, -.75, 1.80]), np.array([.00, -.66, .84])),
            (np.array([-1.0, -.66, .45]), np.array([-.82, -.60, .16]))]


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
        out.append((base - .012 * d, base + .072 * d))
    return out


TEATS = {s: teats(s) for s in SIDES}


def udder_sdf(p):
    d = np.full(p.shape[:-1], 1e3)
    for s in SIDES:
        c = cup_sdf_one(p, s)
        for a, b in TEATS[s]:
            c = S.smin(c, S.round_cone(p, a, b, .0160, .0122), .014)
        d = np.minimum(d, c)
    return d
