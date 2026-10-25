"""Render storyboard frames / video of the rigged v10 dance from rigged.pkl."""
import sys, pickle, subprocess, time
from pathlib import Path
import numpy as np
from PIL import Image
import render as R
import anim as AN


def frame_image(model, mats, angle=-10, el=4, size=(540, 720), center=(0, .90, .05), height=1.9, clay=False, title=None, sub=None):
    P = R.skin_parts(model, mats)
    tmp = type(model)()
    tmp.materials, tmp.images, tmp.parts = model.materials, model.images, P
    r = R.Renderer(tmp)
    r.cache = frame_image.cache
    im = r.render(angle, el, size, center=center, height=height, clay=clay)
    if title:
        R.label(im, title, sub)
    return im


frame_image.cache = {}


def storyboard(data, times, out, views=((-12, 4),), **kw):
    model, mats, T = data['model'], data['mats'], data['times']
    w, h = kw.get('size', (540, 720))
    sheet = Image.new('RGB', (w * len(times), h * len(views)), '#161b22')
    for j, (a, e) in enumerate(views):
        for i, t in enumerate(times):
            k = int(round(t * AN.FPS)) % (len(T) - 1)
            ph = AN.PHASES[int((t % AN.DURATION) // 3)]
            sheet.paste(frame_image(model, mats[k], a, e, title='Chicken Dance' if j == 0 else None, sub=f'{ph.upper()}  t={t:.2f}s', **kw), (w * i, h * j))
    sheet.save(out, quality=92)


def video(data, out, size=(720, 960), angle=-14):
    model, mats, T = data['model'], data['mats'], data['times']
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', f'{size[0]}x{size[1]}',
           '-framerate', str(AN.FPS), '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(len(T) - 1):
        t = T[k]
        ph = AN.PHASES[int((t % AN.DURATION) // 3)]
        im = frame_image(model, mats[k], angle, 4, size, title='Chicken Dance', sub=f'{int(t // 3) + 1:02d} / {ph.upper()}')
        p.stdin.write(im.tobytes())
        if k % 60 == 0:
            print(f'frame {k}/{len(T)-1} {time.time()-t0:.0f}s', flush=True)
    p.stdin.close(); assert p.wait() == 0


if __name__ == '__main__':
    data = pickle.load(open(sys.argv[1], 'rb'))
    mode = sys.argv[2]
    if mode == 'board':
        times = [float(x) for x in sys.argv[4].split(',')]
        views = [tuple(map(float, v.split(':'))) for v in (sys.argv[5].split(',') if len(sys.argv) > 5 else ['-12:4'])]
        storyboard(data, times, sys.argv[3], views)
    elif mode == 'video':
        video(data, sys.argv[3])
