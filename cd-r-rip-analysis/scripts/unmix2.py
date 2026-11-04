import sys, numpy as np
sys.path.insert(0, sys.argv[2] if len(sys.argv) > 2 else '.')
from unmix import load, place
N, H = 2048, 512; W = np.sqrt(np.hanning(N+1)[:-1])
def stft(x):
    fr = np.lib.stride_tricks.sliding_window_view(np.r_[np.zeros(N), x, np.zeros(N)], N)[::H]
    return np.fft.rfft(fr*W, axis=1)
def istft(X, n):
    fr = np.fft.irfft(X, N, axis=1)*W; y = np.zeros((len(fr)-1)*H+N)
    for i, f in enumerate(fr): y[i*H:i*H+N] += f
    return y[N:N+n] / (np.sum(W**2)/H)
def smooth_t(A, k):   # moving average along time axis
    c = np.cumsum(np.vstack([np.zeros((1,)+A.shape[1:], A.dtype), A]), axis=0)
    out = (c[k:] - c[:-k])/k; pad = k//2
    return np.vstack([np.repeat(out[:1], pad, 0), out, np.repeat(out[-1:], len(A)-len(out)-pad, 0)])
def separate(mixc, v, taps=6, ksm=86, reg=1e-2, chunk=32):
    """per-bin multi-frame (convolutive) time-varying least squares: Y(t,f) ~ sum_k G_k(t,f) X(t-k,f)"""
    X = stft(v).astype(np.complex128); Y = stft(mixc).astype(np.complex128); T, F = X.shape
    E = np.zeros_like(Y)
    for f0 in range(0, F, chunk):
        sl = slice(f0, min(F, f0+chunk)); Xc = X[:, sl]; nf = Xc.shape[1]
        Xs = np.stack([np.vstack([np.zeros((k, nf), np.complex128), Xc[:T-k]]) for k in range(taps)], -1)
        R = smooth_t(np.einsum('tfi,tfj->tfij', Xs.conj(), Xs), ksm)
        p = smooth_t(np.einsum('tfi,tf->tfi', Xs.conj(), Y[:, sl]), ksm)
        lam = reg*np.trace(R, axis1=2, axis2=3).real[...,None,None]/taps + 1e-12
        G = np.linalg.solve(R + lam*np.eye(taps, dtype=np.complex128), p[...,None])[...,0]
        E[:, sl] = np.einsum('tfk,tfk->tf', G, Xs)
    return istft(Y - E, len(mixc)), istft(E, len(mixc))
if __name__ == '__main__':
    B = sys.argv[1]; AF = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
    out = sys.argv[3]
    for tag, mixf, voxf, start in (("IBelieve", "I Believe.wav", "vox-IBelieve-9", -59467), ("30sNightclub", "30'sGermanNightclub", "vox--11", -117228)):
        mix = load(SEL+mixf, 2); v = place(load(AF+voxf,1)[:,0], start, len(mix))
        inst = np.zeros_like(mix); vin = np.zeros_like(mix)
        for c in range(2): inst[:,c], vin[:,c] = separate(mix[:,c], v)
        fr = 4410; e = lambda x: np.array([np.mean(x[i*fr:(i+1)*fr]**2) for i in range(len(x)//fr)])
        act = e(v) > np.percentile(e(v), 70)
        def band(x, lo, hi):
            Xf = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/44100); Xf[(f<lo)|(f>hi)] = 0; return np.fft.irfft(Xf, len(x))
        for lo, hi in ((200,800),(800,2500),(2500,5000)):
            mb, ib = band(mix.mean(1),lo,hi), band(inst.mean(1),lo,hi)
            a, n = e(ib)[act].sum()/e(mb)[act].sum(), e(ib)[~act].sum()/e(mb)[~act].sum()
            print(f'{tag} {lo}-{hi} Hz: vocal sections {10*np.log10(a):6.1f} dB, non-vocal sections {10*np.log10(n):6.1f} dB')
        np.save(f'{out}/{tag}_inst.npy', inst.astype(np.float32)); np.save(f'{out}/{tag}_vocal_in_mix.npy', vin.astype(np.float32))
