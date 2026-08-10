// Render single frames at a chosen time, for quick visual checks.
//
//   node tools/still.js 0,45,90 0.28
//   node tools/still.js 30 0.28 --dark
//   node tools/still.js 30 0.28 --speaker --overlay
//
import { createCanvas, Path2D, GlobalFonts } from '@napi-rs/canvas';
import { writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

globalThis.Path2D = Path2D;

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
GlobalFonts.registerFromPath(resolve(root, 'Karbon-Semibold.otf'), 'Karbon');

const { createScene, drawScene, applyBloom, drawVenueOverlay, stateFactors, DURATION } =
  await import('../src/scene.js');
const { CANVAS_W, CANVAS_H } = await import('../src/brand.js');

const args = process.argv.slice(2);
const flags = args.filter((a) => a.startsWith('--'));
const rest = args.filter((a) => !a.startsWith('--'));

const times = (rest[0] || '0,30,60,90,116,150').split(',').map(Number);
const scale = Number(rest[1] || 0.28);
const dark = flags.includes('--dark') ? 1 : 0;
const speaker = flags.includes('--speaker')
  ? { name: 'Glenda Crisp', lines: ['President & CEO,', 'Vector Institute'] }
  : null;

const scene = createScene();
const cache = {};
const makeCanvas = (w, h) => createCanvas(w, h);
const out_dir = process.env.STILL_DIR || '/tmp';

for (const t of times) {
  const canvas = createCanvas(CANVAS_W, CANVAS_H);
  const ctx = canvas.getContext('2d');
  drawScene(ctx, t, scene, { dark, speaker });
  applyBloom(ctx, makeCanvas, cache, stateFactors(dark).bloom);
  if (flags.includes('--overlay')) drawVenueOverlay(ctx);

  const out = createCanvas(Math.round(CANVAS_W * scale), Math.round(CANVAS_H * scale));
  const octx = out.getContext('2d');
  octx.drawImage(canvas, 0, 0, out.width, out.height);
  const tag = `${dark ? 'dark' : 'show'}${speaker ? '_spk' : ''}`;
  const name = `${out_dir}/still_${tag}_${String(t).padStart(3, '0')}.png`;
  writeFileSync(name, out.toBuffer('image/png'));
  console.log('wrote', name, `${out.width}x${out.height}  t=${t}s / ${DURATION}s`);
}
