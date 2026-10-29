"""Prepare colour-corrected, square-padded reference images for the full-body cow kit.

python3 -I prep_refs_cow.py <extracted_photos_dir> <playbook_dir> <out_refs_dir>
"""
import sys, os
import numpy as np
from PIL import Image, ImageOps

SRC, PB, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
ORIG = "Original Cow Photo Shoot (Proper Body Proportions)/Cow - Original Photo Shoot ({} of 8).jpg"
OTHER = "Other Costume Reference Materials/"

def load(rel):
    return ImageOps.exif_transpose(Image.open(os.path.join(SRC, rel))).convert("RGB")

def wb(im, box, target=228, strength=1.0):
    """White-balance on a region that should be white fur / white mask.
    target=None only neutralises the colour cast and keeps the exposure."""
    a = np.asarray(im).astype(float); H, W, _ = a.shape
    x0, y0, x1, y1 = box
    m = np.median(a[int(y0*H):int(y1*H), int(x0*W):int(x1*W)].reshape(-1, 3), 0)
    g = 1 + strength * ((target or m.max()) / m - 1)
    return Image.fromarray(np.clip(a * g, 0, 255).astype(np.uint8))

def crop(im, box):
    W, H = im.size; x0, y0, x1, y1 = box
    return im.crop((int(x0*W), int(y0*H), int(x1*W), int(y1*H)))

def pad_square(im, size=1536, margin=0.0):
    inner = int(size * (1 - 2 * margin)); s = inner / max(im.size)
    im = im.resize((max(1, round(im.width*s)), max(1, round(im.height*s))), Image.LANCZOS)
    c = Image.new("RGB", (size, size), (255, 255, 255))
    c.paste(im, ((size - im.width)//2, (size - im.height)//2)); return c

def save(im, name, size=1536):
    pad_square(im, size).save(os.path.join(OUT, name), optimize=True); print(name)

def ref(rel, box, wbbox, name, size=1536, strength=1.0, target=228):
    im = load(rel)
    if wbbox: im = wb(im, wbbox, target=target, strength=strength)
    save(crop(im, box), name, size)

o = ORIG.format
# --- whole / large references ---
ref(o(8), (0.06, 0.06, 0.99, 1.0), (0.36, 0.56, 0.46, 0.62), "REF_A_whole_costume_front_no_overlays.png")
ref(o(4), (0.0, 0.0, 0.66, 0.93), (0.19, 0.27, 0.24, 0.33), "REF_B_body_front_standing_ORIGINAL_WEARER.png")
ref(o(3), (0.22, 0.08, 0.86, 0.66), (0.48, 0.125, 0.54, 0.145), "REF_C_head_and_torso_front_ORIGINAL_WEARER.png")
ref(o(1), (0.0, 0.02, 1.0, 0.80), None, "REF_D_true_colours_neutral_light.png")
ref(OTHER + "misanthropicCow_bigBatchOfStuff_ (388 of 724).tif (2).jpg", (0.0, 0.0, 1.0, 1.0), (0.45, 0.62, 0.55, 0.72), "REF_E_back_upper_hood_patches_bow.png")
ref(OTHER + "Sequence 01.00_00_49_17.Still008.png", (0.0, 0.05, 1.0, 1.0), (0.35, 0.55, 0.50, 0.62), "REF_F_back_full_body.png")
ref(OTHER + "Sequence 01.00_00_40_08.Still005.png", (0.0, 0.0, 1.0, 0.92), (0.10, 0.35, 0.25, 0.45), "REF_G_side_body_udders_belly.png", strength=0.6)
ref(OTHER + "misanthropicCow_bigBatchOfStuff_ (413 of 724).tif (2).jpg", (0.36, 0.26, 0.74, 0.72), (0.52, 0.55, 0.58, 0.62), "REF_H_head_side_profile.png", target=None)
ref(OTHER + "misCowRyerson.jpg", (0.25, 0.12, 0.82, 0.95), (0.62, 0.42, 0.70, 0.50), "REF_I_whole_look_other_wearer.png")
# --- detail crops ---
ref(OTHER + "IMG_6681.JPG", (0.13, 0.05, 0.82, 0.52), (0.36, 0.22, 0.46, 0.26), "DETAIL_1_mask_face.png", 1024, target=None)
ref(OTHER + "misanthropicCow_bigBatchOfStuff_ (386 of 724).tif.jpg", (0.15, 0.12, 0.85, 0.52), (0.40, 0.17, 0.50, 0.22), "DETAIL_2_mask_face_alt_light.png", 1024, target=None)
ref(OTHER + "IMG_6681.JPG", (0.26, 0.05, 0.84, 0.25), (0.36, 0.22, 0.46, 0.26), "DETAIL_3_horns_on_fur_bolster.png", 1024, target=None)
ref(o(4), (0.14, 0.0, 0.56, 0.17), (0.19, 0.27, 0.24, 0.33), "DETAIL_4_udder_cups_and_teats.png", 1024)
ref(o(1), (0.10, 0.46, 0.34, 0.68), None, "DETAIL_5_glove_with_black_hoof.png", 1024)
ref(o(8), (0.74, 0.03, 0.99, 0.40), (0.36, 0.56, 0.46, 0.62), "DETAIL_6_arm_tuft_and_hoof.png", 1024)
ref(o(4), (0.12, 0.14, 0.58, 0.38), (0.19, 0.27, 0.24, 0.33), "DETAIL_7_belly_and_black_shag_patch.png", 1024)
ref(o(4), (0.13, 0.33, 0.53, 0.48), (0.19, 0.27, 0.24, 0.33), "DETAIL_8_beige_briefs_lace_sides.png", 1024)
ref(o(4), (0.12, 0.40, 0.53, 0.83), (0.19, 0.27, 0.24, 0.33), "DETAIL_9_spotted_leggings.png", 1024)
ref(o(4), (0.12, 0.78, 0.53, 0.93), (0.19, 0.27, 0.24, 0.33), "DETAIL_10_slippers_worn.png", 1024)
ref(OTHER + "misanthropicCow_bigBatchOfStuff_ (388 of 724).tif (2).jpg", (0.30, 0.80, 0.85, 1.0), (0.45, 0.62, 0.55, 0.72), "DETAIL_11_gold_bow_and_cord_tail.png", 1024)
ref(o(8), (0.28, 0.20, 0.64, 0.44), (0.36, 0.56, 0.46, 0.62), "DETAIL_12_chest_tuft_under_muzzle.png", 1024)
# slipper (the real object, from the slipper project)
sl = Image.open(os.path.join(PB, "worked_example/references/REF_A_three-quarter_front.jpg")).convert("RGB")
save(sl, "DETAIL_13_slipper_real_object.png", 1024)
