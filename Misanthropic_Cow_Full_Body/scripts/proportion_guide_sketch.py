"""Flat-colour proportion sketch of the cow in an A-pose, built from the measured
proportions of the original-shoot collage. Fallback edit base for ChatGPT when a photo
collage trips its filters.  python3 -I proportion_guide_sketch.py <out.png>"""
import sys, math
from PIL import Image, ImageDraw

SS = 2                                  # supersampling
W, Hc = 1024 * SS, 1536 * SS
FLOOR, TOP = 1460 * SS, 140 * SS
H = FLOOR - TOP                         # floor to horn tips
CX = W // 2
def y(f): return FLOOR - f * H          # height fraction -> pixel row
def u(f): return f * H                  # size fraction -> pixels

C = dict(fur=(240, 240, 236), line=(70, 70, 70), black=(28, 28, 28), pink=(238, 172, 182),
         beige=(218, 200, 176), yellow=(238, 206, 64), red=(186, 32, 42), mask=(246, 246, 242),
         legging=(32, 32, 34), glove=(232, 232, 226), chen=(228, 220, 196))
im = Image.new("RGB", (W, Hc), (255, 255, 255)); d = ImageDraw.Draw(im)
LW = 3 * SS
def ell(cx, cy, rx, ry, fill, outline=C["line"]): d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=outline, width=LW)
def poly(pts, fill, outline=C["line"]): d.polygon(pts, fill=fill, outline=outline, width=LW)
def limb(x0, y0, x1, y1, w0, w1, fill):
    a = math.atan2(y1 - y0, x1 - x0) + math.pi / 2; ca, sa = math.cos(a), math.sin(a)
    poly([(x0 + ca * w0, y0 + sa * w0), (x1 + ca * w1, y1 + sa * w1), (x1 - ca * w1, y1 - sa * w1), (x0 - ca * w0, y0 - sa * w0)], fill)

# legs (black leggings, white spots), slippers
for s in (-1, 1):
    lx = CX + s * u(0.055)
    limb(lx, y(0.47), CX + s * u(0.058), y(0.04), u(0.047), u(0.03), C["legging"])
    for fy, fx, r in ((0.40, 0.012, 0.016), (0.27, -0.01, 0.014), (0.13, 0.008, 0.012)):
        ell(CX + s * u(0.055 + fx * s), y(fy), u(r), u(r * 0.75), C["fur"], None)
    sx = CX + s * u(0.065)
    ell(sx, y(0.028), u(0.062), u(0.032), C["black"])            # chenille fringe
    ell(sx, y(0.04), u(0.052), u(0.034), C["chen"])               # cream chenille head
    ell(sx, y(0.028), u(0.036), u(0.022), C["mask"])              # white plush muzzle
# bloomers
poly([(CX - u(0.112), y(0.535)), (CX + u(0.112), y(0.535)), (CX + u(0.105), y(0.47)), (CX + u(0.02), y(0.455)),
      (CX - u(0.02), y(0.455)), (CX - u(0.105), y(0.47))], C["beige"])
# arms in A-pose (behind the belly edge), gloves with black hooves
for s in (-1, 1):
    sx, sy = CX + s * u(0.125), y(0.825)
    ang = math.radians(32); L = u(0.33)
    ex, ey = sx + s * math.sin(ang) * L, sy + math.cos(ang) * L
    limb(sx, sy, ex, ey, u(0.036), u(0.03), C["fur"])
    gx, gy = sx + s * math.sin(ang) * (L + u(0.04)), sy + math.cos(ang) * (L + u(0.04))
    limb(ex, ey, gx, gy, u(0.028), u(0.026), C["glove"])
    hx, hy = sx + s * math.sin(ang) * (L + u(0.075)), sy + math.cos(ang) * (L + u(0.075))
    limb(gx, gy, hx, hy, u(0.026), u(0.012), C["black"])
    mx, my = sx + s * math.sin(ang) * L * 0.55, sy + math.cos(ang) * L * 0.55
    ell(mx + s * u(0.03), my, u(0.016), u(0.022), C["black"], None)   # elbow tuft
# torso and belly
poly([(CX - u(0.135), y(0.845)), (CX + u(0.135), y(0.845)), (CX + u(0.14), y(0.70)), (CX - u(0.14), y(0.70))], C["fur"])
ell(CX, y(0.625), u(0.14), u(0.105), C["fur"])
ell(CX + u(0.01), y(0.60), u(0.05), u(0.045), C["black"], None)       # belly patch
for s in (-1, 1): ell(CX + s * u(0.138), y(0.66 if s > 0 else 0.76), u(0.012), u(0.022), C["black"], None)
# udder: two big pink lobes with four nubs
for s in (-1, 1):
    ox, oy = CX + s * u(0.062), y(0.79)
    limb(ox + s * u(0.045), oy + u(0.03), ox + s * u(0.085), oy + u(0.045), u(0.008), u(0.007), C["pink"])
    limb(ox + s * u(0.01), oy + u(0.05), ox + s * u(0.012), oy + u(0.085), u(0.008), u(0.007), C["pink"])
    ell(ox, oy, u(0.064), u(0.058), C["pink"])
ell(CX - u(0.055), y(0.85), u(0.03), u(0.022), C["black"], None)      # tuft under the snout
# hood, bolster, horns, mask
ell(CX, y(0.905), u(0.056), u(0.068), C["fur"])
ell(CX, y(0.902), u(0.044), u(0.056), C["mask"])
ell(CX + u(0.02), y(0.925), u(0.022), u(0.028), C["black"], None)     # big mask patch (viewer's right)
ell(CX - u(0.024), y(0.93), u(0.012), u(0.01), C["black"], None)
for s in (-1, 1): ell(CX + s * u(0.016), y(0.912), u(0.007), u(0.007), C["yellow"])
ell(CX, y(0.865), u(0.028), u(0.019), C["red"])                       # snout
for s in (-1, 1): d.line((CX + s * u(0.008), y(0.875), CX + s * u(0.008), y(0.855)), fill=C["black"], width=4 * SS)
d.rounded_rectangle((CX - u(0.052), y(0.982), CX + u(0.052), y(0.956)), radius=u(0.012), fill=C["fur"], outline=C["line"], width=LW)
# horns: viewer's right = long crescent with a pointed tip; viewer's left = short, ending in a wire tuft
pts = [(0.048, 0.969), (0.078, 0.974), (0.096, 0.992), (0.099, 1.015), (0.09, 1.033)]
for (x0, y0), (x1, y1), w0, w1 in zip(pts, pts[1:], (0.015, 0.014, 0.012, 0.008), (0.014, 0.012, 0.008, 0.001)):
    limb(CX + u(x0), y(y0), CX + u(x1), y(y1), u(w0), u(w1), C["yellow"])
for (x0, y0, x1, y1) in ((0.062, 0.957, 0.064, 0.985), (0.083, 0.969, 0.098, 0.98), (0.09, 1.0, 0.107, 1.003)):
    d.line((CX + u(x0), y(y0), CX + u(x1), y(y1)), fill=C["black"], width=3 * SS)
limb(CX - u(0.048), y(0.969), CX - u(0.08), y(0.976), u(0.015), u(0.012), C["yellow"])
for xx in (0.06, 0.071): d.line((CX - u(xx), y(0.956), CX - u(xx + 0.002), y(0.985)), fill=C["black"], width=3 * SS)
for k in range(5):
    d.line((CX - u(0.08), y(0.976), CX - u(0.083 + 0.004 * k), y(1.0 + 0.006 * (k % 3))), fill=(105, 105, 112), width=2 * SS)
im.resize((W // SS, Hc // SS), Image.LANCZOS).save(sys.argv[1], optimize=True)
