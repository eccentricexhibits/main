# Digital Performer session decode: "DrasticMeasures-New Songs"

The session document was made with MOTU Digital Performer 3.1.1. DP's file
format is not publicly documented, so everything below was worked out from
the bytes and then **checked against the audio**. Each finding carries a
confidence label.

## 1. What the session file contains

| Region (offset) | Contents | Decoded? |
|---|---|---|
| `0x00000`–`0x2C000` | Undo history ("Record on Track 'vox-IBelieve'", "Nudge Selection in Track 'Baby Dolls'", …) | Names only |
| `0x30000`–`0x3B000` | Take files and audio file references (with full original paths on "LaCie d2 78 GB") | Yes |
| `0x3B200`–`0x3C000` | **Soundbite table**: 25 soundbites | **Yes** (see §2) |
| `0x4BF00`–`0x8A000` | **Sequences ("chunks")**: one per song, each followed by packed event data | Names and structure only |
| `0x8A000`–`0x8FC00` | **Track list**: names, inputs and outputs, plug-ins | Yes (see §3) |
| `0x91600`–`0x92400` | MIDI devices: E-mu Orbit V2, Roland JV-880, E-mu ESI-32, SampleCell, Casio CZ-101, Roland A-50 | Yes |
| `0xA9900`–`0xB08A1` | MOTU plug-in list plus DP's drum-pattern library | Yes |

Sequences found: `piano-Sweetheart-107bpm`, `JehovasDaughter-keys-117`,
`WarIsPeace-160`, `IBelieve-104`, `30'sGermanNightclub-79`, `WarIsPeace-79-`,
`piano-Sweetheart`, `piano-layw/me`.

## 2. Soundbite table (decoded)

Each record has: name, linked audio file, length (samples, 64-bit big-endian),
soundbite ID, **time stamp** (samples from sequence start; mislabelled "sync"
in my first pass), trim offset, the **tempo at recording** (stored as
360,000,000 ÷ BPM), and a recording-pass ID that is identical for takes
recorded together. The full table is in `soundbites.json`.

How the time-stamp field was verified:
* `I Believe` (76,327) vs `vox-IBelieve-9` (16,860) predicts −1.348 s. Audio
  correlation gives −1.347 s.
* `30'sGermanNightclub` (117,228) vs `vox--11` (0) predicts −2.658 s. Audio gives −2.657 s.
* `WarIsPeace` (181,913) vs `Untitled-7` (0) predicts −4.125 s. Audio gives −4.11 s.
* Trimmed sub-regions shift their stamp by exactly the trim
  (`Teddy Bears Live*` +333,825; `vox--11.2` +572,271), and `vox-1-3`'s stamp
  equals the length of `vox-1-2.2`, the punch-in point.

| Soundbite (file) | Tempo | What it is | Real performance? |
|---|---|---|---|
| I Believe (`I Believe-0.L/R`) | 104 | Stereo mix = CD track 9 | yes |
| vox-IBelieve-9 | 104 | Lead vocal **used in the CD mix** | yes |
| vox-IBelieve-8 | 104 | Alternate vocal, first 95 s | yes |
| 30'sGermanNightclub (`I Believe copy-2.L/R`) | 79 | Stereo mix = CD track 8 | yes |
| vox--11 / vox--11.2 | 79 | Lead vocal **used in the CD mix** | yes |
| vox--10 | 79 | Alternate opening line (9 s) | yes |
| WarIsPeace (`WarIsPeace-1.L/R`) | 160 | Stereo mix = CD track 10 | yes |
| Untitled-7 | 160 | Headphone bleed only (peaks at −39 dBFS) | no |
| Teddy Bears Live-0 / Teddy Bears Live* | 79 | Stereo live mix; the CD uses the trimmed version | yes |
| Baby Dolls | n/a | Stereo mix = CD track 1 (from the Selections folder) | yes |
| bass-layw/me-0 | n/a | New bass part for Lay W/Me (D#1–G#2) | yes |
| vox..WarIsPeace-79 (`Untitled-12`) | 79 | **Bass** part (D1–G#2) for a 79 bpm WarIsPeace version, despite the name | yes |
| 2-13 + Untitled-1 | 79 | One pass, two inputs (bass DI plus mic, or bass plus second instrument), 5:17 | yes |
| bass-0 + vox-1-5 | 117 | Bass and vocal sketch for the Jehovas' Daughter keys sequence, 1:28 | yes |
| vox-JD copy-6 + bass-JD copy-1 | 167 | 6 s, silent | no |
| vox-1-0 … vox-1-4, vox-1-2.2 | 82–107 | Near-silent (peaks at −40 to −55 dBFS) | no |

## 3. Track list and processing (decoded)

Audio tracks: vox-JehovasDaughter, vox-IBelieve, vox-30'sGermanNightclub,
vox..WarIsPeace-79-, vox-Sweetheart-79, aco-1, bass-JehovasDaughter,
bass-Sweetheart, bass-layw/me, Teddy Bears Live, I Believe, WarIsPeace,
30'sGermanNightclub, I Believe copy (×2) and Baby Dolls. Plus Aux-1/2-dly
(MOTU Delay, stereo) and Aux-3/4.
* The vocal tracks use **MOTU Dynamics (mono)**. vox-IBelieve and
  vox-30'sGermanNightclub also use **ParaEQ 8-band**, with band gains of
  −4.33 dB and −3.33 dB.
* Inputs come from a MOTU 2408 (Analog-C 1–8) and a 1224 (Analog-A); there are
  ADAT returns and ReWire returns from Reason, ReBirth and Ableton Live.

## 4. What could not be decoded: the event streams

Each sequence's notes and soundbite placements are stored in a packed stream.
Note events are visible: a time unit, then a length unit, then the note number
and velocity (e.g. Sweetheart piano notes C#4–B4, velocities 106–127). The
time and length values use a variable-length number encoding: the first byte
sets the length (`5D`/`61` = 3 bytes, `8B` = 4, `94`–`98` = 5, `B5`–`BC` = 6,
`CE`–`D4` = 7, `DF`–`E1` = 8), and the payload format is still unknown.
Consequences:
* **MIDI parts are not recoverable yet.** That covers the keys, piano and drums
  played on the Orbit V2, JV-880 and similar. They were never recorded as
  audio, and they are the backing for the new arrangements (Lay W/Me, the
  Sweetheart 107 version, the Jehovas' Daughter keys sequence, WarIsPeace-79).
* Audio placement relies on time stamps plus audio verification instead. Time
  stamps were wrong (stale) for two takes: `vox-IBelieve-8` and `vox--10`
  were placed from audio alignment instead (correlation 0.32 against the sister
  take; 6.5σ above chance against the mix).

The most reliable way to recover the MIDI parts is to open the session in a
working copy of Digital Performer and export standard MIDI files.

## 5. Reconstruction results

* **Aligned stem sets** for I Believe and 30's German Nightclub: the mix, the
  lead vocal and the alternate vocal, all starting at the same instant.
* **Vocal-up and vocal-down (±3 dB) mixes** for both. I built a model of the
  in-mix vocal from the vocal take (fixed FIR filter, coherence 0.6–0.8) and
  added or subtracted a fraction of it.
* **Full vocal removal / instrumental is not achievable cleanly.** The vocal
  in the mix went through a compressor and a delay. Static subtraction removes
  about 3 dB overall (−8 to −11 dB above 2.5 kHz), and a time-varying model
  starts removing instruments too. Replacing the lead vocal with an alternate
  take is therefore not possible without leaving the original audible
  underneath.
* **Remaster** of all 11 Selections mixes: 20 Hz high-pass, gain to −14 LUFS,
  4× oversampled peak limiting to −1 dBTP (between 0 and about 3.9 dB of
  limiting on the loudest transients), and TPDF dither to 16-bit. No EQ or
  compression, because no one listened during processing. The original
  spread was −10.4 to −18.2 LUFS; after processing every track is
  −14.0 ±0.1 LUFS.
