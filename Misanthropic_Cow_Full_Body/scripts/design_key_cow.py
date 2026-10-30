"""Annotated design key for the full Misanthropic Cow costume.
python3 -I design_key_cow.py <refs_dir> <out_png> [grid]"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
R, OUT = sys.argv[1], sys.argv[2]
GRID = len(sys.argv) > 3
F = "/usr/share/fonts/truetype/dejavu/"
fB = lambda s: ImageFont.truetype(F + "DejaVuSans-Bold.ttf", s)
fR = lambda s: ImageFont.truetype(F + "DejaVuSans.ttf", s)
H = 1300
def fit(name, box=None):
    im = Image.open(os.path.join(R, name)).convert("RGB")
    if box: im = im.crop(box)
    s = H / im.height
    return im.resize((int(im.width*s), H), Image.LANCZOS)
front = fit("REF_A_whole_costume_front_no_overlays.png", (241, 0, 1458, 1536))
head = fit("DETAIL_1_mask_face.png", (100, 0, 960, 1024))
back = fit("REF_E_back_upper_hood_patches_bow.png", (250, 0, 1290, 1536))
pad = 40
panels = [(front, "FRONT (original shoot; ignore the backdrop and wide-angle lens)"), (head, "HEAD / MASK close-up"), (back, "BACK")]
W = sum(p.width for p, _ in panels) + pad*(len(panels)+1)
legend = [
 (1, "Rigid sculpted MASK, white with a cracked plaster texture, set into the fur hood. Heavy, scowling brow ridge.", True),
 (2, "Black cow patches PAINTED on the mask: big one over the mask's own LEFT eye (viewer's right) running to the top; smaller one over the other brow; one beside each side of the muzzle.", False),
 (3, "Glossy YELLOW bead eyes with round black pupils, close together under the brow.", False),
 (4, "Protruding snout ending in a flat oval of RED shaggy/flocked fabric with TWO VERTICAL black slit NOSTRILS. No mouth, teeth or tongue.", True),
 (5, "Two YELLOW horns on a white fur BOLSTER, NOT a matching pair (draw them from DETAIL_3, the original shoot): the costume's own RIGHT horn is short", True),
 (None, "     and ends in a deliberate tuft of twisted bare WIRE; its LEFT horn is a long crescent with an intact POINTED tip (broken in this close-up: don't copy that).", True),
 (6, "White shaggy-fur HOOD, one piece with the top; frames the mask.", False),
 (7, "Black long-shag tuft just under the snout, on the costume's own right (viewer's left).", False),
 (8, "Big PINK fabric UDDER sewn high on the front, just under the snout: two large round lobes side by side, four stubby pink nubs (one sideways, one down per lobe).", True),
 (9, "White long-pile fur TOP: very round, stuffed BELLY, wider than the hips. Hem ends at the hips.", True),
 (10, "Black long-shag cow patches sewn on: big one on the lower belly, small tufts on both flanks, the outer elbows and the back.", False),
 (11, "White knit GLOVES: plain white thumb; two broad, blunt black HOOF halves over the fingers (no claws).", False),
 (12, "Short BEIGE satin BLOOMERS with beige lace side panels, worn over the leggings, showing below the fur hem.", True),
 (13, "BLACK LEGGINGS with irregular WHITE painted cow spots.", False),
 (14, "Small GOLD satin BOW at the centre of the lower back, with a thin white cord TAIL hanging from it.", True),
 (15, "Big black shag patch across the upper back on the costume's own left; smaller patches lower down.", False),
 (16, "Cow SLIPPERS (see DETAIL_13): white plush muzzle with a black smile, cream mop chenille, black fringe.", False),
]
lh = 48
canvas = Image.new("RGB", (W, 150 + H + 60 + 30 + lh*len(legend) + 40), (255, 255, 255))
d = ImageDraw.Draw(canvas)
d.text((pad, 30), "THE MISANTHROPIC COW: FULL COSTUME DESIGN KEY", font=fB(48), fill=(20, 20, 20))
d.text((pad, 92), "One character. Check every generated view against this. Never draw these numbers, lines or text.", font=fR(28), fill=(90, 90, 90))
x = pad; oy = 150; org = {}
for i, (p, cap) in enumerate(panels):
    canvas.paste(p, (x, oy)); org[i] = x
    d.text((x, oy + H + 10), cap, font=fR(22), fill=(90, 90, 90)); x += p.width + pad
if GRID:
    for gx in range(0, W, 50):
        d.line((gx, oy, gx, oy+H), fill=(0, 255, 255) if gx % 100 == 0 else (255, 255, 0), width=1)
        if gx % 100 == 0: d.text((gx+2, oy+2), str(gx), fill=(255, 0, 0), font=fR(16))
    for gy in range(0, H, 50):
        d.line((0, oy+gy, W, oy+gy), fill=(0, 255, 255) if gy % 100 == 0 else (255, 255, 0), width=1)
        if gy % 100 == 0: d.text((2, oy+gy+2), str(gy), fill=(255, 0, 0), font=fR(16))
ACC = (0, 110, 210)
def badge(cx, cy, n, r=24):
    d.ellipse((cx-r-3, cy-r-3, cx+r+3, cy+r+3), fill=(255, 255, 255))
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=ACC)
    t = str(n); f = fB(26 if n < 10 else 22); w = d.textlength(t, font=f)
    d.text((cx - w/2, cy - 15), t, font=f, fill=(255, 255, 255))
# (feature_x, feature_y, badge_x, badge_y) in canvas px, y relative to panel top
MARKS = {}
try:
    from design_key_marks import MARKS
except ImportError:
    pass
for n, pts in MARKS.items():
    for fx, fy, bx, by in pts:
        fy += oy; by += oy
        if (fx, fy) != (bx, by):
            d.line((fx, fy, bx, by), fill=(255, 255, 255), width=7); d.line((fx, fy, bx, by), fill=ACC, width=3)
            d.ellipse((fx-7, fy-7, fx+7, fy+7), fill=ACC, outline=(255, 255, 255), width=2)
        badge(bx, by, n)
ly = oy + H + 60
for i, (n, txt, bold) in enumerate(legend):
    y = ly + i*lh
    if n is not None: badge(pad + 24, y + 18, n, r=20)
    d.text((pad + 62, y + 4), txt, font=(fB(25) if bold else fR(25)), fill=(20, 20, 20))
canvas.save(OUT, optimize=True); print(canvas.size, {i: org[i] for i in org})
