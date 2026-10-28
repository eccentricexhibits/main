"""Dump a Blender object's vertices/faces/normals and per-vertex Tripo base colour to .npz for numpy work.
usage: python3 bl_dump_mesh.py <file.blend> <object> <out.npz> [basecolor.jpg]"""
import sys, bpy, numpy as np
B, OBN, OUT = sys.argv[1:4]; BC = sys.argv[4] if len(sys.argv) > 4 else None
bpy.ops.wm.open_mainfile(filepath=B); me = bpy.data.objects[OBN].data
n = len(me.vertices); V = np.empty(n * 3, np.float32); me.vertices.foreach_get("co", V)
me.calc_loop_triangles() if hasattr(me, "calc_loop_triangles") else None
F = np.empty(len(me.polygons) * 3, np.int32); me.polygons.foreach_get("vertices", F)
N = np.empty(n * 3, np.float32); me.vertices.foreach_get("normal", N)
out = dict(V=V.reshape(-1, 3), F=F.reshape(-1, 3), N=N.reshape(-1, 3))
if BC:
    from PIL import Image; Image.MAX_IMAGE_PIXELS = None
    img = np.asarray(Image.open(BC).convert("RGB")); H, W = img.shape[:2]
    uv = np.empty(len(me.loops) * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", lv)
    col = img[np.clip(((1 - uv[:, 1] % 1) * (H - 1)).astype(int), 0, H - 1), np.clip((uv[:, 0] % 1 * (W - 1)).astype(int), 0, W - 1)]
    vc = np.zeros((n, 3)); cnt = np.zeros(n); np.add.at(vc, lv, col); np.add.at(cnt, lv, 1)
    out["C"] = (vc / np.maximum(cnt, 1)[:, None]).astype(np.uint8)
np.savez(OUT, **out); print({k: v.shape for k, v in out.items()})
