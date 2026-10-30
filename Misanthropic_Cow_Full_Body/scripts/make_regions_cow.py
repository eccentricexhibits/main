"""Stage 9c: per-texel material regions for the LOW cow and the scanned mask (after the slipper project's make_masks.py).

python3 -I make_regions_cow.py <bake_dir> <fit.json> <swaps.json> <horns.json> <REF_J photo> <out_dir>

Body atlas (Cow_LOW, 4K): from the baked Tripo colour, the per-texel position/normal and the part id.
  - parts: socks, tail cord, wire tuft are their own classes; the horns are yellow with black rings placed by
    arc length along each horn's centreline (long horn 3 rings, short horn 2);
  - body: hands (20 cm from the fingertip along the arm) -> white knit / black hooves (dark); the bloomers band is
    found per azimuth around the hips (the height range where Tripo's colour is mostly beige) -> satin at front and
    back, lace on the side panels; below it -> black leggings / white paint spots (light, not beige); gold on the lower back -> bow;
    pink above the belly -> udder; dark above the bloomers -> black shag; everything else -> white fur.
  - clean-up: specks smaller than ~1 cm^2 are absorbed into their surroundings.
Mask with face=tripo (the user's choice): Tripo's face, inside the real mask's outline (mask_footprint.npz from
  build_swaps_cow.py), on the body atlas; classes from Tripo's painted colours: black paint, red snout (with its dark
  slits), yellow eyes (with dark pupils), white plaster.
Mask atlas with face=scan (Mask_LOW, 2K; the first version):
  - eyes and pupils from the scan's bead spheres (yellow bead, black pupil on its front);
  - black paint, red flocked snout and the two nostril slits from REF_J (front-on photo), projected orthographically
    with an affine fit on three landmarks (both eyes, snout centre); the snout oval and the slits are measured on
    the photo (SNOUT_C, SNOUT_AX, SLITS); below the snout's lower edge the photo shows the costume, so those texels, and texels that face
    sideways, take the class of the nearest front-facing texel that has a photo class.
Writes regions_cow.png (/ regions_mask.png with face=scan) (class ids), colour-coded previews, and regions.json (classes, counts).
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


def uv_coverage(obj, size, grow=8):
    """Texels covered by the mesh's UV triangles (+ the bake margin). Bake alpha is 1 everywhere, so it can't say this."""
    import trimesh
    m = trimesh.load(obj, process=False, force="mesh")
    t = m.visual.uv[m.faces]
    pts = np.stack([t[..., 0] * size, (1 - t[..., 1]) * size], -1)
    img = np.zeros((size, size), np.uint8)
    cv2.fillPoly(img, [np.round(q * 4).astype(np.int32) for q in pts], 1, lineType=cv2.LINE_8, shift=2)
    return cv2.dilate(img, np.ones((2 * grow + 1, 2 * grow + 1), np.uint8)).astype(bool)


def clean(cls, valid, min_px):
    """Absorb connected specks smaller than min_px: drop them, then fill each dropped texel from the nearest kept one."""
    from scipy.ndimage import distance_transform_edt
    keep = valid.copy()
    for c in np.unique(cls[valid]):
        n, lab, st, _ = cv2.connectedComponentsWithStats((cls == c).astype(np.uint8), connectivity=8)
        small = np.r_[False, st[1:, cv2.CC_STAT_AREA] < min_px]
        keep &= ~small[lab]
    _, (iy, ix) = distance_transform_edt(~keep, return_indices=True)
    out = cls[iy, ix]; out[~valid] = 0
    return out


def preview(cls, path):
    im = np.full(cls.shape + (3,), 255, np.uint8)
    for k, (_, rgb) in CLASSES.items(): im[cls == k] = rgb
    Image.fromarray(im).save(path)


# ---------------- body atlas ----------------
col = np.asarray(Image.open(f"{BK}/cow_color_4096.png").convert("RGB")).astype(np.float32) / 255
P = np.load(f"{BK}/geom_cow_position.npy"); N = np.load(f"{BK}/geom_cow_normal.npy"); part = np.load(f"{BK}/geom_cow_part.npy")
valid = uv_coverage(f"{BK}/Cow_LOW.obj", part.shape[0])
part = np.where(valid, part, -1)
x, y, z = P[..., 0], P[..., 1], P[..., 2]
r, g, b = col[..., 0], col[..., 1], col[..., 2]; L = col.mean(-1)
dark = L < 0.27
pink = (r > 0.75) & (g > 0.45) & (g < 0.82) & (b > 0.5) & (r - g > 0.12)
gold = (r > 0.47) & (g > 0.31) & (b < 0.75 * g) & (r - b > 0.16)
beige = (r > 0.55) & (g > 0.45) & (b > 0.32) & (r - b > 0.06) & (r - b < 0.35) & ~pink
cls = np.zeros(part.shape, np.uint8)
body = valid & (part == 0)
cls[body] = 1
# gloves: within 20 cm of the fingertip along the arm (A-pose: the arm points out and down at about 45 degrees)
hands = np.zeros_like(body)
for sg in (1, -1):
    arm = body & (sg * x > 0.30) & (z < 1.2)
    d = np.array([sg, 0, -1.0]) / np.sqrt(2); proj = P @ d
    hands |= arm & (proj > proj[arm].max() - 0.20)
# bloomers: per azimuth around the hips, the contiguous height range where the Tripo colour is mostly beige
yc = float(np.median(y[body & (z > 0.72) & (z < 0.88)]))
az = np.arctan2(x, -(y - yc)); NA = 36
ai = ((az + np.pi) / (2 * np.pi) * NA).astype(int) % NA
zi = np.floor((z - 0.60) / 0.01).astype(int); NZ = 36
cand = body & ~hands & (zi >= 0) & (zi < NZ)
tot = np.zeros((NA, NZ)); bei = np.zeros((NA, NZ))
np.add.at(tot, (ai[cand], zi[cand]), 1); np.add.at(bei, (ai[cand], zi[cand]), beige[cand])
frac = bei / np.maximum(tot, 1)
zlo, zhi = np.full(NA, np.nan), np.full(NA, np.nan)
for a in range(NA):
    on = frac[a] > 0.35
    for k in range(1, NZ - 2):                                   # bridge 1-2 bin gaps
        if not on[k] and on[k - 1] and (on[k + 1] or on[min(k + 2, NZ - 1)]): on[k] = True
    best, run = (0, 0, 0), None
    for k in range(NZ + 1):
        if k < NZ and on[k]: run = k if run is None else run
        elif run is not None:
            if k - run > best[0]: best = (k - run, run, k)
            run = None
    if best[0] >= 3: zlo[a], zhi[a] = 0.60 + best[1] * 0.01, 0.60 + best[2] * 0.01
ok_ = ~np.isnan(zlo)
idx = np.arange(NA)
zlo = np.interp(idx, idx[ok_], zlo[ok_], period=NA); zhi = np.interp(idx, idx[ok_], zhi[ok_], period=NA)
med = lambda a: np.array([np.median(np.take(a, range(i - 2, i + 3), mode="wrap")) for i in range(NA)])
zlo, zhi = med(zlo), med(zhi)
print("bloomers band (m): bottom", zlo.min().round(3), "-", zlo.max().round(3), " top", zhi.min().round(3), "-", zhi.max().round(3))
# continuous in azimuth (bin centres, wrapped) so the edges don't stair-step
ctr = (np.arange(NA) + 0.5) / NA * 2 * np.pi - np.pi
zl = np.interp(az, ctr, zlo, period=2 * np.pi); zh = np.interp(az, ctr, zhi, period=2 * np.pi)
torso = np.abs(x) < 0.27                                       # the hanging arms are not bloomers
band = body & ~hands & torso & (z >= zl) & (z < zh)
legs = body & ~hands & (z < zl) & (z < 0.80)
cls[body & dark & (z >= 0.76) & ~hands] = 2
cls[body & pink & (z > 1.0)] = 3
bl = band & ~(gold & (y > 0.05))
cls[bl] = 4
cls[bl & (np.abs(np.sin(az)) > 0.8)] = 5                      # the side panels are lace
cls[legs] = 6
cls[legs & (L > 0.55) & (np.abs(r - b) < 0.1)] = 7            # white paint (not the beige of the bloomers)
cls[hands] = 8
cls[hands & dark] = 9
cls[body & gold & (y > 0.05) & (z > 0.78) & (z < 0.95)] = 10
# the fill cap behind the mask (under the chin, facing forward) is hood fur, not the striped Tripo texels it got
cap = body & (N[..., 1] < -0.5) & (z > 1.29) & (z < 1.42) & (np.abs(x) < 0.09) & (y > -0.07) & (y < 0.0)
cls[cap] = 1
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
TRIPO_FACE = not os.path.exists(f"{BK}/Mask_LOW.obj")
if TRIPO_FACE:
    # face=tripo: the mask is Tripo's own face, inside the real mask's outline (the scan moved onto the head) and in
    # front of its back plane; its classes come from Tripo's painted colours
    fz = np.load(f"{os.path.dirname(SWAPS)}/mask_footprint.npz")
    gi = ((z - fz["z0"]) / fz["grid"]).astype(int); gj = ((x - fz["x0"]) / fz["grid"]).astype(int)
    ok = (gi >= 0) & (gi < fz["fp"].shape[0]) & (gj >= 0) & (gj < fz["fp"].shape[1])
    infp = np.zeros_like(ok); infp[ok] = fz["fp"][gi[ok], gj[ok]]
    mk = body & infp & (y < fz["y_back"] + 0.02) & (z > fz["zmin"] - 0.03) & (z < fz["zmax"])
    redm = mk & (r > 0.40) & (r > 1.6 * g) & (r > 1.3 * b)
    yel = mk & (r > 0.5) & (g > 0.38) & (b < 0.6 * g)
    blk = mk & (L < 0.22)
    cls[mk] = 20
    cls[blk] = 21
    cr = P[redm].mean(0); rr_ = np.percentile(np.linalg.norm(P[redm] - cr, axis=1), 92)
    snout = mk & (np.linalg.norm(P - cr, axis=-1) < rr_)
    cls[snout] = 24
    cls[snout & blk] = 25                                     # the dark slits in the red flock
    for sg in (-1, 1):                                        # each eye: Tripo's yellow, with its dark centre as the pupil
        ys = yel & (sg * x > 0)
        if ys.sum() < 50: continue
        ce = P[ys].mean(0); er = np.percentile(np.linalg.norm(P[ys] - ce, axis=1), 95)
        eye = mk & (np.linalg.norm(P - ce, axis=-1) < er)
        cls[eye] = 22; cls[eye & blk] = 23
        print(f"eye {'own left' if sg > 0 else 'own right'}: radius {er * 1000:.0f} mm")
    print(f"mask on Tripo's face: {mk.sum():,} texels; snout radius {rr_ * 1000:.0f} mm")
cls = clean(cls, valid, 60)                                    # ~1 cm^2 at this texel density
cls[~valid] = 0
Image.fromarray(cls).save(f"{OUT}/regions_cow.png"); preview(cls, f"{OUT}/regions_cow_preview.png")

# ---------------- mask atlas (face=scan only) ----------------
mcls = None
if not TRIPO_FACE:
    MP = np.load(f"{BK}/geom_mask_position.npy"); MN = np.load(f"{BK}/geom_mask_normal.npy"); mval = uv_coverage(f"{BK}/Mask_LOW.obj", MP.shape[0])
    mcls = np.zeros(mval.shape, np.uint8); mcls[mval] = 20
    eyes = [to_cow(np.array(e["centre"])[None])[0] for e in fit["scan_eye_beads_mm"]]
    # photo landmarks: eye centres = yellow blobs, snout centre = red blob
    ph = np.asarray(Image.open(PHOTO).convert("RGB")).astype(np.float32) / 255
    pr, pg, pb = ph[..., 0], ph[..., 1], ph[..., 2]; pL = ph.mean(-1)
    yel = (pr > 0.45) & (pg > 0.4) & (pb < 0.5 * pg)
    red = (pr > 0.28) & (pr > 1.6 * pg) & (pr > 1.3 * pb)
    # eyes: yellow rings around dark pupils -> close the rings, search only the face band (the horns are yellow too)
    band_ = np.zeros_like(yel); band_[int(ph.shape[0] * 0.28):int(ph.shape[0] * 0.55)] = True
    ye = cv2.morphologyEx((yel & band_).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    n, lab, st, cen = cv2.connectedComponentsWithStats(ye)
    big = np.argsort(-st[1:, cv2.CC_STAT_AREA])[:2] + 1
    eye_px = sorted([cen[i] for i in big], key=lambda c: c[0])
    # the red snout and its two slits, measured on REF_J (px): the slits merge into the shadow under the snout, so
    # they can't be found by thresholds; the slipper project also fixed landmarks by hand on the original photos
    SNOUT_C, SNOUT_AX = (435, 570), (98, 67)
    SLITS = [(377, 543, 397, 627), (449, 543, 474, 627)]
    yy_, xx_ = np.mgrid[:ph.shape[0], :ph.shape[1]]
    snout_mask = ((xx_ - SNOUT_C[0]) / SNOUT_AX[0]) ** 2 + ((yy_ - SNOUT_C[1]) / SNOUT_AX[1]) ** 2 <= 1
    snout_px = np.array(SNOUT_C, float)
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
    hull = snout_mask
    pcls = cv2.medianBlur(pcls, 5)
    pcls[hull] = 24
    for x0, y0, x1, y1 in SLITS: pcls[y0:y1, x0:x1] = 25
    # below the snout's lower edge the photo shows the costume, not the mask: leave it unknown (0)
    pcls[SNOUT_C[1] + SNOUT_AX[1] + 4:, :] = 0
    uv = np.c_[mv[:, 0], mv[:, 2]] @ A[:, :2].T + A[:, 2]
    ui = np.clip(uv[:, 0].round().astype(int), 0, pL.shape[1] - 1); vi = np.clip(uv[:, 1].round().astype(int), 0, pL.shape[0] - 1)
    pc = pcls[vi, ui]
    facing = (MN[mval][:, 1] < -0.3) & (pc > 0)
    lab_m = np.full(len(mv), 20, np.uint8)
    lab_m[facing] = pc[facing]
    _, nn = cKDTree(mv[facing]).query(mv[~facing]); lab_m[~facing] = pc[facing][nn]
    for c, er in zip(eyes, [e["diameter"] / 2000 for e in fit["scan_eye_beads_mm"]]):
        d = np.linalg.norm(mv - c, axis=1); on = d < er + 0.0015
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
counts.update({CLASSES[k][0]: int(((mcls if mcls is not None else cls) == k).sum()) for k in CLASSES if k >= 20})
json.dump({"classes": {k: v[0] for k, v in CLASSES.items()}, "colours": {k: v[1] for k, v in CLASSES.items()},
           "texel_counts": counts, "face": "tripo" if TRIPO_FACE else "scan"},
          open(f"{OUT}/regions.json", "w"), indent=1)
for k, v in counts.items(): print(f"{k:24s} {v:10,d}")
print("wrote", OUT)
