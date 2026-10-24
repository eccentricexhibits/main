"""Crop a photo region and overlay a labelled pixel grid (original-pixel coordinates)."""
import sys
from PIL import Image, ImageDraw
src, out, x0, y0, x1, y1, step = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:8])
im = Image.open(src).convert('RGB').crop((x0, y0, x1, y1))
sc = 900 / max(x1 - x0, y1 - y0); im = im.resize((int((x1 - x0) * sc), int((y1 - y0) * sc)))
d = ImageDraw.Draw(im)
for x in range((x0 // step + 1) * step, x1, step):
    px = (x - x0) * sc; d.line([(px, 0), (px, im.size[1])], fill=(0, 200, 255) if x % (5 * step) else (255, 60, 60))
    d.text((px + 2, 2), str(x), fill=(0, 255, 255))
for y in range((y0 // step + 1) * step, y1, step):
    py = (y - y0) * sc; d.line([(0, py), (im.size[0], py)], fill=(0, 200, 255) if y % (5 * step) else (255, 60, 60))
    d.text((2, py + 2), str(y), fill=(0, 255, 255))
im.save(out)
