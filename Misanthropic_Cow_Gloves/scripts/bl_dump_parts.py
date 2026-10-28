"""Dump every mesh object of a .blend (world space) to one .npz: <name>_V, <name>_F, <name>_M (material idx),
<name>_O (origin). usage: python3 bl_dump_parts.py <file.blend> <out.npz>"""
import sys, bpy, numpy as np
bpy.ops.wm.open_mainfile(filepath=sys.argv[1]); out = {}
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    me = o.data; mw = np.array(o.matrix_world)
    V = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", V); V = V.reshape(-1, 3)
    V = V @ mw[:3, :3].T + mw[:3, 3]
    me.calc_loop_triangles(); T = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get("vertices", T)
    M = np.empty(len(me.loop_triangles), np.int32); me.loop_triangles.foreach_get("material_index", M)
    mats = [m.name if m else "" for m in me.materials]
    out[o.name + "_V"] = V; out[o.name + "_F"] = T.reshape(-1, 3); out[o.name + "_M"] = M
    out[o.name + "_O"] = np.array(o.matrix_world.translation); out[o.name + "_mats"] = np.array(mats)
np.savez(sys.argv[2], **out); print(sorted(k for k in out if k.endswith("_V")))
