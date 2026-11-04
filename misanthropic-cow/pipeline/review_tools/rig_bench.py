"""Rig test bench for the round 37+ body: build_v10.py in separate, restartable steps, each saving its result.

usage (from pipeline/, REBUILD set as for build_static.py):
  python review_tools/rig_bench.py assemble <dir> [--quick]          model + skin weights + bind -> <dir>/model.pkl
  python review_tools/rig_bench.py bake <dir> [clip,clip,...]         bake clips (default all) -> <dir>/clips/<name>.pkl
  python review_tools/rig_bench.py validate <dir> [clip,...]          validate.py metrics -> <dir>/validation/<name>.json
  python review_tools/rig_bench.py rigged <dir>                       rigged.pkl (as build_v10.py writes it) from the steps
  python review_tools/rig_bench.py glb <dir> <out.glb>                the rigged GLB from model.pkl and the baked clips
  python review_tools/rig_bench.py sheet <dir> <out.jpg> clip,clip [per] [angle]   pose sheet of baked clips
  python review_tools/rig_bench.py pose <dir> <out.jpg> clip:t,clip:t [angle,angle] [clay]   frames without physics

Each step skips work whose output already exists (delete the file to redo it), so a killed run can be restarted."""
import sys, os, json, pickle, time, copy
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rig as RG, anim as AN, glb as G


def _src():
    pipe = Path(__file__).resolve().parent.parent
    RI = Path(os.environ.get('REBUILD', pipe.parent.parent / 'Rebuild_Inputs/project'))
    return RI / 'dist/assets/geometry-v09.glb', RI / 'model-source/textures-v09'


def _safe(name):
    return name.replace(' ', '_').replace('(', '').replace(')', '')


def _dump(obj, path):
    tmp = Path(str(path) + '.tmp')
    with open(tmp, 'wb') as f:
        pickle.dump(obj, f, protocol=4)
    os.replace(tmp, path)


def assemble(d, quick):
    import assemble as AS, gloves as GL
    src, tex = _src()
    t0 = time.time()
    model, report = AS.build(src, tex, d / 'assets_tmp', quick=quick)
    gloves = {s: [p for p in model.parts if p.get('group') == f'glove_{s}'] for s in 'LR'}
    B = RG.bind_positions(gloves)
    palm = {}
    for side in 'LR':
        o, hd, _, pn = GL.hand_frame(side)
        v = np.vstack([p['v'] for p in gloves[side]])
        v = v[(v - o) @ hd > 0]
        palm[side] = float(np.percentile((v - o) @ pn, 99.5))
    # round 45: the sleeve heads widened to fill the corner under the shoulder caps (before tangents and correctives)
    import correctives as CO
    if CO.SLEEVE_HEADS:                                  # round 44B: off by default, as in round 44
        report.update(CO.sleeve_head(model))
    RG.hood_follow_mask(model, [p.get('group') for p in model.parts])     # round 46
    for p in model.parts:
        p['j'], p['w'] = RG.quantize(p.pop('W'))
        nt = model.materials[p['material']].get('normalTexture')
        if nt is not None:
            uvn = p['uv1'] if nt.get('texCoord', 0) == 1 else p['uv']
            p['tangent'] = G.tangents(p['v'], p['n'], uvn, p['f'])
    # round 44: the shoulder correctives (delta mush, socket fill and fillet at key arm poses), from the final weights
    report.update(CO.relax_targets(model, B))
    if CO.SLEEVE_HEADS:
        report.update(CO.sleeve_head_targets(model))      # round 50: the sleeve heads as corrective shapes
    if CO.SHOULDER_TRIM:
        report.update(CO.shoulder_trim(model))            # round 52: the cap's lip drawn in as the arm swings
    report.update(CO.trim_armup(model))                  # round 44B: tenths of a millimetre dropped from ArmUp
    groups = [p.get('group') for p in model.parts]
    model.parts = [{k: v for k, v in p.items() if k not in ('group', 'hoof_w', 'thumb_w', 'toe_w', 'part')} for p in model.parts]
    _dump({'model': model, 'groups': groups, 'B': B, 'palm_half': palm, 'report': report}, d / 'model.pkl')
    print('assembled', report, f'{time.time() - t0:.0f}s', flush=True)


def load(d):
    return pickle.load(open(d / 'model.pkl', 'rb'))


def clip_classes(names=None):
    import clips as CL
    return [c for c in CL.ALL if names is None or c.name in names]


def bake(d, names):
    M = load(d)
    (d / 'clips').mkdir(exist_ok=True)
    for Cls in clip_classes(names):
        out = d / 'clips' / f'{_safe(Cls.name)}.pkl'
        if out.exists():
            continue
        t0 = time.time()
        clip = Cls(M['B'])
        clip.palm_half.update(M['palm_half'])
        times, Gs = clip.bake()
        _dump({'name': clip.name, 'times': times, 'Gs': Gs, 'duration': clip.duration, 'phases': clip.phases}, out)
        print('baked', clip.name, f'{time.time() - t0:.0f}s', flush=True)


def baked(d, names=None):
    import clips as CL
    order = names or CL.ORDER
    return {n: pickle.load(open(d / 'clips' / f'{_safe(n)}.pkl', 'rb')) for n in order
            if (d / 'clips' / f'{_safe(n)}.pkl').exists()}


def validate(d, names):
    import validate as V
    M = load(d)
    (d / 'validation').mkdir(exist_ok=True)
    for Cls in clip_classes(names):
        out = d / 'validation' / f'{_safe(Cls.name)}.json'
        src = d / 'clips' / f'{_safe(Cls.name)}.pkl'
        if out.exists() or not src.exists():
            continue
        t0 = time.time()
        c = pickle.load(open(src, 'rb'))
        clip = Cls(M['B'])
        mats = np.stack([AN.skin_matrices(g, M['B']) for g in c['Gs']])
        m = V.validate(M['model'], M['groups'], M['B'], c['Gs'], mats, c['times'], clip)
        out.write_text(json.dumps(m, indent=1))
        print('validated', clip.name, f'{time.time() - t0:.0f}s', flush=True)


def data_dict(d, names=None):
    M = load(d)
    store = {}
    for n, c in baked(d, names).items():
        store[n] = {'times': c['times'], 'mats': np.stack([AN.skin_matrices(g, M['B']) for g in c['Gs']]).astype(np.float32),
                    'phases': c['phases'], 'duration': c['duration']}
    out = {'model': M['model'], 'groups': M['groups'], 'B': M['B'], 'clips': store}
    if 'Chicken Dance' in store:
        out['times'], out['mats'] = store['Chicken Dance']['times'], store['Chicken Dance']['mats']
    return out


def transition(name):
    """Round 43: how to blend into this clip from another (glTF extras; the viewer does the same).  'phase': a gait
    whose loop starts at the left heel strike, so from another gait (or the same clip's other style) start it at the
    same share of its loop; 'start': start it from its beginning, a standing pose, as every other clip begins and ends."""
    cls = {c.name: c for c in clip_classes()}[name]
    sync = getattr(cls, 'SYNC', 'start')
    return {'sync': sync, 'blend_seconds': .45 if sync == 'phase' else .8,
            'note': 'gaits start at the left heel strike; blend between gaits at the same share of the loop' if sync == 'phase'
            else 'starts and ends standing; blend in from its start, or out at the end of a loop'}


def write_glb(d, out):
    import clips as CL
    M = load(d)
    model = M['model']
    cl = baked(d)
    missing = [n for n in CL.ORDER if n not in cl]
    if missing:
        sys.exit(f'not baked yet: {missing}')
    model.skin = {'name': 'Misanthropic_Cow_v10_rig', 'names': RG.NAMES, 'parents': RG.PARENTS, 'bind': M['B']}
    import correctives as CO
    has_morph = any(p.get('morph') is not None for p in model.parts)
    model.animations = [{'name': n, 'times': cl[n]['times'], 'tracks': AN.tracks(cl[n]['Gs'], RG.PARENTS),
                         'morph_weights': CO.track([AN.skin_matrices(g, M['B']) for g in cl[n]['Gs']]) if has_morph else None,
                         'extras': {'duration_seconds': cl[n]['duration'],
                                    'phases': [{'name': a, 'start': b, 'end': c} for a, b, c in cl[n]['phases']],
                                    'transition': transition(n)}}
                        for n in CL.ORDER]
    model.extras = {'title': 'The Misanthropic Cow v10', 'units': 'metres', 'up': '+Y', 'forward': '+Z',
                    'left': '+X (character left)', **({'morph_names': CO.NAMES} if has_morph else {})}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    print('wrote', out, G.write(model, out))


def pose_sheet(d, out, specs, angles, clay):
    """Frames straight from the clips' pose solver (no springs, no swivel): fast checks of weights and poses."""
    import render_dance as RD
    from PIL import Image
    M = load(d)
    cls = {c.name: c for c in clip_classes()}
    w, h = 420, 560
    sheet = Image.new('RGB', (w * len(specs), h * len(angles)), '#161b22')
    for i, sp in enumerate(specs):
        name, t = sp.rsplit(':', 1)
        clip = cls[name](M['B'])
        mats = AN.skin_matrices(clip.pose(float(t)), M['B'])
        for j, a in enumerate(angles):
            im = RD.frame_image(M['model'], mats, a, 4, (w, h), center=(0, .93, .03), height=2.05, clay=clay,
                                title=name if j == 0 else None, sub=f't={float(t):.2f}s')
            sheet.paste(im, (w * i, h * j))
    sheet.save(out, quality=88)


if __name__ == '__main__':
    cmd, d = sys.argv[1], Path(sys.argv[2])
    d.mkdir(parents=True, exist_ok=True)
    rest = [a for a in sys.argv[3:] if not a.startswith('--')]
    names = lambda i: rest[i].split(',') if len(rest) > i else None
    if cmd == 'assemble':
        assemble(d, '--quick' in sys.argv)
    elif cmd == 'bake':
        bake(d, names(0))
    elif cmd == 'validate':
        validate(d, names(0))
    elif cmd == 'rigged':
        _dump(data_dict(d), d / 'rigged.pkl')
    elif cmd == 'glb':
        write_glb(d, Path(rest[0]))
    elif cmd == 'sheet':
        import render_dance as RD
        RD.clip_sheet(data_dict(d, names(1)), rest[0], names(1), per=int(rest[2]) if len(rest) > 2 else 5)
    elif cmd == 'pose':
        pose_sheet(d, rest[0], rest[1].split(','), [float(a) for a in (rest[2].split(',') if len(rest) > 2 else ['-28'])],
                   'clay' in rest[3:])
