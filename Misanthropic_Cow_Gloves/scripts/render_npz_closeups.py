"""Before/after clay close-ups from mesh arrays (Blender frame: Z up, back of hand = -Y, thumb = +X).
usage: python3 -I render_npz_closeups.py <base.npz (V,F)> <out.jpg> <label>=<npz with V> [...]  [w=<npz with w>]"""
import os, sys
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw
base = np.load(sys.argv[1]); F = base["F"]; OUT = sys.argv[2]
sets = [a.split("=", 1) for a in sys.argv[3:]]
r = pyrender.OffscreenRenderer(800, 800)
def look(eye, tgt, up=(0, 0, 1)):
    f = tgt - eye; f /= np.linalg.norm(f); s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    T = np.eye(4); T[:3, 0], T[:3, 1], T[:3, 2], T[:3, 3] = s, u, -f, eye; return T
V0 = base["V"]; lo, hi = V0.min(0), V0.max(0); L = hi[2] - lo[2]; cx, cy = (lo[:2] + hi[:2]) / 2
shots = [("thumb side, lower", (1, 0, 0), 0.32, 0.2), ("little-finger side, lower", (-1, 0, 0), 0.32, 0.2),
         ("cuff edge", (0, -1, 0.35), 0.06, 0.13), ("cuff from below", (0, -0.001, -1), 0.0, 0.28)]
rows = []
for label, path in sets:
    d = np.load(path)
    if label == "w":
        w = d["w"]; col = np.c_[0.75 + 0.25 * w, 0.75 - 0.5 * w, 0.78 - 0.5 * w]; V = V0
    else:
        V = d["V"]; col = np.full((len(V), 3), 0.8)
    m = trimesh.Trimesh(V, F, vertex_colors=(np.c_[col, np.ones(len(col))] * 255).astype(np.uint8), process=False)
    mesh = pyrender.Mesh.from_trimesh(m, smooth=False); row = []
    for name, dv, fz, mag in shots:
        dv = np.array(dv, float); dv /= np.linalg.norm(dv); tgt = np.array([cx, cy, lo[2] + fz * L])
        up = (0, 1, 0) if abs(dv[2]) > 0.9 else (0, 0, 1)
        sc = pyrender.Scene(bg_color=[.12, .12, .12, 1], ambient_light=[.18, .18, .18]); sc.add(mesh)
        sc.add(pyrender.OrthographicCamera(xmag=mag, ymag=mag, znear=.01, zfar=10), pose=look(tgt + dv * 3, tgt, up))
        side = np.cross(dv, up); side /= np.linalg.norm(side)
        sc.add(pyrender.DirectionalLight(intensity=4), pose=look(tgt + (dv + 0.9 * side + 0.5 * np.array(up)) * 3, tgt, up))
        col_, _ = r.render(sc); im = Image.fromarray(col_[..., :3]).resize((400, 400))
        ImageDraw.Draw(im).text((6, 6), f"{label}: {name}", fill=(255, 140, 210)); row.append(im)
    rows.append(row)
sheet = Image.new("RGB", (400 * len(shots), 400 * len(rows)))
for j, row in enumerate(rows):
    for i, im in enumerate(row): sheet.paste(im, (400 * i, 400 * j))
sheet.save(OUT, quality=90)
