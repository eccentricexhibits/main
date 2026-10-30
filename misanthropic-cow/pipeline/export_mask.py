"""Export the mask on its own (the scanned papier-mâché face with its two lower-jaw side pieces, both
horns, the exposed wire of the broken horn, and the fur-covered tube joining the horns) from the static
v10 model, as a GLB and as an OBJ with its MTL and textures.

The piece keeps its real-world size (metres) and the model's axes (+Y up, +Z forward, +X = the
character's left). It is moved so it stands on y = 0 and is centred front to back (z); x is left as it
is, so the mask's mirror plane stays at x = 0. Adding OFFSET back puts it on the v10 body as worn.

Everything else is copied byte for byte: textures, UVs, normals, the tube's tangents and second UV set,
and the baked ambient occlusion in the vertex colours.  The OBJ can carry only one UV set, so it leaves
out the tube's normal map (which uses the second set); its vertex colours use the common "v x y z r g b"
form that Blender and MeshLab read.

usage: python export_mask.py ../models/Misanthropic_Cow_v10.glb <out folder>
"""
import json
import struct
import sys
from pathlib import Path
import numpy as np

NODES = ['Mask_scanned_face', 'Mask_lower_jaw_left_side', 'Mask_lower_jaw_right_side', 'Horn_left_complete',
         'Horn_right_broken', 'Horn_right_exposed_wire', 'Mask_horn_tube_white_faux_fur']
# the v09 horn materials were named from the viewer's side; name them from the character's, like the meshes
RENAME = {'Right_Horn_Yellow_Bands': 'Horn_L_complete_yellow_bands', 'Broken_Left_Horn_Yellow_Bands': 'Horn_R_broken_yellow_bands',
          'Mask_Photo_Projection': 'Mask_face_photo_projection', 'Lower_Jaw_Side_Photo_Projection': 'Mask_lower_jaw_side_photo_projection',
          'Exposed_Dark_Wires': 'Horn_R_exposed_wire', 'Mask_horn_tube_white_faux_fur': 'Horn_tube_white_faux_fur'}
DT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}


def read_glb(path):
    b = Path(path).read_bytes()
    n = struct.unpack('<I', b[12:16])[0]
    o = 20 + n
    return json.loads(b[20:o]), b[o + 8:o + 8 + struct.unpack('<I', b[o:o + 4])[0]]


def write_glb(path, doc, blob):
    js = json.dumps(doc, separators=(',', ':')).encode()
    js += b' ' * (-len(js) % 4)
    blob = bytes(blob) + b'\0' * (-len(blob) % 4)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, 28 + len(js) + len(blob)))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(blob), 0x004E4942)); f.write(blob)


def view_bytes(doc, blob, i):
    bv = doc['bufferViews'][i]
    o = bv.get('byteOffset', 0)
    return blob[o:o + bv['byteLength']]


def accessor(doc, blob, i):
    a = doc['accessors'][i]
    data = view_bytes(doc, blob, a['bufferView'])
    k = NC[a['type']]
    arr = np.frombuffer(data, DT[a['componentType']], a['count'] * k, a.get('byteOffset', 0)).reshape(a['count'], k)
    if a.get('normalized'):
        arr = arr / float(np.iinfo(arr.dtype).max)
    return arr


def subset(doc, blob):
    """The mask nodes as a new glTF document and binary chunk, with positions moved by OFFSET."""
    names = {nd.get('name'): i for i, nd in enumerate(doc['nodes'])}
    picked = [doc['nodes'][names[n]] for n in NODES]
    pos = np.concatenate([accessor(doc, blob, p['attributes']['POSITION'])
                          for nd in picked for p in doc['meshes'][nd['mesh']]['primitives']])
    offset = np.array([0., -pos[:, 1].min(), -(pos[:, 2].min() + pos[:, 2].max()) / 2])
    out = {'asset': {'version': '2.0', 'generator': 'Misanthropic Cow v10 pipeline (export_mask.py)'},
           'scene': 0, 'scenes': [{'name': 'Misanthropic_Cow_Mask', 'nodes': [0]}],
           'nodes': [{'name': 'Misanthropic_Cow_Mask', 'children': []}], 'meshes': [], 'materials': [], 'textures': [],
           'images': [], 'samplers': doc.get('samplers', []), 'accessors': [], 'bufferViews': [], 'buffers': [{}]}
    nb = bytearray()
    maps = {'materials': {}, 'textures': {}, 'images': {}}

    def add_view(data, target=None):
        nb.extend(b'\0' * (-len(nb) % 4))
        bv = {'buffer': 0, 'byteOffset': len(nb), 'byteLength': len(data)}
        if target:
            bv['target'] = target
        nb.extend(data)
        out['bufferViews'].append(bv)
        return len(out['bufferViews']) - 1

    def add_accessor(i, move=False):
        a = dict(doc['accessors'][i])
        old = doc['bufferViews'][a['bufferView']]
        data = bytes(view_bytes(doc, blob, a['bufferView']))
        if move:
            v = np.frombuffer(data, np.float32).reshape(-1, 3) + offset.astype(np.float32)
            data = v.astype(np.float32).tobytes()
            a['min'], a['max'] = v.min(0).tolist(), v.max(0).tolist()
        a['bufferView'] = add_view(data, old.get('target'))
        out['accessors'].append(a)
        return len(out['accessors']) - 1

    def remap(kind, i, make):
        if i not in maps[kind]:
            out[kind].append(make(i))
            maps[kind][i] = len(out[kind]) - 1
        return maps[kind][i]

    def image(i):
        im = dict(doc['images'][i])
        im['bufferView'] = add_view(bytes(view_bytes(doc, blob, im['bufferView'])))
        return im

    def texture(i):
        t = dict(doc['textures'][i])
        t['source'] = remap('images', t['source'], image)
        return t

    def material(i):
        m = json.loads(json.dumps(doc['materials'][i]))
        m['name'] = RENAME.get(m.get('name'), m.get('name'))
        refs = [m.get('pbrMetallicRoughness', {}), m]
        for holder in refs:
            for key, val in list(holder.items()):
                if isinstance(val, dict) and 'index' in val:
                    val['index'] = remap('textures', val['index'], texture)
        return m

    for nd in picked:
        mesh = doc['meshes'][nd['mesh']]
        prims = []
        for p in mesh['primitives']:
            q = {'attributes': {k: add_accessor(v, move=(k == 'POSITION')) for k, v in p['attributes'].items()},
                 'indices': add_accessor(p['indices']), 'material': remap('materials', p['material'], material)}
            if 'mode' in p:
                q['mode'] = p['mode']
            prims.append(q)
        out['meshes'].append({'name': mesh.get('name'), 'primitives': prims})
        out['nodes'].append({'name': nd['name'], 'mesh': len(out['meshes']) - 1})
        out['nodes'][0]['children'].append(len(out['nodes']) - 1)
    used = sorted({k for m in out['materials'] for k in m.get('extensions', {})})
    if used:
        out['extensionsUsed'] = used
    out['buffers'][0]['byteLength'] = len(nb) + (-len(nb) % 4)
    return out, nb, offset


def write_obj(doc, blob, folder, stem):
    """OBJ + MTL + textures from the exported document (one UV set; vertex colours as v x y z r g b)."""
    tex_dir = folder / 'textures'
    tex_dir.mkdir(parents=True, exist_ok=True)
    files = {}

    def tex_file(ref, suffix):
        """Write the image behind a texture reference once, named after its first material."""
        i = doc['textures'][ref['index']]['source']
        if i not in files:
            im = doc['images'][i]
            files[i] = m['name'] + suffix + ('.png' if im.get('mimeType') == 'image/png' else '.jpg')
            (tex_dir / files[i]).write_bytes(bytes(view_bytes(doc, blob, im['bufferView'])))
        return 'textures/' + files[i]

    mtl = [f'# {stem}: materials for the Misanthropic Cow mask (metallic-roughness values in Pr / Pm)']
    for m in doc['materials']:
        pbr = m.get('pbrMetallicRoughness', {})
        c = pbr.get('baseColorFactor', [1, 1, 1, 1])
        mtl += ['', f"newmtl {m['name']}", f'Kd {c[0]:.4f} {c[1]:.4f} {c[2]:.4f}', 'Ka 0 0 0', 'Ks 0.04 0.04 0.04',
                f"Pr {pbr.get('roughnessFactor', 1):.3f}", f"Pm {pbr.get('metallicFactor', 1):.3f}", 'illum 2']
        if 'baseColorTexture' in pbr:
            mtl.append('map_Kd ' + tex_file(pbr['baseColorTexture'], ''))
        nt = m.get('normalTexture')
        if nt and nt.get('texCoord', 0) == 0:       # a normal map on a second UV set can't be carried by OBJ
            mtl.append('norm ' + tex_file(nt, '_normal'))
    (folder / f'{stem}.mtl').write_text('\n'.join(mtl) + '\n')
    lines = [f'# {stem}: the Misanthropic Cow mask, metres, +Y up, +Z forward', f'mtllib {stem}.mtl']
    base = 1
    for nd in doc['nodes'][1:]:
        p = doc['meshes'][nd['mesh']]['primitives'][0]
        at = p['attributes']
        v = accessor(doc, blob, at['POSITION']); nrm = accessor(doc, blob, at['NORMAL']); uv = accessor(doc, blob, at['TEXCOORD_0'])
        col = accessor(doc, blob, at['COLOR_0'])[:, :3] if 'COLOR_0' in at else np.ones_like(v)
        f = accessor(doc, blob, p['indices']).reshape(-1, 3).astype(np.int64) + base
        lines += [f"o {nd['name']}", f"usemtl {doc['materials'][p['material']]['name']}"]
        lines += [f'v {a:.6f} {b:.6f} {c:.6f} {r:.4f} {g:.4f} {bb:.4f}' for (a, b, c), (r, g, bb) in zip(v, col)]
        lines += [f'vt {a:.6f} {1 - b:.6f}' for a, b in uv]
        lines += [f'vn {a:.5f} {b:.5f} {c:.5f}' for a, b, c in nrm]
        lines += ['f ' + ' '.join(f'{i}/{i}/{i}' for i in t) for t in f]
        base += len(v)
    (folder / f'{stem}.obj').write_text('\n'.join(lines) + '\n')


def main(src, dst):
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    doc, blob = read_glb(src)
    out, nb, offset = subset(doc, blob)
    stem = 'Misanthropic_Cow_Mask_v10'
    write_glb(dst / f'{stem}.glb', out, nb)
    write_obj(out, nb, dst / 'OBJ', stem)
    pos = np.concatenate([accessor(out, nb, p['attributes']['POSITION']) for m in out['meshes'] for p in m['primitives']])
    tris = sum(out['accessors'][p['indices']]['count'] // 3 for m in out['meshes'] for p in m['primitives'])
    info = {'triangles': int(tris), 'vertices': int(len(pos)), 'size_m': (pos.max(0) - pos.min(0)).round(4).tolist(),
            'offset_to_v10_body_m': (0 - offset).round(5).tolist(), 'parts': NODES}
    (dst / 'mask_info.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(info))


if __name__ == '__main__':
    main(*sys.argv[1:3])
