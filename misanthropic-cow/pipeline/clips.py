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
import design as D
import rig as RG

rot = AN.rot
smooth = AN.smooth


def neutral(clip):
    return dict(shift=np.zeros(3), hips=np.zeros(3), spine=np.zeros(3), chest=np.zeros(3), neck=np.zeros(3),
                head=np.zeros(3), fingers=-.12, thumb=.10, spread=0., clav={'L': 0., 'R': 0.},    # hooves and thumb relaxed, a little curled
                fk={'L': np.array([0., 0., 0.]), 'R': np.array([0., 0., 0.])},
                hrot={'L': relaxed_hand(clip, 'L'), 'R': relaxed_hand(clip, 'R')}, feet=None)


# round 41: a relaxed hand hangs: the fingers (and the hoof toes) turn from the forearm's line most of the way towards
# straight down; round 18-40's ('follow', .12) tipped each hand forward at the wrist, so with the A-pose's forearms the
# hooves pointed out and forward, and up as an arm swung forward (the owner's note).
# Round 42: further down (round 41: 60 % of the way, at most 55 degrees; the owner: "still angled upwards too much"), and
# as a fixed wrist pose relative to the forearm: the hang worked out once for the resting arm (REST_ARM), to a little behind straight down.  Round 41
# recomputed it every frame from the forearm's direction, which swings fast as an arm lifts, and between that and a set
# pose (the Exasperated fling's palms-up, a hoof at the face) the hand could take the other way round and flip half a
# turn in a frame (the owner's "glitch on the left arm").
RELAXED_HANG, RELAXED_MAX = .95, np.deg2rad(70.)
RELAXED_TWIST = float(__import__('os').environ.get('COW_RELAXED_TWIST', .35))   # round 45: the forearm's inward turn (rad)
RELAXED_DIR = (0., -1., -.27)    # where the relaxed hand's line points: down, 15 degrees back (the hoof itself curves forward)
RELAXED_HAND = ('hang', .6)      # round 41's (kept for reference; the clips use relaxed_hand)


def relaxed_hand(clip, side):
    """The relaxed hand as an ('local', R) wrist pose for anim.Dance.pose (cached per clip)."""
    cache = clip.__dict__.setdefault('_relaxed', {})
    if side not in cache:
        s = 1 if side == 'L' else -1
        a = RG.ARM[side]; B = clip.B
        bu0 = B[a['fore']] - B[a['upper']]; bf0 = B[a['hand']] - B[a['fore']]
        hinge0 = np.cross(bu0, bf0); hinge0 /= np.linalg.norm(hinge0)
        abd, flex, bend = REST_ARM
        Rf = rot([0, 0, 1], s * abd) @ rot([1, 0, 0], -flex) @ rot(hinge0, clip.flex_sign[side] * bend)
        fdir = Rf @ (bf0 / np.linalg.norm(bf0))
        down = np.asarray(RELAXED_DIR) / np.linalg.norm(RELAXED_DIR)
        ax = np.cross(fdir, down); sn = np.linalg.norm(ax)
        ang = min(RELAXED_HANG * np.arctan2(sn, fdir @ down), RELAXED_MAX)
        # round 45: the forearm turned in a little (RELAXED_TWIST), so the backs of the hooves face out and forward and
        # the palms in towards the thighs, as a relaxed hand hangs (round 41-44: square to the side)
        bfn = bf0 / np.linalg.norm(bf0)
        cache[side] = ('local', rot(Rf.T @ (ax / sn), ang) @ rot(bfn, -s * RELAXED_TWIST))
    return cache[side]


def local_hand(clip, side, Rhand, hand, pole, clav=0.):
    """Round 42: see anim.Dance.local_hand (the Exasperated fling and face-palm, the Idle's hoof check)."""
    return clip.local_hand(side, Rhand, hand, pole, clav)

REST_ARM = (-.07, -.03, .40)    # round 39: the relaxed arm, as FK (abduction, flexion, elbow bend) from the bind pose;
#                                 round 45: the elbow softly bent (23 degrees; round 39-44: 8, which looked stiff, "like a
#                                 mannequin" again to the owner: "very stiff and awkward"), the upper arm a touch behind


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


def drop_curve(t, drop, bump_cfg):
    """Round 42: a hand let go (drop: start, length) falls under its own weight: slow to leave, gathering speed as it
    falls, so it arrives moving and bumps out off the belly's side, settling in a couple of small swings
    (bump_cfg: out, forward (m), Hz, decay (s)).  Returns (path share still to go 1..0, hoof turn share 1..0 (the hoof
    trails the arm), landing envelope, bump offset (out, forward), fall progress 0..1)."""
    t0, T = drop
    tau = np.clip((t - t0) / T, 0, 1)
    u = 1 - tau * tau * (2 - tau)
    turn = 1 - smooth(.04, .90, tau)
    dt = t - (t0 + T)
    out, fwd, f, dec = bump_cfg
    bump = np.zeros(2)
    land = 0.
    if dt > 0:
        e = np.exp(-dt / dec) * (1 - smooth(.55, .9, dt))      # gone within a second
        bump = np.array([out * e * np.sin(2 * np.pi * f * dt),
                         fwd * e * np.sin(2 * np.pi * .8 * f * dt + .9) - fwd * np.sin(.9) * np.exp(-dt / .08)])
        land = np.exp(-((dt - .12) / .22) ** 2)
    return u, turn, land, bump, tau


def fk_pole(clip, side, abd, flex, bend):
    """The elbow pole (chest's bind frame) anim.Dance.pose uses for these FK angles, so an IK arm can match an FK one."""
    s = 1 if side == 'L' else -1
    a = RG.ARM[side]; B = clip.B
    bu0 = B[a['fore']] - B[a['upper']]; bf0 = B[a['hand']] - B[a['fore']]
    hinge0 = np.cross(bu0, bf0); hinge0 /= np.linalg.norm(hinge0)
    Rl = rot([0, 0, 1], s * abd) @ rot([1, 0, 0], -flex)
    sh = B[a['upper']]
    el = sh + Rl @ bu0
    wr = el + Rl @ rot(hinge0, clip.flex_sign[side] * bend) @ bf0
    mid = sh + (wr - sh) * (((el - sh) @ (wr - sh)) / ((wr - sh) @ (wr - sh)))
    off = el - mid
    if np.linalg.norm(off) < 2e-3:
        off = Rl @ np.cross(hinge0, bu0)
    return el + .3 * off / np.linalg.norm(off)


class Idle(AN.Dance):
    """Standing about, 15.6 s (round 45; round 42-44: 20 s with a hoof check, round 39: 8 s).  She settles onto one leg;
    heaves a long, bored sigh; gives the room a slow side-eye down her nose with a little shake of the head; shifts her
    weight and taps a foot, waiting; and rolls her eyes (the head circles up and round) before settling back.  The
    performance layer adds the breathing and a slow sway, gentler than the other clips' (the owner: "too much
    wiggling").  Round 45: the hoof check is gone (the owner: "can we remove the hand checking animation"), and the
    arms hang more loosely (REST_ARM, and IDLE_ARMS: the two arms not mirror images)."""
    name = 'Idle'
    duration = 15.6
    phases = [('Settle', 0, 3.0), ('Sigh', 3.0, 6.0), ('Side-eye', 6.0, 9.6), ('Foot tap', 9.6, 13.0), ('Eye roll', 13.0, 15.6)]
    use_swivel = False
    NOISE_SCALE = .4                # round 42: the slow drift at 40 % (round 39: the same as the other clips)
    BREATH = .4
    # (time, settings): weight > 0 on the left leg (the character's), glance > 0 to her left, nose > 0 chin up,
    # inhale / slump the sigh, tap the left foot's taps
    KEYS = [(0.0, dict(weight=-.15)), (1.6, dict(weight=.8)), (3.0, dict(weight=.75)),
            (3.9, dict(weight=.7, inhale=1.)), (4.2, dict(weight=.7, inhale=1.)), (5.3, dict(weight=.65, slump=1.)),
            (6.0, dict(weight=.6, slump=.5)),
            (6.9, dict(weight=.55, glance=-.85, nose=.7, slump=.2)), (7.9, dict(weight=.5, glance=-.9, nose=.75)),
            (8.6, dict(weight=-.1, glance=-.3, nose=.4, shake=1.)), (9.4, dict(weight=-.55, glance=0., nose=.1)),
            (10.0, dict(weight=-.85, nose=.25, glance=.15)), (10.2, dict(weight=-.85, nose=.25, glance=.15, tap=1.)),
            (12.2, dict(weight=-.85, nose=.3, glance=.2, tap=1.)), (12.6, dict(weight=-.7, nose=.2)),
            (13.0, dict(weight=-.6)), (14.5, dict(weight=-.45, roll=1.)), (15.6, dict(weight=-.15))]
    FIELDS = ['weight', 'glance', 'nose', 'inhale', 'slump', 'shake', 'tap', 'roll']
    ARM_REST = REST_ARM             # the arms' (abduction, forward flexion, elbow bend) from the bind pose
    IDLE_ARMS = {'L': (0., -.02, .07), 'R': (.02, .03, -.04)}   # round 45: each arm's own offset from it (not mirror images)
    TAPS = (10.35, 12.05, 4)        # the foot taps: from, to, how many

    def key(self, t, weight=0., glance=0., nose=0., inhale=0., slump=0., shake=0., tap=0., roll=0.):
        p = neutral(self)
        w = weight
        # the eye roll: the head tips up, round to one side and back down (roll 0..1 through the circle)
        r = np.clip(roll, 0, 1)
        er = np.array([-.20 * np.sin(np.pi * r) ** 1.5, .14 * np.sin(2 * np.pi * r), -.08 * np.sin(2 * np.pi * r)]) * smooth(0, .15, r) * (1 - smooth(.85, 1., r))
        sh = .16 * shake * np.sin(2 * np.pi * 1.6 * t)          # a slow "tsk" shake
        # the hips move over the standing leg and drop on the free side, so its knee eases; the chest tilts back
        # against them, and the whole body sits a little lower so the standing leg is never at full stretch
        p['shift'] = np.array([.024 * w, -.006 - .008 * abs(w) + .004 * inhale - .010 * slump, -.004 * abs(w)])
        p['hips'] = np.array([.01, -.06 * w, .055 * w])
        p['spine'] = np.array([.015 + .04 * slump - .02 * inhale, .03 * w, -.035 * w])
        p['chest'] = np.array([.0 - .05 * inhale + .05 * slump, .02 * w + .10 * glance, -.025 * w])
        p['neck'] = np.array([.02 - .12 * nose + .05 * slump - .03 * inhale, .25 * glance + .4 * sh, .0]) + .4 * er
        p['head'] = np.array([-.01 - .14 * nose + .06 * slump - .04 * inhale, .45 * glance + .6 * sh,
                              -.05 * w + .06 * nose * np.sign(glance or 1)]) + .6 * er
        # the foot taps: the free (left) foot's toe comes up and slaps down, a quick lift and a quicker drop
        taps = 0.
        if tap > 0:
            t0, t1, n = self.TAPS
            ph = np.clip((t - t0) / (t1 - t0), 0, 1) * n % 1.
            taps = tap * np.sin(np.pi * min(ph / .62, 1.)) ** 2 if ph < .62 else 0.
        p['feet'] = {}
        for side in 'LR':
            pitch = -.24 * taps if side == 'L' else 0.
            pos = self.B[RG.LEG[side]['foot']].copy()
            pos[1] += self.ankle_height(pitch) - self.ankle_height(0.)
            p['feet'][side] = {'pos': pos, 'pitch': pitch, 'yaw': 0.}
        for side, s in [('L', 1), ('R', -1)]:
            load = max(0., s * w)                 # the arm on the standing side hangs a little further out
            a, f, b = np.add(self.ARM_REST, self.IDLE_ARMS[side])
            # the arm on the free side swings a little forward with the hips; the elbows sag as she slumps
            p['fk'][side] = np.array([a + .03 * load, f + .03 * (1 - load) - .04 * inhale + .03 * slump, b + .05 * (1 - load) + .08 * slump])
            p['clav'][side] = -.03 - .02 * load + .05 * inhale - .05 * slump
        return p

    def sample(self, t):
        return self.key(t % self.duration, **keyed(self.KEYS, t, self.duration, self.FIELDS))


class Walk(AN.Dance):
    name = 'Walk'
    SYNC = 'phase'          # round 43: a gait, its loop starting at the left heel strike (blend at the same phase)
    duration = 1.12
    phases = [('Walk', 0, 1.12)]
    use_swivel = False
    STABILIZE = .6         # round 39: the head floats over the step instead of nodding with it
    ARM_ABD = -.02         # how far out the arms swing, from the bind pose's 34 degrees (round 39; round 38: .17, 44 degrees)
    stride, stance, lift = .36, .60, .055

    def sample(self, t):
        p = neutral(self)
        ph = (t / self.duration) % 1.0
        w = 2 * np.pi * ph
        p['feet'] = {'L': gait(self, ph, self.B[RG.LEG['L']['foot']][0], self.stride, self.stance, self.lift),
                     'R': gait(self, ph + .5, self.B[RG.LEG['R']['foot']][0], self.stride, self.stance, self.lift)}
        # round 39: lowest just after each heel strike (both feet down, the weight landing), highest passing over the
        # standing leg; round 18 had it the other way round.  The landing dips a little sharper than the rise.
        land = 2 * np.pi * ((2 * ph + .94) % 1.0)
        p['shift'] = np.array([.022 * np.sin(w), -.045 - .010 * np.cos(land) - .004 * np.cos(2 * land), .0])
        p['hips'] = np.array([.0, -.10 * np.sin(w), -.035 * np.sin(w)])
        p['spine'] = np.array([.03, .05 * np.sin(w), .02 * np.sin(w)])
        p['chest'] = np.array([.02, .08 * np.sin(w), 0])
        p['head'] = np.array([-.02, -.03 * np.sin(w), .015 * np.sin(w)])
        for side, s in [('L', 1), ('R', -1)]:
            swing = -s * np.sin(w)               # arm swings opposite its own leg
            # round 45: the elbows a little softer (.32; round 39-44: .22)
            p['fk'][side] = np.array([self.ARM_ABD, .30 * swing + .05, .32 + .12 * max(0, swing)])
        return p


class Run(AN.Dance):
    name = 'Run'
    SYNC = 'phase'          # round 43: a gait, its loop starting at the left heel strike (blend at the same phase)
    duration = .72
    phases = [('Run', 0, .72)]
    use_swivel = False
    STABILIZE = .5
    stride, stance, lift = .52, .42, .16
    # round 42: the arms in closer to the sides (.47 until round 41; the owner: "less out to the side"); the palm still
    # clears the cup at the front of the pump
    ARM_ABD, ARM_ABD_FWD = .22, 0.

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
        p['hem'] = 1.          # round 38: the round 37 belly hangs lower; its front rides up over the high knee
        for side, s in [('L', 1), ('R', -1)]:
            swing = -s * np.sin(w)
            # abducted enough that the glove's palm clears the cup at the front of the pump
            p['fk'][side] = np.array([self.ARM_ABD + self.ARM_ABD_FWD * max(0., swing), .42 * swing + .05, 1.15 + .15 * swing])
            p['hrot'][side] = ('follow', .2)
        p['fingers'] = -.6; p['thumb'] = .4
        return p


class Sneak(AN.Dance):
    """Cartoon tiptoe: crouched, high knees, pointed toes, hooves dangling in front of the chest."""
    name = 'Sneak'
    SYNC = 'phase'          # round 43: a gait, its loop starting at the left heel strike (blend at the same phase)
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
        p['hem'] = 1.          # round 38: as in Run
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
    ARM_ABD = -.04         # the arms at the bottom of each jack, from the bind pose; they reach 2.5 rad up (round 38: .10)

    def sample(self, t):
        p = neutral(self)
        # round 39: no two jacks alike: the timing drifts a little within the 4 s loop (a smooth, always-forward warp
        # of time) and each jack reaches a little higher or lower with the arms and feet, tiring towards the third
        u = 2 * np.pi * t / self.duration
        tw = t + .045 * np.sin(u + .4) + .02 * np.sin(2 * u + 1.9)
        ph = tw % 1.0
        reach = 1 - .05 * (.5 - .5 * np.cos(u - 3.4)) + .015 * np.sin(3 * u + .7)
        open_ = (.5 - .5 * np.cos(2 * np.pi * ph))
        air = abs(np.sin(2 * np.pi * ph)) ** 1.3          # airborne mid-transition, landing at open/closed
        land = (1 - abs(np.sin(2 * np.pi * ph))) ** 6
        p['shift'] = np.array([0, -.035 + .075 * air - .045 * land, 0])
        p['spine'] = np.array([.02 * land, 0, 0])
        p['head'] = np.array([-.04 * open_, 0, 0])
        p['feet'] = {}
        for side, s in [('L', 1), ('R', -1)]:
            pitch = .30 * air
            x = self.B[RG.LEG[side]['foot']][0] + s * .17 * open_ * (.97 + .03 * reach + .02 * s * np.sin(u + 2.2))
            p['feet'][side] = {'pos': np.array([x, self.ankle_height(pitch) + .075 * air, -.022]), 'pitch': pitch, 'yaw': s * .12 * open_}
            p['fk'][side] = np.array([self.ARM_ABD + (2.50 * reach - .04 * s * np.sin(u) - self.ARM_ABD) * open_, .26 * open_, .10 + .15 * (1 - open_)])
            p['clav'][side] = .22 * open_
            p['hrot'][side] = ('follow', .1)
        return p


class LookAround(AN.Dance):
    """Turn to look left and right with a hoof shading the eyes, look up, then lean in and peer."""
    name = 'Look Around'
    duration = 6.0
    phases = [('Look Around', 0, 6.0)]
    use_swivel = True
    # round 39: the eyes and head lead each look and the body follows, slower (the brow-shading hooves keep their paths)
    MOTION = {'spine': (1.8, .70), 'chest': (2.2, .65), 'neck': None, 'head': None, 'hand': None}

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
            rest = rest_hand(self, side, s)                    # relaxed, against the belly's side (round 39)
            pole_rest = self.B[RG.ARM[side]['fore']] + np.array([s * .25, 0, -.15])
            brow = neck + rot([0, 1, 0], yaw) @ (np.array([s * .035, 1.585, .25]) - neck)
            # out and up at the side first (clear of the cup), then in over the brow (clear of the muzzle)
            c1 = np.array([s * .47, 1.12, -.02])
            c2 = neck + rot([0, 1, 0], yaw) @ (np.array([s * .24, 1.66, .20]) - neck)
            tgt = bspline_reach(rest, c1, c2, brow, shade)
            p['hand'][side] = tgt + np.array([0, 0, .02 * lean]) * (1 - shade)
            p['pole'][side] = pole_rest * (1 - shade) + np.array([s * .60, 1.40, -.12]) * shade
            flat = self.hand_rot(side, rot([0, 1, 0], yaw) @ np.array([-s, .12, .30]), [0, -1, 0])
            p['hrot'][side] = ('blend', relaxed_hand(self, side), flat, smooth(.55, 1, shade))   # turn the hoof flat only near the brow
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


def fk_wrist(clip, side, abd, flex, bend):
    """Where the wrist is (chest's bind frame) with the arm at these FK angles, as anim.Dance.pose places it."""
    s = 1 if side == 'L' else -1
    a = RG.ARM[side]; B = clip.B
    bu0 = B[a['fore']] - B[a['upper']]; bf0 = B[a['hand']] - B[a['fore']]
    hinge0 = np.cross(bu0, bf0); hinge0 /= np.linalg.norm(hinge0)
    Rl = rot([0, 0, 1], s * abd) @ rot([1, 0, 0], -flex)
    return B[a['upper']] + Rl @ bu0 + Rl @ rot(hinge0, clip.flex_sign[side] * bend) @ bf0


def rest_hand(clip, side, s):
    # round 39: the arm hanging against the belly's side (REST_ARM); round 38 held the hand 4 cm further out than the
    # model's own A-pose, about 40 degrees from the body
    return fk_wrist(clip, side, *REST_ARM)


# ---------------------------------------------------------------- the four mood clips
class DepressedWalk(AN.Dance):
    """Head hung low, shoulders dropped, a slow shuffle with the arms dangling."""
    name = 'Depressed Walk'
    SYNC = 'phase'          # round 43: a gait, its loop starting at the left heel strike (blend at the same phase)
    duration = 1.6
    phases = [('Depressed Walk', 0, 1.6)]
    use_swivel = False
    STABILIZE = .35
    ARM_ABD = -.02         # round 39 (round 38: .11)
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
            p['fk'][side] = np.array([self.ARM_ABD, .07 * swing + .02 - lean, .10])
            p['clav'][side] = -.06
            p['hrot'][side] = ('hang', .7)               # round 41: the dangling hands hang under gravity
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
    DROP, BACK = .71 + D.LEG_LIFT, .30         # the hips land as low as before: the legs are longer
    # seated, the hooves rest on the outside of the knees, elbows out clear of the belly
    LAP_OFF, LAP_POLE = (.10, .14, -.06), (1.0, .3, -.4)
    # reaching back, the hooves land beside and behind the hips (relative to the seated hips)
    SUPPORT, SUPPORT_POLE = (.34, .21, -.26), (.7, .7, -.5)
    BELLY_SEAT_LIFT = (0., 0., 0.)               # how far the belly rides up on the legs once seated (round 38: 3 cm took 0.7 mm
    #                                            off the hem on the legs but pushed the belly 15 mm up into the teats)

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
        # round 38: seated, the stuffed belly rides up onto the crossed legs (the Belly bone; spine frame)
        p['belly_lift'] = np.array(self.BELLY_SEAT_LIFT) * fall
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
            p['hrot'][side] = relaxed_hand(self, side)
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
    MOTION = {'neck': None, 'head': None, 'hand': None}      # round 39: the hooves stay on the eyes
    spring_k, spring_gain = .8, 1.1
    KEYS = [(0.0, {}), (1.0, dict(face=1, hunch=1, sob=.3)), (1.4, dict(face=1, hunch=1, sob=1)),
            (5.0, dict(face=1, hunch=1, sob=.8)), (5.9, dict(hunch=.8, sob=.3)), (7.0, {})]
    FIELDS = ['face', 'hunch', 'sob']
    FACE_POLE = (.62, 1.15, .05)         # where the elbows point with the hooves at the eyes
    WRIST_DIR = (.15, -.5, .85)          # from the eye to the wrist (head frame)

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
            # the hoof toes reach 19 cm past the wrist: hold the wrist that far out (and 1.5 cm more), below the eye
            wd = np.array(self.WRIST_DIR) * [s, 1, 1]; wd = wd / np.linalg.norm(wd)
            wrist, _ = head_point(self, p, np.array([s * .050, 1.522, .135]) + .206 * wd)
            rest = rest_hand(self, side, s)
            tgt = bezier_reach(rest, np.array([s * .44, 1.12, .06]), np.array([s * .34, 1.36, .30]),
                               np.array([s * .20, 1.38, .36]), wrist, face)
            p['hand'][side] = tgt
            p['pole'][side] = (self.B[RG.ARM[side]['fore']] + np.array([s * .25, 0, -.15])) * (1 - face) + np.array(self.FACE_POLE) * [s, 1, 1] * face
            on_face = self.hand_rot(side, eye - wrist, Rh @ np.array([0, 0, -1.]))
            p['hrot'][side] = ('blend', relaxed_hand(self, side), on_face, smooth(.6, 1, face))
            p['clav'][side] = .04 * hunch + .05 * shudder + .04 * gulp
        p['fingers'] = -.3 * face
        return p

    def sample(self, t):
        return self.key(t % self.duration, **keyed(self.KEYS, t, self.duration, self.FIELDS))


class Exasperated(AN.Dance):
    """Arms flung out palms-up with the head thrown back, a heavy drop of the arms with a slap on the
    hips and a head shake, then a face-palm with a slow shake inside the hoof; the head comes up out of
    the hoof and the arm drops away under its own weight, bumps against the side and settles."""
    name = 'Exasperated'
    duration = 6.5
    phases = [('Exasperated', 0, 6.5)]
    use_swivel = True
    MOTION = {'neck': None, 'head': None, 'hand': None}      # round 39: the face-palm stays on the brow
    spring_k, spring_gain = .8, 1.1
    KEYS = [(0.0, {}), (.55, dict(fling=1, back=1)), (1.3, dict(fling=1, back=.8)),
            (1.7, dict(slap=1, slump=.6)), (2.0, dict(slap=1, slump=.8, shake=1)), (2.9, dict(slap=.6, slump=.7, shake=1)),
            (3.6, dict(palm=1, slump=.5)), (4.9, dict(palm=1, slump=.6, shake=.6)), (5.05, dict(palm=1, slump=.55)),
            (5.9, dict(slump=.3)), (6.5, {})]
    FIELDS = ['fling', 'back', 'slap', 'palm', 'shake', 'slump']
    PALM_POLE = (.60, 1.30, -.05)        # where the right elbow points in the face-palm (round 38: 1.15 pressed the upper arm into the cup)
    # round 42: the face-palm's release (the owner: "when the cow puts her hand down ... it looks very robotic"; round 41
    # ran the reach backwards, easing out of the face and into the rest at the same even pace).  Now the head comes up
    # out of the hoof first; then the arm drops: slow to leave, gathering speed as it falls (DROP: start, length), so it
    # arrives moving, bumps out off the belly's side and settles in a couple of small swings (BUMP: out, forward, Hz,
    # decay s); the hoof trails the arm, still half turned to the face as the arm falls; the shoulders sag with the
    # arm's weight as it lands.
    DROP = (5.02, .50)
    BUMP = (.030, .022, 1.35, .30)

    def __init__(self, B):
        super().__init__(B)
        self._fling_local = {}

    def drop(self, t):
        return drop_curve(t, self.DROP, self.BUMP)

    def key(self, t, fling=0., back=0., slap=0., palm=0., shake=0., slump=0.):
        p = neutral(self)
        dropping = t >= self.DROP[0]
        u, turn, land, bump, tau = self.drop(t) if dropping else (palm, 1., 0., np.zeros(2), 0.)
        # the head: buried in the hoof, then up out of it just before the arm goes (and tipped back with a sigh)
        hp = palm if not dropping else 1 - smooth(self.DROP[0] - .12, self.DROP[0] + .25, t)
        sigh = smooth(4.92, 5.25, t) * (1 - smooth(5.45, 6.1, t))
        p['shift'] = np.array([0, -.012 * slump - .008 * fling - .006 * land, -.012 * back])
        p['spine'] = np.array([-.05 * back + .08 * slump + .02 * land, 0, 0])
        p['chest'] = np.array([-.06 * back + .06 * slump - .04 * sigh + .03 * land, 0, .015 * land])
        yaw = .26 * shake * np.sin(2 * np.pi * 2.0 * t)
        p['neck'] = np.array([-.22 * back + .10 * slump + .10 * hp - .06 * sigh, .4 * yaw, 0])
        p['head'] = np.array([-.28 * back + .12 * slump + .12 * hp - .10 * sigh, .6 * yaw, .03 * slump])
        p.pop('fk')
        p['hand'], p['pole'] = {}, {}
        # round 42: the hands turn palm-up as the arms go out (not from the first moment)
        hturn = smooth(.15, 1., fling)
        for side, s in [('L', 1), ('R', -1)]:
            rest = rest_hand(self, side, s)
            pole_rest = self.B[RG.ARM[side]['fore']] + np.array([s * .25, 0, -.15])
            out = np.array([s * .50, 1.22, .24])                    # flung out to the side, palm up
            hip = rest + np.array([s * .025, .02, -.01])            # dropped onto the hips
            tgt = rest * (1 - fling - slap) + out * fling + hip * slap
            pole = pole_rest * (1 - fling) + np.array([s * .55, .85, -.30]) * fling
            up = self.hand_rot(side, [s * .55, .05, .55], [0, 1, 0])
            if side not in self._fling_local:
                self._fling_local[side] = local_hand(self, side, up, out, [s * .55, .85, -.30], .10)
            # relaxed to palm-up as a turn relative to the forearm, then onto the chest-frame palm-up itself (a few degrees
            # away, as the swivel and the springs move the elbow) once it is nearly there
            hr = ('blend', ('blend', relaxed_hand(self, side), self._fling_local[side], hturn), up, smooth(.75, 1., hturn))
            if side == 'R' and (palm > 0 or dropping):
                brow, Rh = head_point(self, p, [-.015, 1.575, .115])
                wrist, _ = head_point(self, p, np.array([-.015, 1.575, .115]) + .222 * np.array([-.15, -.62, .77]))
                tgt = bezier_reach(tgt, np.array([s * .44, 1.12, .04]), np.array([s * .36, 1.42, .20]),
                                   np.array([s * .16, 1.52, .36]), wrist, u)
                tgt = tgt + np.array([s * bump[0], 0, bump[1]])
                pw = u if not dropping else smooth(0, 1, 1 - tau)
                pole = pole * (1 - pw) + np.array(self.PALM_POLE) * [s, 1, 1] * pw
                face = self.hand_rot(side, brow - wrist, Rh @ np.array([0, 0, -1.]))
                # round 42: to and from the face as a turn relative to the forearm (see local_hand), then onto the face
                fl = local_hand(self, side, face, wrist, np.array(self.PALM_POLE) * [s, 1, 1], .10 * fling - .05 * slump)
                w = smooth(.6, 1, palm) if not dropping else turn
                hr = ('blend', ('blend', hr, fl, w), face, smooth(.8, 1., w))
            p['hand'][side], p['pole'][side], p['hrot'][side] = tgt, pole, hr
            p['clav'][side] = .10 * fling - .05 * slump - (.05 * land if side == 'R' else .02 * land)
        p['fingers'] = .15 * fling - .2 * (palm if not dropping else u) + .12 * land
        p['spread'] = .40 * fling                  # flung out, the hoof toes part in a V
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
