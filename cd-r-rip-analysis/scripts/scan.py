import sys, os, numpy as np
root = sys.argv[1]
for dp, dn, fn in sorted(os.walk(root)):
    for f in sorted(fn):
        if f.startswith('._') or f in ('Icon','DrasticMeasures-SelectionsCD','DrasticMeasures-New Songs'): continue
        p = os.path.join(dp,f); ch = 2 if 'Selections' in dp else 1
        x = np.frombuffer(open(p,'rb').read(), '>i2').astype(np.int64).reshape(-1,ch)
        hits_blk = 0; iso = []
        for c in range(ch):
            y = x[:,c]
            pred = (y[:-2]+y[2:])//2; mid = y[1:-1]
            nb = np.minimum(np.abs(y[:-2]), np.abs(y[2:]))
            m = (mid == 0) & (nb > 300) & (np.sign(y[:-2]) == np.sign(y[2:]))
            idx = np.nonzero(m)[0]+1
            iso += list(idx)
            hits_blk += int(np.sum((idx % 131072) == 131071))
        print(f'{os.path.relpath(p,root):70} isolated-zero glitches: {len(iso):4d}  at 128k-block ends: {hits_blk}')
