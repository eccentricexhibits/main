"""Make a Patchbay page holding only a bar range of a song (shifted to start at bar 1), so
stem renders are fast. Controller, program and tempo state from before the range is kept.
usage: python3 trim.py <song folder with .mid files> <out.html> <first bar> <bar after last>"""
import mido, sys, pathlib, base64, json, io
root = pathlib.Path(__file__).resolve().parent.parent
src, out, b0, b1 = pathlib.Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
a, z = (b0 - 1) * 1920, (b1 - 1) * 1920
files = []
for f in sorted(src.glob('*.mid')):
    nm = mido.MidiFile(type=1, ticks_per_beat=480)
    for tr in mido.MidiFile(f).tracks:
        t = 0; ev = []; state = {}
        for x in tr:
            t += x.time
            if x.type == 'end_of_track': continue
            if t < a:
                if not x.is_meta and x.type in ('control_change', 'program_change', 'pitchwheel'): state[(x.type, getattr(x, 'control', None), x.channel)] = x
                elif x.is_meta and x.type in ('track_name', 'set_tempo', 'time_signature'): state[(x.type,)] = x
                continue
            if t >= z:
                if x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0): ev.append((z, x))
                continue
            ev.append((t, x))
        nt = mido.MidiTrack(); now = a
        for x in state.values(): nt.append(x.copy(time=0))
        for t, x in sorted(ev, key=lambda e: e[0]): nt.append(x.copy(time=t - now)); now = t
        nm.tracks.append(nt)
    buf = io.BytesIO(); nm.save(file=buf); files.append({'name': f.name, 'b64': base64.b64encode(buf.getvalue()).decode()})
s = (root / 'src/patchbay.src.html').read_text()
body = s.replace('__DEMO_MIDI__', base64.b64encode((root / 'src/demo.mid').read_bytes()).decode()).replace('/*__PRELOAD__*/null', json.dumps({'title': 'excerpt', 'files': files}))
HEAD = eval('(' + (root / 'build.py').read_text().split('HEAD = (')[1].split("')\n")[0] + "')")   # the page header build.py uses
pathlib.Path(out).write_text(HEAD + body + '</body></html>')
print('wrote', out, f'(bars {b0}-{b1 - 1})')
