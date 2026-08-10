// Vector Institute — "Arrival": the arrows-into-logo moment.
//
// A short, one-shot piece for the walls in the minute before a keynote speaker
// takes the stage. It opens on the same field as the main loop, so it can be
// cut to live without the room appearing to change, then the arrows gather out
// of their travel axis and assemble the Vector mark on the west wall.
//
// The gather is the whole idea: the arrows do not fade out and get replaced by
// a logo, they *become* it. Each one is given a target sampled from inside the
// icon's own outline, so at the moment the shape closes it is still made of the
// marks that were flying a second earlier — then the solid lockup resolves on
// top and the wordmark follows.
//
// Unlike the main loop this does not loop: it ends on a hold, long enough to
// sit under an introduction and be cut away from on a cue.

import {
  CANVAS_W,
  CANVAS_H,
  VENUE,
  ARROW_REGULAR,
  ARROW_LONG,
  LOGO_ICON,
  LOGO_WORDMARK,
  gradientAt,
  rgba,
} from './brand.js';
import { FLOW_DEG, drawBackground, stateFactors } from './scene.js';

export const MOMENT_DURATION = 12; // seconds, one shot

const TH = (FLOW_DEG * Math.PI) / 180;
const DIR = { x: Math.cos(TH), y: -Math.sin(TH) };
const PERP = { x: Math.sin(TH), y: Math.cos(TH) };

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const lerp = (a, b, k) => a + (b - a) * k;
const smooth = (k) => {
  const t = clamp01(k);
  return t * t * (3 - 2 * t);
};

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let x = Math.imul(a ^ (a >>> 15), 1 | a);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------------------------------------------------------------------------
// Timeline
// ---------------------------------------------------------------------------

const T_GATHER = 3.0;   // arrows start leaving the travel axis
const T_FORMED = 7.2;   // the shape has closed
const T_SOLID = 8.6;    // the solid icon has taken over
const T_WORD = 10.0;    // the wordmark has arrived
                        // ...then hold to MOMENT_DURATION

// ---------------------------------------------------------------------------
// Placement — centred on the domino screen
//
// The west wall carries a physical LED screen at x 2633..4243, y 0..628. That
// is the brightest, flattest surface in the room and the one the audience is
// already facing, so the lockup is centred in it rather than on the wall as a
// whole. Proportions are the official ones.
// ---------------------------------------------------------------------------

const DM = VENUE.domino;
const CX = (DM.x0 + DM.x1) / 2;
const CY = (DM.y0 + DM.y1) / 2;

const ICON_H = 384;
const ICON_W = ICON_H * (LOGO_ICON.x1 - LOGO_ICON.x0) / (LOGO_ICON.y1 - LOGO_ICON.y0);
const WORD_W = 900;
const WORD_H = WORD_W * (LOGO_WORDMARK.y1 - LOGO_WORDMARK.y0) /
  (LOGO_WORDMARK.x1 - LOGO_WORDMARK.x0);
const GAP = 54;

const BLOCK_H = ICON_H + GAP + WORD_H;
const ICON_TOP = CY - BLOCK_H / 2;
const WORD_TOP = ICON_TOP + ICON_H + GAP;

const ICON_BOX = {
  x0: CX - ICON_W / 2, y0: ICON_TOP, x1: CX + ICON_W / 2, y1: ICON_TOP + ICON_H,
};
const WORD_BOX = {
  x0: CX - WORD_W / 2, y0: WORD_TOP, x1: CX + WORD_W / 2, y1: WORD_TOP + WORD_H,
};

// ---------------------------------------------------------------------------
// Target points — sampled from the icon's own outline
//
// Rasterising the official paths and reading back the covered pixels is the
// only way to get points that are genuinely *inside* the mark, including the
// notch between the V and the arrow. Approximating it with a grid and a
// hand-written mask would drift the moment the artwork is updated.
// ---------------------------------------------------------------------------

function sampleIcon(makeCanvas, count) {
  const P2D = globalThis.Path2D;
  const N = 180;
  const c = makeCanvas(N, N);
  const g = c.getContext('2d');
  const sx = N / (LOGO_ICON.x1 - LOGO_ICON.x0);
  const sy = N / (LOGO_ICON.y1 - LOGO_ICON.y0);

  g.save();
  g.scale(sx, sy);
  g.translate(-LOGO_ICON.x0, -LOGO_ICON.y0);
  for (const part of LOGO_ICON.parts) {
    g.fillStyle = part.fill;
    g.fill(new P2D(part.d));
  }
  g.restore();

  const data = g.getImageData(0, 0, N, N).data;
  const inside = [];
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const i = (y * N + x) * 4;
      if (data[i + 3] > 140) {
        // Keep which half of the mark the point came from, so the arrows that
        // land in the logo's own arrow can be lit differently.
        inside.push([x / N, y / N, data[i] > 200 && data[i + 1] < 120 ? 1 : 0]);
      }
    }
  }

  const rnd = mulberry32(0x10c0);
  const out = [];
  for (let i = 0; i < count; i++) {
    const [u, v, accent] = inside[Math.floor(rnd() * inside.length)];
    out.push({
      x: ICON_BOX.x0 + u * ICON_W,
      y: ICON_BOX.y0 + v * ICON_H,
      accent,
    });
  }
  return out;
}

// ---------------------------------------------------------------------------
// Arrows
// ---------------------------------------------------------------------------

const MARGIN_A = 950;
const MARGIN_B = 420;

const EXT = (() => {
  let aMin = Infinity, aMax = -Infinity, bMin = Infinity, bMax = -Infinity;
  for (const [x, y] of [[0, 0], [CANVAS_W, 0], [0, CANVAS_H], [CANVAS_W, CANVAS_H]]) {
    const a = x * DIR.x + y * DIR.y;
    const b = x * PERP.x + y * PERP.y;
    aMin = Math.min(aMin, a); aMax = Math.max(aMax, a);
    bMin = Math.min(bMin, b); bMax = Math.max(bMax, b);
  }
  return {
    a0: aMin - MARGIN_A, aLen: aMax - aMin + MARGIN_A * 2,
    b0: bMin - MARGIN_B, bLen: bMax - bMin + MARGIN_B * 2,
  };
})();

export function createMoment(makeCanvas) {
  const P2D = globalThis.Path2D;
  if (!P2D) throw new Error('Path2D is required (set globalThis.Path2D in Node).');

  const rnd = mulberry32(0xa27f);
  const COUNT = 620;
  const targets = sampleIcon(makeCanvas, COUNT);

  const arrows = [];
  for (let i = 0; i < COUNT; i++) {
    const depth = Math.pow(rnd(), 1.35);
    arrows.push({
      u0: rnd(),
      lane: rnd(),
      laps: 1 + Math.floor(rnd() * 3),
      wob: rnd() * Math.PI * 2,
      wobAmt: 30 + rnd() * 90,
      depth,
      // Weighted small: 620 arrows at the main loop's hero sizes fills the
      // room with a wall of chevrons instead of a field with depth in it.
      h: lerp(0.022, 0.40, Math.pow(clamp01(depth * 0.8 + rnd() * 0.25), 1.7)),
      long: rnd() < 0.16,
      // Staggering the gather is what makes it read as a swarm converging
      // rather than a single rigid transform of the whole field.
      delay: rnd() * 0.42,
      landed: lerp(15, 27, rnd()),
      target: targets[i],
      alphaVar: 0.75 + rnd() * 0.4,
    });
  }

  return {
    arrows,
    paths: {
      arrowRegular: new P2D(ARROW_REGULAR.d),
      arrowLong: new P2D(ARROW_LONG.d),
      icon: LOGO_ICON.parts.map((p) => ({ fill: p.fill, path: new P2D(p.d) })),
      word: LOGO_WORDMARK.parts.map((p) => ({ fill: p.fill, path: new P2D(p.d) })),
    },
  };
}

function flowPosition(a, t) {
  // Same axis and the same speeds as the main loop, so a cut into this piece
  // from the loop does not show a jump.
  const u = (a.u0 + (a.laps * t) / 26) % 1;
  const along = EXT.a0 + u * EXT.aLen;
  const across = EXT.b0 + a.lane * EXT.bLen + Math.sin(a.wob + t * 0.4) * a.wobAmt;
  return {
    x: along * DIR.x + across * PERP.x,
    y: along * DIR.y + across * PERP.y,
  };
}

// ---------------------------------------------------------------------------
// Draw
// ---------------------------------------------------------------------------

export function drawMoment(ctx, time, moment, opts = {}) {
  const t = Math.min(Math.max(time, 0), MOMENT_DURATION);
  const k = stateFactors(opts.dark ?? 0);

  drawBackground(ctx, t, k);

  // How far each arrow has left the travel axis, and how far the solid lockup
  // has taken over from the swarm.
  const solid = smooth((t - T_FORMED) / (T_SOLID - T_FORMED));
  const word = smooth((t - T_SOLID) / (T_WORD - T_SOLID));

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';

  for (const a of moment.arrows) {
    const flow = flowPosition(a, t);
    const span = T_FORMED - T_GATHER;
    const g = smooth(((t - T_GATHER) / span - a.delay) / (1 - a.delay));

    const x = lerp(flow.x, a.target.x, g);
    const y = lerp(flow.y, a.target.y, g);

    const src = a.long ? ARROW_LONG : ARROW_REGULAR;
    const h = lerp(CANVAS_H * a.h, a.landed, g);
    const w = (h / src.h) * src.w;
    if (x < -w - 80 || x > CANVAS_W + w + 80) continue;
    if (y < -h - 80 || y > CANVAS_H + h + 80) continue;

    // As an arrow arrives it takes the colour of the part of the mark it lands
    // in, and the swarm dims as the solid lockup comes up underneath it.
    const flown = gradientAt(clamp01(x / CANVAS_W), clamp01(0.45 + a.depth * 0.55));
    const col = g > 0.001
      ? [
        Math.round(lerp(flown[0], a.target.accent ? 237 : 255, g)),
        Math.round(lerp(flown[1], a.target.accent ? 44 : 255, g)),
        Math.round(lerp(flown[2], a.target.accent ? 138 : 255, g)),
      ]
      : flown;

    // Held below the main loop's level on purpose: 620 arrows overlapping
    // additively drive violet up its red channel first, and a saturated
    // violet stack reads pink — the one colour that is meant to stay out of
    // the room.
    const alpha = (0.22 + 0.78 * a.depth) * a.alphaVar * 0.84 *
      lerp(1, 0.55, g) * (1 - solid) * k.marks;
    if (alpha < 0.006) continue;

    ctx.save();
    ctx.translate(x - w / 2, y - h / 2);
    ctx.scale(h / src.h, h / src.h);
    ctx.fillStyle = rgba(col, Math.min(alpha, 0.95));
    ctx.fill(a.long ? moment.paths.arrowLong : moment.paths.arrowRegular);
    ctx.restore();
  }

  ctx.restore();

  if (solid > 0.001) drawLockup(ctx, moment, solid, word, k);
}

function drawPartsIn(ctx, parts, box, src, alpha) {
  const sx = (box.x1 - box.x0) / (src.x1 - src.x0);
  const sy = (box.y1 - box.y0) / (src.y1 - src.y0);
  ctx.save();
  ctx.translate(box.x0, box.y0);
  ctx.scale(sx, sy);
  ctx.translate(-src.x0, -src.y0);
  ctx.globalAlpha = alpha;
  for (const p of parts) {
    ctx.fillStyle = p.fill;
    ctx.fill(p.path);
  }
  ctx.restore();
}

function drawLockup(ctx, moment, solid, word, k) {
  // The lockup is the official full-colour reverse variant, magenta arrow and
  // all. Magenta is out of the room's *palette*, but the mark is the mark —
  // repainting it would be the brand error, not the restraint.
  drawPartsIn(ctx, moment.paths.icon, ICON_BOX, LOGO_ICON, solid * k.marks);
  if (word > 0.001) {
    drawPartsIn(ctx, moment.paths.word, WORD_BOX, LOGO_WORDMARK, word * k.marks);
  }
}
