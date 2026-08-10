// Final render: rasterise the scene at full resolution and encode.
//
// The work is split into contiguous segments across worker processes; each
// worker pipes raw RGBA straight into its own ffmpeg, and the segments are
// concatenated with a stream copy so nothing is re-encoded.
//
//   node tools/render.js                       # 6878x1080, 30 fps, H.264
//   node tools/render.js --pix-fmt yuv444p     # better and smaller, sw playback
//   node tools/render.js --dark                # the presentation state
//   node tools/render.js --moment              # the arrows-into-logo piece
//   node tools/render.js --speaker "Glenda Crisp|President & CEO,|Vector Institute"
//   node tools/render.js --fps 60 --crf 14
//   node tools/render.js --walls               # also cut per-projector files
//   node tools/render.js --duration 10         # short test render
//
import { createCanvas, Path2D, GlobalFonts } from '@napi-rs/canvas';
import { spawn, fork } from 'node:child_process';
import { mkdirSync, writeFileSync, rmSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import ffmpegPath from 'ffmpeg-static';

globalThis.Path2D = Path2D;

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');

GlobalFonts.registerFromPath(resolve(root, 'Karbon-Semibold.otf'), 'Karbon');

const { createScene, drawScene, applyBloom, stateFactors, DURATION } =
  await import('../src/scene.js');
const { createMoment, drawMoment, MOMENT_DURATION } = await import('../src/logo-moment.js');
const { CANVAS_W, CANVAS_H, VENUE } = await import('../src/brand.js');

// ---------------------------------------------------------------------------
// Arguments
// ---------------------------------------------------------------------------

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith('--')
    ? process.argv[i + 1]
    : fallback;
}
const has = (name) => process.argv.includes(`--${name}`);

// The presentation state and the logo moment are separate deliverables, not
// separate scenes: same geometry, same palette, driven by the same functions.
const MOMENT = has('moment');
const DARK = has('dark') ? 1 : 0;
const SPEAKER = (() => {
  const v = arg('speaker', null);
  if (!v) return null;
  const [name, ...lines] = v.split('|');
  return { name, lines };
})();

const FPS = Number(arg('fps', 30));
const CRF = Number(arg('crf', 16));
const DUR = Number(arg('duration', MOMENT ? MOMENT_DURATION : DURATION));
const GOP = Number(arg('gop', Math.round(Number(arg('fps', 30)))));
const WORKERS = Number(arg('workers', 4));
// yuv420p is the compatible default. yuv444p measures better *and* smaller on
// this content — saturated brand colour on near-black is the worst case for
// chroma subsampling — but needs software playback. See the README.
const PIX = arg('pix-fmt', 'yuv420p');
const DEFAULT_NAME = MOMENT
  ? 'out/vector-arrival-6878x1080.mp4'
  : `out/vector-convergence${DARK ? '-dark' : ''}-6878x1080.mp4`;
const OUT = resolve(root, arg('out', DEFAULT_NAME));
const TMP = resolve(root, 'out/.segments');

const TOTAL_FRAMES = Math.round(DUR * FPS);

// ---------------------------------------------------------------------------
// Worker: render a frame range and encode it to one segment
// ---------------------------------------------------------------------------

if (process.env.RENDER_WORKER) {
  const { index, start, end } = JSON.parse(process.env.RENDER_WORKER);
  const makeCanvas = (w, h) => createCanvas(w, h);
  const scene = MOMENT ? createMoment(makeCanvas) : createScene();
  const canvas = createCanvas(CANVAS_W, CANVAS_H);
  const ctx = canvas.getContext('2d');
  const bloomCache = {};
  const bloom = stateFactors(DARK).bloom;
  const segPath = resolve(TMP, `seg${String(index).padStart(3, '0')}.mp4`);

  const ff = spawn(ffmpegPath, [
    '-y', '-loglevel', 'error',
    '-f', 'rawvideo', '-pix_fmt', 'rgba',
    '-s', `${CANVAS_W}x${CANVAS_H}`, '-r', String(FPS),
    '-i', 'pipe:0',
    '-an',
    // Convert RGB->YUV explicitly with BT.709. ffmpeg's automatic conversion
    // uses BT.601 regardless of the colour tags below, so tagging alone
    // produces a file that is converted with one matrix and played back with
    // another — a systematic colour shift, and a ~4.8 dB error against the
    // source. The input from canvas is full-range RGB; video convention is
    // limited-range YUV, which is what the tags declare.
    '-vf', 'scale=in_range=full:in_color_matrix=bt709:out_range=tv:out_color_matrix=bt709',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', String(CRF),
    '-pix_fmt', PIX,
    // Short, fixed GOP with scene-cut detection off: keeps seeking and loop
    // restarts snappy on venue playback hardware, and guarantees every segment
    // opens on a keyframe so the concat below is a clean stream copy.
    '-x264-params', `keyint=${GOP}:min-keyint=${GOP}:scenecut=0`,
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
    '-color_range', 'tv',
    segPath,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  const done = new Promise((res, rej) => {
    ff.on('close', (c) => (c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}`))));
    ff.on('error', rej);
  });

  for (let f = start; f < end; f++) {
    if (MOMENT) drawMoment(ctx, f / FPS, scene, { dark: DARK });
    else drawScene(ctx, f / FPS, scene, { dark: DARK, speaker: SPEAKER });
    applyBloom(ctx, makeCanvas, bloomCache, bloom);
    const buf = ctx.getImageData(0, 0, CANVAS_W, CANVAS_H).data;
    if (!ff.stdin.write(Buffer.from(buf.buffer, buf.byteOffset, buf.byteLength))) {
      await new Promise((r) => ff.stdin.once('drain', r));
    }
    if ((f - start) % 25 === 0) {
      process.send?.({ index, done: f - start, total: end - start });
    }
  }
  ff.stdin.end();
  await done;
  process.send?.({ index, done: end - start, total: end - start, finished: true });
  process.exit(0);
}

// ---------------------------------------------------------------------------
// Coordinator
// ---------------------------------------------------------------------------

console.log(
  `Rendering ${MOMENT ? 'Arrival' : 'Convergence'}${DARK ? ' (dark state)' : ''}` +
  `${SPEAKER ? ` · speaker "${SPEAKER.name}"` : ''}\n` +
  `  ${TOTAL_FRAMES} frames · ${CANVAS_W}x${CANVAS_H} · ${FPS} fps · ` +
  `${DUR}s · CRF ${CRF} · ${PIX} · ${WORKERS} workers`
);

rmSync(TMP, { recursive: true, force: true });
mkdirSync(TMP, { recursive: true });
mkdirSync(dirname(OUT), { recursive: true });

const bounds = [];
for (let i = 0; i < WORKERS; i++) {
  bounds.push({
    index: i,
    start: Math.floor((i * TOTAL_FRAMES) / WORKERS),
    end: Math.floor(((i + 1) * TOTAL_FRAMES) / WORKERS),
  });
}

const progress = new Array(WORKERS).fill(0);
const totals = bounds.map((b) => b.end - b.start);
const t0 = Date.now();

function report() {
  const done = progress.reduce((a, b) => a + b, 0);
  const pct = ((done / TOTAL_FRAMES) * 100).toFixed(1);
  const el = (Date.now() - t0) / 1000;
  const eta = done > 0 ? (el / done) * (TOTAL_FRAMES - done) : 0;
  process.stdout.write(
    `\r  ${done}/${TOTAL_FRAMES} frames (${pct}%)  elapsed ${el.toFixed(0)}s  eta ${eta.toFixed(0)}s   `
  );
}

await Promise.all(
  bounds.map(
    (b) =>
      new Promise((res, rej) => {
        const child = fork(fileURLToPath(import.meta.url), process.argv.slice(2), {
          env: { ...process.env, RENDER_WORKER: JSON.stringify(b) },
          stdio: ['inherit', 'inherit', 'inherit', 'ipc'],
        });
        child.on('message', (m) => {
          progress[m.index] = m.done;
          report();
        });
        child.on('exit', (c) => {
          if (c === 0) {
            progress[b.index] = totals[b.index];
            report();
            res();
          } else rej(new Error(`worker ${b.index} exited ${c}`));
        });
      })
  )
);

console.log('\n  concatenating segments…');

const listPath = resolve(TMP, 'list.txt');
writeFileSync(
  listPath,
  bounds.map((b) => `file '${resolve(TMP, `seg${String(b.index).padStart(3, '0')}.mp4`)}'`).join('\n')
);

function run(args) {
  return new Promise((res, rej) => {
    const p = spawn(ffmpegPath, args, { stdio: ['ignore', 'inherit', 'inherit'] });
    p.on('close', (c) => (c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}`))));
  });
}

await run(['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', listPath, '-c', 'copy', OUT]);

// Optional per-projector cuts, straight from the master.
if (has('walls')) {
  console.log('  cutting per-projector files…');
  for (const w of VENUE.walls) {
    const width = w.x1 - w.x0;
    const dest = OUT.replace(/\.mp4$/, `-${w.id}-${width}x${CANVAS_H}.mp4`);
    await run([
      '-y', '-loglevel', 'error', '-i', OUT,
      '-vf', `crop=${width}:${CANVAS_H}:${w.x0}:0`,
      '-c:v', 'libx264', '-preset', 'slow', '-crf', String(CRF), '-pix_fmt', PIX,
      '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
      '-color_range', 'tv', '-an', dest,
    ]);
    console.log(`    ${dest}`);
  }
}

rmSync(TMP, { recursive: true, force: true });

const secs = ((Date.now() - t0) / 1000).toFixed(0);
console.log(`\nDone in ${secs}s → ${OUT}`);
if (existsSync(OUT)) {
  const { statSync } = await import('node:fs');
  console.log(`  ${(statSync(OUT).size / 1e6).toFixed(0)} MB`);
}
