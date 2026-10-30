"""ChatGPT fabric-tile kit (playbook stage 9c, step 1): one folder per fabric with PROMPT.txt and
the real-fabric crop to attach, zipped. python3 -I build_tile_kit_cow.py <fabric_crops_dir> <out_dir>"""
import os, sys, shutil, zipfile

SRC, OUT = sys.argv[1], sys.argv[2]
# (folder, crop file, fabric name, colour, size cm, detail notes, geometry note or None)
TILES = [
 ("TILE_01_white_faux_fur", "FABRIC_1_white_faux_fur.png", "long-pile white faux fur (a slightly matted, lumpy costume fur)", "warm white", 10,
  "Pile about 2-3 cm long, lying mostly in one direction with soft clumps and gentle shading between them. Slightly matted in places, like a well-used costume.", None),
 ("TILE_02_black_shag_fur", "FABRIC_2_black_shag_fur.png", "long black shaggy faux fur", "black with a slight sheen", 10,
  "Long, glossy, slightly wavy strands.", "the 3D model already has the big tufts as shapes. This texture is only the surface of the fur: fine strands lying flat and fuzz, NOT big clumps or tufts"),
 ("TILE_03_pink_fleece", "FABRIC_3_pink_fleece_udder.png", "smooth pink fleece / minky fabric", "soft baby pink", 8,
  "A very short, velvety pile with a faint soft sheen. No pattern, no seams.", None),
 ("TILE_04_beige_satin", "FABRIC_4_beige_satin.png", "smooth beige satin", "pale beige / nude", 8,
  "Fine satin weave with a soft sheen; only the faint weave texture, no folds or wrinkles.", None),
 ("TILE_05_beige_lace", "FABRIC_5_beige_lace.png", "beige floral lace", "pale beige / nude, the same colour as the satin", 8,
  "A fine net background with a dense floral pattern of leaves and petals outlined in thicker threads, like the photo.", None),
 ("TILE_06_black_leggings", "FABRIC_6_black_leggings.png", "black opaque jersey knit (leggings fabric)", "deep black", 6,
  "A very fine knit with tiny vertical ribs, matte, with a faint soft sheen. No paint, no spots.", None),
 ("TILE_07_white_fabric_paint", "FABRIC_7_white_fabric_paint_spot.png", "thick white fabric paint brushed onto black fabric", "off-white", 6,
  "The paint only (filling the whole square): slightly uneven, rough and dry-brushed, with fine cracks and creases and a few thin spots where the black fabric shows through faintly. No edge of the spot, no black background.", None),
 ("TILE_08_white_knit", "FABRIC_8_white_knit_glove.png", "fuzzy white knit (like a chenille or plush sock knit)", "warm white", 6,
  "Small soft loops in neat rows, slightly fuzzy.", None),
 ("TILE_09_cracked_white_plaster", "FABRIC_9_cracked_white_plaster_mask.png", "painted white plaster / papier-mache surface", "clean warm white", 8,
  "Matte white paint over a slightly lumpy surface, with fine hairline cracks and a few tiny chips, like an old hand-made mask. Clean white, not dirty or grey.", None),
 ("TILE_10_red_flocked_snout", "FABRIC_10_red_flocked_snout.png", "shaggy red flocked fabric (short, dense, slightly matted fibres)", "crimson red", 5,
  "Short tangled fibres with darker red in the gaps, a little sparkle. Ignore the two black slits in the photo: no slits, no stitching.", None),
]
TEMPLATE = """Create a seamless, tileable square texture of the {name} in the attached photo. Make it in {colour}.
{geo}
- View: straight down at a flat piece, filling the entire square edge to edge.
- Scale: the square shows about {cm} cm x {cm} cm. {notes}
- Lighting: completely flat and even. No shadows, highlights, shine, vignetting or gradients.
- Nothing else: no seams, stitching, edges, folds, objects or text.
- It must tile seamlessly when repeated left-right and up-down.
- Square image, as large as you can make it."""
FOLLOW = """IF IT'S OFF, paste one of these in the same chat:
- "Flatter, more even light, like a scanned swatch."
- "Keep the same size of detail across the whole square."
- "Only the flat material filling the square, nothing else."
- "Closer in: only the surface texture." """
README = """THE MISANTHROPIC COW: FABRIC TILES FOR CHATGPT
============================================================
Ten fabrics, one NEW ChatGPT chat each. In each folder: PROMPT.txt and the photo to attach.
1. New chat. 2. Attach the photo. 3. Paste the prompt. 4. Download the result and save it with
   the folder's name (e.g. TILE_01_white_faux_fur.png). 5. Send me all ten.
I fix the seams, make the height maps and derive the colour variants myself
(gold satin for the bow from the beige satin, glossy black paint for the mask patches), so
don't worry if a seam shows or a colour is a little off.
Solid colours (yellow horns, eyes, glossy black hooves) need no tile.
"""
os.makedirs(OUT, exist_ok=True)
kit = os.path.join(OUT, "Cow_fabric_tiles_kit"); shutil.rmtree(kit, ignore_errors=True); os.makedirs(kit)
open(os.path.join(kit, "README_START_HERE.txt"), "w").write(README)
for folder, crop, name, colour, cm, notes, geo in TILES:
    d = os.path.join(kit, folder); os.makedirs(d)
    shutil.copy(os.path.join(SRC, crop), os.path.join(d, "1_" + crop))
    g = f"Important: {geo}.\n" if geo else ""
    txt = f"{folder}\n{'=' * 60}\nNEW CHAT. ATTACH: 1_{crop}\nPASTE:\n{'-' * 60}\n" + TEMPLATE.format(name=name, colour=colour, geo=g, cm=cm, notes=notes) + f"\n{'-' * 60}\nSAVE AS: {folder}.png\n\n" + FOLLOW + "\n"
    open(os.path.join(d, "PROMPT.txt"), "w").write(txt)
zp = os.path.join(OUT, "Cow_fabric_tiles_kit.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(kit):
        for f in sorted(files): z.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), OUT))
print(zp, os.path.getsize(zp) // 1024, "KB")
