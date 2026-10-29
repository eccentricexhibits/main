"""Shared-atlas baking helper for the glove parts (imported by the bl_bake_*.py / bl_glove_material.py scripts).

Why: the three parts share one UV atlas and are baked one after another. Baking them all into the same image
with a margin lets a later part's margin (edge padding) paint over texels an earlier part already baked, wherever
their islands sit close together (v4: a ring-little terry island 20 px from the index-middle hoof island left
cream specks on the hoof). So each part is baked into its own image, every texel is taken only from the part
whose UV triangles cover it, and the margin is added once at the end (nearest covered texel).

    owners = uv_ownership(objs, size)                  # H x W int8: index into objs, -1 = empty (bottom row first)
    acc = Atlas(size, owners)
    for i, o in enumerate(objs): <bake o into img with use_clear=True>; acc.add(i, img)
    acc.finish(margin_px) -> write into a bpy image with acc.write(img)
"""
import numpy as np, cv2
from scipy import ndimage as nd


def uv_ownership(objs, size):
    """Rasterise each object's UV faces (pixel centres, same convention as Blender's bake)."""
    own = np.full((size, size), -1, np.int8)
    for k, o in enumerate(objs):
        me = o.data; uv = np.empty(len(me.loops) * 2, np.float64); me.uv_layers.active.data.foreach_get("uv", uv)
        uv = uv.reshape(-1, 2) * size - 0.5                       # pixel i has its centre at u*size = i + 0.5
        lt = np.empty(len(me.polygons), np.int64); me.polygons.foreach_get("loop_total", lt)
        ls = np.empty(len(me.polygons), np.int64); me.polygons.foreach_get("loop_start", ls)
        m = np.zeros((size, size), np.uint8)
        polys = [np.round(uv[s:s + n] * 16).astype(np.int32) for s, n in zip(ls, lt)]
        for i in range(0, len(polys), 4096):
            cv2.fillPoly(m, polys[i:i + 4096], 1, lineType=cv2.LINE_8, shift=4)
        own[(m > 0) & (own < 0)] = k
    return own


class Atlas:
    def __init__(self, size, owners):
        self.size, self.own = size, owners
        self.acc = np.zeros((size, size, 4), np.float32)

    def add(self, k, img):
        px = np.empty(self.size * self.size * 4, np.float32); img.pixels.foreach_get(px)
        px = px.reshape(self.size, self.size, 4); sel = self.own == k
        self.acc[sel] = px[sel]

    def finish(self, margin):
        cov = self.own >= 0
        _, (iy, ix) = nd.distance_transform_edt(~cov, return_indices=True)
        d = nd.distance_transform_edt(~cov)
        fill = (~cov) & (d <= margin)
        self.acc[fill] = self.acc[iy[fill], ix[fill]]
        self.acc[..., 3] = (cov | fill).astype(np.float32)     # alpha = baked or margin texel
        return self.acc

    def write(self, img):
        img.pixels.foreach_set(self.acc.ravel()); img.update()
