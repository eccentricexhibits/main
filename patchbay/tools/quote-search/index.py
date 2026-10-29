"""Index a MIDI corpus: per piece, pitch-class duration vectors and lowest note per quarter-note beat.
usage: python3 -I index.py <corpus dir> <out.npz-dir>"""
import mido, sys, pathlib, numpy as np, pickle, traceback
root, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
idx = []
files = sorted(p for p in root.rglob('*') if p.suffix.lower() in ('.mid', '.midi'))
for n, f in enumerate(files):
    try:
        m = mido.MidiFile(f, clip=True); tpb = m.ticks_per_beat
        notes = []; tempos = [(0, 500000)]; sigs = []
        for tr in m.tracks:
            t = 0; on = {}
            for x in tr:
                t += x.time
                if x.type == 'set_tempo': tempos.append((t, x.tempo))
                elif x.type == 'time_signature': sigs.append((t, x.numerator, x.denominator))
                elif x.type == 'note_on' and x.velocity and x.channel != 9: on.setdefault((x.channel, x.note), []).append(t)
                elif x.type in ('note_on', 'note_off') and x.channel != 9 and on.get((x.channel, x.note)):
                    s = on[(x.channel, x.note)].pop(0)
                    if t > s: notes.append((s / tpb, t / tpb, x.note))
        if len(notes) < 20: continue
        nb = int(np.ceil(max(e for s, e, p in notes)))
        pc = np.zeros((nb, 12)); low = np.full(nb, 999); top = np.full(nb, -1)
        for s, e, p in notes:
            for b in range(int(s), min(nb, int(np.ceil(e)))):
                ov = min(e, b + 1) - max(s, b)
                if ov <= 0: continue
                pc[b, p % 12] += ov
                if ov > 0.2: low[b] = min(low[b], p); top[b] = max(top[b], p)
        tempos.sort(); sigs.sort()
        sec_per_beat = np.median([te for _, te in tempos[-50:]]) / 1e6 if len(tempos) > 1 else 0.5
        rec = dict(path=str(f.relative_to(root)), nb=nb, sig=(sigs[0][1], sigs[0][2]) if sigs else (4, 4), spb=float(sec_per_beat), nnotes=len(notes))
        np.savez_compressed(out / f'{len(idx):05d}.npz', pc=pc.astype(np.float32), low=low.astype(np.int16), top=top.astype(np.int16))
        idx.append(rec)
    except Exception as ex:
        print('skip', f.name, type(ex).__name__, ex)
pickle.dump(idx, open(out / 'index.pkl', 'wb'))
print(root.name, 'indexed', len(idx), 'of', len(files))
