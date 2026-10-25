"""De-light the photographed mask texture: flatten baked shading so the white paint reads white.

The original photographs are kept unchanged in the source package; this produces an adjusted copy.
Method: estimate the local illumination as a smoothed upper envelope of luminance (the white paint),
divide it out, then apply a gentle tone curve.  Saturated colours (gold eyes, red muzzle) keep their hue.
"""
import numpy as np
from PIL import Image
from scipy import ndimage


def delight(rgb, radius=48, target=.93, strength=.85):
    a = rgb.astype(np.float64) / 255
    lin = a ** 2.2
    lum = lin @ [.2126, .7152, .0722]
    env = ndimage.maximum_filter(ndimage.gaussian_filter(lum, 3), size=radius)
    env = ndimage.gaussian_filter(env, radius * .6)
    env = np.maximum(env, .02)
    gain = (target ** 2.2 / env) ** strength
    gain = np.clip(gain, 1, 4.5)
    out = np.clip(lin * gain[..., None], 0, 1) ** (1 / 2.2)
    # keep near-black paint black: blend back toward the original where it was very dark
    dark = np.clip((a.mean(-1) - .06) / .10, 0, 1)[..., None]
    out = a + (out - a) * dark
    return np.uint8(np.clip(out, 0, 1) * 255 + .5)


if __name__ == '__main__':
    import sys
    im = np.asarray(Image.open(sys.argv[1]).convert('RGB'))
    Image.fromarray(delight(im)).save(sys.argv[2], quality=93)
