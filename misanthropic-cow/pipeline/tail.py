"""The tail: a gold satin bow tied on at the back of the suit's hem, with a tan two-core lamp cord
hanging from its knot down to the floor, ending in a two-prong plug (the owner's photos: shoot 0071
and the back view with the bow).

The cord is a chain of bones driven by a baked rope simulation (anim.Dance.dynamics): it swings
with the hips, collides with the seat, thighs, shins, slippers and the floor, and settles back.
Everything is built at the bind pose with the cord hanging straight down.
"""
import numpy as np
import sdf as S
import design as D
import garments as Gm

KNOT = np.array([0, .950, -.201])         # on the fur at the back, just above the suit hem (y ~ .90 at x = 0)
ANCHOR = KNOT + np.array([0, -.014, -.004])
N_SEG = 12
SEG = .072                                 # 12 x 7.2 cm = 86 cm of cord
PLUG_SEG = .050                            # cord end to blade tips: the plug rides its own rope segment
CORD_A, CORD_B = .0036, .0019              # zip-cord half width / half thickness
FLOOR = .0045
PLUG_FLOOR = .015                          # the plug is ~1.5 x 2.7 cm in section, so it rests a little higher


def rest_points():
    """Particles at the bind pose, straight down from the knot: 0..N_SEG along the cord, then one
    more at the plug's blade tips."""
    cord = ANCHOR + np.arange(N_SEG + 1)[:, None] * np.array([0, -SEG, 0])
    return np.vstack([cord, cord[-1] + [0, -PLUG_SEG, 0]])


# ---------------------------------------------------------------- bow
def _box(p, c, h):
    q = np.abs(p - c) - h
    return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(q.max(-1), 0)


def bow_sdf(p):
    """Two puffed ribbon loops, a gathered knot and two tails with V-cut ends; local frame at the knot
    with x sideways, y up and z out of the back (world -z)."""
    q = p - KNOT
    x, y, z = q[..., 0], q[..., 1], -q[..., 2]
    th = .0016
    d = np.full(x.shape, 1e3)
    for sg in (1, -1):
        a = np.deg2rad(14) * sg                      # loops tilt up toward their outer ends
        xl = x * np.cos(a) + y * np.sin(a)
        yl = -x * np.sin(a) + y * np.cos(a)
        cx, ax, az = sg * .036, .034, .0095
        r = np.sqrt(((xl - cx) / ax) ** 2 + ((z - .007) / az) ** 2)
        ring = (r - 1) * az
        u = np.clip(sg * (xl - cx) / ax * .5 + .5, 0, 1)
        hy = .0055 + .0105 * u ** .8 - .002 * u ** 4
        loop = np.maximum(np.abs(ring) - th, np.abs(yl) - hy)
        d = np.minimum(d, loop)
        # tail: a flat ribbon strip falling down and out from the knot, V-notched at the end
        a0, a1 = np.array([sg * .004, -.004]), np.array([sg * .028, -.078])
        dv = a1 - a0; L = np.linalg.norm(dv); dv /= L
        rel = np.stack([x - a0[0], y - a0[1]], -1)
        t = rel @ dv
        perp = rel @ np.array([-dv[1], dv[0]])
        hw = .0085 + .003 * np.clip(t / L, 0, 1)
        notch = .010 * (1 - np.clip(np.abs(perp) / hw, 0, 1))
        strip = np.maximum.reduce([np.abs(z - .010 + .004 * np.clip(t / L, 0, 1)) - th, np.abs(perp) - hw, -t, t - (L - notch)])
        d = np.minimum(d, strip)
    knot = S.ellipsoid(np.stack([x, y, z], -1), (0, 0, .010), (.0105, .0125, .0085))
    return S.smin(d, knot, .004)


# ---------------------------------------------------------------- plug
def plug_frame():
    """Plug at the end of the cord, in bind space: top centre and the hanging direction."""
    end = rest_points()[N_SEG]
    return end, np.array([0, -1., 0])


def plug_body_sdf(p):
    end, dn = plug_frame()
    q = p - end
    yl = -(q @ np.array([0, 1., 0]))                     # distance down from the cord's end
    x, z = q[..., 0], q[..., 2]
    relief = S.round_cone(p, end + [0, .002, 0], end + [0, -.011, 0], .0042, .0068)
    body = _box(np.stack([x, yl, z], -1), np.array([0, .023, 0]), np.array([.0115, .0115, .0055])) - .0022
    grip = .00025 * np.sin(yl * 1400) * np.clip((yl - .014) / .004, 0, 1)      # moulded grip ridges
    return S.smin(relief, body + grip, .004)


def plug_blade_sdf(p):
    end, dn = plug_frame()
    q = p - end
    yl = -q[..., 1]
    d = np.full(yl.shape, 1e3)
    for sx in (1, -1):
        d = np.minimum(d, _box(np.stack([q[..., 0], yl, q[..., 2]], -1), np.array([sx * .0064, .0405, 0]),
                               np.array([.0006, .0085, .0031])) - .0002)
    return d


# ---------------------------------------------------------------- cord
def cord_mesh(rings_per_m=260, around=14):
    """Tube along the bind polyline with a zip-cord section (two cores joined by a thin web)."""
    P = rest_points()
    top = KNOT + np.array([0, -.004, -.002])
    length = SEG * N_SEG
    s = np.linspace(-np.linalg.norm(ANCHOR - top), length + .004, int((length + .02) * rings_per_m))
    th = np.linspace(0, 2 * np.pi, around, endpoint=False)
    cx = CORD_A * np.cos(th)
    cz = CORD_B * np.sin(th) * (1 - .30 * np.exp(-(np.cos(th) / .28) ** 2))      # the groove between the cores
    v = []
    for si in s:
        c = top + (ANCHOR - top) * (1 + si / np.linalg.norm(ANCHOR - top)) if si < 0 else ANCHOR + np.array([0, -si, 0])
        v.append(np.stack([c[0] + cx, np.full(around, c[1]), c[2] + cz], 1))
    v = np.vstack(v)
    f = []
    for i in range(len(s) - 1):
        for k in range(around):
            a, b = i * around + k, i * around + (k + 1) % around
            c_, d_ = a + around, b + around
            f += [[a, c_, b], [b, c_, d_]]
    f = np.array(f)
    uv = np.stack([np.tile(th / (2 * np.pi), len(s)), np.repeat(s / .05, around)], 1)
    return v, f, uv, np.repeat(s, around)


def cord_weights(s, NB, bow_joint, cord_joints):
    """Each stretch of cord follows its segment's bone, blending half-and-half at every particle."""
    W = np.zeros((len(s), NB))
    fpos = np.clip(s / SEG, 0, N_SEG - 1e-6)
    i = np.floor(fpos).astype(int); fr = fpos - i
    sm = lambda a, b, x: (lambda w: w * w * (3 - 2 * w))(np.clip((x - a) / (b - a), 0, 1))
    wn = .5 * sm(.5, 1, fr) * (i < N_SEG - 1)
    wp = .5 * sm(.5, 0, fr) * (i > 0)
    cj = np.array(cord_joints)
    rows = np.arange(len(s))
    W[rows, cj[i]] += 1 - wn - wp
    W[rows, cj[np.minimum(i + 1, N_SEG - 1)]] += wn
    W[rows, cj[np.maximum(i - 1, 0)]] += wp
    top = s < 0
    W[top] = 0; W[top, bow_joint] = 1
    return W


def build(step=.0008):
    """Mesh parts (bind space): bow, cord, plug body, plug blades."""
    parts = []
    lo, hi = KNOT - [.085, .095, .03], KNOT + [.085, .035, .03]
    v, f = Gm.mesh_from(bow_sdf, lo, hi, step, 14000, smooth=5)
    parts.append(('Tail_gold_satin_bow', v, f, 'bow'))
    end = rest_points()[N_SEG]
    lo, hi = end - [.025, .055, .015], end + [.025, .006, .015]
    v, f = Gm.mesh_from(plug_body_sdf, lo, hi, step * .7, 5000, smooth=2)
    parts.append(('Tail_plug_body', v, f, 'plug'))
    v2, f2 = S.mesh_sdf(plug_blade_sdf, lo, hi, step * .5)      # both blades (mesh_from keeps one piece)
    v2, f2 = S.decimate(v2, f2, 1600)
    parts.append(('Tail_plug_brass_blades', v2, f2, 'blades'))
    return parts


# ---------------------------------------------------------------- rope simulation
def _capsule_push(x, a, b, ra, rb):
    ab = b - a; L2 = ab @ ab
    t = np.clip(((x - a) @ ab) / max(L2, 1e-9), 0, 1)
    c = a + t[:, None] * ab
    r = ra + (rb - ra) * t + CORD_A
    d = x - c; dist = np.linalg.norm(d, axis=1)
    hit = dist < r
    if hit.any():
        n = d[hit] / np.maximum(dist[hit], 1e-9)[:, None]
        x[hit] = c[hit] + n * r[hit][:, None]
    return hit


def body_capsules(G, B, RG):
    caps = []
    for side, s in [('L', 1), ('R', -1)]:
        L = RG.LEG[side]
        hip, knee, ank = [G[j, :3, 3] for j in (L['thigh'], L['shin'], L['foot'])]
        Rf = G[L['foot'], :3, :3]
        caps += [(hip + G[RG.HIPS, :3, :3] @ np.array([0, .02, 0]), knee, .108, .068), (knee, ank, .063, .045),
                 (ank + Rf @ np.array([0, -.045, -.055]), ank + Rf @ np.array([0, -.050, .150]), .050, .045)]
    return caps


def seat_push(x, G, B, RG):
    """Keep particles outside the pelvis/seat (the leggings' pelvis part, rigid with the hips)."""
    Rh, th = G[RG.HIPS, :3, :3], G[RG.HIPS, :3, 3]
    q = (x - th) @ Rh + B[RG.HIPS]
    d = D.legging_parts(q)['pelvis'] - CORD_A - .002
    hit = d < 0
    if hit.any():
        e = 1e-3
        g = np.stack([D.legging_parts(q[hit] + dd)['pelvis'] - D.legging_parts(q[hit] - dd)['pelvis'] for dd in np.eye(3) * e], 1)
        g /= np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-9)
        x[hit] = x[hit] + (Rh @ g.T).T * (-d[hit])[:, None]


def simulate(anchors, frames_G, B, RG, fps, sub=16, iters=8):
    """Verlet rope: particle 0 pinned to the knot, gravity, light damping, stretch limits and a
    little stiffness, collisions with seat, legs, slippers and the floor (with friction).
    anchors: (T, 3) knot positions per frame; frames_G: posed joint matrices per frame."""
    n = N_SEG + 2
    seg = np.r_[np.full(N_SEG, SEG), PLUG_SEG]
    floor = np.r_[np.full(N_SEG, FLOOR), PLUG_FLOOR, PLUG_FLOOR]
    x = rest_points() - ANCHOR + anchors[0]
    xp = x.copy()
    dt = 1 / (fps * sub)
    g = np.array([0, -9.81, 0])
    out = []
    for i in range(len(anchors)):
        a0 = anchors[i - 1] if i else anchors[0]
        caps = body_capsules(frames_G[i], B, RG)
        for k in range(sub):
            w = (k + 1) / sub
            v = (x - xp) * .996
            xp = x.copy()
            x = x + v + g * dt * dt
            x[0] = a0 * (1 - w) + anchors[i] * w
            for _ in range(iters):
                for j in range(n - 1):
                    d = x[j + 1] - x[j]; L = np.linalg.norm(d)
                    corr = (L - seg[j]) / max(L, 1e-9) * d
                    if j == 0:
                        x[j + 1] -= corr
                    else:
                        x[j] += .5 * corr; x[j + 1] -= .5 * corr
                for j in range(n - 2):                      # a lamp cord does not fold sharply
                    d = x[j + 2] - x[j]; L = np.linalg.norm(d)
                    lim = 1.25 * SEG if j < N_SEG - 1 else .85 * (SEG + PLUG_SEG)     # stiffer at the plug's strain relief
                    if L < lim:
                        corr = (L - lim) / max(L, 1e-9) * d * .25
                        if j == 0:
                            x[j + 2] -= 2 * corr
                        else:
                            x[j] += corr; x[j + 2] -= corr
                x[0] = a0 * (1 - w) + anchors[i] * w
            for c in caps:
                sp = x[1:]
                _capsule_push(sp, *c)
                x[1:] = sp
            x, xp = follow_the_leader(x, xp, seg, floor)
            for c in caps:                                  # the legs win over exact length
                sp = x[1:]
                _capsule_push(sp, *c)
                x[1:] = sp
            low = x[:, 1] < floor
            low[0] = False
            if low.any():
                x[low, 1] = floor[low]
                xp[low] = xp[low] + (x[low] - xp[low]) * np.array([.55, 1, .55])      # friction on the floor
                xp[low, 1] = floor[low]
        sp = x[1:].copy(); seat_push(sp, frames_G[i], B, RG); x[1:] = sp
        x, _ = follow_the_leader(x, x.copy(), seg, floor)
        out.append(x.copy())
    return np.array(out)


def follow_the_leader(x, xp, seg, floor):
    """Exact segment lengths, walking out from the knot (the cord and plug never stretch).  A
    particle that would end up under the floor keeps its length by swinging sideways instead, so the
    plug tips over and lies down rather than poking through.  Corrections are kept out of the
    velocity (xp moves too), so the projection adds no energy."""
    x = x.copy(); xp = xp.copy()
    for i in range(1, len(x)):
        d = x[i] - x[i - 1]; L = np.linalg.norm(d)
        d = d / L if L > 1e-9 else np.array([0, -1., 0])
        new = x[i - 1] + seg[i - 1] * d
        if new[1] < floor[i]:
            dy = floor[i] - x[i - 1][1]
            h = np.sqrt(max(seg[i - 1] ** 2 - dy * dy, 0.))
            hd = np.array([d[0], 0, d[2]]); hn = np.linalg.norm(hd)
            if hn < 1e-6:
                prev = x[i - 1] - x[i - 2] if i > 1 else np.array([0, 0, -1.])
                hd = np.array([prev[0], 0, prev[2]]); hn = np.linalg.norm(hd)
                hd, hn = (hd, hn) if hn > 1e-6 else (np.array([0, 0, -1.]), 1.)
            new = np.array([x[i - 1][0], max(floor[i], x[i - 1][1] - seg[i - 1]), x[i - 1][2]]) + hd / hn * h
            new[1] = max(new[1], floor[i]) if abs(dy) <= seg[i - 1] else new[1]
        xp[i] += .9 * (new - x[i])
        x[i] = new
    return x, xp


def relength(x):
    """Restore exact segment lengths (and the floor) after blending two rope states."""
    n = len(x)
    seg = np.r_[np.full(N_SEG, SEG), PLUG_SEG][:n - 1]
    floor = np.r_[np.full(N_SEG, FLOOR), PLUG_FLOOR, PLUG_FLOOR][:n]
    return follow_the_leader(x, x.copy(), seg, floor)[0]
