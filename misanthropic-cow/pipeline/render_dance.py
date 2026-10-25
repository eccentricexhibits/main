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


def showcase(data, out, size=(720, 960), angle=-24):
    """One video of every clip in turn (a few loops each), labelled."""
    plan = [('Idle', 1), ('Walk', 4), ('Run', 5), ('Sneak', 2), ('Jumping Jacks', 1), ('Look Around', 1), ('Chicken Dance', 1)]
    model = data['model']
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', f'{size[0]}x{size[1]}',
           '-framerate', str(AN.FPS), '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time(); n = 0
    for name, loops in plan:
        c = data['clips'][name]
        frames = len(c['times']) - 1
        for k in range(frames * loops):
            i = k % frames
            t = c['times'][i]
            ph = next((a for a, b, e in c['phases'] if b <= t < e), c['phases'][-1][0])
            sub = name.upper() if ph == name else f'{name.upper()} \u00b7 {ph.upper()}'
            im = frame_image(model, c['mats'][i], angle, 4, size, center=(0, .92, .04), height=2.0, title='Animation library', sub=sub)
            p.stdin.write(im.tobytes()); n += 1
        print(f'{name}: {n} frames {time.time()-t0:.0f}s', flush=True)
    p.stdin.close(); assert p.wait() == 0


def clip_sheet(data, out, names=None, per=5, size=(380, 500)):
    names = names or list(data['clips'])
    sheet = Image.new('RGB', (per * size[0], len(names) * size[1]), '#161b22')
    for r, name in enumerate(names):
        c = data['clips'][name]
        for i in range(per):
            k = int(round(i * (len(c['times']) - 1) / per))
            t = c['times'][k]
            im = frame_image(data['model'], c['mats'][k], -28, 4, size, center=(0, .93, .03), height=2.05,
                             title=name if i == 0 else None, sub=f't={t:.2f}s')
            sheet.paste(im, (i * size[0], r * size[1]))
    sheet.save(out, quality=88)


if __name__ == '__main__':
    data = pickle.load(open(sys.argv[1], 'rb'))
    mode = sys.argv[2]
    if mode == 'board':
        times = [float(x) for x in sys.argv[4].split(',')]
        views = [tuple(map(float, v.split(':'))) for v in (sys.argv[5].split(',') if len(sys.argv) > 5 else ['-12:4'])]
        storyboard(data, times, sys.argv[3], views)
    elif mode == 'video':
        video(data, sys.argv[3])
    elif mode == 'showcase':
        showcase(data, sys.argv[3])
    elif mode == 'sheet':
        clip_sheet(data, sys.argv[3], ['Idle', 'Walk', 'Run', 'Sneak', 'Jumping Jacks', 'Look Around'])
