"""Stage 7 check: HIGH vs LOW, same orthographic cameras. Silhouette IoU from 8 directions and clay renders
(whole figure front/side/back, head close-up).

python3 -I compare_lod_cow.py <ply_dir> <out.jpg>
Uses <name>_HIGH.ply / <name>_LOW.ply pairs from bl_decimate_cow.py; slippers are drawn in both.
"""
import os, sys, glob
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw

PLY, OUT = sys.argv[1:3]


def load(kind):
    ms = [trimesh.load(f, process=False) for f in sorted(glob.glob(f"{PLY}/*_{kind}.ply"))]
    ms += [trimesh.load(f, process=False) for f in sorted(glob.glob(f"{PLY}/Slipper_*.ply"))]
    return ms


def look_at(eye, t, up):
    f = t - eye; f /= np.linalg.norm(f); r = np.cross(f, up); r /= np.linalg.norm(r); u = np.cross(r, f)
    m = np.eye(4); m[:3, 0] = r; m[:3, 1] = u; m[:3, 2] = -f; m[:3, 3] = eye; return m


def scene(ms):
    s = pyrender.Scene(bg_color=[1, 1, 1, 0], ambient_light=[0.3] * 3)
    mat = pyrender.MetallicRoughnessMaterial(baseColorFactor=[0.8, 0.8, 0.78, 1], metallicFactor=0, roughnessFactor=0.8)
    for m in ms: s.add(pyrender.Mesh.from_trimesh(m, material=mat, smooth=True))
    return s


def shoot(s, centre, d, half, size):
    d = np.asarray(d, float); d /= np.linalg.norm(d); up = np.array([0, 0, 1.0])
    cn = s.add(pyrender.OrthographicCamera(xmag=half, ymag=half, znear=0.05, zfar=10), pose=look_at(centre + d * 4, centre, up))
    ln = s.add(pyrender.DirectionalLight(intensity=3), pose=look_at(centre + (d + up * 0.6 + np.cross(d, up) * 0.4) * 4, centre, up))
    r = pyrender.OffscreenRenderer(size, size); img, dep = r.render(s, flags=pyrender.RenderFlags.RGBA); r.delete()
    s.remove_node(cn); s.remove_node(ln)
    a = img[..., 3:4] / 255
    return Image.fromarray((img[..., :3] * a + 255 * (1 - a)).astype(np.uint8)), dep > 0


H, L = scene(load("HIGH")), scene(load("LOW"))
c_full = np.array([0, 0, 0.82]); half_full = 0.88
ious = []
for k in range(8):
    a = 2 * np.pi * k / 8; d = [np.sin(a), -np.cos(a), 0]
    _, mh = shoot(H, c_full, d, half_full, 900); _, ml = shoot(L, c_full, d, half_full, 900)
    ious.append((mh & ml).sum() / (mh | ml).sum())
print("silhouette IoU HIGH vs LOW, 8 directions:", np.round(ious, 4).tolist(), "min", round(min(ious), 4))
tiles = []
for title, c, d, half in (("front", c_full, [0, -1, 0], half_full), ("back", c_full, [0, 1, 0], half_full),
                          ("head 3/4", np.array([0, -0.05, 1.45]), [0.6, -1, 0.15], 0.17), ("hand", np.array([0.45, 0, 0.92]), [0.3, -1, 0.1], 0.12)):
    row = []
    for tag, s in (("HIGH", H), ("LOW", L)):
        im, _ = shoot(s, c, d, half, 700); ImageDraw.Draw(im).text((8, 8), f"{tag} {title}", fill=(200, 0, 0)); row.append(im)
    tiles += row
sheet = Image.new("RGB", (700 * 4, 700 * 2), "white")
for i, im in enumerate(tiles): sheet.paste(im, ((i % 4) * 700, (i // 4) * 700))
ImageDraw.Draw(sheet).text((10, 1380), "silhouette IoU (8 views): " + ", ".join(f"{x:.4f}" for x in ious), fill=(0, 0, 0))
sheet.save(OUT, quality=88); print("wrote", OUT)
