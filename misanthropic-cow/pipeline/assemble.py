"""Assemble the static (unrigged) v10 model: garments + baked textures + kept assets + shag + AO."""
import io, json
from pathlib import Path
import numpy as np
from PIL import Image
import sdf as S
import design as D
import garments as Gm
import textures as T
import assets as A
import glb as G
import noise as N
import rig as RG
from scipy.spatial import cKDTree

SHEEN = lambda c, r: {'KHR_materials_sheen': {'sheenColorFactor': [c, c, c], 'sheenRoughnessFactor': r}}


def scene_sdf(p):
    return np.minimum(np.minimum(D.body_sdf(p), D.legging_sdf(p)), D.udder_sdf(p))


def sdf_ao(v, n, k=1.0, steps=5, h=.013):
    occ = np.zeros(len(v))
    for i in range(1, steps + 1):
        d = scene_sdf(v + n * (h * i))
        occ += (h * i - np.minimum(d, h * i)) / (2 ** (i - 1))
    return np.clip(1 - k * occ / h * .38, .35, 1).astype(np.float32)


def tinted_tile(tile, colour):
    t = tile / max(tile.mean(), 1e-3)
    t = .82 + .18 * t           # keep the weave subtle
    return np.clip(t * np.asarray(colour), 0, 1)


def shag_strands(v, f, n, m, clump_density=3.0e3, per_clump=5, seed=7):
    """Black shag suggested by sparse clumps of short tapered strands (the texture carries the rest).
    Returns verts, faces, normals, t-along-strand (0 root .. 1 tip), strand id, roots."""
    rng = np.random.default_rng(seed)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    area = .5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    w = area * np.clip((m - .55) / .45, 0, 1)
    nclump = int(w.sum() * clump_density)
    fi = rng.choice(len(f), nclump, p=w / w.sum())
    r1, r2 = rng.random(nclump), rng.random(nclump)
    s1 = np.sqrt(r1)
    bc = np.stack([1 - s1, s1 * (1 - r2), s1 * r2], 1)
    croot = np.einsum('ij,ijk->ik', bc, v[f[fi]])
    cn = np.einsum('ij,ijk->ik', bc, n[f[fi]]); cn /= np.linalg.norm(cn, axis=1, keepdims=True)
    down = np.array([0, -1, 0.])
    cdir = cn * .45 + down * .55 + rng.normal(0, .18, (nclump, 3))
    cdir /= np.linalg.norm(cdir, axis=1, keepdims=True)
    cL = rng.uniform(.016, .036, nclump)
    count = nclump * per_clump
    root = np.repeat(croot, per_clump, 0) + rng.normal(0, .0035, (count, 3))
    nr = np.repeat(cn, per_clump, 0)
    d = np.repeat(cdir, per_clump, 0) + rng.normal(0, .07, (count, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    L = np.repeat(cL, per_clump, 0) * rng.uniform(.75, 1.1, count)
    tipc = np.repeat(croot + cdir * cL[:, None] * .9, per_clump, 0)   # strands of a clump converge
    side = np.cross(d, rng.normal(0, 1, (count, 3)))
    side /= np.linalg.norm(side, axis=1, keepdims=True)
    segs = 3
    ts = np.linspace(0, 1, segs + 1)
    width = .0050 * (1 - ts * .9)
    verts = []
    for k, t in enumerate(ts):
        straight = root - nr * .0015 + d * (L * t)[:, None] + down * (.25 * L * t * t)[:, None]
        ctr = straight * (1 - .45 * t * t) + tipc * (.45 * t * t)
        verts += [ctr - side * width[k] / 2, ctr + side * width[k] / 2]
    V = np.stack(verts, 1)
    idx = np.arange(count)[:, None] * (2 * (segs + 1))
    F = []
    for k in range(segs):
        a0, a1, b0, b1 = 2 * k, 2 * k + 1, 2 * k + 2, 2 * k + 3
        F += [np.hstack([idx + a0, idx + a1, idx + b1]), np.hstack([idx + a0, idx + b1, idx + b0])]
    return (V.reshape(-1, 3), np.vstack(F), np.repeat(nr, 2 * (segs + 1), 0), np.tile(np.repeat(ts, 2), count),
            np.repeat(np.arange(count), 2 * (segs + 1)), root, np.repeat(fi, per_clump), np.repeat(bc, per_clump, 0))


def build(v09_path, tex_dir, out_dir, quick=False):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    src = G.read(v09_path)
    model = G.Model()
    tiles = {k: T.load_tile(Path(tex_dir) / f) for k, f in [
        ('white', 'white_faux_fur_basecolor.jpg'), ('black', 'black_shag_fur_basecolor.jpg'),
        ('cotton', 'cotton_weave_basecolor.jpg')]}
    raw = lambda f: (Path(tex_dir) / f).read_bytes()
    img_fur_n = model.add_image(raw('white_faux_fur_normal.jpg'))
    img_cot_n = model.add_image(raw('cotton_weave_normal.jpg'))
    sc = .5 if quick else 1
    report = {}

    # --- suit
    suit = Gm.build_suit(step=.006 if quick else .0042, target=60000 if quick else 170000)
    sv, sf, sn = suit['v'], suit['f'], suit['n']
    ao_suit = sdf_ao(sv, sn)
    W_suit = RG.suit_weights(sv, sf, suit['labels'])
    sizes = {'Suit_torso': (2048, 2048), 'Suit_hood': (1024, 1024), 'Suit_sleeve_L': (1024, 1024), 'Suit_sleeve_R': (1024, 1024),
             'Horn_tube': (512, 512)}
    for ch in suit['charts']:
        key = '_'.join(ch['name'].split('_')[:3]) if 'sleeve' in ch['name'] else '_'.join(ch['name'].split('_')[:2])
        W, H = [int(x * sc) for x in sizes[key]]
        p, n, cover = T.bake_chart(ch, sn, W, H)
        nn = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
        col, m = T.suit_color(p, nn, tiles['white'], tiles['black'], T.patches_for(ch['name']))
        col = T.dilate(col, cover)
        img = model.add_image(T.to_jpeg(col))
        mat = model.add_material({'name': ch['name'], 'pbrMetallicRoughness': {
            'baseColorTexture': {'image': img, 'texCoord': 0}, 'metallicFactor': 0, 'roughnessFactor': .95},
            'normalTexture': {'image': img_fur_n, 'texCoord': 1, 'scale': .6}, 'extensions': SHEEN(.75, .55)})
        model.parts.append({'name': ch['name'], 'v': ch['v'].astype(np.float32), 'n': sn[ch['src']].astype(np.float32),
                            'uv': ch['uv'].astype(np.float32), 'uv1': ch['uv1'].astype(np.float32),
                            'ao': ao_suit[ch['src']], 'f': ch['f'].astype(np.int32), 'material': mat, 'group': 'suit',
                            'W': W_suit[ch['src']]})
    # shag strands on the black patches
    fl = suit['labels']
    cen = sv[sf].mean(1)
    piece = np.where(fl == 2, 1, np.where(fl == 3, 2, 0))          # 0 torso/hood/tube, 1 sleeve L, 2 sleeve R
    allowed = [T.TORSO_PATCHES, T.SLEEVE_PATCHES['L'], T.SLEEVE_PATCHES['R']]
    m_face = np.zeros(len(sf))
    for k in range(3):
        sel = piece == k
        m_face[sel] = T.shag_mask(cen[sel], allowed[k])
    sv2, sf2, sn2, tco, sid, roots, rface, rbc = shag_strands(sv, sf, sn, m_face, clump_density=(1.5e3 if quick else 3.0e3))
    # strand roots follow the face they grew from; tips swing with that piece's own patch spring bone
    W_root = np.einsum('ij,ijk->ik', rbc, W_suit[sf[rface]])
    pm = np.stack([T.blob_mask(roots, [pc]) for pc in T.all_patches()], 1)
    for k in range(3):
        mask = np.ones(pm.shape[1], bool); mask[allowed[k]] = False
        rows = np.nonzero(piece[rface] == k)[0]
        pm[np.ix_(rows, np.nonzero(mask)[0])] = -1
    patch = pm.argmax(1)
    W_strand = W_root[sid].copy()
    k = (.85 * tco ** 1.2)[:, None]
    tipw = np.zeros_like(W_strand); tipw[np.arange(len(sid)), np.asarray(RG.SHAG)[patch[sid]]] = 1
    W_strand = W_strand * (1 - k) + tipw * k
    shag_mat = model.add_material({'name': 'Black_shag_fur_strands', 'doubleSided': True, 'pbrMetallicRoughness': {
        'baseColorFactor': [.018, .018, .02, 1], 'metallicFactor': 0, 'roughnessFactor': .55}, 'extensions': SHEEN(.06, .5)})
    model.parts.append({'name': 'Suit_black_shag_strands', 'v': sv2.astype(np.float32), 'n': sn2.astype(np.float32),
                        'uv': None, 'uv1': None, 'ao': (.55 + .45 * tco).astype(np.float32), 'f': sf2.astype(np.int32),
                        'material': shag_mat, 'group': 'suit', 'W': W_strand})
    report['shag_strands'] = int(len(roots))

    # --- leggings
    leg = Gm.build_leggings(step=.006 if quick else .0040, target=40000 if quick else 90000)
    lv, lf, ln = leg['v'], leg['f'], leg['n']
    ao_leg = sdf_ao(lv, ln)
    W_leg = RG.leg_weights(lv, lf)
    spots = T.legging_spots([c for c in leg['charts'] if 'seat' not in c['name']])
    for ch in leg['charts']:
        W, H = [int(x * sc) for x in ((1024, 512) if 'seat' in ch['name'] else (1024, 2048))]
        p, n, cover = T.bake_chart(ch, ln, W, H)
        nn = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
        col = T.dilate(T.legging_color(p, nn, tiles['cotton'], spots), cover)
        img = model.add_image(T.to_jpeg(col))
        mat = model.add_material({'name': ch['name'], 'pbrMetallicRoughness': {
            'baseColorTexture': {'image': img, 'texCoord': 0}, 'metallicFactor': 0, 'roughnessFactor': .86},
            'normalTexture': {'image': img_cot_n, 'texCoord': 1, 'scale': .35}})
        model.parts.append({'name': ch['name'], 'v': ch['v'].astype(np.float32), 'n': ln[ch['src']].astype(np.float32),
                            'uv': ch['uv'].astype(np.float32), 'uv1': ch['uv1'].astype(np.float32),
                            'ao': ao_leg[ch['src']], 'f': ch['f'].astype(np.int32), 'material': mat, 'group': 'legs',
                            'W': W_leg[ch['src']]})
    # --- panties (pink satin, sits on the leggings)
    pan = Gm.build_panties(leg)
    satin = model.add_image(T.to_jpeg(tinted_tile(tiles['cotton'], (.97, .79, .83))))
    mat = model.add_material({'name': 'Panties_pink_satin', 'pbrMetallicRoughness': {
        'baseColorTexture': {'image': satin, 'texCoord': 0}, 'metallicFactor': 0, 'roughnessFactor': .42},
        'normalTexture': {'image': img_cot_n, 'texCoord': 1, 'scale': .12}, 'extensions': SHEEN(.5, .3)})
    model.parts.append({'name': pan['name'], 'v': pan['v'].astype(np.float32), 'n': ln[pan['src']].astype(np.float32),
                        'uv': pan['uv'].astype(np.float32), 'uv1': pan['uv1'].astype(np.float32), 'ao': ao_leg[pan['src']],
                        'f': pan['f'].astype(np.int32), 'material': mat, 'group': 'legs', 'W': W_leg[pan['src']]})
    # --- udder
    pink = model.add_image(T.to_jpeg(tinted_tile(tiles['cotton'], (.94, .66, .72))))
    umat = model.add_material({'name': 'Udder_soft_pink_cloth', 'pbrMetallicRoughness': {
        'baseColorTexture': {'image': pink, 'texCoord': 0}, 'metallicFactor': 0, 'roughnessFactor': .80},
        'normalTexture': {'image': img_cot_n, 'texCoord': 1, 'scale': .18}, 'extensions': SHEEN(.35, .5)})
    for ch in Gm.build_udder(step=.004 if quick else .0028, target=20000 if quick else 50000):
        n = S.vertex_normals(ch['v'], ch['f'])
        model.parts.append({'name': ch['name'], 'v': ch['v'].astype(np.float32), 'n': n.astype(np.float32),
                            'uv': ch['uv'].astype(np.float32), 'uv1': ch['uv1'].astype(np.float32),
                            'ao': sdf_ao(ch['v'], n, .6), 'f': ch['f'].astype(np.int32), 'material': umat, 'group': 'udder',
                            'W': RG.udder_weights(ch['v'], 'L' if '_L_' in ch['name'] else 'R')})

    # --- kept assets (mask, horns, wire, gloves, slippers)
    remap = {}
    for p, grp in A.load(src):
        mi = p['material']
        if mi not in remap:
            mat = json.loads(json.dumps(src.materials[mi]))
            for holder in [mat.get('pbrMetallicRoughness', {}), mat]:
                for k in list(holder):
                    if k.endswith('Texture') and isinstance(holder[k], dict) and 'image' in holder[k]:
                        im = holder[k]['image']
                        data, mime = src.images[im]
                        if mat['name'] in ('Mask_Photo_Projection', 'Lower_Jaw_Side_Photo_Projection') and k == 'baseColorTexture':
                            arr = np.asarray(Image.open(io.BytesIO(data)).convert('RGB'))
                            data = T.to_jpeg(T.mild_lift(arr), 93)
                        holder[k]['image'] = model.add_image(data, mime)
            ext = mat.get('extensions', {})
            for e in ext.values():
                for k in list(e):
                    if k.endswith('Texture'):
                        e[k]['image'] = model.add_image(*src.images[e[k]['image']])
            if mat['name'] == 'Glove_v07_dark_hoof_caps':
                # the hoof caps are glossy black in every photo (v08 had them mid grey-teal)
                mat['pbrMetallicRoughness']['baseColorFactor'] = [.028, .028, .032, 1]
                mat['pbrMetallicRoughness']['roughnessFactor'] = .42
            remap[mi] = model.add_material(mat)
        q = dict(p); q['material'] = remap[mi]; q['group'] = grp
        if q.get('ao') is None:
            q['ao'] = np.ones(len(q['v']), np.float32)
        if q.get('uv') is None:
            q['uv1'] = None
        W = np.zeros((len(q['v']), RG.NB))
        if grp == 'head':
            W[:, RG.HEAD] = 1
        elif grp.startswith('glove'):
            W = RG.glove_weights(q, grp[-1])
        elif grp.startswith('foot'):
            W[:, RG.LEG[grp[-1]]['foot']] = 1
        q['W'] = W
        model.parts.append(q)
    report['triangles'] = int(sum(len(p['f']) for p in model.parts))
    report['vertices'] = int(sum(len(p['v']) for p in model.parts))
    return model, report
