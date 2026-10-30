"""Stage 9c: live fabric materials for the cow and the mask, AO bake, final bakes (after the slipper project's bl_fabric2.py).

python3 -I bl_fabric_cow.py <cow_baked_work.blend> <tiles_dir> <mix_dir> <bake_dir> <out_dir> [body_size=4096] [mask_size=2048] [samples=2]

Material per object, driven by the sequential mix masks (make_mix_masks_cow.py):
- fabrics are box-projected tiles in object space (metres) at the size the tile prompts asked for; each also has a
  height map that feeds a Bump on top of the baked detail normal (from the full-detail model);
- solids (hooves, eyes, pupils, horn paint and rings, wire, cord, slits) are flat colours;
- the lace is see-through: its opacity tile mixes the lace over the black leggings;
- roughness, sheen and coat follow the same mix chain; metallic is 0 everywhere.
AO is baked to its own map (2K body, 1K mask) and NOT multiplied into the colour: it goes into the GLB as a separate
occlusion texture (no baked lighting in the colour). Final bakes: base colour, roughness, tangent normal.
Saves Cow_fabric_live.blend (live materials, external textures) and the baked maps.
"""
import sys, os, time
import bpy

SRC, TILES, MIX, BK, OUT = sys.argv[1:6]
BS = int(sys.argv[6]) if len(sys.argv) > 6 else 4096
MS = int(sys.argv[7]) if len(sys.argv) > 7 else 2048
SAMPLES = int(sys.argv[8]) if len(sys.argv) > 8 else 2
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=SRC)
for o in list(bpy.data.objects):
    if o.name.endswith("_HIGH"): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES

# class order matches make_mix_masks_cow.py. (tile, tile size cm, roughness, sheen, coat) or (rgb, None, rough, sheen, coat)
T = lambda n: f"{TILES}/{n}.png"
BODY = [("TILE_01_white_faux_fur", 10, 0.92, 0.5, 0), ("TILE_02_black_shag_fur", 10, 0.85, 0.5, 0), ("TILE_03_pink_fleece", 8, 0.88, 0.4, 0),
        ("TILE_04_beige_satin", 8, 0.35, 0.3, 0), ("LACE", 8, 0.70, 0.2, 0), ("TILE_06_black_leggings", 6, 0.75, 0.3, 0),
        ("TILE_07_white_fabric_paint", 6, 0.80, 0.0, 0), ("TILE_08_white_knit", 6, 0.90, 0.4, 0), ((0.012, 0.012, 0.014), None, 0.25, 0, 0.6),
        ("TILE_04b_gold_satin", 8, 0.35, 0.3, 0), ("TILE_06_black_leggings", 6, 0.80, 0.3, 0), ((0.80, 0.80, 0.78), None, 0.70, 0.2, 0),
        ((0.85, 0.70, 0.10), None, 0.50, 0, 0), ((0.015, 0.015, 0.015), None, 0.45, 0, 0), ((0.33, 0.33, 0.35), None, 0.30, 0, 0)]
MASK = [("TILE_09_cracked_white_plaster", 8, 0.75, 0, 0), ("TILE_09b_glossy_black_paint", 8, 0.35, 0, 0.3), ((0.85, 0.62, 0.04), None, 0.10, 0, 0.8),
        ((0.008, 0.008, 0.008), None, 0.10, 0, 0.8), ("TILE_10_red_flocked_snout", 5, 0.95, 0.6, 0), ((0.01, 0.01, 0.01), None, 0.85, 0, 0)]


def img(path, data=False):
    im = bpy.data.images.load(path, check_existing=True)
    if data: im.colorspace_settings.name = "Non-Color"
    return im


def sock(node, name, kind, out=False):
    kind = {"FLOAT": "VALUE"}.get(kind, kind)
    for s in (node.outputs if out else node.inputs):
        if s.name == name and s.type == kind: return s
    raise KeyError(name)


def build(ob, tag, classes, mixfiles, normal_png, ao_size):
    mat = bpy.data.materials.new(f"{tag}_Fabric"); mat.use_nodes = True
    nt = mat.node_tree; N = nt.nodes; Lk = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial"); out.location = (2400, 0)
    bs = N.new("ShaderNodeBsdfPrincipled"); bs.location = (2000, 0); Lk.new(bs.outputs["BSDF"], out.inputs["Surface"])
    bs.inputs["Metallic"].default_value = 0.0; bs.inputs["Specular IOR Level"].default_value = 0.35
    uvm = N.new("ShaderNodeUVMap"); uvm.location = (-2200, -900)

    def uvtex(image, loc, label):
        n = N.new("ShaderNodeTexImage"); n.image = image; n.location = loc; n.label = label; n.interpolation = "Linear"
        Lk.new(uvm.outputs["UV"], n.inputs["Vector"]); return n
    fac = [None]
    for i, mf in enumerate(mixfiles):
        t = uvtex(img(f"{MIX}/{mf}", True), (-1800, 900 - i * 260), mf)
        sp = N.new("ShaderNodeSeparateColor"); sp.location = (-1550, 900 - i * 260); Lk.new(t.outputs["Color"], sp.inputs["Color"])
        fac += [sp.outputs[k] for k in range(3)]
    tc = N.new("ShaderNodeTexCoord"); tc.location = (-2200, -300)
    maps = {}

    def tiled(path, cm, data, loc):
        key = cm
        if key not in maps:
            mp = N.new("ShaderNodeMapping"); mp.location = (loc[0] - 300, loc[1]); k = 100.0 / cm
            mp.inputs["Scale"].default_value = (k, k, k); Lk.new(tc.outputs["Object"], mp.inputs["Vector"]); maps[key] = mp
        n = N.new("ShaderNodeTexImage"); n.image = img(path, data); n.projection = "BOX"; n.projection_blend = 0.3; n.location = loc
        Lk.new(maps[key].outputs["Vector"], n.inputs["Vector"]); return n
    cols, hts, rgh, shn, cot = [], [], [], [], []
    for i, (src, cm, r, s, c) in enumerate(classes):
        y = -300 - i * 280
        if isinstance(src, tuple):
            cols.append(src + (1,)); hts.append(0.5)
        elif src == "LACE":
            lace = tiled(T("TILE_05_beige_lace"), cm, False, (-1200, y)); lop = tiled(T("TILE_05_beige_lace_opacity"), cm, True, (-950, y))
            under = tiled(T("TILE_06_black_leggings"), 6, False, (-700, y))
            mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.location = (-450, y)
            Lk.new(lop.outputs["Color"], mx.inputs["Factor"]); Lk.new(under.outputs["Color"], sock(mx, "A", "RGBA")); Lk.new(lace.outputs["Color"], sock(mx, "B", "RGBA"))
            cols.append(sock(mx, "Result", "RGBA", out=True))
            hts.append(tiled(T("TILE_05_beige_lace_height"), cm, True, (-200, y)).outputs["Color"])
        else:
            cols.append(tiled(T(src), cm, False, (-1200, y)).outputs["Color"])
            hts.append(tiled(T(src + "_height"), cm, True, (-950, y)).outputs["Color"])
        rgh.append(r); shn.append(s); cot.append(c)

    def chain(values, kind, x0, y0):
        acc = None
        for i, v in enumerate(values):
            if i == 0:
                if isinstance(v, (float, int, tuple)):
                    vn = N.new("ShaderNodeValue" if kind == "FLOAT" else "ShaderNodeRGB"); vn.location = (x0 - 200, y0)
                    vn.outputs[0].default_value = v; acc = vn.outputs[0]
                else: acc = v
                continue
            mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA" if kind == "RGBA" else "FLOAT"; mx.location = (x0 + i * 160, y0)
            Lk.new(fac[i], mx.inputs["Factor"])
            Lk.new(acc, sock(mx, "A", kind))
            b_s = sock(mx, "B", kind)
            if isinstance(v, (float, int, tuple)): b_s.default_value = v
            else: Lk.new(v, b_s)
            acc = sock(mx, "Result", kind, out=True)
        return acc
    col_out = chain(cols, "RGBA", -100, 1300); hgt_out = chain(hts, "FLOAT", -100, 1600)
    rgh_out = chain(rgh, "FLOAT", -100, 1900); shn_out = chain(shn, "FLOAT", -100, 2200); cot_out = chain(cot, "FLOAT", -100, 2500)
    Lk.new(col_out, bs.inputs["Base Color"]); Lk.new(col_out, bs.inputs["Sheen Tint"])
    Lk.new(rgh_out, bs.inputs["Roughness"]); Lk.new(shn_out, bs.inputs["Sheen Weight"]); bs.inputs["Sheen Roughness"].default_value = 0.5
    Lk.new(cot_out, bs.inputs["Coat Weight"]); bs.inputs["Coat Roughness"].default_value = 0.05
    nmt = uvtex(img(normal_png, True), (1100, -600), "detail normal (from the full-detail model)")
    nmap = N.new("ShaderNodeNormalMap"); nmap.location = (1400, -600); Lk.new(nmt.outputs["Color"], nmap.inputs["Color"])
    bump = N.new("ShaderNodeBump"); bump.location = (1700, -500)
    bump.inputs["Strength"].default_value = 0.3; bump.inputs["Distance"].default_value = 0.0015
    Lk.new(hgt_out, bump.inputs["Height"]); Lk.new(nmap.outputs["Normal"], bump.inputs["Normal"]); Lk.new(bump.outputs["Normal"], bs.inputs["Normal"])
    tgt = N.new("ShaderNodeTexImage"); tgt.name = "BAKE_TARGET"; tgt.location = (2000, 700); tgt.label = "bake target"
    ob.data.materials.clear(); ob.data.materials.append(mat)
    return mat, tgt


cow, mask = bpy.data.objects["Cow_LOW"], bpy.data.objects["Mask_LOW"]
jobs = [(cow, "Cow", BODY, ["mix_cow_a.png", "mix_cow_b.png", "mix_cow_c.png", "mix_cow_d.png", "mix_cow_e.png"], f"{BK}/cow_normal_4096.png", 2048, BS),
        (mask, "Mask", MASK, ["mix_mask_a.png", "mix_mask_b.png"], f"{BK}/mask_normal_2048.png", 1024, MS)]
built = [(ob, tag, *build(ob, tag, cl, mf, nrm, ao), ao, size) for ob, tag, cl, mf, nrm, ao, size in jobs]
print(f"materials built {time.time() - t0:.0f}s", flush=True)

sc.world = sc.world or bpy.data.worlds.new("World"); sc.world.light_settings.distance = 0.05
bk = sc.render.bake; bk.use_selected_to_active = False; bk.margin = 8; bk.margin_type = "EXTEND"
for ob, tag, mat, tgt, ao, size in built:
    for o in sc.objects: o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob; mat.node_tree.nodes.active = tgt
    for kind, key, data, n, smp, kw in (("AO", "ao", True, ao, 16, {}), ("DIFFUSE", "basecolor", False, size, SAMPLES, {"pass_filter": {"COLOR"}}),
                                         ("ROUGHNESS", "roughness", True, size, SAMPLES, {}), ("NORMAL", "normal", True, size, SAMPLES, {"normal_space": "TANGENT"})):
        t = time.time(); sc.cycles.samples = smp
        im = bpy.data.images.new(f"{tag}_{key}", n, n, alpha=False, is_data=data)
        if data: im.colorspace_settings.name = "Non-Color"
        tgt.image = im
        bpy.ops.object.bake(type=kind, use_clear=True, **kw)
        im.filepath_raw = f"{OUT}/{tag}_{key}_{n}.png"; im.file_format = "PNG"; im.save()
        print(f"{tag} {key} {n}: {time.time() - t:.0f}s", flush=True)
    tgt.image = None
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/Cow_fabric_live.blend")
print(f"saved {OUT}/Cow_fabric_live.blend, {time.time() - t0:.0f}s")
