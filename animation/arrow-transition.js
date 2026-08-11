/*
 * Transition — the once-per-loop event where the ambient field converges and
 * resolves into the Vector logo on the Domino screen.
 *
 * Sequence
 * --------
 *   sweep    the ambient layers fade down; arrows run *horizontally* along their
 *            own band toward the west wall, turning to fly nose-first. Nothing
 *            moves vertically yet, so the four bands stay in their own lanes.
 *   gather   near the centre each arrow swoops out of its lane onto a point
 *            sampled from the Vector mark, straightening up as it lands, while
 *            its colour crosses from the ambient gradient to white or magenta.
 *            Arrows with no point to fill dissolve.
 *
 * There is no gate. An arrow bends when it comes within its own randomised
 * distance of its destination, so no two break at the same x — a single shared
 * turn-in point draws a vertical column of arrows down the wall.
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
  feed: 0.9, // extra run laid out beyond each band, so arrows keep feeding in
  /*
   * How far short of its destination an arrow starts to bend out of its lane.
   * Randomised per arrow: a single figure makes every arrow break at the same x
   * and draws a seam down the wall, which is the "vertical column" the earlier
   * gate produced. The shortest of these still keeps the arrow travelling flat
   * until it is essentially at the west wall.
   */
  swoop: [420, 860],
  magenta: '#EB088A',
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

  const bands = venue.bands;
  const run = bands[0].w * (1 + cfg.feed);
  // One speed for everything. Journeys are laid out backwards from where each
  // arrow has to end up, so the length of the run — not the speed — is what
  // staggers arrivals across the window.
  const speed = run / (cfg.sweep + cfg.gather * 0.9);

  // South-side arrows take the left of the mark and north-side the right, so
  // the two streams interleave in the middle instead of reaching across.
  const half = Math.round(targets.length / 2);
  const jobs = targets.map((target, i) => ({ target, dir: i < half ? 1 : -1 }));
  for (let i = 0; i < cfg.extras; i++) {
    // Extras aim at a scatter around the mark and dissolve before they land.
    const angle = rand() * Math.PI * 2;
    const r = mix(140, 460, rand());
    jobs.push({
      dir: i % 2 ? 1 : -1,
      target: {
        x: geo.formed.x + geo.formed.w / 2 + Math.cos(angle) * r,
        y: geo.formed.y + geo.formed.h / 2 + Math.sin(angle) * r * 0.6,
        magenta: false,
      },
      ghost: true,
    });
  }

  const particles = jobs.map((job) => {
    const lane = bands.filter((b) => b.dir === job.dir);
    const band = lane[Math.floor(rand() * lane.length)];

    /*
     * A conveyor, not a one-shot drain. Distances are spread across the whole
     * run, so arrows that begin off the outer end keep feeding in behind the
     * leaders and the wall stays populated to the end of the sweep. Starting
     * every arrow inside the band empties the far ends within seconds.
     */
    const reach = mix(700, run, rand());
    const start = { x: job.target.x - job.dir * reach, y: band.y + 12 + rand() * (band.h - 24) };
    const launch = t.start;
    const arrive = launch + reach / speed;
    // Arrows laid out beyond the wall appear as they cross into it.
    const edge = job.dir > 0 ? 0 : venue.width;
    const outside = job.dir > 0 ? start.x < edge : start.x > edge;
    const fadeIn = outside ? launch + Math.abs(edge - start.x) / speed : launch;

    return {
      start,
      target: job.target,
      ghost: !!job.ghost,
      dir: job.dir,
      launch,
      arrive,
      swoop: mix(cfg.swoop[0], cfg.swoop[1], rand()),
      size0: mix(cfg.arrowStart[0], cfg.arrowStart[1], Math.pow(rand(), 1.7)),
      size1: mix(cfg.arrowEnd[0], cfg.arrowEnd[1], rand()),
      tint: palette[Math.floor(rand() * palette.length)],
      fadeIn,
    };
  });

  return { particles, geo, times: t, speed };
}

/* ------------------------------------------------------------------ drawing */

function makeRenderer(canvas, cfg, venue, markPoints, arrow, palette, rand) {
  const ctx = canvas.getContext('2d');
  const { particles, geo, times } = buildParticles(cfg, venue, markPoints, palette, rand);
  const blend = makeMixer();

  // Centred on the arrow's own middle, so rotation turns it about itself.
  const path = new Path2D();
  arrow.points.split(' ').forEach((pair, i) => {
    const [px, py] = pair.split(',').map(Number);
    const x = px - arrow.w / 2;
    const y = py - arrow.h / 2;
    i ? path.lineTo(x, y) : path.moveTo(x, y);
  });
  path.closePath();

  const WHITE = '#FFFFFF';
  const MAGENTA = cfg.magenta;
  // The arrow's own axis, so "rotation 0" means the artwork as drawn.
  const THETA0 = Math.atan2(-RISE, RUN);

  function draw(t) {
    ctx.clearRect(0, 0, venue.width, venue.height);
    if (t < times.start || t > times.end) return;

    const packDown = span(t, times.gatherEnd, times.revealEnd);

    for (const p of particles) {
      if (t < p.fadeIn) continue;

      const flight = clamp01((t - p.launch) / (p.arrive - p.launch));
      const x = mix(p.start.x, p.target.x, flight);

      /*
       * The swoop. Vertical position is a function of how close the arrow is to
       * its destination in x, not of elapsed time — so every arrow travels flat
       * down its own lane and only bends out of it near the middle, and because
       * the bend distance is randomised no two arrows break at the same place.
       */
      const remain = Math.abs(p.target.x - x);
      const s = clamp01((p.swoop - remain) / p.swoop);
      const curve = s * s * (3 - 2 * s);
      const rise = p.target.y - p.start.y;
      const y = p.start.y + rise * curve;

      const size = mix(p.size0, p.size1, curve);
      let alpha = span(t, p.fadeIn, p.fadeIn + 1.1) * (1 - packDown);
      let colour = p.tint;
      if (p.ghost) {
        alpha *= 1 - clamp01((s - 0.35) / 0.5); // give up before landing
      } else {
        colour = blend(p.tint, p.target.magenta ? MAGENTA : WHITE, clamp01(s * 1.5));
      }
      if (alpha <= 0.004) continue;

      /*
       * Turn to fly along the path, then straighten up on arrival so the mark is
       * built out of arrows in their proper orientation.
       */
      const slope = (rise * 6 * s * (1 - s)) / p.swoop;
      const heading = Math.atan2(slope * p.dir, p.dir);
      const land = clamp01((s - 0.74) / 0.26);
      const align = clamp01((t - p.fadeIn) / 1.4) * (1 - land * land * (3 - 2 * land));
      const rot = align * (heading - THETA0);

      const k = size / arrow.h;
      const cos = Math.cos(rot) * k;
      const sin = Math.sin(rot) * k;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = colour;
      ctx.setTransform(cos, sin, -sin, cos, x, y);
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
    filter: `drop-shadow(0 0 26px ${cfg.magenta}47)`,
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
