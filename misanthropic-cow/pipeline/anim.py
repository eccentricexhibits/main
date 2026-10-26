"""Animation solver for the v10 cow + the Chicken Dance (Beaks, Wings, Wiggle, Claps; 12 s, 4 x 3 s).

`Dance` holds the generic solver (arm IK/FK with elbow swivel, foot IK, half-rotation helpers, baked
spring physics).  Other clips subclass it and override `sample(t)` (see clips.py)."""
import numpy as np
from scipy.spatial.transform import Rotation, Slerp
import design as D
import rig as RG
import tail as TL

FPS = 30
SOFT_REACH = .02        # soft-IK band at full arm reach (m)
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


def ik(a, target, l1, l2, pole, swivel=0.0, soft=0.0):
    d = target - a; dist = np.linalg.norm(d); d /= dist
    if soft:
        # soft IK: near full reach the arm straightens gradually instead of snapping, so the elbow
        # never pops when a target moves in from just out of reach
        s0 = l1 + l2 - soft
        if dist > s0:
            dist = s0 + soft * (1 - np.exp(-(dist - s0) / soft))
    dist = np.clip(dist, abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3)
    wrist = a + d * dist
    along = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    perp = pole - a - d * ((pole - a) @ d); perp /= np.linalg.norm(perp)
    if swivel:
        perp = rot(d, swivel) @ perp          # swing the elbow round the shoulder-wrist line
    elbow = a + d * along + perp * np.sqrt(max(0, l1 * l1 - along * along))
    return elbow, wrist


_SOLE = None


def sole_points():
    """The slippers' sole region relative to the ankle joint, in the foot's frame (both feet)."""
    global _SOLE
    if _SOLE is None:
        import glb as G, assets as A
        pts = []
        for p in G.read(A.SLIPPER_ASSET).parts:
            s = 1 if '_L_' in p['name'] else -1
            v = p['v'][p['v'][:, 1] < .035]
            v = v @ rot([0, 1, 0], s * np.deg2rad(7)).T
            pts.append(v + np.array([0, A.SLIPPER_SOLE - D.J['Foot_L'][1], 0]))
        _SOLE = np.vstack(pts)[::3]
    return _SOLE


def smooth(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)


class Dance:
    name = 'Chicken Dance'
    duration = DURATION
    phases = [(n, 3 * i, 3 * i + 3) for i, n in enumerate(PHASES)]
    use_swivel = True

    def __init__(self, B):
        self.B = np.asarray(B, float)
        self.palm_half = {}
        self.bind_hand = {}
        self.flex_sign = {}
        for side, s in [('L', 1), ('R', -1)]:
            a = RG.ARM[side]
            df = self.B[a['hand']] - self.B[a['fore']]
            bu = self.B[a['fore']] - self.B[a['upper']]
            self.bind_hand[side] = frame(df, [-s, 0, 0])
            self.palm_half[side] = .03
            hinge = np.cross(bu, df); hinge /= np.linalg.norm(hinge)
            self.flex_sign[side] = 1 if (rot(hinge, .4) @ df)[2] > df[2] else -1
        # slipper contact points relative to the ankle (heel and toe), for keeping soles on the floor
        self.sole = sole_points()
        self._twist = {}

    def ankle_height(self, pitch):
        """Ankle height that keeps the lowest point of the slipper sole on the floor at this pitch."""
        R = rot([1, 0, 0], pitch)
        return float(-(self.sole @ R.T)[:, 1].min()) + .003

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
                p['hand'][side] = np.array([s * .150, 1.350 + .01 * snap, .405])
                p['pole'][side] = np.array([s * .65, 1.05, .05])
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
                p['hand'][side] = np.array([s * (half + .0015 + .24 * open_), 1.395 + .02 * open_, .405 - .03 * open_])
                p['pole'][side] = np.array([s * .75, 1.12, .02])
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
        t = t % self.duration
        stage = int(t // 3); u = (t - stage * 3) / 3
        bl = .35 / 3
        if u < bl:
            return self.blend(self.params((stage - 1) % 4, 1), self.params(stage, u), smooth(-bl, bl, u))
        if u > 1 - bl:
            return self.blend(self.params(stage, u), self.params((stage + 1) % 4, 0), smooth(-bl, bl, u - 1))
        return self.params(stage, u)

    # ---------------------------------------------------------------- obstacles for the arms
    def clearance(self, G, pts):
        """Signed distance of posed points to the udder cups and torso (rigid in chest/spine frames)."""
        B = self.B
        best = np.full(len(pts), 1e3)
        for j in (RG.CHEST, RG.SPINE):
            q = (pts - G[j, :3, 3]) @ G[j, :3, :3] + B[j]          # back to bind space
            best = np.minimum(best, D.torso_sdf(q))
            if j == RG.CHEST:
                best = np.minimum(best, D.udder_sdf(q))
        return best

    def arm_samples(self, sh, elbow, wrist):
        pu = sh + (elbow - sh) * np.linspace(.30, 1, 6)[:, None]
        pf = elbow + (wrist - elbow) * np.linspace(0, 1, 7)[:, None]
        return np.vstack([pu, pf])

    def arm_cost(self, G, sh, elbow, wrist):
        d = self.clearance(G, self.arm_samples(sh, elbow, wrist))
        r = np.r_[np.full(6, .074), np.full(7, .062)]
        # the relaxed arms already rest against the padded body: only count contact deeper than at rest
        side = 'L' if sh[0] > 0 else 'R'
        if not hasattr(self, '_rest_clear'):
            Gb = np.tile(np.eye(4), (RG.NB, 1, 1)); Gb[:, :3, 3] = self.B
            self._rest_clear = {}
            for sd in 'LR':
                a = RG.ARM[sd]
                self._rest_clear[sd] = self.clearance(Gb, self.arm_samples(self.B[a['upper']], self.B[a['fore']], self.B[a['hand']]))
        r = np.minimum(r, self._rest_clear[side])
        return float(np.sum(np.maximum(0, r - d) ** 2))

    def solve_swivel(self, fps=FPS):
        """Pick, per frame, how far to swing each elbow around the shoulder-wrist line to stay clear
        of the cups and torso; continuity-weighted, then smoothed around the loop."""
        self.swivel = None
        if not self.use_swivel:
            return
        times = np.arange(0, self.duration, 1 / fps)
        cand = np.linspace(-1.1, 1.1, 23)
        out = {}
        costs = {s: np.zeros((len(times), len(cand))) for s in 'LR'}
        for i, t in enumerate(times):
            G, arm = self.pose(t, solve=True)
            for side in 'LR':
                sh, target, l1, l2, pole, soft = arm[side]
                for c, phi in enumerate(cand):
                    el, wr = ik(sh, target, l1, l2, pole, phi, soft)
                    costs[side][i, c] = self.arm_cost(G, sh, el, wr) + 2e-4 * phi * phi
        for side in 'LR':
            C = costs[side]
            # Viterbi over the loop (twice round for wrap-around), penalising elbow jumps
            jump = 2e-3 * (cand[:, None] - cand[None, :]) ** 2
            acc = C[0].copy(); back = []
            seq = np.r_[np.arange(len(times)), np.arange(len(times))]
            for i in seq[1:]:
                tot = acc[:, None] + jump
                arg = tot.argmin(0); back.append(arg)
                acc = tot.min(0) + C[i]
            path = [int(acc.argmin())]
            for arg in reversed(back):
                path.append(int(arg[path[-1]]))
            path = np.array(path[::-1])[len(times):]
            phi = cand[path]
            k = np.exp(-np.arange(-6, 7) ** 2 / 8.0); k /= k.sum()
            ext = np.r_[phi[-6:], phi, phi[:6]]
            out[side] = np.convolve(ext, k, 'valid')
            self.swivel_cost = getattr(self, 'swivel_cost', {})
            self.swivel_cost[side] = float(C[np.arange(len(times)), path].max())
        self.swivel = (times, out)

    def swivel_at(self, t, side):
        if getattr(self, 'swivel', None) is None:
            return 0.0
        times, phi = self.swivel
        return float(np.interp(t % self.duration, np.r_[times, self.duration], np.r_[phi[side], phi[side][0]]))

    # ---------------------------------------------------------------- pose solve
    def pose(self, t, dyn=None, solve=False):
        B = self.B
        p = self.sample(t)
        G = np.tile(np.eye(4), (RG.NB, 1, 1))
        dyn = dyn or {}
        trans = dyn.get('trans', {})

        def at(i, parent, R):
            G[i, :3, :3] = R
            G[i, :3, 3] = G[parent, :3, :3] @ (B[i] - B[parent]) + G[parent, :3, 3] + trans.get(i, 0)
        Rh = euler(p['hips'])
        G[RG.HIPS, :3, :3] = Rh; G[RG.HIPS, :3, 3] = B[RG.HIPS] + p['shift']
        at(RG.SPINE, RG.HIPS, Rh @ euler(p['spine']))
        at(RG.BELLY, RG.SPINE, G[RG.SPINE, :3, :3])
        at(RG.CHEST, RG.SPINE, G[RG.SPINE, :3, :3] @ euler(p['chest']))
        Rc = G[RG.CHEST, :3, :3]
        for side in 'LR':
            at(RG.UDDER[side], RG.CHEST, Rc)
            for k in range(2):
                j = RG.TEAT[(side, k)]
                at(j, RG.UDDER[side], Rc)
                if j in dyn.get('teat', {}):
                    G[j, :3, :3] = align(Rc @ self.teat_dir[j], dyn['teat'][j]) @ Rc
        at(RG.NECK, RG.CHEST, Rc @ euler(p['neck']))
        at(RG.HEAD, RG.NECK, G[RG.NECK, :3, :3] @ euler(p['head']))
        # legs first, so a hand can be placed relative to a knee
        for side in 'LR':
            L = RG.LEG[side]
            hip = G[RG.HIPS, :3, :3] @ (B[L['thigh']] - B[RG.HIPS]) + G[RG.HIPS, :3, 3]
            ft = (p.get('feet') or {}).get(side)
            if ft is None:
                ankle, Rfoot = B[L['foot']].copy(), np.eye(3)
            else:
                ankle = np.asarray(ft['pos'], float)
                Rfoot = rot([0, 1, 0], ft.get('yaw', 0.)) @ rot([1, 0, 0], ft.get('pitch', 0.))
            l1 = np.linalg.norm(B[L['shin']] - B[L['thigh']]); l2 = np.linalg.norm(B[L['foot']] - B[L['shin']])
            knee_dir = np.asarray((ft or {}).get('knee', (0, -.35, .8)), float)   # (0, .8, .35) for knees up when seated
            knee_pole = hip + rot([0, 1, 0], (ft or {}).get('yaw', 0.)) @ knee_dir
            knee, ankle = ik(hip, ankle, l1, l2, knee_pole)
            for j, st, en, rest in [(L['thigh'], hip, knee, B[L['shin']] - B[L['thigh']]), (L['shin'], knee, ankle, B[L['foot']] - B[L['shin']])]:
                G[j, :3, :3] = align(rest, en - st); G[j, :3, 3] = st
            G[L['foot'], :3, :3] = Rfoot; G[L['foot'], :3, 3] = ankle
        arm_in = {}
        for side, s in [('L', 1), ('R', -1)]:
            a = RG.ARM[side]
            at(a['shoulder'], RG.CHEST, Rc @ rot([0, 0, 1], s * p.get('clav', {}).get(side, 0.)))
            sh = G[a['shoulder'], :3, :3] @ (B[a['upper']] - B[a['shoulder']]) + G[a['shoulder'], :3, 3]
            l1 = np.linalg.norm(B[a['fore']] - B[a['upper']]); l2 = np.linalg.norm(B[a['hand']] - B[a['fore']])
            if side in p.get('fk', {}):
                # forward kinematics: abduction / forward flexion of the upper arm (chest frame) and
                # extra elbow bend, turned into an IK target + pole that reproduce it exactly
                abd, flex, bend = p['fk'][side]
                bu0 = B[a['fore']] - B[a['upper']]; bf0 = B[a['hand']] - B[a['fore']]
                hinge0 = np.cross(bu0, bf0); hinge0 /= np.linalg.norm(hinge0)
                Rl = rot([0, 0, 1], s * abd) @ rot([1, 0, 0], -flex)
                el_fk = sh + Rc @ Rl @ bu0
                wr_fk = el_fk + Rc @ Rl @ rot(hinge0, self.flex_sign[side] * bend) @ bf0
                mid = sh + (wr_fk - sh) * (((el_fk - sh) @ (wr_fk - sh)) / ((wr_fk - sh) @ (wr_fk - sh)))
                off = el_fk - mid
                if np.linalg.norm(off) < 2e-3:
                    off = Rc @ Rl @ np.cross(hinge0, bu0)
                target = wr_fk
                pole = el_fk + .3 * off / np.linalg.norm(off)
            else:
                target = Rc @ (p['hand'][side] - B[RG.CHEST]) + G[RG.CHEST, :3, 3]
                pole = Rc @ (p['pole'][side] - B[RG.CHEST]) + G[RG.CHEST, :3, 3]
            if side in p.get('hand_joint', {}):
                # hand placed on a joint (e.g. resting on a knee): (joint, world offset, world pole, weight)
                j, off, pole_w, w = p['hand_joint'][side]
                target = target * (1 - w) + (G[j, :3, 3] + off) * w
                pole = pole * (1 - w) + np.asarray(pole_w, float) * w
            if side in p.get('hand_world', {}):
                # world-space hand target (e.g. a hoof on the floor), blended in by world_w
                w = p.get('world_w', {}).get(side, 1.)
                target = target * (1 - w) + np.asarray(p['hand_world'][side], float) * w
                pole = pole * (1 - w) + np.asarray(p['pole_world'][side], float) * w
            soft = 0. if side in p.get('fk', {}) else SOFT_REACH     # FK targets are exactly reachable
            arm_in[side] = (sh, target, l1, l2, pole, soft)
            elbow, wrist = ik(sh, target, l1, l2, pole, self.swivel_at(t, side), soft)
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
                    return Rf @ rot(hinge_b, h[1])
                if isinstance(h, tuple) and h[0] == 'blend':
                    A, Bm = resolve(h[1]), resolve(h[2])
                    return Slerp([0, 1], Rotation.from_matrix([A, Bm]))([h[3]]).as_matrix()[0]
                return Rc @ h
            Rhand = resolve(p['hrot'][side])
            rel = Rf.T @ Rhand
            q = Rotation.from_matrix(rel).as_quat()
            if q[3] < 0:
                q = -q
            ax = bf / np.linalg.norm(bf)
            twist = 2 * np.arctan2(q[:3] @ ax, q[3])
            # keep the wrist twist continuous from one sample to the next (poses are evaluated in time
            # order), so a hand rolled near 180 degrees never flips the forearm half a turn
            prev = self._twist.get(side)
            if prev is not None:
                twist += 2 * np.pi * np.round((prev - twist) / (2 * np.pi))
            self._twist[side] = twist
            Rf = Rf @ rot(ax, .5 * twist)
            G[a['upper'], :3, :3] = Ru; G[a['upper'], :3, 3] = sh
            G[a['fore'], :3, :3] = Rf; G[a['fore'], :3, 3] = elbow
            G[a['hand'], :3, :3] = Rhand; G[a['hand'], :3, 3] = wrist
            half = lambda A, Bm: Slerp([0, 1], Rotation.from_matrix([A, Bm]))([.5]).as_matrix()[0]
            G[RG.ROOT_HALF[side], :3, :3] = half(G[a['shoulder'], :3, :3], Ru); G[RG.ROOT_HALF[side], :3, 3] = sh
            G[RG.ELBOW_HALF[side], :3, :3] = half(Ru, Rf); G[RG.ELBOW_HALF[side], :3, 3] = elbow
            fd = bf / np.linalg.norm(bf)
            knuckle = np.cross(fd, [-s, 0, 0]); knuckle /= np.linalg.norm(knuckle)
            sign = 1 if (rot(knuckle, .3) @ fd) @ np.array([-s, 0, 0]) > 0 else -1
            at(a['fingers'], a['hand'], Rhand @ rot(knuckle, -sign * p['fingers']))
            at(a['thumb'], a['hand'], Rhand @ rot(knuckle, -sign * p['thumb']))
        for j, parent in zip(RG.SHAG, RG.SHAG_PARENTS):
            pi = RG.NAMES.index(parent)
            at(j, pi, G[pi, :3, :3])
        # the tail: bow rigid on the hips; the cord follows the baked rope (or hangs rigidly without it)
        Rh = G[RG.HIPS, :3, :3]
        at(RG.TAIL_BOW, RG.HIPS, Rh)
        rope = dyn.get('tail')
        for i, j in enumerate(RG.TAIL):
            if rope is None:
                at(j, RG.PARENTS[j], Rh)
            else:
                rest = (B[RG.TAIL[i + 1]] if i + 1 < len(RG.TAIL) else B[j] + [0, -TL.PLUG_SEG, 0]) - B[j]
                G[j, :3, :3] = align(rest, rope[i + 1] - rope[i])
                G[j, :3, 3] = rope[i]
        if solve:
            return G, arm_in
        return G

    # ---------------------------------------------------------------- light physics (baked)
    @property
    def teat_dir(self):
        if not hasattr(self, '_teat_dir'):
            self._teat_dir, self._teat_len = {}, {}
            for side, s in [('L', 1), ('R', -1)]:
                for k, (a, b) in enumerate(D.TEATS[s]):
                    j = RG.TEAT[(side, k)]
                    d = b - self.B[j]
                    self._teat_len[j] = float(np.linalg.norm(d)); self._teat_dir[j] = d / np.linalg.norm(d)
        return self._teat_dir

    def dynamics(self, times):
        """Damped springs for belly, udder cups, shag patches and teats; teats collide with the belly.
        Simulated for three loops; the last loop is kept so the animation cycles seamlessly."""
        sub, fps = 8, FPS
        dt = 1 / (fps * sub)
        D_ = self.duration
        tt = np.arange(0, 3 * D_, 1 / fps)
        springs = {RG.BELLY: (110., 9., .55, .020), RG.UDDER['L']: (150., 8., .6, .016), RG.UDDER['R']: (150., 8., .6, .016)}
        for j in RG.SHAG:
            springs[j] = (70., 5.5, .9, .022)
        # heavier clips (the alt set) use softer, slower springs that swing a little further
        ks, gs = getattr(self, 'spring_k', 1.), getattr(self, 'spring_gain', 1.)
        springs = {j: (k * ks, c * np.sqrt(ks), g * gs, lim * gs) for j, (k, c, g, lim) in springs.items()}
        base = [self.pose(t) for t in tt]
        trans_hist = {}
        for j, (k, c, gain, lim) in springs.items():
            P = np.array([g[j, :3, 3] for g in base])
            acc = np.gradient(np.gradient(P, tt, axis=0), tt, axis=0)
            x = np.zeros(3); v = np.zeros(3); hist = []
            for i in range(len(tt)):
                for _ in range(sub):
                    v += (-k * x - c * v - gain * acc[i]) * dt; x += v * dt
                hist.append(x.copy())
            h = np.clip(np.array(hist), -lim, lim)
            if j in RG.UDDER.values():
                h[:, 1] = np.maximum(h[:, 1], -.006)          # cups never sink into the belly
            trans_hist[j] = h
        # teats: tips follow their rest direction on a spring, then are pushed clear of the belly
        posed = [self.pose(t, {'trans': {j: trans_hist[j][i] for j in trans_hist}}) for i, t in enumerate(tt)]
        teat_hist = {}
        for j in self.teat_dir:
            L = self._teat_len[j]
            rest = np.array([g[j, :3, 3] + g[j, :3, :3] @ (self.teat_dir[j] * L) for g in posed])
            acc = np.gradient(np.gradient(rest, tt, axis=0), tt, axis=0)
            o = np.zeros(3); v = np.zeros(3); dirs = []
            for i in range(len(tt)):
                for _ in range(sub):
                    v += (-260. * o - 11. * v - .8 * acc[i] + np.array([0, -1.5, 0])) * dt; o += v * dt
                o = np.clip(o, -.02, .02)
                g = posed[i]; b0 = g[j, :3, 3]
                tip = rest[i] + o
                for _ in range(3):
                    dvec = tip - b0; dvec /= np.linalg.norm(dvec); tip = b0 + dvec * L
                    for frac in (.55, 1.0):
                        q = b0 + dvec * L * frac
                        qb = (q - g[RG.SPINE, :3, 3]) @ g[RG.SPINE, :3, :3] + self.B[RG.SPINE]
                        dist = D.torso_sdf(qb[None])[0]
                        need = .017          # teat radius (~1.5 cm) plus a little
                        if dist < need:
                            e = 1e-3
                            grad = np.array([D.torso_sdf((qb + dd)[None])[0] - D.torso_sdf((qb - dd)[None])[0] for dd in np.eye(3) * e]) / (2 * e)
                            grad = g[RG.SPINE, :3, :3] @ (grad / max(np.linalg.norm(grad), 1e-9))
                            tip = tip + grad * (need - dist) / frac
                dvec = tip - b0
                dirs.append(dvec / np.linalg.norm(dvec))
                o = tip - rest[i]
            teat_hist[j] = np.array(dirs)
        # the tail cord: a rope pinned to the bow, colliding with the seat, legs, slippers and floor
        anchors = np.array([g[RG.TAIL_BOW, :3, :3] @ (TL.ANCHOR - self.B[RG.TAIL_BOW]) + g[RG.TAIL_BOW, :3, 3] for g in posed])
        rope = TL.simulate(anchors, posed, self.B, RG, fps)
        last = tt >= 2 * D_ - 1e-9
        idx = np.searchsorted(tt[last], (times % D_) + 2 * D_ - 1e-9).clip(0, last.sum() - 1)
        per = int(round(D_ * fps))
        out = []
        for i in range(len(times)):
            k = np.nonzero(last)[0][idx[i]]
            # cross-fade the third loop into the second over the clip, so the rope's end state meets its start
            u = smooth(0, 1, (times[i] % D_) / D_)
            out.append({'trans': {j: trans_hist[j][k] for j in trans_hist}, 'teat': {j: teat_hist[j][k] for j in teat_hist},
                        'tail': TL.relength(rope[k] * (1 - u) + rope[max(k - per, 0)] * u)})
        return out

    def bake(self, fps=FPS):
        self.solve_swivel(fps)
        times = np.linspace(0, self.duration, int(round(self.duration * fps)) + 1)
        dyn = self.dynamics(times)
        dyn[-1] = dyn[0]
        Gs = np.stack([self.pose(t, dyn[i]) for i, t in enumerate(times)])
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
