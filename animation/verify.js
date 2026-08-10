#!/usr/bin/env node
/*
 * Renders frames of the 6878 x 1080 surface headlessly so they can be checked
 * for the three things that are easy to get subtly wrong:
 *
 *   1. seamless loop — the frame at t = duration must equal the frame at t = 0
 *   2. travel angle  — measured by matching two frames a known interval apart
 *   3. ink coverage  — fraction of non-background pixels
 *
 *   node animation/verify.js [t0 t1 t2 ...]     (seconds; default 0 10 90 180)
 *
 * Frames land in animation/.verify/ as t<seconds>.png at VERIFY_SCALE.
 * animation/analyze.py does the pixel maths on them.
 */
const path = require('path');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright');

const FILE = 'file://' + path.join(__dirname, 'arrow-animation-render.html');
const SCALE = Number(process.env.VERIFY_SCALE || 0.25);
const W = Math.round(6878 * SCALE);
const H = Math.round(1080 * SCALE);
const OUT = path.join(__dirname, '.verify');
const args = process.argv.slice(2);
const layerFlag = args.indexOf('--layer');
const LAYER = layerFlag === -1 ? null : args.splice(layerFlag, 2)[1];
const times = args.map(Number);
const FRAMES = times.length ? times : [0, 10, 90, 180];

(async () => {
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto(LAYER ? `${FILE}?layer=${LAYER}` : FILE);
  await page.addStyleTag({
    content:
      `html,body{width:${W}px;height:${H}px;overflow:hidden}` +
      `#stage{transform:scale(${SCALE});transform-origin:0 0}`,
  });

  const metrics = await page.evaluate(() => window.metrics);
  console.log('layer   tile          arrow  opacity  per tile  on screen   px/s   loop travel');
  for (const m of metrics) {
    console.log(
      `  ${m.index}    ${String(m.tileW).padStart(4)} x ${String(m.tileH).padEnd(4)}` +
        `   ${String(m.arrow).padStart(4)}    ${m.opacity.toFixed(2)}       ` +
        `${String(m.count).padStart(3)}        ${String(m.onScreen).padStart(3)}     ` +
        `${m.speed.toFixed(2)}    ${Math.round(m.travel)} px`
    );
  }
  const total = metrics.reduce((n, m) => n + m.onScreen, 0);
  console.log(`  arrows on screen: ${total}`);

  // Exactness of the travel direction is structural, not something to eyeball:
  // every layer's loop translation is (tileW, -tileH), so tileH:tileW must be 37:15.
  const offAxis = metrics.filter((m) => m.tileH * 15 !== m.tileW * 37 || !Number.isInteger(m.tileH));
  console.log(
    offAxis.length
      ? `  ANGLE ERROR on layer(s) ${offAxis.map((m) => m.index).join(', ')}`
      : '  travel vector is exactly 15:37 (slope 2.4667, 67.93 deg) on every layer'
  );

  for (const t of FRAMES) {
    await page.evaluate((t) => window.seek(t), t);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    await page.screenshot({ path: path.join(OUT, `t${t}.png`), clip: { x: 0, y: 0, width: W, height: H } });
  }

  // Background-only plate, so ink coverage is measured against the actual ground
  // (a vertical gradient plus grain) rather than a single flat colour.
  if (!LAYER) {
    await page.goto(`${FILE}?bare=1`);
    await page.addStyleTag({ content: `#stage{transform:scale(${SCALE});transform-origin:0 0}` });
    await page.screenshot({ path: path.join(OUT, 'plate.png'), clip: { x: 0, y: 0, width: W, height: H } });
  }

  await browser.close();
  console.log(`\n${FRAMES.length} frames at ${W}x${H} -> ${OUT}`);
})();
