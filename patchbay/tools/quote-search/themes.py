"""Like match.py, but only windows that start in a movement's first bars (where its theme is stated),
scored with the tempo and meter preferences, against full and half-length song progressions."""
import numpy as np, pickle, sys, pathlib, json, math
exec(open('match.py').read().split('res = {')[0])     # NN, Q, ch, TARGETS, NAMES, tmpl
TARGETS.update({
 'verse_a': [ch(x) for x in ['Dm','C','Bbmaj7','A7','Dm','C']],          # verse bars 8-10
 'verse_b': [ch(x) for x in ['A7','A7','Dm','C','Bbmaj7','A7']],          # verse bars 7-9
 'chorus_half': [ch(x) for x in ['Gm7','C7','F','F']],
 'bridge_half': [ch('Am7'), ch('Bbadd9','A'), ch('Gm7add11'), ch('C9')],
})
SONG = 2 * 60 / 156
res = []
for d in sys.argv[1:]:
    d = pathlib.Path(d); idx = pickle.load(open(d / 'index.pkl', 'rb')); comp = d.name[4:]
    for i, rec in enumerate(idx):
        z = np.load(d / f'{i:05d}.npz'); pc, low = z['pc'].astype(float), z['low'].astype(int)
        barlen = rec['sig'][0] * 4 / rec['sig'][1]; lim = int(barlen * 4) + 1   # windows starting in the first 4 bars
        for u in (1, 2, 4):
            cs = np.cumsum(np.vstack([np.zeros(12), pc]), axis=0); U = cs[u:] - cs[:-u]
            if len(U) < 4 * u + lim: continue
            nrm = np.linalg.norm(U, axis=1); ok = nrm > 0.2; Un = U / np.maximum(nrm, 1e-9)[:, None]
            L = np.array([low[j:j + u].min() for j in range(len(U))]); Lpc = np.where(L < 999, L % 12, -1)
            unit_sec = u * rec['spb']; ratio = SONG / max(unit_sec, 1e-3)
            tempo = math.exp(-abs(math.log(ratio)) / math.log(1.6)); duple = rec['sig'][0] in (2, 4)
            for name, prog in TARGETS.items():
                n = len(prog); J = min(lim, len(U) - (n - 1) * u)
                if J <= 0: continue
                for t in range(12):
                    cos = np.zeros(J); bas = np.zeros(J); empty = np.zeros(J, bool)
                    for k, (pcs, b) in enumerate(prog):
                        sl = slice(k * u, k * u + J); cos += Un[sl] @ tmpl(pcs, -t); bas += (Lpc[sl] == (b - t) % 12); empty |= ~ok[sl]
                    score = 0.6 * cos / n + 0.4 * bas / n; score[empty] = 0
                    j = int(score.argmax()); s = float(score[j])
                    adj = s * (0.7 + 0.3 * tempo) * (1.0 if duple else 0.85)
                    res.append(dict(target=name, adj=adj, score=s, comp=comp, path=rec['path'], unit=u, beat=j, bar=j / barlen + 1, t=t,
                        key=NAMES[(5 - t) % 12] + '/' + NAMES[(2 - t) % 12] + 'm', ratio=ratio, sig=rec['sig'], n=n))
best = {}
for r in res:
    k = (r['target'], r['path'])
    if k not in best or r['adj'] > best[k]['adj']: best[k] = r
json.dump(list(best.values()), open('themes.json', 'w'))
for name in TARGETS:
    L = sorted((r for r in best.values() if r['target'] == name), key=lambda r: -r['adj'])
    print(f'\n=== {name} ({len(TARGETS[name])} chords): themes that fit')
    for r in L[:10]:
        print(f"{r['adj']:.3f} raw {r['score']:.2f} {r['comp']:9} {r['path'][-64:]:64} u={r['unit']} bar {r['bar']:.2f} in {r['key']:8} x{r['ratio']:.2f} {r['sig'][0]}/{r['sig'][1]}")
