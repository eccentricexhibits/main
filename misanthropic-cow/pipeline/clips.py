"""Animation library for the v10 cow, built on the generic solver in anim.py.

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
                head=np.zeros(3), fingers=0., thumb=0., clav={'L': 0., 'R': 0.},
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
            side_hi = np.array([s * .40, 1.52, .04])
            if shade < .5:
                u = shade / .5
                c1 = np.array([s * .47, 1.12, -.02])
                tgt = rest * (1 - u) ** 2 + c1 * 2 * u * (1 - u) + side_hi * u * u
            else:
                u = (shade - .5) / .5
                c2 = neck + rot([0, 1, 0], yaw) @ (np.array([s * .24, 1.66, .20]) - neck)
                tgt = side_hi * (1 - u) ** 2 + c2 * 2 * u * (1 - u) + brow * u * u
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


ALL = [AN.Dance, Idle, Walk, Run, Sneak, JumpingJacks, LookAround]
