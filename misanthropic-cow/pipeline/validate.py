"""Numerical checks for the rigged v10 cow and its Chicken Dance."""
import numpy as np
from scipy.spatial import cKDTree
import render as R
import rig as RG
import anim as AN


def posed(model, mats_frame):
    return R.skin_parts(model, mats_frame)


def tri_stretch(v0, v1, f):
    e0 = np.stack([np.linalg.norm(v0[f[:, a]] - v0[f[:, b]], axis=1) for a, b in [(0, 1), (1, 2), (2, 0)]], 1)
    e1 = np.stack([np.linalg.norm(v1[f[:, a]] - v1[f[:, b]], axis=1) for a, b in [(0, 1), (1, 2), (2, 0)]], 1)
    return (e1 / np.maximum(e0, 1e-9)).max(1)


def phase_of(clip, t):
    t = t % clip.duration
    for name, a, b in clip.phases:
        if a <= t < b:
            return name
    return clip.phases[-1][0]


def validate(model, groups, B, Gs, mats, times, dance):
    m = {}
    m['joints'] = len(RG.NAMES)
    m['frames'] = len(times)
    m['fps'] = AN.FPS
    m['duration_seconds'] = dance.duration
    PH = [ph[0] for ph in dance.phases]
    m['triangles'] = int(sum(len(p['f']) for p in model.parts))
    m['weights_sum_255'] = bool(all(np.all(p['w'].astype(int).sum(1) == 255) for p in model.parts))
    m['joint_indices_valid'] = bool(all(p['j'].max() < len(RG.NAMES) for p in model.parts))
    m['loop_matrix_max_error'] = float(np.abs(mats[0] - mats[-1]).max())
    feet_move = not np.allclose(Gs[:, RG.LEG['L']['foot'], :3, 3], B[RG.LEG['L']['foot']], atol=1e-4)
    if not feet_move:
        m['planted_feet_max_drift_m'] = float(max(np.abs(Gs[:, RG.LEG[s]['foot'], :3, 3] - B[RG.LEG[s]['foot']]).max() for s in 'LR'))
    suit_idx = [i for i, g in enumerate(groups) if g == 'suit' and model.parts[i]['name'].startswith(('Suit_', 'Hood_')) and 'strand' not in model.parts[i]['name'] and 'tuft' not in model.parts[i]['name']]
    glove_idx = {s: [i for i, g in enumerate(groups) if g == f'glove_{s}'] for s in 'LR'}
    torso = [i for i in suit_idx if 'torso' in model.parts[i]['name']][0]
    sleeves = {s: [i for i in suit_idx if f'sleeve_{s}' in model.parts[i]['name']][0] for s in 'LR'}
    # sleeve end ring and glove cuff top
    rings, cuffs = {}, {}
    for side, s in [('L', 1), ('R', -1)]:
        a = RG.ARM[side]
        d = B[a['hand']] - B[a['fore']]; d /= np.linalg.norm(d)
        sv = model.parts[sleeves[side]]['v']
        t = (sv - B[a['hand']]) @ d
        rings[side] = np.nonzero(t > -.012)[0]
        cuffs[side] = [(i, None) for i in glove_idx[side] if 'hoof_cap' not in model.parts[i]['name']]
    stretch_torso, stretch_arm, stretch_leg, sleeve_gap, overlap, pen, clap = [], [], [], [], [], {k: 0. for k in PH}, []
    legs = [i for i, p in enumerate(model.parts) if p['name'].startswith('Leggings_')]
    sole = []
    foot_idx = [i for i, g in enumerate(groups) if g and g.startswith('foot')]
    v_rest = {i: model.parts[i]['v'] for i in suit_idx}
    clap_times = [c * dance.duration / 12.0 for c in (9.375, 10.125, 10.875, 11.625)]   # alt plays slower
    clap_frames = [int(round(t * AN.FPS)) for t in clap_times]
    for k in range(0, len(times), 3):
        P = posed(model, mats[k])
        st = tri_stretch(v_rest[torso], P[torso]['v'], model.parts[torso]['f'])
        stretch_torso.append(float(np.percentile(st, 99.9)))
        stretch_arm.append(float(max(np.percentile(tri_stretch(v_rest[sleeves[s]], P[sleeves[s]]['v'], model.parts[sleeves[s]]['f']), 99.9) for s in 'LR')))
        stretch_leg.append(float(max(np.percentile(tri_stretch(model.parts[i]['v'], P[i]['v'], model.parts[i]['f']), 99.9) for i in legs)))
        phase = phase_of(dance, times[k])
        sole.append(float(min(P[i]['v'][:, 1].min() for i in foot_idx)))
        for side in 'LR':
            # the glove palm sits inside its own sleeve by design, so exclude that sleeve
            others = [i for i in suit_idx if i != sleeves[side]]
            body = np.vstack([P[i]['v'] for i in others] + [P[i]['v'] for i, g in enumerate(groups) if g == 'udder'])
            bn = np.vstack([P[i]['n'] for i in others] + [P[i]['n'] for i, g in enumerate(groups) if g == 'udder'])
            tree = cKDTree(body)
            ring = P[sleeves[side]]['v'][rings[side]]
            cuff = np.vstack([P[i]['v'] for i, _ in cuffs[side]])
            dist = cKDTree(cuff).query(ring)[0]
            sleeve_gap.append(float(np.percentile(dist, 95)))
            gv = np.vstack([P[i]['v'] for i in glove_idx[side]])
            dd, ii = tree.query(gv)
            depth = -np.einsum('ij,ij->i', gv - body[ii], bn[ii])
            depth[dd > .04] = 0     # behind the nearest vertex's plane but far from it is not contact
            pen[phase] = max(pen[phase], float(np.percentile(depth, 99.5)))
    if dance.name.startswith('Chicken Dance'):
        for k in clap_frames:
            P = posed(model, mats[k])
            gl = np.vstack([P[i]['v'] for i in glove_idx['L']]); gr = np.vstack([P[i]['v'] for i in glove_idx['R']])
            clap.append(float(cKDTree(gl).query(gr)[0].min()))
    # clipping: arm surfaces (away from the sleeve head) and gloves into the cups/torso; teats into the belly
    import design as D
    arm_pts = {}
    for side, s in [('L', 1), ('R', -1)]:
        sh = D.arm_points(s)[0]
        el = D.arm_points(s)[1]; du = (el - sh) / np.linalg.norm(el - sh)
        sv = model.parts[sleeves[side]]['v']
        arm_pts[side] = np.nonzero((sv - sh) @ du > .13)[0]
    udder_idx = [i for i, g in enumerate(groups) if g == 'udder']
    teat_v = {}
    for i in udder_idx:
        p = model.parts[i]
        tj = set(RG.TEAT.values())
        isteat = np.isin(p['j'], list(tj)) & (p['w'] > 128)
        teat_v[i] = np.nonzero(isteat.any(1))[0]
    arm_clip, teat_clip = {k: [] for k in PH}, {k: [] for k in PH}
    for k in range(0, len(times), 2):
        P = posed(model, mats[k])
        G = Gs[k]
        phase = phase_of(dance, times[k])
        pts = np.vstack([P[sleeves[s]]['v'][arm_pts[s]] for s in 'LR'] + [P[i]['v'] for s in 'LR' for i in glove_idx[s]])
        arm_clip[phase].append(float(np.percentile(np.maximum(0, -dance.clearance(G, pts)), 99.5)))
        tv = np.vstack([P[i]['v'][teat_v[i]] for i in udder_idx])
        qb = (tv - G[RG.SPINE, :3, 3]) @ G[RG.SPINE, :3, :3] + B[RG.SPINE]
        teat_clip[phase].append(float(np.percentile(np.maximum(0, -D.torso_sdf(qb)), 99.5)))
    m['arm_into_cups_or_torso_p995_m'] = {k: max(v) for k, v in arm_clip.items()}
    m['teats_into_belly_p995_m'] = {k: max(v) for k, v in teat_clip.items()}
    m['suit_torso_edge_stretch_p999_max'] = max(stretch_torso)
    m['sleeve_edge_stretch_p999_max'] = max(stretch_arm)
    m['leggings_edge_stretch_p999_max'] = max(stretch_leg)
    m['sleeve_end_to_glove_gap_p95_rest_m'] = sleeve_gap[0]
    m['sleeve_end_to_glove_gap_p95_max_during_dance_m'] = max(sleeve_gap)
    m['glove_into_body_penetration_p995_m'] = pen
    if clap:
        m['clap_min_glove_distance_m'] = clap
    m['lowest_slipper_point_m'] = min(sole)
    m.update(tail_metrics(model, groups, B, Gs, mats))
    m.update(leg_body_metrics(model, groups, mats))
    return m


def tail_metrics(model, groups, B, Gs, mats):
    """Tail cord: lowest point over the clip (floor is y = 0) and deepest dip of a cord bone into
    the leg and slipper capsules the rope collides with."""
    import tail as TL
    tail_idx = [i for i, g in enumerate(groups) if g == 'tail']
    if not tail_idx:
        return {}
    low, into = 1e3, 0.
    for k in range(0, len(Gs), 2):
        P = posed(model, mats[k])
        low = min(low, min(float(P[i]['v'][:, 1].min()) for i in tail_idx))
        x = Gs[k][RG.TAIL, :3, 3]
        for a, b, ra, rb in TL.body_capsules(Gs[k], B, RG):
            ab = b - a
            t = np.clip(((x - a) @ ab) / (ab @ ab), 0, 1)
            d = np.linalg.norm(x - (a + t[:, None] * ab), axis=1) - (ra + (rb - ra) * t)
            into = max(into, float(np.max(-d)))
    return {'tail_lowest_point_m': low, 'tail_cord_into_legs_max_m': max(0., into)}


def _depth_into(src, dst_v, dst_n, lim=.08):
    """How far each source point lies behind the surface of its nearest destination vertex."""
    dd, ii = cKDTree(dst_v).query(src, distance_upper_bound=lim)
    near = np.isfinite(dd)
    dep = np.zeros(len(src))
    dep[near] = -np.einsum('ij,ij->i', src[near] - dst_v[ii[near]], dst_n[ii[near]])
    return dep


def leg_body_metrics(model, groups, mats, step=3):
    """Leggings and briefs against the suit torso and cups, both ways (sitting, crouching and high
    kicks are where a thigh can pass into the belly or hem). What already overlaps at rest by design
    (the tops of the leggings and briefs under the suit) is left out."""
    names = [p['name'] for p in model.parts]
    body = [i for i, n in enumerate(names) if n.startswith('Suit_torso') or groups[i] == 'udder']
    legs = [i for i, n in enumerate(names) if n.startswith(('Leggings_', 'Panties'))]
    if not body or not legs:
        return {}
    # pose only the parts measured (the full model is mostly shag strands)
    sub = type(model)(); sub.parts = [model.parts[i] for i in body + legs]
    body, legs = list(range(len(body))), list(range(len(body), len(body) + len(legs)))
    stack = lambda P, ix, k: np.vstack([P[i][k] for i in ix])
    rest = sub.parts
    mask_b = _depth_into(stack(rest, body, 'v'), stack(rest, legs, 'v'), stack(rest, legs, 'n')) > -.002
    mask_l = _depth_into(stack(rest, legs, 'v'), stack(rest, body, 'v'), stack(rest, body, 'n')) > -.002
    b2l, l2b = 0., 0.
    for k in range(0, len(mats), step):
        P = posed(sub, mats[k])
        d = _depth_into(stack(P, body, 'v'), stack(P, legs, 'v'), stack(P, legs, 'n')); d[mask_b] = 0
        b2l = max(b2l, float(np.percentile(d, 99.5)))
        d = _depth_into(stack(P, legs, 'v'), stack(P, body, 'v'), stack(P, body, 'n')); d[mask_l] = 0
        l2b = max(l2b, float(np.percentile(d, 99.5)))
    return {'body_into_legs_p995_max_m': b2l, 'legs_into_body_p995_max_m': l2b}
