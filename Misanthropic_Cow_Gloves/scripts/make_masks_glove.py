"""Material mask for the glove atlas: paint vs terry, from geometry (not colour).
Paint = texels of the two finger-pair parts above the hoof base plane (the real paint edge was a clean, straight
cut); everything else is terry. Soft 1-2 px edge.
usage: python3 -I make_masks_glove.py <geom_dir> <planes.json> <out_dir> [size=4096]
Writes mask_paint.png (lossless, 8-bit: 255 = paint) and class_preview.png (cream terry / red paint)."""
import sys, os, json, numpy as np, cv2
from PIL import Image
G, PJ, OUT = sys.argv[1:4]; SZ = int(sys.argv[4]) if len(sys.argv) > 4 else 4096
os.makedirs(OUT, exist_ok=True)
pos = np.load(os.path.join(G, f"geom_position_{SZ}.npy"))[..., :3]; part = np.load(os.path.join(G, f"geom_part_{SZ}.npy"))
P = json.load(open(PJ)); bc, bn = np.array(P["base_co"]), np.array(P["base_no"]); bn /= np.linalg.norm(bn)
# positions are in the work file's units (glove 0.972 tall); signed distance to the hoof base plane, in texels' metres
d = (pos - bc) @ bn
# texels the bake missed (tiny faces at chart edges) take the class of the nearest baked texel, so no
# terry flecks appear on the hoof rim (and no paint flecks on the terry)
from scipy import ndimage as nd
miss = part == 0
_, (iy, ix) = nd.distance_transform_edt(miss, return_indices=True)
part_f, d_f = part[iy, ix], d[iy, ix]
paint = ((part_f >= 2) & (d_f > 0)).astype(np.float32)
part_cov = part
paint = cv2.GaussianBlur(paint, (0, 0), 0.8)
Image.fromarray((paint * 255).astype(np.uint8)).save(os.path.join(OUT, "mask_paint.png"))
terry_c = np.array([226, 214, 182], np.float32); paint_c = np.array([200, 40, 40], np.float32)
prev = terry_c * (1 - paint[..., None]) + paint_c * paint[..., None]; 
Image.fromarray(prev.astype(np.uint8)).save(os.path.join(OUT, "class_preview.png"))
cov = part_cov > 0
print(f"paint {100*(paint[cov] > 0.5).mean():.1f}% of covered texels, terry {100*(paint[cov] <= 0.5).mean():.1f}%")
