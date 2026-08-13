#!/usr/bin/env python3
"""
Build the registered flip-book: one PDF, four pages, one scale and one origin.

    python3 src/build_flipbook.py     ->  dist/building-flipbook.pdf

Every page draws its floor into the *same* frame at the *same* scale, so the
sheet's frame, scale bar and north arrow never move. Flip through the pages
and anything that holds still is genuinely in the same plan position.

REGISTRATION — read before trusting a position
----------------------------------------------
The three DX blueprints were each drawn on their own sheet, so whether they
share an origin is an empirical question. Cross-correlating the extracted
wall outlines against Floor 1 answers it:

    Floor 2   overlap peaks at 40.0%, 8.6 sigma above background,
              after a nudge of (-4, -8) pt = (-0.9, -1.8) ft.
              Envelope edges then agree within 2 ft on all four sides.
              -> Floors 1 and 2 share an origin. The nudge is applied.

    Floor 3   overlap peaks at 21.1%, only 4.4 sigma, and no rigid move
              fixes it: the drawn footprint is 92 x 129 ft against Floor 1's
              102 x 117 ft — inset ~5 ft on BOTH long sides while running
              13.7 ft further at the far end. Mirroring is worse (20.2%).
              The clincher is the freight shaft: blueprint x ~105 on Floors
              1-2 but x ~467 on Floor 3, still ~87 ft apart after the
              best-fit offset. A shaft cannot move 87 ft between floors.
              -> Floor 3 does NOT register. It gets two pages: one on its
                 own drawn origin, one best-fit shifted, both labelled.

Either Floor 3 is drawn on a different origin, or the Gallery occupies a
different volume of the DX complex. The drawings cannot say which — it is a
venue question. See HANDOFF section 4.6 and 9.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymupdf

import event_map as E
import gallery_data
import lobby_data
import trading_data

# Shared frame: the union of all four page placements plus a small margin,
# in blueprint pt, so no floor is clipped on any page.
SHARED = (64.0, 146.0, 543.0, 767.0)

# Measured registration offsets onto Floor 1, blueprint pt (see the header).
OFF_L2 = (-4.0, -8.0)
OFF_L3 = (28.0, -36.0)

OUT = "building-flipbook.pdf"


class Page:
    """A data module with a few SHEET/CARDS fields overridden for this page."""

    def __init__(self, mod, **over):
        self._m, self._o = mod, over

    def __getattr__(self, k):
        try:
            return self._o[k]
        except KeyError:
            return getattr(self._m, k)


def sheet(mod, key, **over):
    s = dict(mod.SHEET)
    s.update(over)
    s["key"] = key
    return s


NOT_REGISTERED = dict(
    title="This page does not register", accent="magenta",
    body="Level 3's drawing does not share an origin with Levels 1 and 2. "
         "Its drawn footprint is 92 by 129 ft against Level 1's 102 by 117, "
         "and the freight shaft sits about 87 ft away from where Levels 1 "
         "and 2 put it. Compare sizes across pages, not positions.")

BEST_FIT = dict(
    title="Best-fit alignment — unverified", accent="magenta",
    body="The same floor shifted 6.2 ft east and 8.0 ft north, the offset "
         "that best matches Level 1's walls. It is the closest fit available, "
         "not a confirmed one: the footprints differ in size, so no shift can "
         "truly align them. Treat any position read across pages as indicative.")


PAGES = [
    (Page(lobby_data,
          SHEET=sheet(lobby_data, "flip-1-lobby",
                      scale_note="Shared frame · 4.5 pt = 1 ft on every page · "
                                 "north up · Level 1 is the registration datum")),
     (0.0, 0.0)),
    (Page(trading_data,
          SHEET=sheet(trading_data, "flip-2-trading-floor",
                      scale_note="Shared frame · registers with Level 1 to about "
                                 "2 ft · nudged 1.8 ft to fit")),
     OFF_L2),
    (Page(gallery_data,
          SHEET=sheet(gallery_data, "flip-3-gallery-as-drawn",
                      tagline="As drawn — does not register with Levels 1–2",
                      footer_left="Event floor map · Gallery, Level 3 — as drawn",
                      scale_note="Shared frame · Level 3 on its own drawn origin — "
                                 "positions are NOT comparable to pages 1–2"),
          CARDS=[NOT_REGISTERED]),
     (0.0, 0.0)),
    (Page(gallery_data,
          SHEET=sheet(gallery_data, "flip-4-gallery-best-fit",
                      tagline="Best-fit aligned to Level 1 — unverified",
                      footer_left="Event floor map · Gallery, Level 3 — best-fit",
                      scale_note="Shared frame · Level 3 shifted +6.2 ft east, "
                                 "+8.0 ft north — alignment unverified"),
          CARDS=[BEST_FIT]),
     OFF_L3),
]


def main():
    os.makedirs(E.DIST, exist_ok=True)
    keys = []
    for page, off in PAGES:
        E.configure_shared(page, SHARED, off)
        key = page.SHEET["key"]
        svg = os.path.join(E.DIST, key + ".svg")
        with open(svg, "w", encoding="utf-8") as f:
            f.write(E.document())
        E.render(svg, key)
        keys.append(key)
        print("built", key)

    book = pymupdf.open()
    for key in keys:
        book.insert_pdf(pymupdf.open(os.path.join(E.DIST, key + ".pdf")))
    path = os.path.join(E.DIST, OUT)
    book.save(path)
    book.close()
    print("built %s (%d pages)" % (OUT, len(keys)))


if __name__ == "__main__":
    main()
