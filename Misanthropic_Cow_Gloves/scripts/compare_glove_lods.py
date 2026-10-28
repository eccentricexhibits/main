"""Compare simplified glove meshes against the full-detail one from identical cameras (playbook stage 7).

usage: python3 -I compare_glove_lods.py <out_dir> <full.glb> name=path.glb [name=path.glb ...]
Scores per mesh over 8 views: mean shading difference (0-255, smooth-shaded clay) and silhouette mismatch
(% of the full mesh's silhouette). Writes a close-up sheet: hoof rim + cleft, thumb, terry/cuff.
GLB frame: Y up, back of hand toward +Z, thumb +X.
"""
import os, sys
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
items = [("full", sys.argv[2])] + [tuple(a.split("=", 1)) for a in sys.argv[3:]]
S = 900
dirs = [(0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0), (0.6, 0.4, 0.7), (-0.6, 0.4, -0.7), (0.5, -0.5, 0.7), (0, 1, 0.05)]
def look(eye, tgt):
    f = tgt - eye; f /= np.linalg.norm(f); up = np.array([0, 1.0, 0]) if abs(f[1]) < 0.95 else np.array([0, 0, 1.0])
    s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    M = np.eye(4); M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = s, u, -f, eye; return M
def load(p):
    m = trimesh.load(p, process=False, force="mesh"); m = trimesh.Trimesh(m.vertices, m.faces, process=False)
    m.visual = trimesh.visual.ColorVisuals(m, vertex_colors=[205, 205, 210, 255]); return m
ref = load(items[0][1]); lo, hi = ref.bounds; ctr = (lo + hi) / 2; ext = hi - lo; R = float(np.linalg.norm(ext)) * 1.3
L = ext[1]
closeups = [("hoof rim + cleft", (0, 0.1, 1), np.array([ctr[0], lo[1] + 0.85 * L, ctr[2]]), 0.09),
            ("thumb", (0.4, 0.1, 1), np.array([lo[0] + 0.86 * ext[0], lo[1] + 0.47 * L, ctr[2]]), 0.11),
            ("terry, cuff", (-0.3, 0.2, 1), np.array([ctr[0], lo[1] + 0.18 * L, ctr[2]]), 0.13)]
r = pyrender.OffscreenRenderer(S, S)
def shoot(pm, d, tgt, mag):
    d = np.array(d, float); d /= np.linalg.norm(d)
    sc = pyrender.Scene(bg_color=[0, 0, 0, 1], ambient_light=[0.15, 0.15, 0.15]); sc.add(pm)
    pose = look(tgt + d * R, tgt)
    sc.add(pyrender.OrthographicCamera(xmag=mag, ymag=mag, znear=0.01, zfar=R * 3), pose=pose)
    sc.add(pyrender.DirectionalLight(intensity=3.0), pose=look(tgt + np.array([0.5, 1, 0.8]) * R, tgt))
    sc.add(pyrender.DirectionalLight(intensity=1.0), pose=pose)
    return r.render(sc)[0].astype(np.float32).mean(-1)
renders, crops = {}, {}
for name, path in items:
    m = ref if name == "full" else load(path); pm = pyrender.Mesh.from_trimesh(m, smooth=True)
    renders[name] = [shoot(pm, d, ctr, float(ext.max()) * 0.58) for d in dirs]
    crops[name] = [shoot(pm, d, t, mag) for _, d, t, mag in closeups]
    print(f"rendered {name}: {len(m.faces):,} triangles", flush=True)
for name, _ in items[1:]:
    mad = np.mean([np.abs(a - b)[(a > 8) | (b > 8)].mean() for a, b in zip(renders[name], renders["full"])])
    sil = np.mean([((a > 8) != (b > 8)).sum() / max((b > 8).sum(), 1) for a, b in zip(renders[name], renders["full"])])
    print(f"{name}: mean shading difference {mad:.2f} (0-255), silhouette mismatch {100*sil:.2f}%")
W = 380; sheet = Image.new("L", (W * len(items), W * len(closeups) + 34), 255); d = ImageDraw.Draw(sheet)
for i, (name, _) in enumerate(items):
    d.text((i * W + 8, 10), name, fill=0)
    for j in range(len(closeups)):
        sheet.paste(Image.fromarray(crops[name][j].astype(np.uint8)).resize((W, W)), (i * W, 34 + j * W))
sheet.save(os.path.join(out, "lod_closeups.jpg"), quality=90)
