#!/usr/bin/env python3
"""Extract the Vector logo artwork from the supplied Illustrator EPS.

    python3 animation/tools/eps-to-svg.py <in.eps> <out.svg>

The EPS is an AI11 EPS whose page content is plain PostScript using Illustrator's
short operator names — mo/li/cv/cp for path construction, cmyk for colour, f for
fill. That is enough to recover the artwork exactly, with no rasterising and no
Ghostscript (which is not available in this container).

Illustrator emits `1 -1 scale 0 -H translate` at the top of the page, which puts
the path coordinates into a y-down space with the origin at the top left — i.e.
already SVG's convention, so the numbers transfer unchanged.
"""
import re
import sys


def cmyk_to_hex(c, m, y, k):
    r = round(255 * (1 - min(1, c + k)))
    g = round(255 * (1 - min(1, m + k)))
    b = round(255 * (1 - min(1, y + k)))
    return f"#{r:02X}{g:02X}{b:02X}"


def parse(text):
    """Yield (fill_hex, path_d) for every filled path in page order."""
    body = text[text.find("%%EndPageSetup"):]
    tokens = body.split()
    stack = []
    d = []
    colour = "#000000"
    out = []
    seen_clip = False

    for tok in tokens:
        try:
            stack.append(float(tok))
            continue
        except ValueError:
            pass

        if tok == "mo":
            y, x = stack.pop(), stack.pop()
            d.append(f"M{x:.4f} {y:.4f}")
        elif tok == "li":
            y, x = stack.pop(), stack.pop()
            d.append(f"L{x:.4f} {y:.4f}")
        elif tok == "cv":
            vals = [stack.pop() for _ in range(6)][::-1]
            d.append("C" + " ".join(f"{v:.4f}" for v in vals))
        elif tok == "cp":
            d.append("Z")
        elif tok == "cmyk":
            k, y, m, c = stack.pop(), stack.pop(), stack.pop(), stack.pop()
            colour = cmyk_to_hex(c, m, y, k)
        elif tok == "clp":
            # The page-bounds clip. Discard it rather than emitting it as art.
            d, seen_clip = [], True
        elif tok == "f":
            if d:
                out.append((colour, "".join(d)))
            d = []
        else:
            stack.clear()

    if not seen_clip:
        print("warning: no clip path found — check the EPS structure", file=sys.stderr)
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    raw = open(src, "rb").read().decode("latin-1")
    box = re.search(r"%%HiResBoundingBox:\s*0\s+0\s+([\d.]+)\s+([\d.]+)", raw)
    w, h = float(box.group(1)), float(box.group(2))

    paths = parse(raw)
    if len(paths) < 3:
        sys.exit(f"expected the mark plus a wordmark, got {len(paths)} paths")

    # Illustrator emits the artwork in z-order: the white "V", the magenta arrow,
    # then the wordmark letters. Splitting them lets the particles form the mark
    # alone while the full lockup fades in over it.
    mark = paths[:2]
    wordmark = paths[2:]

    def group(gid, members):
        merged = {}
        for colour, d in members:
            merged.setdefault(colour, []).append(d)
        inner = "\n".join(
            f'    <path fill="{c}" d="{"".join(ds)}"/>' for c, ds in merged.items()
        )
        return f'  <g id="{gid}">\n{inner}\n  </g>'

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">\n'
        + group("mark", mark)
        + "\n"
        + group("wordmark", wordmark)
        + "\n</svg>\n"
    )
    open(dst, "w").write(svg)

    colours = sorted({c for c, _ in paths})
    print(f"{len(paths)} filled paths ({len(mark)} mark, {len(wordmark)} wordmark)")
    print(f"colours: {', '.join(colours)}")
    print(f"viewBox 0 0 {w} {h} -> {dst}")


if __name__ == "__main__":
    main()
