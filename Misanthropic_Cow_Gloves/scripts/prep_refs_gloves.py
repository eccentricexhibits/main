"""Glove reference prep: white-background square cut-outs + detail crops.
usage: python3 -I prep_refs_gloves.py <photo_dir> <out_dir> [job_index]
Each cut-out runs the segmentation model; run one job per process (birefnet at full size
can exhaust 16 GB if several run in one process)."""
import sys, os
import numpy as np
from PIL import Image, ImageOps
from rembg import remove, new_session

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
ONLY = int(sys.argv[3]) if len(sys.argv) > 3 else None
_ses = None
def ses():
    global _ses
    if _ses is None:
        _ses = new_session("birefnet-general")
    return _ses

def load(name, box):
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, name))).convert("RGB")
    W, H = im.size
    return im.crop((int(box[0]*W), int(box[1]*H), int(box[2]*W), int(box[3]*H)))

def neutralise(im, alpha, strength=0.8):
    """White balance on the brightest masked pixels (the cream terry)."""
    a = np.asarray(im).astype(float); m = np.asarray(alpha) > 200
    lum = a.mean(2); sel = m & (lum > np.percentile(lum[m], 85))
    means = a[sel].mean(0)
    # cream target: keep a slight warm tint (R>G>B) like the real fabric in neutral light
    # exposure too: bring the bright terry to ~238 (dim, colour-lit shoots read as grey otherwise)
    target = 238 * np.array([1.0, 0.985, 0.93])
    g = 1 + strength * (target / means - 1)
    return Image.fromarray(np.clip(a * g, 0, 255).astype(np.uint8))

def pad_square(im, size=1536, margin=0.06, bg=(255, 255, 255)):
    w, h = im.size; inner = int(size * (1 - 2 * margin)); s = inner / max(w, h)
    im = im.resize((max(1, int(w*s)), max(1, int(h*s))), Image.LANCZOS)
    c = Image.new("RGB", (size, size), bg); c.paste(im, ((size-im.width)//2, (size-im.height)//2)); return c

def cutout(name, box, out, rot=0, wb=True, keep_largest=True, drop_lavender=False):
    im = load(name, box); im.thumbnail((1600, 1600))
    if drop_lavender:  # a lilac ribbon from the photo shoot lies over the hoof: inpaint it, then segment
        import cv2
        a0 = np.asarray(im); hsv = cv2.cvtColor(a0, cv2.COLOR_RGB2HSV)
        lil = ((hsv[..., 0] > 115) & (hsv[..., 0] < 160) & (hsv[..., 1] > 25) & (hsv[..., 2] > 110)).astype(np.uint8)
        lil = cv2.dilate(lil, np.ones((15, 15), np.uint8))
        im = Image.fromarray(cv2.inpaint(a0, lil, 9, cv2.INPAINT_TELEA))
    rgba = remove(im, session=ses())
    a = rgba.getchannel("A")
    if keep_largest:
        import cv2
        m = (np.asarray(a) > 128).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        if n > 2:
            big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
            keep = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 0.15 * st[big, cv2.CC_STAT_AREA]])
            a = Image.fromarray((np.asarray(a) * keep).astype(np.uint8))
    rgb = neutralise(im, a) if wb else im
    rgba = rgb.convert("RGBA"); rgba.putalpha(a)
    if rot:
        rgba = rgba.rotate(rot, resample=Image.BICUBIC, expand=True)
    bb = rgba.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    rgba = rgba.crop(bb)
    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255)); bg.alpha_composite(rgba)
    sq = pad_square(bg.convert("RGB")); sq.save(os.path.join(OUT, out), optimize=True); print(out)

def detail(name, box, out, size=1024, wb_ref=None):
    im = load(name, box)
    w, h = im.size; s = size / max(w, h)
    im = im.resize((int(w*s), int(h*s)), Image.LANCZOS)
    c = Image.new("RGB", (size, size), (255, 255, 255)); c.paste(im, ((size-im.width)//2, (size-im.height)//2))
    c.save(os.path.join(OUT, out), quality=92); print(out)

L  = "Left Hand Glove - No Hand Inside.jpg"
R  = "Right Hand Glove - No Hand Inside.jpg"

P  = lambda n: f"Original Costume - Glove Reference ({n} of 13).jpg"

# Whole-glove references. Flat-lay gloves rotated so the hoof points UP (cuff at the bottom).
if ONLY in (None, 0): cutout(L,  (0.14, 0.16, 0.97, 0.97), "REF_A_left_glove_flat_back_of_hand.png", rot=-135)
if ONLY in (None, 1): cutout(P(10), (0.15, 0.68, 0.70, 0.95), "REF_B_worn_side_hoof_almost_closed.png", drop_lavender=True)
if ONLY in (None, 2): cutout(P(13), (0.00, 0.05, 0.17, 0.25), "REF_C_worn_hoof_closed_from_above.png")  # stops before the fur sleeve

# Detail crops (photos as they are, not cut out)
if ONLY in (None, 3): detail(P(7),  (0.42, 0.08, 0.65, 0.38), "DETAIL_1_hoof_toes_shape_and_rim.jpg")
if ONLY in (None, 4): detail(P(9),  (0.38, 0.45, 0.52, 0.56), "DETAIL_2_closed_hoof_end_on_cleft.jpg")
if ONLY in (None, 5): detail(P(10), (0.26, 0.74, 0.46, 0.92), "DETAIL_3_terry_loop_texture.jpg")
if ONLY in (None, 6): detail(L,     (0.15, 0.50, 0.55, 0.95), "DETAIL_4_hoof_surface_brush_texture.jpg")
if ONLY in (None, 7): detail(P(13), (0.03, 0.08, 0.19, 0.22), "DETAIL_5_hoof_closed_top_cleft.jpg")
