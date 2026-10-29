"""Make a true-displacement copy of the live-material glove .blend (Cycles only; renders, not real-time).

usage: python3 bl_terry_displace.py <Glove_pair_live.blend> <displace_mask.png> <out.blend> [height_mm=1.2] [dice=mm:0.3]
                                     [soften_mm=0.12]
- Every glove part gets a Subdivision modifier, type SIMPLE (adds micro-polygons without rounding the shape) with
  Cycles adaptive subdivision. dice = mm:<edge> (default mm:0.3: micro-polygon edges of 0.3 mm on the object, about
  1.6 M micro-triangles per glove whatever the camera; terry loops are ~1.5 mm) or px:<size> (diced to <size>
  pixels on screen: finer in close-ups, but a 1 px dice of a 3 cm close-up ran out of 16 GB).
- The material displaces the terry along the normal by the terry tile's height map (box-projected in each part's
  own coordinates, as for the colour; softened by a Gaussian of soften_mm first, written to
  textures/height_terry_displace.png), times displace_mask.png (UV): 0 on the hoof and the cut walls, fading in
  over 3 mm from the wall edges so the palm and the toes still meet exactly. height_mm = full range of the map
  (midlevel 0.5; the loops stand about +-height/4 around the surface on average).
- Where the terry is displaced, its tile bump is switched off (the geometry carries it now); the hoof keeps its
  bump and the baked detail normal as before.
- Why soften: the tile's height has detail finer than the micro-polygons; displaced as is, it turns into sharp
  spikes (a burr-like outline with dark slivers between them). 0.3 mm softening was too much (it is about the
  loop size: patchy nubs); 0.12 mm keeps the loop pattern. Softened, the loops come out as rounded nubs and
  the fine grain stays in the bump (the unsoftened height still feeds it where the terry is not displaced, and the
  colour tile carries it everywhere).
The mask is copied to <out dir>/textures/ and referenced relatively; the .blend sits next to the live one.
"""
import sys, os, shutil, bpy
import numpy as np, cv2
B, MASK, OUT = sys.argv[1:4]
HMM = float(sys.argv[4]) if len(sys.argv) > 4 else 1.2
SOFT = float(sys.argv[6]) if len(sys.argv) > 6 else 0.12
DK, DV = (sys.argv[5] if len(sys.argv) > 5 else "mm:0.3").split(":"); DV = float(DV)
bpy.ops.wm.open_mainfile(filepath=B)
tex = os.path.join(os.path.dirname(os.path.abspath(OUT)), "textures"); os.makedirs(tex, exist_ok=True)
dst = os.path.join(tex, "displace_mask.png")
if os.path.abspath(MASK) != os.path.abspath(dst): shutil.copyfile(MASK, dst)

parts = [o for o in bpy.data.objects if o.type == "MESH"]
zs = [(o.matrix_world @ v.co).z for o in parts for v in o.data.vertices]
UPM = (max(zs) - min(zs)) / 0.247                                           # units per metre (glove 24.7 cm tall)
mat = bpy.data.materials["Glove_Terry_Hoof_live"]; nt = mat.node_tree; N, Lk = nt.nodes, nt.links
ht_terry = next(n for n in N if n.type == "TEX_IMAGE" and n.label == "terry height")
bump = next(n for n in N if n.type == "BUMP")
hgt_mix = bump.inputs["Height"].links[0].from_node                          # mix(paint mask, terry height, paint height)
a_in = next(s for s in hgt_mix.inputs if s.name == "A" and s.type == "VALUE")
uvm = next(n for n in N if n.type == "UVMAP")
outn = next(n for n in N if n.type == "OUTPUT_MATERIAL")

dm = N.new("ShaderNodeTexImage"); dm.label = "displace mask (terry, fades out at the cut walls)"; dm.location = (-1100, 1000)
dm.image = bpy.data.images.load(dst, check_existing=True); dm.image.colorspace_settings.name = "Non-Color"
dm.interpolation = "Linear"; Lk.new(uvm.outputs["UV"], dm.inputs["Vector"])
def fmix(fac, a, b, loc):
    x = N.new("ShaderNodeMix"); x.data_type = "FLOAT"; x.location = loc
    Lk.new(fac, x.inputs["Factor"])
    for name, v in (("A", a), ("B", b)):
        s = next(s for s in x.inputs if s.name == name and s.type == "VALUE")
        if isinstance(v, float): s.default_value = v
        else: Lk.new(v, s)
    return next(s for s in x.outputs if s.name == "Result" and s.type == "VALUE")
# bump: terry height only where it is NOT displaced (flat 0.5 elsewhere)
terry_bump = fmix(dm.outputs["Color"], ht_terry.outputs["Color"], 0.5, (-550, 150))
Lk.new(terry_bump, a_in)
# displacement: 0.5 (no move) outside the mask, terry height inside
hsrc = ht_terry.image
if SOFT > 0:                                     # softened copy of the terry height for the displacement only
    from PIL import Image
    a = np.asarray(Image.open(bpy.path.abspath(hsrc.filepath)).convert("L")).astype(np.float32); sd0 = a.std()
    tile_cm = 4.0; sig = SOFT / (tile_cm * 10) * a.shape[0]; pad = int(sig * 4) + 1   # terry tile = 4 cm
    a = cv2.GaussianBlur(np.pad(a, pad, mode="wrap"), (0, 0), sig)[pad:-pad, pad:-pad]  # wrap: still tiles
    a = 127.5 + (a - 127.5) * (sd0 / max(a.std(), 1e-3)) ** 0.5           # give back half the contrast the blur took
    hp = os.path.join(tex, "height_terry_displace.png"); Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(hp)
    hd = N.new("ShaderNodeTexImage"); hd.label = f"terry height, softened {SOFT} mm (displacement)"; hd.location = (1000, -1100)
    hd.image = bpy.data.images.load(hp, check_existing=True); hd.image.colorspace_settings.name = "Non-Color"
    hd.projection = "BOX"; hd.projection_blend = ht_terry.projection_blend
    Lk.new(ht_terry.inputs["Vector"].links[0].from_socket, hd.inputs["Vector"]); hsock = hd.outputs["Color"]
else:
    hsock = ht_terry.outputs["Color"]
dh = fmix(dm.outputs["Color"], 0.5, hsock, (1300, -900))
disp = N.new("ShaderNodeDisplacement"); disp.location = (1600, -900); disp.space = "OBJECT"
disp.inputs["Midlevel"].default_value = 0.5; disp.inputs["Scale"].default_value = HMM / 1000 * UPM
Lk.new(dh, disp.inputs["Height"]); Lk.new(disp.outputs["Displacement"], outn.inputs["Displacement"])
mat.displacement_method = "DISPLACEMENT"

sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.max_subdivisions = 12
if DK == "px": sc.cycles.dicing_rate = DV
for o in parts:
    m = o.modifiers.new("terry_displace", "SUBSURF"); m.subdivision_type = "SIMPLE"; m.levels = 0; m.render_levels = 6
    m.use_adaptive_subdivision = True
    if DK == "px": m.adaptive_space = "PIXEL"; m.adaptive_pixel_size = DV
    else: m.adaptive_space = "OBJECT"; m.adaptive_object_edge_length = DV / 1000 * UPM
bpy.ops.wm.save_as_mainfile(filepath=OUT)
try: bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_as_mainfile(filepath=OUT)
except Exception as e: print("paths:", e)
if os.path.exists(OUT + "1"): os.remove(OUT + "1")
print(f"saved {OUT}: {len(parts)} parts, adaptive {DK}:{DV}, terry height range {HMM} mm, softened {SOFT} mm ({UPM:.2f} units/m)")
