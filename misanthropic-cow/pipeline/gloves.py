"""Hoof gloves.

Since the hands round, the gloves are the owner's Tripo model of the glove photo, cut out and
re-baked by tripo_gloves.py, closed by repair_gloves.py and rebuilt as smooth solids with a cuff that
fits the sleeve by rebuild_gloves.py (assets/gloves_tripo.glb), and placed here on each hand: a long cream
terry mitten with a thumb, and two glossy black hoof halves chipped to red card (left) and green
card (right).  Each glove is one seamless mesh; the hoof halves follow the HoofFingers bone and the
thumb the Thumb bone through smooth per-vertex weights (`hoof_w`, `thumb_w`).

The procedural gloves below (used when the asset is missing) were the previous version, rebuilt from
the close-up glove photos (For_Next_Step: glove images 1-5) and shaped
after the Tripo "Shy Cow" model the owner liked.

Each glove is a long heathered terry-cloth mitten with a separate cloth thumb standing out from the
side, and two dark brown lacquered hoof halves over the fingertips: domed shells with a straight
inner edge, side by side and slightly splayed so they read as a cloven hoof, curling toward the palm
at their points.  The mitten narrows into them and its tip tucks inside.  The halves are
papier-mache over printed card; the paint is chipped, showing red card on one glove and green on
the other.

Everything is built in the hand's own frame at the bind pose:
  u  along the hand from the wrist joint toward the hoof tip,
  a  across the palm, positive toward the thumb,
  w  out of the palm (the palm faces the body at rest).
"""
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
import sdf as S
import design as D
import garments as Gm
import textures as T

CHIP = {'L': (.78, .27, .10), 'R': (.13, .55, .18)}       # card showing through the chipped paint
ASSET = Path(__file__).resolve().parent.parent / 'assets' / 'gloves_tripo.glb'
_TRIPO = []


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
    e3 = _ellipsoid(u, a, w, (.108, 0, 0), (.050, .039, .018))      # tapers into the hoof
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
    """One hoof half (h = +1 thumb side, -1 little-finger side), shaped like a real cloven hoof as in
    the Shy Cow reference: a domed shell over the fingertips (rounded back, flatter sole), curling
    toward the palm at its point, with a straight inner edge along the split, splayed 3 degrees."""
    u, a, w = local(p, side)
    c = np.array([.138, h * .030, 0.])
    sp = np.deg2rad(3) * h
    du, da = u - c[0], a - c[1]
    u2 = c[0] + du * np.cos(sp) + da * np.sin(sp)
    a2 = c[1] - du * np.sin(sp) + da * np.cos(sp)
    t = np.clip((u2 - c[0]) / .062, -1, 1)
    w2 = w - .016 * np.clip(t, 0, 1) ** 2              # the point curls toward the palm
    w2 = w2 + .006                                       # dome on the back of the hand, flatter sole
    narrow = 1 - .35 * np.clip(t, 0, 1) ** 1.5           # tapers to a rounded point
    e = _ellipsoid(u2, (a2 - c[1]) / narrow + c[1], w2, c, (.062, .033, .026)) * np.minimum(narrow, 1)
    edge = -(h * (a2 - c[1]) + .029)                     # straight inner edge, 1 mm off the split
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
    base = np.array([.84, .81, .74])
    col = base[None, None] * (.80 + .22 * loops[..., None]) * (1 - .05 * np.clip(soil, 0, 3)[..., None])
    # heathered yarn: scattered darker grey-brown loops through the cream (Shy Cow reference)
    fleck = (rng.random((size, size)) < .07) * loops
    col = col * (1 - .32 * gaussian_filter(fleck, .7, mode='wrap')[..., None] * 2.2)
    hgt = gaussian_filter(loops, .8, mode='wrap')
    gy, gx = np.gradient(hgt)
    nrm = np.dstack([-gx * 4, -gy * 4, np.ones_like(hgt)])
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    return np.clip(col, 0, 1), nrm * .5 + .5


def hoof_texture(side, size=512, seed=11):
    """Glossy dark brown paint with a few chips showing the printed card underneath."""
    rng = np.random.default_rng(seed + (0 if side == 'L' else 7))
    n = gaussian_filter(rng.normal(size=(size, size)), 18, mode='wrap')
    n2 = gaussian_filter(rng.normal(size=(size, size)), 3, mode='wrap')
    n = n / n.std() + .45 * n2 / n2.std()
    chip = gaussian_filter((n > 2.25).astype(float), 1.2)
    edge = np.clip(gaussian_filter((n > 2.0).astype(float), 2) - chip, 0, 1)
    # dark brown lacquer with a brushed grain along the hoof (Shy Cow, Ryerson photo)
    grain = gaussian_filter(rng.normal(size=(size, size)), (14, 1.2), mode='wrap')
    grain = grain / grain.std()
    brown = np.array([.105, .058, .038])[None, None] * (1 + .22 * grain[..., None])
    col = brown * (1 - chip[..., None]) + np.array(CHIP[side])[None, None] * chip[..., None]
    col = col * (1 - .5 * edge[..., None]) + np.array([.10, .10, .10]) * .5 * edge[..., None]
    rough = .32 + .45 * chip
    return np.clip(col, 0, 1), rough


def _ss(a, b, x):
    w = np.clip((x - a) / (b - a), 0, 1)
    return w * w * (3 - 2 * w)


def tripo_asset():
    if not _TRIPO and ASSET.exists():
        import glb as G
        _TRIPO.append((G.read(str(ASSET)), json.loads(ASSET.with_suffix('.json').read_text())))
    return _TRIPO[0] if _TRIPO else None


# The thumb lies along the thumb-side edge of each Tripo mitten as its own lobe, rooted at about
# u = 0 and reaching its tip at u = .08-.09.  It is the part beyond this line in (u, a) (from the
# owner's glove model, both gloves alike); the mitten body stays below it.
THUMB_LINE = ((-.040, .036), (.000, .044), (.030, .047), (.115, .041))
THUMB_U = (-.035, -.010, .100, .115)        # the lobe starts and ends along the hand


def _thumb_line(u):
    pu, pa = np.array(THUMB_LINE).T
    return np.interp(u, pu, pa)


_GLOVE = {}


def tripo_glove(side):
    """The Tripo glove for one hand, moved from its own frame onto the hand at the bind pose."""
    if side not in _GLOVE:
        _GLOVE[side] = _tripo_glove(side)
    return dict(_GLOVE[side])


def _tripo_glove(side):
    m, meta = tripo_asset()
    p = [q for q in m.parts if q['name'] == f'Glove_{side}_tripo'][0]
    u, a, w = p['v'].astype(float).T
    hoof_u = meta['gloves'][side]['hoof_u']
    o, d, aa, pn = hand_frame(side)
    v = o + u[:, None] * d + a[:, None] * aa + w[:, None] * pn
    f = p['f'].astype(np.int64)
    # the asset already fits the sleeve: rebuild_gloves.py eased its wrist into the sleeve opening and
    # gave it a round cuff that fills the sleeve to 8 mm inside its surface, so it is placed rigidly
    hoof_w = _ss(hoof_u - .022, hoof_u + .004, u)
    line = _thumb_line(u)
    thumb_w = _ss(line - .002, line + .008, a) * _ss(THUMB_U[0], THUMB_U[1], u) * _ss(THUMB_U[3], THUMB_U[2], u)
    return {'name': f'Glove_{side}_terry_mitten_thumb_and_black_hooves', 'v': v, 'f': f,
            'n': S.vertex_normals(v, f), 'uv': p['uv'], 'uv1': None, 'kind': 'tripo',
            'hoof_w': hoof_w, 'thumb_w': thumb_w, 'src_material': p['material']}


def thumb_hinge(parts, side):
    """Root and pointing direction of the Tripo glove's thumb at the bind pose (None for the
    procedural gloves), so the Thumb bone can curl it toward the palm about its own hinge."""
    for p in parts:
        if 'thumb_w' in p:
            v, tw = p['v'], p['thumb_w']
            root = v[(tw > .3) & (tw < .7)].mean(0)
            o, d, aa, pn = hand_frame(side)
            tip = v[tw > .9][np.argmax((v[tw > .9] - o) @ d)]
            dr = tip - root; dr -= pn * (dr @ pn)
            return root, dr / np.linalg.norm(dr)
    return None


def tripo_material(model, side):
    """Copy the asset's baked material for one glove (and its images) into the model."""
    m, _ = tripo_asset()
    p = [q for q in m.parts if q['name'] == f'Glove_{side}_tripo'][0]
    mat = json.loads(json.dumps(m.materials[p['material']]))
    pb = mat['pbrMetallicRoughness']
    for k in ('baseColorTexture', 'metallicRoughnessTexture'):
        if k in pb:
            pb[k]['image'] = model.add_image(*m.images[pb[k]['image']])
    return model.add_material(mat)


def joint_points(parts, side):
    """Bind positions of the HoofFingers and Thumb bones from a glove's parts."""
    o, d, aa, pn = hand_frame(side)
    for p in parts:
        if 'hoof_w' in p:
            v = p['v']; t = (v - o) @ d
            base = (p['hoof_w'] > .5) & (t < np.percentile(t[p['hoof_w'] > .5], 15))
            return v[base].mean(0), thumb_hinge(parts, side)[0]
    caps = np.vstack([p['v'] for p in parts if 'hoof_cap' in p['name']])
    top = caps[:, 1] > np.percentile(caps[:, 1], 88)
    th = np.vstack([p['v'] for p in parts if p['name'].endswith('cloth_thumb')])
    proj = (th - o) @ d
    return caps[top].mean(0), th[proj < np.percentile(proj, 15)].mean(0)


def build(side, step=.0016):
    """Return the glove parts for one side: the Tripo glove if its asset is present, otherwise the
    procedural mitten, thumb and two hoof plates."""
    if tripo_asset() is not None:
        return [tripo_glove(side)]
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
            'name': f'Glove_{side}_dark_brown_lacquer_hoof',
            'pbrMetallicRoughness': {'baseColorTexture': {'image': img, 'texCoord': 0}, 'baseColorFactor': [1, 1, 1, 1],
                                     'metallicRoughnessTexture': {'image': img_mr, 'texCoord': 0},
                                     'metallicFactor': 1, 'roughnessFactor': 1}})
    return out
