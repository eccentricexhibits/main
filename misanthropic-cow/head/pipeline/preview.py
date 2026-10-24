"""Quick shaded preview of the assembled parts (flat colours)."""
import sys, numpy as np, trimesh
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from render import render, sheet
d, out = sys.argv[1], sys.argv[2]
names = ['body_hi', 'hornbar', 'horn_L', 'horn_R', 'wire_R']
base = [[0.95, 0.95, 0.97], [0.95, 0.95, 0.97], [0.95, 0.8, 0.1], [0.95, 0.8, 0.1], [0.3, 0.3, 0.3]]
V, F, C, o = [], [], [], 0
for n, b in zip(names, base):
    m = trimesh.load(f'{d}/{n}.ply')
    c = np.tile(b, (len(m.vertices), 1))
    if n == 'body_hi':
        lab = np.load(f'{d}/body_is_mask.npy'); c[lab > 0.5] = [0.85, 0.78, 0.7]
    V.append(m.vertices); F.append(m.faces + o); o += len(m.vertices); C.append(c)
V, F, C = np.vstack(V), np.vstack(F), np.vstack(C)
ims = []
for yaw in (0, 35, 90, 150, 180, -90):
    a = np.radians(yaw); R = np.array([[np.cos(a), 0, -np.sin(a)], [0, 1, 0], [np.sin(a), 0, np.cos(a)]])
    ims.append(render(V, F, R, size=500, center=np.array([0, 125, -10]), scale=1.45, colors=C))
sheet(ims, ['front', '35', 'side (char left)', '150', 'back', 'side (char right)'], cols=3).save(out)
