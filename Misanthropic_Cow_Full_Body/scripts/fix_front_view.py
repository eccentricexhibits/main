"""Deterministic proportion fixes on the approved front view (no AI redraw).

python3 -I fix_front_view.py <in.png> <out.png>
- long horn (image right) scaled about its base on the bolster
- legs stretched below the hoof tips so floor-to-crotch matches the original shoot
Coordinates are for Gemini's 848x1264 front view (round 2) and are rescaled for other sizes.
"""
import sys
import numpy as np, cv2
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
H, W, _ = a.shape
kx, ky = W / 848, H / 1264
BG = np.median(np.concatenate([a[:20, :20].reshape(-1, 3), a[:20, -20:].reshape(-1, 3)]), 0)

# ---- 1. long horn: shrink about its root at the bolster's right end ----
HORN_SCALE = 0.65
bx0, by0, bx1, by1 = int(464 * kx), int(55 * ky), int(540 * kx), int(152 * ky)
px, py = 466 * kx, 134 * ky                      # root of the horn on the bolster
box = a[by0:by1, bx0:bx1]
hsv = cv2.cvtColor(box.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
horn = ((hsv[..., 0] > 15) & (hsv[..., 0] < 40) & (hsv[..., 1] > 70)) | (hsv[..., 2] < 110)
horn = cv2.morphologyEx(horn.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(horn)
horn = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.float32)
erase = cv2.GaussianBlur(cv2.dilate(horn, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 1.5)
horn = cv2.GaussianBlur(cv2.dilate(horn, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.8)
full_m = np.zeros((H, W), np.float32); full_m[by0:by1, bx0:bx1] = horn
erase[:, :int(5 * kx)] = 0                       # leave the bolster's edge alone
full_e = np.zeros((H, W), np.float32); full_e[by0:by1, bx0:bx1] = erase
# remove the old horn and its soft edge (to background), then paste the scaled one
out = a * (1 - full_e[..., None]) + BG * full_e[..., None]
M = np.float32([[HORN_SCALE, 0, px * (1 - HORN_SCALE)], [0, HORN_SCALE, py * (1 - HORN_SCALE)]])
sh = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_AREA)
sm = cv2.warpAffine(full_m, M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
out = sh * sm + out * (1 - sm)

# ---- 2. legs: stretch rows below the hoof tips ----
LEG_SCALE = 1.06
y0, floor = int(772 * ky), int(1205 * ky)
top, bot = out[:y0], out[y0:floor]
bot = cv2.resize(bot, (W, int(round((floor - y0) * LEG_SCALE))), interpolation=cv2.INTER_CUBIC)
canvas = np.empty((y0 + bot.shape[0] + (H - floor), W, 3), np.float32)
canvas[:y0] = top; canvas[y0:y0 + bot.shape[0]] = bot; canvas[y0 + bot.shape[0]:] = out[floor:]
Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).save(dst)
print("in", (W, H), "out", canvas.shape[1::-1])
