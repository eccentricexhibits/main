// Deterministic offline renderer: samples the shared scene at frame times,
// emits one flat SVG per frame, rasterizes with resvg (no browser compositor).
// Usage: node render-svg.js <startFrame> <endFrameExclusive> <outDir> [--svg-only]
'use strict';
const fs = require('fs');
const path = require('path');
const SB = require('./scene-builder.js');
const { Resvg } = require('@resvg/resvg-js');

const scene = SB.build();
const { els, CW, CH, T } = scene;
const FRAMES = 360;

// stable z-order: z ascending, then insertion order
const ordered = els.map((e, i) => ({ e, i })).sort((a, b) => (a.e.z - b.e.z) || (a.i - b.i));

const ARROW_POINTS = '308.51 0 46.97 114.42 0 224.04 208.02 137.79 68.91 480.94 67.58 484.26 113.86 600 286.24 169.06 376.67 375.07 422.98 267.08';
const TRAIL_OP = [0.28, 0.13, 0.05];
const UXv = scene.UX, UYv = scene.UY;

const STREAK_COLORS = ['#b659f0', '#48c0d9', '#7f8de5'];
const SPARK_COLORS = ['#b659f0', '#48c0d9', '#dff6ff'];

function defs() {
  let d = `<defs>
<linearGradient id="arrowGrad" gradientUnits="userSpaceOnUse" x1="0" y1="600" x2="268.65" y2="-62.65">
<stop offset="0" stop-color="#b659f0"/><stop offset="1" stop-color="#48c0d9"/>
</linearGradient>
<polygon id="arrowShape" fill="url(#arrowGrad)" points="${ARROW_POINTS}"/>
<filter id="glowF" x="-30%" y="-30%" width="160%" height="160%">
<feDropShadow dx="0" dy="0" stdDeviation="13" flood-color="#7f8de5" flood-opacity="0.5"/>
</filter>
<filter id="ghostF" x="-20%" y="-20%" width="140%" height="140%">
<feGaussianBlur stdDeviation="4"/>
</filter>`;
  STREAK_COLORS.forEach((c, i) => {
    d += `<linearGradient id="sg${i}" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="${c}" stop-opacity="0"/><stop offset="0.35" stop-color="${c}"/>
<stop offset="0.65" stop-color="${c}"/><stop offset="1" stop-color="${c}" stop-opacity="0"/>
</linearGradient>
<filter id="sf${i}" x="-40%" y="-300%" width="180%" height="700%">
<feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="${c}" flood-opacity="0.33"/>
</filter>`;
  });
  SPARK_COLORS.forEach((c, i) => {
    d += `<radialGradient id="pg${i}">
<stop offset="0" stop-color="${c}"/><stop offset="0.4" stop-color="${c}" stop-opacity="0.53"/>
<stop offset="1" stop-color="${c}" stop-opacity="0"/>
</radialGradient>`;
  });
  return d + '</defs>';
}
const DEFS = defs();

function visible(minX, minY, maxX, maxY) {
  return maxX > 0 && minX < CW && maxY > 0 && minY < CH;
}

function arrowMarkup(el, x, y, s, o) {
  const { w, h } = el;
  // trails extend down-left, opposite of travel
  const pad = 115 * (el.trails || 0) * (h / 600);
  const grow = (s - 1) * Math.max(w, h) / 2 + (el.glow ? 60 : 0) + (el.kind === 'ghost' ? 20 : 0);
  if (!visible(x - pad * UXv * -1 - w * 0.2 - grow, y - grow, x + w + grow, y + h + pad * (-UYv) + grow)) return '';
  const tx = x + (w / 2) * (1 - s), ty = y + (h / 2) * (1 - s);
  const k = s * (h / 600);
  let inner = '';
  for (let t = el.trails || 0; t >= 1; t--) {
    inner += `<use href="#arrowShape" transform="translate(${(-UXv * 115 * t).toFixed(2)} ${(-UYv * 115 * t).toFixed(2)})" opacity="${TRAIL_OP[t - 1]}"/>`;
  }
  inner += '<use href="#arrowShape"/>';
  const filt = el.glow ? ' filter="url(#glowF)"' : (el.kind === 'ghost' ? ' filter="url(#ghostF)"' : '');
  return `<g transform="translate(${tx.toFixed(2)} ${ty.toFixed(2)}) scale(${k.toFixed(5)})" opacity="${o.toFixed(3)}"${filt}>${inner}</g>`;
}

function frameSvg(fi) {
  const tf = (fi * (T / FRAMES)) / T;
  let body = '';
  for (const { e: el } of ordered) {
    const o = el.kind === 'arrow' ? el.op : SB.sampleProp(el.kf, 'o', tf);
    if (!o || o <= 0.001) continue;
    const x = SB.sampleProp(el.kf, 'x', tf);
    const y = SB.sampleProp(el.kf, 'y', tf);
    if (el.kind === 'arrow') {
      const s = SB.sampleProp(el.kf, 's', tf);
      body += arrowMarkup(el, x, y, s, o);
    } else if (el.kind === 'ghost') {
      body += arrowMarkup(el, x, y, 1, o);
    } else if (el.kind === 'streak') {
      const { len, th, rot } = el;
      const half = len / 2 + 20;
      if (!visible(x + len / 2 - half, y + th / 2 - half, x + len / 2 + half, y + th / 2 + half)) continue;
      const ci = STREAK_COLORS.indexOf(el.col);
      body += `<g transform="translate(${(x + len / 2).toFixed(2)} ${(y + th / 2).toFixed(2)}) rotate(${rot}) translate(${(-len / 2).toFixed(2)} ${(-th / 2).toFixed(2)})" opacity="${o.toFixed(3)}" filter="url(#sf${ci})">` +
        `<rect width="${len.toFixed(1)}" height="${th.toFixed(2)}" rx="${(th / 2).toFixed(2)}" fill="url(#sg${ci})"/></g>`;
    } else if (el.kind === 'spark') {
      const r = el.sz;   // core + glow footprint
      if (!visible(x - r * 2, y - r * 2, x + r * 2, y + r * 2)) continue;
      const ci = SPARK_COLORS.indexOf(el.col);
      body += `<circle cx="${(x + el.sz / 2).toFixed(2)}" cy="${(y + el.sz / 2).toFixed(2)}" r="${r.toFixed(2)}" fill="url(#pg${ci})" opacity="${o.toFixed(3)}"/>`;
    } else if (el.kind === 'sweep') {
      const { bw, bh, rot } = el;
      body += `<g transform="translate(${(x + bw / 2).toFixed(2)} ${(y + bh / 2).toFixed(2)}) rotate(${rot}) translate(${-bw / 2} ${-bh / 2})" opacity="${o.toFixed(3)}">` +
        `<rect width="${bw}" height="${bh}" fill="url(#swg)"/></g>`;
    }
  }
  const sweepGrad = `<linearGradient id="swg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#dff6ff" stop-opacity="0"/><stop offset="0.35" stop-color="#dff6ff" stop-opacity="0.13"/>
<stop offset="0.5" stop-color="#b659f0" stop-opacity="0.10"/><stop offset="0.65" stop-color="#48c0d9" stop-opacity="0.13"/>
<stop offset="1" stop-color="#dff6ff" stop-opacity="0"/>
</linearGradient>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${CW}" height="${CH}" viewBox="0 0 ${CW} ${CH}">${DEFS}${sweepGrad}${body}</svg>`;
}

const start = parseInt(process.argv[2] || '0', 10);
const end = parseInt(process.argv[3] || String(FRAMES), 10);
const outDir = process.argv[4] || 'frames-svg';
const svgOnly = process.argv.includes('--svg-only');
fs.mkdirSync(outDir, { recursive: true });

for (let i = start; i < end; i++) {
  const svg = frameSvg(i);
  const name = `frame_${String(i).padStart(4, '0')}`;
  if (svgOnly) {
    fs.writeFileSync(path.join(outDir, name + '.svg'), svg);
  } else {
    const png = new Resvg(svg, { fitTo: { mode: 'original' } }).render().asPng();
    fs.writeFileSync(path.join(outDir, name + '.png'), png);
  }
  if ((i - start) % 20 === 0) console.log(`frame ${i} done`);
}
console.log('DONE', start, '..', end);
