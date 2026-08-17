#!/usr/bin/env node
/*
 * A single frame as a PNG, optionally over transparency.
 *
 *   node animation/export-still.js --at 1:40 --alpha 0.5 --out frame.png
 *   node animation/export-still.js --at 264                 # opaque, as it ships
 *
 * With --alpha the ground keeps its colours but ramps from fully transparent at
 * the top to that opacity at the bottom, and the arrows keep whatever alpha they
 * already had. Grain is dropped in this mode: it exists to dither an 8-bit ramp,
 * and that has to happen downstream once the ground is composited onto something.
 *
 * Options
 *   --at T        time in the loop, seconds or m:ss (default 0)
 *   --alpha A     ground opacity at the bottom edge; omit for an opaque frame
 *   --scale F     render scale (default 1)
 *   --out FILE    output path (default animation/frame.png)
 */
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright');

const WIDTH = 6878;
const HEIGHT = 1080;

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? fallback : process.argv[i + 1];
}

function seconds(value) {
  const parts = String(value).split(':').map(Number);
  return parts.length === 2 ? parts[0] * 60 + parts[1] : parts[0];
}

(async () => {
  const at = seconds(arg('at', 0));
  const alpha = arg('alpha', null);
  const scale = Number(arg('scale', 1));
  const out = path.resolve(arg('out', path.join(__dirname, 'frame.png')));

  const w = Math.round(WIDTH * scale);
  const h = Math.round(HEIGHT * scale);

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const query = alpha === null ? '' : `?alpha=${alpha}`;
  await page.goto('file://' + path.join(__dirname, 'arrow-animation-render.html') + query);
  await page.addStyleTag({
    content:
      `html,body{width:${w}px;height:${h}px;overflow:hidden;margin:0}` +
      (scale === 1 ? '' : `#stage{transform:scale(${scale});transform-origin:0 0}`),
  });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() =>
    Promise.all(
      [...document.images].map((img) =>
        img.complete ? null : new Promise((r) => (img.onload = img.onerror = r))
      )
    )
  );

  await page.evaluate((t) => window.seek(t), at);
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.screenshot({
    path: out,
    clip: { x: 0, y: 0, width: w, height: h },
    // Without this Chromium paints its own opaque white behind the page.
    omitBackground: alpha !== null,
  });
  await browser.close();

  console.log(
    `${out}  ${w}x${h}  t=${at}s  ` +
      (alpha === null ? 'opaque' : `alpha ground 0 -> ${alpha}`) +
      `  ${(fs.statSync(out).size / 1048576).toFixed(2)} MB`
  );
})();
