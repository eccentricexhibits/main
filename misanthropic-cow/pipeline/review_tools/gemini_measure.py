"""Measure the approved generated views in model coordinates: floor -> 0, crotch -> 0.747 m, horn tip -> 1.696 m
(vertical, piecewise linear), horizontal at the torso's scale about the leg axis.  Prints torso outlines, the
hem and the cups and briefs extents, and saves the outlines for fitting.
usage: python gemini_measure.py <genviews dir> <out.npz>"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

CROTCH, HORN = .747, 1.696
VIEWS = {  # name: (file, top row, crotch row, floor row, leg-axis column, model horizontal axis, sign)
    'front': ('1_FRONT_approved.png', 83, 748, 1233, 421, 0, 1),
    'back': ('2_BACK_approved.png', 72, 870, 1458, 507, 0, -1),
    'left': ('3_SIDE_facing_left_approved.png', 54, 727, 1220, 477, 2, -1),
    'right': ('Gemini_Generated_Image_f4u2n8f4u2n8f4u2.jpg', 58, 729, 1221, 401, 2, 1),
}


def row_to_y(r, top, crotch, floor):
    return np.interp(-np.asarray(r, float), [-floor, -crotch, -top], [0, CROTCH, HORN])


def y_to_row(y, top, crotch, floor):
    return np.interp(y, [0, CROTCH, HORN], [floor, crotch, top])


def load(name, gdir):
    f, top, crotch, floor, axis, hax, sign = VIEWS[name]
    a = np.asarray(Image.open(f'{gdir}/{f}').convert('RGB')).astype(float)
    k = (HORN - CROTCH) / (crotch - top)                 # metres per pixel (torso scale)
    L, sat = a.mean(-1), a.max(-1) - a.min(-1)
    fg = ~((L > 246) & (sat < 10))
    fg = ndimage.binary_opening(ndimage.binary_fill_holes(ndimage.binary_closing(fg, iterations=2)), iterations=2)
    return dict(a=a, fg=fg, L=L, sat=sat, top=top, crotch=crotch, floor=floor, axis=axis, k=k, hax=hax, sign=sign)


def col_to_h(c, v):
    return v['sign'] * (np.asarray(c, float) - v['axis']) * v['k']


def runs(mask_row):
    xs = np.flatnonzero(mask_row)
    if len(xs) == 0:
        return []
    parts = np.split(xs, np.flatnonzero(np.diff(xs) > 2) + 1)
    return [(p.min(), p.max()) for p in parts if len(p) > 3]


def main(gdir, out):
    V = {n: load(n, gdir) for n in VIEWS}
    ys = np.round(np.arange(.70, 1.42, .01), 3)
    res = {'y': ys}
    for n in ('left', 'right'):
        v = V[n]; fr, bk = [], []
        for y in ys:
            r = int(round(y_to_row(y, v['top'], v['crotch'], v['floor'])))
            rr = runs(v['fg'][r])
            # the body's run is the widest one; its ends are the front and back of the figure at this height
            a_, b_ = max(rr, key=lambda t: t[1] - t[0]) if rr else (np.nan, np.nan)
            h1, h2 = col_to_h(a_, v), col_to_h(b_, v)
            fr.append(max(h1, h2)); bk.append(min(h1, h2))
        res[n + '_front'], res[n + '_back'] = np.array(fr), np.array(bk)
    for n in ('front', 'back'):
        v = V[n]; lo, hi = [], []
        for y in ys:
            r = int(round(y_to_row(y, v['top'], v['crotch'], v['floor'])))
            rr = runs(v['fg'][r])
            cand = [t for t in rr if t[0] - 3 <= v['axis'] + 0 <= t[1] + 3] or rr
            a_, b_ = cand[0] if cand else (np.nan, np.nan)
            h1, h2 = col_to_h(a_, v), col_to_h(b_, v)
            lo.append(min(h1, h2)); hi.append(max(h1, h2))
        res[n + '_xmin'], res[n + '_xmax'] = np.array(lo), np.array(hi)
    # cups (pink, saturated) and briefs (pale pink, low saturation) extents in each view
    for n, v in V.items():
        a = v['a']; r, g, b = a[..., 0], a[..., 1], a[..., 2]
        cup = (r - g > 35) & (r > 170) & (r - b > 15)
        rows, cols = np.nonzero(cup)
        keep = row_to_y(rows, v['top'], v['crotch'], v['floor']) > 1.0
        rows, cols = rows[keep], cols[keep]
        if len(rows):
            yv = row_to_y(rows, v['top'], v['crotch'], v['floor']); hv = col_to_h(cols, v)
            print(f'{n:5s} cups: y {np.percentile(yv, 2):.3f}-{np.percentile(yv, 98):.3f}  horizontal {np.percentile(hv, 2):+.3f}..{np.percentile(hv, 98):+.3f}')
            res[n + '_cups'] = np.array([np.percentile(yv, 2), np.percentile(yv, 98), np.percentile(hv, 2), np.percentile(hv, 98)])
    for k_, v_ in res.items():
        if k_ != 'y' and v_.ndim == 1 and len(v_) == len(ys):
            print(f'{k_:12s}', ' '.join(f'{ys[i]:.2f}:{v_[i]:+.3f}' for i in range(0, len(ys), 6)))
    np.savez(out, **res)


if __name__ == '__main__':
    main(*sys.argv[1:3])
