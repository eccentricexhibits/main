# Wasting My Time (electronic, lush)

**Listen:** https://claude.ai/artifact/C3DNm9dtLV7iqEBvThHXgZ (Patchbay opens on it; private to you)
or open `Patchbay.html` in this folder offline.

You asked for a version that's far more lush, with something like the number of layers in
the orchestral original. The electronic version stays as it was, at its own link
(https://claude.ai/artifact/PNuxKWNP47NispmTnLW8mt, `../wasting-my-time-electronic/`).

## What's different

The electronic version carries **3,839 of v18's 9,600 notes** (40%): the tune, the hook, and
the lines that suit synths. Whole parts of the orchestra were missing:
- piccolo, English horn, most of the oboes and clarinets
- the low reeds, horns 3·4, trombones and tuba
- timpani and the suspended-cymbal swells

This version keeps everything in the electronic one unchanged (leads, drums, bass, the
pickup and bridge fixes, the dynamics) and layers three things on top. It has **52 parts and
21,158 notes**, against 27 parts and 9,245 notes.

### 1. A synth orchestra: every v18 line is back

| Part | Sound | Plays v18's |
|---|---|---|
| String machine (violins I / II / violas / cellos) | Synth Strings 1 / 2 / 5 / 3 | the full string section |
| String machine (bridge solo, tremolo) | Synth Strings 1 | the bridge's solo violin and tremolo |
| Synth flutes | Synth Calliope | flutes and piccolo |
| Synth reeds | Square Lead 3 | oboes and English horn |
| Synth clarinets | Square Wave | clarinets |
| Synth low reeds | Pulse Bass | bass clarinet and bassoons |
| Synth horns | Synth Brass 4 | horns 1–4, velocity capped at 90 (mellow, as you like them) |
| Synth trumpets / trombones | Synth Brass 1 / 2 | trumpets; trombones and bass trombone |
| Synth contrabass | Synth Bass 2 | double basses, contrabassoon and tuba |
| Synth harp | Synth Chime | the harp: soft outside the bridge, full inside it |
| Synth timpani | 808 Tom | the timpani strokes (the rolls are left out: they machine-gun on a synth tom) |
| Cymbal swells | Orchestral kit | the suspended-cymbal rolls and triangle |

### 2. Width: detuned twins

- **Hook lead (detuned left / right):** two extra copies of the hook lead, tuned about 10
  cents flat and sharp and panned hard left and right. This is the "ensemble" that makes a
  synth lead sound wide.
- **Pad ensemble (left / right):** the same trick on every pad chord, about 12 cents either
  way.

### 3. Air

- **Halo pad:** a high pad on the chords through the whole song.
- **Choir pad (oohs):** in the choruses, tags, verse 4, the ending, and the bridge from its
  second statement.
- **Verse tune (vocal double):** a soft vocal-like unison on the verse tune.
- **Shimmer arp:** 16th notes up through the chord in the choruses, the bridge climax and
  the ending, with a dotted-8th echo on the other side.

## Checks

- **Verse tune over the rest:** V1 **+2.1**, V2 **+2.1**, V3 **+1.6 dB**.
  - Your v18 values are +2.2 / +2.2 / +1.6.
  - Here "melody" includes the tune's own layers: the cellos (violas in verse 2) on the
    string machine, the bassoons in verse 3, and the vocal double.
  - To get there, those layers play louder in their verse, and the new accompaniment layers
    sit 1.5 dB back in the verses only. The choruses keep their full weight.
- **Fuller everywhere, same shape:**
  - Every section is 2–4 LU fuller than the electronic version.
  - The choruses are still about 4.8 LU over the verses.
  - The bridge climbs from −16.2 to −11.0. Bar 63 is a 0.9 LU dip, as in the other versions.
  - The ending gets louder every bar (−11.9 → −8.9) into the hit.
- **Whole song:** −13.0 LUFS (the electronic version is −15.0). Peak −0.2 dBFS: the export
  scales the file down slightly to stay under its 0.98 ceiling.
- **Low end not muddier:**
  - Relative to the whole mix, the sub band is lower than in the electronic version.
  - The 500 Hz–1 kHz body is about 4 dB stronger in the choruses, which moves it toward
    v18's balance.
- **Every part loaded its intended sound.**

## Files

- `Wasting My Time (electronic, lush) (Patchbay preview).mp3`: the full song
- Comparison clips, each playing the electronic version, then 2 s of silence, then the lush
  version:
  - `Wasting My Time - electronic vs lush, verse 1 to chorus 1 (0m09-0m31).mp3`
  - `Wasting My Time - electronic vs lush, bridge (1m30-1m53).mp3`
  - `Wasting My Time - electronic vs lush, ending (2m38-2m52).mp3`
- The four MIDI files. Load them together:
  - `…_part1_synths.mid`
  - `…_part2_drums_bass_fx.mid`
  - `…_part3_synth_orchestra.mid`
  - `…_part4_layers.mid`
- `lush.py`: builds all four files.
  - It runs `../wasting-my-time-electronic/electronic.py` first, then adds the layers. A fix
    to the electronic version carries over here on the next build.
  - The tables near the top set each layer's sound and level: `ORCH` (the synth orchestra),
    `LAYERS` (the detuned twins and vocal double), the halo/choir/arp settings, and `trim()`
    for the verse balance.
- `lush-parts.json`: note count per part.

## Easy next tweaks

- **Too much of a layer:** turn its row down in Patchbay, or change its CC7 in `ORCH` /
  `LAYERS`.
- **Less shimmer:** lower the `shimmer(...)` velocities, or remove the bridge call.
- **Wider or narrower:** change the detune amounts (410 ≈ 10 cents) and the pans in `LAYERS`.
