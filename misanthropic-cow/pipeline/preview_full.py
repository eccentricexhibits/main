"""Clay preview of SDF body + refitted kept assets."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import glb as G, render as R, assets as A
from preview_shapes import build

V09 = Path(sys.argv[2])
m = build(float(sys.argv[3]) if len(sys.argv) > 3 else .007)
src = G.read(V09)
off = len(m.materials)
m.materials += src.materials
m.images = src.images
for p, grp in A.load(src):
    p = dict(p); p['material'] += off
    m.parts.append(p)
r = R.Renderer(m)
clay = '--clay' in sys.argv
views = [(0, 0), (90, 0), (35, 5), (180, 0)]
sheet = Image.new('RGB', (2000, 640))
for i, (a, e) in enumerate(views):
    sheet.paste(r.render(a, e, (500, 640), center=(0, .87, 0), height=1.85, clay=clay), (500 * i, 0))
sheet.save(sys.argv[1], quality=90)
under = Image.new('RGB', (1000, 500))
for i, (a, e) in enumerate([(20, -35), (100, -10)]):
    under.paste(r.render(a, e, (500, 500), center=(0, .85, .08), height=.55, clay=True), (500 * i, 0))
under.save(sys.argv[1].replace('.jpg', '_under.jpg'), quality=90)
head = Image.new('RGB', (1600, 600))
for i, (a, e) in enumerate([(0, 0), (40, 5), (90, 0), (150, 10)]):
    head.paste(r.render(a, e, (400, 600), center=(0, 1.47, .03), height=.5, clay=clay), (400 * i, 0))
head.save(sys.argv[1].replace('.jpg', '_head.jpg'), quality=90)
