"""Kept v09 assets (scanned mask, horns, wires, gloves, slippers, rear bow), refitted to the v10 body."""
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


def load(src):
    """Return list of (part, group) with transformed geometry. group in {mask, horn, glove_L, ...}."""
    out = []
    for name in MASK_KEEP:
        p = dict(src.part(name))
        p['v'] = D.mask_transform(p['v'])
        if 'Horn' in name or 'Wires' in name:
            p['v'] = p['v'] + D.HORN_SHIFT          # horns ride on the ends of the tube
        p['v'] = p['v'].astype(np.float32)
        p['name'] = NEW_NAMES[name]
        out.append((p, 'head'))
    for old, side in [('Right_glove_v08_', 'L'), ('Left_glove_v08_', 'R')]:
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
    for old, side in [('Right_slipper_v04_', 'L'), ('Left_slipper_v04_', 'R')]:
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
