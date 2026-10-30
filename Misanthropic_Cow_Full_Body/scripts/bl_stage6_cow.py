"""Stage 6 cleanup in Blender (bpy): import the Tripo OBJ, weld vertices split at UV seams,
set metallic to 0 (fabric), and save the high-poly working .blend.

python3 bl_stage6_cow.py <model.obj> <out.blend>
Blender frame after OBJ import: Z up, front toward -Y, the costume's own left toward +X.
"""
import sys, time
import bpy, bmesh

OBJ, OUT = sys.argv[1], sys.argv[2]
t = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=OBJ, forward_axis="NEGATIVE_Z", up_axis="Y")
ob = bpy.context.selected_objects[0]
ob.name = "Cow_HIGH"; ob.data.name = "Cow_HIGH"
print("import transform: rot", [round(a, 3) for a in ob.rotation_euler], "scale", list(ob.scale))
bpy.context.view_layer.objects.active = ob
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)   # bake the Y-up -> Z-up conversion into the mesh
me = ob.data
print(f"imported {len(me.vertices):,} verts / {len(me.polygons):,} faces in {time.time() - t:.0f}s")

bm = bmesh.new(); bm.from_mesh(me)
n0 = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bm.to_mesh(me); bm.free()
print(f"welded {n0 - len(me.vertices):,} duplicate verts -> {len(me.vertices):,}")
me.shade_smooth() if hasattr(me, "shade_smooth") else None

for mat in me.materials:
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    sock = bsdf.inputs["Metallic"]
    for l in list(sock.links): nt.links.remove(l)
    sock.default_value = 0.0
    if "Sheen Weight" in bsdf.inputs: bsdf.inputs["Sheen Weight"].default_value = 0.3
    print("material", mat.name, "metallic -> 0")

lo = [min(v.co[i] for v in me.vertices) for i in range(3)]
hi = [max(v.co[i] for v in me.vertices) for i in range(3)]
print("bounds (Blender XYZ)", [round(x, 3) for x in lo], [round(x, 3) for x in hi])
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print(f"saved {OUT} in {time.time() - t:.0f}s")
