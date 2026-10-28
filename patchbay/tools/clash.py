"""Count harsh clashes (minor 2nds / major 7ths overlapping by at least an 8th note, ignoring
untuned percussion and the sustain pedal) in a revision, against the original files.
usage: python3 clash.py <folder with the revised .mid files> <version tag, e.g. v18>"""
import mido, collections, sys
BAR = 1920
SKIP = ('Snare', 'Bass Drum', 'Suspended', 'Timpani')
import os
ORIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'songs', 'wasting-my-time', '')   # the originals
F = ['Wasting_My_Time_orchestral_VI_part1_winds_brass', 'Wasting_My_Time_orchestral_VI_part2_perc_harp_strings']
def notes(paths):
    out = []
    for path in paths:
        for tr in mido.MidiFile(path).tracks:
            name = next((x.name for x in tr if x.type == 'track_name'), '')
            if name.startswith(SKIP): continue
            t = 0; op = {}
            for x in tr:
                t += x.time
                if x.type == 'note_on' and x.velocity > 0: op.setdefault(x.note, []).append(t)
                elif x.type in ('note_on', 'note_off') and op.get(x.note): out.append((op[x.note].pop(0), t, x.note, name))
    return out
def clashes(ns):
    per = collections.Counter(); ex = collections.defaultdict(list); ns = sorted(ns)
    for i, a in enumerate(ns):
        for b in ns[i + 1:]:
            if b[0] >= a[1]: break
            if a[3] == b[3] or min(a[1], b[1]) - max(a[0], b[0]) < 240: continue
            if abs(a[2] - b[2]) % 12 in (1, 11):
                bar = max(a[0], b[0]) // BAR + 1; per[bar] += 1; ex[bar].append(f"{a[3][:8]}:{a[2]} vs {b[3][:8]}:{b[2]}")
    return per, ex
if __name__ == '__main__':
    folder, tag = sys.argv[1].rstrip('/') + '/', sys.argv[2]
    o, _ = clashes(notes([ORIG + f + '.mid' for f in F])); n, ex = clashes(notes([folder + f + f' ({tag}).mid' for f in F]))
    print(f'harsh clashes: original {sum(o.values())}, {tag} {sum(n.values())}')
    for bar in sorted(set(n) | set(o)):
        if n[bar] > o[bar]: print(f"  bar {bar}: {o[bar]} → {n[bar]}  e.g. {ex[bar][:4]}")
