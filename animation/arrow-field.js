/*
 * Arrow field — generative tiling animation engine.
 *
 * Builds a seamlessly looping field of the official arrow travelling along its
 * own axis (slope +37/15 = 2.4667, i.e. 67.93 deg above horizontal).
 *
 * How the seamless loop works
 * ---------------------------
 * Each layer is one element carrying a repeating background tile of TW x TH px.
 * TH / TW is fixed at 37/15, so the vector (TW, -TH) points exactly along the
 * travel direction AND is a lattice vector of the tiling. Translating a layer by
 * (TW, -TH) therefore lands the pattern back on itself: the last frame of the
 * loop is pixel-identical to the first. Loop distance per layer is fixed at
 * |(TW, -TH)| = 2.6617 * TW, so tile width alone sets that layer's speed.
 */

const ARROW = {
  // "Vector Official - Arrow Regular.svg", untouched.
  points:
    '308.51,0 46.97,114.42 0,224.04 208.02,137.79 68.91,480.94 67.58,484.26 ' +
    '113.86,600 286.24,169.06 376.67,375.07 422.98,267.08',
  w: 422.98,
  h: 600,
};

// Travel direction. 37/15 is the slope of the arrow's own shaft edge
// (208.02,137.79) -> (68.91,480.94), which is what the 2.467 spec describes.
const RISE = 37;
const RUN = 15;

const CONFIG = {
  width: 6878,
  height: 1080,
  duration: 360, // seconds, one full loop
  background: { top: '#13071A', bottom: '#3B1056' }, // near-black purple -> dark purple
  gradientFrom: '#8A25C9', // lower-left end of each arrow
  gradientTo: '#48C0D9', // upper-right end of each arrow
  // Halo and light trail. Lengths and blurs are fractions of the arrow's height,
  // so both scale with the arrow and every layer keeps the same look.
  glow: { blur: 0.055, opacity: 0.5 },
  trail: { length: 0.9, taper: 0.28, blur: 0.04, opacity: 0.2 },
  // Static grain over the background gradient. 1080 px of a shallow ramp bands
  // badly on a large LED wall; a couple of percent of noise dissolves the steps.
  // Set to 0 to switch it off.
  dither: 0.03,
  /*
   * Set to { top, bottom } to export with an alpha ground: the ground gradient
   * keeps its colours but carries those alphas instead of being opaque, so the
   * piece can be composited over something else. Arrows keep their own alpha
   * either way. Grain is skipped in this mode — it exists to dither an 8-bit
   * ramp, and that has to happen downstream once the ground is composited.
   */
  alphaGround: null,
  seed: 20260810,
  overscan: 16,
  // tileW must be a multiple of RUN so tileH = tileW / RUN * RISE stays integral
  // (fractional tile sizes produce visible seams in the repeated background).
  layers: [
    { tileW: 525, arrow: 48, opacity: 0.1, count: 10 },
    { tileW: 645, arrow: 68, opacity: 0.16, count: 12 },
    { tileW: 750, arrow: 92, opacity: 0.25, count: 12 },
    { tileW: 990, arrow: 130, opacity: 0.42, count: 14 },
    { tileW: 1200, arrow: 175, opacity: 0.68, count: 14 },
    { tileW: 1350, arrow: 235, opacity: 1.0, count: 12 },
  ],
  sizeJitter: [0.7, 1.35], // per-arrow multiplier on the layer's arrow height
  opacityJitter: [0.72, 1.0], // per-arrow multiplier on the layer's opacity
};

/* ---------------------------------------------------------------- utilities */

/** '#13071A' + 0.5 -> 'rgba(19, 7, 26, 0.5)'. */
function withAlpha(hex, alpha) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Gradient endpoints, in objectBoundingBox units, that make the colour bands run
 * perpendicular to the travel direction once the unit box is stretched back to a
 * `w` x `h` bbox. Solved so the gradient starts at the box corner furthest
 * down-left along the axis and ends at the corner furthest up-right.
 *
 * objectBoundingBox applies a *non-uniform* stretch, so mapping user-space points
 * into it is not enough — perpendicularity has to survive the stretch, which is
 * what the k below enforces. Any element whose bbox has this aspect can share the
 * result, which is why one gradient serves every arrow.
 */
function gradientEndpoints(w = ARROW.w, h = ARROW.h) {
  const dx = RUN;
  const dy = -RISE;
  // Band normal in bbox units must satisfy (gx / w) : (gy / h) = dx : dy.
  const k = (h / w) * (dy / dx); // gy = k * gx
  // Corner projections onto (1, k), with gx factored out.
  const proj = [0, 1, k, 1 + k];
  const lo = Math.min(...proj);
  const hi = Math.max(...proj);
  // |g|^2 must equal the projection span so the gradient maps [lo, hi] onto [0, 1].
  const gx = (hi - lo) / (1 + k * k);
  const g = [gx, k * gx];
  const gLen2 = g[0] * g[0] + g[1] * g[1];
  const t = (lo * gx) / gLen2; // start point = t * g
  return { x1: t * g[0], y1: t * g[1], x2: t * g[0] + g[0], y2: t * g[1] + g[1] };
}

/**
 * The light trail: a tapered quad running back down the travel axis from the
 * shaft's end cap, so it continues the line of the arrow rather than crossing it.
 * Built in the arrow's own coordinates, identical for every instance.
 */
function trailGeometry(cfg) {
  const norm = Math.hypot(RUN, RISE);
  const back = [-RUN / norm, RISE / norm]; // down-left, opposite to travel
  const A = [67.58, 484.26]; // shaft end cap, left corner
  const B = [113.86, 600]; // shaft end cap, right corner
  const mid = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2];
  const len = cfg.trail.length * ARROW.h;
  const t = cfg.trail.taper;
  const far = (p) => [
    mid[0] + (p[0] - mid[0]) * t + back[0] * len,
    mid[1] + (p[1] - mid[1]) * t + back[1] * len,
  ];
  const C = far(B);
  const D = far(A);
  const pts = [A, B, C, D];
  const xs = pts.map((p) => p[0]);
  const ys = pts.map((p) => p[1]);
  const box = { x: Math.min(...xs), y: Math.min(...ys) };
  box.w = Math.max(...xs) - box.x;
  box.h = Math.max(...ys) - box.y;
  return {
    d: `M${pts.map((p) => `${p[0].toFixed(2)} ${p[1].toFixed(2)}`).join('L')}Z`,
    box,
  };
}

/**
 * Bounding box of everything one arrow paints — body, trail and the blur that
 * spills past both. Edge duplication and tile culling work off this, not the
 * arrow's own bbox, or glow would be clipped at tile seams.
 */
function spriteBox(cfg, trail) {
  const bleed = 3 * Math.max(cfg.glow.blur, cfg.trail.blur) * ARROW.h;
  const x = Math.min(0, trail.box.x) - bleed;
  const y = Math.min(0, trail.box.y) - bleed;
  return {
    x,
    y,
    w: Math.max(ARROW.w, trail.box.x + trail.box.w) + bleed - x,
    h: Math.max(ARROW.h, trail.box.y + trail.box.h) + bleed - y,
  };
}

/** Blue-noise-ish sample of `n` points on a w x h torus, so tiles butt cleanly. */
function poissonTorus(w, h, n, rng) {
  const pts = [];
  let radius = 0.75 * Math.sqrt((w * h) / n);
  const far = (p, x, y) => {
    let ddx = Math.abs(p.x - x);
    let ddy = Math.abs(p.y - y);
    if (ddx > w / 2) ddx = w - ddx;
    if (ddy > h / 2) ddy = h - ddy;
    return ddx * ddx + ddy * ddy >= radius * radius;
  };
  while (pts.length < n) {
    let placed = false;
    for (let attempt = 0; attempt < 150; attempt++) {
      const x = rng() * w;
      const y = rng() * h;
      if (pts.every((p) => far(p, x, y))) {
        pts.push({ x, y });
        placed = true;
        break;
      }
    }
    if (!placed) radius *= 0.92;
  }
  return pts;
}

/* ------------------------------------------------------------- tile builder */

function buildTile(layer, index, cfg) {
  const tileH = (layer.tileW / RUN) * RISE;
  const rng = mulberry32(cfg.seed + index * 7919);
  const grad = gradientEndpoints();
  const trail = trailGeometry(cfg);
  const trailGrad = gradientEndpoints(trail.box.w, trail.box.h);
  const sprite = spriteBox(cfg, trail);
  const [sMin, sMax] = cfg.sizeJitter;
  const [oMin, oMax] = cfg.opacityJitter;

  const parts = [];
  for (const p of poissonTorus(layer.tileW, tileH, layer.count, rng)) {
    const scale = (layer.arrow * (sMin + rng() * (sMax - sMin))) / ARROW.h;
    const alpha = oMin + rng() * (oMax - oMin);
    // Anchor on the arrow's own centre; the sprite reaches further than that.
    const x0 = p.x - (ARROW.w * scale) / 2;
    const y0 = p.y - (ARROW.h * scale) / 2;
    // Repeat across tile edges so an arrow straddling a seam is drawn on both sides.
    for (let i = -1; i <= 1; i++) {
      for (let j = -1; j <= 1; j++) {
        const x = x0 + i * layer.tileW;
        const y = y0 + j * tileH;
        const left = x + sprite.x * scale;
        const top = y + sprite.y * scale;
        if (left > layer.tileW || left + sprite.w * scale < 0) continue;
        if (top > tileH || top + sprite.h * scale < 0) continue;
        parts.push(
          `<use href="#s" transform="translate(${x.toFixed(2)} ${y.toFixed(2)}) ` +
            `scale(${scale.toFixed(5)})" opacity="${alpha.toFixed(3)}"/>`
        );
      }
    }
  }

  // Blurs are declared in the arrow's own coordinates, inside the reused group,
  // so the use element's scale carries them — glow stays proportional at every size.
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${layer.tileW}" height="${tileH}" ` +
    `viewBox="0 0 ${layer.tileW} ${tileH}">` +
    '<defs>' +
    `<linearGradient id="g" x1="${grad.x1.toFixed(5)}" y1="${grad.y1.toFixed(5)}" ` +
    `x2="${grad.x2.toFixed(5)}" y2="${grad.y2.toFixed(5)}">` +
    `<stop offset="0" stop-color="${cfg.gradientFrom}"/>` +
    `<stop offset="1" stop-color="${cfg.gradientTo}"/>` +
    '</linearGradient>' +
    `<linearGradient id="tg" x1="${trailGrad.x1.toFixed(5)}" y1="${trailGrad.y1.toFixed(5)}" ` +
    `x2="${trailGrad.x2.toFixed(5)}" y2="${trailGrad.y2.toFixed(5)}">` +
    `<stop offset="0" stop-color="${cfg.gradientFrom}" stop-opacity="0"/>` +
    `<stop offset="0.55" stop-color="${cfg.gradientFrom}" stop-opacity="${(cfg.trail.opacity * 0.45).toFixed(3)}"/>` +
    `<stop offset="1" stop-color="${cfg.gradientFrom}" stop-opacity="${cfg.trail.opacity.toFixed(3)}"/>` +
    '</linearGradient>' +
    `<filter id="fg" x="-45%" y="-45%" width="190%" height="190%">` +
    `<feGaussianBlur stdDeviation="${(cfg.glow.blur * ARROW.h).toFixed(2)}"/></filter>` +
    `<filter id="ft" x="-40%" y="-40%" width="180%" height="180%">` +
    `<feGaussianBlur stdDeviation="${(cfg.trail.blur * ARROW.h).toFixed(2)}"/></filter>` +
    `<polygon id="a" points="${ARROW.points}"/>` +
    '<g id="s">' +
    (cfg.trail.opacity > 0 ? `<path d="${trail.d}" fill="url(#tg)" filter="url(#ft)"/>` : '') +
    (cfg.glow.opacity > 0
      ? `<use href="#a" fill="url(#g)" filter="url(#fg)" opacity="${cfg.glow.opacity}"/>`
      : '') +
    '<use href="#a" fill="url(#g)"/>' +
    '</g>' +
    '</defs>' +
    parts.join('') +
    '</svg>';

  return { svg, tileH };
}

/** Seamless grey grain, used at a few percent to keep the background ramp smooth. */
function ditherTile(size = 180) {
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">` +
    '<filter id="n" x="0" y="0" width="100%" height="100%">' +
    '<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch"/>' +
    '<feColorMatrix type="saturate" values="0"/>' +
    '<feComponentTransfer><feFuncA type="table" tableValues="1 1"/></feComponentTransfer>' +
    '</filter>' +
    `<rect width="${size}" height="${size}" filter="url(#n)"/>` +
    '</svg>'
  );
}

/* ------------------------------------------------------------------- mount */

/**
 * Fills `stage` with the animated layers and returns the layer metrics.
 * `stage` is expected to be exactly cfg.width x cfg.height with overflow hidden.
 */
function mountArrowField(stage, cfg = CONFIG) {
  const doc = stage.ownerDocument;
  const style = doc.createElement('style');
  const rules = [];
  const metrics = [];

  const ground = cfg.alphaGround
    ? `linear-gradient(180deg, ${withAlpha(cfg.background.top, cfg.alphaGround.top)} 0%, ` +
      `${withAlpha(cfg.background.bottom, cfg.alphaGround.bottom)} 100%)`
    : `linear-gradient(180deg, ${cfg.background.top} 0%, ${cfg.background.bottom} 100%)`;
  stage.style.background = ground;
  stage.style.position = stage.style.position || 'relative';

  if (cfg.dither > 0 && !cfg.alphaGround) {
    const grain = doc.createElement('div');
    grain.className = 'af-grain';
    Object.assign(grain.style, {
      position: 'absolute',
      inset: '0',
      backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(ditherTile())}")`,
      backgroundRepeat: 'repeat',
      opacity: String(cfg.dither),
      mixBlendMode: 'overlay',
      pointerEvents: 'none',
    });
    stage.appendChild(grain);
  }

  // The drifting layers live in their own wrapper so the transition can fade the
  // whole ambient field down as one thing without disturbing per-layer opacity.
  const ambient = doc.createElement('div');
  ambient.className = 'af-ambient';
  Object.assign(ambient.style, { position: 'absolute', inset: '0' });
  stage.appendChild(ambient);

  cfg.layers.forEach((layer, index) => {
    const { svg, tileH } = buildTile(layer, index, cfg);
    const travel = Math.hypot(layer.tileW, tileH);
    const el = doc.createElement('div');
    el.className = 'af-layer';
    el.dataset.layer = String(index + 1);
    Object.assign(el.style, {
      position: 'absolute',
      left: `${-layer.tileW - cfg.overscan}px`,
      top: `${-cfg.overscan}px`,
      width: `${cfg.width + layer.tileW + cfg.overscan * 2}px`,
      height: `${cfg.height + tileH + cfg.overscan * 2}px`,
      backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(svg)}")`,
      backgroundRepeat: 'repeat',
      backgroundSize: `${layer.tileW}px ${tileH}px`,
      opacity: String(layer.opacity),
      animation: `af-drift-${index} ${cfg.duration}s linear infinite`,
      willChange: 'transform',
    });
    rules.push(
      `@keyframes af-drift-${index}{` +
        'from{transform:translate3d(0,0,0)}' +
        `to{transform:translate3d(${layer.tileW}px,${-tileH}px,0)}}`
    );
    ambient.appendChild(el);

    metrics.push({
      index: index + 1,
      tileW: layer.tileW,
      tileH,
      arrow: layer.arrow,
      opacity: layer.opacity,
      count: layer.count,
      onScreen: Math.round((layer.count * cfg.width * cfg.height) / (layer.tileW * tileH)),
      travel,
      speed: travel / cfg.duration,
    });
  });

  style.textContent = rules.join('');
  doc.head.appendChild(style);

  // The once-per-loop logo event, if the transition module and its assets are
  // present. Ambient-only builds simply skip it.
  let transition = null;
  if (typeof mountTransition === 'function' && typeof MARK_POINTS !== 'undefined' && cfg.layers.length) {
    transition = mountTransition(stage, ambient, {
      config: cfg.transition,
      venue: VENUE,
      markPoints: MARK_POINTS,
      arrow: ARROW,
      logoSvg: VECTOR_LOGO_SVG,
      wipeArrow: WIPE_ARROW_SVG,
      portrait: SPEAKER_PORTRAIT,
      duration: cfg.duration,
      rng: mulberry32(cfg.seed ^ 0x5f3a),
    });
  }

  return { metrics, ambient, transition };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CONFIG,
    ARROW,
    RISE,
    RUN,
    mulberry32,
    gradientEndpoints,
    trailGeometry,
    buildTile,
    ditherTile,
    mountArrowField,
  };
}
