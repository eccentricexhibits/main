"""Animation library for the v10 cow, built on the generic solver in anim.py.

Two sets: the standard clips, and an "alt" version of each original clip (`lumbering`) that plays
them as the character is: heavy, awkward, a little depressed.  The new mood clips (Depressed Walk,
Sit Cross-Legged, Crying, Exasperated) are written in that style from the start.

Every clip loops seamlessly and plays in place (no root travel), so it can be dropped into a viewer or
an engine's locomotion system.  Arms are given either as IK targets (hand position in the chest's
bind frame + elbow pole) or as FK angles (abduction, forward flexion, extra elbow bend), feet as ankle
targets with pitch so heel-strike / toe-off read and the slippers never go through the floor.
"""
import numpy as np
from scipy.spatial.transform import Rotation, Slerp
import anim as AN
import rig as RG

rot = AN.rot
smooth = AN.smooth


def neutral(clip):
    return dict(shift=np.zeros(3), hips=np.zeros(3), spine=np.zeros(3), chest=np.zeros(3), neck=np.zeros(3),
                head=np.zeros(3), fingers=-.12, thumb=.10, clav={'L': 0., 'R': 0.},    # hooves and thumb relaxed, a little curled
                fk={'L': np.array([0., 0., 0.]), 'R': np.array([0., 0., 0.])},
                hrot={'L': ('follow', .12), 'R': ('follow', .12)}, feet=None)


def mix(a, b, w):
    """Blend two parameter dicts (vectors linearly, hand rotations by slerp)."""
    out = {}
    for k, va in a.items():
        vb = b[k]
        if k == 'hrot':
            out[k] = {s: ('blend', va[s], vb[s], w) for s in va}
        elif k == 'feet':
            out[k] = None if va is None else {s: {kk: np.asarray(va[s][kk], float) * (1 - w) + np.asarray(vb[s][kk], float) * w
                                                  for kk in va[s]} for s in va}
        elif isinstance(va, dict):
            out[k] = {s: np.asarray(va[s], float) * (1 - w) + np.asarray(vb[s], float) * w for s in va}
        else:
            out[k] = np.asarray(va, float) * (1 - w) + np.asarray(vb, float) * w
    return out


def gait(clip, phase, side_x, stride, stance, lift, heel=-.22, toeoff=.38, tiptoe=0., lift_early=1.0):
    """One foot of an in-place gait cycle. phase in [0,1): 0 = heel strike (foot forward)."""
    phase %= 1.0
    if phase < stance:
        u = phase / stance
        z = stride / 2 - stride * u
        y = 0.
        pitch = tiptoe + heel * (1 - smooth(0, .18, u)) + toeoff * smooth(.65, 1, u)
    else:
        u = (phase - stance) / (1 - stance)
        z = -stride / 2 + stride * smooth(0, 1, u)
        y = lift * np.sin(np.pi * u ** lift_early) ** 1.2
        pitch = tiptoe + toeoff * (1 - smooth(0, .45, u)) + heel * smooth(.6, 1, u)
    pos = np.array([side_x, clip.ankle_height(pitch) + y, -.022 + z])
    return {'pos': pos, 'pitch': pitch, 'yaw': 0.}


class Idle(AN.Dance):
    name = 'Idle'
    duration = 4.0
    phases = [('Idle', 0, 4)]
    use_swivel = False

    def sample(self, t):
        p = neutral(self)
        b = np.sin(2 * np.pi * t / self.duration)
        b2 = np.sin(4 * np.pi * t / self.duration)
        p['shift'] = np.array([.006 * b, -.004 * (1 - np.cos(2 * np.pi * t / self.duration)) * .5, 0])
        p['chest'] = np.array([-.012 * b2, 0, .01 * b])
        p['head'] = np.array([.02 * b2, .06 * np.sin(2 * np.pi * t / self.duration + .7), 0])
        for side, s in [('L', 1), ('R', -1)]:
            p['fk'][side] = np.array([.10 + .01 * b * s, .03 * b2, .06])
        return p


class Walk(AN.Dance):
    name = 'Walk'
    duration = 1.12
    phases = [('Walk', 0, 1.12)]
    use_swivel = False
    stride, stance, lift = .36, .60, .055

    def sample(self, t):
        p = neutral(self)
        ph = (t / self.duration) % 1.0
        w = 2 * np.pi * ph
        p['feet'] = {'L': gait(self, ph, self.B[RG.LEG['L']['foot']][0], self.stride, self.stance, self.lift),
                     'R': gait(self, ph + .5, self.B[RG.LEG['R']['foot']][0], self.stride, self.stance, self.lift)}
        p['shift'] = np.array([.022 * np.sin(w), -.045 + .012 * np.cos(2 * w), .0])
        p['hips'] = np.array([.0, -.10 * np.sin(w), -.035 * np.sin(w)])
        p['spine'] = np.array([.03, .05 * np.sin(w), .02 * np.sin(w)])
        p['chest'] = np.array([.02, .08 * np.sin(w), 0])
        p['head'] = np.array([-.02, -.03 * np.sin(w), .015 * np.sin(w)])
        for side, s in [('L', 1), ('R', -1)]:
            swing = -s * np.sin(w)               # arm swings opposite its own leg
            p['fk'][side] = np.array([.17, .30 * swing + .05, .22 + .12 * max(0, swing)])
        return p


class Run(AN.Dance):
    name = 'Run'
    duration = .72
    phases = [('Run', 0, .72)]
    use_swivel = False
    stride, stance, lift = .52, .42, .16

    def sample(self, t):
        p = neutral(self)
        ph = (t / self.duration) % 1.0
        w = 2 * np.pi * ph
        p['feet'] = {'L': gait(self, ph, self.B[RG.LEG['L']['foot']][0], self.stride, self.stance, self.lift, -.15, .55, lift_early=.8),
                     'R': gait(self, ph + .5, self.B[RG.LEG['R']['foot']][0], self.stride, self.stance, self.lift, -.15, .55, lift_early=.8)}
        air = np.clip(np.sin(2 * w + .6), 0, 1)
        p['shift'] = np.array([.015 * np.sin(w), -.085 + .035 * air, .02])
        p['hips'] = np.array([.08, -.12 * np.sin(w), -.03 * np.sin(w)])
        p['spine'] = np.array([.12, .06 * np.sin(w), 0])
        p['chest'] = np.array([.06, .10 * np.sin(w), 0])
        p['neck'] = np.array([-.10, 0, 0])
        p['head'] = np.array([-.08, -.05 * np.sin(w), 0])
        for side, s in [('L', 1), ('R', -1)]:
            swing = -s * np.sin(w)
            p['fk'][side] = np.array([.42, .42 * swing + .05, 1.15 + .15 * swing])
            p['hrot'][side] = ('follow', .2)
        p['fingers'] = -.6; p['thumb'] = .4
        return p


class Sneak(AN.Dance):
    """Cartoon tiptoe: crouched, high knees, pointed toes, hooves dangling in front of the chest."""
    name = 'Sneak'
    duration = 2.6
    phases = [('Sneak', 0, 2.6)]
    use_swivel = True
    stride, stance, lift = .30, .58, .15

    def sample(self, t):
        p = neutral(self)
        ph = (t / self.duration) % 1.0
        w = 2 * np.pi * ph
        p['feet'] = {'L': gait(self, ph, self.B[RG.LEG['L']['foot']][0] + .02, self.stride, self.stance, self.lift, .0, .25, tiptoe=.45, lift_early=.75),
                     'R': gait(self, ph + .5, self.B[RG.LEG['R']['foot']][0] - .02, self.stride, self.stance, self.lift, .0, .25, tiptoe=.45, lift_early=.75)}
        p['shift'] = np.array([.03 * np.sin(w), -.040 + .018 * np.cos(2 * w), -.02])
        p['hips'] = np.array([.10, -.12 * np.sin(w), -.05 * np.sin(w)])
        p['spine'] = np.array([.10, .06 * np.sin(w), .03 * np.sin(w)])
        p['chest'] = np.array([.06, .06 * np.sin(w), 0])
        look = np.sin(w + .8)
        p['neck'] = np.array([.10, .20 * look, 0])
        p['head'] = np.array([.05, .22 * look, -.04 * look])
        bob = .012 * np.sin(2 * w)
        for side, s in [('L', 1), ('R', -1)]:
            p.pop('fk', None)
            p.setdefault('hand', {})[side] = np.array([s * .205, 1.285 + bob, .345])
            p.setdefault('pole', {})[side] = np.array([s * .62, 1.02, -.06])
            p['hrot'][side] = self.hand_rot(side, [s * .05, -1, .30], [0, .30, -1])
            p['clav'][side] = .06
        p['fingers'] = -.55; p['thumb'] = .35
        return p


class JumpingJacks(AN.Dance):
    name = 'Jumping Jacks'
    duration = 4.0
    phases = [('Jumping Jacks', 0, 4.0)]
    use_swivel = False

    def sample(self, t):
        p = neutral(self)
        ph = (t / 1.0) % 1.0
        open_ = .5 - .5 * np.cos(2 * np.pi * ph)
        air = abs(np.sin(2 * np.pi * ph)) ** 1.3          # airborne mid-transition, landing at open/closed
        land = (1 - abs(np.sin(2 * np.pi * ph))) ** 6
        p['shift'] = np.array([0, -.035 + .075 * air - .045 * land, 0])
        p['spine'] = np.array([.02 * land, 0, 0])
        p['head'] = np.array([-.04 * open_, 0, 0])
        p['feet'] = {}
        for side, s in [('L', 1), ('R', -1)]:
            pitch = .30 * air
            x = self.B[RG.LEG[side]['foot']][0] + s * .17 * open_
            p['feet'][side] = {'pos': np.array([x, self.ankle_height(pitch) + .075 * air, -.022]), 'pitch': pitch, 'yaw': s * .12 * open_}
            p['fk'][side] = np.array([.10 + 2.40 * open_, .26 * open_, .10 + .15 * (1 - open_)])
            p['clav'][side] = .22 * open_
            p['hrot'][side] = ('follow', .1)
        return p


class LookAround(AN.Dance):
    """Turn to look left and right with a hoof shading the eyes, look up, then lean in and peer."""
    name = 'Look Around'
    duration = 6.0
    phases = [('Look Around', 0, 6.0)]
    use_swivel = True

    def key(self, look_yaw=0., look_pitch=0., lean=0., shade_L=0., shade_R=0., squat=0.):
        """The hoof on the side being looked toward shades the eyes, so no arm crosses the face."""
        p = neutral(self)
        p['shift'] = np.array([.02 * np.sign(look_yaw) * min(1, abs(look_yaw) / .5), -.02 * squat, .015 * lean])
        p['spine'] = np.array([.08 * lean, .25 * look_yaw, 0])
        p['chest'] = np.array([.04 * lean, .20 * look_yaw, 0])
        p['neck'] = np.array([.4 * look_pitch, .25 * look_yaw, 0])
        p['head'] = np.array([.6 * look_pitch, .30 * look_yaw, -.05 * look_yaw])
        p.pop('fk')
        p['hand'], p['pole'] = {}, {}
        yaw = .55 * look_yaw                      # head yaw relative to the chest
        neck = np.array([0, 1.40, -.03])
        for side, s in [('L', 1), ('R', -1)]:
            shade = shade_L if side == 'L' else shade_R
            rest = self.B[RG.ARM[side]['hand']] + np.array([s * .04, .0, .015])      # relaxed, clear of the belly
            pole_rest = self.B[RG.ARM[side]['fore']] + np.array([s * .25, 0, -.15])
            brow = neck + rot([0, 1, 0], yaw) @ (np.array([s * .035, 1.585, .25]) - neck)
            # out and up at the side first (clear of the cup), then in over the brow (clear of the muzzle)
            c1 = np.array([s * .47, 1.12, -.02])
            c2 = neck + rot([0, 1, 0], yaw) @ (np.array([s * .24, 1.66, .20]) - neck)
            tgt = bspline_reach(rest, c1, c2, brow, shade)
            p['hand'][side] = tgt + np.array([0, 0, .02 * lean]) * (1 - shade)
            p['pole'][side] = pole_rest * (1 - shade) + np.array([s * .60, 1.40, -.12]) * shade
            flat = self.hand_rot(side, rot([0, 1, 0], yaw) @ np.array([-s, .12, .30]), [0, -1, 0])
            p['hrot'][side] = ('blend', ('follow', .12), flat, smooth(.55, 1, shade))   # turn the hoof flat only near the brow
        return p

    def sample(self, t):
        keys = [(0.0, dict()), (.9, dict(look_yaw=1., shade_L=1.)), (1.9, dict(look_yaw=1.1, shade_L=1., lean=.6)),
                (2.5, dict(look_yaw=.1)),
                (3.2, dict(look_yaw=-1., shade_R=1.)), (4.1, dict(look_yaw=-1.1, shade_R=1., lean=.5)),
                (4.8, dict(look_pitch=-.9)), (5.4, dict(look_pitch=-.5, squat=.4)), (6.0, dict())]
        t = t % self.duration
        fields = ['look_yaw', 'look_pitch', 'lean', 'shade_L', 'shade_R', 'squat']
        for (t0, k0), (t1, k1) in zip(keys[:-1], keys[1:]):
            if t0 <= t <= t1:
                w = smooth(0, 1, (t - t0) / (t1 - t0))
                # interpolate the settings, not the finished pose, so the hand follows its curved reach
                return self.key(**{f: k0.get(f, 0.) * (1 - w) + k1.get(f, 0.) * w for f in fields})
        return self.key()


def head_point(clip, p, P):
    """A point given in the head's bind space, in the chest's bind frame for pose p (hand IK targets
    are given in the chest frame), plus the head's rotation in that frame."""
    B = clip.B
    Rn = AN.euler(p['neck'])
    Rh = Rn @ AN.euler(p['head'])
    head = B[RG.NECK] + Rn @ (B[RG.HEAD] - B[RG.NECK])
    return Rh @ (np.asarray(P, float) - B[RG.HEAD]) + head, Rh


def bspline_reach(rest, c1, c2, end, u):
    """Hand path from rest to `end` (u in 0..1) along a quadratic B-spline with control points
    rest, c1, c2, end: two arcs that meet half-way between c1 and c2 with a shared tangent, so the
    hand never changes direction abruptly."""
    m = (c1 + c2) / 2
    if u < .5:
        a = u / .5
        return rest * (1 - a) ** 2 + c1 * 2 * a * (1 - a) + m * a * a
    a = (u - .5) / .5
    return m * (1 - a) ** 2 + c2 * 2 * a * (1 - a) + end * a * a


def bezier_reach(rest, side_lo, side_hi, c2, end, u):
    """Hand path from rest, out round the side of the cup, up, then in to `end` (u in 0..1).
    It runs as a B-spline over side_lo and c2, which keeps it smooth through the turn; side_hi (the
    old join point) is kept in the signature for the callers' readability."""
    return bspline_reach(rest, side_lo, c2, end, u)


def keyed(keys, t, duration, fields):
    """Interpolate keyed settings (smoothstep between keys) for a looping clip."""
    t = t % duration
    for (t0, k0), (t1, k1) in zip(keys[:-1], keys[1:]):
        if t0 <= t <= t1:
            w = smooth(0, 1, (t - t0) / (t1 - t0))
            return {f: k0.get(f, 0.) * (1 - w) + k1.get(f, 0.) * w for f in fields}
    return {f: 0. for f in fields}


def rest_hand(clip, side, s):
    return clip.B[RG.ARM[side]['hand']] + np.array([s * .04, .0, .015])      # relaxed, clear of the belly


# ---------------------------------------------------------------- the four mood clips
class DepressedWalk(AN.Dance):
    """Head hung low, shoulders dropped, a slow shuffle with the arms dangling."""
    name = 'Depressed Walk'
    duration = 1.6
    phases = [('Depressed Walk', 0, 1.6)]
    use_swivel = False
    stride, stance, lift = .24, .64, .022
    spring_k, spring_gain = .8, 1.1

    def sample(self, t):
        p = neutral(self)
        ph = (t / self.duration) % 1.0
        w = 2 * np.pi * ph
        p['feet'] = {side: gait(self, ph + (0 if side == 'L' else .5), self.B[RG.LEG[side]['foot']][0], self.stride,
                                self.stance, self.lift, -.08, .14, lift_early=.9) for side in 'LR'}
        p['shift'] = np.array([.028 * np.sin(w), -.050 + .008 * np.cos(2 * w), -.010])
        p['hips'] = np.array([.04, -.06 * np.sin(w), -.045 * np.sin(w)])
        p['spine'] = np.array([.20, .03 * np.sin(w), .015 * np.sin(w)])
        p['chest'] = np.array([.04, .05 * np.sin(w), 0])
        p['neck'] = np.array([.22, 0, 0])
        p['head'] = np.array([.30 + .03 * np.cos(2 * w), -.02 * np.sin(w), .05])     # nods with each heavy step
        lean = .04 + .20 + .04          # the chest's forward pitch; arms hang plumb from it
        for side, s in [('L', 1), ('R', -1)]:
            swing = -s * np.sin(w)
            p['fk'][side] = np.array([.11, .07 * swing + .02 - lean, .10])
            p['clav'][side] = -.06
            p['hrot'][side] = ('follow', .05)
        p['fingers'] = -.10
        return p


class SitCrossLegged(AN.Dance):
    """Step one foot across the other, sink down with the knees falling open, reach back and land
    heavily cross-legged on the floor; slump with the hooves on the knees and sigh, then lean
    push off the floor and rise back up on crossed feet and step out of it.

    Seated, the body leans back and the belly settles onto the thighs; the hem helper bones
    (rig.HEM, driven in anim.pose) let the front of the suit ride up over the lifted thighs."""
    name = 'Sit Cross-Legged'
    duration = 11.0
    phases = [('Sit Cross-Legged', 0, 11.0)]
    use_swivel = True
    spring_k, spring_gain = .8, 1.1
    KEYS = [(0.0, {}), (1.0, dict(cross=1)), (1.5, dict(cross=1, down=.12)),
            (2.3, dict(cross=1, down=.62, support=.5)), (2.75, dict(cross=1, down=1, support=1)),
            (3.6, dict(cross=1, down=1, support=1, slump=.3)), (4.5, dict(cross=1, down=1, lap=1, slump=1)),
            (7.4, dict(cross=1, down=1, lap=1, slump=1)), (8.2, dict(cross=1, down=1, support=1, slump=.3)),
            (9.1, dict(cross=1, down=.62, support=.5)), (9.7, dict(cross=1, down=.12)),
            (10.3, dict(cross=1)), (11.0, {})]
    FIELDS = ['cross', 'down', 'support', 'lap', 'slump']
    # seated: (x, z, extra height) of each ankle, the knee's target point, the foot's yaw and roll
    # (the right foot rests on the left shin, soles turned out)
    SEAT = {'L': ((-.06, .12, 0.), (.36, .13, -.06), -1.2, .9), 'R': ((.06, .20, .07), (-.36, .15, .0), 1.2, -.9)}
    # standing with the feet crossed: the right foot steps across in front of the left
    STAND = {'L': ((.08, -.02), .12), 'R': ((.0, .22), -.30)}
    DROP, BACK = .71, .30
    # seated, the hooves rest on the outside of the knees, elbows out clear of the belly
    LAP_OFF, LAP_POLE = (.10, .14, -.06), (1.0, .3, -.4)
    # reaching back, the hooves land beside and behind the hips (relative to the seated hips)
    SUPPORT, SUPPORT_POLE = (.34, .21, -.26), (.7, .7, -.5)

    def key(self, t, cross=0., down=0., support=0., lap=0., slump=0.):
        p = neutral(self)
        u = (t / self.duration) % 1.0
        sigh = np.sin(2 * np.pi * 3 * u) * slump
        k = smooth(.25, 1, down)                     # how far the feet and knees have gone to the seated pose
        fall = down * down * (3 - 2 * down)
        p['shift'] = np.array([.02 * cross * (1 - down), -self.DROP * fall - .004 * sigh + .012 * slump * down,
                               .03 * cross * (1 - down) - self.BACK * fall])
        # lowering, the body pitches forward to keep balance over the feet, then leans back on landing
        bal = np.sin(np.pi * min(down, 1.))
        p['hips'] = np.array([.30 * bal - .45 * fall, 0, 0])
        p['spine'] = np.array([.10 * bal + .12 * fall + .16 * slump, 0, 0])
        # the chest stays back as she slumps, so the cups don't fold down onto the belly
        p['chest'] = np.array([.04 * bal - .03 * fall - .03 * slump + .015 * sigh, 0, 0])
        p['neck'] = np.array([.05 * bal + .33 * fall + .10 * slump - .12 * bal * fall, 0, 0])
        p['head'] = np.array([.20 * fall + .20 * slump + .02 * sigh, .06 * slump * np.sin(2 * np.pi * u), .05 * slump])
        p['hem'] = 1.                                # the front hem rides up over the lifted thighs
        p['feet'] = {}
        Rh = AN.euler(p['hips'])
        for side, s in [('L', 1), ('R', -1)]:
            (sx, sz), syaw = self.STAND[side]
            rest = self.B[RG.LEG[side]['foot']]
            stand = np.array([rest[0] + (sx - rest[0]) * cross, 0, rest[2] + (sz - rest[2]) * cross])
            (cx, cz, lift), knee_at, yaw1, roll1 = self.SEAT[side]
            seat = np.array([cx, 0, cz])
            pos = stand * (1 - k) + seat * k
            yaw = syaw * cross * (1 - k) + yaw1 * k
            roll = roll1 * k
            # the top foot lifts over the other on its way across
            pos[1] = self.ankle_height(0., roll) + lift * k + (.09 * np.sin(np.pi * k) if lift else 0.)
            hip = Rh @ (self.B[RG.LEG[side]['thigh']] - self.B[RG.HIPS]) + self.B[RG.HIPS] + p['shift']
            knee_seat = AN.rot([0, 1, 0], -yaw) @ (np.array(knee_at) - hip)
            knee_seat /= np.linalg.norm(knee_seat)
            knee_mid = np.array([s * .75, -.1, .65])          # sinking, the knees fall open
            knee_stand = np.array([0, -.35, .8])
            knee = knee_stand * (1 - smooth(0, .5, down)) + knee_mid * smooth(0, .5, down)
            knee = knee * (1 - k) + knee_seat * k
            p['feet'][side] = {'pos': pos, 'pitch': 0., 'yaw': yaw, 'roll': roll, 'knee': tuple(knee)}
        p.pop('fk')
        p['hand'], p['pole'], p['hand_world'], p['pole_world'], p['world_w'], p['hand_joint'] = {}, {}, {}, {}, {}, {}
        for side, s in [('L', 1), ('R', -1)]:
            p['hand'][side] = rest_hand(self, side, s)
            p['pole'][side] = self.B[RG.ARM[side]['fore']] + np.array([s * .25, 0, -.15])
            if lap > 1e-6:
                p['hand_joint'][side] = (RG.LEG[side]['shin'], np.array(self.LAP_OFF) * [s, 1, 1],
                                         np.array(self.LAP_POLE) * [s, 1, 1], lap)
            if support > 1e-6:
                # hooves planted on the floor beside and behind the hips
                p['hand_world'][side] = np.array(self.SUPPORT) * [s, 1, 1] - [0, 0, self.BACK]
                p['pole_world'][side] = np.array(self.SUPPORT_POLE) * [s, 1, 1] - [0, 0, self.BACK]
                p['world_w'][side] = support
            p['hrot'][side] = ('follow', .12)
            p['clav'][side] = .06 * bal - .04 * slump
        p['fingers'] = -.2
        return p

    def sample(self, t):
        return self.key(t, **keyed(self.KEYS, t, self.duration, self.FIELDS))


class Crying(AN.Dance):
    """Hunch over, hooves up to the mask's eyes, sob with shaking shoulders, then lower them."""
    name = 'Crying'
    duration = 7.0
    phases = [('Crying', 0, 7.0)]
    use_swivel = True
    spring_k, spring_gain = .8, 1.1
    KEYS = [(0.0, {}), (1.0, dict(face=1, hunch=1, sob=.3)), (1.4, dict(face=1, hunch=1, sob=1)),
            (5.0, dict(face=1, hunch=1, sob=.8)), (5.9, dict(hunch=.8, sob=.3)), (7.0, {})]
    FIELDS = ['face', 'hunch', 'sob']

    def key(self, t, face=0., hunch=0., sob=0.):
        p = neutral(self)
        shudder = sob * (.6 * np.sin(2 * np.pi * 2.6 * t) + .4 * np.sin(2 * np.pi * 4.1 * t + 1.))
        gulp = sob * np.abs(np.sin(2 * np.pi * .9 * t)) ** 6           # catching the breath
        p['shift'] = np.array([0, -.030 * hunch + .005 * shudder + .006 * gulp, -.010 * hunch])
        p['spine'] = np.array([.18 * hunch, 0, 0])
        p['chest'] = np.array([.04 * hunch + .025 * shudder - .03 * gulp, 0, 0])
        p['neck'] = np.array([.16 * hunch, 0, 0])
        p['head'] = np.array([.20 * hunch + .035 * shudder - .04 * gulp, .06 * sob * np.sin(2 * np.pi * .45 * t), .05 * hunch])
        p.pop('fk')
        p['hand'], p['pole'] = {}, {}
        for side, s in [('L', 1), ('R', -1)]:
            eye, Rh = head_point(self, p, [s * .050, 1.522, .135])
            # the hoof plates reach ~21 cm past the wrist: hold the wrist that far out, below the eye
            wrist, _ = head_point(self, p, np.array([s * .050, 1.522, .135]) + .213 * np.array([s * .05, -.79, .61]))
            rest = rest_hand(self, side, s)
            tgt = bezier_reach(rest, np.array([s * .44, 1.12, .06]), np.array([s * .34, 1.36, .30]),
                               np.array([s * .20, 1.38, .36]), wrist, face)
            p['hand'][side] = tgt
            p['pole'][side] = (self.B[RG.ARM[side]['fore']] + np.array([s * .25, 0, -.15])) * (1 - face) + np.array([s * .62, 1.0, .05]) * face
            on_face = self.hand_rot(side, eye - wrist, Rh @ np.array([0, 0, -1.]))
            p['hrot'][side] = ('blend', ('follow', .12), on_face, smooth(.6, 1, face))
            p['clav'][side] = .04 * hunch + .05 * shudder + .04 * gulp
        p['fingers'] = -.3 * face
        return p

    def sample(self, t):
        return self.key(t % self.duration, **keyed(self.KEYS, t, self.duration, self.FIELDS))


class Exasperated(AN.Dance):
    """Arms flung out palms-up with the head thrown back, a heavy drop of the arms with a slap on the
    hips and a head shake, then a face-palm with a slow shake inside the hoof."""
    name = 'Exasperated'
    duration = 6.5
    phases = [('Exasperated', 0, 6.5)]
    use_swivel = True
    spring_k, spring_gain = .8, 1.1
    KEYS = [(0.0, {}), (.55, dict(fling=1, back=1)), (1.3, dict(fling=1, back=.8)),
            (1.7, dict(slap=1, slump=.6)), (2.0, dict(slap=1, slump=.8, shake=1)), (2.9, dict(slap=.6, slump=.7, shake=1)),
            (3.6, dict(palm=1, slump=.5)), (4.9, dict(palm=1, slump=.6, shake=.6)), (5.6, dict(slump=.3)), (6.5, {})]
    FIELDS = ['fling', 'back', 'slap', 'palm', 'shake', 'slump']

    def key(self, t, fling=0., back=0., slap=0., palm=0., shake=0., slump=0.):
        p = neutral(self)
        p['shift'] = np.array([0, -.012 * slump - .008 * fling, -.012 * back])
        p['spine'] = np.array([-.05 * back + .08 * slump, 0, 0])
        p['chest'] = np.array([-.06 * back + .06 * slump, 0, 0])
        yaw = .26 * shake * np.sin(2 * np.pi * 2.0 * t)
        p['neck'] = np.array([-.22 * back + .10 * slump + .10 * palm, .4 * yaw, 0])
        p['head'] = np.array([-.28 * back + .12 * slump + .12 * palm, .6 * yaw, .03 * slump])
        p.pop('fk')
        p['hand'], p['pole'] = {}, {}
        for side, s in [('L', 1), ('R', -1)]:
            rest = rest_hand(self, side, s)
            pole_rest = self.B[RG.ARM[side]['fore']] + np.array([s * .25, 0, -.15])
            out = np.array([s * .50, 1.22, .24])                    # flung out to the side, palm up
            hip = rest + np.array([s * .025, .02, -.01])            # dropped onto the hips
            tgt = rest * (1 - fling - slap) + out * fling + hip * slap
            pole = pole_rest * (1 - fling) + np.array([s * .55, .85, -.30]) * fling
            hr = ('blend', ('follow', .12), self.hand_rot(side, [s * .55, .05, .55], [0, 1, 0]), fling)
            if side == 'R' and palm > 0:
                brow, Rh = head_point(self, p, [-.015, 1.575, .115])
                wrist, _ = head_point(self, p, np.array([-.015, 1.575, .115]) + .222 * np.array([-.15, -.62, .77]))
                tgt = bezier_reach(tgt, np.array([s * .44, 1.12, .04]), np.array([s * .36, 1.42, .20]),
                                   np.array([s * .16, 1.52, .36]), wrist, palm)
                pole = pole * (1 - palm) + np.array([s * .60, 1.15, -.05]) * palm
                hr = ('blend', hr, self.hand_rot(side, brow - wrist, Rh @ np.array([0, 0, -1.])), smooth(.6, 1, palm))
            p['hand'][side], p['pole'][side], p['hrot'][side] = tgt, pole, hr
            p['clav'][side] = .10 * fling - .05 * slump
        p['fingers'] = .15 * fling - .2 * palm
        return p

    def sample(self, t):
        return self.key(t % self.duration, **keyed(self.KEYS, t, self.duration, self.FIELDS))


# ---------------------------------------------------------------- the alt (lumbering) set
SLOW = 1.25         # alt clips play 25 % slower


def lumber(clip, p, q, u):
    """Re-voice a pose: slumped with the neck forward but eyes level, dropped shoulders, heavier sway, upper body trailing
    the hips (q is the same clip sampled a moment earlier), arms hanging plumb, feet dragging."""
    T = clip.duration
    breath = np.sin(2 * np.pi * u * max(1, round(T / 3.5)))
    for k in ('chest', 'neck', 'head'):
        p[k] = np.asarray(q[k], float).copy()
    nh = 0.
    for side in p.get('hand', {}):
        nh = max(nh, smooth(.26, .14, np.linalg.norm(np.asarray(p['hand'][side]) - [0, 1.55, .12])))
    # the slouch bends the lower spine; the chest stays over it so the cups don't tip onto the belly
    p['spine'] = np.asarray(p['spine'], float) + [.08, 0, 0]
    p['chest'] = p['chest'] + [.01 + .012 * breath, 0, 0]
    # the neck juts forward with the slump, but the head tips back up so the eyes stay level and she
    # can see where she is going (spine .08 + chest .01 + neck .04 - head .12 = level gaze)
    p['neck'] = p['neck'] + [.04 * (1 - nh), 0, 0]
    p['head'] = p['head'] + [-.12 * (1 - nh), 0, .035 * (1 - nh)]
    p['hips'] = np.asarray(p['hips'], float) * [1, 1, 1.4]
    sh = np.asarray(p['shift'], float)
    p['shift'] = np.array([1.4 * sh[0], .7 * sh[1] - .014 - .004 * (.5 + .5 * breath), sh[2]])
    p['clav'] = {s: .8 * v - .04 for s, v in p['clav'].items()}
    lean = .09 + .012 * breath
    for side, (abd, flex, bend) in list(p.get('fk', {}).items()):
        p['fk'][side] = np.array([abd if abd < .6 else .9 * abd, .65 * flex - lean, .8 * bend + .05])
    for side in p.get('hand', {}):
        p['hand'][side] = np.asarray(p['hand'][side], float) + [0, -.012, 0]
    p['fingers'] = .8 * p['fingers']; p['thumb'] = .8 * p['thumb']
    if p.get('feet'):
        feet = {}
        for side, ft in p['feet'].items():
            pitch = .75 * ft['pitch']
            pos = np.array(ft['pos'], float)
            pos[1] = clip.ankle_height(pitch) + .62 * (pos[1] - clip.ankle_height(ft['pitch']))
            feet[side] = dict(ft, pos=pos, pitch=pitch)
        p['feet'] = feet
    return p


def lumbering(Base, slow=SLOW, lag=.07):
    class Alt(Base):
        __doc__ = f'{Base.name}, played heavy and lumbering.'
        name = Base.name + ' (alt)'
        duration = Base.duration * slow
        phases = [(n, a * slow, b * slow) for n, a, b in Base.phases]
        # softer, swingier springs; the dance's deep Wiggle squat keeps the standard ones so the
        # belly doesn't bounce up into the teats
        spring_k, spring_gain = (1., 1.) if Base is AN.Dance else (.85, 1.1)

        def sample(self, t):
            tb = (t % self.duration) / slow
            self.duration = Base.duration          # the base clip reads its own loop length
            try:
                p = Base.sample(self, tb)
                q = Base.sample(self, (tb - lag) % Base.duration)
            finally:
                del self.duration
            return lumber(self, p, q, tb / Base.duration)
    Alt.__name__ = Base.__name__ + 'Alt'
    return Alt


BASE = [AN.Dance, Idle, Walk, Run, Sneak, JumpingJacks, LookAround]
MOOD = [DepressedWalk, SitCrossLegged, Crying, Exasperated]
ALT = [lumbering(C) for C in BASE]
ALL = BASE + MOOD + ALT
ORDER = (['Idle', 'Walk', 'Run', 'Sneak', 'Jumping Jacks', 'Look Around', 'Chicken Dance']
         + [C.name for C in MOOD]
         + [n + ' (alt)' for n in ['Idle', 'Walk', 'Run', 'Sneak', 'Jumping Jacks', 'Look Around', 'Chicken Dance']])
