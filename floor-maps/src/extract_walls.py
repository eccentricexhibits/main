#!/usr/bin/env python3
"""
Pull vector geometry out of the Design Exchange blueprint PDFs.

The blueprints draw the building in distinct graphic layers, which we separate
so the wayfinding map can re-style each one:

    walls   0.60 grey filled poche - structure and partitions
    dark    near-black filled shapes - glazed screen walls, thresholds
    light   0.80 grey fills - window glazing in the exterior walls
    detail  short dark strokes - stair treads, escalators, lift shafts,
            door swings, plumbing fixtures.  Long strokes are dimension
            lines and leaders, so anything with a bounding box bigger than
            DETAIL_MAX is dropped.

Red strokes (the blueprints' clear-width annotations) are dropped everywhere.

    python3 src/extract_walls.py            # writes geometry/f{1,2,3}.json
"""
import json
import os
import sys

import pymupdf

SRC = "/root/.claude/uploads/abe3e93b-9922-5128-8a37-4b5ba43cbaaf"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "geometry")

SHEETS = [
    ("3eb0a45f-Floor_1__Floor_Plan.pdf", "f1"),
    ("97d0aeb4-Floor_2__Floor_Plan.pdf", "f2"),
    ("498abfea-Floor_3__Floor_Plan.pdf", "f3"),
]

DETAIL_MAX = 95.0     # pt; larger stroked paths are dimension lines


def path_d(p):
    out = []
    for it in p["items"]:
        k = it[0]
        if k == "l":
            a, b = it[1], it[2]
            out.append("M%.2f,%.2fL%.2f,%.2f" % (a.x, a.y, b.x, b.y))
        elif k == "c":
            a, b, c, d = it[1], it[2], it[3], it[4]
            out.append("M%.2f,%.2fC%.2f,%.2f %.2f,%.2f %.2f,%.2f"
                       % (a.x, a.y, b.x, b.y, c.x, c.y, d.x, d.y))
        elif k == "re":
            r = it[1]
            out.append("M%.2f,%.2fH%.2fV%.2fH%.2fZ" % (r.x0, r.y0, r.x1, r.y1, r.x0))
        elif k == "qu":
            q = it[1]
            out.append("M%.2f,%.2fL%.2f,%.2fL%.2f,%.2fL%.2f,%.2fZ"
                       % (q.ul.x, q.ul.y, q.ur.x, q.ur.y, q.lr.x, q.lr.y, q.ll.x, q.ll.y))
    return "".join(out)


def is_grey(c, lo=0.50, hi=0.72):
    return c is not None and lo <= c[0] <= hi and abs(c[0] - c[1]) < 0.06 and abs(c[1] - c[2]) < 0.06


def is_pale(c):
    return c is not None and 0.74 <= c[0] <= 0.88 and abs(c[0] - c[1]) < 0.06 and abs(c[1] - c[2]) < 0.06


def is_dark(c):
    return c is not None and max(c) < 0.30


def is_red(c):
    return c is not None and c[0] > 0.8 and c[1] < 0.45 and c[2] < 0.35


def extract(pdf, out_path):
    doc = pymupdf.open(pdf)
    page = doc[0]
    walls, dark, light, detail = [], [], [], []

    for p in page.get_drawings():
        if is_red(p.get("color")) or is_red(p.get("fill")):
            continue
        d = path_d(p)
        if not d:
            continue
        r = p["rect"]
        fill = p.get("fill")
        if is_grey(fill):
            walls.append(d)
        elif is_dark(fill):
            dark.append(d)
        elif is_pale(fill):
            light.append(d)
        elif p.get("color") is not None and max(r.width, r.height) <= DETAIL_MAX:
            detail.append(d)

    xs, ys = [], []
    for p in page.get_drawings():
        if is_grey(p.get("fill")):
            xs += [p["rect"].x0, p["rect"].x1]
            ys += [p["rect"].y0, p["rect"].y1]
    bbox = [min(xs), min(ys), max(xs), max(ys)]

    json.dump({"bbox": bbox, "walls": walls, "dark": dark, "light": light,
               "detail": detail, "page": [page.rect.width, page.rect.height]},
              open(out_path, "w"))
    print("%-38s walls=%-4d dark=%-4d light=%-4d detail=%-4d bbox=%s"
          % (os.path.basename(pdf), len(walls), len(dark), len(light), len(detail),
             [round(v) for v in bbox]))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fname, key in SHEETS:
        src = os.path.join(SRC, fname)
        if not os.path.exists(src):
            sys.exit("missing source blueprint: " + src)
        extract(src, os.path.join(OUT, key + ".json"))
