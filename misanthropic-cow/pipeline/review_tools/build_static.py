"""Assemble only the static model (no rig, no clips) with the pipeline, for quick shape checks.
usage: python build_static.py <pipeline dir> <out.glb> [--quick]
  REBUILD=<Rebuild_Inputs/project>   where the v09 inputs are (default: ../../Rebuild_Inputs/project from the pipeline)
  COW_ARM_RAISE=70                   build the arms-raised pose (the round-20 "Arms raised" model)
  COW_MARKINGS_CACHE=<file.pkl>      share the projected markings between the arms-down and arms-raised builds:
                                     build arms-down first with it set, then arms-raised with the same file
Rounds 19-24 have no rig yet, so this is the build that makes their models."""
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import assemble as AS, glb as G
pipe = Path(sys.argv[1]).resolve(); root = pipe.parent.parent
import os
RI = Path(os.environ.get('REBUILD', root / 'Rebuild_Inputs/project'))
src = RI / 'dist/assets/geometry-v09.glb'; tex = RI / 'model-source/textures-v09'
out = Path(sys.argv[2]); out.parent.mkdir(parents=True, exist_ok=True)
model, report = AS.build(src, tex, out.parent, quick='--quick' in sys.argv)
model.parts = [{k: v for k, v in p.items() if k not in ('group', 'hoof_w', 'thumb_w', 'toe_w', 'part', 'W')} for p in model.parts]
model.skin = None; model.animations = []
print(report, G.write(model, out))
