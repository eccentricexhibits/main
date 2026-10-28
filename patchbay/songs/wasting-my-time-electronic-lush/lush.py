"""Wasting My Time, electronic (lush): the electronic arrangement with v18's full orchestration back.

usage: python3 lush.py [out folder]   (default: this script's folder)

The electronic version (../wasting-my-time-electronic/electronic.py) carries 40% of v18's notes:
the tune, the hook and the lines that suit synths. This version builds on it unchanged (same
leads, drums, bass, fixes and dynamics) and layers on top:

1. A synth orchestra (file 3): every v18 line, each family on its own synth: string machines
   for violins/violas/cellos, synth brass for horns/trumpets/trombones, soft square and calliope
   leads for the woodwinds, low synths for the bass instruments, a chime for the harp, tuned
   808 toms for the timpani, and the suspended cymbal swells on the orchestral kit.
2. Width (file 4): detuned left/right twins of the hook lead and of the pads, the "ensemble"
   that makes a synth sound wide.
3. Air (file 4): a high halo pad through the whole song, a choir pad in the big sections, a
   unison vocal double of the verse tune, and a 16th-note shimmer arpeggio with echoes in the
   choruses, the bridge climax and the ending.

The user's v18 preferences still hold: horns mellow (velocity capped at 90), the harp soft
outside the bridge, the choir as colour, the verse tune about 2 dB over everything else.
"""
import importlib.util, pathlib, sys, json, collections
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('electronic', HERE.parent / 'wasting-my-time-electronic' / 'electronic.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)   # builds the electronic version's parts
T, BAR, BEAT, add, section, chord_at = e.T, e.BAR, e.BEAT, e.add, e.section, e.chord_at
OUT = {'A': 'Wasting_My_Time_electronic_lush_part1_synths.mid', 'B': 'Wasting_My_Time_electronic_lush_part2_drums_bass_fx.mid',
       'C': 'Wasting_My_Time_electronic_lush_part3_synth_orchestra.mid', 'D': 'Wasting_My_Time_electronic_lush_part4_layers.mid'}
TITLE = {'A': '1 of 4: synths', 'B': '2 of 4: drums, bass and FX', 'C': '3 of 4: synth orchestra', 'D': '4 of 4: width and air'}

# ---------------------------------------------------------------- 1. the synth orchestra
# role: (file, channel, track name, bank, program, CC7, pan, reverb), and the v18 tracks it plays
ORCH = {
    'o_flute':   (('C', 1, 'Synth flutes (flute, piccolo)', 0, 82, 72, 18, 75), ('Flute 1·2', 'Piccolo')),          # Synth Calliope
    'o_reed':    (('C', 2, 'Synth reeds (oboe, cor anglais)', 13, 80, 70, -20, 70), ('Oboe 1·2', 'English Horn')),  # Square Lead 3
    'o_clar':    (('C', 3, 'Synth clarinets', 1, 80, 70, 24, 70), ('Clarinet 1·2 in Bb',)),                         # Square Wave
    'o_lowreed': (('C', 4, 'Synth low reeds', 11, 39, 62, -10, 50), ('Bass Clarinet in Bb', 'Bassoon 1·2')),       # Pulse Bass
    'o_horn':    (('C', 5, 'Synth horns', 8, 63, 80, -26, 70), ('Horn 1·2 in F', 'Horn 3·4 in F')),                  # Synth Brass 4
    'o_tpt':     (('C', 6, 'Synth trumpets', 0, 62, 70, 14, 65), ('Trumpet 1·2·3 in Bb',)),                          # Synth Brass 1
    'o_tbn':     (('C', 7, 'Synth trombones', 0, 63, 68, 22, 60), ('Trombone 1·2', 'Bass Trombone')),                # Synth Brass 2
    'o_low':     (('C', 8, 'Synth contrabass', 0, 39, 60, 0, 30), ('Contrabass', 'Contrabassoon', 'Tuba')),         # Synth Bass 2
    'o_harp':    (('C', 9, 'Synth harp', 11, 98, 66, -30, 80), ('Harp',)),                                          # Synth Chime
    'o_cym':     (('C', 10, 'Cymbal swells', 0, 48, 70, 0, 80), ('Suspended Cymbal · Triangle',)),                  # Orchestral kit
    'o_vn1':     (('C', 11, 'String machine (violins I)', 0, 50, 82, -14, 80), ('Violin I',)),                       # Synth Strings 1
    'o_vn2':     (('C', 12, 'String machine (violins II)', 0, 51, 80, 14, 80), ('Violin II',)),                      # Synth Strings 2
    'o_vla':     (('C', 13, 'String machine (violas)', 11, 51, 80, -6, 80), ('Viola',)),                             # Synth Strings 5
    'o_vc':      (('C', 14, 'String machine (cellos)', 8, 50, 78, 8, 75), ('Violoncello',)),                         # Synth Strings 3
    'o_timp':    (('C', 15, 'Synth timpani', 8, 118, 58, 0, 60), ('Timpani',)),                                     # 808 Tom
    'o_bridge':  (('C', 16, 'String machine (bridge solo, tremolo)', 0, 50, 76, 20, 100), ('Solo Violin', 'Strings (tremolo)')),
}
# In each verse one orchestra layer doubles the tune (cellos in 1 and 3, violas in 2, the bassoons
# an octave under in 3): it plays louder there and counts as melody in the verse balance.
TUNE = {7: ('o_vc',), 21: ('o_vla',), 40: ('o_vc', 'o_lowreed')}
def tune_layer(role, t):
    a, b, k = section(t // BAR + 1)
    return k == 'verse' and role in TUNE[a]
VEL = {'o_horn': (1.0, 90), 'o_tpt': (0.9, 96), 'o_tbn': (0.9, 96), 'o_harp': (0.6, 127), 'o_timp': (0.7, 110), 'o_low': (0.85, 127)}
for role, ((f, ch, name, bank, prog, vol, pan, rev), srcs) in ORCH.items():
    e.ROLES[role] = (f, ch, name, bank, prog, vol, pan, rev)
    k, vmax = VEL.get(role, (0.9, 127))
    for src in srcs:
        for s, en, p, v in e.SRCN[src]:
            if role == 'o_timp' and en - s < 0.2 * BEAT: continue     # rolls would machine-gun on a synth tom
            if role == 'o_harp' and 59 <= s // BAR + 1 < 71: k2 = 1.0  # the bridge harp at full strength, as in v18
            elif tune_layer(role, s): k2 = 1.2
            else: k2 = k
            add(role, s, en, p, min(v * k2, vmax))

# ---------------------------------------------------------------- 2. width: detuned twins
# Pitch bend is ±2 semitones by default, so 410 ≈ 10 cents.
LAYERS = {
    'w_hookL': ('D', 1, 'Hook lead (detuned left)', 0, 81, 92, -50, 60, -410, 'lead', 0.82),
    'w_hookR': ('D', 2, 'Hook lead (detuned right)', 0, 81, 92, 50, 60, 410, 'lead', 0.82),
    'w_padL':  ('D', 3, 'Pad ensemble (left)', 0, 89, 84, -54, 80, -490, ('pad', 'pump'), 0.95),
    'w_padR':  ('D', 4, 'Pad ensemble (right)', 0, 89, 84, 54, 80, 490, ('pad', 'pump'), 0.95),
    'w_vox':   ('D', 5, 'Verse tune (vocal double)', 0, 85, 96, 0, 70, 0, 'lead_v', 0.75),
}
for role, (f, ch, name, bank, prog, vol, pan, rev, bend, src, k) in LAYERS.items():
    e.ROLES[role] = (f, ch, name, bank, prog, vol, pan, rev)
    for r in (src if isinstance(src, tuple) else (src,)):
        for s, en, p, v in list(e.NOTES[r]): add(role, s, en, p, v * k)
    if bend: e.BEND[role] = [(0, bend)]

# ---------------------------------------------------------------- 3. air: halo pad, choir pad, shimmer arp
e.ROLES['a_halo'] = ('D', 6, 'Halo pad', 0, 94, 82, 0, 100)        # Halo Pad
e.ROLES['a_oohs'] = ('D', 7, 'Choir pad (oohs)', 0, 53, 74, 0, 100)  # Voice Oohs
e.ROLES['a_arp'] = ('D', 8, 'Shimmer arp', 0, 102, 70, 30, 90)       # Echo Drops
e.ROLES['a_arpE'] = ('D', 9, 'Shimmer arp echo', 0, 102, 62, -40, 100)
BIG = ('chorus', 'final', 'tag', 'verse4', 'inter2', 'ending')
for a, b, k in e.SECTIONS:
    if k == 'hit': continue
    e.chord_pad('a_halo', a, b, 60 if k in ('intro', 'break', 'verse', 'outro') else 74, lo=64, hi=86)
    if k in BIG: e.chord_pad('a_oohs', a, b, 66, lo=55, hi=72)
e.chord_pad('a_oohs', 62, 71, 62, lo=55, hi=72)   # the bridge from its second statement
def shimmer(a, b, vel):
    """16th notes up through the chord's tones over two octaves, re-voiced at each half bar."""
    for bar in range(a, b):
        for h in (0, 1):
            pcs, _ = chord_at(bar, h); tones = sorted(p for p in range(72, 97) if p % 12 in pcs)
            seq = tones[:7] if len(tones) >= 4 else tones
            for i in range(8):
                t = T(bar, 1 + 2 * h) + i * 120; p = seq[i % len(seq)]; v = vel * (1.0 if i % 4 == 0 else 0.78)
                add('a_arp', t, t + 100, p, v); add('a_arpE', t + 360, t + 460, p, v * 0.45)
for a, b, k in e.SECTIONS:
    if k in ('chorus', 'final', 'verse4', 'inter2'): shimmer(a, b, 80)
    elif k == 'ending': shimmer(a, b, 86)
shimmer(65, 71, 72)

# ---------------------------------------------------------------- dynamics for the new layers
NEW = set(ORCH) | set(LAYERS) | {'a_halo', 'a_oohs', 'a_arp', 'a_arpE'}
e.LEADS = e.LEADS + ('w_hookL', 'w_hookR', 'w_vox')   # leads keep their level in every section
base_level = e.level
def level(role, bar):
    if role == 'o_cym': return 120
    return base_level(role, bar)
e.level = level
base_trim = e.trim
def trim(t, role=None):
    """The new accompaniment layers sit a further 1.5 dB back in the verses, so the tune keeps the
    balance the user settled on (about +2.2 / +2.2 / +1.6 dB over everything else)."""
    db = base_trim(t, role)
    if role in NEW and role not in e.LEADS and section(t // BAR + 1)[2] == 'verse' and not tune_layer(role, t): db -= 1.5
    return db
e.trim = trim
e.PUMP.update({'w_padL': 0.5, 'w_padR': 0.5, 'a_halo': 0.3, 'a_oohs': 0.3, 'o_vn1': 0.22, 'o_vn2': 0.22, 'o_vla': 0.22, 'a_arp': 0.15})
e.REVERB_BRIDGE = e.REVERB_BRIDGE + ('o_vn1', 'o_vn2', 'o_vla', 'o_vc', 'o_bridge', 'o_harp', 'a_halo', 'a_oohs', 'w_padL', 'w_padR', 'w_hookL', 'w_hookR')

# ---------------------------------------------------------------- write
if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
    out.mkdir(parents=True, exist_ok=True)
    for tag in 'ABCD':
        mf = e.build(tag)
        mf.tracks[0][[i for i, m in enumerate(mf.tracks[0]) if m.type == 'track_name'][0]].name = f'Wasting My Time (electronic, lush) - part {TITLE[tag]}'
        mf.save(out / OUT[tag])
    summary = {e.ROLES[r][0] + ' ' + e.ROLES[r][2]: len(set(v)) for r, v in sorted(e.NOTES.items(), key=lambda x: (e.ROLES[x[0]][0], e.ROLES[x[0]][1]))}
    (out / 'lush-parts.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print('wrote', ', '.join(OUT.values()), '·', len(summary), 'parts ·', sum(summary.values()), 'notes')
