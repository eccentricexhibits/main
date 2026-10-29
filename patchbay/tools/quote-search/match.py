"""Find passages in the indexed corpora whose harmony follows the song's progressions.
usage: python3 -I match.py idx_bach idx_beethoven idx_mozart"""
import numpy as np, pickle, sys, pathlib, json
NN = {'C':0,'C#':1,'Db':1,'D':2,'Eb':3,'E':4,'F':5,'F#':6,'G':7,'Ab':8,'A':9,'Bb':10,'B':11}
Q = {'':[0,4,7],'m':[0,3,7],'7':[0,4,7,10],'m7':[0,3,7,10],'maj7':[0,4,7,11],'add9':[0,4,7,2],'9':[0,4,7,10,2],'m7add11':[0,3,7,10,5],'sus':[0,5,7,10]}
def ch(name, bass=None):
    r = name[:2] if len(name) > 1 and name[1] in '#b' else name[:1]
    pcs = [(NN[r] + i) % 12 for i in Q[name[len(r):]]]; return pcs, NN[bass] if bass else NN[r]
TARGETS = {
 'verse':  [ch(x) for x in ['A7','A7','Dm','C','Bbmaj7','A7','Dm','C','Bbmaj7','A7','Dm','Dm']],
 'chorus': [ch(x) for x in ['Gm7','C7','F','F','Gm7','C7','F','F']],
 'bridge': [ch('Am7'), ch('Bbadd9','A'), ch('Gm7add11'), ch('C9')] * 2,
}
NAMES = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
def tmpl(pcs, t):
    v = np.zeros(12); v[[(p + t) % 12 for p in pcs]] = 1; return v / np.linalg.norm(v)
res = {k: [] for k in TARGETS}
for d in sys.argv[1:]:
    d = pathlib.Path(d); idx = pickle.load(open(d / 'index.pkl', 'rb')); comp = d.name[4:]
    for i, rec in enumerate(idx):
        z = np.load(d / f'{i:05d}.npz'); pc, low = z['pc'].astype(float), z['low'].astype(int)
        nb = len(pc); barlen = rec['sig'][0] * 4 / rec['sig'][1]
        for u in (1, 2, 3, 4):
            if nb < u * 8: continue
            cs = np.cumsum(np.vstack([np.zeros(12), pc]), axis=0); U = cs[u:] - cs[:-u]          # unit starting at every beat
            nrm = np.linalg.norm(U, axis=1); ok = nrm > 0.2; Un = U / np.maximum(nrm, 1e-9)[:, None]
            L = np.array([low[j:j + u].min() for j in range(len(U))]); Lpc = np.where(L < 999, L % 12, -1)
            for name, prog in TARGETS.items():
                n = len(prog); span = (n - 1) * u; J = len(U) - span
                if J <= 0: continue
                for t in range(12):
                    cos = np.zeros(J); bas = np.zeros(J); empty = np.zeros(J, bool)
                    for k, (pcs, b) in enumerate(prog):
                        sl = slice(k * u, k * u + J)
                        cos += Un[sl] @ tmpl(pcs, -t); bas += (Lpc[sl] == (b - t) % 12); empty |= ~ok[sl]
                    score = 0.6 * cos / n + 0.4 * bas / n; score[empty] = 0
                    j = int(score.argmax())
                    res[name].append(dict(score=float(score[j]), cos=float(cos[j] / n), bass=float(bas[j] / n), comp=comp, path=rec['path'], unit=u,
                        beat=j, bar=j / barlen + 1, barstart=abs((j / barlen) - round(j / barlen)) < 1e-6, t=t, sig=rec['sig'],
                        key=NAMES[(5 - t) % 12] + ' maj / ' + NAMES[(2 - t) % 12] + ' min', unit_sec=u * rec['spb']))
for name in res:
    best = {}
    for r in res[name]:
        k = r['path']
        if k not in best or r['score'] > best[k]['score']: best[k] = r
    L = sorted(best.values(), key=lambda r: -r['score'])
    json.dump(L[:200], open(f'top_{name}.json', 'w'), indent=0)
    print(f'\n=== {name}: top 25 of {len(L)} pieces')
    for r in L[:25]:
        print(f"{r['score']:.3f} (fit {r['cos']:.2f}, bass {r['bass']:.2f}) {r['comp']:9} {r['path'][-70:]:70} u={r['unit']} bar {r['bar']:.2f} {'|' if r['barstart'] else ' '} key {r['key']:16} {r['unit_sec']:.2f}s/chord")
