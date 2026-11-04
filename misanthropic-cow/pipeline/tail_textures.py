"""Round 45: textures for the tail (the owner: "is the bow tie / electrical cord textured yet?"; until now each piece
was one flat colour, the bow with a satin sheen).

* bow: gold satin.  A fine satin weave in the normal map, long soft sheen streaks running out along each wing from
  the pinched knot, and darker creases where the knot gathers the fabric.  UVs are a projection from behind (the
  bow is nearly flat), u across, v up.
* cord: tan PVC two-core lamp cord.  Fine ribs along its length, the raised polarity rib along one core, and the
  embossed rating line real cords carry ("SPT-1 18AWG 2C 105C ...") along the other, repeating; slight tone
  variation.  The cord's own UVs: u round the section, v along it, one unit every 5 cm (tail.cord_mesh).
* plug: the same plastic with a light moulded grain; projected from behind.
* blades: brushed brass, the brushing along the blades; projected from the side.

All are made here procedurally (numpy + PIL) as JPEGs; normal maps are tangent-space, +Y up in texture space."""
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def _jpeg(a, q=92):
    buf = io.BytesIO()
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(buf, 'JPEG', quality=q)
    return buf.getvalue()


def _noise(h, w, scale, seed, octaves=3):
    """Smooth value noise in [-1, 1] (tileable), summed over octaves."""
    g = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp, tot = 1., 0.
    for o in range(octaves):
        gh, gw = max(2, int(h / scale * 2 ** o)), max(2, int(w / scale * 2 ** o))
        grid = g.uniform(-1, 1, (gh, gw))
        im = Image.fromarray(((grid + 1) * 127.5).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += amp * (np.asarray(im, float) / 127.5 - 1); tot += amp; amp *= .5
    return out / tot


def _normal_from_height(hgt, strength):
    """Tangent-space normal map from a height field (rows = v, top row = v 1)."""
    dy, dx = np.gradient(hgt)
    n = np.stack([-dx * strength, dy * strength, np.ones_like(hgt)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return (n * .5 + .5) * 255


# ---------------------------------------------------------------- bow
BOW_SIZE = 512
BOW_GOLD = np.array([.80, .56, .20])


def bow_uv(v, knot):
    """Projection from behind: u across (13 cm), v up (6 cm), centred on the knot."""
    q = np.asarray(v, float) - knot
    return np.stack([.5 + q[:, 0] / .13, .5 + q[:, 1] / .06], 1).astype(np.float32)


def bow_textures():
    n = BOW_SIZE
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1.)
    x = (xx - .5) * .13; y = (.5 - yy) * .06                    # metres, from the knot (row 0 = top)
    ax = np.abs(x)
    s = np.clip((ax - .008) / .052, 0, 1)
    # sheen streaks fanning out along each wing from the knot (satin catches the light along its folds)
    ang = np.arctan2(y, ax + .01)
    streak = _noise(n, n, 24, 3, 2)
    fan = np.sin(ang * 9 + 2.0 * streak) * .5 + .5
    tone = .92 + .10 * fan * (.4 + .6 * s) + .03 * _noise(n, n, 60, 5)
    # creases gathered into the knot: dark lines converging on it, strongest close in
    crease = np.exp(-(np.sin(ang * 7 + 1.3) ** 2) / .02) * np.clip(1 - s * 1.4, 0, 1)
    tone -= .16 * crease
    # the knot itself a touch darker and its wrap's edges
    knot = np.exp(-((x / .0125) ** 2 + (y / .016) ** 2))
    tone -= .07 * knot
    col = (BOW_GOLD[None, None] * tone[..., None]) ** (1 / 1.0) * 255
    col = np.clip(col, 0, 255)
    # satin weave: very fine, the warp floats running across
    weave = np.sin(xx * n * np.pi * .9) * .25 + np.sin((xx + yy) * n * np.pi * .45) * .12
    hgt = .6 * weave + 1.3 * crease + 1.0 * _noise(n, n, 40, 7)
    nrm = _normal_from_height(hgt, .9)
    return _jpeg(col), _jpeg(nrm)


# ---------------------------------------------------------------- cord
CORD_W, CORD_H = 128, 512          # u round the section, v along 5 cm
CORD_TAN = np.array([.72, .52, .24])
RATING = 'SPT-1  18AWG  2C  105°C  300V  VW-1  '


def cord_textures():
    w, h = CORD_W, CORD_H
    u = (np.arange(w) + .5) / w                                   # round the section: th = 2 pi u
    th = 2 * np.pi * u
    # ribs along the length all round, finer on the flat faces
    rib = .35 * np.sin(th * 46)[None, :].repeat(h, 0)
    # the polarity rib along one core (the outer edge of the +x core, th ~ 0)
    pol = np.exp(-(np.angle(np.exp(1j * th)) / .09) ** 2)[None, :].repeat(h, 0) * 1.6
    # the embossed rating line on the other core's face (th ~ pi + .45), repeating along the cord
    txt = Image.new('L', (h, 24), 0)
    d = ImageDraw.Draw(txt)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
    except Exception:
        font = ImageFont.load_default()
    d.text((4, 3), RATING, fill=255, font=font)
    txt = np.asarray(txt.filter(ImageFilter.GaussianBlur(.6)), float) / 255          # (24, h): along the cord in x
    band = np.zeros((h, w))
    c0 = int(round(((np.pi + .55) / (2 * np.pi)) * w)); half = 12
    cols = np.clip(np.arange(c0 - half, c0 + half), 0, w - 1)
    band[:, cols] = txt.T[::-1, :len(cols)]
    # (only variation that repeats every 5 cm along the cord: the texture tiles along it)
    v = (np.arange(h) + .5)[:, None] / h
    wob = np.sin(2 * np.pi * (2 * v + .3 * np.sin(th[None, :] * 3))) * .5 + np.sin(2 * np.pi * (5 * v + .7)) * .25
    hgt = rib + pol + 1.4 * band + .15 * wob
    nrm = _normal_from_height(hgt, 1.1)
    tone = 1. + .03 * wob - .05 * band - .02 * rib
    col = CORD_TAN[None, None] * tone[..., None] * 255
    return _jpeg(col), _jpeg(nrm)


# ---------------------------------------------------------------- plug and blades
def plug_uv(v, end):
    q = np.asarray(v, float) - end
    return np.stack([.5 + q[:, 0] / .03, .5 + q[:, 1] / .06], 1).astype(np.float32)


def blade_uv(v, end):
    q = np.asarray(v, float) - end
    return np.stack([.5 + q[:, 2] / .012, .5 + q[:, 1] / .06], 1).astype(np.float32)


def plug_textures():
    n = 256
    grain = _noise(n, n, 6, 17, 2)
    col = CORD_TAN[None, None] * (.97 + .03 * grain[..., None]) * 255
    nrm = _normal_from_height(.8 * grain + .3 * _noise(n, n, 2, 19, 1), 1.)
    return _jpeg(col), _jpeg(nrm)


def blade_textures():
    """Brushed brass: fine lines along the blades (v), varying across them (u)."""
    n = 256
    g = np.random.default_rng(23)
    lines = np.asarray(Image.fromarray(g.uniform(0, 255, (8, n)).astype(np.uint8)).resize((n, n), Image.BILINEAR), float) / 255
    col = np.array([.86, .72, .45])[None, None] * (.93 + .10 * lines[..., None]) * 255
    nrm = _normal_from_height(1.5 * lines, .6)
    return _jpeg(col), _jpeg(nrm)
