"""The six close-ups of the round 19 problem areas.  usage: python problems.py <pipe> <glb> <out> [label]"""
import sys
sys.path.insert(0, sys.argv[1])
from PIL import Image, ImageDraw, ImageFont
import glb as G, render as R
r = R.Renderer(G.read(sys.argv[2])); lab = sys.argv[4] + ' · ' if len(sys.argv) > 4 else ''
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
shots = [('head + shoulders, side', 90, 0, (0, 1.38, 0), .55), ('head + shoulders, front', 0, 0, (0, 1.38, 0), .55), ('lower torso, front', 0, 0, (0, .9, 0), .6),
         ('lower torso, side', 90, 0, (0, .9, 0), .6), ('lower legs, side', 90, 0, (0, .22, 0), .45), ('lower legs, front', 0, 0, (0, .22, 0), .45)]
tiles = []
for name, a, e, c, h in shots:
    im = r.render(a, e, (520, 560), center=c, height=h); d = ImageDraw.Draw(im); d.rectangle((0, 0, 520, 30), fill='#161b22'); d.text((8, 4), lab + name, font=f, fill='white'); tiles.append(im)
sheet = Image.new('RGB', (520 * 3, 560 * 2))
for i, t in enumerate(tiles): sheet.paste(t, ((i % 3) * 520, (i // 3) * 560))
sheet.save(sys.argv[3], quality=88)
