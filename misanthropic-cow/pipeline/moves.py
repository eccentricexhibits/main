"""General versions of four platformer moves, in the regular set (the owner: "add some of these animations into the
regular set, but slightly tweaked to be general animations (Jump, skid, death, and victory)", and "rework victory?
Maybe it can be a little dance").

Like the other regular clips each loops, starts and ends standing on her spot (so any two blend), and has a lumbering
alt version:

* Jump (2.2 s): a crouch, the push off, a real 30 cm hop (the body follows a falling body's arc), the landing and back
  up; the platformer's Jump Start / Rise / Apex / Fall / Land in one, with the height in the clip.
* Skid (3.0 s): she lunges into a skid, slides 26 cm on her heel with the arms windmilling, teeters forward over her
  toes as if at an edge, catches her balance, sighs with relief and steps back to her spot.
* Death (7.4 s): the platformer's death (hit, wobble, the knees buckle, she sits down hard and tips over on to her
  back), lies still with a twitch of the leg, then lifts her head, sits up, gathers her feet, gets up, and shrugs it
  off.
* Victory (6.4 s): a little dance, 16 beats at 150 a minute: step-touch side to side with bent arms swinging; raise
  the roof with the knees bouncing and the hips wiggling; a shoulder shimmy, arms out, sinking down and back up;
  then a fist pump each side and both arms up in a V on her toes.  It replaces the platformer's fist-pump Victory and
  serves both sets.

The poses are platformer.Platform's settings (see there).  The lumbering versions are clips.lumbering's, except that
where she is low (seated, lying, a deep squat) the body keeps its height instead of lumber's 70 %, so she stays on
the floor (lumbering_grounded)."""
import numpy as np
import anim as AN
import clips as CL
import platformer as PF

smooth = AN.smooth
FIELDS = PF.FIELDS + ['shim']


class Jump(PF.Platform):
    """Crouch, push off, a 30 cm hop, land and back up (loops, standing to standing)."""
    name = 'Jump'
    duration = 2.2
    phases = [('Crouch', 0, .8), ('Air', .8, 1.3), ('Land', 1.3, 2.2)]
    T0, T1, HEIGHT = .8, 1.3, .30          # take-off, touch-down, the top of the arc (m): .5 s of flight is a 31 cm hop
    KEYS = [(0., {}), (.32, dict(look=.04)),
            (.62, dict(PF.CROUCH, y=-.15, lean=.32, aup=-.6, elbow=.3), 'smooth'),
            (.80, dict(PF.TAKEOFF, y=.0, aup=1.9, aout=.3), 'in'),
            (.95, dict(tuck=.09, stagger=.10, toe=.35, lean=.04, look=-.16, aup=2.1, aout=.32, elbow=.25, reach=.2, fist=.4)),
            (1.07, dict(tuck=.13, stagger=.04, toe=.30, lean=.06, look=-.05, aup=1.7, aout=.45, elbow=.3, reach=.1, fist=.3)),
            (1.24, dict(tuck=.02, toe=.12, lean=.08, look=.14, aup=.8, aout=.75, elbow=.35), 'in'),
            (1.30, dict(y=-.02, lean=.10, look=.12, aup=.55, aout=.7, elbow=.35), 'lin'),
            (1.43, dict(y=-.14, lean=.26, bend=.12, look=.04, aup=.25, aout=.45, elbow=.4, clav=-.04), 'out'),
            (1.78, dict(y=-.03, lean=.05, bend=.02, look=-.02, aup=.05, aout=.08, elbow=.1)),
            (2.2, {})]

    def sample(self, t):
        t = t % self.duration
        f = PF.shot_keys(self.KEYS, t)
        u = (t - self.T0) / (self.T1 - self.T0)
        if 0 < u < 1:
            f['air'] += self.HEIGHT * 4 * u * (1 - u)
        return self.key(t, f)


class Skid(PF.Platform):
    """Lunge into a skid, slide on the left heel with the arms windmilling, teeter forward at the end, recover, sigh,
    and step back to the spot (loops, standing to standing)."""
    name = 'Skid'
    duration = 3.0
    phases = [('Skid', 0, .95), ('Teeter', .95, 1.85), ('Relief', 1.85, 2.3), ('Step back', 2.3, 3.0)]
    BRACE = dict(y=-.07, z=.04, lean=-.18, bend=-.06, look=.02, heel=.45, lfz=.20, rfz=-.08, rpitch=.25, aup=.9, aout=.7,
                 elbow=.25, reach=.1, clav=.05)
    KEYS = [(0., {}), (.25, dict(y=-.02, lean=.12, bend=.05, aup=.2, look=-.03)),
            (.40, BRACE, 'out'),
            (.95, dict(BRACE, z=.30, lfz=.46, rfz=.18, flail=.35, aup=1.0, aout=.9), 'out'),
            (1.15, dict(y=-.02, z=.30, lean=.25, bend=.12, look=.28, toe=.35, lfz=.30, rfz=.22, flail=.45, aup=1.3, aout=1.1,
                        elbow=.3, clav=.06)),
            (1.55, dict(y=-.02, z=.30, lean=.18, bend=.10, look=.24, toe=.25, lfz=.30, rfz=.22, flail=.30, aup=1.1, aout=1.0,
                        elbow=.3, clav=.05)),
            (1.85, dict(y=-.01, z=.28, lean=-.05, look=.0, lfz=.30, rfz=.26, aup=.3, aout=.3, elbow=.2)),
            (2.15, dict(y=-.03, z=.28, bend=.10, look=.12, lfz=.30, rfz=.26, clav=-.06, aup=.0, elbow=.15)),
            (2.33, dict(y=-.01, z=.22, lfz=.30, rfz=.13, rfy=.06, look=.04)),
            (2.50, dict(y=-.02, z=.15, lfz=.30, rfz=.0)),
            (2.65, dict(y=-.01, z=.08, lfz=.15, lfy=.06, rfz=.0)),
            (2.80, dict(y=-.015, z=.0, lfz=.0, rfz=.0)),
            (3.0, {})]


class Death(PF.Platform):
    """The platformer's death, then she gets up again: lies still with a twitch of the leg, lifts her head, sits up,
    gathers her feet, pushes up through a squat and shrugs it off (loops, standing to standing)."""
    name = 'Death'
    duration = 7.4
    phases = [('Hit', 0, .12), ('Collapse', .12, 2.0), ('Lie', 2.0, 3.9), ('Sit up', 3.9, 5.4), ('Get up', 5.4, 6.5),
              ('Shrug', 6.5, 7.4)]
    SEAT_Y, SEAT_Z, SEAT_PITCH = PF.Death.SEAT_Y, PF.Death.SEAT_Z, PF.Death.SEAT_PITCH
    LIE_Y, LIE_Z, LIE_PITCH = PF.Death.LIE_Y, PF.Death.LIE_Z, PF.Death.LIE_PITCH
    posef, lie_pose = PF.Death.posef, PF.Death.lie_pose
    LIE = PF.Death.LIE
    ARM_DOWN = .70                  # (the game version's .80 took a glove 6 mm into the floor with this clip's arm drift)
    SIT_UP = dict(lie=.32, look=.25, tilt=-.05, aup=.5, aout=.4, elbow=.4, shake=.6)
    SQUAT = dict(y=-.40, lean=.55, bend=.20, look=.15, aup=.85, aout=.15, elbow=.45, clav=-.03)
    KEYS = PF.Death.KEYS[:-1] + [
        (2.6, LIE), (3.05, LIE), (3.18, dict(LIE, lfy=.09), 'out'), (3.34, LIE, 'in'), (3.9, LIE),
        (4.35, dict(LIE, look=.45, tilt=.1, turn=.1)),
        (5.0, SIT_UP),
        (5.4, dict(SQUAT, lie=.32, gather=1.)),
        (6.0, dict(SQUAT, gu=1.)),
        (6.5, dict(y=-.07, lean=.10, bend=.05, look=.05, aup=.1, elbow=.2)),
        (6.95, dict(clav=.14, aout=.35, elbow=.75, aup=.25, look=-.08, tilt=.12, shake=.4)),
        (7.4, {})]

    def sample(self, t):
        t = t % self.duration
        return self.posef(t, PF.shot_keys(self.KEYS, t))


B = .4      # one beat of the dance (150 a minute)


class Victory(PF.Platform):
    """A little victory dance, 16 beats (loops, standing to standing)."""
    name = 'Victory'
    duration = 16 * B
    phases = [('Step-touch', 0, 4 * B), ('Raise the roof', 4 * B, 8 * B), ('Shimmy', 8 * B, 12 * B), ('Ta-da', 12 * B, 16 * B)]
    ARMS = dict(aup=.55, elbow=1.25, fist=.9)                  # bent arms swinging, fists loose
    ROOF = dict(aup=2.2, aout=.35, elbow=1.1, clav=.05)       # hands overhead, palms up
    PUSH = dict(ROOF, aup=2.35, elbow=.35, clav=.10)
    SHIM = dict(aup=.4, aout=.9, elbow=.8, fist=.3, clav=.08, shim=1.)
    KEYS = [(0., {}),
            # step-touch to her right and back to her left, the arms swinging in turn, the head bobbing
            (.2, dict(ARMS, rfy=.05, rfx=-.06, x=-.02, y=-.02, aup=.4, elbow=.9, lup=.2, rup=-.2, fist=.7)),
            (.4, dict(ARMS, rfx=-.12, x=-.06, y=-.055, roll=.05, lup=.25, rup=-.25, look=.06, tilt=-.06)),
            (.6, dict(ARMS, rfx=-.12, lfx=-.05, lfy=.035, x=-.08, y=-.02, lup=-.25, rup=.25)),
            (.8, dict(ARMS, rfx=-.12, lfx=-.10, lpitch=.30, x=-.09, y=-.045, lup=-.25, rup=.25, look=-.04, tilt=.06)),
            (1.0, dict(ARMS, rfx=-.12, lfx=-.05, lfy=.04, x=-.06, y=-.02, lup=.25, rup=-.25)),
            (1.2, dict(ARMS, rfx=-.12, x=-.03, y=-.055, roll=-.05, lup=.25, rup=-.25, look=.06, tilt=.06)),
            (1.4, dict(ARMS, rfx=-.05, rfy=.035, x=-.01, y=-.02, lup=-.25, rup=.25)),
            (1.6, dict(ARMS, rpitch=.30, y=-.045, lup=-.25, rup=.25, look=-.04, tilt=-.06)),
            # raise the roof: palms up overhead, pushing on the beat, knees bouncing, hips wiggling
            (1.8, dict(ROOF, y=-.02, yaw=.12)), (2.0, dict(PUSH, y=-.06, yaw=.12, look=-.12)),
            (2.2, dict(ROOF, y=-.02, yaw=-.12)), (2.4, dict(PUSH, y=-.06, yaw=-.12, look=-.12)),
            (2.6, dict(ROOF, y=-.02, yaw=.12)), (2.8, dict(PUSH, y=-.06, yaw=.12, look=-.12)),
            (3.0, dict(ROOF, y=-.02, yaw=-.12)), (3.2, dict(PUSH, y=-.06, yaw=-.12, look=-.12)),
            # the shimmy: arms out, shoulders shaking, sinking down and coming back up, the hips rocking on the beat
            (3.4, dict(SHIM, y=-.05, roll=.05)), (3.6, dict(SHIM, y=-.08, roll=-.05, tilt=.06)),
            (3.8, dict(SHIM, y=-.10, roll=.05)), (4.0, dict(SHIM, y=-.12, roll=-.05, look=.1, tilt=-.06)),
            (4.2, dict(SHIM, y=-.10, roll=.05)), (4.4, dict(SHIM, y=-.07, roll=-.05, tilt=.06)),
            (4.6, dict(SHIM, y=-.04, roll=.05)),
            (4.8, dict(aup=.3, aout=.3, elbow=.6, fist=1., y=-.02)),
            # a fist pump each side, then both arms up in a V, up on her toes: ta-da
            (5.0, dict(lout=1.9, lup=.35, lel=.1, rout=.2, rel=.7, fist=1., y=-.05, roll=.06, look=-.1, tilt=.08)),
            (5.4, dict(rout=1.9, rup=.35, rel=.1, lout=.2, lel=.7, fist=1., y=-.05, roll=-.06, look=-.1, tilt=-.08)),
            (5.8, dict(lout=2.0, rout=2.0, lup=.35, rup=.35, lel=.3, rel=.3, fist=.2, toe=.45, y=.01, look=-.2, bend=-.05), 'out'),
            (6.05, dict(lout=2.0, rout=2.0, lup=.35, rup=.35, lel=.3, rel=.3, fist=.2, toe=.40, y=.01, look=-.18, bend=-.05)),
            (6.4, {})]
    SHIM_HZ = 5.                                               # 32 shakes a loop

    def sample(self, t):
        t = t % self.duration
        f = PF.shot_keys(self.KEYS, t, FIELDS)
        p = self.key(t, f)
        sh = f['shim'] * np.sin(2 * np.pi * self.SHIM_HZ * t)
        p['chest'] = p['chest'] + [0, .10 * sh, 0]
        p['clav'] = {sd: v + .03 * f['shim'] * (sh if sd == 'L' else -sh) for sd, v in p['clav'].items()}
        return p


def lumbering_grounded(Base):
    """clips.lumbering(Base), but low down (seated, lying, a deep squat) the body keeps its own height (lumber takes it to
    70 %, which would lift her off the floor)."""
    Alt = CL.lumbering(Base)

    class G(Alt):
        def sample(self, t):
            p = Alt.sample(self, t)
            tb = (t % self.duration) / CL.SLOW
            self.duration = Base.duration
            try:
                y0 = float(Base.sample(self, tb)['shift'][1])
            finally:
                del self.duration
            keep = smooth(.05, .25, -y0)
            p['shift'] = np.asarray(p['shift'], float).copy()
            p['shift'][1] = p['shift'][1] * (1 - keep) + y0 * keep
            return p
    G.__name__ = Base.__name__ + 'Alt'
    return G


STD = [Jump, Skid, Death, Victory]
ALT = [lumbering_grounded(C) for C in STD]
NAMES = [C.name for C in STD]
