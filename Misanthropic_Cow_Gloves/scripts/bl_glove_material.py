"""Live terry + painted-hoof material for the three glove parts, AO, and final bakes (playbook stage 9c).

usage: python3 bl_glove_material.py <in.blend> <tiles_dir> <mask_paint.png> <detail_normal.jpg> <out_dir> <size> <samples>
                                    <mode: live | live:<ao.png> | ao_only | <ao.png>> [height_cm=24.7] [passes]
AO: the raw bake is denoised and normalised outside (open surfaces = 1, see the handoff) and multiplied in at 0.5.
  live      build the material and save <out_dir>/Glove_live.blend (no bakes)
  live:<ao.png>  same, with that AO multiplied in (for the delivered live .blend)
  ao_only   bake ambient occlusion to <out_dir>/ao_raw_<size>.png (denoise it outside, then run again with it)
  <ao.png>  build with that AO multiplied in, bake final colour / roughness / tangent normal into the shared atlas
            (<out_dir>/glove_{basecolor,roughness,normal}_<size>.png) and save Glove_live.blend

Material: one shader for all parts. Tiles are box-projected from each part's OWN object coordinates at real size
(terry 4 cm, hoof paint 6 cm), so on the toes the brush strokes run along local Z, base to tip, and move with the
toe when it spreads. mask_paint.png (UV) switches terry -> paint. Height from the tiles is bumped on top of the
baked detail normal from the full Tripo model (which carries the hoof's stroke grooves and the terry lumps).
Units: the model's units per metre are derived from its height (height_cm), so this works on the work file
(0.97 units tall) and on the real-size export alike.
"""
import sys, os, time, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bake_atlas import uv_ownership, Atlas
BL, TILES, MASK, NRM, OUT, SIZE, SAMP, MODE = sys.argv[1:9]
SIZE, SAMP = int(SIZE), int(SAMP); H_CM = float(sys.argv[9]) if len(sys.argv) > 9 else 24.7
PASSES = sys.argv[10].split(",") if len(sys.argv) > 10 else ["basecolor", "roughness", "normal"]
AO_FAC = 0.5
os.makedirs(OUT, exist_ok=True); t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=BL)
hc = bpy.data.collections.get("HIGH")
if hc:
    for o in list(hc.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(hc)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMP
parts = [o for o in bpy.data.objects if o.type == "MESH" and ("Palm" in o.name or "Toe_" in o.name)]
zs = [(o.matrix_world @ v.co).z for o in parts for v in o.data.vertices]
U = (max(zs) - min(zs)) / (H_CM / 100)                    # model units per metre
def m(cm): return cm / 100 * U
def img(path, noncolor=False):
    im = bpy.data.images.load(path, check_existing=True)
    if noncolor: im.colorspace_settings.name = "Non-Color"
    return im

mat = bpy.data.materials.new("Glove_Terry_Hoof_live"); mat.use_nodes = True
nt = mat.node_tree; N = nt.nodes; Lk = nt.links; N.clear()
outn = N.new("ShaderNodeOutputMaterial"); outn.location = (1900, 0)
bs = N.new("ShaderNodeBsdfPrincipled"); bs.location = (1550, 0); Lk.new(bs.outputs["BSDF"], outn.inputs["Surface"])
bs.inputs["Metallic"].default_value = 0.0; bs.inputs["Specular IOR Level"].default_value = 0.4
uvm = N.new("ShaderNodeUVMap"); uvm.location = (-1500, 700)
tc = N.new("ShaderNodeTexCoord"); tc.location = (-1500, -200)
def uvtex(image, loc, label):
    n = N.new("ShaderNodeTexImage"); n.image = image; n.location = loc; n.label = label
    Lk.new(uvm.outputs["UV"], n.inputs["Vector"]); return n
def boxtex(image, tile_cm, loc, label):
    mp = N.new("ShaderNodeMapping"); mp.location = (loc[0] - 250, loc[1]); k = 1 / m(tile_cm)
    mp.inputs["Scale"].default_value = (k, k, k); Lk.new(tc.outputs["Object"], mp.inputs["Vector"])
    n = N.new("ShaderNodeTexImage"); n.image = image; n.projection = "BOX"; n.projection_blend = 0.3
    n.location = loc; n.label = label; Lk.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
def mix(kind, fac, a, b, loc, blend="MIX"):
    x = N.new("ShaderNodeMix"); x.data_type = kind; x.blend_type = blend; x.location = loc
    Lk.new(fac, x.inputs["Factor"]) if not isinstance(fac, float) else x.inputs["Factor"].__setattr__("default_value", fac)
    sa = [s for s in x.inputs if s.name == "A" and s.type == ("RGBA" if kind == "RGBA" else "VALUE")][0]
    sb = [s for s in x.inputs if s.name == "B" and s.type == ("RGBA" if kind == "RGBA" else "VALUE")][0]
    for s, v in ((sa, a), (sb, b)):
        if isinstance(v, (float, int, tuple)): s.default_value = v
        else: Lk.new(v, s)
    return [s for s in x.outputs if s.name == "Result" and s.type == ("RGBA" if kind == "RGBA" else "VALUE")][0], x

mk = uvtex(img(MASK, True), (-1100, 700), "mask: paint (white) vs terry"); mk.interpolation = "Linear"
fac = mk.outputs["Color"]
tc_terry = boxtex(img(f"{TILES}/tile_terry.jpg"), 4.0, (-800, 300), "terry (4 cm tile)")
ht_terry = boxtex(img(f"{TILES}/height_terry.jpg", True), 4.0, (-800, 0), "terry height")
tc_paint = boxtex(img(f"{TILES}/tile_paint.jpg"), 6.0, (-800, -300), "hoof paint (6 cm tile, strokes along local Z)")
ht_paint = boxtex(img(f"{TILES}/height_paint.jpg", True), 6.0, (-800, -600), "paint height")
rg_paint = boxtex(img(f"{TILES}/rough_paint.jpg", True), 6.0, (-800, -900), "paint roughness")

col, _ = mix("RGBA", fac, tc_terry.outputs["Color"], tc_paint.outputs["Color"], (-300, 300))
hp_scaled, _ = mix("FLOAT", 0.45, 0.5, ht_paint.outputs["Color"], (-500, -600))      # strokes: shallower relief
hgt, _ = mix("FLOAT", fac, ht_terry.outputs["Color"], hp_scaled, (-300, 0))
rgh, _ = mix("FLOAT", fac, 0.92, rg_paint.outputs["Color"], (-300, -300))
shn, _ = mix("FLOAT", fac, 0.45, 0.0, (-300, -500))
ao_file = MODE.split(":", 1)[1] if MODE.startswith("live:") else (MODE if MODE.endswith(".png") else None)
if ao_file:
    AO = bpy.data.images.load(ao_file); AO.colorspace_settings.name = "Non-Color"; AO.name = "bake_ao"
else:
    AO = bpy.data.images.new("bake_ao", SIZE, SIZE, alpha=False); AO.colorspace_settings.name = "Non-Color"
aon = uvtex(AO, (-300, 700), "baked AO")
col_ao, aomix = mix("RGBA", 0.0, col, aon.outputs["Color"], (100, 400), blend="MULTIPLY")
Lk.new(col_ao, bs.inputs["Base Color"]); Lk.new(col_ao, bs.inputs["Sheen Tint"])
Lk.new(rgh, bs.inputs["Roughness"]); Lk.new(shn, bs.inputs["Sheen Weight"]); bs.inputs["Sheen Roughness"].default_value = 0.5
nmt = uvtex(img(NRM, True), (500, -700), "detail normal (full Tripo model)")
nmap = N.new("ShaderNodeNormalMap"); nmap.location = (800, -700); Lk.new(nmt.outputs["Color"], nmap.inputs["Color"])
bump = N.new("ShaderNodeBump"); bump.location = (1150, -500)
bump.inputs["Strength"].default_value = 0.45; bump.inputs["Distance"].default_value = m(0.15)
Lk.new(hgt, bump.inputs["Height"]); Lk.new(nmap.outputs["Normal"], bump.inputs["Normal"]); Lk.new(bump.outputs["Normal"], bs.inputs["Normal"])
tgt = N.new("ShaderNodeTexImage"); tgt.name = "BAKE_TARGET"; tgt.location = (1550, 600); tgt.label = "bake target"
for o in parts:
    me = o.data; me.materials.clear(); me.materials.append(mat)
    me.polygons.foreach_set("material_index", [0] * len(me.polygons)); me.update()
print(f"material built; {U:.3f} units per metre", round(time.time() - t0, 1), "s", flush=True)
owners = uv_ownership(parts, SIZE) if MODE == "ao_only" or (ao_file and not MODE.startswith("live")) else None

def bake_all(kind, image, **kw):
    """Each part baked into a cleared image, only its own texels kept, margin added once (bake_atlas.py)."""
    tgt.image = image; N.active = tgt; margin = 16 if SIZE >= 4096 else 8
    bk = sc.render.bake; bk.use_selected_to_active = False; bk.margin = margin; bk.margin_type = "EXTEND"
    t = time.time(); acc = Atlas(SIZE, owners)
    for i, o in enumerate(parts):
        for x in sc.objects: x.select_set(False)
        o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.bake(type=kind, use_clear=True, **kw); acc.add(i, image)
    acc.finish(margin); acc.write(image)
    print(kind, "baked", round(time.time() - t, 1), "s", flush=True)

if MODE == "ao_only":
    sc.world = sc.world or bpy.data.worlds.new("World"); sc.world.light_settings.distance = m(1.5)
    bake_all("AO", AO)
    AO.filepath_raw = f"{OUT}/ao_raw_{SIZE}.png"; AO.file_format = "PNG"; AO.save(); print("saved ao"); sys.exit(0)
if ao_file:
    aomix.inputs["Factor"].default_value = AO_FAC
if ao_file and not MODE.startswith("live"):
    for kind, key, noncolor, kw in (("DIFFUSE", "basecolor", False, {"pass_filter": {"COLOR"}}),
                                     ("ROUGHNESS", "roughness", True, {}),
                                     ("NORMAL", "normal", True, {"normal_space": "TANGENT"})):
        if key not in PASSES: continue
        im = bpy.data.images.new(f"glove_{key}", SIZE, SIZE, alpha=False, is_data=noncolor)
        if noncolor: im.colorspace_settings.name = "Non-Color"
        bake_all(kind, im, **kw)
        im.filepath_raw = f"{OUT}/glove_{key}_{SIZE}.png"; im.file_format = "PNG"; im.save()
    tgt.image = None
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/Glove_live.blend")
print("saved", f"{OUT}/Glove_live.blend", round(time.time() - t0, 1), "s")
