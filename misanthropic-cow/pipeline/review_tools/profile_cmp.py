"""Per-height silhouette extents, model vs Gemini, in each view (metres, about the leg axis).
usage: python profile_cmp.py <pipeline dir> <glb> <genviews dir> [y0 y1 step]"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import glb as G, render as R
import pair_sheet as P
from gemini_measure import runs

def main(pipe, glb, gdir, y0=.70, y1=1.62, st=.02):
    r = R.Renderer(G.read(glb))
    for title, fn, angle, top, floor, axis in P.VIEWS:
        g = Image.open(f'{gdir}/{fn}').convert('RGB')
        _, mfg = P.render_like(r, angle, g.width, g.height, top, floor, axis)
        gfg = P.gem_fg(g)
        sc = (floor - top) / P.HORN
        print(f'== {title}: y  model[lo,hi]  gemini[lo,hi]  (dlo, dhi)')
        for y in np.arange(float(y0), float(y1) + 1e-6, float(st)):
            row = int(round(floor - y * sc))
            out = []
            for m in (mfg, gfg):
                rr = runs(m[row]);
                if not rr: out.append((np.nan, np.nan)); continue
                # the run containing (or nearest) the axis
                best = min(rr, key=lambda t: 0 if t[0] <= axis <= t[1] else min(abs(t[0]-axis), abs(t[1]-axis)))
                out.append(((best[0] - axis) / sc, (best[1] - axis) / sc))
            (a, b), (c, d) = out
            print(f'{y:.2f}  [{a:+.3f},{b:+.3f}]  [{c:+.3f},{d:+.3f}]  ({a-c:+.3f},{b-d:+.3f})')

if __name__ == '__main__':
    main(*sys.argv[1:4], *map(float, sys.argv[4:]))
