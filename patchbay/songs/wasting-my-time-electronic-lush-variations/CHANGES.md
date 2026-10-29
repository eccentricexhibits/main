# Wasting My Time (electronic, lush + variations)

**Listen:** https://claude.ai/artifact/X9bybUGwR1YfhSM7r9RLMj (Patchbay opens on it; private to you), or open `Patchbay.html` in this
folder offline.

You liked the background, but the reason for the classical search was the **lead melody**: the
same verse and chorus tune all the way through. This version makes the main melody develop as
the song goes on. Everything else (arrangement, drums, pads, the Mozart counter-melody
elsewhere) is the lush + Mozart version, which stays as it was.

## Verses: Bach's Chaconne, one variation per verse

**Why it fits.** Bach's Chaconne in D minor (from the Partita No. 2 for solo violin, BWV 1004)
is a set of variations over a four-bar bass that repeats throughout: D – C♯ – G/B♭ – A. That's
the verse's own bass, D – C – B♭ – A, in the same key. Bach writes a new melody over it each
time, which is exactly what the verses needed.

| Verse | Melody | What it's like |
|---|---|---|
| 1 (0:09) | the song's own tune, unchanged | establishes the song |
| 2 (0:31) | **the Chaconne's opening theme** (bars 1–8), led in by the run that closes its first half (bar 4) | the slow sarabande: "A · A E \| E · E F \| D · C B♭ \| A G F E…" |
| 3 (1:00) | **Bach's next variation** (bars 9–16) | the same harmony with more motion: dotted rhythms and quick turns |
| 4 (1:56) | **the variation after that** (bars 17–24) | higher and more intense, for the louder verse 4 |

**How it's fitted:**
- **Rhythm.** Each Chaconne bar fills one of the song's chords (half a bar). Its 3/4 therefore
  sits as **quarter-note triplets** over the song's 4/4: a floating rhythm, unlike the
  original tune. At the theme's density (3–4 notes a chord) it moves at about the original
  tune's pace.
- **Opening bar.** The verse's A7 bar carries Bach's A-bar run as a lead-in.
- **Last bar.** Bach's next bar is compressed into beats 1–3, so **the pickup into the
  pre-chorus is kept**.
- **One adjustment to Bach's notes:** his C♯ (D minor's leading tone) is played as C wherever
  it would rub against the song's C chord. That's the only change.
- **Same parts as before.** Verses 2 and 3 are on the verse lead, with its echo and vocal
  double. Each has a string-machine doubling an octave below: violas in verse 2, cellos in
  verse 3, as the old tune had. Verse 4 is on the hook lead with its detuned twins.

## Choruses: the hook, then a different Mozart answer each time

The hook ("Wasting all my time on you") opens every chorus. Its second phrase used to repeat it
exactly; now each chorus answers it differently, all from the same Mozart slow movement (K. 191)
as the counter-melody, at the same ii–V–I:

| Chorus | Second phrase (lead) | Counter-melody |
|---|---|---|
| 1 (0:25) | the hook again, unchanged | Mozart's theme, as before |
| 2 (0:46) | **Mozart's bassoon answer from bar 29**: G F E F \| D D C B♭, leading into the tag | Mozart's own violin line from the same bars |
| 3 (1:15) | **his florid violin passage from bar 39**: B♭ C B♭ A G… | the bassoon line beneath it |
| Final (2:11) | the variation you liked, unchanged | Mozart's theme, as before |

## Clearing the way

Where the melody changes, every part that doubled the old melody there is taken out, so the old
tune doesn't play against the new one:
- **Cleared outright:** the lead's echoes, detuned twins and vocal double, and the hook's
  harmony and octave stack in those chorus phrases.
- **Only the doubling notes, from the synth orchestra:**
  - the violas' and horns' copy of the verse 2 tune
  - the cellos' and bassoons' copy in verse 3
  - the violins, flutes and oboes in verse 4
  - the hook's parallel thirds and sixths in those chorus phrases

  The rest of each part, its accompaniment, stays.
- **Background notes trimmed:** 13. Each rubbed against the new melody, wasn't a tone of the
  chord there, and was a leftover of the old melody's harmony.

## Checks

- **Clashes:** in the changed passages, no new melody note rubs a semitone against anything,
  except:
  - the melody's B♭ against the A in B♭maj7 (the chord's own 7th)
  - Mozart's F suspended over the C7 before it falls to E
- **Verse melody over everything else:** V1 +2.1, V2 **+2.1**, V3 **+1.6 dB**, your settled
  balance. The Chaconne verses' accompaniment sits 0.9 / 1.6 dB further back to get there.
- **Unchanged elsewhere:** the render differs from lush + Mozart only at 0:30–0:41 (verse 2),
  0:49–0:53 (chorus 2), 1:00–1:10 (verse 3), 1:18–1:23 (chorus 3) and 1:56–2:06 (verse 4).
- **Loudness:** verses 2 and 3 are about 1 LU quieter than before, so the choruses land a
  little harder. The whole song is −12.9 LUFS.

## Files

- `Wasting My Time (electronic, lush + variations) (Patchbay preview).mp3`: the full song
- `Wasting My Time - verses 2-4, before and after.mp3`: verse 2, then verse 3, then verse 4.
  Each plays without the change, then 2 s of silence, then with it.
- `Wasting My Time - choruses 2-3, before and after.mp3`: the second phrase of choruses 2 and 3,
  the same way
- `Bach - Chaconne BWV 1004, opening (reference).mp3`: the Chaconne's opening as Bach wrote it,
  rendered through Patchbay
- The four MIDI files. Load them together.
- `variations.py`: builds this version on top of `../wasting-my-time-electronic-lush-mozart/mozart.py`.
  - The Mozart passages are written in as data.
  - `verse_spec()` and `bach()` place the Chaconne bars.
  - `DOUBLED_BY` lists what was cleared.
  - `EXTRA_REST` holds the verse balance.
- `chaconne-top-voice.json`: the Chaconne's top voice, bars 1–25. It's written by
  `extract_chaconne.py` from the Mutopia edition (typeset by Hajo Dezelski, CC BY-SA 3.0; Bach's
  music is public domain).

## Easy next tweaks

- **Chaconne in verse 1 too:** add a `melody('lead_v', bach(verse_spec(…, 7, …)), …)` line.
  That would make all four verses variations.
- **Other variations:** change the first-bar numbers in `verse_spec()`. Bars 25–36 (variations 7–9)
  are also in D minor. They're busier, and would need extending `chaconne-top-voice.json` past
  bar 25.
- **The pre-choruses still repeat the same melody.** Their chromatic harmony (G | B/F♯ | E♭m7 |
  D7) found no good classical match, but they could be varied by hand next.
