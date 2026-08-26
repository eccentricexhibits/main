// Shared scene builder for the Diagonal Arrow Transition.
// Single source of truth used by BOTH the web mock-up (embedded via build
// step) and the offline frame renderer. Pure math — no DOM, no timers.
//
// Element descriptor: { kind, z, ... , kf: [entry...] }
//   entry: { off (0..1), x?, y?, s?, o?, ease? }  ease: [x1,y1,x2,y2] or null (linear)
// Per WAAPI semantics each property interpolates over the entries that define
// it; the easing of the entry starting the interval applies.

var SceneBuilder = (function () {
  'use strict';

  var CW = 6878, CH = 1080;          // canvas size
  var T = 6000;                      // timeline length, ms
  var PEAK = 3000;                   // full-cover moment, ms
  var ANGLE = 67.93 * Math.PI / 180; // travel angle above horizontal
  var UX = Math.cos(ANGLE);          // 0.37575  (rightward)
  var UY = -Math.sin(ANGLE);         // -0.92672 (upward, screen coords)
  var AR = 422.98 / 600;             // arrow width / height

  var EASE_IN = [0.25, 0.7, 0.45, 0.98];   // decelerating arrival, never flat
  var EASE_OUT = [0.62, 0.03, 0.9, 0.34];  // accelerating exit

  // separate streams so patch-list edits never shift the effects layout
  function prng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  var LAYERS = [
    { sx: 150, sy: 160, hMin: 70,  hMax: 170, opMin: 0.10, opMax: 0.22, z: 1, glow: false, trails: 1 },
    { sx: 175, sy: 185, hMin: 150, hMax: 380, opMin: 0.16, opMax: 0.34, z: 2, glow: false, trails: 2 },
    { sx: 240, sy: 290, hMin: 300, hMax: 640, opMin: 0.42, opMax: 0.68, z: 3, glow: false, trails: 3 },
    { sx: 330, sy: 410, hMin: 480, hMax: 900, opMin: 0.78, opMax: 1.00, z: 4, glow: true,  trails: 3 }
  ];

  // coverage patches: dense fill over the spots the seeded tiling leaves
  // open at the PEAK frame (verified against the 6878x1080 render)
  var PATCHES = [
    [2630, 893, 2804, 1073], [5963, 262, 6074, 392], [4763, 279, 4830, 401],
    [3246, 370, 3343, 429], [6595, 596, 6723, 720], [1422, 384, 1456, 469],
    [1208, 1031, 1227, 1066], [3931, 389, 3935, 396], [0, 716, 20, 723],
    [630, 1077, 671, 1079]
  ];

  var STREAK_COLORS = ['#b659f0', '#48c0d9', '#7f8de5'];
  var SPARK_COLORS = ['#b659f0', '#48c0d9', '#dff6ff'];
  var DEG = -67.93;

  function build() {
    var rand = prng(20260826);   // arrows + patches (patches consume last)
    var randE = prng(555);       // streaks, sparks, ghosts
    var els = [];
    var arrowCount = 0;

    // spawn one flying arrow that sits exactly on (px, py) at PEAK
    function spawnArrow(px, py, h, op, z, glow, trails) {
      // sweep phase: bottom-left enters first, exits first
      var p = (px * UX + (CH - py) * -UY) / (CW * UX + 2 * CH * -UY);
      p = Math.min(1, Math.max(0, p));

      var delay = p * 1000 + rand() * 600;              // <= 1600
      var durIn = 800 + rand() * 600;                   // landed <= 3000
      var tLand = delay + durIn;
      var tExit = 3200 + p * 800 + rand() * 400;        // 3200..4400
      var durOut = Math.min(900 + rand() * 600, T - 100 - tExit);
      var tGone = tExit + durOut;                       // <= 5900

      // never stop: stream through the grid slot, exactly on it at PEAK
      var v = 0.16 + rand() * 0.18;                     // px per ms (160-340 px/s)
      var preX = px - UX * v * (PEAK - tLand),  preY = py - UY * v * (PEAK - tLand);
      var postX = px + UX * v * (tExit - PEAK), postY = py + UY * v * (tExit - PEAK);

      var dIn = (CH - preY) / -UY + 180 + rand() * 260;    // start fully below frame
      var dOut = (postY + h) / -UY + 180 + rand() * 260;   // end fully above frame

      els.push({
        kind: 'arrow', w: h * AR, h: h, op: op, z: z, glow: glow, trails: trails,
        kf: [
          { off: 0,         x: preX - UX * dIn, y: preY - UY * dIn, s: 0.82, ease: null },
          { off: delay / T, x: preX - UX * dIn, y: preY - UY * dIn, s: 0.82, ease: EASE_IN },
          { off: tLand / T, x: preX, y: preY, s: 1, ease: null },
          { off: tExit / T, x: postX, y: postY, s: 1, ease: EASE_OUT },
          { off: tGone / T, x: postX + UX * dOut, y: postY + UY * dOut, s: 1.06, ease: null },
          { off: 1,         x: postX + UX * dOut, y: postY + UY * dOut, s: 1.06, ease: null }
        ]
      });
      arrowCount++;
    }

    LAYERS.forEach(function (L) {
      var row = 0;
      for (var y = -L.sy - 500; y < CH + 80; y += L.sy, row++) {
        var xOffset = (row % 2) * L.sx / 2;  // brick-stagger alternate rows
        for (var x = -320 + xOffset; x < CW + 320; x += L.sx) {
          spawnArrow(
            x + (rand() * 2 - 1) * L.sx * 0.22,
            y + (rand() * 2 - 1) * L.sy * 0.22,
            L.hMin + rand() * (L.hMax - L.hMin),
            L.opMin + rand() * (L.opMax - L.opMin),
            L.z, L.glow, L.trails);
        }
      }
    });

    PATCHES.forEach(function (b) {
      var margin = 60;
      for (var y = b[1] - margin; y <= b[3] + margin; y += 70) {
        for (var x = b[0] - margin; x <= b[2] + margin; x += 70) {
          // solid mid-body of the arrow centered over the gap pixel
          spawnArrow(x - 85, y - 150, 240 + rand() * 80, 0.32 + rand() * 0.16, 2, false, 1);
        }
      }
    });

    // straight run along the slope over [ts, te]; linear motion, faded ends
    function runKf(Px, Py, d1, d2, ts, te, opPeak, flicker) {
      var span = d1 + d2;
      var w = te - ts;
      var fade = w * 0.18;
      function at(f) { var s = -d1 + span * f; return { x: Px + UX * s, y: Py + UY * s }; }
      var p0 = at(0), p1 = at(1);
      var kf = [
        { off: 0,               x: p0.x, y: p0.y, o: 0, ease: null },
        { off: ts / T,          x: p0.x, y: p0.y, o: 0, ease: null },
        { off: (ts + fade) / T, o: opPeak, ease: null }
      ];
      if (flicker) {
        kf.push({ off: (ts + w * 0.38) / T, o: opPeak * 0.3, ease: null });
        kf.push({ off: (ts + w * 0.58) / T, o: opPeak, ease: null });
        kf.push({ off: (ts + w * 0.78) / T, o: opPeak * 0.25, ease: null });
      }
      kf.push({ off: (te - fade) / T, o: flicker ? opPeak * 0.8 : opPeak, ease: null });
      kf.push({ off: te / T, x: p1.x, y: p1.y, o: 0, ease: null });
      kf.push({ off: 1, x: p1.x, y: p1.y, o: 0, ease: null });
      return kf;
    }

    // gradient speed streaks along the slope
    for (var i = 0; i < 120; i++) {
      var front = i >= 75;                          // last 45 fly over the arrows
      var len = 250 + randE() * 650;
      var th = 2 + randE() * 5;
      var sOp = front ? 0.1 + randE() * 0.2 : 0.14 + randE() * 0.26;
      var col = STREAK_COLORS[Math.floor(randE() * 3)];
      var Px = -300 + randE() * (CW + 500);
      var Py = randE() * CH;
      var ts = randE() * 3400;
      var te = Math.min(ts + 1500 + randE() * 1600, T - 100);
      els.push({
        kind: 'streak', len: len, th: th, col: col, rot: DEG, z: front ? 5 : 2,
        kf: runKf(Px, Py, (CH - Py) / -UY + 300, (Py + 100) / -UY + 300, ts, te, sOp, false)
      });
    }

    // sparkle particles: glowing motes with flicker
    for (var i = 0; i < 150; i++) {
      var sz = 3 + randE() * 7;
      var col = SPARK_COLORS[Math.floor(randE() * 3)];
      var Px = -200 + randE() * (CW + 400);
      var Py = randE() * CH;
      var ts = randE() * 3600;
      var te = Math.min(ts + 1300 + randE() * 1800, T - 100);
      els.push({
        kind: 'spark', sz: sz, col: col, z: 5,
        kf: runKf(Px, Py, (CH - Py) / -UY + 200, (Py + 60) / -UY + 200, ts, te,
                  0.35 + randE() * 0.55, true)
      });
    }

    // giant blurred ghost arrows: fast foreground parallax
    for (var i = 0; i < 10; i++) {
      var h = 1100 + randE() * 500;
      var op = 0.05 + randE() * 0.07;
      var Px = -600 + randE() * (CW + 400);
      var Py = randE() * CH - h / 2;
      var ts = 300 + randE() * 3000;
      var te = Math.min(ts + 1400 + randE() * 1200, T - 100);
      els.push({
        kind: 'ghost', w: h * AR, h: h, z: 6,
        kf: runKf(Px, Py, (CH - Py) / -UY + 400, (Py + h) / -UY + 400, ts, te, op, false)
      });
      arrowCount++;
    }

    // light sweep crossing the frame at the cover moment
    var cx = CW / 2 - 4500, cy = CH / 2 - 300;  // band top-left, pre-rotation
    els.push({
      kind: 'sweep', bw: 9000, bh: 600, rot: 22.07, z: 7,
      kf: [
        { off: 0,        x: cx + UX * -1400, y: cy + UY * -1400, o: 0, ease: null },
        { off: 2500 / T, x: cx + UX * -1400, y: cy + UY * -1400, o: 0, ease: null },
        { off: 3000 / T, x: cx, y: cy, o: 0.9, ease: null },
        { off: 3600 / T, x: cx + UX * 1400, y: cy + UY * 1400, o: 0, ease: null },
        { off: 1,        x: cx + UX * 1400, y: cy + UY * 1400, o: 0, ease: null }
      ]
    });

    return { els: els, arrowCount: arrowCount, CW: CW, CH: CH, T: T, PEAK: PEAK, UX: UX, UY: UY };
  }

  // cubic-bezier easing (CSS timing function semantics)
  function bezier(e, u) {
    if (!e) return u;
    if (u <= 0) return 0;
    if (u >= 1) return 1;
    var x1 = e[0], y1 = e[1], x2 = e[2], y2 = e[3];
    function sample(t, a, b) { // 1D cubic bezier with P0=0, P3=1
      var omt = 1 - t;
      return 3 * omt * omt * t * a + 3 * omt * t * t * b + t * t * t;
    }
    // solve sample(t, x1, x2) = u by bisection (robust, plenty fast here)
    var lo = 0, hi = 1, t = u;
    for (var i = 0; i < 40; i++) {
      var x = sample(t, x1, x2);
      if (Math.abs(x - u) < 1e-6) break;
      if (x < u) lo = t; else hi = t;
      t = (lo + hi) / 2;
    }
    return sample(t, y1, y2);
  }

  // sample one property over the entries defining it (WAAPI per-property rules)
  function sampleProp(kf, prop, tf) {
    var defs = [];
    for (var i = 0; i < kf.length; i++) if (kf[i][prop] !== undefined) defs.push(kf[i]);
    if (!defs.length) return undefined;
    if (tf <= defs[0].off) return defs[0][prop];
    var last = defs[defs.length - 1];
    if (tf >= last.off) return last[prop];
    for (var i = 0; i < defs.length - 1; i++) {
      var a = defs[i], b = defs[i + 1];
      if (tf >= a.off && tf <= b.off) {
        if (b.off === a.off) return b[prop];
        var u = bezier(a.ease, (tf - a.off) / (b.off - a.off));
        return a[prop] + (b[prop] - a[prop]) * u;
      }
    }
    return last[prop];
  }

  var api = { build: build, sampleProp: sampleProp, T: T };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  return api;
})();
