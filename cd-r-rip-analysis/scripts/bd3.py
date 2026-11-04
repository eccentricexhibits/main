import sys, numpy as np
B = sys.argv[1]
rd = lambda p: np.frombuffer(open(p,'rb').read(), '>i2').astype(np.int64)
s = rd(B+'/DrasticMeasures-Selections/Baby Dolls').reshape(-1,2)
L = rd(B+'/DrasticMeasures-NewSong Project/Audio Files/Baby Dolls.L'); R = rd(B+'/DrasticMeasures-NewSong Project/Audio Files/Baby Dolls.R')
diffmask = (s[:,0]!=L)|(s[:,1]!=R)
d = np.nonzero(diffmask)[0]; br = np.where(np.diff(d) > 2000)[0]
starts = np.r_[d[0], d[br+1]]; ends = np.r_[d[br], d[-1]]
print('periods (frames):', np.unique(np.diff(starts)), ' window lens:', np.unique(ends-starts+1))
print('start frames mod 131072:', np.unique(starts % 131072)[:5], ' start byte offsets (stereo):', [hex(x*4) for x in starts[:4]])
a, b = starts[0], ends[0]
print('example window around start', a)
for i in range(a-3, a+4): print('  ', i, 'sel', s[i,0], 'src', L[i])
print('example window around end', b)
for i in range(b-3, b+4): print('  ', i, 'sel', s[i,0], 'src', L[i])
# which one is the artefact: check exact sample repeats (held sample) and second-difference energy at the edges
def edge_energy(x, idx):
    return np.mean([abs(x[i+1]-2*x[i]+x[i-1]) for i in idx])
hold_sel = np.mean([s[i,0]==s[i-1,0] and s[i,1]==s[i-1,1] for i in starts])
hold_src = np.mean([L[i]==L[i-1] and R[i]==R[i-1] for i in starts])
hold_sel_e = np.mean([s[i+1,0]==s[i,0] for i in ends]); hold_src_e = np.mean([L[i+1]==L[i] for i in ends])
print('fraction of windows with duplicated sample at start: sel %.2f src %.2f; at end: sel %.2f src %.2f' % (hold_sel, hold_src, hold_sel_e, hold_src_e))
idx = list(starts)+list(ends)
print('2nd-diff energy at window edges: sel %.0f  src %.0f   (baseline random sel %.0f)' % (edge_energy(s[:,0], idx), edge_energy(L, idx), edge_energy(s[:,0], list(starts+1000))))
