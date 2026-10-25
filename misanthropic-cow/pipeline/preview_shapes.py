"""Fast clay preview of the SDF body for proportion iteration."""
import sys, time
from pathlib import Path
import numpy as np
import sdf as S, design as D, glb as G, render as R

def build(step):
    model = G.Model()
    model.add_material({'name': 'clay', 'pbrMetallicRoughness': {'baseColorFactor': [1, 1, 1, 1], 'roughnessFactor': .9}})
    for name, fn, lo, hi in [('suit', D.suit_sdf, (-.30, .70, -.24), (.30, 1.45, .32)),
                             ('hood', D.hood_sdf, (-.12, 1.32, -.16), (.12, 1.67, .09)),
                             ('tube', D.tube_sdf, D.TUBE_C - [.09, .05, .05], D.TUBE_C + [.09, .05, .05]),
                             ('sleeves', lambda q: np.minimum(D.sleeve_sdf(q, 'L'), D.sleeve_sdf(q, 'R')), (-.45, .75, -.2), (.45, 1.45, .2)),
                             ('leggings', D.legging_sdf, (-.25, .04, -.20), (.25, 1.05, .16)),
                             ('udder', D.udder_sdf, (-.32, .98, -.06), (.32, 1.32, .30))]:
        t = time.time()
        v, f = S.mesh_sdf(fn, lo, hi, step)
        n = S.vertex_normals(v, f)
        model.parts.append({'name': name, 'v': v.astype(np.float32), 'n': n.astype(np.float32), 'f': f.astype(np.int32), 'material': 0, 'uv': None, 'uv1': None, 'ao': None})
        print(name, len(v), len(f), f'{time.time()-t:.1f}s', flush=True)
    return model

if __name__ == '__main__':
    out = Path(sys.argv[1]); step = float(sys.argv[2]) if len(sys.argv) > 2 else .008
    m = build(step)
    extra = sys.argv[3] if len(sys.argv) > 3 else None
    if extra:
        k = G.read(extra)
        for p in k.parts:
            p['material'] = 0
        m.parts += k.parts
    r = R.Renderer(m)
    ims = [r.render(a, 0, (500, 640), center=(0, .86, 0), height=1.85, clay=True) for a in (0, 90, 35)]
    from PIL import Image
    sheet = Image.new('RGB', (1500, 640))
    for i, im in enumerate(ims):
        sheet.paste(im, (500 * i, 0))
    sheet.save(out, quality=90)
