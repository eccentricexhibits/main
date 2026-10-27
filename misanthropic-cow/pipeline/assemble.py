"""Assemble the static (unrigged) v10 model: garments + baked textures + kept assets + shag.

No lighting is baked into the model: no ambient occlusion or contact shadows in the vertex colours or
the textures.  Shading belongs to whatever renders the model (the viewer, a game engine), where it
follows the pose; occlusion baked in the rest pose stays put when the arms move."""
import io, json
from pathlib import Path
import numpy as np
from PIL import Image
import sdf as S
import design as D
import garments as Gm
import textures as T
import assets as A
import gloves as GL
import glb as G
import noise as N
import rig as RG
from scipy.spatial import cKDTree

SHEEN = lambda c, r: {'KHR_materials_sheen': {'sheenColorFactor': [c, c, c], 'sheenRoughnessFactor': r}}


def scene_sdf(p):
    return np.minimum(np.minimum(D.body_sdf(p), D.legging_sdf(p)), D.udder_sdf(p))


def tinted_tile(tile, colour):
    t = tile / max(tile.mean(), 1e-3)
    t = .82 + .18 * t           # keep the weave subtle
    return np.clip(t * np.asarray(colour), 0, 1)


def build(v09_path, tex_dir, out_dir, quick=False):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    src = G.read(v09_path)
    model = G.Model()
    tiles = {k: T.load_tile(Path(tex_dir) / f) for k, f in [
        ('white', 'white_faux_fur_basecolor.jpg'), ('cotton', 'cotton_weave_basecolor.jpg')]}
    tiles['black'] = T.load_tile(Path(__file__).resolve().parent.parent / 'textures' / 'black_shag_tile.jpg')
    raw = lambda f: (Path(tex_dir) / f).read_bytes()
    img_fur_n = model.add_image(raw('white_faux_fur_normal.jpg'))
    img_cot_n = model.add_image(raw('cotton_weave_normal.jpg'))
    sc = .5 if quick else 1
    report = {}

    # --- suit
    suit = Gm.build_suit(step=.006 if quick else .0042, target=60000 if quick else 170000)
    sv, sf, sn = suit['v'], suit['f'], suit['n']
    W_suit = RG.suit_weights(sv, sf, suit['labels'])
    sizes = {'Suit_torso': (2048, 2048), 'Hood_white': (1024, 1024), 'Suit_sleeve_L': (1024, 1024), 'Suit_sleeve_R': (1024, 1024),
             'Mask_horn': (512, 512)}
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
                            'ao': None, 'f': ch['f'].astype(np.int32), 'material': mat, 'group': 'suit',
                            'W': W_suit[ch['src']]})
    # shag strands on the black patches
    fl = suit['labels']
    cen = sv[sf].mean(1)
    piece = np.where(fl == 2, 1, np.where(fl == 3, 2, np.where(fl == 0, 0, 3)))   # torso, sleeve L, sleeve R, hood/tube
    allowed = [T.TORSO_PATCHES, T.SLEEVE_PATCHES['L'], T.SLEEVE_PATCHES['R'], []]
    m_face = np.zeros(len(sf))
    for k in range(3):
        sel = piece == k
        m_face[sel] = T.shag_mask(cen[sel], allowed[k])
    import groom as GR
    hair = GR.shag_strands(sv, sf, sn, m_face, scene_sdf, scale=(.6 if quick else 1.0))
    tco, sid, roots, rface, rbc = hair['t'], hair['cid'], hair['roots'], hair['face'], hair['bc']
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
    # opaque, untextured strands: the tubes' own round shading and the root-to-tip tone do the work.
    # Specular is turned down and there is no sheen: thousands of thin glossy tubes otherwise pick up
    # the viewer's room lighting from every side and the black turns charcoal grey.
    shag_mat = model.add_material({'name': 'Black_shag_strands',
                                   'pbrMetallicRoughness': {'baseColorFactor': [.040, .038, .042, 1], 'metallicFactor': 0,
                                                            'roughnessFactor': .55},
                                   'extensions': {'KHR_materials_specular': {'specularFactor': .45}}})
    # split into pieces of whole strands under 65,536 vertices, so each can use 16-bit indices
    starts = hair['starts']
    cuts = [0]
    while cuts[-1] < len(starts) - 1:
        cuts.append(int(np.searchsorted(starts, starts[cuts[-1]] + 65536, 'right')) - 1)
    for k, (s0, s1) in enumerate(zip(cuts[:-1], cuts[1:])):
        v0, v1 = starts[s0], starts[s1]
        fsel = (hair['f'][:, 0] >= v0) & (hair['f'][:, 0] < v1)
        model.parts.append({'name': f'Suit_black_shag_strands_{k + 1}', 'v': hair['v'][v0:v1].astype(np.float32),
                            'n': hair['n'][v0:v1].astype(np.float32), 'uv': None, 'uv1': None,
                            'ao': hair['tone'][v0:v1].astype(np.float32), 'f': (hair['f'][fsel] - v0).astype(np.int32),
                            'material': shag_mat, 'group': 'suit', 'W': W_strand[v0:v1]})
    report['shag_clumps'] = int(len(roots))
    report['shag_strands'] = int(hair['strands'])

    # --- leggings
    leg = Gm.build_leggings(step=.006 if quick else .0040, target=40000 if quick else 90000)
    lv, lf, ln = leg['v'], leg['f'], leg['n']
    W_leg = RG.leg_weights(lv, lf)
    pan = Gm.build_panties(step=.005 if quick else .0035, target=20000 if quick else 45000)
    dk, ik = cKDTree(lv).query(pan['v'], 6)
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
                            'ao': None, 'f': ch['f'].astype(np.int32), 'material': mat, 'group': 'legs',
                            'W': W_leg[ch['src']]})
    # --- panties (pink satin, sits on the leggings)
    # the briefs move with the leggings under them: inverse-distance blend of the nearest few
    wk = 1 / np.maximum(dk, 1e-4); wk /= wk.sum(1, keepdims=True)
    W_pan = np.einsum('vk,vkj->vj', wk, W_leg[ik])
    satin = model.add_image(T.to_jpeg(tinted_tile(tiles['cotton'], (.97, .79, .83))))
    mat = model.add_material({'name': 'Panties_pink_satin', 'pbrMetallicRoughness': {
        'baseColorTexture': {'image': satin, 'texCoord': 0}, 'metallicFactor': 0, 'roughnessFactor': .58},
        'normalTexture': {'image': img_cot_n, 'texCoord': 1, 'scale': .30}, 'extensions': SHEEN(.45, .35)})
    model.parts.append({'name': pan['name'], 'v': pan['v'].astype(np.float32), 'n': pan['n'].astype(np.float32),
                        'uv': pan['uv'].astype(np.float32), 'uv1': pan['uv1'].astype(np.float32),
                        'ao': None,
                        'f': pan['f'].astype(np.int32), 'material': mat, 'group': 'legs', 'W': W_pan})
    # --- udder
    pink = model.add_image(T.to_jpeg(tinted_tile(tiles['cotton'], (.94, .66, .72))))
    umat = model.add_material({'name': 'Udder_soft_pink_cloth', 'pbrMetallicRoughness': {
        'baseColorTexture': {'image': pink, 'texCoord': 0}, 'metallicFactor': 0, 'roughnessFactor': .80},
        'normalTexture': {'image': img_cot_n, 'texCoord': 1, 'scale': .18}, 'extensions': SHEEN(.35, .5)})
    for ch in Gm.build_udder(step=.004 if quick else .0028, target=20000 if quick else 50000):
        n = S.vertex_normals(ch['v'], ch['f'])
        model.parts.append({'name': ch['name'], 'v': ch['v'].astype(np.float32), 'n': n.astype(np.float32),
                            'uv': ch['uv'].astype(np.float32), 'uv1': ch['uv1'].astype(np.float32),
                            'ao': None, 'f': ch['f'].astype(np.int32), 'material': umat, 'group': 'udder',
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
        q['ao'] = None              # v09 carried ambient occlusion in its vertex colours
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

    # --- slippers: the knitted cow heads cut from the Shy Cow model
    for q, grp in A.shy_cow_slippers(model):
        q['group'] = grp
        q['ao'] = None
        q['uv1'] = None
        W = np.zeros((len(q['v']), RG.NB)); W[:, RG.LEG[grp[-1]]['foot']] = 1
        q['W'] = W
        model.parts.append(q)

    # --- hoof gloves, rebuilt from the glove close-ups
    gm = GL.materials(model) if GL.tripo_asset() is None else {}
    for side in 'LR':
        for p in GL.build(side, step=.0022 if quick else .0016):
            mat = GL.tripo_material(model, side) if p['kind'] == 'tripo' else gm['terry'] if p['kind'] == 'terry' else gm['hoof_' + side]
            q = {'name': p['name'], 'v': p['v'].astype(np.float32), 'n': p['n'].astype(np.float32),
                 'f': p['f'].astype(np.int32), 'uv': p['uv'].astype(np.float32),
                 'uv1': None if p.get('uv1') is None else p['uv1'].astype(np.float32), 'ao': None,
                 'material': mat, 'group': f'glove_{side}'}
            for k in ('hoof_w', 'thumb_w'):
                if k in p:
                    q[k] = p[k]
            q['W'] = RG.glove_weights(q, side)
            model.parts.append(q)
    # --- tail: gold satin bow on the back of the hem, a lamp cord down to the floor, a two-prong plug
    import tail as TL
    tm = {'bow': model.add_material({'name': 'Tail_gold_satin_bow', 'pbrMetallicRoughness': {
              'baseColorFactor': [.80, .56, .20, 1], 'metallicFactor': 0, 'roughnessFactor': .34}, 'extensions': SHEEN(.55, .35)}),
          'cord': model.add_material({'name': 'Tail_tan_lamp_cord_plastic', 'pbrMetallicRoughness': {
              'baseColorFactor': [.72, .52, .24, 1], 'metallicFactor': 0, 'roughnessFactor': .38}})}
    tm['plug'] = tm['cord']
    tm['blades'] = model.add_material({'name': 'Tail_plug_brass_blades', 'pbrMetallicRoughness': {
        'baseColorFactor': [.86, .72, .45, 1], 'metallicFactor': 1, 'roughnessFactor': .32}})
    tail_parts = TL.build(step=.0011 if quick else .0008)
    cv, cf, cuv, cs = TL.cord_mesh()
    tail_parts.append(('Tail_tan_lamp_cord', cv, cf, 'cord'))
    for name, v, f, kind in tail_parts:
        n = S.vertex_normals(v, f)
        if kind == 'cord':
            W = TL.cord_weights(cs, RG.NB, RG.TAIL_BOW, RG.TAIL)
            uv = cuv
        else:
            W = np.zeros((len(v), RG.NB)); W[:, RG.TAIL_BOW if kind == 'bow' else RG.TAIL[-1]] = 1
            uv = None
        model.parts.append({'name': name, 'v': v.astype(np.float32), 'n': n.astype(np.float32), 'f': f.astype(np.int32),
                            'uv': None if uv is None else uv.astype(np.float32), 'uv1': None,
                            'ao': None, 'material': tm[kind], 'group': 'tail', 'W': W})
    report['triangles'] = int(sum(len(p['f']) for p in model.parts))
    report['vertices'] = int(sum(len(p['v']) for p in model.parts))
    return model, report
