# CD-R rip analysis: "bd" (Drastic Measures, 2004)

## Summary

| Check | Result |
|---|---|
| Upload integrity (16 × RAR5 volumes, SHA-256 vs. upload record) | All 16 OK |
| RAR archive CRC test (`unrar t`) | All files OK, no errors |
| Session file references (28 files in the DP session) | All 28 present |
| CD layout references (10 tracks) | All 10 present |
| CD-R read damage (zeroed sectors, silence gaps, truncation, odd sizes) | None found |
| Audio damage | **One file pair: `Baby Dolls.L` / `Baby Dolls.R` in the session. Repaired.** |

## What the disc contains

`bd/BD-2024/` is a Mac OS project from October 2004 by "Drastic Measures". The ten
`._*` AppleDouble files carry the classic Mac resource forks and Finder type/creator
codes. These are essential, because the audio itself has no headers.

### 1. `DrasticMeasures-NewSong Project/`: MOTU Digital Performer 3.1.1 session
* `DrasticMeasures-New Songs` is the session document. Its type/creator is `PERF`/`MOUP`,
  and its `vers` resource reads "Digital Performer™ v3.1.1". It was originally on
  "LaCie d2 78 GB:FW 27B:DrasticMeasures:…".
* `Audio Files/` holds 28 Sound Designer II files: 16-bit, 44.1 kHz, mono, with
  stereo tracks split into `.L`/`.R`. They cover full-band takes (Baby Dolls,
  I Believe, Teddy Bears Live, WarIsPeace, Untitled-1/-7/-12, 2-13), bass takes and
  vocal takes.
* `Undo/` holds 6 small SD2 fragments, which are DP's undo history (safe to ignore).

### 2. `DrasticMeasures-Selections/`: the CD master
* 11 stereo SD2 mixes (16-bit/44.1 kHz).
* `DrasticMeasures-SelectionsCD` is a burn layout document (`CrTC`/`CDr3`). Its data
  fork is 0 bytes, which is normal because everything lives in the resource fork:
  title "Audio CD" and 10 tracks:
  1. Baby Dolls 2. Flowers 3. IMadeYouCry 4. LayW/Me 5. Teddy Bears Live*
  6. Jehovas'Daughter 7. SweetHeart 8. 30'sGermanNightclub 9. I Believe 10. WarIsPeace
* `Teddy Bears...` (2:22) is an extra mix that is **not** in the CD layout.
* `Icon\r` is the custom folder icon.

## Issues found

### A. `Baby Dolls.L` / `.R` (session copies): periodic single-sample glitches. REPAIRED
* Every 131,072 samples (about 2.97 s, a 256 KiB block of a mono file), the last
  3,278 samples before the block boundary are shifted one sample early, and a
  single `0` sample is inserted at the boundary (e.g. `… -198, -528, 0, -604 …`).
  This happens 69 times per channel, and each one is an audible tick.
* The mechanical, block-aligned pattern points to a buffer bug in the software that
  wrote or copied the file, not to CD-R read damage (the RAR CRCs match).
* The stereo `Selections/Baby Dolls` mix is bit-identical to the L/R pair everywhere
  else and is smooth across those boundaries. Its second-difference energy at the
  boundaries is 682, against a baseline of 514 and the damaged copy's 3,445. That
  makes it the good copy.
* **Repair:** I rebuilt `Baby Dolls.L` and `Baby Dolls.R` from the left and right
  channels of the clean stereo mix. That replaced 225,946 (L) and 225,940 (R)
  samples. Zero samples at block boundaries went from 69 to 0 per channel. File
  lengths are unchanged, so the original resource forks and DP session stay valid.
* No other file has this signature (0 hits in all 44 other audio files).

### B. Not damage, but worth knowing
* **Filenames with Mac-only characters** are stored as Unicode private-use
  characters in the RAR (macOS/SMB "SFM" mapping): U+F022 = `/`, U+F021 = `*`,
  U+F029 = trailing `.`, U+F00D = `\r`. On Windows or Linux, `unrar` truncates
  them: `LayW/Me` becomes `LayW`, `bass-layw/me-0` becomes `bass-layw`,
  `Teddy Bears Live*` becomes `Teddy Bears Live`, and `Icon\r` becomes `Icon`.
  Extracting on a Mac restores them correctly.
* **The audio files have no headers.** This is raw big-endian PCM (Sound Designer
  II), so most modern software sees them as "data". Tools like `file` report false
  positives ("AIX core file", "AAC", "Atari bitmap"). The WAV/FLAC exports below
  fix this.
* **The `I Believe.wav` filename is misleading.** It isn't a WAV; it's an SD2 file
  that was renamed after the CD layout was made, so the layout's alias points to
  `I Believe`. Toast/Jam may ask you to locate it.
* **The session file `I Believe copy-2.L/.R` is actually "30's German Nightclub".**
  It's bit-identical to the CD track `30'sGermanNightclub`, so it was probably a
  copied region reused for a different song. Labelling only; nothing is lost.
* The CD's `Teddy Bears Live` is the session's `Teddy Bears Live-0` with the first
  7.57 s trimmed (bit-identical otherwise). `I Believe` and `WarIsPeace` are
  bit-identical to their session L/R pairs.
* `Baby Dolls` has 2 full-scale (clipped) samples, and `I Believe-0.R` has 11 sharp
  transients. Both are present identically in the independent stereo copies, so
  they're part of the original recordings.

## Deliverables (produced in the analysis session)
* `DrasticMeasures-Selections-CD-FLAC.zip`: the 10 CD tracks in burn order, plus the
  extra Teddy Bears mix. Lossless, tagged, verified bit-exact against the source.
* `DrasticMeasures-NewSong-Stems-FLAC.zip`: all 23 session takes (L/R pairs joined
  into stereo, Baby Dolls repaired). Verified bit-exact.
* `BabyDolls-SD2-repaired.zip`: drop-in replacement data forks for
  `DrasticMeasures-NewSong Project/Audio Files/Baby Dolls.L` and `.R`, for use with
  the original Mac project. Keep the existing `._` resource-fork files.

`scripts/` contains the analysis and repair tools (Python 3 + NumPy), so the results
can be reproduced from the original RAR set.
