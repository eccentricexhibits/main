"""Build The Misanthropic Cow v10: static master, rigged Chicken Dance GLB, review renders, video.

usage: python build_v10.py <v09 review glb> <textures-v09 dir> <out dir> [--quick] [--video]
"""
import sys, json, time, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
import assemble as AS
import anim as AN
import rig as RG
import glb as G
import render as R
import validate as V


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    quick = '--quick' in sys.argv
    src, tex, out = Path(args[0]), Path(args[1]), Path(args[2])
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    model, report = AS.build(src, tex, out, quick=quick)
    print('assembled', report, f'{time.time()-t0:.0f}s', flush=True)
    gloves = {s: [p for p in model.parts if p.get('group') == f'glove_{s}'] for s in 'LR'}
    B = RG.bind_positions(gloves)
    for p in model.parts:
        p['j'], p['w'] = RG.quantize(p.pop('W'))
        nt = model.materials[p['material']].get('normalTexture')
        if nt is not None:
            uvn = p['uv1'] if nt.get('texCoord', 0) == 1 else p['uv']
            p['tangent'] = G.tangents(p['v'], p['n'], uvn, p['f'])
    model.skin = {'name': 'Misanthropic_Cow_v10_rig', 'names': RG.NAMES, 'parents': RG.PARENTS, 'bind': B}
    import clips as CL
    clips = {}
    for Cls in CL.ALL:
        clip = Cls(B)
        # calibrate clap contact from glove thickness along the palm normal
        for side, s in [('L', 1), ('R', -1)]:
            v = np.vstack([p['v'] for p in gloves[side]])
            rel = (v - B[RG.ARM[side]['hand']]) @ np.array([-s, 0, 0.])
            clip.palm_half[side] = float(np.percentile(rel, 99.5))
        times, Gs = clip.bake()
        clips[clip.name] = (clip, times, Gs)
        print('baked', clip.name, Gs.shape, f'{time.time()-t0:.0f}s', flush=True)
    order = CL.ORDER
    model.animations = []
    for nm in order:
        clip, times, Gs = clips[nm]
        model.animations.append({'name': nm, 'times': times, 'tracks': AN.tracks(Gs, RG.PARENTS),
                                 'extras': {'duration_seconds': clip.duration,
                                            'phases': [{'name': a, 'start': b, 'end': c} for a, b, c in clip.phases]}})
    model.extras = {'title': 'The Misanthropic Cow v10', 'units': 'metres', 'up': '+Y', 'forward': '+Z',
                    'left': '+X (character left)'}
    clean_parts = [{k: v for k, v in p.items() if k not in ('group',)} for p in model.parts]
    groups = [p.get('group') for p in model.parts]
    model.parts = clean_parts
    name = 'Misanthropic_Cow_v10' + ('_quick' if quick else '')
    size = G.write(model, out / f'{name}_Animated.glb')
    import copy
    static = copy.copy(model); static.skin = None; static.animations = []
    G.write(static, out / f'{name}.glb')
    print('wrote rigged glb', size, flush=True)
    report['glb_bytes'] = size
    metrics = {'model': report, 'clips': {}}
    store = {}
    for nm in order:
        clip, times, Gs = clips[nm]
        mats = np.stack([AN.skin_matrices(g, B) for g in Gs])
        metrics['clips'][nm] = V.validate(model, groups, B, Gs, mats, times, clip)
        store[nm] = {'times': times, 'mats': mats.astype(np.float32), 'phases': clip.phases, 'duration': clip.duration}
        print('validated', nm, json.dumps(metrics['clips'][nm]), flush=True)
    (out / 'validation_v10.json').write_text(json.dumps(metrics, indent=2))
    import pickle
    pickle.dump({'model': model, 'groups': groups, 'B': B, 'clips': store,
                 'times': store['Chicken Dance']['times'], 'mats': store['Chicken Dance']['mats']}, open(out / 'rigged.pkl', 'wb'))


if __name__ == '__main__':
    main()
