// Vector Institute — "Convergence" immersive wall animation.
//
// One deterministic scene function drives both the browser preview and the
// final 6878x1080 render, so what is approved in the browser is exactly what
// gets encoded. Everything is a pure function of loop time `t`, which makes
// the piece scrubbable and seamlessly loopable.
//
// Narrative: two fields of brand marks — magenta on the south wall, cobalt on
// the north — advance toward each other, meet as violet on the west wall
// directly in the viewer's eye-line, surge upward behind the Vector icon, then
// disperse back to their starting positions.

import {
  VENUE,
  CANVAS_W,
  CANVAS_H,
  WEST_CENTRE,
  ARROW_REGULAR,
  ARROW_LONG,
  LOGO_ICON,
  PLUS_BAR_RATIO,
  gradientAt,
  rgba,
} from './brand.js';

export const DURATION = 180; // seconds, seamless loop

// ---------------------------------------------------------------------------
// Deterministic randomness
// ---------------------------------------------------------------------------

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let x = Math.imul(a ^ (a >>> 15), 1 | a);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);
const clamp01 = (v) => clamp(v, 0, 1);
const smoothstep = (x) => {
  const t = clamp01(x);
  return t * t * (3 - 2 * t);
};
const lerp = (a, b, k) => a + (b - a) * k;

// Piecewise keyframe curve with smoothstep easing between stops.
function curve(stops) {
  return function (t) {
    if (t <= stops[0][0]) return stops[0][1];
    const last = stops[stops.length - 1];
    if (t >= last[0]) return last[1];
    for (let i = 0; i < stops.length - 1; i++) {
      const [ta, va] = stops[i];
      const [tb, vb] = stops[i + 1];
      if (t >= ta && t <= tb) {
        return lerp(va, vb, smoothstep((t - ta) / (tb - ta)));
      }
    }
    return last[1];
  };
}

// ---------------------------------------------------------------------------
// Timing curves — the choreography of the piece
// ---------------------------------------------------------------------------

// How far each field reaches inward from its wall, as a fraction of canvas
// width. At 0.5 the two fields touch on the west wall.
const reachAt = curve([
  [0, 0.13], [30, 0.16], [58, 0.33], [80, 0.52],
  [100, 0.56], [118, 0.575], [140, 0.4], [165, 0.175], [180, 0.13],
]);

// Global density and brightness.
const intensityAt = curve([
  [0, 0.55], [28, 0.62], [60, 0.86], [84, 1.0],
  [112, 1.0], [134, 0.92], [160, 0.66], [180, 0.55],
]);

// Horizontal motion-blur trails, peaking during the advance.
const streakAt = curve([
  [0, 0], [28, 0.12], [46, 1.0], [62, 0.62], [80, 0.12], [100, 0], [180, 0],
]);

// Upward surge behind the logo moment.
const ascendAt = curve([
  [0, 0], [98, 0], [116, 1.0], [132, 0.62], [152, 0.16], [180, 0],
]);

// Vector icon presence.
const logoAt = curve([
  [0, 0], [101, 0], [112, 1], [125, 1], [135, 0], [180, 0],
]);

// Vertical spread of the flow band.
const spreadAt = curve([
  [0, 0.62], [60, 0.78], [100, 0.94], [130, 0.86], [180, 0.62],
]);

// Flow rate. Integrated below so the loop closes exactly.
const speedAt = curve([
  [0, 0.55], [30, 0.75], [50, 1.35], [70, 1.05],
  [100, 0.85], [120, 1.0], [150, 0.7], [180, 0.55],
]);

// Integrate the speed curve once, then normalise to [0,1] across the loop.
// A particle assigned `k` whole laps therefore returns to its exact starting
// position at t = DURATION, whatever the speed curve does in between.
const FLOW_LUT = (() => {
  const N = 3600;
  const lut = new Float64Array(N + 1);
  let acc = 0;
  const dt = DURATION / N;
  for (let i = 1; i <= N; i++) {
    const a = speedAt((i - 1) * dt);
    const b = speedAt(i * dt);
    acc += ((a + b) / 2) * dt;
    lut[i] = acc;
  }
  const total = lut[N];
  for (let i = 0; i <= N; i++) lut[i] /= total;
  return lut;
})();

function flowPhase(t) {
  const N = FLOW_LUT.length - 1;
  const x = clamp01(t / DURATION) * N;
  const i = Math.min(N - 1, Math.floor(x));
  return lerp(FLOW_LUT[i], FLOW_LUT[i + 1], x - i);
}

// ---------------------------------------------------------------------------
// Field shape
// ---------------------------------------------------------------------------

// Centreline of the flow band. Sags gently toward the west wall so the two
// fields meet slightly below the viewer's eye-line, then lift on the ascent.
function bandCentre(xn, t, ascend) {
  const loop = (t / DURATION) * Math.PI * 2;
  const sag = 0.105 * Math.sin(Math.PI * xn);
  const drift = 0.022 * Math.sin(loop + xn * 3.4) + 0.014 * Math.sin(loop * 2 + xn * 7.1);
  return CANVAS_H * (0.47 + sag + drift - 0.1 * ascend);
}

// Half-height of the band. Wide at the outer walls, converging toward a
// vanishing point on the west wall — the perspective read in the reference
// frames — relaxing toward uniform as the fields converge.
function bandSpread(xn, t, spread, converge) {
  const edgeBias = 0.34 + 0.66 * Math.pow(Math.abs(2 * xn - 1), 1.3);
  const shape = lerp(edgeBias, 0.92, converge * 0.75);
  return CANVAS_H * 0.5 * spread * shape;
}

// Logo clear space. The guidelines require breathing room around the mark, so
// while the icon is on screen the field is pushed back inside an ellipse
// centred on it. Returns a multiplier in [0,1].
const LOGO_CX = WEST_CENTRE;
const LOGO_CY = CANVAS_H * 0.4;

function logoClearance(x, y, logoAlpha) {
  if (logoAlpha < 0.01) return 1;
  const rx = CANVAS_H * 0.62;
  const ry = CANVAS_H * 0.46;
  const d = Math.hypot((x - LOGO_CX) / rx, (y - LOGO_CY) / ry);
  // Floor at 0.08 rather than 0 so the field thins behind the mark instead of
  // punching a hard hole through the gradient.
  const clear = 0.08 + 0.92 * smoothstep((d - 0.5) / 0.55);
  return lerp(1, clear, logoAlpha);
}

// Density envelope: how present the field is at a given x.
function envelope(xn, reach) {
  const falloff = (s) => {
    if (s <= 0.6) return 1;
    const k = (s - 0.6) / 0.9;
    return Math.exp(-k * k * 2.6);
  };
  const eL = falloff(xn / reach);
  const eR = falloff((1 - xn) / reach);
  return Math.min(1.25, eL + eR);
}

// ---------------------------------------------------------------------------
// Element construction
// ---------------------------------------------------------------------------

// Lap counts available to particles. Integer laps keep the loop seamless while
// still giving parallax between near and far marks.
const LAPS = [2, 3, 4, 5, 6, 8];

function buildParticles(seed, count) {
  const rnd = mulberry32(seed);
  const out = [];
  for (let i = 0; i < count; i++) {
    // Bias depth toward the far field so big marks stay rare and deliberate.
    const depth = Math.pow(rnd(), 1.9);
    // Lane position within the band, clustered toward the centreline.
    const l = rnd() + rnd() + rnd();
    const lane = (l / 3) * 2 - 1;
    out.push({
      u0: rnd(),
      lane,
      depth,
      laps: LAPS[Math.min(LAPS.length - 1, Math.floor(depth * LAPS.length + rnd() * 0.9))],
      kind: rnd() < 0.55 ? 0 : 1, // 0 = pixel, 1 = plus
      // Pixels in the official pattern sit on-grid; a small rotation on a
      // minority of marks reads as motion without breaking the pattern.
      rot: rnd() < 0.22 ? (rnd() - 0.5) * 0.5 : 0,
      twPhase: rnd() * Math.PI * 2,
      twRate: 1 + Math.floor(rnd() * 4),
      twAmt: 0.15 + rnd() * 0.4,
      jitter: rnd() * Math.PI * 2,
      sizeVar: 0.75 + rnd() * 0.55,
    });
  }
  return out;
}

function buildArrows(seed, count, minH, maxH, longChance) {
  const rnd = mulberry32(seed);
  const out = [];
  for (let i = 0; i < count; i++) {
    const depth = Math.pow(rnd(), 1.35);
    const l = rnd() + rnd();
    out.push({
      u0: rnd(),
      lane: (l / 2) * 2 - 1,
      depth,
      laps: LAPS[Math.min(LAPS.length - 1, Math.floor(depth * LAPS.length + rnd() * 0.9))],
      // Size tracks depth. Decoupling them produces large, dim arrows that
      // read as flat washes rather than as objects sitting further back.
      h: lerp(minH, maxH, clamp01(depth * 0.78 + rnd() * 0.3)),
      long: rnd() < longChance,
      twPhase: rnd() * Math.PI * 2,
      twRate: 1 + Math.floor(rnd() * 3),
      alphaVar: 0.6 + rnd() * 0.5,
      jitter: rnd() * Math.PI * 2,
    });
  }
  return out;
}

// ---------------------------------------------------------------------------
// Scene — built once, evaluated per frame
// ---------------------------------------------------------------------------

export function createScene() {
  const P2D = globalThis.Path2D;
  if (!P2D) throw new Error('Path2D is required (set globalThis.Path2D in Node).');

  const paths = {
    arrowRegular: new P2D(ARROW_REGULAR.d),
    arrowLong: new P2D(ARROW_LONG.d),
    logo: LOGO_ICON.parts.map((p) => ({ fill: p.fill, path: new P2D(p.d) })),
  };

  const particles = buildParticles(0x5ec7, 4200);
  // Arrow counts are deliberately restrained. The reference art reads as a
  // particle field punctuated by arrows, not a field of arrows — overlapping
  // translucent arrowheads under an additive blend turn to mush very quickly.
  const arrowsFar = buildArrows(0xa11e, 58, 0.03, 0.1, 0.0);
  const arrowsMid = buildArrows(0xb22f, 30, 0.11, 0.26, 0.1);
  const arrowsHero = buildArrows(0xc33a, 10, 0.3, 0.66, 0.3);
  const arrowsLong = buildArrows(0xd44b, 6, 0.55, 0.98, 1.0);

  return { paths, particles, arrowsFar, arrowsMid, arrowsHero, arrowsLong };
}

// Position a flowing element. Elements travel up and to the right, matching
// the fixed orientation of the official arrow.
function place(el, phase, t, ascend, spread, converge) {
  // Travel 1.2 canvas widths per lap so marks enter and exit off-screen.
  let u = (el.u0 + el.laps * phase) % 1;
  const x = (u * 1.24 - 0.12) * CANVAS_W;
  const xn = clamp01(x / CANVAS_W);
  const centre = bandCentre(xn, t, ascend);
  const half = bandSpread(xn, t, spread, converge);
  // Marks rise slightly as they travel right, echoing the arrow direction.
  const rise = -CANVAS_H * 0.05 * (u - 0.5) * (0.5 + el.depth);
  const wobble = Math.sin(el.jitter + t * 0.35 + u * 6.0) * CANVAS_H * 0.012;
  return { x, xn, y: centre + el.lane * half + rise + wobble, u };
}

export function drawScene(ctx, time, scene) {
  const t = ((time % DURATION) + DURATION) % DURATION;

  const reach = reachAt(t);
  const intensity = intensityAt(t);
  const streak = streakAt(t);
  const ascend = ascendAt(t);
  const spread = spreadAt(t);
  const logoAlpha = logoAt(t);
  const phase = flowPhase(t);
  const converge = smoothstep((reach - 0.3) / 0.26);

  drawBackground(ctx, t, reach, intensity, converge);

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';

  drawArrowLayer(ctx, scene, scene.arrowsFar, t, phase, ascend, spread, converge, reach, intensity, 0.5, logoAlpha);
  drawParticles(ctx, scene, t, phase, ascend, spread, converge, reach, intensity, streak, logoAlpha);
  drawArrowLayer(ctx, scene, scene.arrowsMid, t, phase, ascend, spread, converge, reach, intensity, 0.6, logoAlpha);
  drawArrowLayer(ctx, scene, scene.arrowsLong, t, phase, ascend, spread, converge, reach, intensity, 0.5, logoAlpha);
  drawArrowLayer(ctx, scene, scene.arrowsHero, t, phase, ascend, spread, converge, reach, intensity, 0.78, logoAlpha);

  ctx.restore();

  if (logoAlpha > 0.001) drawLogo(ctx, scene, logoAlpha, t);
}

// ---------------------------------------------------------------------------
// Background
// ---------------------------------------------------------------------------

function drawBackground(ctx, t, reach, intensity, converge) {
  const g = ctx.createLinearGradient(0, 0, CANVAS_W, 0);
  g.addColorStop(0.0, '#0d0010');
  g.addColorStop(0.35, '#080011');
  g.addColorStop(0.5, '#070113');
  g.addColorStop(0.72, '#040314');
  g.addColorStop(1.0, '#030616');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

  // Ambient wash from each field, plus a violet bloom where they meet.
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';

  // Kept deliberately faint: the reference art sits on near-black, with light
  // coming off the marks themselves rather than from a background wash.
  const breathe = 0.88 + 0.12 * Math.sin((t / DURATION) * Math.PI * 4);
  const washes = [
    { cx: CANVAS_W * 0.06, col: gradientAt(0.02, 0.6), a: 0.085 * intensity * breathe, r: CANVAS_W * 0.17 },
    { cx: CANVAS_W * 0.95, col: gradientAt(0.98, 0.6), a: 0.085 * intensity * breathe, r: CANVAS_W * 0.17 },
    { cx: WEST_CENTRE, col: gradientAt(0.5, 0.8), a: 0.11 * converge * intensity, r: CANVAS_W * 0.13 },
  ];
  for (const w of washes) {
    if (w.a <= 0.002) continue;
    const rg = ctx.createRadialGradient(w.cx, CANVAS_H * 0.5, 0, w.cx, CANVAS_H * 0.5, w.r);
    rg.addColorStop(0, rgba(w.col, w.a));
    rg.addColorStop(0.55, rgba(w.col, w.a * 0.28));
    rg.addColorStop(1, rgba(w.col, 0));
    ctx.fillStyle = rg;
    ctx.fillRect(w.cx - w.r, 0, w.r * 2, CANVAS_H);
  }
  ctx.restore();
}

// ---------------------------------------------------------------------------
// Particle field — official pixel and plus marks
// ---------------------------------------------------------------------------

function drawParticles(ctx, scene, t, phase, ascend, spread, converge, reach, intensity, streak, logoAlpha) {
  const bar = PLUS_BAR_RATIO;

  for (const p of scene.particles) {
    const pos = place(p, phase, t, ascend, spread, converge);
    if (pos.x < -140 || pos.x > CANVAS_W + 140) continue;

    const env = envelope(pos.xn, reach);
    if (env < 0.012) continue;

    const tw = 1 - p.twAmt + p.twAmt * (0.5 + 0.5 * Math.sin(p.twPhase + (t / DURATION) * Math.PI * 2 * p.twRate * 3));
    let alpha = (0.1 + 0.62 * Math.pow(p.depth, 1.25)) * env * intensity * tw;
    alpha *= 1 + 0.35 * ascend * p.depth;
    alpha *= logoClearance(pos.x, pos.y, logoAlpha);
    if (alpha < 0.006) continue;

    const emissive = clamp01(0.25 + p.depth * 0.75);
    const col = gradientAt(pos.xn, emissive);

    let size = CANVAS_H * (0.0055 + 0.05 * Math.pow(p.depth, 2.1)) * p.sizeVar;
    size *= 1 + 0.22 * ascend * p.depth;

    // Trailing motion blur during the advance.
    if (streak > 0.02 && p.depth > 0.3) {
      const len = size * (1.5 + 16 * streak * (p.laps / 8));
      const th = Math.max(1, size * (p.kind === 0 ? 0.3 : 0.22));
      ctx.fillStyle = rgba(col, alpha * 0.2 * streak);
      ctx.fillRect(pos.x - len, pos.y - th / 2, len, th);
    }

    ctx.fillStyle = rgba(col, alpha);

    if (p.rot !== 0) {
      ctx.save();
      ctx.translate(pos.x, pos.y);
      ctx.rotate(p.rot);
      if (p.kind === 0) ctx.fillRect(-size / 2, -size / 2, size, size);
      else fillPlus(ctx, 0, 0, size, bar);
      ctx.restore();
    } else if (p.kind === 0) {
      ctx.fillRect(pos.x - size / 2, pos.y - size / 2, size, size);
    } else {
      fillPlus(ctx, pos.x, pos.y, size, bar);
    }
  }
}

// The official plus: a square outline with a bar 20.6% of its width.
function fillPlus(ctx, cx, cy, size, bar) {
  const h = size / 2;
  const b = (size * bar) / 2;
  ctx.fillRect(cx - h, cy - b, size, b * 2);
  ctx.fillRect(cx - b, cy - h, b * 2, size);
}

// ---------------------------------------------------------------------------
// Arrows — never rotated, per the brand rules
// ---------------------------------------------------------------------------

function drawArrowLayer(ctx, scene, arrows, t, phase, ascend, spread, converge, reach, intensity, weight, logoAlpha) {
  for (const a of arrows) {
    const pos = place(a, phase, t, ascend, spread, converge);
    const src = a.long ? ARROW_LONG : ARROW_REGULAR;
    const h = CANVAS_H * a.h * (1 + 0.14 * ascend * a.depth);
    const w = (h / src.h) * src.w;

    if (pos.x < -w - 80 || pos.x > CANVAS_W + w + 80) continue;

    const env = envelope(pos.xn, reach);
    if (env < 0.012) continue;

    const tw = 0.72 + 0.28 * Math.sin(a.twPhase + (t / DURATION) * Math.PI * 2 * a.twRate * 2);
    let alpha = weight * (0.22 + 0.78 * a.depth) * env * intensity * tw * a.alphaVar;
    alpha *= 1 + 0.3 * ascend * a.depth;
    if (alpha < 0.006) continue;

    // Keep tall arrows inside the frame: the taller the arrow, the less it is
    // allowed to stray from the centreline.
    const centreY = bandCentre(pos.xn, t, ascend);
    const room = Math.max(CANVAS_H * 0.05, (CANVAS_H - h) / 2);
    const y = centreY + clamp(pos.y - centreY, -room, room);

    alpha *= logoClearance(pos.x, y, logoAlpha);
    if (alpha < 0.006) continue;

    const col = gradientAt(pos.xn, clamp01(0.3 + a.depth * 0.7));
    const tail = gradientAt(pos.xn, clamp01(0.1 + a.depth * 0.4));

    ctx.save();
    ctx.translate(pos.x - w / 2, y - h / 2);
    ctx.scale(h / src.h, h / src.h);
    // Brand shapes may carry a gradient fill; running it tail-to-head gives
    // each arrow a lit leading edge, as in the reference art.
    const grad = ctx.createLinearGradient(0, src.h, src.w, 0);
    grad.addColorStop(0, rgba(tail, Math.min(alpha, 0.95) * 0.5));
    grad.addColorStop(1, rgba(col, Math.min(alpha, 0.95)));
    ctx.fillStyle = grad;
    ctx.fill(a.long ? scene.paths.arrowLong : scene.paths.arrowRegular);
    ctx.restore();
  }
}

// ---------------------------------------------------------------------------
// Vector icon — resolves on the west wall at the peak of the piece
// ---------------------------------------------------------------------------

function drawLogo(ctx, scene, alpha, t) {
  const src = LOGO_ICON;
  const iw = src.x1 - src.x0;
  const ih = src.y1 - src.y0;
  const h = CANVAS_H * 0.54;
  const s = h / ih;
  const cx = LOGO_CX;
  const cy = LOGO_CY;

  // Settles into place as it fades up.
  const settle = 1 + 0.06 * (1 - alpha);

  ctx.save();
  ctx.translate(cx, cy);
  ctx.scale(s * settle, s * settle);
  ctx.translate(-src.x0 - iw / 2, -src.y0 - ih / 2);
  ctx.globalAlpha = alpha;
  for (const part of scene.paths.logo) {
    ctx.fillStyle = part.fill;
    ctx.fill(part.path);
  }
  ctx.restore();
}

// ---------------------------------------------------------------------------
// Bloom — cheap two-tap downscale blur composited additively
// ---------------------------------------------------------------------------

export function applyBloom(ctx, makeCanvas, cache, strength = 0.55) {
  const src = ctx.canvas;
  const W = src.width;
  const H = src.height;

  if (!cache.a || cache.w !== W) {
    // A tight tap for the halo that hugs each mark, and a wide one for the
    // faint room glow. Keeping the tight tap dominant preserves the crisp
    // shape edges the reference art has. Taps are sized off the real backing
    // store so the bloom radius stays proportional at any preview resolution.
    cache.a = makeCanvas(Math.max(1, Math.round(W / 5)), Math.max(1, Math.round(H / 5)));
    cache.b = makeCanvas(Math.max(1, Math.round(W / 22)), Math.max(1, Math.round(H / 22)));
    cache.w = W;
  }
  const a = cache.a;
  const b = cache.b;
  const ca = a.getContext('2d');
  const cb = b.getContext('2d');

  ca.globalCompositeOperation = 'copy';
  ca.globalAlpha = 1;
  ca.drawImage(src, 0, 0, a.width, a.height);

  cb.globalCompositeOperation = 'copy';
  cb.drawImage(a, 0, 0, b.width, b.height);

  // Fold the wide tap into the tight one while both are still small. Upscaling
  // to the full canvas dominates the cost of this pass, so it is worth doing
  // exactly once.
  ca.globalCompositeOperation = 'lighter';
  ca.globalAlpha = 0.4;
  ca.drawImage(b, 0, 0, a.width, a.height);
  ca.globalAlpha = 1;

  ctx.save();
  // Composite in device pixels, ignoring any preview scaling transform.
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalCompositeOperation = 'lighter';
  ctx.globalAlpha = strength;
  ctx.drawImage(a, 0, 0, W, H);
  ctx.restore();
}

// ---------------------------------------------------------------------------
// Venue overlay — preview only
// ---------------------------------------------------------------------------

export function drawVenueOverlay(ctx) {
  ctx.save();
  ctx.lineWidth = 3;
  ctx.font = '600 30px system-ui, sans-serif';
  ctx.textBaseline = 'top';

  for (const c of VENUE.corners) {
    ctx.fillStyle = 'rgba(255,255,255,0.10)';
    ctx.fillRect(c.x0, 0, c.x1 - c.x0, CANVAS_H);
  }

  // Wall names are rendered as DOM text by the preview page so they stay
  // legible at any zoom; only the boundary is drawn here.
  for (const w of VENUE.walls) {
    ctx.strokeStyle = 'rgba(255,255,255,0.85)';
    ctx.strokeRect(w.x0 + 1.5, 1.5, w.x1 - w.x0 - 3, CANVAS_H - 3);
  }

  ctx.setLineDash([14, 10]);
  ctx.strokeStyle = 'rgba(80,220,255,0.85)';
  for (const w of [VENUE.walls[0], VENUE.walls[2]]) {
    ctx.beginPath();
    ctx.moveTo(w.x0, VENUE.cubeTop);
    ctx.lineTo(w.x1, VENUE.cubeTop);
    ctx.stroke();
  }

  ctx.strokeStyle = 'rgba(255,120,120,0.9)';
  ctx.fillStyle = 'rgba(255,120,120,0.10)';
  for (const g of VENUE.grills) {
    ctx.fillRect(g.x0, g.y0, g.x1 - g.x0, g.y1 - g.y0);
    ctx.strokeRect(g.x0, g.y0, g.x1 - g.x0, g.y1 - g.y0);
  }

  ctx.strokeStyle = 'rgba(255,210,90,0.85)';
  ctx.fillStyle = 'rgba(255,210,90,0.10)';
  for (const d of VENUE.drapes) {
    ctx.fillRect(d.x0, d.y0, d.x1 - d.x0, d.y1 - d.y0);
    ctx.strokeRect(d.x0, d.y0, d.x1 - d.x0, d.y1 - d.y0);
  }

  ctx.setLineDash([]);
  ctx.strokeStyle = 'rgba(140,255,180,0.8)';
  const dm = VENUE.domino;
  ctx.strokeRect(dm.x0, dm.y0 + 1.5, dm.x1 - dm.x0, dm.y1 - dm.y0);

  ctx.restore();
}
