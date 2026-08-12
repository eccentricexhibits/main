#!/usr/bin/env python3
"""
Build the Design Exchange event floor maps.

Outputs, per level plus a building overview sheet:
    dist/<key>.svg   vector, fonts embedded
    dist/<key>.png   2x raster for slides and screens
    dist/<key>.pdf   24 x 36 in press-ready
and dist/index.html, a single-file viewer for all four sheets.

    python3 src/build.py
"""
from __future__ import annotations

import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapdata import (BRAND, BOH_FILL, FLOORS, GLYPH_ON, INK, INK_SOFT, PAPER,
                     PT_PER_FT, ROLE, WALL_EDGE, WALL_FILL)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
DIST = os.path.join(ROOT, "dist")
GEO = os.path.join(ROOT, "geometry")

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# 24 x 36 in at 72 units/in
SHEET_W, SHEET_H = 1728, 2592
MARGIN = 108

HEAD_H = 300          # black header band
MAP_TOP = 372
MAP_BOT = 1946
META_Y = 1998         # north arrow + scale bar strip
LEGEND_TOP = 2062


# ------------------------------------------------------------------ assets --
def font_face() -> str:
    faces = []
    for weight, fname in ((400, "Karbon-Regular.otf"), (600, "Karbon-Semibold.otf")):
        path = os.path.join(REPO, fname)
        if not os.path.exists(path):
            continue
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        faces.append(
            "@font-face{font-family:'Karbon';font-style:normal;font-weight:%d;"
            "src:url(data:font/otf;base64,%s) format('opentype');}" % (weight, b64)
        )
    return "".join(faces)


def vector_logo_symbol() -> str:
    """Vector Institute vertical lockup, recoloured for a dark ground."""
    path = os.path.join(REPO, "Official Vector Logo.svg")
    if not os.path.exists(path):
        return '<symbol id="vector-logo" viewBox="0 0 3000 2700"></symbol>'
    raw = open(path, encoding="utf-8").read()
    body = raw[raw.index(">", raw.index("<svg")) + 1: raw.rindex("</svg>")]
    body = re.sub(r"<defs>.*?</defs>", "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = body.replace('class="st0"', 'fill="%s"' % BRAND["magenta"])
    body = body.replace('class="st1"', 'fill="#FFFFFF"')
    return '<symbol id="vector-logo" viewBox="0 0 3000 2700">%s</symbol>' % body


ICONS = {
    "washroom": '<circle cx="7.2" cy="4.2" r="2.3"/><rect x="4.7" y="7.2" width="5" height="8.4" rx="1.7"/>'
                '<rect x="5.4" y="14.4" width="1.6" height="7" rx=".8"/><rect x="7.5" y="14.4" width="1.6" height="7" rx=".8"/>'
                '<circle cx="16.8" cy="4.2" r="2.3"/><path d="M16.8 7.2 20.6 16.2 13 16.2Z"/>'
                '<rect x="15" y="15.6" width="1.5" height="5.8" rx=".7"/><rect x="17.1" y="15.6" width="1.5" height="5.8" rx=".7"/>',
    "accessible": '<circle cx="14.2" cy="3.9" r="2.2"/>'
                  '<path d="M13.5 7.6v5.6h4.9" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
                  '<circle cx="11.6" cy="16.1" r="5.5" fill="none" stroke="currentColor" stroke-width="2.2"/>'
                  '<path d="M18.4 13.2 20.8 20.6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>',
    "elevator": '<rect x="3.2" y="2.8" width="17.6" height="18.4" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
                '<path d="M12 6.2 15.4 10.8H8.6Z"/><path d="M12 17.8 8.6 13.2h6.8Z"/>',
    "stairs": '<path d="M3 20.6h4.6v-3.9h4.6v-3.9h4.6V8.9h4.6V4.6" fill="none" stroke="currentColor" '
              'stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>',
    "escalator": '<path d="M3.6 20.3h4.8L19.4 6.4" fill="none" stroke="currentColor" stroke-width="2.4" '
                 'stroke-linecap="round" stroke-linejoin="round"/><path d="M21.3 4.1 21.3 7.9 17.5 4.9Z"/>',
    "theatre": '<rect x="2.6" y="4.4" width="18.8" height="11.4" rx="1.2" fill="none" stroke="currentColor" stroke-width="2"/>'
               '<path d="M12 21.6 7.4 17.4h9.2Z"/>',
    "coat": '<path d="M12 9.4V7.6a2.2 2.2 0 1 1 2.2-2.2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
            '<path d="M12 9.2 3.2 16.4h17.6Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    "info": '<circle cx="12" cy="5.6" r="1.9"/><rect x="10.1" y="9.4" width="3.8" height="11.2" rx="1.9"/>',
    "entrance": '<path d="M13.6 3.2h6.8v17.6h-6.8" fill="none" stroke="currentColor" stroke-width="2.2" '
                'stroke-linejoin="round" stroke-linecap="round"/>'
                '<path d="M3.4 12h9" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'
                '<path d="M9.2 8.2 13 12l-3.8 3.8" fill="none" stroke="currentColor" stroke-width="2.2" '
                'stroke-linecap="round" stroke-linejoin="round"/>',
    "food": '<path d="M4.4 7.4h11.8V13a5.9 5.9 0 0 1-11.8 0Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
            '<path d="M16.2 8.8h1.9a2.7 2.7 0 0 1 0 5.4h-1.9" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M3.4 20.6h13.8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
}


def icon_defs() -> str:
    return "".join(
        '<symbol id="ic-%s" viewBox="0 0 24 24" fill="currentColor">%s</symbol>' % (k, v)
        for k, v in ICONS.items()
    )


# -------------------------------------------------------------- primitives --
def esc(s):
    return html.escape(str(s), quote=True)


def T(x, y, s, size=16, weight=400, fill=INK, anchor="start", ls=0, op=1.0,
      family="Karbon", baseline=None, halo=0):
    extra = ""
    if ls:
        extra += ' letter-spacing="%s"' % ls
    if op != 1.0:
        extra += ' opacity="%s"' % op
    if baseline:
        extra += ' dominant-baseline="%s"' % baseline
    if halo:
        # cartographic halo so labels stay readable over wall poche and tints
        extra += (' stroke="#FFFFFF" stroke-width="%.1f" stroke-linejoin="round" '
                  'paint-order="stroke fill"' % halo)
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%.1f" font-weight="%d" '
            'fill="%s" text-anchor="%s"%s>%s</text>'
            % (x, y, family, size, weight, fill, anchor, extra, esc(s)))


def wrap(words, max_chars):
    lines, cur = [], ""
    for w in words.split():
        trial = (cur + " " + w).strip()
        if len(trial) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def poly(pts, **kw):
    d = " ".join("%.2f,%.2f" % p for p in pts)
    attrs = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<polygon points="%s" %s/>' % (d, attrs)


# ------------------------------------------------------------------- header --
def header(title, level, tagline, eyebrow="Vector Institute at Design Exchange"):
    """level=None renders the header without the level badge."""
    o = ['<rect x="0" y="0" width="%d" height="%d" fill="#0B0B0B"/>' % (SHEET_W, HEAD_H)]
    o.append('<use href="#vector-logo" x="%d" y="70" width="178" height="160"/>' % MARGIN)
    x = MARGIN + 244
    o.append('<rect x="%d" y="74" width="2" height="152" fill="#3A3A3A"/>' % (x - 46))
    o.append(T(x, 122, eyebrow.upper(), 21, 600, BRAND["magenta"], ls=3.4))
    o.append(T(x, 186, title, 58, 600, "#FFFFFF"))
    o.append(T(x, 224, tagline, 24, 400, "#B9B6B6"))
    # level badge
    if level is not None:
        bx = SHEET_W - MARGIN - 150
        o.append('<rect x="%d" y="74" width="150" height="152" rx="18" fill="%s"/>'
                 % (bx, BRAND["magenta"]))
        o.append(T(bx + 75, 128, "LEVEL", 19, 600, "#FFFFFF", "middle", ls=2.6))
        o.append(T(bx + 75, 208, level, 76, 600, "#FFFFFF", "middle"))
    # brand gradient rule
    o.append('<rect x="0" y="%d" width="%d" height="12" fill="url(#brandgrad)"/>' % (HEAD_H, SHEET_W))
    return "".join(o)


def footer(note):
    y = SHEET_H - 74
    o = ['<rect x="%d" y="%d" width="%d" height="2" fill="#E2E0E0"/>'
         % (MARGIN, y - 34, SHEET_W - 2 * MARGIN)]
    o.append(T(MARGIN, y, note, 19, 400, INK_SOFT))
    o.append(T(SHEET_W - MARGIN, y, "Design Exchange  ·  234 Bay Street, Toronto",
               19, 400, INK_SOFT, "end"))
    return "".join(o)


# ------------------------------------------------------------- floor sheet --
def build_floor(floor):
    geo = json.load(open(os.path.join(GEO, floor["geometry"])))
    bx0, by0, bx1, by1 = floor["bbox"]

    avail_w = SHEET_W - 2 * MARGIN
    avail_h = MAP_BOT - MAP_TOP
    s = min(avail_w / (bx1 - bx0), avail_h / (by1 - by0))
    tx = MARGIN + (avail_w - (bx1 - bx0) * s) / 2 - bx0 * s
    ty = MAP_TOP + (avail_h - (by1 - by0) * s) / 2 - by0 * s

    def P(x, y):
        return (x * s + tx, y * s + ty)

    o = []
    o.append('<rect width="%d" height="%d" fill="%s"/>' % (SHEET_W, SHEET_H, PAPER))
    o.append(header(floor["name"], floor["level"], floor["tagline"]))

    # ---- zones (under the wall poche so any overshoot is masked by walls)
    for z in floor["zones"]:
        col = ROLE[z["role"]]
        pts = [P(*p) for p in z["pts"]]
        fillop = 0.20 if z["role"] == "event" else 0.16
        if z["role"] == "boh":
            o.append(poly(pts, fill=BOH_FILL, stroke="none"))
        else:
            o.append(poly(pts, fill=col, fill_opacity=fillop, stroke=col,
                          stroke_opacity=0.55, stroke_width=2.5,
                          stroke_linejoin="round"))

    # The source sheets carry a title block (DX logo, north rose, scale note)
    # in the same coordinate space, so clip everything to the building itself.
    clip = "plan-%s" % floor["key"]
    o.append('<clipPath id="%s"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/></clipPath>'
             % (clip, bx0 * s + tx, by0 * s + ty, (bx1 - bx0) * s, (by1 - by0) * s))

    # ---- base plan: glazing, wall poche, glazed screens, then thin detail
    # (clip lives on an untransformed wrapper so the rect stays in sheet space)
    o.append('<g clip-path="url(#%s)">' % clip)
    o.append('<g transform="translate(%.3f,%.3f) scale(%.5f)">' % (tx, ty, s))
    for d in geo.get("light", []):
        o.append('<path d="%s" fill="#E7E5E5" fill-rule="evenodd"/>' % d)
    for d in geo["walls"]:
        o.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, WALL_FILL))
    for d in geo.get("dark", []):
        o.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, "#8E8B8B"))
    o.append("</g>")
    o.append('<g transform="translate(%.3f,%.3f) scale(%.5f)" fill="none" '
             'stroke="%s" stroke-width="%.3f" stroke-opacity=".85" stroke-linejoin="round">'
             % (tx, ty, s, WALL_EDGE, 0.8 / s))
    for d in geo["walls"]:
        o.append('<path d="%s"/>' % d)
    o.append("</g>")
    o.append('<g transform="translate(%.3f,%.3f) scale(%.5f)" fill="none" '
             'stroke="#9E9B9B" stroke-width="%.3f" stroke-opacity=".8" stroke-linecap="round">'
             % (tx, ty, s, 0.7 / s))
    for d in geo.get("detail", []):
        o.append('<path d="%s"/>' % d)
    o.append("</g>")
    o.append("</g>")  # close clip wrapper

    # ---- projection / screen surfaces
    for sc in floor.get("screens", []):
        a, b = P(*sc["p0"]), P(*sc["p1"])
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="11" '
                 'stroke-linecap="round"/>' % (a[0], a[1], b[0], b[1], BRAND["magenta"]))
        lx, ly = P(*sc["label_at"])
        rot = sc.get("rot", 0)
        o.append('<g transform="translate(%.1f,%.1f) rotate(%d)">%s</g>'
                 % (lx, ly, rot, T(0, 0, sc["label"], 20, 600, BRAND["magenta"],
                                   "middle", ls=2.4)))

    # ---- zone labels
    for z in floor["zones"]:
        if not z.get("label"):
            continue
        lx, ly = P(*z["label_at"])
        sz = {"xl": 46, "m": 30, "s": 24, "xs": 19}[z.get("size", "s")]
        anchor = z.get("label_anchor", "start")
        col = INK if z["role"] != "boh" else INK_SOFT
        block = [T(0, 0, z["label"], sz, 600, col, anchor, ls=1.6 if sz > 30 else 0.8, halo=5)]
        if z.get("sub"):
            block.append(T(0, sz * 0.72, z["sub"], max(17, sz * 0.42), 400, INK_SOFT,
                           anchor, halo=4))
        o.append('<g transform="translate(%.1f,%.1f) rotate(%d)">%s</g>'
                 % (lx, ly, z.get("rot", 0), "".join(block)))

    # ---- pins
    R, G = 27, 30
    for p in floor["pins"]:
        cx, cy = P(*p["at"])
        col = ROLE[p["role"]]
        o.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="#FFFFFF"/>' % (cx, cy, R + 4))
        o.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (cx, cy, R, col))
        o.append('<use href="#ic-%s" x="%.1f" y="%.1f" width="%d" height="%d" color="%s"/>'
                 % (p["icon"], cx - G / 2, cy - G / 2, G, G, GLYPH_ON[col]))
        # Most pins run icon-only; the key carries the meaning. Only the few
        # routes people ask for by name get typeset next to the icon.
        if p.get("label") and p.get("show_label"):
            right = p.get("side", "right") == "right"
            lx = cx + (R + 16) if right else cx - (R + 16)
            anchor = "start" if right else "end"
            o.append(T(lx, cy - (2 if p.get("note") else -7), p["label"], 22, 600, INK,
                       anchor, halo=5))
            if p.get("note"):
                o.append(T(lx, cy + 22, p["note"], 18, 400, INK_SOFT, anchor, halo=4))

    # ---- callouts
    for c in floor.get("callouts", []):
        cx, cy = P(*c["at"])
        w = c["w"] * s
        lines = wrap(c["body"], int(w / 8.4))
        h = 62 + len(lines) * 25
        col = BRAND["magenta"] if c.get("warn") else BRAND["cobalt"]
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="14" fill="#FFFFFF" '
                 'fill-opacity=".94" stroke="%s" stroke-width="3"/>'
                 % (cx - w / 2, cy - h / 2, w, h, col))
        ty0 = cy - h / 2 + 40
        o.append(T(cx, ty0, c["title"], 25, 600, col, "middle"))
        for i, ln in enumerate(lines):
            o.append(T(cx, ty0 + 32 + i * 25, ln, 19, 400, INK, "middle"))

    # ---- meta strip: north arrow + scale bar, clear of the drawing
    nx, ny = MARGIN + 22, META_Y
    # North on the DX blueprints points to the RIGHT of the page, not up, so
    # these sheets — which keep the blueprint's own orientation — say so.
    o.append('<path d="M%d %d L%d %d L%d %d Z" fill="%s"/>'
             % (nx + 26, ny, nx - 10, ny - 12, nx - 10, ny + 12, INK))
    o.append(T(nx + 36, ny + 9, "N", 24, 600, INK))
    bar_ft = 20
    bw = bar_ft * PT_PER_FT * s
    bxs, bys = MARGIN + 150, ny - 4
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="10" fill="%s"/>' % (bxs, bys, bw, INK))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="10" fill="#FFFFFF" stroke="%s" '
             'stroke-width="1.5"/>' % (bxs, bys, bw / 2, INK))
    o.append(T(bxs, bys - 12, "0", 17, 400, INK_SOFT, "middle"))
    o.append(T(bxs + bw, bys - 12, "%d ft" % bar_ft, 17, 400, INK_SOFT, "middle"))
    o.append(T(bxs + bw + 34, ny + 8, "Drawn from the venue's blueprints  ·  north is to the right",
               19, 400, INK_SOFT))

    # ---- legend
    o.append(legend_block(floor))
    o.append(footer("Event floor map  ·  %s, Level %s" % (floor["name"], floor["level"])))

    return svg_document(o)


def legend_block(floor):
    used, seen = [], set()
    order = ["info", "entrance", "theatre", "stairs", "escalator", "elevator",
             "washroom", "accessible", "coat", "food"]
    names = {
        "info": ("Check-in", "Front desk"),
        "entrance": ("Entrance", "Bay St. / TD Concourse"),
        "theatre": ("Projection space", "Immersive walls"),
        "stairs": ("Stairs", "All levels"),
        "escalator": ("Escalators", "To TD Concourse"),
        "elevator": ("Elevator", "All levels"),
        "washroom": ("Washrooms", "Women's / men's"),
        "accessible": ("Universal washroom", "Step-free"),
        "coat": ("Coat check", ""),
        "food": ("Kitchen / bar", ""),
    }
    present = {p["icon"]: p["role"] for p in floor["pins"]}
    for ic in order:
        if ic in present and ic not in seen:
            seen.add(ic)
            used.append((ic, present[ic]))

    o = ['<rect x="%d" y="%d" width="%d" height="2" fill="#E2E0E0"/>'
         % (MARGIN, LEGEND_TOP - 30, SHEET_W - 2 * MARGIN)]
    o.append(T(MARGIN, LEGEND_TOP + 14, "KEY", 21, 600, INK, ls=3.4))

    cols, y0 = 5, LEGEND_TOP + 62
    cw = (SHEET_W - 2 * MARGIN) / cols
    for i, (ic, role) in enumerate(used):
        cx = MARGIN + (i % cols) * cw + 26
        cy = y0 + (i // cols) * 86
        col = ROLE[role]
        o.append('<circle cx="%.1f" cy="%.1f" r="24" fill="%s"/>' % (cx, cy, col))
        o.append('<use href="#ic-%s" x="%.1f" y="%.1f" width="26" height="26" color="%s"/>'
                 % (ic, cx - 13, cy - 13, GLYPH_ON[col]))
        o.append(T(cx + 40, cy - 2, names[ic][0], 22, 600, INK))
        if names[ic][1]:
            o.append(T(cx + 40, cy + 22, names[ic][1], 18, 400, INK_SOFT))

    # getting between floors
    gy = y0 + ((len(used) - 1) // cols + 1) * 86 + 22
    o.append('<rect x="%d" y="%.1f" width="%d" height="120" rx="14" fill="%s" fill-opacity=".10"/>'
             % (MARGIN, gy, SHEET_W - 2 * MARGIN, BRAND["cobalt"]))
    o.append(T(MARGIN + 30, gy + 44, "GETTING BETWEEN FLOORS", 20, 600, BRAND["cobalt"], ls=2.8))
    for i, ln in enumerate(wrap(floor["connections"], 118)):
        o.append(T(MARGIN + 30, gy + 76 + i * 26, ln, 20, 400, INK))
    return "".join(o)


# --------------------------------------------------------- overview sheet --
def svg_document(body_parts):
    defs = ('<defs><style>%s</style>'
            '<linearGradient id="brandgrad" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0%%" stop-color="%s"/><stop offset="55%%" stop-color="%s"/>'
            '<stop offset="100%%" stop-color="%s"/></linearGradient>%s%s</defs>'
            % (font_face(), BRAND["magenta"], BRAND["violet"], BRAND["cobalt"],
               vector_logo_symbol(), icon_defs()))
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'viewBox="0 0 %d %d" width="%d" height="%d">%s%s</svg>'
            % (SHEET_W, SHEET_H, SHEET_W, SHEET_H, defs, "".join(body_parts)))


def render(svg_path, key):
    """Rasterise + print to PDF with Chromium."""
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp()
    page_html = os.path.join(tmp, "p.html")
    with open(page_html, "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset=utf-8>"
                "<style>@page{size:24in 36in;margin:0}html,body{margin:0;padding:0}"
                "svg{display:block}</style>" + open(svg_path, encoding="utf-8").read())
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME,
                              args=["--no-sandbox", "--font-render-hinting=none"])
        pg = b.new_page(viewport={"width": SHEET_W, "height": SHEET_H}, device_scale_factor=2)
        pg.goto("file://" + page_html)
        pg.wait_for_timeout(700)
        pg.locator("svg").screenshot(path=os.path.join(DIST, key + ".png"))
        pg.pdf(path=os.path.join(DIST, key + ".pdf"), width="24in", height="36in",
               print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    shutil.rmtree(tmp, ignore_errors=True)


def build_viewer(sheets):
    cards = []
    for key, title, sub, size in sheets:
        b64 = base64.b64encode(open(os.path.join(DIST, key + ".png"), "rb").read()).decode()
        cards.append(
            '<section id="%s"><header><h2>%s</h2><p>%s</p>'
            '<nav><a href="%s.pdf" download>PDF (%s)</a>'
            '<a href="%s.svg" download>SVG</a>'
            '<a href="%s.png" download>PNG</a></nav></header>'
            '<img src="data:image/png;base64,%s" alt="%s"></section>'
            % (key, esc(title), esc(sub), key, esc(size), key, key, b64,
               esc(title)))
    nav = "".join('<a href="#%s">%s</a>' % (k, esc(t)) for k, t, _, _ in sheets)
    doc = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Floor Maps — Vector Institute at Design Exchange</title>
<style>
%s
:root{--ink:#141414;--soft:#5C5A5A;--line:#E2E0E0;--mag:%s;--cob:%s}
*{box-sizing:border-box}
body{margin:0;font-family:'Karbon',system-ui,sans-serif;color:var(--ink);background:#FAFAFA}
.top{position:sticky;top:0;z-index:9;background:#0B0B0B;color:#fff;padding:18px 28px;
 display:flex;flex-wrap:wrap;gap:18px;align-items:baseline}
.top strong{font-size:19px;letter-spacing:.14em;color:var(--mag)}
.top nav{display:flex;gap:18px;flex-wrap:wrap}
.top nav a{color:#D8D6D6;text-decoration:none;font-size:17px}
.top nav a:hover{color:#fff}
main{max-width:1180px;margin:0 auto;padding:32px 20px 80px}
section{margin:0 0 56px}
header h2{font-size:32px;margin:0 0 4px}
header p{margin:0 0 14px;color:var(--soft);font-size:18px}
header nav{display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap}
header nav a{font-size:15px;text-decoration:none;border:2px solid var(--line);
 border-radius:999px;padding:7px 16px;color:var(--ink)}
header nav a:hover{border-color:var(--cob);color:var(--cob)}
img{width:100%%;height:auto;display:block;border:1px solid var(--line);border-radius:10px;background:#fff}
@media (prefers-color-scheme:dark){
 body{background:#111;color:#F2F1F1}
 header p,.top nav a{color:#A9A6A6}
 img{border-color:#2C2C2C}
 header nav a{border-color:#2C2C2C;color:#F2F1F1}
}
</style></head><body>
<div class="top"><strong>VECTOR INSTITUTE AT DESIGN EXCHANGE</strong><nav>%s</nav></div>
<main>%s</main></body></html>""" % (font_face(), BRAND["magenta"], BRAND["cobalt"], nav, "".join(cards))
    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(doc)


def main():
    os.makedirs(DIST, exist_ok=True)
    # event maps first — the guest-facing style
    import event_map
    import gallery_data
    import lobby_data
    import trading_data
    sheets = []
    for mod, title, sub in ((lobby_data, "Lobby — event map",
                             "Level 1, as a guest-facing event map"),
                            (trading_data, "Trading Floor — event map",
                             "Level 2, as a guest-facing event map"),
                            (gallery_data, "Gallery — event map",
                             "Level 3, as a guest-facing event map")):
        event_map.build(mod)
        sheets.append((mod.SHEET["key"], title, sub, "24 × 16 in"))
    for fl in FLOORS:
        svg = build_floor(fl)
        p = os.path.join(DIST, fl["key"] + ".svg")
        open(p, "w", encoding="utf-8").write(svg)
        render(p, fl["key"])
        sheets.append((fl["key"], "Level %s — %s" % (fl["level"], fl["name"]),
                       fl["tagline"], "24 × 36 in"))
        print("built", fl["key"])

    import build_overview_map
    build_overview_map.main()
    sheets.append(("building-overview", "Getting Around",
                   "How the levels connect — a section, not a plan", "24 × 16 in"))

    build_viewer(sheets)
    print("built index.html")


if __name__ == "__main__":
    main()
