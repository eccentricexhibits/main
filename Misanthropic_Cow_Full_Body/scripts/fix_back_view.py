"""Deterministic fixes on ChatGPT's back view (views/chatgpt_back_try1.webp), no AI redraw.

python3 -I fix_back_view.py <back_in> <front_approved.png> <out.png>
1. long horn (image left): replaced by the approved front view's long horn (3 rings), mirrored
2. neck gap: the skin between hood and collar is covered by extending the hood's fur edge down
3. bow: moved to the centre of the back; its old spot is filled with plain fur from the same rows
4. ankles: the strip of skin between each legging cuff and sock is coloured to match the black
Coordinates are for the 1024x1536 back view.
"""
import sys
import numpy as np, cv2
from PIL import Image

bk, fr, dst = sys.argv[1:4]
a = np.asarray(Image.open(bk).convert("RGB")).astype(np.float32)
f = np.asarray(Image.open(fr).convert("RGB")).astype(np.float32)
H, W, _ = a.shape
BG = np.median(np.concatenate([a[:30, :30].reshape(-1, 3), a[:30, -30:].reshape(-1, 3)]), 0)

def hsv(img): return cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
def horn_mask(img, box, dark_v=110):
    x0, y0, x1, y1 = box; h = hsv(img[y0:y1, x0:x1])
    yel = (h[..., 0] > 12) & (h[..., 0] < 40) & (h[..., 1] > 70)
    m = yel | ((h[..., 2] < dark_v) & (cv2.dilate(yel.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0))
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    return (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
def feather(m, r): return cv2.GaussianBlur(m.astype(np.float32), (0, 0), r)

out = a.copy()
# ---- 1. long horn ----
BB = (380, 50, 470, 175)                       # back view, long horn on the image left
FB = (455, 60, 540, 170)                       # front view (848x1292), long horn on the image right
mb = horn_mask(a, BB); mf = horn_mask(f, FB)
ys, xs = np.where(mb); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max(), ys.max()
ys2, xs2 = np.where(mf); fx0, fy0, fx1, fy1 = xs2.min(), ys2.min(), xs2.max(), ys2.max()
er = np.zeros((H, W), np.float32)
er[BB[1]:BB[3], BB[0]:BB[2]] = cv2.dilate(mb, np.ones((7, 7), np.uint8))
er[:, BB[0] + int(bx1) + 3:] = 0                 # keep the hood edge at the horn root
er = feather(er, 1.2)
out = out * (1 - er[..., None]) + BG * er[..., None]
patch = f[FB[1]:FB[3], FB[0]:FB[2]][fy0:fy1 + 1, fx0:fx1 + 1][:, ::-1]
pm = mf[fy0:fy1 + 1, fx0:fx1 + 1][:, ::-1].astype(np.float32)
s = (by1 - by0 + 1) / patch.shape[0]           # match the back horn's height
patch = cv2.resize(patch, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
pm = feather(cv2.resize(pm, (patch.shape[1], patch.shape[0]), interpolation=cv2.INTER_AREA), 0.6)
ox, oy = BB[0] + bx1 + 1 - patch.shape[1], BB[1] + by0  # root side (right) and top aligned
out[oy:oy + patch.shape[0], ox:ox + patch.shape[1]] = patch * pm[..., None] + out[oy:oy + patch.shape[0], ox:ox + patch.shape[1]] * (1 - pm[..., None])

# ---- 2. neck gap ----
nx0, ny0, nx1, ny1 = 470, 296, 590, 330
h = hsv(a[ny0:ny1, nx0:nx1])
skin = (h[..., 0] < 25) & (h[..., 1] > 35) & (h[..., 2] > 110)
skin = cv2.dilate(skin.astype(np.uint8), np.ones((7, 7), np.uint8))
sm = np.zeros((H, W), np.float32); sm[ny0:ny1, nx0:nx1] = skin; sm = feather(sm, 2.0)
SH = 26                                          # hood fur from just above, moved down over the gap
src = np.roll(out, SH, axis=0)
out = src * sm[..., None] + out * (1 - sm[..., None])

# ---- 3. bow to the centre ----
qx0, qy0, qx1, qy1 = 495, 680, 640, 770
h = hsv(a[qy0:qy1, qx0:qx1])
gold = ((h[..., 0] > 5) & (h[..., 0] < 35) & (h[..., 1] > 50)).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(gold)
gold = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
hull = cv2.convexHull(np.argwhere(gold)[:, ::-1].astype(np.int32))
gold = cv2.fillConvexPoly(np.zeros_like(gold), hull, 1)  # the whole bow, shaded folds included
gold = cv2.dilate(gold, np.ones((7, 7), np.uint8))
ys, xs = np.where(gold); cx_bow = qx0 + xs.mean()
row = np.where(~(a[720] > 235).all(1))[0]; cx_body = (row.min() + row.max()) / 2
dx = int(round(cx_body - cx_bow))
gm = np.zeros((H, W), np.float32); gm[qy0:qy1, qx0:qx1] = gold; gm = feather(gm, 1.5)
FUR_DX = 140                                     # plain fur from the same rows, further left (the fur ribs are horizontal)
fur = np.roll(out, FUR_DX, axis=1)
out = fur * gm[..., None] + out * (1 - gm[..., None])
bow = np.roll(a, dx, axis=1); bm = np.roll(gm, dx, axis=1)
out = bow * bm[..., None] + out * (1 - bm[..., None])

# ---- 4. ankle skin ----
for ax0, ax1 in ((392, 440), (572, 621)):        # only the strip between cuff and sock
    y0, y1 = 1354, 1367
    h = hsv(out[y0:y1, ax0:ax1])
    sk = (h[..., 2] > 70).astype(np.uint8)
    sk = feather(cv2.dilate(sk, np.ones((3, 3), np.uint8)), 0.8)
    out[y0:y1, ax0:ax1] = np.array([22, 22, 24]) * sk[..., None] + out[y0:y1, ax0:ax1] * (1 - sk[..., None])

Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print("bow moved", dx, "px; horn scale", round(s, 3))
