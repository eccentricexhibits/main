/*
 * Transition — the once-per-loop event where the ambient field converges and
 * resolves into the Vector logo on the Domino screen.
 *
 * Sequence
 * --------
 *   sweep    the ambient layers fade down; arrows drop in from off the top and
 *            bottom edges, round a corner into a horizontal lane, and cruise
 *            toward the centre nose-first, striking light trails as they go.
 *   gather   each arrow swoops out of its lane onto a point sampled from the
 *            Vector mark, straightening up as it lands. Arrows with no point to
 *            fill dissolve short of the shape.
 *   reveal   the crisp mark fades in over the arrows; the arrows fade out.
 *   resolve  the mark eases into its slot in the full bilingual lockup as the
 *            wordmark fades in beside it.
 *   hold     the finished logo sits at 70% of the Domino screen's width.
 *   release  the logo fades out and the ambient field comes back up.
 *
 * Every arrow in the event is white or magenta — the logo's own colours — from
 * the moment it enters.
 *
 * There is no gate. An arrow bends out of its lane when it comes within its own
 * randomised distance of its destination, so no two break at the same x; a
 * single shared turn-in point draws a vertical column of arrows down the wall.
 * Corner radius, swoop distance, cruise length, lane wander, speed and the shape
 * of the acceleration are all drawn per arrow, which is what stops the swarm
 * moving as one rigid block.
 *
 * Everything here is a pure function of t. No integration, no accumulated state:
 * draw(t) at any time gives the same pixels, which is what makes the whole loop
 * seekable and therefore exportable frame by frame. It is also what makes the
 * light trails cheap — an echo is the same path function evaluated a little way
 * back along the journey.
 */

const TRANSITION = {
  at: 240, // seconds into the loop
  sweep: 7,
  gather: 4,
  reveal: 2.5,
  resolve: 2,
  hold: 2, // the logo alone, before the speaker cards wipe in
  release: 6,

  /*
   * After the logo has settled, a single magenta arrow runs the length of each
   * of the north and south walls, wiping in a speaker card behind it, then fades
   * as it comes in toward the centre. Cards sit on the wall panels only — never
   * across the cube band below them.
   */
  speaker: {
    wipe: 3.2, // how long the arrow takes to cross its wall
    hold: 6, // how long the cards stay up afterwards
    fill: 0.5, // card width, as a fraction of the wall panel's width
    arrow: 300, // height of the wiping arrow, px
    fadeFrom: 0.72, // point in the crossing where the arrow starts to go
    name: 'Glenda Crisp',
    title: ['President &amp; CEO,', 'Vector Institute'],
  },

  extras: 130, // arrows beyond those needed for the mark, which dissolve on arrival
  // Arrows drop in from off the top and bottom edges, round a corner into a lane,
  // and cruise from there. Lanes are kept on the side the arrow entered from, so
  // nothing has to cross the full height of the wall to reach its cruise line.
  entryMargin: 340, // how far off the edge an arrow starts
  lane: [80, 1000], // cruise heights; each arrow drops in from whichever edge is nearer
  corner: [110, 430], // radius of the turn from the entry into the cruise
  cruise: [900, 3500], // horizontal run before the swoop begins, capped by the wall
  laneDrift: [8, 46], // how far an arrow wanders off its lane while cruising
  baseSpeed: 660, // px/s before the per-arrow multiplier
  speedVar: [0.72, 1.3],
  pace: [0.72, 1.45], // acceleration shape: <1 leaves fast, >1 rushes the finish
  stagger: 2.4, // spread of launch times, seconds
  trail: { count: 4, gap: [26, 54], alpha: 0.19 },
  glow: 0.4, // blur radius as a fraction of the arrow's height
  // Arrows leave the wall at roughly ambient scale and shrink as they gather, so
  // the field reads as turning and condensing rather than being swapped out for
  // a different, much smaller set of arrows.
  arrowStart: [34, 120],
  arrowEnd: [11, 17],
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

/* ------------------------------------------------------------------- timing */

function phases(cfg) {
  const t = { start: cfg.at };
  t.sweepEnd = t.start + cfg.sweep;
  t.gatherEnd = t.sweepEnd + cfg.gather;
  t.revealEnd = t.gatherEnd + cfg.reveal;
  t.resolveEnd = t.revealEnd + cfg.resolve;
  t.holdEnd = t.resolveEnd + cfg.hold;
  t.wipeEnd = t.holdEnd + cfg.speaker.wipe;
  t.speakerEnd = t.wipeEnd + cfg.speaker.hold;
  t.end = t.speakerEnd + cfg.release;
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

function buildParticles(cfg, venue, markPoints, rand) {
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

  // South-side arrows take the left of the mark and north-side the right, so
  // the two streams interleave in the middle instead of reaching across.
  const half = Math.round(targets.length / 2);
  const jobs = targets.map((target, i) => ({
    target,
    // Split by side so the streams do not reach across each other, but swap a
    // quarter of them over. A strict split sends every magenta arrow — they are
    // all on the mark's right — down one stream, and the two sides read as two
    // differently coloured flocks.
    dir: (i < half ? 1 : -1) * (rand() < 0.25 ? -1 : 1),
  }));
  // Extras aim at a scatter around the mark and dissolve before they land. They
  // carry the logo's colours in the same proportion as the mark itself, so the
  // whole swarm is white and magenta with nothing left over from the ambient palette.
  const magentaShare = targets.filter((p) => p.magenta).length / targets.length;
  for (let i = 0; i < cfg.extras; i++) {
    const angle = rand() * Math.PI * 2;
    const r = mix(140, 460, rand());
    jobs.push({
      dir: i % 2 ? 1 : -1,
      target: {
        x: geo.formed.x + geo.formed.w / 2 + Math.cos(angle) * r,
        y: geo.formed.y + geo.formed.h / 2 + Math.sin(angle) * r * 0.6,
        magenta: rand() < magentaShare,
      },
      ghost: true,
    });
  }

  /*
   * Each journey is three moves: drop in from off the top or bottom edge, round
   * a corner into a horizontal lane, cruise, then swoop out of the lane onto the
   * target. Nothing about it is shared between arrows — corner radius, swoop
   * distance, cruise length, speed and the shape of the acceleration are all
   * drawn per arrow, which is what stops the swarm moving as one rigid block.
   */
  const particles = jobs.map((job) => {
    const laneY = mix(cfg.lane[0], cfg.lane[1], rand());
    const fromTop = laneY < venue.height / 2;
    const startY = fromTop ? -cfg.entryMargin : venue.height + cfg.entryMargin;

    // Reach as far out as the wall allows, so arrows enter across its whole
    // width rather than bunching around the middle third.
    const room = (job.dir > 0 ? job.target.x : venue.width - job.target.x) - 60;
    const cruise = Math.min(mix(cfg.cruise[0], cfg.cruise[1], Math.pow(rand(), 0.72)), room);
    const startX = job.target.x - job.dir * cruise;
    const entryLen = Math.abs(laneY - startY);
    const corner = mix(cfg.corner[0], cfg.corner[1], rand());
    // The corner overlaps the two legs, so it is not travelled twice.
    const total = entryLen + cruise - corner;

    const launch = t.start + rand() * cfg.stagger;
    let dur = total / (cfg.baseSpeed * mix(cfg.speedVar[0], cfg.speedVar[1], rand()));
    dur = Math.min(dur, t.gatherEnd - launch);

    return {
      startX,
      startY,
      laneY,
      entryLen,
      cruise,
      corner,
      total,
      target: job.target,
      ghost: !!job.ghost,
      dir: job.dir,
      launch,
      dur: Math.max(0.5, dur),
      // <1 leaves fast and eases in; >1 creeps out and rushes the last stretch.
      pace: mix(cfg.pace[0], cfg.pace[1], rand()),
      swoop: mix(cfg.swoop[0], cfg.swoop[1], rand()),
      drift: mix(cfg.laneDrift[0], cfg.laneDrift[1], rand()),
      driftWave: mix(420, 1100, rand()),
      driftPhase: rand() * Math.PI * 2,
      trailGap: mix(cfg.trail.gap[0], cfg.trail.gap[1], rand()),
      size0: mix(cfg.arrowStart[0], cfg.arrowStart[1], Math.pow(rand(), 1.7)),
      size1: mix(cfg.arrowEnd[0], cfg.arrowEnd[1], rand()),
    };
  });

  return { particles, geo, times: t };
}

/**
 * Position along a journey after travelling `d`. Returns the swoop factor too,
 * since size and colour key off it. Kept as one closed-form function so the
 * heading can be taken as a finite difference rather than derived by hand for
 * each leg — and so the whole thing stays a pure function of t.
 */
function positionAt(p, d) {
  if (d < p.entryLen) {
    // Dropping in. Sideways drift builds over the leg so the turn into the lane
    // is a curve rather than a corner.
    const u = clamp01(d / p.entryLen);
    return {
      x: p.startX + p.dir * p.corner * u * u,
      y: mix(p.startY, p.laneY, u * u * (3 - 2 * u)),
      s: 0,
    };
  }
  const along = p.corner + (d - p.entryLen);
  const x = p.startX + p.dir * Math.min(along, p.cruise);
  const remain = Math.abs(p.target.x - x);
  const s = clamp01((p.swoop - remain) / p.swoop);
  // A long, shallow wander down the lane. Ruler-straight cruising is what makes
  // a swarm look mechanical; this also keeps the heading alive, since rotation
  // is read off the path.
  const settled = clamp01((along - p.corner) / 320) * (1 - s);
  const wander = p.drift * Math.sin(p.driftPhase + along / p.driftWave) * settled;
  return { x, y: mix(p.laneY + wander, p.target.y, s * s * (3 - 2 * s)), s };
}

/* ------------------------------------------------------------------ drawing */

function makeRenderer(canvas, cfg, venue, markPoints, arrow, rand) {
  const ctx = canvas.getContext('2d');
  const { particles, geo, times } = buildParticles(cfg, venue, markPoints, rand);
  const trailCount = cfg.trail.count;

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
      if (t < p.launch) continue;

      // Per-arrow acceleration shape, so no two cover their run the same way.
      const u = clamp01((t - p.launch) / p.dur);
      const d = p.total * Math.pow(u, p.pace);
      const here = positionAt(p, d);
      const s = here.s;

      const size = mix(p.size0, p.size1, s * s * (3 - 2 * s));
      let alpha = span(t, p.launch, p.launch + 0.35) * (1 - packDown);
      // Every arrow in the event carries the logo's colours; the ones with no
      // point to fill dissolve rather than changing colour.
      const colour = p.target.magenta ? MAGENTA : WHITE;
      if (p.ghost) alpha *= 1 - clamp01((s - 0.3) / 0.45);
      if (alpha <= 0.004) continue;

      const k = size / arrow.h;

      /*
       * Fly along the path — nose down on the way in, along the lane on the
       * cruise, banking through the swoop — then straighten up on arrival so the
       * mark is built out of arrows in their proper orientation. Heading is a
       * finite difference along the same closed-form path.
       */
      const land = clamp01((s - 0.74) / 0.26);
      const align = 1 - land * land * (3 - 2 * land);
      const headingAt = (at, from) => {
        if (align <= 0.001) return 0;
        const dx = at.x - from.x;
        const dy = at.y - from.y;
        return dx || dy ? align * (Math.atan2(dy, dx) - THETA0) : 0;
      };
      const rot = headingAt(positionAt(p, Math.min(p.total, d + 6)), here);

      const stamp = (px, py, scale, angle, a) => {
        const sk = k * scale;
        const cos = Math.cos(angle) * sk;
        const sin = Math.sin(angle) * sk;
        ctx.globalAlpha = a;
        ctx.setTransform(cos, sin, -sin, cos, px, py);
        ctx.fill(path);
      };

      ctx.fillStyle = colour;

      /*
       * A light trail struck along the arrow's own path: because position is a
       * closed-form function of distance travelled, an echo is just the same
       * function evaluated a little way back. It fades out as the arrow settles,
       * so the finished mark is clean rather than smeared.
       */
      const speedNow = Math.max(0, d - p.total * Math.pow(clamp01(u - 0.02), p.pace));
      const heat = clamp01(speedNow / 14) * (1 - s) * alpha;
      if (heat > 0.01) {
        for (let i = trailCount; i >= 1; i--) {
          const back = d - i * p.trailGap;
          if (back <= 0) continue;
          const echo = positionAt(p, back);
          const fade = (1 - i / (trailCount + 1)) * cfg.trail.alpha * heat;
          if (fade <= 0.004) continue;
          stamp(echo.x, echo.y, 1 - 0.115 * i, headingAt(here, echo), fade);
        }
      }

      /*
       * A real blur for the halo, not a scaled copy of the arrow — at this size
       * an enlarged copy reads as a second, greyer arrow sitting behind the
       * first rather than as light coming off it.
       */
      ctx.shadowColor = colour;
      ctx.shadowBlur = size * cfg.glow;
      stamp(here.x, here.y, 1, rot, alpha);
      ctx.shadowBlur = 0;
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
  const { config, venue, markPoints, arrow, logoSvg, portrait, duration } = opts;
  const cfg = Object.assign({}, TRANSITION, config || {});
  const doc = stage.ownerDocument;
  const t = phases(cfg);

  if (t.end >= duration) {
    throw new Error(`transition ends at ${t.end}s but the loop is only ${duration}s`);
  }

  const rand = opts.rng;

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

  const renderer = makeRenderer(canvas, cfg, venue, markPoints, arrow, rand);
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
      `${pct(t.resolveEnd)}%,${pct(t.speakerEnd)}%{opacity:1;transform:none}` +
      `${pct(t.end)}%,100%{opacity:0;transform:none}}`,
    '@keyframes af-wordmark-in{' +
      `0%,${pct(t.revealEnd)}%{opacity:0}` +
      `${pct(t.resolveEnd)}%,${pct(t.speakerEnd)}%{opacity:${keepsWordmark ? 1 : 0}}` +
      `${pct(t.end)}%,100%{opacity:0}}`,
    // The ambient field steps back for the event and returns afterwards.
    '@keyframes af-ambient-out{' +
      `0%,${pct(t.start)}%{opacity:1}` +
      `${pct(t.start + cfg.sweep * 0.55)}%,${pct(t.speakerEnd)}%{opacity:0}` +
      `${pct(t.end)}%,100%{opacity:1}}`,
  ];

  const cards = mountSpeakers(stage, cfg, venue, arrow, portrait, t, pct, rules);

  const style = doc.createElement('style');
  style.textContent = rules.join('');
  doc.head.appendChild(style);

  holder.style.animation = `af-logo-in ${duration}s linear infinite`;
  if (wordmark) wordmark.style.animation = `af-wordmark-in ${duration}s linear infinite`;
  ambient.style.animation = `af-ambient-out ${duration}s linear infinite`;
  cards.forEach((c) => c.start(duration));

  return {
    draw: renderer.draw,
    times: t,
    geo,
    particles: renderer.count,
    markPoints: markPoints.points.length,
    speakers: cards.map((c) => c.rect),
  };
}

/* ---------------------------------------------------------------- speakers */

/**
 * A magenta arrow crosses each of the north and south wall panels, wiping in a
 * speaker card behind it, then fades as it comes in toward the centre.
 *
 * The card and the arrow are driven off the same normalised crossing, so the
 * reveal edge is always exactly where the arrow is: the clip-path keyframes sit
 * at the fractions of the crossing where the arrow's tip meets the card's near
 * and far edges. Both are CSS animations on the loop's own timeline, which keeps
 * them seekable alongside everything else.
 *
 * Cards are confined to the wall panels, above the cube band — nothing of the
 * portrait or the type falls onto the cube faces or the draped returns.
 */
function mountSpeakers(stage, cfg, venue, arrow, portrait, t, pct, rules) {
  const doc = stage.ownerDocument;
  const spec = cfg.speaker;
  const band = venue.cubeTop; // wall panels run from y 0 down to the cube band
  const walls = [
    { id: 'south', x: venue.panels.southWall.x, w: venue.panels.southWall.w, dir: 1 },
    { id: 'north', x: venue.panels.northWall.x, w: venue.panels.northWall.w, dir: -1 },
  ];

  const portraitH = Math.round(band * 0.5);
  rules.push(
    '.af-speaker{position:absolute;pointer-events:none;display:flex;align-items:center;' +
      "justify-content:center;gap:56px;font-family:'Karbon',system-ui,sans-serif;font-weight:600}" +
      `.af-speaker img{height:${portraitH}px;width:auto;object-fit:cover;display:block;` +
      'border-radius:4px}' +
      '.af-speaker-name{color:#fff;font-size:130px;line-height:1.04;letter-spacing:-0.015em}' +
      `.af-speaker-title{color:${cfg.magenta};font-size:90px;line-height:1.14;margin-top:20px}` +
      '.af-wipe{position:absolute;pointer-events:none}'
  );

  return walls.map((wall) => {
    /*
     * The card covers its whole wall panel and centres its content, so the wipe
     * is simply the arrow's progress across that panel — no need to work out
     * where the arrow meets the artwork. Confining it to the panel is also what
     * keeps the portrait and type off the cube band and the draped returns.
     */
    const rect = { x: wall.x, y: 0, w: wall.w, h: band };

    const card = doc.createElement('div');
    card.className = `af-speaker af-speaker-${wall.id}`;
    Object.assign(card.style, {
      left: `${rect.x}px`,
      top: `${rect.y}px`,
      width: `${rect.w}px`,
      height: `${rect.h}px`,
    });
    card.innerHTML =
      `<img src="${portrait}" alt="">` +
      '<div><div class="af-speaker-name"></div>' +
      `<div class="af-speaker-title">${spec.title.join('<br>')}</div></div>`;
    card.querySelector('.af-speaker-name').textContent = spec.name;
    stage.appendChild(card);

    // The arrow's run: on from off the outer edge, off toward the centre.
    const runFrom = wall.dir > 0 ? wall.x - spec.arrow : wall.x + wall.w + spec.arrow;
    const runTo = wall.dir > 0 ? wall.x + wall.w + spec.arrow : wall.x - spec.arrow;
    const at = (x) => clamp01((x - runFrom) / (runTo - runFrom));
    const hitNear = at(wall.dir > 0 ? rect.x : rect.x + rect.w);
    const hitFar = at(wall.dir > 0 ? rect.x + rect.w : rect.x);

    const wipe = doc.createElement('div');
    wipe.className = 'af-wipe';
    const aw = spec.arrow * (arrow.w / arrow.h);
    Object.assign(wipe.style, {
      left: `${-aw / 2}px`,
      top: `${Math.round(band / 2 - spec.arrow / 2)}px`,
      width: `${aw}px`,
      height: `${spec.arrow}px`,
      opacity: '0',
      filter: `drop-shadow(0 0 34px ${cfg.magenta}80)`,
    });
    wipe.innerHTML =
      `<svg viewBox="0 0 ${arrow.w} ${arrow.h}" width="100%" height="100%">` +
      `<polygon points="${arrow.points}" fill="${cfg.magenta}"/></svg>`;
    stage.appendChild(wipe);

    // Between the crossing and the card's own fraction of it, keyframe times.
    const cross = (u) => t.holdEnd + (t.wipeEnd - t.holdEnd) * u;
    const key = wall.id;

    rules.push(
      `@keyframes af-wipe-${key}{` +
        `0%,${pct(t.holdEnd)}%{opacity:0;transform:translateX(${runFrom}px)}` +
        `${pct(cross(0.06))}%{opacity:1}` +
        `${pct(cross(spec.fadeFrom))}%{opacity:1}` +
        `${pct(t.wipeEnd)}%,100%{opacity:0;transform:translateX(${runTo}px)}}`,
      `@keyframes af-card-${key}{` +
        `0%,${pct(cross(hitNear))}%{opacity:1;clip-path:inset(0 ${wall.dir > 0 ? '100% 0 0' : '0 0 100%'})}` +
        `${pct(cross(hitFar))}%,${pct(t.speakerEnd)}%{opacity:1;clip-path:inset(0 0 0 0)}` +
        `${pct(t.end)}%,100%{opacity:0;clip-path:inset(0 0 0 0)}}`
    );

    return {
      rect,
      start(duration) {
        wipe.style.animation = `af-wipe-${key} ${duration}s linear infinite`;
        card.style.animation = `af-card-${key} ${duration}s linear infinite`;
      },
    };
  });
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { TRANSITION, phases, layout, mountTransition };
}
