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

// The primary gradient is magenta -> cobalt (p7). It is NOT used in the room:
// magenta is the summit's wayfinding colour — signs and directional arrows —
// and keeping it out of the immersive piece is what stops the two competing.
// Kept here because the same palette module serves the print pieces.
export const GRADIENT_WAYFINDING = [
  { t: 0.0, base: [235, 8, 138], glow: [253, 9, 124] }, // magenta
  { t: 0.42, base: [235, 8, 138], glow: [254, 6, 135] }, // magenta hold
  { t: 0.5, base: [138, 37, 201], glow: [164, 40, 242] }, // violet transition
  { t: 0.58, base: [49, 60, 255], glow: [24, 58, 251] }, // cobalt
  { t: 1.0, base: [49, 60, 255], glow: [0, 112, 255] }, // cobalt hold
];

// The room runs on the secondary violet -> turquoise pairing (p7/p12). Violet
// enters on the south wall, turquoise on the north, and the two meet across the
// west wall — the same place the field's perspective funnel converges, so the
// two audiences the palette stands for literally come together in the middle of
// the room. Each stop carries a brighter "glow" partner that the additive bloom
// drives toward, matched to the supplied reference frames.
//
// Note the guidelines assign these the other way round to the brief: p13 has
// Industry #8A25C9 (violet) and Academic Institutions #48C0D9 (turquoise). The
// pairing and its direction across the room are unaffected — only which end the
// caption names.
// The violet glow is deliberately kept on the blue side of the hue. Brightening
// violet along the obvious path takes it toward pink, and once the additive
// bloom stacks a few marks the south wall reads magenta — which is precisely
// the colour that is supposed to stay outside the room.
export const GRADIENT_ENV = [
  { t: 0.0, base: [138, 37, 201], glow: [124, 64, 252] }, // violet
  { t: 0.3, base: [138, 37, 201], glow: [124, 64, 252] }, // violet hold
  { t: 0.5, base: [105, 114, 209], glow: [128, 150, 255] }, // convergence
  { t: 0.7, base: [72, 192, 217], glow: [96, 226, 255] }, // turquoise
  { t: 1.0, base: [72, 192, 217], glow: [96, 226, 255] }, // turquoise hold
];

// Deep violet falling away into almost black. The violet is carried at the
// bottom of the frame and at the two outer walls; the top of the frame and the
// middle of the room — where the speaker and the domino screen are — go to
// near-black, so the walls never compete with what is on stage.
export const ROOM = {
  black: [5, 3, 11],
  violet: [46, 12, 96],
  centreFade: 0.78, // how far the middle of the room is pulled back to black
};

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

function sample(stops, u, emissive) {
  const t = clamp01(u);
  let a = stops[0];
  let b = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (t >= stops[i].t && t <= stops[i + 1].t) {
      a = stops[i];
      b = stops[i + 1];
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

// Sample the room gradient at normalised x (0 = far south wall, 1 = far north
// wall). `emissive` blends toward the glow variant for lit elements.
export const gradientAt = (u, emissive = 0) => sample(GRADIENT_ENV, u, emissive);
export const wayfindingAt = (u, emissive = 0) => sample(GRADIENT_WAYFINDING, u, emissive);

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

// The wordmark, lifted from the same file. Source viewBox is 3000 x 2700; the
// wordmark occupies x 48..2948, y 2183..2652. Kept as geometry rather than as
// text because it is drawn artwork, not type — Karbon will not reproduce it.
export const LOGO_WORDMARK = {
  x0: 47.75,
  y0: 2183.0,
  x1: 2948.0,
  y1: 2652.0,
  parts: [
  { fill: '#ffffff', d: 'M117.6,2370.85 L47.75,2187.3 L82.07,2187.3 L137.08,2339.02 L191.77,2187.3 L225.47,2187.3 L155.62,2370.85 L117.6,2370.85 Z' },
  { fill: '#ffffff', d: 'M370.09,2343.03 L370.09,2370.86 L256.04,2370.86 L256.04,2187.27 L368.22,2187.27 L368.22,2215.11 L287.25,2215.11 L287.25,2264.55 L362.35,2264.55 L362.35,2291.76 L287.25,2291.76 L287.25,2343.03 L370.09,2343.03 Z' },
  { fill: '#ffffff', d: 'M548.09,2231.79c-12.67-12.05-30.28-19.16-50.69-19.16-36.15,0-62.12,26.55-62.12,66.43s27.21,66.47,63.05,66.47c20.72,0,37.39-6.18,51.93-18.85v33.66c-16.09,9.56-34.01,13.61-52.87,13.61-56.56,0-94.58-38.91-94.58-94.89s39.88-94.89,94.58-94.89c18.85,0,35.88,4.04,50.69,12.98v34.63Z' },
  { fill: '#ffffff', d: 'M662.74,2370.85 L631.21,2370.85 L631.21,2215.09 L573.1,2215.09 L573.1,2187.3 L720.54,2187.3 L720.54,2215.09 L662.74,2215.09 L662.74,2370.85 Z' },
  { fill: '#ffffff', d: 'M838.58,2212.64c-35.26,0-62.74,26.24-62.74,66.43s27.48,66.43,62.74,66.43,62.74-26.24,62.74-66.43-27.52-66.43-62.74-66.43M838.58,2184.19c52.86,0,95.2,38.64,95.2,94.89s-42.33,94.89-95.2,94.89-95.2-38.64-95.2-94.89,42.02-94.89,95.2-94.89' },
  { fill: '#ffffff', d: 'M1006.38,2279.7h15.47c24.99,0,41.09-10.81,41.09-34.64,0-20.99-14.54-33.35-42.33-33.35-3.69,0-10.85.31-14.23.62v67.36ZM1006.38,2370.85h-31.53v-183.28c11.12-1.83,30.9-3.38,45.75-3.38,48.2,0,74.48,21.3,74.48,59.94,0,26.9-15.16,46.37-36.46,54.42l55.31,72.3h-38.02l-48.82-65.19h-20.72v65.19Z' },
  { fill: '#ffffff', d: 'M56.26,2465.16 L87.16,2465.16 L87.16,2648.75 L56.26,2648.75 Z' },
  { fill: '#ffffff', d: 'M260.08,2600.84 L260.08,2465.17 L290.09,2465.17 L290.09,2648.73 L260.39,2648.73 L168.03,2514.31 L168.03,2648.73 L138.02,2648.73 L138.02,2465.17 L169.55,2465.17 L260.08,2600.84 Z' },
  { fill: '#ffffff', d: 'M330.64,2606.09c13.91,10.81,28.45,18.85,47.54,18.85,17.88,0,33.31-7.11,33.31-25.66,0-16.99-13.02-23.48-33-29.66-34.52-11.12-50.26-25.03-50.26-55.98,0-33.35,26.36-51.58,57.22-51.58,19.4,0,33.94,5.56,46.02,13.92v31.49c-14.23-11.7-27.83-18.5-45.09-18.5s-27.87,9.56-27.87,23.79,10.3,21.03,33,28.45c35.14,10.81,50.26,25.93,50.26,57.14,0,36.81-28.45,53.49-63.28,53.49-19.71,0-36.34-5.56-47.85-13.6v-32.15Z' },
  { fill: '#ffffff', d: 'M550.8,2648.73 L519.9,2648.73 L519.9,2492.98 L462.95,2492.98 L462.95,2465.14 L607.44,2465.14 L607.44,2492.98 L550.8,2492.98 L550.8,2648.73 Z' },
  { fill: '#ffffff', d: 'M640.42,2465.16 L671.3199999999999,2465.16 L671.3199999999999,2648.75 L640.42,2648.75 Z' },
  { fill: '#ffffff', d: 'M792.17,2648.73 L761.26,2648.73 L761.26,2492.98 L704.32,2492.98 L704.32,2465.14 L848.8,2465.14 L848.8,2492.98 L792.17,2492.98 L792.17,2648.73 Z' },
  { fill: '#ffffff', d: 'M878.47,2465.16h30.9v115.29c0,35.22,18.15,44.51,44.82,44.51,13.92,0,24.84-1.24,35.41-3.11v-156.69h30.9v178.34c-16.64,4.63-44.82,8.32-66.31,8.32-40.89,0-75.72-14.81-75.72-65.81v-120.85Z' },
  { fill: '#ffffff', d: 'M1141.34,2648.73 L1110.43,2648.73 L1110.43,2492.98 L1053.48,2492.98 L1053.48,2465.14 L1197.97,2465.14 L1197.97,2492.98 L1141.34,2492.98 L1141.34,2648.73 Z' },
  { fill: '#ffffff', d: 'M1342.72,2620.92 L1342.72,2648.75 L1230.97,2648.75 L1230.97,2465.16 L1340.93,2465.16 L1340.93,2492.99 L1261.56,2492.99 L1261.56,2542.44 L1335.14,2542.44 L1335.14,2569.61 L1261.56,2569.61 L1261.56,2620.92 L1342.72,2620.92 Z' },
  { fill: '#ffffff', d: 'M1735.83,2184.27 L1766.6899999999998,2184.27 L1766.6899999999998,2367.86 L1735.83,2367.86 Z' },
  { fill: '#ffffff', d: 'M1939.62,2319.95 L1939.62,2184.29 L1969.59,2184.29 L1969.59,2367.88 L1939.93,2367.88 L1847.58,2233.43 L1847.58,2367.88 L1817.61,2367.88 L1817.61,2184.29 L1849.05,2184.29 L1939.62,2319.95 Z' },
  { fill: '#ffffff', d: 'M2010.18,2325.21c13.91,10.85,28.45,18.85,47.54,18.85,17.88,0,33.31-7.11,33.31-25.66,0-16.99-13.02-23.48-33-29.66-34.52-11.12-50.26-25.03-50.26-55.94,0-33.39,26.36-51.62,57.22-51.62,19.36,0,33.94,5.56,46.02,13.92v31.53c-14.23-11.74-27.83-18.54-45.09-18.54s-27.87,9.56-27.87,23.79,10.3,21.03,33,28.45c35.14,10.81,50.3,25.97,50.3,57.18,0,36.73-28.49,53.45-63.32,53.45-19.67,0-36.34-5.56-47.85-13.6v-32.15Z' },
  { fill: '#ffffff', d: 'M2230.35,2367.87 L2199.45,2367.87 L2199.45,2212.11 L2142.54,2212.11 L2142.54,2184.28 L2286.99,2184.28 L2286.99,2212.11 L2230.35,2212.11 L2230.35,2367.87 Z' },
  { fill: '#ffffff', d: 'M2319.99,2184.27 L2350.89,2184.27 L2350.89,2367.86 L2319.99,2367.86 Z' },
  { fill: '#ffffff', d: 'M2471.72,2367.87 L2440.81,2367.87 L2440.81,2212.11 L2383.87,2212.11 L2383.87,2184.28 L2528.35,2184.28 L2528.35,2212.11 L2471.72,2212.11 L2471.72,2367.87 Z' },
  { fill: '#ffffff', d: 'M2558.01,2184.29h30.9v115.29c0,35.22,18.15,44.47,44.82,44.47,13.92,0,24.84-1.24,35.41-3.07v-156.69h30.9v178.3c-16.64,4.66-44.82,8.36-66.31,8.36-40.89,0-75.72-14.81-75.72-65.81v-120.85Z' },
  { fill: '#ffffff', d: 'M2820.89,2367.87 L2789.99,2367.87 L2789.99,2212.11 L2733.04,2212.11 L2733.04,2184.28 L2877.52,2184.28 L2877.52,2212.11 L2820.89,2212.11 L2820.89,2367.87 Z' },
  { fill: '#ffffff', d: 'M1798.56,2645.74 L1727.35,2462.19 L1762.33,2462.19 L1818.43,2613.9 L1874.21,2462.19 L1908.57,2462.19 L1837.36,2645.74 L1798.56,2645.74 Z' },
  { fill: '#ffffff', d: 'M2056.1,2617.94 L2056.1,2645.77 L1939.79,2645.77 L1939.79,2462.18 L2054.19,2462.18 L2054.19,2489.97 L1971.63,2489.97 L1971.63,2539.42 L2048.2,2539.42 L2048.2,2566.63 L1971.63,2566.63 L1971.63,2617.94 L2056.1,2617.94 Z' },
  { fill: '#ffffff', d: 'M2237.63,2506.68c-12.94-12.05-30.9-19.16-51.7-19.16-36.85,0-63.36,26.55-63.36,66.43s27.76,66.47,64.29,66.47c21.15,0,38.17-6.18,52.98-18.85v33.66c-16.36,9.6-34.67,13.61-53.91,13.61-57.65,0-96.44-38.95-96.44-94.89s40.7-94.89,96.44-94.89c19.24,0,36.58,4.04,51.7,12.98v34.63Z' },
  { fill: '#ffffff', d: 'M2354.58,2645.74 L2322.43,2645.74 L2322.43,2489.98 L2263.15,2489.98 L2263.15,2462.19 L2413.51,2462.19 L2413.51,2489.98 L2354.58,2489.98 L2354.58,2645.74 Z' },
  { fill: '#ffffff', d: 'M2564.18,2617.94 L2564.18,2645.77 L2447.88,2645.77 L2447.88,2462.18 L2562.31,2462.18 L2562.31,2489.97 L2479.71,2489.97 L2479.71,2539.42 L2556.33,2539.42 L2556.33,2566.63 L2479.71,2566.63 L2479.71,2617.94 L2564.18,2617.94 Z' },
  { fill: '#ffffff', d: 'M2605.17,2462.17h32.15v115.26c0,35.26,18.93,44.51,46.65,44.51,14.5,0,25.81-1.24,36.89-3.07v-156.69h32.15v178.3c-17.34,4.66-46.65,8.36-69.04,8.36-42.56,0-78.79-14.81-78.79-65.85v-120.81Z' },
  { fill: '#ffffff', d: 'M2838.09,2554.58h15.74c25.54,0,41.94-10.81,41.94-34.64,0-20.99-14.81-33.35-43.19-33.35-3.77,0-11.04.31-14.5.62v67.36ZM2838.09,2645.74h-32.15v-183.28c11.35-1.83,31.53-3.38,46.65-3.38,49.17,0,75.96,21.3,75.96,59.94,0,26.9-15.43,46.37-37.2,54.42l56.4,72.3h-38.76l-49.79-65.19h-21.11v65.19Z' },
  { fill: '#ffffff', d: 'M1540.81,2183.61 L1550.06,2183.61 L1550.06,2646.61 L1540.81,2646.61 Z' },
  { fill: '#ffffff', d: 'M2944.2,2635.13 L2944.2,2645.97 L2933.36,2645.97 L2933.36,2647.3 L2945.53,2647.3 L2945.53,2635.13 L2944.2,2635.13 Z' },
  { fill: '#ffffff', d: 'M1658.45,1855.17c0-26.51,19.57-47.09,46.35-47.09s46.59,20.57,46.59,47.09-19.59,46.83-46.59,46.83-46.35-20.56-46.35-46.83ZM1741.73,1855.17c0-21.56-15.11-38.41-36.93-38.41s-36.68,16.85-36.68,38.41,15.11,38.17,36.68,38.17,36.93-17.1,36.93-38.17ZM1699.59,1877.23h-10.9v-45.1c3.71-.75,9.67-1.49,14.37-1.49,11.16,0,19.57,5.21,19.57,16.36,0,6.19-3.47,11.15-8.17,13.38l12.15,16.85h-12.65l-9.91-14.37h-4.46v14.37ZM1699.59,1853.44h3.47c4.96,0,8.17-1.74,8.17-6.44s-3.47-6.45-7.93-6.45c-.75,0-2.72,0-3.71.24v12.64Z' },
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
