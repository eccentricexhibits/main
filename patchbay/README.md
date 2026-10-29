# Patchbay MIDI Studio

A MIDI player that lists every channel and lets you assign an instrument to each, plus the
song "Wasting My Time" made with it. Start with `HANDOFF.md`.

- `songs/wasting-my-time-v18/`: the approved orchestral version
- `songs/wasting-my-time-electronic/`: the electronic arrangement of v18 (see its `CHANGES.md`)
- `songs/wasting-my-time-electronic-lush/`: the same with v18's full orchestration layered back on synths
- `songs/wasting-my-time-electronic-lush-mozart/`: the lush version with a Mozart (K. 191) counter-melody in the choruses
- `songs/wasting-my-time-electronic-lush-variations/`: the main melody developing: Bach Chaconne verses, Mozart chorus answers
- `electronic-instruments.md` and `free-instruments.md`: free plugins and SoundFonts to enrich the sound
- `src/patchbay.src.html` → `python3 build.py` builds every page. The SoundFont parts in `sounds/`
  are not committed (43 MB). Rebuild them from GeneralUser-GS.sf2 as described in HANDOFF.md.
- Older revisions (v2–v17) are in the user's handoff zip and aren't included here.
