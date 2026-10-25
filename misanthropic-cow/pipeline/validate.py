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


def validate(model, groups, B, Gs, mats, times, dance):
    m = {}
    m['joints'] = len(RG.NAMES)
    m['frames'] = len(times)
    m['fps'] = AN.FPS
    m['duration_seconds'] = AN.DURATION
    m['triangles'] = int(sum(len(p['f']) for p in model.parts))
    m['weights_sum_255'] = bool(all(np.all(p['w'].astype(int).sum(1) == 255) for p in model.parts))
    m['joint_indices_valid'] = bool(all(p['j'].max() < len(RG.NAMES) for p in model.parts))
    m['loop_matrix_max_error'] = float(np.abs(mats[0] - mats[-1]).max())
    m['planted_feet_max_drift_m'] = float(max(np.abs(Gs[:, RG.LEG[s]['foot'], :3, 3] - B[RG.LEG[s]['foot']]).max() for s in 'LR'))
    suit_idx = [i for i, g in enumerate(groups) if g == 'suit' and model.parts[i]['name'].startswith('Suit_') and 'strand' not in model.parts[i]['name']]
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
    stretch_torso, stretch_arm, sleeve_gap, overlap, pen, clap = [], [], [], [], {k: 0. for k in AN.PHASES}, []
    v_rest = {i: model.parts[i]['v'] for i in suit_idx}
    clap_times = [9.375, 10.125, 10.875, 11.625]
    clap_frames = [int(round(t * AN.FPS)) for t in clap_times]
    for k in range(0, len(times), 3):
        P = posed(model, mats[k])
        st = tri_stretch(v_rest[torso], P[torso]['v'], model.parts[torso]['f'])
        stretch_torso.append(float(np.percentile(st, 99.9)))
        stretch_arm.append(float(max(np.percentile(tri_stretch(v_rest[sleeves[s]], P[sleeves[s]]['v'], model.parts[sleeves[s]]['f']), 99.9) for s in 'LR')))
        phase = AN.PHASES[min(3, int((times[k] % AN.DURATION) // 3))]
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
            pen[phase] = max(pen[phase], float(np.percentile(depth, 99.5)))
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
    arm_clip, teat_clip = {k: [] for k in AN.PHASES}, {k: [] for k in AN.PHASES}
    for k in range(0, len(times), 2):
        P = posed(model, mats[k])
        G = Gs[k]
        phase = AN.PHASES[min(3, int((times[k] % AN.DURATION) // 3))]
        pts = np.vstack([P[sleeves[s]]['v'][arm_pts[s]] for s in 'LR'] + [P[i]['v'] for s in 'LR' for i in glove_idx[s]])
        arm_clip[phase].append(float(np.percentile(np.maximum(0, -dance.clearance(G, pts)), 99.5)))
        tv = np.vstack([P[i]['v'][teat_v[i]] for i in udder_idx])
        qb = (tv - G[RG.SPINE, :3, 3]) @ G[RG.SPINE, :3, :3] + B[RG.SPINE]
        teat_clip[phase].append(float(np.percentile(np.maximum(0, -D.torso_sdf(qb)), 99.5)))
    m['arm_into_cups_or_torso_p995_m'] = {k: max(v) for k, v in arm_clip.items()}
    m['teats_into_belly_p995_m'] = {k: max(v) for k, v in teat_clip.items()}
    m['suit_torso_edge_stretch_p999_max'] = max(stretch_torso)
    m['sleeve_edge_stretch_p999_max'] = max(stretch_arm)
    m['sleeve_end_to_glove_gap_p95_rest_m'] = sleeve_gap[0]
    m['sleeve_end_to_glove_gap_p95_max_during_dance_m'] = max(sleeve_gap)
    m['glove_into_body_penetration_p995_m'] = pen
    m['clap_min_glove_distance_m'] = clap
    return m
