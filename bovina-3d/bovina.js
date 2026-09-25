// Bovina: a procedural Three.js model of the "Bloody Cadaver Burgers" cow character.
// createBovina() returns a THREE.Group, about 1.85 units tall, feet at y = 0, facing +Z.
// Every shape and texture is generated in code, so the model has no external assets.

import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);

// The layout was traced from the reference photo, in its pixel coordinates.
// These helpers turn photo pixels into model units before the final rescale.
const PX = 1 / 680;
const X = (px) => (px - 1120) * PX;
const Y = (py) => (1970 - py) * PX + 0.22;

const COLORS = {
  fur: 0xf1efea,
  black: 0x141414,
  mask: 0xf4f2ee,
  udder: 0xf2c3cf,
  teat: 0xe9a9b8,
  muzzle: 0xc4384c,
  muzzleDark: 0x8e1f33,
  eye: 0xe7b21c,
  horn: 0xf1e2b3,
  jacketBlue: 0x2a2fb0,
  jacketWhite: 0xf4f4f8,
  capNavy: 0x1f2c8f,
  patch: 0x9a1d3e,
  briefs: 0xe8e1d4,
  pants: 0x121212,
  pan: 0x1a1a1c,
  patty: 0x6f5f57,
};

// ---------------------------------------------------------------- utilities

function mulberry32(seed) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hash3(x, y, z) {
  let h = Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 1274126177);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

// Smooth 3D value noise in [0, 1].
function noise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const s = (t) => t * t * (3 - 2 * t);
  const u = s(x - xi), v = s(y - yi), w = s(z - zi);
  const l = (a, b, t) => a + (b - a) * t;
  const c = (dx, dy, dz) => hash3(xi + dx, yi + dy, zi + dz);
  return l(
    l(l(c(0, 0, 0), c(1, 0, 0), u), l(c(0, 1, 0), c(1, 1, 0), u), v),
    l(l(c(0, 0, 1), c(1, 0, 1), u), l(c(0, 1, 1), c(1, 1, 1), u), v),
    w,
  );
}

function fbm3(x, y, z) {
  return 0.55 * noise3(x, y, z) + 0.3 * noise3(x * 2.1, y * 2.1, z * 2.1) + 0.15 * noise3(x * 4.3, y * 4.3, z * 4.3);
}

function makeCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  return c;
}

function canvasTexture(canvas, { repeat = [1, 1], srgb = true } = {}) {
  const t = new THREE.CanvasTexture(canvas);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeat[0], repeat[1]);
  t.anisotropy = 4;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// A tileable normal map built from thousands of short random strokes, which reads as fur or felt.
function furNormalTexture({ size = 256, strands = 9000, strength = 2.2, seed = 7, repeat = [4, 4] } = {}) {
  const rnd = mulberry32(seed);
  const h = new Float32Array(size * size);
  for (let i = 0; i < strands; i++) {
    const x0 = rnd() * size, y0 = rnd() * size;
    const a = rnd() * Math.PI * 2;
    const len = 3 + rnd() * 9;
    const amp = 0.3 + rnd() * 0.7;
    for (let t = 0; t < len; t += 0.5) {
      const xi = ((Math.round(x0 + Math.cos(a) * t) % size) + size) % size;
      const yi = ((Math.round(y0 + Math.sin(a) * t) % size) + size) % size;
      const k = yi * size + xi;
      h[k] = Math.max(h[k], amp * (1 - t / len));
    }
  }
  const canvas = makeCanvas(size, size);
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(size, size);
  const at = (x, y) => h[((y + size) % size) * size + ((x + size) % size)];
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const nx = (at(x - 1, y) - at(x + 1, y)) * strength;
      const ny = (at(x, y - 1) - at(x, y + 1)) * strength;
      const len = Math.hypot(nx, ny, 1);
      const o = (y * size + x) * 4;
      img.data[o] = ((nx / len) * 0.5 + 0.5) * 255;
      img.data[o + 1] = ((ny / len) * 0.5 + 0.5) * 255;
      img.data[o + 2] = ((1 / len) * 0.5 + 0.5) * 255;
      img.data[o + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  return canvasTexture(canvas, { repeat, srgb: false });
}

// Blue and white stripes. vertical = true varies along U, otherwise along V.
function stripeTexture(count, vertical, repeat = [1, 1]) {
  const canvas = vertical ? makeCanvas(512, 8) : makeCanvas(8, 512);
  const ctx = canvas.getContext('2d');
  const n = count * 2;
  for (let i = 0; i < n; i++) {
    ctx.fillStyle = i % 2 ? '#f4f4f8' : '#2a2fb0';
    if (vertical) ctx.fillRect((i * 512) / n, 0, 512 / n + 1, 8);
    else ctx.fillRect(0, (i * 512) / n, 8, 512 / n + 1);
  }
  return canvasTexture(canvas, { repeat });
}

function hornTexture() {
  const canvas = makeCanvas(256, 8);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#f1e2b3';
  ctx.fillRect(0, 0, 256, 8);
  ctx.fillStyle = '#161616';
  ctx.fillRect(78, 0, 14, 8);
  ctx.fillRect(150, 0, 14, 8);
  const t = canvasTexture(canvas);
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

// Cap crown: navy front half, white mesh back half, the burger patch at the front.
function capTexture() {
  const W = 1024, H = 256;
  const canvas = makeCanvas(W, H);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#eef0f4';
  ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#b9bfcc';
  for (let y = 0; y < H; y += 6) for (let x = (y / 6) % 2 ? 3 : 0; x < W; x += 6) ctx.fillRect(x, y, 2, 2);
  ctx.fillStyle = '#1f2c8f';
  ctx.fillRect(0, 0, W / 2, H);
  // Patch: a ragged maroon square with white lettering.
  const cx = W / 4, px = 100, top = 58, bottom = 232;
  ctx.fillStyle = '#f2f2f2';
  ctx.fillRect(cx - px - 6, top - 6, px * 2 + 12, bottom - top + 12);
  ctx.fillStyle = '#9a1d3e';
  ctx.fillRect(cx - px, top, px * 2, bottom - top);
  const rnd = mulberry32(11);
  for (let i = 0; i < 1400; i++) {
    ctx.fillStyle = rnd() > 0.5 ? 'rgba(200,60,100,0.5)' : 'rgba(80,10,30,0.45)';
    ctx.fillRect(cx - px + rnd() * px * 2, top + rnd() * (bottom - top), 2, 2);
  }
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.font = 'bold 34px Georgia, "Times New Roman", serif';
  ['BLOODY', 'CADAVER', 'BURGERS'].forEach((word, i) => {
    ctx.save();
    ctx.translate(cx, 98 + i * 46);
    ctx.scale(0.85, 1.45);
    ctx.fillText(word, 0, 0);
    ctx.restore();
  });
  const t = canvasTexture(canvas);
  t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

function nameTagTexture() {
  const canvas = makeCanvas(512, 200);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#1b1b1b';
  ctx.fillRect(0, 0, 512, 200);
  ctx.fillStyle = '#fbfbf7';
  ctx.fillRect(14, 14, 484, 172);
  ctx.fillStyle = '#1b1b1b';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.font = 'italic bold 40px "Comic Sans MS", "Marker Felt", cursive, sans-serif';
  ctx.fillText('HELLO MY NAME IS', 256, 58);
  ctx.fillStyle = '#c21f2b';
  ctx.font = 'bold 72px "Comic Sans MS", "Marker Felt", cursive, sans-serif';
  ctx.fillText('BOVINA', 256, 132);
  const t = canvasTexture(canvas);
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

function pattyTexture() {
  const S = 256;
  const canvas = makeCanvas(S, S);
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(S, S);
  for (let y = 0; y < S; y++) {
    for (let x = 0; x < S; x++) {
      const n = fbm3(x / 9, y / 9, 3.3);
      const speck = hash3(x, y, 5) > 0.93 ? 0.25 : 0;
      const v = 0.72 + (n - 0.5) * 0.5 + speck;
      const o = (y * S + x) * 4;
      img.data[o] = 118 * v;
      img.data[o + 1] = 101 * v;
      img.data[o + 2] = 92 * v;
      img.data[o + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  // Grill hatching.
  ctx.strokeStyle = 'rgba(40,30,28,0.55)';
  ctx.lineWidth = 3;
  for (let i = -S; i < S * 2; i += 18) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i + S * 0.35, S);
    ctx.stroke();
  }
  const t = canvasTexture(canvas);
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

const rgb = (hex) => [(hex >> 16) & 255, (hex >> 8) & 255, hex & 255];

// Bake a colour texture texel by texel. mixAt(u, v) returns 0..1 between colours a and b.
function bakeTexture(w, h, a, b, mixAt) {
  const canvas = makeCanvas(w, h);
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(w, h);
  const ca = rgb(a), cb = rgb(b);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const t = mixAt((x + 0.5) / w, 1 - (y + 0.5) / h);
      const o = (y * w + x) * 4;
      for (let k = 0; k < 3; k++) img.data[o + k] = ca[k] + (cb[k] - ca[k]) * t;
      img.data[o + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  const tex = canvasTexture(canvas);
  tex.wrapT = THREE.ClampToEdgeWrapping;
  return tex;
}

// Cow patches for SphereGeometry UVs: ragged discs around the given directions.
function spherePatchTexture(patches, base, patch) {
  const d = new THREE.Vector3();
  return bakeTexture(1024, 512, base, patch, (u, v) => {
    const phi = u * Math.PI * 2, theta = (1 - v) * Math.PI;
    d.set(-Math.cos(phi) * Math.sin(theta), Math.cos(theta), Math.sin(phi) * Math.sin(theta));
    let edge = Infinity;
    for (const p of patches) {
      const wobble = (fbm3(d.x * 3 + p.seed, d.y * 3, d.z * 3) - 0.5) * 0.35;
      edge = Math.min(edge, d.angleTo(p.dir) - p.r - wobble);
    }
    return THREE.MathUtils.smoothstep(-edge, -0.008, 0.008);
  });
}

// Cow patches for LatheGeometry UVs, from 3D noise over the lathe's surface.
function lathePatchTexture(profile, base, patch, { freq = 5, threshold = 0.57, seed = 0, zScale = 1 } = {}) {
  const n = profile.length - 1;
  return bakeTexture(512, 512, base, patch, (u, v) => {
    const f = v * n, i = Math.min(n - 1, Math.floor(f)), t = f - i;
    const r = THREE.MathUtils.lerp(profile[i].x, profile[i + 1].x, t);
    const y = THREE.MathUtils.lerp(profile[i].y, profile[i + 1].y, t);
    const phi = u * Math.PI * 2;
    const nz = fbm3(Math.sin(phi) * r * freq + seed, y * freq, Math.cos(phi) * r * zScale * freq);
    return THREE.MathUtils.smoothstep(nz, threshold - 0.01, threshold + 0.01);
  });
}

function mixNoiseColors(geo, a, b, freq = 18) {
  const pos = geo.attributes.position;
  const ca = new THREE.Color(a), cb = new THREE.Color(b), c = new THREE.Color();
  const colors = new Float32Array(pos.count * 3);
  for (let i = 0; i < pos.count; i++) {
    const n = fbm3(pos.getX(i) * freq, pos.getY(i) * freq, pos.getZ(i) * freq);
    c.copy(ca).lerp(cb, THREE.MathUtils.smoothstep(n, 0.35, 0.75)).toArray(colors, i * 3);
  }
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  return geo;
}

function ellipsoid(radii, segW = 64, segH = 48) {
  const g = new THREE.SphereGeometry(1, segW, segH);
  g.scale(radii.x, radii.y, radii.z);
  return g;
}

// Point on the front (+Z) of an axis-aligned ellipsoid at a given x, y, with its outward normal.
function ellipsoidFront(center, radii, x, y) {
  const dx = (x - center.x) / radii.x, dy = (y - center.y) / radii.y;
  const k = Math.sqrt(Math.max(0, 1 - dx * dx - dy * dy));
  const p = V(x, y, center.z + radii.z * k);
  const n = V(
    (p.x - center.x) / (radii.x * radii.x),
    (p.y - center.y) / (radii.y * radii.y),
    (p.z - center.z) / (radii.z * radii.z),
  ).normalize();
  return { p, n };
}

// Tube whose radius tapers from r0 to r1 along the curve.
function taperedTube(curve, r0, r1, tubular = 48, radial = 16, closed = false) {
  const g = new THREE.TubeGeometry(curve, tubular, 1, radial, closed);
  const pos = g.attributes.position;
  const v = new THREE.Vector3();
  for (let i = 0; i <= tubular; i++) {
    const t = i / tubular;
    const c = curve.getPointAt(t);
    const r = THREE.MathUtils.lerp(r0, r1, t);
    for (let j = 0; j <= radial; j++) {
      const k = i * (radial + 1) + j;
      v.fromBufferAttribute(pos, k).sub(c).multiplyScalar(r).add(c);
      pos.setXYZ(k, v.x, v.y, v.z);
    }
  }
  g.computeVertexNormals();
  return g;
}

function cylinderBetween(a, b, r0, r1, radial = 16) {
  const dir = b.clone().sub(a);
  const g = new THREE.CylinderGeometry(r1, r0, dir.length(), radial, 1);
  g.translate(0, dir.length() / 2, 0);
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), dir.normalize()));
  g.translate(a.x, a.y, a.z);
  return g;
}

// A clump of hair: thin curved cones, merged into one geometry.
function hairClump(roots, { radius = 0.0045, seed = 1 } = {}) {
  const rnd = mulberry32(seed);
  const up = V(0, 1, 0);
  const geos = [];
  for (const { p, dir, len } of roots) {
    const g = new THREE.ConeGeometry(radius * (0.7 + rnd() * 0.6), len, 4, 4);
    g.translate(0, len / 2, 0);
    const bend = (rnd() - 0.5) * 0.6 * len;
    const pos = g.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const t = pos.getY(i) / len;
      pos.setX(i, pos.getX(i) + bend * t * t);
    }
    g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(up, dir.clone().normalize()));
    g.translate(p.x, p.y, p.z);
    geos.push(g);
  }
  const merged = mergeGeometries(geos);
  merged.computeVertexNormals();
  return merged;
}

function lathe(points, segments = 64, phiStart = 0, phiLength = Math.PI * 2) {
  return new THREE.LatheGeometry(points, segments, phiStart, phiLength);
}

// Smooth a sparse (radius, y) profile into a lathe profile.
function smoothProfile(pts, samples = 60) {
  const curve = new THREE.SplineCurve(pts.map(([r, y]) => new THREE.Vector2(r, y)));
  return curve.getSpacedPoints(samples).map((p) => new THREE.Vector2(Math.max(0, p.x), p.y));
}

function mesh(geo, mat, name) {
  const m = new THREE.Mesh(geo, mat);
  m.name = name;
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

// ---------------------------------------------------------------- character

export function createBovina() {
  const root = new THREE.Group();
  root.name = 'Bovina';

  const furNormal = furNormalTexture({ repeat: [10, 10] });
  const fineFurNormal = furNormalTexture({ seed: 3, repeat: [2, 2], strength: 1.6 });

  const mat = {
    fur: new THREE.MeshPhysicalMaterial({ name: 'Fur', color: COLORS.fur, roughness: 1, normalMap: furNormal, normalScale: new THREE.Vector2(0.35, 0.35), sheen: 1, sheenColor: 0xffffff, sheenRoughness: 0.7 }),
    mask: new THREE.MeshStandardMaterial({
      name: 'Mask',
      roughness: 0.55,
      map: spherePatchTexture([
        { dir: V(0.6, 0.45, 0.65).normalize(), r: 0.5, seed: 1 },
        { dir: V(-0.35, 0.8, 0.5).normalize(), r: 0.22, seed: 2 },
        { dir: V(0.8, -0.35, 0.5).normalize(), r: 0.3, seed: 3 },
        { dir: V(-0.75, -0.25, 0.55).normalize(), r: 0.13, seed: 4 },
        { dir: V(0.2, 0.3, -0.9).normalize(), r: 0.45, seed: 5 },
      ], COLORS.mask, COLORS.black),
    }),
    maskWhite: new THREE.MeshStandardMaterial({ name: 'MaskWhite', color: COLORS.mask, roughness: 0.55 }),
    maskBlack: new THREE.MeshStandardMaterial({ name: 'MaskBlack', color: COLORS.black, roughness: 0.55 }),
    black: new THREE.MeshStandardMaterial({ name: 'BlackFur', color: COLORS.black, roughness: 0.8 }),
    udder: new THREE.MeshStandardMaterial({ name: 'Udder', color: COLORS.udder, roughness: 0.8, normalMap: fineFurNormal, normalScale: new THREE.Vector2(0.25, 0.25) }),
    teat: new THREE.MeshStandardMaterial({ name: 'Teat', color: COLORS.teat, roughness: 0.7 }),
    muzzle: new THREE.MeshStandardMaterial({ name: 'Muzzle', vertexColors: true, roughness: 1, normalMap: fineFurNormal, normalScale: new THREE.Vector2(1.5, 1.5) }),
    nostril: new THREE.MeshStandardMaterial({ name: 'Nostril', color: 0x231419, roughness: 0.9 }),
    eye: new THREE.MeshStandardMaterial({ name: 'Eye', color: COLORS.eye, roughness: 0.15, metalness: 0.05 }),
    pupil: new THREE.MeshStandardMaterial({ name: 'Pupil', color: 0x0a0a0a, roughness: 0.1 }),
    horn: new THREE.MeshStandardMaterial({ name: 'Horn', map: hornTexture(), roughness: 0.5 }),
    jacket: new THREE.MeshStandardMaterial({ name: 'Jacket', map: stripeTexture(34, true), roughness: 0.55, side: THREE.DoubleSide }),
    sleeve: new THREE.MeshStandardMaterial({ name: 'Sleeve', map: stripeTexture(7, false), roughness: 0.55 }),
    zipper: new THREE.MeshStandardMaterial({ name: 'Zipper', color: 0xd9d9df, roughness: 0.3, metalness: 0.6 }),
    capCrown: new THREE.MeshStandardMaterial({ name: 'CapCrown', map: capTexture(), roughness: 0.7 }),
    capNavy: new THREE.MeshStandardMaterial({ name: 'CapNavy', color: COLORS.capNavy, roughness: 0.7 }),
    tag: new THREE.MeshStandardMaterial({ name: 'NameTag', map: nameTagTexture(), roughness: 0.4 }),
    briefs: new THREE.MeshStandardMaterial({ name: 'Briefs', color: COLORS.briefs, roughness: 0.8, normalMap: fineFurNormal, normalScale: new THREE.Vector2(0.3, 0.3) }),
    glove: new THREE.MeshStandardMaterial({ name: 'Glove', color: 0x0e0e0e, roughness: 0.35 }),
    pan: new THREE.MeshStandardMaterial({ name: 'Pan', color: COLORS.pan, roughness: 0.35, metalness: 0.4, side: THREE.DoubleSide }),
    patty: new THREE.MeshStandardMaterial({ name: 'Patty', map: pattyTexture(), roughness: 0.9 }),
    pattySide: new THREE.MeshStandardMaterial({ name: 'PattySide', color: 0x5f514b, roughness: 0.95 }),
  };

  // ------------------------------------------------------------- torso
  const torsoCenterX = X(1160);
  const torsoZ = 0.7; // front-to-back squash of the round torso
  const torsoProfile = [
    [0, 745], [0.15, 760], [0.3, 792], [0.42, 830], [0.44, 880], [0.425, 960],
    [0.405, 1050], [0.375, 1150], [0.345, 1250], [0.32, 1330], [0.28, 1390], [0.2, 1430], [0, 1442],
  ];
  const torsoRadiusAt = (py) => {
    for (let i = 0; i < torsoProfile.length - 1; i++) {
      const [r0, y0] = torsoProfile[i], [r1, y1] = torsoProfile[i + 1];
      if (py >= y0 && py <= y1) return THREE.MathUtils.lerp(r0, r1, (py - y0) / (y1 - y0));
    }
    return 0;
  };
  // Point on the torso surface at photo pixel (px, py), plus its outward normal.
  const torsoSurface = (px, py, front = true) => {
    const r = torsoRadiusAt(py);
    const dx = X(px) - torsoCenterX;
    const z = Math.sqrt(Math.max(0, r * r - dx * dx)) * torsoZ * (front ? 1 : -1);
    return { p: V(X(px), Y(py), z), n: V(dx, 0.15, z / (torsoZ * torsoZ)).normalize() };
  };

  const torsoGeo = lathe(smoothProfile(torsoProfile.map(([r, py]) => [r, Y(py)])), 72);
  const torso = mesh(torsoGeo, mat.fur, 'Torso');
  torso.position.x = torsoCenterX;
  torso.scale.z = torsoZ;
  root.add(torso);

  const bellyCenter = V(X(1090), Y(1220), 0.12);
  const bellyRadii = V(0.33, 0.27, 0.3);
  root.add(mesh(ellipsoid(bellyRadii).translate(bellyCenter.x, bellyCenter.y, bellyCenter.z), mat.fur, 'Belly'));

  // Udders: two big pink breasts, each with two teats.
  const breasts = [
    { c: V(X(995), Y(958), 0.3), teats: [[845, 1015, -0.9], [905, 1080, 0.15]] },
    { c: V(X(1170), Y(962), 0.3), teats: [[1085, 1075, -0.35], [1205, 1045, 0.1]] },
  ];
  const breastRadii = V(0.15, 0.13, 0.14);
  breasts.forEach((b, i) => {
    root.add(mesh(ellipsoid(breastRadii).translate(b.c.x, b.c.y, b.c.z), mat.udder, `Udder${i + 1}`));
    b.teats.forEach(([px, py, sideways], j) => {
      const dir = V(X(px) - b.c.x, Y(py) - b.c.y, 0.06).normalize();
      const base = b.c.clone().add(V(dir.x * breastRadii.x, dir.y * breastRadii.y, dir.z * breastRadii.z).multiplyScalar(0.92));
      const out = V(dir.x + sideways * 0.3, dir.y - 0.25, dir.z + 0.35).normalize();
      const g = new THREE.CapsuleGeometry(0.018, 0.055, 6, 12);
      g.translate(0, 0.035, 0);
      g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), out));
      g.translate(base.x, base.y, base.z);
      root.add(mesh(g, mat.teat, `Teat${i + 1}${j + 1}`));
    });
  });

  // Black belly hair: a ragged patch hanging off the front of the belly.
  {
    const rnd = mulberry32(21);
    const roots = [];
    const cx = X(1075), cy = Y(1262);
    for (let i = 0; i < 900; i++) {
      const a = rnd() * Math.PI * 2;
      const edge = 0.15 * (1 + 0.28 * Math.sin(3 * a + 1) + 0.15 * Math.sin(5 * a));
      const r = Math.sqrt(rnd()) * edge;
      const x = cx + Math.cos(a) * r * 0.95, y = cy + Math.sin(a) * r * 1.05;
      const { p, n } = ellipsoidFront(bellyCenter, bellyRadii, x, y);
      const dir = n.clone().multiplyScalar(0.55).add(V((rnd() - 0.5) * 0.9, -0.55 - rnd() * 0.3, (rnd() - 0.5) * 0.3));
      roots.push({ p: p.addScaledVector(n, -0.004), dir, len: 0.05 + rnd() * 0.07 * (1 - r / edge * 0.5) });
    }
    root.add(mesh(hairClump(roots, { radius: 0.005, seed: 22 }), mat.black, 'BellyHair'));
  }

  // Black shoulder fur sticking up on the viewer's-left shoulder.
  {
    const rnd = mulberry32(31);
    const roots = [];
    for (let i = 0; i < 420; i++) {
      const px = 905 + rnd() * 110, py = 775 + rnd() * 80;
      const { p, n } = torsoSurface(px, py);
      const dir = n.clone().multiplyScalar(0.7).add(V(-0.35 - rnd() * 0.4, 0.5 + rnd() * 0.5, (rnd() - 0.5) * 0.5));
      roots.push({ p, dir, len: 0.05 + rnd() * 0.09 });
    }
    root.add(mesh(hairClump(roots, { radius: 0.006, seed: 32 }), mat.black, 'ShoulderFur'));
  }

  // ------------------------------------------------------------- jacket
  // Same lathe as the torso but a little bigger, with the front cut open.
  const jacketProfile = smoothProfile(
    torsoProfile.filter(([, py]) => py >= 775 && py <= 1400).map(([r, py]) => [r * 1.06 + 0.012, Y(py)]),
    60,
  );
  const openRight = 0.45; // zipper side, viewer's right
  const openLeft = 1.2; // viewer's left, mostly hidden by the arm
  const jacket = mesh(lathe(jacketProfile, 72, openRight, Math.PI * 2 - openRight - openLeft), mat.jacket, 'Jacket');
  jacket.position.x = torsoCenterX;
  jacket.scale.z = torsoZ;
  root.add(jacket);

  // Zipper running down the open edge.
  {
    const pts = jacketProfile.filter((_, i) => i % 3 === 0).map((p) => V(torsoCenterX + Math.sin(openRight) * p.x, p.y, Math.cos(openRight) * p.x * torsoZ));
    const zip = mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 60, 0.007, 6), mat.zipper, 'Zipper');
    root.add(zip);
  }

  // Collar folded round the back of the neck.
  {
    const collar = mesh(new THREE.TorusGeometry(0.2, 0.035, 12, 48, Math.PI * 1.35), mat.jacket, 'Collar');
    collar.rotation.set(Math.PI / 2, 0, Math.PI * 0.18 - Math.PI);
    collar.position.set(torsoCenterX, Y(785), -0.01);
    collar.scale.set(1.15, 0.8, 1);
    root.add(collar);
  }

  // Name tag on the right chest, laid on the jacket surface.
  {
    const phi = 0.66, py = 818;
    const r = torsoRadiusAt(py) * 1.06 + 0.02;
    const p = V(torsoCenterX + Math.sin(phi) * r, Y(py), Math.cos(phi) * r * torsoZ);
    const tag = mesh(new THREE.PlaneGeometry(0.15, 0.058), mat.tag, 'NameTag');
    tag.position.copy(p);
    tag.rotation.set(-0.3, Math.atan2(Math.sin(phi), Math.cos(phi) / torsoZ), -0.12);
    root.add(tag);
  }

  // ------------------------------------------------------------- arms
  const addArm = (name, pts, r0, r1) => {
    const curve = new THREE.CatmullRomCurve3(pts);
    root.add(mesh(taperedTube(curve, r0, r1, 48, 20), mat.sleeve, `${name}Sleeve`));
    root.add(mesh(new THREE.SphereGeometry(r0 * 1.02, 24, 16).translate(pts[0].x, pts[0].y, pts[0].z), mat.jacket, `${name}Shoulder`));
    const end = curve.getPointAt(1);
    const cuff = mesh(new THREE.TorusGeometry(r1 * 0.95, 0.018, 8, 24), mat.jacket, `${name}Cuff`);
    cuff.position.copy(end);
    cuff.quaternion.setFromUnitVectors(V(0, 0, 1), curve.getTangentAt(1));
    root.add(cuff);
    return curve;
  };

  // Viewer's-left arm, bent forward to hold the pan.
  addArm('ArmR', [V(X(890), Y(845), -0.03), V(X(820), Y(1000), 0.0), V(X(798), Y(1165), 0.07), V(X(790), Y(1290), 0.2)], 0.095, 0.078);
  const handR = V(X(785), Y(1345), 0.25);
  root.add(mesh(ellipsoid(V(0.062, 0.078, 0.062), 32, 24).translate(handR.x, handR.y, handR.z), mat.fur, 'MittenR'));

  // Viewer's-right arm, hanging down: white mitten over a black glove.
  addArm('ArmL', [V(X(1432), Y(850), -0.03), V(X(1495), Y(1000), -0.01), V(X(1505), Y(1180), 0.02), V(X(1472), Y(1425), 0.06)], 0.105, 0.088);
  root.add(mesh(ellipsoid(V(0.075, 0.1, 0.072), 32, 24).translate(X(1456), Y(1485), 0.07), mat.fur, 'MittenL'));
  {
    const glove = new THREE.Group();
    glove.name = 'GloveL';
    glove.add(mesh(ellipsoid(V(0.045, 0.085, 0.032), 32, 24), mat.glove, 'GloveLPalm'));
    const thumb = mesh(new THREE.CapsuleGeometry(0.014, 0.05, 6, 10), mat.glove, 'GloveLThumb');
    thumb.position.set(-0.035, 0.01, 0.02);
    thumb.rotation.z = -0.6;
    glove.add(thumb);
    glove.position.set(X(1405), Y(1592), 0.085);
    glove.rotation.z = -0.35;
    root.add(glove);
  }

  // ------------------------------------------------------------- frying pan and patties
  {
    const pan = new THREE.Group();
    pan.name = 'FryingPan';
    const center = V(X(650), Y(1512), 0.4);
    const normal = V(0.12, 0.72, 0.68).normalize();
    pan.position.copy(center);
    pan.quaternion.setFromUnitVectors(V(0, 1, 0), normal);

    const R = 0.245;
    pan.add(mesh(lathe(smoothProfile([[0, 0], [0.19, 0], [0.214, 0.01], [0.232, 0.035], [R, 0.058]], 24), 64), mat.pan, 'PanBody'));
    const rim = mesh(new THREE.TorusGeometry(R, 0.006, 8, 64), mat.pan, 'PanRim');
    rim.rotation.x = Math.PI / 2;
    rim.position.y = 0.058;
    pan.add(rim);

    // Patties: slightly lumpy discs with grill-marked tops.
    [[0.035, -0.105, 0.3], [-0.085, 0.07, 1.4], [0.1, 0.055, 2.2]].forEach(([x, z, rot], i) => {
      const g = new THREE.CylinderGeometry(0.086, 0.09, 0.024, 40, 1);
      const pos = g.attributes.position;
      for (let k = 0; k < pos.count; k++) {
        const a = Math.atan2(pos.getZ(k), pos.getX(k));
        const s = 1 + (noise3(Math.cos(a) * 2 + i * 5, Math.sin(a) * 2, 0) - 0.5) * 0.12;
        pos.setX(k, pos.getX(k) * s);
        pos.setZ(k, pos.getZ(k) * s);
      }
      g.computeVertexNormals();
      const patty = mesh(g, [mat.pattySide, mat.patty, mat.pattySide], `Patty${i + 1}`);
      patty.position.set(x, 0.013 + i * 0.001, z);
      patty.rotation.y = rot;
      pan.add(patty);
    });
    root.add(pan);

    // Handle: from the rim to (and through) the mitten.
    const toHand = handR.clone().sub(center);
    const inPlane = toHand.clone().addScaledVector(normal, -toHand.dot(normal)).normalize();
    const start = center.clone().addScaledVector(inPlane, R - 0.01).addScaledVector(normal, 0.05);
    const end = handR.clone().addScaledVector(inPlane, 0.07);
    root.add(mesh(cylinderBetween(start, end, 0.016, 0.019, 12), mat.pan, 'PanHandle'));
  }

  // ------------------------------------------------------------- briefs, legs, shoes
  {
    const prof = smoothProfile([[0.345 * 1.05, 1355], [0.32 * 1.05, 1392], [0.26, 1422], [0.18, 1446], [0, 1458]].map(([r, py]) => [r, Y(py)]), 30);
    const briefs = mesh(lathe(prof, 64), mat.briefs, 'Briefs');
    briefs.position.x = torsoCenterX;
    briefs.scale.z = 0.9;
    root.add(briefs);
  }

  [[1045, 3], [1275, 9]].forEach(([px, seed], i) => {
    const top = Y(1428);
    const prof = smoothProfile([[0, Y(1418)], [0.16, top], [0.165, top * 0.88], [0.14, top * 0.64], [0.11, top * 0.44], [0.092, top * 0.24], [0.075, top * 0.1], [0.07, 0.07], [0, 0.065]], 50);
    const g = lathe(prof, 48);
    g.scale(1, 1, 0.85);
    const pants = new THREE.MeshStandardMaterial({ name: `Pants${i + 1}`, roughness: 0.75, map: lathePatchTexture(prof, COLORS.pants, 0xe9e7e2, { seed, zScale: 0.85 }) });
    const leg = mesh(g, pants, `Leg${i + 1}`);
    leg.position.x = X(px);
    root.add(leg);
    const shoe = mesh(ellipsoid(V(0.08, 0.055, 0.14), 32, 16).translate(X(px), 0.055, 0.045), mat.glove, `Shoe${i + 1}`);
    root.add(shoe);
  });

  // ------------------------------------------------------------- head
  const head = new THREE.Group();
  head.name = 'Head';
  head.position.set(X(1125), Y(760), 0.02);
  head.rotation.set(0.04, 0.24, -0.04);
  head.scale.set(1.2, 1.3, 1.2);
  root.add(head);

  const headC = V(0, 0.19, 0);
  const headR = V(0.185, 0.19, 0.17);
  {
    // Mask: an egg-shaped shell, narrower at the top, painted with black patches.
    const g = new THREE.SphereGeometry(1, 96, 72);
    const pos = g.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i);
      const pinch = 1 - 0.14 * Math.max(0, y);
      pos.setXYZ(i, pos.getX(i) * pinch * headR.x, y * headR.y, pos.getZ(i) * headR.z);
    }
    g.computeVertexNormals();
    g.translate(headC.x, headC.y, headC.z);
    head.add(mesh(g, mat.mask, 'Mask'));
  }
  // Fur hood around the back of the mask, and the fur topknot the horns sit in.
  head.add(mesh(ellipsoid(V(0.2, 0.2, 0.16)).translate(0, 0.2, -0.06), mat.fur, 'Hood'));
  head.add(mesh(ellipsoid(V(0.125, 0.1, 0.11), 32, 24).translate(-0.01, 0.39, -0.035), mat.fur, 'Topknot'));

  // Eyes: yellow, close set, under heavy scowling brows.
  [-1, 1].forEach((s) => {
    const { p, n } = ellipsoidFront(headC, headR, s * 0.064, 0.235);
    const eyeC = p.clone().addScaledVector(n, -0.012);
    head.add(mesh(new THREE.SphereGeometry(0.027, 32, 24).translate(eyeC.x, eyeC.y, eyeC.z), mat.eye, s < 0 ? 'EyeR' : 'EyeL'));
    const pupil = eyeC.clone().addScaledVector(n, 0.024);
    head.add(mesh(ellipsoid(V(0.009, 0.009, 0.005), 16, 12).translate(pupil.x, pupil.y, pupil.z), mat.pupil, s < 0 ? 'PupilR' : 'PupilL'));

    // Upper lid: half a shell over the eye, angled down toward the nose.
    // The viewer's-right eye sits inside the black patch, so its lid and brow are black.
    const skin = s > 0 ? mat.maskBlack : mat.maskWhite;
    const lid = mesh(new THREE.SphereGeometry(0.031, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.42), skin, s < 0 ? 'LidR' : 'LidL');
    lid.position.copy(eyeC);
    lid.rotation.set(0.55, 0, s * 0.45);
    head.add(lid);

    const brow = mesh(ellipsoid(V(0.058, 0.017, 0.028), 32, 16), skin, s < 0 ? 'BrowR' : 'BrowL');
    const b = ellipsoidFront(headC, headR, s * 0.062, 0.272);
    brow.position.copy(b.p).addScaledVector(b.n, -0.008);
    brow.rotation.set(0.2, s * 0.35, s * 0.42);
    head.add(brow);
  });
  // Furrow between the brows.
  {
    const f = ellipsoidFront(headC, headR, 0, 0.255);
    const furrow = mesh(ellipsoid(V(0.012, 0.034, 0.018), 16, 12), mat.maskWhite, 'Furrow');
    furrow.position.copy(f.p).addScaledVector(f.n, -0.006);
    head.add(furrow);
  }

  // Muzzle: fuzzy red snout with two vertical nostril slits.
  {
    const mC = V(0, 0.103, 0.138);
    const mR = V(0.104, 0.07, 0.078);
    const g = mixNoiseColors(ellipsoid(mR, 48, 32), COLORS.muzzle, COLORS.muzzleDark, 22);
    g.translate(mC.x, mC.y, mC.z);
    head.add(mesh(g, mat.muzzle, 'Muzzle'));
    [-1, 1].forEach((s) => {
      const { p, n } = ellipsoidFront(mC, mR, s * 0.032, 0.1);
      const slit = mesh(new THREE.CapsuleGeometry(0.0075, 0.04, 4, 10), mat.nostril, s < 0 ? 'NostrilR' : 'NostrilL');
      slit.position.copy(p).addScaledVector(n, -0.004);
      slit.rotation.y = Math.atan2(n.x, n.z);
      head.add(slit);
    });
  }

  // Horns: short, stubby, ringed with two black bands.
  {
    const hornL = new THREE.CatmullRomCurve3([V(-0.07, 0.45, 0.0), V(-0.125, 0.455, 0.015), V(-0.165, 0.475, 0.025), V(-0.178, 0.505, 0.015)]);
    const hornR = new THREE.CatmullRomCurve3([V(0.05, 0.45, 0.0), V(0.105, 0.457, 0.015), V(0.145, 0.478, 0.02), V(0.155, 0.51, 0.01)]);
    [[hornL, 'HornR'], [hornR, 'HornL']].forEach(([c, name]) => {
      head.add(mesh(taperedTube(c, 0.028, 0.011, 32, 16), mat.horn, name));
      const tip = c.getPointAt(1);
      head.add(mesh(new THREE.SphereGeometry(0.011, 12, 8).translate(tip.x, tip.y, tip.z), mat.horn, `${name}Tip`));
    });
    // Wiry black whisker curling off the left horn.
    const wire = new THREE.CatmullRomCurve3([
      V(-0.172, 0.5, 0.015), V(-0.18, 0.545, 0.02), V(-0.15, 0.585, 0.03), V(-0.12, 0.575, 0.02),
      V(-0.13, 0.615, 0.02), V(-0.1, 0.64, 0.015), V(-0.075, 0.625, 0.01),
    ]);
    head.add(mesh(new THREE.TubeGeometry(wire, 64, 0.0028, 6), mat.black, 'Whisker'));
    const sprig = new THREE.CatmullRomCurve3([V(-0.15, 0.585, 0.03), V(-0.18, 0.6, 0.025), V(-0.19, 0.63, 0.02)]);
    head.add(mesh(new THREE.TubeGeometry(sprig, 24, 0.0022, 6), mat.black, 'WhiskerSprig'));
  }

  // Trucker cap perched on top, brim toward the front-left.
  {
    const cap = new THREE.Group();
    cap.name = 'Cap';
    const r = 0.19;
    const crown = mesh(new THREE.SphereGeometry(r, 64, 24, 0, Math.PI * 2, 0, Math.PI / 2), mat.capCrown, 'CapCrown');
    crown.scale.set(1, 0.62, 1.08);
    cap.add(crown);
    const button = mesh(new THREE.SphereGeometry(0.012, 12, 8), mat.capNavy, 'CapButton');
    button.position.y = r * 0.62;
    cap.add(button);
    const band = mesh(new THREE.TorusGeometry(r, 0.006, 6, 64), mat.capNavy, 'CapBand');
    band.rotation.x = Math.PI / 2;
    band.scale.set(1, 1.08, 1);
    cap.add(band);

    // Crescent: outer edge sweeps out in front, inner edge follows the crown.
    const brimPts = [];
    for (let i = 0; i <= 48; i++) {
      const a = (i / 48) * Math.PI;
      brimPts.push(new THREE.Vector2(Math.cos(a) * r, Math.sin(a) * (r * 1.08 + 0.15)));
    }
    for (let i = 48; i >= 0; i--) {
      const a = (i / 48) * Math.PI;
      brimPts.push(new THREE.Vector2(Math.cos(a) * r * 0.97, Math.sin(a) * r * 1.05));
    }
    const brimShape = new THREE.Shape(brimPts);
    const brimGeo = new THREE.ExtrudeGeometry(brimShape, { depth: 0.008, bevelEnabled: true, bevelThickness: 0.003, bevelSize: 0.003, bevelSegments: 2, curveSegments: 48 });
    const brim = mesh(brimGeo, mat.capNavy, 'CapBrim');
    brim.rotation.x = Math.PI / 2 + 0.06; // tipped slightly up at the front
    brim.position.y = 0.006;
    cap.add(brim);
    const lining = mesh(new THREE.CircleGeometry(r, 64), mat.capNavy, 'CapLining');
    lining.rotation.x = Math.PI / 2;
    lining.scale.set(1, 1.08, 1);
    cap.add(lining);

    cap.position.set(0.07, 0.51, -0.02);
    cap.rotation.set(0.22, -0.5, 0.12);
    head.add(cap);
  }

  // ------------------------------------------------------------- finish
  // Rescale so the character stands about 1.85 units tall with feet on y = 0.
  root.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(root);
  const s = 1.85 / box.max.y;
  root.scale.setScalar(s);

  return root;
}
