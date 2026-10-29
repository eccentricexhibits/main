"""One-off conversion: the owner's finished glove model (Glove_pair.glb, v4 of the glove project: the
"slipper look" with the terry smoothed at 20 mm) into the asset gloves.py puts on the hands
(assets/gloves_hoof.glb + gloves_hoof.json).

The gloves are the real prop: a cream looped-terry mitten with a separate terry thumb, and the four
fingers in two compartments, each capped by a hard black painted-card toe (satin black with grey
drag strokes and a thin beaded rim); together the toes are a cloven hoof.  The file holds three meshes
per glove, 100k triangles in all, sharing one baked 4K atlas (colour, roughness, tangent normal):
  Glove_Palm                palm, thumb and closed cuff
  Glove_Toe_IndexMiddle     finger compartment + toe cap on the thumb side
  Glove_Toe_RingLittle      finger compartment + toe cap on the little-finger side
The toes are children of the palm, pivoting on the middle/ring finger web at mid-thickness, 20 mm
below the hoof base: they part like a Vulcan salute (spread) and curl toward the palm.  The right
glove is the left one mirrored.

This script keeps the model at its real size (24.7 cm cuff to hoof tip) and moves the left glove into
the hand frame gloves.py builds in (metres):
  u  along the hand from the wrist joint toward the hoof tip   (glTF +y, shifted by U0)
  a  across the palm, toward the thumb                         (glTF +x)
  w  out of the palm (the palm faces the body at rest)         (glTF -z: the back of the hand is +z)
U0 puts the hoof base (the paint edge) where the previous gloves' was, 10.3 cm past the wrist; the
cuff then sits 5.6 cm inside the sleeve, 8-18 mm clear of the sleeve opening all round, and the hoof
tip lands 19.1 cm past the wrist.  Both hands use these coordinates (the right hand's frame is the
mirror image of the left's), so only the triangle winding is flipped for the right glove.

The glove project baked its ambient occlusion into the colour map (multiplied in at 50 %, in linear
light: colour x (0.5 + 0.5 AO)).  The model carries no lighting, so when that AO map is given (the live
material's textures/ao_2048.jpg, in the same UV atlas) it is divided back out.

usage: python hoof_gloves.py <Glove_pair.glb> ../assets/gloves_hoof.glb [ao_2048.jpg]
"""
import sys
import json
from pathlib import Path
import io
import numpy as np
from PIL import Image
from scipy import ndimage
import glb as G
import textures as T

U0 = -.056               # u of the glove's cuff bottom (glTF y = 0)
NAMES = {'Glove_L_Palm': 'palm', 'Glove_L_Toe_IndexMiddle': 'toe_index_middle', 'Glove_L_Toe_RingLittle': 'toe_ring_little'}


def to_hand(x):
    """glTF (x, y, z) of the left glove -> hand frame (u, a, w)."""
    return np.stack([x[:, 1], x[:, 0], -x[:, 2]], 1)


def remove_ao(jpeg, ao_path):
    """Divide the baked AO (multiplied in at 0.5, in linear light) back out of the colour map."""
    col = np.asarray(Image.open(io.BytesIO(jpeg)).convert('RGB')).astype(float) / 255
    ao = np.asarray(Image.open(ao_path).convert('L')).astype(float) / 255
    # texels outside the UV islands are 0 in the AO map: fill them from the nearest island texel first,
    # so the upscaled map doesn't fall toward 0 along the island borders
    empty = ao < .02
    idx = ndimage.distance_transform_edt(empty, return_distances=False, return_indices=True)
    ao = ao[tuple(idx)]
    ao = np.asarray(Image.fromarray((ao * 65535).astype(np.uint16)).resize(col.shape[1::-1], Image.BILINEAR)).astype(float) / 65535
    lin = np.where(col <= .04045, col / 12.92, ((col + .055) / 1.055) ** 2.4)
    lin = np.clip(lin / (.5 + .5 * ao)[..., None], 0, 1)
    srgb = np.where(lin <= .0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - .055)
    print('AO removed: mean brightness', col.mean().round(3), '->', srgb.mean().round(3))
    return T.to_jpeg(srgb, 92)


def main(src, out, ao_path=None):
    doc, blob = G._read(src)
    m = G.read(src)                                  # materials and images, texture indices resolved
    o = G.Model()
    o.images = list(m.images)
    mat = json.loads(json.dumps(m.materials[0]))
    if ao_path:
        ci = mat['pbrMetallicRoughness']['baseColorTexture']['image']
        o.images[ci] = (remove_ao(o.images[ci][0], ao_path), 'image/jpeg')
    mat['name'] = 'Glove_terry_and_painted_hoof'
    mi = o.add_material(mat)
    pivot = None
    for node in doc['nodes']:
        if node.get('name') not in NAMES:
            continue
        prim = doc['meshes'][node['mesh']]['primitives'][0]
        at = prim['attributes']
        v = G._accessor(doc, blob, at['POSITION']).astype(float)
        n = G._accessor(doc, blob, at['NORMAL']).astype(float)
        uv = G._accessor(doc, blob, at['TEXCOORD_0']).astype(np.float32)
        f = G._accessor(doc, blob, prim['indices']).astype(np.int64).reshape(-1, 3)
        if node['name'] != 'Glove_L_Palm':
            t = np.array(node['translation'])            # the toes hang off the palm at the web pivot
            v = v + t
            pivot = to_hand(t[None])[0] + [U0, 0, 0]
        q = to_hand(v); q[:, 0] += U0
        o.parts.append({'name': f'Glove_hoof_{NAMES[node["name"]]}', 'v': q.astype(np.float32),
                        'n': to_hand(n).astype(np.float32), 'uv': uv, 'uv1': None, 'ao': None,
                        'f': f.astype(np.int32), 'material': mi})
        print(node['name'], 'triangles', len(f), 'u', q[:, 0].min().round(3), q[:, 0].max().round(3),
              'a', q[:, 1].min().round(3), q[:, 1].max().round(3), 'w', q[:, 2].min().round(3), q[:, 2].max().round(3))
    G.write(o, out)
    meta = {'frame': 'u along the hand (wrist joint at 0), a toward the thumb, w out of the palm; metres; left glove',
            'source': Path(src).name, 'cuff_u': U0, 'toe_pivot': [round(float(x), 5) for x in pivot],
            'hoof_base_u': round(U0 + .1588, 4), 'baked_ao_removed': bool(ao_path)}
    Path(out).with_suffix('.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('pivot', meta['toe_pivot'])


if __name__ == '__main__':
    main(*sys.argv[1:4])
