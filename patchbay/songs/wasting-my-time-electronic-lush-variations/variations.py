"""Wasting My Time, electronic (lush + variations): the main melody develops through the song.

usage: python3 variations.py [out folder]   (default: this script's folder)

The lush + Mozart version keeps one verse tune and one chorus hook throughout. Here the melody
changes as the song goes on, using passages chosen by the same harmonic search as before
(../../tools/quote-search/): they follow the song's chords at about their written tempo.

Verses: Bach, Chaconne from the Partita No. 2 in D minor, BWV 1004. The Chaconne is a set of
variations over a four-bar ground (D – C# – G/Bb – A), essentially the verse's own bass
(D – C – Bb – A). Each later verse takes a successive variation, as Bach's do:
- Verse 1: the song's own tune (unchanged).
- Verse 2: the Chaconne's opening theme (bars 1-8), led in by the run that closes its first half (bar 4).
- Verse 3: Bach's next variation (bars 9-16): dotted rhythms and quick turns.
- Verse 4: the variation after (bars 17-24), higher and more intense.
Each Chaconne bar fills one of the song's chords (half a bar), so its 3/4 sits as quarter-note
triplets over the song's 4/4. Each verse's last bar is Bach's next bar compressed to beats 1-3,
so the pickup into the pre-chorus (beat 4) is kept. Bach's C# (D minor's leading tone) is
played as C wherever it would rub against the song's C chord.

Choruses: Mozart, Bassoon Concerto K. 191, 2nd movement, already the counter-melody.
- Chorus 1: the hook twice (unchanged).
- Chorus 2: the hook, then Mozart's bassoon answer from bar 29 (G F E F | D D C Bb) on the
  lead, with his violins' line from the same bars as the counter-melody.
- Chorus 3: the hook, then his florid violin passage from bar 39 on the lead, with the bassoon
  line beneath.
- Final chorus: the variation you liked (unchanged).

Where the melody changes, every background part that doubled the old melody there is taken out
(the lead's echoes, detuned twins and vocal double, and the synth-orchestra lines that move with
it), so the old tune doesn't play against the new one.
"""
import importlib.util, pathlib, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mozart', HERE.parent / 'wasting-my-time-electronic-lush-mozart' / 'mozart.py')
mz = importlib.util.module_from_spec(spec); spec.loader.exec_module(mz)
lush, e = mz.lush, mz.e
T, BAR, BEAT, add, chord_at = e.T, e.BAR, e.BEAT, e.add, e.chord_at
N = e.NOTES

# ---------------------------------------------------------------- source material (pitch, start beat, length in beats)
# Bach, Chaconne BWV 1004: the top voice of bars 1-25 is in chaconne-top-voice.json (written by
# extract_chaconne.py from the Mutopia edition typeset by Hajo Dezelski, CC BY-SA 3.0).
# Mozart, K. 191, 2nd mvt (Mutopia, Liang Seng, public domain), in his quarter-note beats from the passage's start.
MOZ_BASSOON_29 = [(-0.057, 0.055, 57), (0, 0.5, 55), (0.5, 1, 53), (1.5, 0.5, 52), (2, 0.25, 53), (2.25, 0.25, 62), (2.5, 1, 62), (3.5, 0.25, 60), (3.75, 0.25, 58)]
MOZ_VIOLIN_29 = [(0.25, 0.25, 67), (0.5, 0.25, 65), (0.75, 0.125, 65), (1, 0.25, 65), (1.25, 0.25, 69), (1.5, 0.25, 67), (1.75, 0.25, 64), (2, 1, 65)]
MOZ_VIOLIN_39 = [(0, .125, 70), (.125, .125, 72), (.25, .125, 70), (.375, .125, 69), (.5, .25, 67), (.75, .125, 67), (1, .125, 67), (1.25, .25, 67), (1.5, .25, 69),
                 (1.75, .25, 70), (2, .125, 72), (2.125, .125, 74), (2.25, .125, 72), (2.375, .125, 70), (2.5, .25, 69), (2.75, .125, 69), (3, .125, 69), (3.25, .25, 72), (3.5, .25, 70), (3.75, .25, 69)]
MOZ_BASSOON_39 = [(0, 1, 48), (1, 0.75, 58), (1.75, .125, 57), (1.875, .125, 58), (2, .25, 57), (2.25, .5, 65), (2.75, .5, 60), (3.25, .5, 57), (3.75, .25, 53)]

# ---------------------------------------------------------------- 1. take the old melody out where it changes
VERSE_SPANS = [(21, 26), (40, 45), (73, 78)]            # verse 2, 3, 4: bars, up to beat 4 of the last (the pickup stays)
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
              ((40, 45), {'o_vc': 'pc', 'o_lowreed': 'pc'}),                # verse 3: cellos, bassoons
              ((73, 78), {'o_vn1': 'pc', 'o_vn2': 'pc', 'o_flute': 'pc', 'o_reed': 'pc'}),   # verse 4: violins, flutes, oboes
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
# The Mozart counter-melody's second half in choruses 2 and 3 makes way for Mozart's own second voice there.
N['mozart'] = [n for n in N['mozart'] if not any(T(a) <= n[0] < T(b) for a, b in CHORUS_SPANS)]

# ---------------------------------------------------------------- 2. the new melodies
def fit_to_chord(t, p, dur):
    """A long note a semitone from a chord tone and outside the chord moves onto the chord (Bach's C# over C becomes C)."""
    bar = int(t // BAR) + 1; half = int((t % BAR) // (2 * BEAT))
    pcs, _ = chord_at(bar, half)
    if p % 12 in pcs or dur < 240: return p
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
def bach(spec, bars):
    """spec: [(Chaconne bar, song bar, half 0/1, song beats it fills)]."""
    out = []
    for cb, sb, half, beats in spec:
        t0 = T(sb, 1 + 2 * half); k = beats / 3 * BEAT   # ticks per Chaconne beat
        out += [(int(t0 + s * k), int(d * k), p) for s, d, p in bars[cb]]
    return out
def verse_spec(first, song_bar, lead_in):
    """A lead-in bar (an A bar) over the A7 bar, eight bars over the Dm C | Bbmaj7 A7 pairs, then one bar in beats 1-3."""
    s = [(lead_in, song_bar, 0, 4)]
    for i in range(8): s.append((first + i, song_bar + 1 + i // 2, i % 2, 2))
    s.append((first + 8, song_bar + 5, 0, 3))
    return s
import json
CHACONNE = {int(k): [tuple(x) for x in v] for k, v in json.loads((HERE / 'chaconne-top-voice.json').read_text()).items()}
VOX = [('w_vox', 0, 0.75)]
melody('lead_v', bach(verse_spec(1, 21, 4), CHACONNE), 98, echo='echo_v', double=VOX + [('o_vla', -12, 0.95)])   # verse 2: the theme, violas an octave under as before
melody('lead_v', bach(verse_spec(9, 40, 8), CHACONNE), 98, echo='echo_v', double=VOX + [('o_vc', -12, 1.0)])     # verse 3: variation 2, cellos an octave under
melody('lead', bach(verse_spec(17, 73, 16), CHACONNE), 100, echo='echo',                          # verse 4: variation 3
       double=[('w_hookL', 0, 0.82), ('w_hookR', 0, 0.82), ('harm', -12, 0.8)])
def mozart(src, bar, shift, role, vel, double=None, echo=None):
    melody(role, [(int(T(bar) + s * 960), int(d * 960), p + shift) for s, d, p in src], vel, echo=echo, double=double)
HOOK2 = [('w_hookL', 0, 0.82), ('w_hookR', 0, 0.82)]
mozart(MOZ_BASSOON_29, 33, 12, 'lead', 100, HOOK2, 'echo'); mozart(MOZ_VIOLIN_29, 33, -12, 'mozart', 104)   # chorus 2
mozart(MOZ_VIOLIN_39, 52, 0, 'lead', 100, HOOK2, 'echo'); mozart(MOZ_BASSOON_39, 52, 0, 'mozart', 104)     # chorus 3

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
# The Chaconne lines sit at the user's verse-tune balance (about +2.2 dB over everything else in
# verse 2, +1.6 in verse 3): the accompaniment in those two verses goes a little further back.
EXTRA_REST = {21: -0.9, 40: -1.6}
DOUBLING = {21: 'o_vla', 40: 'o_vc'}
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
