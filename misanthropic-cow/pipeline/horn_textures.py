"""Round 47: textures for the horns and the broken horn's exposed wires (the owner: "texture the horn wires and add
horn normal maps").

* horns: papier-mache painted yellow with black bands (the costume's, and the v09 colour maps).  The colour maps are
  kept; each horn gets a normal map: soft lumps of the pasted paper layers, fine paper fibre and brush marks, and the
  black paint standing a little proud of the yellow at the bands' edges.  The two horns' UVs run at different scales
  (and the broken one wraps round a seam), so the relief is made in metres on each horn's own UV scale, with noise
  that tiles both ways.
* wires: the dark galvanised steel armature wire that sticks out of the broken horn: drawing lines along the wire, a
  mottled zinc coat, dark specks and a few rust freckles.  UVs from assets.wire_uv: u round the wire, v along it,
  one unit every WIRE_V m.

Photos supplied in textures/ (see handoff/TEXTURE_PROMPTS.md) replace or refine the procedural maps:
* horn_paint.png/.jpg: a seamless swatch of the painted papier-mache surface, about HORN_SWATCH m across; its
  brightness detail is laid over the horns' colour maps (keeping their bands) and it gives the normal map's relief;
* horn_wire.png/.jpg: a seamless swatch of the wire's surface, lines running down the image, spanning its girth
  across (tiled along the wire like the cord)."""
import io
import numpy as np
from PIL import Image
import tail_textures as TT

HORN_SWATCH = .05            # m across a supplied horn_paint swatch (round 48: .03 made its grain read as fuzz)
WIRE_R = .00075              # the exposed wires' radius (m; 4.6 mm round, from their UVs)
WIRE_V = .03                 # m of wire per texture unit along it
WIRE_W, WIRE_H = 128, 512


def _field(h, w, mpu, mpv, scale, seed, aniso=(1., 1.)):
    """Periodic (tiling) gaussian noise on an h x w texture whose u unit spans mpu m and v unit mpv m, with features
    about `scale` m across (stretched by aniso = (along u, along v)).  Unit variance."""
    g = np.random.default_rng(seed)
    wn = np.fft.fft2(g.normal(size=(h, w)))
    fu = np.fft.fftfreq(w)[None, :] * w / mpu            # cycles per m along u
    fv = np.fft.fftfreq(h)[:, None] * h / mpv
    k2 = (fu * scale * aniso[0]) ** 2 + (fv * scale * aniso[1]) ** 2
    out = np.real(np.fft.ifft2(wn * np.exp(-k2 * 4)))
    return (out - out.mean()) / (out.std() + 1e-12)


def _uv_scale(v, uv, f):
    """Median metres per unit of u and of v over the faces."""
    v, uv, f = np.asarray(v, float), np.asarray(uv, float), np.asarray(f)
    e1, e2 = v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]]
    d1, d2 = uv[f[:, 1]] - uv[f[:, 0]], uv[f[:, 2]] - uv[f[:, 0]]
    det = d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]
    ok = (np.abs(det) > 1e-9) & (np.ptp(uv[f][:, :, 0], axis=1) < .5)
    Pu = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2])[ok] / det[ok, None]
    Pv = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1])[ok] / det[ok, None]
    return float(np.median(np.linalg.norm(Pu, axis=1))), float(np.median(np.linalg.norm(Pv, axis=1)))


def _normal(hgt, pu, pv):
    """Tangent-space normal map (0-255) from a height field in metres on texels pu m wide (u) and pv m tall (v);
    rows run from v 1 at the top, +Y up in texture space as in tail_textures."""
    dy, dx = np.gradient(hgt)
    n = np.stack([-dx / pu, dy / pv, np.ones_like(hgt)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return (n * .5 + .5) * 255


def _z(a):
    return (a - a.mean()) / (a.std() + 1e-12)


def _blur(a, px):
    from PIL import ImageFilter
    lo, hi = a.min(), a.max()
    im = Image.fromarray(((a - lo) / (hi - lo + 1e-12) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(px))
    return np.asarray(im, float) / 255 * (hi - lo) + lo


def horn_maps(col, part, seed=0, size=(512, 1024)):
    """The horn's colour map (RGB 0-255 array, rows = v from the top) and its normal map, both as JPEG bytes, at
    size (w, h).  part: the horn's mesh (v, uv, f), for its UV scale."""
    w, h = size
    col = np.asarray(Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), float)
    mpu, mpv = _uv_scale(part['v'], part['uv'], part['f'])
    lumps = _field(h, w, mpu, mpv, .007, seed + 1)                 # the pasted paper layers
    fibre = _field(h, w, mpu, mpv, .0006, seed + 2)                # paper fibre and paint grain
    brush = _field(h, w, mpu, mpv, .0012, seed + 3, (3.5, .6))     # brush marks laid round the horn
    dark = col.mean(-1) < 90                                       # the black bands
    paint = _blur(dark.astype(float), 1.2)                         # the black paint a little proud at its edges
    hgt = 1.0 * lumps + .35 * fibre + .45 * brush + 2.2 * paint
    sup = TT.supplied('horn_paint')
    if sup is not None:
        sw = _swatch(sup, w, h, mpu, mpv)
        lum = sw.mean(-1)
        col = col * (lum / lum.mean())[..., None] ** .8
        # round 48: the relief from the photo's brightness, its finest grain softened (at the horns' size it read
        # as fuzz)
        hgt = .4 * lumps + .7 * _z(_blur(lum, 1.3)) + 2.2 * paint
    nrm = _normal(hgt * .00018, mpu / w, mpv / h)                  # about .18 mm of relief per unit
    return TT._jpeg(col, 90), TT._jpeg(nrm, 84)        # (the GLB must stay under 100 MiB)


def _swatch(img, w, h, mpu, mpv):
    """A supplied seamless swatch (HORN_SWATCH m across) tiled over a w x h texture of the given UV scale."""
    a = np.asarray(img, float)
    nu, nv = max(1, int(round(mpu / HORN_SWATCH))), max(1, int(round(mpv / HORN_SWATCH)))
    tile = np.tile(a, (nv, nu, 1))
    return np.asarray(Image.fromarray(np.clip(tile, 0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), float)


def wire_textures():
    """Colour and normal maps (JPEG bytes) of the dark galvanised wire: u round it, v along it (WIRE_V m)."""
    w, h = WIRE_W, WIRE_H
    mpu, mpv = 2 * np.pi * WIRE_R, WIRE_V
    lines = _field(h, w, mpu, mpv, .00015, 41, (1., 40.))          # drawing lines along the wire
    mottle = _field(h, w, mpu, mpv, .0025, 42)                     # the zinc coat's patches
    fine = _field(h, w, mpu, mpv, .0002, 43)
    specks = np.clip(_field(h, w, mpu, mpv, .0003, 44) - 2.6, 0, None)
    rust = np.clip(_field(h, w, mpu, mpv, .0015, 45) - 2.2, 0, None)
    tone = .42 + .05 * mottle + .025 * lines + .02 * fine - .25 * np.clip(specks, 0, 1)
    base = np.array([.92, .95, 1.0])[None, None] * tone[..., None]
    rc = np.array([.45, .26, .14])
    a = np.clip(rust * 1.5, 0, .8)[..., None]
    col = (base * (1 - a) + rc[None, None] * a) * 255
    hgt = .6 * lines + .3 * fine + .4 * mottle - 1.5 * np.clip(specks, 0, 1)
    nrm = _normal(hgt * .00003, mpu / w, mpv / h)
    sup = TT.supplied('horn_wire')
    if sup is not None:
        reps = max(1, int(round(WIRE_V / (mpu * sup.shape[0] / sup.shape[1]))))
        t = np.concatenate([sup] * reps, 0)
        col = np.asarray(Image.fromarray(np.clip(t, 0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), float)
        lum = col.mean(-1)
        nrm = _normal(_z(lum) * .00003, mpu / w, mpv / h)
    return TT._jpeg(col, 90), TT._jpeg(nrm, 90)
