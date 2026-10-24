"""Overlay the projected mask (shaded, semi-transparent) on each photo to check camera fits."""
import sys, json, numpy as np, trimesh
from PIL import Image
from scipy.spatial.transform import Rotation as Rot
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from render import sheet
mask_path, photo_dir, cams, out = sys.argv[1:5]
m = trimesh.load(mask_path); V, N = m.vertices, m.vertex_normals
ims = []
for fr, p in json.load(open(cams)).items():
    img = np.asarray(Image.open(f'{photo_dir}/cow_frame-{fr}.jpg').convert('RGB')).astype(float)
    R = Rot.from_rotvec(p[:3]).as_matrix(); q = V @ R.T; n = N @ R.T
    u = np.round(p[3] * q[:, 0] + p[4]).astype(int); v = np.round(-p[3] * q[:, 1] + p[5]).astype(int)
    ok = (u >= 0) & (u < img.shape[1]) & (v >= 0) & (v < img.shape[0])
    o = np.argsort(q[ok, 2]); u, v, z, nn = u[ok][o], v[ok][o], q[ok, 2][o], n[ok][o]
    shade = np.clip(nn[:, 2], 0, 1)
    lay = np.zeros(img.shape[:2]); lay[v, u] = 0.3 + 0.7 * shade  # nearest wins (sorted by depth)
    a = (lay > 0) * 0.45
    col = np.stack([lay * 0 + 40, lay * 255, lay * 255], -1)
    img = img * (1 - a[..., None]) + col * a[..., None]
    ims.append(Image.fromarray(img.astype(np.uint8)).resize((648, 675)))
sheet(ims, list(json.load(open(cams)).keys()), cols=4).save(out)
