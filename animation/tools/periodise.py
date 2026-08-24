#!/usr/bin/env python3
"""Force a plate to be exactly periodic on its travel vector.

    python3 animation/tools/periodise.py DIR

The short-loop plates are built from a placement that is periodic on the travel
vector by construction — every arrow has an identical twin one travel vector
away. The *rasterisation* is not quite: Chromium's Gaussian blur is not
position-independent, so the two copies of an arrow come out differing by a
handful of levels on their glow. Measured on the 2-minute plates that is a mean
of about 0.01/255 with a peak near 45, on well under 1% of pixels.

Small, but it lands exactly at the loop point, where the whole design promise is
that nothing happens. So rather than argue about whether it is visible, this
removes it: pixels related by the travel vector form an orbit that *should* hold
one value, so each orbit is collapsed onto a single member.

Sweeping from the bottom up means every source is already final when it is read,
which makes each orbit take the value of its lowest member in the plate. Only
pixels that already agree to within a few levels are touched, so the picture does
not change — it just becomes exactly periodic, and the loop becomes bit-exact.
"""
import json
import sys
import pathlib
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def periodise(arr: np.ndarray, dx: int, dy: int) -> np.ndarray:
    """Make arr[y, x] == arr[y - dy, x + dx] wherever both are in bounds."""
    out = arr.copy()
    h = out.shape[0]
    for y in range(h - dy - 1, -1, -1):
        out[y, dx:] = out[y + dy, : out.shape[1] - dx]
    return out


def orbit_error(arr: np.ndarray, dx: int, dy: int):
    """Max and mean disagreement between pixels one travel vector apart."""
    a = arr.astype(np.int32)
    pm = np.concatenate([a[..., :3] * a[..., 3:4] // 255, a[..., 3:4]], axis=2)
    d = np.abs(pm[dy:, :-dx] - pm[:-dy, dx:])
    return d.max(), d.mean()


def main(root: str) -> None:
    base = pathlib.Path(root)
    meta = json.loads((base / "layers.json").read_text())
    for m in meta["layers"]:
        path = base / "plates" / m["plate"]
        dx, dy = int(m["travelX"]), int(m["travelY"])
        arr = np.asarray(Image.open(path).convert("RGBA"))
        before = orbit_error(arr, dx, dy)
        fixed = periodise(arr, dx, dy)
        after = orbit_error(fixed, dx, dy)
        changed = int((np.abs(fixed.astype(np.int32) - arr.astype(np.int32)).max(axis=2) > 0).sum())
        Image.fromarray(fixed, "RGBA").save(path, optimize=True)
        print(
            f"layer {m['layer']}  travel {dx},-{dy}  "
            f"orbit error {before[0]}/{before[1]:.5f} -> {after[0]}/{after[1]:.5f}  "
            f"pixels touched {changed} ({changed / arr[..., 0].size * 100:.3f}%)"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
