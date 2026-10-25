"""Bake garment base-colour atlases from 3D-defined markings + tiled source swatches."""
import io
import numpy as np
from PIL import Image
from scipy import ndimage
import noise as N
import render as R

TILE = .11


def load_tile(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float32) / 255


def sample(tile, uv):
    h, w = tile.shape[:2]
    x = (uv[..., 0] % 1) * w - .5
    y = (uv[..., 1] % 1) * h - .5
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
    x0 %= w; y0 %= h; x1 = (x0 + 1) % w; y1 = (y0 + 1) % h
    return (tile[y0, x0] * (1 - fx) * (1 - fy) + tile[y0, x1] * fx * (1 - fy) +
            tile[y1, x0] * (1 - fx) * fy + tile[y1, x1] * fx * fy)


def triplanar(tile, p, n, scale):
    """Sample a tile by 3D position (nap of the swatch runs down -Y on the side planes)."""
    w = np.abs(n) ** 4 + 1e-6
    w /= w.sum(-1, keepdims=True)
    q = p / scale
    cx = sample(tile, np.stack([q[..., 2], -q[..., 1]], -1))
    cy = sample(tile, np.stack([q[..., 0], q[..., 2]], -1))
    cz = sample(tile, np.stack([q[..., 0], -q[..., 1]], -1))
    return cx * w[..., :1] + cy * w[..., 1:2] + cz * w[..., 2:]


def blob_mask(p, blobs, rough=.32, edge=.06, seed=3):
    """Union of noisy ellipsoids. blobs: list of (centre, radii)."""
    m = np.zeros(p.shape[:-1], np.float32)
    nz = N.fbm(p * 22, 4, seed=seed) + .5 * N.fbm(p * 70, 2, seed=seed + 7)
    for c, r in blobs:
        d = np.linalg.norm((p - np.asarray(c)) / np.asarray(r), axis=-1)
        d = d * (1 + rough * nz)
        m = np.maximum(m, np.clip((1 - d) / edge + .5, 0, 1))
    return m


def bake_chart(chart, normals_src, W, H):
    attr = np.hstack([chart['v'], normals_src[chart['src']]])
    out, cover = R.bake(chart['f'], chart['uv'], attr, W, H)
    return out[..., :3], out[..., 3:6], cover


def dilate(img, cover, iters=None):
    idx = ndimage.distance_transform_edt(~cover, return_distances=False, return_indices=True)
    return img[idx[0], idx[1]]


def to_jpeg(img, q=90):
    b = io.BytesIO()
    Image.fromarray(np.uint8(np.clip(img, 0, 1) * 255 + .5)).save(b, 'JPEG', quality=q, optimize=True)
    return b.getvalue()


# ----------------------------------------------------------------- markings (character frame: +X = left)
SHAG_PATCHES = [
    ((-.115, 1.325, .045), (.085, .070, .11)),     # upper chest / shoulder, wearer's right (photos 0120, 0330)
    ((.020, .875, .270), (.125, .105, .13)),       # low belly patch below the udder
    ((-.095, 1.215, -.155), (.115, .125, .10)),    # upper back, wearer's right (12_388)
    ((.120, .935, -.165), (.085, .075, .10)),      # lower back, wearer's left
]


def elbow_patches():
    import design as D
    out = []
    for s, side, r in [(1, 'L', (.060, .075, .060)), (-1, 'R', (.050, .062, .052))]:
        el = D.J[f'Forearm_{side}']
        out.append((el + np.array([s * .045, .015, -.035]), r))
    return out


def all_patches():
    return SHAG_PATCHES + elbow_patches()


# which patches may appear on which suit piece (a patch never spills across the sleeve seam)
TORSO_PATCHES, SLEEVE_PATCHES = [0, 1, 2, 3], {'L': [4], 'R': [5]}


def patches_for(chart_name):
    for side in 'LR':
        if f'sleeve_{side}' in chart_name:
            return SLEEVE_PATCHES[side]
    return TORSO_PATCHES


def shag_mask(p, which=None):
    """Patch mask whose edges break into hanging tufts (noise stretched along gravity)."""
    m = np.zeros(p.shape[:-1], np.float32)
    nz = N.fbm(p * np.array([30, 9, 30]), 4, seed=3) + .6 * N.fbm(p * np.array([90, 22, 90]), 2, seed=10)
    allp = all_patches()
    for c, r in [allp[i] for i in (which if which is not None else range(len(allp)))]:
        q = (p - np.asarray(c)) / np.asarray(r)
        d = np.linalg.norm(q, axis=-1)
        below = np.clip(-q[..., 1], 0, 1)          # tufts hang lower under the patch
        d = d * (1 + .38 * nz) - .18 * below * np.clip(nz + .4, 0, 1)
        m = np.maximum(m, np.clip((1 - d) / .05 + .5, 0, 1))
    return m


def shag_detail(p, black):
    """Long-pile look in the texture: clumped streaks running downward, dark roots, glossy tips."""
    streak = N.fbm(p * np.array([75, 10, 75]), 4, seed=41)
    fine = N.fbm(p * np.array([260, 30, 260]), 2, seed=43)
    clump = N.fbm(p * 18, 3, seed=47)
    shade = .55 + .55 * np.clip(streak * .9 + fine * .35 + .25, 0, 1) - .25 * np.clip(-clump, 0, 1)
    tips = .06 * np.clip(fine + streak - .3, 0, 1)
    return np.clip(black * shade[..., None] + tips[..., None], 0, 1)


def suit_color(p, n, white, black, which=None):
    m = shag_mask(p, which)
    wc = triplanar(white, p, n, TILE)
    bc = shag_detail(p, triplanar(black, p, n, TILE * 1.4))
    # very slight low-frequency warmth/soil variation in the white plush
    var = 1 + .035 * N.fbm(p * 6, 3, seed=11)[..., None]
    wc = np.clip(wc * var * np.array([1.0, .992, .975]), 0, 1)
    return wc * (1 - m[..., None]) + bc * m[..., None], m


def legging_spots(charts_leg, seed=12):
    """Random painted spots, spaced out, placed on the leg charts' surfaces."""
    rng = np.random.default_rng(seed)
    spots = []
    for ch in charts_leg:
        v = ch['v']
        cand = v[(v[:, 1] > .16) & (v[:, 1] < .76)]
        chosen = []
        for i in rng.permutation(len(cand)):
            p = cand[i]
            if all(np.linalg.norm(p - q) > .115 for q in chosen):
                chosen.append(p)
            if len(chosen) >= 11:
                break
        for p in chosen:
            r = rng.uniform(.022, .046)
            spots.append((p, (r * rng.uniform(.8, 1.25), r * rng.uniform(.8, 1.3), r * rng.uniform(.8, 1.25))))
    return spots


def legging_color(p, n, cotton, spots):
    base = triplanar(cotton, p, n, TILE * .6)
    lum = base.mean(-1, keepdims=True)
    black = np.array([.085, .085, .092]) * (.75 + .5 * lum)
    m = blob_mask(p, spots, rough=.45, edge=.10, seed=21)
    brush = .88 + .12 * N.fbm(p * 160, 2, seed=4)[..., None]
    paint = np.array([.94, .94, .92]) * brush
    return black * (1 - m[..., None]) + paint * m[..., None]


def mild_lift(rgb):
    """Gentle brightening of the photographed mask (keeps black paint black)."""
    a = rgb.astype(np.float32) / 255
    l = a.mean(-1, keepdims=True)
    sat = a.max(-1, keepdims=True) - a.min(-1, keepdims=True)
    lift = np.clip((l - .22) / .35, 0, 1) * np.clip(1 - sat * 2.5, 0, 1)   # white paint only, not eyes/muzzle
    out = a + (1 - (1 - a) ** 1.8 - a) * lift
    return out
