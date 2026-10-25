"""Minimal glTF 2.0 binary (GLB) reader/writer for the Misanthropic Cow v10 pipeline.

Parts are plain dicts:
  name, v (N,3 f32), n (N,3), uv (N,2) or None, uv1 or None, ao (N,) or None,
  f (M,3 int), material (index into Model.materials),
  optional j (N,4 u8) / w (N,4 u8) skin attributes.
Materials are glTF material dicts whose texture references point at Model.images
(index) via {'image': i, 'texCoord': k}; the writer turns them into textures.
"""
from pathlib import Path
import json, struct, io
import numpy as np

COMP = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1', 5122: '<i2', 5120: 'i1'}
WIDTH = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


class Model:
    def __init__(self):
        self.parts = []
        self.materials = []
        self.images = []          # list of (bytes, mimeType)
        self.skin = None          # dict(names, parents, bind(N,3), ibm optional)
        self.animations = []      # list of dict(name, times, tracks{joint:(T,R)}, extras)
        self.extras = {}

    def part(self, name):
        for p in self.parts:
            if p['name'] == name:
                return p
        raise KeyError(name)

    def add_material(self, mat):
        self.materials.append(mat)
        return len(self.materials) - 1

    def add_image(self, data, mime='image/jpeg'):
        self.images.append((data, mime))
        return len(self.images) - 1


def _read(path):
    data = Path(path).read_bytes()
    assert data[:4] == b'glTF'
    jl = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20 + jl])
    blob = data[28 + jl:] if len(data) > 28 + jl else b''
    return doc, blob


def _accessor(doc, blob, i):
    a = doc['accessors'][i]
    bv = doc['bufferViews'][a['bufferView']]
    width = WIDTH[a['type']]
    dt = np.dtype(COMP[a['componentType']])
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = bv.get('byteStride')
    if stride and stride != dt.itemsize * width:
        raw = np.frombuffer(blob, np.uint8, count=stride * a['count'], offset=off).reshape(a['count'], stride)
        x = raw[:, :dt.itemsize * width].copy().view(dt).reshape(-1, width)
    else:
        x = np.frombuffer(blob, dtype=dt, count=a['count'] * width, offset=off).reshape(-1, width).copy()
    if a.get('normalized'):
        x = x.astype(np.float64) / np.iinfo(x.dtype).max
    return x


def read(path):
    doc, blob = _read(path)
    m = Model()
    for im in doc.get('images', []):
        bv = doc['bufferViews'][im['bufferView']]
        o = bv.get('byteOffset', 0)
        m.images.append((bytes(blob[o:o + bv['byteLength']]), im.get('mimeType', 'image/jpeg')))
    tex = doc.get('textures', [])

    def fix(info):
        if info is None:
            return None
        out = dict(info)
        out['image'] = tex[out.pop('index')]['source']
        return out
    for mat in doc.get('materials', []):
        mat = json.loads(json.dumps(mat))
        pb = mat.setdefault('pbrMetallicRoughness', {})
        for k in ['baseColorTexture', 'metallicRoughnessTexture']:
            if k in pb:
                pb[k] = fix(pb[k])
        for k in ['normalTexture', 'occlusionTexture', 'emissiveTexture']:
            if k in mat:
                mat[k] = fix(mat[k])
        sh = mat.get('extensions', {}).get('KHR_materials_sheen')
        if sh:
            for k in ['sheenColorTexture', 'sheenRoughnessTexture']:
                if k in sh:
                    sh[k] = fix(sh[k])
        m.materials.append(mat)
    for node in doc['nodes']:
        if 'mesh' not in node:
            continue
        mesh = doc['meshes'][node['mesh']]
        for pi, prim in enumerate(mesh['primitives']):
            a = prim['attributes']
            p = {'name': mesh.get('name', 'mesh') + (f'_{pi}' if pi else ''),
                 'v': _accessor(doc, blob, a['POSITION']).astype(np.float32),
                 'n': _accessor(doc, blob, a['NORMAL']).astype(np.float32) if 'NORMAL' in a else None,
                 'uv': _accessor(doc, blob, a['TEXCOORD_0']).astype(np.float32) if 'TEXCOORD_0' in a else None,
                 'uv1': _accessor(doc, blob, a['TEXCOORD_1']).astype(np.float32) if 'TEXCOORD_1' in a else None,
                 'ao': None, 'material': prim.get('material', 0)}
            if 'COLOR_0' in a:
                c = _accessor(doc, blob, a['COLOR_0'])
                if c.dtype != np.float64 and c.dtype != np.float32:
                    c = c.astype(np.float64) / 255
                p['ao'] = c[:, 0].astype(np.float32)
            p['f'] = _accessor(doc, blob, prim['indices']).reshape(-1, 3).astype(np.int32)
            if 'JOINTS_0' in a:
                p['j'] = _accessor(doc, blob, a['JOINTS_0']).astype(np.uint8)
                p['w'] = np.rint(_accessor(doc, blob, a['WEIGHTS_0']) * 255).astype(np.uint8)
            m.parts.append(p)
    return m


def image_array(model, i):
    from PIL import Image
    return np.asarray(Image.open(io.BytesIO(model.images[i][0])).convert('RGB'))


def write(model, path, generator='Misanthropic Cow v10 pipeline'):
    data = bytearray()
    doc = {'asset': {'version': '2.0', 'generator': generator}, 'scene': 0,
           'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [], 'accessors': [],
           'bufferViews': [], 'materials': [], 'textures': [], 'images': [], 'samplers': [
               {'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497}]}
    used_ext = set()

    def view(raw, target=None):
        while len(data) % 4:
            data.append(0)
        bv = {'buffer': 0, 'byteOffset': len(data), 'byteLength': len(raw)}
        if target:
            bv['target'] = target
        doc['bufferViews'].append(bv)
        data.extend(raw)
        return len(doc['bufferViews']) - 1

    def acc(x, kind, ctype, normalized=False, minmax=False, target=None):
        x = np.ascontiguousarray(x)
        i = len(doc['accessors'])
        a = {'bufferView': view(x.tobytes(), target), 'componentType': ctype,
             'count': int(len(x)), 'type': kind}
        if normalized:
            a['normalized'] = True
        if minmax:
            a['min'] = np.asarray(x).reshape(len(x), -1).min(0).astype(float).tolist()
            a['max'] = np.asarray(x).reshape(len(x), -1).max(0).astype(float).tolist()
        doc['accessors'].append(a)
        return i

    img_tex = {}

    def texref(info):
        if info is None:
            return None
        info = dict(info)
        im = info.pop('image')
        if im not in img_tex:
            img_tex[im] = len(doc['textures'])
            doc['textures'].append({'sampler': 0, 'source': im})
        info['index'] = img_tex[im]
        return info
    for raw, mime in model.images:
        doc['images'].append({'bufferView': view(raw), 'mimeType': mime})
    for mat in model.materials:
        mat = json.loads(json.dumps(mat))
        pb = mat.setdefault('pbrMetallicRoughness', {})
        for k in ['baseColorTexture', 'metallicRoughnessTexture']:
            if k in pb:
                pb[k] = texref(pb[k])
        for k in ['normalTexture', 'occlusionTexture', 'emissiveTexture']:
            if k in mat:
                mat[k] = texref(mat[k])
        for e, body in mat.get('extensions', {}).items():
            used_ext.add(e)
            for k in list(body):
                if k.endswith('Texture'):
                    body[k] = texref(body[k])
        doc['materials'].append(mat)
    skinned = model.skin is not None
    mesh_nodes = []
    for p in model.parts:
        attrs = {'POSITION': acc(p['v'].astype('<f4'), 'VEC3', 5126, minmax=True, target=34962)}
        if p.get('n') is not None:
            attrs['NORMAL'] = acc(p['n'].astype('<f4'), 'VEC3', 5126, target=34962)
        if p.get('uv') is not None:
            attrs['TEXCOORD_0'] = acc(p['uv'].astype('<f4'), 'VEC2', 5126, target=34962)
        if p.get('uv1') is not None:
            attrs['TEXCOORD_1'] = acc(p['uv1'].astype('<f4'), 'VEC2', 5126, target=34962)
        if p.get('tangent') is not None:
            attrs['TANGENT'] = acc(p['tangent'].astype('<f4'), 'VEC4', 5126, target=34962)
        if p.get('ao') is not None:
            c = np.repeat(np.clip(np.rint(p['ao'] * 255), 0, 255).astype(np.uint8)[:, None], 3, 1)
            attrs['COLOR_0'] = acc(np.hstack([c, np.full((len(c), 1), 255, np.uint8)]), 'VEC4', 5121, normalized=True, target=34962)
        if skinned:
            attrs['JOINTS_0'] = acc(p['j'].astype(np.uint8), 'VEC4', 5121, target=34962)
            attrs['WEIGHTS_0'] = acc(p['w'].astype(np.uint8), 'VEC4', 5121, normalized=True, target=34962)
        nv = len(p['v'])
        idx = p['f'].astype('<u2' if nv < 65536 else '<u4').reshape(-1)
        prim = {'attributes': attrs, 'indices': acc(idx, 'SCALAR', 5123 if nv < 65536 else 5125, target=34963),
                'material': int(p['material'])}
        doc['meshes'].append({'name': p['name'], 'primitives': [prim]})
        node = {'name': p['name'], 'mesh': len(doc['meshes']) - 1}
        doc['nodes'].append(node)
        mesh_nodes.append(len(doc['nodes']) - 1)
    doc['scenes'][0]['nodes'] = list(mesh_nodes)
    if skinned:
        sk = model.skin
        names, parents, bind = sk['names'], sk['parents'], np.asarray(sk['bind'], float)
        rest_rot = sk.get('rest_rot')  # (N,3,3) global rest rotations, default identity
        if rest_rot is None:
            rest_rot = np.tile(np.eye(3), (len(names), 1, 1))
        G = np.tile(np.eye(4), (len(names), 1, 1))
        G[:, :3, :3] = rest_rot
        G[:, :3, 3] = bind
        first = len(doc['nodes'])
        from scipy.spatial.transform import Rotation
        for i, name in enumerate(names):
            L = G[i] if parents[i] < 0 else np.linalg.inv(G[parents[i]]) @ G[i]
            node = {'name': name, 'translation': L[:3, 3].tolist()}
            q = Rotation.from_matrix(L[:3, :3]).as_quat()
            if np.abs(q[:3]).max() > 1e-9:
                node['rotation'] = q.tolist()
            ch = [first + j for j, pp in enumerate(parents) if pp == i]
            if ch:
                node['children'] = ch
            doc['nodes'].append(node)
        ibm = np.linalg.inv(G).transpose(0, 2, 1).reshape(-1, 16).astype('<f4')
        roots = [first + i for i, pp in enumerate(parents) if pp < 0]
        doc['skins'] = [{'name': sk.get('name', 'Cow_rig'), 'joints': list(range(first, first + len(names))),
                         'skeleton': roots[0], 'inverseBindMatrices': acc(ibm, 'MAT4', 5126)}]
        for ni in mesh_nodes:
            doc['nodes'][ni]['skin'] = 0
        doc['scenes'][0]['nodes'] += roots
        anims = []
        for an in model.animations:
            t = np.asarray(an['times'], '<f4')
            tin = acc(t[:, None], 'SCALAR', 5126, minmax=True)
            A = {'name': an['name'], 'samplers': [], 'channels': []}
            if an.get('extras'):
                A['extras'] = an['extras']
            for ji, (T, Q) in an['tracks'].items():
                for channel, vals, kind in [('translation', T, 'VEC3'), ('rotation', Q, 'VEC4')]:
                    if vals is None:
                        continue
                    s = len(A['samplers'])
                    A['samplers'].append({'input': tin, 'output': acc(np.asarray(vals, '<f4'), kind, 5126), 'interpolation': 'LINEAR'})
                    A['channels'].append({'sampler': s, 'target': {'node': first + ji, 'path': channel}})
            anims.append(A)
        if anims:
            doc['animations'] = anims
    if not doc['textures']:
        for k in ['textures', 'images', 'samplers']:
            doc.pop(k)
    if used_ext:
        doc['extensionsUsed'] = sorted(used_ext)
    if model.extras:
        doc['asset']['extras'] = model.extras
    while len(data) % 4:
        data.append(0)
    doc['buffers'] = [{'byteLength': len(data)}]
    js = json.dumps(doc, separators=(',', ':')).encode()
    js += b' ' * ((-len(js)) % 4)
    out = struct.pack('<III', 0x46546C67, 2, 28 + len(js) + len(data))
    out += struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(data), 0x004E4942) + bytes(data)
    Path(path).write_bytes(out)
    return len(out)


def tangents(v, n, uv, f):
    """Per-vertex tangents (xyz + handedness w) for a normal map sampled with `uv`."""
    v = np.asarray(v, np.float64); n = np.asarray(n, np.float64); uv = np.asarray(uv, np.float64)
    e1 = v[f[:, 1]] - v[f[:, 0]]; e2 = v[f[:, 2]] - v[f[:, 0]]
    d1 = uv[f[:, 1]] - uv[f[:, 0]]; d2 = uv[f[:, 2]] - uv[f[:, 0]]
    r = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    r = np.where(np.abs(r) < 1e-14, 1e-14, r)
    t = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / r[:, None]
    b = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) / r[:, None]
    T = np.zeros_like(v); Bt = np.zeros_like(v)
    for k in range(3):
        np.add.at(T, f[:, k], t); np.add.at(Bt, f[:, k], b)
    T = T - n * np.einsum('ij,ij->i', n, T)[:, None]
    bad = np.linalg.norm(T, axis=1) < 1e-12
    alt = np.cross(n, [0, 1, 0]); alt[np.linalg.norm(alt, axis=1) < 1e-6] = [1, 0, 0]
    T[bad] = alt[bad]
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    w = np.where(np.einsum('ij,ij->i', np.cross(n, T), Bt) < 0, -1.0, 1.0)
    return np.hstack([T, w[:, None]]).astype(np.float32)
