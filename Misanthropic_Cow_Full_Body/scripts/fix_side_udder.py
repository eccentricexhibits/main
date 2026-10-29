"""Enlarge the udder in a side view about its top attachment point (no AI redraw).

python3 -I fix_side_udder.py <in> <out> <scale> <box x0,y0,x1,y1 as fractions>
The right-facing side view's udder stuck out ~22% less than the left-facing one's,
and less than the front view's lobe width implies; the belly stuck out past it.
"""
import sys
import numpy as np, cv2
from PIL import Image

src, dst, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
fx0, fy0, fx1, fy1 = [float(v) for v in sys.argv[4].split(",")]
a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
H, W, _ = a.shape
x0, y0, x1, y1 = int(fx0 * W), int(fy0 * H), int(fx1 * W), int(fy1 * H)
h = cv2.cvtColor(a[y0:y1, x0:x1].astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
pink = (((h[..., 0] < 12) | (h[..., 0] > 160)) & (h[..., 1] > 22) & (h[..., 1] < 150) & (h[..., 2] > 140)).astype(np.uint8)
pink = cv2.morphologyEx(pink, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(pink)
pink = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
cnts, _ = cv2.findContours(pink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
pink = cv2.drawContours(np.zeros_like(pink), cnts, -1, 1, -1)       # fill holes
m = np.zeros((H, W), np.float32); m[y0:y1, x0:x1] = pink
ys, xs = np.where(m > 0)
facing_right = xs.mean() > (xs.min() + xs.max()) / 2 - 1e9 and fx0 > 0.5
px = xs.min() if facing_right else xs.max()      # attachment edge at the chest
py = ys.min()                                     # top: the udder grows outward and down
M = np.float32([[scale, 0, px * (1 - scale)], [0, scale, py * (1 - scale)]])
big = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_CUBIC)
bm = cv2.GaussianBlur(cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR), (0, 0), 0.8)[..., None]
out = big * bm + a * (1 - bm)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print("udder bbox", xs.min(), ys.min(), xs.max(), ys.max(), "scaled", scale)
