#!/usr/bin/env python3
"""
Vector Institute — event name badges.

Carries the "Convergence" venue design onto the badge: the same official
arrow, pixel and plus marks, travelling on the same 67.93 degree axis, over
the brand's category gradient.

Output is one layered PDF per category. Layers are real PDF optional content
groups, artwork is vector, and every text field is live text in Karbon — so the
whole thing stays editable in Illustrator. The supplied reference badge is
placed on the top layer for alignment and can simply be deleted.

    python3 tools/badges.py [outdir]
"""
import math
import os
import re
import sys

import cairosvg
import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Badge geometry — measured from the supplied reference badges
# 549 x 792 px at 144 dpi = 3.8127 x 5.5003 in = 274.5 x 396 pt
# ---------------------------------------------------------------------------

W, H = 274.5, 396.0
CORNER = 14.5

# Lanyard slots. Nothing load-bearing goes above them.
SLOTS = [(16.5, 14.0, 59.5, 24.0), (215.0, 14.0, 258.5, 24.0)]

LOGO_BAND = (46.5, 65.0, 231.0, 101.0)      # x0, y0, x1, y1
NAME_PANEL = (20.5, 130.5, 254.0, 216.0)
ORG_Y = [250.0, 266.0]                       # baselines
PROG_Y = [298.5, 315.0, 331.0]
CAT_Y = 363.0

# ---------------------------------------------------------------------------
# Palette — exact values from the brand guidelines (p6)
# Each category maps onto one of the four official gradient pairings (p7).
# The lighter colour always sits at the top, so body text lands on the darker
# end and stays legible.
# ---------------------------------------------------------------------------

MAGENTA = "#EB088A"
COBALT = "#313CFF"
VIOLET = "#8A25C9"
TURQUOISE = "#48C0D9"
TANGERINE = "#FF9E00"
LIME = "#CFF933"

# The venue piece sits on a near-black ground; the badges inherit it at the top.
GROUND = "#0B0413"

# The logo sits on the light end of every gradient. Measured against the four
# top colours, white runs 1.2:1 (Lime) to 4.3:1 (Magenta) — failing on three of
# four — while black runs 4.9:1 to 17.3:1. Black is an official variant, so the
# category colour can stay pure and full-strength at the top of the badge.
LOGO_INK = "#000000"

# Top band that carries the logo: solid to HEADER_SOLID, gone by HEADER_FADE.
HEADER_SOLID = 100.0
HEADER_FADE = 138.0

# `hold` is how far the dark ground is held before easing into the category
# colour. Tuned per category against a measured contrast target for the white
# logo — the lighter the top colour, the longer the ground has to hold.
CATEGORIES = [
    # id,          label,                    top,        bottom,   hold
    ("student",  "Student",                 MAGENTA,    COBALT,   0.26),
    ("employer", "Employer",                TURQUOISE,  VIOLET,   0.26),
    ("partner",  "Partner",                 LIME,       COBALT,   0.26),
    ("staff",    "Vector Institute Staff",  TANGERINE,  VIOLET,   0.26),
]

# Placeholder copy, verbatim from the reference badges.
NAME_LINES = ["Yastrzhemabsky", "Yastrzhembsky"]
ORG_LINES = ["University/Organization Line 1,", "University/Org Line 2"]
PROG_LINES = [
    "Program/Job Title Line Number 1,",
    "Program/Job Title Line 2,",
    "Line Number 3",
]

NAME_SIZE = 25.0
BODY_SIZE = 12.5

# Which supplied badge goes on the reference layer of which category.
REFERENCE = {
    "student":  "Name Badge Example 4.png",
    "employer": "Name Badge Example 2.png",
    "partner":  "Name Badge Example 3.png",
    "staff":    "Name Badge Example 1.png",
}
SEEDS = {"student": 0x51D, "employer": 0xE99, "partner": 0x9A7, "staff": 0x3C4}

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
# Background — the category gradient
# ---------------------------------------------------------------------------


def background_svg(top, bottom, hold):
    """Category gradient, top-left to bottom-right, as the reference badges run."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="g" x1="0.22" y1="0" x2="0.46" y2="1">
      <stop offset="0" stop-color="{top}"/>
      <stop offset="{hold:.3f}" stop-color="{top}"/>
      <stop offset="0.52" stop-color="{bottom}"/>
      <stop offset="1" stop-color="{bottom}"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" rx="{CORNER}" fill="url(#g)"/>
</svg>'''


def header_svg():
    """The venue's near-black ground, held across the top and faded out.

    Two jobs. It is the most direct quotation of the room — that piece lives on
    near-black — and it is what makes the white logo legible on every category.
    Run straight onto the category colour the way the reference badges do, the
    logo sits at 1.3:1 on Lime and about 1.5:1 on Turquoise and Tangerine.
    """
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="h" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0.00" stop-color="{GROUND}" stop-opacity="0.93"/>
      <stop offset="{HEADER_SOLID/H:.3f}" stop-color="{GROUND}" stop-opacity="0.88"/>
      <stop offset="{HEADER_FADE/H:.3f}" stop-color="{GROUND}" stop-opacity="0"/>
      <stop offset="1.00" stop-color="{GROUND}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" rx="{CORNER}" fill="url(#h)"/>
</svg>'''


# ---------------------------------------------------------------------------
# Pattern — the venue's vocabulary, composed for a portrait badge
# ---------------------------------------------------------------------------


def pattern_svg(seed):
    """The venue vocabulary, recomposed for a portrait badge.

    Same organising idea as the room: everything travels up and to the right on
    the 67.93 degree axis, and a single perspective factor drives size, opacity
    and trail length together so the field funnels rather than just scattering.
    Here the funnel runs from a dense, large bottom-left to a fine, distant
    top-right, which leaves the upper area calm enough for the logo.
    """
    r = rng(seed)
    th = math.radians(FLOW_DEG)
    parts = []

    def depth_at(x, y):
        # 1 at the near (bottom-left) end, 0 at the far (top-right) end.
        u = (x / W) * 0.45 + (1.0 - y / H) * 0.55
        return max(0.0, min(1.0, 1.0 - u))

    def arrow(x, y, h, opacity, long=False):
        src = ARROW_LONG if long else ARROW_REGULAR
        s = h / src["h"]
        parts.append(
            f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})" '
            f'opacity="{opacity:.3f}"><path d="{src["d"]}" fill="#ffffff"/></g>'
        )

    def pixel(x, y, s, opacity):
        parts.append(f'<rect x="{x-s/2:.2f}" y="{y-s/2:.2f}" width="{s:.2f}" '
                     f'height="{s:.2f}" fill="#ffffff" opacity="{opacity:.3f}"/>')

    def plus(x, y, s, opacity):
        b = s * PLUS_BAR / 2
        parts.append(
            f'<g opacity="{opacity:.3f}" fill="#ffffff">'
            f'<rect x="{x-s/2:.2f}" y="{y-b:.2f}" width="{s:.2f}" height="{b*2:.2f}"/>'
            f'<rect x="{x-b:.2f}" y="{y-s/2:.2f}" width="{b*2:.2f}" height="{s:.2f}"/></g>'
        )

    # --- structural arrows: large, soft, anchored low-left and mid-right ----
    for ax, ay, hf, lg in ((-0.10, 1.02, 0.62, False), (0.30, 1.12, 0.78, True),
                           (0.74, 0.86, 0.50, False), (0.98, 1.06, 0.66, True),
                           (0.14, 0.60, 0.34, False), (0.60, 0.42, 0.26, False),
                           (0.90, 0.30, 0.20, False)):
        x, y = ax * W, ay * H
        h = hf * H
        arrow(x - h * 0.18, y - h, h, 0.035 + 0.045 * depth_at(x, y), long=lg)

    # --- mid arrows riding the axis ----------------------------------------
    for _ in range(18):
        x = r() * W * 1.12 - W * 0.06
        y = r() * H * 1.05
        d = depth_at(x, y)
        if r() > 0.30 + 0.70 * d:
            continue
        h = (0.06 + 0.20 * d) * H * (0.7 + 0.6 * r())
        arrow(x - h * 0.18, y - h / 2, h, 0.06 + 0.09 * d)

    # --- official cluster patterns, drawn whole -----------------------------
    for kind, count in ((1, 3), (0, 3)):
        pattern = PLUS_CLUSTER if kind else PIXEL_CLUSTER
        markr = PLUS_CLUSTER_MARK if kind else PIXEL_CLUSTER_MARK
        for _ in range(count):
            cx, cy = r() * W, H * (0.25 + 0.8 * r())
            d = depth_at(cx, cy)
            size = (0.24 + 0.34 * d) * W * (0.7 + 0.5 * r())
            op = 0.08 + 0.11 * d
            for ox, oy in pattern:
                mx, my = cx + ox * size, cy + oy * size
                if -20 < mx < W + 20 and -20 < my < H + 20:
                    (plus if kind else pixel)(mx, my, size * markr, op)

    # --- loose marks, denser and larger toward the near end -----------------
    for _ in range(230):
        x, y = r() * W, r() * H
        d = depth_at(x, y)
        if r() > 0.10 + 0.62 * d:
            continue
        s = (1.8 + 15.0 * d ** 1.7) * (0.55 + 0.9 * r())
        op = 0.05 + 0.13 * d * (0.45 + 0.55 * r())
        (pixel if r() < 0.55 else plus)(x, y, s, op)

    # --- a few crisp near marks for sparkle --------------------------------
    for _ in range(9):
        x, y = r() * W, H * (0.45 + 0.6 * r())
        d = depth_at(x, y)
        s = (5 + 12 * d) * (0.6 + 0.7 * r())
        (pixel if r() < 0.6 else plus)(x, y, s, 0.18 + 0.12 * r())

    # --- motion trails along the travel axis --------------------------------
    for _ in range(34):
        x, y = r() * W, r() * H
        d = depth_at(x, y)
        if r() > 0.2 + 0.8 * d:
            continue
        ln = (16 + 78 * d) * (0.5 + r())
        tw = 0.5 + 1.8 * d
        parts.append(
            f'<g transform="translate({x:.2f} {y:.2f}) rotate({-FLOW_DEG:.3f})">'
            f'<rect x="{-ln:.2f}" y="{-tw/2:.2f}" width="{ln:.2f}" height="{tw:.2f}" '
            f'fill="#ffffff" opacity="{0.04 + 0.08*d:.3f}"/></g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs><clipPath id="badge"><rect x="0" y="0" width="{W}" height="{H}" rx="{CORNER}"/></clipPath></defs>
  <g clip-path="url(#badge)">{''.join(parts)}</g>
</svg>'''


def dieline_svg():
    """Cut outline and lanyard slot punches, on their own layer.

    The supplied reference badges show the slots as filled shapes; for a print
    file they belong as an unfilled die-line so artwork can bleed underneath.
    """
    slots = "".join(
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{(y1-y0)/2}" '
        f'fill="none" stroke="#EB088A" stroke-width="0.5"/>'
        for x0, y0, x1, y1 in SLOTS
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <rect x="0.25" y="0.25" width="{W-0.5}" height="{H-0.5}" rx="{CORNER}"
        fill="none" stroke="#EB088A" stroke-width="0.5"/>
  {slots}
</svg>'''


def scrim_svg():
    # A soft darkening over the lower half only. Keeps white body copy off the
    # lighter end of every gradient without muddying the brand colour up top.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="s" x1="0" y1="0.50" x2="0" y2="0.95">
      <stop offset="0" stop-color="#000000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.26"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" rx="{CORNER}" fill="url(#s)"/>
</svg>'''


def panel_svg():
    x0, y0, x1, y1 = NAME_PANEL
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="7" fill="#ffffff"/>
</svg>'''


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------


def svg_to_pdf(svg, path):
    open(path + ".svg", "w").write(svg)
    cairosvg.svg2pdf(url=path + ".svg", write_to=path)
    return fitz.open(path)


def svg_layer(page, svg, path, oc, rect=None):
    open(path + ".svg", "w").write(svg)
    cairosvg.svg2pdf(url=path + ".svg", write_to=path)
    src = fitz.open(path)
    page.show_pdf_page(rect or page.rect, src, 0, oc=oc)
    src.close()


def build(cat, outdir, tmpdir):
    cid, label, top, bottom, top_stop = cat
    reg = os.path.join(ROOT, "Karbon-Regular.otf")
    semi = os.path.join(ROOT, "Karbon-Semibold.otf")
    if not (os.path.exists(reg) and os.path.exists(semi)):
        raise SystemExit("Karbon fonts not found next to this script")

    doc = fitz.open()
    page = doc.new_page(width=W, height=H)

    oc = {
        "bg":    doc.add_ocg("1 Background gradient", on=True),
        "pat":   doc.add_ocg("2 Brand pattern", on=True),
        "scrim": doc.add_ocg("3 Legibility scrim", on=True),
        "logo":  doc.add_ocg("4 Vector logo", on=True),
        "panel": doc.add_ocg("5 Name panel", on=True),
        "text":  doc.add_ocg("6 Text fields", on=True),
        "die":   doc.add_ocg("7 Die-line (cut + slot punches)", on=True),
        "ref":   doc.add_ocg("8 REFERENCE TEMPLATE - delete", on=True),
    }
    t = lambda n: os.path.join(tmpdir, f"{cid}_{n}.pdf")

    svg_layer(page, background_svg(top, bottom, top_stop), t("bg"), oc["bg"])
    svg_layer(page, pattern_svg(SEEDS[cid]), t("pat"), oc["pat"])
    svg_layer(page, scrim_svg(), t("scrim"), oc["scrim"])
    lx0, ly0, lx1, ly1 = LOGO_BAND
    svg_layer(page, logo_svg(lx1 - lx0, ly1 - ly0), t("logo"), oc["logo"],
              rect=fitz.Rect(lx0, ly0, lx1, ly1))
    svg_layer(page, panel_svg(), t("panel"), oc["panel"])

    # ---- text: real Karbon glyphs, centred using true font metrics --------
    f_semi = fitz.Font(fontfile=semi)
    dark = fitz.TextWriter(page.rect)
    light = fitz.TextWriter(page.rect)

    def put(writer, text, y, size):
        w = f_semi.text_length(text, fontsize=size)
        writer.append(((W - w) / 2, y), text, font=f_semi, fontsize=size)

    x0, y0, x1, y1 = NAME_PANEL
    put(dark, NAME_LINES[0], y0 + 36.0, NAME_SIZE)
    put(dark, NAME_LINES[1], y0 + 69.0, NAME_SIZE)
    for i, line in enumerate(ORG_LINES):
        put(light, line, ORG_Y[i], BODY_SIZE)
    for i, line in enumerate(PROG_LINES):
        put(light, line, PROG_Y[i], BODY_SIZE)
    put(light, label, CAT_Y, BODY_SIZE)

    dark.write_text(page, color=(0.07, 0.07, 0.09), oc=oc["text"])
    light.write_text(page, color=(1, 1, 1), oc=oc["text"])

    svg_layer(page, dieline_svg(), t("die"), oc["die"])

    # ---- supplied reference badge on the top layer, for alignment ---------
    page.insert_image(page.rect, filename=os.path.join(ROOT, REFERENCE[cid]),
                      oc=oc["ref"], overlay=True)

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
