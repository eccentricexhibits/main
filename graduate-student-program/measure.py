"""Report text line boxes and the minimum gap between text and the plus pattern."""
import pathlib
from playwright.sync_api import sync_playwright
d = pathlib.Path(__file__).parent
JS = '''() => {
  const out = {text: [], plus: []};
  for (const sel of ['.pill', 'h1', '.by', '.tr', '.logo']) {
    const el = document.querySelector(sel);
    let rects = [];
    if (sel === '.pill' || sel === '.logo') rects = [el.getBoundingClientRect()];
    else { const r = document.createRange(); r.selectNodeContents(el); rects = [...r.getClientRects()]; }
    for (const b of rects) out.text.push([sel, b.left, b.top, b.right, b.bottom]);
  }
  for (const p of document.querySelectorAll('svg.fx g[fill="#fff"] path')) {
    const b = p.getBoundingClientRect(); out.plus.push([b.left, b.top, b.right, b.bottom]);
  }
  const c = document.querySelector('.card').getBoundingClientRect(); out.card = [c.left, c.top, c.right, c.bottom];
  return out;
}'''
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': 1200, 'height': 627})
    pg.goto((d/'graphic.html').as_uri()); pg.wait_for_timeout(300)
    r = pg.evaluate(JS); b.close()
def gap(a, b):
    dx = max(b[0]-a[2], a[0]-b[2], 0); dy = max(b[1]-a[3], a[1]-b[3], 0)
    return (dx*dx + dy*dy) ** .5
worst = min((gap(t[1:], q), t[0]) for t in r['text'] for q in r['plus'])
for t in r['text']: print('%-6s x %4.0f-%4.0f  y %4.0f-%4.0f' % (t[0], t[1], t[3], t[2], t[4]))
print('pattern x %.0f-%.0f  card x %.0f-%.0f' % (min(q[0] for q in r['plus']), max(q[2] for q in r['plus']), r['card'][0], r['card'][2]))
print('min text-to-plus gap: %.0fpx (%s)' % worst)
