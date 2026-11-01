"""Leggings spots, model vs Gemini, per view in the Gemini frame.  green both, red model only, blue Gemini only.
usage: python spot_cmp.py <pipe> <glb> <genviews> <out.jpg>"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pair_sheet as P
import glb as G, render as R
pipe, glb, gdir, out = sys.argv[1:5]
m = G.read(glb); m.parts = [p for p in m.parts if p['name'].startswith('Leggings')]
r = R.Renderer(m)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
tiles = []
for title, fn, angle, top, floor, axis in P.VIEWS:
    g = Image.open(f'{gdir}/{fn}').convert('RGB'); ga = np.asarray(g).astype(float)
    im, fg = P.render_like(r, angle, g.width, g.height, top, floor, axis)
    a = np.asarray(im).astype(float)
    sc = (floor - top) / P.HORN
    rows = np.arange(g.height)[:, None]
    band = (rows > floor - .745 * sc) & (rows < floor - .20 * sc)
    msp = fg & (a.mean(-1) > 120) & band
    L, sat = ga.mean(-1), ga.max(-1) - ga.min(-1)
    dark = (L < 90)
    # Gemini legs region: rows' dark extents
    gl = np.zeros_like(dark)
    for rr in range(int(floor - .745 * sc), int(floor - .20 * sc)):
        xs = np.flatnonzero(dark[rr])
        if len(xs) > 10:
            gl[rr, xs.min():xs.max() + 1] = True
    gsp = gl & (L > 140) & (sat < 70)
    o = np.full(ga.shape, 250.)
    o[gl | (fg & band)] = (200, 200, 200)
    o[msp & gsp] = (40, 170, 60); o[msp & ~gsp] = (230, 60, 50); o[gsp & ~msp] = (60, 100, 230)
    y0, y1 = int(floor - .80 * sc), int(floor - .12 * sc)
    crop = lambda x: x.crop((0, y0, g.width, y1))
    t = [crop(im), crop(g), crop(Image.fromarray(o.astype(np.uint8)))]
    row = Image.new('RGB', (sum(x.width for x in t), t[0].height), 'white'); xo = 0
    for x in t:
        row.paste(x, (xo, 0)); xo += x.width
    ImageDraw.Draw(row).text((10, 10), title, font=font, fill=(200, 0, 0))
    tiles.append(row)
W = max(t.width for t in tiles); H = sum(t.height for t in tiles)
sheet = Image.new('RGB', (W, H), 'white'); yo = 0
for t in tiles:
    sheet.paste(t, (0, yo)); yo += t.height
k = 1800 / W; sheet.resize((1800, int(H * k))).save(out, quality=88); print(out)
