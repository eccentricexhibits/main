"""Static review renders + before/after comparison sheet + dance storyboard for v10."""
import sys, pickle
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
import render as R
import render_dance as RD
import glb as G
import anim as AN

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def caption(im, text, size=26):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size)
    d.rectangle((0, im.height - size - 24, im.width, im.height), fill='#161b22')
    d.text((16, im.height - size - 14), text, font=f, fill='#efeee9')
    return im


def main(rigged, out, v09=None, photos=()):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    d = pickle.load(open(rigged, 'rb'))
    m = d['model']
    r = R.Renderer(m)
    for name, a, e in [('front', 0, 0), ('quarter', 30, 5), ('side', 90, 0), ('back', 180, 0)]:
        R.label(r.render(a, e, (1200, 1500), center=(0, .86, .02), height=1.82), 'v10 · 2012 shoot proportions').save(out / f'v10_{name}.jpg', quality=92)
    R.label(r.render(0, 0, (1200, 1500), center=(0, .86, .02), height=1.82, clay=True), 'v10 · clay').save(out / 'v10_clay.jpg', quality=92)
    R.label(r.render(22, 4, (1400, 1300), center=(0, 1.49, .05), height=.48), 'Head · scanned mask in fur hood').save(out / 'v10_head.jpg', quality=93)
    R.label(r.render(12, 5, (1300, 1400), center=(0, 1.08, .06), height=.80), 'Torso · udder cups, belly, shag').save(out / 'v10_torso.jpg', quality=93)
    R.label(r.render(-25, 6, (1200, 1300), center=(-.30, .87, .08), height=.42), 'Hand · glove tucked into the sleeve end').save(out / 'v10_hand.jpg', quality=93)
    # before / after sheet
    tiles = []
    for p in photos:
        im = ImageOps.exif_transpose(Image.open(p)).convert('RGB'); im.thumbnail((600, 760))
        c = Image.new('RGB', (600, 760), '#161b22'); c.paste(im, ((600 - im.width) // 2, 0))
        tiles.append(caption(c, '2012 shoot · ' + Path(p).stem.split('__')[-1]))
    if v09:
        old = G.read(v09)
        tiles.append(caption(R.Renderer(old).render(0, 0, (600, 760), center=(0, 1.0, 0), height=2.05), 'v09 (before)'))
    tiles.append(caption(r.render(0, 0, (600, 760), center=(0, .86, .02), height=1.82), 'v10 (after)'))
    tiles.append(caption(r.render(30, 5, (600, 760), center=(0, .86, .02), height=1.82), 'v10 quarter'))
    sheet = Image.new('RGB', (600 * len(tiles), 760), '#161b22')
    for i, t in enumerate(tiles):
        sheet.paste(t, (600 * i, 0))
    sheet.save(out / 'v10_vs_shoot_and_v09.jpg', quality=90)
    # dance storyboard: 4 phases x 2 views
    times = [1.30, 4.00, 7.10, 9.375]
    RD.storyboard(d, times, out / 'Chicken_Dance_Pose_Review_v10.jpg', views=((-12, 4), (55, 4)), size=(600, 800), center=(0, .90, .04), height=1.88)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, sys.argv[4:])
