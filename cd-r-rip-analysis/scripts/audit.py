import sys, os, numpy as np, hashlib
root = sys.argv[1]
rows = []
for dp, dn, fn in os.walk(root):
    for f in sorted(fn):
        if f.startswith('._') or f in ('Icon','DrasticMeasures-SelectionsCD','DrasticMeasures-New Songs'): continue
        p = os.path.join(dp, f); raw = open(p,'rb').read()
        ch = 2 if 'Selections' in dp else 1
        odd = len(raw) % (2*ch)
        be = np.frombuffer(raw[:len(raw)-odd], '>i2').astype(np.int32)
        le = np.frombuffer(raw[:len(raw)-odd], '<i2').astype(np.int32)
        smooth_be = np.mean(np.abs(np.diff(be))); smooth_le = np.mean(np.abs(np.diff(le)))
        x = be.reshape(-1, ch)
        n = len(x); dur = n/44100
        nz = np.nonzero(np.any(x != 0, axis=1))[0]
        first, last = (nz[0], nz[-1]) if len(nz) else (0, 0)
        inner = x[first:last+1]
        # longest interior run of digital silence
        z = np.all(inner == 0, axis=1).astype(np.int8)
        d = np.diff(np.concatenate([[0], z, [0]])); starts = np.where(d==1)[0]; ends = np.where(d==-1)[0]
        runs = ends - starts
        long_runs = [(int(s+first), int(r)) for s, r in zip(starts, runs) if r >= 256]
        # 2048-byte (data CD sector) aligned zero blocks inside audio
        blk = 2048
        nb = len(raw)//blk
        b = np.frombuffer(raw[:nb*blk], np.uint8).reshape(nb, blk)
        zb = np.where(~b.any(axis=1))[0]
        fb, lb = (first*2*ch)//blk, (last*2*ch)//blk
        inner_zb = [int(i) for i in zb if fb < i < lb]
        peak = int(np.abs(x).max()); clip = int(np.sum(np.abs(x) >= 32767))
        rms = float(np.sqrt(np.mean(x.astype(np.float64)**2)))
        # spikes: sample-to-sample jump far above local norm
        dd = np.abs(np.diff(x[:,0]))
        spikes = int(np.sum(dd > 20000))
        rows.append((os.path.relpath(p, root), len(raw), odd, ch, dur, 'BE' if smooth_be < smooth_le else 'LE?', peak, clip, round(20*np.log10(rms/32768+1e-12),1), first/44100, (n-last)/44100, long_runs[:4], len(long_runs), len(inner_zb), spikes, hashlib.md5(raw).hexdigest()[:10]))
for r in rows:
    print(' | '.join(str(v) if not isinstance(v, float) else f'{v:.2f}' for v in r))
