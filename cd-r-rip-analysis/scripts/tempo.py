import sys, os, numpy as np
sys.path.insert(0, sys.argv[2]); from onsetalign import load, onset_env, HOP, SR
B = sys.argv[1]; AF = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
def tempo(env):
    e = env - env.mean(); ac = np.correlate(e, e, 'full')[len(e)-1:]
    fps = SR/HOP; lags = np.arange(len(ac))
    bpm = 60*fps/np.maximum(lags,1); m = (bpm >= 60) & (bpm <= 180)
    # comb over multiples to prefer true beat period
    best = max(((ac[l] + 0.5*ac[2*l] if 2*l < len(ac) else ac[l]), l) for l in lags[m])
    return 60*fps/best[1]
def centroid(x):
    n=4096; f=np.fft.rfftfreq(n,1/SR); fr=np.lib.stride_tricks.sliding_window_view(x,n)[::n*4]
    S=np.abs(np.fft.rfft(fr*np.hanning(n),axis=1)); e=S.sum(1); keep=e>np.percentile(e,50)
    return float((S[keep]*f).sum()/S[keep].sum())
for f in sorted(os.listdir(SEL)):
    if f.startswith('._') or f in ('Icon','DrasticMeasures-SelectionsCD'): continue
    x = load(SEL+f, 2); print(f'MIX  {f:24} tempo~{tempo(onset_env(x)):6.1f}')
for f in ['bass-layw','bass-0','vox-1-5','vox-1-2','vox-1-3','vox-1-4','Untitled-7','Untitled-12','Untitled-1','2-13','vox--10','vox-IBelieve-8','vox-JehovasDaughter copy-6','bass-JehovasDaughter copy-1','vox-1-1','vox-1-0']:
    x = load(AF+f, 1); r = 20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
    print(f'TAKE {f:28} tempo~{tempo(onset_env(x)):6.1f}  centroid {centroid(x):6.0f} Hz  rms {r:6.1f} dBFS  dur {len(x)/SR:6.1f}s')
