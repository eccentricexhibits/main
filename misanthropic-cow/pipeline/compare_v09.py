"""Measure the v09 Chicken Dance rig with the same edge-stretch metric used for v10 (before/after)."""
import sys, json
import numpy as np
import glb as G
import render as R
from validate import tri_stretch

model = G.read(sys.argv[1])                          # cow-dance-test.glb (skinned)
mats = np.frombuffer(open(sys.argv[2], 'rb').read(), '<f4').reshape(-1, 19, 4, 4).transpose(0, 1, 3, 2)
names = ['Coat_torso_continuous_surface', 'Left_sleeve_continuous_surface', 'Right_sleeve_continuous_surface']
idx = [i for i, p in enumerate(model.parts) if p['name'] in names]
out = {n: [] for n in names}
for k in range(0, len(mats), 3):
    P = R.skin_parts(model, np.ascontiguousarray(mats[k]))
    for i in idx:
        out[model.parts[i]['name']].append(float(np.percentile(tri_stretch(model.parts[i]['v'], P[i]['v'], model.parts[i]['f']), 99.9)))
res = {'v09_torso_edge_stretch_p999_max': max(out[names[0]]),
       'v09_sleeve_edge_stretch_p999_max': max(max(out[names[1]]), max(out[names[2]]))}
print(json.dumps(res, indent=1))
json.dump(res, open(sys.argv[3], 'w'), indent=1)
