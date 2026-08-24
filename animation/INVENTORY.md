# What exists, and what it is for

Short version: **there are no finished videos.** The deliverables are layers you stack in
Premiere. `ASSEMBLY.md` is the instruction sheet; this page is the parts list.

## 1. Layers you build from

| Folder | What it is | Length | Size |
| --- | --- | --- | --- |
| `ambient-layer/` | The drifting arrows. Six plates + keyframes. | 6:00 loop | 7 MB |
| `ambient-2min/` | The same arrows at the same speed, on a 2:00 loop | 2:00 loop | 3 MB |
| `logo-layer/` | The Vector logo formation. PNG sequence, 2,040 frames at 60 fps. | 0:34 | 753 MB |

All full resolution (6878 × 1080) and transparent. The ambient folders are plates rather
than frames because six images and six linear keyframes reproduce the whole loop exactly at
any frame rate — the frame sequence for one 6-minute loop at 120 fps would be 43,200 frames
and about 84 GB.

Two pieces of the show are **not** here:

- **The ground gradient.** Build it in Premiere: vertical, `#13071A` top to `#3B1056`
  bottom, plus ~3% grain over it. A PNG of a gradient this wide will band on the wall; the
  grain has to go on after the gradient reaches final values, which is why the transparent
  exports carry none.
- **The speaker cards.** Never exported as a layer. They run 4:17.5 → 4:26.7 on the
  six-minute clock, wall panels only. Ask and they come out like the others.

## 2. Which ambient folder to use

Both are the same field at the same arrow speed. They differ only in loop length.

- Making a **6-minute** piece → `ambient-layer/`
- Making a **2-minute** piece (the venue cap) → `ambient-2min/`

The build is identical either way — six plates, linear position keyframes, opacities as
tabled — with the sequence length and the second keyframe time changed to match. Each
folder's README carries its own Position table; the numbers differ between them, so use the
table from the folder you are actually using.

`ambient-2min/other-speeds/` holds four variants at 0.5x, 1x, 2x and 3x **arrow speed**,
built when I misread a request as being about speed rather than file length. They are
sound, but they change the motion, so ignore them unless you deliberately want faster or
slower arrows. `3x/` is the approved field played three times as fast, and its plates are
byte-identical to `ambient-layer/`.

## 3. Old test exports — safe to delete

None of these are part of the show. They are earlier experiments, kept only because nobody
has said to bin them. Together they are about 500 MB of the repository's ~1.9 GB.

| File | What it was | Why it is dead |
| --- | --- | --- |
| `arrow-loop_3-45_4-40_60fps_half.mp4` | 55 s of the logo event, half resolution | a test of the MP4 export path |
| `arrow-alpha-4s_qtrle.mov` | 4 s, lossless alpha | proving a codec could carry alpha |
| `arrow-alpha-2s_qtrle_quarter.mov` | 2 s, lossless alpha, quarter size | same, smaller |
| `png-seq/` | 60 s transparent PNG sequence, quarter resolution | superseded by `logo-layer/` |

Say the word and they go.

## 4. Preview clips sent in chat

Not deliverables and not in the repository — quarter size, flattened onto black, made only
so you could see something before committing to a build:

- the logo formation
- the ambient field crossing its 6-minute loop point
- four arrow speeds stacked for comparison
- the 2-minute loop crossing its wrap point

If you want any of them regenerated, they cost a few minutes each.

## 5. So what are the actual videos?

Whatever you assemble. As things stand the show is one 6-minute piece, or a 2-minute piece
if the venue's cap applies. The logo formation is timed to land at 3:59 on the six-minute
clock; on a 2-minute timeline it has to be re-placed or dropped, and re-timing it is a
change to the formation layer, not something you can do by trimming.

If you tell me which finished pieces the venue actually needs — lengths, and whether each
one contains the logo event — I can say exactly which layers each of them takes.
