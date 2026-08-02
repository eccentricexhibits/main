// Vector Institute — "Convergence" immersive wall animation.
//
// One deterministic scene function drives both the browser preview and the
// final 6878x1080 render, so what is approved in the browser is exactly what
// gets encoded. Everything is a pure function of loop time `t`, which makes
// the piece scrubbable and seamlessly loopable.
//
// The field is a single sustained state rather than a sequence of movements:
// brand marks drift slowly up and to the right along the arrow axis, carrying
// motion trails, and leave the frame at the top. Colour is a function of
// horizontal position, so the room reads magenta on the south wall, violet
// across the west wall in the viewer's eye-line, and cobalt on the north.

import {
  VENUE,
  CANVAS_W,
  CANVAS_H,
  WEST_CENTRE,
  ARROW_REGULAR,
  ARROW_LONG,
  PLUS_BAR_RATIO,
  PLUS_CLUSTER,
  PLUS_CLUSTER_MARK,
  PIXEL_CLUSTER,
  PIXEL_CLUSTER_MARK,
  gradientAt,
  rgba,
} from './brand.js';

export const DURATION = 180; // seconds, seamless loop

// Travel direction: up and to the right along the arrow axis.
export const FLOW_DEG = 67.93;
const TH = (FLOW_DEG * Math.PI) / 180;
const DIR = { x: Math.cos(TH), y: -Math.sin(TH) };
const PERP = { x: Math.sin(TH), y: Math.cos(TH) };

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
const lerp = (a, b, k) => a + (b - a) * k;
const frac = (v) => v - Math.floor(v);

// ---------------------------------------------------------------------------
// Flow field geometry
//
// Positions are tracked in a basis aligned to the travel direction: `a` runs
// along it, `b` across it. Wrapping `a` on a span comfortably larger than the
// canvas means elements recycle well outside the frame, so the loop never
// shows a seam and marks genuinely exit the top edge.
// ---------------------------------------------------------------------------

const MARGIN_A = 950;
const MARGIN_B = 420;

const EXT = (() => {
  let aMin = Infinity, aMax = -Infinity, bMin = Infinity, bMax = -Infinity;
  for (const [x, y] of [[0, 0], [CANVAS_W, 0], [0, CANVAS_H], [CANVAS_W, CANVAS_H]]) {
    const a = x * DIR.x + y * DIR.y;
    const b = x * PERP.x + y * PERP.y;
    if (a < aMin) aMin = a;
    if (a > aMax) aMax = a;
    if (b < bMin) bMin = b;
    if (b > bMax) bMax = b;
  }
  return {
    a0: aMin - MARGIN_A,
    aLen: aMax - aMin + MARGIN_A * 2,
    b0: bMin - MARGIN_B,
    bLen: bMax - bMin + MARGIN_B * 2,
  };
})();

// Whole laps per loop. With a constant rate these keep the loop exact while
// still giving parallax: roughly 30 px/s for the far field up to 90 px/s for
// the nearest marks — slow enough to sit calmly across a very wide projection.
const LAPS = [1, 1, 2, 2, 3, 3];

function place(el, phase, t) {
  const a = EXT.a0 + frac(el.a0 + el.laps * phase) * EXT.aLen;
  // A slow drift across the travel axis keeps paths from reading as rails.
  const drift = Math.sin(el.wob + (t / DURATION) * Math.PI * 2 * el.wobRate) * el.wobAmt;
  const b = EXT.b0 + el.b0 * EXT.bLen + drift;
  const x = a * DIR.x + b * PERP.x;
  const y = a * DIR.y + b * PERP.y;
  return { x, y, xn: clamp01(x / CANVAS_W) };
}

// Gentle vertical weighting so the field has a centre of gravity without
// hard-edged banding — marks stay visible as they leave the top of the frame.
function bandWeight(y) {
  const d = (y / CANVAS_H - 0.5) / 0.52;
  return 0.26 + 0.74 * Math.exp(-d * d * 2.1);
}

// Blend a weighting toward 1. Large shapes need the field's density
// modulation applied gently, or they survive at full size but near-zero alpha
// and read as grey ghosts rather than as arrows.
const soft = (w, k) => 1 - k + k * w;

// A slow swell across the width, drifting over the loop. Amplitude is small:
// this is texture, not choreography.
function fieldWeight(xn, t) {
  const loop = (t / DURATION) * Math.PI * 2;
  return 0.86 + 0.14 * Math.sin(xn * Math.PI * 1.6 + loop) + 0.08 * Math.sin(xn * Math.PI * 3.1 - loop * 2);
}

// ---------------------------------------------------------------------------
// Element construction
// ---------------------------------------------------------------------------

function baseFields(rnd, depth) {
  return {
    a0: rnd(),
    b0: rnd(),
    depth,
    laps: LAPS[Math.min(LAPS.length - 1, Math.floor(depth * LAPS.length + rnd() * 0.9))],
    wob: rnd() * Math.PI * 2,
    wobRate: 1 + Math.floor(rnd() * 3),
    wobAmt: 30 + rnd() * 90,
    twPhase: rnd() * Math.PI * 2,
    twRate: 1 + Math.floor(rnd() * 4),
  };
}

function buildParticles(seed, count) {
  const rnd = mulberry32(seed);
  const out = [];
  for (let i = 0; i < count; i++) {
    const depth = Math.pow(rnd(), 1.9);
    out.push({
      ...baseFields(rnd, depth),
      kind: rnd() < 0.55 ? 0 : 1, // 0 = pixel, 1 = plus
      twAmt: 0.12 + rnd() * 0.34,
      sizeVar: 0.75 + rnd() * 0.55,
      trail: 0.35 + rnd() * 0.9,
    });
  }
  return out;
}

function buildClusters(seed, count, minSize, maxSize) {
  const rnd = mulberry32(seed);
  const out = [];
  for (let i = 0; i < count; i++) {
    const depth = Math.pow(rnd(), 1.5);
    out.push({
      ...baseFields(rnd, depth),
      size: lerp(minSize, maxSize, clamp01(depth * 0.8 + rnd() * 0.3)),
      alphaVar: 0.7 + rnd() * 0.5,
    });
  }
  return out;
}

function buildArrows(seed, count, minH, maxH, longChance) {
  const rnd = mulberry32(seed);
  const out = [];
  for (let i = 0; i < count; i++) {
    const depth = Math.pow(rnd(), 1.35);
    out.push({
      ...baseFields(rnd, depth),
      // Size tracks depth. Decoupling them produces large, dim arrows that
      // read as flat washes rather than as objects sitting further back.
      h: lerp(minH, maxH, clamp01(depth * 0.78 + rnd() * 0.3)),
      long: rnd() < longChance,
      alphaVar: 0.75 + rnd() * 0.4,
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

  return {
    paths: {
      arrowRegular: new P2D(ARROW_REGULAR.d),
      arrowLong: new P2D(ARROW_LONG.d),
    },
    // Counts are set against the rotated wrap region, not the canvas. Only
    // about 18% of that region is on screen at any moment, so the totals here
    // are far larger than the number of marks actually visible.
    particles: buildParticles(0x5ec7, 13500),
    plusClusters: buildClusters(0xe55a, 40, 190, 620),
    pixelClusters: buildClusters(0xf66b, 24, 170, 520),
    arrowsFar: buildArrows(0xa11e, 240, 0.03, 0.1, 0.0),
    arrowsMid: buildArrows(0xb22f, 100, 0.11, 0.26, 0.1),
    arrowsHero: buildArrows(0xc33a, 38, 0.34, 0.78, 0.3),
    arrowsLong: buildArrows(0xd44b, 24, 0.55, 0.98, 1.0),
  };
}

export function drawScene(ctx, time, scene) {
  const t = ((time % DURATION) + DURATION) % DURATION;
  const phase = t / DURATION;

  drawBackground(ctx, t);

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';

  drawArrowLayer(ctx, scene, scene.arrowsFar, t, phase, 0.62);
  drawClusterLayer(ctx, scene.pixelClusters, t, phase, 0, 0.62);
  drawParticles(ctx, scene, t, phase);
  drawClusterLayer(ctx, scene.plusClusters, t, phase, 1, 0.75);
  drawArrowLayer(ctx, scene, scene.arrowsMid, t, phase, 0.85);
  drawArrowLayer(ctx, scene, scene.arrowsLong, t, phase, 0.72);
  drawArrowLayer(ctx, scene, scene.arrowsHero, t, phase, 1.05);

  ctx.restore();
}

// ---------------------------------------------------------------------------
// Background
// ---------------------------------------------------------------------------

function drawBackground(ctx, t) {
  const g = ctx.createLinearGradient(0, 0, CANVAS_W, 0);
  g.addColorStop(0.0, '#0d0010');
  g.addColorStop(0.35, '#080011');
  g.addColorStop(0.5, '#070113');
  g.addColorStop(0.72, '#040314');
  g.addColorStop(1.0, '#030616');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

  // Kept deliberately faint: the reference art sits on near-black, with light
  // coming off the marks themselves rather than from a background wash.
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const breathe = 0.9 + 0.1 * Math.sin((t / DURATION) * Math.PI * 2);
  const washes = [
    { cx: CANVAS_W * 0.06, col: gradientAt(0.02, 0.6), a: 0.085 * breathe, r: CANVAS_W * 0.17 },
    { cx: WEST_CENTRE, col: gradientAt(0.5, 0.8), a: 0.07 * breathe, r: CANVAS_W * 0.12 },
    { cx: CANVAS_W * 0.95, col: gradientAt(0.98, 0.6), a: 0.085 * breathe, r: CANVAS_W * 0.17 },
  ];
  for (const w of washes) {
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
// Individual marks
//
// Pixels and pluses are drawn axis-aligned, exactly as the official patterns
// are constructed — no rotation.
// ---------------------------------------------------------------------------

function fillPixel(ctx, cx, cy, size) {
  ctx.fillRect(cx - size / 2, cy - size / 2, size, size);
}

function fillPlus(ctx, cx, cy, size) {
  const h = size / 2;
  const b = (size * PLUS_BAR_RATIO) / 2;
  ctx.fillRect(cx - h, cy - b, size, b * 2);
  ctx.fillRect(cx - b, cy - h, b * 2, size);
}

// Motion trail, drawn along the travel axis behind the mark.
function drawTrail(ctx, x, y, len, thickness, style) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(-TH);
  ctx.fillStyle = style;
  ctx.fillRect(-len, -thickness / 2, len, thickness);
  ctx.restore();
}

function drawParticles(ctx, scene, t, phase) {
  for (const p of scene.particles) {
    const pos = place(p, phase, t);
    if (pos.x < -180 || pos.x > CANVAS_W + 180 || pos.y < -180 || pos.y > CANVAS_H + 180) continue;

    const tw = 1 - p.twAmt + p.twAmt * (0.5 + 0.5 * Math.sin(p.twPhase + phase * Math.PI * 2 * p.twRate * 3));
    const alpha = (0.14 + 0.72 * Math.pow(p.depth, 1.2)) * bandWeight(pos.y) * fieldWeight(pos.xn, t) * tw;
    if (alpha < 0.006) continue;

    const col = gradientAt(pos.xn, clamp01(0.25 + p.depth * 0.75));
    const size = CANVAS_H * (0.0055 + 0.05 * Math.pow(p.depth, 2.1)) * p.sizeVar;

    // Trails are a permanent part of the look, not a passing effect: they give
    // the wide middle of the room something to read at walking pace.
    if (p.depth > 0.3) {
      const len = size * (2.2 + 9 * p.trail * (p.laps / 3));
      const th = Math.max(1, size * (p.kind === 0 ? 0.26 : 0.2));
      drawTrail(ctx, pos.x, pos.y, len, th, rgba(col, alpha * 0.2));
    }

    ctx.fillStyle = rgba(col, alpha);
    if (p.kind === 0) fillPixel(ctx, pos.x, pos.y, size);
    else fillPlus(ctx, pos.x, pos.y, size);
  }
}

// ---------------------------------------------------------------------------
// Official cluster patterns, drawn whole
// ---------------------------------------------------------------------------

function drawClusterLayer(ctx, clusters, t, phase, kind, weight) {
  const pattern = kind === 1 ? PLUS_CLUSTER : PIXEL_CLUSTER;
  const markRatio = kind === 1 ? PLUS_CLUSTER_MARK : PIXEL_CLUSTER_MARK;

  for (const c of clusters) {
    const pos = place(c, phase, t);
    const r = c.size * 0.75;
    if (pos.x < -r || pos.x > CANVAS_W + r || pos.y < -r || pos.y > CANVAS_H + r) continue;

    const tw = 0.75 + 0.25 * Math.sin(c.twPhase + phase * Math.PI * 2 * c.twRate * 2);
    const alpha = weight * (0.2 + 0.8 * c.depth) * bandWeight(pos.y) * fieldWeight(pos.xn, t) * tw * c.alphaVar;
    if (alpha < 0.006) continue;

    const mark = c.size * markRatio;

    for (const [dx, dy] of pattern) {
      const mx = pos.x + dx * c.size;
      const my = pos.y + dy * c.size;
      if (mx < -mark || mx > CANVAS_W + mark || my < -mark || my > CANVAS_H + mark) continue;
      // Colour each mark by its own position so a cluster spanning the west
      // wall still sits correctly on the gradient.
      const col = gradientAt(clamp01(mx / CANVAS_W), clamp01(0.3 + c.depth * 0.7));
      ctx.fillStyle = rgba(col, alpha);
      if (kind === 1) fillPlus(ctx, mx, my, mark);
      else fillPixel(ctx, mx, my, mark);
    }
  }
}

// ---------------------------------------------------------------------------
// Arrows — never rotated, per the brand rules. They travel along the axis they
// already point down, so they read as shooting off the top of the frame.
// ---------------------------------------------------------------------------

function drawArrowLayer(ctx, scene, arrows, t, phase, weight) {
  for (const a of arrows) {
    const pos = place(a, phase, t);
    const src = a.long ? ARROW_LONG : ARROW_REGULAR;
    const h = CANVAS_H * a.h;
    const w = (h / src.h) * src.w;

    if (pos.x < -w - 80 || pos.x > CANVAS_W + w + 80) continue;
    if (pos.y < -h - 80 || pos.y > CANVAS_H + h + 80) continue;

    const tw = 0.8 + 0.2 * Math.sin(a.twPhase + phase * Math.PI * 2 * a.twRate * 2);
    const alpha =
      weight * (0.22 + 0.78 * a.depth) *
      soft(bandWeight(pos.y), 0.55) * soft(fieldWeight(pos.xn, t), 0.5) *
      tw * a.alphaVar;
    if (alpha < 0.006) continue;

    const col = gradientAt(pos.xn, clamp01(0.45 + a.depth * 0.55));
    const tail = gradientAt(pos.xn, clamp01(0.2 + a.depth * 0.4));
    const capped = Math.min(alpha, 0.95);

    ctx.save();
    ctx.translate(pos.x - w / 2, pos.y - h / 2);
    ctx.scale(h / src.h, h / src.h);
    // Brand shapes may carry a gradient fill; running it tail-to-head gives
    // each arrow a lit leading edge, as in the reference art.
    const grad = ctx.createLinearGradient(0, src.h, src.w, 0);
    grad.addColorStop(0, rgba(tail, capped * 0.62));
    grad.addColorStop(1, rgba(col, capped));
    ctx.fillStyle = grad;
    ctx.fill(a.long ? scene.paths.arrowLong : scene.paths.arrowRegular);
    ctx.restore();
  }
}

// ---------------------------------------------------------------------------
// Bloom — cheap downscale blur composited additively
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
