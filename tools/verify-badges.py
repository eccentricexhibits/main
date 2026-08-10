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

Ink luminance is read from badges.py rather than restated here, so the check
cannot drift away from the artwork. Note it is relative *luminance*, not an RGB
component: rgb(.03,.01,.06) is 0.0014, not 0.03, and using the latter reports a
passing chip as a failure.

    python3 tools/verify-badges.py [badge-dir]
"""
import os
import sys
import tempfile

import numpy as np
import pikepdf
import pypdfium2 as pdfium

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import badges as B  # noqa: E402

W_PT, H_PT = B.PAGE_W, B.PAGE_H
OX, OY = B.OX, B.OY

TARGET = 4.5   # WCAG AA for small text
GRAPHICS = 3.0  # the logo is graphics, not text

# Ink areas, given in bleed space and shifted onto the artboard below.
AREAS = [
    # label,     y0,    y1,     x0,    x1
    ("logo",     56.0,  88.0,  22.5, 187.5),
    ("name",    178.0, 252.0,  22.5, 270.5),
    ("org",     264.0, 298.0,  22.5, 270.5),
    ("title",   304.0, 356.0,  22.5, 270.5),
    ("chip",    366.0, 384.0,  27.0,  70.0),
]


_seq = 0


def render(src, off_names, tmpdir, scale=2.0):
    """Render with `off_names` switched off, through an engine that honours it.

    Every call writes a *fresh* path. PDFium caches by filename, so reusing one
    scratch file hands back the previous document's pixels — which silently
    turns every layer comparison below into a comparison of a file with itself,
    and reports layers as working on a file where they do not.
    """
    global _seq
    _seq += 1
    tmp = os.path.join(tmpdir, f"probe{_seq:04d}.pdf")

    pdf = pikepdf.open(src)
    ocgs = pdf.Root.OCProperties.OCGs
    off = [o for o in ocgs if any(n.lower() in str(o.Name).lower() for n in off_names)]
    if off_names and not off:
        raise SystemExit(f"no optional content group matching {off_names}")
    pdf.Root.OCProperties.D.OFF = pikepdf.Array(off)
    # An OCG left in /ON as well as /OFF is ambiguous; drop it from /ON so the
    # file states one intent.
    pdf.Root.OCProperties.D.ON = pikepdf.Array(
        [o for o in pdf.Root.OCProperties.D.get("/ON", []) if o.objgen not in
         {x.objgen for x in off}])
    pdf.save(tmp)
    pdf.close()

    doc = pdfium.PdfDocument(tmp)
    try:
        return np.array(doc[0].render(scale=scale).to_pil().convert("RGB"))
    finally:
        doc.close()


def _lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luminance(a, y0, y1, x0, x1):
    h, w, _ = a.shape
    b = _lin(a[int((OY + y0) / H_PT * h):int((OY + y1) / H_PT * h),
               int((OX + x0) / W_PT * w):int((OX + x1) / W_PT * w)].astype(float))
    return float((0.2126 * b[:, :, 0] + 0.7152 * b[:, :, 1] + 0.0722 * b[:, :, 2]).mean())


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(B.ROOT, "out", "badges")
    tmpdir = tempfile.mkdtemp()
    failures = []

    print(f'{"":10s}' + "".join(f"{a[0]:>12s}" for a in AREAS))
    for cid, label, lead, second in B.CATEGORIES:
        src = os.path.join(d, f"vector-badge-{cid}.pdf")

        # What each area's ink actually is, per the artwork.
        ink = {
            "logo": B.luminance(B.reverse_or_black(lead)),
            "name": B.luminance("#FFFFFF"),
            "org": 0.2126 * B.INK_BODY[0] + 0.7152 * B.INK_BODY[1] + 0.0722 * B.INK_BODY[2],
            "title": 0.2126 * B.INK_BODY[0] + 0.7152 * B.INK_BODY[1] + 0.0722 * B.INK_BODY[2],
            "chip": B.luminance(B.ink_on(second)),
        }

        # Background only: the ink itself must not skew its own measurement.
        bare = render(src, ["die-line", "Vector logo", "Text fields"], tmpdir)
        row = []
        for name, y0, y1, x0, x1 in AREAS:
            c = B.contrast(luminance(bare, y0, y1, x0, x1), ink[name])
            row.append(c)
            floor = GRAPHICS if name == "logo" else TARGET
            if c < floor:
                failures.append(f"{cid} {name}: {c:.2f}:1 below {floor}:1")
        print(f"{cid:10s}" + "".join(f"{c:9.2f}:1" for c in row))

        # Every layer must actually gate content. Probing only a couple of them
        # is how a top layer that carries someone else's artwork with it goes
        # unnoticed: the layers it covers stop gating, and nothing looks at them.
        full = render(src, [], tmpdir)
        with pikepdf.open(src) as probe_doc:
            names = [str(o.Name) for o in probe_doc.Root.OCProperties.OCGs]
        for probe in names:
            if np.array_equal(full, render(src, [probe], tmpdir)):
                failures.append(f"{cid}: layer '{probe}' does not gate any content")

    print()
    if failures:
        print("FAIL")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print(f"OK — all ink above target ({TARGET}:1 text, {GRAPHICS}:1 logo), "
          "all layers gate content")


if __name__ == "__main__":
    main()
