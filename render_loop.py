#!/usr/bin/env python3
"""CPU port of the hero banner's FluidGradient shader.

Renders frames of the 108 s cycle at exact loop-phase values
(angle = 2*pi * i / N), so frame N wraps seamlessly to frame 0.

The noise field is sampled at a fixed scale of 0.5 units per 1080 px of
height (the scale used for every wall render), so any output size shows
the pattern at identical feature size: a narrower frame is a crop of the
same field, never a squish. OFFSET_X_PX shifts the crop window, in
output pixels, relative to the left edge of the 6872x1080 wall frame.

Configure with env vars: RENDER_W, RENDER_H, RENDER_OFFSET_X_PX,
RENDER_COLOR_A, RENDER_COLOR_B (e.g. '#8A25C9'). Needs numpy and
imageio-ffmpeg (or FFMPEG=/path/to/ffmpeg with libx264).

Usage: render_loop.py START COUNT OUT.mp4   (segment worker, frames START..START+COUNT-1 of 6480)
       render_loop.py --still T OUT.png     (single frame at time T seconds)
"""
import os
import subprocess
import sys

import numpy as np

f32 = np.float32

W = int(os.environ.get('RENDER_W', '1920'))
H = int(os.environ.get('RENDER_H', '1080'))
OFFSET_X_PX = float(os.environ.get('RENDER_OFFSET_X_PX', '2476'))  # centre of the wall frame
FPS = 60
DURATION = 108.0                      # shader cycle length in seconds
N = int(round(FPS * DURATION))        # 6480 frames
BASE_OFFSET = (f32(37.25), f32(61.70))  # fixed u_offset (random per-load on the site)


def hex_color(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=f32) / f32(255.0)


COLOR_A = hex_color(os.environ.get('RENDER_COLOR_A', '#8A25C9'))
COLOR_B = hex_color(os.environ.get('RENDER_COLOR_B', '#FF9E00'))

FFMPEG = os.environ.get('FFMPEG') or __import__('imageio_ffmpeg').get_ffmpeg_exe()


def fract(x):
    return x - np.floor(x)


def hash2(px, py):
    hx = fract(px * f32(234.34))
    hy = fract(py * f32(435.345))
    d = hx * (hx + f32(34.23)) + hy * (hy + f32(34.23))
    hx = hx + d
    hy = hy + d
    return fract(hx * hy)


def noise(px, py):
    ix = np.floor(px)
    iy = np.floor(py)
    fx = px - ix
    fy = py - iy
    ux = fx * fx * (f32(3.0) - f32(2.0) * fx)
    uy = fy * fy * (f32(3.0) - f32(2.0) * fy)
    a = hash2(ix, iy)
    b = hash2(ix + f32(1.0), iy)
    c = hash2(ix, iy + f32(1.0))
    d = hash2(ix + f32(1.0), iy + f32(1.0))
    ab = a + (b - a) * ux
    cd = c + (d - c) * ux
    return ab + (cd - ab) * uy


def fbm(px, py):
    v = np.zeros_like(px)
    a = f32(0.5)
    for _ in range(4):
        v = v + a * noise(px, py)
        px = px * f32(2.0) + f32(3.1)
        py = py * f32(2.0) + f32(1.7)
        a = a * f32(0.5)
    return v


def domain_warp(px, py, ctx, cty):
    qx = fbm(px + ctx * f32(0.8), py + cty * f32(0.8))
    qy = fbm(px + cty * f32(0.6) + f32(5.2), py + ctx * f32(0.6) + f32(1.3))
    rx = fbm(px + f32(3.0) * qx + ctx * f32(0.5) + f32(1.7),
             py + f32(3.0) * qy + cty * f32(0.5) + f32(9.2))
    ry = fbm(px + f32(3.0) * qx + cty * f32(0.4) + f32(8.3),
             py + f32(3.0) * qy + ctx * f32(0.4) + f32(2.8))
    return fbm(px + f32(3.5) * rx + ctx * f32(0.3),
               py + f32(3.5) * ry + cty * f32(0.3))


def base_grid(w=None, h=None, offset_x_px=None):
    w = W if w is None else w
    h = H if h is None else h
    offset_x_px = OFFSET_X_PX if offset_x_px is None else offset_x_px
    # 0.5 noise units per 1080 px vertically; horizontally the same per-pixel
    # scale (0.5 units per 1920 px at 16:9 reference), i.e. square pixels.
    xs = (np.arange(w, dtype=f32) + f32(0.5) + f32(offset_x_px)) / f32(1920.0)
    ys = f32(1.0) - (np.arange(h, dtype=f32) + f32(0.5)) / f32(h)
    px = xs * f32(0.5) + BASE_OFFSET[0]
    py = ys * f32(0.5) + BASE_OFFSET[1]
    return (np.broadcast_to(px, (h, w)).copy(),
            np.broadcast_to(py[:, None], (h, w)).copy())


def render_frame(px, py, phase, color_a=None, color_b=None):
    """phase in [0, 1): fraction of the 108 s cycle."""
    color_a = COLOR_A if color_a is None else color_a
    color_b = COLOR_B if color_b is None else color_b
    angle = f32(2.0 * np.pi) * f32(phase)
    ctx = f32(np.cos(angle) * 0.5)
    cty = f32(np.sin(angle) * 0.5)
    t = domain_warp(px, py, ctx, cty)
    tt = np.clip((t - f32(0.1)) / f32(0.5), f32(0.0), f32(1.0))
    s = tt * tt * (f32(3.0) - f32(2.0) * tt)
    rgb = color_a[None, None, :] + (color_b - color_a)[None, None, :] * s[:, :, None]
    rgb = np.clip(rgb, 0.0, 1.0)  # 1.12 web-brightness boost removed
    return (rgb * f32(255.0) + f32(0.5)).astype(np.uint8)


def main():
    if sys.argv[1] == '--still':
        t_sec = float(sys.argv[2])
        out = sys.argv[3]
        px, py = base_grid()
        frame = render_frame(px, py, (t_sec % DURATION) / DURATION)
        subprocess.run(
            [FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo',
             '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-i', '-', '-frames:v', '1', out],
            input=frame.tobytes(), check=True)
        return

    start, count, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    px, py = base_grid()
    enc = subprocess.Popen(
        [FFMPEG, '-y', '-loglevel', 'error',
         '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
         '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '10',
         '-pix_fmt', 'yuv444p', out],
        stdin=subprocess.PIPE)
    for i in range(start, start + count):
        frame = render_frame(px, py, i / N)
        enc.stdin.write(frame.tobytes())
    enc.stdin.close()
    enc.wait()
    if enc.returncode:
        sys.exit(enc.returncode)


if __name__ == '__main__':
    main()
