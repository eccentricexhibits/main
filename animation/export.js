#!/usr/bin/env node
/*
 * Frame-accurate export of the 6878 x 1080 surface, or any span of it.
 *
 *   node animation/export.js --fps 60 --from 3:45 --to 4:40 --out arrow-loop.mp4
 *   node animation/export.js --fps 30                      # the whole loop
 *
 * Every frame is seeked explicitly rather than screen-captured, so none is
 * dropped or duplicated and the result is identical however slowly the machine
 * renders. Frames are piped straight into ffmpeg: at this resolution a PNG
 * sequence for even a minute of 60 fps runs to tens of gigabytes on disk.
 *
 * Times accept seconds (225) or m:ss (3:45). --to may exceed the loop length;
 * the surface wraps, so a span across the loop point exports cleanly.
 *
 * Options
 *   --fps N        frame rate (default 60)
 *   --from T       start time, default 0
 *   --to T         end time, default the full duration
 *   --crf N        x264 quality, lower is better (default 16)
 *   --preset NAME  x264 preset (default slow)
 *   --scale F      render scale (default 1). 0.5 renders the surface at half size
 *                  rather than scaling the output afterwards — the cost per frame
 *                  is rasterising and PNG-encoding 7.4M pixels, so downscaling
 *                  only at the end would save no time at all.
 *   --alpha A      export over transparency, ground opacity A at the bottom edge
 *                  (0 for no ground at all). Forces an alpha-capable codec.
 *   --codec NAME   h264 (default), vp9, prores or qtrle. H.264 carries no alpha,
 *                  so --alpha switches to vp9 unless another is asked for.
 *
 *                  A caveat worth knowing: this container's ffmpeg encodes VP9
 *                  alpha (the file comes out ~45% larger than without, and
 *                  alpha_mode is set) but cannot decode it back, and the headless
 *                  Chromium here decodes no video at all — so a VP9 alpha export
 *                  cannot be verified locally. qtrle and prores round-trip
 *                  verifiably; use one of those when the alpha has to be proven.
 *   --speakers 0   run the logo event without the speaker cards
 *   --ambient 0    drop the drifting tile layers, keeping only the logo event —
 *                  for exporting the formation as its own layer
 *   --seq DIR      write a numbered PNG sequence to DIR instead of encoding a
 *                  movie. With --alpha those PNGs carry the alpha channel
 *                  straight from the browser, with no codec in the path at all —
 *                  which is the route to take when a codec's alpha is suspect.
 *   --out FILE     output path (default animation/arrow-loop.mp4)
 */
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright');

const WIDTH = 6878;
const HEIGHT = 1080;

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? fallback : process.argv[i + 1];
}

/** "3:45" or "225" or "225.5" -> seconds. */
function seconds(value) {
  const parts = String(value).split(':').map(Number);
  return parts.length === 2 ? parts[0] * 60 + parts[1] : parts[0];
}

function ffmpegPath() {
  if (process.env.FFMPEG) return process.env.FFMPEG;
  const bundled =
    '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2';
  return fs.existsSync(bundled) ? bundled : 'ffmpeg';
}

(async () => {
  const fps = Number(arg('fps', 60));
  const crf = String(arg('crf', 16));
  const preset = String(arg('preset', 'slow'));
  const scale = Number(arg('scale', 1));
  const alpha = arg('alpha', null);
  const speakers = arg('speakers', '1') !== '0';
  const ambient = arg('ambient', '1') !== '0';
  const codec = String(arg('codec', alpha === null ? 'h264' : 'vp9'));
  const out = path.resolve(arg('out', path.join(__dirname, 'arrow-loop.mp4')));

  const seq = arg('seq', null);

  if (alpha !== null && codec === 'h264' && !seq) {
    throw new Error('h264 carries no alpha channel — use --codec vp9 or --codec prores');
  }

  // yuv420p needs even dimensions on both axes.
  const w = Math.round((WIDTH * scale) / 2) * 2;
  const h = Math.round((HEIGHT * scale) / 2) * 2;

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const query = [];
  if (alpha !== null) query.push(`alpha=${alpha}`);
  if (!speakers) query.push('speakers=0');
  if (!ambient) query.push('ambient=0');
  await page.goto(
    'file://' + path.join(__dirname, 'arrow-animation-render.html') +
      (query.length ? `?${query.join('&')}` : '')
  );
  await page.addStyleTag({
    content:
      `html,body{width:${w}px;height:${h}px;overflow:hidden}` +
      (scale === 1 ? '' : `#stage{transform:scale(${scale});transform-origin:0 0}`),
  });
  // Fonts and the inlined portrait must be decoded before the first frame.
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() =>
    Promise.all(
      [...document.images].map((img) =>
        img.complete ? null : new Promise((r) => (img.onload = img.onerror = r))
      )
    )
  );

  const duration = await page.evaluate(() => CONFIG.duration);
  const from = seconds(arg('from', 0));
  const to = seconds(arg('to', duration));
  const total = Math.round((to - from) * fps);

  if (!(total > 0)) throw new Error(`--from ${from} to --to ${to} is not a forward span`);

  if (seq) {
    fs.mkdirSync(seq, { recursive: true });
    console.log(
      `${total} frames  ${fps} fps  ${from}s -> ${to}s  ${w}x${h}` +
        (scale === 1 ? '' : ` (render scale ${scale})`) +
        `  PNG sequence` + (alpha === null ? '' : `  alpha ground 0 -> ${alpha}`) +
        (speakers ? '' : '  no speakers') + (ambient ? '' : '  no ambient')
    );
    const began = Date.now();
    let bytes = 0;
    for (let f = 0; f < total; f++) {
      const t = (from + f / fps) % duration;
      await page.evaluate((t) => window.seek(t), t);
      await page.evaluate(
        () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))
      );
      // Chromium's PNG goes straight to disk — no re-encode, nothing lossy.
      const file = path.join(seq, `f_${String(f).padStart(5, '0')}.png`);
      await page.screenshot({
        path: file,
        clip: { x: 0, y: 0, width: w, height: h },
        omitBackground: alpha !== null,
      });
      bytes += fs.statSync(file).size;
      if (f % 25 === 0 || f === total - 1) {
        const rate = (f + 1) / ((Date.now() - began) / 1000);
        process.stdout.write(
          `\r${f + 1}/${total}  ${rate.toFixed(2)} fps  ` +
            `${(bytes / 1048576).toFixed(0)} MB  eta ${Math.round((total - f - 1) / Math.max(rate, 0.001) / 60)} min   `
        );
      }
    }
    await browser.close();
    console.log(`\n${seq}  ${total} files  ${(bytes / 1048576).toFixed(0)} MB  ` +
      `(${((Date.now() - began) / 60000).toFixed(1)} min)`);
    return;
  }

  // VP9 is the only alpha-capable codec here that stays a sane size; ProRes 4444
  // is the one an editor will actually want, at roughly fifty times the bytes.
  const codecArgs = {
    h264: ['-c:v', 'libx264', '-preset', preset, '-crf', crf,
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart'],
    vp9: ['-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', crf,
          '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2'],
    prores: ['-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le'],
    // Lossless RGBA. Verifiable alpha and far lighter than ProRes 4444, but still
    // intra-only, so budget on the order of a quarter megabyte per frame at half size.
    qtrle: ['-c:v', 'qtrle', '-pix_fmt', 'argb'],
  }[codec];
  if (!codecArgs) throw new Error(`unknown --codec ${codec}`);

  const ff = spawn(ffmpegPath(), [
    '-y',
    '-f', 'image2pipe',
    '-c:v', 'png',
    '-framerate', String(fps),
    '-i', '-',
    ...codecArgs,
    out,
  ]);
  const ffDone = new Promise((resolve, reject) => {
    let log = '';
    ff.stderr.on('data', (d) => (log += d.toString().slice(-2000)));
    ff.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}\n${log}`))));
  });

  const write = (buf) =>
    ff.stdin.write(buf) ? Promise.resolve() : new Promise((r) => ff.stdin.once('drain', r));

  console.log(
    `${total} frames  ${fps} fps  ${from}s -> ${to}s  ${w}x${h}` +
      (scale === 1 ? '' : ` (render scale ${scale})`) +
      `  ${codec}` + (alpha === null ? '' : `  alpha ground 0 -> ${alpha}`) +
      (speakers ? '' : '  no speakers')
  );

  const started = Date.now();
  for (let f = 0; f < total; f++) {
    const t = (from + f / fps) % duration;
    await page.evaluate((t) => window.seek(t), t);
    await page.evaluate(
      () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))
    );
    await write(
      await page.screenshot({
        clip: { x: 0, y: 0, width: w, height: h },
        omitBackground: alpha !== null,
      })
    );

    if (f % 25 === 0 || f === total - 1) {
      const rate = (f + 1) / ((Date.now() - started) / 1000);
      const eta = Math.round((total - f - 1) / Math.max(rate, 0.001) / 60);
      process.stdout.write(
        `\r${f + 1}/${total}  ${rate.toFixed(2)} fps  eta ${eta} min      `
      );
    }
  }

  ff.stdin.end();
  await browser.close();
  await ffDone;

  const mb = (fs.statSync(out).size / 1048576).toFixed(1);
  console.log(`\n${out}  ${mb} MB  (${((Date.now() - started) / 60000).toFixed(1)} min)`);
})();
