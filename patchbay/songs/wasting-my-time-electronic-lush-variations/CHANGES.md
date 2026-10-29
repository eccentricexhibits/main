# Wasting My Time (electronic, lush + variations), revision 2

**Listen:** https://claude.ai/artifact/X9bybUGwR1YfhSM7r9RLMj (Patchbay opens on it; private to
you), or open `Patchbay.html` in this folder offline.

The aim is a main melody that isn't the same verse and chorus tune all the way through, using
passages from the classical search that fit the song's chords. Everything else is the
lush + Mozart version, which stays as it was.

## What went wrong in revision 1

You found revision 1 incoherent, with far too many notes. Both were real, and both came from how
the material was fitted:

- **Too fast.** The Chaconne changes chord about every 2.5 s; the verse changes every 0.77 s. To
  fit, each Chaconne bar was squeezed into one of the song's chords: about **three times Bach's
  speed**. The search had flagged this mismatch for the Chaconne.
- **Too busy.** Verses 3 and 4 used Bach's busier variations, so the melody ran 12–14 notes a
  bar, with his quick turns shrunk to 40-millisecond blips.
- **Wrong rhythm.** Squeezing 3/4 into the song's 4/4 put the melody in triplets against the
  straight beat.
- **Not one line.** The "melody" was the top note of Bach's violin chords at each moment, which
  hops between his voices instead of following one line.

Revision 1 is in the git history.

## Revision 2: less material, at the song's pace

The rules this time:
- no more notes than about the original tune's (≈ 5 a bar)
- straight quarters and eighths
- one singable line, written out note by note

| Section | Main melody |
|---|---|
| Verse 1 (0:09) | your tune |
| **Verse 2 (0:31)** | **the Chaconne's opening theme**: A A E \| E E F \| D C B♭ \| A G F E, then again climbing to B♭, resolving E→F→D before the pre-chorus |
| Verse 3 (1:00) | your tune (as before) |
| Verse 4 (1:56) | your tune with v18's "C B♭ A" variation (as before) |
| Chorus 1 (0:25) | the hook twice (as before) |
| **Chorus 2 (0:46)** | the hook, then **Mozart's bassoon answer** (K. 191, bar 29): G F E F \| D D C B♭, leading into the tag. The counter-melody takes Mozart's violin line from the same bars. |
| **Chorus 3 (1:15)** | the hook, then **Mozart's sighing cadence** A–G–F–E–F, the end of the counter-melody's theme. The lead sings it an octave above the counter-melody. |
| Final chorus (2:11) | the variation you liked (as before) |

**How the Chaconne theme is fitted.** Each Bach bar fills one of the song's chords as quarter,
eighth, eighth: his long first note, the re-struck note, then beat 3. That keeps his notes in
order at the original tune's pace. His 16th-note cadence runs (bars 4 and 8) become four
eighths. Its bass (D–C♯–G/B♭–A) is the verse's own (D–C–B♭–A). The theme starts on the verse's
second bar, after a calm lead-in over the A7 (E · · D C♯).

**Kept from revision 1:**
- **Doublings cleared:** where the melody changes, the background parts that doubled the old
  melody (echoes, detuned twins, vocal double, and the synth-orchestra notes moving with it) are
  taken out.
- **Background notes trimmed:** a few non-chord background notes that rubbed against the new
  line.

## Checks

- **Density:** verse 2 has 5.2 notes a bar (verse 1's tune has 4.2); the chorus answers 4–6.
  The shortest notes are eighths. Revision 1 had 12–14 a bar, with notes as short as 1/32.
- **Clashes:** none in the changed passages, except Mozart's own F suspended over the C7 before
  it falls to E.
- **Verse 2 melody over everything else:** **+2.3 dB**, your verse balance. The lighter line
  needed no extra room, so revision 1's accompaniment trim is gone.
- **Unchanged elsewhere:** the render differs from lush + Mozart only at 0:30–0:41 (verse 2),
  0:49–0:53 (chorus 2) and 1:18–1:23 (chorus 3).
- **Whole song:** −12.9 LUFS.

## Files

- `Wasting My Time (electronic, lush + variations) (Patchbay preview).mp3`: the full song
- `Wasting My Time - verse 2, before and after (0m31-0m40).mp3`: verse 2 with your tune, then 2 s
  of silence, then with the Chaconne theme
- `Wasting My Time - choruses 2 and 3, before and after.mp3`: chorus 2, then chorus 3, each
  before and after
- `Bach - Chaconne BWV 1004, opening (reference).mp3`: the Chaconne's opening as Bach wrote it,
  rendered through Patchbay
- The four MIDI files. Load them together.
- `variations.py`: builds this version on top of `../wasting-my-time-electronic-lush-mozart/mozart.py`.
  - `THEME` is the verse-2 melody, note by note.
  - The Mozart passages are written in as data, from the Mutopia editions: Chaconne typeset by
    Hajo Dezelski (CC BY-SA 3.0), K. 191 by Liang Seng (public domain).

## If you'd like to go further

These are only worth trying if verse 2 and choruses 2 and 3 work for you:
- **Verse 3:** a second Chaconne passage there, kept to the same pace.
- **Pre-choruses:** varied by hand; they still repeat.
