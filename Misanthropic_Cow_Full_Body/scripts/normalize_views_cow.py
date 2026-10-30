"""Tripo inputs: put the four approved views on 1536x1536 white squares with the same figure
height and ground line, centred. Off-white AI backgrounds and faint floor shadows are cleaned to
pure white first, so they don't count as part of the figure.

python3 -I normalize_views_cow.py <views_dir> <out_dir>
"""
import os, sys
import numpy as np, cv2
from PIL import Image

V, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
VIEWS = [("1_FRONT_approved.png", "Front.png"), ("2_BACK_approved.png", "Back.png"),
         ("3_SIDE_facing_left_approved.png", "Left_facing_left.png"),
         ("4_SIDE_facing_right_approved.png", "Right_facing_right.png")]
SIZE, FIG_H, GROUND = 1536, 1380, 1468

def clean(a):
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(np.float32)
    std = np.sqrt(np.maximum(cv2.blur(g * g, (7, 7)) - cv2.blur(g, (7, 7)) ** 2, 0))
    # background: bright, colourless and smooth; white fur is textured, so it stays
    bgish = (hsv[..., 2] > 236) & (hsv[..., 1] < 22) & (std < 3.0)
    n, lab, st, _ = cv2.connectedComponentsWithStats(bgish.astype(np.uint8))
    H, W = bgish.shape
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))                                   # only background touching the border
    bg = cv2.morphologyEx(bg.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)
    # faint floor shadows: light grey, colourless, smooth, below the figure's widest point
    shadow = (hsv[..., 2] > 150) & (hsv[..., 1] < 30) & (std < 6.0)
    shadow[: int(H * 0.85)] = False
    bg |= shadow
    alpha = cv2.GaussianBlur((~bg).astype(np.float32), (0, 0), 0.8)[..., None]
    return (a * alpha + 255 * (1 - alpha)).astype(np.uint8), ~bg

for src, dst in VIEWS:
    a = np.asarray(Image.open(os.path.join(V, src)).convert("RGB"))
    a, fig = clean(a)
    ys, xs = np.where(fig)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    crop = a[y0:y1 + 1, x0:x1 + 1]
    s = FIG_H / crop.shape[0]
    crop = cv2.resize(crop, (round(crop.shape[1] * s), FIG_H), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    can = np.full((SIZE, SIZE, 3), 255, np.uint8)
    ox = (SIZE - crop.shape[1]) // 2
    can[GROUND - FIG_H:GROUND, ox:ox + crop.shape[1]] = crop
    Image.fromarray(can).save(os.path.join(OUT, dst))
    print(f"{dst:24s} figure {x1 - x0 + 1}x{y1 - y0 + 1} px -> scale {s:.3f}")

ims = [Image.open(os.path.join(OUT, d)).resize((512, 512)) for _, d in VIEWS]
sheet = Image.new("RGB", (512 * 4, 512), "white")
for i, im in enumerate(ims): sheet.paste(im, (512 * i, 0))
from PIL import ImageDraw
d = ImageDraw.Draw(sheet)
for y in (int(GROUND / 3), int((GROUND - FIG_H) / 3)): d.line((0, y, 2048, y), fill=(255, 0, 0), width=1)
sheet.save(os.path.join(OUT, "lineup_check.jpg"), quality=90)
