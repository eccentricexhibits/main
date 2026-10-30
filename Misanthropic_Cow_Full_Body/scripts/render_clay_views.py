"""Clay renders of one or more meshes from several directions, in one contact sheet.

python3 -I render_clay_views.py <out.jpg> <view_axes> <mesh> [<mesh> ...]
  view_axes: comma list from +x,-x,+y,-y,+z,-z,iso (camera sits on that side looking at the centre),
  e.g. "-y,+x,+z,iso". Up is +Z unless the camera is on +/-z (then +Y).
Meshes are drawn together, each in its own colour (grey, then orange, blue, green). Orthographic, white background.
Every panel has a 10-unit-agnostic scale bar: the label gives the panel width in mesh units.
"""
import os, sys
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw

COLS = [(0.78, 0.78, 0.76), (0.95, 0.55, 0.2), (0.3, 0.55, 0.95), (0.35, 0.8, 0.4), (0.25, 0.25, 0.28), (0.7, 0.45, 0.85), (0.9, 0.2, 0.2)]


def look_at(eye, target, up):
    f = target - eye; f /= np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    m = np.eye(4); m[:3, 0] = r; m[:3, 1] = u; m[:3, 2] = -f; m[:3, 3] = eye
    return m


def render_views(meshes, axes, size=700, alpha_flags=None):
    lo = np.min([m.bounds[0] for m in meshes], 0); hi = np.max([m.bounds[1] for m in meshes], 0)
    c = (lo + hi) / 2; rad = np.linalg.norm(hi - lo) / 2
    scene = pyrender.Scene(bg_color=[1, 1, 1, 1], ambient_light=[0.25] * 3)
    for i, m in enumerate(meshes):
        mat = pyrender.MetallicRoughnessMaterial(baseColorFactor=list(COLS[i % len(COLS)]) + [1], metallicFactor=0, roughnessFactor=0.8)
        scene.add(pyrender.Mesh.from_trimesh(m, material=mat, smooth=False))
    r = pyrender.OffscreenRenderer(size, size)
    out = []
    for a in axes:
        if a == "iso":
            d = np.array([1.0, -1.0, 0.7]); up = np.array([0, 0, 1.0])
        else:
            d = np.zeros(3); d["xyz".index(a[1])] = 1 if a[0] == "+" else -1
            up = np.array([0, 1.0, 0]) if a[1] == "z" else np.array([0, 0, 1.0])
        d = d / np.linalg.norm(d)
        pose = look_at(c + d * rad * 3, c, up)
        cam = pyrender.OrthographicCamera(xmag=rad * 1.05, ymag=rad * 1.05, znear=rad * 0.5, zfar=rad * 6)
        cn = scene.add(cam, pose=pose)
        ln = scene.add(pyrender.DirectionalLight(intensity=3.0), pose=look_at(c + (d + up * 0.6 + np.cross(d, up) * 0.4) * rad * 3, c, up))
        img, _ = r.render(scene, flags=pyrender.RenderFlags.RGBA)
        scene.remove_node(cn); scene.remove_node(ln)
        a_ = img[..., 3:4].astype(np.float32) / 255
        im = Image.fromarray((img[..., :3] * a_ + 255 * (1 - a_)).astype(np.uint8))   # RGBA -> on white
        ImageDraw.Draw(im).text((8, 8), f"{a}  panel width {2 * rad * 1.05:.3g}", fill=(0, 0, 0))
        out.append(im)
    r.delete()
    return out


def sheet(ims, cols=4):
    w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
    s = Image.new("RGB", (w * min(cols, len(ims)), h * rows), "white")
    for i, im in enumerate(ims):
        s.paste(im, ((i % cols) * w, (i // cols) * h))
    return s


if __name__ == "__main__":
    out, axes, files = sys.argv[1], sys.argv[2].split(","), sys.argv[3:]
    meshes = [trimesh.load(f, force="mesh", process=False) for f in files]
    sheet(render_views(meshes, axes)).save(out, quality=90)
    print("wrote", out)
