"""Render a textured OBJ from several angles (textured + clay) with pyrender/EGL."""
import os, sys, time
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw, ImageFont

OBJ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
t = time.time()
mesh = trimesh.load(OBJ, process=False, force="mesh")
print("loaded", mesh.vertices.shape, mesh.faces.shape, round(time.time() - t, 1), "s")
lo, hi = mesh.bounds
print("bounds", lo.round(3), hi.round(3), "extent", (hi - lo).round(3))
print("watertight", mesh.is_watertight, "components?", "skipped")

center = (lo + hi) / 2
ext = hi - lo
R = float(np.linalg.norm(ext)) * 1.25

def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(np.asarray, (eye, target, up))
    f = target - eye; f = f / np.linalg.norm(f)
    s = np.cross(f, up); s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = s, u, -f, eye
    return m

try:
    mat = mesh.visual.material.to_pbr()
    mat.baseColorFactor = [255, 255, 255, 255]
    mat.metallicFactor = 0.0
    mat.metallicRoughnessTexture = None
    mat.roughnessFactor = 0.85
    mesh.visual.material = mat
except Exception as ex:
    print("material patch failed", ex)
tm_tex = pyrender.Mesh.from_trimesh(mesh, smooth=False)
clay = mesh.copy(); clay.visual = trimesh.visual.ColorVisuals(clay, vertex_colors=[200, 200, 205, 255])
tm_clay = pyrender.Mesh.from_trimesh(clay, smooth=False)

views = {k: v for k, v in [a.split("=") for a in sys.argv[3].split(";")]} if len(sys.argv) > 3 else None
# default: axis-aligned views in the mesh's own frame (+Z front, +X right, +Y up)
dirs = {
    "pz": (0, 0, 1), "nz": (0, 0, -1), "px": (1, 0, 0), "nx": (-1, 0, 0),
    "top": (0, 1, 0.001), "bottom": (0, -1, 0.001),
    "q1": (0.7, 0.45, 0.7), "q2": (-0.7, 0.45, -0.7), "q3": (-0.7, 0.35, 0.7), "q4": (0.7, 0.35, -0.7),
}
S = 900
r = pyrender.OffscreenRenderer(S, S)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
for kind, m in (("tex", tm_tex), ("clay", tm_clay)):
    for name, dv in dirs.items():
        scene = pyrender.Scene(bg_color=[1, 1, 1, 1], ambient_light=[0.55, 0.55, 0.55] if kind == "tex" else [0.25, 0.25, 0.25])
        scene.add(m)
        dv = np.array(dv, float); dv /= np.linalg.norm(dv)
        eye = center + dv * R
        up = (0, 0, -1) if name == "top" else ((0, 0, 1) if name == "bottom" else (0, 1, 0))
        pose = look_at(eye, center, up)
        cam = pyrender.OrthographicCamera(xmag=float(ext.max()) * 0.62, ymag=float(ext.max()) * 0.62, znear=0.01, zfar=R * 3)
        scene.add(cam, pose=pose)
        scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=2.2 if kind == "tex" else 3.0), pose=pose)
        key = look_at(center + np.array([0.5, 1.0, 0.6]) * R, center)
        scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=1.2), pose=key)
        col, _ = r.render(scene)
        im = Image.fromarray(col)
        ImageDraw.Draw(im).text((14, 10), f"{name} ({kind})", font=font, fill=(200, 0, 120))
        im.save(f"{OUT}/{kind}_{name}.jpg", quality=88)
print("rendered", round(time.time() - t, 1), "s")
