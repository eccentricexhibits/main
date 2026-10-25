"""Hoof gloves, rebuilt from the close-up glove photos (For_Next_Step: glove images 1-5).

Each glove is a long cream terry-cloth mitten with a separate cloth thumb standing out from the
side, and two long black lacquered hoof plates over the fingertips: half-ovals with a straight inner
edge, side by side and slightly splayed so they read as a cloven hoof.  The mitten's tip tucks inside
the plates.  The plates are papier-mache over printed card; the black paint is chipped, showing red
card on one glove and green on the other.

Everything is built in the hand's own frame at the bind pose:
  u  along the hand from the wrist joint toward the hoof tip,
  a  across the palm, positive toward the thumb,
  w  out of the palm (the palm faces the body at rest).
"""
import numpy as np
from scipy.ndimage import gaussian_filter
import sdf as S
import design as D
import garments as Gm
import textures as T

CHIP = {'L': (.78, .27, .10), 'R': (.13, .55, .18)}       # card showing through the chipped paint


def hand_frame(side):
    s = 1 if side == 'L' else -1
    el, wr = D.J[f'Forearm_{side}'], D.J[f'Hand_{side}']
    d = (wr - el) / np.linalg.norm(wr - el)
    pn = np.array([-s, 0, 0.]); pn = pn - d * (pn @ d); pn /= np.linalg.norm(pn)
    a = s * np.cross(pn, d)
    return wr, d, a, pn


def local(p, side):
    o, d, a, pn = hand_frame(side)
    q = p - o
    return q @ d, q @ a, q @ pn


def _ellipsoid(u, a, w, c, r):
    k0 = np.sqrt(((u - c[0]) / r[0]) ** 2 + ((a - c[1]) / r[1]) ** 2 + ((w - c[2]) / r[2]) ** 2)
    k1 = np.sqrt(((u - c[0]) / r[0] ** 2) ** 2 + ((a - c[1]) / r[1] ** 2) ** 2 + ((w - c[2]) / r[2] ** 2) ** 2)
    return k0 * (k0 - 1) / np.maximum(k1, 1e-9)


def mitten_sdf(p, side):
    """Soft rounded mitten: narrow cuff inside the sleeve, wider flat palm, rounded finger end."""
    u, a, w = local(p, side)
    e1 = _ellipsoid(u, a, w, (-.020, 0, 0), (.050, .036, .020))
    e2 = _ellipsoid(u, a, w, (.045, .002, .001), (.055, .046, .023))
    e3 = _ellipsoid(u, a, w, (.112, 0, 0), (.054, .044, .019))
    return S.smin(S.smin(e1, e2, .02), e3, .02)


def thumb_axis(side):
    ang = np.deg2rad(42)
    b0 = np.array([.040, .034, .004])
    b1 = b0 + .060 * np.array([np.cos(ang), np.sin(ang), .12])
    return b0, b1


def thumb_sdf(p, side):
    o, d, a, pn = hand_frame(side)
    b0, b1 = thumb_axis(side)
    P0 = o + b0[0] * d + b0[1] * a + b0[2] * pn
    P1 = o + b1[0] * d + b1[1] * a + b1[2] * pn
    return S.round_cone(p, P0, P1, .0175, .0145)


def plate_sdf(p, side, h):
    """One hoof half (h = +1 thumb side, -1 little-finger side): a long half-oval, thinning toward its
    rounded point, with a straight inner edge along the split; splayed 3 degrees off the hand line."""
    u, a, w = local(p, side)
    c = np.array([.148, h * .031, 0.])
    sp = np.deg2rad(3) * h
    du, da = u - c[0], a - c[1]
    u2 = c[0] + du * np.cos(sp) + da * np.sin(sp)
    a2 = c[1] - du * np.sin(sp) + da * np.cos(sp)
    taper = 1 - .25 * np.clip((u2 - c[0]) / .070, 0, 1)
    e = _ellipsoid(u2, a2, w / taper, c, (.070, .034, .021)) * np.minimum(taper, 1)
    edge = -(h * (a2 - c[1]) + .030)                     # straight inner edge, 1 mm off the split
    return S.smax(e, edge, .004)


def terry_tile(size=1024, seed=3):
    """Tileable cream terry-cloth loops (height map and colour) at TILE metres per repeat."""
    rng = np.random.default_rng(seed)
    f = np.fft.fftfreq(size)[:, None] ** 2 + np.fft.fftfreq(size)[None, :] ** 2
    loops_per_tile = Gm.TILE / .0015                      # ~1.5 mm loops
    k = loops_per_tile / size
    band = np.exp(-((np.sqrt(f) - k) / (.55 * k)) ** 2)
    h = np.real(np.fft.ifft2(np.fft.fft2(rng.normal(size=(size, size))) * band))
    h = (h - h.mean()) / h.std()
    loops = np.clip((h + .3) / 1.6, 0, 1) ** .8           # separate little loop tops, not ridges
    soil = np.real(np.fft.ifft2(np.fft.fft2(rng.normal(size=(size, size))) * np.exp(-f / (2 * (3 / size) ** 2))))
    soil = (soil - soil.mean()) / soil.std()
    base = np.array([.86, .83, .75])
    col = base[None, None] * (.80 + .22 * loops[..., None]) * (1 - .05 * np.clip(soil, 0, 3)[..., None])
    hgt = gaussian_filter(loops, .8, mode='wrap')
    gy, gx = np.gradient(hgt)
    nrm = np.dstack([-gx * 4, -gy * 4, np.ones_like(hgt)])
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    return np.clip(col, 0, 1), nrm * .5 + .5


def hoof_texture(side, size=512, seed=11):
    """Glossy black paint with a few chips showing the printed card underneath."""
    rng = np.random.default_rng(seed + (0 if side == 'L' else 7))
    n = gaussian_filter(rng.normal(size=(size, size)), 18, mode='wrap')
    n2 = gaussian_filter(rng.normal(size=(size, size)), 3, mode='wrap')
    n = n / n.std() + .45 * n2 / n2.std()
    chip = gaussian_filter((n > 2.25).astype(float), 1.2)
    edge = np.clip(gaussian_filter((n > 2.0).astype(float), 2) - chip, 0, 1)
    black = np.array([.022, .022, .026])
    col = black[None, None] * (1 - chip[..., None]) + np.array(CHIP[side])[None, None] * chip[..., None]
    col = col * (1 - .5 * edge[..., None]) + np.array([.10, .10, .10]) * .5 * edge[..., None]
    rough = .32 + .45 * chip
    return np.clip(col, 0, 1), rough


def build(side, step=.0016):
    """Return the glove parts for one side: mitten, thumb and the two hoof plates."""
    o, d, a, pn = hand_frame(side)
    lo = np.minimum(o - .08 * d, o + .25 * d) - .08
    hi = np.maximum(o - .08 * d, o + .25 * d) + .08
    parts = []
    axis = [o - .08 * d, o + .17 * d]
    for name, fn, target in [('terry_mitten', lambda q: mitten_sdf(q, side), 9000),
                             ('cloth_thumb', lambda q: thumb_sdf(q, side), 2500)]:
        v, f = Gm.mesh_from(fn, lo, hi, step, target, smooth=4)
        uvfn = lambda q: Gm.cyl_uv(q, axis, -a, pn, .03, (-.08, .17))
        ch = Gm.make_chart(v, f, np.zeros(len(f), int), 0, uvfn, f'Glove_{side}_{name}')
        ch['n'] = S.vertex_normals(ch['v'], ch['f'])
        ch['kind'] = 'terry'
        parts.append(ch)
    for h, name in [(1, 'index_middle_hoof_cap'), (-1, 'pinky_ring_hoof_cap')]:
        v, f = Gm.mesh_from(lambda q: plate_sdf(q, side, h), lo, hi, step, 5000, smooth=4)
        u_, a_, w_ = local(v, side)
        uv = np.stack([(u_ - .07) / .16, (h * a_) / .085 + .5 * (w_ > 0)], 1)
        parts.append({'name': f'Glove_{side}_{name}', 'v': v, 'f': f, 'n': S.vertex_normals(v, f), 'uv': uv,
                      'uv1': None, 'kind': 'hoof'})
    # contact shadow where the mitten disappears into the hoof plates and where the thumb meets it
    plates = lambda q: np.minimum(plate_sdf(q, side, 1), plate_sdf(q, side, -1))
    for p in parts:
        if p['kind'] == 'terry':
            dist = np.minimum(plates(p['v']), thumb_sdf(p['v'], side) if 'mitten' in p['name'] else mitten_sdf(p['v'], side))
            p['ao'] = (.55 + .45 * np.clip(dist / .012, 0, 1)).astype(np.float32)
        else:
            p['ao'] = (.65 + .35 * np.clip(mitten_sdf(p['v'], side) / .010, 0, 1)).astype(np.float32)
    return parts


def materials(model):
    """Add the terry and the two hoof-paint materials; returns {'terry': i, 'hoof_L': j, 'hoof_R': k}."""
    col, nrm = terry_tile()
    img_c = model.add_image(T.to_jpeg(col, 90), 'image/jpeg')
    img_n = model.add_image(T.to_jpeg(nrm, 92), 'image/jpeg')
    out = {'terry': model.add_material({
        'name': 'Glove_cream_terry_cloth',
        'pbrMetallicRoughness': {'baseColorTexture': {'image': img_c, 'texCoord': 1}, 'baseColorFactor': [1, 1, 1, 1],
                                 'metallicFactor': 0, 'roughnessFactor': .95},
        'normalTexture': {'image': img_n, 'texCoord': 1, 'scale': .9},
        'extensions': {'KHR_materials_sheen': {'sheenColorFactor': [.25, .24, .22], 'sheenRoughnessFactor': .7}}})}
    for side in 'LR':
        c, r = hoof_texture(side)
        img = model.add_image(T.to_jpeg(c, 92), 'image/jpeg')
        mr = np.dstack([np.zeros_like(r), r, np.zeros_like(r)])          # glTF: G = roughness, B = metallic
        img_mr = model.add_image(T.to_jpeg(mr, 92), 'image/jpeg')
        out['hoof_' + side] = model.add_material({
            'name': f'Glove_{side}_black_lacquer_hoof',
            'pbrMetallicRoughness': {'baseColorTexture': {'image': img, 'texCoord': 0}, 'baseColorFactor': [1, 1, 1, 1],
                                     'metallicRoughnessTexture': {'image': img_mr, 'texCoord': 0},
                                     'metallicFactor': 1, 'roughnessFactor': 1}})
    return out
