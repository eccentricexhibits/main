# Wasting My Time (electronic, lush + Mozart)

**Listen:** https://claude.ai/artifact/2D458a9rDDDmeqAZ9HVE6j (Patchbay opens on it; private to you),
or open `Patchbay.html` in this folder offline.

This is the lush version with one addition: a **counter-melody from Mozart** in every chorus.
The lush and electronic versions stay as they were.

## Why this piece

You felt the song is melodically a bit simple, and asked for a piece from Bach, Mozart or
Beethoven that fits its chords and key, not something slapped on. So the choice was made by
searching, not by picking a famous tune:

- **What was searched:** all 1,592 MIDI files you supplied: 1,127 Bach, 265 Beethoven and
  200 Mozart.
- **How:** each piece was reduced to its harmony beat by beat. The song's verse, chorus and
  bridge progressions were slid along it in all 12 keys, scoring how well the notes fit each
  chord and whether the bass matches.
- **Then filtered for:**
  - passages that work at their **written tempo**, with chords changing at the song's pace
  - **duple meter**, like the song
  - **themes**, the tune a movement opens with, rather than fragments from deep in a
    development section
- The scripts are in `../../tools/quote-search/`.

**The winner, with a clear lead, is the opening theme of the slow movement (Andante ma
adagio) of Mozart's Bassoon Concerto in B-flat, K. 191 (1774):**

- **Same key.** It's in F major, so it needs no transposition.
- **Same chords.** Its bass moves G – C – F – A – B♭ – C – F: ii – V – I – I⁶ – IV – V – I.
  That's the chorus's Gm7 C7 | F | Gm7 C7 | F.
- **Same pace.** One of Mozart's beats per song chord is within 3% of his written tempo, and
  the phrase fills one 4-bar chorus exactly.
- **The right mood.** The melody is a chain of falling "sighs": F–E, B♭–A, A–G–F, E–F. That's
  melancholic and lyrical, not bright. Mozart thought enough of it to rework it as the
  Countess's lament "Porgi, amor" in *The Marriage of Figaro*.
- **It complements the hook.** It moves while the hook holds its long G and A, so the two
  lines answer each other instead of competing.

## What was done

- **Choruses 1–3 (0:25, 0:46, 1:15):**
  - The phrase plays an octave below written pitch, at E3–G4.
  - That makes it a warm tenor counter-melody **under** the hook, not a bright line above it,
    which you'd rejected early in the song.
  - The hook ("Wasting all my time on you") is unchanged.
- **Final chorus (2:11):**
  - The phrase plays at written pitch, E4–G5. The hook is an octave higher there, so the
    counter-melody rises with it.
  - Its last two bars repeat the phrase's cadence (A–G–F–E–F), the way Mozart often echoes a
    cadence.
- **One arranger's adjustment.** In Mozart the first sigh's E lands on a half-beat, which in
  the song would rub against the Gm7's F. It's moved to arrive exactly on the C7, the one
  change to his notes. His grace notes are kept.
- **Its own part:** "Mozart counter-melody (K. 191)", on Square Lead 2, the same voice as the
  song's other counter-lines, so its level can be adjusted in Patchbay.

## Checks

- **The two dissonances that remain** are Mozart's own, and each resolves within a beat as it
  does in his score:
  - the B♭ leaning onto A on the F chord (an appoggiatura)
  - the F hanging over the change to C7 before falling to E (a 4–3 suspension)
- **Level:** the counter-melody is **3.7 dB under the hook** in chorus 1. The hook stays the
  main melody; Mozart is clearly heard beneath it.
- **Unchanged elsewhere:** everything outside the choruses renders the same as the lush
  version (the render differs only at 0:24–0:31, 0:46–0:52, 1:15–1:22 and 2:11–2:21).
- **Loudness:** the choruses are 0.3–0.5 LU fuller. The whole song is −12.9 LUFS (lush −13.0).

## Runners-up from the search

In case you'd like to try another:

| Piece | Fits | Notes |
|---|---|---|
| **Bach, Chaconne from Partita No. 2 in D minor, BWV 1004** | Verse | Best harmonic match for the verse, in the same key. Its variations ride the same falling bass, D–C–B♭–A. But it moves one chord per slow 3/4 bar, so fitting the verse would mean playing it about 3× faster. Better suited to a new, slower section than to a counter-melody. |
| **Bach, Sinfonia No. 4 in D minor, BWV 790** | Chorus | Also in the key at its written tempo, but the fitting stretch is only a 2-bar cadence figure, not a theme. |
| **Bach, "Sheep May Safely Graze," BWV 208** | Verse (Dm C B♭maj7 A7 Dm C) | Fits half the verse at its written tempo; it needs transposing. |
| **Mozart, Eine kleine Nachtmusik, K. 525, 1st mvt** | Chorus | Fits well, but bright and cheerful, against the mood you want. |

## Files

- `Wasting My Time (electronic, lush + Mozart) (Patchbay preview).mp3`: the full song
- `Mozart - Bassoon Concerto K. 191, 2nd mvt, opening (reference).mp3`: Mozart's original
  opening, rendered through Patchbay, so you can hear where the line comes from
- `Wasting My Time - lush vs lush + Mozart, chorus 1 (0m23-0m31).mp3` and
  `…, final chorus (2m10-2m21).mp3`: each plays the passage without Mozart, then 2 s of
  silence, then with
- The four MIDI files. Load them together.
- `mozart.py`:
  - Builds the version: it runs the lush version's builder, then adds the counter-melody.
  - Mozart's phrase is written into the script as data, with its source: violins I, bars 1–3,
    from the Mutopia Project edition typeset by Liang Seng, which is public domain.
  - `place(...)` sets where it plays and in which octave.
