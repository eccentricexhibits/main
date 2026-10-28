# Free instruments and effects for the electronic arrangement

_Researched 2026-10-28. This adds to `free-instruments.md` (Surge XT, Vital, Dexed, OB-Xf,
Odin 2, TAL-NoiseMaker, Tyrell N6 and the rest) and doesn't repeat it._

The goal is more richness and tonal complexity in **Wasting My Time (electronic)**
(`songs/wasting-my-time-electronic/`).

## What each part could use

The built-in GeneralUser GS sounds are single samples with fixed envelopes. Most of the
richness a real electronic production has comes from three things this bank can't do:
- moving timbre (wavetables, filters, granular)
- detuned and chorused layers
- effects: big reverbs, tape and saturation, multiband "sheen"

Once the Windows edition hosts VST3s, these are the natural upgrades:

| Part (row in Patchbay) | Now (GeneralUser GS) | Upgrade, bundle-safe first | Why |
|---|---|---|---|
| Lead (hook), Saw stack | Saw Lead, Bright Saw Stack | **Surge XT** or **Vital** supersaw + **Valhalla Supermassive** + **Xfer OTT** (light) | A real 7-voice detuned saw with filter movement, plus width and shimmer |
| Lead (verse tune) | Chiffer Lead | **Zebralette 3** (spectral) or **Surge XT**, + **CHOW Tape Model** | A breathing, slightly wobbly tone suits the melancholy |
| Pad (bridge wall), Choir pad | Solar Wind, Space Voice | **Vaporizer2** (wavetable/additive), **PaulXStretch** on the choir stem, **Surge XT Effects: Nimbus** | Slowly evolving, PADsynth-like spectra: the lushness of the string bridge, in synth form |
| Pad (warm), Pad (pumping) | Warm Pad, Synth Strings 4 | **OB-Xf** / **Tyrell N6** + **TAL-Chorus-LX**; pumping with **gate-12** | Analog-style poly pads with Juno chorus; smooth sidechain instead of stepped CC11 |
| Gated pad | Polysynth, chopped notes | **gate-12** on a sustained pad | A smooth, sample-accurate trance gate |
| Pluck, Bells | Synth Mallet, Crystal | **Six Sines** (FM), **RipplerX** (physical modelling), **ChowMatrix** delays | Inharmonic, struck tones that subtractive synths can't make |
| E-piano | Chorused Tine EP | **Dexed** (DX7 EP) or **Six Sines** + **TAL-Chorus-LX** | The classic chorused FM e-piano |
| Sub bass, Saw bass | Sine Wave, Mean Saw Bass | **Odin 2** / **Surge XT**; **TDR Nova** for frequency-only ducking | Ducks only the lows under the kick, keeps the bass's bite |
| Kick, Snare · Clap, Hats | 808/909 kit | **Geonkick** (a kick tuned to D), **ChowKick**, **BP-909** samples | Kick and sub in tune; real 909 hats and claps |
| Riser, Reverse cymbal | White Noise Wave + pitch bend | **Cardinal** (noise + filter modules), **Valhalla Freq Echo** | Filtered, modulated sweeps instead of a bent noise sample |
| Whole mix | master compressor | **Airwindows Consolidated** (console + ToTape), **Dragonfly Reverb** | Analog glue and a better shared reverb |

**Today, in the browser edition**, without the Windows build:
- **The FreePats synth SoundFonts and the Electric & Synthesizer Percussion kit** are CC0,
  so they can be bundled. Their pads were rendered from ZynAddSubFX, so they bring PADsynth
  textures into the browser.
- They're single-instrument `.sf2` files. Add them with "Add .sf2" and assign them to the pad
  rows, or merge them into one bank with Polyphone.
- Other banks (Arachno, Timbres of Heaven, SGM) sound good but can't be bundled; see the
  exclusions below.

## Recommended electronic starter pack

| # | Item | Licence | Account? | Bundle? |
|---|---|---|---|---|
| 1 | Vaporizer2 3.5.0: wavetable/additive pads | GPL-3.0 | No | Yes |
| 2 | Six Sines 1.2.1: FM bells, EP, plucks | MIT | No | Yes |
| 3 | RipplerX 1.5.19: physical-modelling bells and perc | GPL-3.0 | No | Yes |
| 4 | Geonkick 3.9.0: tuned kicks and synth drums | GPL-3.0 | No | Yes |
| 5 | gate-12 1.3.3: trance gate and sidechain pumping | GPL-3.0 | No | Yes |
| 6 | CHOW Tape Model 2.11.4 (or Airwindows Consolidated, MIT) | GPL-3.0 | No | Yes |
| 7 | Valhalla Supermassive (or Dragonfly Reverb, GPL) | Freeware | No | Link only |
| 8 | Xfer OTT 1.37 | Freeware | No | Link only |
| + | FreePats synth SF2s + Electric Percussion (browser edition) | CC0 | No | Yes |

---

## The full research

**Verification key** (the "Checked" column):
- **GH**: confirmed on the project's own GitHub repo or release page (version, date and Windows asset seen).
- **OFF**: confirmed only from search-engine snippets of the developer's own page. The page itself could not be fetched from this session.
- **3P**: confirmed only from third-party press or listings (KVR, BPB, Synthanatomy, Rekkerd and similar). Treat these as provisional.

**Redistribution shorthand**:
- **GPL**: can be redistributed. You must ship the licence and offer the source. Shipping it as a separate plugin file next to your host is normally treated as aggregation, but get your own legal check.
- **MIT/BSD**: permissive. Keep the copyright notice.
- **Freeware EULA**: free to use, but it cannot be bundled or re-hosted without the developer's written permission. Link to the developer's download page instead.


## A. Synths that add tonal complexity

| Name | Developer | Version (date) | What it adds to this arrangement | Windows formats | Licence | Account? | Redistributable? | Checked | Official URL |
|---|---|---|---|---|---|---|---|---|---|
| **Vaporizer2** | VAST Dynamics | 3.5.0 (2024-03-02) | Hybrid wavetable + additive + granular/sampling engine (780+ wavetables, 410+ presets). Good for the **evolving bridge pad wall**: slow wavetable-position and spectral morphs under the supersaw. Its additive/"spectral" modes give a PADsynth-like shimmer for the choir-pad layer. | VST3, VST2, CLAP, AAX, standalone (64-bit installer zip, 402 MB) | GPL-3.0 (open-sourced 2023) | No | Yes (GPL) | GH | https://github.com/VASTDynamics/Vaporizer2 |
| **Zebralette 3** | u-he | 3.0 final (released mid-Dec 2025) | "Zebra 3 lite" spectral-wavetable oscillator (one oscillator, spectral effects, complex modulation). Use it for **glassy evolving pads and bell-like spectral leads** that sit above the supersaws, and for "breathing" pad textures in the verses. Arguably the best-sounding free synth released in the last year. | VST3, CLAP, AAX (64-bit) | Freeware EULA | Not confirmed (u-he introduced a new licensing system alongside it; reported as having no subscription and no online requirement) | No | 3P (+OFF for "free from u-he website") | https://u-he.com/products/zebralette3/ |
| **Six Sines** | BaconPaul (Surge Synth Team developer) | 1.2.1 (2026-07-20) | 6-op PM/AM/FM synth (TX81Z-style, MPE) with CZ-style phase distortion added in 1.2. Good for **FM bells, DX-style e-piano layers and the arpeggiated glassy plucks**. Sits well against Dexed, with a more modern mod matrix. | VST3, CLAP, standalone (Windows .exe/.zip); AU on macOS | MIT | No | Yes (MIT) | GH | https://github.com/baconpaul/six-sines |
| **RipplerX** | tiagolr | 1.5.19 (2026-06-13) | Physical-modelling (modal) synth in the AAS Chromaphone/Collision style, with 9 resonator models (beam, marimba, plate, membrane, tubes and more). Gives **real "struck" bells, mallet plucks for the arp, and metallic percussion hits** with inharmonic richness that subtractive synths can't produce. | VST3, LV2 (CLAP planned) | GPL-3.0 | No | Yes (GPL) | GH | https://github.com/tiagolr/ripplerx |
| **Cardinal** | DISTRHO (VCV Rack fork) | 26.02 (2026-02-28) | Self-contained modular rack with Audible Instruments (Mutable Instruments Plaits/Rings/Clouds-style macro-osc, resonator and granular), Surge XT modules, Bogaudio and Valley. Use it for **granular "Clouds" textures on the riser/breakdown, Rings resonator pads, and generative arps**. Three variants: Main, Synth, FX. | VST3, VST2, CLAP (work in progress), LV2; win64 installer | GPL-3.0-or-later (some panel artwork is CC-BY-NC-SA or custom-licensed) | No | Yes (GPL code). Artwork terms vary: check `docs/LICENSES.md` before bundling. | GH | https://github.com/DISTRHO/Cardinal |
| **plugdata** | plugdata team | v0.9.3-2 (2026-03-05) | Pure Data (plus ELSE/cyclone) inside a plugin. Use it for **custom granular, spectral or randomised generators**, for example a bespoke trance-gate or arp generator tied to the 156 BPM grid. It is more of a sound-design workshop than a preset synth. | VST3, LV2, CLAP, standalone (Win64 .msi) | GPL-3.0 source; compiled app AGPL-3.0 (JUCE) | No | Yes (GPL/AGPL) | GH | https://github.com/plugdata-team/plugdata |
| **PaulXStretch** | Sonosaurus / essej | 1.6.0 (2022-06-16) | Extreme spectral time-stretch, playable as an instrument. Feed it the song's own choir or e-piano stem to create **huge frozen ambient pads for the intro and the bridge "wall"**. This is the closest free Windows tool to PADsynth-style smear. | VST3, standalone (Windows .exe) | GPL-3.0 | No | Yes (GPL) | GH | https://github.com/essej/paulxstretch |
| **Tunefish 4** | Brain Control | 4.2.0 (VST3 added; 4.3.0 beta reported) | Additive-flavoured virtual-analog synth that is tiny and CPU-light. Gives **thick additive supersaw-ish leads and pads** as a cheap layer. | VST3 (from 4.2.0), VST2 | GPL-3.0 | No | Yes (GPL) | GH (licence, source) / 3P (version, VST3) | https://github.com/paynebc/tunefish |
| **Pendulate** | Newfangled Audio / Eventide | n/a (2020 release) | Chaotic double-pendulum oscillator with a Buchla-style wavefolder and low-pass gate (monosynth). Good for **gritty mid-bass and evolving drone/riser layers**. | VST3, AU, AAX (64-bit) | Freeware EULA | Yes: email form, plus iLok account/License Manager reported for authorisation | No | 3P | https://www.eventideaudio.com/plug-ins/pendulate/ |
| **Arturia Analog Lab Play** | Arturia | n/a (launched 2023-10-31) | 100 presets drawn from V Collection and Pigments. A **quick source of "classic" pads, keys and polysynths** to audition, but with very little editing. | VST, VST3, AU, AAX | Freeware EULA | **Yes**: My Arturia account plus Arturia Software Center activation (confirmed on Arturia support) | No | OFF (support article) | https://www.arturia.com/products/software-instruments/analoglab/free |
| **Monique** | Surge Synth Team (ex-Monoplugs) | Nightly only (latest build 2024-08-07) | Unusual morphing monosynth. Good for **evolving mono mid-bass and lead lines**. | VST3 / CLAP (Windows 64-bit nightly setup.exe) | GPL-3.0 + MIT dual | No | Yes | GH (nightly assets) | https://github.com/surge-synthesizer/monique-monosynth |

**Already on the list, still the core:** Surge XT and Vital are the supersaw and wavetable workhorses, and OB-Xf/Odin 2 cover the analog-modelled polysynth role. None of the new picks replace them. They add the spectral, FM, physical-modelling and granular colours those synths lack.

### Flagged in group A
- **ZynAddSubFX / Zyn-Fusion (PADsynth)**: the engine is GPL-2.0+ and free as source, but **official Windows Zyn-Fusion 3.0.x binaries are paid** ("Demo / Full Release 45+ USD"). The demo goes silent after 10 minutes. The free official Windows download is an old 2.x build, which is VST2-era. There are no free official Windows VST3 builds. **Workaround:** the FreePats CC0 synth SF2s (group D) were rendered *from* ZynAddSubFX/Yoshimi, so the browser edition can get PADsynth-style pads anyway. (Verified via search snippets of zynaddsubfx.sourceforge.io; the site itself was unreachable.)
- **Helm** (Matt Tytel): the GitHub repo was **archived on 8 Feb 2025** and is read-only. The last version is 0.9.0 (July 2017), listed as discontinued. KVR lists a Windows VST3 path, but there are reports of a broken GUI on hi-DPI Windows 11. Vital supersedes it, so skip it.
- **Synth1** (Daichi): only 64-bit **VST2** found (1.13 beta line). There is no confirmed Windows VST3, so it is **excluded for the VST3 host**.
- **Kilohearts**: it has no free synth (Phase Plant is paid). Only the effects (Essentials) are free.
- **Cloud Seed 2** (Ghost Note Audio): see group C. Its core DSP is MIT, but the plugin is now commercial.

---

## B. Electronic drums and percussion synths

| Name | Developer | Version (date) | What it adds to this arrangement | Windows formats | Licence | Account? | Redistributable? | Checked | Official URL |
|---|---|---|---|---|---|---|---|---|---|
| **Geonkick** | Iurie Nistor / Quamplex | 3.9.0 (2026-10-06) | Percussion synthesizer: kicks, snares, claps, hats, 16-instrument kits. Lets you design a **tuned kick in D (or F) so the kick and sub don't fight**, plus synth claps and zaps for the 909-style groove. | VST3, LV2 (free "basic" Windows installer on GitHub; paid ready-to-run builds also sold) | GPL-3.0+ | No (GitHub "basic" build) | Yes (GPL) | GH | https://github.com/Geonkick-Synthesizer/geonkick |
| **ChowKick** | Chowdhury DSP | 1.2.0 (2023-01-16) | Circuit-modelled 808/909-style kick: pulse into a resonant filter, pitch can track the MIDI note. Gives a **boomy 808 kick that can be pitched to the song's root**, layered under a sampled 909 click. | Windows 64-bit installer (ChowKick-Win-64bit-1.2.0.exe); VST3 expected as with all Chow plugins, exact format list not shown on GitHub | BSD-3-Clause | No | Yes (BSD) | GH (version/asset), formats unverified | https://github.com/Chowdhury-DSP/ChowKick |
| **RipplerX** (see A) | tiagolr | 1.5.19 | Membrane and drumhead models give **tom fills, metallic perc and tuned "pings"** for the build-ups. | VST3, LV2 | GPL-3.0 | No | Yes | GH | https://github.com/tiagolr/ripplerx |
| **BP-909** | Bipolar Audio | n/a (Dec 2024) | Sample-based 909 drum machine. The **classic 909 hats, claps and open-hat offbeats** a trance-ish 156 BPM groove needs. A WAV pack is included, which you could load into sfizz or Decent Sampler. | VST3, VST2 (Windows only; Mac "coming soon") | Freeware (licence text not found) | Not stated | Unknown: assume no | 3P | https://www.kvraudio.com/product/bp-909-by-bipolar-audio |
| **SampleScience RC909 Pro** | SampleScience | v1.1 | Sample-based 909 with 19 kit variations and built-in distortion, tape and sub. **Free only until 31 Oct 2026** with coupon `FREE909DRUMS` (normally $30). | VST3, VST, AU (64-bit) | Commercial EULA (free promo) | Gumroad checkout (email) | No | 3P (deal and press reports) | https://samplescience.gumroad.com/l/rc909pro |
| **808XD** | Audiolatry | n/a (Oct 2022) | 808 bass ROMpler (31 presets, from saturated to clean). Fills the **sub-bass/808 slot under the drop** when you want trap-style glide 808s rather than a pure sine sub. | VST3 (Windows); VST3/AU (macOS) | Freeware | Gumroad, €0 with coupon `FREE` (email) | No | OFF (Gumroad listing snippet) | https://audiolatry.gumroad.com/l/808xd |
| **Cardinal drum modules** (see A) | DISTRHO | 26.02 | Bogaudio and Surge drum and noise modules give **noise-sweep risers, snare rolls and white-noise uplifters** with modulated filters. | VST3 etc. | GPL-3.0+ | No | Yes | GH | https://github.com/DISTRHO/Cardinal |
| **FreePats Electric and Synthesizer Percussion** | FreePats project | 2022-07-18 | Vintage-analog-style drum kit made with Geonkick and Yoshimi. It is **bundle-safe**: an SFZ version (sfizz, Windows edition) and an SF2 version (browser edition) are both available. | SF2 (~1.0–1.6 MiB), SFZ/WAV, Hydrogen | CC0-1.0 | No | **Yes (public domain)** | OFF (snippet of freepats.zenvoid.org) + GH (FreePats org repo `synthesizer-percussion`, CC0) | https://freepats.zenvoid.org/Percussion/electric-percussion.html |

### Flagged in group B
- **Sitala** (Decomposer): the **free version (1.0) has no VST3**. It is VST2/AU/AAX/standalone only. VST3 arrived in the **paid** Sitala 2.x ($20). It is excluded for the VST3 host unless you buy it.
- **DR.89** (Sender Spike, May 2026): fully synthesized 909-style machine, but **VST2 only, Windows 64-bit**. No VST3 is listed. Flag it.
- **TS-808** (Tactile Sounds): only 32-bit VST2 is confirmed. Excluded.
- **BazzISM** (kick synth): the unregistered version has limitations (trialware), so it is not truly free. Excluded.

---

## C. Effects that add richness

| Name | Developer | Version (date) | What it adds to this arrangement | Windows formats | Licence | Account? | Redistributable? | Checked | Official URL |
|---|---|---|---|---|---|---|---|---|---|
| **Valhalla Supermassive** | Valhalla DSP | 5.0 (adds "Sirius" mode) | Huge modulated delay/reverb hybrids. Gives the **"anthemic" depth on the supersaw lead, infinite shimmer tails on the choir pad, and washed-out throws into the breakdown**. This is the single biggest richness upgrade for free. | VST2, VST3, AAX (64-bit) | Freeware EULA | No (no registration reported) | No | OFF / 3P | https://valhalladsp.com/shop/reverb/valhalla-supermassive/ |
| **Valhalla Space Modulator** / **Freq Echo** | Valhalla DSP | n/a | Space Modulator: flanger/doubler that **widens plucks and adds jet sweeps on risers**. Freq Echo: frequency-shifted delay for **dub-style rising feedback in transitions**. | VST/VST3/AU/AAX (Space Mod confirmed; Freq Echo VST3 not confirmed) | Freeware EULA | No | No | 3P | https://valhalladsp.com/product-category/modulation/ |
| **Dragonfly Reverb** | Michael Willis | 3.2.10 (23 Apr, year not shown) | Hall, Room, Plate and Early Reflections plugins (Freeverb3-based). An **open-source alternative to Supermassive: a plate on the snare and clap, a hall on the pads**. Choose it when you need something bundle-safe. | Win64 zip (VST2/VST3/LV2; CLAP not confirmed) | GPL-3.0 | No | Yes (GPL) | GH | https://github.com/michaelwillis/dragonfly-reverb |
| **TAL-Reverb-4** | TAL Software | 4.0.4 | Lush 80s plate-style algorithmic reverb with modulation. Gives **vintage-sounding pad and e-piano space** and is cheaper on CPU than Supermassive. | VST3, CLAP, AAX (VST2/AU on other platforms) | Freeware EULA | No (no registration) | No | OFF / 3P | https://tal-software.com/products/tal-reverb-4 |
| **TAL-Chorus-LX** | TAL Software | 1.6.3 | Juno-60 chorus emulation (modes I, II, I+II). Gives the **classic warm stereo spread on pads, e-piano and arp plucks**. It is the quickest way to make a dry saw pad sound "expensive". | VST3, CLAP, AAX | Freeware EULA | No | No | 3P | https://tal-software.com/products/tal-chorus-lx |
| **CHOW Tape Model** | Chowdhury DSP | 2.11.4 (2023-11-05) | Physical model of reel-to-reel tape (saturation, wow/flutter, loss). Gives **tape glue on the drum bus, gentle saturation and wobble on the lead and pads** (melancholic lo-fi colour in the verses). | VST3, VST2, CLAP, AAX (Win 64-bit installer) | GPL-3.0 | No | Yes (GPL) | GH | https://github.com/jatinchowdhury18/AnalogTapeModel |
| **Airwindows Consolidated** | Chris Johnson (Airwindows), packaged by BaconPaul | Rolling build 2026-10-24 (dcf98a3) | All ~400+ Airwindows effects in one plugin: console emulations, tape, Density/saturation, Pafnuty, reverbs, wideners. Gives **subtle harmonic richness on every bus**, for example a console plugin on all synth buses and "ToTape" on the master. | VST3, CLAP, LV2, standalone (Win x64 setup.exe/zip, ARM64EC, Win7 builds) | MIT (builds pull in GPL3 JUCE/VST3 deps) | No | Yes | GH | https://github.com/baconpaul/airwin2rack |
| **Xfer OTT** | Xfer Records | 1.37 | Aggressive upward/downward 3-band compression. Gives the **"EDM sheen" on supersaws, plucks and risers**. Use it at 20–40 % depth for richness and 100 % for an in-your-face drop. | VST3 (since 1.33), VST2, AAX | Freeware EULA | No | No | OFF (snippet of xferrecords.com/freeware) | https://xferrecords.com/freeware |
| **gate-12** | tiagolr | 1.3.3 (2026-01-21) | Trance-gate / volume shaper in the GrossBeat/ShaperBox mould, with **sidechain input triggering**. Covers both jobs: **16th-note trance-gated pads and kick-triggered sidechain pumping** on pads and bass. | VST3, LV2 (CLAP planned) | GPL-3.0 | No | Yes (GPL) | GH | https://github.com/tiagolr/gate12 |
| **Kilohearts Essentials** | Kilohearts | n/a (30+ plugins) | Includes **Trance Gate** (sequenced gate), Chorus, Ensemble, Haas, Phaser, Transient Shaper, Tape Stop and more. A quick toolbox for **gated pads, Haas-widened plucks and tape-stop transitions**. | VST2, VST3, AAX (CLAP not confirmed) | Freeware EULA | **Yes**: free Kilohearts account required | No | 3P | https://kilohearts.com/products/kilohearts_essentials |
| **Polyverse Wider** | Polyverse Music / Infected Mushroom | 2.0 | Mono-compatible pseudo-stereo widener (with Low Bypass in 2.0). Gives **wide supersaws and pads that don't collapse in mono**. Keep it off the sub. | VST2, VST3, AAX (Win 64-bit) | Freeware EULA | Email required to receive the download link | No | 3P | https://polyversemusic.com/products/wider |
| **Deelay** | Sixth Sample (with Integraudio) | 1.3.2 | Delay with 5 modes (tape, pitch, ducking, reverse, diffuse/reverb). **Ducked 3/16 dotted delays on the lead** (about 288 ms at 156 BPM) that stay out of the vocal or lead's way. | VST3 (Win 10+, 64-bit) | Freeware EULA | Not confirmed | No | 3P | Sixth Sample site (URL not verified; KVR: https://www.kvraudio.com/product/deelay-by-sixth-sample) |
| **TDR Nova** | Tokyo Dawn Labs | 2.2.2 | Dynamic EQ with external sidechain. Gives **frequency-selective ducking (only the 40–120 Hz of the bass ducks under the kick)**, which is cleaner than full-band pumping. | VST2, VST3, AAX (Win 64-bit) | Freeware EULA | No (believed; not confirmed) | No | 3P | https://www.tokyodawnlabs.com/products/tdr-nova/ |
| **Klanghelm IVGI** | Klanghelm | 2.5.0 (download page) | Simple saturation/distortion (IVGI 2). **Gentle harmonic "fattening" on the mid-bass and e-piano**. | VST/VST3/AAX (VST3 not stated in the IVGI 2 manual) | Freeware EULA | No | No | OFF / 3P | https://klanghelm.com/contents/products/IVGI |
| **ChowMatrix** | Chowdhury DSP | 1.3.0 (2021-12-21) | Tree-of-delays matrix delay. Gives **evolving, cascading delay clouds on the bells and plucks**. | VST3, VST2, AAX, LV2 | BSD-3-Clause | No | Yes | GH | https://github.com/Chowdhury-DSP/ChowMatrix |
| **Surge XT Effects** | Surge Synth Team | Ships with Surge XT 1.3.4 | Surge's full FX rack as a standalone effect plugin: Nimbus granular, Rotary, Ensemble, Spring reverb, Combulator, Vocoder. **Nimbus granular on the choir pad and Combulator on noise risers** stand out. It is already installed if they have Surge XT. | VST3, CLAP | GPL-3.0 | No | Yes | OFF (search snippet of surge-synthesizer.github.io) | https://surge-synthesizer.github.io/ |

### Flagged in group C
- **Cloud Seed**: v1 (ValdemarOrn) is MIT and free, but it is a legacy build (Windows VST2-era) and the repo says it "has moved to a new home". **Cloud Seed 2.0's plugin is commercial**. Only its core DSP (`GhostNoteAudio/CloudSeedCore`) is MIT. That core is interesting as an *embeddable* reverb for Patchbay itself (MIT, C++14), but it is not a free plugin.
- **Devious Machines Duck**: paid ($39.99). It is not free.
- **Sender Spike QB** and similar: VST2-only Windows freeware. Excluded.

---

## D. Free .sf2 SoundFonts with synth and electronic content (browser edition)

All of these are .sf2, not .sf3. "Bundle-safe" means you can host or ship the file inside Patchbay.

| Name | Author / source | Version | What it adds | Licence | Bundle-safe? | Account? | Checked | Official source |
|---|---|---|---|---|---|---|---|---|
| **FreePats Synth Pad set**: Synth Pad Choir, Sweep Pad (GM 96), New Age (GM 89), Synth Pad Bowed | FreePats (Roberto, zenvoid.org) | Per-instrument dates (e.g. New Age 2019-07-30) | **Pads rendered from ZynAddSubFX/Yoshimi, including PADsynth-style.** Use them for the choir pad and evolving pad layers. Synth Pad Choir is about 12 MiB and Sweep Pad about 7.2 MiB. | CC0-1.0 | **Yes** | No | OFF (zenvoid snippets) + GH (`freepats/synth-pad-choir`, `synth-pad-bowed`: CC0) | https://freepats.zenvoid.org/Synthesizer/synth-pad.html |
| **FreePats Synth Lead set**: Synth Bass & Lead, Synth Fifths, Synth Lead Square (GM 81), Synth Lead Calliope (GM 83) | FreePats | Per instrument | **Square and fifths leads for the topline and the counter-melody** (Calliope uses Hexter + Zyn). | CC0-1.0 | **Yes** | No | OFF + GH | https://freepats.zenvoid.org/Synthesizer/synth-lead.html |
| **FreePats Synth Bass / Brass / Strings / Effects**: Synth Bass 1 & 2, Synth Brass 1 & 2, Synth Strings 1 & 2, Crystal, Goblins, Sci-Fi, Soundtrack | FreePats | e.g. Synth Brass 1: 2021-04-26; Synth Brass 2: 2024-06-10 | **Mid-bass, brassy stabs, string-machine pads and FX hits**, including **Crystal (GM 98) for bells** and Sci-Fi/Goblins for riser and transition FX. | CC0-1.0 | **Yes** | No | OFF + GH (17 CC0 "synth-*" repos in the FreePats GitHub org) | https://freepats.zenvoid.org/ (Synthesizer section) |
| **FreePats Electric and Synthesizer Percussion** | FreePats | 2022-07-18 | **Analog drum-machine-style kit** (made with Geonkick and Yoshimi) to replace GM drums on channel 10. | CC0-1.0 | **Yes** | No | OFF + GH | https://freepats.zenvoid.org/Percussion/electric-percussion.html |
| **JummBox SoundFont** ("Fixed JummBox SoundFont13.sf2") | stgiga (from micasddsa4000's original) | 13 (about 1 GB) | Full GM set of **BeepBox/JummBox chip and FM synth patches** plus FM and Piconica drums. Gives bright, characterful leads and arps. It is very large for a browser. | Mixed: MIT (BeepBox/JummBox), CC-BY-SA-4.0 (Zandro OPL2/3), CC-BY-3.0 (Retro Player bank), public domain (W. B. Santos) | Probably, **with attribution and share-alike** (licence taken from a mirror of an earlier version; check the bundled readme) | No (pay-what-you-want on itch.io) | 3P | https://stgiga.itch.io/jummboxsoundfont |
| **GeneralUser GS** (already in use, 2.0.3) | S. Christian Collins | 2.0.3 | Its GM 81–104 synth lead/pad/FX programs and electronic drum kits (GS-style kits on bank 128, e.g. program 24 "Electronic" / 25 "TR-808", if present in the bank; check) are already usable. Before adding more banks, try **switching channel-10 programs to the 808/909/Electronic kits**. | GeneralUser GS licence (bundling allowed) | Yes (already shipped) | No | (not re-researched) | https://github.com/mrbumpy409/GeneralUser-GS |

**Practical note for the browser edition:** most FreePats SF2s are **single-instrument banks mapped to one GM program**. To use several at once, either (a) support layering multiple SF2s with per-program or bank precedence, or (b) merge the chosen FreePats instruments into one "Patchbay Electronic" SF2 with Polyphone. CC0 allows any modification and redistribution. The same instruments also exist as SFZ, so the Windows edition can load them in sfizz.

### Flagged / excluded in group D
- **Arachno SoundFont 1.0**: personal use only, no sharing (Polyphone listing; NixOS marks it unfree). Users can load it locally, but **do not bundle it**.
- **Timbres of Heaven 3.4**: "may not be distributed on any site without written permission". Personal use only. Do not bundle.
- **SGM-V2.01**: no licence found. The author says it contains some commercial samples (Spectrasonics/Synthogy) and has since withdrawn it. **Exclude.**
- **FatBoy (v0.785–0.79x)**: "free, non-commercial", but the licence text could not be verified (fatboy.site not reachable). Local use only until checked.
- **HS TR-808 Drums / HS Synthetic Electronic (HammerSound, 1998)**: tiny sets with good retro synths and an 808 kit, but the **licence is unclear** (Polyphone lists "give credit" for HS sets). Do not bundle without confirmation.
- **Unison**, **SRB2 "gzdoom.sf2"**, **SNES soundfonts**: Polyphone uploaders label these "public domain", but they are compilations of unclear provenance. **Do not trust that label for bundling.**
- **Sonivox EAS**: Apache-2.0, but it ships as embedded samples or DLS inside a library, not as a standalone GM .sf2. Not directly usable.

---

## How this was checked

- **Network limits in this session:** only `github.com` / `raw.githubusercontent.com` could be fetched directly. Developer sites returned DNS/egress blocks: valhalladsp.com, tal-software.com, u-he.com, xferrecords.com, kilohearts.com, tokyodawn.net, klanghelm.com, freepats.zenvoid.org, musical-artifacts.com, zynaddsubfx.sourceforge.io, surge-synthesizer.github.io, geonkick.org, chowdsp.com and others. The GitHub REST API (`gh`/`curl`) was also blocked.
- **Open-source items (GH)** were verified on each repo's README and release page. Versions and dates come from the release asset timestamps (`/releases/expanded_assets/<tag>`), which also confirmed a Windows x64 binary exists.
- **Freeware items (OFF/3P)** were verified through web search. Where possible the search was scoped to the developer's own pages (search snippets), and otherwise to recent press (KVR, Bedroom Producers Blog, Synthanatomy, Rekkerd, Gearnews). **Re-confirm the version, formats and account requirement on the developer page before publishing links in the app.**
- **Host-side note:** the Steinberg **VST3 SDK is now MIT-licensed only** (SDK 3.8.x; GPLv3/proprietary options withdrawn), confirmed on github.com/steinbergmedia/vst3sdk. This simplifies the JUCE Windows host's licensing.

### Could not verify (treat as provisional)
- Exact current versions and dates for Valhalla (Supermassive 5.0 date), TAL-Chorus-LX, Kilohearts Essentials, Polyverse Wider, Deelay, TDR Nova, IVGI, BP-909, 808XD.
- Whether Zebralette 3 requires registration under u-he's new licensing system.
- Pendulate's account requirement (sources conflict: email-only vs iLok account).
- Dragonfly 3.2.10's release year and whether its Windows zip includes CLAP. Tunefish 4.2.0's VST3 build comes from press only.
- The FreePats per-instrument SF2 file sizes and dates (zenvoid.org unreachable; the CC0 licence is confirmed via the FreePats GitHub org).
- JummBox SoundFont component licences (taken from a mirror of an earlier version).

## Excluded and why

| Item | Reason |
|---|---|
| Helm | Archived 2025-02-08, last release 2017, hi-DPI GUI issues; superseded by Vital |
| Synth1 | Windows 64-bit **VST2 only** |
| ZynAddSubFX / Zyn-Fusion (Windows) | Official Windows 3.x binaries are **paid** (free demo times out). FreePats CC0 SF2s used as the workaround. |
| Sitala (free) | Free 1.0 is **VST2/AU/AAX only**; VST3 needs paid 2.x |
| DR.89 (Sender Spike) | **VST2 only** |
| TS-808 (Tactile Sounds) | 32-bit VST2 only |
| BazzISM | Trialware (unregistered limitations) |
| Cloud Seed 2 | Plugin is commercial (only the core DSP is MIT) |
| Devious Machines Duck | Paid |
| Shortcircuit XT | Free/open source but self-described alpha/beta ("many things will be incomplete"); revisit when 1.0 ships |
| Monique | Only nightly builds (Aug 2024); included as optional, not recommended for the pack |
| Arachno, Timbres of Heaven, SGM-V2.01, FatBoy, HS sets, Unison, SRB2 | Licence forbids or doesn't clearly allow bundling (see group D) |
| Native Instruments Komplete Start, iZotope Ozone Imager, Softube freebies | Account and installer-manager required, no redistribution; not researched further because they are lower priority than the no-account options above |
