"""Stage 9c: the approved region maps -> sequential mix factors for the live material (after the slipper project).

python3 -I make_mix_masks_cow.py <regions_dir> <out_dir>

For classes c_0 (base) .. c_n in a fixed order, each texel's soft weights w_i (one-hot blurred by 1.2 px) become
factors f_i = w_i / (w_0 + ... + w_i); a chain of Mix nodes acc_i = mix(acc_{i-1}, c_i, f_i) then gives the weighted
average, with soft, unjagged edges. Empty texels are first filled with the nearest class so the bake margins
carry the right fabric. Three factors per PNG (R, G, B); PNG keeps them lossless.
  body (regions_cow.png):  1 fur (base), 2 shag, 3 fleece, 4 satin, 5 lace, 6 leggings, 7 paint, 8 knit, 9 hooves,
                           10 bow, 11 socks, 12 cord, 13 horn paint, 14 horn rings, 15 wire   -> mix_cow_a..e.png
  mask (regions_mask.png): 20 plaster (base), 21 black paint, 22 eye, 23 pupil, 24 snout, 25 slits -> mix_mask_a..b.png
"""
import sys, os, json
import numpy as np, cv2
from PIL import Image
from scipy.ndimage import distance_transform_edt

RG, OUT = sys.argv[1:3]
os.makedirs(OUT, exist_ok=True)
ORDER = {"cow": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "mask": [20, 21, 22, 23, 24, 25]}
info = {}
for tag, order in ORDER.items():
    cls = np.asarray(Image.open(f"{RG}/regions_{tag}.png"))
    empty = cls == 0
    _, (iy, ix) = distance_transform_edt(empty, return_indices=True)
    cls = cls[iy, ix]
    w = np.stack([cv2.GaussianBlur((cls == k).astype(np.float32), (0, 0), 1.2) for k in order], -1)
    cum = np.cumsum(w, -1)
    f = np.where(cum > 1e-6, w / np.maximum(cum, 1e-6), 0)[..., 1:]           # factors for classes 1..n
    pad = (-f.shape[-1]) % 3
    f = np.concatenate([f, np.zeros(f.shape[:2] + (pad,), np.float32)], -1)
    names = []
    for i in range(f.shape[-1] // 3):
        n = f"mix_{tag}_{'abcde'[i]}.png"; names.append(n)
        Image.fromarray(np.round(f[..., 3 * i:3 * i + 3] * 255).astype(np.uint8)).save(f"{OUT}/{n}")
    info[tag] = {"order": order, "files": names}
    print(tag, "->", names)
json.dump(info, open(f"{OUT}/mix_masks.json", "w"), indent=1)
