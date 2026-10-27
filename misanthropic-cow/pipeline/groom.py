"""Black shag as real strands: clumps of thin, tapered fibre tubes grown from the patch areas.

This replaces the alpha-cut lock cards. Each card was one flat pane with a photo of a lock on it;
however they were laid, their outlines and grey highlights read as feathers.  Here the shag is
grown as strands, in two layers:
  - an undercoat of short, loosely clumped strands that stand off the suit in all directions and
    give the patch its matted volume;
  - long locks over it: clumps whose strands root in a small disc, leave the suit at an angle,
    droop under gravity and gather toward the tip.  A few strays per lock stay loose and kink
    outward, which breaks up the outline the way the costume's fur does.
Each strand is a 3-sided tapered tube (about 1 mm across at the root, a point at the tip), so it has
volume and shades round from every side; nothing is flat and nothing needs an alpha cut.  Every
strand point is kept outside the body, belly and cups, so long locks never dive into them.
"""
import numpy as np

SIDES = 3

# per layer: clump density (per m2 of full patch), length (m), root/tip elevation off the suit (deg),
# hang-direction noise, strands per clump, clump radius (m), how far the strands gather at the tip,
# frizz amplitude (m), strand root radius (m), tube segments, chance of a stray
UNDERCOAT = dict(density=7.0e3, length=(.014, .026), e0=(40, 80), e1=(5, 35), noise=.9, per=(5, 8),
                 rc=(.003, .005), clump=(.25, .55), frizz=(.002, .004), r0=(.00045, .00065), segs=3, stray=.0)
LOCKS = dict(density=4.2e3, length=(.045, .076), e0=(30, 62), e1=(-14, 8), noise=.32, per=(8, 12),
             rc=(.0035, .0065), clump=(.65, .95), frizz=(.0012, .0035), r0=(.00038, .00058), segs=4, stray=.12)


def _unit(x):
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-12)


def _push_out(p, floor, sdf, iters=4, h=1e-3):
    """Move points whose signed distance is below `floor` back out along the SDF gradient."""
    for _ in range(iters):
        d = sdf(p)
        bad = d < floor
        if not bad.any():
            break
        q = p[bad]
        g = np.stack([sdf(q + e) - sdf(q - e) for e in np.eye(3) * h], 1) / (2 * h)
        p[bad] = q + _unit(g) * (floor[bad] - d[bad])[:, None]
    return p


def _layer(rng, v, f, n, m, sdf, P, scale):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    area = .5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    mw = np.clip((m - .30) / .55, 0, 1)                 # reaches out to the painted edge of the patch
    w = area * mw
    nc = int(w.sum() * P['density'] * scale)
    fi = rng.choice(len(f), nc, p=w / w.sum())
    r1, r2 = rng.random(nc), rng.random(nc)
    s1 = np.sqrt(r1)
    bc = np.stack([1 - s1, s1 * (1 - r2), s1 * r2], 1)
    root = np.einsum('ij,ijk->ik', bc, v[f[fi]])
    nr = _unit(np.einsum('ij,ijk->ik', bc, n[f[fi]]))
    down = np.array([0, -1, 0.]) + rng.normal(0, P['noise'], (nc, 3))
    hang = down - nr * np.einsum('ij,ij->i', down, nr)[:, None]
    bad = np.linalg.norm(hang, axis=1) < 1e-3
    hang[bad] = np.cross(nr[bad], [1, 0, 0])
    hang = _unit(hang)
    side = np.cross(nr, hang)

    # ---- clump guides: leave the suit at an angle, droop toward the hang direction, gentle wave
    edge = np.clip(mw[fi] * 1.4, 0, 1)                  # shorter, flatter locks where the patch thins out
    L = rng.uniform(*P['length'], nc) * (.45 + .55 * edge)
    e0 = np.deg2rad(rng.uniform(*P['e0'], nc)) * (.55 + .45 * edge)
    e1 = np.deg2rad(rng.uniform(*P['e1'], nc))
    KG = 10
    tg = np.linspace(0, 1.1, KG + 1)
    elev = e0[:, None] * np.clip(1 - tg[None] / .9, 0, 1) ** 1.6 + e1[:, None] * np.clip(tg[None] / .9, 0, 1)
    wave_a = rng.uniform(.10, .40, nc)[:, None]
    wave_f = rng.uniform(1.0, 2.6, nc)[:, None]
    wave_p = rng.uniform(0, 2 * np.pi, nc)[:, None]
    yaw = wave_a * np.sin(2 * np.pi * wave_f * tg[None] + wave_p) * tg[None]
    dirs = (nr[:, None] * np.sin(elev)[..., None] +
            np.cos(elev)[..., None] * (hang[:, None] * np.cos(yaw)[..., None] + side[:, None] * np.sin(yaw)[..., None]))
    step = (L * 1.1 / KG)[:, None, None]
    guide = np.concatenate([root[:, None], root[:, None] + np.cumsum(dirs[:, :-1] * step, 1)], 1)   # (nc, KG+1, 3)

    # ---- strands in each clump
    per = rng.integers(P['per'][0], P['per'][1] + 1, nc)
    S = int(per.sum())
    cid = np.repeat(np.arange(nc), per)
    rc = rng.uniform(*P['rc'], nc)[cid]
    ang = rng.uniform(0, 2 * np.pi, S)
    rad = np.sqrt(rng.random(S)) * rc
    off0 = side[cid] * (rad * np.cos(ang))[:, None] + nr[cid] * (.35 * rad * np.sin(ang))[:, None]
    stray = rng.random(S) < P['stray']
    clump = np.where(stray, rng.uniform(.0, .35, S), rng.uniform(*P['clump'], S))
    frizz = np.where(stray, rng.uniform(.006, .013, S), rng.uniform(*P['frizz'], S))
    length = rng.uniform(.70, 1.05, S) * np.where(stray, rng.uniform(.6, 1.0, S), 1)
    fdir = _unit(rng.normal(0, 1, (S, 3)))
    fdir2 = _unit(rng.normal(0, 1, (S, 3)))
    segs = P['segs']
    t = np.linspace(0, 1, segs + 1)
    u = (t[None] * length[:, None]) / 1.1 * KG                    # position along the guide polyline
    i0 = np.clip(np.floor(u).astype(int), 0, KG - 1)
    fr = (u - i0)[..., None]
    G = guide[cid]
    X = G[np.arange(S)[:, None], i0] * (1 - fr) + G[np.arange(S)[:, None], i0 + 1] * fr
    shrink = 1 - clump[:, None] * t[None] ** .8
    kink = (fdir[:, None] * np.sin(np.pi * t[None] * 1.3)[..., None] + fdir2[:, None] * (t[None] ** 2)[..., None])
    X = X + off0[:, None] * shrink[..., None] + kink * (frizz[:, None] * t[None] ** 1.4)[..., None]
    X[:, 0] -= nr[cid] * .0015                        # root tucked just under the pile

    # ---- keep every strand point out of the body, belly and cups
    d_root = sdf(root)[cid]
    floor = np.repeat(d_root, segs + 1) + np.tile(.0015 * np.minimum(t * 4, 1), S)
    flat = _push_out(X.reshape(-1, 3).copy(), floor, sdf).reshape(S, segs + 1, 3)
    flat[:, 0] = X[:, 0]
    X = flat

    # ---- tapered 3-sided tubes
    T = _unit(np.gradient(X, axis=1))
    U = np.cross(T, nr[cid][:, None])
    weak = np.linalg.norm(U, axis=-1) < 1e-4
    U[weak] = np.cross(T[weak], np.broadcast_to(side[cid][:, None], T.shape)[weak])
    U = _unit(U)
    Wv = np.cross(T, U)
    r0 = rng.uniform(*P['r0'], S)
    radius = r0[:, None] * (1 - .88 * t[None] ** 1.2)
    phase = rng.uniform(0, 2 * np.pi, S)[:, None, None]
    th = 2 * np.pi * np.arange(SIDES)[None, None] / SIDES + phase
    ring = U[:, :, None] * np.cos(th)[..., None] + Wv[:, :, None] * np.sin(th)[..., None]   # (S, K+1, SIDES, 3)
    V = X[:, :, None] + ring * radius[..., None, None]
    nper = (segs + 1) * SIDES
    base = (np.arange(S) * nper)[:, None]
    faces = []
    for k in range(segs):
        for j in range(SIDES):
            a0 = k * SIDES + j; a1 = k * SIDES + (j + 1) % SIDES
            b0 = a0 + SIDES; b1 = a1 + SIDES
            faces += [np.hstack([base + a0, base + a1, base + b1]), np.hstack([base + a0, base + b1, base + b0])]
    tv = np.repeat(np.tile(t, S), SIDES)
    # dark roots, lifting toward glossy tips; each strand a slightly different black
    tone = np.repeat(rng.uniform(.78, 1.0, S), nper)
    return {'v': V.reshape(-1, 3), 'n': ring.reshape(-1, 3), 'f': np.vstack(faces), 't': tv,
            'ao': np.clip((.30 + .70 * tv ** .7) * tone, 0, 1), 'cid': np.repeat(cid, nper),
            'roots': root, 'face': fi, 'bc': bc, 'nper': np.full(S, nper)}


def shag_strands(v, f, n, m, sdf, scale=1.0, seed=7):
    """Grow the undercoat and the locks on the faces of (v, f) where the patch mask m (per face) is set.
    scale multiplies both clump densities (the quick build uses fewer).

    Returns per-vertex arrays (v, n, t along the strand 0 root..1 tip, ao, clump id), faces, the
    vertex offset where each strand starts, and per-clump roots, source faces and barycentrics."""
    rng = np.random.default_rng(seed)
    out = {k: [] for k in ('v', 'n', 'f', 't', 'ao', 'cid', 'roots', 'face', 'bc', 'nper')}
    nv = nc = 0
    for P in (UNDERCOAT, LOCKS):
        h = _layer(rng, v, f, n, m, sdf, P, scale)
        h['f'] = h['f'] + nv
        h['cid'] = h['cid'] + nc
        nv += len(h['v']); nc += len(h['roots'])
        for k in out:
            out[k].append(h[k])
    out = {k: np.concatenate(x) for k, x in out.items()}
    out['starts'] = np.concatenate([[0], np.cumsum(out.pop('nper'))])
    out['strands'] = len(out['starts']) - 1
    return out
