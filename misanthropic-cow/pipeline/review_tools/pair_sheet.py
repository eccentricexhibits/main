"""Each model view beside the matching approved generated view (front/front, left/left, right/right, back/back),
rendered at the image's own scale (floor and horn tip on the same rows, leg axis on the same column), plus a
silhouette overlay.  usage: python pair_sheet.py <pipeline dir> <glb> <genviews dir> <out.jpg> [label]"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, sys.argv[1])
import glb as G, render as R

HORN = 1.696
# view: (image, camera angle, top row, floor row, leg-axis column)
VIEWS = [('front', '1_FRONT_approved.png', 0, 83, 1233, 420),
         ('left side', '3_SIDE_facing_left_approved.png', 90, 54, 1220, 477),
         ('right side', 'Gemini_Generated_Image_f4u2n8f4u2n8f4u2.jpg', -90, 58, 1221, 401),
         ('back', '2_BACK_approved.png', 180, 72, 1458, 505)]
BG = np.array([.085, .098, .115]) * 255
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)


def render_like(r, angle, w, h, top, floor, axis):
    scale = (floor - top) / HORN                        # px per metre
    height = h * .9 / scale
    th = np.deg2rad(angle)
    right = np.array([np.cos(th), 0, -np.sin(th)])
    c = -((axis - w / 2) / scale) * right
    c[1] = (floor - h / 2) / scale
    im = np.asarray(r.render(angle, 0, (w, h), center=tuple(c), height=height, bg=False)).astype(float)
    im2 = np.asarray(r.render(angle, 0, (w, h), center=tuple(c), height=height, bg=True)).astype(float)
    fg = np.abs(im - im2).sum(-1) < .5                  # the backdrop differs between the two renders, the model doesn't
    im[~fg] = 255
    return Image.fromarray(im.astype(np.uint8)), fg


def gem_fg(im):
    a = np.asarray(im).astype(float)
    return ~((a.mean(-1) > 246) & (a.max(-1) - a.min(-1) < 10))


def label(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, 36), fill='#161b22'); d.text((10, 5), t, font=FONT, fill='white')
    return im


def main(pipe, glb, gdir, out, name='Model'):
    r = R.Renderer(G.read(glb))
    rows = []
    for title, fn, angle, top, floor, axis in VIEWS:
        g = Image.open(f'{gdir}/{fn}').convert('RGB')
        m, mfg = render_like(r, angle, g.width, g.height, top, floor, axis)
        gfg = gem_fg(g)
        ov = np.full((g.height, g.width, 3), 250, np.uint8)
        ov[mfg & gfg] = (195, 195, 195); ov[mfg & ~gfg] = (235, 110, 100); ov[gfg & ~mfg] = (100, 140, 235)
        H = 900
        tiles = [label(m, f'{name} · {title}'), label(g.copy(), f'Gemini · {title}'),
                 label(Image.fromarray(ov), 'overlay: red model only, blue Gemini only')]
        tiles = [t.resize((int(t.width * H / t.height), H)) for t in tiles]
        row = Image.new('RGB', (sum(t.width for t in tiles), H), 'white'); x = 0
        for t in tiles:
            row.paste(t, (x, 0)); x += t.width
        rows.append(row)
    sheet = Image.new('RGB', (max(r_.width for r_ in rows), sum(r_.height for r_ in rows)), 'white'); y = 0
    for r_ in rows:
        sheet.paste(r_, (0, y)); y += r_.height
    sheet.save(out, quality=86)
    print(out, sheet.size)


if __name__ == '__main__':
    main(*sys.argv[1:])
