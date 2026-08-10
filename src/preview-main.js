import { CANVAS_W, CANVAS_H, VENUE } from './brand.js';
import {
  createScene, drawScene, applyBloom, drawVenueOverlay, stateFactors, DURATION,
} from './scene.js';
import { createMoment, drawMoment, MOMENT_DURATION } from './logo-moment.js';

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

const makeCanvas = (w, h) => {
  const el = document.createElement('canvas');
  el.width = w;
  el.height = h;
  return el;
};

const scene = createScene();
const moment = createMoment(makeCanvas);
const bloomCache = {};

// Which piece is on the timeline. The two share a background, a palette and an
// axis, so switching is only a change of what drives the clock.
const PIECES = {
  loop: { dur: DURATION, tick: 15 },
  moment: { dur: MOMENT_DURATION, tick: 1 },
};
let piece = 'loop';
const duration = () => PIECES[piece].dur;

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
// Scrub track
// ---------------------------------------------------------------------------

const timeline = document.getElementById('timeline');
const head = document.getElementById('head');
const fill = document.getElementById('fill');

function fmt(s) {
  const m = Math.floor(s / 60);
  return `${m}:${(s - m * 60).toFixed(1).padStart(4, '0')}`;
}

function buildTicks() {
  for (const el of [...timeline.querySelectorAll('.tick')]) el.remove();
  const { dur, tick: step } = PIECES[piece];
  const major = piece === 'loop' ? 60 : 5;
  for (let s = step; s < dur; s += step) {
    const tick = document.createElement('div');
    const isMajor = s % major === 0;
    tick.className = isMajor ? 'tick major' : 'tick';
    tick.style.left = `${(s / dur) * 100}%`;
    if (isMajor) tick.innerHTML = `<b>${fmt(s)}</b>`;
    timeline.appendChild(tick);
  }
  timeline.setAttribute('aria-valuemax', String(dur));
}
buildTicks();

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
const pieceEl = document.getElementById('piece');
const darkEl = document.getElementById('dark');
const darkValEl = document.getElementById('darkval');
const speakerEl = document.getElementById('speaker');
const speakerNameEl = document.getElementById('speakername');
const speakerRoleEl = document.getElementById('speakerrole');

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

pieceEl.onchange = () => {
  piece = pieceEl.value;
  // The seam test is meaningless on a one-shot piece.
  if (piece !== 'loop') { seam = false; loopmarkEl.checked = false; }
  loopmarkEl.disabled = piece !== 'loop';
  t = 0;
  buildTicks();
  document.getElementById('specdur').textContent =
    piece === 'loop' ? '3:00 · seamless' : '0:12 · one shot';
  if (!playing) render();
};

const onDark = () => {
  darkValEl.textContent = `${darkEl.value}%`;
  if (!playing) render();
};
darkEl.oninput = onDark;
for (const el of [speakerEl, speakerNameEl, speakerRoleEl]) {
  el.oninput = () => { if (!playing) render(); };
  el.onchange = () => { if (!playing) render(); };
}

function speakerSpec() {
  if (!speakerEl.checked) return null;
  return {
    name: speakerNameEl.value,
    lines: speakerRoleEl.value.split(',').map((s) => s.trim()).filter(Boolean)
      .map((s, i, all) => (i < all.length - 1 ? `${s},` : s)),
  };
}

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
  t = k * duration();
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
  if (e.key === 'ArrowRight') t = (t + step) % duration();
  else if (e.key === 'ArrowLeft') t = (t - step + duration()) % duration();
  else if (e.key === 'Home') t = 0;
  else if (e.key === 'End') t = duration() - 0.05;
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
    t = (t + step + duration()) % duration();
    if (!playing) render();
  }
});

// ---------------------------------------------------------------------------
// Frame loop
// ---------------------------------------------------------------------------

function render() {
  const dark = Number(darkEl.value) / 100;
  ctx.setTransform(quality, 0, 0, quality, 0, 0);
  if (piece === 'moment') drawMoment(ctx, t, moment, { dark });
  else drawScene(ctx, t, scene, { dark, speaker: speakerSpec() });
  if (bloomEl.checked) applyBloom(ctx, makeCanvas, bloomCache, stateFactors(dark).bloom);
  ctx.setTransform(quality, 0, 0, quality, 0, 0);
  if (overlayEl.checked) drawVenueOverlay(ctx);

  const pct = (t / duration()) * 100;
  timeEl.innerHTML = `${fmt(t)} <span>/ ${fmt(duration())}</span>`;
  head.style.left = `${pct}%`;
  fill.style.width = `${pct}%`;
  timeline.setAttribute('aria-valuenow', t.toFixed(1));
  timeline.setAttribute('aria-valuetext', fmt(t));
}

function frame(now) {
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;

  if (playing) {
    t += dt;
    if (seam) {
      // Ping-pong across the loop point so the seam can be judged directly.
      if (t > DURATION + 0.5) t = DURATION - 0.5;
    } else if (piece === 'moment') {
      // A one-shot piece: hold on the last frame rather than snapping back.
      if (t >= duration()) { t = duration(); setPlaying(false); }
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
