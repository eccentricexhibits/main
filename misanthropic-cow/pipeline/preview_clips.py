"""Quick choreography preview: a few frames of each clip, no physics or elbow swivel."""
import sys, pickle
import numpy as np
from PIL import Image
import rig as RG, anim as AN, clips as CL, render_dance as RD

m = pickle.load(open(sys.argv[1], 'rb'))
for p in m.parts:
    if 'W' in p:
        p['j'], p['w'] = RG.quantize(p.pop('W'))
gloves = {s: [p for p in m.parts if p.get('group') == f'glove_{s}'] for s in 'LR'}
B = RG.bind_positions(gloves)
names = sys.argv[3].split(',') if len(sys.argv) > 3 else [c.name for c in CL.ALL[1:]]
rows = []
for Cls in CL.ALL:
    if Cls.name not in names:
        continue
    clip = Cls(B)
    ts = np.linspace(0, clip.duration, 6)[:-1]
    row = Image.new('RGB', (5 * 360, 480))
    for i, t in enumerate(ts):
        G = clip.pose(t)
        mats = AN.skin_matrices(G, B)
        row.paste(RD.frame_image(m, mats, -30, 3, (360, 480), center=(0, .92, 0), height=2.0, title=clip.name if i == 0 else None, sub=f't={t:.2f}s'), (360 * i, 0))
    rows.append(row)
sheet = Image.new('RGB', (5 * 360, 480 * len(rows)))
for i, r in enumerate(rows):
    sheet.paste(r, (0, 480 * i))
sheet.save(sys.argv[2], quality=85)
