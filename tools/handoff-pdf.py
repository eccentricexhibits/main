#!/usr/bin/env python3
"""Render HANDOFF.md to a print-ready PDF in the Vector palette.

Kept as a script rather than a one-off so the PDF cannot drift from the
Markdown: whoever edits HANDOFF.md reruns this and the two stay in step.

    python3 tools/handoff-pdf.py [out.pdf]

Writes to dist/ rather than out/, because dist/ is committed: a handoff document
that can only be read by first installing a toolchain is not much of a handoff.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_chrome():
    """Locate a Chromium to print with.

    The bundled browser's directory carries its build number, so anything
    hard-coded breaks the next time the image is rebuilt — this script was
    written against 1194 and found 1243 on the first clean run. Glob for it
    instead, then fall back to whatever is on PATH.
    """
    patterns = (
        "/opt/pw-browsers/chromium-*/chrome-linux*/chrome",
        "/opt/pw-browsers/chromium_headless_shell-*/*/chrome-headless-shell",
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome"),
    )
    for pattern in patterns:
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("no Chromium found — install one, or set CHROME=/path/to/chrome")


CHROME = os.environ.get("CHROME") or find_chrome()

CSS = """
@page { size: A4; margin: 17mm 16mm 16mm; }
:root {
  --ink: #15121a; --dim: #55505f; --rule: #ddd9e2;
  --violet: #8A25C9; --turquoise: #48C0D9; --magenta: #EB088A;
}
* { box-sizing: border-box; }
body {
  margin: 0; color: var(--ink); background: #fff;
  font: 10pt/1.55 "Karbon", "Open Sans", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}
h1 {
  font-size: 23pt; line-height: 1.15; margin: 0 0 6pt; letter-spacing: -0.01em;
  background: linear-gradient(95deg, var(--violet), #6f6ae0 55%, var(--turquoise));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
h2 {
  font-size: 13pt; margin: 20pt 0 7pt; padding-top: 7pt;
  border-top: 1.4pt solid var(--violet); letter-spacing: -0.005em;
  break-after: avoid;
}
h3 { font-size: 10.5pt; margin: 13pt 0 5pt; color: var(--violet); break-after: avoid; }
p, li { margin: 0 0 6pt; }
ul, ol { margin: 0 0 8pt; padding-left: 15pt; }
li { margin-bottom: 3pt; }
strong { font-weight: 600; }
hr { border: 0; border-top: 0.6pt solid var(--rule); margin: 16pt 0; }
code {
  font: 8.6pt/1.4 ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  background: #f3f1f6; padding: 1pt 3pt; border-radius: 2pt;
}
pre {
  background: #14111b; color: #e8e4ee; padding: 9pt 11pt; border-radius: 4pt;
  break-inside: avoid; margin: 0 0 9pt;
  /* Print has no horizontal scroll: an over-long line is silently cut off at
     the block's edge rather than clipped visibly, so wrap instead. */
  white-space: pre-wrap; overflow-wrap: anywhere;
}
pre code { background: none; color: inherit; padding: 0; font-size: 8.1pt; line-height: 1.5; }
table {
  border-collapse: collapse; width: 100%; margin: 0 0 10pt;
  font-size: 9pt; break-inside: avoid;
}
th {
  text-align: left; font-weight: 600; font-size: 7.8pt; text-transform: uppercase;
  letter-spacing: 0.07em; color: var(--dim);
  border-bottom: 1pt solid var(--ink); padding: 0 8pt 3pt 0;
}
td { padding: 4pt 8pt 4pt 0; border-bottom: 0.5pt solid var(--rule); vertical-align: top; }
blockquote {
  margin: 0 0 9pt; padding: 7pt 11pt; background: #f7f5fa;
  border-left: 2.5pt solid var(--turquoise); color: var(--dim);
}
blockquote p:last-child { margin-bottom: 0; }
em { color: var(--dim); }
h1 + p { font-size: 10.5pt; color: var(--dim); }
"""


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
    return (f"Generated from commit `{sha}`"
            + (f", {when}" if when else "")
            + (" — **working tree had uncommitted changes**" if dirty else "") + ".")


def main():
    out = (sys.argv[1] if len(sys.argv) > 1
           else os.path.join(ROOT, "dist", "AI-Summit-2026-handoff.pdf"))
    os.makedirs(os.path.dirname(out), exist_ok=True)

    src = open(os.path.join(ROOT, "HANDOFF.md"), encoding="utf-8").read()
    # Stamp the commit at build time. A hand-written one goes stale the moment
    # anything is committed, and a stale one in a handoff document is worse
    # than none.
    src = src.replace("<!--STAMP-->", stamp())
    body = markdown.markdown(src, extensions=["tables", "fenced_code", "sane_lists"])

    font = os.path.join(ROOT, "Karbon-Semibold.otf")
    face = ""
    if os.path.exists(font):
        import base64
        reg = os.path.join(ROOT, "Karbon-Regular.otf")
        for path, weight in ((reg if os.path.exists(reg) else font, 400), (font, 600)):
            b64 = base64.b64encode(open(path, "rb").read()).decode()
            face += (f'@font-face{{font-family:"Karbon";font-weight:{weight};'
                     f'src:url(data:font/otf;base64,{b64}) format("opentype");}}\n')

    html = (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<title>AI Summit 2026 handoff</title>'
            f"<style>{face}{CSS}</style></head><body>{body}</body></html>")

    tmp = os.path.join(tempfile.mkdtemp(), "handoff.html")
    open(tmp, "w", encoding="utf-8").write(html)

    subprocess.run(
        [CHROME, "--headless", "--no-sandbox", "--disable-gpu",
         "--no-pdf-header-footer", f"--print-to-pdf={out}", f"file://{tmp}"],
        check=True, capture_output=True)
    print("wrote", out, f"({os.path.getsize(out) / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
