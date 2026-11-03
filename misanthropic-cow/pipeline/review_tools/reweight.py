"""Round 43: fast weight experiments.

usage (from pipeline/): python review_tools/reweight.py <src dir> <dst dir> [quick]  -- recompute the suit's skin weights (torso, hood, sleeves; shag roots
near the shoulders from the nearest suit vertex) with the current rig.py
(and its COW_* settings) into a copy of src's model.pkl (a rig_bench assemble directory; --quick if quick), so a few
clips can be baked and rendered with rig_bench in seconds instead of a full assemble.  The strands' tip springs near
the shoulders are not rebuilt, so use it for looking at the suit, then assemble properly."""
import sys, os, pickle, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from pathlib import Path
import numpy as np, garments as Gm, rig as RG
src, dst = Path(sys.argv[1]), Path(sys.argv[2]); dst.mkdir(parents=True, exist_ok=True)
quick = len(sys.argv) > 3
cache = src / ('suit_quick.pkl' if quick else 'suit_full.pkl')    # the suit mesh, built once (it does not depend on the weights)
t0 = time.time()
if cache.exists():
    suit = pickle.load(open(cache, 'rb'))
else:
    suit = Gm.build_suit(step=.006 if quick else .0042, target=60000 if quick else 170000)
    pickle.dump(suit, open(cache, 'wb'), protocol=4)
print('suit', f'{time.time() - t0:.0f}s', flush=True)
W = RG.suit_weights(suit['v'], suit['f'], suit['labels'])
M = pickle.load(open(src / 'model.pkl', 'rb'))
byname = {p['name']: p for p in M['model'].parts}
n = 0
for ch in suit['charts']:
    p = byname.get(ch['name'])
    if p is None or len(p['v']) != len(ch['src']):
        print('skip', ch['name']); continue
    assert np.abs(p['v'] - ch['v']).max() < 1e-4
    p['j'], p['w'] = RG.quantize(W[ch['src']]); n += 1
# the shag strands: nearest torso vertex's new weights at the root, blended to the old tip weights by the old ratio
from scipy.spatial import cKDTree
tree = cKDTree(suit['v'])
for p in M['model'].parts:
    if not p['name'].startswith('Suit_black_shag'):
        continue
    # strands keep their own tip bones; only the arm/shoulder bones near the shoulders are re-taken from the nearest suit vertex
    near = np.linalg.norm(p['v'] - np.array([[.19, 1.275, -.03]]), axis=1) < .2
    near |= np.linalg.norm(p['v'] - np.array([[-.19, 1.275, -.03]]), axis=1) < .2
    if near.any():
        _, idx = tree.query(p['v'][near])
        jj, ww = RG.quantize(W[idx])
        p['j'][near], p['w'][near] = jj, ww
pickle.dump(M, open(dst / 'model.pkl', 'wb'), protocol=4)
print('reweighted', n, 'charts', f'{time.time() - t0:.0f}s')
