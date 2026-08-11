#!/usr/bin/env python3
"""
Build the Level 3 Gallery event map — the guest-facing, colour-blocked sheet.

    python3 src/build_gallery.py

Outputs dist/gallery-event-map.{svg,png,pdf} at 24 x 16 in landscape.

Where the earlier level sheets draw the venue's blueprint and wash colour over
it, this one throws the poche away and rebuilds the floor as flat shapes: one
tone per category, white gaps between rooms, numbered pins keyed to a panel.
The geometry still comes from the blueprint (see gallery_data), so the
simplification stays true to the building.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gallery_data as G
from build import (CHROME, esc, font_face, icon_defs, T, vector_logo_symbol,
                   wrap)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")

# 24 x 16 in at 72 units/in
SHEET_W, SHEET_H = 1728, 1152
HEAD_H = 168
RULE_H = 7

# plan panel
S = 1.95                       # sheet units per blueprint point
MX, MY = 62.0, 238.0
MAP_W, MAP_H = G.MAP_W * S, G.MAP_H * S        # 1070 x 770

# right-hand key column
COL_X, COL_W = 1196, 472


def P(x, y):
    """Blueprint point -> sheet point, rotated 90 deg CCW so north is up."""
    return (MX + (y - G.PLATE[1]) * S, MY + (G.PLATE[2] - x) * S)


def poly(pts, **kw):
    d = " ".join("%.2f,%.2f" % P(*p) for p in pts)
    a = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<polygon points="%s" %s/>' % (d, a)


def path(pts, **kw):
    d = "M " + " L ".join("%.2f %.2f" % P(*p) for p in pts)
    a = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<path d="%s" fill="none" %s/>' % (d, a)


# ------------------------------------------------------------------ header --
def header():
    o = ['<rect x="0" y="0" width="%d" height="%d" fill="#0B0B0B"/>' % (SHEET_W, HEAD_H),
         '<rect x="0" y="%d" width="%d" height="%d" fill="url(#brandgrad)"/>'
         % (HEAD_H, SHEET_W, RULE_H),
         '<use xlink:href="#vector-logo" x="64" y="34" width="122" height="110"/>',
         '<rect x="214" y="40" width="1.6" height="88" fill="#FFFFFF" opacity=".34"/>',
         T(248, 72, "Vector Institute at Design Exchange", size=18, weight=600,
           fill=G.BRAND["magenta"], ls=3.4),
         T(246, 122, G.SHEET["title"], size=52, weight=600, fill="#FFFFFF"),
         T(560, 120, G.SHEET["tagline"], size=23, fill="#FFFFFF", op=.78)]
    # level chip
    o += ['<rect x="%d" y="34" width="118" height="110" rx="10" fill="%s"/>'
          % (SHEET_W - 182, G.BRAND["magenta"]),
          T(SHEET_W - 123, 72, "LEVEL", size=15, weight=600, fill="#FFFFFF",
            anchor="middle", ls=2.6),
          T(SHEET_W - 123, 126, G.SHEET["level"], size=52, weight=600,
            fill="#FFFFFF", anchor="middle")]
    return o


# -------------------------------------------------------------------- plan --
def plan():
    o = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"/>'
         % (MX, MY, MAP_W, MAP_H, G.FILL["staff"])]

    for z in G.ZONES:
        o.append(poly(z["pts"], fill=G.FILL[z["cat"]], stroke=G.PAPER,
                      stroke_width=3.4, stroke_linejoin="round"))
    for z in G.ZONES:
        if z.get("stroke"):
            o.append(poly(z["pts"], fill="none", stroke=G.ACCENT[z["cat"]],
                          stroke_width=1.7, opacity=".48",
                          stroke_linejoin="round"))

    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
             'fill="none" stroke="%s" stroke-width="3.6"/>'
             % (MX, MY, MAP_W, MAP_H, G.PLATE_EDGE))

    o += corridor_labels()
    o += vendor_tables()
    o += routes()
    o += projection()
    o += screen()
    o += titles()
    o += features()
    return o


def corridor_labels():
    o = []
    for lb in G.CORRIDOR_LABELS:
        px, py = P(*lb["at"])
        o.append('<g transform="rotate(-90 %.1f %.1f)">%s</g>'
                 % (px, py, T(px, py, lb["text"], size=12.5, weight=600,
                              fill=G.INK_SOFT, anchor="middle", ls=2.4,
                              halo=3.0)))
    return o


def vendor_tables():
    """Table runs, drawn as furniture so they never read as architecture."""
    o = []
    lw, lt = 27.0, 13.0                     # 6 ft x ~3 ft
    for run in G.VENDOR:
        span = run["hi"] - run["lo"]
        step = span / run["n"]
        for i in range(run["n"]):
            c = run["lo"] + step * (i + .5)
            if run["axis"] == "y":          # run marches along blueprint y
                x0, x1, y0, y1 = (run["const"] - lt / 2, run["const"] + lt / 2,
                                  c - lw / 2, c + lw / 2)
            else:
                x0, x1, y0, y1 = (c - lw / 2, c + lw / 2,
                                  run["const"] - lt / 2, run["const"] + lt / 2)
            a, b = P(x0, y0), P(x1, y1)
            o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2.5" '
                     'fill="%s" opacity=".82"/>'
                     % (min(a[0], b[0]), min(a[1], b[1]), abs(b[0] - a[0]),
                        abs(b[1] - a[1]), G.TABLE_FILL))
    for lb in G.VENDOR_LABELS:
        px, py = P(*lb["at"])
        rot = ' transform="rotate(-90 %.1f %.1f)"' % (px, py) if lb["rot"] else ""
        o.append('<g%s>%s</g>' % (rot, T(px, py, lb["text"], size=15, weight=600,
                                         fill=G.INK_SOFT, anchor="middle",
                                         ls=2.2, halo=3.4)))
    return o


def routes():
    o = []
    for r in G.ROUTES:
        o.append(path(r, stroke=G.ROUTE, stroke_width=3.2, opacity=".55",
                      stroke_dasharray="9 7", stroke_linecap="round",
                      stroke_linejoin="round"))
        sx, sy = P(*r[0])
        o.append('<circle cx="%.1f" cy="%.1f" r="4.6" fill="%s" opacity=".55"/>'
                 % (sx, sy, G.ROUTE))
    return o


def projection():
    o = [path(G.PROJECTION["path"], stroke=G.BRAND["magenta"], stroke_width=15,
              opacity=".16", stroke_linecap="round", stroke_linejoin="round"),
         path(G.PROJECTION["path"], stroke=G.BRAND["magenta"], stroke_width=6,
              stroke_linecap="round", stroke_linejoin="round")]
    px, py = P(*G.PROJECTION["label_at"])
    o.append(T(px, py, G.PROJECTION["label"], size=15, weight=600,
               fill=G.BRAND["magenta"], anchor="middle", ls=2.4, halo=3.8))
    o.append(chip(px - len(G.PROJECTION["label"]) * 5.3 - 26, py - 5,
                  G.PROJECTION["num"]))
    return o


def screen():
    a, b = P(*G.SCREEN["p0"]), P(*G.SCREEN["p1"])
    lx, ly = P(*G.SCREEN_LABEL_AT)
    return ['<path d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="5" '
            'stroke-linecap="round"/>' % (a[0], a[1], b[0], b[1],
                                          G.BRAND["magenta"]),
            T(lx, ly, G.SCREEN["label"], size=12, weight=600,
              fill=G.BRAND["magenta"], anchor="middle", ls=1.8, halo=3.2)]


def titles():
    o = []
    for t in G.TITLES:
        px, py = P(*t["at"])
        col = t.get("colour", G.INK)
        lines = wrap(t["text"], t.get("max_chars", 40))
        y = py - (len(lines) - 1) * t["size"] * .52
        for ln in lines:
            o.append(T(px, y, ln, size=t["size"], weight=t.get("weight", 600),
                       fill=col, anchor="middle", ls=1.6, halo=4.2))
            y += t["size"] * 1.04
        if t.get("sub"):
            o.append(T(px, y + t["sub_size"] * .28, t["sub"], size=t["sub_size"],
                       fill=G.INK_SOFT, anchor="middle", halo=3.6))
        if t.get("num"):
            w = max(len(l) for l in lines) * t["size"] * .55
            o.append(chip(px - w / 2 - 30, py - (len(lines) - 1) * t["size"] * .52
                          - t["size"] * .28, t["num"]))
    return o


# ------------------------------------------------------------- map furniture --
def chip(cx, cy, n, r=15):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="2.4"/>%s'
            % (cx, cy, r, G.BRAND["magenta"], G.PAPER,
               T(cx, cy + r * .36, str(n), size=r * 1.18, weight=600,
                 fill="#FFFFFF", anchor="middle")))


def badge(cx, cy, cat, icon, size=44):
    acc = G.ACCENT[cat]
    g = G.GLYPH_ON[acc]
    o = ['<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="10" fill="%s" '
         'stroke="%s" stroke-width="2.6"/>'
         % (cx - size / 2, cy - size / 2, size, size, acc, G.PAPER)]
    s = size * .66
    o.append('<use xlink:href="#ic-%s" x="%.1f" y="%.1f" width="%.1f" '
             'height="%.1f" color="%s" fill="%s"/>'
             % (icon, cx - s / 2, cy - s / 2, s, s, g, g))
    return o


def pill(cx, cy, text, size=15):
    w = len(text) * size * .47 + 22
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" '
            'fill="%s" stroke="#D9D7D6" stroke-width="1.2" opacity=".96"/>%s'
            % (cx - w / 2, cy - size * .82, w, size * 1.66, G.PAPER,
               T(cx, cy + size * .34, text, size=size, weight=600, fill=G.INK,
                 anchor="middle")))


def features():
    o = []
    for f in G.FEATURES:
        cx, cy = P(*f["at"])
        o += badge(cx, cy, f["cat"], f["icon"])
        o.append(chip(cx + 21, cy - 21, f["num"], r=13.5))
        side = f["side"]
        if side == "below":
            o.append(pill(cx, cy + 44, f["label"]))
        elif side == "right":
            o.append(pill(cx + 30 + len(f["label"]) * 3.6 + 12, cy, f["label"]))
        else:
            o.append(pill(cx - 30 - len(f["label"]) * 3.6 - 12, cy, f["label"]))
    return o


# ----------------------------------------------------------- scale / north --
def meta_strip():
    y = MY + MAP_H + 42
    ft = 20
    w = ft * G.PT_PER_FT * S
    o = [T(MX + 2, y - 16, "0", size=13, fill=G.INK_SOFT),
         T(MX + w, y - 16, "%d ft" % ft, size=13, fill=G.INK_SOFT,
           anchor="middle")]
    for i in range(4):
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="9" fill="%s"/>'
                 % (MX + i * w / 4, y - 9, w / 4, G.INK if i % 2 else "#FFFFFF"))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="9" fill="none" '
             'stroke="%s" stroke-width="1.4"/>' % (MX, y - 9, w, G.INK))
    # north arrow
    nx = MX + w + 92
    o += ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
          % (nx, y - 30, nx + 9.5, y - 2, nx - 9.5, y - 2, G.INK),
          T(nx + 20, y - 4, "N", size=19, weight=600, fill=G.INK)]
    o.append(T(nx + 62, y - 5, G.SHEET["scale_note"], size=15, fill=G.INK_SOFT))
    return o


# --------------------------------------------------------------- key panel --
def key_panel():
    o = [T(COL_X, 258, "MAP KEY", size=19, weight=600, fill=G.INK, ls=3.4)]
    y = 288
    for k in G.KEY:
        o.append(chip(COL_X + 16, y + 15, k["num"], r=13))
        mx = COL_X + 52
        if k.get("swatch"):
            o.append('<rect x="%d" y="%.1f" width="34" height="26" rx="6" '
                     'fill="%s" stroke="%s" stroke-width="1.6"/>'
                     % (mx, y + 2, G.FILL[k["cat"]], G.ACCENT[k["cat"]]))
        elif k.get("rule"):
            o.append('<rect x="%d" y="%.1f" width="34" height="7" rx="3.5" '
                     'fill="%s"/>' % (mx, y + 11, G.BRAND["magenta"]))
        elif k.get("table"):
            for i in range(2):
                o.append('<rect x="%d" y="%.1f" width="14" height="24" rx="2.5" '
                         'fill="%s" opacity=".82"/>' % (mx + i * 20, y + 3,
                                                        G.TABLE_FILL))
        else:
            o += badge(mx + 17, y + 15, k["cat"], k["icon"], size=30)
        o.append(T(COL_X + 104, y + 12, k["label"], size=17, weight=600,
                   fill=G.INK))
        o.append(T(COL_X + 104, y + 30, k["sub"], size=13.5, fill=G.INK_SOFT))
        y += 40
    # route note
    o += ['<path d="M %d %.1f L %d %.1f" stroke="%s" stroke-width="3.2" '
          'stroke-dasharray="9 7" stroke-linecap="round" opacity=".55"/>'
          % (COL_X + 4, y + 14, COL_X + 44, y + 14, G.ROUTE),
          T(COL_X + 58, y + 19, "Route from the hall to the washrooms",
            size=13.5, fill=G.INK_SOFT)]
    return o, y + 40


def card(x, y, w, title, lines, accent, h):
    o = ['<rect x="%d" y="%.1f" width="%d" height="%.1f" rx="12" fill="%s" '
         'opacity=".5"/>' % (x, y, w, h, G.FILL["corridor"]),
         '<rect x="%d" y="%.1f" width="5" height="%.1f" rx="2.5" fill="%s"/>'
         % (x, y, h, accent),
         T(x + 22, y + 30, title, size=17, weight=600, fill=accent, ls=2.4)]
    return o


def av_card(y):
    h = 186
    o = card(COL_X, y, COL_W, G.AV_CARD["title"].upper(), None,
             G.BRAND["magenta"], h)
    ry = y + 58
    for label, val in G.AV_CARD["rows"]:
        soft = label.startswith("  ")
        o.append(T(COL_X + 22, ry, label.strip(), size=14.5,
                   fill=G.INK_SOFT if soft else G.INK))
        o.append(T(COL_X + COL_W - 22, ry, val, size=14.5, weight=600,
                   fill=G.INK_SOFT if soft else G.INK, anchor="end"))
        ry += 21
    o.append(T(COL_X + 22, ry + 8, G.AV_CARD["note"], size=13.5,
               fill=G.INK_SOFT, op=.9))
    return o, y + h + 16


def floors_card(y):
    lines = wrap(G.FLOORS_CARD["body"], 54)
    h = 54 + len(lines) * 21
    o = card(COL_X, y, COL_W, G.FLOORS_CARD["title"].upper(), None,
             G.BRAND["cobalt"], h)
    ry = y + 58
    for ln in lines:
        o.append(T(COL_X + 22, ry, ln, size=14.5, fill=G.INK))
        ry += 21
    return o, y + h


def footer():
    y = SHEET_H - 44
    return ['<rect x="62" y="%.1f" width="%d" height="1.3" fill="#DCDAD9"/>'
            % (y - 26, SHEET_W - 124),
            T(62, y, G.SHEET["footer_left"], size=15, fill=G.INK_SOFT),
            T(SHEET_W - 62, y, G.SHEET["footer_right"], size=15,
              fill=G.INK_SOFT, anchor="end")]


# ------------------------------------------------------------------ output --
def document():
    parts = ['<rect width="%d" height="%d" fill="%s"/>' % (SHEET_W, SHEET_H, G.PAPER)]
    parts += header()
    parts += plan()
    parts += meta_strip()
    kp, y = key_panel()
    parts += kp
    ac, y = av_card(y)
    parts += ac
    fc, y = floors_card(y)
    parts += fc
    parts += footer()

    defs = ('<defs><style>%s</style>'
            '<linearGradient id="brandgrad" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0%%" stop-color="%s"/><stop offset="55%%" stop-color="%s"/>'
            '<stop offset="100%%" stop-color="%s"/></linearGradient>%s%s</defs>'
            % (font_face(), G.BRAND["magenta"], G.BRAND["violet"],
               G.BRAND["cobalt"], vector_logo_symbol(), icon_defs()))
    return ('<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 %d %d" '
            'width="%d" height="%d">%s%s</svg>'
            % (SHEET_W, SHEET_H, SHEET_W, SHEET_H, defs, "".join(parts)))


def render(svg_path, key):
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp()
    page = os.path.join(tmp, "p.html")
    with open(page, "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset=utf-8>"
                "<style>@page{size:24in 16in;margin:0}html,body{margin:0;padding:0}"
                "svg{display:block}</style>" + open(svg_path, encoding="utf-8").read())
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME,
                              args=["--no-sandbox", "--font-render-hinting=none"])
        pg = b.new_page(viewport={"width": SHEET_W, "height": SHEET_H},
                        device_scale_factor=2)
        pg.goto("file://" + page)
        pg.wait_for_timeout(700)
        pg.locator("svg").screenshot(path=os.path.join(DIST, key + ".png"))
        pg.pdf(path=os.path.join(DIST, key + ".pdf"), width="24in", height="16in",
               print_background=True,
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    os.makedirs(DIST, exist_ok=True)
    key = G.SHEET["key"]
    svg_path = os.path.join(DIST, key + ".svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(document())
    print("wrote", svg_path)
    render(svg_path, key)
    print("rendered", key + ".png /", key + ".pdf")


if __name__ == "__main__":
    main()
