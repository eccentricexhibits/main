#!/usr/bin/env node
/*
 * Frame-accurate export of the 6878 x 1080 loop. NOT run as part of the review —
 * this exists so that "approved" is a one-command step.
 *
 *   node animation/export-frames.js --fps 30 --out /path/to/frames
 *
 * Each frame is seeked explicitly rather than screen-captured, so no frame is
 * dropped or duplicated and frame N-1 hands back cleanly to frame 0.
 * Encode the result with, for example:
 *
 *   ffmpeg -framerate 30 -i frames/f_%05d.png -c:v libx264 -preset slow \
 *          -crf 14 -pix_fmt yuv420p arrow-loop.mp4
 *
 * For a 6878 px wide master, prefer ProRes 422 HQ or HAP for playback hardware:
 *
 *   ffmpeg -framerate 30 -i frames/f_%05d.png -c:v prores_ks -profile:v 3 arrow-loop.mov
 */
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright');

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? fallback : process.argv[i + 1];
}

const FPS = Number(arg('fps', 30));
const OUT = path.resolve(arg('out', path.join(__dirname, 'frames')));
const WIDTH = 6878;
const HEIGHT = 1080;
const DURATION = 180;
const TOTAL = Math.round(DURATION * FPS);

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 1,
  });
  await page.goto('file://' + path.join(__dirname, 'arrow-animation-render.html'));

  const started = Date.now();
  for (let f = 0; f < TOTAL; f++) {
    await page.evaluate((t) => window.seek(t), f / FPS);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    await page.screenshot({
      path: path.join(OUT, `f_${String(f).padStart(5, '0')}.png`),
      clip: { x: 0, y: 0, width: WIDTH, height: HEIGHT },
    });
    if (f % 60 === 0) {
      const rate = (f + 1) / ((Date.now() - started) / 1000);
      process.stdout.write(
        `\r${f + 1}/${TOTAL} frames  ${rate.toFixed(1)}/s  ` +
          `eta ${Math.round((TOTAL - f) / Math.max(rate, 0.01) / 60)} min   `
      );
    }
  }

  await browser.close();
  console.log(`\n${TOTAL} frames at ${FPS} fps -> ${OUT}`);
})();
