import sys, os, numpy as np
sys.path.insert(0, sys.argv[2]); from onsetalign import load, onset_env, xcorr, HOP, SR
B = sys.argv[1]; AF = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
mixes = [f for f in sorted(os.listdir(SEL)) if not f.startswith('._') and f not in ('Icon','DrasticMeasures-SelectionsCD')]
bands = {'full':(None,None), 'low':(30,250), 'mid':(250,4000)}
M = {(m,b): onset_env(load(SEL+m,2), *bands[b]) for m in mixes for b in bands}
for take in ['bass-layw','bass-0','vox-1-5','vox-1-2','vox-1-3','Untitled-12','Untitled-1','2-13','vox--10','vox-IBelieve-8','Untitled-7']:
    x = load(AF+take,1); res=[]
    for b in bands:
        t = onset_env(x, *bands[b])
        for m in mixes:
            off, pk, ratio = xcorr(M[(m,b)], t, maxlag=int(150*SR/HOP)); res.append((ratio, pk, m, b, off))
    res.sort(reverse=True)
    print(f'{take:15}', ' | '.join(f'{m[:14]}/{b} off {off:7.2f}s r={ratio:.2f} c={pk:.2f}' for ratio,pk,m,b,off in res[:3]))
