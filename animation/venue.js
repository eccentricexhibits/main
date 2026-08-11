/*
 * Venue geometry — DX Trading Floor immersive surface.
 *
 * Measured off DX_TradingFloor_Immersive_Template-scaled_fullSize.png, which is
 * itself exactly 6878 x 1080, by detecting the template's rule lines. Panel
 * boundaries below are the detected rule centres, so the panels tile the full
 * width with no gaps; they land within a pixel or two of the labelled sizes
 * (the difference is the thickness of the rules in the template).
 *
 *   panel            labelled      here
 *   south wall       2239 x 1080   0    -> 2241
 *   west-faced nook   262 x 1080   2241 -> 2503
 *   south-faced nook   95 x 1080   2503 -> 2598
 *   west wall        1679 x 1080   2598 -> 4278
 *   north-faced nook   95 x 1080   4278 -> 4373
 *   west-faced nook   262 x 1080   4373 -> 4636
 *   north wall       2239 x 1080   4636 -> 6878
 *
 * The cube band starts at y = 674 (detected) and is 406 tall, which is the
 * labelled figure. "Above cube 2239 x 684" carries ten rows of overlap behind
 * the cube's top edge, so artwork for the upper band should bleed to y = 684.
 */

const VENUE = {
  width: 6878,
  height: 1080,

  // Vertical panel boundaries, left to right.
  seams: [0, 2241, 2503, 2598, 4278, 4373, 4636, 6878],

  cubeTop: 674, // cube band: y 674..1080, 406 tall
  cubeBleed: 10, // upper-band artwork continues to y 684, hidden behind the cube

  panels: {
    southWall: { x: 0, w: 2241 },
    southWestNook: { x: 2241, w: 262 },
    southFacedNook: { x: 2503, w: 95 },
    westWall: { x: 2598, w: 1680 },
    northFacedNook: { x: 4278, w: 95 },
    northWestNook: { x: 4373, w: 263 },
    northWall: { x: 4636, w: 2242 },
  },

  // Draped returns either side of each cube face — live surface, but angled away.
  cube: {
    southDrapedA: { x: 0, w: 301 },
    south: { x: 301, w: 1728 },
    southDrapedB: { x: 2029, w: 209 },
    northDrapedC: { x: 4636, w: 209 },
    north: { x: 4845, w: 1728 },
    northDrapedD: { x: 6573, w: 305 },
  },

  // The Domino screen sits in the top 630 of the west wall. The template draws it
  // as a shallow trapezoid narrowing downward; this is the rectangle inscribed in
  // it, centred in the panel, matching the labelled 1653 x 630.
  domino: { x: 2611, y: 0, w: 1653, h: 630 },
};

/**
 * The four bands the transition sweeps inward. Each spans from its outer edge to
 * the west wall, so arrows run continuously across the wall and its nooks before
 * they reach the centre — and each keeps its own vertical slice, so nothing
 * crosses between bands on the way in.
 */
VENUE.bands = [
  { id: 'southUpper', x: 0, w: 2598, y: 0, h: VENUE.cubeTop, dir: 1, gate: 2598 },
  { id: 'southCube', x: 0, w: 2598, y: VENUE.cubeTop, h: 1080 - VENUE.cubeTop, dir: 1, gate: 2598 },
  { id: 'northUpper', x: 4278, w: 2600, y: 0, h: VENUE.cubeTop, dir: -1, gate: 4278 },
  { id: 'northCube', x: 4278, w: 2600, y: VENUE.cubeTop, h: 1080 - VENUE.cubeTop, dir: -1, gate: 4278 },
];

VENUE.domino.cx = VENUE.domino.x + VENUE.domino.w / 2;
VENUE.domino.cy = VENUE.domino.y + VENUE.domino.h / 2;

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { VENUE };
}
