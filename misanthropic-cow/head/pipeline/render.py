"""Tiny numpy triangle rasterizer for previewing meshes (orthographic, z-buffer, Lambert)."""
import numpy as np
from PIL import Image, ImageDraw

def rot(yaw=0, pitch=0, roll=0):
    """Rotation matrices in degrees: yaw about Z, pitch about X, roll about Y."""
    y, p, r = np.radians([yaw, pitch, roll])
    Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(p), -np.sin(p)], [0, np.sin(p), np.cos(p)]])
    Ry = np.array([[np.cos(r), 0, np.sin(r)], [0, 1, 0], [-np.sin(r), 0, np.cos(r)]])
    return Rx @ Ry @ Rz

def render(V, F, R, size=600, center=None, scale=None, colors=None, light=(0.3, 0.5, 1.0), bg=(30, 30, 30)):
    """View space: x right, y up, z toward viewer. R maps world->view."""
    P = (V - (V.mean(0) if center is None else center)) @ R.T
    if scale is None:
        scale = 0.9 * size / (2 * np.abs(P[:, :2]).max())
    xy = P[:, :2] * scale + size / 2
    xy[:, 1] = size - xy[:, 1]
    z = P[:, 2]
    tri = xy[F]; tz = z[F]
    n = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    L = np.array(light, float); L /= np.linalg.norm(L)
    shade = np.clip(np.abs(n @ L), 0, 1) * 0.8 + 0.2
    if colors is None:
        col = np.ones((len(F), 3)) * 0.85
    else:
        col = colors[F].mean(1) if colors.shape[0] == len(V) else colors
    zbuf = np.full((size, size), -np.inf); img = np.zeros((size, size, 3)); img[:] = np.array(bg) / 255
    # rasterize by sampling barycentric points per triangle (dense meshes -> small tris)
    e1 = tri[:, 1] - tri[:, 0]; e2 = tri[:, 2] - tri[:, 0]
    area = np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]) / 2
    k = int(np.clip(np.ceil(np.sqrt(np.percentile(area, 99))) + 1, 2, 12))
    us, vs = np.meshgrid(np.linspace(0, 1, k + 1), np.linspace(0, 1, k + 1))
    m = (us + vs) <= 1; us, vs = us[m], vs[m]
    big = area > 4 * k * k
    for idx, (u, v) in enumerate(zip(us, vs)):
        w = 1 - u - v
        pts = tri[:, 0] * w[..., None] + tri[:, 1] * u + tri[:, 2] * v
        pz = tz[:, 0] * w + tz[:, 1] * u + tz[:, 2] * v
        px = np.round(pts).astype(int)
        ok = (px[:, 0] >= 0) & (px[:, 0] < size) & (px[:, 1] >= 0) & (px[:, 1] < size)
        lin = px[ok, 1] * size + px[ok, 0]
        zz = pz[ok]
        order = np.argsort(zz)
        lin, zz, fi = lin[order], zz[order], np.nonzero(ok)[0][order]
        zf = zbuf.reshape(-1); imf = img.reshape(-1, 3)
        better = zz > zf[lin]
        lin, zz, fi = lin[better], zz[better], fi[better]
        zf[lin] = zz  # later (larger z) wins due to sort order
        imf[lin] = col[fi] * shade[fi, None]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))

def sheet(images, labels=None, cols=4):
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    S = Image.new('RGB', (w * cols, h * rows), 'black')
    d = ImageDraw.Draw(S)
    for i, im in enumerate(images):
        S.paste(im, ((i % cols) * w, (i // cols) * h))
        if labels:
            d.text(((i % cols) * w + 8, (i // cols) * h + 8), labels[i], fill='yellow')
    return S
