"""Render the violet -> turquoise background as exact brand-colour mixes.

Every pixel is violet + t * (turquoise - violet) for some t in [0, 1], so the solid
areas are exactly #8A25C9 / #48C0D9 (no browser gradient dithering or filter drift).
"""
import pathlib
import numpy as np
from PIL import Image

VIOLET = np.array([0x8A, 0x25, 0xC9], float)
TURQ = np.array([0x48, 0xC0, 0xD9], float)
W, H, K = 1200, 627, 2                      # rendered at 2x

y, x = np.mgrid[0:H*K, 0:W*K] / K + 0.5 / K

def smooth(e0, e1, v):
    v = np.clip((v - e0) / (e1 - e0), 0, 1)
    return v * v * (3 - 2 * v)

def bump(cx, cy, rx, ry):
    """Soft blob that is exactly 0 outside its ellipse."""
    d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
    return np.clip(1 - d, 0, 1) ** 2

t = smooth(0.36, 0.92, (x + 0.30 * y) / W)              # diagonal base gradient
t = t + (1 - t) * bump(1130, 90, 330, 250)              # turquoise glow, top right
t = t + (1 - t) * 0.55 * bump(1080, 660, 420, 170)      # turquoise sweep, bottom right

img = VIOLET + t[..., None] * (TURQ - VIOLET)
out = pathlib.Path(__file__).parent / 'bg@2x.png'
Image.fromarray(np.rint(img).astype(np.uint8)).save(out, optimize=True)
