# Song-revision tools

These are the scripts used to make and check every revision of "Wasting My Time". They
need Python 3 with `mido`, and Node with `playwright` (a Chromium headless browser).

## Making a new revision (vN+1 from vN)

1. **Copy the newest script.** Copy `songs/wasting-my-time-vN/revise_vN.py` to
   `revise_vN+1.py`. Then:
   - add a line to the docstring
   - make the edit
   - change the two `(vN)` output names and `vN-changes.json`

   Every script rebuilds from the **original** MIDI files in `songs/wasting-my-time/`
   and repeats all the earlier edits, so each version is self-contained.
2. **Generate the MIDI files:** `python3 revise_vN+1.py out/` writes the two
   `… (vN+1).mid` files and a change log.
3. **Package:** make `songs/wasting-my-time-vN+1/` and put these in it:
   - the two MIDI files
   - the script. Its `SRC` line finds `songs/wasting-my-time/` relative to the
     script's own location, so it runs from anywhere. `revise_v18.py` is set up
     this way; older scripts have a `/home/user/...` path to change.
   - `title.txt` containing `Wasting My Time (vN+1)`
4. **Build:** `python3 build.py`. This writes `patchbay-song.html` (the artifact
   body) and `Patchbay.html` (offline) into every song folder.
5. **Render:**
   - Serve a folder that contains the song's `Patchbay.html` and a `sounds`
     symlink to `sounds/` (the three `generaluser-gs-*.b64.txt` parts):
     `python3 -m http.server 8765 --bind 127.0.0.1`
   - Then run `node tools/render.js http://127.0.0.1:8765/vN+1.html out.wav`.
6. **Check:**
   - `python3 tools/clash.py <folder> vN+1`: harsh clashes. 334 has been the
     count since v8, and it should not rise.
   - `ffmpeg -i out.wav -af ebur128 -f null -`: whole-song loudness (about
     −14.5 LUFS).
   - `node tools/verse_balance.js [--k] <url>`: the verse melody against
     everything else. The user's settled values are in HANDOFF.md.
   - `node tools/solo_level.js <url> '<regex>' [from] [to]`: any part's level
     against the mix, second by second.
   - `python3 tools/show.py <folder> vN+1 <bar> <bar> [track]`: read the notes
     and CC7/CC11 changes in a passage.
7. **MP3s:** use `ffmpeg … -codec:a libmp3lame -b:a 192k`.
   - full preview
   - a before/after clip of the changed passage, joined with 2 s of silence
     (`apad=pad_dur=2` and `concat`)
8. **Publish:** publish `patchbay-song.html` as an artifact with:
   - `capabilities: {downloads: true}`
   - `files` copying `sounds/generaluser-gs-{0,1,2}.b64.txt` from
     https://claude.ai/artifact/RmKv4ph63HoFihzA3wSfeg

   Then write `CHANGES.md`, update HANDOFF.md, and rebuild the zip.

## Measuring an arrangement by groups of parts

Used for the electronic arrangement, where the parts are new and need balancing from scratch:
- `python3 tools/trim.py <song folder> out.html <first bar> <bar after last>` writes a page
  holding just that excerpt (with the controller and tempo state from before it), so a render
  takes seconds instead of minutes.
- `node tools/stems.js <url> 156 '{"leads":"^Lead","drums":"^(Kick|Snare|Hats)"}' '[["V1",7,13]]'`
  solos each group, renders, and prints its RMS (and the band under 120 Hz) per bar window,
  next to the mix. "Melody minus rest" = melody dB − 10·log10(10^(mix/10) − 10^(melody/10)).

## Notes

- **Engine gain:** (CC7/127)² × (CC11/127)². Multiplying CC11 by f changes the
  level by 40·log10(f) dB.
- **Export normalisation:** the export scales the file down if its peak is over
  0.98. If a dense passage peaks higher, the whole file comes out quieter.
- **Velocity:** it changes brightness as well as level. Lowering it softens
  attacks: that's how the harp stopped sounding like a piano, and why the horns
  are capped at 100.
- **Background servers:** a background `http.server` can get stopped between
  turns. Check it with `curl` before rendering.
