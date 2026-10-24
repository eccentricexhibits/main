#!/usr/bin/env bash
# Rebuild the head from the raw inputs.
#   IN   folder holding cowMask.obj (2014 MakerBot Digitizer scan) and photos/cow_frame-*.jpg
#   OUT  working folder for intermediates
# Needs: pip install trimesh scipy scikit-image xatlas fast-simplification pillow
set -euo pipefail
IN=${1:?input folder}; OUT=${2:?work folder}; HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT/parts" "$OUT/baked" "$OUT/export"

# 0. voxelize the watertight scan at 1 mm
python3 -c "
import trimesh, numpy as np
m = trimesh.load('$IN/cowMask.obj', process=True)
v = m.voxelized(1.0).fill()
np.savez_compressed('$OUT/vox1mm.npz', occ=v.matrix, T=v.transform)"

# 1. carve the mask out (drop box, turntable, scanner blobs). sym_plane.npy holds the mask's
#    mirror plane in scan coordinates (found by mirror-ICP; the box is square to it).
python3 "$HERE/step1_mask.py" "$OUT/vox1mm.npz" "$OUT/mask_clean.ply" "$HERE/sym_plane.npy"
# 2. assemble mask + fur hood + horn bar + horns in the model frame
python3 "$HERE/step2_head.py" "$OUT/mask_clean_field.npz" "$HERE/sym_plane.npy" "$OUT/parts"
# 3. decimate, unwrap, bake colour from the photos (cams.json = fitted photo cameras; refit with
#    fit_cameras.py against a model-frame copy of the mask if the scan processing changes)
python3 "$HERE/step3_texture.py" "$OUT/parts" "$IN/photos" "$HERE/cams.json" "$OUT/baked"
# 4. export GLB + OBJ
python3 "$HERE/step4_export.py" "$OUT/baked" "$OUT/parts" "$OUT/export"
