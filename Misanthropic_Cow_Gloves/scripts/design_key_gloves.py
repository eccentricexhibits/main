"""Annotated design key for the Misanthropic Cow hoof glove.
usage: python3 -I design_key_gloves.py <references_dir> <out_dir>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
F = "/usr/share/fonts/truetype/dejavu/"
fB = lambda s: ImageFont.truetype(F + "DejaVuSans-Bold.ttf", s)
fR = lambda s: ImageFont.truetype(F + "DejaVuSans.ttf", s)

panels = [
    ("REF_A_left_glove_flat_back_of_hand.png", "A · Left glove, empty, toes parted"),
    ("REF_B_worn_side_hoof_almost_closed.png", "B · Worn, toes slightly parted"),
    ("REF_C_worn_hoof_closed_from_above.png", "C · Worn, hoof CLOSED (the 3D target)"),
]
# feature -> [(panel, feature_x, feature_y, badge_x, badge_y)] in the 1536 px reference images
_m = {
    1: [(0, 645, 1150, 250, 1080)],
    2: [(0, 1075, 737, 1330, 640)],
    3: [(1, 560, 690, 470, 250)],
    4: [(0, 584, 384, 290, 330), (0, 891, 400, 1180, 330)],
    5: [(0, 614, 110, 440, 70), (0, 837, 165, 1010, 90)],
    6: [(0, 860, 625, 1180, 560), (1, 768, 880, 640, 1330)],
    7: [(1, 1229, 507, 1390, 380)],
    8: [(1, 1000, 930, 1120, 1330)],
    9: [(0, 600, 1395, 300, 1480)],
    10: [(2, 470, 806, 330, 330), (2, 100, 822, 120, 1130)],
}
legend = [
    (1, "Cream / off-white looped TERRY mitten (like a towel or fluffy sock). Plain: no spots, seams or ribbing.", False),
    (2, "THUMB: separate, terry only, rounded tip. NO hoof and no nail on the thumb.", True),
    (3, "Fingers sit in TWO compartments (index+middle, ring+little) with a soft crease between them.", False),
    (4, "A black CLOVEN HOOF: exactly TWO hard toe caps, one per finger compartment. Not five fingers, not claws.", True),
    (5, "Each toe: straight inner edge along the cleft, curved outer edge, tip leaning in toward the cleft.", False),
    (6, "The toe caps start at a clean straight edge where the terry tucks inside them.", False),
    (7, "Thin raised rim along each toe's edges, catching light-grey highlights.", False),
    (8, "SATIN black paint with soft grey brush-streak highlights. Hard, like painted papier-mache. NOT glossy or metallic.", True),
    (9, "Cuff: plain open edge at the wrist, about as wide as the palm. No fur trim, no ribbing.", False),
    (10, "CLOSED: the two toes touch along a straight cleft and their tips meet in one point, like a cow's hoof.", True),
]

H = 900
ims = []
for fn, _ in panels:
    im = Image.open(os.path.join(SRC, fn)).convert("RGB")
    ims.append(im.resize((H, H), Image.LANCZOS))
K = H / 1536
pad = 40
W = pad * 4 + H * 3
legend_h = 30 + 50 * len(legend)
canvas = Image.new("RGB", (W, 150 + H + 70 + legend_h), (255, 255, 255))
d = ImageDraw.Draw(canvas)
d.text((pad, 34), "THE MISANTHROPIC COW — HOOF GLOVE DESIGN KEY", font=fB(50), fill=(20, 20, 20))
d.text((pad, 98), "One glove (left hand shown). Use this to check every generated view. Ignore dirt marks and photo lighting.",
       font=fR(30), fill=(90, 90, 90))
oy = 150
ox = [pad + i * (H + pad) for i in range(3)]
for i, im in enumerate(ims):
    canvas.paste(im, (ox[i], oy))
    d.rectangle((ox[i], oy, ox[i] + H - 1, oy + H - 1), outline=(215, 215, 215), width=2)
    d.text((ox[i], oy + H + 12), panels[i][1], font=fR(28), fill=(90, 90, 90))

ACC = (0, 110, 210)
def badge(cx, cy, n, r=24):
    d.ellipse((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), fill=(255, 255, 255))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACC)
    t = str(n); f = fB(26 if n < 10 else 22)
    w = d.textlength(t, font=f)
    d.text((cx - w / 2, cy - 16), t, font=f, fill=(255, 255, 255))

for n, pts in _m.items():
    for p, fx, fy, bx, by in pts:
        fx, fy = ox[p] + fx * K, oy + fy * K
        bx, by = ox[p] + bx * K, oy + by * K
        d.line((fx, fy, bx, by), fill=(255, 255, 255), width=7)
        d.line((fx, fy, bx, by), fill=ACC, width=3)
        d.ellipse((fx - 7, fy - 7, fx + 7, fy + 7), fill=ACC, outline=(255, 255, 255), width=2)
for n, pts in _m.items():
    for p, fx, fy, bx, by in pts:
        badge(ox[p] + bx * K, oy + by * K, n)

ly = oy + H + 70
for i, (n, txt, bold) in enumerate(legend):
    y = ly + 10 + i * 50
    badge(pad + 24, y + 18, n, r=21)
    d.text((pad + 66, y + 3), txt, font=(fB(29) if bold else fR(29)), fill=(20, 20, 20))

canvas.save(os.path.join(OUT, "DESIGN_KEY.png"), optimize=True)
print(canvas.size)
