#!/usr/bin/env python3
"""
Vector Institute — AI Summit 2026 name badges.

Layout is the one that came out of the Concept C review — the category gradient
across the top, the lower two thirds in near-black, the name set large on the
black — carrying the confirmed colour system and the Concept A finish.

The finish is the change that matters here. Marketing reserved the graphic,
textured gradient (arrows, pixels, pluses) for posters and environmental
signage; badges take a smooth gradient. So the mark field that used to stream
across the card is gone, and the top panel is a single clean sweep of the
category's official pairing. At badge scale that is also the better read: the
texture was competing with the name at exactly the distance the badge is used.

Built on the artboard from Concept_3_badges_fixed_2.pdf — 5.8125 x 7.5 in page
with the 3.8125 x 5.5 in tag centred in it, and the die-line carried on its own
reference layer, so these drop straight into the working Illustrator file.

Output is one layered PDF per category plus a combined four-page file. Layers
are real PDF optional content groups, artwork is vector, and every text field is
live Karbon text.

    python3 tools/badges.py [outdir]
"""
import math
import os
import re
import sys
import tempfile

import cairosvg
import fitz
import pikepdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTBOARD = "Concept_3_badges_fixed_2.pdf"

# ---------------------------------------------------------------------------
# Print geometry, in points
#
# The page is the imposition artboard: a 1 in margin around the tag. All the
# artwork below is laid out in *bleed* space (0..W, 0..H) and placed at ORIGIN,
# so the numbers stay the ones printed on the supplied template.
# ---------------------------------------------------------------------------

PAGE_W, PAGE_H = 418.50, 540.00       # 5.8125 x 7.5 in artboard
OX, OY = 63.00, 63.00                 # bleed origin within the artboard

W, H = 292.50, 414.00                 # 4.0625 x 5.75 in bleed
TRIM = (9.0, 9.0, 283.5, 405.0)       # 3.8125 x 5.5 in
SAFE = (22.5, 49.5, 270.5, 391.5)     # 3.4375 x 4.75 in

SX0, SY0, SX1, SY1 = SAFE
SAFE_W = SX1 - SX0

# ---------------------------------------------------------------------------
# Palette — exact values from the brand guidelines (p6)
# ---------------------------------------------------------------------------

MAGENTA = "#EB088A"
COBALT = "#313CFF"
VIOLET = "#8A25C9"
TURQUOISE = "#48C0D9"
TANGERINE = "#FF9E00"
LIME = "#CFF933"

GROUND = "#07030E"        # the room's near-black
GROUND_HI = "#120820"     # a touch of lift so the card is not flat black

# The four official pairings (guidelines p7/p12), assigned per the confirmed
# badge colour system. Every pairing leads with a dark colour, which is what
# lets the reverse logo run on all four.
CATEGORIES = [
    # id,          label,                     from,    to
    ("student",  "Student",                  VIOLET,  TURQUOISE),
    ("employer", "Employer",                 VIOLET,  TANGERINE),
    ("partner",  "Partner",                  COBALT,  LIME),
    ("staff",    "Vector Institute Staff",   MAGENTA, COBALT),
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
LOGO_SIZE = (165.0, 32.0)

# Lower edge of the colour panel, at the left and right edges of the bleed. The
# slant runs with the venue piece's travel axis rather than square to the card.
PANEL_L = 148.0
PANEL_R = 174.0

# Type is sized against the safe width, not to a preset scale: a 14-character
# surname at 36 pt still uses only three quarters of the 248 pt safe line.
NAME_MAX = 36.0
NAME_Y = [206.0, 244.0]
BODY = 13.0
ORG_Y = [276.0, 293.0]
PROG_Y = [316.0, 333.0, 350.0]

CHIP_TOP = 360.0
CHIP_H = 28.0
CHIP_PAD = 12.0
CHIP_RADIUS = 4.5
CHIP_SIZE = 13.0

INK_NAME = (1.0, 1.0, 1.0)
INK_BODY = (0.86, 0.85, 0.90)


# ---------------------------------------------------------------------------
# Ink choice by measured contrast
#
# Both the reverse (white) and black logo lockups are official. Which one to use
# is not a taste call — it is whichever clears the 3:1 graphics floor on the
# colour it actually sits on. Same rule picks the chip label ink.
# ---------------------------------------------------------------------------


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour):
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    r, g, b = (_srgb_to_linear(v) for v in (r, g, b))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def ink_on(hex_colour, floor=4.5):
    """Black or white, whichever reads better on this background."""
    bg = luminance(hex_colour)
    return "#000000" if contrast(bg, 0.0) >= contrast(bg, 1.0) else "#FFFFFF"


def reverse_or_black(hex_colour, floor=3.0):
    """Prefer the reverse (white) lockup, drop to black only if it fails.

    Straight max-contrast would flip the logo to black on Magenta — 4.92:1
    against white's 4.36:1 — and one black lockup in a set of four reads as a
    mistake at a lanyard's distance. White clears the 3:1 graphics floor on all
    four lead colours, so the set stays consistent without anything failing.
    """
    return "#FFFFFF" if contrast(luminance(hex_colour), 1.0) >= floor else "#000000"


# ---------------------------------------------------------------------------
# Official shape geometry (verbatim from the supplied SVGs), and the
# deterministic randomness that places it — a rerun reproduces the same badge.
# ---------------------------------------------------------------------------

ARROW_REGULAR = dict(
    w=422.98, h=600.0,
    d=("M308.51,0 L46.97,114.42 L0,224.04 L208.02,137.79 L68.91,480.94 "
       "L67.58,484.26 L113.86,600 L286.24,169.06 L376.67,375.07 L422.98,267.08 Z"),
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
# Logo — horizontal lockup, built from the official SVG
#
# The supplied artwork is the vertical lockup. Icon and wordmark are separated
# with clip paths rather than by editing the paths, so the official outlines are
# used untouched; only their arrangement changes, which the guidelines allow
# ("use your best judgement between horizontal and vertical").
# ---------------------------------------------------------------------------

ICON_BOX = (720.0, 48.0, 2370.0, 1894.0)     # measured by rendering
WORD_BOX = (48.0, 2183.0, 2948.0, 2652.0)


def logo_svg(width_pt, height_pt, ink):
    src = open(os.path.join(ROOT, "Official Vector Logo.svg")).read()
    body = src[src.index("<polygon"):src.rindex("</svg>")]
    gi = body.index("<g>")
    icon_body, word_body = body[:gi], body[gi:]

    iw = ICON_BOX[2] - ICON_BOX[0]
    ih = ICON_BOX[3] - ICON_BOX[1]
    ww = WORD_BOX[2] - WORD_BOX[0]
    wh = WORD_BOX[3] - WORD_BOX[1]

    # Icon full height; wordmark at 70% of it, both vertically centred, with a
    # gap of a third of the icon width. Reproduces the 5.1:1 proportion of the
    # reference lockup.
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
    <style>.st0,.st1{{fill:{ink}}}</style>
  </defs>
  <g transform="translate({x0} {(height_pt-ih_t)/2}) scale({si}) translate({-ICON_BOX[0]} {-ICON_BOX[1]})">
    <g clip-path="url(#ci)">{icon_body}{word_body}</g>
  </g>
  <g transform="translate({x0+iw_t+gap} {(height_pt-wh_t)/2}) scale({sw}) translate({-WORD_BOX[0]} {-WORD_BOX[1]})">
    <g clip-path="url(#cw)">{word_body}</g>
  </g>
</svg>'''


# ---------------------------------------------------------------------------
# Artwork — smooth gradient only
# ---------------------------------------------------------------------------


def panel_points():
    """The colour panel: full bleed width, lower edge slanting down to the
    right so it runs across the venue piece's travel axis."""
    return f"0,0 {W},0 {W},{PANEL_R} 0,{PANEL_L}"


def ground_svg():
    """Near-black, with a slow vertical lift so the card is not flat."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="gr" x1="0" y1="0" x2="0.28" y2="1">
      <stop offset="0" stop-color="{GROUND_HI}"/>
      <stop offset="1" stop-color="{GROUND}"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" fill="url(#gr)"/>
</svg>'''


def panel_svg(a, b):
    """The category gradient.

    One clean sweep corner to corner. The pairing's first colour holds through
    the opening third so the lockup sits on flat colour rather than on the part
    of the ramp where the hue is moving, then runs to the second colour at the
    far edge. Below the panel, the same light falls off into the black over
    about forty points — still a smooth gradient, no texture — so the two halves
    read as one card lit from above rather than as two stacked blocks.
    """
    spill = 42.0
    # The spill carries the panel's own gradient, so the light under the violet
    # end of the edge is violet and under the turquoise end is turquoise — a
    # single colour here puts turquoise haze beneath a violet edge.
    #
    # Its fade runs *perpendicular to the slanted edge*, not straight down. A
    # vertical fade starts at one y for the whole width, which on a 26 pt slant
    # means it begins 26 pt inside the panel at the right-hand end. Projecting
    # the axis onto the edge normal makes the whole edge the zero point.
    ex, ey = W, PANEL_R - PANEL_L
    n = math.hypot(ex, ey)
    nx, ny = -ey / n, ex / n
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="cg" gradientUnits="userSpaceOnUse"
                    x1="0" y1="0" x2="{W:.2f}" y2="{PANEL_R * 1.30:.2f}">
      <stop offset="0" stop-color="{a}"/>
      <stop offset="0.34" stop-color="{a}"/>
      <stop offset="1" stop-color="{b}"/>
    </linearGradient>
    <linearGradient id="fade" gradientUnits="userSpaceOnUse"
                    x1="0" y1="{PANEL_L:.2f}"
                    x2="{nx * spill:.2f}" y2="{PANEL_L + ny * spill:.2f}">
      <stop offset="0" stop-color="#FFFFFF"/>
      <stop offset="1" stop-color="#000000"/>
    </linearGradient>
    <mask id="sp" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <rect x="0" y="0" width="{W}" height="{H}" fill="url(#fade)"/>
    </mask>
  </defs>
  <polygon points="0,{PANEL_L} {W},{PANEL_R} {W},{PANEL_R + spill} 0,{PANEL_L + spill}"
           fill="url(#cg)" opacity="0.34" mask="url(#sp)"/>
  <polygon points="{panel_points()}" fill="url(#cg)"/>
</svg>'''


# ---------------------------------------------------------------------------
# The mark field
#
# The official arrow, pixel and plus marks running across the whole card at low
# opacity. Drawn twice against the same geometry — once in the ground colour
# clipped to the colour panel, once in the category gradient clipped to
# everything below it — so a mark straddling the panel edge reads as one
# continuous shape that simply changes ink where the ground changes.
#
# The arrows are a *lattice*, not a scatter: one pitch, half-dropped rows, jitter
# small enough that the repeat still reads. Only opacity and a few skipped cells
# break it up. That is what keeps a much lower arrow count from looking sparse —
# a scatter at this density reads as leftovers, a tile reads as a pattern.
# ---------------------------------------------------------------------------

ARROW_TILE_X = 82.0
ARROW_TILE_Y = 108.0
ARROW_TILE_H = 58.0
ARROW_JITTER = 5.0
ARROW_SKIP = 0.18       # fraction of lattice cells left empty

MARK_OP_PANEL = 0.20    # ground-colour ink knocking into the category colour
MARK_OP_GROUND = 0.42   # category-colour ink on the near-black


def lighten(hex_colour, k):
    """Mix a colour toward white.

    The marks on the near-black take the pairing's own colours, and at badge
    scale those arrive with wildly different weight: Lime sits at 0.86
    luminance and Cobalt at 0.11, so one pairing's field shouts and another's
    disappears. Lifting every stop most of the way to white evens them out and
    matches how the marks read in the room, where they are emissive rather than
    printed.
    """
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(v + (255 - v) * k) for v in (r, g, b))


def logo_clear(x, y):
    """Fade marks sitting behind the lockup.

    Anything dense behind the logo competes directly with the letterforms, and
    the lockup is the one element on the card with no fallback if it goes soft.
    Returns a multiplier: near zero under the lockup, 1 well clear of it.
    """
    lx, ly = LOGO_XY
    lw, lh = LOGO_SIZE
    cx, cy = lx + lw / 2, ly + lh / 2
    d = math.hypot((x - cx) / (lw * 0.80), (y - cy) / (lh * 2.4))
    return min(1.0, max(0.08, (d - 0.55) / 0.60))


def name_clear(y):
    """Hold the field back off the name block.

    The name is the whole job of the badge. Marks are already faint, but a plus
    landing inside a counter still costs legibility at the distance this is read
    from, so the band the type occupies runs at a third of the field's opacity.
    """
    top, bottom = NAME_Y[0] - NAME_MAX, PROG_Y[-1] + 6
    if top <= y <= bottom:
        return 0.34
    edge = 26.0
    if top - edge < y < top:
        return 0.34 + 0.66 * (top - y) / edge
    if bottom < y < bottom + edge:
        return 0.34 + 0.66 * (y - bottom) / edge
    return 1.0


def marks_svg(seed, a, b, in_panel):
    r = rng(seed)
    parts = []
    ink = GROUND if in_panel else "url(#mg)"

    def fade(x, y):
        f = name_clear(y)
        return f * logo_clear(x, y) if in_panel else f

    def arrow(x, y, h, op):
        s = ARROW_REGULAR
        k = h / s["h"]
        op *= fade(x, y + h * 0.5)
        if op < 0.004:
            return
        parts.append(f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.5f})" '
                     f'opacity="{op:.3f}"><path d="{s["d"]}" fill="{ink}"/></g>')

    def pixel(x, y, s, op):
        op *= fade(x, y)
        if op < 0.004:
            return
        parts.append(f'<rect x="{x-s/2:.2f}" y="{y-s/2:.2f}" width="{s:.2f}" '
                     f'height="{s:.2f}" fill="{ink}" opacity="{op:.3f}"/>')

    def plus(x, y, s, op):
        op *= fade(x, y)
        if op < 0.004:
            return
        bar = s * PLUS_BAR / 2
        parts.append(f'<g opacity="{op:.3f}" fill="{ink}">'
                     f'<rect x="{x-s/2:.2f}" y="{y-bar:.2f}" width="{s:.2f}" height="{bar*2:.2f}"/>'
                     f'<rect x="{x-bar:.2f}" y="{y-s/2:.2f}" width="{bar*2:.2f}" height="{s:.2f}"/></g>')

    base = MARK_OP_PANEL if in_panel else MARK_OP_GROUND

    # ---- the arrow lattice ------------------------------------------------
    cols = int(W / ARROW_TILE_X) + 2
    rows = int(H / ARROW_TILE_Y) + 2
    for row in range(-1, rows):
        for col in range(-1, cols):
            if r() < ARROW_SKIP:
                continue
            x = col * ARROW_TILE_X + (ARROW_TILE_X / 2 if row % 2 else 0)
            y = row * ARROW_TILE_Y
            x += (r() * 2 - 1) * ARROW_JITTER
            y += (r() * 2 - 1) * ARROW_JITTER
            h = ARROW_TILE_H * (0.88 + 0.24 * r())
            arrow(x, y, h, base * (0.42 + 0.75 * r()))

    # ---- pixels and pluses ------------------------------------------------
    # The official cluster patterns, drawn whole so the real pattern stays
    # recognisable rather than only its constituent marks.
    for kind, count in ((1, 2), (0, 2)):
        pat = PLUS_CLUSTER if kind else PIXEL_CLUSTER
        mk = PLUS_CLUSTER_MARK if kind else PIXEL_CLUSTER_MARK
        for _ in range(count):
            cx, cy = r() * W, r() * H
            size = (0.30 + 0.34 * r()) * W
            op = base * (0.5 + 0.5 * r())
            for ox, oy in pat:
                mx, my = cx + ox * size, cy + oy * size
                if -20 < mx < W + 20 and -20 < my < H + 20:
                    (plus if kind else pixel)(mx, my, size * mk, op)

    # A loose scatter over the top, at a wide spread of sizes and opacities, so
    # the field has some grain in it and does not read as one flat screen.
    for _ in range(120):
        x, y = r() * W, r() * H
        s = 2.0 + 9.0 * r() ** 2.2
        (pixel if r() < 0.55 else plus)(x, y, s, base * (0.30 + 0.85 * r()))

    if in_panel:
        clip = f'<clipPath id="c"><polygon points="{panel_points()}"/></clipPath>'
        grad = ""
    else:
        clip = (f'<clipPath id="c"><path d="M0,0 H{W} V{H} H0 Z '
                f'M0,{PANEL_L} L{W},{PANEL_R} L{W},0 L0,0 Z" clip-rule="evenodd"/></clipPath>')
        # Marks below the panel take the colour of the panel above them, so the
        # two halves of the card sit on one gradient rather than two.
        la, lb = lighten(a, 0.55), lighten(b, 0.30)
        grad = (f'<linearGradient id="mg" gradientUnits="userSpaceOnUse" '
                f'x1="0" y1="0" x2="{W:.2f}" y2="{PANEL_R * 1.30:.2f}">'
                f'<stop offset="0" stop-color="{la}"/>'
                f'<stop offset="0.34" stop-color="{la}"/>'
                f'<stop offset="1" stop-color="{lb}"/></linearGradient>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <defs>{clip}{grad}</defs>
  <g clip-path="url(#c)">{''.join(parts)}</g>
</svg>'''


def chip_svg(fill, width):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">
  <rect x="{SX0}" y="{CHIP_TOP:.2f}" width="{width:.2f}" height="{CHIP_H}"
        rx="{CHIP_RADIUS}" fill="{fill}"/>
</svg>'''


# ---------------------------------------------------------------------------
# The die-line, lifted from the supplied artboard
#
# Taken from the working file rather than redrawn, so the tag edge and slot
# punches are exactly the ones the printer cuts to.
#
# Switching the artwork layer *off* is not enough. Illustrator writes its layers
# as marked-content sections in the page stream (`/OC /MC0 BDC ... EMC`), and
# placing that page copies the stream verbatim — the optional-content state is a
# property of the source document, not of the operators. The artwork rides along
# and lands on top of everything, which is exactly the failure that hid a whole
# badge design behind the old mockup once already. So the guides section is cut
# out of the stream instead, and nothing else comes with it.
# ---------------------------------------------------------------------------

GUIDES_LAYER = "Guides"


def _marked_section(data, tag):
    """The operators between `/OC /<tag> BDC` and its matching `EMC`."""
    start = data.find(b"/OC /" + tag + b" BDC")
    if start < 0:
        raise SystemExit(f"no marked-content section /{tag.decode()} in {ARTBOARD}")
    i = data.index(b"BDC", start) + 3
    depth = 1
    for m in re.finditer(rb"\b(BDC|BMC|EMC)\b", data[i:]):
        depth += 1 if m.group(1) in (b"BDC", b"BMC") else -1
        if depth == 0:
            return data[i:i + m.start()]
    raise SystemExit(f"unterminated marked-content section /{tag.decode()}")


def guides_pdf(tmpdir):
    out = os.path.join(tmpdir, "guides.pdf")
    src = pikepdf.open(os.path.join(ROOT, ARTBOARD))
    page = src.pages[0]

    tag = None
    for key, ocg in page.Resources.Properties.items():
        if GUIDES_LAYER.lower() in str(ocg.Name).lower():
            tag = str(key).lstrip("/").encode()
    if tag is None:
        raise SystemExit(f"no '{GUIDES_LAYER}' layer in {ARTBOARD}")

    contents = page.Contents
    data = b"".join(bytes(s.read_bytes()) for s in contents) \
        if isinstance(contents, pikepdf.Array) else bytes(contents.read_bytes())

    doc = pikepdf.new()
    dest = doc.add_blank_page(page_size=(PAGE_W, PAGE_H))
    dest.Contents = doc.make_stream(_marked_section(data, tag))
    dest.Resources = doc.copy_foreign(src.make_indirect(page.Resources))
    doc.save(out)
    return out


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

ART_RECT = fitz.Rect(OX, OY, OX + W, OY + H)


def svg_layer(page, svg, path, oc, rect=None):
    open(path + ".svg", "w").write(svg)
    cairosvg.svg2pdf(url=path + ".svg", write_to=path)
    src = fitz.open(path)
    page.show_pdf_page(rect or ART_RECT, src, 0, oc=oc)
    src.close()


def fit(font, text, size, maxw):
    """Shrink until the line fits the safe width — names vary a lot."""
    while size > 8 and font.text_length(text, fontsize=size) > maxw:
        size -= 0.25
    return size


def add_ocgs(doc):
    return {k: doc.add_ocg(n, on=True) for k, n in (
        ("ground", "1 Ground"),
        ("marks_g", "2 Brand marks (ground)"),
        ("panel", "3 Category gradient"),
        ("marks_p", "4 Brand marks (panel)"),
        ("logo", "5 Vector logo"),
        ("chip", "6 Category chip"),
        ("text", "7 Text fields"),
        ("guides", "8 Die-line (reference only)"),
    )}


def compose(doc, oc, cat, tmpdir, guides):
    cid, label, a, b = cat
    page = doc.new_page(width=PAGE_W, height=PAGE_H)
    t = lambda n: os.path.join(tmpdir, f"{cid}_{n}.pdf")

    seed = SEEDS[cid]
    svg_layer(page, ground_svg(), t("ground"), oc["ground"])
    svg_layer(page, marks_svg(seed, a, b, False), t("mg"), oc["marks_g"])
    svg_layer(page, panel_svg(a, b), t("panel"), oc["panel"])
    # Same seed on both passes: the lattice and the scatter must line up across
    # the panel edge, or a mark straddling it turns into two different marks.
    svg_layer(page, marks_svg(seed, a, b, True), t("mp"), oc["marks_p"])

    # The lockup sits on the panel's opening colour, so that is what decides
    # which official variant runs. Every pairing leads dark, so all four land on
    # the reverse lockup — but the rule is measured, not assumed.
    logo_ink = reverse_or_black(a)
    lx, ly = LOGO_XY
    lw, lh = LOGO_SIZE
    svg_layer(page, logo_svg(lw, lh, logo_ink), t("logo"), oc["logo"],
              rect=fitz.Rect(OX + lx, OY + ly, OX + lx + lw, OY + ly + lh))

    semi = os.path.join(ROOT, "Karbon-Semibold.otf")
    if not os.path.exists(semi):
        raise SystemExit("Karbon-Semibold.otf not found in the repository root")
    f_semi = fitz.Font(fontfile=semi)

    # The chip carries the pairing's second colour — the one the panel does not
    # lead with — so the two ends of the gradient bracket the card.
    chip_fill = b
    chip_ink = ink_on(chip_fill)
    track = CHIP_SIZE * 0.06
    chip_w = min(SAFE_W, f_semi.text_length(label.upper(), fontsize=CHIP_SIZE)
                 + track * len(label) + CHIP_PAD * 2)
    svg_layer(page, chip_svg(chip_fill, chip_w), t("chip"), oc["chip"])

    # ---- text -------------------------------------------------------------
    tw_name = fitz.TextWriter(page.rect)
    tw_body = fitz.TextWriter(page.rect)
    tw_chip = fitz.TextWriter(page.rect)

    size = min(fit(f_semi, line, NAME_MAX, SAFE_W) for line in NAME_LINES)
    for i, line in enumerate(NAME_LINES):
        tw_name.append((OX + SX0, OY + NAME_Y[i]), line, font=f_semi, fontsize=size)
    for ys, lines in ((ORG_Y, ORG_LINES), (PROG_Y, PROG_LINES)):
        for i, line in enumerate(lines):
            tw_body.append((OX + SX0, OY + ys[i]), line, font=f_semi,
                           fontsize=fit(f_semi, line, BODY, SAFE_W))

    # chip label: uppercase, letter-spaced by hand since TextWriter has no tracking
    cx = OX + SX0 + CHIP_PAD
    cy = OY + CHIP_TOP + CHIP_H / 2 + CHIP_SIZE * 0.34
    for ch in label.upper():
        tw_chip.append((cx, cy), ch, font=f_semi, fontsize=CHIP_SIZE)
        cx += f_semi.text_length(ch, fontsize=CHIP_SIZE) + track

    tw_name.write_text(page, color=INK_NAME, oc=oc["text"])
    tw_body.write_text(page, color=INK_BODY, oc=oc["text"])
    ci = tuple(int(chip_ink[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    tw_chip.write_text(page, color=ci, oc=oc["text"])

    # ---- die-line, on top --------------------------------------------------
    g = fitz.open(guides)
    page.show_pdf_page(page.rect, g, 0, oc=oc["guides"])
    g.close()


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out", "badges")
    os.makedirs(outdir, exist_ok=True)
    tmpdir = tempfile.mkdtemp()
    guides = guides_pdf(tmpdir)

    combined = fitz.open()
    oc_all = add_ocgs(combined)
    for cat in CATEGORIES:
        compose(combined, oc_all, cat, tmpdir, guides)

        doc = fitz.open()
        compose(doc, add_ocgs(doc), cat, tmpdir, guides)
        out = os.path.join(outdir, f"vector-badge-{cat[0]}.pdf")
        doc.save(out, garbage=3, deflate=True)
        doc.close()
        print("wrote", out)

    out = os.path.join(outdir, "vector-badges-all.pdf")
    combined.save(out, garbage=3, deflate=True)
    combined.close()
    print("wrote", out)


if __name__ == "__main__":
    main()
