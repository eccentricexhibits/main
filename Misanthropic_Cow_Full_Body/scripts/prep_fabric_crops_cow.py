"""Close crops of each real fabric, white-balanced, to attach to the ChatGPT fabric-tile prompts.
python3 -I prep_fabric_crops_cow.py <extracted_photos_dir> <reference_dir> <out_dir>
"""
import os, sys
import numpy as np
from PIL import Image, ImageOps

SRC, REFD, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
O = "Original Cow Photo Shoot (Proper Body Proportions)/Cow - Original Photo Shoot ({} of 8).jpg".format
X = "Other Costume Reference Materials/"

def load(p): return ImageOps.exif_transpose(Image.open(p)).convert("RGB")
def wb(im, box, target=None):
    a = np.asarray(im).astype(float); H, W, _ = a.shape; x0, y0, x1, y1 = box
    m = np.median(a[int(y0*H):int(y1*H), int(x0*W):int(x1*W)].reshape(-1, 3), 0)
    return Image.fromarray(np.clip(a * ((target or m.max()) / m), 0, 255).astype(np.uint8))
def crop(im, b):
    W, H = im.size; return im.crop((int(b[0]*W), int(b[1]*H), int(b[2]*W), int(b[3]*H)))
def save(im, name, size=768):
    s = size / max(im.size); im = im.resize((max(1, round(im.width*s)), max(1, round(im.height*s))), Image.LANCZOS)
    im.save(os.path.join(OUT, name), optimize=True); print(name, im.size)

o4 = wb(load(os.path.join(SRC, O(4))), (0.19, 0.27, 0.24, 0.33), 228)
o8 = wb(load(os.path.join(SRC, O(8))), (0.36, 0.56, 0.46, 0.62), 228)
o1 = load(os.path.join(SRC, O(1)))
refj = wb(load(os.path.join(REFD, "REF_J_head_front_on_new_photo.webp")), (0.45, 0.22, 0.55, 0.27))

save(crop(o4, (0.155, 0.255, 0.235, 0.335)), "FABRIC_1_white_faux_fur.png")
save(crop(o4, (0.29, 0.235, 0.375, 0.30)), "FABRIC_2_black_shag_fur.png")
save(crop(o4, (0.215, 0.045, 0.30, 0.105)), "FABRIC_3_pink_fleece_udder.png")
save(crop(o8, (0.48, 0.80, 0.60, 0.87)), "FABRIC_4_beige_satin.png")
save(crop(o8, (0.40, 0.78, 0.46, 0.83)), "FABRIC_5_beige_lace.png")
save(crop(o4, (0.20, 0.47, 0.27, 0.54)), "FABRIC_6_black_leggings.png")
save(crop(o4, (0.365, 0.535, 0.445, 0.605)), "FABRIC_7_white_fabric_paint_spot.png")
save(crop(o1, (0.15, 0.53, 0.25, 0.62)), "FABRIC_8_white_knit_glove.png")
save(crop(load(os.path.join(SRC, X + "IMG_6681.JPG")), (0.45, 0.33, 0.59, 0.39)), "FABRIC_9_cracked_white_plaster_mask.png")
save(crop(refj, (0.45, 0.49, 0.60, 0.57)), "FABRIC_10_red_flocked_snout.png")
