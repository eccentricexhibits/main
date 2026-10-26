"""Downscale textures inside a GLB without touching anything else (skin, animations, tangents and
extras are carried over byte for byte), for the web copies that must stay under the viewer host's
size limit.

usage: python web_textures.py in.glb out.glb MAX_PX [material-name prefix ...]
With prefixes, only images used by materials whose names start with one of them are downscaled;
without, every image larger than MAX_PX is.
"""
import io
import json
import struct
import sys
from PIL import Image


def read(path):
    b = open(path, 'rb').read()
    n = struct.unpack('<I', b[12:16])[0]
    doc = json.loads(b[20:20 + n])
    o = 20 + n
    blen = struct.unpack('<I', b[o:o + 4])[0]
    return doc, bytearray(b[o + 8:o + 8 + blen])


def write(path, doc, blob):
    js = json.dumps(doc, separators=(',', ':')).encode()
    js += b' ' * (-len(js) % 4)
    blob = bytes(blob) + b'\0' * (-len(blob) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(blob), 0x004E4942)); f.write(blob)


def images_of(doc, prefixes):
    tex = doc.get('textures', [])
    out = set()
    for mat in doc.get('materials', []):
        if prefixes and not mat.get('name', '').startswith(tuple(prefixes)):
            continue
        refs = list(mat.get('pbrMetallicRoughness', {}).values()) + [mat.get(k) for k in ('normalTexture', 'occlusionTexture', 'emissiveTexture')]
        for ext in mat.get('extensions', {}).values():
            refs += list(ext.values())
        for r in refs:
            if isinstance(r, dict) and 'index' in r:
                out.add(tex[r['index']]['source'])
    return out


def main(src, dst, max_px, *prefixes):
    max_px = int(max_px)
    doc, blob = read(src)
    pick = images_of(doc, prefixes) if prefixes else set(range(len(doc.get('images', []))))
    views = doc['bufferViews']
    new = {}
    for i in pick:
        im = doc['images'][i]
        bv = views[im['bufferView']]
        o = bv.get('byteOffset', 0)
        data = bytes(blob[o:o + bv['byteLength']])
        pic = Image.open(io.BytesIO(data))
        if max(pic.size) <= max_px:
            continue
        png = im.get('mimeType') == 'image/png'
        pic = pic.convert('RGBA' if png else 'RGB')
        pic.thumbnail((max_px, max_px), Image.LANCZOS)
        out = io.BytesIO()
        pic.save(out, 'PNG' if png else 'JPEG', **({} if png else {'quality': 88}))
        new[im['bufferView']] = out.getvalue()
    # rebuild the binary chunk view by view (4-byte aligned), keeping every other byte as it was
    nb = bytearray()
    for k, bv in enumerate(views):
        o = bv.get('byteOffset', 0)
        data = new.get(k, bytes(blob[o:o + bv['byteLength']]))
        nb += b'\0' * (-len(nb) % 4)
        bv['byteOffset'] = len(nb)
        bv['byteLength'] = len(data)
        nb += data
    doc['buffers'][0]['byteLength'] = len(nb) + (-len(nb) % 4)
    write(dst, doc, nb)
    print(f'{len(new)} images downscaled to {max_px}px; {len(nb) / 1e6:.1f} MB binary')


if __name__ == '__main__':
    main(*sys.argv[1:])
