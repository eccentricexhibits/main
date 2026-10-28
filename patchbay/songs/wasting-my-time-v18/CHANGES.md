# Wasting My Time (v18): verses 1 and 2 a little louder

v18 is v17 with the melody in verses 1 and 2 raised by about 0.5 dB. Verse 3 and
everything after it render exactly the same as v17.

| Verse | Tune | Expression, v17 | **v18** | Tune vs. the rest, v17 | **v18** |
|---|---|---|---|---|---|
| 1 (0:09–0:18) | cellos, G3–A3 | ×1.145 | **×1.18** | 1.5 dB over | **2.2 dB over** |
| 2 (0:31–0:40) | violas + horns 1·2, G3–A3 | ×1.22 / ×1.10 | **×1.257 / ×1.133** | 1.6 dB over | **2.2 dB over** |
| 3 (1:00–1:09) | cellos G4–A4 + bassoons G3–A3 | ×1.22 / ×1.18 | (unchanged) | 1.6 dB over | 1.6 dB over |

Verse 2 now sits between v16 (1.6 dB over, which you approved) and v14 (2.8 dB
over, a touch too loud).

## Why verse 3 needs less

It isn't louder:
- **Plain energy:** in v17 all three verses measured within 0.1 dB of each
  other.
- **Loudness weighting:** this measure (K-weighting, the standard used for
  loudness) gives more weight to higher notes. On it, verse 3 was actually the
  lowest: 1.5 dB over the rest, against 2.2 and 1.9.

The difference is **register**:
- **Verse 3:** the cellos play the tune an octave higher, at G4–A4, in a range
  of their own. The violas' 16ths are below it, the violin chords are above, and
  the bassoons double it an octave lower.
- **Verses 1 and 2:** the tune is at G3–A3, right in among the accompaniment.
  In verse 1 that's the violas' chords and the second violins' broken chords. In
  verse 2 it's the bassoons' counter-line and the harp. So it needs a little more
  level to come through as clearly.

## Checks

- **Harsh clashes:** 334.
- **Whole song:** −14.6 LUFS.

## Files

- `Wasting My Time - verses 1 and 2 v17 vs v18 (0m08-0m41).mp3`: verse 1, the
  pre-chorus, chorus 1 and verse 2, first as v17, then as v18 (0:00 v17, 0:35
  v18)
- `Wasting My Time v18 - verses 1-3 (0m08-1m11).mp3`: all three verses in a row
  in v18
- `Wasting My Time v18 (Patchbay preview).mp3`: the full song
- `… (v18).mid`: the two MIDI files
- `revise_v18.py`: builds v18 from the originals. The verse balance is in the
  `VERSES` table.
