"""Check and prepare the 10 ChatGPT fabric tiles (stage 9c step 1), after the slipper project's prep_tiles.py.

python3 -I prep_tiles_cow.py <raw_tiles_dir> <real_fabric_crops_dir> <out_dir>

Checks per raw tile (printed and written to tile_report.json):
- seam x/y: mean jump across the wrap-around edge / mean neighbouring-pixel difference (1.0 = invisible, >1.5 shows)
- light: unevenness of the lighting, std of a heavily blurred luminance / mean (gradients, vignetting; <0.03 is flat)
- luma vs real: mean luminance against the white-balanced crop of the real fabric
- detail: dominant repeat (knit rows, ribs, lace motifs) in mm, from the autocorrelation, at the prompt's tile size
Outputs: seamless 2048 tiles, height maps, gold satin (from beige satin) and glossy black paint (from the plaster),
a lace opacity mask (the lace's gaps show the leggings underneath), and _tiling_check.jpg (each tile repeated 2x2).
Colour corrections after comparing with the real-fabric crops (ADJUST below).
"""
import sys, os, json
import numpy as np, cv2
from PIL import Image

RAW, REAL, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
SZ = 2048
# name: (real crop file, tile size in cm from the prompt, patterned -> period-aligned seam fix)
TILES = {
    "TILE_01_white_faux_fur": ("FABRIC_1_white_faux_fur", 10, False),
    "TILE_02_black_shag_fur": ("FABRIC_2_black_shag_fur", 10, False),
    "TILE_03_pink_fleece": ("FABRIC_3_pink_fleece_udder", 8, False),
    "TILE_04_beige_satin": ("FABRIC_4_beige_satin", 8, True),
    "TILE_05_beige_lace": ("FABRIC_5_beige_lace", 8, False),
    "TILE_06_black_leggings": ("FABRIC_6_black_leggings", 6, True),
    "TILE_07_white_fabric_paint": ("FABRIC_7_white_fabric_paint_spot", 6, False),
    "TILE_08_white_knit": ("FABRIC_8_white_knit_glove", 6, True),
    "TILE_09_cracked_white_plaster": ("FABRIC_9_cracked_white_plaster_mask", 8, False),
    "TILE_10_red_flocked_snout": ("FABRIC_10_red_flocked_snout", 5, False),
}


def luma(a):
    return cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)


def wblur(img, sigma):
    p = int(sigma * 3) + 1
    pad = ((p, p), (p, p)) + (((0, 0),) if img.ndim == 3 else ())
    return cv2.GaussianBlur(np.pad(img, pad, mode="wrap"), (0, 0), sigma)[p:-p, p:-p]


def seam_score(a):
    ix = np.abs(np.diff(a, axis=1)).mean(); iy = np.abs(np.diff(a, axis=0)).mean()
    return round(float(np.abs(a[:, 0] - a[:, -1]).mean() / ix), 2), round(float(np.abs(a[0] - a[-1]).mean() / iy), 2)


def period(g, axis, lo=6):
    """Dominant repeat along an axis (pixels) from the autocorrelation of the row/column means; 0 if none."""
    sig = (g - g.mean()).mean(axis=1 - axis)
    f = np.fft.rfft(sig, n=len(sig) * 2); ac = np.fft.irfft(f * np.conj(f))[:len(sig)]
    ac /= ac[0] + 1e-9
    seg = ac[lo:len(sig) // 4]
    i = int(np.argmax(seg)); return (i + lo, float(seg[i])) if seg[i] > 0.2 else (0, float(seg[i]))


def seamless_axis(a, axis, shift, ramp_frac=0.22, compensate=True):
    n = a.shape[axis]
    rolled = np.roll(a, shift, axis=axis)
    x = np.arange(n, dtype=np.float32)
    w = np.clip(np.minimum(x, n - 1 - x) / (ramp_frac * n), 0, 1)
    w = 0.5 - 0.5 * np.cos(np.pi * w)
    w = w[:, None, None] if axis == 0 else w[None, :, None]
    b = a * w + rolled * (1 - w)
    if compensate:            # restore the contrast lost by mixing two uncorrelated textures
        mean = wblur(b, 24)
        b = mean + (b - mean) / np.sqrt(w ** 2 + (1 - w) ** 2)
    return np.clip(b, 0, 255)


def flatten_light(a, sigma=160):
    """Divide out very-low-frequency lighting (keeps the mean colour)."""
    L = luma(a); low = wblur(L, sigma)
    return np.clip(a * (L.mean() / (low + 1e-3))[..., None], 0, 255)


def height(a, sigma=18):
    g = luma(a); hp = g - wblur(g, sigma)
    return np.clip(0.5 + hp / (hp.std() * 4 + 1e-6), 0, 1)


def recolor(a, target_rgb, contrast=1.0):
    g = luma(a); rel = (g / (wblur(g, 60) + 1)) ** contrast
    return np.clip(np.array(target_rgb, np.float32)[None, None, :] * rel[..., None], 0, 255)


def to_mean(a, rgb):
    """Scale each channel so the tile's mean colour becomes rgb (keeps the texture's relative contrast)."""
    return np.clip(a * (np.array(rgb, np.float32) / a.reshape(-1, 3).mean(0)), 0, 255)


def soften(a, k):
    """Scale the texture's contrast about its local mean by k (k < 1 smooths)."""
    m = wblur(a, 30); return np.clip(m + (a - m) * k, 0, 255)


ADJUST = {
    "TILE_02_black_shag_fur": lambda a: to_mean(a, (34, 34, 36)),          # the real fur is 2.7x lighter (sheen on the strands)
    "TILE_03_pink_fleece": lambda a: to_mean(a, (242, 192, 200)),          # the tile's red channel clips at 255
    "TILE_04_beige_satin": lambda a: soften(a, 0.35),                     # the twill weave reads as canvas; satin is smooth
    "TILE_09_cracked_white_plaster": lambda a: to_mean(a, (222, 219, 212)),  # x0.94: pure 235 white blows out under light
    "TILE_10_red_flocked_snout": lambda a: to_mean(a, (112, 22, 28)),      # the real flock is a dark crimson, not pure red
}

report, ready = {}, {}
for name, (real, cm, patterned) in TILES.items():
    a0 = np.asarray(Image.open(f"{RAW}/{name}.png").convert("RGB")).astype(np.float32)
    L0 = luma(a0)
    r = np.asarray(Image.open(f"{REAL}/{real}.png").convert("RGB")).astype(np.float32)
    rep = {"size_px": list(a0.shape[:2][::-1]), "seam_raw": seam_score(a0),
           "light_unevenness": round(float(wblur(L0, a0.shape[0] / 8).std() / L0.mean()), 3),
           "mean_rgb": a0.reshape(-1, 3).mean(0).round(0).tolist(), "luma": round(float(L0.mean()), 1),
           "real_mean_rgb": r.reshape(-1, 3).mean(0).round(0).tolist(), "real_luma": round(float(luma(r).mean()), 1)}
    rep["luma_vs_real"] = round(rep["luma"] / max(rep["real_luma"], 1), 2)
    px, pc = period(L0, 1); py, pcy = period(L0, 0)
    mm = cm * 10 / a0.shape[0]
    rep["repeat_mm_x_y"] = [round(px * mm, 2) if px else None, round(py * mm, 2) if py else None]
    a = cv2.resize(a0, (SZ, SZ), interpolation=cv2.INTER_AREA)
    if rep["light_unevenness"] > 0.03:
        a = flatten_light(a); rep["light_fixed"] = True
    if max(rep["seam_raw"]) > 1.25:
        if patterned:
            g = luma(a); qx, _ = period(g, 1); qy, _ = period(g, 0)
            sx = (SZ // 2 // qx) * qx if qx else SZ // 2; sy = (SZ // 2 // qy) * qy if qy else SZ // 2
            a = seamless_axis(seamless_axis(a, 1, sx, compensate=False), 0, sy, compensate=False)
        else:
            a = seamless_axis(seamless_axis(a, 1, SZ // 2), 0, SZ // 2)
        rep["seam_fixed"] = seam_score(a)
    if name in ADJUST: a = ADJUST[name](a); rep["adjusted"] = True; rep["mean_rgb_ready"] = a.reshape(-1, 3).mean(0).round(0).tolist()
    ready[name] = a
    report[name] = rep
    print(f"{name:30s} seam {rep['seam_raw']} -> {rep.get('seam_fixed', '-')}  light {rep['light_unevenness']}"
          f"  luma {rep['luma']} vs real {rep['real_luma']} ({rep['luma_vs_real']})  repeat mm {rep['repeat_mm_x_y']}")

ready["TILE_04b_gold_satin"] = recolor(ready["TILE_04_beige_satin"], (196, 150, 62), contrast=1.4)
ready["TILE_09b_glossy_black_paint"] = recolor(ready["TILE_09_cracked_white_plaster"], (22, 22, 24), contrast=1.8)
lace = luma(ready["TILE_05_beige_lace"])          # threads are light, the gaps between them dark
lo, hi = np.percentile(lace, 25), np.percentile(lace, 60)
alpha = np.clip((lace - lo) / (hi - lo), 0, 1)
Image.fromarray((alpha * 255).astype(np.uint8)).save(f"{OUT}/TILE_05_beige_lace_opacity.png")
report["TILE_05_beige_lace"]["opacity_mean"] = round(float(alpha.mean()), 2)
for n, a in ready.items():
    Image.fromarray(a.astype(np.uint8)).save(f"{OUT}/{n}.png")
    Image.fromarray((height(a) * 255).astype(np.uint8)).save(f"{OUT}/{n}_height.png")
prev = []
for n, a in ready.items():
    t = cv2.resize(a, (384, 384), interpolation=cv2.INTER_AREA)
    t = np.concatenate([np.concatenate([t, t], 1)] * 2, 0).astype(np.uint8)
    t = cv2.putText(t.copy(), n.replace("TILE_", ""), (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)
    prev.append(t)
while len(prev) % 4: prev.append(np.full_like(prev[0], 255))
rows = [np.concatenate(prev[i:i + 4], 1) for i in range(0, len(prev), 4)]
Image.fromarray(np.concatenate(rows, 0)).save(f"{OUT}/_tiling_check.jpg", quality=85)
json.dump(report, open(f"{OUT}/tile_report.json", "w"), indent=1)
print("wrote", OUT)
