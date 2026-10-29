"""Wasting My Time, electronic (lush + variations), revision 2: a less repetitive main melody.

usage: python3 variations.py [out folder]   (default: this script's folder)

Revision 1 fitted whole Chaconne variations to verses 2-4 by squeezing each 3/4 bar into one of
the song's chords: about three times Bach's written speed, in triplets, with up to 14 notes a bar
taken from the top of his violin chords. It sounded incoherent and far too busy. Revision 2 keeps
the new material to the original tune's pace and rhythm:

- Verse 2: the Chaconne's opening theme (Bach, Partita No. 2 in D minor, BWV 1004), reduced to
  its main notes in straight quarters and eighths, about 5 notes a bar like the song's tune:
  A A E | E E F | D C Bb | A G F E, twice, the second time climbing to Bb. Its ground
  (D – C# – G/Bb – A) is the verse's bass (D – C – Bb – A).
- Verses 1, 3 and 4: the song's own tune (verse 4 with v18's "C Bb A" variation).
- Chorus 2: the hook, then Mozart's bassoon answer from bar 29 of the K. 191 slow movement
  (G F E F | D D C Bb), with his violins' line from the same bars as the counter-melody.
- Chorus 3: the hook, then Mozart's sighing cadence (A–G–F–E–F, the end of the counter-melody's
  theme) on the lead, in octaves with the counter-melody.
- Choruses 1 and final: unchanged.

Where the melody changes, the parts that doubled the old melody there are taken out.
"""
import importlib.util, pathlib, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mozart', HERE.parent / 'wasting-my-time-electronic-lush-mozart' / 'mozart.py')
mz = importlib.util.module_from_spec(spec); spec.loader.exec_module(mz)
lush, e = mz.lush, mz.e
T, BAR, BEAT, add, chord_at = e.T, e.BAR, e.BEAT, e.add, e.chord_at
N = e.NOTES

# ---------------------------------------------------------------- source material (pitch, start beat, length in beats)
# Mozart, K. 191, 2nd mvt (Mutopia, Liang Seng, public domain), in his quarter-note beats from the passage's start.
MOZ_BASSOON_29 = [(-0.057, 0.055, 57), (0, 0.5, 55), (0.5, 1, 53), (1.5, 0.5, 52), (2, 0.25, 53), (2.25, 0.25, 62), (2.5, 1, 62), (3.5, 0.25, 60), (3.75, 0.25, 58)]
MOZ_VIOLIN_29 = [(0.25, 0.25, 67), (0.5, 0.25, 65), (0.75, 0.125, 65), (1, 0.25, 65), (1.25, 0.25, 69), (1.5, 0.25, 67), (1.75, 0.25, 64), (2, 1, 65)]

# ---------------------------------------------------------------- 1. take the old melody out where it changes
VERSE_SPANS = [(21, 26)]                                # verse 2: bars, up to beat 4 of the last (the pickup stays)
CHORUS_SPANS = [(33, 35), (52, 54)]                     # choruses 2 and 3, second phrase
spans = [(T(a), T(b, 4)) for a, b in VERSE_SPANS] + [(T(a), T(b)) for a, b in CHORUS_SPANS]
inside = lambda t: any(a <= t < b for a, b in spans)
WHOLE = ('lead_v', 'echo_v', 'w_vox', 'lead', 'echo', 'w_hookL', 'w_hookR', 'harm', 'stack', 'counter')   # melody parts: cleared outright
old_melody = [n for r in ('lead_v', 'lead') for n in N[r] if inside(n[0])]
old_at = collections.defaultdict(set)                    # onset (to 60 ticks) -> pitch classes of the old melody
for s, en, p, v in old_melody:
    for k in range(-1, 2): old_at[s // 60 + k].add(p % 12)
# Which background parts doubled the old melody in each changed passage (from v18's scoring):
# 'pc' = same pitch class at any octave, starting together; 'any' = any note starting together
# (the hook's parallel thirds and sixths in the choruses).
DOUBLED_BY = [((21, 26), {'o_vla': 'pc', 'o_horn': 'pc'}),                  # verse 2: violas, horns 1-2
              ((33, 34), {'o_vn1': 'pc', 'o_vn2': 'any', 'o_flute': 'any', 'o_clar': 'any', 'o_reed': 'pc', 'bells': 'pc'}),
              ((52, 53), {'o_vn1': 'pc', 'o_vn2': 'any', 'o_flute': 'any', 'o_clar': 'any', 'o_reed': 'pc', 'bells': 'pc'})]
def doubles(r, s, p):
    for (a, b), parts in DOUBLED_BY:
        if T(a) <= s < T(b + 1) and r in parts:
            hit = old_at.get(s // 60)
            return bool(hit) and (parts[r] == 'any' or p % 12 in hit)
    return False
removed = collections.Counter()
for r in list(N):
    keep = []
    for n in N[r]:
        if inside(n[0]) and (r in WHOLE or doubles(r, n[0], n[2])): removed[r] += 1; continue
        keep.append(n)
    N[r] = keep
# In chorus 2 the counter-melody's second half makes way for Mozart's own second voice there.
# In chorus 3 it stays: the lead sings the same cadence an octave above it.
N['mozart'] = [n for n in N['mozart'] if not (T(33) <= n[0] < T(35))]

# ---------------------------------------------------------------- 2. the new melodies
def fit_to_chord(t, p, dur):
    """A long note a semitone from a chord tone and outside the chord moves onto the chord (Bach's C# over C becomes C)."""
    bar = int(t // BAR) + 1; half = int((t % BAR) // (2 * BEAT))
    pcs, _ = chord_at(bar, half)
    if p % 12 in pcs or dur < 400: return p   # passing eighths stay as Bach and Mozart wrote them
    for d in (-1, 1):
        if (p + d) % 12 in pcs: return p + d
    return p
def melody(role, notes, vel=96, echo=None, double=None):
    """notes: (song tick, length in ticks, pitch). Shapes velocity by length, adds echo and doubling parts."""
    for t, d, p in notes:
        p = fit_to_chord(t, p, d)
        v = vel if d >= 300 else vel - 10 if d >= 140 else vel - 22
        add(role, t, t + max(d - 12, 30), p, v)
        if echo and d >= 400:
            for k, g in ((1, 0.42), (2, 0.2)): add(echo, t + 360 * k, t + 360 * k + min(d, 300), p, v * g)
        for r, shift, k in (double or []): add(r, t, t + max(d - 12, 30), p + shift, v * k)
# Verse 2: the Chaconne's opening theme (bars 1-8), its main notes in straight time. Each Bach bar
# fills one song chord as quarter, eighth, eighth (his long first note, the re-struck note, beat 3);
# his 16th-note cadence runs (bars 4 and 8) become four eighths. Bar 21 (the A7 bar) is a calm
# lead-in, E . . D C#; bar 26 resolves E -> F and falls to D before the pre-chorus pickup.
A4, Bb4, C5, Cs5, D5, E5, F5, G5, A5, Bb5, E4, F4, G4 = 69, 70, 72, 73, 74, 76, 77, 79, 81, 82, 64, 65, 67
THEME = [(21, 1, 3, E5), (21, 4, .5, D5), (21, 4.5, .5, Cs5),
         (22, 1, 1, A4), (22, 2, .5, A4), (22, 2.5, .5, E5),  (22, 3, 1, E5), (22, 4, .5, E5), (22, 4.5, .5, F5),      # Dm | C
         (23, 1, 1, D5), (23, 2, .5, C5), (23, 2.5, .5, Bb4), (23, 3, .5, A4), (23, 3.5, .5, G4), (23, 4, .5, F4), (23, 4.5, .5, E4),   # Bbmaj7 | A7
         (24, 1, 1, A4), (24, 2, .5, A4), (24, 2.5, .5, E5),  (24, 3, 1, E5), (24, 4, .5, E5), (24, 4.5, .5, F5),      # Dm | C
         (25, 1, 1, D5), (25, 2, .5, D5), (25, 2.5, .5, Bb5), (25, 3, .5, A5), (25, 3.5, .5, G5), (25, 4, .5, F5), (25, 4.5, .5, E5),   # Bbmaj7 | A7
         (26, 1, 2, F5), (26, 3, 1, D5)]                                                                             # Dm
VOX = [('w_vox', 0, 0.75)]
melody('lead_v', [(T(bar, beat), int(d * BEAT), p) for bar, beat, d, p in THEME], 98, echo='echo_v', double=VOX + [('o_vla', -12, 0.95)])
def mozart(src, bar, shift, role, vel, double=None, echo=None):
    melody(role, [(int(T(bar) + s * 960), int(d * 960), p + shift) for s, d, p in src], vel, echo=echo, double=double)
HOOK2 = [('w_hookL', 0, 0.82), ('w_hookR', 0, 0.82)]
mozart(MOZ_BASSOON_29, 33, 12, 'lead', 100, HOOK2, 'echo'); mozart(MOZ_VIOLIN_29, 33, -12, 'mozart', 104)   # chorus 2
CADENCE = [(s - 6, d, p) for s, d, p in mz.PHRASE if s >= 5.9]   # A (grace) G F E F: the end of Mozart's theme
mozart(CADENCE, 52, 0, 'lead', 100, HOOK2, 'echo')                  # chorus 3, an octave over the counter-melody

# ---------------------------------------------------------------- 3. make room for the new melody
# In the changed passages, a background note that rubs a semitone against the new melody for an 8th
# or more, and isn't a tone of the chord there (v18's held notes that belonged to the old melody's
# harmony), stops where the new note starts.
NEW_MELODY = ('lead_v', 'lead', 'mozart')   # (the string doublings are spared too: they move with it)
SPARE = set(NEW_MELODY) | {'o_vla', 'o_vc', 'echo', 'echo_v', 'w_hookL', 'w_hookR', 'w_vox', 'harm', 'kick', 'snare', 'hats', 'cym', 'riser', 'revcym', 'boom', 'o_cym'}
mel = sorted(n for r in NEW_MELODY for n in N[r] if inside(n[0]))
trimmed = collections.Counter()
for r in list(N):
    if r in SPARE: continue
    out = []
    for n in N[r]:
        s, en, p, v = n
        if inside(s) or inside(en - 1):
            for s2, e2, p2, v2 in mel:
                if min(en, e2) - max(s, s2) >= 240 and abs(p - p2) % 12 in (1, 11):
                    t = max(s, s2); bar = int(t // BAR) + 1; pcs, _ = chord_at(bar, int((t % BAR) // (2 * BEAT)))
                    if p % 12 not in pcs:
                        trimmed[r] += 1; n = (s, s2, p, v) if s2 - s >= 60 else None; break
        if n: out.append(n)
    N[r] = out

# ---------------------------------------------------------------- 4. verse balance
# The Chaconne line sits at the user's verse-tune balance (about +2.2 dB over everything else in
# verse 2): the accompaniment there goes a little further back.
EXTRA_REST = {21: 0.0}   # revision 2: the lighter line needs no extra room (measured +2.9 with -0.9)
DOUBLING = {21: 'o_vla'}
base_trim = e.trim
def trim(t, role=None):
    db = base_trim(t, role); a, b, k = e.section(t // BAR + 1)
    if k == 'verse' and a in EXTRA_REST and role not in e.LEADS and role != DOUBLING[a]: db += EXTRA_REST[a]
    return db
e.trim = trim

if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
    out.mkdir(parents=True, exist_ok=True)
    names = {k: v.replace('electronic_lush', 'electronic_lush_variations') for k, v in lush.OUT.items()}
    for tag in 'ABCD':
        mf = e.build(tag)
        mf.tracks[0][[i for i, m in enumerate(mf.tracks[0]) if m.type == 'track_name'][0]].name = f'Wasting My Time (electronic, lush + variations) - part {lush.TITLE[tag]}'
        mf.save(out / names[tag])
    print('wrote', ', '.join(names.values()))
    print('old-melody notes taken out:', dict(removed)); print('background notes trimmed for the new melody:', dict(trimmed))
