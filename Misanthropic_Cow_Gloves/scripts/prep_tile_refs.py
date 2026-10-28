"""Reference swatches for the two ChatGPT tile prompts (terry, painted hoof). Hoof swatches are rotated so the
brush strokes run vertically, the direction they will run on the toes (base to tip).
usage: python3 -I prep_tile_refs.py <photo_dir> <kit_dir>"""
import sys, os
from PIL import Image, ImageOps
SRC, OUT = sys.argv[1:3]
def load(n): return ImageOps.exif_transpose(Image.open(os.path.join(SRC, n))).convert("RGB")
def crop(im, box): W, H = im.size; return im.crop((int(box[0]*W), int(box[1]*H), int(box[2]*W), int(box[3]*H)))
def rot_square(im, ang, frac=0.62, size=1024):
    r = im.rotate(ang, resample=Image.BICUBIC, expand=False); W, H = r.size; s = int(min(W, H) * frac)
    return r.crop(((W - s)//2, (H - s)//2, (W + s)//2, (H + s)//2)).resize((size, size), Image.LANCZOS)
L = "Left Hand Glove - No Hand Inside.jpg"; P10 = "Original Costume - Glove Reference (10 of 13).jpg"
# A: long brush streaks on the flat glove's toe (strokes run ~40 deg up-right -> rotate 50 deg CCW)
rot_square(crop(load(L), (0.17, 0.52, 0.42, 0.80)), 50).save(os.path.join(OUT, "2_Hoof_paint", "ref_a_brush_strokes.jpg"), quality=93)
# B: satin sheen + grey drag marks on the worn glove's toe (strokes run ~55 deg up-right -> rotate 125 deg CCW)
rot_square(crop(load(P10), (0.455, 0.745, 0.60, 0.80)), 125, frac=0.72).save(os.path.join(OUT, "2_Hoof_paint", "ref_b_satin_sheen.jpg"), quality=93)
# terry: clean loops on the worn glove
t = crop(load(P10), (0.26, 0.75, 0.39, 0.86)); s = min(t.size); t = t.crop((0, 0, s, s)).resize((1024, 1024), Image.LANCZOS)
t.save(os.path.join(OUT, "1_Terry", "ref_a_terry_loops.jpg"), quality=93)
t = crop(load(P10), (0.22, 0.79, 0.30, 0.86)); s = min(t.size); t = t.crop((0, 0, s, s)).resize((1024, 1024), Image.LANCZOS)
t.save(os.path.join(OUT, "1_Terry", "ref_b_terry_closeup.jpg"), quality=93)        # closer in: individual loops
print(sorted(os.listdir(os.path.join(OUT, "1_Terry"))), sorted(os.listdir(os.path.join(OUT, "2_Hoof_paint"))))
