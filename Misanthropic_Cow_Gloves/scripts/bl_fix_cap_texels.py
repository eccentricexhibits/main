"""Paint the cut walls (toe inner walls, web caps) straight into the baked maps instead of baking them:
the low and high caps are coplanar, so their bake comes out broken (renders as a grey translucent sheet).
Wall texels above the hoof base -> black paint (roughness 0.75), below -> cream terry (0.9); normal flat.
Paint/terry colours are sampled from the baked atlas itself (median of clearly painted / clearly terry texels).

usage: python3 bl_fix_cap_texels.py <work.blend> <planes.json> <maps_dir>   (edits glove_*.jpg in place)
Run on the unwrapped .blend from BEFORE baking: the bake assigns one material to every slot, so only the
pre-bake file still names the cap slots (Hoof_InnerWall / Terry_Inner). Same UVs either way."""
import sys, json, bpy, numpy as np
from mathutils import Vector
from PIL import Image, ImageDraw
BL, PJ, MD = sys.argv[1:4]
bpy.ops.wm.open_mainfile(filepath=BL)
P = json.load(open(PJ)); bco, bno = Vector(P["base_co"]), Vector(P["base_no"]).normalized()
col = Image.open(f"{MD}/glove_color.jpg").convert("RGB"); W, H = col.size
nrm = Image.open(f"{MD}/glove_normal.jpg").convert("RGB"); rgh = Image.open(f"{MD}/glove_roughness.jpg").convert("L")
a = np.asarray(col).astype(float); lum = a.mean(2)
paint = tuple(int(v) for v in np.median(a[(lum > 8) & (lum < 45)], 0)); terry = tuple(int(v) for v in np.median(a[lum > 190], 0))
print("paint", paint, "terry", terry)
mask_p = Image.new("L", (W, H), 0); mask_t = Image.new("L", (W, H), 0); dp, dt = ImageDraw.Draw(mask_p), ImageDraw.Draw(mask_t)
n = 0
for name in ("Glove_Palm", "Toe_IndexMiddle", "Toe_RingLittle"):
    o = bpy.data.objects[name]; me = o.data; mw = o.matrix_world
    mats = [m.name if m else "" for m in me.materials]
    capi = {i for i, nm in enumerate(mats) if nm in ("Hoof_InnerWall", "Terry_Inner")}
    assert capi or name == "Glove_Palm", f"{name}: no cap material slots - use the pre-bake .blend"
    uv = me.uv_layers.active.data
    for p in me.polygons:
        if p.material_index not in capi: continue
        pts = [(uv[li].uv.x * W, (1 - uv[li].uv.y) * H) for li in p.loop_indices]
        above = ((mw @ p.center) - bco).dot(bno) > 0
        (dp if above else dt).polygon(pts, fill=255); n += 1
print("cap faces painted:", n)
from PIL import ImageFilter
mp = mask_p.filter(ImageFilter.MaxFilter(5)); mt = mask_t.filter(ImageFilter.MaxFilter(5))   # cover the bake margin
col.paste(Image.new("RGB", (W, H), terry), mask=mt); col.paste(Image.new("RGB", (W, H), paint), mask=mp)
nrm.paste(Image.new("RGB", (W, H), (128, 128, 255)), mask=Image.fromarray(np.maximum(np.asarray(mp), np.asarray(mt))))
rs = rgh.size; mpr = mp.resize(rs); mtr = mt.resize(rs)
rgh.paste(Image.new("L", rs, int(0.90 * 255)), mask=mtr); rgh.paste(Image.new("L", rs, int(0.75 * 255)), mask=mpr)   # flat walls: rougher than the brushed outer paint, or they mirror the room at grazing angles
col.save(f"{MD}/glove_color.jpg", quality=90); nrm.save(f"{MD}/glove_normal.jpg", quality=92); rgh.save(f"{MD}/glove_roughness.jpg", quality=92)
