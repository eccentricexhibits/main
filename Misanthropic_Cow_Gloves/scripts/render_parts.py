"""Gate render for the split: the three parts in colour, closed and with the toes opened.
usage: python3 -I render_parts.py <parts.npz> <out.jpg> [spread_deg=18]
Blender frame: Z up, back of hand = -Y, thumb = +X. Toes rotate about the Y axis through their pivot."""
import os, sys
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw
d = np.load(sys.argv[1]); OUT = sys.argv[2]; SP = float(sys.argv[3]) if len(sys.argv) > 3 else 18
_names = sorted(k[:-2] for k in d.files if k.endswith("_V"))
BODY = next(n for n in _names if "Palm" in n or "Mitten" in n)
_toes = [n for n in _names if n != BODY]
parts = {BODY: (0.86, 0.82, 0.70), next(n for n in _toes if "Index" in n): (0.85, 0.35, 0.30), next(n for n in _toes if "Ring" in n): (0.30, 0.45, 0.85)}
CAP = {"Hoof_InnerWall": (0.25, 0.25, 0.28), "Terry_Inner": (0.95, 0.85, 0.35)}
def rotY(V, p, deg):
    a = np.radians(deg); R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    return (V - p) @ R.T + p
def meshes(spread):
    out = []
    for name, col in parts.items():
        V = d[name + "_V"]; Fc = d[name + "_F"]; M = d[name + "_M"]; mats = list(d[name + "_mats"])
        if name != BODY:
            sgn = 1 if "Index" in name else -1          # thumb-side toe tips move toward +X
            V = rotY(V, d[name + "_O"], sgn * spread)
        fc = np.tile([*col, 1.0], (len(Fc), 1))
        for cname, ccol in CAP.items():
            if cname in mats: fc[M == mats.index(cname)] = [*ccol, 1.0]
        m = trimesh.Trimesh(V, Fc, face_colors=(fc * 255).astype(np.uint8), process=False)
        out.append(pyrender.Mesh.from_trimesh(m, smooth=False))
    return out
def look(eye, tgt, up=(0, 0, 1)):
    f = tgt - eye; f /= np.linalg.norm(f); s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    T = np.eye(4); T[:3, 0], T[:3, 1], T[:3, 2], T[:3, 3] = s, u, -f, eye; return T
r = pyrender.OffscreenRenderer(700, 700)
allV = np.concatenate([d[n + "_V"] for n in parts]); lo, hi = allV.min(0), allV.max(0); c = (lo + hi) / 2
shots = [("closed, back of hand", 0, (0, -1, 0), c, 0.56), ("closed, thumb side", 0, (1, 0, 0), c, 0.56),
         (f"toes spread {SP:.0f} deg", SP, (0, -1, 0), c, 0.56), ("spread, 3/4 from above", SP, (0.5, -0.8, 0.6), c, 0.56),
         ("spread, close-up of the cleft", SP, (0.15, -1, 0.25), np.array([c[0], c[1], lo[2] + 0.72 * (hi[2] - lo[2])]), 0.2),
         ("spread, from the tips", SP, (0.05, -0.25, 1), np.array([c[0], c[1], lo[2] + 0.75 * (hi[2] - lo[2])]), 0.22)]
tiles = []; cache = {}
for name, sp, dv, tgt, mag in shots:
    if sp not in cache: cache[sp] = meshes(sp)
    sc = pyrender.Scene(bg_color=[1, 1, 1, 1], ambient_light=[.35, .35, .35])
    for m in cache[sp]: sc.add(m)
    dv = np.array(dv, float); dv /= np.linalg.norm(dv); up = (0, 1, 0) if abs(dv[2]) > 0.9 else (0, 0, 1)
    sc.add(pyrender.OrthographicCamera(xmag=mag, ymag=mag, znear=.01, zfar=10), pose=look(tgt + dv * 3, tgt, up))
    sc.add(pyrender.DirectionalLight(intensity=3), pose=look(tgt + (dv + np.array([0.6, -0.2, 0.8])) * 3, tgt, up))
    im = Image.fromarray(r.render(sc)[0][..., :3]).resize((450, 450)); ImageDraw.Draw(im).text((6, 6), name, fill=(0, 0, 0)); tiles.append(im)
sheet = Image.new("RGB", (1350, 930), "white"); dr = ImageDraw.Draw(sheet)
for i, t in enumerate(tiles): sheet.paste(t, ((i % 3) * 450, (i // 3) * 450))
dr.text((8, 908), "cream = palm · red = index+middle toe · blue = ring+little toe · dark grey = hoof inner walls · yellow = terry inner faces (web stub, finger inner walls)", fill=(0, 0, 0))
sheet.save(OUT, quality=90)
