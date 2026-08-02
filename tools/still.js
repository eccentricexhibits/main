// Render single frames at a chosen time, for quick visual checks.
import { createCanvas, Path2D } from '@napi-rs/canvas';
import { writeFileSync } from 'node:fs';

globalThis.Path2D = Path2D;

const { createScene, drawScene, applyBloom, drawVenueOverlay, DURATION } = await import('../src/scene.js');
const { CANVAS_W, CANVAS_H } = await import('../src/brand.js');

const args = process.argv.slice(2);
const times = (args[0] || '0,30,60,90,116,150').split(',').map(Number);
const scale = Number(args[1] || 0.28);
const overlay = args[2] === 'overlay';

const scene = createScene();
const cache = {};
const makeCanvas = (w, h) => createCanvas(w, h);

for (const t of times) {
  const canvas = createCanvas(CANVAS_W, CANVAS_H);
  const ctx = canvas.getContext('2d');
  drawScene(ctx, t, scene);
  applyBloom(ctx, makeCanvas, cache);
  if (overlay) drawVenueOverlay(ctx);

  const out = createCanvas(Math.round(CANVAS_W * scale), Math.round(CANVAS_H * scale));
  const octx = out.getContext('2d');
  octx.drawImage(canvas, 0, 0, out.width, out.height);
  const name = `/tmp/claude-0/-home-user-main/8e0cdc3f-7351-516a-b2f6-76a372b42eb0/scratchpad/still_${String(t).padStart(3, '0')}.png`;
  writeFileSync(name, out.toBuffer('image/png'));
  console.log('wrote', name, `${out.width}x${out.height}  t=${t}s / ${DURATION}s`);
}
