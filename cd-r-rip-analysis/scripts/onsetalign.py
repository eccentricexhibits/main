import sys, numpy as np
B = sys.argv[1]; AF = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
SR = 44100; HOP = 441  # 10 ms frames
def load(p, ch): return np.frombuffer(open(p,'rb').read(), '>i2').astype(np.float32).reshape(-1,ch).mean(1)/32768
def onset_env(x, lo=None, hi=None):
    n = 2048; w = np.hanning(n).astype(np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::HOP]
    S = np.abs(np.fft.rfft(frames*w, axis=1)); f = np.fft.rfftfreq(n, 1/SR)
    m = np.ones_like(f, bool)
    if lo: m &= f >= lo
    if hi: m &= f <= hi
    S = np.log1p(100*S[:, m])
    flux = np.maximum(0, np.diff(S, axis=0)).sum(1)
    flux -= np.convolve(flux, np.ones(50)/50, 'same')   # remove slow trend
    return np.maximum(flux, 0)
def xcorr(a, b, maxlag):
    n = 1 << int(np.ceil(np.log2(len(a)+len(b))))
    c = np.fft.irfft(np.fft.rfft(a-a.mean(), n)*np.conj(np.fft.rfft(b-b.mean(), n)), n)
    lags = np.r_[np.arange(0, n//2), np.arange(-n//2, 0)]
    m = np.abs(lags) <= maxlag; c, lags = c[m], lags[m]
    c /= (np.linalg.norm(a-a.mean())*np.linalg.norm(b-b.mean()) + 1e-9)
    i = np.argmax(c); srt = np.sort(c)[::-1]
    # second-best peak outside +-0.3 s of the best
    far = c[np.abs(lags - lags[i]) > 30]
    return lags[i]*HOP/SR, c[i], c[i]/(far.max()+1e-9)
if __name__ == '__main__':
  tests = [("bass-layw","LayW",(30,300)), ("bass-0","Jehovas'Daughter",(30,300)), ("vox-1-5","Jehovas'Daughter",(150,4000)),
         ("vox-1-2","SweetHeart",(150,4000)), ("vox-1-3","SweetHeart",(150,4000)), ("vox-1-4","SweetHeart",(150,4000)),
         ("Untitled-7","WarIsPeace",(None,None)), ("Untitled-12","WarIsPeace",(150,4000)),
         ("vox-IBelieve-8","I Believe.wav",(150,4000)), ("vox-IBelieve-9","I Believe.wav",(150,4000)), ("vox--10","30'sGermanNightclub",(150,4000)),
         ("vox--11","30'sGermanNightclub",(150,4000)), ("Untitled-1","WarIsPeace",(None,None)), ("2-13","WarIsPeace",(None,None)),
         ("bass-JehovasDaughter copy-1","Jehovas'Daughter",(30,300)), ("vox-JehovasDaughter copy-6","Jehovas'Daughter",(150,4000))]
  cache = {}
  for take, mix, (lo, hi) in tests:
      t = onset_env(load(AF+take,1), lo, hi)
      key = (mix, lo, hi)
      if key not in cache: cache[key] = onset_env(load(SEL+mix,2), lo, hi)
      off, peak, ratio = xcorr(cache[key], t, maxlag=int(120*SR/HOP))
      print(f'{take:28} -> {mix:20} take starts at {off:8.2f}s in mix   corr {peak:.3f}  peak/next {ratio:.2f}')
