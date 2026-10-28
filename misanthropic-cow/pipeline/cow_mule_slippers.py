"""One-off conversion: the owner's finished slipper model (Cow_Slippers_pair.glb, the "v3 fabric"
version from the slipper project) into the asset assets.py places on the feet
(assets/slippers_cow_mule.glb).

The slippers are the real handmade prop: open-back mules with a white plush muzzle (stitched smile,
magenta nostrils), bead eyes, stubby tan horns, floppy black-and-magenta ears with pearls, a cream
mop-chenille head with black patches, a black chenille fringe round the sole and a flat black plush
footbed exposed for the rear ~42 %.  Their file holds one 150k-triangle mesh with 4K baked colour,
roughness and normal maps, used twice: node A, and node B mirrored left to right.

This script:
  1. scales the model to metres (1 unit = 27.5 cm, as the slipper project's handoff states: a 27 cm
     slipper);
  2. moves it into the slipper frame assets.py and anim.py expect: the ankle axis at the origin
     (centred across the footbed, ANKLE_FROM_HEEL in front of the heel), the sole at y = 0, the toe
     along +z;
  3. makes the left slipper from node A (it stands on the wearer's left in the file) and the right
     from the mirrored node B, with its triangles' winding flipped so it still faces outward;
  4. keeps the baked maps as they are, under a material named Slipper_ so the web copies cap them.

usage: python cow_mule_slippers.py <Cow_Slippers_pair.glb> ../assets/slippers_cow_mule.glb
"""
import sys
import json
import numpy as np
import glb as G

SCALE = .275              # model units -> metres
ANKLE_FROM_HEEL = .068    # the ankle axis this far in front of the back of the slipper


def main(src, out):
    m = G.read(src)
    p = m.parts[0]                                  # both nodes share this mesh
    v = p['v'].astype(float) * SCALE
    v[:, 1] -= v[:, 1].min()
    v[:, 0] -= .5 * (v[:, 0].min() + v[:, 0].max())
    v[:, 2] -= v[:, 2].min() + ANKLE_FROM_HEEL
    o = G.Model()
    o.images = list(m.images)
    mat = json.loads(json.dumps(m.materials[p['material']]))
    mat['name'] = 'Slipper_cow_mule_fabric'
    mi = o.add_material(mat)
    f = p['f'].astype(np.int64)
    for side, mirror in (('L', False), ('R', True)):
        k = np.array([-1., 1, 1]) if mirror else np.ones(3)
        vs, ns = v * k, p['n'].astype(float) * k      # the model's own normals, mirrored with it
        fs = f[:, ::-1] if mirror else f
        o.parts.append({'name': f'Slipper_{side}_cow_mule', 'v': vs.astype(np.float32),
                        'n': ns.astype(np.float32), 'uv': p['uv'].astype(np.float32),
                        'uv1': None, 'ao': None, 'f': fs.astype(np.int32), 'material': mi})
        print(side, 'triangles', len(fs), 'bounds', vs.min(0).round(3), vs.max(0).round(3))
    G.write(o, out)


if __name__ == '__main__':
    main(*sys.argv[1:3])
