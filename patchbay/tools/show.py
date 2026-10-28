"""Print every note (bar.beat:pitch/length-in-beats v velocity) and CC7/CC11 change in a bar range.
usage: python3 show.py <folder> <version tag or ''> <first bar> <last bar> [track name filter]"""
import mido, sys
NN = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
nm = lambda p: NN[p % 12] + str(p // 12 - 1)
folder, tag, b0, b1 = sys.argv[1].rstrip('/') + '/', sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) + 1
only = sys.argv[5] if len(sys.argv) > 5 else None
for fn in ['Wasting_My_Time_orchestral_VI_part1_winds_brass', 'Wasting_My_Time_orchestral_VI_part2_perc_harp_strings']:
    for tr in mido.MidiFile(folder + fn + (f' ({tag})' if tag else '') + '.mid').tracks:
        name = next((m.name for m in tr if m.type == 'track_name'), '')
        if only and only not in name: continue
        t = 0; on = {}; out = []; cc = []
        for m in tr:
            t += m.time
            if m.type == 'note_on' and m.velocity: on[(m.channel, m.note)] = (t, m.velocity)
            elif m.type in ('note_on', 'note_off') and (m.channel, m.note) in on:
                s, v = on.pop((m.channel, m.note))
                if (b0 - 1) * 1920 <= s < b1 * 1920: out.append((s, t, m.note, v))
            elif m.type == 'control_change' and m.control in (7, 11) and (b0 - 1) * 1920 <= t < b1 * 1920:
                cc.append(f"cc{m.control}={m.value}@{t // 1920 + 1}.{(t % 1920) // 480 + 1}")
        if out:
            print(f"## {name} ({len(out)}) {' '.join(cc)}")
            print('  ' + ' '.join(f"{a // 1920 + 1}.{(a % 1920) / 480 + 1:g}:{nm(p)}/{(b - a) / 480:g}v{v}" for a, b, p, v in sorted(out)))
