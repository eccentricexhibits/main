"""Tripo inputs for the glove: every view on a 1536 white square, same glove height, same top and
bottom lines, centred on the hand's axis (the middle of the hoof), not on the bounding box, so the
thumb sticking out in the front/back views doesn't shift the glove sideways.

usage: python3 -I normalize_glove_views.py <out_dir> <front> <side_little_finger> [side_thumb]
Writes Front.png, Back.png (= mirrored front), Right_little_finger_side.png, Left_thumb_side.png and a
line-up check image. Slots follow the slipper project: Left = the object's own left = the side on the
viewer's RIGHT in the front view, i.e. the thumb side of this left glove.
"""
import sys, os
import numpy as np
from PIL import Image, ImageOps, ImageDraw

SIZE, TOP, BOTTOM = 1536, 115, 1421          # glove spans 85 % of the height
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)

def mask(im, thr=236):
    return (np.asarray(im).astype(int) < thr).any(axis=2)

def normalize(src, out, mirror=False):
    im = Image.open(src).convert("RGB")
    if mirror:
        im = ImageOps.mirror(im)
    m = mask(im); ys, xs = np.where(m)
    y0, y1 = ys.min(), ys.max()
    hoof = m[y0:y0 + int(0.3 * (y1 - y0))]            # hoof rows: centred on the hand axis
    hx = np.where(hoof.any(0))[0]; axis_x = (hx.min() + hx.max()) / 2
    s = (BOTTOM - TOP) / (y1 - y0)
    crop = im.crop((0, y0, im.width, y1 + 1))
    crop = crop.resize((round(crop.width * s), round(crop.height * s)), Image.LANCZOS)
    canvas = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    canvas.paste(crop, (round(SIZE / 2 - axis_x * s), TOP))
    a = np.asarray(canvas).copy(); a[(a > 246).all(2)] = 255   # flatten the off-white background
    Image.fromarray(a).save(os.path.join(OUT, out))
    return out

views = [(sys.argv[2], "Front.png", False), (sys.argv[2], "Back.png", True),
         (sys.argv[3], "Right_little_finger_side.png", False)]
if len(sys.argv) > 4:
    views.append((sys.argv[4], "Left_thumb_side.png", False))
names = [normalize(*v) for v in views]

# line-up check: all views side by side with the shared top/bottom lines and the centre axis
t = 480; k = t / SIZE
sheet = Image.new("RGB", (t * len(names), t + 30), (255, 255, 255)); d = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    sheet.paste(Image.open(os.path.join(OUT, n)).resize((t, t)), (i * t, 0))
    d.text((i * t + 6, t + 8), n, fill=(0, 0, 0))
    d.line((i * t + t // 2, 0, i * t + t // 2, t), fill=(120, 170, 255), width=1)
for y in (TOP, BOTTOM):
    d.line((0, y * k, sheet.width, y * k), fill=(255, 80, 80), width=1)
sheet.save(os.path.join(OUT, "_lineup_check.jpg"), quality=90)
print(names)
