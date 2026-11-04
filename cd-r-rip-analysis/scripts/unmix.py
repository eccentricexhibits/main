import sys, numpy as np
SR = 44100
def load(p, ch): return np.frombuffer(open(p,'rb').read(), '>i2').astype(np.float64).reshape(-1,ch)/32768
def place(x, start, n):
    """put mono x so that it starts at sample `start` of an n-sample timeline"""
    y = np.zeros(n); a, b = max(0, start), min(n, start+len(x))
    if b > a: y[a:b] = x[a-start:b-start]
    return y
def wiener_fir(x, y, nfft=8192, taps=4096):
    """estimate FIR h with y ~= h*x (frame-averaged cross spectra), return h"""
    hop = nfft//2; w = np.hanning(nfft)
    Sxx = np.zeros(nfft//2+1); Sxy = np.zeros(nfft//2+1, complex)
    for i in range(0, len(x)-nfft, hop):
        X = np.fft.rfft(w*x[i:i+nfft]); Y = np.fft.rfft(w*y[i:i+nfft])
        Sxx += (X*X.conj()).real; Sxy += Y*X.conj()
    H = Sxy/(Sxx + 1e-3*Sxx.mean())
    h = np.fft.irfft(H, nfft)
    h = np.roll(h, taps//2)[:taps] * np.hanning(taps)   # allow +-taps/2 latency
    return h, taps//2
def apply_fir(x, h, delay):
    n = 1 << int(np.ceil(np.log2(len(x)+len(h))))
    y = np.fft.irfft(np.fft.rfft(x, n)*np.fft.rfft(h, n), n)[:len(x)+len(h)]
    return y[delay:delay+len(x)]
def unmix(mix, vox, start):
    n = len(mix); v = place(vox, start, n); out = np.empty_like(mix); est = np.empty_like(mix)
    for c in range(mix.shape[1]):
        h, dl = wiener_fir(v, mix[:,c]); e = apply_fir(v, h, dl)
        est[:,c] = e; out[:,c] = mix[:,c] - e
    return out, est, v
if __name__ == '__main__':
    B = sys.argv[1]; AF = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
    for mixf, voxf, start in (("I Believe.wav", "vox-IBelieve-9", 76327-16860 and (16860-76327)), ("30'sGermanNightclub", "vox--11", -117228)):
        mix = load(SEL+mixf, 2); vox = load(AF+voxf, 1)[:,0]
        inst, est, v = unmix(mix, vox, start)
        # measure: energy in frames where vocal is loud
        fr = 4410; nfr = len(mix)//fr
        ve = np.array([np.mean(v[i*fr:(i+1)*fr]**2) for i in range(nfr)])
        loud = ve > np.percentile(ve, 70)
        me = np.array([np.mean(mix[i*fr:(i+1)*fr]**2) for i in range(nfr)]); ie = np.array([np.mean(inst[i*fr:(i+1)*fr]**2) for i in range(nfr)])
        ee = np.array([np.mean(est[i*fr:(i+1)*fr]**2) for i in range(nfr)])
        print(f'{mixf}: vocal-estimate share of mix energy in vocal sections {10*np.log10(ee[loud].sum()/me[loud].sum()):.1f} dB; '
              f'mix->instrumental change in vocal sections {10*np.log10(ie[loud].sum()/me[loud].sum()):.1f} dB, in non-vocal {10*np.log10(ie[~loud].sum()/me[~loud].sum()):.1f} dB')
        # residual vocal: correlate instrumental with vocal
        r = np.corrcoef(inst[:,0][v!=0], v[v!=0])[0,1]; r0 = np.corrcoef(mix[:,0][v!=0], v[v!=0])[0,1]
        print(f'   correlation with vocal: mix {r0:.3f} -> instrumental {r:.3f}')
