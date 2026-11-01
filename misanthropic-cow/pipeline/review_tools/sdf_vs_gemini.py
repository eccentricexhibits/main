"""Project the design SDF parts (torso, hood, cups, arms, legs) and draw their outlines on the Gemini views.
usage: python sdf_vs_gemini.py <pipeline dir> <genviews> <out.jpg> [step]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import design as D
import gemini_measure as GM

def main(pipe, gdir, out, st=.006):
    st = float(st)
    xs = np.arange(-.42, .42, st); ys = np.arange(.0, 1.72, st); zs = np.arange(-.40, .45, st)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    P = np.stack([X, Y, Z], -1)
    parts = {}
    sp = D.suit_parts(P)
    parts['torso'] = sp['torso'] < 0
    parts['hood'] = sp['hood'] < 0
    parts['arms'] = (sp['arm_L'] < 0) | (sp['arm_R'] < 0)
    parts['cups'] = (np.minimum(D.cup_sdf_one(P, 1), D.cup_sdf_one(P, -1)) < 0)
    try:
        lp = D.legging_parts(P); parts['legs'] = lp['full'] < 0
    except Exception as e:
        print('legs', e)
    cols = {'torso': (220, 40, 40), 'hood': (30, 90, 230), 'arms': (20, 160, 60), 'cups': (230, 40, 200), 'legs': (240, 140, 0)}
    tiles = []
    for vn, ax_proj in (('left', 0), ('front', 2)):
        v = GM.load(vn, gdir)
        img = Image.fromarray((255 - (255 - v['a']) * .6).astype(np.uint8)); d = ImageDraw.Draw(img)
        for name, m in parts.items():
            pr = m.any(axis=ax_proj)          # (x or y..) -> 2D
            if vn == 'left':      # pr[y, z]
                hh, yy = np.meshgrid(zs, ys)
                prr = pr
            else:                 # pr[x, y] -> [y, x]
                prr = pr.T; hh, yy = np.meshgrid(xs, ys)
            edge = prr & ~ndimage.binary_erosion(prr)
            yv, hv = yy[edge], hh[edge]
            rows = GM.y_to_row(yv, v['top'], v['crotch'], v['floor'])
            colsx = v['axis'] + hv / (v['sign'] * v['k'])
            for r, c in zip(rows, colsx):
                d.ellipse((c - 2, r - 2, c + 2, r + 2), fill=cols[name])
        # horizontal guides every 10 cm
        for y in np.arange(.7, 1.71, .1):
            r = GM.y_to_row(y, v['top'], v['crotch'], v['floor']); d.line((0, r, 25, r), fill=(0, 0, 0)); d.text((28, r - 6), f'{y:.1f}', fill=(0, 0, 0))
        tiles.append(img)
    H = 1300
    tiles = [t.resize((int(t.width * H / t.height), H)) for t in tiles]
    sheet = Image.new('RGB', (sum(t.width for t in tiles), H), 'white'); x = 0
    for t in tiles:
        sheet.paste(t, (x, 0)); x += t.width
    sheet.save(out, quality=88); print(out)

if __name__ == '__main__':
    main(*sys.argv[1:])
