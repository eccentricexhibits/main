"""Quick animation-test GLB from the split high-poly: uniform decimation per part, plain colours, pivots and
parenting kept. Not the final asset (no UVs/textures yet).
usage: python3 bl_preview_glb.py <split.blend> <out.glb> [ratio=0.04]"""
import sys, bpy
B, OUT = sys.argv[1:3]; R = float(sys.argv[3]) if len(sys.argv) > 3 else 0.04
bpy.ops.wm.open_mainfile(filepath=B)
cols = {"Glove_Mitten": (0.86, 0.82, 0.70), "Hoof_Toe_IndexMiddle": (0.04, 0.04, 0.045), "Hoof_Toe_RingLittle": (0.04, 0.04, 0.045)}
for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    m = o.modifiers.new("dec", 'DECIMATE'); m.ratio = R
    bpy.context.view_layer.objects.active = o
    with bpy.context.temp_override(object=o, active_object=o):
        bpy.ops.object.modifier_apply(modifier="dec")
    mat = bpy.data.materials.new(o.name + "_preview"); mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*cols.get(o.name, (0.5, 0.5, 0.5)), 1)
    b.inputs["Roughness"].default_value = 0.85 if "Mitten" in o.name else 0.5; b.inputs["Metallic"].default_value = 0
    o.data.materials.clear(); o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    print(o.name, len(o.data.polygons), "faces")
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_apply=False)
print("wrote", OUT)
