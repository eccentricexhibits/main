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
BG = np.array([0x8A, 0x25, 0xC9])
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


def coverage(img):
    d = np.abs(img - BG).sum(axis=2)
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
    for name in sorted(os.listdir(FRAMES)):
        if name.endswith(".png"):
            frames[name[:-4]] = load(os.path.join(FRAMES, name))
    if not frames:
        sys.exit("no frames — run `node animation/verify.js` first")

    scale = next(iter(frames.values())).shape[1] / 6878.0
    print(f"frames at {next(iter(frames.values())).shape[1]}x{next(iter(frames.values())).shape[0]} "
          f"({scale:.3f} of full size)\n")

    print("ink coverage (fraction of pixels differing from the purple ground)")
    print("  frame     >12    >25    >40    >60")
    for name, img in frames.items():
        c = coverage(img)
        print(f"  {name:<8}" + "  ".join(f"{c[t]:.3f}" for t in (12, 25, 40, 60)))
    print("  reference  0.145  0.119  0.102  0.075")

    if "t0" in frames and "t180" in frames:
        diff = np.abs(frames["t0"] - frames["t180"])
        print(f"\nloop seam  t=180 vs t=0: max channel diff {diff.max()}, mean {diff.mean():.4f}")
        print("  " + ("SEAMLESS" if diff.max() <= 2 else "MISMATCH — the loop will jump"))
        if scale < 0.999:
            print("  (only meaningful at VERIFY_SCALE=1 — a scaled screenshot lands layers "
                  "on half-pixels and shows anti-aliasing noise)")

    if "t0" in frames and "t10" in frames:
        peak, dx, dy = best_shift(frames["t0"], frames["t10"])
        if dx:
            full_dx, full_dy = dx / scale, dy / scale
            slope = -full_dy / full_dx
            speed = (full_dx**2 + full_dy**2) ** 0.5 / 10
            print(f"\ntravel  over 10 s: ({dx}, {dy}) px at {scale:.3f} scale "
                  f"-> ({full_dx:.0f}, {full_dy:.0f}) px full size")
            print(f"  slope {slope:.3f} (spec 2.467)   dominant-layer speed {speed:.1f} px/s "
                  f"  correlation peak {peak:.3f}")
            print("  (a multi-speed field has no single slope in the composite; run "
                  "`node animation/verify.js --layer N` to measure one layer)")


if __name__ == "__main__":
    main()
