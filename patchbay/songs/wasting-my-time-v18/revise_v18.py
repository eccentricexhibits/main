"""Wasting My Time — revision 18.  Usage: python3 revise_v18.py <output folder>/
v18 = v17 with the verse 1 and 2 melody about 0.5 dB louder (it sits in the accompaniment's register there; verse 3 doesn't).
(History — revision 17:
v17 = v16 with the verse 1 and verse 3 melody matched to verse 2's level (about 1.6 dB over the rest).
(History — revision 16:
v16 = v15 with verse 2's melody halfway between v14 (too loud) and v15 (too quiet).
(History — revision 15:
v15 = v14 with verse 2's melody eased back a touch, and the ending reworked: no step back, five repeats
instead of eight, a new instrument joining on every repeat, and the percussion drives entering at full strength.
(History — revision 14:
v14 = v13 with the verse melody brought forward (verses 1-3) and a new ending: the closing figure repeats,
accelerating and building, before the same cold hit.
(History — revision 13:
v13 = v12 with a softer harp outside the bridge (its rolling arpeggios were reading as a piano).
(History — revision 12:
v12 = v11 with the rolling piano quiet and only at the end of the bridge (bars 68-70).
(History — revision 11:
v11 = v10's string-orchestra bridge + a soft choir at the climax (bars 68-70) + piano: the right hand supports the hook
(S2-S6), the left hand rolls arpeggios through the chords (8ths, then 16ths), pedalled with the harmony.
(History — revision 10:
v10 = v9's lush bridge turned into a string orchestra: winds, brass, choir and celesta sit out bars 59-70; a solo violin,
viola countermelody, tremolo strings and pizzicato join violins I/II, cellos, basses, the slow-string pad and a softer harp.
(History — revision 9:
v9 = v8's bridge melody (the chorus hook "Wasting all my time on you", six statements in its sung rhythm) in a very lush
setting: long bass notes, a slow string pad and a soft choir on enriched chords (Am7, Bb add9, Gm7 add11, C9), harp sweeps,
a high violin descant, celesta shimmer, swelling timpani/cymbals and much more reverb. No harpsichord. Everything else as v4/v5.
(History: revision 3.
v2 plus the user's notes: melancholic (not brighter) chorus answers and verse lines before verse 4,
a cleaned-up bridge / violin solo (bars 59-70, transcribed from the original guitar solo), and softer horns.
Reads the two ORIGINAL MIDI files, applies the edits below, writes "(v3)" copies and a change log."""
import mido, sys, json
import os
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wasting-my-time', '')   # the originals; run: python3 revise_v18.py <output folder>/
OUT = sys.argv[1] if len(sys.argv) > 1 else SRC
FILES = {'A': 'Wasting_My_Time_orchestral_VI_part1_winds_brass', 'B': 'Wasting_My_Time_orchestral_VI_part2_perc_harp_strings'}
BAR, Q, E8 = 1920, 480, 240
NN = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
nm = lambda p: NN[p % 12] + str(p // 12 - 1)
def at(bar, beat=1.0): return (bar - 1) * BAR + int(round((beat - 1) * Q))
log = []
HARP_SOFT = 0.72
HARP_VOL = 80

# ---------------------------------------------------------------- load: per track, notes + other events
class Track:
    def __init__(self, mtrack):
        self.name = ''; self.other = []; self.notes = []
        t = 0; open_ = {}
        for msg in mtrack:
            t += msg.time
            if msg.type == 'track_name': self.name = msg.name
            if msg.type == 'note_on' and msg.velocity > 0:
                open_.setdefault((msg.channel, msg.note), []).append((t, msg.velocity))
            elif msg.type in ('note_off', 'note_on'):
                k = (msg.channel, msg.note)
                if open_.get(k):
                    s, v = open_[k].pop(0)
                    self.notes.append({'s': s, 'e': t, 'p': msg.note, 'v': v, 'ch': msg.channel})
            elif msg.type != 'end_of_track':
                self.other.append((t, msg))
        self.ch = self.notes[0]['ch'] if self.notes else 0
    def at(self, t, pc=None, tol=12):
        return [n for n in self.notes if abs(n['s'] - t) <= tol and (pc is None or n['p'] % 12 == pc)]
    def window(self, t0, t1):
        return [n for n in self.notes if t0 <= n['s'] < t1]
    def add(self, s, e, p, v):
        self.notes.append({'s': int(s), 'e': int(e), 'p': int(p), 'v': max(1, min(127, int(v))), 'ch': self.ch})
    def to_mido(self):
        ev = [(t, 1, m) for t, m in self.other]
        for n in self.notes:
            ev.append((n['s'], 2, mido.Message('note_on', channel=n['ch'], note=n['p'], velocity=n['v'])))
            ev.append((n['e'], 0, mido.Message('note_off', channel=n['ch'], note=n['p'], velocity=0)))
        ev.sort(key=lambda x: (x[0], x[1]))
        tr = mido.MidiTrack(); last = 0
        for t, _, m in ev:
            tr.append(m.copy(time=t - last)); last = t
        tr.append(mido.MetaMessage('end_of_track', time=0))
        return tr

mids = {k: mido.MidiFile(SRC + v + '.mid') for k, v in FILES.items()}
tracks = {k: [Track(t) for t in m.tracks] for k, m in mids.items()}
def T(name):
    for k in tracks:
        for t in tracks[k]:
            if t.name == name: return t
    raise KeyError(name)
PERC = ('Snare', 'Bass Drum', 'Suspended', 'Timpani', 'Tubular', 'Harp')   # glockenspiel doubles the tune, so it is included
def melodic_tracks():
    return [t for k in tracks for t in tracks[k] if t.notes and not t.name.startswith(PERC)]
def split(t, n, at_tick):
    """Cut note n at at_tick; return the second half (already added to the track)."""
    m = dict(n); m['s'] = at_tick; n['e'] = at_tick - 10; t.notes.append(m); return m
def top(notes):  # highest note of a chord group
    return max(notes, key=lambda n: n['p']) if notes else None

# ---------------------------------------------------------------- 1. chorus answers
# The 2-bar chorus phrase is  Bb A Bb C | G (over C) | A  and it was never varied.
# 'cadence': ... C | D  E | F   (resolves to the tonic)      'question': ... C | D | C  (a step higher than G | A)
# 'sigh':    ... C | D  C | Bb→A  (reaches past C, then falls back with a 4-3 sigh onto the original A: melancholic)
def chorus_phrase(X, kind):
    x1, x3, y1, y2 = at(X), at(X, 3), at(X + 1), at(X + 2)
    for t in melodic_tracks():
        g = [top(t.at(at(X, b))) for b in (1, 1.5, 2, 2.5)]
        if any(n is None for n in g):
            # skeleton doubling: Bb (half) G (half) | A (whole)
            bb, gg, aa = t.at(x1, 10), t.at(x3, 7), t.at(y1, 9)
            if bb and gg and aa and bb[0]['e'] - bb[0]['s'] >= 3 * E8 and gg[0]['p'] == bb[0]['p'] - 3:
                b = bb[0]['p']; G = gg[0]; A = aa[0]
                if kind == 'cadence':
                    G['p'] = b + 4; mid = G['s'] + Q; e = G['e']; G['e'] = mid; t.add(mid, e, b + 6, G['v']); A['p'] = b + 7
                elif kind == 'sigh':
                    G['p'] = b + 4; mid = G['s'] + Q; e = G['e']; G['e'] = mid - 10; t.add(mid, e, b + 2, G['v'])
                    split(t, A, A['s'] + Q)['p'] = b - 1; A['p'] = b
                else:
                    G['p'] = b + 4; A['p'] = b + 2
                log.append(f"bar {X}-{X+1} {t.name}: skeleton line → {dict(cadence='D E | F', question='D | C', sigh='D C | Bb A')[kind]}")
            continue
        pcs = [n['p'] % 12 for n in g]
        chordal = len(t.at(x1)) >= 3
        if pcs == [10, 9, 10, 0]:                       # the tune itself (any octave)
            c = g[3]['p']
            if chordal:                                  # trumpets harmonise the tune in the last chorus
                old = [n for n in t.window(x3, y1)] + [n for n in t.at(y1)]
                v = old[0]['v'] if old else 90
                for n in old: t.notes.remove(n)
                for (s, e, chord) in ((x3, x3 + Q - 20, (c - 8, c - 2, c + 2)), (x3 + Q, y1 - 20, (c - 5, c, c + 4)), (y1, y1 + 4 * Q - 20, (c - 3, c, c + 5))):
                    for p in chord: t.add(s, e, p, v)
                log.append(f"bar {X}-{X+1} {t.name}: harmonised tune follows the new D E | F (C9 → C7 → F)")
                continue
            beats34 = [n for n in t.window(x3, y1) if n['p'] in (c - 5, c - 3)]
            nextbar = [n for n in t.window(y1, y2) if n['p'] in (c - 3, c - 2)]
            if kind == 'sigh':
                v = beats34[0]['v'] if beats34 else 90
                plain34 = all(n['p'] == c - 5 for n in beats34) and len(beats34) <= 2
                for n in beats34: t.notes.remove(n)
                t.add(x3, x3 + Q - 15, c + 2, v); t.add(x3 + Q, y1 - 10, c, v)               # D  C
                trill = len(nextbar) > 2
                if trill:                                                                       # keep the A-Bb trill after a plain Bb
                    for n in [n for n in nextbar if n['s'] < y1 + Q]: t.notes.remove(n)
                    t.add(y1, y1 + Q - 10, c - 2, v)
                else:
                    for n in nextbar:
                        if n['p'] == c - 3 and n['e'] - n['s'] > Q: split(t, n, n['s'] + Q); n['p'] = c - 2   # Bb (q) then A
                log.append(f"bar {X}-{X+1} {t.name}: tune C | D C | Bb-A sigh (was C | G | A) at {nm(c)}")
                continue
            plain = beats34 and all(n['p'] == c - 5 for n in beats34) and len(beats34) <= 2
            if plain and kind == 'cadence':              # long G (or two struck Gs) → D, E
                G = beats34[0]
                if len(beats34) == 1: e = G['e']; G['e'] = G['s'] + Q - 15; t.add(G['s'] + Q, e, c + 4, G['v'])
                else: beats34[1]['p'] = c + 4
                G['p'] = c + 2
            elif plain:                                  # question: G → D
                for n in beats34: n['p'] = c + 2
            else:                                        # trill: shift the whole figure
                for n in beats34: n['p'] += 7
            for n in t.window(x3, y1):                   # new notes stop at the bar line (a ringing glockenspiel E would clash with the F chord)
                if n['p'] in (c + 2, c + 4, c - 5 + 7, c - 3 + 7): n['e'] = min(n['e'], y1 - 10)
            for n in nextbar:
                n['p'] += (8 if n['p'] == c - 3 else 9) if kind == 'cadence' else (3 if n['p'] == c - 3 else 4)
            log.append(f"bar {X}-{X+1} {t.name}: tune {'C | D E | F' if kind=='cadence' else 'C | D | C'} (was C | G | A) at {nm(c)}")
        elif pcs == [7, 5, 7, 9]:                       # harmony a third below the tune
            a = g[3]['p']
            beats34 = [n for n in t.window(x3, y1) if n['p'] % 12 == 4]
            nextbar = [n for n in t.window(y1, y2) if n['p'] == a - 4]
            if kind == 'sigh':
                if len(beats34) == 1:
                    n = beats34[0]; e = n['e']; n['p'] = a + 1; n['e'] = n['s'] + Q - 15; t.add(n['s'] + Q, e, a, n['v'])
                elif len(beats34) >= 2: beats34[0]['p'] = a + 1; beats34[1]['p'] = a
                for n in nextbar:
                    if n['e'] - n['s'] > Q: split(t, n, n['s'] + Q)
                    n['p'] = a - 2                                                              # G (q) then F
                log.append(f"bar {X}-{X+1} {t.name}: harmony a third below follows (Bb A | G-F)")
                continue
            if kind == 'cadence':
                if len(beats34) == 1:
                    n = beats34[0]; e = n['e']; n['p'] = a + 1; n['e'] = n['s'] + Q - 15; t.add(n['s'] + Q, e, a + 3, n['v'])
                elif len(beats34) >= 2: beats34[0]['p'] = a + 1; beats34[1]['p'] = a + 3
            else:
                if len(beats34) >= 2:
                    beats34[0]['p'] = a + 1; beats34[0]['e'] = beats34[-1]['e']
                    for n in beats34[1:]: t.notes.remove(n)
                elif beats34: beats34[0]['p'] = a + 1
            for n in nextbar: n['p'] = a
            log.append(f"bar {X}-{X+1} {t.name}: harmony a third below follows ({'Bb C | A' if kind=='cadence' else 'Bb | A'})")

# Choruses 1-3 keep the ORIGINAL answer: it is the song's vocal line ("Wasting all my time on you", sung twice).
# Only the final chorus varies it (question, then the climb to F).
for X in (87,):
    chorus_phrase(X, 'cadence')
    # the harp's E (from the C chord) is damped at the bar line so it doesn't ring into the new F arrival
    for n in T('Harp').window(at(X, 4), at(X + 1)):
        if n['p'] % 12 == 4: n['e'] = min(n['e'], at(X + 1) - 10)
chorus_phrase(85, 'question')

# ---------------------------------------------------------------- 2. verse high point
# 5th bar of the verse (over Bb maj7): A G F  →  C Bb A
def verse_peak(X, kind='high'):
    for t in melodic_tracks():
        a, g, f = t.at(at(X), 9), t.at(at(X, 2), 7), t.at(at(X, 2.5), 5)
        if a and g and f and abs((a[0]['e'] - a[0]['s']) - Q) < 60 and g[0]['p'] == a[0]['p'] - 2 and f[0]['p'] == a[0]['p'] - 4:
            if kind == 'high':
                a[0]['p'] += 3; g[0]['p'] += 3; f[0]['p'] += 4
                log.append(f"bar {X} {t.name}: verse line rises C Bb A (was A G F) at {nm(a[0]['p'])}")
            else:   # A Bb A | G F E: leans on Bb (the minor sixth of D minor), then falls step by step
                g[0]['p'] += 3; f[0]['p'] += 4
                log.append(f"bar {X} {t.name}: verse line A Bb A (was A G F) at {nm(a[0]['p'])}")

# ---------------------------------------------------------------- 3. verse 2 gets the tune (horns)
# Verse 2 (bars 21-26) had no melody. Horns 1-2 take the verse 1 cello line, same octave.
cello, horns12 = T('Violoncello'), T('Horn 1·2 in F')
for n in cello.window(at(7), at(13)):
    horns12.add(n['s'] + 14 * BAR, n['e'] + 14 * BAR, n['p'], n['v'] * 0.95)
log.append("bars 21-26 Horn 1·2: double the violas' verse tune (verse 2 had it in violas alone)")

for X in (11, 25, 44): verse_peak(X, 'neighbour')
verse_peak(77, 'high')

# ---------------------------------------------------------------- 4. baroque bridge (bars 59-70), v8
# Harmony (2-bar loop x6): | Am . . Bb | Gm7 . C7 . |. The hook (Bb A Bb C | G | A) fits it at its original pitch.
# Six statements, each in the sung rhythm, more instruments each time, joined by 2-note pickups:
#   S1 60-61  violins I (Bb4)                          S4 66-67  violins I + flute (Bb5), violins II a third below,
#   S2 62-63  violins I (D5), violins II on the hook             oboes (Bb4) and cellos (Bb3): three octaves; sigh onto A
#             a third below                            S5 68-69  a third higher (D6), same doubling; sigh onto C
#   S3 64-65  cellos + bassoons (Bb3) with violins I   S6 70     tutti at Bb5 + piccolo, trumpets in harmony, the G becomes
#             an octave up (Bb4)                                 a trill that resolves to F at the interlude (bar 71)
# Baroque frame from v5: walking continuo bass, broken-chord violins, trio-sonata thirds, a (now quiet) harpsichord.
# Percussion builds underneath: timpani heartbeat → snare → bass drum → crashes → rolls into the interlude.
import math
SCALE = [0, 2, 4, 5, 7, 9, 10]                      # F major's notes counted from C: C D E F G A Bb
def dia(p, steps):
    deg = (p // 12) * 7 + SCALE.index(p % 12) + steps
    return (deg // 7) * 12 + SCALE[deg % 7]
def put(t, line, vel, shift=0):
    for bar, beat, dur, p in line:
        s0 = at(bar, beat); t.add(s0, s0 + int(round(dur * Q)) - 12, p + shift, vel)
def clear(t, b0, b1, cc=False):
    t0, t1 = at(b0), at(b1)
    old = t.window(t0, t1)
    for n in old: t.notes.remove(n)
    if cc: t.other = [(tt, m) for tt, m in t.other if not (t0 <= tt < t1 and m.type == 'control_change' and m.control == 11)]
    return len(old)
def cc11_at(t, tick):
    v = 127
    for tt, m in sorted(t.other, key=lambda x: x[0]):
        if tt > tick: break
        if m.type == 'control_change' and m.control == 11: v = m.value
    return v
def ramp11(t, b0, v0, b1, v1, step=Q // 2):
    t0, t1 = at(b0), at(b1); restore = cc11_at(t, t1)
    t.other = [(tt, m) for tt, m in t.other if not (t0 <= tt < t1 and m.type == 'control_change' and m.control == 11)]
    for tick in range(t0, t1, step):
        u = (tick - t0) / (t1 - t0)
        t.other.append((tick, mido.Message('control_change', channel=t.ch, control=11, value=int(v0 + (v1 - v0) * u))))
    t.other.append((t1, mido.Message('control_change', channel=t.ch, control=11, value=restore)))
HOOK0 = [70, 69, 70, 72, 67, 69]                    # Bb A Bb C | G . | A . . .
def hook(bar, steps=0, octave=0, resolve='plain'):
    """The hook in its sung rhythm, moved by scale steps/octaves. resolve: 'plain' (A, dotted half), 'sigh' (upper note
    leans in first, baroque), or None (no resolution bar)."""
    b, a_, b2, c, g, a2 = [dia(p, steps) + 12 * octave for p in HOOK0]
    if steps < 0: a2 = dia(69, -3) + 12 * octave       # harmony under the long A: E (A minor), not F
    line = [(bar,1,.5,b),(bar,1.5,.5,a_),(bar,2,.5,b2),(bar,2.5,.5,c),(bar,3,2,g)]
    if resolve == 'plain': line += [(bar+1,1,3,a2)]
    elif resolve == 'sigh': line += [(bar+1,1,.5,dia(a2, 1)),(bar+1,1.5,2.5,a2)]
    return line
names = ('Violin I','Violin II','Flute 1·2','Violoncello','Contrabass','Clarinet 1·2 in Bb','Oboe 1·2','Piccolo','Harp',
         'Horn 1·2 in F','Viola','Bassoon 1·2','Trumpet 1·2·3 in Bb')
vln, vln2, fl, vc, cb, cl, ob, picc, harp, hn12, viola, bsn, tpt = (T(n) for n in names)
removed = {t.name: clear(t, 59, 71) for t in (vln, vln2, vc, cb, harp, fl, picc)}
removed['Oboe'] = clear(ob, 64, 71); removed['Bassoon'] = clear(bsn, 64, 66)

# --- melody
V1 = (hook(60) + [(61,4,.5,70),(61,4.5,.5,72)]                                   # S1 Bb4 | A | pickup Bb C
      + hook(62, 2) + [(63,4,.5,74),(63,4.5,.5,72)]                              # S2 D5  | C | pickup D C
      + hook(64) + [(65,4,.5,74),(65,4.5,.5,77)]                                 # S3 Bb4 (with the cellos) | pickup D F
      + hook(66, 0, 1, 'sigh') + [(67,4,.5,82),(67,4.5,.5,84)]                   # S4 Bb5 | Bb→A | pickup Bb C
      + hook(68, 2, 1, 'sigh') + [(69,4,.5,86),(69,4.5,.5,84)]                   # S5 D6  | D→C | pickup D C
      + [(70,1,.5,82),(70,1.5,.5,81),(70,2,.5,82),(70,2.5,.5,84),                # S6 Bb5 A5 Bb5 C6, trill on G → F (bar 71)
         (70,3,.25,81),(70,3.25,.25,79),(70,3.5,.25,81),(70,3.75,.25,79),(70,4,.25,81),(70,4.25,.25,79),(70,4.5,.25,77),(70,4.75,.25,79)])
for bar, beat, dur, p in V1:
    put(vln, [(bar, beat, dur, p)], 80 if bar < 64 else 88 if bar < 66 else 98 if bar < 68 else 106)
put(fl, [x for x in V1 if x[0] >= 66], 90)
put(picc, [(b, bt, d, p + 12) for b, bt, d, p in V1 if b == 70], 92)                                # piccolo joins S6, 8va
put(ob, hook(66, 0, 0, 'sigh') + [(67,4,.5,70),(67,4.5,.5,72)] + hook(68, 2, 0, 'sigh') + [(69,4,.5,74),(69,4.5,.5,72)]
        + [(70,1,.5,70),(70,1.5,.5,69),(70,2,.5,70),(70,2.5,.5,72),(70,3,2,67)], 94)                # oboes an octave below (S4-S6)
log.append("bars 60-70 Violin I: the hook in its sung rhythm, six statements (Bb4, D5, Bb4, Bb5, D6, Bb5) joined by 2-note pickups; "
           "baroque sighs only on S4/S5, the trill on S6")
log.append("bars 66-70: flute doubles the top line, oboes an octave below; piccolo joins S6")

# --- violins II: broken chords, then a third below the hook
ODD_V2 = [64, 69, 72, 69, 64, 69, 65, 70]          # E4 A4 C5 A4 E4 A4 | F4 Bb4   (Am . . Bb)
EVEN_V2 = [62, 67, 70, 67, 64, 67, 72, 67]         # D4 G4 Bb4 G4 | E4 G4 C5 G4  (Gm7 . C7)
def broken(bar, pat, vel): put(vln2, [(bar, 1 + i * .5, .5, p) for i, p in enumerate(pat)], vel)
HALO = [(59,1,3,76),(59,4,1,77),(60,1,2,74),(60,3,2,76),(61,1,3,72),(61,4,1,74),      # a slow high descant on chord tones
        (64,1,2,77),(64,3,2,79),(65,1,3,76),(65,4,1,77)]                                 # E5 . . F5 | D5 . E5 . | C5 . . D5 || F5 . G5 . | E5 . . F5
put(vln2, HALO, 70)
put(vln2, hook(62) + [(63,4,.5,70),(63,4.5,.5,69)], 76)                                     # S2: the hook itself under violins I
put(vln2, hook(66, -2, 1, 'sigh') + [(67,4,.5,77),(67,4.5,.5,81)], 90)                      # S4 a third below (G5 …)
put(vln2, hook(68, 0, 1, 'sigh') + [(69,4,.5,82),(69,4.5,.5,81)], 98)                       # S5 a third below (Bb5 …)
put(vln2, [(70,1,.5,79),(70,1.5,.5,77),(70,2,.5,79),(70,2.5,.5,81),(70,3,2,76)], 104)     # S6: G F G A | E under the trill
log.append("bars 59-70 Violin II: a slow high descant between statements (E5 F5 D5 E5 C5 D5 … F5 G5 E5 F5), a third below the hook in S2, S4, S5, S6")

# --- continuo: cellos walk, except when they sing the hook (S3, S4); the double basses walk then
SINGING = (64, 65, 66, 67)                         # cellos sing the hook here; otherwise they hold long bass notes
for bar in range(59, 71):
    roots = [(1, 3, 45), (4, 1, 46)] if bar % 2 else [(1, 2, 43), (3, 2, 48)]           # A2 . . Bb2 | G2 . C3 .
    put(cb, [(bar, bt, d, p - 12) for bt, d, p in roots], 70 if bar < 66 else 86)
    if bar not in SINGING: put(vc, [(bar, bt, d, p) for bt, d, p in roots], 72 if bar < 66 else 88)
put(vc, hook(64, 0, -1) + hook(66, 0, -1, 'sigh'), 92)                                     # S3 + S4 in the cellos (Bb3)
put(bsn, hook(64, 0, -1), 84)                                                               # bassoons with the cellos in S3
log.append("bars 59-70 Violoncello + Contrabass: long bass notes (A . . Bb | G . C .) instead of the walking bass; cellos sing the hook in S3 and S4")
log.append("bars 64-65 Bassoon 1·2: double the cellos' hook")

# --- trumpets join the last statement, in harmony
TPT = {70: (62, 67, 70), 69: (62, 65, 69), 72: (65, 69, 72), 67: (60, 64, 67)}          # Bb, A, C, G (C E G over C7)
clear(tpt, 70, 71)
for bar, beat, dur, p in hook(70, 0, 0, None):
    for q in TPT[p]: tpt.add(at(bar, beat), at(bar, beat) + int(round(dur * Q)) - 12, q, 100)
log.append("bar 70 Trumpets: the last statement in harmony (as in the final chorus)")

# --- lush layers. Chords per half bar: Am7 (beats 1-3) Bb add9 (beat 4) | Gm7 add11 (1-2) C9 (3-4):
# rich, but with no semitone rubs against the tune.
def chords(bar):
    return [(1, 3, 'Am7'), (4, 1, 'Bb')] if bar % 2 else [(1, 2, 'Gm'), (3, 2, 'C9')]
PAD = {'Am7': [48, 52, 55, 57, 60, 64], 'Bb': [50, 53, 58, 60, 62, 65], 'Gm': [50, 53, 55, 58, 60, 65], 'C9': [52, 55, 58, 62, 64, 67]}
PAD_UP = {'Am7': [67, 69], 'Bb': [70, 72], 'Gm': [70, 74], 'C9': [70, 74]}              # extra top voices from S4 on
CHOIR = {'Am7': [64, 67, 69, 72], 'Bb': [65, 70, 72, 74], 'Gm': [65, 70, 72, 74], 'C9': [64, 67, 70, 74]}
HARP = {'Am7': [9, 0, 4, 7], 'Bb': [10, 0, 2, 5], 'Gm': [7, 10, 0, 2, 5], 'C9': [0, 4, 7, 10, 2]}
CELESTA = {'Am7': [72, 76, 79, 81], 'Bb': [74, 77, 82, 84], 'Gm': [74, 77, 79, 82], 'C9': [76, 79, 82, 86]}
def new_track(key, name, ch, program, vol, pan, rev=110):
    t = Track(mido.MidiTrack()); t.name = name; t.ch = ch
    t.other = [(0, mido.MetaMessage('track_name', name=name)), (0, mido.Message('program_change', channel=ch, program=program)),
               (0, mido.Message('control_change', channel=ch, control=7, value=vol)), (0, mido.Message('control_change', channel=ch, control=10, value=pan)),
               (0, mido.Message('control_change', channel=ch, control=91, value=rev)), (0, mido.Message('control_change', channel=ch, control=11, value=70))]
    tracks[key].append(t); return t
def legato(t, events, vel):
    """events: list of (start_tick, end_tick, [pitches]); a pitch held across consecutive chords is tied, not re-attacked."""
    held = {}
    for s0, e0, ps in events:
        for p_ in list(held):
            if p_ not in ps: st, v = held.pop(p_); t.add(st, s0 - 6, p_, v)
        for p_ in ps:
            if p_ not in held: held[p_] = (s0, vel(s0))
    for p_, (st, v) in held.items(): t.add(st, events[-1][1] - 10, p_, v)
pad = new_track('B', 'Strings (pad)', 10, 49, 92, 70)                  # slow strings
choir = new_track('B', 'Choir', 11, 52, 84, 58)                        # choir aahs
cel = new_track('A', 'Celesta', 15, 8, 70, 80)                          # celesta
grow = lambda tick: (tick - at(59)) / (at(71) - at(59))
ev_pad, ev_choir = [], []
for bar in range(59, 71):
    for beat, dur, c in chords(bar):
        s0, e0 = at(bar, beat), at(bar, beat + dur)
        ev_pad.append((s0, e0, PAD[c] + (PAD_UP[c] if bar >= 66 else [])))
        if bar >= 62: ev_choir.append((s0, e0, CHOIR[c]))
        # harp: a 16th-note sweep up and back down through the chord, A2..A5
        tones = [q for q in range(45, 82) if q % 12 in HARP[c]]
        up = tones[::max(1, len(tones) // 8)][:8]; seq = (up + up[-2:0:-1]) if dur >= 2 else up[:4]
        for i in range(int(dur * 4)):
            q = seq[i % len(seq)]; tt = s0 + i * Q // 4
            harp.add(tt, min(tt + Q, e0 - 10), q, int(48 + 34 * grow(tt) + (8 if i % 4 == 0 else 0)))   # damped at the chord change
        # celesta shimmer: 8th-note broken chords, high, fading out as the choir arrives
        if bar <= 63:
            for i in range(int(dur * 2)):
                tt = s0 + i * Q // 2; cel.add(tt, tt + Q // 2, CELESTA[c][i % 4], int(52 - 4 * (bar - 59)))
legato(pad, ev_pad, lambda tick: int(58 + 50 * grow(tick)))
legato(choir, ev_choir, lambda tick: int(50 + 50 * grow(tick)))
for t, v0, v1 in ((pad, 72, 122), (choir, 64, 118)): ramp11(t, 59, v0, 71, v1)
log.append("bars 59-70 Strings (pad) — new track, slow strings: six-voice sustained chords (Am7, Bb add9, Gm7 add11, C9), tied where notes are shared, eight voices from S4")
log.append("bars 62-70 Choir — new track, choir aahs: four-voice chords from the 2nd statement on, swelling")
log.append("bars 59-70 Harp: 16th-note sweeps up and down each chord, A2-A5, growing")
log.append("bars 59-63 Celesta — new track: high broken-chord shimmer that fades as the choir arrives")

# --- percussion: a build from a heartbeat to rolls
tim, sn, bd, cym = T('Timpani'), T('Snare Drum'), T('Bass Drum · Cymbals'), T('Suspended Cymbal · Triangle')
for t in (tim, sn, bd, cym): removed[t.name] = clear(t, 59, 71)
def hit(t, bar, beat, p, vel, dur=.25): t.add(at(bar, beat), at(bar, beat) + int(dur * Q), p, vel)
def roots_at(bar, beat):
    if bar % 2: return 46 if beat >= 4 else 45            # Bb2 on beat 4, else A2
    return 48 if beat >= 3 else 43                        # C3 on beats 3-4, else G2
def roll(t, p_, b0, beat0, b1, beat1, v0, v1):
    t0, t1 = at(b0, beat0), at(b1, beat1); n = max(1, (t1 - t0) // 60)
    for i, tick in enumerate(range(t0, t1, 60)): t.add(tick, tick + 55, p_, int(v0 + (v1 - v0) * (i / n) ** 1.3))
for k, bar in enumerate((59, 61, 63, 65, 67)):              # a swell into every statement: timpani roll + cymbal, each one bigger
    lvl = k / 4
    roll(tim, 45, bar, 3, bar + 1, 1, int(26 + 30 * lvl), int(54 + 50 * lvl))
    roll(cym, 59, bar, 3, bar + 1, 1, int(16 + 20 * lvl), int(40 + 50 * lvl))
    hit(tim, bar + 1, 1, 43, int(60 + 50 * lvl), 1)                                        # soft timpani G on each statement
    if bar + 1 >= 62: hit(bd, bar + 1, 1, 36, int(60 + 45 * lvl), 1)                     # bass drum on each statement from S2
for bar in (66, 68): hit(bd, bar, 1, 57, 90 if bar == 66 else 104, 2)                  # crashes on S4 and S5
for bar in (68, 69):                                                                    # snare only at the end: 16ths, then a roll
    for i in range(16): hit(sn, bar, 1 + i * .25, 38, int(46 + 30 * (bar - 68 + i / 16) + (12 if i % 4 == 0 else 0)))
for bar in (60, 62): hit(cym, bar, 1, 81, 40, 1)                                       # triangle sparkle
for i, tick in enumerate(range(at(70), at(71), 60)):         # bar 70: timpani roll on C and snare roll, crescendo
    u = i / 32; tim.add(tick, tick + 55, 48, int(70 + 50 * u)); sn.add(tick, tick + 55, 38, int(78 + 44 * u))
for i, tick in enumerate(range(at(69, 3), at(71), 60)):      # big cymbal swell into the interlude (its crash at bar 71 is kept)
    cym.add(tick, tick + 55, 59, int(30 + 80 * (i / 48) ** 1.4))
for t, v0, v1 in ((tim, 80, 124), (sn, 84, 124), (bd, 90, 124), (cym, 80, 120)): ramp11(t, 59, v0, 71, v1)
log.append("bars 59-70 percussion swells instead of marching: a timpani roll + cymbal swell into every statement, each bigger; "
           "soft timpani and bass drum on each statement; crashes on S4 and S5; snare only in bars 68-70 (16ths, then a roll); "
           "timpani roll on C and the big cymbal swell into the interlude")
log.append("removed in bars 59-70: " + ', '.join(f"{k} {v}" for k, v in removed.items()))
# ---------------------------------------------------------------- 4b. v10: centred on strings
WINDS = ('Piccolo', 'Flute 1·2', 'Oboe 1·2', 'English Horn', 'Clarinet 1·2 in Bb', 'Bass Clarinet in Bb', 'Bassoon 1·2', 'Contrabassoon',
         'Horn 1·2 in F', 'Horn 3·4 in F', 'Trumpet 1·2·3 in Bb', 'Trombone 1·2', 'Bass Trombone', 'Tuba')
silenced = sum(clear(T(n), 59, 71) for n in WINDS)
for key in tracks: tracks[key] = [t for t in tracks[key] if t.name not in ('Choir', 'Celesta')]
clear(sn, 59, 71); clear(bd, 59, 71)                                   # drums out; timpani rolls and cymbal swells stay
for n in harp.window(at(59), at(71)): n['v'] = int(n['v'] * 0.72)      # harp steps back
log.append(f"bars 59-70: woodwinds and brass silent ({silenced} notes removed), choir and celesta dropped, snare and bass drum out, harp softer")
solo = new_track('B', 'Solo Violin', 11, 40, 96, 60)
trem = new_track('B', 'Strings (tremolo)', 12, 44, 82, 72)
pizz = new_track('B', 'Strings (pizzicato)', 13, 45, 92, 56)
# solo violin: sings S1, floats a high countermelody over S2-S3, then joins violins I for S4-S6
put(solo, hook(60) + [(61,4,.5,70),(61,4.5,.5,72)], 84)
put(solo, [(62,1,2,77),(62,3,2,79),(63,1,3,81),(63,4,1,77),(64,1,2,86),(64,3,2,84),(65,1,3,84),(65,4,1,86)], 80)   # F5 . G5 . | A5 . . F5 | D6 . C6 . | C6 . . D6
put(solo, [x for x in V1 if x[0] >= 66], 96)
# violas: a slow rising countermelody under S1-S2, then the hook an octave below violins I (S3-S6)
clear(viola, 59, 71)
put(viola, [(59,1,3,60),(59,4,1,62),(60,1,2,62),(60,3,2,64),(61,1,3,64),(61,4,1,65),(62,1,2,65),(62,3,2,67),(63,1,3,67),(63,4,1,65)], 76)  # C D | D E | E F | F G | G F
put(viola, hook(64) + [(65,4,.5,74),(65,4.5,.5,77)] + hook(66, 0, 0, 'sigh') + [(67,4,.5,70),(67,4.5,.5,72)]
           + hook(68, 2, 0, 'sigh') + [(69,4,.5,74),(69,4.5,.5,72)] + hook(70, 0, 0, None), 92)
put(vc, hook(70, 0, -1, None), 98)                                     # cellos join the last statement
# tremolo strings: shimmering high chords from S2, swelling (they take the choir's place)
legato(trem, [(s0, e0, CHOIR[c]) for s0, e0, c in
              [(at(bar, beat), at(bar, beat + dur), c) for bar in range(62, 71) for beat, dur, c in chords(bar)]],
       lambda tick: int(50 + 55 * grow(tick)))
ramp11(trem, 62, 60, 71, 122)
# pizzicato: a string pulse that builds: beats 1 and 3 → every beat → 8ths
PZ = {'Am7': [45, 52], 'Bb': [46, 53], 'Gm': [43, 50], 'C9': [48, 55]}
for bar in range(64, 71):
    step = 2 if bar <= 65 else 1 if bar <= 67 else .5
    for beat, dur, c in chords(bar):
        b_ = beat
        while b_ < beat + dur - 1e-6:
            for q in PZ[c]: pizz.add(at(bar, b_), at(bar, b_) + Q // 2, q, int(62 + 40 * grow(at(bar, b_))))
            b_ += step
log.append("bars 59-70 strings: Solo Violin (new) sings S1, a high countermelody over S2-S3 (F5 G5 A5 F5 D6 C6 C6 D6), then doubles violins I; "
           "violas rise C-D-E-F-G under S1-S2 and carry the hook an octave below violins I from S3; cellos join S6; "
           "Strings (tremolo) (new) shimmer from S2; Strings (pizzicato) (new) pulse from S3: half notes → quarters → 8ths")

# ---------------------------------------------------------------- 4c. v11: soft choir at the climax, piano colour
choir = new_track('B', 'Choir', 15, 52, 70, 58)
legato(choir, [(at(bar, beat), at(bar, beat + dur), CHOIR[c]) for bar in range(68, 71) for beat, dur, c in chords(bar)],
       lambda tick: int(48 + 16 * (tick - at(68)) / (at(71) - at(68))))
ramp11(choir, 68, 52, 71, 92)
piano = new_track('B', 'Piano (rolling)', 14, 0, 84, 64, rev=96)           # quieter than v11 (112)          # left hand, pedalled with the harmony
piano_mel = new_track('A', 'Piano (melody)', 15, 0, 112, 66, rev=96)        # right hand on its own channel, no pedal, so passing notes stay clean
# right hand: the hook with violins I from S2; octaves from S4
for bar, beat, dur, p_ in V1:
    if bar < 62: continue
    v = int(84 + 30 * grow(at(bar, beat)))
    s0 = at(bar, beat); e0 = s0 + int(round(dur * Q)) - 12
    piano_mel.add(s0, e0, p_, v)
    if bar >= 66 and dur >= .5: piano_mel.add(s0, e0, p_ - 12, v - 8)
# left hand: rolling arpeggios up and back down each chord, from the low register
ROLL = {'Am7': (33, [9, 0, 4, 7]), 'Bb': (34, [10, 2, 5, 0]), 'Gm': (31, [7, 10, 2, 5]), 'C9': (36, [0, 4, 7, 10, 2])}
ROLL_FROM = 68                                                  # only towards the end of the bridge (S5-S6)
for bar in range(ROLL_FROM, 71):
    sub = 4                                                      # 16ths
    for beat, dur, c in chords(bar):
        root, pcs = ROLL[c]
        tones = [root, root + 7, root + 12] + [q for q in range(root + 13, root + 31) if q % 12 in pcs]
        seq = tones + tones[-2:0:-1]
        s0, e0 = at(bar, beat), at(bar, beat + dur)
        piano.other.append((s0 + 15, mido.Message('control_change', channel=14, control=64, value=127)))   # pedal with the harmony
        piano.other.append((e0 - 25, mido.Message('control_change', channel=14, control=64, value=0)))
        for i in range(int(dur * sub)):
            tt = s0 + i * Q // sub; q = seq[i % len(seq)]
            u = (tt - at(ROLL_FROM)) / (at(71) - at(ROLL_FROM))
            piano.add(tt, tt + Q // sub, q, int(42 + 22 * u + (6 if i % sub == 0 else 0)))         # soft: 42-70, growing a little
# the harp keeps only its upper notes from S4 on, so the piano owns the low rolling
thinned = 0
for n in [n for n in harp.window(at(ROLL_FROM), at(71)) if n['p'] < 60]: harp.notes.remove(n); thinned += 1
log.append("bars 68-70 Choir (back, soft): chords under S5-S6, low volume (CC7 70, velocity 48-64), swelling gently")
log.append("bars 62-70 Piano (melody) (file A channel 16, no pedal): doubles the hook from S2, octaves from S4. "
           "Piano (rolling) (file B channel 15): quiet 16th-note rolling arpeggios only in bars 68-70 (S5-S6), "
           "channel volume 84, velocity 42-70, sustain pedal changed with every chord")
log.append(f"bars 68-70 Harp: low notes removed ({thinned}) so the piano's rolling arpeggios own that register")

# reverb (CC91): every non-drum part goes much wetter for the bridge, and back at the interlude
wet = 0
for key in tracks:
    for t in tracks[key]:
        if not t.notes or t.name.startswith(('Snare', 'Bass Drum')) or t.name in ('Strings (pad)', 'Choir', 'Celesta', 'Solo Violin', 'Strings (tremolo)', 'Strings (pizzicato)', 'Piano (rolling)', 'Piano (melody)'): continue
        if not t.window(at(59), at(71)): continue
        base = 45
        for tt, m in sorted(t.other, key=lambda x: x[0]):
            if m.type == 'control_change' and m.control == 91 and tt <= at(59): base = m.value
        for i, tick in enumerate(range(at(58, 4), at(59) + 1, Q // 4)):
            t.other.append((tick, mido.Message('control_change', channel=t.ch, control=91, value=int(base + (112 - base) * i / 4))))
        t.other.append((at(71), mido.Message('control_change', channel=t.ch, control=91, value=base)))
        wet += 1
log.append(f"bars 59-70 reverb: {wet} parts' reverb send raised from 45 to 112 (CC91) for the bridge, back to 45 at the interlude")

# ---------------------------------------------------------------- 5. thickening
# 5a. verse 3 harp: verse 2's flowing harp arpeggios, a little softer (harp was silent in verse 3)
harp = T('Harp')
for n in harp.window(at(21), at(27)):
    harp.add(n['s'] + 19 * BAR, n['e'] + 19 * BAR, n['p'], n['v'] * 0.8)
log.append("bars 40-45 Harp: arpeggios added (verse 2 pattern, softer)")
# 5b. bridge: horns 1-2 softly double the violas' chords in bars 59-62 (horns used to enter at 63)
viola = T('Viola')
# (v5: no horn chords in the bridge; the baroque texture is strings + harpsichord)
# 5c. choruses 1 and 3: flute 2 plays a third below flute 1 (thirds in F major; the final F gets A below)
THIRD_DOWN = {10: -3, 9: -4, 0: -3, 7: -3, 2: -4, 4: -4, 5: -8}
fl = T('Flute 1·2')
for b0 in (17, 50):
    added = 0
    for n in [n for n in fl.window(at(b0), at(b0 + 4)) if n['e'] - n['s'] >= E8 - 30]:
        if n['p'] % 12 in THIRD_DOWN:
            fl.add(n['s'], n['e'], n['p'] + THIRD_DOWN[n['p'] % 12], n['v'] * 0.85); added += 1
    log.append(f"bars {b0}-{b0+3} Flute 1·2: second flute in thirds under the tune ({added} notes)")

# 5d. final chorus: the tubular bell (which rings G at each phrase start) also rings the tonic F on the last cadence
bells = T('Tubular Bells'); g = bells.at(at(87), 7)
if g: bells.add(at(88), at(88) + 4 * Q, g[0]['p'] - 2, g[0]['v']); log.append("bar 88 Tubular Bells: F rung on the final chorus's resolution")

# ---------------------------------------------------------------- 6. horns: less honk
# In this sound set horn velocity sets brightness as well as level, so loud horns turn brassy.
# Velocities ×0.82 (capped at 100) mellow the tone but keep the shape; channel volume 100 → 90.
for name in ('Horn 1·2 in F', 'Horn 3·4 in F'):
    t = T(name)
    for n in t.notes: n['v'] = max(20, min(100, round(n['v'] * 0.82)))
    for i, (tt, msg) in enumerate(t.other):
        if msg.type == 'control_change' and msg.control == 7: t.other[i] = (tt, msg.copy(value=min(msg.value, 90)))
    log.append(f"{name}: velocities ×0.82 (max 100), channel volume 90: mellower, less brassy")

# ---------------------------------------------------------------- 7. v13: softer harp outside the bridge
# Its rolling arpeggios in the verses and choruses read as a piano; a lighter touch softens the attack as well as the level.
# The bridge harp (bars 59-70) already plays at x0.72 and is left as it is.
harp = T('Harp'); soft = 0
for n in harp.notes:
    if not at(59) <= n['s'] < at(71): n['v'] = max(20, round(n['v'] * HARP_SOFT)); soft += 1
for i, (tt, msg) in enumerate(harp.other):
    if msg.type == 'control_change' and msg.control == 7: bridge_vol = msg.value; harp.other[i] = (tt, msg.copy(value=HARP_VOL))
harp.other += [(at(59) - 5, mido.Message('control_change', channel=harp.ch, control=7, value=bridge_vol)),
               (at(71), mido.Message('control_change', channel=harp.ch, control=7, value=HARP_VOL))]
log.append(f"Harp outside the bridge: velocities x{HARP_SOFT} ({soft} notes) and channel volume {bridge_vol} -> {HARP_VOL}, softer and less piano-like")

# ---------------------------------------------------------------- 8. v14: the verse melody, forward
# The verse tune sits in the tenor register (G3-A3) under the violins' broken chords and the harp; it measured
# 2.6-4.3 dB under everything else. Lift it (expression + a firmer touch) and ease the mid/high accompaniment.
def cc11_at(t, tick):
    v = 127
    for tt, m in sorted(t.other, key=lambda x: x[0]):
        if tt > tick: break
        if m.type == 'control_change' and m.control == 11: v = m.value
    return v
def scale_cc11(t, t0, t1, f):
    v0, v1 = cc11_at(t, t0), cc11_at(t, t1)
    for i, (tt, m) in enumerate(t.other):
        if t0 <= tt < t1 and m.type == 'control_change' and m.control == 11:
            t.other[i] = (tt, m.copy(value=max(1, min(127, round(m.value * f)))))
    t.other += [(t0, mido.Message('control_change', channel=t.ch, control=11, value=max(1, min(127, round(v0 * f))))),
                (t1, mido.Message('control_change', channel=t.ch, control=11, value=v1))]
VERSES = [  # bars, melody parts and their expression lift, accompaniment eased by x0.86 (about -2.6 dB)
    (7, 13, {'Violoncello': 1.18},                                 # v18: +0.5 dB (v17 1.145, v14-v16 1.30)
     ('Violin II', 'Viola', 'Harp', 'English Horn', 'Clarinet 1·2 in Bb', 'Horn 3·4 in F')),
    (21, 27, {'Viola': 1.257, 'Horn 1·2 in F': 1.133},           # v18: +0.5 dB (v16-v17 1.22 / 1.10, v14 1.30 / 1.15)
     ('Violin I', 'Violin II', 'Harp', 'Clarinet 1·2 in Bb', 'Horn 3·4 in F', 'Flute 1·2', 'Bassoon 1·2')),
    (40, 46, {'Violoncello': 1.22, 'Bassoon 1·2': 1.18},          # v17: matched to verse 2 (v14-v16: 1.40 / 1.35)
     ('Violin I', 'Violin II', 'Viola', 'Harp', 'Clarinet 1·2 in Bb', 'Bass Clarinet in Bb', 'Flute 1·2')),
]
for b0, b1, lead, accomp in VERSES:
    for name, f in lead.items():
        t = T(name); scale_cc11(t, at(b0), at(b1), f)
        cap = 100 if name.startswith('Horn') else 110          # horns stay mellow
        for n in t.window(at(b0), at(b1)): n['v'] = min(cap, max(n['v'], round(n['v'] * 1.1)))
    for name in accomp:
        scale_cc11(T(name), at(b0), at(b1), 0.86)
    log.append(f"bars {b0}-{b1-1}: verse melody forward ({', '.join(f'{k} x{v}' for k, v in lead.items())} expression, "
               f"touch x1.1), accompaniment x0.86 ({', '.join(accomp)})")

# ---------------------------------------------------------------- 9. v15: the ending repeats, faster and faster, gathering instruments
# Bars 100-102 play the closing figure (F . . G | G G, twice a bar, over a D pedal) three times, adding instruments,
# then the cold hit on D at bar 103. Now the full bar-102 tutti carries on for REPEATS more bars without stepping back,
# accelerating from 156 to END_BPM and getting louder, with a new colour joining on every repeat; the same cold hit
# lands at bar 103 + REPEATS (back at 156, so it's identical).
REPEATS, END_BPM = 5, 228
HIT, SHIFT = at(103), REPEATS * BAR
HIT_NEW = HIT + SHIFT
for k in tracks:
    for t in tracks[k]:
        for n in t.notes:
            if n['s'] >= HIT: n['s'] += SHIFT; n['e'] += SHIFT
        t.other = [(tt + SHIFT if tt >= HIT else tt, m) for tt, m in t.other]
x_of = lambda tick: (tick - HIT) / SHIFT                       # 0 → 1 across the repeats
EXPR_TOP = 115                                                 # below 127 so the drive never peaks above the cold hit
expr = lambda x: round(113 + (EXPR_TOP - 113) * x)             # carries on from where bar 102 ends (113)
def ramp(t, j0, lo=None, cc7=None):
    if cc7 is not None: t.other.append((HIT + j0 * BAR - 5, mido.Message('control_change', channel=t.ch, control=7, value=cc7)))
    for beat in range(j0 * 4, REPEATS * 4):
        tick = HIT + beat * Q; x = x_of(tick)
        v = expr(x) if lo is None else round(lo + (EXPR_TOP - lo) * (beat - j0 * 4) / max(1, REPEATS * 4 - 1 - j0 * 4))
        t.other.append((tick, mido.Message('control_change', channel=t.ch, control=11, value=v)))
DRIVE = REPEATS - 2                                            # the last two bars: percussion drive
TUTTI = ('Piccolo', 'Flute 1·2', 'Oboe 1·2', 'English Horn', 'Clarinet 1·2 in Bb', 'Bass Clarinet in Bb', 'Bassoon 1·2',
         'Contrabassoon', 'Horn 1·2 in F', 'Horn 3·4 in F', 'Trumpet 1·2·3 in Bb', 'Trombone 1·2', 'Bass Trombone', 'Tuba',
         'Timpani', 'Snare Drum', 'Bass Drum · Cymbals', 'Violin I', 'Violin II', 'Viola', 'Violoncello', 'Contrabass')
for name in TUTTI:                                             # everyone from bar 102 keeps going
    t = T(name); cell = t.window(at(102), at(103))
    for j in range(REPEATS):
        if name in ('Snare Drum', 'Bass Drum · Cymbals') and j >= DRIVE: continue   # their own drive, below
        if name == 'Timpani' and j == REPEATS - 1: continue                       # a roll, below
        for n in cell:
            s = n['s'] + (j + 1) * BAR
            t.add(s, n['e'] + (j + 1) * BAR, n['p'], min(100 if name.startswith('Horn') else 127, n['v'] * (1 + 0.03 * x_of(s))))
    ramp(t, 0)
# new colours, one more on every repeat (all stop at the hit, so the ending stays cold)
def cut(t):                                                    # nothing new rings into the hit
    for n in t.notes:
        if HIT <= n['s'] < HIT_NEW: n['e'] = min(n['e'], HIT_NEW - 10)
harp, bells, glock = T('Harp'), T('Tubular Bells'), T('Glockenspiel')
trem, choir, pno = T('Strings (tremolo)'), T('Choir'), T('Piano (melody)')
ARP = [50, 53, 57, 62, 65, 69, 74, 77, 81, 77, 74, 69, 65, 62, 57, 53]    # D minor, up and back (D3..A5; light, above the bass)
for j in range(0, REPEATS):                                    # 1st repeat: harp sweeps + tubular bell on every downbeat
    b = HIT + j * BAR
    for i, p in enumerate(ARP):
        tt = b + i * Q // 4; harp.add(tt, tt + Q // 2, p, 64 + 24 * x_of(tt) + (6 if i % 4 == 0 else 0))
    bells.add(b, b + 2 * Q, 74, 76 + 24 * x_of(b))
ramp(harp, 0, cc7=100); ramp(bells, 0)
for j in range(1, REPEATS):                                    # 2nd: glockenspiel doubles the figure; tremolo strings on D-A-D
    for n in T('Violin I').window(at(102), at(103)):
        s = n['s'] + (j + 1) * BAR; glock.add(s, s + Q // 2, n['p'], 62 + 22 * x_of(s))
    b = HIT + j * BAR
    for p in (62, 69, 74): trem.add(b, b + BAR - 10, p, 70 + 26 * x_of(b))
ramp(glock, 1); ramp(trem, 1, lo=80, cc7=100)
for j in range(2, REPEATS):                                    # 3rd: choir on D-A-D-A, piano doubles the figure an octave up
    b = HIT + j * BAR
    for p in (50, 57, 62, 69): choir.add(b, b + BAR - 10, p, 72 + 28 * x_of(b))
    for n in T('Violin II').window(at(102), at(103)):
        s = n['s'] + (j + 1) * BAR
        pno.add(s, n['e'] + (j + 1) * BAR, n['p'] + 12, 74 + 22 * x_of(s))
ramp(choir, 2, lo=84, cc7=100); ramp(pno, 2)
for t in (harp, bells, glock, trem, choir, pno): cut(t)
# 4th-5th: the drive. Snare 16ths, bass drum on every beat and a cymbal roll, all entering as loud as what they replace
sn, bd, cym, tim = T('Snare Drum'), T('Bass Drum · Cymbals'), T('Suspended Cymbal · Triangle'), T('Timpani')
drive0 = HIT + DRIVE * BAR; nd = 2 * 16
for i in range(nd):
    tt = drive0 + i * Q // 4; sn.add(tt, tt + Q // 4 - 10, 38, 84 + 14 * i / (nd - 1) + (4 if i % 4 == 0 else 0))
for i in range(8):
    tt = drive0 + i * Q; bd.add(tt, tt + Q - 10, 36, 84 + 10 * i / 7)
cym_roll = cym.window(at(98, 2), at(100))
for i in range(64):
    tt = drive0 + i * Q // 8; cym.add(tt, tt + Q // 8 - 5, cym_roll[0]['p'], 64 + 40 * i / 63)
ramp(cym, DRIVE, lo=96)
roll0 = HIT + (REPEATS - 1) * BAR                               # timpani: a roll on D in the last bar, from full strength
for i in range(32):
    tt = roll0 + i * Q // 8; tim.add(tt, tt + Q // 8 - 5, 50, 80 + 16 * i / 31)
# accelerando: one tempo per beat, 156 → END_BPM, quickening more towards the end; the hit itself is back at 156
for conductor in (tracks['A'][0], tracks['B'][0]):
    for beat in range(REPEATS * 4):
        bpm = 156 * (END_BPM / 156) ** ((beat / (REPEATS * 4 - 1)) ** 1.4)
        conductor.other.append((HIT + beat * Q, mido.MetaMessage('set_tempo', tempo=round(60e6 / bpm))))
log.append(f"ending: the closing figure repeats {REPEATS} more times (bars 103-{102 + REPEATS}) at full strength, accelerating "
           f"156 → {END_BPM} BPM and growing louder; joining in turn: harp sweeps + tubular bell, glockenspiel + tremolo "
           f"strings, choir + piano, then snare 16ths, bass drum and a cymbal roll, and a timpani roll in the last bar; "
           f"the cold hit moves to bar {103 + REPEATS}, unchanged")

# ---------------------------------------------------------------- write
import os; os.makedirs(OUT, exist_ok=True)
for k, m in mids.items():
    new = mido.MidiFile(type=m.type, ticks_per_beat=m.ticks_per_beat)
    for t in tracks[k]: new.tracks.append(t.to_mido())
    new.save(OUT + FILES[k] + ' (v18).mid')
json.dump(log, open(OUT + 'v18-changes.json', 'w'), indent=1)
print('\n'.join(log))
