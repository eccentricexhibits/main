/*
 * Transition — the once-per-loop event where the ambient field converges and
 * resolves into the Vector logo on the Domino screen.
 *
 * Sequence
 * --------
 *   sweep    the ambient layers fade down; arrows run *horizontally* along their
 *            own band toward the west wall. Nothing moves vertically yet, so the
 *            four bands stay in their own lanes right up to the centre.
 *   gather   past the gate, each arrow eases onto a point sampled from the
 *            Vector mark, and its colour crosses from the ambient gradient to
 *            white or magenta. Arrows with no point to fill dissolve.
 *   reveal   the crisp mark fades in over the arrows; the arrows fade out.
 *   resolve  the mark eases down into its slot in the full bilingual lockup as
 *            the wordmark fades in beside it.
 *   hold     the finished logo sits at 70% of the Domino screen's width.
 *   release  the logo fades out and the ambient field comes back up.
 *
 * Everything here is a pure function of t. No integration, no accumulated state:
 * draw(t) at any time gives the same pixels, which is what makes the whole loop
 * seekable and therefore exportable frame by frame.
 */

const TRANSITION = {
  at: 240, // seconds into the loop
  sweep: 14,
  gather: 7,
  reveal: 4,
  resolve: 3,
  hold: 7,
  release: 10,

  extras: 220, // arrows beyond those needed for the mark, which dissolve on arrival
  // Arrows leave the wall at roughly ambient scale and shrink as they gather, so
  // the field reads as turning and condensing rather than being swapped out for
  // a different, much smaller set of arrows.
  arrowStart: [34, 120],
  arrowEnd: [8, 13],
  gateJitter: 150, // spread the turn-in point so the bands do not form a curtain
  feed: 0.9, // extra run laid out beyond each band, so arrows keep feeding in
  markHeight: 0.7, // the formed mark, as a fraction of the Domino screen's height
  logoWidth: 0.7, // the finished lockup, as a fraction of the Domino screen's width
  /*
   * 'settle' forms the mark large, then eases it into the lockup.
   * 'inPlace' forms it at lockup size and just fades the lockup in over the top —
   *   truer to the brief's wording, but the formed mark is only ~219 px wide.
   * 'markOnly' stops at the crisp mark and never brings in the wordmark.
   */
  finish: 'settle',
  seed: 90210,
};

/* ------------------------------------------------------------------- easing */

const ease = {
  inOut: (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2),
  out: (u) => 1 - Math.pow(1 - u, 3),
  outBack: (u) => 1 + 2.2 * Math.pow(u - 1, 3) + 1.2 * Math.pow(u - 1, 2),
};

const clamp01 = (u) => (u < 0 ? 0 : u > 1 ? 1 : u);
const span = (t, a, b) => clamp01((t - a) / (b - a));
const mix = (a, b, u) => a + (b - a) * u;

/* ------------------------------------------------------------------ colours */

function parseHex(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

/** Cached colour lerp — particles quantise their blend so the cache stays small. */
function makeMixer() {
  const cache = new Map();
  return (from, to, u) => {
    const q = Math.round(u * 24);
    const key = `${from}|${to}|${q}`;
    let hit = cache.get(key);
    if (!hit) {
      const a = parseHex(from);
      const b = parseHex(to);
      const v = q / 24;
      hit = `rgb(${Math.round(mix(a[0], b[0], v))},${Math.round(mix(a[1], b[1], v))},${Math.round(
        mix(a[2], b[2], v)
      )})`;
      cache.set(key, hit);
    }
    return hit;
  };
}

/* ------------------------------------------------------------------- timing */

function phases(cfg) {
  const t = { start: cfg.at };
  t.sweepEnd = t.start + cfg.sweep;
  t.gatherEnd = t.sweepEnd + cfg.gather;
  t.revealEnd = t.gatherEnd + cfg.reveal;
  t.resolveEnd = t.revealEnd + cfg.resolve;
  t.holdEnd = t.resolveEnd + cfg.hold;
  t.end = t.holdEnd + cfg.release;
  return t;
}

/* ---------------------------------------------------------------- particles */

/**
 * Where the mark gets built, and where the lockup ends up. In 'settle' the mark
 * forms large and later eases into the lockup; the two rects are what the CSS
 * transform interpolates between.
 */
function layout(cfg, venue, markPoints) {
  const dom = venue.domino;
  const logoAspect = (() => {
    const vb = markPoints.logoViewBox.split(/\s+/).map(Number);
    return { w: vb[2], h: vb[3] };
  })();

  const lockupW = cfg.logoWidth * dom.w;
  const lockupH = (lockupW / logoAspect.w) * logoAspect.h;
  const lockup = {
    x: dom.cx - lockupW / 2,
    y: dom.cy - lockupH / 2,
    w: lockupW,
    h: lockupH,
  };

  // The mark's slot inside that lockup.
  const k = lockupW / logoAspect.w;
  const slot = {
    x: lockup.x + markPoints.markX * k,
    y: lockup.y + markPoints.markY * k,
    w: markPoints.width * k,
    h: markPoints.height * k,
  };

  // Where the arrows actually build it.
  let formed = slot;
  if (cfg.finish !== 'inPlace') {
    const h = cfg.markHeight * dom.h;
    const w = (h / markPoints.height) * markPoints.width;
    formed = { x: dom.cx - w / 2, y: dom.cy - h / 2, w, h };
  }

  return { lockup, slot, formed, scale: formed.h / slot.h };
}

function buildParticles(cfg, venue, markPoints, palette, rand) {
  const t = phases(cfg);
  const geo = layout(cfg, venue, markPoints);

  // Mark points, ordered left to right, so the two streams interleave in the
  // middle rather than one side reaching across the other.
  const targets = markPoints.points
    .map(([mx, my, magenta]) => ({
      x: geo.formed.x + (mx / markPoints.width) * geo.formed.w,
      y: geo.formed.y + (my / markPoints.height) * geo.formed.h,
      magenta: magenta === 1,
    }))
    .sort((a, b) => a.x - b.x);

  const particles = [];
  const total = targets.length + cfg.extras;
  const bands = venue.bands;

  for (let i = 0; i < total; i++) {
    const band = bands[i % bands.length];
    const fromSouth = band.dir > 0;

    /*
     * A conveyor, not a one-shot drain. Arrows are laid out over a run longer
     * than the band itself and all travel at close to the same speed, so ones
     * that begin off the outer end keep feeding in behind the leaders and the
     * wall stays populated until near the end of the sweep. Letting every arrow
     * simply start inside the band empties the far ends within a few seconds.
     */
    const run = band.w * (1 + cfg.feed);
    const reach = rand() * run; // distance this arrow has to cover
    const x0 = band.gate - band.dir * reach;
    const y0 = band.y + 10 + rand() * (band.h - 20);

    const speed = (run / (cfg.sweep * 0.95)) * mix(0.92, 1.08, rand());
    const gateT = Math.min(t.start + reach / speed, t.sweepEnd);
    // Arrows that start beyond the wall appear as they cross its outer edge.
    const fadeIn = t.start + Math.max(0, (reach - band.w) / speed);
    const arriveT = mix(gateT + 1.4, t.gatherEnd, 0.35 + rand() * 0.65);

    particles.push({
      x0,
      y0,
      dir: band.dir,
      gate: band.gate - band.dir * rand() * cfg.gateJitter,
      gateT,
      arriveT,
      size0: mix(cfg.arrowStart[0], cfg.arrowStart[1], Math.pow(rand(), 1.7)),
      size1: mix(cfg.arrowEnd[0], cfg.arrowEnd[1], rand()),
      tint: palette[Math.floor(rand() * palette.length)],
      fadeIn,
      target: null,
      // Where a dissolving arrow drifts to as it gives up.
      driftY: (rand() - 0.5) * 120,
    });
  }

  // Hand the mark's points to the arrows best placed to reach them: south-side
  // arrows take the left of the mark, north-side the right.
  const south = particles.filter((p) => p.dir > 0);
  const north = particles.filter((p) => p.dir < 0);
  const shuffle = (arr) => arr.sort(() => rand() - 0.5);
  shuffle(south);
  shuffle(north);
  const half = Math.round(targets.length / 2);
  south.slice(0, half).forEach((p, i) => (p.target = targets[i]));
  north.slice(0, targets.length - half).forEach((p, i) => (p.target = targets[half + i]));

  return { particles, geo, times: t };
}

/* ------------------------------------------------------------------ drawing */

function makeRenderer(canvas, cfg, venue, markPoints, arrow, palette, rand) {
  const ctx = canvas.getContext('2d');
  const { particles, geo, times } = buildParticles(cfg, venue, markPoints, palette, rand);
  const blend = makeMixer();

  const path = new Path2D();
  const pts = arrow.points.split(' ').map((pair) => pair.split(',').map(Number));
  pts.forEach(([x, y], i) => (i ? path.lineTo(x, y) : path.moveTo(x, y)));
  path.closePath();

  const WHITE = '#FFFFFF';
  const MAGENTA = '#FF0FF1';

  function draw(t) {
    ctx.clearRect(0, 0, venue.width, venue.height);
    if (t < times.start || t > times.end) return;

    for (const p of particles) {
      let x;
      let y;
      let alpha;
      let size = p.size0;
      let colour = p.tint;

      if (t < p.gateT) {
        // Horizontal run along the band. No vertical movement whatsoever.
        const u = span(t, p.fadeIn, p.gateT);
        x = mix(p.x0, p.gate, u);
        y = p.y0;
        alpha = span(t, p.fadeIn, p.fadeIn + 0.9);
      } else if (p.target) {
        const u = ease.inOut(span(t, p.gateT, p.arriveT));
        x = mix(p.gate, p.target.x, u);
        y = mix(p.y0, p.target.y, u);
        size = mix(p.size0, p.size1, u);
        colour = blend(p.tint, p.target.magenta ? MAGENTA : WHITE, Math.min(1, u * 1.35));
        // Once the crisp mark is coming up, the arrows step aside.
        alpha = 1 - span(t, times.gatherEnd, times.revealEnd);
      } else {
        // No point to fill — carry on past the gate and dissolve.
        const u = span(t, p.gateT, p.gateT + 2.2);
        x = p.gate + p.dir * 220 * ease.out(u);
        y = p.y0 + p.driftY * ease.out(u);
        size = mix(p.size0, p.size0 * 0.55, u);
        alpha = 1 - u;
      }

      if (alpha <= 0.004) continue;
      const k = size / arrow.h;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = colour;
      ctx.setTransform(k, 0, 0, k, x - (arrow.w * k) / 2, y - (arrow.h * k) / 2);
      ctx.fill(path);
    }

    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha = 1;
  }

  return { draw, geo, times, count: particles.length };
}

/* ------------------------------------------------------------------- mount */

/**
 * Adds the canvas and the logo to an already-mounted stage, and returns a
 * controller. `ambient` is the wrapper holding the drifting layers, which this
 * fades down for the duration of the event.
 */
function mountTransition(stage, ambient, opts) {
  const { config, venue, markPoints, arrow, logoSvg, duration } = opts;
  const cfg = Object.assign({}, TRANSITION, config || {});
  const doc = stage.ownerDocument;
  const t = phases(cfg);

  if (t.end >= duration) {
    throw new Error(`transition ends at ${t.end}s but the loop is only ${duration}s`);
  }

  const rand = opts.rng;
  const palette = opts.palette;

  const canvas = doc.createElement('canvas');
  canvas.className = 'af-particles';
  canvas.width = venue.width;
  canvas.height = venue.height;
  Object.assign(canvas.style, {
    position: 'absolute',
    inset: '0',
    width: `${venue.width}px`,
    height: `${venue.height}px`,
    pointerEvents: 'none',
  });
  stage.appendChild(canvas);

  const renderer = makeRenderer(canvas, cfg, venue, markPoints, arrow, palette, rand);
  const geo = renderer.geo;

  // The logo, positioned at its final lockup rect. Everything that moves is a
  // transform on this element, so it stays a CSS animation and stays seekable.
  const holder = doc.createElement('div');
  holder.className = 'af-logo';
  Object.assign(holder.style, {
    position: 'absolute',
    left: `${geo.lockup.x}px`,
    top: `${geo.lockup.y}px`,
    width: `${geo.lockup.w}px`,
    height: `${geo.lockup.h}px`,
    opacity: '0',
    pointerEvents: 'none',
    filter: 'drop-shadow(0 0 26px rgba(255, 15, 241, 0.28))',
  });
  holder.innerHTML = logoSvg;
  const svg = holder.querySelector('svg');
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', '100%');
  stage.appendChild(holder);

  const markCx = geo.slot.x - geo.lockup.x + geo.slot.w / 2;
  const markCy = geo.slot.y - geo.lockup.y + geo.slot.h / 2;
  const dx = geo.formed.x + geo.formed.w / 2 - (geo.lockup.x + markCx);
  const dy = geo.formed.y + geo.formed.h / 2 - (geo.lockup.y + markCy);
  holder.style.transformOrigin = `${markCx}px ${markCy}px`;

  const pct = (time) => ((time / duration) * 100).toFixed(4);
  const big = `translate(${dx.toFixed(2)}px, ${dy.toFixed(2)}px) scale(${geo.scale.toFixed(4)})`;
  const wordmark = holder.querySelector('#wordmark');
  const settles = cfg.finish === 'settle';
  const keepsWordmark = cfg.finish !== 'markOnly';

  const rules = [
    '@keyframes af-logo-in{' +
      `0%,${pct(t.gatherEnd)}%{opacity:0;transform:${settles ? big : 'none'}}` +
      `${pct(t.revealEnd)}%{opacity:1;transform:${settles ? big : 'none'}}` +
      `${pct(t.resolveEnd)}%,${pct(t.holdEnd)}%{opacity:1;transform:none}` +
      `${pct(t.end)}%,100%{opacity:0;transform:none}}`,
    '@keyframes af-wordmark-in{' +
      `0%,${pct(t.revealEnd)}%{opacity:0}` +
      `${pct(t.resolveEnd)}%,${pct(t.holdEnd)}%{opacity:${keepsWordmark ? 1 : 0}}` +
      `${pct(t.end)}%,100%{opacity:0}}`,
    // The ambient field steps back for the event and returns afterwards.
    '@keyframes af-ambient-out{' +
      `0%,${pct(t.start)}%{opacity:1}` +
      `${pct(t.start + cfg.sweep * 0.55)}%,${pct(t.holdEnd)}%{opacity:0}` +
      `${pct(t.end)}%,100%{opacity:1}}`,
  ];

  const style = doc.createElement('style');
  style.textContent = rules.join('');
  doc.head.appendChild(style);

  holder.style.animation = `af-logo-in ${duration}s linear infinite`;
  if (wordmark) wordmark.style.animation = `af-wordmark-in ${duration}s linear infinite`;
  ambient.style.animation = `af-ambient-out ${duration}s linear infinite`;

  return {
    draw: renderer.draw,
    times: t,
    geo,
    particles: renderer.count,
    markPoints: markPoints.points.length,
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { TRANSITION, phases, layout, mountTransition };
}
