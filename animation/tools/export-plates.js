#!/usr/bin/env node
/*
 * The ambient field as scrolling plates rather than frames.
 *
 *   node animation/tools/export-plates.js --out DIR                 # the 6-minute field
 *   node animation/tools/export-plates.js --speed 2 --loop 120 --out DIR
 *
 * Each layer of the field is one seamlessly repeating tile sliding on a single
 * linear translate over the whole loop, at fixed opacity — no per-arrow motion
 * of any kind. So six static images and six linear position keyframes reproduce
 * the entire loop exactly, at any frame rate, in a few megabytes, where the
 * frame sequence for one 6-minute loop at 120 fps would be 43,200 frames and
 * ~84 GB.
 *
 * Writes, per layer, the single tile and the pre-tiled plate, both at full
 * opacity with the layer's opacity recorded separately, plus a layers.json
 * carrying the geometry and both forms of the motion — top-left coordinates and
 * the centre coordinates that Premiere and After Effects actually want.
 *
 * Options
 *   --speed S   speed multiple relative to the shipped field (default 1)
 *   --short R   shorten the loop R times over at the shipped speed — the tile
 *               grows to R x R base tiles and the travel per loop shrinks to
 *               1/R, so the plate stays small and the motion is unchanged
 *   --loop T    loop length in seconds (default: the config's own duration)
 *   --out DIR   output directory (required)
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright');

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? fallback : process.argv[i + 1];
}

(async () => {
  const speed = arg('speed', null);
  const short = arg('short', null);
  const loop = arg('loop', null);
  const out = arg('out', null);
  if (!out) throw new Error('--out DIR is required');

  fs.mkdirSync(path.join(out, 'tiles'), { recursive: true });
  fs.mkdirSync(path.join(out, 'plates'), { recursive: true });

  const query = ['event=0', 'alpha=0'];
  if (speed) query.push(`speed=${speed}`);
  if (short) query.push(`short=${short}`);
  if (loop) query.push(`loop=${loop}`);

  const browser = await chromium.launch();
  const probe = await browser.newPage({ viewport: { width: 400, height: 200 } });
  await probe.goto(
    'file://' + path.join(__dirname, '..', 'arrow-animation-render.html') + '?' + query.join('&')
  );
  const duration = await probe.evaluate(() => {
    const el = document.querySelector('.af-layer');
    return parseFloat(getComputedStyle(el).animationDuration);
  });
  // Read the geometry off the built page rather than recomputing it, so the
  // plates cannot drift from what the engine actually renders.
  const layers = await probe.evaluate(() =>
    [...document.querySelectorAll('.af-ambient > *')].map((el, i) => {
      const cs = getComputedStyle(el);
      const m = /url\("(.+)"\)/s.exec(cs.backgroundImage);
      const [bw, bh] = cs.backgroundSize.split(' ').map(parseFloat);
      // Travel per loop is not the tile size once --short is in play, so it
      // comes from the metrics the engine reports rather than being inferred.
      const mx = window.metrics[i];
      return {
        url: m[1], tileW: bw, tileH: bh, opacity: Number(cs.opacity),
        travelX: mx.travelX, travelY: mx.travelY,
        plateW: parseFloat(cs.width), plateH: parseFloat(cs.height),
        left: parseFloat(cs.left), top: parseFloat(cs.top),
      };
    })
  );
  await probe.close();

  const shoot = async (file, w, h, L) => {
    const pg = await browser.newPage({ viewport: { width: Math.round(w), height: Math.round(h) } });
    await pg.setContent(
      `<style>html,body{margin:0;background:transparent}` +
        `div{width:${w}px;height:${h}px;background-image:url("${L.url}");` +
        `background-repeat:repeat;background-size:${L.tileW}px ${L.tileH}px}</style><div></div>`
    );
    await pg.screenshot({ path: file, omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
    await pg.close();
    return fs.statSync(file).size;
  };

  const meta = [];
  for (let i = 0; i < layers.length; i++) {
    const L = layers[i];
    const n = i + 1;
    const tile = path.join(out, 'tiles', `layer${n}_tile_${L.tileW}x${L.tileH}.png`);
    const plate = path.join(out, 'plates', `layer${n}_plate_${L.plateW}x${L.plateH}.png`);
    const tileBytes = await shoot(tile, L.tileW, L.tileH, L);
    const plateBytes = await shoot(plate, L.plateW, L.plateH, L);

    // Two forms of the same motion. Top-left is what the CSS does; centre is
    // what Motion > Position takes, because the anchor point defaults to the
    // middle of the clip and entering top-left there shifts every plate left by
    // half its own width.
    const topLeft = { start: [L.left, L.top], end: [L.left + L.travelX, L.top - L.travelY] };
    const centre = {
      start: [topLeft.start[0] + L.plateW / 2, topLeft.start[1] + L.plateH / 2],
      end: [topLeft.end[0] + L.plateW / 2, topLeft.end[1] + L.plateH / 2],
    };
    meta.push({
      layer: n, tileW: L.tileW, tileH: L.tileH, opacity: L.opacity,
      travelX: L.travelX, travelY: L.travelY,
      plateW: L.plateW, plateH: L.plateH, duration,
      topLeft, centre,
      tile: path.basename(tile), plate: path.basename(plate), tileBytes, plateBytes,
    });
    console.log(
      `layer ${n}  tile ${L.tileW}x${L.tileH}  plate ${L.plateW}x${L.plateH}  ` +
        `opacity ${L.opacity}  ${(plateBytes / 1048576).toFixed(2)} MB`
    );
  }

  fs.writeFileSync(
    path.join(out, 'layers.json'),
    JSON.stringify({ speed: speed ? Number(speed) : 1, duration, layers: meta }, null, 2)
  );
  await browser.close();
  console.log(
    `${out}  ${duration}s loop  ` +
      `${(meta.reduce((a, m) => a + m.plateBytes + m.tileBytes, 0) / 1048576).toFixed(1)} MB`
  );
})();
