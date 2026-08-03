#!/usr/bin/env python3
"""
Vector Institute — event name badges, "Trajectory".

A slice of the Convergence venue piece rather than a tinted card: the room's
near-black ground, a luminous wedge of the category's gradient driving up and
right on the same 67.93 degree axis, and the official arrow, pixel and plus
marks streaming out of it.

Built to the supplied print template — 4.0625 x 5.75 in bleed, 3.8125 x 5.5 in
trim, 3.4375 x 4.75 in safe area, dual slot punches.

Output is one layered PDF per category. Layers are real PDF optional content
groups, artwork is vector, and every text field is live Karbon text.

    python3 tools/badges.py [outdir]
"""
import math
import os
import sys

import cairosvg
import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = "Name Badge Template - 3.8125 x 5.5 - Dual Slot Template (3).pdf"

# ---------------------------------------------------------------------------
# Print geometry — measured from the supplied template, in points
# ---------------------------------------------------------------------------

W, H = 292.50, 414.00                 # bleed = page size
TRIM = (9.0, 9.0, 283.5, 405.0)       # 3.8125 x 5.5 in
SAFE = (22.5, 49.5, 270.5, 391.5)     # 3.4375 x 4.75 in
CORNER = 18.0                         # tag-edge corner radius
SLOTS = [(24.75, 22.5, 69.75, 33.75), (223.25, 22.5, 268.25, 33.75)]

SX0, SY0, SX1, SY1 = SAFE
SAFE_W = SX1 - SX0

# ---------------------------------------------------------------------------
# Palette — exact values from the brand guidelines (p6). Each category is one
# of the four official gradient pairings (p7).
# ---------------------------------------------------------------------------

MAGENTA = "#EB088A"
COBALT = "#313CFF"
VIOLET = "#8A25C9"
TURQUOISE = "#48C0D9"
TANGERINE = "#FF9E00"
LIME = "#CFF933"

GROUND = "#080310"        # the venue's near-black ground
GROUND_HI = "#150A24"     # a touch of lift so the card is not flat black

CATEGORIES = [
    # id,          label,                     near colour, far colour
    ("student",  "Student",                  MAGENTA,   COBALT),
    ("employer", "Employer",                 TURQUOISE, VIOLET),
    ("partner",  "Partner",                  LIME,      COBALT),
    ("staff",    "Vector Institute Staff",   TANGERINE, VIOLET),
]

# Placeholder copy, verbatim from the reference badges.
NAME_LINES = ["Yastrzhemabsky", "Yastrzhembsky"]
ORG_LINES = ["University/Organization Line 1,", "University/Org Line 2"]
PROG_LINES = [
    "Program/Job Title Line Number 1,",
    "Program/Job Title Line 2,",
    "Line Number 3",
]

# ---------------------------------------------------------------------------
# Layout — left aligned, name dominant, category on a chip at the foot
# ---------------------------------------------------------------------------

LOGO_XY = (SX0, 56.0)
LOGO_SIZE = (150.0, 29.0)

WEDGE_L = 170.0           # wedge lower edge, at the left edge of the bleed
WEDGE_R = 200.0           # ...and at the right edge

NAME_MAX = 27.0
NAME_Y = [230.0, 260.0]
BODY = 10.2
ORG_Y = [290.0, 304.0]
PROG_Y = [326.0, 340.0, 354.0]

CHIP_TOP = 366.0
CHIP_H = 25.0
CHIP_PAD = 11.0

FLOW_DEG = 67.93          # the venue's travel axis, kept so the two pieces agree

# Ink colours
INK_NAME = (1.0, 1.0, 1.0)
INK_BODY = (0.86, 0.85, 0.90)
# The logo sits on the wedge, i.e. on the category's own colour. Measured
# against the four: white runs 1.22:1 on Lime and about 2.1:1 on Turquoise and
# Tangerine, failing three of four; black runs 4.93:1 to 17.25:1. Both are
# official variants.
LOGO_INK = "#000000"

SEEDS = {"student": 0x51D, "employer": 0xE99, "partner": 0x9A7, "staff": 0x3C4}


def rng(seed):
    state = seed & 0xFFFFFFFF

    def nxt():
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        x = state
        x = ((x ^ (x >> 15)) * (1 | x)) & 0xFFFFFFFF
        x = (x + (((x ^ (x >> 7)) * (61 | x)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        x ^= x >> 14
        return (x & 0xFFFFFFFF) / 4294967296.0

    return nxt


# ---------------------------------------------------------------------------
# Official shape geometry (verbatim from the supplied SVGs)
# ---------------------------------------------------------------------------

ARROW_REGULAR = dict(
    w=422.98, h=600.0,
    d=("M308.51,0 L46.97,114.42 L0,224.04 L208.02,137.79 L68.91,480.94 "
       "L67.58,484.26 L113.86,600 L286.24,169.06 L376.67,375.07 L422.98,267.08 Z"),
)
ARROW_LONG = dict(
    w=537.23, h=1080.0,
    d=("M463.33,0l-168.9,73.89-29.33,69.19,133.39-53.47L0,1079.82l62.23.18"
       "L448.81,109.21l59.1,131.81,29.33-69.78L463.33,0Z"),
)
PLUS_BAR = 14.99 / 72.85

PLUS_CLUSTER = [
    (-0.22296, -0.32210), (-0.46627, -0.26571), (0.46627, -0.21670),
    (-0.34143, -0.19826), (-0.00794, -0.15883), (0.23622, -0.10344),
    (-0.31760, -0.03868), (0.11288, -0.03599), (-0.17161, 0.03146),
    (-0.28572, 0.11805), (-0.05794, 0.19658), (0.05583, 0.28149),
    (-0.15158, 0.32210),
]
PLUS_CLUSTER_MARK = 0.06745

PIXEL_CLUSTER = [
    (-0.24316, -0.38434), (-0.17375, -0.38434), (0.17333, -0.38434),
    (-0.46529, -0.36141), (-0.10434, -0.31492), (0.10391, -0.31492),
    (0.24275, -0.31492), (-0.39588, -0.29200), (-0.03492, -0.24550),
    (0.17333, -0.24550), (0.24275, -0.24550), (-0.46529, -0.22258),
    (-0.03492, -0.17609), (0.03450, -0.17609), (0.17333, -0.17609),
    (-0.39588, -0.15316), (-0.03492, -0.10667), (0.10391, -0.10667),
    (0.32646, -0.10158), (0.39587, -0.03216), (0.03542, 0.03725),
    (0.17425, 0.03725), (0.24367, 0.03725), (0.46529, 0.03725),
    (0.10484, 0.10667), (0.17425, 0.10667), (0.31309, 0.10667),
    (-0.03400, 0.17609), (0.17425, 0.17609), (0.24367, 0.17609),
    (0.03542, 0.24550), (0.31309, 0.24550), (-0.03400, 0.31492),
    (0.03542, 0.38434),
]
PIXEL_CLUSTER_MARK = 0.06942

FLOW_DEG = 67.93  # the venue's travel axis, kept here so the two pieces agree

# ---------------------------------------------------------------------------
# Deterministic randomness, so a rerun reproduces the same badge exactly
# ---------------------------------------------------------------------------


def rng(seed):
    state = seed & 0xFFFFFFFF

    def nxt():
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        x = state
        x = ((x ^ (x >> 15)) * (1 | x)) & 0xFFFFFFFF
        x = (x + (((x ^ (x >> 7)) * (61 | x)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        x ^= x >> 14
        return (x & 0xFFFFFFFF) / 4294967296.0

    return nxt


# ---------------------------------------------------------------------------
# Logo — horizontal lockup, all white, built from the official SVG
#
# The supplied artwork is the vertical lockup. Icon and wordmark are separated
# with clip paths rather than by editing the paths, so the official outlines
# are used untouched; only their arrangement changes, which the guidelines
# allow ("use your best judgement between horizontal and vertical").
# ---------------------------------------------------------------------------

ICON_BOX = (720.0, 48.0, 2370.0, 1894.0)     # measured by rendering
WORD_BOX = (48.0, 2183.0, 2948.0, 2652.0)


def logo_svg(width_pt, height_pt):
    src = open(os.path.join(ROOT, "Official Vector Logo.svg")).read()
    body = src[src.index("<polygon"):src.rindex("</svg>")]
    gi = body.index("<g>")
    icon_body, word_body = body[:gi], body[gi:]

    iw = ICON_BOX[2] - ICON_BOX[0]
    ih = ICON_BOX[3] - ICON_BOX[1]
    ww = WORD_BOX[2] - WORD_BOX[0]
    wh = WORD_BOX[3] - WORD_BOX[1]

    # Icon full height; wordmark set to 70% of it, both vertically centred,
    # with a gap of a third of the icon width. This reproduces the 5.1:1
    # proportion of the reference lockup.
    ih_t = height_pt
    iw_t = iw / ih * ih_t
    wh_t = height_pt * 0.70
    ww_t = ww / wh * wh_t
    gap = iw_t * 0.34
    total = iw_t + gap + ww_t
    scale = min(1.0, width_pt / total)
    iw_t, ih_t, ww_t, wh_t, gap = (v * scale for v in (iw_t, ih_t, ww_t, wh_t, gap))
    total *= scale
    x0 = (width_pt - total) / 2

    si = ih_t / ih
    sw = wh_t / wh
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width_pt}pt" height="{height_pt}pt"
     viewBox="0 0 {width_pt} {height_pt}">
  <defs>
    <clipPath id="cw"><rect x="{WORD_BOX[0]}" y="2100" width="{ww+200}" height="{wh+200}"/></clipPath>
    <clipPath id="ci"><rect x="0" y="0" width="3000" height="2100"/></clipPath>
    <style>.st0,.st1{{fill:{LOGO_INK}}}</style>
  </defs>
  <g transform="translate({x0} {(height_pt-ih_t)/2}) scale({si}) translate({-ICON_BOX[0]} {-ICON_BOX[1]})">
    <g clip-path="url(#ci)">{icon_body}{word_body}</g>
  </g>
  <g transform="translate({x0+iw_t+gap} {(height_pt-wh_t)/2}) scale({sw}) translate({-WORD_BOX[0]} {-WORD_BOX[1]})">
    <g clip-path="url(#cw)">{word_body}</g>
  </g>
</svg>'''




# ---------------------------------------------------------------------------
# Artwork
# ---------------------------------------------------------------------------

TH = math.radians(FLOW_DEG)
DIRX, DIRY = math.cos(TH), -math.sin(TH)          # travel axis, up and right
PERPX, PERPY = math.sin(TH), math.cos(TH)


def _axis(dx, dy):
    """Endpoints of a gradient axis in user space, spanning the whole card."""
    ts = [x * dx + y * dy for x in (0, W) for y in (0, H)]
    lo, hi = min(ts), max(ts)
    return (lo * dx, lo * dy, hi * dx, hi * dy)


def wedge_points():
    """The wedge: full bleed width, slanted lower edge falling to the right so
    it runs across the travel axis rather than square to the card."""
    return f"0,0 {W},0 {W},{WEDGE_R} 0,{WEDGE_L}"


def ground_svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="gr" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="{GROUND_HI}"/>
      <stop offset="1" stop-color="{GROUND}"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" fill="url(#gr)"/>
</svg>'''


def wedge_svg(near, far):
    # Diagonal across the wedge rather than along the travel axis: it keeps the
    # category's own colour dominant at the top, where the badge is read from
    # across a room, with the paired colour arriving at the far corner.
    x1, y1, x2, y2 = 0.0, 0.0, W * 0.92, WEDGE_R * 1.15
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="cg" gradientUnits="userSpaceOnUse"
                    x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}">
      <stop offset="0" stop-color="{near}"/>
      <stop offset="0.50" stop-color="{near}"/>
      <stop offset="1" stop-color="{far}"/>
    </linearGradient>
  </defs>
  <polygon points="{wedge_points()}" fill="url(#cg)"/>
</svg>'''


def logo_clear(x, y):
    """Fade marks sitting behind the lockup.

    The wedge marks are the same white-ish shapes as the logo, so anything
    dense behind it competes directly with the letterforms. Returns a
    multiplier: near zero under the lockup, 1 well clear of it.
    """
    lx, ly = LOGO_XY
    lw, lh = LOGO_SIZE
    cx, cy = lx + lw / 2, ly + lh / 2
    d = math.hypot((x - cx) / (lw * 0.82), (y - cy) / (lh * 2.6))
    return min(1.0, max(0.10, (d - 0.55) / 0.60))


def marks_svg(seed, near, far, in_wedge):
    """Official marks streaming on the travel axis.

    Drawn twice: once inside the wedge in the ground colour, knocking holes in
    the colour, and once outside it in the category colours, so the field reads
    as continuous across the wedge edge the way the room's does.
    """
    r = rng(seed)
    parts = []
    ink = GROUND if in_wedge else near

    def depth_at(x, y):
        u = (x / W) * 0.4 + (1 - y / H) * 0.6
        return max(0.0, min(1.0, 1.0 - u))

    fade = logo_clear if in_wedge else (lambda x, y: 1.0)

    def arrow(x, y, h, op, long=False):
        s = ARROW_LONG if long else ARROW_REGULAR
        op *= fade(x, y + h * 0.5)
        k = h / s["h"]
        parts.append(f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.5f})" '
                     f'opacity="{op:.3f}"><path d="{s["d"]}" fill="{ink}"/></g>')

    def pixel(x, y, s, op):
        op *= fade(x, y)
        parts.append(f'<rect x="{x-s/2:.2f}" y="{y-s/2:.2f}" width="{s:.2f}" '
                     f'height="{s:.2f}" fill="{ink}" opacity="{op:.3f}"/>')

    def plus(x, y, s, op):
        op *= fade(x, y)
        b = s * PLUS_BAR / 2
        parts.append(f'<g opacity="{op:.3f}" fill="{ink}">'
                     f'<rect x="{x-s/2:.2f}" y="{y-b:.2f}" width="{s:.2f}" height="{b*2:.2f}"/>'
                     f'<rect x="{x-b:.2f}" y="{y-s/2:.2f}" width="{b*2:.2f}" height="{s:.2f}"/></g>')

    ymax = WEDGE_R + 40 if in_wedge else H
    base_op = 0.22 if in_wedge else 0.26

    # hero arrows breaking the wedge edge
    for ax, ay, hf, lg in ((0.06, 1.30, 0.72, True), (0.44, 1.05, 0.52, False),
                           (0.78, 1.34, 0.66, True), (0.96, 0.92, 0.44, False)):
        x, y = ax * W, ay * (WEDGE_R + 60)
        h = hf * H * 0.62
        arrow(x - h * 0.18, y - h, h, base_op * (0.22 + 0.20 * depth_at(x, y)), long=lg)

    for _ in range(14 if in_wedge else 7):
        x, y = r() * W, r() * ymax
        d = depth_at(x, y)
        if r() > 0.25 + 0.75 * d:
            continue
        h = (0.06 + 0.18 * d) * H * (0.7 + 0.6 * r())
        arrow(x - h * 0.18, y - h / 2, h, base_op * (0.30 + 0.40 * d))

    for kind, count in ((1, 3), (0, 2)):
        pat = PLUS_CLUSTER if kind else PIXEL_CLUSTER
        mk = PLUS_CLUSTER_MARK if kind else PIXEL_CLUSTER_MARK
        for _ in range(count):
            cx, cy = r() * W, r() * ymax
            d = depth_at(cx, cy)
            size = (0.22 + 0.30 * d) * W * (0.7 + 0.5 * r())
            op = base_op * (0.40 + 0.45 * d)
            for ox, oy in pat:
                mx, my = cx + ox * size, cy + oy * size
                if -20 < mx < W + 20 and -20 < my < H + 20:
                    (plus if kind else pixel)(mx, my, size * mk, op)

    for _ in range(200 if in_wedge else 120):
        x, y = r() * W, r() * ymax
        d = depth_at(x, y)
        if r() > 0.10 + 0.80 * d:
            continue
        s = (1.8 + 13.0 * d ** 1.7) * (0.55 + 0.9 * r())
        (pixel if r() < 0.55 else plus)(x, y, s, base_op * (0.35 + 0.55 * d * r()))

    for _ in range(24 if in_wedge else 12):
        x, y = r() * W, r() * ymax
        d = depth_at(x, y)
        if r() > 0.2 + 0.8 * d:
            continue
        ln = (16 + 70 * d) * (0.5 + r())
        tw = 0.5 + 1.7 * d
        parts.append(f'<g transform="translate({x:.2f} {y:.2f}) rotate({-FLOW_DEG:.3f})">'
                     f'<rect x="{-ln:.2f}" y="{-tw/2:.2f}" width="{ln:.2f}" height="{tw:.2f}" '
                     f'fill="{ink}" opacity="{base_op*(0.30+0.40*d)*fade(x, y):.3f}"/></g>')

    # The travel axis thins toward the top right, and on some seeds that corner
    # empties out completely. A light scatter of far-field marks keeps it alive
    # without touching the density anywhere else.
    if in_wedge:
        for _ in range(22):
            x = W * (0.52 + 0.50 * r())
            y = WEDGE_L * (0.06 + 0.52 * r())
            sz = (1.6 + 3.4 * r()) * (0.7 + 0.6 * r())
            (pixel if r() < 0.5 else plus)(x, y, sz, base_op * (0.30 + 0.35 * r()))

    clip = (f'<clipPath id="c"><polygon points="{wedge_points()}"/></clipPath>' if in_wedge
            else f'<clipPath id="c"><path d="M0,0 H{W} V{H} H0 Z M0,{WEDGE_L} L{W},{WEDGE_R} '
                 f'L{W},0 L0,0 Z" clip-rule="evenodd"/></clipPath>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>{clip}</defs>
  <g clip-path="url(#c)">{''.join(parts)}</g>
</svg>'''


def chip_svg(near, width):
    y = CHIP_TOP
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <rect x="{SX0}" y="{y:.2f}" width="{width:.2f}" height="{CHIP_H}" fill="{near}"/>
</svg>'''


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------


def svg_layer(page, svg, path, oc, rect=None):
    open(path + ".svg", "w").write(svg)
    cairosvg.svg2pdf(url=path + ".svg", write_to=path)
    src = fitz.open(path)
    page.show_pdf_page(rect or page.rect, src, 0, oc=oc)
    src.close()


def fit(font, text, size, maxw):
    """Shrink until the line fits the safe width — names vary a lot."""
    while size > 8 and font.text_length(text, fontsize=size) > maxw:
        size -= 0.25
    return size


def build(cat, outdir, tmpdir):
    cid, label, near, far = cat
    semi = os.path.join(ROOT, "Karbon-Semibold.otf")
    reg = os.path.join(ROOT, "Karbon-Regular.otf")
    if not (os.path.exists(semi) and os.path.exists(reg)):
        raise SystemExit("Karbon fonts not found in the repository root")

    doc = fitz.open()
    page = doc.new_page(width=W, height=H)
    oc = {k: doc.add_ocg(n, on=True) for k, n in (
        ("ground", "1 Ground"),
        ("marks_o", "2 Brand marks (ground)"),
        ("wedge", "3 Category wedge"),
        ("marks_w", "4 Brand marks (wedge)"),
        ("logo", "5 Vector logo"),
        ("chip", "6 Category chip"),
        ("text", "7 Text fields"),
        ("tmpl", "8 Print template (trim / safe / slots)"),
    )}
    t = lambda n: os.path.join(tmpdir, f"{cid}_{n}.pdf")

    svg_layer(page, ground_svg(), t("ground"), oc["ground"])
    svg_layer(page, marks_svg(SEEDS[cid], near, far, False), t("mo"), oc["marks_o"])
    svg_layer(page, wedge_svg(near, far), t("wedge"), oc["wedge"])
    svg_layer(page, marks_svg(SEEDS[cid] ^ 0x1234, near, far, True), t("mw"), oc["marks_w"])

    lx, ly = LOGO_XY
    lw, lh = LOGO_SIZE
    svg_layer(page, logo_svg(lw, lh), t("logo"), oc["logo"], rect=fitz.Rect(lx, ly, lx + lw, ly + lh))

    f_semi = fitz.Font(fontfile=semi)
    chip_w = f_semi.text_length(label.upper(), fontsize=11) + 2.6 * 11 * 0.06 * len(label) + CHIP_PAD * 2
    chip_w = min(chip_w, SAFE_W)
    svg_layer(page, chip_svg(near, chip_w), t("chip"), oc["chip"])

    # ---- text -------------------------------------------------------------
    tw_name = fitz.TextWriter(page.rect)
    tw_body = fitz.TextWriter(page.rect)
    tw_chip = fitz.TextWriter(page.rect)

    size = min(fit(f_semi, NAME_LINES[0], NAME_MAX, SAFE_W),
               fit(f_semi, NAME_LINES[1], NAME_MAX, SAFE_W))
    for i, line in enumerate(NAME_LINES):
        tw_name.append((SX0, NAME_Y[i]), line, font=f_semi, fontsize=size)
    for i, line in enumerate(ORG_LINES):
        tw_body.append((SX0, ORG_Y[i]), line, font=f_semi,
                       fontsize=fit(f_semi, line, BODY, SAFE_W))
    for i, line in enumerate(PROG_LINES):
        tw_body.append((SX0, PROG_Y[i]), line, font=f_semi,
                       fontsize=fit(f_semi, line, BODY, SAFE_W))

    # chip label: uppercase, letter-spaced by hand since TextWriter has no tracking
    cs = 11.0
    cx = SX0 + CHIP_PAD
    cy = CHIP_TOP + CHIP_H / 2 + cs * 0.34
    track = cs * 0.06
    for ch in label.upper():
        tw_chip.append((cx, cy), ch, font=f_semi, fontsize=cs)
        cx += f_semi.text_length(ch, fontsize=cs) + track

    tw_name.write_text(page, color=INK_NAME, oc=oc["text"])
    tw_body.write_text(page, color=INK_BODY, oc=oc["text"])
    tw_chip.write_text(page, color=(0.03, 0.01, 0.06), oc=oc["text"])

    # ---- supplied print template, on top ----------------------------------
    tmpl = fitz.open(os.path.join(ROOT, TEMPLATE))
    page.show_pdf_page(page.rect, tmpl, 0, oc=oc["tmpl"])
    tmpl.close()

    out = os.path.join(outdir, f"vector-badge-{cid}.pdf")
    doc.save(out, garbage=3, deflate=True)
    doc.close()
    return out


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out", "badges")
    tmpdir = os.path.join(outdir, ".layers")
    os.makedirs(tmpdir, exist_ok=True)
    for cat in CATEGORIES:
        print("wrote", build(cat, outdir, tmpdir))


if __name__ == "__main__":
    main()
