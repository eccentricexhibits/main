// Collision for the cow game: static level triangles in a uniform grid, plus moving
// "bodies" (planks, rafts, gates...) whose triangles are re-transformed when they move.
// The character is treated as a vertical stack of spheres for walls and a point for
// floors/ceilings, which is plenty for a chunky platformer character.

import * as THREE from 'three';

const CELL = 400;
const FLOOR_NY = 0.45; // surfaces flatter than this are floors, steeper ones walls
const _a = new THREE.Vector3(), _b = new THREE.Vector3(), _c = new THREE.Vector3();
const _p = new THREE.Vector3(), _q = new THREE.Vector3();

function makeTri(a, b, c, tag, owner) {
  const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
  const ac = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
  let n = [ab[1] * ac[2] - ab[2] * ac[1], ab[2] * ac[0] - ab[0] * ac[2], ab[0] * ac[1] - ab[1] * ac[0]];
  const len = Math.hypot(n[0], n[1], n[2]);
  if (len < 1e-6) return null;
  n = n.map((v) => v / len);
  const kind = n[1] > FLOOR_NY ? 'floor' : n[1] < -FLOOR_NY ? 'ceil' : 'wall';
  return {
    a, b, c, n, d: -(n[0] * a[0] + n[1] * a[1] + n[2] * a[2]), kind, tag, owner,
    minX: Math.min(a[0], b[0], c[0]), maxX: Math.max(a[0], b[0], c[0]),
    minY: Math.min(a[1], b[1], c[1]), maxY: Math.max(a[1], b[1], c[1]),
    minZ: Math.min(a[2], b[2], c[2]), maxZ: Math.max(a[2], b[2], c[2]),
  };
}

/** Point-in-triangle test in the XZ plane. */
function insideXZ(t, x, z) {
  const s = (p, q) => (q[0] - p[0]) * (z - p[2]) - (q[2] - p[2]) * (x - p[0]);
  const d1 = s(t.a, t.b), d2 = s(t.b, t.c), d3 = s(t.c, t.a);
  const neg = d1 < 0 || d2 < 0 || d3 < 0, pos = d1 > 0 || d2 > 0 || d3 > 0;
  return !(neg && pos);
}

function heightAt(t, x, z) {
  return -(t.n[0] * x + t.n[2] * z + t.d) / t.n[1];
}

const _tri = new THREE.Triangle();
function closestPointOnTri(p, t, out) {
  _tri.set(_a.fromArray(t.a), _b.fromArray(t.b), _c.fromArray(t.c));
  return _tri.closestPointToPoint(p, out);
}

/**
 * A moving collider. `localTris` are { v:[a,b,c], type } in the object's own space;
 * call world.updateBody(body) after moving `object` to refresh its world triangles.
 */
export class Body {
  constructor(object, localTris, opts = {}) {
    this.object = object;
    this.localTris = localTris;
    this.tris = [];
    this.enabled = true;
    this.owner = opts.owner || null;
    this.prevMatrix = new THREE.Matrix4();
    this.matrix = new THREE.Matrix4();
  }
}

export class World {
  constructor(staticTris) {
    this.grid = new Map();
    this.bodies = [];
    this.water = []; // { minX, maxX, minZ, maxZ, y }
    for (const t of staticTris) {
      if (!t.v) continue;
      const tri = makeTri(t.v[0], t.v[1], t.v[2], t.type, null);
      if (tri) this.insert(tri);
    }
  }

  insert(tri) {
    for (let cx = Math.floor(tri.minX / CELL); cx <= Math.floor(tri.maxX / CELL); cx++) {
      for (let cz = Math.floor(tri.minZ / CELL); cz <= Math.floor(tri.maxZ / CELL); cz++) {
        const key = cx * 100003 + cz;
        let list = this.grid.get(key);
        if (!list) this.grid.set(key, (list = []));
        list.push(tri);
      }
    }
  }

  /** Static triangles near (x, z) within r, plus every enabled body's triangles. */
  near(x, z, r = 0) {
    const out = new Set();
    for (let cx = Math.floor((x - r) / CELL); cx <= Math.floor((x + r) / CELL); cx++) {
      for (let cz = Math.floor((z - r) / CELL); cz <= Math.floor((z + r) / CELL); cz++) {
        const list = this.grid.get(cx * 100003 + cz);
        if (list) for (const t of list) out.add(t);
      }
    }
    for (const b of this.bodies) if (b.enabled) for (const t of b.tris) out.add(t);
    return out;
  }

  addBody(body) {
    this.bodies.push(body);
    this.updateBody(body, true);
    return body;
  }

  updateBody(body, reset = false) {
    body.object.updateMatrixWorld(true);
    body.prevMatrix.copy(reset ? body.object.matrixWorld : body.matrix);
    body.matrix.copy(body.object.matrixWorld);
    const m = body.matrix;
    body.tris = [];
    for (const t of body.localTris) {
      const v = t.v.map((p) => _p.fromArray(p).applyMatrix4(m).toArray());
      const tri = makeTri(v[0], v[1], v[2], t.type, body);
      if (tri) body.tris.push(tri);
    }
  }

  /** Highest floor at (x, z) whose surface is at most `stepUp` above y. */
  findFloor(x, y, z, stepUp = 40) {
    let best = null;
    for (const t of this.near(x, z)) {
      if (t.kind !== 'floor' || x < t.minX || x > t.maxX || z < t.minZ || z > t.maxZ) continue;
      if (!insideXZ(t, x, z)) continue;
      const h = heightAt(t, x, z);
      if (h > y + stepUp) continue;
      if (!best || h > best.y) best = { y: h, tri: t, normal: t.n, tag: t.tag, body: t.owner };
    }
    return best;
  }

  /** Lowest ceiling above y at (x, z). */
  findCeil(x, y, z) {
    let best = null;
    for (const t of this.near(x, z)) {
      if (t.kind !== 'ceil' || x < t.minX || x > t.maxX || z < t.minZ || z > t.maxZ) continue;
      if (!insideXZ(t, x, z)) continue;
      const h = heightAt(t, x, z);
      if (h < y) continue;
      if (!best || h < best.y) best = { y: h, tri: t, body: t.owner };
    }
    return best;
  }

  /**
   * Push a vertical stack of spheres (at the given heights above `pos`) out of walls.
   * Walls whose top is within `stepUp` of her feet are steps, not walls; walls only
   * push from their front side. Mutates pos.x / pos.z.
   * Returns the strongest contact { normal, tri, body } or null.
   */
  pushWalls(pos, radius, heights, stepUp = 40) {
    let hit = null, hitDepth = 0;
    for (let iter = 0; iter < 2; iter++) {
      for (const t of this.near(pos.x, pos.z, radius)) {
        if (t.kind !== 'wall' || t.maxY <= pos.y + stepUp) continue;
        if (pos.x + radius < t.minX || pos.x - radius > t.maxX || pos.z + radius < t.minZ || pos.z - radius > t.maxZ) continue;
        for (const h of heights) {
          const cy = pos.y + h;
          if (cy + radius < t.minY || cy - radius > t.maxY) continue;
          _p.set(pos.x, cy, pos.z);
          if (t.n[0] * _p.x + t.n[1] * _p.y + t.n[2] * _p.z + t.d < 0) continue; // behind the wall
          closestPointOnTri(_p, t, _q);
          let dx = _p.x - _q.x, dz = _p.z - _q.z;
          const dy = _p.y - _q.y;
          const dist = Math.hypot(dx, dy, dz);
          if (dist >= radius) continue;
          let hl = Math.hypot(dx, dz);
          if (hl < 1e-4) { dx = t.n[0]; dz = t.n[2]; hl = Math.hypot(dx, dz) || 1; }
          const depth = radius - dist;
          pos.x += (dx / hl) * depth;
          pos.z += (dz / hl) * depth;
          if (depth > hitDepth) { hitDepth = depth; hit = { normal: [dx / hl, 0, dz / hl], tri: t, body: t.owner }; }
        }
      }
    }
    return hit;
  }

  waterAt(x, z) {
    for (const w of this.water) if (x >= w.minX && x <= w.maxX && z >= w.minZ && z <= w.maxZ) return w.y;
    return null;
  }
}
