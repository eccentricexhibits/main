# Arrow transition — PNG sequence (split archive)

360 lossless RGBA PNG frames, 6878 x 1080, 60 FPS, 6.00 s, transparent
background. Split into 95 MB parts to fit GitHub's per-file limit.

## Reassemble

```sh
cat arrow-transition-png-sequence.zip.part-* > arrow-transition-png-sequence.zip
sha256sum -c checksum.sha256
unzip arrow-transition-png-sequence.zip   # extracts frames-final/frame_0000.png ... frame_0359.png
```

Frame 180 = 3.000 s is the fully-covered cut frame.
This branch exists only to carry these files — safe to delete once downloaded.
