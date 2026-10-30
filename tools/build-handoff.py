#!/usr/bin/env python3
"""
Bundle the browser handoff into one self-contained HTML file.

Everything goes inline — the player, the Karbon faces, the badge proofs and the
prose — so the result opens straight off disk, or out of an email attachment,
with no server and no repository.

The prose is read from HANDOFF.md rather than restated, for the same reason the
PDF is: two copies of the same document drift, and the one nobody rebuilds is
the one people read.

    python3 tools/build-handoff.py [out.html]
"""
import base64
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

import markdown
import pikepdf
import pypdfium2 as pdfium

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES = [
    ("student", "Student", "Violet → Turquoise"),
    ("employer", "Employer", "Violet → Tangerine"),
    ("partner", "Partner", "Cobalt → Lime"),
    ("staff", "Vector Institute Staff", "Magenta → Cobalt"),
]


# ---------------------------------------------------------------------------
# Pieces to inline
# ---------------------------------------------------------------------------


def bundle_js():
    """esbuild the player into one IIFE."""
    esbuild = os.path.join(ROOT, "node_modules", ".bin", "esbuild")
    if not os.path.exists(esbuild):
        esbuild = shutil.which("esbuild")
    if not esbuild:
        raise SystemExit("esbuild not found — run `npm install` first")
    return subprocess.run(
        [esbuild, os.path.join(ROOT, "src", "handoff-main.js"),
         "--bundle", "--format=iife", "--target=es2020", "--legal-comments=none"],
        check=True, capture_output=True, text=True).stdout


def font_faces():
    """Karbon, inlined.

    Without the real faces the canvas silently falls back to Open Sans, so the
    speaker names on the wall would be shown in letterforms that are not the
    ones projected — and the page would be quietly lying about the design.
    """
    out = ""
    for name, weight in (("Karbon-Regular.otf", 400), ("Karbon-Semibold.otf", 600)):
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            print(f"  ! {name} not found — type will fall back")
            continue
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        out += (f'@font-face{{font-family:"Karbon";font-weight:{weight};font-display:swap;'
                f'src:url(data:font/otf;base64,{b64}) format("opentype");}}\n')
    return out


def badge_figures(height=760):
    """Render each badge with the die-line hidden, as an inline JPEG.

    JPEG rather than PNG: these are mostly smooth gradient, where PNG is several
    times larger for no visible gain, and the page has to stay small enough to
    email.
    """
    from PIL import Image

    tmpdir = tempfile.mkdtemp()
    figures = []
    for i, (cid, label, pairing) in enumerate(CATEGORIES):
        src = os.path.join(ROOT, "out", "badges", f"vector-badge-{cid}.pdf")
        if not os.path.exists(src):
            raise SystemExit(f"{src} not found — run `python3 tools/badges.py` first")

        pdf = pikepdf.open(src)
        pdf.Root.OCProperties.D.OFF = pikepdf.Array(
            [o for o in pdf.Root.OCProperties.OCGs if "die-line" in str(o.Name).lower()])
        pdf.Root.OCProperties.D.ON = pikepdf.Array([])
        # A fresh path per badge: PDFium caches by filename, and reusing one
        # scratch file hands back the previous badge's pixels.
        probe = os.path.join(tmpdir, f"{i}-{cid}.pdf")
        pdf.save(probe)
        pdf.close()

        doc = pdfium.PdfDocument(probe)
        page = doc[0]
        im = page.render(scale=height / page.get_height()).to_pil().convert("RGB")
        doc.close()

        # Crop the artboard's 1 in margin: it is imposition, not design.
        w, h = im.size
        im = im.crop((round(w * 63 / 418.5), round(h * 63 / 540),
                      round(w * 355.5 / 418.5), round(h * 477 / 540)))

        buf = os.path.join(tmpdir, f"{cid}.jpg")
        im.save(buf, "JPEG", quality=90, optimize=True, progressive=True)
        b64 = base64.b64encode(open(buf, "rb").read()).decode()
        figures.append(
            f'<figure><img alt="{label} badge" src="data:image/jpeg;base64,{b64}">'
            f'<figcaption><b>{label}</b><br>{pairing}</figcaption></figure>')
    return "\n".join(figures)


def stamp():
    def git(*args):
        try:
            return subprocess.run(("git", "-C", ROOT) + args, capture_output=True,
                                  text=True, check=True).stdout.strip()
        except Exception:
            return None

    sha = git("rev-parse", "--short", "HEAD")
    when = git("log", "-1", "--date=format:%d %B %Y", "--format=%ad")
    if not sha:
        return ""
    dirty = git("status", "--porcelain")
    return (f"Generated from commit `{sha}`" + (f", {when}" if when else "")
            + (" — **working tree had uncommitted changes**" if dirty else "") + ".")


def split_callout(html):
    """Lift the "read this before anything else" paragraph out of the prose.

    It is the one thing on the page that must not be scrolled past, and in the
    document's own running order it sits below a table.
    """
    m = re.search(r"<p><strong>Read this before anything else\.</strong>.*?</p>\s*"
                  r"<p>Rendering is a single command.*?</p>", html, re.S)
    if not m:
        return html, ""
    block = m.group(0)
    return html.replace(block, ""), (
        '<div class="callout"><h2>Read this before anything else</h2>'
        + block.replace("<strong>Read this before anything else.</strong> ", "")
        + "</div>")


# ---------------------------------------------------------------------------


def main():
    out = (sys.argv[1] if len(sys.argv) > 1
           else os.path.join(ROOT, "dist", "handoff.html"))
    os.makedirs(os.path.dirname(out), exist_ok=True)

    src = open(os.path.join(ROOT, "HANDOFF.md"), encoding="utf-8").read()
    src = src.replace("<!--STAMP-->", stamp())
    doc = markdown.markdown(src, extensions=["tables", "fenced_code", "sane_lists"])
    doc, callout = split_callout(doc)

    html = open(os.path.join(ROOT, "src", "handoff.html"), encoding="utf-8").read()
    html = html.replace("</style>", font_faces() + "</style>")
    html = html.replace('<script type="module" src="./handoff-main.js"></script>',
                        f"<script>\n{bundle_js()}\n</script>")
    html = html.replace("<!--BADGES-->", badge_figures())
    html = html.replace("<!--CALLOUT-->", callout)
    html = html.replace("<!--DOC-->", doc)

    open(out, "w", encoding="utf-8").write(html)
    print(f"wrote {out}  ({len(html.encode()) / 1024:.0f} kB, self-contained)")


if __name__ == "__main__":
    main()
