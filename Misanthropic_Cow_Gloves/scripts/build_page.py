"""Render the guide page (index.html) from kit_content + manifest."""
import sys, os, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_content as K

OUT = sys.argv[1]
man = json.load(open(os.path.join(OUT, "manifest.json")))
thumbs = man["thumbs"]
e = html.escape

def attach_tiles(items):
    out = []
    for i, (fn, desc) in enumerate(items, 1):
        if "approved" in fn:
            out.append(f'''<li class="tile yours"><span class="ord">{i}</span><div class="ph"><span>Your image</span></div>
<p class="fn">{e(fn)}</p><p class="desc">From an earlier step</p></li>''')
        else:
            out.append(f'''<li class="tile"><span class="ord">{i}</span><img src="{thumbs[fn]}" alt="{e(desc)}" width="520" height="520">
<p class="fn">{i}_{e(fn)}</p><p class="desc">{e(desc)}</p></li>''')
    return "\n".join(out)

steps_html = []
for n, st in enumerate(K.STEPS, 1):
    pid = f"prompt-{n}"
    checks = "\n".join(f'<li><label><input type="checkbox" id="c{n}-{j}"> <span>{e(c)}</span></label></li>' for j, c in enumerate(st["check"]))
    save = f'<p class="save">Save as <code>{e(st["save"])}</code></p>' if st["save"] else ""
    long_cls = " long" if n == 1 else ""
    attach_block = (f'<h3>Attach, in this order</h3>\n  <ol class="tiles">{attach_tiles(st["attach"])}</ol>' if st["attach"] else "")
    steps_html.append(f'''
<section class="step" id="{st["id"]}" aria-labelledby="h-{st["id"]}">
  <header class="step-head">
    <span class="step-no">Step {n}<small> of {len(K.STEPS)}</small></span>
    <h2 id="h-{st["id"]}">{e(st["title"])}</h2>
    <p class="goal">{e(st["goal"])}</p>
    <p class="where">{e(st["where"])} <span class="pkg">Images: <code>{e(st["zip"])}.zip</code></span></p>
  </header>
  {attach_block}
  <div class="prompt-head"><h3>{"Then paste" if st["attach"] else "Do this"}</h3><button class="copy" type="button" data-target="{pid}">Copy{" prompt" if st["attach"] else ""}</button></div>
  <pre class="prompt{long_cls}" id="{pid}" tabindex="0">{e(K.fill(st["prompt"]))}</pre>
  <div class="after">
    <div class="checks"><h3>Check before approving</h3><ul>{checks}</ul></div>
    <div class="next">{save}<p>{e(st["after"])}</p></div>
  </div>
</section>''')

fix_html = "\n".join(f'''<article class="fix">
  <div class="fix-top"><span class="fix-code">{e(code)}</span><button class="copy small" type="button" data-target="fix-{i}">Copy</button></div>
  <h3>{e(when)}</h3>
  <pre class="fixtext" id="fix-{i}">{e(text)}</pre>
</article>''' for i, (code, when, text) in enumerate(K.FIXES))

fix_imgs = "\n".join(f'''<li class="tile mini"><img src="{thumbs[fn]}" alt="{e(desc)}" width="520" height="520"><p class="fn">{e(fn)}</p><p class="desc">{e(desc)}</p></li>''' for fn, desc in K.FIX_ATTACH)
tips = "\n".join(f"<li>{e(t)}</li>" for t in K.TIPS)
tripo_rows = "\n".join(f"<tr><th scope='row'>{e(s)}</th><td><code>{e(f.split(' ')[0])}</code>{(' <span class=\"muted\">' + e(' '.join(f.split(' ')[1:])) + '</span>') if ' ' in f else ''}</td></tr>" for s, f in K.TRIPO)
tripo_notes = "\n".join(f"<li>{e(t)}</li>" for t in K.TRIPO_NOTES)
nav = "\n".join(f'<li><a href="#{st["id"]}"><span>{n}</span>{e(st["title"])}</a></li>' for n, st in enumerate(K.STEPS, 1))

page = f'''<title>Hoof Glove View Kit</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: a single working column, one section per step, like a prop-shop job sheet: attach strip, prompt slip, check-off list. */
:root {{
  --paper: #fbf9f8;
  --card: #ffffff;
  --ink: #1d1a1c;
  --muted: #6b6468;
  --line: #e6dfe2;
  --chenille: #f1ece3;
  --magenta: #a8206f;
  --magenta-soft: #f7e4ef;
  --on-magenta: #ffffff;
  --code-bg: #f5f1f3;
  --f-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --f-body: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  --f-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper: #161315; --card: #1f1b1e; --ink: #f1ecee; --muted: #a79ea3; --line: #352f33;
    --chenille: #2a2522; --magenta: #e05aa7; --magenta-soft: #3a1f2e; --on-magenta: #1a0d14; --code-bg: #151214;
    color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --paper: #161315; --card: #1f1b1e; --ink: #f1ecee; --muted: #a79ea3; --line: #352f33;
  --chenille: #2a2522; --magenta: #e05aa7; --magenta-soft: #3a1f2e; --on-magenta: #1a0d14; --code-bg: #151214;
  color-scheme: dark;
}}
* {{ box-sizing: border-box; }}
body {{
  background: var(--paper); color: var(--ink); font-family: var(--f-body); font-size: 17px; line-height: 1.55;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 0 64px;
}}
.wrap {{ max-width: 960px; margin: 0 auto; display: grid; gap: 56px; }}
h1, h2, h3 {{ font-family: var(--f-display); text-wrap: balance; margin: 0; }}
h1 {{ font-size: clamp(2.1rem, 5.5vw, 3.4rem); font-weight: 800; line-height: 1.02; letter-spacing: -0.02em; }}
h2 {{ font-size: clamp(1.6rem, 3.6vw, 2.1rem); font-weight: 700; line-height: 1.1; }}
h3 {{ font-size: 0.8rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--muted); }}
p {{ margin: 0; }}
code {{ font-family: var(--f-mono); font-size: 0.86em; background: var(--code-bg); border: 1px solid var(--line); padding: 1px 6px; border-radius: 4px; overflow-wrap: anywhere; }}
a {{ color: var(--magenta); }}
:focus-visible {{ outline: 3px solid var(--magenta); outline-offset: 2px; }}

.top {{ padding-top: 40px; display: grid; gap: 18px; }}
.eyebrow {{ font-family: var(--f-mono); font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--magenta); }}
.lede {{ font-size: 1.15rem; max-width: 62ch; }}
.howto {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; list-style: none; padding: 0; margin: 4px 0 0; counter-reset: h; }}
.howto li {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; font-size: 0.95rem; }}
.howto b {{ display: block; font-family: var(--f-display); font-size: 1.05rem; }}
nav.steps ol {{ list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }}
nav.steps a {{ display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px 6px 6px; border: 1px solid var(--line); border-radius: 999px; text-decoration: none; color: var(--ink); background: var(--card); font-size: 0.95rem; }}
nav.steps a span {{ display: inline-grid; place-items: center; width: 24px; height: 24px; border-radius: 50%; background: var(--magenta); color: var(--on-magenta); font-weight: 700; font-size: 0.8rem; }}
nav.steps a:hover {{ border-color: var(--magenta); }}

.rules {{ background: var(--chenille); border-radius: 14px; padding: 20px 22px; display: grid; gap: 10px; }}
.rules ul {{ margin: 0; padding-left: 1.2em; display: grid; gap: 6px; }}

.key {{ display: grid; gap: 12px; }}
.key figure {{ margin: 0; background: #fff; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
.key img {{ display: block; width: 100%; height: auto; }}
.key figcaption {{ color: var(--muted); font-size: 0.95rem; }}

.step {{ display: grid; gap: 16px; padding-top: 28px; border-top: 2px solid var(--ink); scroll-margin-top: 16px; }}
.step-head {{ display: grid; gap: 6px; }}
.step-no {{ font-family: var(--f-mono); font-size: 0.85rem; font-weight: 600; color: var(--magenta); letter-spacing: 0.06em; text-transform: uppercase; }}
.step-no small {{ color: var(--muted); font-size: 1em; }}
.goal {{ font-size: 1.08rem; max-width: 64ch; }}
.where {{ color: var(--muted); font-size: 0.95rem; display: flex; flex-wrap: wrap; gap: 4px 14px; }}

.tiles {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; }}
.tile {{ position: relative; display: grid; gap: 4px; align-content: start; min-width: 0; }}
.tile img, .tile .ph {{ width: 100%; height: auto; aspect-ratio: 1; max-width: 100%; border-radius: 10px; border: 1px solid var(--line); background: #fff; object-fit: contain; display: block; }}
.tile .ph {{ display: grid; place-items: center; background: var(--magenta-soft); border: 2px dashed var(--magenta); color: var(--magenta); font-family: var(--f-display); font-weight: 700; }}
.ord {{ position: absolute; top: 8px; left: 8px; width: 28px; height: 28px; border-radius: 50%; background: var(--ink); color: var(--paper); display: grid; place-items: center; font-weight: 700; font-size: 0.85rem; z-index: 1; }}
.yours .ord {{ background: var(--magenta); color: var(--on-magenta); }}
.fn {{ font-family: var(--f-mono); font-size: 0.72rem; overflow-wrap: anywhere; }}
.desc {{ font-size: 0.85rem; color: var(--muted); line-height: 1.35; }}

.prompt-head {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 6px; }}
.copy {{ font: 700 0.92rem var(--f-body); background: var(--magenta); color: var(--on-magenta); border: 0; border-radius: 8px; padding: 9px 16px; cursor: pointer; }}
.copy:hover {{ filter: brightness(1.08); }}
.copy.small {{ padding: 5px 12px; font-size: 0.82rem; }}
.copy.done {{ background: var(--ink); color: var(--paper); }}
pre {{ font-family: var(--f-mono); font-size: 0.82rem; line-height: 1.55; white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; }}
.prompt {{ background: var(--code-bg); border: 1px solid var(--line); border-left: 4px solid var(--magenta); border-radius: 8px; padding: 16px 18px; max-height: 26rem; overflow: auto; }}
.prompt.long {{ max-height: 22rem; }}

.after {{ display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr); gap: 20px; }}
@media (max-width: 680px) {{ .after {{ grid-template-columns: 1fr; }} }}
.checks ul {{ list-style: none; padding: 0; margin: 8px 0 0; display: grid; gap: 6px; }}
.checks label {{ display: flex; gap: 10px; align-items: flex-start; cursor: pointer; }}
.checks input {{ accent-color: var(--magenta); width: 18px; height: 18px; margin-top: 3px; flex: none; }}
.checks input:checked + span {{ color: var(--muted); text-decoration: line-through; }}
.next {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; display: grid; gap: 8px; align-content: start; font-size: 0.95rem; }}
.save {{ font-weight: 700; }}

.fixes {{ display: grid; gap: 16px; padding-top: 28px; border-top: 2px solid var(--ink); }}
.fixgrid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }}
.fix {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; display: grid; gap: 8px; align-content: start; min-width: 0; }}
.fix-top {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
.fix-code {{ font-family: var(--f-mono); font-size: 0.78rem; font-weight: 600; color: var(--magenta); text-transform: uppercase; letter-spacing: 0.06em; }}
.fix h3 {{ font-size: 1.05rem; text-transform: none; letter-spacing: 0; color: var(--ink); }}
.fixtext {{ font-size: 0.78rem; color: var(--muted); }}
.tiles.minis {{ grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }}

.tripo {{ display: grid; gap: 14px; padding-top: 28px; border-top: 2px solid var(--ink); }}
.tablewrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; min-width: 0; width: 100%; max-width: 640px; }}
th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-family: var(--f-display); width: 6.5rem; }}
.muted {{ color: var(--muted); font-size: 0.9rem; }}
.tripo ul {{ margin: 0; padding-left: 1.2em; display: grid; gap: 6px; }}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior: auto !important; }} }}
html {{ scroll-behavior: smooth; }}
</style>

<div class="wrap">
  <header class="top">
    <p class="eyebrow">The Misanthropic Cow · Tripo multiview · one left glove</p>
    <h1>Hoof Glove View Kit</h1>
    <p class="lede">Five steps to four matching views of one glove: back of hand, little-finger side, thumb side and palm. Three come from ChatGPT, edited from your real photos; the palm view is a mirror. Each step: attach the images shown, in order. Paste the prompt. Check the result. Save it.</p>
    <ul class="howto">
      <li><b>Where the images are</b>Each step has its own package in the chat. The files are numbered in attach order.</li>
      <li><b>Which tool</b>ChatGPT image generation. Keep one chat for Steps 1 to 4.</li>
      <li><b>Pink tiles</b>Images you made and approved in an earlier step. Attach them from your own downloads.</li>
    </ul>
    <nav class="steps" aria-label="Steps"><ol>{nav}
      <li><a href="#fixes"><span>!</span>Fix-ups</a></li>
      <li><a href="#tripo"><span>↑</span>Tripo upload</a></li></ol></nav>
  </header>

  <aside class="rules" aria-label="Ground rules">
    <h3>Ground rules</h3>
    <ul>{tips}</ul>
  </aside>

  <section class="key" aria-labelledby="h-key">
    <h3 id="h-key">Design key: check every result against this</h3>
    <figure><img src="img/design_key_large.jpg" alt="Annotated photos of the glove with 10 numbered parts: cream terry mitten, separate thumb with no hoof, two finger compartments, two black hoof toe caps, toe shape, straight base edge, raised rim, satin black finish, plain cuff, and the closed cleft." width="1600" height="923"></figure>
    <p class="muted">The four details an image model is most likely to get wrong are bold: no hoof on the thumb, exactly two toe caps, satin (not glossy) paint, and the closed cleft.</p>
  </section>

  {"".join(steps_html)}

  <section class="fixes" id="fixes" aria-labelledby="h-fixes">
    <span class="step-no">When a result is wrong</span>
    <h2 id="h-fixes">Fix-up prompts</h2>
    <p class="goal">Paste the one that matches. In ChatGPT, brush over just the wrong area with the Select tool first. Attach a detail image if the model needs reminding. These are all in <code>FIX_UP_PROMPTS.zip</code>.</p>
    <div class="fixgrid">{fix_html}</div>
    <h3>Detail images for fixes</h3>
    <ul class="tiles minis">{fix_imgs}</ul>
  </section>

  <section class="tripo" id="tripo" aria-labelledby="h-tripo">
    <span class="step-no">Finally</span>
    <h2 id="h-tripo">Upload to Tripo multiview</h2>
    <div class="tablewrap"><table><tbody>{tripo_rows}</tbody></table></div>
    <ul>{tripo_notes}</ul>
  </section>
</div>

<script>
document.querySelectorAll("button.copy").forEach(function (btn) {{
  btn.addEventListener("click", function () {{
    var el = document.getElementById(btn.dataset.target);
    var text = el.textContent;
    var label = btn.textContent;
    function flash(msg) {{ btn.textContent = msg; btn.classList.add("done"); setTimeout(function () {{ btn.textContent = label; btn.classList.remove("done"); }}, 1600); }}
    function selectIt() {{ var r = document.createRange(); r.selectNodeContents(el); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); flash("Selected: press Ctrl/Cmd+C"); }}
    try {{
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(function () {{ flash("Copied"); }}, selectIt);
      }} else {{ selectIt(); }}
    }} catch (err) {{ selectIt(); }}
  }});
}});
</script>
'''
with open(os.path.join(OUT, "web", "index.html"), "w") as f:
    f.write(page)
print("ok", len(page))
