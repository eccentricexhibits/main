"""CPU review renderer (orthographic) for GLB-style Models."""
from pathlib import Path
import ctypes, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import glb as G

HERE = Path(__file__).resolve().parent
_lib = None


def lib():
    global _lib
    if _lib is None:
        src = HERE / 'raster.cpp'
        so = Path('/tmp') / f'cow_raster_{int(src.stat().st_mtime)}.so'
        if not so.exists():
            subprocess.run(['g++', '-O3', '-march=native', '-shared', '-fPIC', str(src), '-o', str(so)], check=True)
        L = ctypes.CDLL(str(so))
        F = np.ctypeslib.ndpointer(np.float32, flags='C_CONTIGUOUS')
        I = np.ctypeslib.ndpointer(np.int32, flags='C_CONTIGUOUS')
        U = np.ctypeslib.ndpointer(np.uint8, flags='C_CONTIGUOUS')
        vp = ctypes.c_void_p
        L.raster.argtypes = [ctypes.c_int, F, F, vp, vp, vp, ctypes.c_int, I, ctypes.c_int, ctypes.c_int,
                             ctypes.c_float, ctypes.c_float, ctypes.c_float, vp, ctypes.c_int, ctypes.c_int,
                             vp, ctypes.c_int, ctypes.c_int, ctypes.c_float, F, ctypes.c_float, ctypes.c_float,
                             ctypes.c_int, F, F]
        L.skin.argtypes = [ctypes.c_int, F, F, U, U, F, F, F]
        L.bake.argtypes = [ctypes.c_int, I, F, ctypes.c_int, F, ctypes.c_int, ctypes.c_int, F, U]
        _lib = L
    return _lib


def _ptr(a):
    return None if a is None else a.ctypes.data


class Renderer:
    def __init__(self, model):
        self.model = model
        self.cache = {}

    def image(self, i):
        if i not in self.cache:
            self.cache[i] = np.ascontiguousarray(G.image_array(self.model, i))
        return self.cache[i]

    def render(self, angle=0, el=0, size=(1200, 1500), center=(0, .85, 0), height=1.9, clay=False,
               parts=None, bg=True):
        L = lib()
        th, e = np.deg2rad(angle), np.deg2rad(el)
        fwd = np.array([np.sin(th) * np.cos(e), np.sin(e), np.cos(th) * np.cos(e)])
        right = np.array([np.cos(th), 0, -np.sin(th)])
        up = np.cross(fwd, right)
        basis = np.stack([right, up, fwd], 1)
        w, h = size
        depth = np.full((h, w), -1e20, np.float32)
        yy, xx = np.mgrid[:h, :w]
        rgb = np.broadcast_to(np.float32([.085, .098, .115]), (h, w, 3)).copy()
        if bg:
            rgb += (np.exp(-((xx / w - .5) / .6) ** 2 - ((yy / h - .45) / .6) ** 2)[:, :, None] * [.03, .033, .036]).astype(np.float32)
        rgb = np.ascontiguousarray(rgb, np.float32)
        scale = h * .9 / height
        for p in (parts if parts is not None else self.model.parts):
            ma = self.model.materials[p['material']]
            pb = ma.get('pbrMetallicRoughness', {})
            bt = pb.get('baseColorTexture')
            nt = ma.get('normalTexture')
            tex = self.image(bt['image']) if bt else None
            ntex = self.image(nt['image']) if nt else None
            uv = p['uv'] if not bt or bt.get('texCoord', 0) == 0 else p['uv1']
            uvn = None
            if nt:
                uvn = p['uv1'] if nt.get('texCoord', 0) == 1 else p['uv']
            uv = None if uv is None else np.ascontiguousarray(uv, np.float32)
            uvn = None if uvn is None else np.ascontiguousarray(uvn, np.float32)
            ao = None if p.get('ao') is None else np.ascontiguousarray(p['ao'], np.float32)
            v = np.ascontiguousarray((p['v'] - center) @ basis, np.float32)
            n = np.ascontiguousarray(p['n'] @ basis, np.float32)
            sheen = ma.get('extensions', {}).get('KHR_materials_sheen', {}).get('sheenColorFactor', [0])[0]
            L.raster(len(v), v, n, _ptr(uv), _ptr(uvn), _ptr(ao), len(p['f']), np.ascontiguousarray(p['f'], np.int32),
                     w, h, scale, w * .5, h * .5, _ptr(tex), 0 if tex is None else tex.shape[1], 0 if tex is None else tex.shape[0],
                     _ptr(ntex), 0 if ntex is None else ntex.shape[1], 0 if ntex is None else ntex.shape[0],
                     float(nt.get('scale', 1)) if nt else 1.0,
                     np.ascontiguousarray(pb.get('baseColorFactor', [1, 1, 1, 1])[:3], np.float32),
                     float(pb.get('roughnessFactor', .9)), float(sheen), int(clay), depth, rgb)
        return Image.fromarray(np.uint8(np.clip(rgb, 0, 1) * 255))


def skin_parts(model, mats):
    """Return posed copies of parts given (J,4,4) skinning matrices (global @ inverse bind)."""
    L = lib()
    m = np.ascontiguousarray(mats, np.float32)
    out = []
    for p in model.parts:
        v = np.empty_like(p['v'], dtype=np.float32)
        n = np.empty_like(p['n'], dtype=np.float32)
        L.skin(len(v), np.ascontiguousarray(p['v'], np.float32), np.ascontiguousarray(p['n'], np.float32),
               np.ascontiguousarray(p['j'], np.uint8), np.ascontiguousarray(p['w'], np.uint8), m, v, n)
        q = dict(p)
        q['v'] = v
        q['n'] = n
        out.append(q)
    return out


def label(im, title, sub=None):
    d = ImageDraw.Draw(im)
    font = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:
        f1 = ImageFont.truetype(font, max(14, im.height // 60))
        f2 = ImageFont.truetype(font, max(18, im.height // 40))
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((24, 18), 'THE MISANTHROPIC COW', font=f1, fill='#b0b4bc')
    d.text((23, 18 + f1.size + 6), title, font=f2, fill='#efeee9')
    if sub:
        d.text((24, im.height - f1.size - 20), sub, font=f1, fill='#dfc16d')
    return im


def bake(f, uv, attr, W, H):
    """Interpolate per-vertex attributes (N,k) over a UV chart. Returns (H,W,k) array and coverage mask."""
    attr = np.ascontiguousarray(attr, np.float32)
    k = attr.shape[1]
    out = np.zeros((H, W, k), np.float32)
    cover = np.zeros((H, W), np.uint8)
    lib().bake(len(f), np.ascontiguousarray(f, np.int32), np.ascontiguousarray(uv, np.float32), k, attr, W, H, out, cover)
    return out, cover > 0
