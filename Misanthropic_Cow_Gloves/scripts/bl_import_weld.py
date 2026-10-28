"""Import the Tripo OBJ into Blender, weld UV-seam duplicates, report holes, save a .blend.
usage: python3 bl_import_weld.py <model.obj> <out.blend>"""
import sys, time, bpy, bmesh
import numpy as np
OBJ, OUT = sys.argv[1:3]
t = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=OBJ, forward_axis='NEGATIVE_Z', up_axis='Y')
ob = bpy.context.selected_objects[0]; ob.name = "Glove_HIGH"
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)   # mesh data Z-up, front (back of hand) = -Y
me = ob.data
print("imported", len(me.vertices), "verts", len(me.polygons), "faces", round(time.time() - t, 1), "s")
bm = bmesh.new(); bm.from_mesh(me)
r = bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
nm = [e for e in bm.edges if not e.is_manifold]
bnd = [e for e in nm if e.is_boundary]
print("after weld:", len(bm.verts), "verts;", "non-manifold edges", len(nm), "of which boundary (holes)", len(bnd))
if bnd:
    co = np.array([[*e.verts[0].co] for e in bnd]); print("hole edges z-range (Blender Z = up):", co[:, 2].min().round(3), co[:, 2].max().round(3))
bm.to_mesh(me); bm.free()
for m in me.materials:
    if m and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                for l in list(n.inputs['Metallic'].links): m.node_tree.links.remove(l)
                n.inputs['Metallic'].default_value = 0.0
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT, round(time.time() - t, 1), "s; dims", [round(v, 3) for v in ob.dimensions])
