"""Compare the Tripo model's orthographic silhouettes with the four normalised input views.
A camera on +X sees the costume's own left side (it faces the image's left). Both are scaled so the figure is the same height (horn tips to soles) and centred on its bbox.

python3 -I compare_silhouettes_cow.py <model.obj> <tripo_inputs_dir> <out_dir>
"""
import os, sys
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender, cv2
from PIL import Image

OBJ, INP, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
mesh = trimesh.load(OBJ, process=False, force="mesh")
mesh.visual = trimesh.visual.ColorVisuals(mesh, vertex_colors=[200, 200, 200, 255])
lo, hi = mesh.bounds; c = (lo + hi) / 2; R = float(np.linalg.norm(hi - lo)) * 2
pm = pyrender.Mesh.from_trimesh(mesh, smooth=False)

def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(np.asarray, (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f); s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = s, u, -f, eye; return m

N = 1536
r = pyrender.OffscreenRenderer(N, N)
def sil(d):
    sc = pyrender.Scene(); sc.add(pm)
    sc.add(pyrender.OrthographicCamera(xmag=(hi - lo)[1] * 0.6, ymag=(hi - lo)[1] * 0.6, znear=0.01, zfar=R * 2), pose=look_at(c + np.array(d) * R, c))
    depth = r.render(sc, flags=pyrender.RenderFlags.DEPTH_ONLY)
    return depth > 0

def norm(mask):                                   # crop to bbox, scale to height 1380, centre
    ys, xs = np.where(mask); cr = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8) * 255
    s = 1380 / cr.shape[0]; cr = cv2.resize(cr, (max(1, round(cr.shape[1] * s)), 1380)) > 127
    can = np.zeros((N, N), bool); ox = (N - cr.shape[1]) // 2; can[88:88 + 1380, ox:ox + cr.shape[1]] = cr; return can

def img_mask(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)
    return (a < 245).any(2)

views = [("Front.png", (0, 0, 1)), ("Back.png", (0, 0, -1)), ("Left_facing_left.png", (1, 0, 0)), ("Right_facing_right.png", (-1, 0, 0))]
rows = []
for fn, d in views:
    m = norm(sil(d)); t = norm(img_mask(os.path.join(INP, fn)))
    iou = (m & t).sum() / (m | t).sum()
    vis = np.full((N, N, 3), 255, np.uint8); vis[t & ~m] = (230, 60, 60); vis[m & ~t] = (60, 90, 230); vis[m & t] = (170, 170, 170)
    Image.fromarray(vis).resize((512, 512)).save(os.path.join(OUT, "sil_" + fn.replace(".png", ".jpg")))
    # widths at height fractions (0 = soles, 1 = horn tips)
    prof = []
    for f in (0.3, 0.45, 0.55, 0.62, 0.7, 0.78):
        y = int(88 + 1380 * (1 - f)); a_, b_ = np.where(m[y])[0], np.where(t[y])[0]
        prof.append(f"{f:.2f}: model {a_.max() - a_.min() if len(a_) else 0:4d} / view {b_.max() - b_.min() if len(b_) else 0:4d}")
    rows.append((fn, iou, prof))
for fn, iou, prof in rows:
    print(f"{fn:24s} silhouette IoU {iou:.3f}"); print("   " + " | ".join(prof))
