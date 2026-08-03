#!/usr/bin/env python3
"""
Verify the generated badges, and prove the checks themselves are honest.

Two things here are easy to get wrong and were both got wrong once:

  * PyMuPDF's rasteriser ignores optional-content state. It renders every
    layer no matter what is switched off, so it will happily report that
    layers "work" on a file that has none. Everything below therefore renders
    through PDFium, which does honour it, and the layer test asserts that
    switching a layer off actually changes the pixels.

  * Contrast needs sRGB -> linear conversion first. Skipping it understates
    contrast on saturated darks by roughly two times — plain Cobalt reads
    0.28 naively against a true 0.11 — which is enough to send you
    redesigning a page that was already fine.

    python3 tools/verify-badges.py [badge-dir]
"""
import os
import sys
import tempfile

import numpy as np
import pikepdf
import pypdfium2 as pdfium

W_PT, H_PT = 292.5, 414.0   # bleed page, per the supplied print template
CATEGORIES = ["student", "employer", "partner", "staff"]

# Ink areas: label, y range, ink RELATIVE luminance, x range.
# Note the ink value is relative luminance, not an RGB component — rgb(.03,.01,.06)
# is 0.0014, not 0.03. Getting that wrong reports a passing chip as a failure.
AREAS = [
    # label,     y0,    y1,     ink luminance, x0,    x1
    ("logo",     56.0,  88.0,  0.0,  22.5, 187.5),
    ("name",    178.0, 252.0,  1.0,  22.5, 270.5),
    ("org",     264.0, 298.0,  1.0,  22.5, 270.5),
    ("title",   304.0, 356.0,  1.0,  22.5, 270.5),
    ("chip",    366.0, 384.0,  0.0014, 27.0,  70.0),   # ink is rgb(.03,.01,.06)
]
TARGET = 4.5  # WCAG AA for small text; the logo is graphics and only needs 3:1


def render(src, off_names, tmp, scale=2.2):
    pdf = pikepdf.open(src)
    ocgs = pdf.Root.OCProperties.OCGs
    pdf.Root.OCProperties.D.OFF = pikepdf.Array(
        [o for o in ocgs if any(n in str(o.Name) for n in off_names)]
    )
    pdf.save(tmp)
    return np.array(pdfium.PdfDocument(tmp)[0].render(scale=scale).to_pil().convert("RGB"))


def _lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(a, y0, y1, x0=40.0, x1=234.0):
    h, w, _ = a.shape
    b = _lin(a[int(y0 / H_PT * h):int(y1 / H_PT * h),
               int(x0 / W_PT * w):int(x1 / W_PT * w)].astype(float))
    return float((0.2126 * b[:, :, 0] + 0.7152 * b[:, :, 1] + 0.0722 * b[:, :, 2]).mean())


def contrast(bg, ink):
    hi, lo = max(bg, ink), min(bg, ink)
    return (hi + 0.05) / (lo + 0.05)


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "badges")
    tmpdir = tempfile.mkdtemp()
    failures = []

    print(f'{"":10s}' + "".join(f"{a[0]:>12s}" for a in AREAS))
    for cid in CATEGORIES:
        src = os.path.join(d, f"vector-badge-{cid}.pdf")
        tmp = os.path.join(tmpdir, "t.pdf")

        # Background only: the ink itself must not skew its own measurement.
        bare = render(src, ["template", "Vector logo", "Text fields"], tmp)
        row = []
        for label, y0, y1, ink, x0, x1 in AREAS:
            c = contrast(luminance(bare, y0, y1, x0, x1), ink)
            row.append(c)
            floor = 3.0 if label == "logo" else TARGET
            if c < floor:
                failures.append(f"{cid} {label}: {c:.2f}:1 below {floor}:1")
        print(f"{cid:10s}" + "".join(f"{c:9.2f}:1" for c in row))

        # Layers must actually gate content.
        full = render(src, [], tmp)
        for probe in ("template", "Category wedge", "Ground"):
            if np.array_equal(full, render(src, [probe], tmp)):
                failures.append(f"{cid}: layer '{probe}' does not gate any content")

    print()
    if failures:
        print("FAIL")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print(f"OK — all ink above target ({TARGET}:1 text, 3:1 logo), all layers gate content")


if __name__ == "__main__":
    main()
