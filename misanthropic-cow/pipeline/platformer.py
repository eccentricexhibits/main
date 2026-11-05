"""The platformer set (44B final, after the owner's "what animations would a basic platformer need?"): the jump in
four parts (Jump Start, Jump Rise, Jump Apex, Fall), the two landings, a skid, a hurt reaction, a death and a victory
loop.  The 24 clips in clips.py are not touched: this module only adds to clips.ALL and clips.ORDER.

Like the other clips these play in place: the game moves the character (the jump's height, the fall, the skid's
slide); the clips pose her for it.  In the air the root stays at its standing height and the feet are drawn up
under her, so the engine's capsule and the clip agree on where she is.

Three of them loop (Jump Rise and Fall while she is in the air, Victory); the rest are one-shots that play once and
hold their last frame: Jump Start (standing to take-off), Jump Apex (rising to falling), Land and Hard Landing
(falling to standing), Skid (standing to standing), Hurt (standing to standing) and Death (standing to lying on her
back).  The glTF extras say which (extras.loop, extras.transition).

The bake (anim.Dance.bake, with the performance layer's springs and the belly / cups / shag / teat / tail physics)
runs a clip as a loop; a one-shot (OneShot) is baked as a loop that holds its first pose for LEAD seconds, plays the
shot, then plays it back in reverse, slowly, to the start; the shot's own stretch is kept.  So the springs and the
physics start the shot settled at its first pose and carry their real follow-through into it, and nothing jumps at
the loop's seam."""
import numpy as np
import anim as AN
import clips as CL
import rig as RG

smooth = AN.smooth
neutral = CL.neutral
REST = np.array(CL.REST_ARM)
EASE = {'smooth': lambda x: x * x * (3 - 2 * x), 'in': lambda x: x * x, 'out': lambda x: 1 - (1 - x) ** 2,
        'lin': lambda x: x}
FIELDS = ['y', 'z', 'x', 'lean', 'bend', 'look', 'turn', 'tilt', 'tuck', 'stagger', 'spread', 'toe', 'heel', 'step',
          'aup', 'aout', 'elbow', 'reach', 'flail', 'fist', 'shake', 'lie', 'legs_up', 'splay', 'clav']


def shot_keys(keys, t, fields=FIELDS):
    """Settings at time t from keys [(time, {field: value}, ease?)], clamped at both ends (not looped); the ease of a
    key shapes the stretch that arrives at it ('smooth', 'in': accelerating, 'out': decelerating, 'lin')."""
    if t <= keys[0][0]:
        k = keys[0][1]
        return {f: k.get(f, 0.) for f in fields}
    for a, b in zip(keys[:-1], keys[1:]):
        (t0, k0), (t1, k1) = a[:2], b[:2]
        if t0 <= t <= t1:
            w = EASE[b[2] if len(b) > 2 else 'smooth'](np.clip((t - t0) / (t1 - t0), 0, 1))
            return {f: k0.get(f, 0.) * (1 - w) + k1.get(f, 0.) * w for f in fields}
    k = keys[-1][1]
    return {f: k.get(f, 0.) for f in fields}


class Platform(AN.Dance):
    """The platformer clips' common pose: a handful of named settings (FIELDS) turned into a pose dict.

    y, z, x: the root's offset (m); lean: the hips' pitch (+ forward); bend: the spine and chest's; look: the neck and
    head's (+ chin down); turn, tilt: the head's yaw and roll; tuck: both feet drawn up (m, and forward); stagger: the
    left foot forward and up, the right back (m); spread: the feet apart (m each); toe: the feet's pitch (+ on the
    toes); heel: the left (front) foot's toes up (skid); step: the right foot a step back (m); aup: the arms' forward
    flexion (rad, on top of the relaxed arm); aout: abduction; elbow: extra bend; reach: the left arm higher and the
    right lower by this much; flail: a fast alternating flap of the arms (rad); fist: the hooves curled; shake: the
    head shaking no; clav: the shoulders raised."""
    use_swivel = False
    SYNC = 'start'
    LOOP = True
    # quick actions: the arms' and shoulders' springs stiffer than the standard clips' (motion.py: 2.7 and 3.0 Hz), so a
    # swing in a tenth of a second still arrives
    MOTION = {'fk': (4.2, .66), 'clav': (4.2, .66)}
    FLAIL_HZ = 2.5

    def key(self, t, f):
        p = neutral(self)
        p['hem'] = 1.                       # the front hem rides up over a lifted thigh
        p['shift'] = np.array([f['x'], f['y'], f['z']])
        p['hips'] = np.array([f['lean'], 0., 0.])
        p['spine'] = np.array([.55 * f['bend'], 0., 0.])
        p['chest'] = np.array([.45 * f['bend'], 0., 0.])
        sh = .22 * f['shake'] * np.sin(2 * np.pi * 4.2 * t)
        p['neck'] = np.array([.45 * f['look'], .4 * (f['turn'] + sh), 0.])
        p['head'] = np.array([.55 * f['look'], .6 * (f['turn'] + sh), f['tilt']])
        p['feet'] = {}
        for side, s in [('L', 1), ('R', -1)]:
            rest = self.B[RG.LEG[side]['foot']]
            pitch = f['toe'] - (f['heel'] if side == 'L' else 0.)
            st = s * f['stagger']
            dz = .35 * f['tuck'] + .30 * st - (f['step'] if side == 'R' else 0.)
            dy = f['tuck'] + .35 * max(0., st)
            pos = rest + [s * f['spread'], self.ankle_height(pitch) - self.ankle_height(0.) + dy, dz]
            p['feet'][side] = {'pos': pos, 'pitch': pitch, 'yaw': s * .15 * f['spread'] / .1 if f['spread'] > 0 else 0.}
        w = 2 * np.pi * self.FLAIL_HZ * t
        for side, s in [('L', 1), ('R', -1)]:
            fl = f['flail'] * np.sin(w + (0 if side == 'L' else np.pi))
            fo = .5 * f['flail'] * np.cos(w + (0 if side == 'L' else np.pi))
            p['fk'][side] = REST + [f['aout'] + fo, f['aup'] + s * f['reach'] + fl, f['elbow']]
            p['clav'][side] = f['clav'] + .06 * max(0., f['aup'] - 1.2) + .05 * max(0., f['aout'] - .8)
        p['fingers'] = -.12 - .6 * f['fist']
        p['thumb'] = .10 + .3 * f['fist']
        return p

    def sample(self, t):
        return self.key(t, shot_keys(self.KEYS, t % self.duration))


class OneShot(Platform):
    """A clip that plays once: the bake pads it (see the module's note) and keeps the shot."""
    LOOP = False
    LEAD = 1.0                  # s held at the first pose before the shot (the springs settle)

    def ret(self):
        return max(1.0, 1.5 * self.SHOT)

    def shot(self, t):
        return Platform.sample(self, t)

    def sample(self, t):
        D = self.SHOT
        if self.duration <= D + 1e-9:              # not padded (previews): the shot itself, clamped
            return self.shot(float(np.clip(t, 0, D)))
        tau = t % self.duration
        if tau < self.LEAD:
            u = 0.
        elif tau <= self.LEAD + D:
            u = tau - self.LEAD
        else:                                      # back to the start, slowly, so nothing jumps at the seam
            u = D * (1 - smooth(0, 1, (tau - self.LEAD - D) / self.ret()))
        return self.shot(u)

    def bake(self, fps=AN.FPS):
        D = self.SHOT
        self.duration = self.LEAD + D + self.ret()
        try:
            times, Gs = AN.Dance.bake(self, fps)
        finally:
            self.duration = D
        i0, n = int(round(self.LEAD * fps)), int(round(D * fps)) + 1
        return times[i0:i0 + n] - times[i0], Gs[i0:i0 + n]


# ---------------------------------------------------------------- the poses the jump passes through
STAND = {}
CROUCH = dict(y=-.13, lean=.28, bend=.16, look=-.16, aup=-.55, aout=.06, elbow=.25, clav=-.03)
TAKEOFF = dict(y=.02, lean=-.04, bend=-.06, look=-.18, toe=.55, aup=1.85, aout=.25, elbow=.12, reach=.15, clav=.04)
RISE = dict(tuck=.17, stagger=.28, toe=.45, lean=.06, bend=.04, look=-.12, aup=1.95, aout=.30, elbow=.30, reach=.35,
            fist=.6)
APEX = dict(tuck=.20, stagger=.12, toe=.35, lean=.10, bend=.06, look=.02, aup=1.2, aout=.70, elbow=.35, reach=.15,
            fist=.3)
FALL = dict(tuck=.05, toe=.25, lean=.08, bend=.04, look=.22, aup=.35, aout=1.05, elbow=.35, spread=.03)


class JumpStart(OneShot):
    """Standing to take-off: a quick crouch with the arms swinging back, then the push off the toes with the arms
    swinging up (hand on to Jump Rise as the feet leave the ground)."""
    name = 'Jump Start'
    SHOT = duration = .4
    phases = [('Crouch', 0, .22), ('Push off', .22, .4)]
    KEYS = [(0., STAND), (.22, CROUCH, 'smooth'), (.4, TAKEOFF, 'in')]
    TRANSITION = {'sync': 'start', 'blend_seconds': .15, 'next': 'Jump Rise',
                  'note': 'one-shot from standing; ends at take-off: play Jump Rise as the character leaves the ground'}


class JumpRise(Platform):
    """In the air, going up: the knees drawn up (the left higher), toes pointed, the left fist up; a little kick of
    the legs and wave of the arms (loops)."""
    name = 'Jump Rise'
    duration = .6
    phases = [('Rising', 0, .6)]
    TRANSITION = {'sync': 'start', 'blend_seconds': .12, 'next': 'Jump Apex',
                  'note': 'loops while rising; play Jump Apex as the vertical speed reaches zero'}

    def sample(self, t):
        w = 2 * np.pi * t / self.duration
        f = shot_keys([(0., RISE)], 0.)
        f['stagger'] += .05 * np.sin(w); f['tuck'] += .015 * np.cos(w)
        f['reach'] += .06 * np.sin(w + .8); f['elbow'] += .06 * np.cos(w)
        return self.key(t, f)


class JumpApex(OneShot):
    """The top of the jump: the legs come together and the arms open, rising pose to falling pose."""
    name = 'Jump Apex'
    SHOT = duration = .3
    phases = [('Apex', 0, .3)]
    KEYS = [(0., RISE), (.14, APEX, 'out'), (.3, FALL, 'in')]
    TRANSITION = {'sync': 'start', 'blend_seconds': .1, 'next': 'Fall',
                  'note': 'one-shot at the top of the jump; play Fall when it ends (or when the character starts to fall)'}


class Fall(Platform):
    """Falling: arms out flapping, legs pedalling, looking down for the ground (loops)."""
    name = 'Fall'
    duration = .8
    phases = [('Falling', 0, .8)]
    FLAIL_HZ = 2.5              # two flaps per loop
    TRANSITION = {'sync': 'start', 'blend_seconds': .15, 'next': 'Land',
                  'note': 'loops while falling; play Land or Hard Landing on touching down'}

    def sample(self, t):
        w = 2 * np.pi * t / self.duration
        f = shot_keys([(0., dict(FALL, flail=.28))], 0.)
        f['stagger'] = .10 * np.sin(w); f['tuck'] += .02 * (.5 + .5 * np.cos(2 * w))
        f['tilt'] = .04 * np.sin(w)
        return self.key(t, f)


LANDING_START = FALL
LAND = [(0., LANDING_START), (.05, dict(y=-.03, lean=.08, look=.15, aup=.3, aout=.9, elbow=.35), 'in'),
        (.13, dict(y=-.12, lean=.24, bend=.12, look=.04, aup=.25, aout=.45, elbow=.4, clav=-.04), 'out'),
        (.5, STAND, 'smooth')]
HARD = [(0., LANDING_START), (.06, dict(y=-.05, lean=.10, look=.15, aup=.35, aout=.8, elbow=.35), 'in'),
        (.17, dict(y=-.23, lean=.45, bend=.24, look=.22, aup=.70, aout=.12, elbow=.55, clav=-.06, fist=.2), 'out'),
        (.55, dict(y=-.21, lean=.40, bend=.22, look=.30, aup=.62, aout=.12, elbow=.55, clav=-.05, shake=1., fist=.2)),
        (.85, dict(y=-.07, lean=.12, bend=.06, look=.05, aup=.12, aout=.04, elbow=.2, shake=.6)),
        (1.1, STAND)]


class Land(OneShot):
    """Touching down: the knees give, the arms drop, and she stands back up (falling pose to standing)."""
    name = 'Land'
    SHOT = duration = .5
    phases = [('Impact', 0, .13), ('Recover', .13, .5)]
    KEYS = LAND
    TRANSITION = {'sync': 'start', 'blend_seconds': .06, 'next': 'Idle',
                  'note': 'one-shot on touching down; ends standing (blend to Idle or a gait; can be cut short after the impact)'}


class HardLanding(OneShot):
    """A heavy landing from high up: a deep squat with the hooves towards the knees, a dazed shake of the head, and
    up again slowly (falling pose to standing)."""
    name = 'Hard Landing'
    SHOT = duration = 1.1
    phases = [('Impact', 0, .17), ('Dazed', .17, .55), ('Recover', .55, 1.1)]
    KEYS = HARD
    TRANSITION = {'sync': 'start', 'blend_seconds': .06, 'next': 'Idle',
                  'note': 'one-shot on touching down from a height; ends standing'}


class Skid(OneShot):
    """Braking hard from a run (or turning round): leaning back on the left heel, toes up, the right foot behind, the
    arms out forward for balance, juddering as the slipper slides; then upright (standing to standing)."""
    name = 'Skid'
    SHOT = duration = .6
    phases = [('Brake', 0, .12), ('Slide', .12, .42), ('Recover', .42, .6)]
    SKID = dict(y=-.07, z=-.04, lean=-.20, bend=-.08, look=.02, heel=.45, step=.12, toe=.0, aup=.95, aout=.7,
                elbow=.25, reach=.12, clav=.05)
    KEYS = [(0., STAND), (.12, SKID, 'out'), (.42, dict(SKID, lean=-.16, aup=.85, reach=-.1)), (.6, STAND)]
    TRANSITION = {'sync': 'start', 'blend_seconds': .08, 'next': 'Run',
                  'note': 'one-shot while the character brakes or turns; ends standing (blend to Run the other way, or Idle)'}

    def shot(self, t):
        p = Platform.sample(self, t)
        judder = smooth(.08, .14, t) * (1 - smooth(.36, .44, t))
        p['shift'] = p['shift'] + [0, .005 * judder * np.sin(2 * np.pi * 11 * t), 0]
        p['spine'] = p['spine'] + [.02 * judder * np.sin(2 * np.pi * 11 * t + 1), 0, 0]
        return p


class Hurt(OneShot):
    """Hit: the head and chest thrown back, the arms flung up, a stumble back on the right foot, then a flinch
    forward and back to standing (standing to standing)."""
    name = 'Hurt'
    SHOT = duration = .6
    phases = [('Hit', 0, .08), ('Flinch', .08, .25), ('Recover', .25, .6)]
    HIT = dict(y=-.03, z=-.05, lean=-.20, bend=-.22, look=-.38, turn=.12, tilt=.10, step=.10, aup=.95, aout=.55,
               elbow=.55, reach=.15, clav=.08)
    KEYS = [(0., STAND), (.08, HIT, 'out'), (.25, dict(y=-.05, lean=.12, bend=.10, look=.20, turn=-.05, aup=.15,
                                                       aout=.15, elbow=.3, clav=-.03)), (.6, STAND)]
    TRANSITION = {'sync': 'start', 'blend_seconds': .05, 'next': 'Idle',
                  'note': 'one-shot when hit; ends standing (blend back to whatever was playing)'}


class Death(OneShot):
    """Knocked out: the hit as in Hurt but harder, a wobble, the knees buckle, she sits down hard, tips over backwards
    with the legs flying up, and ends lying on her back, arms flopped out (standing to lying; holds)."""
    name = 'Death'
    SHOT = duration = 2.6
    phases = [('Hit', 0, .12), ('Wobble', .12, .7), ('Sit down', .7, 1.3), ('Tip over', 1.3, 2.0), ('Lie', 2.0, 2.6)]
    HIT = dict(y=-.03, z=-.06, lean=-.24, bend=-.25, look=-.45, turn=.15, tilt=.12, step=.10, aup=1.0, aout=.6,
               elbow=.6, reach=.2, clav=.08)
    WOBBLE = dict(y=-.08, z=.0, lean=.18, bend=.14, look=.30, turn=-.12, tilt=-.10, aup=.05, aout=.08, elbow=.2, clav=-.06)
    BUCKLE = dict(y=-.30, lean=.30, bend=.12, look=.25, tilt=.05, aup=.15, aout=.25, elbow=.35, clav=-.05)
    SIT = dict(lie=.32, look=.05, aup=.35, aout=.55, elbow=.4)
    TIP = dict(lie=.85, legs_up=1., look=-.15, aup=.2, aout=1.0, elbow=.3, splay=.5)
    LIE = dict(lie=1., look=-.30, tilt=.25, turn=.35, aup=.0, aout=1.15, elbow=.35, splay=1.)
    KEYS = [(0., STAND), (.12, HIT, 'out'), (.42, dict(WOBBLE, look=.1, turn=.05)), (.7, WOBBLE),
            (1.0, BUCKLE, 'in'), (1.3, SIT, 'in'), (1.62, TIP, 'out'), (2.0, dict(LIE, legs_up=.15), 'in'),
            (2.2, dict(LIE, legs_up=.25), 'out'), (2.6, LIE)]
    TRANSITION = {'sync': 'start', 'blend_seconds': .05, 'next': None,
                  'note': 'one-shot; ends lying on her back: hold the last frame'}
    # lying: the hips' pitch, height and how far back the root goes (seated at lie .32, flat on the back at 1)
    SEAT_Y, SEAT_Z, SEAT_PITCH = -.75, -.30, -.40
    LIE_Y, LIE_Z, LIE_PITCH = -.75, -.62, -1.42

    def shot(self, t):
        f = shot_keys(self.KEYS, t)
        lie = f['lie']
        if lie <= 1e-6:
            return Platform.key(self, t, f)
        f2 = dict(f, lie=0., y=0., z=0., lean=0., tuck=0., stagger=0., step=0., toe=0.)
        p = Platform.key(self, t, f2)
        # down to the seat (lie 0 .. .32), then over on to the back (.32 .. 1); before the seat the knees buckle
        a = smooth(0, .32, lie); b = smooth(.32, 1., lie)
        y0, z0, l0 = f['y'], f['z'], f['lean']              # where the buckle left her (blended out as she sits)
        y = y0 * (1 - a) + self.SEAT_Y * a * (1 - b) + self.LIE_Y * b
        z = z0 * (1 - a) + self.SEAT_Z * a * (1 - b) + self.LIE_Z * b
        pitch = l0 * (1 - a) + self.SEAT_PITCH * a * (1 - b) + self.LIE_PITCH * b
        p['shift'] = np.array([0., y, z])
        p['hips'] = np.array([pitch, 0., 0.])
        # the back straightens against the floor as she lies down; the head rests on it, turned and tipped aside
        p['spine'] = p['spine'] * (1 - b) + [-.06 * b, 0, 0]
        p['chest'] = p['chest'] * (1 - b) + [-.04 * b, 0, 0]
        Rh = AN.euler(p['hips'])
        for side, s in [('L', 1), ('R', -1)]:
            hip = Rh @ (self.B[RG.LEG[side]['thigh']] - self.B[RG.HIPS]) + self.B[RG.HIPS] + p['shift']
            # seated: the legs out in front, knees a little up; lying: out straight, splayed; legs_up: kicked up
            up = f['legs_up']
            out = s * (.10 + .10 * f['splay'])
            seat_ft = np.array([hip[0] + out, 0., hip[2] + .66])
            lie_ft = np.array([hip[0] + out + s * .04, 0., hip[2] + .76])
            ft = seat_ft * (1 - b) + lie_ft * b
            stand = self.B[RG.LEG[side]['foot']] + [0, 0, 0]
            ft = stand * (1 - a) + ft * a
            pitch_f = -.55 * a - .65 * b
            ft[1] = self.ankle_height(pitch_f) + up * .55 * (1. + .25 * s)
            ft[2] -= up * .25
            knee = np.array([s * .2, .6, .5]) * a + np.array([0, -.35, .8]) * (1 - a)
            p['feet'][side] = {'pos': ft, 'pitch': pitch_f - .5 * up, 'yaw': s * .25 * f['splay'], 'knee': tuple(knee)}
            p['fk'][side] = np.asarray(p['fk'][side]) + [0, -.80 * b, 0]     # the arms down on to the floor
        return p


class Victory(Platform):
    """Celebrating: bouncing on the toes with both fists up in a V, pumping them in turn, the head bobbing side to
    side (loops)."""
    name = 'Victory'
    duration = 2.4
    phases = [('Victory', 0, 2.4)]
    TRANSITION = {'sync': 'start', 'blend_seconds': .3, 'next': None,
                  'note': 'loops; starts and ends standing with the fists up'}

    def sample(self, t):
        u = t / self.duration
        bounce = .5 - .5 * np.cos(2 * np.pi * 4 * u)               # four bounces per loop
        f = {k: 0. for k in FIELDS}
        f.update(y=-.05 * (1 - bounce) + .015, toe=.25 * bounce, lean=-.04, bend=-.06, look=-.15,
                 tilt=.12 * np.sin(2 * np.pi * 2 * u), turn=.10 * np.sin(2 * np.pi * 2 * u - .6), fist=1.)
        p = self.key(t, f)
        for side, s in [('L', 1), ('R', -1)]:
            pump = .5 - .5 * np.cos(2 * np.pi * 2 * u + (0 if side == 'L' else np.pi))   # one pump per side every 1.2 s
            p['fk'][side] = np.array([2.15 + .12 * pump, .35 + .10 * pump, .95 - .80 * pump])
            p['clav'][side] = .12 + .08 * pump
            p['hrot'][side] = ('follow', .1)
        return p


CLIPS = [JumpStart, JumpRise, JumpApex, Fall, Land, HardLanding, Skid, Hurt, Death, Victory]
NAMES = [C.name for C in CLIPS]
