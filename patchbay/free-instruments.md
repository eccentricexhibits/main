# Free Instruments for a Windows MIDI Player (VST3 + SoundFont)

_Researched 2026-10-27. Covers Windows 64-bit VST3 hosting (real-time playback) and General MIDI SoundFonts for the browser build._

> **How this was checked:** GitHub project pages (repos, releases, LICENSE files) were opened and read directly. Other vendor sites could not be opened from the research sandbox, so their pages were confirmed through search results on the vendor's own domain (e.g. `u-he.com`, `spitfireaudio.com`, `amplesound.net`). Each URL below goes to the developer's own site or repo. Third-party mirrors are left out. A size marked **≈ (est.)** is an estimate and was not confirmed. "n/s" means no official figure was found. Free terms change often, so check the license again before you bundle anything.

---

## Recommended starter pack (8)

These eight cover every category, and five of them need no account.

| # | Pick | Covers | Why | Account? |
|---|------|--------|-----|----------|
| 1 | **Surge XT** | Synth leads, pads, bass, FX | Open source (GPL-3.0), standalone VST3/CLAP, huge preset library, actively maintained | No |
| 2 | **Dexed** | FM electric piano, bells, FM bass, organ-ish tones | Open source (GPL-3.0) DX7 emulation. Plays the classic "80s EP" sound and loads any DX7 cartridge | No |
| 3 | **sfizz** + **Salamander Grand Piano** + **VSCO 2 CE** | Acoustic grand piano, chamber orchestra, orchestral percussion | sfizz is a BSD-2 SFZ player that you can embed or bundle. Salamander is CC BY 3.0 and VSCO 2 CE is CC0, so all three can ship with your app | No |
| 4 | **BBC Symphony Orchestra Discover** | Full orchestra (strings, brass, woods, perc) + concert grand | Most polished free orchestra (240 MB). Uses Spitfire's own plugin, not Kontakt | Yes (Spitfire) |
| 5 | **Splice INSTRUMENT** (former Spitfire LABS) | Soft Piano, Electric Piano, Strings, Choir, Electric Guitars, Drums, pads | All LABS sounds now live here. A single VST3 covers many GM gaps | Yes (free Splice login) |
| 6 | **MT Power Drum Kit 2** | Acoustic rock/pop drum kit | Standalone VST3, small (~60 MB), punchy kit, includes grooves | No (see notes) |
| 7 | **Ample Bass P Lite 4** (+ **Ample Guitar M Lite 4**) | Electric bass (Fender P), acoustic guitar (Martin D-41) | Free v4 versions released July 2026. VST3, no account | No |
| 8 | **HaNon B70** | Hammond B3 + Leslie organ | Free tonewheel organ in VST3 that needs no sign-up (no open-source VST3 organ was found) | No |

**No-account, bundle-safe core:** Surge XT, Dexed, OB-Xf, Odin 2, sfizz, and the CC0/CC-BY SFZ content (Salamander, VSCO 2 CE, Naked Drums, Black & Green Guitars). With these your installer can ship a working instrument set and needs no third-party logins.

---

## Sample-player hosts (needed by some picks)

| Host | Developer | Formats (Win x64) | License | Account? | Redistribute? | Official URL | Notes |
|------|-----------|-------------------|---------|----------|---------------|--------------|-------|
| **sfizz** 1.2.3 | SFZTools | VST3, LV2, AU | **BSD-2-Clause** (open source) | No | **Yes** (keep notice) | https://sfztools.github.io/sfizz/ · releases: https://github.com/sfztools/sfizz-ui/releases | Best choice to bundle, or to embed the sfizz C/C++ library directly in your host. Plays SFZ only (SF2 support not confirmed). Some ARIA-extension SFZ libraries may play imperfectly. |
| **sforzando** (~1.98x) | Plogue | VST3 (Win 10 x64+), AU, AAX, standalone | Freeware | No (direct download) | No (link out) | https://www.plogue.com/products/sforzando.html | Reference player for ARIA-flavoured SFZ (Salamander v3, Naked Drums, Karoryfer libraries). Also loads SF2, but is reportedly *not* 16-channel multitimbral for GM banks. |
| **Decent Sampler** (v1.30.x) | Decent Samples | VST, VST3, AAX, standalone | Freeware | **Yes**, it asks you to create an account on first launch | No | https://www.decentsamples.com/product/decent-sampler-plugin/ | Huge Pianobook ecosystem. Some libraries need a separate Pianobook account. |
| **Spitfire App** (for BBC SO Discover) | Spitfire Audio | Installs Spitfire's own VST3 plugin | Freeware | Yes | No | (see BBC SO Discover) | Not Kontakt. |
| **Splice INSTRUMENT** | Splice / Spitfire | VST3, AAX, standalone (~150 MB) | Freeware tier + paid sub | Yes (free Splice account, no subscription) | No | https://splice.com/instrument | Replaced the standalone Spitfire LABS plugin (Oct 2025). Existing LABS installs are auto-detected. |
| Kontakt Player | Native Instruments | VST3 | Freeware | Yes (Native Access) | No | — | **Less ideal**: heavy, account-bound, and libraries are locked to NI's ecosystem. Only one listed pick needs it (SSO Discover), and it is flagged. |

---

## 1. Keys & Piano (acoustic, electric, organ)

| Name | Developer | Sounds like | Format / host | License | Account? | Size | Redistribute? | Official URL |
|------|-----------|-------------|---------------|---------|----------|------|---------------|--------------|
| **Salamander Grand Piano v3** | Alexander Holm (SFZ by sfzinstruments) | Yamaha C5 concert grand, 16 velocity layers, 48 kHz/24-bit | SFZ: sforzando recommended (ARIA opcodes); test in sfizz | **CC BY 3.0** | No | ≈1+ GB (est.) | **Yes**, with attribution | https://github.com/sfzinstruments/SalamanderGrandPiano |
| **Dexed** (v1.0.1 stable; 1.1 in nightly) | Pascal Gauthier (asb2m10) | Yamaha DX7 FM: tine EPs, bells, glassy keys, FM bass | Standalone VST3 / CLAP, 64-bit | **GPL-3.0** (engine Apache-2.0) | No | ≈10 MB (est.) | **Yes** (GPL terms) | https://asb2m10.github.io/dexed/ · https://github.com/asb2m10/dexed/releases |
| **Splice INSTRUMENT: LABS Soft Piano / Electric Piano** | Spitfire Audio / Splice | Intimate felt upright; Rhodes-style EP | VST3 via Splice INSTRUMENT | Freeware | Yes | ~150 MB plugin + content | No | https://splice.com/instrument |
| **BBC SO Discover (concert grand)** | Spitfire Audio | Orchestral concert grand (included in Discover) | VST3 via Spitfire plugin | Freeware | Yes | 240 MB (whole library) | No | https://www.spitfireaudio.com/products/bbc-symphony-orchestra-discover |
| **Greg Sullivan E-Pianos** | Greg Sullivan (SFZ mapping: kinwie) | Yamaha CP80 electric grand, Hohner Pianet T, Wurlitzer EP200 | SFZ (ARIA ext., FLAC): sforzando / sfizz | **CC BY 3.0** | No | n/s | **Yes**, with attribution | https://github.com/sfzinstruments/GregSullivan.E-Pianos |
| **jRhodes3d** | Jeff Learman | 1977 Rhodes Mk I Stage 73, full-length samples, bell-forward EQ | SFZ (FLAC): sforzando | Samples **CC BY-NC 4.0**; music you make is CC0 | No | ~90 MB | **No** for commercial bundling (non-commercial only) | https://github.com/sfzinstruments/jlearman.jRhodes3d |
| **HaNon B70** (v1.5.x) | Lostin70s | Hammond B3 tonewheel (91 wheels) + Leslie 122 | Standalone VST3, 64-bit | Freeware | No | n/s | No | Lostin70s official site. Its domain could not be loaded for verification, so search "Lostin70s HaNon B70". Reports of high CPU use. |
| **Surge XT** (EP / organ presets) | Surge Synth Team | Synth EPs, drawbar-style organs | Standalone VST3/CLAP | GPL-3.0 | No | see Synths | Yes | https://surge-synthesizer.github.io/downloads/ |

_Also CC-licensed on sfzinstruments:_ Headroom Piano (Yamaha C3, CC BY 4.0), Osiris Piano (CC0), Karoryfer Scary Piano (CC0, Iowa samples). Browse them at https://github.com/sfzinstruments.
_Organ gap:_ no **open-source VST3** organ was found. setBfree (GPL-2.0) is excellent, but it ships as LV2 only.

---

## 2. Orchestral (strings, brass, woodwinds, choir)

| Name | Developer | Sounds like | Format / host | License | Account? | Size | Redistribute? | Official URL |
|------|-----------|-------------|---------------|---------|----------|------|---------------|--------------|
| **BBC Symphony Orchestra Discover** | Spitfire Audio | Full BBC SO at Maida Vale: 34 instruments, 47 techniques, one mix, plus concert grand | VST3 via Spitfire plugin (installed by Spitfire App) | Freeware (£0 "purchase") | **Yes** | 240 MB (360 MB during install) | No | https://www.spitfireaudio.com/products/bbc-symphony-orchestra-discover |
| **VSCO 2 Community Edition** (SFZ 1.1.0) | Versilian Studios (Sam Gossner) | Dry, intimate chamber orchestra: strings, brass, woodwinds, timpani/percussion, some keys | SFZ: sfizz / sforzando | **CC0 1.0** (public domain) | No | ≈3 GB full set (Versilian figure) | **Yes**, no conditions | https://versilian-studios.com/vsco-community/ · https://github.com/sgossner/VSCO-2-CE |
| **Virtual Playing Orchestra 3.3** | Paul Battersby | Full orchestra **including choir**, with "Standard" and "Performance" (legato/keyswitch) scripts | SFZ: sforzando recommended (sfizz works) | Mixed: CC0 + CC BY-SA 3.0/4.0 sources. Free redistribution with credit, no resale | No | ~603 MB samples + scripts | **Yes, free with credit.** BY-SA share-alike applies, and you may not sell it | https://virtualplaying.com/virtual-playing-orchestra/ |
| **Splice INSTRUMENT: LABS Strings / Frozen Strings / Choir / Amplified Cello Quartet** | Spitfire Audio / Splice | Cinematic ensemble strings, airy choir pads | VST3 via Splice INSTRUMENT | Freeware | Yes | content per pack | No | https://splice.com/instrument |
| **MTG Solo Sax** | Music Technology Group (UPF) | Soprano, alto, tenor and baritone saxophones (jazz/band woodwinds) | SFZ: sfizz / sforzando | **CC BY 4.0** | No | n/s | **Yes**, with attribution | https://github.com/sfzinstruments/MTG.SoloSax |
| **Ixox Flute** | Xavier Hosxe (SFZ port) | Solo concert flute | SFZ | **CC BY 4.0** | No | n/s | **Yes**, with attribution | https://github.com/sfzinstruments/Ixox.Flute |
| ⚠ **Spitfire Symphony Orchestra Discover** | Spitfire Audio | 44 instruments / 73 articulations from SSO (AIR Lyndhurst) | **Kontakt Player 7.5.2+**, flagged as less ideal | Freeware (email-subscriber offer) | Yes (+ mailing list) | ~5.7 GB (forum figure) | No | https://www.spitfireaudio.com/en-us/products/spitfire-symphony-orchestra-discover |

_Choir options:_ Virtual Playing Orchestra (bundle-able) and LABS Choir (account). No open-licensed standalone choir VST3 was found.

---

## 3. Synths & Electronic (leads, pads, bass)

| Name | Developer | Sounds like | Format | License | Account? | Size | Redistribute? | Official URL |
|------|-----------|-------------|--------|---------|----------|------|---------------|--------------|
| **Surge XT 1.3.4** | Surge Synth Team | Hybrid subtractive/wavetable/FM. Covers everything from supersaw leads to evolving pads to sub bass | Standalone **VST3 + CLAP** + standalone app, Win x64 (also 32-bit) | **GPL-3.0** | No | ≈45–60 MB (plugins-only zip ~43 MB) | **Yes** | https://surge-synthesizer.github.io/downloads/ |
| **Vital** (Basic tier) | Matt Tytel / Vital Audio | Modern spectral-warping wavetable. Produces EDM basses, plucks and huge pads | VST3/VST/standalone, Win 10+ | Source **GPL-3.0**. Official binary is a free tier. "Vital" is a trademark, and the free presets **cannot** be redistributed | **Yes** (free Vital account to download) | n/s | **No** for the official build. A GPL build you compile yourself must not be named Vital or use vital.audio services | https://vital.audio/ · source: https://github.com/mtytel/vital |
| **Dexed** | asb2m10 | DX7 FM basses, bells, digital pads | VST3/CLAP | GPL-3.0 | No | ≈10 MB (est.) | Yes | https://asb2m10.github.io/dexed/ |
| **OB-Xf** (beta) | Surge Synth Team (continuation of OB-Xd) | Oberheim OB-X: brassy poly pads, fat analog leads. Loads OB-Xd patches | Win x64/ARM64 EXE installer (Nightly). Format list not stated on the page, so confirm VST3 | **GPL-3.0** | No | n/s | **Yes** | https://github.com/surge-synthesizer/OB-Xf |
| **OB-Xd 2.20** (Aug 2026) | discoDSP (reales) | Same OB-X character, mature build | VST3, VST2, AAX, AU, LV2 | Freeware ("free for everything"). GPL-3.0 only up to v2.11, binaries only after that | No sign-up | n/s | Unclear, so link to it instead of bundling | https://github.com/reales/OB-Xd/releases |
| **Odin 2** (2.4.x) | TheWaveWarden | 24-voice semi-modular with Moog-ladder / Korg-35 style filters. Strong on basses and leads | VST3, CLAP, AU, LV2 | **GPL-3.0** | No | n/s | **Yes** | https://thewavewarden.com/pages/odin-2 · https://github.com/TheWaveWarden/odin2 |
| **TAL-NoiseMaker 5.0.6** | TAL Software | Low-CPU virtual analog with classic leads, basses and pads | VST, VST3, AU, AAX, CLAP (Win x64) | Freeware (closed source in current versions) | No | n/s | No | https://tal-software.com/products/tal-noisemaker |
| **Tyrell N6 3.0** ("2025 beta") | u-he | Juno-60-inspired poly: warm chords, soft pads, chunky bass | **VST3**, CLAP, AAX (Win x64) | Freeware (no serial) | No | n/s | No | https://u-he.com/products/tyrelln6/ |

---

## 4. Drums & Band (kits, guitars, bass, percussion)

| Name | Developer | Sounds like | Format / host | License | Account? | Size | Redistribute? | Official URL |
|------|-----------|-------------|---------------|---------|----------|------|---------------|--------------|
| **MT Power Drum Kit 2** (2.1.5.x, Apr 2026) | Manda Audio | Punchy, mix-ready acoustic rock/pop kit with groove library | Standalone VST3 / VST / AU / AAX | Freeware (donation reminders; one-time code shown on first run) | No | ~60 MB | No | https://www.powerdrumkit.com/ |
| **SSD 5.5 Free** | Steven Slate Drums | Polished rock kit (Deluxe 2 kit + extra snare, 3 presets) | Via Slate Audio Center. **VST3 for the free build was not confirmed** | Freeware (never-expiring "demo") | **Yes** | ~45 MB installer (2018 figure) + library | No | https://stevenslatedrums.com/ssd5/free |
| **Naked Drums** | Wilkinson Audio | Multi-mic studio kit (Yamaha Recording Custom), 10 round-robins, **GM-mapped preset** | SFZ: sforzando (stereo) / ARIA | **CC BY 4.0** | No | n/s | **Yes**, with attribution | https://github.com/sfzinstruments/WilkinsonAudio.NakedDrums |
| **Drumlabooh 13.0.0** | Peter Semiletov | Drum machine that loads Hydrogen and SFZ kits, ships with a large kit collection | VST3 (Win, NSIS installer), LV2 | **GPL-3.0** (kit licenses vary) | No | n/s | Plugin yes, check each kit | https://psemiletov.github.io/drumlabooh/ · https://github.com/psemiletov/drumlabooh/releases |
| **JDrummer 1.5** | Justin Ehrlichman | Open-source take on EZdrummer, ships with 28 SF2 kits, per-pad mix | VST3 (Win/Linux/mac) | **GPL-3.0** (kits mixed: AVL Drumkits CC BY-SA 3.0, others) | No | n/s | Plugin yes, check each kit | https://github.com/jmantra/jdrummer (new project with some reported bugs) |
| **99Sounds Drumplayer** | 99Sounds | 20 electronic/hybrid kits (trap, lo-fi, dubstep) | VST3 64-bit | Freeware | **Email** sign-up | n/s | No | https://99sounds.org/free-drum-vst/ |
| **Ample Guitar M Lite 4** (Jul 2026) | Ample Sound | Martin D-41 acoustic, fingerstyle, strummer engine | VST2/**VST3**/AU/AAX/standalone, Win 7–11 x64 | Freeware | No | n/s (separate sample library install) | No | https://www.amplesound.net/en/download.asp |
| **Ample Bass P Lite 4** (Jul 2026) | Ample Sound | Fender Precision bass, fingerstyle, slides/mutes, Riffer | VST2/**VST3**/AU/AAX/standalone, Win 7–11 x64 | Freeware | No | ~560 MB–982 MB (sources differ) | No | https://www.amplesound.net/en/download.asp |
| **Black & Green Guitars** | Karoryfer Samples (Brian Wood) | Gretsch Anniversary + Hofner Club **electric** guitars | SFZ: sforzando 1.971+ (download from Releases) | **CC0** | No | n/s | **Yes** | https://github.com/sfzinstruments/karoryfer.black-and-green-guitars |
| **Splice INSTRUMENT: LABS Electric Guitars / Drums / Percussion** | Spitfire / Splice | Multi-character electric guitars, indie drums, world percussion | VST3 via Splice INSTRUMENT | Freeware | Yes | content per pack | No | https://splice.com/instrument |

_More bundle-safe band/percussion content:_ Karoryfer **Black and Blue Basses** (CC0, https://github.com/sfzinstruments/karoryfer.black-and-blue-basses), **VSCO 2 CE** percussion (CC0), jlearman **SteelDrum** (Unlicense), DrumGizmo DRS/Muldjord kits as SFZ (CC BY 4.0), all under https://github.com/sfzinstruments.

---

## General MIDI SoundFonts (browser version, or a GM fallback in the VST host)

| SoundFont | Format & size | License | Bundle / redistribute? | Official source | Notes |
|-----------|---------------|---------|------------------------|-----------------|-------|
| **GeneralUser GS 2.0.3** (2026-02-22) | .sf2, 30.8 MB (~30.7 MB RAM); 261 presets + 13 kits | Custom permissive "License v2.0" (S. Christian Collins) | **Yes**: private, commercial and software-project use are allowed. Host your own copy and **don't hotlink** the author's files. The author can't guarantee where every sample came from | https://www.schristiancollins.com/generaluser · https://github.com/mrbumpy409/GeneralUser-GS | Best-sounding small GM/GS bank. It depends on modulators, and the author says **SpessaSynth** (web) plays every preset correctly. For FluidSynth-class engines there is a legacy "SoftSynth" build (1.44) |
| **MuseScore_General** (0.2) | .sf3 35.9 MB / .sf2 208 MB | **MIT** (some parts PD/CC0) | **Yes**, keep the copyright/acknowledgement notices | https://ftp.osuosl.org/pub/musescore/soundfont/ | Collins' rework of FluidR3Mono. The SF3 is ideal for the web |
| **MS Basic** (MuseScore 4 default) | .sf3, 48.9 MB | **MIT** (lineage FluidR3 → FluidR3Mono → MuseScore_General) | **Yes**, keep notices | https://github.com/musescore/MuseScore/tree/master/share/sound | The most recently maintained of the FluidR3 family |
| **FluidR3_GM** / **FluidR3Mono_GM** | GM .sf2 ≈145 MB installed; Mono .sf3 22.6 MB | **MIT** (Frank Wen; Mono by Michael Cowgill) | **Yes** | https://packages.debian.org/sid/fluid-soundfont-gm · Mono .sf3: https://github.com/musescore/MuseScore/tree/master/share/sound | The classic fully-GM reference bank, and the safest license |
| **TimGM6mb** | .sf2, 5.7 MB | **GPL-2.0** | Yes, under GPL terms (include license text; shipping it alongside your app counts as aggregation) | https://packages.debian.org/sid/timgm6mb-soundfont | Tiny. Good as an instant-load web fallback, lower fidelity |

**Browser tips:** SF3 is Vorbis-compressed, so your web synth must decode it (SpessaSynth does). A good default is MuseScore_General.sf3 or MS Basic.sf3, with TimGM6mb as a quick-start fallback. GeneralUser GS is the sound-quality upgrade.

---

## Licensing notes (read before bundling)

1. **GPL plugins** (Surge XT, Dexed, OB-Xf, Odin 2, Drumlabooh, JDrummer). Your installer may ship the unmodified binaries if you include the license and offer the corresponding source (a link to the upstream tag is the usual practice). Loading a GPL plugin at runtime does not make your host GPL. If you **modify** one of them, your changes must also be released under the GPL.
2. **The VST3 SDK has been MIT since VST 3.8 (Oct 2025)**, so a closed-source host can implement VST3 freely. The ASIO SDK is separate (GPLv3 or proprietary).
3. **sfizz is BSD-2-Clause.** You can embed libsfizz directly in your player to give it SFZ support, then ship the CC0/CC-BY libraries listed above as built-in instruments.
4. **Creative Commons content.** CC0 (VSCO 2 CE, Karoryfer) has no conditions. CC BY (Salamander, Naked Drums, Greg Sullivan EPs, MTG Sax) requires a credits screen. CC BY-SA (parts of Virtual Playing Orchestra, AVL Drumkits) means modified sample sets must stay BY-SA. **CC BY-NC** (jRhodes3d) is not allowed in a commercial product.
5. **Freeware is not redistributable.** This covers Vital official builds, OB-Xd 2.20, TAL-NoiseMaker, Tyrell N6, sforzando, Decent Sampler, Spitfire/Splice, MT Power Drum Kit, SSD, Ample, 99Sounds and HaNon. Treat each as "user downloads it from the developer", and have your app scan the standard VST3 folder (`C:\Program Files\Common Files\VST3`).
6. **Vital trademark.** The GPL source can be rebuilt, but the build can't be called "Vital", can't connect to vital.audio, and can't include the free presets.
7. **Account-bound picks.** BBC SO Discover (Spitfire), Splice INSTRUMENT (Splice), Vital (download), SSD 5.5 Free (Slate), Decent Sampler (first launch), Drumplayer (email), and SSO Discover (Kontakt/Native Access, which is also the least ideal host).

## Changed, discontinued, or excluded

- **Spitfire LABS (standalone plugin)** has been folded into **Splice INSTRUMENT** since Oct 2025. Old projects still load the LABS plugin, but new users should install INSTRUMENT.
- **Ample "Lite II" versions** have been superseded by the free **Lite 4** releases (July 2026).
- **OB-Xd** stopped being open source after v2.11. The open-source line continues as **OB-Xf**.
- Excluded:
  - **Shreddage 3 Stratus Free**: needs Kontakt Player.
  - **setBfree**: LV2 only.
  - **Spicy Guitar**: VST2/AU only per its listings.
  - **BassMIDI VSTi**: VST2 only.
  - **Keyzone Classic** and **Sound Magic Piano One**: free status and downloads unclear, with reports of a broken v7 download.
