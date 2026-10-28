"""Real-world glove size from the mask scan + the overhead photo of gloves beside the mask.

usage: python3 -I measure_scale.py <cowMask1.stl> <photo2.jpg> <glove_mask_L.npy> <glove_mask_R.npy> <out.jpg>

Method
- Scan (mm): fit a sphere to each bead eye -> centre-to-centre spacing (56.9 mm, beads ~23 mm across).
- Photo 2 is the same Nikon D800 frame as "Left Hand Glove - No Hand Inside.jpg" (template match 0.987),
  whose EXIF says 24 mm full frame -> focal length in pixels = 24 / 35.9 * image width.
- Hough circles on the yellow beads -> pixel spacing -> camera distance to the eye plane.
- Eye centres sit ~65 mm above the mat (scan: centre Z 122.7, mask rim resting at Z ~58),
  so the camera is ~44 cm above the mat; the scale is evaluated at each part's height
  (terry ~10 mm, hoof outline ~15 mm above the mat).
- Check: the mat measures 598 mm across (a standard 24 in / 610 mm cutting mat).
- Glove landmarks (cuff mid, hoof-base mid, toe-cap base mid and tip) were picked on a gridded zoom
  of photo 2; widths come from birefnet glove masks (prep: seg_glove step, one .npy per glove).
Uncertainty about +/-5 % (24 mm lens distortion near the frame edge, mask resting height, picking).
"""
import sys, os
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
import numpy as np, cv2, trimesh
from PIL import Image, ImageDraw, ImageFont

STL, PHOTO, ML, MR, OUT = sys.argv[1:6]

# --- scan: sphere fit to the two bead eyes (seed centres found on a top-down height map) ---
V = trimesh.load(STL).vertices
def sphere(cx, cy, rad):
    sel = V[np.hypot(V[:, 0] - cx, V[:, 1] - cy) < rad * 0.8]
    sel = sel[sel[:, 2] > np.percentile(sel[:, 2], 40)]
    A = np.c_[2 * sel, np.ones(len(sel))]; b = (sel ** 2).sum(1)
    for _ in range(3):
        c, *_ = np.linalg.lstsq(A, b, rcond=None); r = np.sqrt(c[3] + c[:3] @ c[:3])
        err = np.abs(np.linalg.norm(sel - c[:3], axis=1) - r); k = err < np.percentile(err, 85)
        A, b, sel = A[k], b[k], sel[k]
    return c[:3], r
ea, _ = sphere(-14.1, 25.2, 11.7); eb, _ = sphere(-13.3, -35.0, 10.5)
EYE_MM = float(np.linalg.norm(ea - eb)); EYE_H = float((ea[2] + eb[2]) / 2 - 58.0)

# --- photo: bead eyes by Hough circles on yellowness ---
im = Image.open(PHOTO).convert("RGB"); a = np.asarray(im)
hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
yl = (((hsv[..., 0] > 20) & (hsv[..., 0] < 38)) * hsv[..., 1]).astype(np.uint8)
roi = cv2.GaussianBlur(yl, (5, 5), 0)[480:720, 760:1150]
cir = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, dp=1, minDist=120, param1=80, param2=18, minRadius=35, maxRadius=60)[0][:2]
cir[:, :2] += (760, 480)  # ROI -> full-image pixels
EYE_PX = float(np.hypot(*(cir[0][:2] - cir[1][:2])))

F_PX = 24 / 35.9 * im.width
D_MAT = F_PX / (EYE_PX / EYE_MM) + EYE_H
s = lambda h: F_PX / (D_MAT - h)            # px per mm at height h above the mat
print(f"eye spacing {EYE_MM:.1f} mm / {EYE_PX:.0f} px; camera {D_MAT:.0f} mm above mat; mat 1820 px = {1820 / s(0):.0f} mm")

G = {"R": dict(cuff=(1807, 727), base=(1407, 1013), toes=[((1363, 953), (1182, 1149)), ((1451, 1074), (1240, 1262))], mask=MR),
     "L": dict(cuff=(178, 621), base=(518, 987), toes=[((550, 938), (798, 1100)), ((486, 1036), (678, 1212))], mask=ML)}
d = ImageDraw.Draw(im)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
def label(p, t):
    x, y = p; w = d.textlength(t, font=font)
    d.rectangle((x - 4, y - 4, x + w + 4, y + 26), fill=(0, 0, 0)); d.text((x, y), t, font=font, fill=(255, 230, 80))
for k, g in G.items():
    c0, c1 = np.array(g["cuff"], float), np.array(g["base"], float)
    L = np.linalg.norm(c1 - c0); ax = (c1 - c0) / L
    toes = [np.linalg.norm(np.subtract(t, b)) / s(15) for b, t in g["toes"]]
    tip = max((np.array(t) - c0) @ ax for _, t in g["toes"]) / s(12)
    m = np.load(g["mask"]); ys, xs = np.where(m); P = np.c_[xs, ys] - c0
    u = P @ ax; v = P @ np.array([-ax[1], ax[0]])
    w = [np.ptp(v[np.abs(u - f * L) < 4]) / s(10) for f in (0.15, 0.3)]
    print(f"glove {k}: terry {L / s(10):.0f} mm, toe caps {toes[0]:.0f}/{toes[1]:.0f} mm, cuff->tip {tip:.0f} mm, flat width (wrist) {w[0]:.0f}-{w[1]:.0f} mm")
    d.line((*c0, *c1), fill=(255, 60, 60), width=4)
    for b, t in g["toes"]:
        d.line((*b, *t), fill=(80, 200, 255), width=4)
    label(((c0 + c1) / 2 + (-60, -40)), f"terry {L / s(10) / 10:.1f} cm")
    for (b, t), tl in zip(g["toes"], toes):
        label(((np.array(b) + np.array(t)) / 2 + (8, 0)), f"{tl / 10:.1f} cm")
d.line((*cir[0][:2], *cir[1][:2]), fill=(80, 255, 120), width=3)
label((cir[0][0] - 40, cir[0][1] - 75), f"eyes {EYE_MM / 10:.1f} cm (scan)")
im.save(OUT, quality=90)
