"""Shag close-ups: the black patches from the front, side and back, and posed in Look Around.
Rendered at 2x and downsampled, so single strands come out smooth rather than as stair-steps.

usage: python render_shag.py rigged.pkl out_dir [before_rigged.pkl | before_Animated.glb]
With a second (before) model, each view is a before | after pair."""
import sys, pickle
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import render as R
import glb as G

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SS = 2

VIEWS = [  # name, angle, elevation, centre, height, clip/time or None
    ('belly', 8, 4, (0, .90, .16), .36, None),
    ('chest', -20, 6, (-.10, 1.27, .06), .30, None),
    ('side', 72, 2, (0, 1.02, .02), .70, None),
    ('back', 175, 4, (0, 1.08, -.12), .62, None),
    ('elbow', -110, 4, (-.20, 1.05, -.05), .36, None),
    ('look_around', 35, 4, (0, .98, .05), .95, ('Look Around', 4.25)),
]


def view(d, name, a, e, c, h, pose, size):
    m = d['model']
    r = R.Renderer(m)
    parts = None
    if pose:
        clip = d['clips'][pose[0]]
        i = int(np.argmin(np.abs(np.asarray(clip['times']) - pose[1] % clip['duration'])))
        parts = R.skin_parts(m, clip['mats'][i])
    im = r.render(a, e, (size[0] * SS, size[1] * SS), center=c, height=h, parts=parts)
    return im.resize(size, Image.LANCZOS)


def tag(im, text):
    dr = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 24)
    dr.rectangle((0, im.height - 44, im.width, im.height), fill='#161b22')
    dr.text((14, im.height - 36), text, font=f, fill='#efeee9')
    return im


def main(after, out, before=None):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    da = pickle.load(open(after, 'rb'))
    db = None
    if before and before.endswith('.glb'):
        # an earlier animated GLB with the same rig: pose it with this build's skinning matrices
        db = {'model': G.read(before), 'clips': da['clips']}
    elif before:
        db = pickle.load(open(before, 'rb'))
    size = (700, 800)
    for name, a, e, c, h, pose in VIEWS:
        im_a = view(da, name, a, e, c, h, pose, size)
        if db is None:
            im_a.save(out / f'shag_{name}.jpg', quality=92)
            continue
        im_b = view(db, name, a, e, c, h, pose, size)
        sheet = Image.new('RGB', (size[0] * 2 + 8, size[1]), '#0d1015')
        sheet.paste(tag(im_b, 'before · flat lock cards'), (0, 0))
        sheet.paste(tag(im_a, 'after · clumped strands'), (size[0] + 8, 0))
        sheet.save(out / f'shag_{name}_before_after.jpg', quality=92)
        print('wrote', name, flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:4])
