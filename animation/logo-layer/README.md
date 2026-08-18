# Logo-formation layer — full size, transparent, 60 fps

The arrows forming the Vector logo, on their own. No ambient arrow field, no ground
gradient, no grain, no speaker cards — just the formation over nothing, at the speed
the piece currently runs.

**2,040 frames · 60 fps · 6878 × 1080 · RGBA · 753 MB**

## Where it sits on the clock

Frame 0 is **t = 239.000 s** on the master 360-second loop, and the sequence runs to
t = 273.000 s. The event itself starts at 240 s, so the first 60 frames are deliberately
fully transparent — a visible marker in the edit that the layer is landing where it
should. It tails off the same way: everything has faded by 272.7 s, so the last ~18
frames are empty too.

Every layer of this piece seeks the same master clock, so parts exported separately drop
onto a timeline in sync with no matching to do. A frame at t = 252 is the same instant in
every layer.

| | |
| --- | --- |
| Frame 0 | t = 239.000 s |
| Event starts | t = 240.000 s (frame 60) |
| Sweep ends | t = 247.000 s (frame 480) |
| Gather ends | t = 251.000 s (frame 720) |
| Logo revealed | t = 253.500 s (frame 870) |
| Logo resolved | t = 255.500 s (frame 990) |
| Release begins | t = 266.700 s (frame 1662) |
| Fully faded | t = 272.700 s (frame 2022) |

## Assembling

Unzip all eight parts into one directory and import `f_%05d.png` as a sequence at
**60 fps**. Frame numbering is continuous across the parts — they are split only to stay
under GitHub's 100 MB per-file limit.

| Part | Frames | Size |
| --- | --- | --- |
| `part01_frames-00000-00194.zip` | 0–194 | 94 MB |
| `part02_frames-00195-00239.zip` | 195–239 | 93 MB |
| `part03_frames-00240-00282.zip` | 240–282 | 94 MB |
| `part04_frames-00283-00334.zip` | 283–334 | 94 MB |
| `part05_frames-00335-00409.zip` | 335–409 | 95 MB |
| `part06_frames-00410-00709.zip` | 410–709 | 95 MB |
| `part07_frames-00710-01307.zip` | 710–1307 | 95 MB |
| `part08_frames-01308-02039.zip` | 1308–2039 | 93 MB |

The parts are split by **size, not frame count**, which is why they hold wildly different
numbers of frames. Frame weight swings by more than ten to one across this window: during
the sweep every particle is on screen trailing and a frame runs to 2.3 MB, while the
gather, logo and hold sit around 170 KB. Part 2 carries 45 frames; part 8 carries 732.

Zips are **stored, not deflated**. PNG is already compressed, so deflating again buys
close to nothing and costs many minutes.

## Compositing note

The arrows and the mark are white, and the piece assumes a dark ground. Over anything
light they disappear. The magenta survives on any background. RGB is unpremultiplied, so
colours hold their value as alpha falls away — composite with a straight-alpha (not
premultiplied) interpretation.

## Regenerating

```sh
node animation/export.js --fps 60 --from 239 --to 273 --scale 1 \
  --alpha 0 --speakers 0 --ambient 0 --seq /tmp/logo-layer
```

`--ambient 0` drops the drifting tile layers and the grain while keeping the logo event,
`--speakers 0` drops the speaker cards, and `--alpha 0` means the ground is there at zero
opacity — that is, not there at all. Chromium's PNGs go straight to disk, so no codec
ever touches the alpha channel.

Took 13.7 minutes in this container: about 1.7 fps through the light stretches, dropping
to ~0.3 fps at the peak of the sweep.

## Verification

- 2,040 files, no gaps, every one 6878 × 1080 RGBA.
- Head and tail confirmed fully transparent; interior frames reach alpha 255.
- All eight zips pass CRC, and together hold each of the 2,040 frames exactly once.
- Spot-checked frames are byte-identical inside the zips and on disk (SHA-256).

These are build artifacts sitting on a feature branch. Deleting the branch once it has
served its purpose reclaims the space — nothing here needs to reach `main`.
