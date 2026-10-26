// A small playground level built from boxes and ramps. Every triangle is used for
// both rendering and SM64-style collision (same winding: CCW = front/outward).
// Units are SM64 units (Mario is ~160 tall, runs at 32 units per frame).

import * as THREE from 'three';
import { SURFACE_DEFAULT, SURFACE_BURNING, SURFACE_DEATH_PLANE, SURFACE_SLIPPERY } from '../engine/surface_terrains.js';

// ---------------------------------------------------------------------------
// Procedural textures (kept tiny and filtered like the N64)

function canvasTexture(size, draw) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const g = c.getContext('2d');
  draw(g, size);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

function noise(g, s, colors, n, size = 2) {
  for (let i = 0; i < n; i++) {
    g.fillStyle = colors[i % colors.length];
    g.fillRect(Math.random() * s, Math.random() * s, size, size);
  }
}

const TEXTURES = {
  grass: () => canvasTexture(64, (g, s) => {
    g.fillStyle = '#4f9a3a'; g.fillRect(0, 0, s, s);
    g.fillStyle = '#5aa843'; g.fillRect(0, 0, s / 2, s / 2); g.fillRect(s / 2, s / 2, s / 2, s / 2);
    noise(g, s, ['#3f8a2e', '#69b84f', '#468f34'], 260);
  }),
  dirt: () => canvasTexture(64, (g, s) => {
    g.fillStyle = '#9c6b3c'; g.fillRect(0, 0, s, s);
    noise(g, s, ['#8a5c31', '#b07d49', '#7a5029'], 300, 3);
  }),
  brick: () => canvasTexture(64, (g, s) => {
    g.fillStyle = '#c9b48a'; g.fillRect(0, 0, s, s);
    g.fillStyle = '#a8916a';
    for (let y = 0; y < 4; y++) {
      g.fillRect(0, y * 16 + 15, s, 1);
      for (let x = 0; x < 3; x++) g.fillRect(((x * 32) + (y % 2) * 16) % s, y * 16, 1, 16);
    }
    noise(g, s, ['#bba57b', '#d6c39b'], 120);
  }),
  stone: () => canvasTexture(64, (g, s) => {
    g.fillStyle = '#8c8f99'; g.fillRect(0, 0, s, s);
    g.strokeStyle = '#6d707a'; g.lineWidth = 2;
    g.strokeRect(1, 1, s - 2, s - 2); g.strokeRect(1, 1, s / 2 - 1, s / 2 - 1); g.strokeRect(s / 2, s / 2, s / 2 - 1, s / 2 - 1);
    noise(g, s, ['#7d808a', '#9da0aa'], 200);
  }),
  wood: () => canvasTexture(64, (g, s) => {
    g.fillStyle = '#b5773a'; g.fillRect(0, 0, s, s);
    g.fillStyle = '#8d5826';
    for (let i = 0; i < 4; i++) g.fillRect(0, i * 16, s, 2);
    noise(g, s, ['#a66c33', '#c4864a'], 160, 3);
  }),
  lava: () => canvasTexture(64, (g, s) => {
    g.fillStyle = '#e8481b'; g.fillRect(0, 0, s, s);
    noise(g, s, ['#ff9a2e', '#ffcf3a', '#c7300f'], 260, 4);
  }),
  check: () => canvasTexture(64, (g, s) => {
    g.fillStyle = '#e8d24a'; g.fillRect(0, 0, s, s);
    g.fillStyle = '#3a63c9'; g.fillRect(0, 0, s / 2, s / 2); g.fillRect(s / 2, s / 2, s / 2, s / 2);
  }),
  slide: () => canvasTexture(64, (g, s) => {
    g.fillStyle = '#5cc0e8'; g.fillRect(0, 0, s, s);
    g.fillStyle = '#86d6f2';
    for (let i = 0; i < 4; i++) g.fillRect(i * 16, 0, 6, s);
  }),
};

// ---------------------------------------------------------------------------

export class LevelBuilder {
  constructor() {
    this.tris = []; // { v: [[x,y,z]x3], type, mat }
  }

  tri(a, b, c, mat, type = SURFACE_DEFAULT) {
    this.tris.push({ v: [a, b, c], type, force: 0, mat });
  }

  quad(a, b, c, d, mat, type) { // a,b,c,d counter-clockwise seen from the front
    this.tri(a, b, c, mat, type);
    this.tri(a, c, d, mat, type);
  }

  /** Axis-aligned box. opts: { top, side, bottom, type, sideType } */
  box(x0, y0, z0, x1, y1, z1, opts = {}) {
    const top = opts.top || 'grass', side = opts.side || 'dirt';
    const type = opts.type ?? SURFACE_DEFAULT;
    const sideType = opts.sideType ?? SURFACE_DEFAULT;
    // top (+Y)
    this.quad([x0, y1, z0], [x0, y1, z1], [x1, y1, z1], [x1, y1, z0], top, type);
    // bottom (-Y)
    if (opts.bottom !== false) this.quad([x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], opts.bottom || side, sideType);
    // +Z
    this.quad([x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1], side, sideType);
    // -Z
    this.quad([x1, y0, z0], [x0, y0, z0], [x0, y1, z0], [x1, y1, z0], side, sideType);
    // +X
    this.quad([x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1], side, sideType);
    // -X
    this.quad([x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0], side, sideType);
  }

  /**
   * Ramp rising along +X or -X/+Z/-Z. dir: 'x+', 'x-', 'z+', 'z-' = uphill direction.
   * Occupies [x0,x1]x[z0,z1], from height y0 (low edge) to y1 (high edge), solid down to yBase.
   */
  ramp(x0, z0, x1, z1, yBase, y0, y1, dir, opts = {}) {
    const top = opts.top || 'grass', side = opts.side || 'dirt';
    const type = opts.type ?? SURFACE_DEFAULT;
    const h = (x, z) => {
      const t = dir === 'x+' ? (x - x0) / (x1 - x0) : dir === 'x-' ? (x1 - x) / (x1 - x0)
        : dir === 'z+' ? (z - z0) / (z1 - z0) : (z1 - z) / (z1 - z0);
      return y0 + (y1 - y0) * t;
    };
    const A = [x0, h(x0, z0), z0], B = [x0, h(x0, z1), z1], C = [x1, h(x1, z1), z1], D = [x1, h(x1, z0), z0];
    this.quad(A, B, C, D, top, type);
    const b = (p) => [p[0], yBase, p[2]];
    // sides: base edge p->q then up the sloped edge, outward-facing when p->q runs
    // counter-clockwise seen from above; zero-height corners collapse to a triangle.
    const side4 = (p, q) => {
      const hp = p[1] - yBase > 0.5, hq = q[1] - yBase > 0.5;
      if (hp && hq) this.quad(b(p), b(q), q, p, side);
      else if (hq) this.tri(b(p), b(q), q, side);
      else if (hp) this.tri(b(p), b(q), p, side);
    };
    side4(A, B); side4(B, C); side4(C, D); side4(D, A);
    if (opts.bottom !== false && y0 > yBase && y1 > yBase) this.quad(b(A), b(D), b(C), b(B), side);
  }

  buildMeshes() {
    const groups = new Map();
    for (const t of this.tris) {
      if (!t.mat) continue;
      if (!groups.has(t.mat)) groups.set(t.mat, []);
      groups.get(t.mat).push(t);
    }
    const root = new THREE.Group();
    for (const [mat, tris] of groups) {
      const pos = [], nrm = [], uv = [];
      for (const t of tris) {
        const [a, b, c] = t.v.map((p) => new THREE.Vector3(...p));
        const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)).normalize();
        const ax = Math.abs(n.x), ay = Math.abs(n.y), az = Math.abs(n.z);
        for (const p of [a, b, c]) {
          pos.push(p.x, p.y, p.z);
          nrm.push(n.x, n.y, n.z);
          // world-space planar mapping, one texture tile per 256 units
          if (ay >= ax && ay >= az) uv.push(p.x / 256, p.z / 256);
          else if (ax >= az) uv.push(p.z / 256, p.y / 256);
          else uv.push(p.x / 256, p.y / 256);
        }
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3));
      g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
      const material = mat === 'lava'
        ? new THREE.MeshBasicMaterial({ map: TEXTURES.lava() })
        : new THREE.MeshLambertMaterial({ map: (TEXTURES[mat] || TEXTURES.check)() });
      const mesh = new THREE.Mesh(g, material);
      mesh.name = mat;
      root.add(mesh);
    }
    return root;
  }
}

/**
 * The playground. Returns { tris, mesh, spawn, redCoins, starPos }.
 */
export function buildPlayground() {
  const L = new LevelBuilder();
  const S = 3000; // half-size of the island

  // Island ground with a lava pit cut out of the south-east quadrant:
  // ground is made of four slabs around the pit [800..2200]x[800..2200].
  const pit = [800, 2200];
  L.box(-S, -400, -S, S, 0, pit[0], {});                 // north half
  L.box(-S, -400, pit[0], pit[0], 0, S, {});             // south-west
  L.box(pit[1], -400, pit[0], S, 0, S, {});              // south-east strip
  L.box(pit[0], -400, pit[1], pit[1], 0, S, {});         // south strip below the pit
  // pit floor (lava) and its walls are the slabs' sides
  L.box(pit[0], -500, pit[0], pit[1], -250, pit[1], { top: 'lava', type: SURFACE_BURNING, side: 'stone' });
  // stepping stones across the lava
  L.box(950, -250, 1000, 1150, 40, 1200, { top: 'stone', side: 'stone' });
  L.box(1350, -250, 1300, 1550, 120, 1500, { top: 'stone', side: 'stone' });
  L.box(1750, -250, 1650, 1950, 200, 1850, { top: 'stone', side: 'stone' });

  // Spawn plaza
  L.box(-300, 0, 1100, 300, 20, 1700, { top: 'check', side: 'stone' });

  // Staircase up to a plateau (north-west)
  for (let i = 0; i < 6; i++) {
    L.box(-1600, 0, -400 - i * 150, -1000, 100 * (i + 1), -250 - i * 150, { top: 'brick', side: 'brick' });
  }
  L.box(-2400, 0, -1900, -1000, 600, -1150, { top: 'grass', side: 'brick' });

  // Long-jump gap: a far ledge 950 units from the plateau, too far for a normal jump
  L.box(-2400, 0, -3000, -1000, 600, -2850, { top: 'grass', side: 'brick' });

  // Gentle hill (north-east)
  L.ramp(400, -2600, 1400, -1600, 0, 0, 400, 'x+', { top: 'grass', side: 'dirt' });
  L.box(1400, 0, -2600, 2000, 400, -1600, { top: 'grass', side: 'dirt' });

  // Steep slide tower: a tall block with a steep ramp down its side
  L.box(2100, 0, -2600, 2800, 1200, -1900, { top: 'stone', side: 'stone' });
  L.box(1900, 0, -2600, 2100, 750, -2350, { top: 'wood', side: 'stone' }); // halfway ledge from the hill
  L.ramp(2100, -1900, 2800, -700, 0, 0, 1200, 'z-', { top: 'slide', side: 'stone', type: SURFACE_SLIPPERY });

  // Wall-kick chimney (east): two tall walls 300 apart
  L.box(2300, 0, -300, 2600, 1500, 300, { top: 'wood', side: 'stone' });
  L.box(2900, 0, -300, 3000, 1500, 300, { top: 'stone', side: 'stone' });

  // Ledge-grab boxes near spawn
  L.box(-900, 0, 400, -600, 180, 700, { top: 'wood', side: 'wood' });
  L.box(-1300, 0, 400, -1000, 300, 700, { top: 'wood', side: 'wood' });
  L.box(-1700, 0, 400, -1400, 460, 700, { top: 'wood', side: 'wood' });

  // Backflip pillar: a low box next to a high pillar
  L.box(600, 0, 300, 900, 120, 600, { top: 'brick', side: 'brick' });
  L.box(950, 0, 300, 1150, 560, 500, { top: 'brick', side: 'brick' });

  // Central tower with the star on top: spiral of platforms around it
  L.box(-300, 0, -1100, 300, 1400, -500, { top: 'stone', side: 'brick' });
  const steps = [
    [380, 200, -800], [280, 420, -360], [-220, 640, -320], [-480, 860, -800], [-200, 1080, -1280], [300, 1240, -1220],
  ];
  for (const [x, y, z] of steps) L.box(x - 110, y - 40, z - 110, x + 110, y, z + 110, { top: 'wood', side: 'wood' });

  // Trees: solid trunks (collision) with decorative canopies (render only)
  const trees = [[-2500, 2400], [-2000, 2600], [2600, 2500], [-2600, 900], [1600, -400], [-800, 2300], [600, 2500], [-2700, -500]];
  for (const [x, z] of trees) L.box(x - 30, 0, z - 30, x + 30, 260, z + 30, { top: 'wood', side: 'wood' });

  // Death plane far below the island
  L.quad([-8000, -3000, -8000], [-8000, -3000, 8000], [8000, -3000, 8000], [8000, -3000, -8000], null, SURFACE_DEATH_PLANE);

  const mesh = L.buildMeshes();
  const canopyMat = new THREE.MeshLambertMaterial({ color: 0x2f8f3a, flatShading: true });
  for (const [x, z] of trees) {
    const canopy = new THREE.Mesh(new THREE.ConeGeometry(170, 420, 7), canopyMat);
    canopy.position.set(x, 260 + 180, z);
    canopy.name = 'canopy';
    canopy.raycast = () => {}; // the camera may pass through foliage
    mesh.add(canopy);
  }

  const redCoins = [
    [-1700, 680, -1500],   // plateau above the stairs
    [-1700, 680, -2925],   // across the long-jump gap
    [2450, 1580, 0],       // top of the wall-kick chimney
    [1850, 280, 1750],     // last stepping stone over the lava
    [1700, 480, -2100],    // hill top
    [2450, 1280, -2250],   // top of the slide tower
    [1050, 640, 400],      // backflip pillar
    [-1550, 540, 550],     // tallest ledge-grab box
  ];
  const starPos = [0, 1500, -800];
  return { tris: L.tris, mesh, spawn: { pos: [0, 20, 1400], yaw: -0x8000 }, redCoins, starPos };
}
