"""Chicken Dance v10: Beaks, Wings, Tail-feather wiggle, Claps (12 s loop, 4 x 3 s, 4 moves each)."""
import numpy as np
from scipy.spatial.transform import Rotation, Slerp
import design as D
import rig as RG

FPS = 30
DURATION = 12.0
PHASES = ['Beaks', 'Wings', 'Wiggle', 'Claps']


def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    return Rotation.from_rotvec(a * ang).as_matrix()


def euler(xyz):
    return Rotation.from_euler('xyz', xyz).as_matrix()


def align(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = np.clip(a @ b, -1, 1)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3)
    return rot(v, np.arccos(c))


def frame(direction, normal):
    x = np.asarray(direction, float); x = x / np.linalg.norm(x)
    z = np.asarray(normal, float); z = z - x * (z @ x); z /= np.linalg.norm(z)
    return np.stack([x, z, np.cross(x, z)], 1)


def ik(a, target, l1, l2, pole):
    d = target - a; dist = np.linalg.norm(d); d /= dist
    dist = np.clip(dist, abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3)
    wrist = a + d * dist
    along = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    perp = pole - a - d * ((pole - a) @ d); perp /= np.linalg.norm(perp)
    elbow = a + d * along + perp * np.sqrt(max(0, l1 * l1 - along * along))
    return elbow, wrist


def smooth(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)


class Dance:
    def __init__(self, B):
        self.B = np.asarray(B, float)
        self.palm_half = {}
        self.bind_hand = {}
        for side, s in [('L', 1), ('R', -1)]:
            a = RG.ARM[side]
            df = self.B[a['hand']] - self.B[a['fore']]
            self.bind_hand[side] = frame(df, [-s, 0, 0])
            self.palm_half[side] = .03

    def hand_rot(self, side, finger_dir, palm_normal):
        return frame(finger_dir, palm_normal) @ self.bind_hand[side].T

    # ---------------------------------------------------------------- choreography
    def params(self, stage, u):
        beat = 2 * np.pi * 4 * u
        bounce = .5 - .5 * np.cos(beat)
        p = dict(shift=np.array([0, -.010 * bounce, 0]), hips=np.zeros(3), spine=np.zeros(3), chest=np.zeros(3),
                 neck=np.zeros(3), head=np.array([.05 * bounce, 0, 0]), hand={}, pole={}, hrot={}, clav={},
                 fingers=0., thumb=0.)
        for side, s in [('L', 1), ('R', -1)]:
            if stage == 0:      # Beaks: hands up in front, hoof "beaks" snap open/shut
                snap = .5 - .5 * np.cos(beat)
                p['hand'][side] = np.array([s * .135, 1.300 + .01 * snap, .355])
                p['pole'][side] = np.array([s * .55, .95, -.05])
                p['hrot'][side] = self.hand_rot(side, [s * -.12, .10, 1], [-s * .35, -1, 0])
                p['fingers'] = -.55 * snap; p['thumb'] = .45 * snap
                p['clav'][side] = .03
                p['head'] = np.array([.06 * snap, 0, 0])
            elif stage == 1:    # Wings: fists tucked at the armpits, elbows flap up and down
                flap = .5 - .5 * np.cos(beat)
                p['hand'][side] = np.array([s * .285, 1.300 + .02 * flap, .130])
                p['pole'][side] = np.array([s * .75, 1.00 + .62 * flap, -.30 + .05 * flap])
                p['hrot'][side] = ('follow', -.55)      # fists ride in line with the forearm, slight bend
                p['clav'][side] = .04 + .22 * flap
                p['fingers'] = -.9; p['thumb'] = .6
                p['shift'] = np.array([0, -.016 * flap, 0])
                p['neck'] = np.array([-.05 + .10 * flap, 0, 0])
                p['head'] = np.array([.08 - .14 * flap, 0, 0])
            elif stage == 2:    # Wiggle the tail feathers: knees bend, hips swish four times
                sway = np.sin(beat)
                down = .5 - .5 * np.cos(2 * np.pi * min(u * 1.6, 1)) if u < .6 else 1
                down = smooth(0, .12, u) * (1 - smooth(.88, 1, u))
                p['shift'] = np.array([.030 * sway, -.075 * down, -.01 * down])
                p['hips'] = np.array([-.10 * down, .22 * sway, -.05 * sway])
                p['spine'] = np.array([.08 * down, -.10 * sway, .04 * sway])
                p['chest'] = np.array([.06 * down, -.08 * sway, .03 * sway])
                p['head'] = np.array([-.03, .06 * sway, -.05 * sway])
                p['hand'][side] = np.array([s * .345, .985 - .03 * down, -.135])
                p['pole'][side] = np.array([s * .70, 1.25, -.25])
                p['hrot'][side] = self.hand_rot(side, [s * .45, -.55, -.70], [0, 0, 1])
                p['clav'][side] = .08
                p['fingers'] = -.15; p['thumb'] = .1
            else:               # Claps: four claps in front of the chest, above the udder
                open_ = .5 + .5 * np.cos(beat)
                half = self.palm_half[side]
                p['hand'][side] = np.array([s * (half + .012 + .24 * open_), 1.345 + .02 * open_, .365 - .03 * open_])
                p['pole'][side] = np.array([s * .70, .98, -.10])
                p['hrot'][side] = self.hand_rot(side, [s * .05 * open_, .55, .84], [-s, 0, 0])
                p['clav'][side] = .05
                p['shift'] = np.array([0, -.012 * (1 - open_), 0])
                p['head'] = np.array([.06 * (1 - open_), 0, 0])
        return p

    def blend(self, a, b, t):
        out = {}
        for k in ['shift', 'hips', 'spine', 'chest', 'neck', 'head', 'fingers', 'thumb']:
            out[k] = a[k] * (1 - t) + b[k] * t
        for k in ['hand', 'pole', 'clav']:
            out[k] = {s: a[k][s] * (1 - t) + b[k][s] * t for s in 'LR'}
        out['hrot'] = {s: ('blend', a['hrot'][s], b['hrot'][s], t) for s in 'LR'}
        return out

    def sample(self, t):
        t = t % DURATION
        stage = int(t // 3); u = (t - stage * 3) / 3
        bl = .35 / 3
        if u < bl:
            return self.blend(self.params((stage - 1) % 4, 1), self.params(stage, u), smooth(-bl, bl, u))
        if u > 1 - bl:
            return self.blend(self.params(stage, u), self.params((stage + 1) % 4, 0), smooth(-bl, bl, u - 1))
        return self.params(stage, u)

    # ---------------------------------------------------------------- pose solve
    def pose(self, t, jiggle=None):
        B = self.B
        p = self.sample(t)
        G = np.tile(np.eye(4), (RG.NB, 1, 1))

        def at(i, parent, R):
            G[i, :3, :3] = R
            G[i, :3, 3] = G[parent, :3, :3] @ (B[i] - B[parent]) + G[parent, :3, 3]
        Rh = euler(p['hips'])
        G[RG.HIPS, :3, :3] = Rh; G[RG.HIPS, :3, 3] = B[RG.HIPS] + p['shift']
        at(RG.SPINE, RG.HIPS, Rh @ euler(p['spine']))
        at(RG.BELLY, RG.SPINE, G[RG.SPINE, :3, :3])
        at(RG.CHEST, RG.SPINE, G[RG.SPINE, :3, :3] @ euler(p['chest']))
        Rc = G[RG.CHEST, :3, :3]
        for side in 'LR':
            at(RG.UDDER[side], RG.CHEST, Rc)
        at(RG.NECK, RG.CHEST, Rc @ euler(p['neck']))
        at(RG.HEAD, RG.NECK, G[RG.NECK, :3, :3] @ euler(p['head']))
        if jiggle is not None:
            for j, off in jiggle.items():
                G[j, :3, 3] += off
        for side, s in [('L', 1), ('R', -1)]:
            a = RG.ARM[side]
            at(a['shoulder'], RG.CHEST, Rc @ rot([0, 0, 1], s * p['clav'][side]))
            sh = G[a['shoulder'], :3, :3] @ (B[a['upper']] - B[a['shoulder']]) + G[a['shoulder'], :3, 3]
            l1 = np.linalg.norm(B[a['fore']] - B[a['upper']]); l2 = np.linalg.norm(B[a['hand']] - B[a['fore']])
            target = Rc @ (p['hand'][side] - B[RG.CHEST]) + G[RG.CHEST, :3, 3]
            pole = Rc @ (p['pole'][side] - B[RG.CHEST]) + G[RG.CHEST, :3, 3]
            elbow, wrist = ik(sh, target, l1, l2, pole)
            bu = B[a['fore']] - B[a['upper']]; bf = B[a['hand']] - B[a['fore']]
            hinge_b = np.cross(bu, bf); hinge_b /= np.linalg.norm(hinge_b)
            nu = elbow - sh; nf = wrist - elbow
            hinge_p = np.cross(nu, nf)
            if np.linalg.norm(hinge_p) < 1e-6:
                hinge_p = np.cross(nu, pole - sh)
            hinge_p /= np.linalg.norm(hinge_p)
            Ru = frame(nu, hinge_p) @ frame(bu, hinge_b).T
            Rf = frame(nf, hinge_p) @ frame(bf, hinge_b).T
            def resolve(h):
                if isinstance(h, tuple) and h[0] == 'follow':
                    return Rf @ rot(hinge_b, h[1])            # relative to the forearm (bind hinge axis)
                if isinstance(h, tuple) and h[0] == 'blend':
                    A, Bm = resolve(h[1]), resolve(h[2])
                    return Slerp([0, 1], Rotation.from_matrix([A, Bm]))([h[3]]).as_matrix()[0]
                return Rc @ h
            Rhand = resolve(p['hrot'][side])
            # distribute half of the wrist twist into the forearm (no candy-wrap at the cuff)
            rel = Rf.T @ Rhand
            axis_l = frame(bf, hinge_b).T @ (bf / np.linalg.norm(bf))
            q = Rotation.from_matrix(rel).as_quat()
            ax = bf / np.linalg.norm(bf)
            twist = 2 * np.arctan2(q[:3] @ ax, q[3])
            Rf = Rf @ rot(ax, .5 * twist)
            G[a['upper'], :3, :3] = Ru; G[a['upper'], :3, 3] = sh
            G[a['fore'], :3, :3] = Rf; G[a['fore'], :3, 3] = elbow
            G[a['hand'], :3, :3] = Rhand; G[a['hand'], :3, 3] = wrist
            fd = bf / np.linalg.norm(bf)
            knuckle = np.cross(fd, [-s, 0, 0]); knuckle /= np.linalg.norm(knuckle)
            sign = 1 if (rot(knuckle, .3) @ fd) @ np.array([-s, 0, 0]) > 0 else -1
            at(a['fingers'], a['hand'], Rhand @ rot(knuckle, -sign * p['fingers']))
            at(a['thumb'], a['hand'], Rhand @ rot(knuckle, -sign * p['thumb']))
        for side in 'LR':
            L = RG.LEG[side]
            hip = G[RG.HIPS, :3, :3] @ (B[L['thigh']] - B[RG.HIPS]) + G[RG.HIPS, :3, 3]
            ankle = B[L['foot']].copy()
            l1 = np.linalg.norm(B[L['shin']] - B[L['thigh']]); l2 = np.linalg.norm(B[L['foot']] - B[L['shin']])
            knee, ankle = ik(hip, ankle, l1, l2, B[L['shin']] + [0, 0, .8])
            for j, st, en, rest in [(L['thigh'], hip, knee, B[L['shin']] - B[L['thigh']]), (L['shin'], knee, ankle, B[L['foot']] - B[L['shin']])]:
                yaw = np.arctan2(*(Rh @ [0, 0, 1])[[0, 2]])
                R = align(rest, en - st)
                G[j, :3, :3] = R; G[j, :3, 3] = st
            G[L['foot'], :3, :3] = np.eye(3); G[L['foot'], :3, 3] = ankle
        return G

    def jiggle_track(self, times):
        """Damped-spring secondary motion of belly and udder bones, looped (3 laps, keep the last)."""
        dt = 1 / 240
        ts = np.arange(0, 3 * DURATION, dt)
        bodies = {RG.BELLY: RG.SPINE, RG.UDDER['L']: RG.CHEST, RG.UDDER['R']: RG.CHEST}
        pos = {j: [] for j in bodies}
        for t in ts[::8]:
            G = self.pose(t)
            for j in bodies:
                pos[j].append(G[j, :3, 3].copy())
        out = {}
        for j in bodies:
            P = np.array(pos[j]); tt = ts[::8]
            acc = np.gradient(np.gradient(P, tt, axis=0), tt, axis=0)
            k, c, gain = (110., 9., .55) if j == RG.BELLY else (150., 8., .6)
            x = np.zeros(3); v = np.zeros(3); hist = []
            for i in range(len(tt)):
                for _ in range(8):
                    a = -k * x - c * v - gain * acc[i]
                    v += a * dt; x += v * dt
                hist.append(x.copy())
            hist = np.clip(np.array(hist), -.02, .02)
            last = tt >= 2 * DURATION
            out[j] = np.stack([np.interp((times % DURATION) + 2 * DURATION, tt[last], hist[last, d]) for d in range(3)], 1)
        return out

    def bake(self, fps=FPS):
        times = np.linspace(0, DURATION, int(round(DURATION * fps)) + 1)
        jig = self.jiggle_track(times)
        Gs = np.stack([self.pose(t, {j: jig[j][i] for j in jig}) for i, t in enumerate(times)])
        return times, Gs


def skin_matrices(G, B):
    M = G.copy()
    M[:, :3, 3] -= np.einsum('nij,nj->ni', G[:, :3, :3], B)
    return M


def tracks(Gs, parents):
    """Local translation/rotation tracks per joint from global matrices (bind rotations are identity)."""
    L = Gs.copy()
    for i, pa in enumerate(parents):
        if pa >= 0:
            L[:, i] = np.linalg.inv(Gs[:, pa]) @ Gs[:, i]
    out = {}
    for i in range(len(parents)):
        q = Rotation.from_matrix(L[:, i, :3, :3]).as_quat()
        for k in range(1, len(q)):
            if q[k] @ q[k - 1] < 0:
                q[k] *= -1
        out[i] = (L[:, i, :3, 3].astype(np.float32), q.astype(np.float32))
    return out
