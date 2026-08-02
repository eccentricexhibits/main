import { CANVAS_W, CANVAS_H, VENUE } from './brand.js';
import { createScene, drawScene, applyBloom, drawVenueOverlay, DURATION } from './scene.js';

const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');

// The scene is authored in 6878x1080 units. For preview we shrink the backing
// store and scale the context, so playback can hit real time without changing
// a single coordinate in the scene itself.
let quality = 0.25;
function resize() {
  canvas.width = Math.round(CANVAS_W * quality);
  canvas.height = Math.round(CANVAS_H * quality);
}
resize();

const scene = createScene();
const bloomCache = {};
const makeCanvas = (w, h) => {
  const el = document.createElement('canvas');
  el.width = w; el.height = h;
  return el;
};

// --- wall labels -----------------------------------------------------------
const wallsEl = document.getElementById('walls');
for (const w of VENUE.walls) {
  const d = document.createElement('div');
  d.style.left = (w.x0 / CANVAS_W * 100) + '%';
  d.style.width = ((w.x1 - w.x0) / CANVAS_W * 100) + '%';
  d.textContent = `${w.label} · ${w.x1 - w.x0}×${CANVAS_H}`;
  wallsEl.appendChild(d);
}

// --- playback --------------------------------------------------------------
let t = 0;
let playing = true;
let last = performance.now();
let frames = 0, fpsAcc = 0;

const playBtn = document.getElementById('play');
const scrub = document.getElementById('scrub');
const timeEl = document.getElementById('time');
const fpsEl = document.getElementById('fps');
const overlayEl = document.getElementById('overlay');
const labelsEl = document.getElementById('labels');
const bloomEl = document.getElementById('bloom');
const loopmarkEl = document.getElementById('loopmark');

playBtn.onclick = () => {
  playing = !playing;
  playBtn.textContent = playing ? 'Pause' : 'Play';
  last = performance.now();
};
scrub.oninput = () => { t = Number(scrub.value); if (!playing) render(); };
labelsEl.onchange = () => wallsEl.classList.toggle('off', !labelsEl.checked);
for (const b of document.querySelectorAll('.phases button')) {
  b.onclick = () => { t = Number(b.dataset.t); scrub.value = t; if (!playing) render(); };
}

// Jump between the last half-second and the first half-second so the seam can
// be judged directly.
let seamDir = 0;
loopmarkEl.onchange = () => { seamDir = loopmarkEl.checked ? 1 : 0; if (seamDir) t = 179.5; };

function fmt(s) {
  const m = Math.floor(s / 60);
  const r = (s - m * 60);
  return `${m}:${r.toFixed(1).padStart(4, '0')}`;
}

function render() {
  ctx.setTransform(quality, 0, 0, quality, 0, 0);
  drawScene(ctx, t, scene);
  if (bloomEl.checked) applyBloom(ctx, makeCanvas, bloomCache);
  ctx.setTransform(quality, 0, 0, quality, 0, 0);
  if (overlayEl.checked) drawVenueOverlay(ctx);
  timeEl.textContent = `${fmt(t)} / ${fmt(DURATION)}`;
}

document.getElementById('quality').onchange = (e) => {
  quality = Number(e.target.value);
  resize();
  bloomCache.a = null;
  if (!playing) render();
};

function frame(now) {
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;
  if (playing) {
    t += dt;
    if (seamDir) {
      // ping-pong across the loop seam
      if (t > 180.5) t = 179.5;
    } else if (t >= DURATION) {
      t -= DURATION;
    }
    scrub.value = Math.min(180, t);
  }
  render();

  frames++; fpsAcc += dt;
  if (fpsAcc > 0.5) { fpsEl.textContent = `${(frames / fpsAcc).toFixed(0)} fps preview`; frames = 0; fpsAcc = 0; }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
