"""Step 3: decimate, UV-unwrap and bake colour.

Mask texels are projected into the fitted turntable photos (visibility-tested, weighted by how
squarely each photo sees the surface). The character's right side is only seen at grazing angles,
so where direct coverage is thin it is filled from the mirrored left side. Fur gets a procedural
off-white with a fine grain.
"""
import sys, json, numpy as np, trimesh, xatlas, fast_simplification
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation as Rot

parts, photo_dir, cams_path, out_dir = sys.argv[1:5]
TEX = 2048
WEIGHT = {'1': 1.0, '8': 1.0, '19': 1.0, '31': 0.35}  # frame 31's fit is the loosest

# ---------- decimate + smooth ----------
hi = trimesh.load(f'{parts}/body_hi.ply'); lab_hi = np.load(f'{parts}/body_is_mask.npy')
v, f = fast_simplification.simplify(hi.vertices.astype(np.float32), hi.faces.astype(np.int32), target_reduction=0.78)
body = trimesh.Trimesh(v, f, process=True)
trimesh.smoothing.filter_taubin(body, lamb=0.5, nu=-0.53, iterations=8)
is_mask = lab_hi[cKDTree(hi.vertices).query(body.vertices)[1]] > 0.5
print('body faces', len(body.faces))

# ---------- UV unwrap ----------
atlas = xatlas.Atlas(); atlas.add_mesh(body.vertices, body.faces)
po = xatlas.PackOptions(); po.resolution = TEX; po.padding = 4; po.bilinear = True
atlas.generate(pack_options=po)
vmap, F, UV = atlas[0]
V = body.vertices[vmap]; Nv = body.vertex_normals[vmap]; M = is_mask[vmap]
print('atlas', atlas.width, atlas.height, 'verts', len(V))

# ---------- rasterize UV space -> per-texel position / normal / mask flag ----------
def raster_uv(F, UV, attrs, res):
    out = [np.zeros((res, res, a.shape[1]), np.float32) for a in attrs]
    cov = np.zeros((res, res), bool)
    T = UV[F] * res - 0.5
    for t, tri in enumerate(T):
        x0, y0 = np.floor(tri.min(0)).astype(int); x1, y1 = np.ceil(tri.max(0)).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, res - 1), min(y1, res - 1)
        if x1 < x0 or y1 < y0: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        a, b, c = tri; den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-12: continue
        w0 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / den
        w1 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-3) & (w1 >= -1e-3) & (w2 >= -1e-3)
        if not inside.any(): continue
        yy, xx = ys[inside], xs[inside]
        for o, a_ in zip(out, attrs):
            o[yy, xx] = w0[inside, None] * a_[F[t, 0]] + w1[inside, None] * a_[F[t, 1]] + w2[inside, None] * a_[F[t, 2]]
        cov[yy, xx] = True
    return out, cov

(Pt, Nt, Mt), cov = raster_uv(F, UV, [V, Nv, M[:, None].astype(np.float32)], TEX)
Nt /= np.linalg.norm(Nt, axis=-1, keepdims=True) + 1e-9
ys, xs = np.nonzero(cov)
P, N, isM = Pt[ys, xs], Nt[ys, xs], Mt[ys, xs, 0] > 0.5
print('texels', len(P), 'mask texels', isM.sum())

# ---------- photo projection ----------
occluders = [body] + [trimesh.load(f'{parts}/{n}.ply') for n in ('hornbar', 'horn_L', 'horn_R')]
OV = np.vstack([o.vertices for o in occluders])
OF = np.vstack([o.faces + sum(len(x.vertices) for x in occluders[:i]) for i, o in enumerate(occluders)])

def depth_map(R, s, t, shape):
    q = OV @ R.T; uv = np.c_[s * q[:, 0] + t[0], -s * q[:, 1] + t[1]]
    zb = np.full(shape, -np.inf)
    tri = uv[OF]; tz = q[OF, 2]
    for a in np.linspace(0, 1, 5):
        for b in np.linspace(0, 1 - a, int(round((1 - a) * 4)) + 1):
            w = 1 - a - b
            p = np.round(tri[:, 0] * w + tri[:, 1] * a + tri[:, 2] * b).astype(int)
            z = tz[:, 0] * w + tz[:, 1] * a + tz[:, 2] * b
            ok = (p[:, 0] >= 0) & (p[:, 0] < shape[1]) & (p[:, 1] >= 0) & (p[:, 1] < shape[0])
            np.maximum.at(zb, (p[ok, 1], p[ok, 0]), z[ok])
    return ndi.maximum_filter(zb, 3)

def sample(P, N, cams, photos):
    acc = np.zeros((len(P), 3)); wsum = np.zeros(len(P))
    for fr, p in cams.items():
        img, fg, zb = photos[fr]
        R = Rot.from_rotvec(p[:3]).as_matrix(); s = p[3]
        q = P @ R.T; n = N @ R.T
        u = s * q[:, 0] + p[4]; v = -s * q[:, 1] + p[5]
        ui, vi = np.round(u).astype(int), np.round(v).astype(int)
        ok = (ui >= 1) & (ui < img.shape[1] - 1) & (vi >= 1) & (vi < img.shape[0] - 1)
        vis = np.zeros(len(P), bool)
        vis[ok] = (q[ok, 2] >= zb[vi[ok], ui[ok]] - 2.5) & fg[vi[ok], ui[ok]]
        w = np.clip(n[:, 2], 0, 1) ** 8 * vis * WEIGHT[fr]  # steep falloff: the most head-on photo dominates, less ghosting
        c = np.zeros((len(P), 3))
        c[ok] = ndi.map_coordinates(img, [np.repeat(v[ok], 3), np.repeat(u[ok], 3), np.tile([0, 1, 2], ok.sum())], order=1).reshape(-1, 3)
        acc += c * w[:, None]; wsum += w
    return acc, wsum

cams = json.load(open(cams_path))
photos = {}
for fr, p in cams.items():
    img = np.asarray(Image.open(f'{photo_dir}/cow_frame-{fr}.jpg').convert('RGB')).astype(np.float32)
    # backdrop = large near-black regions; close first so dark paint and the black zipper nostrils
    # touching the outline are not mistaken for backdrop
    fg = ndi.binary_closing(ndi.binary_opening(img.max(-1) > 28, iterations=2), iterations=18, border_value=0)
    fg = ndi.binary_erosion(ndi.binary_fill_holes(fg), iterations=4)
    photos[fr] = (img, fg, depth_map(Rot.from_rotvec(p[:3]).as_matrix(), p[3], p[4:6], img.shape[:2]))

Pm, Nm = P[isM], N[isM]
acc, w = sample(Pm, Nm, cams, photos)
mir = np.array([-1, 1, 1.])
acc2, w2 = sample(Pm * mir, Nm * mir, cams, photos)
direct = acc / np.maximum(w, 1e-6)[:, None]; mirrored = acc2 / np.maximum(w2, 1e-6)[:, None]
alpha = np.clip(w / 0.03, 0, 1)[:, None]          # trust direct views once coverage is reasonable
col = np.where((w2 > 1e-4)[:, None], alpha * direct + (1 - alpha) * mirrored, direct)
have = (w > 1e-4) | (w2 > 1e-4)
if (~have).any():  # anything still unseen: copy the nearest seen texel
    col[~have] = col[have][cKDTree(Pm[have]).query(Pm[~have])[1]]
print('mask texels: direct %.2f, mirrored-only %.2f, filled %.3f' % ((w > 1e-4).mean(), ((w <= 1e-4) & (w2 > 1e-4)).mean(), (~have).mean()))

# ---------- procedural fur ----------
def grain(P, scale, seed):
    r = np.random.default_rng(seed); k = r.normal(size=(24, 3)) / scale; ph = r.uniform(0, 2 * np.pi, 24)
    return np.sin(P @ k.T + ph).sum(1) / np.sqrt(12)

def fur(P):
    g = 0.55 * grain(P, 1.2, 1) + 0.3 * grain(P, 4, 2) + 0.15 * grain(P, 15, 3)
    return np.clip(np.array([236, 234, 230.]) * (0.93 + 0.05 * g[:, None]), 0, 255)

tex = np.zeros((TEX, TEX, 3), np.float32)
allc = np.zeros((len(P), 3)); allc[isM] = col; allc[~isM] = fur(P[~isM])
tex[ys, xs] = allc
# pad islands so mip-mapping does not bleed background into seams
filled = cov.copy()
idx = ndi.distance_transform_edt(~filled, return_distances=False, return_indices=True)
tex = tex[idx[0], idx[1]]
# rows were rasterized with v pointing down; image files have v=0 at the bottom
Image.fromarray(np.flipud(np.clip(tex, 0, 255)).astype(np.uint8)).save(f'{out_dir}/head_basecolor.png')
np.savez_compressed(f'{out_dir}/head_uvmesh.npz', V=V, F=F, UV=UV, N=Nv)

# ---------- horn bar (fur, vertex colour) + horns ----------
bar = trimesh.load(f'{parts}/hornbar.ply')
v, f = fast_simplification.simplify(bar.vertices.astype(np.float32), bar.faces.astype(np.int32), target_reduction=0.7)
bar = trimesh.Trimesh(v, f); trimesh.smoothing.filter_taubin(bar, iterations=5)
bar.visual.vertex_colors = np.c_[fur(bar.vertices), np.full(len(bar.vertices), 255)].astype(np.uint8)
bar.export(f'{out_dir}/hornbar_col.ply')
for side in ('L', 'R'):
    h = trimesh.load(f'{parts}/horn_{side}.ply', process=False); u = np.load(f'{parts}/horn_{side}_u.npy')
    c = np.array([233, 196, 38.]) * (0.95 + 0.05 * grain(h.vertices, 6, 5))[:, None]
    c = c * (1 - 0.18 * np.clip((u - 0.8) / 0.2, 0, 1))[:, None]  # tips a little grubby, as in the photos
    for c0 in (0.40, 0.62):
        c[np.abs(u - c0) < 0.022] = [22, 20, 18]
    h.visual.vertex_colors = np.c_[c, np.full(len(c), 255)].astype(np.uint8)
    h.export(f'{out_dir}/horn_{side}_col.ply')
