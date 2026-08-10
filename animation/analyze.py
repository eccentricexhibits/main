#!/usr/bin/env python3
"""Pixel checks on the frames written by animation/verify.js.

    python3 animation/analyze.py

Reports ink coverage (target ~12%, matching the client's reference clip),
verifies that t=180 is identical to t=0, and recovers the travel slope by
matching two frames a known interval apart.
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, ".verify")
FFMPEG = os.environ.get("FFMPEG")

if not FFMPEG:
    try:
        import imageio_ffmpeg

        FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        FFMPEG = "ffmpeg"


def load(png):
    """Decode a PNG to an HxWx3 uint8 array via ffmpeg (no image libs needed)."""
    with open(png, "rb") as fh:
        header = fh.read(24)
    w = int.from_bytes(header[16:20], "big")
    h = int.from_bytes(header[20:24], "big")
    raw = subprocess.run(
        [FFMPEG, "-v", "error", "-i", png, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 3).astype(int)


def coverage(img, plate):
    d = np.abs(img - plate).sum(axis=2)
    return {t: float((d > t).mean()) for t in (12, 25, 40, 60)}


def best_shift(a, b):
    """Displacement (dx, dy) carrying frame a onto frame b, by phase correlation."""
    ga = a.sum(axis=2) / 3.0
    gb = b.sum(axis=2) / 3.0
    ga = ga - ga.mean()
    gb = gb - gb.mean()
    h, w = ga.shape
    win = np.outer(np.hanning(h), np.hanning(w))
    fa = np.fft.rfft2(ga * win)
    fb = np.fft.rfft2(gb * win)
    r = fb * np.conj(fa)
    r /= np.abs(r) + 1e-9
    corr = np.fft.irfft2(r, s=(h, w))
    dy, dx = np.unravel_index(np.argmax(corr), corr.shape)
    if dy > h // 2:
        dy -= h
    if dx > w // 2:
        dx -= w
    return float(corr.max()), int(dx), int(dy)


def main():
    frames = {}
    plate = None
    for name in sorted(os.listdir(FRAMES)):
        if not name.endswith(".png"):
            continue
        img = load(os.path.join(FRAMES, name))
        if name == "plate.png":
            plate = img
        else:
            frames[name[:-4]] = img
    if not frames:
        sys.exit("no frames — run `node animation/verify.js` first")

    first = next(iter(frames.values()))
    scale = first.shape[1] / 6878.0
    print(f"frames at {first.shape[1]}x{first.shape[0]} ({scale:.3f} of full size)\n")

    if plate is None:
        print("no plate.png — skipping ink coverage (re-run verify.js to capture one)\n")
    else:
        print("ink coverage (fraction of pixels the arrows touch, vs the bare background)")
        print("  frame     >12    >25    >40    >60")
        for name in sorted(frames, key=lambda n: int(n[1:])):
            c = coverage(frames[name], plate)
            print(f"  {name:<8}" + "  ".join(f"{c[t]:.3f}" for t in (12, 25, 40, 60)))
        print("  the client's reference clip sits at 0.145 / 0.119 / 0.102 / 0.075,")
        print("  but measured against a flat purple ground — indicative only now.")

    times = sorted(int(n[1:]) for n in frames)
    if len(times) > 1 and times[0] == 0:
        last = f"t{times[-1]}"
        diff = np.abs(frames["t0"] - frames[last])
        print(f"\nloop seam  {last} vs t=0: max channel diff {diff.max()}, mean {diff.mean():.4f}")
        print("  " + ("SEAMLESS" if diff.max() <= 2 else "MISMATCH — the loop will jump"))
        if scale < 0.999:
            print("  (only meaningful at VERIFY_SCALE=1 — a scaled screenshot lands layers "
                  "on half-pixels and shows anti-aliasing noise)")

    if "t0" in frames and "t60" in frames:
        peak, dx, dy = best_shift(frames["t0"], frames["t60"])
        if dx:
            full_dx, full_dy = dx / scale, dy / scale
            slope = -full_dy / full_dx
            speed = (full_dx**2 + full_dy**2) ** 0.5 / 60
            print(f"\ntravel  over 60 s: ({dx}, {dy}) px at {scale:.3f} scale "
                  f"-> ({full_dx:.0f}, {full_dy:.0f}) px full size")
            print(f"  slope {slope:.3f} (spec 2.467)   dominant-layer speed {speed:.2f} px/s "
                  f"  correlation peak {peak:.3f}")
            print("  (a multi-speed field has no single slope in the composite; run "
                  "`node animation/verify.js --layer N` to measure one layer)")


if __name__ == "__main__":
    main()
