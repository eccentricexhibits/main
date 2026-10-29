# Finding classical passages that fit the song's harmony

These scripts search a folder of MIDI files for passages whose harmony follows "Wasting My
Time"'s chord progressions. They were used to pick the Mozart counter-melody in
`songs/wasting-my-time-electronic-lush-mozart/`.

1. **Index a corpus:** `python3 -I index.py <folder of .mid files> idx_<name>`.
   For every piece it stores, beat by beat:
   - how long each of the 12 pitch classes sounds
   - the lowest note
2. **Search whole pieces:** `python3 -I match.py idx_bach idx_beethoven idx_mozart`. This
   tests the song's verse, chorus and bridge progressions against every passage. It tries:
   - all 12 transpositions
   - 1, 2, 3 or 4 beats per chord

   A passage scores 60% on how well its notes fit each chord (cosine against the chord's
   tones) and 40% on whether its lowest note is the chord's bass. Results go to
   `top_<target>.json`.
3. **Search themes:** `python3 -I themes.py idx_…`. The same search, but only for windows
   starting in a movement's first four bars, where its theme is stated. It adds two
   preferences, and the half-length progressions (2–3 bars):
   - duple meter
   - chords changing at about the song's pace: half a bar at 156 BPM, so the passage plays
     near its written tempo

Run Python with `-I` when a corpus comes from outside. The scripts only read MIDI data.
