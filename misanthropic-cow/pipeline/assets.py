"""Kept v09 assets (scanned mask, horns, wires, gloves, slippers, rear bow), refitted to the v10 body."""
import json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
import design as D
import glb as G

MASK_KEEP = ['Preserved_mask__Scanned_Face', 'Preserved_mask__Lower_Jaw_Photo_Right',
             'Preserved_mask__Lower_Jaw_Photo_Left_Approximate', 'Preserved_mask__Right_Horn',
             'Preserved_mask__Left_Horn', 'Preserved_mask__Preserved_Exposed_Wires']
NEW_NAMES = {
    'Preserved_mask__Scanned_Face': 'Mask_scanned_face',
    'Preserved_mask__Lower_Jaw_Photo_Right': 'Mask_lower_jaw_left_side',            # +X = character's left
    'Preserved_mask__Lower_Jaw_Photo_Left_Approximate': 'Mask_lower_jaw_right_side',
    'Preserved_mask__Right_Horn': 'Horn_left_complete',
    'Preserved_mask__Left_Horn': 'Horn_right_broken',
    'Preserved_mask__Preserved_Exposed_Wires': 'Horn_right_exposed_wire',
}
GLOVE_SIZE = .93
SLIPPER_SIZE = .90


def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = a @ b
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3)
    return Rotation.from_rotvec(v / np.linalg.norm(v) * np.arccos(np.clip(c, -1, 1))).as_matrix()


def glove_frame(src, prefix):
    cuff = np.vstack([p['v'] for p in src.parts if p['name'].startswith(prefix) and 'cuff' in p['name']])
    top = cuff[cuff[:, 1] > cuff[:, 1].max() - .012].mean(0)
    caps = np.vstack([p['v'] for p in src.parts if p['name'].startswith(prefix) and 'hoof_cap' in p['name']])
    tip = caps.mean(0)
    return top, (tip - top) / np.linalg.norm(tip - top)


def glove_transform(src, old_prefix, side):
    """Map an old glove so its cuff top sits 3.5 cm up the forearm, overlapping the sleeve end."""
    top, axis = glove_frame(src, old_prefix)
    s = 1 if side == 'L' else -1
    el, wr = D.J[f'Forearm_{side}'], D.J[f'Hand_{side}']
    d = (wr - el) / np.linalg.norm(wr - el)
    Rm = rot_between(axis, d)
    anchor = wr - .035 * d
    return lambda v: (v - top) @ Rm.T * GLOVE_SIZE + anchor, Rm


def close_wire_gaps(v, f, touch=.002, reach=.012, bend=.015):
    """Round 45: the exposed wires on the broken horn are five separate tubes; four meet end to end in pairs at the
    top to make two loops, but the fifth stopped 7 mm short of the junction it belongs to and showed as a gap (the
    owner: "a small gap in the left wire horn").  Each upper end of a tube that touches no other tube is bent over its
    last `bend` to meet the nearest junction (or end) within `reach`."""
    from scipy import sparse
    from scipy.sparse.csgraph import connected_components
    v = np.asarray(v, float).copy()
    key = np.round(v / 1e-5).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.ravel()
    fw = inv[np.asarray(f)]; n = len(first)
    A = sparse.coo_matrix((np.ones(fw.size), (fw[:, [0, 1, 2]].ravel(), fw[:, [1, 2, 0]].ravel())), shape=(n, n))
    nc, lab = connected_components(A, directed=False)
    lab = lab[inv]
    tubes = []
    for c in range(nc):
        idx = np.nonzero(lab == c)[0]; pts = v[idx]; ctr = pts.mean(0)
        ax = np.linalg.svd(pts - ctr, full_matrices=False)[2][0]
        t = (pts - ctr) @ ax
        ends = [pts[t > t.max() - .002].mean(0), pts[t < t.min() + .002].mean(0)]
        up = 0 if ends[0][1] > ends[1][1] else 1                # the upper end, out of the horn
        tubes.append(dict(idx=idx, t=t if up == 0 else -t, end=ends[up]))
    tops = np.array([tb['end'] for tb in tubes])
    for k, tb in enumerate(tubes):
        d = np.linalg.norm(tops - tb['end'], axis=1); d[k] = np.inf
        if d.min() < touch or d.min() > reach:
            continue
        j = int(d.argmin())
        dj = np.linalg.norm(tops - tops[j], axis=1); dj[[j, k]] = np.inf
        target = .5 * (tops[j] + tops[int(dj.argmin())]) if dj.min() < touch else tops[j]
        u = np.clip((tb['t'] - (tb['t'].max() - bend)) / bend, 0, 1)
        v[tb['idx']] += (u * u * (3 - 2 * u))[:, None] * (target - tb['end'])
    return v


def wire_uv(v, f, v_unit=.03, step=.001):
    """Round 47: UVs for the exposed wires (v09 left them all at one point): u round each wire, v along it from its
    lower end, one unit every v_unit m.  Along: the distance over the surface from the lower end's cap (Dijkstra on
    the mesh's edges); round: the angle about a centreline (the mean of each step of that distance), in a frame
    carried along it without twist.  Faces across the u seam get duplicated vertices.  Returns (uv, f, src): the
    new faces and, per output vertex, the input vertex it copies."""
    from scipy import sparse
    from scipy.sparse.csgraph import connected_components, dijkstra
    v = np.asarray(v, float); f = np.asarray(f)
    key = np.round(v / 1e-5).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.ravel()
    fw = inv[f]; n = len(first); vw = v[first]
    a, b = fw[:, [0, 1, 2]].ravel(), fw[:, [1, 2, 0]].ravel()
    L = sparse.coo_matrix((np.linalg.norm(vw[a] - vw[b], axis=1) + 1e-9, (a, b)), shape=(n, n)).tocsr()
    nc, lab = connected_components(L, directed=False)
    U = np.zeros(n); V = np.zeros(n)
    for c in range(nc):
        idx = np.nonzero(lab == c)[0]; pts = vw[idx]; ctr = pts.mean(0)
        ax = np.linalg.svd(pts - ctr, full_matrices=False)[2][0]
        t = (pts - ctr) @ ax
        if pts[t > t.max() - .002, 1].mean() < pts[t < t.min() + .002, 1].mean():
            t = -t                                                  # start at the lower end, inside the horn
        src = idx[t < t.min() + .002]
        d = dijkstra(L, directed=False, indices=src, min_only=True)[idx]
        d = np.where(np.isfinite(d), d, 0)
        nb = int(d.max() / step) + 2
        bi = np.minimum((d / step).astype(int), nb - 1)
        cnt = np.bincount(bi, minlength=nb)
        cl = np.stack([np.bincount(bi, pts[:, k], nb) for k in range(3)], 1)
        have = cnt > 0
        cl = np.stack([np.interp(np.arange(nb), np.nonzero(have)[0], cl[have, k] / cnt[have]) for k in range(3)], 1)
        for _ in range(3):
            cl[1:-1] = .25 * cl[:-2] + .5 * cl[1:-1] + .25 * cl[2:]
        T = np.gradient(cl, axis=0); T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
        N = np.zeros_like(T); ref = np.cross(T[0], [0, 1, 0] if abs(T[0][1]) < .9 else [1, 0, 0])
        N[0] = ref / np.linalg.norm(ref)
        for i in range(1, nb):
            q = N[i - 1] - T[i] * (N[i - 1] @ T[i]); N[i] = q / max(np.linalg.norm(q), 1e-12)
        B = np.cross(T, N)
        off = pts - cl[bi]
        U[idx] = (np.arctan2(np.einsum('ij,ij->i', off, B[bi]), np.einsum('ij,ij->i', off, N[bi])) / (2 * np.pi)) % 1
        V[idx] = d / v_unit
    # back to the input's vertices, then split the seam
    u, vv = U[inv], V[inv]
    fu = u[f]
    wrap = np.ptp(fu, axis=1) > .5
    src = list(range(len(v))); uu = list(u); vl = list(vv); dup = {}
    f2 = f.copy()
    for fi in np.nonzero(wrap)[0]:
        for k in range(3):
            i = f[fi, k]
            if u[i] < .5:
                if i not in dup:
                    dup[i] = len(src); src.append(i); uu.append(u[i] + 1); vl.append(vv[i])
                f2[fi, k] = dup[i]
    uv = np.stack([uu, vl], 1).astype(np.float32)
    return uv, f2, np.array(src)


def load(src, keep_gloves=False, keep_slippers=False):
    """Return list of (part, group) with transformed geometry. group in {mask, horn, glove_L, ...}.
    The v08 gloves are replaced by the rebuilt ones in gloves.py, and the v04 slippers by the owner's
    cow mule slippers (slippers below), unless keep_gloves / keep_slippers is set."""
    out = []
    for name in MASK_KEEP:
        p = dict(src.part(name))
        p['v'] = D.mask_transform(p['v'])
        if 'Horn' in name or 'Wires' in name:
            p['v'] = p['v'] + D.HORN_SHIFT          # horns ride on the ends of the tube
        p['v'] = D.head_pose(p['v'])
        if p.get('n') is not None:
            p['n'] = np.asarray(p['n']) @ D.HEAD_R.T
        if 'Wires' in name:
            p['v'] = close_wire_gaps(p['v'], p['f'])
            uv, f2, src = wire_uv(p['v'], p['f'])                 # round 47: for the wire's texture
            nv = len(p['v'])
            for k, x in list(p.items()):
                if k not in ('f', 'uv') and isinstance(x, np.ndarray) and len(x) == nv:
                    p[k] = x[src]
            p['v'] = np.asarray(p['v'])[src]
            if p.get('n') is not None:
                p['n'] = np.asarray(p['n'])[src]
            p['uv'], p['f'] = uv, f2
        p['v'] = p['v'].astype(np.float32)
        p['name'] = NEW_NAMES[name]
        out.append((p, 'head'))
    for old, side in ([('Right_glove_v08_', 'L'), ('Left_glove_v08_', 'R')] if keep_gloves else []):
        T, Rm = glove_transform(src, old, side)
        el, wr = D.J[f'Forearm_{side}'], D.J[f'Hand_{side}']
        d = (wr - el) / np.linalg.norm(wr - el)
        for p in src.parts:
            if p['name'].startswith(old):
                if p['name'].endswith(('attached_cuff_fur', 'soft_fur_cuff')):
                    # the fur sleeve end now covers the glove top directly (3.5 cm overlap, shared
                    # weights); the separate v08 cuff ring z-fought with the sleeve at this size
                    continue
                q = dict(p)
                v = T(p['v'])
                if p['name'].endswith('soft_fur_cuff'):
                    # pull the flared cuff in so it hugs the sleeve end like a wristband
                    t = (v - wr) @ d
                    radial = (v - wr) - t[:, None] * d
                    r = np.linalg.norm(radial, axis=1)
                    r_new = np.where(r > .049, .049 + (r - .049) * .35, r)
                    v = wr + t[:, None] * d + radial * (r_new / np.maximum(r, 1e-9))[:, None]
                q['v'] = v.astype(np.float32)
                q['n'] = (p['n'] @ Rm.T).astype(np.float32)
                if p['name'].endswith('soft_fur_cuff'):
                    import sdf as S
                    q['n'] = S.vertex_normals(v, p['f']).astype(np.float32)
                q['name'] = f'Glove_{side}_' + p['name'][len(old):]
                out.append((q, f'glove_{side}'))
    for old, side in ([('Right_slipper_v04_', 'L'), ('Left_slipper_v04_', 'R')] if keep_slippers else []):
        s = 1 if side == 'L' else -1
        ring = src.part(old + 'padded_ankle_opening')['v']
        c_old = np.array([ring[:, 0].mean(), 0, ring[:, 2].mean()])
        foot = D.J[f'Foot_{side}']
        c_new = np.array([foot[0], 0, foot[2] + .01])
        Ry = Rotation.from_euler('y', s * np.deg2rad(7)).as_matrix()     # slight toe-out
        for p in src.parts:
            if p['name'].startswith(old):
                q = dict(p)
                q['v'] = ((p['v'] - c_old) @ Ry.T * SLIPPER_SIZE + c_new).astype(np.float32)
                q['n'] = (p['n'] @ Ry.T).astype(np.float32)
                q['name'] = f'Slipper_{side}_' + p['name'][len(old):]
                out.append((q, f'foot_{side}'))
    return out


SLIPPER_ASSET = Path(__file__).resolve().parent.parent / 'assets' / 'slippers_cow_mule.glb'
SLIPPER_SOLE = .003          # lowest point of the sole above the floor


def slippers(model):
    """The owner's cow mule slippers (see cow_mule_slippers.py), placed with their ankle axis on each
    ankle and the usual 7 degree toe-out.  Adds their images and material to `model`; returns
    [(part, group)]."""
    src = G.read(SLIPPER_ASSET)
    img = [model.add_image(*im) for im in src.images]
    mat = []
    for m in src.materials:
        m = json.loads(json.dumps(m))
        for holder in (m.get('pbrMetallicRoughness', {}), m):
            for k, t in holder.items():
                if k.endswith('Texture') and isinstance(t, dict) and 'image' in t:
                    t['image'] = img[t['image']]
        mat.append(model.add_material(m))
    out = []
    for p in src.parts:
        side = 'L' if '_L_' in p['name'] else 'R'
        s = 1 if side == 'L' else -1
        foot = D.J[f'Foot_{side}']
        Ry = Rotation.from_euler('y', s * np.deg2rad(7)).as_matrix()
        q = dict(p)
        q['v'] = (p['v'] @ Ry.T + np.array([foot[0], SLIPPER_SOLE, foot[2]])).astype(np.float32)
        q['n'] = (p['n'] @ Ry.T).astype(np.float32)
        q['material'] = mat[p['material']]
        out.append((q, f'foot_{side}'))
    return out
