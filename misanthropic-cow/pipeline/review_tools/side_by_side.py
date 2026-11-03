"""Two versions of the animation library side by side in one video (round 39: round 38 against round 39).

usage: python review_tools/side_by_side.py <rigged_a.pkl> <rigged_b.pkl> <out.mp4> "<label a>" "<label b>"
Both pickles are rig_bench.py's `rigged` output (or build_v10.py's rigged.pkl).  Each clip plays on each side at
its own length (they may differ), for as long as the longer of the two takes over the loops in PLAN."""
import sys, pickle, time
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import render_dance as RD

PLAN = [('Idle', 1), ('Walk', 4), ('Run', 6), ('Sneak', 2), ('Jumping Jacks', 1), ('Look Around', 1), ('Chicken Dance', 1),
        ('Depressed Walk', 3), ('Crying', 1), ('Exasperated', 1)]


def main(a, b, out, la, lb, size=(540, 720), angle=-24):
    A, Bd = pickle.load(open(a, 'rb')), pickle.load(open(b, 'rb'))
    enc = RD.encoder(out, (2 * size[0], size[1]))
    t0 = time.time()
    for name, loops in PLAN:
        ca, cb = A['clips'][name], Bd['clips'][name]
        fa, fb = len(ca['times']) - 1, len(cb['times']) - 1
        for k in range(max(fa, fb) * loops):
            frame = Image.new('RGB', (2 * size[0], size[1]))
            frame.paste(RD.frame_image(A['model'], ca['mats'][k % fa], angle, 4, size, center=(0, .92, .04), height=2.0,
                                       title=la, sub=name.upper()), (0, 0))
            frame.paste(RD.frame_image(Bd['model'], cb['mats'][k % fb], angle, 4, size, center=(0, .92, .04), height=2.0,
                                       title=lb, sub=name.upper()), (size[0], 0))
            enc.stdin.write(frame.tobytes())
        print(f'{name}: {time.time() - t0:.0f}s', flush=True)
    enc.stdin.close(); assert enc.wait() == 0


if __name__ == '__main__':
    main(*sys.argv[1:6])
