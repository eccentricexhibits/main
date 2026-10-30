"""Stage 8b: bakes for the LOW cow (after the slipper project's bl_bake.py and bl_bake_geom.py).

python3 -I bl_bake_cow.py <cow_uv.blend> <out_dir> [body_size=4096] [mask_size=2048] [samples=2]

Cow_LOW  <- Cow_body_HIGH, Socks_HIGH, Tail_cord_HIGH, Horn_*_HIGH: base colour (Tripo's texture and the parts'
            flat colours) and tangent normal, selected-to-active.
Mask_LOW <- Mask_scan_HIGH: tangent normal (the scan has no colour).
Then per-texel geometry for the region masks, float .npy, row 0 = top of the image (v = 1):
  geom_<obj>_position, geom_<obj>_normal (object = world space here, metres) and, for Cow_LOW, geom_cow_part
  (the FACE attribute "part": 0 body, 1 socks, 2 tail, 3 long horn, 4 short horn, 5 wires; -1 = empty texel).
"""
import sys, os, time
import numpy as np, bpy

SRC, OUT = sys.argv[1:3]
BS = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
MS = int(sys.argv[4]) if len(sys.argv) > 4 else 2048
SAMPLES = int(sys.argv[5]) if len(sys.argv) > 5 else 2
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
bk = sc.render.bake; bk.margin = 8; bk.margin_type = "EXTEND"


def bake_target(lo, name):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    lo.data.materials.clear(); lo.data.materials.append(mat)
    n = mat.node_tree.nodes.new("ShaderNodeTexImage"); mat.node_tree.nodes.active = n
    return mat, n


def select(lo, his):
    for o in sc.objects: o.select_set(False)
    for h in his: h.select_set(True)
    lo.select_set(True); bpy.context.view_layer.objects.active = lo


def save_png(img, path):
    img.filepath_raw = path; img.file_format = "PNG"; img.save()


def surface_bakes(lo, his, tag, size, kinds):
    _, node = bake_target(lo, f"{tag}_bake")
    select(lo, his)
    bk.use_selected_to_active = True; bk.cage_extrusion = 0.005; bk.max_ray_distance = 0.02
    for kind in kinds:
        t = time.time()
        img = bpy.data.images.new(f"{tag}_{kind}", size, size, alpha=False, is_data=(kind != "color"))
        if kind != "color": img.colorspace_settings.name = "Non-Color"
        node.image = img
        if kind == "color": bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, use_clear=True)
        else: bk.normal_space = "TANGENT"; bpy.ops.object.bake(type="NORMAL", use_clear=True)
        save_png(img, f"{OUT}/{tag}_{kind}_{size}.png")
        print(f"{tag} {kind} {size}: {time.time() - t:.0f}s", flush=True)


def geom_bakes(lo, tag, size, part=False):
    mat = bpy.data.materials.new(f"{tag}_geom"); mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    geo = nt.nodes.new("ShaderNodeNewGeometry"); node = nt.nodes.new("ShaderNodeTexImage")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    lo.data.materials.clear(); lo.data.materials.append(mat)
    select(lo, []); bk.use_selected_to_active = False
    srcs = [("position", geo.outputs["Position"]), ("normal", geo.outputs["Normal"])]
    if part:
        at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = "GEOMETRY"; at.attribute_name = "part"
        srcs.append(("part", at.outputs["Fac"]))
    for kind, sock in srcs:
        t = time.time()
        img = bpy.data.images.new(f"{tag}_geom_{kind}", size, size, alpha=True, float_buffer=True, is_data=True)
        img.colorspace_settings.name = "Non-Color"
        node.image = img; nt.nodes.active = node
        nt.links.new(sock, em.inputs["Color"])
        bpy.ops.object.bake(type="EMIT", use_clear=True)
        a = np.empty(size * size * 4, np.float32); img.pixels.foreach_get(a); a = a.reshape(size, size, 4)[::-1]
        if kind == "part":
            p = np.where(a[..., 3] > 0.5, np.round(a[..., 0]), -1).astype(np.int8); np.save(f"{OUT}/geom_{tag}_part.npy", p)
        else:
            np.save(f"{OUT}/geom_{tag}_{kind}.npy", a[..., :3].astype(np.float32))
            if kind == "position": np.save(f"{OUT}/geom_{tag}_coverage.npy", a[..., 3] > 0.5)
        print(f"{tag} geom {kind}: {time.time() - t:.0f}s", flush=True)


O = bpy.data.objects
cow, mask = O["Cow_LOW"], O["Mask_LOW"]
his = [O[n] for n in ("Cow_body_HIGH", "Socks_HIGH", "Tail_cord_HIGH", "Horn_long_L_HIGH", "Horn_short_R_HIGH", "Horn_wires_R_HIGH")]
surface_bakes(cow, his, "cow", BS, ("color", "normal"))
surface_bakes(mask, [O["Mask_scan_HIGH"]], "mask", MS, ("normal",))
geom_bakes(cow, "cow", BS, part=True)
geom_bakes(mask, "mask", MS)
for ob, fn in ((cow, "Cow_LOW"), (mask, "Mask_LOW")):            # UV'd meshes for the region previews (Z up, as in Blender)
    select(ob, [])
    bpy.ops.wm.obj_export(filepath=f"{OUT}/{fn}.obj", export_selected_objects=True, export_materials=False, export_uv=True,
                          export_normals=True, forward_axis="Y", up_axis="Z")
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/cow_baked_work.blend")
print(f"done in {time.time() - t0:.0f}s")
