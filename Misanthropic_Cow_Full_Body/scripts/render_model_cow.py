"""Stage 4: load the Tripo OBJ, print stats, and render textured + clay views (pyrender/EGL,
orthographic) for a standing character. glTF/OBJ frame: +Y up, front toward +Z, the costume's
own left toward +X (so "left_side" is a camera on +X).

python3 -I render_model_cow.py <model.obj> <out_dir>
"""
import os, sys, time
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw, ImageFont

OBJ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
t = time.time()
mesh = trimesh.load(OBJ, process=False, force="mesh")
lo, hi = mesh.bounds; ext = hi - lo; center = (lo + hi) / 2
print(f"loaded {len(mesh.vertices):,} verts, {len(mesh.faces):,} faces in {time.time() - t:.0f}s")
print("bounds", lo.round(3), hi.round(3), "extent", ext.round(3))

# texture stats
d = os.path.dirname(OBJ)
for name in ("metallic", "roughness"):
    f = [x for x in os.listdir(d) if name in x]
    if f:
        a = np.asarray(Image.open(os.path.join(d, f[0])).convert("L")).astype(float) / 255
        print(f"{name}: mean {a.mean():.3f}  p50 {np.percentile(a, 50):.3f}  p95 {np.percentile(a, 95):.3f}  max {a.max():.3f}")

def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(np.asarray, (eye, target, up))
    f = target - eye; f = f / np.linalg.norm(f)
    s = np.cross(f, up); s = s / np.linalg.norm(s); u = np.cross(s, f)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = s, u, -f, eye
    return m

mat = mesh.visual.material.to_pbr()
mat.baseColorFactor = [255, 255, 255, 255]; mat.metallicFactor = 0.0
mat.metallicRoughnessTexture = None; mat.roughnessFactor = 0.9
mesh.visual.material = mat
m_tex = pyrender.Mesh.from_trimesh(mesh, smooth=False)
clay = mesh.copy(); clay.visual = trimesh.visual.ColorVisuals(clay, vertex_colors=[205, 205, 210, 255])
m_clay = pyrender.Mesh.from_trimesh(clay, smooth=False)
print(f"meshes ready {time.time() - t:.0f}s")

R = float(np.linalg.norm(ext)) * 1.5
dirs = {"front": (0, 0, 1), "back": (0, 0, -1), "left_side": (1, 0, 0), "right_side": (-1, 0, 0),
        "q_front_left": (0.7, 0.2, 0.7), "q_front_right": (-0.7, 0.2, 0.7), "q_back_left": (0.7, 0.2, -0.7),
        "q_back_right": (-0.7, 0.2, -0.7), "top": (0, 1, 0.001)}
W, H = 700, 1000
r = pyrender.OffscreenRenderer(W, H)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
mag = float(ext[1]) * 0.55
for kind, m in (("tex", m_tex), ("clay", m_clay)):
    for name, dv in dirs.items():
        scene = pyrender.Scene(bg_color=[1, 1, 1, 1], ambient_light=[0.5] * 3 if kind == "tex" else [0.22] * 3)
        scene.add(m)
        dv = np.array(dv, float); dv /= np.linalg.norm(dv)
        pose = look_at(center + dv * R, center, (0, 0, -1) if name == "top" else (0, 1, 0))
        scene.add(pyrender.OrthographicCamera(xmag=mag * W / H, ymag=mag, znear=0.01, zfar=R * 3), pose=pose)
        scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=2.0 if kind == "tex" else 3.0), pose=pose)
        scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=1.2), pose=look_at(center + np.array([0.6, 1.0, 0.8]) * R, center))
        col, _ = r.render(scene, flags=pyrender.RenderFlags.RGBA)
        a = col[..., 3:4].astype(float) / 255
        im = Image.fromarray((col[..., :3] * a + 255 * (1 - a)).astype(np.uint8)); ImageDraw.Draw(im).text((10, 8), f"{name} ({kind})", font=font, fill=(200, 0, 120))
        im.save(f"{OUT}/{kind}_{name}.jpg", quality=88)
print(f"rendered {time.time() - t:.0f}s")
