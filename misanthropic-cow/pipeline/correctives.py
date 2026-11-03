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

NAMES = ['ArmUp_L', 'ArmUp_R']
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


def weights_from_mats(mats):
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
    return w


def track(mats_frames):
    return np.array([weights_from_mats(m) for m in mats_frames], np.float32)
