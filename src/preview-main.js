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
  el.width = w;
  el.height = h;
  return el;
};

// ---------------------------------------------------------------------------
// Wall labels — DOM text so they stay legible at any zoom
// ---------------------------------------------------------------------------

const wallsEl = document.getElementById('walls');
for (const w of VENUE.walls) {
  const d = document.createElement('div');
  d.style.left = `${(w.x0 / CANVAS_W) * 100}%`;
  d.style.width = `${((w.x1 - w.x0) / CANVAS_W) * 100}%`;
  d.textContent = `${w.label} · ${w.x1 - w.x0}×${CANVAS_H}`;
  wallsEl.appendChild(d);
}

// ---------------------------------------------------------------------------
// Phase timeline — the structure of the piece, and the scrubber
// ---------------------------------------------------------------------------

const PHASES = [
  { t0: 0, t1: 30, name: 'Distant', note: 'Fields hold the outer walls', tint: '#eb088a' },
  { t0: 30, t1: 65, name: 'Advance', note: 'Streaming inward, motion trails', tint: '#d81b9e' },
  { t0: 65, t1: 100, name: 'Converge', note: 'Meeting on the west wall', tint: '#8a25c9' },
  { t0: 100, t1: 132, name: 'Ascend', note: 'Surge upward · Vector icon', tint: '#5a34e8' },
  { t0: 132, t1: 180, name: 'Disperse', note: 'Retreat, back to the top', tint: '#313cff' },
];

const timeline = document.getElementById('timeline');
const head = document.getElementById('head');

function fmtShort(s) {
  return `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`;
}
function fmt(s) {
  const m = Math.floor(s / 60);
  return `${m}:${(s - m * 60).toFixed(1).padStart(4, '0')}`;
}

const phaseEls = PHASES.map((p) => {
  const el = document.createElement('div');
  el.className = 'phase';
  el.style.flex = String(p.t1 - p.t0);
  el.style.setProperty('--tint', p.tint);
  el.innerHTML =
    `<i></i><b>${p.name}</b><span>${fmtShort(p.t0)} – ${fmtShort(p.t1)} · ${p.note}</span>`;
  timeline.appendChild(el);
  return el;
});

// ---------------------------------------------------------------------------
// Playback
// ---------------------------------------------------------------------------

let t = 0;
let playing = true;
let last = performance.now();
let frames = 0;
let fpsAcc = 0;
let seam = false;

const playBtn = document.getElementById('play');
const timeEl = document.getElementById('time');
const fpsEl = document.getElementById('fps');
const overlayEl = document.getElementById('overlay');
const labelsEl = document.getElementById('labels');
const bloomEl = document.getElementById('bloom');
const loopmarkEl = document.getElementById('loopmark');

// Viewers who have asked for reduced motion get the opening frame, paused,
// rather than three minutes of movement they did not ask for.
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) playing = false;

function setPlaying(v) {
  playing = v;
  playBtn.textContent = v ? 'Pause' : 'Play';
  last = performance.now();
}
setPlaying(playing);

playBtn.onclick = () => setPlaying(!playing);
labelsEl.onchange = () => { wallsEl.hidden = !labelsEl.checked; };
loopmarkEl.onchange = () => {
  seam = loopmarkEl.checked;
  if (seam) t = DURATION - 0.5;
};

document.getElementById('quality').onchange = (e) => {
  quality = Number(e.target.value);
  resize();
  bloomCache.a = null;
  if (!playing) render();
};

// --- scrubbing -------------------------------------------------------------

function seekFromEvent(e) {
  const r = timeline.getBoundingClientRect();
  const k = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width));
  t = k * DURATION;
  if (!playing) render();
}
let dragging = false;
timeline.addEventListener('pointerdown', (e) => {
  dragging = true;
  timeline.setPointerCapture(e.pointerId);
  seekFromEvent(e);
});
timeline.addEventListener('pointermove', (e) => { if (dragging) seekFromEvent(e); });
timeline.addEventListener('pointerup', () => { dragging = false; });

timeline.addEventListener('keydown', (e) => {
  const step = e.shiftKey ? 10 : 1;
  if (e.key === 'ArrowRight') t = (t + step) % DURATION;
  else if (e.key === 'ArrowLeft') t = (t - step + DURATION) % DURATION;
  else if (e.key === 'Home') t = 0;
  else if (e.key === 'End') t = DURATION - 0.05;
  else return;
  e.preventDefault();
  if (!playing) render();
});

window.addEventListener('keydown', (e) => {
  if (e.target !== document.body) return;
  if (e.code === 'Space') {
    e.preventDefault();
    setPlaying(!playing);
  } else if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
    e.preventDefault();
    const step = (e.shiftKey ? 10 : 1) * (e.key === 'ArrowRight' ? 1 : -1);
    t = (t + step + DURATION) % DURATION;
    if (!playing) render();
  }
});

// ---------------------------------------------------------------------------
// Frame loop
// ---------------------------------------------------------------------------

function currentPhase() {
  return PHASES.find((p) => t >= p.t0 && t < p.t1) || PHASES[PHASES.length - 1];
}

function render() {
  ctx.setTransform(quality, 0, 0, quality, 0, 0);
  drawScene(ctx, t, scene);
  if (bloomEl.checked) applyBloom(ctx, makeCanvas, bloomCache);
  ctx.setTransform(quality, 0, 0, quality, 0, 0);
  if (overlayEl.checked) drawVenueOverlay(ctx);

  timeEl.innerHTML = `${fmt(t)} <span>/ ${fmt(DURATION)}</span>`;
  head.style.left = `${(t / DURATION) * 100}%`;
  timeline.setAttribute('aria-valuenow', t.toFixed(1));
  timeline.setAttribute('aria-valuetext', `${fmt(t)}, ${currentPhase().name}`);
  for (let i = 0; i < PHASES.length; i++) {
    phaseEls[i].classList.toggle('on', t >= PHASES[i].t0 && t < PHASES[i].t1);
  }
}

function frame(now) {
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;

  if (playing) {
    t += dt;
    if (seam) {
      // Ping-pong across the loop point so the seam can be judged directly.
      if (t > DURATION + 0.5) t = DURATION - 0.5;
    } else if (t >= DURATION) {
      t -= DURATION;
    }
  }
  render();

  frames++;
  fpsAcc += dt;
  if (fpsAcc > 0.5) {
    fpsEl.textContent = `${Math.round(frames / fpsAcc)} fps preview`;
    frames = 0;
    fpsAcc = 0;
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
