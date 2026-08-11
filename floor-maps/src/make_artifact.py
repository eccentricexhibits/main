#!/usr/bin/env python3
"""Build the single-file shareable viewer published as an Artifact."""
import base64
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(DIST, "artifact.html")

SHEETS = [
    ("gallery-event-map", "3", "Gallery — event map",
     "Level 3 redrawn as a guest-facing event map: flat colour-blocked spaces "
     "instead of blueprint linework, numbered pins keyed to a panel, north up, "
     "and the vendor rows from the event team&rsquo;s own gallery plan.",
     "24 &times; 16 in"),
    ("level-1-lobby", "1", "Lobby",
     "Arrival, check-in and coat check. Both the Bay Street doors and the TD "
     "Concourse escalators land here, and the Grand Staircase in the south-west "
     "corner is the route up to the show.", "24 &times; 36 in"),
    ("level-2-trading-floor", "2", "Trading Floor",
     "The immersive theatre. Three walls of projection under a 40 ft ceiling, "
     "with the Domino screen on the far wall. No washrooms on this level — the "
     "one thing worth telling guests before they go looking.", "24 &times; 36 in"),
    ("level-3-gallery", "3", "Gallery",
     "Exhibition hall wrapping the building core in an L, plus the Gallery "
     "Boardroom (Patty Watt Room). Washrooms, stairs and elevators all sit "
     "inside the core, reachable from either leg.", "24 &times; 36 in"),
    ("building-overview", "★", "Getting Around",
     "Every vertical route in the building on one sheet — which stair, "
     "escalator or elevator serves which levels, and what each one is for.",
     "24 &times; 36 in"),
]

FACTS = [
    ("The show is on Level 2", "Trading Floor — the immersive projection theatre"),
    ("Washrooms are on 1 and 3", "None on the Trading Floor"),
    ("Four corner stairwells", "Full height of the building, also the fire exits"),
]


def b64(path, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())


def font_face():
    out = []
    for weight, fname in ((400, "Karbon-Regular.otf"), (600, "Karbon-Semibold.otf")):
        p = os.path.join(REPO, fname)
        if os.path.exists(p):
            out.append("@font-face{font-family:'Karbon';font-weight:%d;font-style:normal;"
                       "font-display:swap;src:url(%s) format('opentype')}"
                       % (weight, b64(p, "font/otf")))
    return "".join(out)


CSS = """
%(fonts)s
:root{
  --ground:#FFFFFF; --surface:#F8F6F7; --surface-2:#F1EEF0;
  --line:#E3DFE1; --ink:#161415; --ink-soft:#5E585C;
  --accent:#EB088A; --accent-2:#313CFF; --on-accent:#FFFFFF;
  --frame:#E3DFE1;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0E0D0F; --surface:#171518; --surface-2:#1F1C21;
    --line:#2C282D; --ink:#F4F1F3; --ink-soft:#A39CA0;
    --accent:#FF3FA5; --accent-2:#7C84FF; --on-accent:#12070C;
    --frame:#2C282D;
  }
}
:root[data-theme="dark"]{
  --ground:#0E0D0F; --surface:#171518; --surface-2:#1F1C21;
  --line:#2C282D; --ink:#F4F1F3; --ink-soft:#A39CA0;
  --accent:#FF3FA5; --accent-2:#7C84FF; --on-accent:#12070C;
  --frame:#2C282D;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:'Karbon',system-ui,-apple-system,'Segoe UI',sans-serif;
  font-size:17px; line-height:1.55; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1140px; margin:0 auto; padding:0 24px}

/* ---- masthead ---- */
.mast{border-bottom:1px solid var(--line); padding:56px 0 40px}
.eyebrow{
  font-size:13px; font-weight:600; letter-spacing:.2em; text-transform:uppercase;
  color:var(--accent); margin:0 0 18px;
}
h1{font-size:clamp(40px,7vw,68px); line-height:1.02; margin:0; font-weight:600;
   letter-spacing:-.02em; text-wrap:balance}
.stand{max-width:60ch; color:var(--ink-soft); font-size:19px; margin:18px 0 0}

/* ---- facts ---- */
.facts{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
       gap:1px; background:var(--line); border:1px solid var(--line);
       border-radius:12px; overflow:hidden; margin:36px 0 0}
.fact{background:var(--surface); padding:20px 22px}
.fact b{display:block; font-weight:600; font-size:18px}
.fact span{color:var(--ink-soft); font-size:16px}

/* ---- index rail ---- */
.rail{position:sticky; top:0; z-index:5; background:var(--ground);
      border-bottom:1px solid var(--line); padding:12px 0}
.rail ul{display:flex; gap:8px; list-style:none; margin:0; padding:0;
         overflow-x:auto; scrollbar-width:none}
.rail ul::-webkit-scrollbar{display:none}
.rail a{display:flex; align-items:center; gap:9px; white-space:nowrap;
        text-decoration:none; color:var(--ink); font-size:16px; font-weight:600;
        border:1px solid var(--line); border-radius:999px; padding:7px 15px 7px 8px}
.rail a:hover{border-color:var(--accent); color:var(--accent)}
.rail a:focus-visible{outline:2px solid var(--accent-2); outline-offset:2px}
.chip{display:grid; place-items:center; width:24px; height:24px; border-radius:7px;
      background:var(--accent); color:var(--on-accent); font-size:14px; font-weight:600}

/* ---- sheets ---- */
.sheet{padding:64px 0; border-bottom:1px solid var(--line)}
.sheet:last-of-type{border-bottom:0}
.sheet-head{display:flex; gap:18px; align-items:flex-start; margin:0 0 8px}
.badge{flex:none; display:grid; place-items:center; width:54px; height:54px;
       border-radius:14px; background:var(--accent); color:var(--on-accent);
       font-size:26px; font-weight:600}
.sheet h2{font-size:32px; font-weight:600; margin:2px 0 0; letter-spacing:-.01em}
.sheet p{max-width:62ch; color:var(--ink-soft); margin:10px 0 0}
.dl{display:flex; flex-wrap:wrap; gap:10px; margin:22px 0 26px}
.dl a{font-size:15px; font-weight:600; text-decoration:none; color:var(--ink);
      border:1px solid var(--line); background:var(--surface);
      border-radius:8px; padding:8px 14px}
.dl a:hover{border-color:var(--accent-2); color:var(--accent-2)}
.dl a:focus-visible{outline:2px solid var(--accent-2); outline-offset:2px}
.dl span{font-size:15px; color:var(--ink-soft); align-self:center}
figure{margin:0; border:1px solid var(--frame); border-radius:12px;
       overflow:hidden; background:#FFFFFF}
figure img{display:block; width:100%%; height:auto}

/* ---- notes ---- */
.notes{padding:52px 0 80px}
.notes h3{font-size:13px; font-weight:600; letter-spacing:.2em; text-transform:uppercase;
          color:var(--ink-soft); margin:0 0 18px}
.notes dl{display:grid; gap:20px; margin:0; max-width:74ch}
.notes dt{font-weight:600}
.notes dd{margin:4px 0 0; color:var(--ink-soft)}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.9em;
     background:var(--surface-2); border-radius:5px; padding:2px 6px}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
"""


def main():
    fonts = font_face()
    parts = ["<title>Design Exchange Floor Maps</title>",
             "<style>%s</style>" % (CSS % {"fonts": fonts})]

    parts.append('<header class="mast"><div class="wrap">')
    parts.append('<p class="eyebrow">Vector Institute at Design Exchange</p>')
    parts.append("<h1>Floor Maps</h1>")
    parts.append('<p class="stand">Five wayfinding sheets for the event at 234 Bay Street, '
                 'drawn from the venue&rsquo;s own blueprints. One colour key across all '
                 'three levels: magenta is the event space, cobalt is elevators, violet is '
                 'stairs, turquoise is washrooms.</p>')
    parts.append('<div class="facts">')
    for title, sub in FACTS:
        parts.append("<div class='fact'><b>%s</b><span>%s</span></div>" % (title, sub))
    parts.append("</div></div></header>")

    parts.append('<nav class="rail" aria-label="Sheets"><div class="wrap"><ul>')
    for key, lvl, name, _, _size in SHEETS:
        parts.append('<li><a href="#%s"><span class="chip">%s</span>%s</a></li>' % (key, lvl, name))
    parts.append("</ul></div></nav>")

    parts.append('<main class="wrap">')
    for key, lvl, name, blurb, size in SHEETS:
        png = os.path.join(DIST, key + ".png")
        pdf = os.path.join(DIST, key + ".pdf")
        svg = os.path.join(DIST, key + ".svg")
        parts.append('<section class="sheet" id="%s">' % key)
        parts.append('<div class="sheet-head"><div class="badge">%s</div>'
                     '<div><h2>%s</h2><p>%s</p></div></div>' % (lvl, name, blurb))
        parts.append('<div class="dl">')
        parts.append('<a href="%s" download="%s.pdf">Download PDF</a>' % (b64(pdf, "application/pdf"), key))
        parts.append('<a href="%s" download="%s.svg">Download SVG</a>' % (b64(svg, "image/svg+xml"), key))
        parts.append('<a href="%s" download="%s.png">Download PNG</a>' % (b64(png, "image/png"), key))
        parts.append("<span>%s</span></div>" % size)
        parts.append('<figure><img src="%s" alt="%s floor map sheet"></figure>'
                     % (b64(png, "image/png"), name))
        parts.append("</section>")
    parts.append("</main>")

    parts.append('<footer class="notes"><div class="wrap"><h3>Before these go to print</h3><dl>')
    parts.append("<dt>Confirm the entrance with the venue.</dt><dd>Design Exchange publishes "
                 "Lobby access from Bay Street and the TD Concourse, and the blueprint shows "
                 "escalators up from the concourse plus a link corridor along the north edge. "
                 "The sheets mark the arrival zone rather than asserting one street door — "
                 "worth pinning down, along with which door your guests are routed through "
                 "on the night.</dd>")
    parts.append("<dt>The venue&rsquo;s drawings are not north-up.</dt><dd>The north arrow on "
                 "every DX sheet points to the <em>right</em> of the page, so the blueprints sit "
                 "90&deg; off north. The event map turns the plan back so north is up, which also "
                 "matches the orientation of the event team&rsquo;s own 3D gallery renders. This "
                 "resolves what looked like a contradiction in the tech deck: once the plan is "
                 "read with north to the page-right, the deck&rsquo;s &ldquo;south wall / east "
                 "wall&rdquo; naming lands exactly on the blueprint&rsquo;s geometry. The three "
                 "24 &times; 36 in level sheets still carry the blueprint&rsquo;s own "
                 "orientation and are labelled accordingly.</dd>")
    parts.append("<dt>Source and regeneration.</dt><dd>Everything lives under <code>floor-maps/</code> "
                 "on the <code>claude/design-exchange-floor-maps-0icdz3</code> branch. Labels, "
                 "room names and pin positions live in <code>src/mapdata.py</code> for the "
                 "level sheets and <code>src/gallery_data.py</code> for the event map — edit "
                 "those and re-run <code>src/build.py</code> to regenerate every format.</dd>")
    parts.append("</dl></div></footer>")

    open(OUT, "w", encoding="utf-8").write("\n".join(parts))
    print("wrote", OUT, round(os.path.getsize(OUT) / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
