import sys, os, numpy as np
B = sys.argv[1]; A = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
rd = lambda p: np.frombuffer(open(p,'rb').read(), '>i2').astype(np.int32)
pairs = {"Baby Dolls":"Baby Dolls", "30'sGermanNightclub":"I Believe copy-2", "I Believe.wav":"I Believe-0",
         "Teddy Bears Live":"Teddy Bears Live-0", "WarIsPeace":"WarIsPeace-1"}
for sel, src in pairs.items():
    s = rd(SEL+sel).reshape(-1,2); L = rd(A+src+'.L'); R = rd(A+src+'.R')
    n = min(len(s), len(L))
    # find best offset (in case of trimming) via exact match search on R channel
    best = None
    for off in range(-0, 1):
        pass
    eqL = np.array_equal(s[:n,0], L[:n]); eqR = np.array_equal(s[:n,1], R[:n])
    if eqL and eqR:
        print(f'{sel!r:24} == {src}.L/.R  bit-identical over {n} frames (sel {len(s)}, src {len(L)})'); continue
    # try to locate offset by matching a chunk
    k = 44100*10
    chunk = R[k:k+64]
    idx = [i for i in range(0, len(s)-64) if s[i,1]==chunk[0] and np.array_equal(s[i:i+64,1], chunk)][:1] if True else []
    if idx:
        off = idx[0]-k
        a0 = max(0, off); b0 = max(0, -off); m = min(len(s)-a0, len(L)-b0)
        dL = np.sum(s[a0:a0+m,0] != L[b0:b0+m]); dR = np.sum(s[a0:a0+m,1] != R[b0:b0+m])
        print(f'{sel!r:24} ~ {src}  offset {off} frames ({off/44100:.2f}s), overlap {m}, diff samples L={dL} R={dR}')
    else:
        print(f'{sel!r:24} vs {src}: no exact alignment found (different mix/bounce)')
