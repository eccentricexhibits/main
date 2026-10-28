"""Silhouette check: orthographic renders of the Tripo model vs the normalised input views.
usage: python3 -I compare_to_views.py <model.obj> <tripo_inputs_dir> <out.jpg>
Front = +Z camera, Back = -Z, Left slot (thumb side, object's own left) = +X camera, Right = -X."""
import os, sys
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw
OBJ, INP, OUT = sys.argv[1:4]
m = trimesh.load(OBJ, process=False, force="mesh"); m.visual = trimesh.visual.ColorVisuals(m, vertex_colors=[200, 200, 205, 255])
lo, hi = m.bounds; c = (lo + hi) / 2; L = hi[1] - lo[1]
SIZE, TOP, BOTTOM = 1536, 115, 1421
mag = (SIZE / (BOTTOM - TOP)) * L / 2           # same glove height in the frame as the inputs
r = pyrender.OffscreenRenderer(SIZE, SIZE); mesh = pyrender.Mesh.from_trimesh(m, smooth=False)
def look(eye, tgt, up=(0, 1, 0)):
    f = tgt - eye; f /= np.linalg.norm(f); s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    T = np.eye(4); T[:3, 0], T[:3, 1], T[:3, 2], T[:3, 3] = s, u, -f, eye; return T
views = [("Front.png", (0, 0, 1)), ("Back.png", (0, 0, -1)), ("Left_thumb_side.png", (1, 0, 0)), ("Right_little_finger_side.png", (-1, 0, 0))]
tiles = []
for fn, d in views:
    sc = pyrender.Scene(bg_color=[1, 1, 1, 1], ambient_light=[.3, .3, .3]); sc.add(mesh)
    # centre vertically on the glove's own mid-height, as the inputs are (top 115 / bottom 1421)
    ctr = np.array([c[0], lo[1] + L / 2, c[2]]) if d[0] == 0 else np.array([c[0], lo[1] + L / 2, c[2]])
    pose = look(ctr + np.array(d, float) * 3, ctr)
    sc.add(pyrender.OrthographicCamera(xmag=mag, ymag=mag, znear=.01, zfar=10), pose=pose)
    sc.add(pyrender.DirectionalLight(intensity=3), pose=pose)
    col, depth = r.render(sc)
    sm = depth > 0
    ref = np.asarray(Image.open(os.path.join(INP, fn)).convert("RGB")); rm = (ref < 236).any(2)
    # align horizontally on the hoof axis (as the inputs were), then compare
    def axis(mask):
        ys = np.where(mask.any(1))[0]; top = mask[ys.min(): ys.min() + int(0.3 * (ys.max() - ys.min()))]
        xs = np.where(top.any(0))[0]; return (xs.min() + xs.max()) / 2
    sm = np.roll(sm, int(round(axis(rm) - axis(sm))), axis=1)
    iou = (sm & rm).sum() / (sm | rm).sum()
    ov = np.full((SIZE, SIZE, 3), 255, np.uint8); ov[rm & ~sm] = (230, 60, 60); ov[sm & ~rm] = (60, 110, 230); ov[sm & rm] = (190, 190, 190)
    im = Image.fromarray(ov).resize((512, 512)); ImageDraw.Draw(im).text((8, 8), f"{fn[:-4]}  IoU {iou:.2f}", fill=(0, 0, 0))
    tiles.append(im); print(fn, f"IoU {iou:.3f}")
sheet = Image.new("RGB", (512 * len(tiles), 540), "white"); d = ImageDraw.Draw(sheet)
for i, t in enumerate(tiles): sheet.paste(t, (512 * i, 0))
d.text((8, 518), "grey = both · red = only in the input view · blue = only in the 3D model", fill=(0, 0, 0))
sheet.save(OUT, quality=90)
