"""Deterministic proportion fixes on the approved front view (no AI redraw).

python3 -I fix_front_view.py <in.png> <out.png> <straight-on head photo>
- long horn (image right) replaced by the real horn cut out of a straight-on head photo
  (reference/REF_J_head_front_on_new_photo.webp)
- legs (leggings only, between the hoof tips and the slipper tops) stretched so floor-to-crotch
  matches the original shoot; the slippers are moved down unchanged
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

# ---- 1. long horn: replace Gemini's horn with the real one from a straight-on head photo ----
# Gemini kept drawing it 1.6-3x too big and the wrong shape; scaling it looked pasted on, and
# the horn from original-shoot photo 3 is seen at an angle. Seen straight on, the horn goes out
# sideways and hooks up near the tip. Sizes use the rigid mask as the ruler: mask width at eye
# level is 315 px in REF_J and 132 px here (both photos give the same horn size).
REAL = sys.argv[3]
bx0, by0, bx1, by1 = int(463 * kx), int(30 * ky), int(600 * kx), int(160 * ky)
box = a[by0:by1, bx0:bx1]
hsv = cv2.cvtColor(box.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
yel = (hsv[..., 0] > 15) & (hsv[..., 0] < 40) & (hsv[..., 1] > 70)
old = yel | ((hsv[..., 2] < 110) & (cv2.dilate(yel.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0))
old = cv2.dilate(old.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
old[:, :int(4 * kx)] = 0                              # leave the bolster's edge alone
erase = np.zeros((H, W), np.float32); erase[by0:by1, bx0:bx1] = cv2.GaussianBlur(old, (0, 0), 1.5)
out = a * (1 - erase[..., None]) + BG * erase[..., None]
# fill the gap under the old horn root (between bolster fur and background)
gap = np.zeros((H, W), np.uint8); gap[int(136 * ky):int(158 * ky), int(461 * kx):int(474 * kx)] = 255
out = cv2.inpaint(np.clip(out, 0, 255).astype(np.uint8), gap, 5, cv2.INPAINT_TELEA).astype(np.float32)

r = np.asarray(Image.open(REAL).convert("RGB")).astype(np.float32)
rx0, ry0, rx1, ry1 = 547, 85, 694, 222                # long horn in REF_J, from the bolster edge out
hc = r[ry0:ry1, rx0:rx1]
hh = cv2.cvtColor(hc.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
ry = (hh[..., 0] > 15) & (hh[..., 0] < 40) & (hh[..., 1] > 70)
rm = ry | ((hh[..., 2] < 90) & (hh[..., 1] < 110) & (cv2.dilate(ry.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0))
rm = cv2.morphologyEx(rm.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(rm)
rm = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
rm = cv2.erode(rm, np.ones((3, 3), np.uint8)).astype(np.float32)   # drop the teal background fringe
# match the horn's yellow to Gemini's (sampled on the short horn) and its exposure
gy = cv2.cvtColor(a[int(115 * ky):int(145 * ky), int(330 * kx):int(372 * kx)].astype(np.uint8), cv2.COLOR_RGB2HSV)
gsel = (gy[..., 0] > 15) & (gy[..., 0] < 40) & (gy[..., 1] > 70)
# match hue/saturation/brightness of the yellow in HSV, so the black rings stay black
tgt = np.median(gy[gsel].astype(np.float32), 0)
srh = np.median(hh[ry], 0)
hh2 = hh.copy()
hh2[..., 0] = np.clip(hh[..., 0] + (tgt[0] - srh[0]), 0, 179)
hh2[..., 1] = np.clip(hh[..., 1] * (tgt[1] / srh[1]), 0, 255)
hh2[..., 2] = np.clip(hh[..., 2] * (tgt[2] / srh[2]), 0, 255)
hc = cv2.cvtColor(hh2.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
s_ = 132 / 315 * kx
hc = cv2.GaussianBlur(cv2.resize(hc, None, fx=s_, fy=s_, interpolation=cv2.INTER_AREA), (0, 0), 0.6)  # Gemini's image is soft
rm = cv2.GaussianBlur(cv2.resize(rm, (hc.shape[1], hc.shape[0]), interpolation=cv2.INTER_AREA), (0, 0), 0.6)
# root centre (x at the bolster edge, y mid-root) -> Gemini's horn root on the bolster
ramp = np.linspace(1, 0, 4)[:, None]; rm[-4:] *= ramp      # soften the cut at the bottom of the root
root_src = (0, (177 - ry0) * s_)
ox, oy = int(round(463 * kx - root_src[0])), int(round(132 * ky - root_src[1]))
hgt, wid = rm.shape
out[oy:oy + hgt, ox:ox + wid] = hc * rm[..., None] + out[oy:oy + hgt, ox:ox + wid] * (1 - rm[..., None])

# ---- 2. legs: stretch only the leggings between the hoof tips and the slipper tops ----
# Floor-to-crotch was ~6% short of the original shoot. The slippers keep their shape:
# the rows from the slipper tops to the bottom of the image are moved down, not scaled.
LEG_GAIN = 0.06
crotch, y0, y1, floor = int(742 * ky), int(772 * ky), int(1068 * ky), int(1205 * ky)
add = int(round(LEG_GAIN * (floor - crotch)))
legs = cv2.resize(out[y0:y1], (W, (y1 - y0) + add), interpolation=cv2.INTER_CUBIC)
canvas = np.concatenate([out[:y0], legs, out[y1:]], axis=0)
Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).save(dst)
print("in", (W, H), "out", canvas.shape[1::-1])
