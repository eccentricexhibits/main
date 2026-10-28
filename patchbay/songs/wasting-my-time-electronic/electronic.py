"""Wasting My Time, electronic arrangement: built from v18 (the approved orchestral version).

Revision 2: the pickups into each pre-chorus (violins I's A4, the oboes' "F . F") were being
dropped at the verse/pre-chorus boundary; they're routed now.
Revision 3: bar 6's descending figure (0:07) on the lead; the bridge's first bars (1:29) filled
with a reverse-cymbal swell, a fading warm pad and the harp sweeps on the pluck.

usage: python3 electronic.py [out folder]   (default: this script's folder)

The melody, harmony, form, tempo map (including the 156→228 BPM ending) and the cold hit all
come from v18 unchanged. What changes is who plays them and what plays underneath:

1. ROUTES re-voices v18's lines, section by section, onto synths: the verse tune on a soft
   lead, the hook on a saw lead, Violin II/viola figures on a pluck, harp on e-piano,
   glockenspiel and bells on a crystal bell, horns on mellow synth brass, the bridge's string
   pad on an evolving pad wall, its tremolo strings as a trance gate. v18's orchestral bass and
   percussion are left out; parts 2-6 below replace them.
2. Drums (808/909 kit): half-time in the verses, a two-step break in the choruses, four on the
   floor in the accelerating ending. Fills at section ends, crashes on downbeats.
3. Bass: a sine sub on every chord root, plus a saw bass whose rhythm follows the drums.
4. Pads from the chord chart (CHART), voice-led, and "sidechain" pumping (CC11 ducks at each
   kick) in the driving sections.
5. Dotted-8th echoes of the leads, noise risers with a pitch sweep, reverse cymbals and 808
   booms into the big downbeats.
6. The bridge stays pad/string-centred (no brass), with deep reverb, as in v18.

The verse tune (V1 cello, V2 viola) is played an octave up, at G4-A4 like verse 3, so the
three verses sit in the same register on the lead synth.
"""
import mido, pathlib, sys, math, json, random, collections

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / 'wasting-my-time-v18'
SRC_A = SRC / 'Wasting_My_Time_orchestral_VI_part1_winds_brass (v18).mid'
SRC_B = SRC / 'Wasting_My_Time_orchestral_VI_part2_perc_harp_strings (v18).mid'
OUT_A = 'Wasting_My_Time_electronic_part1_synths.mid'
OUT_B = 'Wasting_My_Time_electronic_part2_drums_bass_fx.mid'
BAR, BEAT = 1920, 480
T = lambda bar, beat=1: int(round((bar - 1) * BAR + (beat - 1) * BEAT))
NN = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
rnd = random.Random(156)   # fixed seed: the same humanising every run

# ---------------------------------------------------------------- form
# (first bar, last bar + 1, kind). Kinds drive drums, bass, pads and levels.
SECTIONS = [(1, 5, 'intro'), (5, 7, 'inter'), (7, 13, 'verse'), (13, 17, 'pre'), (17, 21, 'chorus'),
            (21, 27, 'verse'), (27, 31, 'pre'), (31, 35, 'chorus'), (35, 38, 'tag'), (38, 40, 'break'),
            (40, 46, 'verse'), (46, 50, 'pre'), (50, 54, 'chorus'), (54, 57, 'tag'), (57, 59, 'break'),
            (59, 71, 'bridge'), (71, 73, 'inter2'), (73, 79, 'verse4'), (79, 83, 'pre'), (83, 89, 'final'),
            (89, 92, 'tag'), (92, 94, 'break'), (94, 100, 'outro'), (100, 108, 'ending'), (108, 110, 'hit')]
def section(bar):
    for a, b, k in SECTIONS:
        if a <= bar < b: return a, b, k
    return SECTIONS[-1]

# ---------------------------------------------------------------- chord chart (two chords per bar)
def C(name, bass=None):
    """'Gm7' → (pitch classes, bass pc). Small chord vocabulary, enough for this song."""
    q = {'': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'm7': [0, 3, 7, 10], 'maj7': [0, 4, 7, 11],
         'add9': [0, 4, 7, 2], 'm11': [0, 3, 7, 5], 'sus': [0, 5, 7, 10], '9': [0, 4, 7, 10, 2], 'm7add11': [0, 3, 7, 10, 5], '5': [0, 7]}
    root = name[:2] if len(name) > 1 and name[1] in '#b' else name[:1]
    r = NN[root]; pcs = [(r + i) % 12 for i in q[name[len(root):]]]
    return pcs, NN[bass] if bass else r
VERSE = [('A7',), ('A7',), ('Dm',), ('C',), ('Bbmaj7',), ('A7',), ('Dm',), ('C',), ('Bbmaj7',), ('A7',), ('Dm',), ('Dm',)]
PRE = [('Gsus',), ('Gsus',), ('B', 'F#'), ('B', 'C#'), ('Ebm7',), ('Ebm7',), ('D7', 'A'), ('D7',)]
CHORUS = [('Gm7',), ('C7',), ('F',), ('F',)] * 2
INTRO = [('Am',), ('Bbmaj7',), ('Gm7',), ('C',)] * 2
INTER = [('F',), ('F',), ('F', 'C'), ('F',)]
TAG = [('Gm7',), ('C7',), ('F',), ('F',), ('F', 'C'), ('F', 'A')]
BREAK = [('Dm11',)] * 4
BRIDGE = [('Am7',), ('Bbadd9', 'A'), ('Gm7add11',), ('C9',)] * 6
OUTRO = [('Am',), ('Bbmaj7',), ('Gm7',), ('C',), ('Am',), ('Bbmaj7',), ('Gm7',), ('C',), ('F',), ('F',), ('F', 'C'), ('F', 'A')]
KIND_CHART = {'intro': INTRO, 'inter': INTER, 'inter2': INTER, 'verse': VERSE, 'verse4': VERSE, 'pre': PRE,
              'chorus': CHORUS, 'final': CHORUS + CHORUS[:4], 'tag': TAG, 'break': BREAK, 'bridge': BRIDGE,
              'outro': OUTRO, 'ending': [('Dm11',)] * 16, 'hit': [('D5',)] * 4}
CHART = {}   # (bar, half) → (pcs, bass pc)
for a, b, k in SECTIONS:
    seq = KIND_CHART[k]
    for i in range((b - a) * 2):
        CHART[(a + i // 2, i % 2)] = C(*seq[i % len(seq)])
def chord_at(bar, half): return CHART[(bar, half)]

# ---------------------------------------------------------------- instruments
# role: (file, channel 1-16, track name, bank MSB, program 0-based, CC7, pan -64..63, reverb CC91)
ROLES = {
    'lead_v':  ('A', 1, 'Lead (verse tune)', 0, 83, 127, 0, 50),        # Chiffer Lead: soft, breathy
    'lead':    ('A', 2, 'Lead (hook)', 0, 81, 127, 0, 45),               # Saw Lead
    'harm':    ('A', 3, 'Lead (harmony)', 1, 81, 104, -22, 45),           # Saw Wave
    'stack':   ('A', 4, 'Saw stack (octave)', 11, 100, 96, 22, 55),      # Bright Saw Stack
    'echo':    ('A', 5, 'Lead echo', 0, 81, 96, 40, 70),                 # Saw Lead, dotted-8th repeats
    'pad':     ('A', 6, 'Pad (warm)', 0, 89, 78, 0, 70),                 # Warm Pad
    'pump':    ('A', 7, 'Pad (pumping)', 11, 50, 104, 0, 60),             # Synth Strings 4
    'wall':    ('A', 8, 'Pad (bridge wall)', 11, 89, 92, 0, 100),        # Solar Wind
    'strings': ('A', 9, 'Synth strings', 8, 50, 88, -12, 80),            # Synth Strings 3
    'arp':     ('A', 11, 'Pluck', 1, 98, 84, -18, 55),                   # Synth Mallet
    'bells':   ('A', 12, 'Bells', 0, 98, 70, 26, 80),                    # Crystal
    'ep':      ('A', 13, 'E-piano', 8, 4, 76, -10, 60),                  # Chorused Tine EP
    'brass':   ('A', 14, 'Synth brass', 8, 62, 96, 10, 55),              # Synth Brass 3 (mellow, capped)
    'choir':   ('A', 15, 'Choir pad', 0, 91, 80, 0, 100),                # Space Voice
    'counter': ('A', 16, 'Counter lead', 12, 80, 100, 16, 60),            # Square Lead 2
    'sub':     ('B', 1, 'Sub bass', 8, 80, 92, 0, 0),                   # Sine Wave
    'bass':    ('B', 2, 'Saw bass', 12, 38, 78, 0, 10),                  # Mean Saw Bass
    'gate':    ('B', 3, 'Gated pad', 0, 90, 76, 0, 70),                  # Polysynth, 16th trance gate
    'stab':    ('B', 4, 'Stab', 11, 81, 100, 0, 50),                      # Sawtooth Stab
    'riser':   ('B', 5, 'Riser (noise)', 12, 122, 64, 0, 90),            # White Noise Wave + pitch sweep
    'revcym':  ('B', 6, 'Reverse cymbal', 0, 119, 74, 0, 80),            # Reverse Cymbal
    'boom':    ('B', 7, '808 boom', 8, 118, 84, 0, 40),                  # 808 Tom
    'echo_v':  ('B', 8, 'Verse lead echo', 0, 83, 90, -36, 70),          # Chiffer Lead repeats
    'kick':    ('B', 10, 'Kick', 0, 25, 120, 0, 8),                      # 808/909 kit on channel 10
    'snare':   ('B', 10, 'Snare · Clap', 0, 25, 110, 0, 30),
    'hats':    ('B', 10, 'Hats · Shaker', 0, 25, 90, 0, 20),
    'cym':     ('B', 10, 'Crash · Ride', 0, 25, 84, 0, 45),
}
KICK, SNARE, CLAP, RIM, CH, PH, OH, CRASH, RIDE, SHAKER, TOM_L, TOM_M, TOM_H = 36, 38, 39, 37, 42, 44, 46, 49, 51, 70, 41, 45, 48

# ---------------------------------------------------------------- read v18
def read_notes(path):
    """{track name: [(start, end, pitch, velocity)]}, with the sustain pedal baked into lengths."""
    out = {}
    for tr in mido.MidiFile(path).tracks:
        name = next((m.name for m in tr if m.type == 'track_name'), '')
        t = 0; on = {}; ns = []; pedal = False; held = []
        for m in tr:
            t += m.time
            if m.type == 'control_change' and m.control == 64:
                if m.value < 64 and pedal:
                    for n in held: n[1] = max(n[1], t)
                    held = []
                pedal = m.value >= 64
            elif m.type == 'note_on' and m.velocity: on[m.note] = (t, m.velocity)
            elif m.type in ('note_on', 'note_off') and m.note in on:
                s, v = on.pop(m.note); n = [s, t, m.note, v]; ns.append(n)
                if pedal: held.append(n)
        if ns: out[name] = [tuple(n) for n in ns]
    return out
SRCN = {**read_notes(SRC_A), **read_notes(SRC_B)}
CONDUCTOR = mido.MidiFile(SRC_A).tracks[0]

# ---------------------------------------------------------------- routing
# (track name or its first word(s), first bar, last bar + 1, role, options). The first matching rule wins;
# notes no rule matches are dropped (v18's bass and percussion: their jobs are regenerated).
# options: tr = transpose, vel = velocity scale, vmax = velocity cap, maxlen = length cap in beats,
# beat_from / beat_to = only notes starting in that part of the bar, spill = bars a long lead note may ring past the range,
# short = (beats, role) send notes shorter than that to another role, gate = chop into 16ths, echo = add dotted-8th repeats.
ROUTES = []
def R(src, a, b, role, **o): ROUTES.append((src, a, b, role, o))
for a, b, k in SECTIONS:
    if k == 'intro':
        R('Violin I', a, b, 'arp', vel=0.95, echo='arp'); R('Flute', a, b, 'bells', vel=0.8)
    elif k in ('inter', 'inter2'):
        if k == 'inter':   # bar 6's descending F-major figure is the tune here: oboes on the lead, clarinets under
            R('Oboe', a + 1, b, 'lead', echo='echo'); R('Clarinet', a + 1, b, 'harm', vel=0.9)
        R('Violin I', a, b, 'lead', vel=0.9, echo='echo'); R('Violin II', a, b, 'harm', vel=0.85)
        R('Clarinet', a, b, 'arp', vel=0.9); R('Oboe', a, b, 'bells', vel=0.7)
    elif k == 'verse':
        R('Violoncello' if a in (7, 40) else 'Viola', a, b, 'lead_v', tr=12 if a in (7, 21) else 0, vel=1.0, echo='echo_v')
        if a == 7: R('Violin II', a, b, 'arp', vel=1.05)
        if a == 21: R('Violin II', a, b, 'arp', vel=1.0, maxlen=0.45); R('Bassoon', a, b, 'counter', tr=12, vel=0.85)
        if a == 40: R('Viola', a, b, 'arp', vel=0.95)
        R('Harp', a, b, 'ep', vel=0.62)
    elif k == 'verse4':
        R('Violin I', a, b, 'lead', echo='echo'); R('Violin II', a, b, 'harm', vel=0.9)
        R('Viola', a, b, 'arp'); R('Harp', a, b, 'ep', vel=0.6); R('Horn 1·2', a, b, 'brass', vmax=92)
    elif k == 'pre':
        R('Violin I', a, b, 'lead', echo='echo'); R('Flute', a, b, 'bells', vel=0.75)
        R('Violin II', a, b, 'arp', vel=0.95); R('Horn 1·2', a, b, 'brass', vmax=90)
    elif k in ('chorus', 'final'):
        R('Violin I', a, b, 'lead', echo='echo'); R('Violin II', a, b, 'harm', vel=0.9)
        R('Flute', a, b, 'stack', vel=0.85, short=(0.3, 'bells'))
        R('Viola', a, b, 'arp', vel=0.92); R('Horn 1·2', a, b, 'brass', vmax=92)
        R('Trumpet', a, b, 'stab', vmax=96, vel=0.85); R('Harp', a, b, 'ep', vel=0.55)
    elif k == 'tag':
        R('Violin I', a, b, 'lead'); R('Violin II', a, b, 'harm', vel=0.9)
        R('Flute', a, b, 'bells', vel=0.55); R('Trumpet', a, b, 'stab', vmax=96, vel=0.85)
        R('Viola', a, b, 'arp', vel=0.9); R('Horn 1·2', a, b, 'brass', vmax=90)
    elif k == 'break':
        R('Violin I', a, b, 'lead', vel=0.8, echo='echo'); R('Violin II', a, b, 'harm', vel=0.75)
        R('Viola', a, b, 'arp', vel=0.8)
    elif k == 'bridge':
        R('Violin I', a, b, 'lead', echo='echo'); R('Solo Violin', a, b, 'counter', vel=0.95)
        R('Violin II', a, b, 'harm', vel=0.85); R('Viola', a, b, 'strings'); R('Violoncello', a, b, 'strings', vel=0.9)
        R('Strings (pad)', a, b, 'wall'); R('Strings (tremolo)', a, b, 'gate', gate=True)
        R('Strings (pizzicato)', a, b, 'arp', vel=1.0)
        R('Harp', a, a + 3, 'arp', vel=1.05); R('Harp', a, b, 'bells', vel=0.55)   # sweeps on the pluck while the wall swells in
        R('Choir', a, b, 'choir'); R('Piano', a, b, 'ep', vel=0.9)
    elif k == 'outro':
        R('Violin I', a, b, 'arp', vel=0.95, echo='arp'); R('Flute', a, b, 'counter', vel=0.9)
    elif k == 'ending':
        R('Violin II', a, b, 'lead'); R('Violin I', a, b, 'stack', vel=0.85)
        R('Harp', a, b, 'arp', vel=0.9); R('Strings (tremolo)', a, b, 'gate', gate=True)
        R('Choir', a, b, 'choir'); R('Piano (melody)', a, b, 'ep', vel=0.85)
        R('Horn 1·2', a, b, 'brass', vmax=92); R('Trumpet', a, b, 'stab', vmax=96, vel=0.8)
    elif k == 'hit':
        R('Violin I', a, b, 'lead'); R('Violin II', a, b, 'harm'); R('Trumpet', a, b, 'stab', vmax=110)
        R('Horn 1·2', a, b, 'brass', vmax=100)
# Pickups that start in a verse's last bar but belong to what follows: violins I's A4 on beat 4,
# the pre-chorus melody's first note, and the oboes' "F . F" answer on beats 2-2½.
for a, b, k in SECTIONS:
    if k in ('verse', 'verse4'):
        if k == 'verse': R('Violin I', b - 1, b, 'lead', echo='echo', beat_from=4)
        R('Oboe', b - 1, b, 'counter', vel=1.0, beat_from=2, beat_to=3)
R('Glockenspiel', 1, 108, 'bells', vel=0.85); R('Tubular', 1, 108, 'bells', vel=0.9)

LEADS = ('lead_v', 'lead', 'harm', 'stack', 'counter', 'echo', 'echo_v')
NOTES = collections.defaultdict(list)   # role → [(start, end, pitch, velocity)]
ROLE_VEL = {'lead_v': 1.3, 'lead': 1.25, 'harm': 1.1, 'counter': 1.1}   # the leads' presets are quieter than the beds
def add(role, s, e, p, v): NOTES[role].append((int(s), int(max(e, s + 10)), int(p), int(max(1, min(127, round(v * ROLE_VEL.get(role, 1)))))))
ECHO = collections.defaultdict(list)
for name, ns in SRCN.items():
    for s, e, p, v in ns:
        bar = s // BAR + 1
        for src, a, b, role, o in ROUTES:
            if (name == src or name.startswith(src + ' ')) and a <= bar < b and \
               (o.get('beat_from', 1) - 1) * BEAT <= s % BAR < (o.get('beat_to', 5) - 1) * BEAT: break
        else: continue
        p += o.get('tr', 0); v = min(v * o.get('vel', 1.0), o.get('vmax', 127))
        if 'short' in o and (e - s) < o['short'][0] * BEAT: role = o['short'][1]
        if 'maxlen' in o: e = min(e, s + int(o['maxlen'] * BEAT))
        if role in LEADS and e - s > 4 * BEAT:   # a long held orchestral tail would drone on a synth lead
            e = min(e, T(b + o.get('spill', 0)))
        if o.get('gate'):   # trance gate: 16th slices, every other one accented
            for i, t in enumerate(range(s, e, 120)): add(role, t, min(t + 84, e), p, v * (1.0 if i % 2 == 0 else 0.72))
            continue
        add(role, s, e, p, v)
        if 'echo' in o: ECHO[o['echo']].append((s, e, p, v))

# Dotted-8th delay: two repeats, the second quieter. Kept short so they don't blur the line.
for role, ns in ECHO.items():
    for s, e, p, v in ns:
        for k, g in ((1, 0.42), (2, 0.2)):
            d = 360 * k; add(role, s + d, s + d + min(e - s, 300), p, v * g)

# ---------------------------------------------------------------- pads from the chart (voice-led)
def voicing(pcs, prev, lo=52, hi=74, n=4):
    """n chord tones between lo and hi, as close as possible to the previous voicing."""
    cands = [p for p in range(lo, hi + 1) if p % 12 in pcs]
    best = None
    import itertools
    for combo in itertools.combinations(cands, min(n, len(cands))):
        if len({c % 12 for c in combo}) < min(len(pcs), n): continue
        if max(combo) - min(combo) > 16: continue
        cost = sum(min(abs(c - q) for q in prev) for c in combo) if prev else abs(sum(combo) / len(combo) - (lo + hi) / 2)
        if best is None or cost < best[0]: best = (cost, combo)
    return list(best[1]) if best else sorted(cands)[:n]
def chord_pad(role, a, b, vel, lo=52, hi=74, n=4, split=False):
    prev = None; seg = []
    for bar in range(a, b):
        for h in (0, 1):
            pcs, _ = chord_at(bar, h); t0 = T(bar, 1 + 2 * h)
            if seg and seg[-1][0] == pcs and not split: seg[-1][2] = t0 + 2 * BEAT
            else: seg.append([pcs, t0, t0 + 2 * BEAT])
    for pcs, s, e in seg:
        prev = voicing(pcs, prev, lo, hi, n)
        for p in prev: add(role, s, e - 6, p, vel)
for a, b, k in SECTIONS:
    if k == 'intro': chord_pad('pad', a, b, 70)
    elif k in ('verse', 'pre', 'break'): chord_pad('pad', a, b, 74 if k != 'break' else 66)
    elif k in ('inter',): chord_pad('pad', a, b, 80)
    elif k == 'outro': chord_pad('pad', a, b, 70)
    elif k == 'bridge': chord_pad('pad', a, a + 3, 92)   # fills the bridge's opening, fading as the slow wall arrives
    elif k in ('chorus', 'tag', 'verse4', 'final', 'inter2'): chord_pad('pump', a, b, 88, lo=55, hi=79, split=True)
    elif k == 'ending': chord_pad('pump', a, b, 92, lo=55, hi=79, split=True)

# ---------------------------------------------------------------- drums
# Each verse's accompaniment, a little further back: the verse tune measures V1 +2.2, V2 +2.2, V3 +1.6 dB
# over the rest, the balance the user settled on for v18 (mix minus solo render, as tools/verse_balance.js).
VERSE_REST = {7: -1.0, 21: -2.2, 40: -1.7}
def trim(t, role=None):
    """Section trim in dB, applied to every part (CC11) and drum velocities: the verses sit 2.5 dB back so the drops land."""
    bar = t // BAR + 1; a, b, k = section(bar)
    if k == 'verse': return -2.5 + (0 if role in LEADS else VERSE_REST[a])
    if k == 'pre': x = (t - T(a)) / (T(b) - T(a)); return (-1.0 + 1.0 * x) if a == 79 else (-2.5 + 2.0 * x)   # after verse 4: from its level
    if k in ('verse4', 'outro'): return -1.0
    return 0.0
g40 = lambda db: 10 ** (db / 40)   # engine gain is (CC/127)^2 on CC7 and CC11, and velocity works much the same
def hit(role, t, p, v, d=110): add(role, t, t + d, p, v * g40(trim(t, role)) * (0.94 + 0.08 * rnd.random()))
KICKS = []
def kick(t, v): hit('kick', t, KICK, v); KICKS.append(t)
def drum_bar(bar, style, e=1.0):
    t = T(bar)
    if style == 'pulse':
        kick(t, 80 * e); kick(t + 2 * BEAT, 64 * e)
    elif style == 'half':     # half-time: kick 1 (and the and of 2), clap on 3
        kick(t, 104 * e); kick(t + int(1.5 * BEAT), 78 * e)
        hit('snare', t + 2 * BEAT, CLAP, 100 * e); hit('snare', t + 2 * BEAT, SNARE, 70 * e)
        if bar % 2 == 0: hit('snare', t + int(3.75 * BEAT), SNARE, 40 * e, 60)
        for i in range(8): hit('hats', t + i * 240, CH, (62 if i % 2 else 50) * e, 60)
    elif style == 'two':      # two-step break: kick 1 + the and of 3, snare 2 and 4
        kick(t, 110 * e); kick(t + int(2.5 * BEAT), 96 * e)
        if bar % 2 == 0: kick(t + int(3.25 * BEAT), 70 * e)
        for bt in (1, 3): hit('snare', t + bt * BEAT, SNARE, 108 * e); hit('snare', t + bt * BEAT, CLAP, 84 * e)
        hit('snare', t + int(1.75 * BEAT), SNARE, 38 * e, 60)
        for i in range(16):
            if i == 14 and bar % 2: hit('hats', t + i * 120, OH, 66 * e, 200); continue
            hit('hats', t + i * 120, CH, (70 if i % 4 == 2 else 52 if i % 2 == 0 else 38) * e, 50)
    elif style == 'four':     # four on the floor, open hats on the off-beats
        for bt in range(4):
            kick(t + bt * BEAT, 112 * e); hit('hats', t + bt * BEAT + 240, OH, 70 * e, 160)
            hit('hats', t + bt * BEAT + 120, CH, 44 * e, 50); hit('hats', t + bt * BEAT + 360, CH, 44 * e, 50)
        for bt in (1, 3): hit('snare', t + bt * BEAT, CLAP, 104 * e); hit('snare', t + bt * BEAT, SNARE, 80 * e)
    elif style == 'stomp':    # quarter-note chords in the tags' last bar
        for bt in range(4): kick(t + bt * BEAT, 104 * e); hit('snare', t + bt * BEAT, CLAP, 96 * e)
    elif style == 'hats':
        for i in range(8): hit('hats', t + i * 240, CH, (54 if i % 2 else 40) * e, 60)
    if style in ('half', 'two') and bar % 2 == 1:
        for i in range(16): hit('hats', t + i * 120, SHAKER, (40 if i % 2 else 30) * e, 60)
def fill(bar, beats=1, e=1.0):
    """16th snare/tom fill over the last `beats` beats of the bar."""
    t0 = T(bar, 5 - beats); n = beats * 4
    for i in range(n): hit('snare', t0 + i * 120, [SNARE, SNARE, TOM_H, TOM_M, TOM_L][min(4, i * 5 // n)] if beats == 1 else SNARE, (60 + 50 * i / n) * e, 80)
def roll(a, b, v0, v1, step=120, last32=False):
    """Snare roll from tick a to b with a crescendo; 32nds over the last beat if asked."""
    t = a
    while t < b:
        st = 60 if last32 and t >= b - BEAT else step
        hit('snare', t, SNARE, v0 + (v1 - v0) * (t - a) / max(1, b - a), 50); t += st
def crash(t, v=100): hit('cym', t, CRASH, v, 400)
for bar in range(1, 109):
    a, b, k = section(bar); last = bar == b - 1; i = bar - a
    if k == 'intro':
        if bar >= 3: drum_bar(bar, 'pulse', 0.8 + 0.1 * (bar - 3))
        if bar == 4: roll(T(4, 3), T(5), 40, 96)
    elif k == 'inter':
        drum_bar(bar, 'half', 0.82);  crash(T(bar)) if i == 0 else fill(bar, 1, 0.8)
    elif k == 'verse':
        drum_bar(bar, 'half', 0.72 if a == 7 else 0.76)
        if last: fill(bar, 1, 0.75)
    elif k == 'pre':
        if i < 2: drum_bar(bar, 'half', 0.8)
        elif i == 2: drum_bar(bar, 'two', 0.84)
        else:   # the last bar: kick on 1 and 2, then a roll into the drop
            kick(T(bar), 108); kick(T(bar, 2), 100); roll(T(bar), T(bar + 1), 50, 112, last32=True)
    elif k in ('chorus', 'final', 'verse4', 'inter2'):
        drum_bar(bar, 'two', 0.92 if k == 'verse4' else 1.0)
        if i == 0: crash(T(bar), 108)
        if k == 'final':
            for bt in range(4): hit('cym', T(bar, bt + 1), RIDE, 58, 200)
            if i == 4: crash(T(bar), 96)
        if last: fill(bar, 1, 0.95)
    elif k == 'tag':
        if last: drum_bar(bar, 'stomp')
        else: drum_bar(bar, 'two'); crash(T(bar), 104) if i == 0 else None
    elif k == 'break':
        drum_bar(bar, 'hats', 0.85 - 0.25 * i)
    elif k == 'bridge':   # 59-61 none, 62-64 sparse, 65-67 half-time, 68-69 two-step, 70 roll
        if 62 <= bar <= 64:
            kick(T(bar), 84); hit('snare', T(bar, 3), RIM, 70)
            if bar >= 63: drum_bar(bar, 'hats', 0.8)
        elif 65 <= bar <= 67: drum_bar(bar, 'half', 0.9)
        elif bar in (68, 69): drum_bar(bar, 'two', 0.95); crash(T(bar), 92) if bar == 68 else None
        elif bar == 70: [kick(T(70, bt), 100 + 4 * bt) for bt in (1, 2, 3, 4)]; roll(T(70), T(71), 46, 118, last32=True)
    elif k == 'outro':
        if bar <= 97: drum_bar(bar, 'half', 0.7)
        elif bar == 98: kick(T(98), 90); roll(T(98), T(99), 34, 70, step=240)
        else: kick(T(99), 98); kick(T(99, 3), 100); roll(T(99), T(100), 60, 112, last32=True)
    elif k == 'ending':   # 100-102 two-step, 103-105 four on the floor, 106-107 + a snare roll
        if bar <= 102: drum_bar(bar, 'two', 0.96 + 0.02 * i)
        else: drum_bar(bar, 'four', 1.0)
        if bar in (100, 103, 106): crash(T(bar), 110)
        if bar >= 106: roll(T(bar), T(bar + 1), 70 + 20 * (bar - 106), 100 + 18 * (bar - 106), last32=bar == 107)
# The cold hit
kick(T(108), 124); hit('snare', T(108), CLAP, 120); hit('snare', T(108), SNARE, 110); crash(T(108), 124)
hit('cym', T(108), 57, 118, 600)

# ---------------------------------------------------------------- bass
def oct_into(pc, lo):  # the pitch with class pc in [lo, lo+11]
    return lo + (pc - lo) % 12
for bar in range(3, 109):
    a, b, k = section(bar)
    for h in (0, 1):
        _, r = chord_at(bar, h); t0 = T(bar, 1 + 2 * h); sub = oct_into(r, 28); mid = oct_into(r, 40)
        if not (k == 'bridge' and bar < 59) and k != 'hit':
            add('sub', t0, t0 + 2 * BEAT - 8, sub, 96 if k != 'intro' else 60 + 12 * (bar - 3))
        if k in ('verse', 'inter') or (k == 'pre' and bar - a < 2) or (k == 'bridge' and 65 <= bar <= 67) or (k == 'outro' and bar <= 97):
            add('bass', t0, t0 + int(0.8 * BEAT), mid, 92); add('bass', t0 + int(1.5 * BEAT), t0 + int(1.9 * BEAT), mid, 76)
        elif k in ('chorus', 'final', 'verse4', 'tag', 'inter2', 'pre') or (k == 'bridge' and bar >= 68) or (k == 'outro') or (k == 'ending' and bar <= 102):
            for j in range(4):   # driving 8ths, octave on the third
                add('bass', t0 + j * 240, t0 + j * 240 + 190, mid + (12 if j == 2 else 0), [100, 78, 88, 80][j])
        elif k == 'ending':      # off-beat bass under four on the floor, 16ths in the last two bars
            if bar < 106:
                for j in range(2): add('bass', t0 + j * BEAT + 240, t0 + j * BEAT + 440, mid, 96)
            else:
                for j in range(8): add('bass', t0 + j * 120, t0 + j * 120 + 100, mid + (12 if j % 4 == 2 else 0), 84 + 3 * j)
add('sub', T(108), T(108) + 700, 38, 120); add('bass', T(108), T(108) + 600, 50, 116)

# ---------------------------------------------------------------- FX: risers, reverse cymbals, booms, stabs
RISERS = [(3, 5), (15, 17), (29, 31), (48, 50), (68, 71), (81, 83), (98, 100), (104, 108)]
BEND = collections.defaultdict(list)   # role → [(tick, value)]
for a, b in RISERS:
    s, e = T(a), T(b); add('riser', s, e, 60, 100)
    n = (e - s) // 60
    for j in range(n + 1): BEND['riser'].append((s + j * 60, int(-8192 + 16383 * (j / n) ** 1.6)))
    BEND['riser'].append((e + 30, 0))
for target in (5, 17, 31, 40, 50, 59, 62, 66, 71, 83, 100):   # a reverse cymbal swelling into each
    add('revcym', T(target) - BAR, T(target), 60, 96)
for target in (17, 31, 50, 59, 62, 64, 66, 68, 71, 83, 100, 108):
    add('boom', T(target), T(target) + 2 * BEAT, 38, 110 if target not in (59, 62, 64) else 84)
for target in (17, 31, 50, 83):   # a chord stab on each chorus downbeat
    pcs, _ = chord_at(target, 0)
    for p in voicing(pcs, None, 58, 76, 4): add('stab', T(target), T(target) + 300, p, 98)
for p in (50, 57, 62, 69): add('stab', T(108), T(108) + 400, p, 112)

# ---------------------------------------------------------------- levels (CC11), sidechain, reverb
def level(role, bar):
    """Base expression for a role in a bar (0-127): verses sit back, the drops come forward."""
    a, b, k = section(bar); f = (bar - a) / max(1, b - a - 1)
    if role in ('riser', 'revcym', 'boom', 'kick', 'snare', 'hats', 'cym', 'stab'): return 120
    if role in LEADS: return 112 if k == 'break' else 124
    drop = k in ('chorus', 'final', 'tag', 'verse4', 'inter2')
    if role in ('sub', 'bass') and k in ('verse', 'pre'): return 98 if k == 'verse' else int(100 + 16 * f)
    if drop: return 118 if role in ('sub', 'bass') else 124 if role in ('gate', 'choir', 'wall') else 112   # room for the hook
    if k == 'intro': return int(80 + 30 * f)
    if k == 'inter': return 116
    if k == 'verse': return 104
    if k == 'pre': return int(106 + 16 * f)
    if k == 'break': return 92
    if k == 'bridge' and role == 'pad': return (112, 98, 80)[min(2, bar - 59)]
    if k == 'bridge':
        return int(84 + 36 * (bar - 59) / 11) if role in ('wall', 'strings', 'gate', 'choir', 'arp', 'bells', 'sub') else 112
    if k == 'outro': return 98 if bar < 98 else int(100 + 12 * (bar - 98))
    if k == 'ending': return int(112 + 15 * (bar - 100) / 7)
    return 124
PUMP = {'pump': 0.5, 'sub': 0.5, 'bass': 0.28, 'gate': 0.4, 'arp': 0.18, 'wall': 0.25, 'choir': 0.2}
PUMP_KINDS = ('chorus', 'final', 'verse4', 'tag', 'inter2', 'ending')
kicks = sorted(set(KICKS))
import bisect
def cc11_curve(role):
    out = []; last = None
    for t in range(0, T(110), 30):
        bar = t // BAR + 1; v = level(role, bar) * g40(trim(t, role))
        a, b, k = section(bar)
        if role in PUMP and (k in PUMP_KINDS or (k == 'bridge' and bar >= 68) or role == 'sub'):
            i = bisect.bisect_right(kicks, t) - 1
            if i >= 0 and t - kicks[i] < BEAT:
                x = (t - kicks[i]) / BEAT; depth = PUMP[role] * (1 if role != 'sub' or k in PUMP_KINDS else 0.6)
                v *= 1 - depth * (1 - x) ** 2.2
        v = int(max(0, min(127, round(v))))
        if v != last: out.append((t, v)); last = v
    return out
REVERB_BRIDGE = ('lead', 'harm', 'counter', 'strings', 'wall', 'arp', 'bells', 'ep', 'choir', 'echo')

# ---------------------------------------------------------------- write
def build(file_tag):
    mf = mido.MidiFile(type=1, ticks_per_beat=480)
    cond = mido.MidiTrack(); t = 0
    for m in CONDUCTOR:
        if m.type == 'track_name':
            cond.append(m.copy(name=f'Wasting My Time (electronic) - part {"1 of 2: synths" if file_tag == "A" else "2 of 2: drums, bass and FX"}'))
        else: cond.append(m.copy())
    mf.tracks.append(cond)
    for role, (f, ch, name, bank, prog, vol, pan, rev) in ROLES.items():
        if f != file_tag: continue
        c = ch - 1; ev = []
        drums = c == 9
        first_drum = drums and role == next(r for r, x in ROLES.items() if x[0] == file_tag and x[1] == 10)   # sets the file's kit
        if not drums or first_drum:
            ev += [(0, 0, mido.Message('control_change', channel=c, control=0, value=bank)),
                   (0, 0, mido.Message('control_change', channel=c, control=32, value=0)),
                   (0, 1, mido.Message('program_change', channel=c, program=prog))]
        if not drums:
            ev += [(0, 2, mido.Message('control_change', channel=c, control=7, value=vol)),
                   (0, 2, mido.Message('control_change', channel=c, control=10, value=pan + 64)),
                   (0, 2, mido.Message('control_change', channel=c, control=91, value=rev))]
        else:   # channel 10 is shared: volume from each drum track applies to that track only
            ev += [(0, 2, mido.Message('control_change', channel=c, control=7, value=vol)),
                   (0, 2, mido.Message('control_change', channel=c, control=91, value=rev))]
        if role == 'riser':
            ev += [(0, 2, mido.Message('control_change', channel=c, control=101, value=0)),
                   (0, 2, mido.Message('control_change', channel=c, control=100, value=0)),
                   (0, 2, mido.Message('control_change', channel=c, control=6, value=12))]
        if not drums:
            for t, v in cc11_curve(role): ev.append((t, 2, mido.Message('control_change', channel=c, control=11, value=v)))
        if role in REVERB_BRIDGE:
            ev.append((T(59) - 10, 2, mido.Message('control_change', channel=c, control=91, value=min(127, rev + 50))))
            ev.append((T(71) - 10, 2, mido.Message('control_change', channel=c, control=91, value=rev)))
        for t, v in BEND.get(role, []): ev.append((t, 2, mido.Message('pitchwheel', channel=c, pitch=max(-8192, min(8191, v)))))
        # notes: sort, drop exact duplicates, and end a note early if the same key restarts
        ns = sorted(set(NOTES.get(role, [])))
        bykey = collections.defaultdict(list)
        for n in ns: bykey[n[2]].append(n)
        clean = []
        for p, L in bykey.items():
            L.sort()
            for j, (s, e, _, v) in enumerate(L):
                if j + 1 < len(L) and L[j + 1][0] < e: e = L[j + 1][0] - 1
                if j > 0 and s == L[j - 1][0]: continue
                if e > s: clean.append((s, e, p, v))
        for s, e, p, v in clean:
            ev.append((s, 3, mido.Message('note_on', channel=c, note=p, velocity=v)))
            ev.append((e, 0, mido.Message('note_off', channel=c, note=p, velocity=0)))
        ev.sort(key=lambda x: (x[0], x[1]))
        tr = mido.MidiTrack(); tr.append(mido.MetaMessage('track_name', name=name, time=0)); now = 0
        for t, _, m in ev: tr.append(m.copy(time=t - now)); now = t
        mf.tracks.append(tr)
    return mf
if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
    out.mkdir(parents=True, exist_ok=True)
    build('A').save(out / OUT_A); build('B').save(out / OUT_B)
    summary = {ROLES[r][2]: len(set(v)) for r, v in sorted(NOTES.items(), key=lambda x: (ROLES[x[0]][0], ROLES[x[0]][1]))}
    (out / 'electronic-parts.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print('wrote', OUT_A, OUT_B, '·', sum(summary.values()), 'notes'); print(json.dumps(summary, ensure_ascii=False))
