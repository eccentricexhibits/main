"""Build Patchbay: hosted artifact page + standalone local copy, plus song builds that open on a preloaded song."""
import base64, json, pathlib
root = pathlib.Path(__file__).parent
src = (root / 'src/patchbay.src.html').read_text()
demo = base64.b64encode((root / 'src/demo.mid').read_bytes()).decode()
HEAD = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>')

def page(preload=None, title=None):
    out = src.replace('__DEMO_MIDI__', demo)
    if preload:
        files = [{'name': f.name, 'b64': base64.b64encode(f.read_bytes()).decode()} for f in preload]
        out = out.replace('/*__PRELOAD__*/null', json.dumps({'title': title, 'files': files}))
    return out

# 1. hosted artifact body (demo song)
(root / 'patchbay.html').write_text(page())
# 2. local copy (full HTML document + the SoundFont)
local = root / 'local/Patchbay'
(local / 'sounds').mkdir(parents=True, exist_ok=True)
(local / 'Patchbay.html').write_text(HEAD + page() + '</body></html>')
sf2 = local / 'sounds/GeneralUser-GS.sf2'
parts = [root / f'sounds/generaluser-gs-{i}.bin' for i in range(3)]
if all(p.exists() for p in parts):
    with open(sf2, 'wb') as out:
        for p in parts: out.write(p.read_bytes())
# 3. song builds: every folder under songs/ with .mid files gets a page that opens on that song
for song_dir in sorted((root / 'songs').glob('*/')) if (root / 'songs').exists() else []:
    mids = sorted(song_dir.glob('*.mid'))
    if not mids: continue
    tf = song_dir / 'title.txt'   # optional; otherwise the folder name: wasting-my-time → Wasting My Time
    title = tf.read_text().strip() if tf.exists() else ' '.join(w.capitalize() for w in song_dir.name.split('-'))
    body = page(mids, title).replace('<title>Patchbay MIDI Studio</title>', f'<title>{title}</title>', 1)
    (song_dir / 'patchbay-song.html').write_text(body)                       # artifact body
    (song_dir / 'Patchbay.html').write_text(HEAD + body + '</body></html>')  # double-click local copy
    print('song build:', song_dir.name, [m.name for m in mids])
print('built', len(page()), 'bytes')
