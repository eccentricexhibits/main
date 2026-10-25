"""Generate the v10 garment meshes (fur suit + hood, leggings, panties, udder) with UV charts."""
import numpy as np
import sdf as S
import design as D
import noise as N

TILE = .11           # metres per repeat of the fur / cotton detail tiles (UV1)


def mesh_from(fn, lo, hi, step, target, smooth=6):
    v, f = S.mesh_sdf(fn, lo, hi, step)
    v, f = S.largest_component(v, f)
    v = S.taubin(v, f, smooth)
    v = S.remesh(v, f, fn, step, 2)
    v, f = S.decimate(v, f, target)
    v, f = S.clean(v, f)
    v = S.taubin(v, f, 3, .4, -.42)
    return v, f


def split_seam(v, f, u, extra=()):
    """Duplicate vertices so faces straddling the u wrap (u in [0,1)) get continuous u."""
    fu = u[f]
    bad = (fu.max(1) - fu.min(1)) > .5
    lowv = np.unique(f[bad][fu[bad] < .5])
    dup = {int(i): len(v) + k for k, i in enumerate(lowv)}
    v2 = np.vstack([v, v[lowv]])
    u2 = np.concatenate([u, u[lowv] + 1])
    ex2 = [np.concatenate([e, e[lowv]]) for e in extra]
    f2 = f.copy()
    for fi in np.nonzero(bad)[0]:
        for k in range(3):
            if u[f[fi, k]] < .5:
                f2[fi, k] = dup[int(f[fi, k])]
    return v2, f2, u2, ex2, np.concatenate([np.arange(len(v)), lowv])


def submesh(v, f, mask):
    ff = f[mask]
    used = np.unique(ff)
    remap = -np.ones(len(v), np.int64); remap[used] = np.arange(len(used))
    return used, remap[ff]


def angle_wrap(theta, seam):
    """Map angle to [0,1) with the seam at angle `seam`."""
    return ((theta - seam) / (2 * np.pi)) % 1.0


def cyl_uv(v, axis_pts, seam_vec, fwd_vec, rref, vrange):
    """Cylindrical chart around a polyline axis (list of points). Returns u, v, uv1 (N,2), along (m)."""
    a = np.asarray(axis_pts, float)
    segs = a[1:] - a[:-1]
    lens = np.linalg.norm(segs, axis=1)
    cum = np.concatenate([[0], np.cumsum(lens)])
    best_t = np.zeros(len(v)); best_d = np.full(len(v), 1e9); best_s = np.zeros(len(v), int)
    for i, (p0, d, L) in enumerate(zip(a[:-1], segs, lens)):
        t = np.clip((v - p0) @ d / (L * L), 0, 1)
        q = p0 + t[:, None] * d
        dist = np.linalg.norm(v - q, axis=1)
        m = dist < best_d
        best_d[m] = dist[m]; best_t[m] = t[m]; best_s[m] = i
    along = cum[best_s] + best_t * lens[best_s]
    # local frame: blend segment directions
    d = segs[best_s] / lens[best_s][:, None]
    fwd = np.asarray(fwd_vec, float)
    e1 = fwd - (d @ fwd)[:, None] * d
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(d, e1)
    q = a[best_s] + (best_t * lens[best_s])[:, None] * d
    r = v - q
    theta = np.arctan2(np.einsum('ij,ij->i', r, e2), np.einsum('ij,ij->i', r, e1))
    sv = np.asarray(seam_vec, float)
    seam = np.arctan2(np.einsum('ij,j->i', e2, sv), np.einsum('ij,j->i', e1, sv))
    u = angle_wrap(theta, seam)
    vv = (along - vrange[0]) / (vrange[1] - vrange[0])
    reps = max(1, round(2 * np.pi * rref / TILE))
    return u, vv, along, reps


def sphere_uv(v, c, seam_vec, rref):
    d = v - c
    theta = np.arctan2(d[:, 0], d[:, 2])
    seam = np.arctan2(seam_vec[0], seam_vec[2])
    u = angle_wrap(theta, seam)
    phi = np.arccos(np.clip(d[:, 1] / np.linalg.norm(d, axis=1), -1, 1))
    reps = max(1, round(2 * np.pi * rref / TILE))
    return u, phi / np.pi, phi * rref, reps


def make_chart(v, f, labels, lab, uvfn, name):
    used, ff = submesh(v, f, labels == lab)
    vv = v[used]
    u, w, along, reps = uvfn(vv)
    vv2, ff2, u2, (w2, al2), src = split_seam(vv, ff, u, (w, along))
    uv = np.stack([u2, w2], 1)
    uv1 = np.stack([u2 * reps, al2 / TILE], 1)
    return {'name': name, 'v': vv2, 'f': ff2, 'uv': uv, 'uv1': uv1, 'src': used[src]}


# ---------------------------------------------------------------- suit
def fur_displace(v, n, amp=.0045):
    """Low-frequency clumping so the plush silhouette is not perfectly smooth."""
    k = N.fbm(v * 38, 3, seed=5) * .7 + N.fbm(v * 90, 2, seed=9) * .3
    return v + n * (amp * k)[:, None]


def build_suit(step=.0042, target=170000):
    """Torso, hood, horn tube and two sleeves as separate surfaces (each piece of the costume is its
    own garment).  Returns unified arrays (for weights/AO) plus per-piece UV charts.
    Face labels: 0 torso, 1 hood, 2 sleeve L, 3 sleeve R, 4 horn tube."""
    V, F, Nn, L, charts = [], [], [], [], []
    off = 0
    tube_axis = [D.TUBE_C - [.12, 0, 0], D.TUBE_C + [.12, 0, 0]]
    pieces = [(0, D.suit_sdf, (-.30, .70, -.24), (.30, 1.45, .32), 1.0, .62,
               lambda q: cyl_uv(q, [(0, .60, .0), (0, 1.60, .0)], (0, 0, -1), (0, 0, 1), .21, (.13, .93)), 'Suit_torso_white_faux_fur'),
              (1, D.hood_sdf, (-.12, 1.32, -.16), (.12, 1.67, .09), .7, .10,
               lambda q: sphere_uv(q, np.array([0, 1.52, -.02]), (0, 0, -1), .10), 'Hood_white_faux_fur'),
              (4, D.tube_sdf, D.TUBE_C - [.09, .05, .05], D.TUBE_C + [.09, .05, .05], .6, .02,
               lambda q: cyl_uv(q, tube_axis, (0, -1, -1), (0, 1, 0), .037, (0, .24)), 'Mask_horn_tube_white_faux_fur')]
    for side, lab in [('L', 2), ('R', 3)]:
        s = 1 if side == 'L' else -1
        sh, el, wr = D.arm_points(s)
        top = sh + np.array([-s * .03, .05, 0])
        pieces.append((lab, (lambda q, sd=side: D.sleeve_sdf(q, sd)), np.minimum(sh, wr) - .11, np.maximum(sh, wr) + .11, .9, .13,
                       (lambda q, a=[top, sh, el, wr], s=s: cyl_uv(q, a, (-s * .3, 0, -1), (0, 0, 1), .058, (0, .6))),
                       f'Suit_sleeve_{side}_white_faux_fur'))
    for lab, fn, lo, hi, stepk, frac, uvfn, name in pieces:
        v, f = mesh_from(fn, lo, hi, step * stepk, int(target * frac))
        n = S.vertex_normals(v, f)
        v = fur_displace(v, n, .0045 if lab != 4 else .002)
        n = S.vertex_normals(v, f)
        lab_f = np.full(len(f), lab)
        ch = make_chart(v, f, lab_f, lab, uvfn, name)
        ch['src'] = ch['src'] + off
        charts.append(ch)
        V.append(v); F.append(f + off); Nn.append(n); L.append(lab_f)
        off += len(v)
    return {'v': np.vstack(V), 'f': np.vstack(F), 'n': np.vstack(Nn), 'labels': np.concatenate(L), 'charts': charts}


# ---------------------------------------------------------------- leggings
def build_leggings(step=.0040, target=90000):
    v, f = mesh_from(D.legging_sdf, (-.27, .03, -.21), (.27, 1.05, .17), step, target)
    n = S.vertex_normals(v, f)
    c = v[f].mean(1)
    parts = D.legging_parts(c)
    dist = np.stack([parts['pelvis'] - .02, parts['leg_L'], parts['leg_R']], 1)
    labels = dist.argmin(1)
    labels[(c[:, 1] > .80)] = 0
    labels[(c[:, 1] < .72) & (labels == 0)] = np.where(c[(c[:, 1] < .72) & (labels == 0), 0] > 0, 1, 2)
    charts = []
    charts.append(make_chart(v, f, labels, 0, lambda q: cyl_uv(q, [(0, .55, -.02), (0, 1.1, -.02)], (0, 0, -1), (0, 0, 1), .17, (.12, .50)), 'Leggings_seat_black_cotton'))
    for k, side in [(1, 'L'), (2, 'R')]:
        s = 1 if side == 'L' else -1
        a = [D.J[f'Thigh_{side}'] + [0, .12, 0], D.J[f'Shin_{side}'], D.J[f'Foot_{side}'] - [0, .06, 0]]
        charts.append(make_chart(v, f, labels, k, lambda q, a=a, s=s: cyl_uv(q, a, (-s, 0, -.2), (0, 0, 1), .07, (0, .95)), f'Leggings_{side}_black_cotton'))
    return {'v': v, 'f': f, 'n': n, 'labels': labels, 'charts': charts}


def leg_opening(p):
    """Height of the panty leg opening: low at the crotch, rising over the hip."""
    x = np.abs(p[..., 0])
    back = np.clip(-(p[..., 2] + .02) / .12, 0, 1)
    return .728 + .128 * np.clip(x / .185, 0, 1) ** 1.25 + .012 * back


def build_panties(leg):
    v, f, n = leg['v'], leg['f'], leg['n']
    c = v[f].mean(1)
    m = (c[:, 1] > leg_opening(c)) & (c[:, 1] < .955)
    used, ff = submesh(v, f, m)
    pv = v[used] + n[used] * .0035
    u, w, along, reps = cyl_uv(pv, [(0, .55, -.02), (0, 1.1, -.02)], (0, 0, -1), (0, 0, 1), .17, (.55, 1.1))
    pv2, ff2, u2, (w2, al2), src = split_seam(pv, ff, u, (w, along))
    uv1 = np.stack([u2 * reps, al2 / TILE], 1) * 1.6
    return {'name': 'Panties_pink_satin', 'v': pv2, 'f': ff2, 'uv': uv1, 'uv1': uv1, 'src': used[src]}


# ---------------------------------------------------------------- udder
def build_udder(step=.0028, target=50000):
    v, f = mesh_from(D.udder_sdf, (-.34, .97, -.07), (.34, 1.34, .31), step, target, smooth=4)
    # stuffed-cloth softness: shallow wrinkles + a gathered seam ring where each cup meets the suit
    n = S.vertex_normals(v, f)
    wr = N.fbm(v * np.array([30, 55, 30]), 3, seed=31)
    seam = np.zeros(len(v))
    for s in D.SIDES:
        rel = (v - D.CUP_C[s]) / D.CUP_R
        dz = rel[:, 2] + .15
        seam += np.exp(-(dz / .06) ** 2) * (np.sign(v[:, 0]) == s)
    v = v + n * (.0016 * wr - .0018 * seam)[:, None]
    out = []
    for s, side in [(1, 'L'), (-1, 'R')]:
        c = v[f].mean(1)
        m = np.sign(c[:, 0]) == s
        used, ff = submesh(v, f, m)
        vv = v[used]
        u, w, phi_len, reps = sphere_uv(vv, D.CUP_C[s], (-s * .2, 0, -1), .11)
        vv2, ff2, u2, (w2, pl2), src = split_seam(vv, ff, u, (w, phi_len))
        uv1 = np.stack([u2 * reps, pl2 / TILE], 1)
        out.append({'name': f'Udder_{side}_pink_cloth_cup_and_teats', 'v': vv2, 'f': ff2, 'uv': uv1, 'uv1': uv1, 'src': used[src]})
    return out
