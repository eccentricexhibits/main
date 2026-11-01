"""Close-up of a region in a view beside the same region of the Gemini view.
usage: python head_cmp.py <pipe> <glb> <genviews> <out> <view idx> <y0> <y1> <h0> <h1>"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import pair_sheet as P
import glb as G, render as R
from PIL import Image
pipe, glb, gdir, out, vi, y0, y1, h0, h1 = sys.argv[1:10]
vi = int(vi); y0, y1, h0, h1 = map(float, (y0, y1, h0, h1))
r = R.Renderer(G.read(glb))
title, fn, angle, top, floor, axis = P.VIEWS[vi]
g = Image.open(f'{gdir}/{fn}').convert('RGB')
m, _ = P.render_like(r, angle, g.width, g.height, top, floor, axis)
sc = (floor - top) / P.HORN
box = (int(axis + h0 * sc), int(floor - y1 * sc), int(axis + h1 * sc), int(floor - y0 * sc))
a, b = m.crop(box), g.crop(box)
o = Image.new('RGB', (a.width * 2 + 10, a.height), 'white'); o.paste(a, (0, 0)); o.paste(b, (a.width + 10, 0))
k = 900 / o.height
o.resize((int(o.width * k), 900)).save(out)
