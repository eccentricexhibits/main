import re, math, sys, pathlib
R = pathlib.Path('/home/user/main')
OUT = pathlib.Path(__file__).parent
W, H = 1200, 627

# --- official plus pattern (Vector Official Plus Symbol.svg), rotated 90deg ---
plus_svg = (R/'Vector Official Plus Symbol.svg').read_text()
polys = re.findall(r'points="([^"]+)"', plus_svg)
PW, PH = 1080, 768.58
centers = []
for p in polys:
    n = list(map(float, p.split()))
    xs, ys = n[0::2], n[1::2]
    centers.append(((min(xs)+max(xs))/2, (min(ys)+max(ys))/2))
ROT = sys.argv[1] if len(sys.argv) > 1 else 'ccw'
def rot(x, y):
    if ROT == 'cw':  return (PH - y, x)          # 90 clockwise
    if ROT == 'ccw': return (y, PW - x)          # 90 counter-clockwise
    return (x, y)
PS = 0.43                     # pattern scale
PX, PY = 600, 54              # pattern origin
ARM = 72.85 * PS              # plus width in px
BAR = 14.99 * PS              # stroke thickness in px
pts = [(PX + rot(x, y)[0]*PS, PY + rot(x, y)[1]*PS) for x, y in centers]

def plus(cx, cy):
    a, b = ARM/2, BAR/2
    return (f'<path d="M{cx-a:.2f} {cy-b:.2f}H{cx-b:.2f}V{cy-a:.2f}H{cx+b:.2f}V{cy-b:.2f}H{cx+a:.2f}'
            f'V{cy+b:.2f}H{cx+b:.2f}V{cy+a:.2f}H{cx-b:.2f}V{cy+b:.2f}H{cx-a:.2f}Z"/>')

# --- light trails: each plus -> convergence point at the card ---
CX, CY = 1030, 350
trails = []
for i, (x, y) in enumerate(pts):
    sx = x + ARM/2 + 5
    dx = CX - sx
    c1 = (sx + dx*0.45, y)
    c2 = (CX - dx*0.40, CY + (y - CY)*0.10)
    trails.append(f'M{sx:.1f} {y:.1f}C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {CX} {CY}')
    # a fainter sibling strand for richness
    off = 10 if i % 2 else -10
    trails.append(f'M{sx:.1f} {y+off*0.3:.1f}C{c1[0]+20:.1f} {c1[1]+off:.1f} {c2[0]:.1f} {c2[1]+off*0.6:.1f} {CX} {CY}')

main = ''.join(f'<path d="{d}"/>' for d in trails[0::2])
sib = ''.join(f'<path d="{d}"/>' for d in trails[1::2])

# --- official logo, horizontal bilingual knockout (white) built from the official vertical SVG ---
logo = (R/'Official Vector Logo.svg').read_text()
polys_logo = re.findall(r'<polygon class="st[01]" points="[^"]+"/>', logo)
v_mark, arrow_mark = polys_logo[0], polys_logo[1]
reg = re.search(r'<path class="st1" d="M1658[^"]+"/>', logo).group(0)
text_g = re.search(r'<g>(.*?)</g>', logo, re.S).group(1)
S_M = 0.42
mark = f'<g transform="scale({S_M}) translate(-721.58 -48.16)">{v_mark}{arrow_mark}{reg}</g>'
text = f'<g transform="translate(870.25 -2153.19)">{text_g}</g>'
LOGO_W, LOGO_H = 3816, 775
logo_inner = re.sub(r'class="st[01]"', 'fill="#fff"', mark + text)

# --- official arrow ---
arrow = re.search(r'points="([^"]+)"', (R/'Vector Official - Arrow Regular.svg').read_text()).group(1)

html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Graduate Student Program</title>
<style>
@font-face{{font-family:Karbon;src:url(../Karbon-Regular.otf);font-weight:400}}
@font-face{{font-family:Karbon;src:url(../Karbon-Semibold.otf);font-weight:600}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#8A25C9}}
#c{{position:relative;width:{W}px;height:{H}px;font-family:Karbon,sans-serif;color:#fff;overflow:hidden}}
.bg,svg.fx{{position:absolute;inset:0}}
.pill{{position:absolute;left:64px;top:54px;height:48px;padding:0 24px;border:2px solid #fff;border-radius:24px;
  display:flex;align-items:center;font-size:20px;letter-spacing:.05em;font-weight:400}}
h1{{position:absolute;left:61px;top:126px;font-weight:600;font-size:80px;line-height:.98;letter-spacing:-.012em}}
.by{{position:absolute;left:64px;top:304px;font-size:28px;line-height:1.28;font-weight:400;width:640px}}
.tr{{position:absolute;left:65px;top:433px;font-size:20px;letter-spacing:.18em;font-weight:400}}
.tr i{{font-style:normal;margin:0 .7em 0 .4em}}
.logo{{position:absolute;left:64px;top:510px;height:60px}}
.stage{{position:absolute;left:992px;top:150px;width:176px;height:300px;perspective:900px}}
.card{{width:100%;height:100%;border-radius:24px;background:rgba(255,255,255,.2);
  border:1.5px solid rgba(255,255,255,.55);transform:rotateY(-16deg);transform-origin:0 50%;
  box-shadow:0 0 22px rgba(255,255,255,.14), inset 0 0 30px rgba(255,255,255,.12);backdrop-filter:blur(6px)}}
.card .ln{{position:absolute;left:24px;height:5px;border-radius:3px;background:rgba(255,255,255,.55)}}
.card svg{{position:absolute;left:44px;top:82px;width:106px;filter:drop-shadow(0 0 10px rgba(255,255,255,.7))}}
</style></head><body><div id="c">
<img class="bg" src="bg@2x.png" width="{W}" height="{H}" alt="">
<svg class="fx" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
 <defs>
  <linearGradient id="t" gradientUnits="userSpaceOnUse" x1="640" y1="0" x2="{CX}" y2="0">
   <stop offset="0" stop-color="#fff" stop-opacity=".15"/><stop offset=".55" stop-color="#fff" stop-opacity=".55"/>
   <stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.2"/></filter>
  <filter id="glow2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>
  <filter id="pg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/>
   <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="flare"><stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset=".25" stop-color="#fff" stop-opacity=".45"/>
   <stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
 </defs>
 <g fill="none" stroke="url(#t)" stroke-linecap="round">
  <g stroke-width="7" opacity=".35" filter="url(#glow2)">{main}</g>
  <g stroke-width="3" opacity=".6" filter="url(#glow)">{main}</g>
  <g stroke-width="1.2" opacity=".95">{main}</g>
  <g stroke-width=".7" opacity=".5">{sib}</g>
 </g>
 <g fill="#fff" filter="url(#pg)">{''.join(plus(x, y) for x, y in pts)}</g>
</svg>
<div class="stage"><div class="card">
 <div class="ln" style="top:34px;width:112px"></div><div class="ln" style="top:50px;width:72px;opacity:.7"></div>
 <svg viewBox="0 0 422.98 600"><polygon fill="#fff" points="{arrow}"/></svg>
</div></div>
<svg class="fx" viewBox="0 0 {W} {H}" width="{W}" height="{H}" style="pointer-events:none">
 <ellipse cx="{CX}" cy="{CY}" rx="70" ry="38" fill="url(#flare)" opacity=".85"/>
 <ellipse cx="{CX}" cy="{CY}" rx="16" ry="9" fill="url(#flare)"/>
</svg>
<div class="pill">NOW ACCEPTING APPLICATIONS</div>
<h1>Graduate Student<br>Program</h1>
<p class="by">Connect with AI research supervisors<br>at Canadian universities<br>through one application.</p>
<p class="tr">13 UNIVERSITIES<i>•</i>ONE APPLICATION</p>
<svg class="logo" viewBox="0 0 {LOGO_W} {LOGO_H}" height="60" width="{60*LOGO_W/LOGO_H:.1f}">{logo_inner}</svg>
</div></body></html>'''
(OUT/'graphic.html').write_text(html)
print('pattern bbox', min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts))
