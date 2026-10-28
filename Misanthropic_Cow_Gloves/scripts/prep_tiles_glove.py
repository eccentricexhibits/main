"""Prepare the two glove tiles: seams, height maps, paint roughness, 2x2 tiling check (playbook stage 9c).

usage: python3 -I prep_tiles_glove.py <raw_dir: TILE_1_terry.*, TILE_2_hoof_paint.*> <out_dir>
- terry: already seamless as delivered (edge/interior ratio < 1); resized to 2048, warmed slightly (B x0.95).
- hoof paint: strokes run top to bottom; left-right already tiles, top-bottom showed a seam (ratio 1.5), so only
  the vertical direction gets a half-offset crossfade with contrast compensation (prep_tiles.py method).
- height maps: high-pass of luminance. For the paint, DARK = thick paint = raised, so the paint height is inverted;
  two scales (bristle lines + stroke ridges).
- paint colour: darks deepened with gamma 1.3 (the raw tile read charcoal on the model).
- paint roughness: thin grey drag streaks are drier/rougher (0.72) than the satin black (0.50).
"""
import sys, os, glob
import numpy as np, cv2
from PIL import Image
RAW, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
SZ = 2048

def load(stem):
    p = glob.glob(os.path.join(RAW, stem + ".*"))[0]
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
    return cv2.resize(a, (SZ, SZ), interpolation=cv2.INTER_AREA if a.shape[0] >= SZ else cv2.INTER_CUBIC)

def wblur(img, sigma):
    p = int(sigma * 3) + 1
    pad = ((p, p), (p, p)) + (((0, 0),) if img.ndim == 3 else ())
    return cv2.GaussianBlur(np.pad(img, pad, mode="wrap"), (0, 0), sigma)[p:-p, p:-p]

def seamless_axis(a, axis, ramp_frac=0.22):
    n = a.shape[axis]; rolled = np.roll(a, n // 2, axis=axis)
    x = np.arange(n, dtype=np.float32); w = np.clip(np.minimum(x, n - 1 - x) / (ramp_frac * n), 0, 1)
    w = 0.5 - 0.5 * np.cos(np.pi * w); w = w[:, None, None] if axis == 0 else w[None, :, None]
    b = a * w + rolled * (1 - w)
    mean = cv2.GaussianBlur(b, (0, 0), 24); k = np.sqrt(w ** 2 + (1 - w) ** 2)
    return np.clip(mean + (b - mean) / k, 0, 255)

def seam_score(a):
    ix = np.abs(np.diff(a, axis=1)).mean(); iy = np.abs(np.diff(a, axis=0)).mean()
    return round(float(np.abs(a[:, 0] - a[:, -1]).mean() / ix), 2), round(float(np.abs(a[0] - a[-1]).mean() / iy), 2)

def highpass(g, sigma):
    hp = g - wblur(g, sigma); return hp / (hp.std() + 1e-6)

terry = load("TILE_1_terry") * np.array([1.0, 0.99, 0.95], np.float32)   # slightly warmer cream: the neutral tile read grey on the model
paint = seamless_axis(load("TILE_2_hoof_paint"), axis=0)
# the delivered tile reads charcoal on the model; deepen the darks toward the real satin black (grey drag streaks
# stay visible because a gamma > 1 compresses dark values more than the light streaks)
paint = 255 * (paint / 255) ** 1.3

gt = cv2.cvtColor(terry.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
h_terry = np.clip(0.5 + 0.25 * highpass(gt, 16), 0, 1)
gp = cv2.cvtColor(paint.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
h_paint = np.clip(0.5 - 0.15 * highpass(gp, 4) - 0.10 * highpass(gp, 30), 0, 1)       # dark = thick = raised
grey = cv2.GaussianBlur(np.clip((gp - 22) / 30, 0, 1), (0, 0), 3)
r_paint = 0.50 + 0.22 * grey

def save(a, n, gray=False):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, n), quality=93) if n.endswith(".jpg") \
        else Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, n))
save(terry, "tile_terry.jpg"); save(paint, "tile_paint.jpg")
save(h_terry * 255, "height_terry.jpg"); save(h_paint * 255, "height_paint.jpg"); save(r_paint * 255, "rough_paint.jpg")
for n, a in (("terry", terry), ("paint", paint)):
    print(f"{n:6s} seam x/y {seam_score(a)}  mean RGB {a.reshape(-1, 3).mean(0).round(0)}")
prev = [np.concatenate([np.concatenate([t, t], 1)] * 2, 0) for t in (cv2.resize(terry, (512, 512)), cv2.resize(paint, (512, 512)))]
Image.fromarray(np.concatenate(prev, 1).astype(np.uint8)).save(os.path.join(OUT, "_tiling_check_2x2.jpg"), quality=88)
