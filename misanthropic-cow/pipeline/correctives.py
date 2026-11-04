"""Round 40: corrective shapes for the raised arms (glTF morph targets on the suit).

In the arms-down model the stuffed body carries the root of Tripo's arm: a block of the torso round each shoulder
pivot, with the armpit below it, that the sleeve covers.  When an arm lifts, the block is left standing beside the
chest as a flap and a shelf (the owner: "very weird bunching around the armpits").  The arms-raised static model
(round 20, `design._lifted_shoulders`, `RAISED_WALL`) shapes the body for that pose instead: the block trimmed
back to the side wall, the armpit capped, and a round shoulder ball the sleeve turns in.  Here each torso vertex
gets the offset that takes it onto that shape (one target per side), and the target blends in as that arm leaves
the body (`weights_from_mats`: by the angle between the upper arm and its rest direction, in the chest's frame).
The black shag rooted on the torso moves with it."""
import numpy as np
import design as D
import tripo_body as TB
import rig as RG

# round 44: pose-space shoulder correctives (relax_targets): for each key arm direction (FK abduction, flexion from the
# bind pose, as clips.fk_wrist) the body round the shoulder is posed, delta-mushed and stored as a morph target
RELAX_KEYS = [(.35, 0.), (.70, 0.), (1.15, 0.), (1.70, .05), (2.30, .05), (0., .50), (0., .90), (0., -.55), (.35, 1.45)]
RELAX_SIGMA = np.deg2rad(float(__import__('os').environ.get('COW_RELAX_SIGMA', 20.)))        # the keys' reach (a gaussian of the angle between arm directions)
RELAX_MIN, STRAND_MIN = .001, .003   # the smallest correction kept on the body and on the shag strands (m)
RELAX_R = (.15, .27)                 # the corrected region round the shoulder pivot: full inside, none outside (m)
SOCKET = (.07, .10)                  # the socket's radius round the arm's line: filled inside, not outside (m)
FILLET = float(__import__("os").environ.get("COW_FILLET", .06))   # the radius of the fillet where the body meets the sleeve (m; round 44B: .06 again, round 44's; rounds 46-50: .045; round 44-45: .06, a little bulky at the armpits)
SOCKET_FILL = float(__import__("os").environ.get("COW_SOCKET_FILL", 1.))
RELAX_ITERS = int(__import__("os").environ.get("COW_RELAX_ITERS", 30))                     # the delta mush's smoothing
# round 44B: the sleeve heads (rounds 45-50) are off by default, as in round 44 (COW_SLEEVE_HEADS=1 turns them back on, as
# round 50's corrective shapes)
SLEEVE_HEADS = __import__('os').environ.get('COW_SLEEVE_HEADS', '1') == '1'   # round 44D: on (round 44B: off)
# round 52: the shoulder trim (shoulder_trim), on by default: the cap's lip drawn in to the sleeve as the arm swings
SHOULDER_TRIM = __import__('os').environ.get('COW_SHOULDER_TRIM', '0') == '1'   # 44C only (the owner: it didn't work)
NAMES = ['ArmUp_L', 'ArmUp_R'] + [f'Relax{k}_{side}' for side in 'LR' for k in range(len(RELAX_KEYS))] + (['SleeveHead_L', 'SleeveHead_R'] if SLEEVE_HEADS else []) + (['ShoulderTrim_L', 'ShoulderTrim_R'] if SHOULDER_TRIM else [])
SLEEVE_HEAD_ANGLE = (np.deg2rad(8.), np.deg2rad(22.))   # round 50: the arm's swing from rest over which the sleeve heads blend in
ANGLE = (np.deg2rad(18.), np.deg2rad(75.))      # the arm's lift (from its rest direction) over which the shape blends in
REGION_Y = (1.02, 1.42)                          # only the shoulders and armpits change


# the body's side wall under a lifted arm, up to the top of the shoulder (round 31's RAISED_WALL, carried on up): with the
# arm overhead the shoulder ball of the 70-degree static model stood out past the wall as a shelf, so here the body is
# capped at the wall right up to the shoulder, and the sleeve's own rounded root fills the shoulder as it turns
WALL = np.array([[1.04, .200], [1.10, .182], [1.16, .196], [1.20, .203], [1.24, .212], [1.28, .220], [1.32, .214], [1.36, .195], [1.40, .17]])
WALL_BAND = (1.06, 1.40)


def raised_torso_sdf(p):
    """The torso for a lifted arm: capped at its side wall from the armpit to the top of the shoulder."""
    torso = D.torso_sdf(p)
    y = p[..., 1]
    w = np.interp(y, WALL[:, 0], WALL[:, 1])
    lo = np.clip((y - WALL_BAND[0]) / .04, 0, 1); hi = np.clip((WALL_BAND[1] - y) / .05, 0, 1)
    band = lo * lo * (3 - 2 * lo) * hi * hi * (3 - 2 * hi)
    import sdf as S
    return S.smax(torso, np.abs(p[..., 0]) - w - (1 - band) * .1, .025)


def _project(v, f, iters=4, e=1e-3):
    v = v.copy()
    for _ in range(iters):
        d = f(v)
        g = np.stack([(f(v + e * a) - f(v - e * a)) / (2 * e) for a in np.eye(3)], 1)
        g2 = np.maximum((g * g).sum(1), 1e-6)
        v -= (d / g2)[:, None] * g
    return v


def torso_deltas(v, is_torso):
    """(2, N, 3): for each side, how far each torso vertex moves onto the raised-arm shape."""
    out = np.zeros((2, len(v), 3), np.float32)
    y = v[:, 1]
    cand = is_torso & (y > REGION_Y[0]) & (y < REGION_Y[1]) & (np.abs(v[:, 0]) > .10)
    idx = np.nonzero(cand)[0]
    if not len(idx):
        return out
    f0 = raised_torso_sdf(v[idx])
    moved = np.abs(f0) > .0008
    idx = idx[moved]
    tgt = _project(v[idx], raised_torso_sdf)
    d = tgt - v[idx]
    d[np.linalg.norm(d, axis=1) > .12] = 0           # a vertex the projection flung away keeps its place
    for k, s in enumerate((1, -1)):
        side = s * v[idx, 0] > 0
        out[k, idx[side]] = d[side]
    return out


def smooth_deltas(D_, f, iters=3):
    """A little smoothing of each target over the mesh, so neighbours that land on different parts of the new
    shape don't tear apart."""
    from scipy import sparse
    nv = D_.shape[1]
    i = np.concatenate([f[:, 0], f[:, 1], f[:, 2], f[:, 1], f[:, 2], f[:, 0]])
    j = np.concatenate([f[:, 1], f[:, 2], f[:, 0], f[:, 0], f[:, 1], f[:, 2]])
    A = sparse.coo_matrix((np.ones(len(i)), (i, j)), shape=(nv, nv)).tocsr(); A.data[:] = 1
    M = sparse.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
    out = D_.copy()
    for k in range(len(out)):
        x = out[k]
        active = np.linalg.norm(x, axis=1) > 0
        reach = (M @ active.astype(float)) > 0
        for _ in range(iters):
            x = np.where(reach[:, None], .5 * x + .5 * (M @ x), x)
        out[k] = x
    return out


def _arm_dir(mats, side, Rc):
    s = 1 if side == 'L' else -1
    sh, el, _ = D.arm_points(s)
    d0 = (el - sh) / np.linalg.norm(el - sh)
    return d0, Rc.T @ mats[RG.ARM[side]['upper']][:3, :3] @ d0


def _key_dirs(side):
    s = 1 if side == 'L' else -1
    sh, el, _ = D.arm_points(s)
    d0 = (el - sh) / np.linalg.norm(el - sh)
    from scipy.spatial.transform import Rotation
    rot = lambda ax, a: Rotation.from_rotvec(np.asarray(ax, float) * a).as_matrix()
    return d0, [rot([0, 0, 1], s * a) @ rot([1, 0, 0], -f) @ d0 for a, f in RELAX_KEYS]


def relax_weights(d, d0, keys):
    """Normalised gaussian weights of the key directions (the rest direction is a key with no correction)."""
    ang = lambda a, b: np.arccos(np.clip(a @ b, -1, 1))
    phi = np.array([np.exp(-(ang(d, k) / RELAX_SIGMA) ** 2) for k in keys])
    return phi / (np.exp(-(ang(d, d0) / RELAX_SIGMA) ** 2) + phi.sum() + 1e-9)


def _swing(mats, Rc):
    """Per side, 0..1: how far the upper arm has swung from its rest direction (a smoothstep over SLEEVE_HEAD_ANGLE)."""
    out = np.zeros(2)
    for k, side in enumerate('LR'):
        d0, d = _arm_dir(mats, side, Rc)
        u = np.clip((np.arccos(np.clip(d @ d0, -1, 1)) - SLEEVE_HEAD_ANGLE[0]) / (SLEEVE_HEAD_ANGLE[1] - SLEEVE_HEAD_ANGLE[0]), 0, 1)
        out[k] = u * u * (3 - 2 * u)
    return out


def weights_from_mats(mats, sleeve_heads=None, shoulder_trim=None):
    """Each target's weight from a frame's skinning matrices (bind rotations are identity, so a joint's global
    rotation is its skinning matrix's): how far each upper arm has turned from its rest direction, relative to the
    chest."""
    Rc = mats[RG.CHEST][:3, :3]
    w = np.zeros(2)
    for k, side in enumerate('LR'):
        s = 1 if side == 'L' else -1
        sh, el, _ = D.arm_points(s)
        d0 = (el - sh) / np.linalg.norm(el - sh)
        d = Rc.T @ mats[RG.ARM[side]['upper']][:3, :3] @ d0
        ang = np.arccos(np.clip(d @ d0, -1, 1))
        u = np.clip((ang - ANGLE[0]) / (ANGLE[1] - ANGLE[0]), 0, 1)
        w[k] = u * u * (3 - 2 * u)
    out = [w]
    for side in 'LR':
        d0, keys = _key_dirs(side)
        out.append(relax_weights(_arm_dir(mats, side, Rc)[1], d0, keys))
    if SLEEVE_HEADS if sleeve_heads is None else sleeve_heads:
        out.append(_swing(mats, Rc))                    # round 50: the sleeve heads, by the arm's swing from rest
    if SHOULDER_TRIM if shoulder_trim is None else shoulder_trim:
        out.append(_swing(mats, Rc))                    # round 52: the shoulder trim, the same
    return np.concatenate(out)


def _taper(mag, m):
    """Offsets below m/2 dropped, above 3m/2 kept, a smooth ramp between (a hard cut left millimetre steps that showed
    as stretch)."""
    u = np.clip((mag - .5 * m) / m, 0, 1)
    return u * u * (3 - 2 * u)


SLEEVE_HEAD_SPREAD = .049           # round 48: how far the growth is smoothed over the sleeve (m): passes enough to
#                                     spread it this far on the mesh's own edge length (round 45-47: 4 passes, about
#                                     1 cm on the full build, which left it lumpy: the owner, "a bit of a lumpy bit on
#                                     the shoulders")
SLEEVE_HEAD_MAX = float(__import__('os').environ.get('COW_SLEEVE_HEAD_MAX', .020))   # 44D: .020 (as a pose-driven shape it need not hold back for the rest pose; rounds 46-50: .014)               # round 45-46: the most the sleeve head is widened (m; round 45: .025, which showed as a seam and bulk)
SLEEVE_HEAD = (float(__import__('os').environ.get('COW_SLEEVE_HEAD_GAP', .006)), .45, .16)   # 44D: 6 mm inside the cap (rounds 46-50: 10)   # round 45 (46: kept 1 cm inside the cap, not 4 mm, so it doesn't cut through as the arm moves): the sleeve head: kept inside the body's surface by (m), taper (m of radius per m along the arm), reach along the arm (m)


def sleeve_head(model, gap=None, slope=None, reach=None, as_morph=True):
    """Round 45: the body's shoulder (the root of the Tripo arm) is a rounded cap wider than the sleeve, and the sleeve
    came out from under its lower edge: the corner under the overhang read as a groove down the front and back of the
    shoulder, standing and more so as the arm swings (the owner: "the run shoulder still has a visible groove").  The
    sleeve's top is widened, round its own axis, to just inside the body's surface wherever the cap is wider, and
    below the cap's edge it tapers back to its own width (`slope`), so it fills the corner like a puffy sleeve head
    without breaking out through the cap.  Measured along rays out from the arm's axis against the body's distance
    field (design.torso_sdf), at the sleeve's own vertices."""
    import sdf as S
    gap, slope, reach = [x if x is not None else d for x, d in zip((gap, slope, reach), SLEEVE_HEAD)]
    out = {}
    rs = np.arange(0., .16, .002)
    for side, s in [('L', 1), ('R', -1)]:
        p = [q for q in model.parts if q['name'].startswith(f'Suit_sleeve_{side}')][0]
        V = np.asarray(p['v'], float); Fc = np.asarray(p['f'])
        sh, el, _ = D.arm_points(s)
        du = (el - sh) / np.linalg.norm(el - sh)
        ta = (V - sh) @ du
        radial = (V - sh) - np.outer(ta, du); rv = np.linalg.norm(radial, axis=1)
        dirs = radial / np.maximum(rv, 1e-9)[:, None]
        sel = np.nonzero((ta > -.08) & (ta < reach))[0]
        # the body's extent along each vertex's ray, at every station along the arm up to the vertex (for the taper)
        stations = np.arange(-.08, reach, .004)
        target = rv.copy()
        for k in sel:
            best = 0.
            for t0 in stations[stations <= ta[k] + 1e-9]:
                c0 = sh + du * t0
                pts = c0[None] + rs[:, None] * dirs[k][None]
                ins = D.torso_sdf(pts) < 0
                if not ins[0] or ins.all():
                    continue                                    # outside the cap here, or a ray into the chest
                r_out = rs[np.argmin(ins)]
                best = max(best, r_out - gap - slope * (ta[k] - t0))
            target[k] = max(rv[k], best)
        # round 48: a soft cap (a hard min() left a ridge where it took over) and a wider smoothing below
        grow = SLEEVE_HEAD_MAX * np.tanh((target - rv) / SLEEVE_HEAD_MAX)
        # smooth the growth over the sleeve's surface, so the widened head has no ridges
        key = np.round(V / 2e-5).astype(np.int64)
        _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.ravel()
        from scipy import sparse
        Fw = inv[Fc]; nw = len(first)
        i = np.concatenate([Fw[:, 0], Fw[:, 1], Fw[:, 2]]); j = np.concatenate([Fw[:, 1], Fw[:, 2], Fw[:, 0]])
        A = sparse.coo_matrix((np.ones(len(i)), (i, j)), shape=(nw, nw)); A = ((A + A.T) > 0).astype(float)
        Mavg = sparse.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
        gw = np.zeros(nw); np.maximum.at(gw, inv, grow)
        edge = float(np.median(np.linalg.norm(V[first][i] - V[first][j], axis=1)))
        passes = int(round((SLEEVE_HEAD_SPREAD / max(edge, 1e-4)) ** 2))
        for _ in range(passes):
            gw = .5 * gw + .5 * (Mavg @ gw)
        d = dirs * gw[inv][:, None]
        Vw = (V + d)[first]
        nn = S.vertex_normals(Vw, Fw[(Fw[:, 0] != Fw[:, 1]) & (Fw[:, 1] != Fw[:, 2]) & (Fw[:, 0] != Fw[:, 2])])[inv]
        moved = gw[inv] > 1e-5
        dn = np.zeros_like(d); dn[moved] = nn[moved] - np.asarray(p['n'], float)[moved]
        if as_morph:
            # round 50: kept as a corrective shape (sleeve_head_targets), so at rest the shoulder is round 44's
            p['sleeve_head'] = (side, d.astype(np.float32), dn.astype(np.float32))
        else:
            p['v'] = (V + d).astype(np.float32)
            p['n'] = np.asarray(p['n'], np.float32).copy(); p['n'][moved] = nn[moved].astype(np.float32)
        out[side] = (int(moved.sum()), round(float(gw.max()) * 1000, 1), passes)
    return {'sleeve_head': out}


def sleeve_head_targets(model):
    """Round 50: the sleeve heads (sleeve_head) as two corrective shapes, SleeveHead_L and SleeveHead_R, after the
    others.  Rounds 45-49 widened the sleeves' tops in every pose; that filled the groove under the shoulder cap that
    shows as the arm swings (Run), but it also softened the cap's edge at rest, and the owner preferred round 44's
    shoulders.  Now the widening blends in with the arm's swing from rest (SLEEVE_HEAD_ANGLE, weights_from_mats): none
    while she stands (Idle stays within 6 degrees), partly at the ends of Walk's swing, fully through most of Run's.
    Every part with corrective shapes gets the two (empty but on the sleeves), so all share one weight track."""
    k0 = len(NAMES) - 2 - (2 if SHOULDER_TRIM else 0)   # the trim's two come after these
    for p in model.parts:
        head = p.pop('sleeve_head', None)
        if p.get('morph') is None and head is None:
            continue
        nv = len(p['v'])
        if p.get('morph') is None:
            p['morph'] = np.zeros((k0, nv, 3), np.float32); p['morph_n'] = np.zeros_like(p['morph'])
        ex = np.zeros((2, nv, 3), np.float32); exn = np.zeros_like(ex)
        if head is not None:
            side, d, dn = head
            tp = _taper(np.linalg.norm(d, axis=1), RELAX_MIN)[:, None]   # the smoothing's sub-millimetre tail isn't seen
            ex['LR'.index(side)] = d * tp; exn['LR'.index(side)] = dn * tp   # (and the GLB must stay < 100 MiB)
        p['morph'] = np.concatenate([p['morph'], ex], 0)
        if p.get('morph_n') is not None:
            p['morph_n'] = np.concatenate([p['morph_n'], exn], 0)
    return {}


def relax_targets(model, B, iters=RELAX_ITERS):
    """Round 44: the shoulder correctives.  Linear-blend skinning folds the body into a sharp crease in front of a
    raised arm and cuts a crescent crease where the sleeve's underside meets it (the owner's screenshots of Run and
    Jumping Jacks: "the armpits still look stretched", "weird arm joining issues").  For each key arm pose, the body
    (the suit torso) is skinned as the viewer skins it, then: delta-mushed (smoothed, and the rest pose's own surface
    detail added back in each vertex's local frame), which takes out folds and spreads stretch; the socket the sleeve's
    root sits in, uncovered as the arm lifts, filled in (SOCKET); and the body lifted onto a smooth union with the posed
    sleeve (FILLET), so it meets the sleeve in a rounded join instead of a sharp crease; only round the shoulder
    (RELAX_R).  The change, taken back through each vertex's skinning, is a morph
    target, weighted by the arm's direction (relax_weights).  Adds the targets to the torso part and the shag strands
    near the shoulders (nearest torso vertex), after the existing ArmUp ones."""
    import sdf as S, anim as AN, clips as CL
    from scipy import sparse
    from scipy.spatial import cKDTree
    ti = [i for i, p in enumerate(model.parts) if p['name'].startswith('Suit_torso')][0]
    P0 = model.parts[ti]
    V = np.asarray(P0['v'], float); F = np.asarray(P0['f'])
    # weld the chart seams, so the smoothing sees one surface
    key = np.round(V / 2e-5).astype(np.int64)
    uk, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.ravel(); Vw = V[first]; Fw = inv[F]
    Fw = Fw[(Fw[:, 0] != Fw[:, 1]) & (Fw[:, 1] != Fw[:, 2]) & (Fw[:, 0] != Fw[:, 2])]
    nw = len(Vw)
    i = np.concatenate([Fw[:, 0], Fw[:, 1], Fw[:, 2], Fw[:, 1], Fw[:, 2], Fw[:, 0]])
    j = np.concatenate([Fw[:, 1], Fw[:, 2], Fw[:, 0], Fw[:, 0], Fw[:, 1], Fw[:, 2]])
    A = sparse.coo_matrix((np.ones(len(i)), (i, j)), shape=(nw, nw)).tocsr(); A.data[:] = 1
    Mavg = sparse.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
    nb0 = np.asarray(A.argmax(1)).ravel()                       # one neighbour per vertex, for its tangent

    def smooth(X):
        for _ in range(iters):
            X = .5 * X + .5 * (Mavg @ X)
        return X

    def frames(X):
        n = S.vertex_normals(X, Fw)
        t = X[nb0] - X; t -= n * np.einsum('ij,ij->i', t, n)[:, None]
        t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-12)
        return np.stack([t, np.cross(n, t), n], 2)               # columns t, b, n

    Vs = smooth(Vw); Fv = frames(Vs)
    detail = np.einsum('nji,nj->ni', Fv, Vw - Vs)               # rest detail in the smoothed rest frames
    jj, ww = np.asarray(P0['j']), np.asarray(P0['w'], float) / 255.
    sleeves = {}
    for p in model.parts:
        for side in 'LR':
            if p['name'].startswith(f'Suit_sleeve_{side}'):
                sleeves[side] = {'v': np.asarray(p['v'], float), 'n': np.asarray(p['n'], float), 'j': np.asarray(p['j']),
                                 'w': np.asarray(p['w'], float) / 255.}
    morph = P0.get('morph')
    K = len(RELAX_KEYS)
    out = np.zeros((2 * K, len(V), 3), np.float32)
    for si, (side, s) in enumerate([('L', 1), ('R', -1)]):
        sh, el, _ = D.arm_points(s)
        dist = np.linalg.norm(Vw - sh, axis=1)
        # the socket: the body under the sleeve's rounded root (covered at rest, uncovered as the arm lifts), which is
        # filled in (smoothed without putting its hollow back) rather than delta-mushed
        du = (el - sh) / np.linalg.norm(el - sh)
        ta = (Vw - sh) @ du; ra = np.linalg.norm((Vw - sh) - np.outer(ta, du), axis=1)
        sock = np.clip((SOCKET[1] - ra) / (SOCKET[1] - SOCKET[0]), 0, 1) * np.clip((ta + .09) / .04, 0, 1) * np.clip((.12 - ta) / .04, 0, 1)
        sock = sock * sock * (3 - 2 * sock)
        m = np.clip((RELAX_R[1] - dist) / (RELAX_R[1] - RELAX_R[0]), 0, 1); m = m * m * (3 - 2 * m)
        lat = np.clip((s * Vw[:, 0] - .02) / .05, 0, 1); m *= lat * lat * (3 - 2 * lat)
        for k, (abd, flex) in enumerate(RELAX_KEYS):
            clip = AN.Dance(B); clip.PERFORM = False
            def sample(t, clip=clip, side=side, abd=abd, flex=flex):
                p = CL.neutral(clip)
                p['fk'][side] = np.array([abd, flex, .12])
                return p
            clip.sample = sample
            mats = AN.skin_matrices(clip.pose(0.), B)
            Vm = V.copy()
            if morph is not None:
                Vm = Vm + np.einsum('k,kij->ij', weights_from_mats(mats)[:2], morph[:2])
            Mj = mats[jj]                                           # (N, 4, 4, 4)
            Amat = np.einsum('nk,nkij->nij', ww, Mj[:, :, :3, :3])
            tvec = np.einsum('nk,nki->ni', ww, Mj[:, :, :3, 3])
            P = np.einsum('nij,nj->ni', Amat, Vm) + tvec
            Pw = P[first]
            Ps = smooth(Pw); Fp = frames(Ps)
            Pdm = Ps + np.einsum('nij,nj->ni', Fp, detail)
            # the posed sleeve, and each body point's signed distance off it (< 0: covered by the sleeve)
            sq = sleeves[side]
            Q = np.einsum('nk,nkij,nj->ni', sq['w'], mats[sq['j']][:, :, :3, :3], sq['v']) + np.einsum('nk,nki->ni', sq['w'], mats[sq['j']][:, :, :3, 3])
            Qn = np.einsum('nk,nkij,nj->ni', sq['w'], mats[sq['j']][:, :, :3, :3], sq['n'])
            Qn /= np.maximum(np.linalg.norm(Qn, axis=1, keepdims=True), 1e-9)
            qtree = cKDTree(Q)

            def off_sleeve(X):
                dq, iq = qtree.query(X)
                b = np.einsum('ij,ij->i', X - Q[iq], Qn[iq])
                return np.where(b > 0, np.minimum(b, dq), b)
            # the socket is filled only where the sleeve has moved off it; under the sleeve it stays as it is (hidden)
            sf = SOCKET_FILL * sock * np.clip((off_sleeve(Pw) + .004) / .012, 0, 1)
            Pdm = Pdm * (1 - sf[:, None]) + Ps * sf[:, None]
            if FILLET > 0:
                # a fillet where the body meets the sleeve: the two separate surfaces cut each other in a sharp crease
                # (under a lifted arm, in front of a swung one); each body point just outside the sleeve is lifted onto
                # the smooth union of the two (polynomial smooth-min, radius FILLET), so the body rises to meet the sleeve
                b = off_sleeve(Pdm)
                lift = np.where(b < FILLET, (FILLET - np.clip(b, 0, None)) ** 2 / (4 * FILLET), 0.)
                # under the sleeve it eases in from 1.2 cm deep, and never lifts a covered point out through the sleeve
                u = np.clip((b + .012) / .012, 0, 1)
                lift *= u * u * (3 - 2 * u)
                lift = np.where(b < 0, np.minimum(lift, np.maximum(-b - .002, 0)), lift)
                for _ in range(3):
                    lift = .5 * lift + .5 * (Mavg @ lift)
                Pdm = Pdm + frames(Pdm)[:, :, 2] * lift[:, None]
            corr = (m[:, None] * (Pdm - Pw))[inv]                    # back on every (unwelded) vertex
            d = np.linalg.solve(Amat, corr[..., None])[..., 0]
            d *= _taper(np.linalg.norm(d, axis=1), RELAX_MIN)[:, None]  # small offsets aren't seen (and the GLB must stay < 100 MiB)
            out[si * K + k] = d
    # normals' offsets on the welded surface
    out_n = np.zeros_like(out)
    n_base = S.vertex_normals(Vw, Fw)
    for k in range(len(out)):
        dw = np.zeros((nw, 3)); np.add.at(dw, inv, out[k]); cnt = np.bincount(inv, minlength=nw)[:, None]
        dw /= np.maximum(cnt, 1)
        moved = np.linalg.norm(out[k], axis=1) > 0
        nn = (S.vertex_normals(Vw + dw, Fw) - n_base)[inv]
        out_n[k][moved] = nn[moved]
    def append(part, extra, extra_n):
        if part.get('morph') is None:
            part['morph'] = np.zeros((2, len(part['v']), 3), np.float32); part['morph_n'] = np.zeros_like(part['morph'])
        part['morph'] = np.concatenate([part['morph'], extra.astype(np.float32)], 0)
        if part.get('morph_n') is not None:
            part['morph_n'] = np.concatenate([part['morph_n'], extra_n.astype(np.float32)], 0)
    append(P0, out, out_n)
    # the shag strands rooted near the shoulders move with the nearest torso vertex
    tree = cKDTree(V)
    for p in model.parts:
        if not p['name'].startswith('Suit_black_shag') or p.get('morph') is None:
            continue
        pv = np.asarray(p['v'], float)
        near = (np.linalg.norm(pv - D.arm_points(1)[0], axis=1) < RELAX_R[1] + .05) | (np.linalg.norm(pv - D.arm_points(-1)[0], axis=1) < RELAX_R[1] + .05)
        ex = np.zeros((2 * K, len(pv), 3), np.float32)
        if near.any():
            _, idx = tree.query(pv[near])
            ex[:, near] = out[:, idx]
        m = STRAND_MIN * (2 if p['name'].endswith('armpits') else 1)     # round 46: the armpit hair is mostly under the arm
        ex *= _taper(np.linalg.norm(ex, axis=2), m)[..., None]   # loose black strands: a few mm off the surface do not show
        append(p, ex, np.zeros_like(ex))
    return {'relax_vertices': [int((np.linalg.norm(o, axis=1) > 0).sum()) for o in out]}


SHOULDER_TRIM_F = .6                       # round 52: the share of the cap's overhang taken away
SHOULDER_TRIM_SPREAD = .035                # round 52: how far the trim is smoothed over the body (m)
SHOULDER_TRIM_P = (.004, .03, .035, .06)   # round 52: kept outside the sleeve by (m), the trim's reach up the cap from its
#                                       band's end (m), the most overhang trimmed (m), the most overhang counted as the cap's (m;
#                                       the cap overhangs the sleeve by 3-4 cm at the front and back; the back itself is further)


def shoulder_trim(model):
    """Round 52: the groove under the shoulder cap (Run; the owner's round 44 note, and again on round 44B, circled at the
    back of the shoulder), filled by taking material away rather than adding it ("instead of adding material, what if
    we removed material?").  The body's shoulder is a rounded cap wider than the sleeve, and the sleeve comes out from
    under its lip; as the arm swings, the corner under the lip reads as a groove.  Rounds 45-50 widened the sleeve to
    meet the cap.  Here the cap's lip is drawn in to just outside the sleeve (SHOULDER_TRIM_P), fully at the lip and
    fading out up the cap, on the front and back of the shoulder (where the groove shows; not on top, and not on the
    side wall under the arm), smoothed over the body; as two corrective shapes (ShoulderTrim_L/R) weighted by the arm's
    swing from rest (_swing), so standing she keeps round 44's shoulders.  The shag strands near the shoulder follow
    their nearest body vertex.  Computed in the bind pose, measured against the sleeve along rays from the arm's axis."""
    import sdf as S
    from scipy import sparse
    from scipy.spatial import cKDTree
    gap, reach, most, cap = SHOULDER_TRIM_P
    ti = [i for i, p in enumerate(model.parts) if p['name'].startswith('Suit_torso')][0]
    P0 = model.parts[ti]
    V = np.asarray(P0['v'], float); F = np.asarray(P0['f'])
    key = np.round(V / 2e-5).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.ravel()
    Vw = V[first]; Fw = inv[F]; nw = len(Vw)
    i = np.concatenate([Fw[:, 0], Fw[:, 1], Fw[:, 2]]); j = np.concatenate([Fw[:, 1], Fw[:, 2], Fw[:, 0]])
    A = sparse.coo_matrix((np.ones(len(i)), (i, j)), shape=(nw, nw)); A = ((A + A.T) > 0).astype(float)
    Mavg = sparse.diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
    edge = float(np.median(np.linalg.norm(Vw[i] - Vw[j], axis=1)))
    passes = int(round((SHOULDER_TRIM_SPREAD / max(edge, 1e-4)) ** 2))
    out = np.zeros((2, len(V), 3)); report = {}
    for k, (side, s) in enumerate([('L', 1), ('R', -1)]):
        Sv = np.asarray([q for q in model.parts if q['name'].startswith(f'Suit_sleeve_{side}')][0]['v'], float)
        sh, el, _ = D.arm_points(s)
        du = (el - sh) / np.linalg.norm(el - sh)
        def polar(X):
            t = (X - sh) @ du; rad = (X - sh) - np.outer(t, du); r = np.linalg.norm(rad, axis=1)
            return t, r, rad / np.maximum(r, 1e-9)[:, None]
        ts, rs, ds = polar(Sv)
        tree = cKDTree(sh + np.outer(ts, du) + ds * .06)
        tt, rt, dt = polar(Vw)
        cand = (tt > -.03) & (tt < .11) & (rt < .17)
        dist, nn = tree.query(sh + np.outer(tt, du) + dt * .06)
        rsl = rs[nn]
        over = rt - rsl - gap
        near = cand & (dist < .02) & (over > 0) & (over < cap)
        # the cap's band down the arm (its overhang, 3-4 cm, runs from the shoulder to about 8 cm down), fading at
        # both ends; past it the body is the back and chest, further out
        sm = lambda a, b_, x: (lambda q: q * q * (3 - 2 * q))(np.clip((x - a) / (b_ - a), 0, 1))
        w = sm(-.01, .03, tt) * (1 - sm(.085, .085 + reach, tt)) * SHOULDER_TRIM_F
        side_w = np.clip((np.abs(dt[:, 2]) - .3) / .4, 0, 1)        # front and back of the shoulder only
        amt = np.where(near, np.minimum(over, most) * w * side_w, 0.)
        for _ in range(passes):
            amt = .5 * amt + .5 * (Mavg @ amt)
        out[k] = (-dt * amt[:, None])[inv]
        out[k] *= _taper(np.linalg.norm(out[k], axis=1), RELAX_MIN)[:, None]
        report[side] = (int((np.linalg.norm(out[k], axis=1) > 0).sum()), round(float(np.linalg.norm(out[k], axis=1).max()) * 1000, 1))
    # normals' offsets
    n_base = S.vertex_normals(Vw, Fw[(Fw[:, 0] != Fw[:, 1]) & (Fw[:, 1] != Fw[:, 2]) & (Fw[:, 0] != Fw[:, 2])])
    Fg = Fw[(Fw[:, 0] != Fw[:, 1]) & (Fw[:, 1] != Fw[:, 2]) & (Fw[:, 0] != Fw[:, 2])]
    out_n = np.zeros_like(out)
    for k in range(2):
        dw = np.zeros((nw, 3)); np.add.at(dw, inv, out[k]); dw /= np.maximum(np.bincount(inv, minlength=nw), 1)[:, None]
        moved = np.linalg.norm(out[k], axis=1) > 0
        out_n[k][moved] = (S.vertex_normals(Vw + dw, Fg) - n_base)[inv][moved]
    k0 = len(NAMES) - 2
    tree = cKDTree(V)
    for p in model.parts:
        if p.get('morph') is None:
            continue
        nv = len(p['v'])
        if p is P0:
            ex, exn = out, out_n
        else:
            ex = np.zeros((2, nv, 3)); exn = np.zeros_like(ex)
            if p['name'].startswith('Suit_black_shag'):
                pv = np.asarray(p['v'], float)
                d, idx = tree.query(pv)
                ex = out[:, idx] * (d < .03)[None, :, None]
                ex *= _taper(np.linalg.norm(ex, axis=2), STRAND_MIN)[..., None]
        assert len(p['morph']) == k0, (p['name'], len(p['morph']), k0)
        p['morph'] = np.concatenate([p['morph'], ex.astype(np.float32)], 0)
        if p.get('morph_n') is not None:
            p['morph_n'] = np.concatenate([p['morph_n'], exn.astype(np.float32)], 0)
    return {'shoulder_trim': report}


ARMUP_MIN = .0007   # round 44B (44C: .0012): the smallest arm-raise offset kept (m; half dropped, from 1 mm kept in full)


def trim_armup(model):
    """Round 44B: the arm-raise shapes (ArmUp_L/R, round 40) on the body and the shag were stored wherever they moved a
    vertex at all, mostly by tenths of a millimetre; those are dropped as the shoulder correctives' are (a smooth ramp,
    _taper), which keeps the GLB under 100 MiB without a visible change."""
    n = 0
    for p in model.parts:
        if p.get('morph') is None:
            continue
        m = np.asarray(p['morph'], np.float32)
        for k in range(2):
            mag = np.linalg.norm(m[k], axis=1)
            before = int((mag > 0).sum())
            m[k] = m[k] * _taper(mag, ARMUP_MIN)[:, None]
            n += before - int((np.linalg.norm(m[k], axis=1) > 0).sum())
        p['morph'] = m
        if p.get('morph_n') is not None:
            mn = np.asarray(p['morph_n'], np.float32)
            for k in range(2):
                mn[k][np.linalg.norm(m[k], axis=1) == 0] = 0
            p['morph_n'] = mn
    return {'armup_trimmed': n}


def track(mats_frames):
    return np.array([weights_from_mats(m) for m in mats_frames], np.float32)
