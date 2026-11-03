"""Round 39: the performance layer that makes the procedural clips less robotic.

The clips in clips.py and anim.py describe each pose as functions of time, mostly sines, and every joint
follows its function exactly: the whole body moves in lockstep, left and right mirror each other, every move
starts and stops at once and the head rides rigidly on the bobbing body.  `perform(clip, t)` takes the clip's
own sample and adds what a person inside the suit does on top of it:

* overlap and follow-through: each upper-body joint, and the arms, follow the clip's pose through a damped
  spring of their own (MOTION: natural frequency and damping per channel), softer the further up the chain,
  so the chest trails the hips, the head trails the chest and the arms drag a moment behind and settle with
  a little overshoot after quick moves; the hips, the root and the feet keep their exact timing, so the soles
  stay planted;
* asymmetry and life: a slow, smooth drift on the spine, chest, neck, head, shoulders and arms, different on
  each side and a whole number of cycles per loop, so the loop stays seamless and nothing is ever frozen
  (NOISE: which channels, and how much);
* breathing: the chest and shoulders rise and fall (BREATH);
* a steadier head: in the gaits the neck takes up part of the body's bob and roll, so the head floats over
  them instead of nodding with every step (STABILIZE).

The springs run over three loops of the clip and the last is kept (as the physics does), so every clip still
loops seamlessly.  A channel set to None in MOTION is left exactly as the clip has it: hands that must meet
something (the claps, the hooves at the eyes or the brow) and the head they meet."""
import numpy as np

FPS = 120                      # the performance table's sampling rate
DEFAULT_MOTION = {             # channel: (natural frequency in Hz, damping ratio); None leaves it as it is
    'spine': (4.2, .65), 'chest': (3.4, .60), 'neck': (3.0, .55), 'head': (2.6, .52),
    'clav': (3.0, .60), 'fk': (2.7, .58), 'hand': (3.4, .72), 'pole': (3.4, .72),
}
DEFAULT_NOISE = {              # channel: amplitude per component (rad, or m for shift)
    'spine': (.010, .012, .008), 'chest': (.012, .015, .010), 'neck': (.014, .022, .010), 'head': (.020, .035, .016),
    'clav': .014, 'fk': (.030, .040, .050),
}
SIDE_KEYED = ('clav', 'fk', 'hand', 'pole')


def loop_noise(name, key, T, n_comp):
    """A smooth, loopable wobble: two or three sines with a whole number of cycles per loop of length T,
    between about 0.15 and 0.6 Hz where the loop is long enough (one cycle per loop in short gait loops)."""
    g = np.random.default_rng(sum(ord(c) * (i + 1) for i, c in enumerate(f'{name}|{key}')) % (2 ** 32))
    lo, hi = max(1, int(round(.15 * T))), max(1, int(round(.6 * T)))
    ks = g.integers(lo, hi + 1, size=(3, n_comp))
    ph = g.uniform(0, 2 * np.pi, size=(3, n_comp))
    amp = np.array([1., .6, .35])[:, None] * g.uniform(.7, 1.3, size=(3, n_comp))
    amp /= np.sqrt((amp ** 2).sum(0, keepdims=True))
    return lambda t: (amp * np.sin(2 * np.pi * ks * (t / T) + ph)).sum(0)


def _get(p, key):
    """A channel of a sample as one flat vector (side-keyed channels as L then R), or None if absent."""
    v = p.get(key)
    if v is None:
        return None
    if key in SIDE_KEYED:
        if not isinstance(v, dict) or set(v) != {'L', 'R'}:
            return None
        return np.concatenate([np.atleast_1d(np.asarray(v['L'], float)), np.atleast_1d(np.asarray(v['R'], float))])
    return np.atleast_1d(np.asarray(v, float))


def _set(p, key, vec):
    if key in SIDE_KEYED:
        n = len(vec) // 2
        p[key] = {'L': vec[:n] if n > 1 else float(vec[0]), 'R': vec[n:] if n > 1 else float(vec[n])}
    else:
        p[key] = vec.copy()


def spring_filter(x, dt, f, zeta, sub=4):
    """A damped spring following x (time along axis 0)."""
    w = 2 * np.pi * f
    y = x[0].copy(); v = np.zeros_like(y); out = np.empty_like(x)
    h = dt / sub
    for i in range(len(x)):
        for _ in range(sub):
            v += (w * w * (x[i] - y) - 2 * zeta * w * v) * h
            y += v * h
        out[i] = y
    return out


class Performance:
    def __init__(self, clip):
        T = clip.duration
        self.T = T
        motion = dict(DEFAULT_MOTION); motion.update(getattr(clip, 'MOTION', {}))
        noise = dict(DEFAULT_NOISE); noise.update(getattr(clip, 'NOISE', {}))
        scale = getattr(clip, 'NOISE_SCALE', 1.) * (.5 if T < 2.5 else 1.)
        n = max(8, int(round(T * FPS)))
        self.times = np.arange(n) * (T / n)
        tt = np.concatenate([self.times + k * T for k in range(3)])
        samples = [clip.sample(t % T) for t in tt]
        self.tables = {}
        for key, cfg in motion.items():
            vals = [_get(p, key) for p in samples]
            if any(v is None for v in vals) or len({len(v) for v in vals}) != 1:
                continue
            X = np.array(vals)
            Y = X if cfg is None else spring_filter(X, T / n, *cfg)
            self.tables[key] = Y[2 * n:] - X[2 * n:]            # what the springs add, over the last loop
        # slow drift, a whole number of cycles per loop
        self.noise = {}
        for key, amp in noise.items():
            if amp is None or motion.get(key, 0) is None:
                continue
            v0 = _get(samples[0], key)
            if v0 is None:
                continue
            a = np.resize(np.atleast_1d(np.asarray(amp, float)), len(v0) // (2 if key in SIDE_KEYED else 1))
            if key in SIDE_KEYED:
                a = np.concatenate([a, a])
            f = loop_noise(clip.name, key, T, len(v0))
            self.noise[key] = (a * scale, f)
        b = getattr(clip, 'BREATH', .5)
        self.breath = (b, max(1, int(round(T / 3.8)))) if b and T >= 3.4 else None
        st = getattr(clip, 'STABILIZE', 0.)
        self.stab = None
        if st:
            # the body's swing in pitch and roll under the head, over the loop (after the springs)
            chain = np.zeros((n, 3))
            for key in ('hips', 'spine', 'chest'):
                vals = np.array([_get(p, key) for p in samples[2 * n:]])
                if key in self.tables:
                    vals = vals + self.tables[key]
                chain += vals
            swing = chain - chain.mean(0)
            swing[:, 1] = 0                                     # keep the turns; take up the nods and rolls
            self.stab = -st * swing

    def _at(self, table, t):
        u = (t % self.T) / self.T * len(table)
        i = int(np.floor(u)) % len(table); j = (i + 1) % len(table); w = u - np.floor(u)
        return table[i] * (1 - w) + table[j] * w

    def apply(self, p, t):
        for key, tab in self.tables.items():
            v = _get(p, key)
            if v is not None and len(v) == tab.shape[1]:
                _set(p, key, v + self._at(tab, t))
        for key, (a, f) in self.noise.items():
            v = _get(p, key)
            if v is not None and len(v) == len(a):
                _set(p, key, v + a * f(t % self.T))
        if self.breath:
            amp, k = self.breath
            b = np.sin(2 * np.pi * k * (t % self.T) / self.T)
            p['chest'] = np.asarray(p['chest'], float) + [-.018 * amp * b, 0, 0]
            if isinstance(p.get('clav'), dict):
                p['clav'] = {s: v + .020 * amp * (.5 + .5 * b) for s, v in p['clav'].items()}
            p['shift'] = np.asarray(p['shift'], float) + [0, .0015 * amp * b, 0]
        if self.stab is not None:
            d = self._at(self.stab, t)
            p['neck'] = np.asarray(p['neck'], float) + .45 * d
            p['head'] = np.asarray(p['head'], float) + .55 * d
        return p


def perform(clip, t):
    if not getattr(clip, 'PERFORM', True):
        return clip.sample(t)
    if getattr(clip, '_perf', None) is None or clip._perf.T != clip.duration:
        clip._perf = Performance(clip)
    return clip._perf.apply(clip.sample(t), t)
