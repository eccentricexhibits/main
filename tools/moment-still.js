// Frames from the arrows-into-logo moment, for quick visual checks.
//
//   node tools/moment-still.js 0,3,5.5,7.2,8.6,11 0.30
//
import { createCanvas, Path2D, GlobalFonts } from '@napi-rs/canvas';
import { writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

globalThis.Path2D = Path2D;

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
GlobalFonts.registerFromPath(resolve(root, 'Karbon-Semibold.otf'), 'Karbon');

const { applyBloom, stateFactors } = await import('../src/scene.js');
const { createMoment, drawMoment, MOMENT_DURATION } = await import('../src/logo-moment.js');
const { CANVAS_W, CANVAS_H } = await import('../src/brand.js');

const args = process.argv.slice(2);
const times = (args[0] || '0,3,5.5,7.2,8.6,11').split(',').map(Number);
const scale = Number(args[1] || 0.3);
const dir = process.env.STILL_DIR || '/tmp';

const moment = createMoment((w, h) => createCanvas(w, h));
const cache = {};

for (const t of times) {
  const canvas = createCanvas(CANVAS_W, CANVAS_H);
  const ctx = canvas.getContext('2d');
  drawMoment(ctx, t, moment);
  applyBloom(ctx, (w, h) => createCanvas(w, h), cache, stateFactors(0).bloom);

  const out = createCanvas(Math.round(CANVAS_W * scale), Math.round(CANVAS_H * scale));
  out.getContext('2d').drawImage(canvas, 0, 0, out.width, out.height);
  const name = `${dir}/moment_${String(t).replace('.', '_')}.png`;
  writeFileSync(name, out.toBuffer('image/png'));
  console.log('wrote', name, `t=${t}s / ${MOMENT_DURATION}s`);
}
