import sys, bpy
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[1])
for o in bpy.data.objects:
    print(o.name, o.type, "parent:", o.parent.name if o.parent else None, "loc", [round(v,4) for v in o.matrix_world.translation], "faces", len(o.data.polygons) if o.type=='MESH' else "")
