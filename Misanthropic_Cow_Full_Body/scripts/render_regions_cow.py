"""Colour-coded region map on the model, for approval before the tiles go on.

python3 -I render_regions_cow.py <bake_dir> <regions_dir> <swaps.json> <slippers.glb> <out.jpg>

Cow_LOW.obj / Mask_LOW.obj (from bl_bake_cow.py) textured with regions_*_preview.png; the slippers with their own
baked texture at their placement. Panels: front, back, both sides, head front, head 3/4, a hand, the back of the
bloomers, plus a legend.
"""
import os, sys, json
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw, ImageFont

BK, RG, SWAPS, GLB, OUT = sys.argv[1:6]
sw = json.load(open(SWAPS)); reg = json.load(open(f"{RG}/regions.json"))


def textured(obj, png):
    m = trimesh.load(obj, process=False, force="mesh")
    m.visual = trimesh.visual.TextureVisuals(uv=m.visual.uv, image=Image.open(png).convert("RGB"))
    return pyrender.Mesh.from_trimesh(m, smooth=True)


scene = pyrender.Scene(bg_color=[1, 1, 1, 0], ambient_light=[0.55] * 3)
scene.add(textured(f"{BK}/Cow_LOW.obj", f"{RG}/regions_cow_preview.png"))
scene.add(textured(f"{BK}/Mask_LOW.obj", f"{RG}/regions_mask_preview.png"))
gl = trimesh.load(GLB)
g = list(gl.geometry.values())[0]
for side, sg in (("L", 1), ("R", -1)):
    m = g.copy()
    v = np.asarray(m.vertices); v = np.c_[v[:, 0] * sg, -v[:, 2], v[:, 1]] * 0.275 + np.array(sw["slippers"][side]["offset_m"])
    m.vertices = v
    if sg < 0: m.faces = m.faces[:, ::-1]
    scene.add(pyrender.Mesh.from_trimesh(m, smooth=True))


def look_at(eye, t, up):
    f = t - eye; f /= np.linalg.norm(f); r = np.cross(f, up); r /= np.linalg.norm(r); u = np.cross(r, f)
    M = np.eye(4); M[:3, 0] = r; M[:3, 1] = u; M[:3, 2] = -f; M[:3, 3] = eye; return M


def shot(c, d, half, size=700, title=""):
    c = np.asarray(c, float); d = np.asarray(d, float); d /= np.linalg.norm(d); up = np.array([0, 0, 1.0])
    cn = scene.add(pyrender.OrthographicCamera(xmag=half, ymag=half, znear=0.05, zfar=10), pose=look_at(c + d * 4, c, up))
    ln = scene.add(pyrender.DirectionalLight(intensity=1.8), pose=look_at(c + (d + up * 0.7 + np.cross(d, up) * 0.4) * 4, c, up))
    r = pyrender.OffscreenRenderer(size, size); img, _ = r.render(scene, flags=pyrender.RenderFlags.RGBA); r.delete()
    scene.remove_node(cn); scene.remove_node(ln)
    a = img[..., 3:4] / 255; im = Image.fromarray((img[..., :3] * a + 255 * (1 - a)).astype(np.uint8))
    ImageDraw.Draw(im).text((10, 8), title, fill=(0, 0, 0), font=ImageFont.load_default(22)); return im


body_c = [0, 0, 0.83]
panels = [shot(body_c, [0, -1, 0], 0.88, title="front"), shot(body_c, [0, 1, 0], 0.88, title="back"),
          shot(body_c, [1, 0, 0], 0.88, title="own left side"), shot(body_c, [-1, 0, 0], 0.88, title="own right side"),
          shot([0, -0.05, 1.46], [0, -1, 0], 0.17, title="head, front"), shot([0, -0.05, 1.46], [-0.8, -1, 0.15], 0.17, title="head, own right 3/4"),
          shot([0.43, -0.02, 0.9], [0.4, -1, 0.1], 0.12, title="own left hand"), shot([0, 0.12, 0.78], [0.25, 1, 0.05], 0.22, title="bloomers and bow, back")]
leg = Image.new("RGB", (700, 700), "white"); dr = ImageDraw.Draw(leg); f = ImageFont.load_default(21)
dr.text((14, 10), "REGIONS (colour key)", fill=(0, 0, 0), font=ImageFont.load_default(24))
items = sorted(reg["classes"].items(), key=lambda kv: int(kv[0])) + [("99", "slippers: their own textures")]
for i, (k, name) in enumerate(items):
    yy = 48 + i * 27
    rgb = tuple(reg["colours"][k]) if k in reg["colours"] else (230, 230, 230)
    dr.rectangle([14, yy, 44, yy + 20], fill=rgb, outline=(0, 0, 0)); dr.text((54, yy), name, fill=(0, 0, 0), font=f)
panels.append(leg)
cols = 3; W_ = 700
sheet = Image.new("RGB", (W_ * cols, W_ * ((len(panels) + cols - 1) // cols)), "white")
for i, p in enumerate(panels): sheet.paste(p, ((i % cols) * W_, (i // cols) * W_))
sheet.save(OUT, quality=88); print("wrote", OUT)
