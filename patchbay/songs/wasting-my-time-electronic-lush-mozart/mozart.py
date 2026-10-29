"""Wasting My Time, electronic (lush) + Mozart: the lush version with a counter-melody from
Mozart's Bassoon Concerto in B-flat, K. 191, 2nd movement (Andante ma adagio), in every chorus.

usage: python3 mozart.py [out folder]   (default: this script's folder)

Why this piece: a search of 1,592 Bach, Beethoven and Mozart MIDI files for passages whose
harmony follows the song's progressions, at their written tempo, ranked this movement's opening
theme first for the chorus (Gm7 C7 | F | Gm7 C7 | F):
- It's in F major, the song's key, so it needs no transposition.
- Its bass moves G–C–F–A–B♭–C–F (ii–V–I–I6–IV–V–I): the chorus progression.
- One Mozart beat per song chord puts it within 3% of its written tempo, and the phrase
  fills one 4-bar chorus exactly.
- The tune is a chain of falling sighs (F–E, B♭–A, A–G–F, E–F), melancholic and lyrical.
  Mozart reworked it as the Countess's lament "Porgi, amor" in The Marriage of Figaro.

Placement:
- Choruses 1–3: an octave below written pitch (E3–G4), a tenor line under the hook. It moves
  while the hook holds its long G and A.
- Final chorus: written pitch (E4–G5), under the hook, which is an octave higher there. Its
  last two bars repeat the phrase's cadence.

One arranger's change: the first sigh's E is moved from Mozart's half-beat to the song's
chord change, so it resolves on the C7 instead of rubbing against the Gm7's F.
Source: violins I, bars 1-3, Mutopia Project edition (typeset by Liang Seng, public domain).
"""
import importlib.util, pathlib, sys, json
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('lush', HERE.parent / 'wasting-my-time-electronic-lush' / 'lush.py')
lush = importlib.util.module_from_spec(spec); spec.loader.exec_module(lush)   # builds the lush version's parts
e = lush.e; T, BAR, add = e.T, e.BAR, e.add

# Mozart's theme in his beats (quarter notes, 2/2 time): (start beat, length in beats, MIDI pitch).
# Beat 2 is the downbeat of the phrase over ii (G bass); the 0.05-beat notes are his grace notes.
PHRASE = [(1.9427, 0.0547, 79), (2.0, 0.5, 77), (2.5, 0.5, 76), (3.5, 0.4427, 70), (3.9427, 0.0547, 72), (4.0, 0.5, 70),
          (4.5, 0.5, 69), (5.5, 0.4427, 69), (5.9427, 0.0547, 69), (6.0, 0.5, 67), (6.5, 1.0, 65), (7.5, 0.5, 64), (8.0, 1.0, 65)]
ADAPT = {(2.0, 77): (2.0, 1.0), (2.5, 76): (3.0, 0.5)}   # the first sigh: F held to the chord change, E on the C7
SIGH_TOP = {2.0, 3.5, 4.0, 5.5, 6.0, 7.5}               # the leaning note of each sigh is the louder one

e.ROLES['mozart'] = ('D', 11, 'Mozart counter-melody (K. 191)', 12, 80, 127, -14, 80)   # Square Lead 2
e.LEADS = e.LEADS + ('mozart',)   # a melody: full level in every section, no verse trim
def place(bar, first, last, shift, vel=1.0):
    """Mozart beats [first, last) from song bar `bar`: one Mozart beat = one song chord (half a bar)."""
    for s, d, p in PHRASE:
        if not (first - 0.1 <= s < last): continue
        s2, d2 = ADAPT.get((s, p), (s, d))
        t0 = T(bar) + (s2 - first) * 960
        v = 84 if d2 < 0.1 else (120 if s2 in SIGH_TOP else 100)   # about 4 dB under the hook
        add('mozart', t0, t0 + max(d2 * 960 - 20, 40), p + shift, v * vel)
for bar in (17, 31, 50): place(bar, 2, 10, -12)
place(83, 2, 10, 0, 1.05); place(87, 6, 10, 0, 1.05)

if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
    out.mkdir(parents=True, exist_ok=True)
    names = {k: v.replace('electronic_lush', 'electronic_lush_mozart') for k, v in lush.OUT.items()}
    for tag in 'ABCD':
        mf = e.build(tag)
        mf.tracks[0][[i for i, m in enumerate(mf.tracks[0]) if m.type == 'track_name'][0]].name = f'Wasting My Time (electronic, lush + Mozart) - part {lush.TITLE[tag]}'
        mf.save(out / names[tag])
    print('wrote', ', '.join(names.values()), '·', len(e.NOTES['mozart']), 'Mozart notes')
