# Transparent PNG sequence — 60 s, no ground

1,800 frames, 30 fps, 1720 × 270, RGBA. Covers loop time **3:40 → 4:40**: twenty
seconds of ambient arrows, then the Vector logo build. Speaker cards are off, and
`--alpha 0` means there is no ground at all — arrows, glow and trails over nothing.

Split by size, not by frame count: frame weight swings from ~500 KB in the dense
ambient passages to ~20 KB mid-transition, so equal frame counts gave wildly unequal
parts and one of them overshot GitHub's 100 MB file limit.

| Part | Frames | Size |
| --- | --- | --- |
| `part1_frames-0000-0325.zip` | 0–325 | 80 MB |
| `part2_frames-0326-0637.zip` | 326–637 | 80 MB |
| `part3_frames-0638-1493.zip` | 638–1493 | 80 MB |
| `part4_frames-1494-1799.zip` | 1494–1799 | 73 MB |

Unzip all four into one directory and import `f_%05d.png` as a sequence at 30 fps.
Frame numbering is continuous across the parts.

Regenerate with:

```sh
node animation/export.js --fps 30 --from 220 --to 280 --scale 0.25 \
  --alpha 0 --speakers 0 --seq /tmp/pngseq
```

`--scale 0.5` doubles the resolution and roughly quadruples the bytes (~1.2 GB);
full size is ~4.9 GB, which is why this test set is at quarter scale.

These are build artifacts sitting on a feature branch. Deleting the branch once it
has served its purpose reclaims the space — nothing here needs to reach `main`.
