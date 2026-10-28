# Wasting My Time (electronic): an electronic arrangement of v18

**Listen:** https://claude.ai/artifact/PNuxKWNP47NispmTnLW8mt (Patchbay opens on it; private to you)
or open `Patchbay.html` in this folder offline.

This is a new arrangement, not a v19. It's built from the approved **v18**:
- **Unchanged from v18:** the melody, the chorus hook ("Wasting all my time on you"), the
  harmony, the form, the 156 BPM tempo, the accelerating ending (156→228 BPM) and the cold hit
  on D.
- **New:** the instruments, and everything underneath the tune.

It stays **melancholic but anthemic**. The verses are half-time and spacious, the choruses
drop into a driving two-step beat, and the bridge is a lush pad wall.

## Revision 3: the figure at 0:07 back on the lead, and a fuller bridge opening

**0:07, the interlude's descending figure** (bar 6: A5 F5 C5 A4 over F5 C5 A4 F4):
- In v18 the whole orchestra plays it in octaves, led by the oboes and clarinets.
- In the first version it went to the pluck and bells, which are backing parts.
- It's now on the hook lead (the oboe line, with its echo) and the harmony lead (the
  clarinet line).
- The same figure after the bridge (1:53) was already on the lead, because violins I play it
  there.

**1:29–1:31, the bridge's first bar** had little more than the sub bass, plus a pad wall that
swells in too slowly to be heard yet (about −37 dB). Three things fill it now:
- **A reverse-cymbal swell** into the bridge's downbeat (from 1:28).
- **A warm pad** on the bridge chords (Am7, B♭add9 over A, Gm7add11, C9) for its first three
  bars. It fades (112 → 98 → 80) as the wall arrives.
- **The harp's sweeps** on the pluck for those bars, where they were faint on the bells.

Nothing new is brass or drums, so the bridge stays pad- and string-centred.

**Checks:**
- **Bridge opening:** −20.4 → −19.3 LUFS, and it still builds (−16.4, −14.6, −12.6 over the
  next statements). Bar by bar it now climbs from the first bar.
- **Interlude:** −15.6 → −14.5 LUFS, because the figure is on a lead now.
- **Unchanged elsewhere:** the render differs from revision 2 only at 0:07–0:10 and
  1:27–1:37.
- **Whole song:** −15.0 LUFS.

**Clip:** `Wasting My Time (electronic) - interlude figure and bridge opening, before and
after (0m05-0m11, 1m26-1m35).mp3`. The "v18 vs electronic, bridge" clip is updated too.

## Revision 2: the pickups into the pre-choruses

You noticed missing notes in the melody at 0:17 and 0:40. Two short phrases that lead into
each pre-chorus start in the last bar of the verse, and the routing only took the verse tune
from that bar, so it dropped them:
- **Violins I's A4 on beat 4:** the pre-chorus melody's first note, held into the next bar.
  It's now on the hook lead, with its echo, at the end of verses 1–3 (0:17, 0:40, 1:09).
- **The oboes' "F . F" answer on beats 2–2½:** before pre-choruses 1 and 2. It's now on the
  counter lead.
- **Verse 4's pickup (2:05):** it was being cut to one beat at the section line, against its
  full two in v18. Lead notes now ring across a section boundary; only held tails longer than
  a bar are still cut (the one at 0:31 would drone on a synth).

An audit of every v18 line found no other dropped melody notes. What the routing leaves out on
purpose:
- doublings of lines the leads already play
- the orchestral bass and percussion
- held chord tones the pads cover

**Checks:**
- **Unchanged elsewhere:** the render differs from the previous one only at 0:17–0:20,
  0:38–0:41, 1:08–1:10 and 2:05–2:07.
- **Verse balance:** V1 +2.1, V2 +1.8, V3 +1.6 dB. The verses themselves are unchanged. The
  small drop for V1 and V2 is the new pickup falling inside the verse's measuring window.
- **Whole song:** −15.1 LUFS.

**Clip:** `Wasting My Time (electronic) - pre-chorus pickups, before and after (0m13-0m22,
0m35-0m44).mp3` plays 0:13–0:22 before and after, then 0:35–0:44 before and after.

## How it was made

`electronic.py` reads v18's MIDI and rebuilds it in four steps:

1. **Re-voicing (the `ROUTES` table).** Each orchestral line is sent, section by section, to
   the synth that suits its job. For example, Violin I carries the hook in the choruses, so it
   goes to the saw lead there. In the intro it plays the opening figure, so it goes to the
   pluck.
2. **New parts from the chord chart (`CHART`).** Drums, sub bass, saw bass, pads, stabs,
   risers and reverse cymbals are generated so they follow the song's real chords. The chart
   was read off v18 bar by bar.
3. **Production moves.** These are the things that make it sound electronic:
   - "Sidechain" pumping: pads and bass duck at every kick
   - a 16th-note trance gate on the tremolo strings
   - dotted-8th echoes on the leads
   - noise risers with a pitch sweep, and 808 booms on the big downbeats
4. **Dropped from v18:** its orchestral bass, timpani and percussion. Their jobs are done by
   the new drums and bass.

## The instruments (all from the built-in GeneralUser GS bank)

| Part | Sound | Plays |
|---|---|---|
| Lead (verse tune) | Chiffer Lead | The verse tune in verses 1–3 (cellos / violas / cellos in v18) |
| Lead (hook) | Saw Lead | The chorus hook, pre-choruses, verse 4, bridge hook, ending figure |
| Lead (harmony) | Saw Wave | The line a third or an octave below the hook (Violin II in v18) |
| Saw stack (octave) | Bright Saw Stack | The flutes' octave doubling in the choruses; Violin I in the ending |
| Lead echo / Verse lead echo | same as their lead | Dotted-8th repeats, panned to the sides |
| Counter lead | Square Lead 2 | Verse 2 counter-line (bassoons), bridge countermelody (solo violin), outro flute |
| Pad (warm) | Warm Pad | Chords in the intro, verses, pre-choruses, breaks and outro |
| Pad (pumping) | Synth Strings 4 | Chords in the choruses, tags, verse 4 and ending, ducking at every kick |
| Pad (bridge wall) | Solar Wind | v18's string pad in the bridge |
| Synth strings | Synth Strings 3 | Bridge violas and cellos |
| Gated pad | Polysynth | v18's tremolo strings, chopped into a 16th-note trance gate |
| Pluck | Synth Mallet | Violin II / viola figures, intro and outro melody, bridge pizzicato, ending harp sweeps |
| Bells | Crystal | Glockenspiel, tubular bells, flute sparkle, bridge harp |
| E-piano | Chorused Tine EP | Harp in the verses and choruses (soft); bridge piano parts |
| Synth brass | Synth Brass 3 | Horns. Mellow: velocity capped at 90–92 |
| Stab | Sawtooth Stab | Trumpet stabs, plus a chord stab on each chorus downbeat and the hit |
| Choir pad | Space Voice | The choir at the bridge climax and in the ending |
| Sub bass / Saw bass | Sine Wave / Mean Saw Bass | Chord roots. The saw bass rhythm follows the drums |
| Kick, Snare · Clap, Hats · Shaker, Crash · Ride | 808/909 kit | Four rows, so each has its own fader |
| Riser, Reverse cymbal, 808 boom | White Noise Wave / Reverse Cymbal / 808 Tom | Into each chorus, the bridge statements and the ending |

Any of these can be swapped in Patchbay's instrument browser without touching the MIDI.

## Section by section

| Time | Section | What happens |
|---|---|---|
| 0:00 | Intro | The opening figure on the pluck with echoes, a warm pad, a heartbeat kick from 0:03 and a noise riser into… |
| 0:06 | Interlude | the first downbeat: crash, boom, half-time beat |
| 0:09 / 0:31 / 1:00 | Verses 1–3 | Half-time beat (kick on 1, clap on 3), sub + syncopated saw bass. The tune is on the soft lead with a quiet echo, and Violin II's broken chords are on the pluck. Verse 2's off-beat chords are short stabs. Its bassoon counter-line is on the counter lead. |
| 0:18 / 0:40 / 1:09 | Pre-choruses | The beat thickens bar by bar: half-time, then two-step, then a snare roll (16ths to 32nds) with a riser and reverse cymbal |
| 0:25 / 0:46 / 1:15 | Choruses 1–3 | **The drop.** Two-step beat, crash and boom, chord stab, pumping pad, driving 8th-note bass. The hook is on the saw lead with its harmony and octave stack, the violas' chords on the pluck, horns on synth brass. |
| 0:52 / 1:21 | Tags | Two-step beat, then a stomp on every beat in the last bar |
| 0:57 / 1:26 | Breaks | Drums drop to hats and fade. The ending's "F . . G" cell echoes over a D minor pad. |
| 1:30–1:53 | Bridge | Still pad- and string-centred, with no brass and deep reverb: the solar-wind pad wall, synth strings, the trance-gated pad, the hook and its countermelody. Drums enter in stages: nothing, then a kick and rim, then half-time, then two-step, then a roll. Booms and reverse cymbals mark each statement. Choir and e-piano join at the climax (1:48). |
| 1:53 | Interlude | Release after the bridge: crash, two-step |
| 1:56 | Verse 4 | The tune on the hook lead (higher energy, as in v18), two-step beat |
| 2:11 | Final chorus | As the choruses, with a ride cymbal and the bell on the final F |
| 2:28 | Outro | The opening figure on the pluck again, half-time, then a build |
| 2:38 | Ending | The five accelerating repeats: two-step, then four on the floor with off-beat bass, then snare 16ths into 32nds and a long riser. It gets louder every bar (−14.2 → −10.5 LUFS). |
| 2:49 | Hit | The cold hit on D: kick, clap, crash, boom, sub, stab |

## Checks

- **Verse tune over the rest** (mix minus the tune soloed): V1 **+2.3**, V2 **+2.1**, V3
  **+1.6 dB** (first version; see revision 2). Your v18 values are +2.2 / +2.2 / +1.6.
  - The tune is played at G4–A4 in all three verses. In v18, verses 1 and 2 had it an octave
    lower, among the accompaniment. On a lead synth it needs its own register to come through.
- **Drop:** the choruses are about 4 LU louder than the verses.
  - Verse 1 −18.5, chorus 1 −14.1 LUFS.
  - The bridge builds steadily from −25 to −12.
- **Whole song:** −15.1 LUFS, loudness range 7.2 LU, peak −1.2 dBFS. v18 is −14.6 LUFS with a
  14.6 LU range. A smaller range is normal for electronic music.
- **Every part loaded its intended sound.** That includes the GS variation banks, such as
  Saw Lead and Mean Saw Bass on bank 12. Nothing fell back to a default.
- **Chords:** the generated pads and bass were checked for semitone clashes against the song's
  own lines. The ones that remain come from the song itself: the tune's A over B♭maj7, and the
  bridge's B♭ chords over a held A bass, both as in v18.

## Files

- `Wasting My Time (electronic) (Patchbay preview).mp3`: the full song, exported from Patchbay
- Before/after clips, each playing v18, then 2 s of silence, then the electronic version:
  - `Wasting My Time - v18 vs electronic, verse 1 to chorus 1 (0m09-0m31).mp3`
  - `Wasting My Time - v18 vs electronic, bridge (1m30-1m53).mp3`
  - `Wasting My Time - v18 vs electronic, ending (2m38-2m52).mp3`
- `Wasting_My_Time_electronic_part1_synths.mid` (16 synth parts) and
  `…_part2_drums_bass_fx.mid` (drums on channel 10, bass, FX). Load both together.
- `electronic.py`: rebuilds both files from v18. Every choice is a named table near the top:
  - `ROLES`: sound, volume, pan and reverb per part
  - `ROUTES`: which v18 line goes where
  - `CHART`: the chords
  - drum patterns per section, `level()` and `trim()` for dynamics, `VERSE_REST` for the
    verse balance, `PUMP` for sidechain depth
- `electronic-parts.json`: note count per part

## Easy next tweaks

- **A different lead sound:** change `ROLES['lead']`. Candidates measured at the same
  settings:

  | Sound | Level |
  |---|---|
  | Square Lead | −21.4 dB |
  | Saw Lead | −23.0 dB |
  | Bright Saw Stack | −24.5 dB |
  | Saw Lead 2 | −26.2 dB |

  A quieter sound needs its volume raised to match.
- **Pumping depth:** `PUMP` (0 = none).
- **Drum feel:** the `drum_bar` styles: `half`, `two`, `four`.
- **Richer sounds:** see `../../electronic-instruments.md`, which maps free plugins onto each
  part above.
