import sys, numpy as np
sys.path.insert(0, sys.argv[2]); from onsetalign import load, onset_env, xcorr, HOP, SR
B = sys.argv[1]; AF = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
def corr_at(a, b, lag_s):
    k = int(round(lag_s*SR/HOP))   # b starts at time lag in a
    if k >= 0: aa, bb = a[k:], b
    else: aa, bb = a, b[-k:]
    n = min(len(aa), len(bb)); aa, bb = aa[:n]-aa[:n].mean(), bb[:n]-bb[:n].mean()
    return float(aa@bb/np.sqrt((aa@aa)*(bb@bb)+1e-12))
def pitch_env(x):   # crude voiced-energy envelope in vocal band, 10ms
    return onset_env(x, 200, 1200)
v8, v9 = load(AF+'vox-IBelieve-8',1), load(AF+'vox-IBelieve-9',1)
e8, e9 = onset_env(v8,150,4000), onset_env(v9,150,4000)
print('vox8 vs vox9: free search', xcorr(e9, e8, int(60*SR/HOP)))
print('  at time-stamp lag (-0.382s):', round(corr_at(e9, e8, -0.382),3), ' at onset-mix lag (-3.84s):', round(corr_at(e9, e8, -3.84),3))
mix = onset_env(load(SEL+"I Believe.wav",2),150,4000)
print('vox8 vs mix at -1.731:', round(corr_at(mix, e8, -1.731),3), ' at -5.18:', round(corr_at(mix, e8, -5.18),3))
v10, v11 = load(AF+'vox--10',1), load(AF+'vox--11',1)
e10, e11 = onset_env(v10,150,4000), onset_env(v11,150,4000)
m30 = onset_env(load(SEL+"30'sGermanNightclub",2),150,4000)
print('vox10 vs vox11 free:', xcorr(e11, e10, int(200*SR/HOP)))
print('  at stamp lag 24.54s:', round(corr_at(e11, e10, 24.54),3), ' at 3.26s:', round(corr_at(e11, e10, 3.26),3))
print('vox10 vs mix at 21.88:', round(corr_at(m30, e10, 21.88),3), ' at 0.60:', round(corr_at(m30, e10, 0.60),3))
# local null distribution: correlation at random lags
rng = np.random.default_rng(0); null = [corr_at(m30, e10, l) for l in rng.uniform(0, 150, 200)]
print('  null (random lags) mean %.3f sd %.3f max %.3f' % (np.mean(null), np.std(null), np.max(null)))
null8 = [corr_at(mix, e8, l) for l in rng.uniform(-60, 80, 200)]
print('vox8 null mean %.3f sd %.3f max %.3f' % (np.mean(null8), np.std(null8), np.max(null8)))
