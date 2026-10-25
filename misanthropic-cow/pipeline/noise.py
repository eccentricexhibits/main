"""Small deterministic 3D value-noise / fbm helpers (numpy)."""
import numpy as np


def _hash(ix, iy, iz, seed):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return (h & 0xFFFFFF).astype(np.float64) / 0xFFFFFF


def value3(p, seed=0):
    p = np.asarray(p, np.float64)
    i = np.floor(p).astype(np.int64)
    f = p - i
    u = f * f * (3 - 2 * f)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (u[..., 0] if dx else 1 - u[..., 0]) * (u[..., 1] if dy else 1 - u[..., 1]) * (u[..., 2] if dz else 1 - u[..., 2])
                out = out + w * _hash(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed)
    return out * 2 - 1


def fbm(p, octaves=4, seed=0, lac=2.03, gain=.5):
    amp, tot, norm = 1.0, 0, 0
    p = np.asarray(p, np.float64)
    for o in range(octaves):
        tot = tot + amp * value3(p, seed + o * 17)
        norm += amp
        amp *= gain
        p = p * lac
    return tot / norm
