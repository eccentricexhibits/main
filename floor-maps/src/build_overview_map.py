#!/usr/bin/env python3
"""
Build the "Getting Around" sheet in the event-map style.

    python3 src/build_overview_map.py

Unlike the three floor sheets this one is not a plan. It draws a section: the
levels stacked as bands, with each vertical route running across the bands it
serves and a stop marked at every level it reaches — a transit diagram for the
building. See overview_data.py for why that shape was chosen.

Chrome (header, key card, notes cards, footer) is shared with the floor sheets
via event_map, so the whole set stays one design.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import event_map as E
import overview_data as G
from build import T, wrap

# ---- section geometry, inside event_map's standard panel
X0, X1 = E.PANEL[0], E.PANEL[2]          # 62 .. 1150
LANE_TOP = 250                            # badges + labels above the bands
BAND_TOP = 330
BAND_H, BAND_GAP = 108, 79
LABEL_W = 460                             # level name column, left of the lanes
LANE_X0, LANE_X1 = 470, 1120
LANE_W = 24


def band_y(i):
    top = BAND_TOP + i * (BAND_H + BAND_GAP)
    return top, top + BAND_H, top + BAND_H / 2


def lane_x(i):
    step = (LANE_X1 - LANE_X0) / (len(G.LANES) - 1)
    return LANE_X0 + i * step


def levels_index():
    return {lv["id"]: i for i, lv in enumerate(G.LEVELS)}


def bands():
    o = []
    for i, lv in enumerate(G.LEVELS):
        top, bot, mid = band_y(i)
        o.append('<rect x="%d" y="%.1f" width="%d" height="%d" rx="14" '
                 'fill="%s" stroke="#E4E2E1" stroke-width="1.4"/>'
                 % (X0, top, X1 - X0, BAND_H, G.FILL[lv["cat"]]))
        # level chip
        plain = lv.get("chip_cat") == "plain"
        col = G.INK_SOFT if plain else G.BRAND["magenta"]
        o += ['<rect x="%d" y="%.1f" width="56" height="56" rx="10" fill="%s"/>'
              % (X0 + 20, mid - 28, col),
              T(X0 + 48, mid + 12, lv["id"], size=32, weight=600, fill="#FFFFFF",
                anchor="middle")]
        o.append(T(X0 + 96, mid - 4, lv["name"], size=27, weight=600, fill=G.INK))
        o.append(T(X0 + 96, mid + 22, lv["desc"], size=14, fill=G.INK_SOFT))
        # washroom marker, the question guests ask most
        if lv["washrooms"] is None:
            continue
        bx = X0 + 323
        if lv["washrooms"]:
            o += E.badge(bx, mid, "washroom", "washroom", size=34)
            o.append(E.chip(bx + 16, mid - 16, 7, r=11.5))
        else:
            o += ['<rect x="%.1f" y="%.1f" width="34" height="34" rx="8" '
                  'fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 3" '
                  'opacity=".7"/>' % (bx - 17, mid - 17, G.INK_SOFT),
                  T(bx, mid + 6, "—", size=20, weight=600, fill=G.INK_SOFT,
                    anchor="middle")]
            o.append(T(bx, mid + 34, "no washrooms", size=11, weight=600,
                       fill=G.INK_SOFT, anchor="middle", ls=.6))
    return o


def lanes():
    idx = levels_index()
    o = []
    for i, ln in enumerate(G.LANES):
        cx = lane_x(i)
        acc = G.ACCENT[ln["cat"]]
        stops = sorted(idx[l] for l in ln["levels"])
        y_top = band_y(stops[0])[2]
        y_bot = band_y(stops[-1])[2]
        o += ['<rect x="%.1f" y="%.1f" width="%d" height="%.1f" rx="%d" '
              'fill="%s" opacity=".16"/>'
              % (cx - LANE_W / 2, y_top, LANE_W, y_bot - y_top, LANE_W // 2, acc),
              '<path d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="3.4" '
              'stroke-linecap="round" opacity=".75"/>' % (cx, y_top, cx, y_bot, acc)]
        for s in stops:
            o.append('<circle cx="%.1f" cy="%.1f" r="9" fill="%s" stroke="%s" '
                     'stroke-width="2.6"/>' % (cx, band_y(s)[2], acc, G.PAPER))
        # header: badge, number chip, name
        o += E.badge(cx, LANE_TOP, ln["cat"], ln["icon"], size=42)
        o.append(E.chip(cx + 20, LANE_TOP - 20, ln["num"], r=13))
        ly = LANE_TOP + 40
        for line in wrap(ln["label"], 11):
            o.append(T(cx, ly, line, size=13.5, weight=600, fill=G.INK,
                       anchor="middle"))
            ly += 16
    return o


def note_strip():
    y = BAND_TOP + len(G.LEVELS) * (BAND_H + BAND_GAP) - BAND_GAP + 40
    return [T(X0, y, G.SHEET["note"], size=15, fill=G.INK_SOFT)]


def main():
    E.configure_chrome(G)
    parts = ['<rect width="%d" height="%d" fill="%s"/>'
             % (E.SHEET_W, E.SHEET_H, G.PAPER)]
    parts += E.header()
    parts += bands()
    parts += lanes()
    parts += note_strip()
    parts += E.right_column()
    E.emit(E.svg_wrap(parts), G.SHEET["key"])


if __name__ == "__main__":
    main()
