"""Round 19 markings: the black shag patches on the suit and the white spots painted on the leggings, laid
out as in the owner's approved generated views (1_FRONT, 2_BACK, 3_SIDE_facing_left and the right-side
view), which the Tripo model was made from.

- Shag patches: the Tripo model's black lumps, measured where they sit on the suit (tripo_body_volume.py),
  mapped into the model.  Each is a noisy ellipse (centre, axes, half-extents) on one garment piece.
- Leggings spots: measured on the four views (pixel centre and half-size of each spot) and projected onto
  the leggings along each view's direction.  Each view is scaled from the floor to the crotch, so the spots
  keep their place on the leg although the model's legs are longer than in the generated pictures.
A patch or spot is (centre, half-extents, axes): axes rows are the ellipse's two in-surface directions and
its normal, so painting works the same at any orientation.
"""
import numpy as np

# view -> (floor row, crotch row, horizontal model axis, image column of the leg axis (function of the row),
#          sign from image column to model axis, ray direction into the body)
VIEWS = {
    'front': (1232, 748, 0, lambda r: 420., 1, (0, 0, -1.)),
    'back': (1458, 870, 0, lambda r: 505., -1, (0, 0, 1.)),
    'left': (1218, 728, 2, lambda r: 460., -1, (-1., 0, 0)),          # facing image-left: the character's left side
    'right': (1222, 736, 2, lambda r: 405. + (r - 785) * 115 / 190, 1, (1., 0, 0)),
}
# (view, column, row, half-width px, half-height px), read off gridded enlargements of the approved views
SPOTS = [
    ('front', 390, 785, 20, 30), ('front', 350, 978, 25, 20), ('front', 520, 755, 15, 18), ('front', 475, 865, 33, 28),
    ('front', 428, 910, 10, 12), ('front', 530, 1010, 15, 22),
    ('back', 430, 945, 47, 25), ('back', 585, 945, 35, 13), ('back', 425, 1165, 38, 33), ('back', 435, 1215, 17, 15),
    ('left', 512, 800, 20, 15), ('left', 425, 870, 15, 35), ('left', 440, 935, 8, 15), ('left', 450, 1015, 30, 30),
    ('left', 508, 1010, 8, 10), ('left', 530, 965, 8, 20),
    ('right', 395, 785, 28, 15), ('right', 468, 945, 8, 25), ('right', 615, 975, 18, 22),
]
CROTCH_Y = .747
SPOT_GROW = 1.15         # the spots' painted edge is ragged; measured to the solid white, they read a little larger


def _project(sdf, start, ray):
    """First point where the ray from `start` enters the surface; if it misses, the surface point nearest
    the ray's closest approach."""
    t = np.linspace(0, 1.0, 1001)
    pts = start + t[:, None] * np.asarray(ray)
    d = sdf(pts)
    j = np.flatnonzero(d < 0)
    if len(j):
        return pts[j[0]]
    p = pts[np.argmin(d)].copy()
    for _ in range(6):
        g = np.array([sdf(p[None] + e[None])[0] - sdf(p[None] - e[None])[0] for e in np.eye(3) * 1e-3]) / 2e-3
        p = p - sdf(p[None])[0] * g / max(np.linalg.norm(g), 1e-9)
    return p


def leg_spots(legging_sdf):
    out = []
    for view, col, row, rw, rh in SPOTS:
        floor, crotch, hax, ref, sign, ray = VIEWS[view]
        k = CROTCH_Y / (floor - crotch)
        y = (floor - row) * k
        h = sign * (col - ref(row)) * k
        start = np.zeros(3)
        start[1], start[hax] = y, h
        start -= .6 * np.asarray(ray)
        c = _project(legging_sdf, start, ray)
        u = np.zeros(3); u[hax] = 1.
        out.append((c, np.array([rw * k, rh * k, .03]) * SPOT_GROW, np.array([u, [0, 1., 0], np.asarray(ray)])))
    keep = []
    for s in sorted(out, key=lambda s: -s[1][0] * s[1][1]):            # a spot seen in two views is kept once
        if all(np.linalg.norm(s[0] - q[0]) > .05 for q in keep):
            keep.append(s)
    return keep


# shag patch -> spring bone (rig.SHAG_NAMES order): chest, belly, upper back, lower back, left sleeve, right sleeve
def _bone(piece, c):
    if piece == 'sleeve_L':
        return 4
    if piece == 'sleeve_R':
        return 5
    if c[2] > 0:
        return 0 if c[1] > 1.15 else 1
    return 2 if c[1] > 1.15 else 3


MIN_LUMP = 1000          # Tripo lumps smaller than this (vertices) are specks, not patches
GROW = 1.30              # the measured footprint trims the ragged edge; the approved views read bolder


def shag_patches(raw, torso_y, head_dz):
    """(centre, half-extents, axes, piece, bone) for each of Tripo's lumps, mapped into the model."""
    out = []
    for p in raw:
        if p['n'] < MIN_LUMP:
            continue
        c = np.array(p['c'], float)
        U = np.array(p['axes'], float)
        r = np.array(list(p['r']) + [0.], float) * GROW
        if p['piece'] == 'torso':
            c[1] = float(torso_y(c[1]))
            if c[2] > head_dz and c[1] > 1.33:
                if c[1] > 1.37:
                    continue            # under the mask's chin: the neckline dips there, so no suit to carry it
                c[1] = 1.30             # the throat patch runs down onto the right side of the chest
            r[2] = .06
        else:
            r[2] = .035
        out.append((c, r, U, p['piece'], _bone(p['piece'], c)))
    return out
