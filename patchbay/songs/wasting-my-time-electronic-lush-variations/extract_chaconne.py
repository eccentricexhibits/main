"""Write chaconne-top-voice.json: the top voice of bars 1-25 of Bach's Chaconne (BWV 1004/5),
as {bar: [[start beat in the 3/4 bar, length in beats, MIDI pitch], ...]}.
usage: python3 -I extract_chaconne.py <bwv-1004_5.mid from the Mutopia Project>"""
import mido, sys, json, pathlib
m = mido.MidiFile(sys.argv[1]); tpb = m.ticks_per_beat; ns = []
for tr in m.tracks:
    t = 0; on = {}
    for x in tr:
        t += x.time
        if x.type == 'note_on' and x.velocity: on[x.note] = t
        elif x.type in ('note_on', 'note_off') and x.note in on: s = on.pop(x.note); ns.append((s / tpb, t / tpb, x.note))
out = {}
for b in range(1, 26):
    a = (b - 1) * 3; top = {}
    for s, en, p in ns:   # the highest note at each onset (the top of Bach's chords is the melody)
        if a <= s < a + 3 and (s not in top or p > top[s][1]): top[s] = (en, p)
    on = sorted(top)
    out[b] = [[round(s - a, 4), round(min(top[s][0], on[i + 1] if i + 1 < len(on) else a + 3) - s, 4), top[s][1]] for i, s in enumerate(on)]
(pathlib.Path(__file__).resolve().parent / 'chaconne-top-voice.json').write_text(json.dumps(out))
print('wrote bars 1-25:', sum(len(v) for v in out.values()), 'notes')
