"""Bake garment base-colour atlases from 3D-defined markings + tiled source swatches."""
import io
import numpy as np
from PIL import Image
from scipy import ndimage
from design import LEG_LIFT
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


def _local(p, blob):
    """Coordinates of p in a blob's ellipsoid: (centre, radii) is axis-aligned; (centre, radii, axes) is
    turned so its rows are the ellipse's axes (round 19's patches and spots follow the surface)."""
    c, r = np.asarray(blob[0]), np.asarray(blob[1])
    if len(blob) > 2:
        return ((p - c) @ np.asarray(blob[2]).T) / r
    return (p - c) / r


def blob_mask(p, blobs, rough=.32, edge=.06, seed=3):
    """Union of noisy ellipsoids. blobs: list of (centre, radii) or (centre, radii, axes)."""
    m = np.zeros(p.shape[:-1], np.float32)
    nz = N.fbm(p * 22, 4, seed=seed) + .5 * N.fbm(p * 70, 2, seed=seed + 7)
    for blob in blobs:
        d = np.linalg.norm(_local(p, blob), axis=-1)
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
    # belly patch below the udder: round 18 centres it on the belly as in the original shoot (0077, "5 of 15"),
    # its top under the teats; at .875 it sat on the hem, and over the briefs once the hem rose
    ((.020, .960, .275), (.125, .105, .13)),
    ((-.095, 1.215, -.155), (.115, .125, .10)),    # upper back, wearer's right (12_388)
    ((.120, .935 + LEG_LIFT, -.165), (.085, .075, .10)),      # lower back, wearer's left
]


def elbow_patches():
    import design as D
    out = []
    for s, side, r in [(1, 'L', (.060, .075, .060)), (-1, 'R', (.050, .062, .052))]:
        el = D.J[f'Forearm_{side}']
        out.append((el + np.array([s * .045, .015, -.035]), r))
    return out


def all_patches():
    if _TRIPO:
        return [(c, r, U) for c, r, U, piece, bone in _TRIPO]
    return SHAG_PATCHES + elbow_patches()


# which patches may appear on which suit piece (a patch never spills across the sleeve seam), and which
# spring bone each patch's strands swing with (rig.SHAG order)
TORSO_PATCHES, SLEEVE_PATCHES = [0, 1, 2, 3], {'L': [4], 'R': [5]}
PATCH_BONE = [0, 1, 2, 3, 4, 5]
_TRIPO = []
import design as _D
if _D.BODY_SOURCE == 'tripo':
    # round 19: the patch layout of the approved generated views, as the Tripo model carries it (markings.py)
    import markings as _MK
    import tripo_body as _TB
    _TRIPO = _MK.shag_patches(_TB.MARKINGS['patches'], _TB.torso_y, _D.HEAD_DZ)
    TORSO_PATCHES = [i for i, t in enumerate(_TRIPO) if t[3] == 'torso']
    SLEEVE_PATCHES = {s: [i for i, t in enumerate(_TRIPO) if t[3] == 'sleeve_' + s] for s in 'LR'}
    PATCH_BONE = [t[4] for t in _TRIPO]


# Round 19: the markings are painted straight from the approved views (approved_views.py), so the shag and
# the leggings' spots have the drawing's own shapes; set_occluders() must run first (assemble.build does).
PROJECTED = _D.BODY_SOURCE == 'tripo'
_OCC, _LEG_EXTENT = None, {}


def set_occluders(points, leg_v):
    """Depth maps of the whole figure per view, and the model legs' extents by height (for matching the
    drawing's legs row by row)."""
    global _OCC
    import approved_views as AV
    _OCC = AV.Occluders(points)
    ys = np.arange(.02, .82, .01)
    for name, (f, top, crotch, floor, axis, hax, sign, cam) in AV.VIEWS.items():
        for side in (1, -1):
            v = leg_v[(leg_v[:, 0] * side) > .0]
            lo, hi = np.full(len(ys), np.nan), np.full(len(ys), np.nan)
            for i, y in enumerate(ys):
                q = v[np.abs(v[:, 1] - y) < .006, hax]
                if len(q) > 3:
                    lo[i], hi[i] = q.min(), q.max()
            ok = np.isfinite(lo)
            if ok.sum() > 2:
                _LEG_EXTENT[(name, side)] = (ys[ok], lo[ok], hi[ok])


BLOBS = False             # set by fit_projected_patches: the shag is drawn as round 18's tufted blobs
MIN_PATCH_AREA = 6e-4     # m^2: smaller specks of the projection are dropped
MIN_SPOT_AREA = 1.5e-4
SPLIT_FILL = .70          # a component filling less of its ellipse than this is split in two


def _fit_blobs(pts, area, nrm, depth=0):
    """Ellipsoids (centre, radii, axes) covering one connected patch on the surface: an ellipse in the patch's
    tangent plane from its area-weighted spread, split in two (k-means) while it is a poor fit."""
    wgt = area / area.sum()
    c = wgt @ pts
    nz = wgt @ nrm; nz /= max(np.linalg.norm(nz), 1e-9)
    t1 = np.cross(nz, [0, 1, 0]); t1 = t1 / np.linalg.norm(t1) if np.linalg.norm(t1) > 1e-6 else np.array([1., 0, 0])
    t2 = np.cross(nz, t1)
    q = np.stack([(pts - c) @ t1, (pts - c) @ t2], 1)
    cov = (q * wgt[:, None]).T @ q
    ev, evec = np.linalg.eigh(cov)
    r = 2 * np.sqrt(np.maximum(ev, 1e-8)) * 1.08
    fill = area.sum() / (np.pi * r[0] * r[1])
    if fill < SPLIT_FILL and depth < 3 and len(pts) > 40 and area.sum() > 2 * MIN_PATCH_AREA:
        # split along the long axis, then refine with a few k-means steps
        lab = (q @ evec[:, 1]) > 0
        for _ in range(8):
            cs = [q[lab == k].mean(0) for k in (0, 1)]
            lab = np.linalg.norm(q - cs[1], axis=1) < np.linalg.norm(q - cs[0], axis=1)
        if 0 < lab.sum() < len(lab):
            return sum((_fit_blobs(pts[lab == k], area[lab == k], nrm[lab == k], depth + 1) for k in (False, True)), [])
    a1, a2 = evec[0, 0] * t1 + evec[1, 0] * t2, evec[0, 1] * t1 + evec[1, 1] * t2
    sag = np.abs((pts - c) @ nz).max()
    radii = np.array([r[0], r[1], max(.035, 1.5 * sag + .02)])
    return [(c, radii, np.stack([a1, a2, nz]))]


def _mask_blobs(cen, area, nrm, m, vox, min_area):
    """Ellipsoid blobs for the connected regions of faces (centres cen) where the projected mask m > 0.5."""
    from scipy import ndimage
    on = np.flatnonzero(m > .5)
    if not len(on):
        return []
    ijk = np.floor((cen[on] - cen[on].min(0)) / vox).astype(int)
    grid = np.zeros(ijk.max(0) + 1, bool); grid[tuple(ijk.T)] = True
    lab, nlab = ndimage.label(grid, np.ones((3, 3, 3)))
    fl = lab[tuple(ijk.T)]
    out = []
    for i in range(1, nlab + 1):
        f = on[fl == i]
        if area[f].sum() >= min_area:
            out += _fit_blobs(cen[f], area[f], nrm[f])
    return out


def fit_projected_patches(sv, sf, labels, quick=False):
    """Round 19b: the approved views' patches, projected onto the suit, become round 18's kind of patch: a few
    tufted ellipses per patch, drawn by shag_mask and grown with strands, instead of the projection's own
    ragged per-texel edges (which made the shag look patchy and glitchy)."""
    global _TRIPO, TORSO_PATCHES, SLEEVE_PATCHES, PATCH_BONE, BLOBS
    from scipy import ndimage
    cen = sv[sf].mean(1)
    fn = np.cross(sv[sf[:, 1]] - sv[sf[:, 0]], sv[sf[:, 2]] - sv[sf[:, 0]])
    area = .5 * np.linalg.norm(fn, axis=1)
    fn = fn / np.maximum(2 * area[:, None], 1e-12)
    piece = np.where(labels == 2, 1, np.where(labels == 3, 2, np.where(labels == 0, 0, 3)))
    sel = piece < 3
    m = np.zeros(len(sf)); m[sel] = patch_mask(cen[sel], fn[sel])
    blobs = []
    for k, name in [(0, 'torso'), (1, 'sleeve_L'), (2, 'sleeve_R')]:
        sel = piece == k
        for c, r, U in _mask_blobs(cen[sel], area[sel], fn[sel], m[sel], .012, MIN_PATCH_AREA):
            bone = int(bone_of(c[None], np.array([k]))[0])
            blobs.append((c, r, U, name, bone))
    _TRIPO = blobs
    TORSO_PATCHES = [i for i, t in enumerate(blobs) if t[3] == 'torso']
    SLEEVE_PATCHES = {s: [i for i, t in enumerate(blobs) if t[3] == 'sleeve_' + s] for s in 'LR'}
    PATCH_BONE = [t[4] for t in blobs]
    BLOBS = True
    return blobs


def patch_mask(p, n):
    import approved_views as AV
    shp = p.shape[:-1]
    m = AV.project_patches(p.reshape(-1, 3), n.reshape(-1, 3), _OCC)
    return m.reshape(shp).astype(np.float32)


def bone_of(p, piece):
    """Shag spring bone for strand roots p on suit piece (0 torso, 1 sleeve L, 2 sleeve R), by region."""
    front, high = p[:, 2] > 0, p[:, 1] > 1.15
    b = np.where(front, np.where(high, 0, 1), np.where(high, 2, 3))
    return np.where(piece == 1, 4, np.where(piece == 2, 5, b))


def bone_centres():
    if PROJECTED:
        import design as D
        return [np.array([-.05, 1.30, .14]), np.array([0., .97, .28]), np.array([.03, 1.26, -.16]),
                np.array([0., 1.0, -.16]), D.J['Forearm_L'] + [0, .08, 0], D.J['Forearm_R'] + [0, .08, 0]]
    return _bone_centres_patches()


def _bone_centres_patches():
    """Where each shag spring bone sits: the middle of the patches that swing with it."""
    allp = all_patches()
    out = []
    for b in range(6):
        cs = [np.asarray(allp[i][0]) for i in range(len(allp)) if PATCH_BONE[i] == b]
        out.append(np.mean(cs, 0) if cs else np.asarray(SHAG_PATCHES[min(b, 3)][0]))
    return out


def patches_for(chart_name):
    if 'Hood' in chart_name or 'tube' in chart_name:
        return []
    for side in 'LR':
        if f'sleeve_{side}' in chart_name:
            return SLEEVE_PATCHES[side]
    return TORSO_PATCHES


def shag_mask(p, which=None):
    """Patch mask whose edges break into hanging tufts (noise stretched along gravity)."""
    m = np.zeros(p.shape[:-1], np.float32)
    nz = N.fbm(p * np.array([30, 9, 30]), 4, seed=3) + .6 * N.fbm(p * np.array([90, 22, 90]), 2, seed=10)
    allp = all_patches()
    for blob in [allp[i] for i in (which if which is not None else range(len(allp)))]:
        q = _local(p, blob)
        d = np.linalg.norm(q, axis=-1)
        below = np.clip(-(p[..., 1] - blob[0][1]) / np.asarray(blob[1])[:2].mean(), 0, 1)   # tufts hang lower under the patch
        d = d * (1 + (.28 if _TRIPO else .38) * nz) - .18 * below * np.clip(nz + .4, 0, 1)
        m = np.maximum(m, np.clip((1 - d) / .05 + .5, 0, 1))
    return m


def shag_detail(p, black):
    """Long-pile look in the texture: clumped streaks running downward, dark roots, glossy tips."""
    streak = N.fbm(p * np.array([75, 10, 75]), 4, seed=41)
    fine = N.fbm(p * np.array([260, 30, 260]), 2, seed=43)
    clump = N.fbm(p * 18, 3, seed=47)
    shade = .80 + .35 * np.clip(streak * .9 + fine * .35 + .25, 0, 1) - .20 * np.clip(-clump, 0, 1)
    return np.clip(black * shade[..., None] * 1.15, 0, 1)


def suit_color(p, n, white, black, which=None):
    m = patch_mask(p, n) if (PROJECTED and not BLOBS) else shag_mask(p, which)
    wc = triplanar(white, p, n, TILE)
    # under the strands only the black backing shows in the gaps; the swatch photo is too light for it
    bc = shag_detail(p, triplanar(black, p, n, .22)) * .5
    # very slight low-frequency warmth/soil variation in the white plush
    var = 1 + .035 * N.fbm(p * 6, 3, seed=11)[..., None]
    wc = np.clip(wc * var * np.array([1.0, .992, .975]), 0, 1)
    return wc * (1 - m[..., None]) + bc * m[..., None], m


def legging_spots(charts_leg, seed=12):
    """Painted spots: round 19 takes them from the approved generated views (markings.leg_spots); before,
    random spots spaced out on the leg charts' surfaces."""
    if PROJECTED:
        # round 19b: the spots projected from the approved views become painted blobs (an ellipse or a few per
        # spot), so their edges are clean paint rather than the projection's streaks at the legs' sides
        import approved_views as AV
        out = []
        for ch in charts_leg:
            v, f = ch['v'], ch['f']
            cen = v[f].mean(1)
            fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
            area = .5 * np.linalg.norm(fn, axis=1)
            fn = fn / np.maximum(2 * area[:, None], 1e-12)
            m = AV.project_spots(cen, fn, _OCC, _LEG_EXTENT)
            out += [(c, r * np.array([1.06, 1.06, 1.]), U) for c, r, U in _mask_blobs(cen, area, fn, m, .008, MIN_SPOT_AREA)]
        return out
    rng = np.random.default_rng(seed)
    spots = []
    for ch in charts_leg:
        v = ch['v']
        cand = v[(v[:, 1] > .23) & (v[:, 1] < .76 + LEG_LIFT)]       # none on the black socks below the calf
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


SOCK_TOP = .192          # top of the black socks' ribbed cuff (m)


def sock_cuff(y):
    """1 on the sock's ribbed cuff band, 0 elsewhere."""
    return np.clip((y - (SOCK_TOP - .026)) / .004, 0, 1) * np.clip((SOCK_TOP - y) / .004, 0, 1)


def legging_color(p, n, cotton, spots):
    base = triplanar(cotton, p, n, TILE * .6)
    lum = base.mean(-1, keepdims=True)
    black = np.array([.085, .085, .092]) * (.75 + .5 * lum)
    m = spots(p, n) if callable(spots) else blob_mask(p, spots, rough=(.30 if PROJECTED else .45), edge=.10, seed=21)
    brush = .88 + .12 * N.fbm(p * 160, 2, seed=4)[..., None]
    paint = np.array([.94, .94, .92]) * brush
    out = black * (1 - m[..., None]) + paint * m[..., None]
    # black socks pulled up over the tights' feet: plain knit with a ribbed cuff at the top
    cuff = sock_cuff(p[..., 1])
    ang = np.arctan2(p[..., 2] + .02, np.abs(p[..., 0]) - .10)
    rib = .5 + .5 * np.sin(ang * 46)
    sock = np.array([.060, .060, .066]) * (.85 + .3 * lum) * (1 + .35 * cuff[..., None] * rib[..., None])
    under = (p[..., 1] < SOCK_TOP)[..., None]
    return np.where(under, sock, out)


def mild_lift(rgb):
    """Gentle brightening of the photographed mask (keeps black paint black)."""
    a = rgb.astype(np.float32) / 255
    l = a.mean(-1, keepdims=True)
    sat = a.max(-1, keepdims=True) - a.min(-1, keepdims=True)
    lift = np.clip((l - .22) / .35, 0, 1) * np.clip(1 - sat * 2.5, 0, 1)   # white paint only, not eyes/muzzle
    out = a + (1 - (1 - a) ** 1.8 - a) * lift
    return out
