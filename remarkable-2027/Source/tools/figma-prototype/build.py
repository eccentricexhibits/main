import base64, json, os, sys
here = os.path.dirname(os.path.abspath(__file__)); out = sys.argv[1]
os.makedirs(out, exist_ok=True)
spec = json.load(open(os.path.join(here, 'data/spec.json')))
files = sorted(f for f in os.listdir(os.path.join(here, 'data')) if f.endswith(('.jpg', '.png')))
images = {f: base64.b64encode(open(os.path.join(here, 'data', f), 'rb').read()).decode() for f in files}
src = open(os.path.join(here, 'plugin_src.js')).read()
svgs = spec.pop('svgs', {}); spec.pop('images', None)
code = src.replace('__DATA__', json.dumps(spec, separators=(',', ':'))).replace('__IMAGES__', json.dumps(images, separators=(',', ':'))).replace('__SVGS__', json.dumps(svgs, separators=(',', ':')))
open(os.path.join(out, 'code.js'), 'w').write(code)
json.dump({"name": "Remarkable 2027 Prototype Builder", "id": "remarkable-2027-prototype-builder", "api": "1.0.0",
           "main": "code.js", "editorType": ["figma"], "documentAccess": "dynamic-page",
           "networkAccess": {"allowedDomains": ["none"]}}, open(os.path.join(out, 'manifest.json'), 'w'), indent=2)
print('code.js', os.path.getsize(os.path.join(out, 'code.js')) // 1024, 'KB')
