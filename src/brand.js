// Vector Institute — brand constants, venue geometry, and official shape geometry.
// Values taken from BrandGuidelines_QuickReference_10_31_25.pdf and the official SVGs.

// ---------------------------------------------------------------------------
// Colour
// ---------------------------------------------------------------------------

// Primary palette (p6 of the guidelines)
export const MAGENTA = '#EB088A';
export const BLACK = '#000000';
export const GREY = '#E9E8E8';

// Secondary palette (p6). Violet sits between magenta and cobalt on the
// primary gradient, so it doubles as the transition hue.
export const VIOLET = '#8A25C9';
export const COBALT = '#313CFF';
export const TURQUOISE = '#48C0D9';
export const TANGERINE = '#FF9E00';
export const LIME = '#CFF933';

// The primary gradient is magenta -> cobalt (p7). The reference art renders it
// as an emissive field, so each brand stop carries a brighter "glow" partner
// that the additive bloom pass drives toward. Sampling the supplied reference
// frames gives the glow values below.
export const GRADIENT = [
  { t: 0.0, base: [235, 8, 138], glow: [253, 9, 124] }, // magenta
  { t: 0.42, base: [235, 8, 138], glow: [254, 6, 135] }, // magenta hold
  { t: 0.5, base: [138, 37, 201], glow: [164, 40, 242] }, // violet transition
  { t: 0.58, base: [49, 60, 255], glow: [24, 58, 251] }, // cobalt
  { t: 1.0, base: [49, 60, 255], glow: [0, 112, 255] }, // cobalt hold
];

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

// Sample the primary gradient at normalised x (0 = far south wall, 1 = far
// north wall). `emissive` blends toward the glow variant for lit elements.
export function gradientAt(u, emissive = 0) {
  const t = clamp01(u);
  let a = GRADIENT[0];
  let b = GRADIENT[GRADIENT.length - 1];
  for (let i = 0; i < GRADIENT.length - 1; i++) {
    if (t >= GRADIENT[i].t && t <= GRADIENT[i + 1].t) {
      a = GRADIENT[i];
      b = GRADIENT[i + 1];
      break;
    }
  }
  const span = b.t - a.t;
  const k = span <= 0 ? 0 : (t - a.t) / span;
  const out = [0, 0, 0];
  for (let i = 0; i < 3; i++) {
    const base = a.base[i] + (b.base[i] - a.base[i]) * k;
    const glow = a.glow[i] + (b.glow[i] - a.glow[i]) * k;
    out[i] = Math.round(base + (glow - base) * clamp01(emissive));
  }
  return out;
}

export function rgba([r, g, b], alpha) {
  return `rgba(${r},${g},${b},${alpha.toFixed(4)})`;
}

// ---------------------------------------------------------------------------
// Venue geometry — DX Trading Floor immersive template, 6878 x 1080
// Region bounds measured directly from the supplied template PNG.
// ---------------------------------------------------------------------------

export const CANVAS_W = 6878;
export const CANVAS_H = 1080;

export const VENUE = {
  width: CANVAS_W,
  height: CANVAS_H,

  // The three projected wall surfaces, in canvas order.
  walls: [
    { id: 'south', label: 'South Wall', x0: 0, x1: 2239 },
    { id: 'west', label: 'West Wall', x0: 2596, x1: 4277 },
    { id: 'north', label: 'North Wall', x0: 4634, x1: 6878 },
  ],

  // Physical corner returns between the walls. Content crossing these is
  // wrapping around a real corner, so nothing load-bearing should land here.
  corners: [
    { label: 'West-faced corner', x0: 2239, x1: 2501 },
    { label: 'South-faced corner', x0: 2501, x1: 2596 },
    { label: 'South-faced corner', x0: 4277, x1: 4371 },
    { label: 'West-faced corner', x0: 4371, x1: 4634 },
  ],

  // Horizontal break where the side walls meet the physical cube structure.
  cubeTop: 674,

  // Below this line the template is marked "background graphics only, no text".
  noTextBelow: 538,

  // Speaker grills — physical perforated panels; artwork behind them reads as
  // texture at best, so hero elements should not be centred here.
  grills: [
    { label: 'South Grill', x0: 430, x1: 1376, y0: 358, y1: 488 },
    { label: 'North Grill', x0: 5481, x1: 6426, y0: 358, y1: 488 },
  ],

  // Draped fabric flanking each cube — soft, non-flat surfaces.
  drapes: [
    { label: 'A', x0: 0, x1: 301, y0: 674, y1: 1080 },
    { label: 'B', x0: 2031, x1: 2239, y0: 674, y1: 1080 },
    { label: 'C', x0: 4634, x1: 4845, y0: 674, y1: 1080 },
    { label: 'D', x0: 6575, x1: 6878, y0: 674, y1: 1080 },
  ],

  // Central LED/projection screen on the west wall.
  domino: { x0: 2633, x1: 4243, y0: 0, y1: 628 },
};

// Centre of the west wall — the viewer's natural eye-line in the room.
export const WEST_CENTRE = (VENUE.walls[1].x0 + VENUE.walls[1].x1) / 2;

// ---------------------------------------------------------------------------
// Official shape geometry (verbatim from the supplied SVGs)
// ---------------------------------------------------------------------------

// "Vector Arrow" — Vector Official - Arrow Regular.svg, viewBox 0 0 422.98 600
export const ARROW_REGULAR = {
  w: 422.98,
  h: 600,
  d:
    'M308.51,0 L46.97,114.42 L0,224.04 L208.02,137.79 L68.91,480.94 L67.58,484.26 ' +
    'L113.86,600 L286.24,169.06 L376.67,375.07 L422.98,267.08 Z',
};

// "Vector Arrow (extended)" — Vector Official - Arrow Long.svg,
// viewBox 0 0 537.23 1080
export const ARROW_LONG = {
  w: 537.23,
  h: 1080,
  d:
    'M463.33,0l-168.9,73.89-29.33,69.19,133.39-53.47L0,1079.82l62.23.18L448.81,109.21' +
    'l59.1,131.81,29.33-69.78L463.33,0Z',
};

// Logo icon (the "V" + arrow), lifted from Official Vector Logo.svg. The
// guidelines allow the icon to stand alone without the wordmark, which also
// keeps us inside the template's "background graphics only, no text" rule.
// Source viewBox is 3000 x 2700; the icon occupies x 722..2369, y 48..1893.
export const LOGO_ICON = {
  x0: 721.58,
  y0: 48.16,
  x1: 2369.3,
  y1: 1893.09,
  parts: [
    {
      fill: '#ffffff',
      d:
        'M1649.64,1408.87 L1232.78,314.36 L1440.01,314.36 L1440.01,177.41 ' +
        'L721.58,177.41 L721.58,314.36 L929.23,314.36 L1472.62,1737.49 ' +
        'L1538.97,1893.09 L1685.91,1499.05 Z',
    },
    {
      fill: '#ed2c8a',
      d:
        'M2194.88,48.16 L1796.37,222.5 L1724.81,389.53 L2041.77,258.1 ' +
        'L1829.8,780.97 L1827.78,786.02 L1898.29,962.38 L2160.95,305.76 ' +
        'L2298.75,619.65 L2369.3,455.1 Z',
    },
  ],
};

// The plus mark from Vector Official Plus Symbol.svg is a 72.85 square with a
// 14.99 bar. Normalised to a unit cell centred on the origin.
export const PLUS_BAR_RATIO = 14.99 / 72.85;

// The pixel mark from Vector Official Pixel Symbol.svg is a plain 74.97 square
// on a 74.97 grid pitch, i.e. a unit cell with no gap.
export const PIXEL_CELL = 1.0;

// The official cluster patterns, taken verbatim from the supplied symbol
// artwork. Coordinates are mark centres, normalised so the cluster is one unit
// wide with its origin at the cluster centre; MARK is the size of a single
// mark in the same units. Drawing these as a unit keeps the real pattern
// recognisable rather than only its individual marks.
export const PLUS_CLUSTER = [
  [-0.22296, -0.32210], [-0.46627, -0.26571], [0.46627, -0.21670],
  [-0.34143, -0.19826], [-0.00794, -0.15883], [0.23622, -0.10344],
  [-0.31760, -0.03868], [0.11288, -0.03599], [-0.17161, 0.03146],
  [-0.28572, 0.11805], [-0.05794, 0.19658], [0.05583, 0.28149],
  [-0.15158, 0.32210],
];
export const PLUS_CLUSTER_MARK = 0.06745;

export const PIXEL_CLUSTER = [
  [-0.24316, -0.38434], [-0.17375, -0.38434], [0.17333, -0.38434],
  [-0.46529, -0.36141], [-0.10434, -0.31492], [0.10391, -0.31492],
  [0.24275, -0.31492], [-0.39588, -0.29200], [-0.03492, -0.24550],
  [0.17333, -0.24550], [0.24275, -0.24550], [-0.46529, -0.22258],
  [-0.03492, -0.17609], [0.03450, -0.17609], [0.17333, -0.17609],
  [-0.39588, -0.15316], [-0.03492, -0.10667], [0.10391, -0.10667],
  [0.32646, -0.10158], [0.39587, -0.03216], [0.03542, 0.03725],
  [0.17425, 0.03725], [0.24367, 0.03725], [0.46529, 0.03725],
  [0.10484, 0.10667], [0.17425, 0.10667], [0.31309, 0.10667],
  [-0.03400, 0.17609], [0.17425, 0.17609], [0.24367, 0.17609],
  [0.03542, 0.24550], [0.31309, 0.24550], [-0.03400, 0.31492],
  [0.03542, 0.38434],
];
export const PIXEL_CLUSTER_MARK = 0.06942;
