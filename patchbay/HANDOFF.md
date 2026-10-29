# Patchbay MIDI Studio — project handoff

Upload this whole folder (or the zip) to a new Claude conversation and paste the
"Starter prompt" at the bottom. Everything the next session needs is here.

---

## Start here: where things stand

**The user is happy with Wasting My Time v18.** It's the approved version. Treat
it as the base for any further song work; don't redo it.

**Newest (2026-10-29): lush + variations, revision 2.**
- **Live:** https://claude.ai/artifact/X9bybUGwR1YfhSM7r9RLMj
- **Folder:** `songs/wasting-my-time-electronic-lush-variations/`
- **Revision 1 was rejected** ("awful, incoherent, an absurd amount of notes"). It had put
  Chaconne variations in verses 2–4 at about 3× Bach's speed, in triplets, 12–14 notes a bar,
  using the top note of his violin chords as the melody.
- **Revision 2** keeps new material to the original tune's pace and rhythm:
  - verse 2: the Chaconne's opening theme, reduced by hand to straight quarters and eighths,
    about 5 notes a bar
  - choruses 2 and 3: two short Mozart K. 191 answers after the hook
  - verses 1, 3 and 4, chorus 1 and the final chorus: unchanged
- **Verse 2 balance:** +2.3 dB.
- **Waiting on:** the user's verdict.
- **Lesson for further melodic work:** the user is sensitive to busy or incoherent lines. Stay
  at or below the original tune's note density, in straight rhythm, and never speed source
  material up to fit the harmony.

**Before that (2026-10-29): lush + Mozart.**
- **Live:** https://claude.ai/artifact/2D458a9rDDDmeqAZ9HVE6j
- **Folder:** `songs/wasting-my-time-electronic-lush-mozart/`, built by `mozart.py` on top of
  `lush.py`.
- **The request:** the user felt the melody was too simple and asked for a Bach, Mozart or
  Beethoven piece that fits the song's chords and key.
- **The search:** 1,592 MIDI files (`tools/quote-search/`).
  - It picked the opening theme of Mozart's Bassoon Concerto K. 191, 2nd mvt: F major,
    ii–V–I, at its written tempo.
  - It's now a counter-melody in every chorus: under the hook an octave down in choruses 1–3,
    at written pitch in the final chorus.
- **Runners-up** are in that folder's `CHANGES.md`. The Bach Chaconne (BWV 1004) fits the
  verse but is far slower.
- **The source MIDI collections are not in the repo.** The phrase is embedded in `mozart.py`.

**Also (2026-10-28): a lush electronic version.**
- **Live:** https://claude.ai/artifact/C3DNm9dtLV7iqEBvThHXgZ
- **Folder:** `songs/wasting-my-time-electronic-lush/`, built by `lush.py` on top of
  `electronic.py`.
- **What it is:** the electronic version plus all of v18's lines on a synth orchestra,
  detuned ensemble twins, halo/choir pads and a shimmer arp. 52 parts, 21k notes.
- **Checks:**
  - verse tune over the rest: +2.1 / +2.1 / +1.6 dB
  - −13.0 LUFS overall
- **The user asked to keep the electronic version too.** Both are live.

**Also (2026-10-28): an electronic arrangement of v18.**
- **Live:** https://claude.ai/artifact/PNuxKWNP47NispmTnLW8mt (private to the user)
- **Folder:** `songs/wasting-my-time-electronic/`. Read its `CHANGES.md`; it's rebuilt from v18
  by `electronic.py`.
- **What it is:** the same melody, hook, harmony, form, tempo map and cold hit, on 27 synth
  and drum parts from GeneralUser GS:
  - leads, pads, a pluck and bells
  - 808/909 drums: half-time verses, two-step choruses, four on the floor in the ending
  - sub and saw bass, sidechain pumping, a trance gate, echoes and risers
- **Checks:**
  - verse tune over the rest: V1 +2.3, V2 +2.1, V3 +1.6 dB
  - choruses about 4 LU over the verses
  - −15.1 LUFS overall
- **Revision 2:** the user heard missing melody notes at 0:17 and 0:40. These were the
  pickups into each pre-chorus (violins I's A4, the oboes' "F . F"), dropped at the
  verse/pre-chorus boundary. Now routed.
- **Revision 3:**
  - bar 6's descending figure (0:07) moved from the pluck and bells to the leads
  - the bridge's first bar (1:29) filled: a reverse cymbal, a fading warm pad, and the harp on
    the pluck
- **Waiting on:** the user's next listen.
- **Plugins:** `electronic-instruments.md` lists free VST3s, effects and CC0 SoundFonts that
  would enrich it, mapped part by part, with a starter pack.

| | |
|---|---|
| **v18, live** | https://claude.ai/artifact/LtQ9Az47zEMnkAc4zoNZib (Patchbay opens on the song; private to the user) |
| **v18 files** | `songs/wasting-my-time-v18/`: the two MIDI files, `CHANGES.md`, full preview MP3, `revise_v18.py`, and `Patchbay.html` for offline use |
| **The app** | https://claude.ai/artifact/RmKv4ph63HoFihzA3wSfeg (browser edition; opens on a demo song) |
| **Offline app** | `Patchbay-local/` (the user also has `Patchbay-local.zip` with the SoundFont) |
| **Tools** | `tools/`: render, measure and check scripts, plus the step-by-step revision recipe (`tools/README.md`) |
| **Open item** | the **Windows VST3 edition** (section 5). It's blocked on one question: is there a GitHub repo for it, or should one be created? |

### v18 at a glance (2:53, F major, 156 BPM)

| Time | Section | What's there |
|---|---|---|
| 0:00 | Intro, interlude | as the original |
| 0:09 / 0:31 / 1:00 | Verses 1–3 | Verse tune on cellos (V1), violas + horns 1·2 (V2), cellos up an octave + bassoons (V3). Lifted over a lighter accompaniment. Harp softer than the original. |
| 0:18 / 0:40 / 1:09 | Pre-choruses | as in v3 |
| 0:25 / 0:46 / 1:15 | Choruses 1–3 | The original vocal hook "Bb A Bb C \| G \| A" ("Wasting all my time on you", twice), kept on purpose. The answering phrases were made more melancholic in v3. Flute 2 plays in thirds in choruses 1 and 3. |
| 1:30–1:53 | Bridge (bars 59–70) | A lush string orchestra built on six statements of the chorus hook (no winds or brass), with deep reverb, harp sweeps, and timpani/cymbal swells. Piano doubles the tune from 1:35. A soft choir and a quiet rolling piano come in only at the climax (1:48–1:53). |
| 1:56 | Verse 4 | "C Bb A" line (from v3) |
| 2:11 | Final chorus | varied ending of the hook (G→A, D→C, D–E→F) with a tubular bell on the final F |
| 2:28 | Outro | as the original |
| 2:38 | Ending | The closing figure (F . . G \| G G over a D pedal) builds for 3 bars, then repeats 5 more times. It accelerates 156→228 BPM, gets louder, and gathers instruments: harp + bell, glockenspiel + tremolo strings, choir + piano, then snare/bass drum/cymbal drive and a timpani roll. Then the original **cold hit** on D at 2:49. |

### The user's preferences, learned over 18 revisions (keep them)

- **Mood:** melancholic but anthemic. Bright, "happy" high motifs early in the
  song were rejected.
- **Choruses 1–3:** keep the original vocal line. The final-chorus variation
  is liked.
- **Horns:** mellow, never honking. Velocity is capped at 100 and the channel
  volume is 90.
- **Bridge:** string-centred and lush. History of what was rejected:
  - harpsichord too loud
  - two "theme" bridges with no distinctive melody
  - a literal Deep Note swell
- **Piano:** used only as colour. The rolling piano is quiet and only at the
  end of the bridge. The user thought they heard piano outside the bridge; it
  was the harp, now softened.
- **Ending:** must build continuously, with no step back and no dips. Five
  repeats, not eight. New instruments join as it speeds up. The hit is
  unchanged.
- **Verse tune** (melody minus everything else, RMS, measured with
  `tools/verse_balance.js`):
  - V1 +2.2, V2 +2.2, V3 +1.6 dB.
  - V3 needs less because its tune sits in its own register.
  - The user notices about 0.5 dB, so adjust in small steps.
- **Working style:**
  - The user listens to MP3s and gives precise notes with timestamps.
  - Send a before/after comparison clip with every change.
  - Change only what was asked, and confirm by measurement that the rest
    renders identically.

---

## 0. Wasting My Time (the user's song, included)

| | |
|---|---|
| **Play it now** | https://claude.ai/artifact/UPqVJY673QQMX9UJn3K76e: Patchbay opens directly on the song (private to the user) |
| **Offline** | `songs/wasting-my-time/Patchbay.html`: double-click and the song is already loaded; pick `GeneralUser-GS.sf2` once if asked |
| **Source MIDI** | `Wasting_My_Time_orchestral_VI_part1_winds_brass.mid` (14 channels: piccolo → tuba) and `…part2_perc_harp_strings.mid` (10 channels: timpani, glockenspiel, tubular bells, 3 percussion tracks on ch 10, harp, strings) |
| **Session** | `Wasting My Time.patchbay.json`: the instrument assignment and mix for all 26 parts |
| **Preview** | `Wasting My Time (Patchbay preview).mp3`: full 2:45 render, −14.5 LUFS, 14.6 LU loudness range |

Song facts: 156 BPM, 4/4, 8,256 notes, 25 section markers (Intro, Interlude,
Verse 1–4, Pre-chorus, Chorus, Tag, Bridge, Violin solo, Outro, Ending).

**Instrument assignment** (GeneralUser GS):
- Piccolo, Flute, Oboe, English Horn, Clarinet (also used for bass clarinet),
  Bassoon (also used for contrabassoon), French Horns ×2, Trumpet, Trombone ×2,
  Tuba.
- Timpani, Glockenspiel, Tubular Bells, and the Orchestral kit (bank 128,
  program 49) on the three percussion rows.
- Orchestral Harp.
- Strings: Fast Strings for Violin I/II and Viola, Cello, and Double Bass, plus
  articulation slots: Tremolo Strings (violins and viola), Pizzicato Strings
  (Violin II, cello, bass), and solo Violin (Violin I).

GM has no bass clarinet or contrabassoon, so those borrow clarinet and bassoon.
The Windows edition is the natural place to give them dedicated VST instruments.

### Revision v2 (melody + thickening)

The user asked for slight adjustments to improve the melody and thicken the
arrangement. That produced **v2**:

- **Live:** https://claude.ai/artifact/JVYFX1dYxruG3To4GXokYm (opens on v2)
- **Folder:** `songs/wasting-my-time-v2/`, containing:
  - the two `(v2).mid` files
  - `CHANGES.md`, a bar-by-bar list of the changes and the reason for each
  - `Wasting My Time v2 (Patchbay preview).mp3`
  - `Wasting My Time - before and after.mp3`, with the five changed passages
    played original then v2
  - `revise.py`, which regenerates v2 from the originals with each change as a
    named step

The changes:
1. Each chorus's second phrase now climbs C–D–E to F instead of repeating G | A,
   and every part doubling the tune follows it.
2. The final chorus builds over its three phrases: G→A, then D→C, then D–E→F, with
   a tubular bell on F.
3. The fifth bar of each verse now starts C–B♭–A instead of A–G–F, giving the
   verse a high point.
4. The third statement of the bridge figure is sequenced up a third.
5. Horns double the violas' tune in verse 2.
6. Verse 3 gets harp arpeggios.
7. Soft horns double the violas' chords at the start of the bridge.
8. Flute 2 plays in thirds in choruses 1 and 3.

v2 adds 134 notes (to 8,390). Harsh clashes went down from 392 to 339. The form,
harmony, tempo, dynamics and markers are unchanged.

Analysis notes for further work:
- **Key and harmony:** F major, with D minor verses
  (A7 | Dm C | B♭maj7 A7 | Dm C | B♭maj7 A7 | Dm), a chromatic pre-chorus
  (G | B/F♯ | E♭m7 | D7), a ii–V–I chorus (Gm7 C7 | F), a bridge of
  Am B♭maj7 | Gm7 C7, and a D major ending.
- **Who carries the verse tune:** cellos (V1), violas (V2), cellos up an octave (V3),
  flute + oboe + violins I (V4).
- **Who carries the chorus tune:** violins I + flutes, with piccolo, oboes and
  glockenspiel in later choruses. Violins II and the clarinets play a third below.

### Revision v3 (superseded; based on the user's notes on v2)

- **Live:** https://claude.ai/artifact/5tmiHVbALXegpCcjNF3rn5
- **Folder:** `songs/wasting-my-time-v3/`, containing `CHANGES.md`, the `(v3).mid`
  files, a preview, `Wasting My Time - v2 vs v3.mp3`, and `revise_v3.py`, which
  builds v3 from the originals.

The user's feedback on v2:
- They liked v2 overall.
- The "higher" changes in the early sections (chorus answers at 0:29, 0:50 and
  1:19, and the verse 3 line at 1:06) were too bright. The piece should be
  **melancholic but anthemic**. Higher versions are fine from verse 4 (2:04) on.
- The horns honked at times.
- The bridge and violin solo (1:29–1:54, a transcription of the original
  pop-rock song's guitar solo) were melodically messy.

What v3 does in response:
1. **Choruses 1–3:** the answer phrase is now B♭ A B♭ C | D C | B♭→A, a one-beat
   4–3 sigh onto the original A. Every doubling and harmony part follows it.
   The final chorus keeps the climb to F.
2. **Verses 1–3:** the line is now A B♭ A | G F E, leaning on the minor sixth.
   Verse 4 keeps C B♭ A.
3. **Bridge, bars 63–64:** a falling answer, C . . B♭ | G . E .
4. **Violin solo, bars 65–70:** rewritten in clean two-bar phrases (33 notes → 26)
   with the slides and chromatic flicks removed. CHANGES.md has a bar-by-bar
   table.
5. **Horns 1·2 and 3·4:** velocity ×0.82 (max 100) and CC7 90. Velocity also
   controls brightness in this sound set.

Harsh clashes: original 392, v2 339, v3 365. The difference from v2 is the
intentional sighs.

### Revision v18 (current): verses 1 and 2 a little louder

On v17 the user felt verses 1 and 2 were ever so slightly too quiet, and verse 3
was fine. They asked whether that's due to the different instruments.

v18 is v17 with verses 1 and 2 about +0.5 dB:
- V1 cello ×1.18
- V2 viola ×1.257, horns 1·2 ×1.133

Result:
- Melody over the rest (RMS): V1 +2.2, V2 +2.2, V3 +1.6 dB (unchanged).
- Everything from verse 3 on renders identically to v17.
- −14.6 LUFS; clashes 334.

**Why verse 3 needs less:** it's register, not level.
- With K-weighting (t32.js in the scratchpad: BS.1770 shelf + high-pass), v17
  measured V1 +2.2, V2 +1.9, V3 +1.5. So V3 wasn't louder.
- V3's cello tune is at G4–A4, in its own register: viola 16ths below, violin
  chords above, bassoon an octave under.
- V1/V2's tune is at G3–A3, in among the accompaniment's register. That's the
  V1 viola chords and violin II broken chords, and the V2 bassoon counter-line
  and harp.

**User preferences on the verse tune:**
- V1/V2 about +2.2 dB RMS over the rest.
- V3 about +1.6.
- V2 is a sensitive spot: +2.8 was too loud, +0.7 too quiet.
- If this is still not right, thinning the accompaniment in the tune's register
  is an alternative to more level.

Where to find it:
- **Live:** https://claude.ai/artifact/LtQ9Az47zEMnkAc4zoNZib
- **Folder:** `songs/wasting-my-time-v18/`

**Next: ask whether the three verses now feel even.**

### Revision v17 (superseded): the verse melody at one level in all three verses

The user approved verse 2 in v16, then noticed verses 1 and 3 were inconsistent
with it. They still had the v14 lift: +3.8 and +4.0 dB over the rest.

v17 is v16 with:
- V1 cello expression ×1.145 (was 1.30)
- V3 cello ×1.22 and bassoon ×1.18 (were 1.40 / 1.35)

Result:
- Verse melody over the rest: V1 +1.5, V2 +1.6, V3 +1.6 dB.
- Everything outside verses 1 and 3 renders identically to v16.
- Whole song −14.5 LUFS. The 0.2 LU rise is from gating: the quieter verses now
  fall below the relative gate.
- Harsh clashes: 334.

**The user's verse level:** verse 2 at +1.6 dB is the level the user approved.
Keep all three verses at that level.

Where to find it:
- **Live:** https://claude.ai/artifact/DLp63JEfZuJT8obwv2BHvF
- **Folder:** `songs/wasting-my-time-v17/`

### Revision v16 (superseded): verse 2's melody, in between

The user liked v15, except that verse 2's melody was now slightly too quiet. v14's
verse 2 had been a touch too loud.

v16 is v15 with verse 2 set between the two:
- viola expression ×1.22 (v14 1.30, v15 1.15)
- horns 1·2 ×1.10 (v14 1.15, v15 1.05)

Result: the melody is +1.6 dB over the rest (v14 +2.8, v15 +0.7). Everything
else renders identically to v15. Whole song −14.7 LUFS; clashes 334.

Where to find it:
- **Live:** https://claude.ai/artifact/DAGx9v6PTrfFNxPRYf2e5X
- **Folder:** `songs/wasting-my-time-v16/`, with a three-way verse 2 comparison
  (v14/v15/v16)

### Revision v15 (superseded): verse 2 eased back, and the ending reworked

User feedback on v14:
1. The lead was a touch too loud in verse 2.
2. The ending started too quietly, had a weird volume drop, and repeated a few
   too many times; add instruments as the speed builds.

v15 is v14 with these changes:
- **Verse 2:** viola expression ×1.15 (was 1.30) and horns 1·2 ×1.05 (was 1.15).
  The melody is now +0.7 dB over the rest (v14: +2.8). Verses 1 and 3 are
  unchanged (+3.8 / +4.0).
- **Ending:**
  - No step back: the full bar-102 tutti continues.
  - 5 repeats (bars 103–107; was 8). The hit is at bar 108, 2:48.9.
  - Tempo per beat 156→228; bars start at 156/163/175/190/210 BPM.
  - Expression 113→`EXPR_TOP` 115. It's kept low because the master
    compressor's fast attack lets the dense last bar's transients set the
    export peak.
  - New colours, one pair per repeat, all cut at the hit:
    - harp D-minor 16th sweeps (D3–A5) + tubular bell D5 on every downbeat
    - glockenspiel doubling the figure + tremolo strings D–A–D
    - choir D–A–D–A + Piano (melody) doubling the figure an octave up
  - Drive (snare 16ths, bass drum every beat, cymbal roll) enters at full
    strength in bar 106. Timpani roll in bar 107.
  - The v14 dip came from the drive entering softer than the patterns it
    replaced.
- **Export loudness:** −14.7 LUFS. The ending's peak sets the export's
  normalisation (`k = 0.98/peak`), so the body of the export is 0.75 dB quieter
  than v14. Live playback is unaffected.
  - Tried to remove it by lowering the drive and colours: each step bought only
    about 0.2 dB, because of the compressor.
- **Harsh clashes:** 334.

Where to find it:
- **Live:** https://claude.ai/artifact/MgHMD7HtzphLfxxYVbfZ16
- **Folder:** `songs/wasting-my-time-v15/`, with the ending and verse 2
  comparisons

### Revision v14 (superseded): verse melody forward, and an accelerating ending

The user asked for two things:
1. The verse melody before the bridge was too quiet or buried.
2. A new ending: repeat the last bit several times, building faster and faster,
   into the same cold ending.

**Verses 1–3** (bars 7–12, 21–26, 40–45):
- The tune is low (G3–A3): cellos in V1, violas with horns 1·2 in V2, cellos
  with bassoons in V3. It measured 2.6–4.3 dB under the rest (solo render
  subtracted from the full mix).
- Melody CC11 is raised (×1.30–1.40; horns 1·2 ×1.15) with velocity ×1.1, and
  horns stay capped at 100.
- The mid/high accompaniment's CC11 is ×0.86, then restored at the section end.
- The `VERSES` table in revise_v14.py sets this.
- Result: the melody is now 2.8–4.0 dB above the rest.
- Engine note: gain = (CC7/127)² × (CC11/127)², i.e. 40·log10 of the ratio, in dB.

**Ending:**
- Bars 100–102 are unchanged: the figure F . . G | G G over a D pedal, built in
  3 layers.
- 8 new bars (103–110) repeat bar 102's cell in layers:
  - bar-100 texture first
  - + flutes, horns 1·2 and trumpets at 105
  - + piccolo and snare at 107
  - snare 16ths, bass drum every beat and a cymbal roll at 109
  - a timpani roll in 110
- CC11 rises 100→127 and velocity ×0.9→1.07.
- Tempo goes per beat from 156 to 228 BPM, with exponent 1.4 so it quickens late.
- The original hit and everything after it are shifted 8 bars, to bar 111. The
  tempo returns to 156 at the hit, so it's identical.
- Settings: `REPEATS`, `END_BPM`.
- Timings: hit at 2:53 (was 2:42); song 2:56.

Checks:
- Harsh clashes: 334.
- Whole song: −14.1 LUFS.
- Same peak as v13.

Where to find it:
- **Live:** https://claude.ai/artifact/1MbZunydRJYEy89s7oqhqV
- **Folder:** `songs/wasting-my-time-v14/`, with the verse and ending
  comparisons

### Revision v13 (superseded): a softer harp outside the bridge

The user agreed the "piano outside the bridge" was probably the harp, and asked to
soften it.

v13 is v12 with only the harp changed, outside bars 59–70:
- velocity ×0.72 (`HARP_SOFT`), for a lighter, less piano-like attack
- CC7 100 → 80 (`HARP_VOL`), with CC7 back to 100 just before bar 59 and 80
  again at bar 71

The harp outside the bridge is now about 5 dB softer: about 11 dB under the mix,
where it was about 8 dB. That was measured by soloing it in Patchbay. Velocity
alone gave only 2.3 dB, which is why the CC7 change is there too.

Checks:
- The bridge renders identically to v12.
- Harsh clashes: 334.
- Whole song: −14.1 LUFS.

Where to find it:
- **Live:** https://claude.ai/artifact/KYFVn5VdBp9X9HrvxsYJmp
- **Folder:** `songs/wasting-my-time-v13/`, including
  `Wasting My Time - harp v12 vs v13 (0m04-0m37).mp3`

### Revision v12 (superseded): a quieter rolling piano, only at the end of the bridge

The user said (1) the piano seemed to play outside the bridge, and (2) asked for
the rolling piano to be quiet and only towards the end of the bridge.

v12 is v11 with:
- **Piano (rolling)** only in bars 68–70 (1:48–1:53), 16ths, CC7 84 (was 112),
  velocity 42 rising to 70. That's about 20–23 dB under the mix (v11: 10–15 dB),
  measured by soloing it in Patchbay. Pedal still changes per chord.
- **Harp** keeps its full sweeps until bar 68, then only notes ≥ C4.
- Choir and Piano (melody) unchanged.

**About "piano outside the bridge":** checked v11 and v12. Both piano tracks
have notes only in bars 62–70, and a solo-piano render is silent outside
1:35–1:53. The likeliest piano-like sound elsewhere is the harp's rolling
arpeggios in the verses and choruses (GM harp). Another possibility: cross-file
channel collisions, if the files are played through one shared GM synth outside
Patchbay. The user was asked for a timestamp.

Checks:
- Harsh clashes: 334.
- Whole song: −14.1 LUFS.
- Outside the bridge the audio is identical to v11.

Where to find it:
- **Live:** https://claude.ai/artifact/GkvFBiNzw8Jc8wxi7ApLbs
- **Folder:** `songs/wasting-my-time-v12/`, including
  `Wasting My Time - bridge v11 vs v12.mp3`

### Revision v11 (superseded): choir at the climax, and piano colour

The user asked to bring the choir back softly for the climax and to add piano for
colour: a piano supporting the central melody, plus a rolling piano part for
drama.

v11 is v10 plus:
- **Choir** (file B, channel 16, program 53): four-voice chords in bars 68–70
  only. CC7 70, velocity 48–64, CC11 swell 52→92.
- **Piano (melody)** (file A, channel 16, program 1, no pedal): doubles the hook
  with violins I from S2, adding the octave below from S4.
- **Piano (rolling)** (file B, channel 15, program 1): low arpeggios up and down
  each chord (8ths in S2–S3, 16ths in S4–S6), with CC64 pedal down/up at every
  chord change.
  - Why two tracks: one shared pedal would have held the melody's passing notes
    against the chords.
- **Piano level:** first pass about −20 dB under the strings. Raised (CC7 112,
  higher velocities) to about −13 dB at S2 and −9 dB at S4, measured by
  subtracting the v10 render from v11.
- **Harp:** only notes ≥ C4 from S4 on, so the piano owns the low register.

Checks:
- Harsh clashes: 334.
- Whole song: −14.1 LUFS.

Where to find it:
- **Live:** https://claude.ai/artifact/Mtj31HwSAdUocP8q5RwJdD
- **Folder:** `songs/wasting-my-time-v11/`, including
  `Wasting My Time - bridge v10 vs v11.mp3`


### Revision v10 (superseded): a lush string-orchestra bridge

The user asked to keep v9's lushness but centre the bridge heavily on many string
instruments.

v10 is v9's bridge (bars 59–70) with:
- **Out:** all 14 woodwind and brass parts, plus the choir, celesta, snare and
  bass drum. The harp plays at ×0.72 velocity.
- **New tracks (file B):**
  - "Solo Violin": channel 12, program 41
  - "Strings (tremolo)": channel 13, program 45
  - "Strings (pizzicato)": channel 14, program 46
  - "Strings (pad)": still channel 11, program 50
- **Roles:**
  - Solo violin: sings S1, a high countermelody over S2–S3, then doubles
    violins I for S4–S6.
  - Violas: a slow rising countermelody (C D | D E | E F | F G | G F) under
    S1–S2, then the hook an octave below violins I from S3 (replacing the oboes).
  - Cellos: also join S6.
  - Tremolo strings: high shimmering chords from S2, in place of the choir.
  - Pizzicato: a building pulse from S3 (half notes, then quarters, then 8ths)
    in place of the drums.
  - Percussion: timpani rolls and cymbal swells only.

Checks:
- Harsh clashes: 334.
- Bridge loudness every 3 s: v9 −22.9 → −18.3 → −9.9, v10 −23.6 → −18.3 → −10.5.
- Whole song: −14.1 LUFS.

Where to find it:
- **Live:** https://claude.ai/artifact/6CkgtAC7K5qqZMNUBgfTQH
- **Folder:** `songs/wasting-my-time-v10/`, including
  `Wasting My Time - bridge v9 vs v10.mp3`

**Next: ask how v10's bridge sounds.** Possible tweaks:
- the solo violin's level
- the density of the pizzicato
- whether to bring a soft horn or the choir back at the climax
- the reverb amount

### Revision v9 (superseded): a very lush bridge

The user asked to make the bridge "very, very lush" so it stands out further from
the rest of the piece.

v9 keeps v8's melody: the hook in six statements in its sung rhythm, with the same
doublings, sighs on S4 and S5, and the final trill. The texture around it in
bars 59–70 is rebuilt:
- **Reverb:** CC91 raised from 45 to 112 on 19 parts for the bridge, restored at
  bar 71. **The app now supports CC91 automation**: parsed as auto type 2 and
  applied through a `revAuto` gain on each strip's reverb send, relative to the
  part's starting reverb. The main artifact was republished with this.
- **Enriched chords** with no semitone rubs: Am7 / B♭ add9 | Gm7 add11 / C9.
- **New tracks:**
  - "Strings (pad)": file B, channel 11, program 50 (slow strings). Six voices,
    tied, eight from S4.
  - "Choir": file B, channel 12, program 53 (choir aahs). Four voices from S2.
  - "Celesta": file A, channel 16, program 9. Shimmer in bars 59–63.
- **Harp:** 16th-note sweeps through each chord, damped at chord changes.
- **Bass:** long notes in cellos and double basses instead of the walking bass.
- **Violins II:** a slow high descant between statements.
- **Harpsichord:** removed.
- **Percussion:** a timpani roll + cymbal swell into each statement, each bigger;
  soft timpani + bass drum on each statement; crashes on S4/S5; snare only in
  bars 68–70; then the roll and swell into the interlude.

Checks:
- Harsh clashes: 334.
- Bridge loudness every 3 s: v8 −29.8 → −21.7 → −10.5, v9 −22.9 → −18.3 → −9.9.
- Whole song: −14.0 LUFS.

Where to find it:
- **Live:** https://claude.ai/artifact/U7NZyNf54HJ2qtvtXm9EJz
- **Folder:** `songs/wasting-my-time-v9/`, including
  `Wasting My Time - bridge v8 vs v9.mp3`

**Next: ask how v9's bridge lands.** Easy tweaks:
- the reverb amount (the 112 in `revise_v9.py`)
- the choir level, or where it enters
- the harp density
- whether to keep the celesta

### Revision v8 (superseded): back to the baroque bridge, with more melody and a percussion build

The user's feedback on v7: go back to v5 (the baroque bridge), incorporate more
of the main melody, and add more percussion for a building quality. Their earlier
note on v5 also applies: the harpsichord was far too loud.

v8 changes only bars 59–70:
1. **The hook in its sung rhythm in every statement** (B♭ A B♭ C | G | A), joined by
   2-note pickups. The v5 turns and the 16th countermelody are gone; the sighs
   remain only on S4 and S5, and the final trill stays.
2. **More instruments on the tune:**
   - S1: violins I (B♭4)
   - S2: violins I (D5) + violins II on the hook
   - S3: cellos + bassoons (B♭3) with violins I (B♭4); the double basses walk
   - S4: three octaves (violins I + flute B♭5, violins II a third below, oboes
     B♭4, cellos B♭3)
   - S5: D6, with oboes on D5
   - S6: tutti + piccolo, with trumpets in harmony (C E G under the G)
3. **Percussion build:**
   - timpani: heartbeat (59–61), every beat (62–63), 8ths (64–67), 16ths
     (68–69), then a roll on C (70)
   - snare: enters at S2 with a march figure, then 8ths, 16ths and a roll
   - bass drum: from S3, once, then twice, then four times per bar
   - cymbals: crashes on S4 and S5; swells into S4 and into the interlude
   - triangle: on the opening statements
   - CC11 ramps on the percussion tracks
4. **Harpsichord** (B, channel 11): CC7 50 (was 88), velocity 42–52 (was 64–76),
   5 chords per 2 bars (was 8). About 12 dB quieter.

Checks:
- Harsh clashes: 334.
- Bridge loudness every 3 s: v5 −28.5 → −24.1 → −11.8, v8 −29.8 → −21.7 → −10.5.
- Whole song: −14.1 LUFS.

Where to find it:
- **Live:** https://claude.ai/artifact/Lk7YytJFLNPoJxzk3bC2fR
- **Folder:** `songs/wasting-my-time-v8/`, including
  `Wasting My Time - bridge v5 vs v8.mp3`

**Next: ask how v8 lands.** Specifically ask about the harpsichord level, since it
was the main complaint about v5. It can be removed entirely.

### Revision v7 (superseded): the swell, sooner and more melodic

The user's feedback on v6: they liked the effect, but (a) it needed to happen
sooner, and (b) it should be more melodic, suggesting the Deep Note rather than
literally recreating it.

v7 changes only the swell under the hook in bars 59–70. The hook statements are
as in v6.
1. **Sooner:** the 16 instruments gather in bars 59–60, one every half beat
   instead of over 59–64. The fan-out starts at bar 61 (1:32) instead of 65.
2. **The cluster** is now in key (A C D E F G, with no B♭ against A), and the
   wavering is ±0.2 semitone, only while gathering.
3. **The fan-out:** at each chord change (Am . . B♭ | Gm7 . C7 .) each voice
   moves to the chord tone nearest its eased path toward its target, with a short
   pitch-bend slide (≤ half a beat, RPN range ±7) into each new note. Upper voices
   climb and lower voices descend.
4. **The widest point** (bar 70 beat 3) is a root-position C7, one instrument per
   note: C2 G2 C3 E3 G3 B♭3 C4 E4 G4 B♭4 C5 E5 G5 B♭5 E6 C7. It resolves into
   the F major interlude.
5. **Landing:** the timpani roll is on C, and the harp glissando uses only the
   C7's notes (C E G B♭) from C3 to C7, with short notes.
6. **Fix:** the oboes' third-below line resolves to E, not F, under the long A.

Checks:
- Harsh clashes: 335 (lowest yet); the bridge adds none.
- Loudness: about −26 LUFS at the start of the bridge, −9 at the peak, −14.2
  overall.

Where to find it:
- **Live:** https://claude.ai/artifact/YBbFZ4XVkRxDJBVPPQ6mB2
- **Folder:** `songs/wasting-my-time-v7/`, including
  `Wasting My Time - bridge v6 vs v7.mp3`

**Next: ask how v7's bridge compares with v6.** Easy settings in
`revise_v7.py`:
- `SPREAD0` / `SPREAD1` (when the fan-out starts and peaks)
- the length of the slides
- the targets in `SWELL`

### Revision v6 (superseded): the swell bridge

The user's feedback on v5:
- The harpsichord was far too loud and overpowering.
- Some of the other bridge ideas were fine.
- New direction: stay closer to the main melody, but make the bridge very intense
  and dense, with each instrument contributing its own frequency, like the THX
  Deep Note or the crescendo in the Beatles' "A Day in the Life".

v6 is v4/v5 everywhere except bars 59–70. It has no harpsichord.
- **The hook:** "Wasting all my time on you", plain at its sung rhythm, stated six
  times and getting louder and higher:
  1. violins (B♭4)
  2. violins at D5 + oboes
  3. violins at B♭5 + oboes + 1st trumpet
  4. tutti at B♭5, with the oboes in thirds, the trumpets in harmony and the
     glockenspiel
  5. the same at D6
  6. B♭5 again, leading into the interlude
- **The swell, setup:** 16 instruments enter one at a time (bars 59–64) on a
  drifting cluster, one note each from G3 to B♭4, every one with its own slow
  random detune.
- **The swell, glide:** from bar 65 they slide by pitch bend (RPN range ±4, reset
  to ±2 at bar 71, a fresh attack every few semitones) to their own notes of a
  six-octave F major chord: F1 C2 F2 A2 C3 F3 A3 C4 F4 A4 C5 F5 A5 C6 F6 C7. They
  lock in at bar 70 beat 3. CC11 ramps from about 72 to 127.
- **Landing:** timpani roll on F (bars 67–70), suspended-cymbal swell (68–70),
  harp glissando F3–F6 (bar 70, beats 3–4). The original snare roll and the bass
  drum + crash at 71 are kept.
- **Levels:** the bridge goes from −27 LUFS (it was −35 at first; the opening was
  raised so the hook is audible) to −9 LUFS at the landing, the loudest point in
  the song. The whole song is −14.2 LUFS.
- **Live:** https://claude.ai/artifact/2D8Pc5CFETmQFSP98g31TT
- **Folder:** `songs/wasting-my-time-v6/`, with `CHANGES.md` (including a table of
  instrument → chord note), the bridge excerpt, the full preview and
  `revise_v6.py`. The `SWELL` table in the script sets the cluster, the targets
  and the entry order.

**Next: ask how the swell sounds.** Likely tweaks:
- how long the glide takes, or how late it locks in
- how wide the wavering is
- the hook's level against the swell
- a different final chord voicing
- ending on a hard cut, like "A Day in the Life", instead of running into the
  interlude

### Revision v5 (superseded): the baroque bridge

The user's feedback on v4:
- All the other changes are good.
- Neither bridge option worked.
- They asked for "a variant of one of the vocal lines, but with a baroque flair".

v5 is v4 with a new bridge (bars 59–70) built on the chorus hook ("Wasting all my
time on you", B♭ A B♭ C | G | A).
- **Why it fits:** the hook sits at its original pitch on the bridge's
  Gm7–C7 bar, and its A resolves onto the following A minor.
- **Six statements:**
  1. B♭4 in violins I.
  2. A third up (D5), with violins II playing the hook a third below.
  3. In the cellos (B♭3), with 16th runs above it.
  4. An octave up (B♭5) in violins I + flute, violins II a third below.
  5. A third up again (D6), the high point.
  6. B♭5, with the G turned into a cadential trill that resolves to F at the
     interlude.
- **Baroque devices:**
  - appoggiatura sighs (B♭→A, D→C)
  - 16th-note turns
  - walking 8th-note cello bass, double basses on every beat
  - a new **Harpsichord** track (file B, channel 11, program 7)
  - violins in thirds
  - terraced dynamics
- **Removed in bars 59–70:** the old violin figure and solo, violin II pads and
  arpeggios, cello echo, held bass notes, harp, flute doublings, the oboe bar-64
  run and the piccolo bar-70 run.
- **Live:** https://claude.ai/artifact/4BLFdgu7pMSdDZmCxSYje5
- **Folder:** `songs/wasting-my-time-v5/`, containing `CHANGES.md` (a table of the
  six statements), the bridge excerpt MP3, the full preview and `revise_v5.py`.
- **Harsh clashes:** 336, the lowest of any version (original 392).

**Next: ask how the baroque bridge sounds.** If it's close, likely tweaks are:
- harpsichord level
- the speed of the 16th runs
- whether the trill is too busy
- swapping which statement the cellos take

### Revision v4 (superseded: the user rejected both bridge options)

The user's feedback on v3:
- **Chorus:** keep the original second phrase in choruses 1–3. It reproduces the
  original vocal hook, "Wasting all my time on you", sung twice.
- **Bridge:** v3's cleaned-up bridge still didn't have a distinctive melody, and
  the user asked for other ideas.

v4 does the following:
1. **Choruses 1–3** are back to the original B♭ A B♭ C | G | A, with all parts
   restored. The final chorus still varies it (G→A, then D→C, then D–E→F, with a
   bell). It isn't confirmed that the user wants this; offer to revert it.
2. **The solo section (bars 65–70)** has a new 6-bar theme replacing the guitar
   solo: | A . . F | G . E . | E A C . | D . C B♭ | A . G F | D . E . |, leading to
   F. Violins I play it, with the flute in unison.
3. **The bridge (bars 59–64)** comes in two options:
   - **A, "the hook in minor":** the chorus hook's shape in A minor, stated three
     times a third higher each time:
     A G A B♭ F . | G . E . → C B♭ C D A D | B♭ . G . → E D E F C . | D . C .
     Played by violins, then violins + clarinets, then tutti.
     - Folder: `songs/wasting-my-time-v4-bridge-a/`
     - Live: https://claude.ai/artifact/17zw65tqnJVLDycaCZQwTY
   - **B, "theme low, then high":** the theme in cellos + soft horns two octaves
     down, then violins + flute up high.
     - Folder: `songs/wasting-my-time-v4-bridge-b/`
     - Live: https://claude.ai/artifact/1rqFv6uqN1iEx5ZTw9QzB7
- **Comparison clip:** `Wasting My Time - bridge options.mp3` plays bars 57–72 as
  v3, then A, then B.
- **Script:** `revise_v4.py <out>/ A|B` builds either option from the originals.
- **Harsh clashes:** original 392, A 356, B 351.

**Next: ask which bridge the user prefers.** It could also be a mix, such as A's
bridge with B's horn colour.
- If neither works, two directions were discussed: (a) a descant over the
  original guitar figure, or (b) a slower hymn-like theme.
- If the theme itself doesn't land, it is the part to rework, since both options
  use it.

(MP3s for v2–v17 are left out of this package for size. v18's verses comparison
includes v17's verses 1 and 2. Their pages and
MIDI files are included.)

---

## 1. What the user wants

An audio program built to work with Claude:

1. **Load MIDI files** into a window that lists every MIDI channel.
2. **Assign an instrument to each channel**, choosing from a library of free
   instruments grouped by music category.
3. Two editions:
   - **Browser edition ("handoff window")**: opened from Claude each time.
   - **Windows edition**: runs locally and hosts **real VST3 plugins**.

### Decisions the user already made (don't re-ask)

| Question | Answer |
|---|---|
| Browser edition sound source | **SoundFonts** (VSTs can't run in a browser) |
| Windows edition VST behaviour | **Real-time playback** with plugin windows (not just render-to-WAV) |
| Instrument categories that matter | **Keys & Piano, Orchestral, Synths & Electronic, Drums & Band** (all four) |
| Build order | Browser edition and instrument research in parallel (both done) |

### Open question for the user

**Is there a GitHub repository for the Windows edition, or should one be created?**
Building a Windows `.exe` needs a Windows machine, so the plan is to build it on
GitHub (Windows runner). This answer is the blocker for the next phase.

---

## 2. Current status

| Piece | Status |
|---|---|
| Browser edition | **Done and published**: https://claude.ai/artifact/RmKv4ph63HoFihzA3wSfeg (private to the user; opens on the demo song) |
| Wasting My Time song page | **Done and published**: the original at https://claude.ai/artifact/UPqVJY673QQMX9UJn3K76e; the approved **v18** at https://claude.ai/artifact/LtQ9Az47zEMnkAc4zoNZib |
| Song revisions | **v2–v18 done**; v18 approved by the user. Each `songs/wasting-my-time-vN/` folder has its own `CHANGES.md` |
| Offline copy (double-click HTML) | **Done**: `Patchbay-local/` (the user was also sent `Patchbay-local.zip` with the SoundFont inside) |
| Free instrument research | **Done**: `free-instruments.md` |
| Windows VST3 edition | **Not started**: blocked on the GitHub repo question |

Also tested with the user's two "Wasting My Time" files layered: 26 parts,
8,256 notes, 2:45 long, 25 section markers, and every part assigned the GM
program its file asks for. That includes Orchestra kit 49 on the three
percussion tracks, Tremolo and Pizzicato Strings articulations on the strings,
and a solo Violin passage. No notes needed the range fallback with GeneralUser
GS. The session save/load round trip works. A full export measures −14.5 LUFS
integrated with a 14.6 LU loudness range. The session file and an MP3 preview are
in `songs/wasting-my-time/`.

Tested in headless Chromium: the bank loads (287 presets: 261 instruments plus 13
drum kits that appear in both bank 120 and bank 128), the demo song renders on
every channel (peak about 0.76), and there are no console errors at 1280 px or
400 px width. The user has used it throughout the song revisions.

---

## 3. Browser edition: what it does

- Opens with an original 16-bar demo song, "Night Drive" (piano, strings, bass,
  pad, lead, drums), so Play works immediately.
- Open MIDI or drag-and-drop a `.mid` / `.midi` / `.kar` / RIFF RMID file.
  Format 0 and 1 are supported; SMPTE timing is not.
- **Layering**: picking or dropping several MIDI files at once, or using
  **Add MIDI**, merges them onto one timeline. This handles scores split across
  files: the user's "Wasting My Time" orchestral arrangement comes as part 1
  (winds/brass, 14 channels) plus part 2 (percussion/harp/strings, 10 channels),
  which loads as **26 parts**. Rows are labelled A01, B10 and so on (file letter
  plus channel). When files are added, existing parts keep their settings.
- **One row per part**, where a part is a (track, channel) pair. Tracks that share
  a channel get separate rows; for example, three percussion tracks on channel 10
  each get a row with its own volume. Controllers sent from a part's own track
  apply only to that part; controllers from elsewhere apply to the whole channel.
  Each row has a colored tag, the track name, what the file asked for (GM program,
  note count, range), an instrument picker, mute/solo, volume/pan/reverb sliders,
  and a level meter.
- **Articulation switches**: when a part changes program mid-song (strings going
  bowed → tremolo → pizzicato, or Violin I → solo violin), the program with the
  most notes is the main instrument and each other program gets its own slot
  (`S.ch[i].alt[program]`). The instrument browser shows "This part switches
  sounds. Changing: …" chips to pick a slot. Each note keeps its program
  (`n.prog`).
- **Section markers** (MIDI marker events, e.g. Intro / Verse 1 / Violin solo)
  appear on a second ruler line, and the LCD has a SECTION readout.
- **Range fallback**: a note with no sampled zone at its key or velocity stretches
  the nearest zone instead of going silent. For drum kits this only fills
  velocity gaps.
- **Instrument browser**: category chips (All, Keys & Piano, Orchestral,
  Synths & Electronic, Drums & Band, World & FX) with counts, search, and a list
  grouped by SoundFont. Clicking assigns the instrument and plays a preview
  (an arpeggio, or a drum groove for kits). "Use the file's instrument" resets it.
- **Piano roll** colored by channel, with a bar ruler, Fit/2×/4×/8× zoom, click or
  drag to seek, and follow-scroll while zoomed.
- **Transport**: play/pause, stop, back to start, loop. The LCD shows bar·beat,
  time, tempo and meter. Keys: Space (play/pause), Home (back to start).
- **Sound library**: GeneralUser GS 2.0.3 is built in. Users can add any `.sf2`;
  added banks are cached in IndexedDB. `.sf3` is rejected with a clear message.
- **Master**: output level and room reverb.
- **Export WAV**: offline render at 44.1 kHz / 16-bit stereo that respects
  mute/solo (so soloing a channel exports a stem). In the artifact it saves as
  `.zip` containing the `.wav`, because the artifact `downloads` capability doesn't
  allow `.wav`. The local copy saves a plain `.wav`.
- **Save/Load session**: a `.json` file (schema below), meant to carry over to
  the Windows edition.

### Engine notes (all custom, no libraries)

- **MIDI parser**: tempo map, time signatures, running status, sustain pedal
  (CC64, applied when parsing), CC7 volume / CC11 expression as automation, CC10
  and CC91 as initial pan and reverb, bank select CC0, pitch bend with RPN 0 range,
  CC121 reset.
- **SF2 parser/synth**: preset × instrument zone merging (global zones, additive
  preset generators, key/velocity range intersection). It implements:
  - the volume envelope (delay, attack, hold, decay, sustain, release, with
    key-number scaling)
  - initialAttenuation with the 0.4 EMU/FluidSynth factor
  - default velocity modulators (to attenuation and to filter cutoff)
  - lowpass filter with Q, and the modulation envelope applied to filter cutoff
  - vibrato and mod LFO to pitch
  - loop modes
  - exclusive class (hi-hat choke)
  - per-zone pan
  - scale tuning, coarse and fine tune, and the sample's pitch correction

  **Not implemented**: chorus, LFO to volume or filter, custom SF2 modulators,
  SF3.
- **Engine**: one Web Audio graph per context, with one strip per part
  (`Engine.ensure(n)` grows the strip count), so the same code drives live play
  and OfflineAudioContext export. Each channel strip runs input → MIDI-volume gain
  → fader → panner → master, plus a reverb send. Reverb is a convolver with a
  generated impulse response, and a compressor sits on the master.
- **Export**: notes are fed into the OfflineAudioContext 2–4 s ahead using
  `suspend()`, and finished voices disconnect themselves. Scheduling a long score
  all at once made render time grow with the square of the length: the 2:45
  orchestral song took more than 15 minutes in the test container, and about 95 s
  after this change.
- **Scheduler**: 25 ms timer with a 0.3 s lookahead (1.6 s when the tab is
  hidden). Loop wraps seamlessly.

### Hosting details (needed to republish the artifact)

- The artifact CSP blocks external fetches and `.bin` files, so the 32 MB
  SoundFont ships as **three base64 text files** next to the page:
  `sounds/generaluser-gs-{0,1,2}.b64.txt`, each 11,000,000 raw bytes; total base64
  size 43,092,532.
- Republish with: `capabilities: {downloads: true}` and `files` mapping those three
  `.txt` paths.
- The page is self-contained HTML with no CDN scripts, only Google Fonts
  (Archivo, Martian Mono). If the sound files are missing (for example the local
  copy under `file://`), the library shows a "Choose .sf2 file…" button.

### Rebuilding

```
# 1. Get the SoundFont (license allows redistribution; host your own copy)
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/mrbumpy409/GeneralUser-GS gugs
mkdir -p sounds && split -b 11000000 -d -a 1 gugs/GeneralUser-GS.sf2 sounds/generaluser-gs-
for f in sounds/generaluser-gs-?; do mv "$f" "$f.bin"; base64 -w0 "$f.bin" > "${f}.b64.txt"; done
# 2. Build: writes patchbay.html (artifact body) and local/Patchbay/ (full HTML + .sf2)
#    and, for every songs/<name>/ folder holding .mid files, a song build:
#    songs/<name>/patchbay-song.html (artifact body) + songs/<name>/Patchbay.html (offline)
python3 build.py
```

**Song builds**: the source has a `PRELOAD` slot (`/*__PRELOAD__*/null`).
`build.py` fills it with the folder's MIDI files as base64. On boot the page then
layers those files, exactly as if they were opened together, instead of loading the
demo. The page `<title>` comes from the folder name (`wasting-my-time` → "Wasting My
Time"). The song artifact was published with its three sound files copied server
side from the main artifact:
`files: {"sounds/generaluser-gs-N.b64.txt": {"artifact": "https://claude.ai/artifact/RmKv4ph63HoFihzA3wSfeg", "path": "sounds/generaluser-gs-N.b64.txt"}}`
plus `capabilities: {downloads: true}`. To update it, republish
`songs/wasting-my-time/patchbay-song.html` to
https://claude.ai/artifact/UPqVJY673QQMX9UJn3K76e.

`src/patchbay.src.html` is the only source file. The demo song is
`src/demo.mid`, generated by `src/demo_midi.py`; it is original, so there are no
rights issues.

### Source map (`src/patchbay.src.html`, sections marked `/* ==== name */`)

constants (GM names, categories, colours) → MIDI file parser → SoundFont 2 parser
→ audio engine → state → banks & storage (IndexedDB) → transport → export & files
(WAV, zip, session JSON) → UI: song & strips → UI: banks → UI: instrument browser
→ piano roll → frame loop (LCD, meters) → wiring → boot.

Category mapping: GM family (program ÷ 8) maps to a category. Piano, Chromatic
percussion and Organ go to Keys; Strings, Ensemble, Brass, Reed and Pipe go to
Orchestral; Synth lead, pad and effects go to Synths; Guitar, Bass, Percussive and
all drum kits (bank 128 and bank 120) go to Drums & Band; Ethnic and Sound effects
go to World & FX.

---

## 4. Session file schema (the browser → Windows bridge)

```json
{
  "format": "patchbay-session", "version": 2, "savedAt": "2026-10-27T20:00:00.000Z",
  "midi": { "name": "Wasting My Time", "files": ["…part1_winds_brass.mid", "…part2_perc_harp_strings.mid"], "duration": 165.4, "notes": 8256 },
  "master": { "level": 80, "room": 50 },
  "channels": [
    { "part": 23, "file": "…part2_perc_harp_strings.mid", "channel": 6, "track": "Violin II",
      "drums": false, "fileProgram": 49,
      "instrument": { "name": "Fast Strings", "category": "Orchestral", "family": "Ensemble",
                      "bank": 0, "program": 49, "soundfont": "GeneralUser GS", "plugin": null },
      "articulations": [ { "fileProgram": 46, "notes": 48, "instrument": { "name": "Pizzicato Strings", "…": "…" } } ],
      "volume": 100, "pan": -18, "reverb": 45, "mute": false, "solo": false }
  ]
}
```

- Parts are matched on load by `file` + `channel` + `track`. Version 1 files,
  which have only `channel`, still load.
- `channel` and `program` are **1-based**.
- `volume` and `reverb` run 0–127, where volume 100 means unity.
- `pan` runs −64 to 63.
- `instrument.plugin` is reserved for the Windows edition. The plan is to store
  the VST3 class ID and name there, plus a base64 copy of the plugin's state.

---

## 5. Windows edition: the agreed plan

- **Stack**: C++ with **JUCE** (AudioPluginHost-style graph), built with CMake.
  The VST3 SDK has been MIT-licensed since 3.8, so licensing is simple.
- **Build**: a GitHub Actions `windows-latest` workflow builds `Patchbay.exe`
  (plus an installer or zip) as a release artifact. This is why the repo is needed.
- **Features, in order**:
  1. Scan VST3 folders and list plugins by the same five categories, using
     plugin metadata plus a user-editable mapping.
  2. Load MIDI, show one strip per channel, and assign a VST3 instrument per
     channel. Each strip gets an "Edit" button that opens the plugin's own window.
  3. Real-time playback with a transport, mixer (volume, pan, mute/solo) and
     meters.
  4. Open and save the same `patchbay-session` JSON. When a channel has no
     plugin, fall back to a built-in SF2 player so browser sessions still play.
  5. Render to WAV.
- **Instruments**: see `free-instruments.md`. Starter pack:
  - Surge XT
  - Dexed
  - sfizz with Salamander Grand Piano and VSCO 2 CE (these can be bundled)
  - BBC Symphony Orchestra Discover
  - Splice INSTRUMENT (the former Spitfire LABS)
  - MT Power Drum Kit 2
  - Ample Bass P Lite 4 and Ample Guitar M Lite 4
  - HaNon B70

  Most of these can't be redistributed, so the app links to them rather than
  bundling them.

### Ideas raised but not built

- SF3 support in the browser edition (decode the Ogg samples with
  `decodeAudioData`), or switch the synth to SpessaSynth. The GeneralUser GS author
  says SpessaSynth plays every preset correctly.
- Chorus, LFO to volume and filter, custom SF2 modulators.
- Per-channel MIDI CC automation lanes and editing notes.

---

## 6. Files in this package

| Path | What it is |
|---|---|
| `HANDOFF.md` | This brief |
| `patchbay.html` | Hosted artifact build (page body; the artifact wrapper adds the doctype) |
| `Patchbay-local/Patchbay.html` | Standalone copy; open it in any browser and pick an `.sf2` once |
| `src/patchbay.src.html` | Source (the only one) |
| `src/demo.mid`, `src/demo_midi.py` | Original demo song and its generator |
| `build.py` | Builds both editions plus song builds |
| `free-instruments.md` | Researched free VST3 instruments and SoundFonts with licenses and links |
| `electronic-instruments.md` | Free synths, drum synths, effects and CC0 SoundFonts for the electronic arrangement, mapped to its parts |
| `songs/wasting-my-time-electronic-lush-variations/` | **Lush + variations (revision 2)**: the Chaconne theme in verse 2, Mozart answers in choruses 2–3. MIDI, `CHANGES.md`, preview, before/after clips, Chaconne reference, `variations.py` |
| `songs/wasting-my-time-electronic-lush-mozart/` | **Lush + Mozart**: the lush version with a K. 191 counter-melody in the choruses. MIDI, `CHANGES.md` (search method, runners-up), preview, Mozart reference clip, before/after clips, `mozart.py` |
| `tools/quote-search/` | Scripts that search a MIDI corpus for passages fitting the song's chords |
| `songs/wasting-my-time-electronic-lush/` | **Lush electronic version**: the electronic arrangement plus v18's full orchestration on synths, ensemble width and air layers. Four MIDI files, `CHANGES.md`, preview, electronic-vs-lush clips, `lush.py` |
| `songs/wasting-my-time-electronic/` | **Electronic arrangement of v18**: MIDI files, `CHANGES.md`, full preview, three v18-vs-electronic clips, `electronic.py`, and pages that open on it |
| `tools/` | `render.js`, `verse_balance.js`, `solo_level.js`, `clash.py`, `show.py`, `trim.py`, `stems.js` and `README.md`: the revision recipe and checks |
| `songs/wasting-my-time-v18/` | **v18 (current, approved)**: v17 with verses 1 and 2 about 0.5 dB louder. MIDI files, `CHANGES.md`, full preview, verses 1 and 2 v17-vs-v18 comparison, a verses 1–3 clip, `revise_v18.py`, and pages that open on v18 |
| `songs/wasting-my-time-v17/` | v17 (superseded): the verse melody at one level (≈ +1.6 dB) in all three verses. MIDI files, `CHANGES.md`, full preview, verses 1 and 3 v16-vs-v17 comparison, a verses 1–3 clip, `revise_v17.py`, and pages that open on v17 |
| `songs/wasting-my-time-v16/` | v16 (superseded): v15 with verse 2's melody between v14 and v15. MIDI files, `CHANGES.md`, full preview, verse 2 v14/v15/v16 comparison, `revise_v16.py`, and pages that open on v16 |
| `songs/wasting-my-time-v15/` | v15 (superseded): verse 2 eased back; the ending reworked (five repeats, no step back, new instruments joining). MIDI files, `CHANGES.md`, full preview, ending and verse 2 v14-vs-v15 comparisons, ending clip, `revise_v15.py`, and pages that open on v15 |
| `songs/wasting-my-time-v14/` | v14 (superseded): the verse melody forward and the accelerating ending. MIDI files, `CHANGES.md`, full preview, verse and ending v13-vs-v14 comparisons, ending clip, `revise_v14.py`, and pages that open on v14 |
| `songs/wasting-my-time-v13/` | v13 (superseded): v12 with a softer harp outside the bridge. MIDI files, `CHANGES.md`, full preview, harp v12-vs-v13 comparison, `revise_v13.py`, and pages that open on v13 |
| `songs/wasting-my-time-v12/` | v12 (superseded): v11 with the rolling piano quieter and only in bars 68–70. MIDI files, `CHANGES.md`, full preview, bridge clip, v11-vs-v12 comparison, `revise_v12.py`, and pages that open on v12 |
| `songs/wasting-my-time-v11/` | v11 (superseded): the string-orchestra bridge plus a soft choir at the climax and piano (melody support and rolling arpeggios). MIDI files, `CHANGES.md`, full preview, bridge clip, v10-vs-v11 comparison, `revise_v11.py`, and pages that open on v11 |
| `songs/wasting-my-time-v10/` | v10 (superseded): the lush string-orchestra bridge. MIDI files, `CHANGES.md`, full preview, bridge clip, v9-vs-v10 comparison, `revise_v10.py`, and pages that open on v10 |
| `songs/wasting-my-time-v9/` | v9 (superseded): the lush bridge (choir, string pad, harp sweeps, celesta, deep reverb). MIDI files, `CHANGES.md`, full preview, bridge clip, v8-vs-v9 comparison, `revise_v9.py`, and pages that open on v9 |
| `songs/wasting-my-time-v8/` | v8 (superseded): the baroque bridge with more melody, a percussion build and a quiet harpsichord. MIDI files, `CHANGES.md`, full preview, bridge clip, v5-vs-v8 comparison, `revise_v8.py`, and pages that open on v8 |
| `songs/wasting-my-time-v7/` | v7 (superseded): the earlier, chord-based swell. MIDI files, `CHANGES.md`, full preview, bridge clip, v6-vs-v7 comparison, `revise_v7.py`, and pages that open on v7 |
| `songs/wasting-my-time-v6/` | v6 (superseded): the swell bridge. MIDI files, `CHANGES.md`, full preview, bridge excerpt, `revise_v6.py`, and pages that open on v6 |
| `songs/wasting-my-time-v5/` | v5 (superseded): the baroque bridge. MIDI files (B now has a Harpsichord track), `CHANGES.md`, full preview, bridge excerpt, `revise_v5.py`, and pages that open on v5 |
| `songs/wasting-my-time-v4-bridge-a/`, `-v4-bridge-b/` | v4 (superseded), one folder per bridge option: MIDI files, `CHANGES.md`, previews, the bridge comparison MP3, `revise_v4.py` (in -a), and pages that open on each |
| `songs/wasting-my-time-v3/` | **v3 revision**: the revised MIDI files, `CHANGES.md`, preview and v2-vs-v3 MP3s, `revise_v3.py`, and pages that open on v3 |
| `songs/wasting-my-time-v2/` | **v2 revision**: the revised MIDI files, `CHANGES.md`, preview and before/after MP3s, `revise.py`, and pages that open on v2 |
| `songs/wasting-my-time/` | **Wasting My Time**: the two MIDI files, `Patchbay.html` (opens on the song), `patchbay-song.html` (artifact body), the session file, and the MP3 preview |

Not included because of size: `GeneralUser-GS.sf2` (32 MB). It's in the user's
`Patchbay-local.zip` and on GitHub at mrbumpy409/GeneralUser-GS.

---

## Starter prompt (paste this into the new conversation)

> I'm continuing my Patchbay MIDI Studio project. The attached HANDOFF.md explains
> what's built, the decisions I've already made and the plan. Read it first,
> starting with "Start here". The browser edition is live at
> https://claude.ai/artifact/RmKv4ph63HoFihzA3wSfeg. My orchestral song "Wasting My
> Time" is finished for now at v18, which I'm happy with:
> https://claude.ai/artifact/LtQ9Az47zEMnkAc4zoNZib (details in
> songs/wasting-my-time-v18/CHANGES.md; the scripts for making and checking
> revisions are in tools/). Next I want to [work further on the song / start the
> Windows VST3 edition / something else: describe it].
