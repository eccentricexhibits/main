"""Skeleton and skin weights for the v10 cow.

Key fixes over v09:
* arm/torso separation comes from SDF membership of the primitives that built the suit, with a
  narrow blend in the armpit, so torso flank never follows the upper arm ("wings" under the arms);
* a clavicle (Shoulder_*) bone carries the top of the shoulder when the elbows lift;
* the sleeve end and the glove cuff are weighted by ONE function of position along the forearm
  axis, and the glove cuff overlaps the sleeve by 3.5 cm, so hands stay connected when they turn.
"""
import numpy as np
from scipy import sparse
import design as D
import sdf as S

NAMES, PARENTS = [], []


def _j(name, parent):
    NAMES.append(name); PARENTS.append(NAMES.index(parent) if parent else -1)
    return len(NAMES) - 1


HIPS = _j('Hips', None)
SPINE = _j('Spine', 'Hips')
BELLY = _j('Belly', 'Spine')
CHEST = _j('Chest', 'Spine')
UDDER = {'L': _j('Udder_L', 'Chest'), 'R': _j('Udder_R', 'Chest')}
NECK = _j('Neck', 'Chest')
HEAD = _j('Head', 'Neck')
ARM = {}
for side in 'LR':
    sh = _j(f'Shoulder_{side}', 'Chest')
    up = _j(f'UpperArm_{side}', f'Shoulder_{side}')
    fo = _j(f'Forearm_{side}', f'UpperArm_{side}')
    ha = _j(f'Hand_{side}', f'Forearm_{side}')
    fi = _j(f'HoofFingers_{side}', f'Hand_{side}')
    th = _j(f'Thumb_{side}', f'Hand_{side}')
    ARM[side] = dict(shoulder=sh, upper=up, fore=fo, hand=ha, fingers=fi, thumb=th)
LEG = {}
for side in 'LR':
    t = _j(f'Thigh_{side}', 'Hips'); s = _j(f'Shin_{side}', f'Thigh_{side}'); f = _j(f'Foot_{side}', f'Shin_{side}')
    LEG[side] = dict(thigh=t, shin=s, foot=f)
# helpers that take half of a joint's rotation (keeps volume at the shoulder root and elbow)
ROOT_HALF, ELBOW_HALF = {}, {}
for side in 'LR':
    ROOT_HALF[side] = _j(f'UpperArmRoot_{side}', f'Shoulder_{side}')
    ELBOW_HALF[side] = _j(f'Elbow_{side}', f'UpperArm_{side}')
# soft-body bones (driven by baked spring physics): one per teat, one per shag patch
TEAT = {}
for side in 'LR':
    for k, kind in enumerate(['bottom', 'outer']):
        TEAT[(side, k)] = _j(f'Teat_{side}_{kind}', f'Udder_{side}')
SHAG_NAMES = ['Shag_chest_R', 'Shag_belly', 'Shag_back_upper_R', 'Shag_back_lower_L', 'Shag_elbow_L', 'Shag_elbow_R']
SHAG_PARENTS = ['Chest', 'Belly', 'Chest', 'Spine', 'Elbow_L', 'Elbow_R']
SHAG = [_j(n, p) for n, p in zip(SHAG_NAMES, SHAG_PARENTS)]
NB = len(NAMES)
BELLY_C = np.array([0, .925, .085])


def bind_positions(glove_parts):
    B = np.zeros((NB, 3))
    for k in ['Hips', 'Spine', 'Chest', 'Neck', 'Head']:
        B[NAMES.index(k)] = D.J[k]
    B[BELLY] = BELLY_C
    for side, s in [('L', 1), ('R', -1)]:
        B[UDDER[side]] = D.CUP_C[s] + [0, .02, -.04]
        for key, jn in [('shoulder', 'Shoulder'), ('upper', 'UpperArm'), ('fore', 'Forearm'), ('hand', 'Hand')]:
            B[ARM[side][key]] = D.J[f'{jn}_{side}']
        caps = np.vstack([p['v'] for p in glove_parts[side] if 'hoof_cap' in p['name']])
        top = caps[:, 1] > np.percentile(caps[:, 1], 88)
        B[ARM[side]['fingers']] = caps[top].mean(0)
        th = np.vstack([p['v'] for p in glove_parts[side] if p['name'].endswith('cloth_thumb')])
        d = (D.J[f'Hand_{side}'] - D.J[f'Forearm_{side}']); d /= np.linalg.norm(d)
        proj = (th - D.J[f'Hand_{side}']) @ d
        B[ARM[side]['thumb']] = th[proj < np.percentile(proj, 15)].mean(0)
        for key, jn in [('thigh', 'Thigh'), ('shin', 'Shin'), ('foot', 'Foot')]:
            B[LEG[side][key]] = D.J[f'{jn}_{side}']
        sh, el, wr = D.arm_points(s)
        B[ROOT_HALF[side]] = sh
        B[ELBOW_HALF[side]] = el
        for k, (a, b) in enumerate(D.TEATS[s]):
            d = (b - a) / np.linalg.norm(b - a)
            B[TEAT[(side, k)]] = a + .012 * d
    import textures as T
    for j, (c, r) in zip(SHAG, T.all_patches()):
        B[j] = c
    return B


def ss(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1)
    return u * u * (3 - 2 * u)


def arm_chain(p, side):
    """Weights (upper, fore, hand) by position along the arm; shared by sleeve and glove cuff."""
    s = 1 if side == 'L' else -1
    sh, el, wr = D.arm_points(s)
    du = el - sh; Lu = np.linalg.norm(du); du /= Lu
    df = wr - el; Lf = np.linalg.norm(df); df /= Lf
    # along-arm coordinate: projection onto upper arm, then forearm
    tu = (p - sh) @ du
    tf = (p - el) @ df
    elbow_blend = ss(-.045, .035, tf) * ss(Lu - .08, Lu + .02, tu + 0 * tf)
    elbow_blend = np.maximum(elbow_blend, ss(-.03, .03, tf))
    hand = ss(Lf - .065, Lf + .004, tf)
    upper = 1 - elbow_blend
    fore = elbow_blend * (1 - hand)
    hand = elbow_blend * hand
    return upper, fore, hand


def smooth_weights(W, f, iters, lock=None):
    nv = len(W)
    i = np.concatenate([f[:, 0], f[:, 1], f[:, 2], f[:, 1], f[:, 2], f[:, 0]])
    j = np.concatenate([f[:, 1], f[:, 2], f[:, 0], f[:, 0], f[:, 1], f[:, 2]])
    A = sparse.coo_matrix((np.ones(len(i)), (i, j)), shape=(nv, nv)).tocsr(); A.data[:] = 1
    deg = np.maximum(np.asarray(A.sum(1)).ravel(), 1)
    M = sparse.diags(1 / deg) @ A
    for _ in range(iters):
        W2 = .5 * W + .5 * (M @ W)
        if lock is not None:
            W2[lock] = W[lock]
        W = W2
    return W


def suit_weights(v, f, face_labels):
    """Torso/hood vertices never take arm weights (only the clavicle and the half-rotation helper on
    the shoulder cap); sleeve vertices take only the arm chain (+ the helper at the sleeve head)."""
    vl = np.zeros(len(v), int)
    for k in range(3):
        vl[f[:, k]] = face_labels
    sleeve = {'L': vl == 2, 'R': vl == 3}
    W = np.zeros((len(v), NB))
    y = v[:, 1]
    W[:, HIPS] = 1 - ss(.90, 1.02, y)
    W[:, SPINE] = ss(.90, 1.02, y) * (1 - ss(1.10, 1.22, y))
    W[:, CHEST] = ss(1.10, 1.22, y)
    e = np.linalg.norm((v - [0, .915, .20]) / [.25, .21, .19], axis=1)
    bw = .65 * ss(1.05, .45, e)
    W *= (1 - bw)[:, None]; W[:, BELLY] += bw
    for side, s in [('L', 1), ('R', -1)]:
        a = ARM[side]
        sh = D.arm_points(s)[0]
        dsh = np.linalg.norm(v - sh, axis=1)
        cl = .55 * ss(.17, .07, dsh) * ss(1.20, 1.30, y)
        W *= (1 - cl)[:, None]; W[:, a['shoulder']] += cl
    # the torso's neckline follows the neck a little
    nk = .3 * ss(1.36, 1.405, y)
    W *= (1 - nk)[:, None]; W[:, NECK] += nk
    # the hood is its own garment on the head and neck; the horn tube is part of the mask (head)
    hood = (vl == 1) | (vl == 4)
    head = np.where(vl == 4, 1.0, ss(1.42, 1.47, y))
    hw = np.zeros((len(v), NB)); hw[:, NECK] = 1 - head; hw[:, HEAD] = head
    W[hood] = hw[hood]
    for side, s in [('L', 1), ('R', -1)]:
        # the shoulder cap is a ball round the arm's pivot, so it can follow the half-rotation helper
        # (a turn about its own centre) and keep the sleeve head inside it as the arm rises
        sh = D.arm_points(s)[0]
        k = .55 * ss(.12, .06, np.linalg.norm(v - sh, axis=1)) * ss(.09, .13, s * v[:, 0]) * ss(1.20, 1.27, y)
        W *= (1 - k)[:, None]; W[:, ROOT_HALF[side]] += k
    torso_mask = ~(sleeve['L'] | sleeve['R'] | (vl == 4))
    ft = f[np.all(torso_mask[f], axis=1)]
    W[torso_mask] = smooth_weights(W, ft, 6)[torso_mask]
    for side, s in [('L', 1), ('R', -1)]:
        a = ARM[side]
        m = sleeve[side]
        sh, el, wr = D.arm_points(s)
        up, fo, ha = arm_chain(v[m], side)
        du = (el - sh) / np.linalg.norm(el - sh)
        tu = (v[m] - sh) @ du
        root = ss(.075, .0, tu)                    # sleeve head shares the half-rotation helper
        aw = np.zeros((m.sum(), NB))
        aw[:, a['upper']] = up * (1 - .65 * root); aw[:, ROOT_HALF[side]] = up * .65 * root
        aw[:, a['fore']] = fo; aw[:, a['hand']] = ha
        ed = np.linalg.norm(v[m] - el, axis=1)
        ew = .55 * np.exp(-(ed / .055) ** 2)        # elbow helper keeps the bend from collapsing
        aw *= (1 - ew)[:, None]; aw[:, ELBOW_HALF[side]] += ew
        W[m] = aw
    return W


def leg_weights(v, f):
    c = D.legging_parts(v)
    W = np.zeros((len(v), NB))
    W[:, HIPS] = 1
    y = v[:, 1]
    for side, s in [('L', 1), ('R', -1)]:
        L = LEG[side]
        legm = ss(-.03, .02, c['pelvis'] - c['leg_' + side]) * (s * v[:, 0] > -.01)
        legm = np.maximum(legm * (1 - ss(.80, .88, y)), (1 - ss(.70, .80, y)) * (s * v[:, 0] > 0))
        knee = D.J[f'Shin_{side}'][1]; ank = D.J[f'Foot_{side}'][1]
        shin = 1 - ss(knee - .04, knee + .05, y)
        foot = 1 - ss(ank - .01, ank + .05, y)
        lw = np.zeros((len(v), NB))
        lw[:, L['thigh']] = 1 - shin
        lw[:, L['shin']] = shin * (1 - foot)
        lw[:, L['foot']] = shin * foot
        W = W * (1 - legm)[:, None] + lw * legm[:, None]
    return smooth_weights(W, f, 4)


def glove_weights(p, side):
    a = ARM[side]
    v = p['v']
    W = np.zeros((len(v), NB))
    name = p['name']
    up, fo, ha = arm_chain(v, side)
    if 'hoof_cap' in name:
        W[:, a['fingers']] = 1
    elif 'cloth_thumb' in name:
        d = D.J[f'Hand_{side}'] - D.J[f'Forearm_{side}']; d /= np.linalg.norm(d)
        t = (v - D.J[f'Hand_{side}']) @ d
        k = ss(.015, .045, t)
        W[:, a['thumb']] = k; W[:, a['hand']] = 1 - k
    elif 'cuff' in name:
        W[:, a['upper']] = up; W[:, a['fore']] = fo; W[:, a['hand']] = ha
    else:
        d = D.J[f'Hand_{side}'] - D.J[f'Forearm_{side}']; d /= np.linalg.norm(d)
        t = (v - D.J[f'Hand_{side}']) @ d
        above = 1 - ss(-.03, .005, t)          # the part of the glove that is up over the sleeve
        W[:, a['upper']] = above * up; W[:, a['fore']] = above * fo
        W[:, a['hand']] = above * ha + (1 - above)
        k = ss(.085, .115, t) * .6             # palm fur next to the hoof caps follows them a little
        W *= (1 - k)[:, None]; W[:, a['fingers']] += k
    return W


def udder_weights(v, side):
    W = np.zeros((len(v), NB))
    s = 1 if side == 'L' else -1
    e = np.linalg.norm((v - D.CUP_C[s]) / D.CUP_R, axis=1)
    front = ss(-.02, .09, v[:, 2] - .02)
    k = .25 + .6 * front
    W[:, UDDER[side]] = k
    W[:, CHEST] = 1 - k
    for kk, (a, b) in enumerate(D.TEATS[s]):
        d = b - a; L = np.linalg.norm(d); d /= L
        t = (v - a) @ d
        r = np.linalg.norm((v - a) - t[:, None] * d, axis=1)
        m = (r < .026) & (t > -.006)
        tw = ss(.004, .026, t) * m
        W *= (1 - tw)[:, None]; W[:, TEAT[(side, kk)]] += tw
    return W


def quantize(W):
    W = np.clip(W, 0, None)
    W /= W.sum(1, keepdims=True)
    J = np.argsort(-W, axis=1)[:, :4]
    w = np.take_along_axis(W, J, axis=1)
    w /= w.sum(1, keepdims=True)
    q = np.rint(w * 255).astype(np.int32)
    q[:, 0] += 255 - q.sum(1)
    J = np.where(q > 0, J, 0)
    return J.astype(np.uint8), q.astype(np.uint8)
