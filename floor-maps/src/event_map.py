#!/usr/bin/env python3
"""
Renderer for the guest-facing *event map* sheets.

One floor per data module (gallery_data, lobby_data, ...). The module supplies
geometry, zones, pins and copy; everything here is layout and drawing, so a new
floor is a data file rather than new code.

    from event_map import build
    import lobby_data
    build(lobby_data)

Every sheet is 24 x 16 in landscape: plan on the left, key card and notes on
the right. The plan is auto-fitted to the panel, so floors with different
proportions all fill the same frame.

The drawing order is what makes these read as event maps rather than
blueprints: room floors tinted by category first, the venue's own poche and
detail linework over them, then furniture, numbered pins and labels on top.
Tinting *under* the poche means the simplified zone polygons in the data
modules never have to line up exactly with the real walls.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import CHROME, font_face, icon_defs, T, vector_logo_symbol, wrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
GEO = os.path.join(ROOT, "geometry")

# 24 x 16 in at 72 units/in
SHEET_W, SHEET_H = 1728, 1152
HEAD_H, RULE_H = 168, 7

# plan panel and the right-hand column
PANEL = (62, 238, 1150, 1008)
COL_X, COL_W = 1196, 472
ROW_H = 38

# A poche path bigger than this (blueprint pt^2) is a solid mass — a service
# core or an adjoining structure — not a wall, and is toned as floor.
MASS_AREA = 9000

_CMD = re.compile(r"([MLHVCSQTAZmlhvcsqtaz])([^MLHVCSQTAZmlhvcsqtaz]*)")
_NUM = re.compile(r"-?\d+\.?\d*")

G = None
S = MX = MY = MAP_W = MAP_H = 0.0
PLAN_XF = ""


def configure(mod):
    """Bind a floor's data module and fit its plan to the panel."""
    global G, S, MX, MY, MAP_W, MAP_H, PLAN_XF
    G = mod
    fw, fh = G.FRAME[3] - G.FRAME[1], G.FRAME[2] - G.FRAME[0]
    px, py, pw, ph = PANEL[0], PANEL[1], PANEL[2] - PANEL[0], PANEL[3] - PANEL[1]
    S = min(pw / fw, ph / fh)
    MAP_W, MAP_H = fw * S, fh * S
    MX, MY = px + (pw - MAP_W) / 2, py + (ph - MAP_H) / 2
    # the same rotation as an SVG matrix, so blueprint path data goes in as-is
    PLAN_XF = "matrix(0,%.6f,%.6f,0,%.4f,%.4f)" % (
        -S, S, MX - S * G.FRAME[1], MY + S * G.FRAME[2])


def configure_chrome(mod):
    """Bind a data module for the shared chrome only — header, key card, notes
    cards, footer. Used by sheets that draw their own body and have no plan to
    fit, such as the Getting Around section."""
    global G
    G = mod


def P(x, y):
    """Blueprint point -> sheet point, rotated 90 deg CCW so north is up."""
    return (MX + (y - G.FRAME[1]) * S, MY + (G.FRAME[2] - x) * S)


def poly(pts, **kw):
    d = " ".join("%.2f,%.2f" % P(*p) for p in pts)
    a = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<polygon points="%s" %s/>' % (d, a)


def path(pts, **kw):
    d = "M " + " L ".join("%.2f %.2f" % P(*p) for p in pts)
    a = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<path d="%s" fill="none" %s/>' % (d, a)


def opt(name, default=()):
    return getattr(G, name, default)


def path_points(d):
    """Vertices of an absolute SVG path. The blueprints use M/L/H/V/C/Z, and
    H and V carry a single coordinate, so the numbers cannot just be paired
    off two at a time."""
    pts, cx, cy = [], 0.0, 0.0
    for cmd, body in _CMD.findall(d):
        n = [float(v) for v in _NUM.findall(body)]
        if cmd == "H":
            for v in n:
                cx = v
                pts.append((cx, cy))
        elif cmd == "V":
            for v in n:
                cy = v
                pts.append((cx, cy))
        elif cmd in "MLT":
            for i in range(0, len(n) - 1, 2):
                cx, cy = n[i], n[i + 1]
                pts.append((cx, cy))
        elif cmd in "CSQA":
            # only the on-curve endpoint matters for extent and area
            if len(n) >= 2:
                cx, cy = n[-2], n[-1]
                pts.append((cx, cy))
    return pts


def is_mass(d):
    """True for a solid block of poche — a service core or an adjoining
    structure — as opposed to a run of wall.

    Bounding-box area alone is not enough: a long diagonal wall has a huge
    box but encloses almost nothing, so the polygon's own area has to fill a
    fair share of that box before it counts as a mass.
    """
    pts = path_points(d)
    if len(pts) < 3:
        return False
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    box = (max(xs) - min(xs)) * (max(ys) - min(ys))
    if box <= MASS_AREA:
        return False
    area = abs(sum(xs[i] * ys[(i + 1) % len(pts)] - xs[(i + 1) % len(pts)] * ys[i]
                   for i in range(len(pts)))) / 2
    return area / box > 0.55


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
         T(246 + len(G.SHEET["title"]) * 30 + 30, 120, G.SHEET["tagline"],
           size=23, fill="#FFFFFF", op=.78),
         '<rect x="%d" y="34" width="118" height="110" rx="10" fill="%s"/>'
         % (SHEET_W - 182, G.BRAND["magenta"]),
         T(SHEET_W - 123, 72, G.SHEET.get("chip_top", "LEVEL"), size=15,
           weight=600, fill="#FFFFFF", anchor="middle", ls=2.6),
         T(SHEET_W - 123, 126, G.SHEET.get("chip_main", G.SHEET.get("level", "")),
           size=G.SHEET.get("chip_size", 52), weight=600, fill="#FFFFFF",
           anchor="middle")]
    return o


# -------------------------------------------------------------------- plan --
def plan():
    a, b = P(G.PLATE[0], G.PLATE[1]), P(G.PLATE[2], G.PLATE[3])
    o = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
         % (min(a[0], b[0]), min(a[1], b[1]), abs(b[0] - a[0]), abs(b[1] - a[1]),
            G.FILL["staff"])]
    for z in G.ZONES:
        o.append(poly(z["pts"], fill=G.FILL[z["cat"]], stroke="none"))
    o += base_plan()
    o += overheads()
    o += small_labels()
    o += furniture()
    o += routes()
    o += surfaces()
    o += titles()
    o += features()
    return o


def base_plan():
    """Wall poche, glazing and thin detail, from the blueprint's own vectors."""
    geo = json.load(open(os.path.join(GEO, G.SHEET["geometry"])))
    clip = "plan-clip"
    o = ['<clipPath id="%s"><rect x="%.1f" y="%.1f" width="%.1f" '
         'height="%.1f"/></clipPath>' % (clip, MX, MY, MAP_W, MAP_H),
         '<g clip-path="url(#%s)">' % clip, '<g transform="%s">' % PLAN_XF]
    for d in geo.get("light", []):
        o.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, G.GLAZE_FILL))
    for d in geo["walls"]:
        fill = G.MASS_FILL if is_mass(d) else G.WALL_FILL
        o.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, fill))
    for d in geo.get("dark", []):
        o.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, G.WALL_DARK))
    o.append("</g>")
    o.append('<g transform="%s" fill="none" stroke="%s" stroke-width="%.4f" '
             'stroke-linejoin="round" stroke-opacity=".9">'
             % (PLAN_XF, G.WALL_EDGE, 0.95 / S))
    for d in geo["walls"]:
        o.append('<path d="%s"/>' % d)
    o.append("</g>")
    o.append('<g transform="%s" fill="none" stroke="%s" stroke-width="%.4f" '
             'stroke-linejoin="round" stroke-linecap="round" stroke-opacity=".62">'
             % (PLAN_XF, G.DETAIL_INK, 0.7 / S))
    for d in geo.get("detail", []):
        o.append('<path d="%s"/>' % d)
    o.append("</g></g>")
    return o


def overheads():
    """Things that cross above the floor rather than sitting on it — the
    Trading Floor's bridge. Drawn as a dashed band so it reads as overhead,
    not as a room."""
    o = []
    for ov in opt("OVERHEAD"):
        x0, y0, x1, y1 = ov["box"]
        o.append(poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                      fill=G.INK_SOFT, fill_opacity=".07", stroke=G.INK_SOFT,
                      stroke_width=1.6, stroke_dasharray="7 6",
                      stroke_opacity=".55"))
        if ov.get("label"):
            px, py = P(*ov["label_at"])
            g = T(px, py, ov["label"], size=ov.get("size", 12.5), weight=600,
                  fill=G.INK_SOFT, anchor="middle", ls=2.4, halo=3.2)
            if ov.get("rot"):
                g = '<g transform="rotate(-90 %.1f %.1f)">%s</g>' % (px, py, g)
            o.append(g)
    return o


def small_labels():
    """Quiet in-plan captions — corridors, back-of-house, and the like."""
    o = []
    for lb in opt("SMALL_LABELS"):
        px, py = P(*lb["at"])
        g = T(px, py, lb["text"], size=lb.get("size", 12.5), weight=600,
              fill=G.INK_SOFT, anchor="middle", ls=2.4, halo=3.0)
        if lb.get("rot"):
            g = '<g transform="rotate(-90 %.1f %.1f)">%s</g>' % (px, py, g)
        o.append(g)
    return o


def furniture():
    """Repeated runs (vendor tables), lattices (seating) and one-off blocks."""
    o = []
    for run in opt("RUNS"):
        lw, lt = run.get("len", 27.0), run.get("depth", 13.0)
        step = (run["hi"] - run["lo"]) / run["n"]
        for i in range(run["n"]):
            c = run["lo"] + step * (i + .5)
            if run["axis"] == "y":
                box = (run["const"] - lt / 2, c - lw / 2, run["const"] + lt / 2, c + lw / 2)
            else:
                box = (c - lw / 2, run["const"] - lt / 2, c + lw / 2, run["const"] + lt / 2)
            o.append(furn_rect(*box))
    for g in opt("GRIDS"):
        nx, ny = g["nx"], g["ny"]
        w, d = g.get("w", 6.5), g.get("d", 7.5)
        for i in range(nx):
            x = g["x0"] + (g["x1"] - g["x0"]) * i / max(nx - 1, 1)
            for j in range(ny):
                y = g["y0"] + (g["y1"] - g["y0"]) * j / max(ny - 1, 1)
                o.append(furn_rect(x - w / 2, y - d / 2, x + w / 2, y + d / 2))
    for blk in opt("BLOCKS"):
        o.append(furn_rect(*blk["box"]))
    for lb in opt("RUN_LABELS"):
        px, py = P(*lb["at"])
        g = T(px, py, lb["text"], size=15, weight=600, fill=G.INK_SOFT,
              anchor="middle", ls=2.2, halo=3.4)
        if lb.get("rot"):
            g = '<g transform="rotate(-90 %.1f %.1f)">%s</g>' % (px, py, g)
        o.append(g)
    return o


def furn_rect(x0, y0, x1, y1):
    a, b = P(x0, y0), P(x1, y1)
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2.5" '
            'fill="%s" opacity=".82"/>'
            % (min(a[0], b[0]), min(a[1], b[1]), abs(b[0] - a[0]),
               abs(b[1] - a[1]), G.TABLE_FILL))


def routes():
    o = []
    for r in opt("ROUTES"):
        o.append(path(r, stroke=G.ROUTE, stroke_width=3.2, opacity=".55",
                      stroke_dasharray="9 7", stroke_linecap="round",
                      stroke_linejoin="round"))
        sx, sy = P(*r[0])
        o.append('<circle cx="%.1f" cy="%.1f" r="4.6" fill="%s" opacity=".55"/>'
                 % (sx, sy, G.ROUTE))
    return o


def surfaces():
    """Projection runs, LED and screen walls — heavy magenta rules."""
    o = []
    for s in opt("SURFACES"):
        pts = s["path"]
        if s.get("glow", True):
            o.append(path(pts, stroke=G.BRAND["magenta"], stroke_width=15,
                          opacity=".16", stroke_linecap="round",
                          stroke_linejoin="round"))
        o.append(path(pts, stroke=G.BRAND["magenta"],
                      stroke_width=s.get("w", 6), stroke_linecap="round",
                      stroke_linejoin="round"))
        if not s.get("label"):
            continue
        px, py = P(*s["label_at"])
        size = s.get("size", 15)
        g = T(px, py, s["label"], size=size, weight=600,
              fill=G.BRAND["magenta"], anchor="middle", ls=2.4, halo=3.8)
        if s.get("rot"):
            g = '<g transform="rotate(-90 %.1f %.1f)">%s</g>' % (px, py, g)
        o.append(g)
        if s.get("num"):
            reach = len(s["label"]) * size * .35 + 26
            cx, cy = (px, py + reach) if s.get("rot") else (px - reach, py - 5)
            o.append(chip(cx, cy, s["num"]))
    return o


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
            o.append(chip(px - w / 2 - 30,
                          py - (len(lines) - 1) * t["size"] * .52 - t["size"] * .28,
                          t["num"]))
    return o


# ------------------------------------------------------------ map furniture --
def chip(cx, cy, n, r=15):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="2.4"/>%s'
            % (cx, cy, r, G.BRAND["magenta"], G.PAPER,
               T(cx, cy + r * .36, str(n), size=r * 1.18, weight=600,
                 fill="#FFFFFF", anchor="middle")))


def badge(cx, cy, cat, icon, size=44):
    acc = G.ACCENT[cat]
    gl = G.GLYPH_ON[acc]
    s = size * .66
    return ['<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="10" fill="%s" '
            'stroke="%s" stroke-width="2.6"/>'
            % (cx - size / 2, cy - size / 2, size, size, acc, G.PAPER),
            '<use xlink:href="#ic-%s" x="%.1f" y="%.1f" width="%.1f" '
            'height="%.1f" color="%s" fill="%s"/>'
            % (icon, cx - s / 2, cy - s / 2, s, s, gl, gl)]


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
        sz = f.get("size", 44)
        o += badge(cx, cy, f["cat"], f["icon"], size=sz)
        o.append(chip(cx + sz / 2 - 1, cy - sz / 2 + 1, f["num"], r=13.5))
        side, lab = f["side"], f["label"]
        if side == "below":
            o.append(pill(cx, cy + sz, lab))
        elif side == "above":
            o.append(pill(cx, cy - sz, lab))
        elif side == "right":
            o.append(pill(cx + sz * .68 + len(lab) * 3.6 + 12, cy, lab))
        else:
            o.append(pill(cx - sz * .68 - len(lab) * 3.6 - 12, cy, lab))
    return o


# ------------------------------------------------------------ scale / north --
def meta_strip():
    y = MY + MAP_H + 42
    ft = 20
    w = ft * G.PT_PER_FT * S
    x0 = PANEL[0]
    o = [T(x0 + 2, y - 16, "0", size=13, fill=G.INK_SOFT),
         T(x0 + w, y - 16, "%d ft" % ft, size=13, fill=G.INK_SOFT, anchor="middle")]
    for i in range(4):
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="9" fill="%s"/>'
                 % (x0 + i * w / 4, y - 9, w / 4, G.INK if i % 2 else "#FFFFFF"))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="9" fill="none" '
             'stroke="%s" stroke-width="1.4"/>' % (x0, y - 9, w, G.INK))
    nx = x0 + w + 92
    o += ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
          % (nx, y - 30, nx + 9.5, y - 2, nx - 9.5, y - 2, G.INK),
          T(nx + 20, y - 4, "N", size=19, weight=600, fill=G.INK),
          T(nx + 62, y - 5, G.SHEET["scale_note"], size=15, fill=G.INK_SOFT)]
    return o


# --------------------------------------------------------------- key + cards --
def key_panel():
    card_h = 60 + len(G.KEY) * ROW_H + (44 if opt("ROUTES") else 12)
    o = ['<rect x="%d" y="238" width="%d" height="%d" rx="14" fill="%s" '
         'stroke="#E4E2E1" stroke-width="1.6"/>' % (COL_X, COL_W, card_h, G.PAPER),
         T(COL_X + 22, 278, "MAP KEY", size=19, weight=600, fill=G.INK, ls=3.4)]
    y = 296
    for i, k in enumerate(G.KEY):
        if i:
            o.append('<rect x="%d" y="%.1f" width="%d" height="1" fill="#EEECEB"/>'
                     % (COL_X + 22, y - 2, COL_W - 44))
        o.append(chip(COL_X + 38, y + 15, k["num"], r=13))
        mx = COL_X + 74
        if k.get("swatch"):
            o.append('<rect x="%d" y="%.1f" width="34" height="26" rx="6" '
                     'fill="%s" stroke="%s" stroke-width="1.6"/>'
                     % (mx, y + 2, G.FILL[k["cat"]], G.ACCENT[k["cat"]]))
        elif k.get("rule"):
            o.append('<rect x="%d" y="%.1f" width="34" height="7" rx="3.5" '
                     'fill="%s"/>' % (mx, y + 11, G.BRAND["magenta"]))
        elif k.get("dash"):
            o.append('<rect x="%d" y="%.1f" width="34" height="26" rx="4" '
                     'fill="%s" fill-opacity=".07" stroke="%s" stroke-width="1.6" '
                     'stroke-dasharray="5 4" stroke-opacity=".55"/>'
                     % (mx, y + 2, G.INK_SOFT, G.INK_SOFT))
        elif k.get("table"):
            for j in range(2):
                o.append('<rect x="%d" y="%.1f" width="14" height="24" rx="2.5" '
                         'fill="%s" opacity=".82"/>' % (mx + j * 20, y + 3, G.TABLE_FILL))
        else:
            o += badge(mx + 16, y + 15, k["cat"], k["icon"], size=29)
        o.append(T(COL_X + 126, y + 12, k["label"], size=16.5, weight=600, fill=G.INK))
        o.append(T(COL_X + 126, y + 29, k["sub"], size=13, fill=G.INK_SOFT))
        y += ROW_H
    if opt("ROUTES"):
        o += ['<path d="M %d %.1f L %d %.1f" stroke="%s" stroke-width="3.2" '
              'stroke-dasharray="9 7" stroke-linecap="round" opacity=".55"/>'
              % (COL_X + 26, y + 16, COL_X + 66, y + 16, G.ROUTE),
              T(COL_X + 80, y + 21, G.ROUTE_LABEL, size=13, fill=G.INK_SOFT)]
    return o, 238 + card_h + 18


def cards(y):
    o = []
    for c in G.CARDS:
        accent = G.BRAND[c.get("accent", "magenta")]
        if c.get("rows"):
            h = 58 + len(c["rows"]) * 21 + (20 if c.get("note") else 4)
        else:
            lines = wrap(c["body"], 54)
            h = 50 + len(lines) * 21
        o += ['<rect x="%d" y="%.1f" width="%d" height="%.1f" rx="12" fill="%s" '
              'opacity=".5"/>' % (COL_X, y, COL_W, h, G.FILL["corridor"]),
              '<rect x="%d" y="%.1f" width="5" height="%.1f" rx="2.5" fill="%s"/>'
              % (COL_X, y, h, accent),
              T(COL_X + 22, y + 30, c["title"].upper(), size=17, weight=600,
                fill=accent, ls=2.4)]
        ry = y + 58
        if c.get("rows"):
            for label, val in c["rows"]:
                soft = label.startswith("  ")
                col = G.INK_SOFT if soft else G.INK
                o.append(T(COL_X + 22, ry, label.strip(), size=14.5, fill=col))
                o.append(T(COL_X + COL_W - 22, ry, val, size=14.5, weight=600,
                           fill=col, anchor="end"))
                ry += 21
            if c.get("note"):
                o.append(T(COL_X + 22, ry + 8, c["note"], size=13.5,
                           fill=G.INK_SOFT, op=.9))
        else:
            for ln in wrap(c["body"], 54):
                o.append(T(COL_X + 22, ry, ln, size=14.5, fill=G.INK))
                ry += 21
        y += h + 12
    return o, y


def footer():
    y = SHEET_H - 44
    return ['<rect x="62" y="%.1f" width="%d" height="1.3" fill="#DCDAD9"/>'
            % (y - 26, SHEET_W - 124),
            T(62, y, G.SHEET["footer_left"], size=15, fill=G.INK_SOFT),
            T(SHEET_W - 62, y, G.SHEET["footer_right"], size=15, fill=G.INK_SOFT,
              anchor="end")]


# ------------------------------------------------------------------- output --
def document():
    parts = ['<rect width="%d" height="%d" fill="%s"/>' % (SHEET_W, SHEET_H, G.PAPER)]
    parts += header()
    parts += plan()
    parts += meta_strip()
    parts += right_column()
    return svg_wrap(parts)


def right_column():
    """Key card plus the notes cards, shared by every sheet."""
    kp, y = key_panel()
    cb, y = cards(y)
    if y > SHEET_H - 70:
        print("  ! right column overruns the sheet by %d pt" % (y - (SHEET_H - 70)))
    return kp + cb + footer()


def svg_wrap(parts):
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


def emit(svg, key):
    """Write + rasterise an already-assembled sheet."""
    os.makedirs(DIST, exist_ok=True)
    svg_path = os.path.join(DIST, key + ".svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    render(svg_path, key)
    print("built", key)
    return key


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


def build(mod):
    configure(mod)
    os.makedirs(DIST, exist_ok=True)
    key = G.SHEET["key"]
    svg_path = os.path.join(DIST, key + ".svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(document())
    render(svg_path, key)
    print("built", key)
    return key
