"""Stage 9c: per-texel material regions for the LOW cow and the scanned mask (after the slipper project's make_masks.py).

python3 -I make_regions_cow.py <bake_dir> <fit.json> <swaps.json> <horns.json> <REF_J photo> <out_dir>

Body atlas (Cow_LOW, 4K): from the baked Tripo colour, the per-texel position/normal and the part id.
  - parts: socks, tail cord, wire tuft are their own classes; the horns are yellow with black rings placed by
    arc length along each horn's centreline (long horn 3 rings, short horn 2);
  - body: hands -> white knit / black hooves (dark); below the bloomers -> black leggings / white paint spots (light);
    the bloomers band (beige) -> satin at front and back, lace on the side panels; gold on the lower back -> bow;
    pink above the belly -> udder; dark above the bloomers -> black shag; everything else -> white fur.
  - clean-up: specks smaller than ~1 cm^2 are absorbed into their surroundings.
Mask atlas (Mask_LOW, 2K):
  - eyes and pupils from the scan's bead spheres (yellow bead, black pupil on its front);
  - black paint, red flocked snout and the two nostril slits from REF_J (front-on photo), projected orthographically
    with an affine fit on three landmarks (both eyes, snout centre); texels that face sideways take the class of
    the nearest front-facing texel; everything else is the white plaster.
Writes regions_cow.png / regions_mask.png (class ids), colour-coded previews, and regions.json (classes, counts).
"""
import sys, os, json
import numpy as np, cv2
from PIL import Image
from scipy.spatial import cKDTree

BK, FIT, SWAPS, HORNS, PHOTO, OUT = sys.argv[1:7]
os.makedirs(OUT, exist_ok=True)
CLASSES = {
    1: ("white faux fur", (225, 225, 220)), 2: ("black shag fur", (20, 20, 20)), 3: ("pink fleece udder", (245, 150, 180)),
    4: ("beige satin bloomers", (205, 175, 130)), 5: ("beige lace side panels", (150, 95, 50)), 6: ("black leggings", (55, 65, 95)),
    7: ("white paint spots", (90, 220, 230)), 8: ("white knit gloves", (150, 225, 140)), 9: ("black glossy hooves", (110, 40, 140)),
    10: ("gold satin bow", (240, 190, 20)), 11: ("black socks", (10, 30, 160)), 12: ("white cord tail", (255, 60, 60)),
    13: ("yellow horn paint", (255, 240, 60)), 14: ("black horn rings", (120, 70, 20)), 15: ("bare wire", (160, 160, 175)),
    20: ("mask white plaster", (240, 240, 235)), 21: ("mask black paint", (25, 25, 25)), 22: ("yellow eye bead", (255, 215, 0)),
    23: ("black pupil", (200, 0, 120)), 24: ("red flocked snout", (210, 20, 30)), 25: ("black nostril slits", (0, 200, 120)),
}
fit = json.load(open(FIT)); sw = json.load(open(SWAPS)); hj = json.load(open(HORNS))
S = sw["metres_per_tripo_unit"]; F = fit["scan_mm_to_tripo_units"]
to_cow = lambda X: S * (F["s"] * np.asarray(X, float) @ np.array(F["R"]).T + np.array(F["t"]))


def clean(cls, valid, min_px):
    """Absorb connected specks smaller than min_px into the most common neighbouring class."""
    out = cls.copy()
    for c in np.unique(cls[valid]):
        n, lab, st, _ = cv2.connectedComponentsWithStats((cls == c).astype(np.uint8), connectivity=8)
        for i in np.nonzero(st[1:, cv2.CC_STAT_AREA] < min_px)[0] + 1:
            m = lab == i
            ring = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m & valid
            if ring.any():
                v, k = np.unique(out[ring], return_counts=True); out[m] = v[np.argmax(k)]
    return out


def preview(cls, path):
    im = np.full(cls.shape + (3,), 255, np.uint8)
    for k, (_, rgb) in CLASSES.items(): im[cls == k] = rgb
    Image.fromarray(im).save(path)


# ---------------- body atlas ----------------
col = np.asarray(Image.open(f"{BK}/cow_color_4096.png").convert("RGB")).astype(np.float32) / 255
P = np.load(f"{BK}/geom_cow_position.npy"); N = np.load(f"{BK}/geom_cow_normal.npy"); part = np.load(f"{BK}/geom_cow_part.npy")
valid = part >= 0
x, y, z = P[..., 0], P[..., 1], P[..., 2]
r, g, b = col[..., 0], col[..., 1], col[..., 2]; L = col.mean(-1)
dark = L < 0.27
pink = (r > 0.75) & (g > 0.45) & (g < 0.82) & (b > 0.5) & (r - g > 0.12)
gold = (r > 0.47) & (g > 0.31) & (b < 0.75 * g) & (r - b > 0.16)
beige = (r > 0.55) & (g > 0.45) & (b > 0.32) & (r - b > 0.06) & (r - b < 0.35) & ~pink
cls = np.zeros(part.shape, np.uint8)
body = valid & (part == 0)
cls[body] = 1
hands = body & (np.abs(x) > 0.36) & (z < 1.05)
legs = body & (z < 0.745) & ~hands
band = body & (z >= 0.70) & (z < 0.90) & ~hands
cls[body & dark & (z >= 0.76)] = 2
cls[body & pink & (z > 1.0)] = 3
bl = band & beige & ~(gold & (y > 0.05))
cls[bl] = 4
cls[bl & (np.abs(N[..., 0]) > 0.55)] = 5
cls[legs] = 6
cls[legs & (L > 0.55)] = 7
cls[hands] = 8
cls[hands & dark] = 9
cls[body & gold & (y > 0.05) & (z > 0.78) & (z < 0.95)] = 10
cls[valid & (part == 1)] = 11
cls[valid & (part == 2)] = 12
cls[valid & (part == 5)] = 15
for pid, key, side in ((3, "long_horn", "L"), (4, "short_horn", "R")):
    m = valid & (part == pid)
    C = to_cow(np.array(hj["long_centreline" if pid == 3 else "short_centreline"])) + np.array(sw["horn_shift_m"][side])
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]
    d, i = cKDTree(C).query(P[m])
    s = seg[i] - seg[1]; Lh = seg[-1] - seg[1]                 # arc length from the visible root (after the plug)
    ring = np.zeros(len(s), bool)
    for fr in hj[key]["rings_at_fraction"]:
        ring |= np.abs(s - fr * Lh) < hj[key]["ring_width_mm"] / 2000
    cls[m] = np.where(ring, 14, 13)
cls = clean(cls, valid, 60)                                    # ~1 cm^2 at this texel density
cls[~valid] = 0
Image.fromarray(cls).save(f"{OUT}/regions_cow.png"); preview(cls, f"{OUT}/regions_cow_preview.png")

# ---------------- mask atlas ----------------
MP = np.load(f"{BK}/geom_mask_position.npy"); MN = np.load(f"{BK}/geom_mask_normal.npy"); mval = np.load(f"{BK}/geom_mask_coverage.npy")
mcls = np.zeros(mval.shape, np.uint8); mcls[mval] = 20
eyes = [to_cow(np.array(e["centre"])[None])[0] for e in fit["scan_eye_beads_mm"]]
eye_r = 0.0118
# photo landmarks: eye centres = yellow blobs, snout centre = red blob
ph = np.asarray(Image.open(PHOTO).convert("RGB")).astype(np.float32) / 255
pr, pg, pb = ph[..., 0], ph[..., 1], ph[..., 2]; pL = ph.mean(-1)
yel = (pr > 0.45) & (pg > 0.4) & (pb < 0.5 * pg)
red = (pr > 0.28) & (pr > 1.6 * pg) & (pr > 1.3 * pb)
n, lab, st, cen = cv2.connectedComponentsWithStats(yel.astype(np.uint8))
big = np.argsort(-st[1:, cv2.CC_STAT_AREA])[:2] + 1
eye_px = sorted([cen[i] for i in big if st[i, cv2.CC_STAT_AREA] > 200], key=lambda c: c[0])
eye_px = [e for e in eye_px if e[1] > ph.shape[0] * 0.25][:2]   # skip the yellow horns at the top
n, lab, st, cen = cv2.connectedComponentsWithStats(red.astype(np.uint8))
ri = np.argmax(st[1:, cv2.CC_STAT_AREA]) + 1; snout_px = cen[ri]
snout_mask = lab == ri
# cow-frame landmarks (x, z): eye centres (image left = the costume's own right = -X), snout front centre
mv = MP[mval]; front = mv[mv[:, 1] < mv[:, 1].min() + 0.015]
snout_c = front.mean(0)
src = np.array([[eyes[0][0], eyes[0][2]], [eyes[1][0], eyes[1][2]], [snout_c[0], snout_c[2]]], np.float32)
dst = np.array([eye_px[0], eye_px[1], snout_px], np.float32)
A = cv2.getAffineTransform(src, dst)
# photo classes: 21 black paint, 24 red snout, 25 nostril slits (dark inside the snout's filled outline), else plaster
pcls = np.full(pL.shape, 20, np.uint8)
blue_bg = (pb > pr + 0.05) & (pg > pr)
pcls[(pL < 0.2) & ~blue_bg] = 21
pcls[red] = 24
hull = cv2.morphologyEx(snout_mask.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))).astype(bool)
pcls[hull & (pL < 0.2)] = 25
pcls[hull & ~(pL < 0.2)] = 24
pcls = cv2.medianBlur(pcls, 5)
uv = np.c_[mv[:, 0], mv[:, 2]] @ A[:, :2].T + A[:, 2]
ui = np.clip(uv[:, 0].round().astype(int), 0, pL.shape[1] - 1); vi = np.clip(uv[:, 1].round().astype(int), 0, pL.shape[0] - 1)
pc = pcls[vi, ui]
facing = MN[mval][:, 1] < -0.3
lab_m = np.full(len(mv), 20, np.uint8)
lab_m[facing] = pc[facing]
_, nn = cKDTree(mv[facing]).query(mv[~facing]); lab_m[~facing] = pc[facing][nn]
for c in eyes:
    d = np.linalg.norm(mv - c, axis=1); on = d < eye_r + 0.0015
    lab_m[on] = 22
    fwd = (mv - c) @ np.array([0, -1.0, 0]) / np.maximum(d, 1e-6)
    lab_m[on & (fwd > 0.93)] = 23
mcls[mval] = lab_m
mcls = clean(mcls, mval, 25)
mcls[~mval] = 0
Image.fromarray(mcls).save(f"{OUT}/regions_mask.png"); preview(mcls, f"{OUT}/regions_mask_preview.png")
# check image: the photo's classes with the projected mask outline
chk = np.full(pcls.shape + (3,), 255, np.uint8)
for k, (_, rgb) in CLASSES.items(): chk[pcls == k] = rgb
chk = (0.5 * chk + 0.5 * (ph * 255)).astype(np.uint8)
for u_, v_ in zip(ui[::25], vi[::25]): chk[v_, u_] = (0, 120, 255)
for e in eye_px + [snout_px]: cv2.circle(chk, (int(e[0]), int(e[1])), 6, (255, 0, 255), 2)
Image.fromarray(chk).save(f"{OUT}/mask_photo_projection_check.png")

counts = {CLASSES[k][0]: int((cls == k).sum()) for k in CLASSES if k < 20}
counts.update({CLASSES[k][0]: int((mcls == k).sum()) for k in CLASSES if k >= 20})
json.dump({"classes": {k: v[0] for k, v in CLASSES.items()}, "colours": {k: v[1] for k, v in CLASSES.items()},
           "texel_counts": counts, "photo_landmarks_px": {"eyes": [list(map(float, e)) for e in eye_px], "snout": list(map(float, snout_px))}},
          open(f"{OUT}/regions.json", "w"), indent=1)
for k, v in counts.items(): print(f"{k:24s} {v:10,d}")
print("wrote", OUT)
