// "Cow 64": a low-poly, Mario-proportioned version of The Misanthropic Cow.
//
// Instead of retargeting, each body part is a rigid mesh authored in the local frame
// of one of Mario's 20 animated parts (the way Mario's own N64 model is built), and is
// attached to the hidden Mario model's scene graph. Every Mario animation, the punch /
// kick scaling and the crawl/slide floor alignment therefore fit it exactly.
//
// Local frames (Mario model units, 4 per in-game unit): torso, butt and head have
// X = up, Y = forward, Z = the character's left. Limbs extend along +X from the joint.
// Feet: X = toward the toes, +Y = toward the sole. Right-side parts mirror the left in Z.

import * as THREE from 'three';

// Cow 64 is drawn a little larger than Mario (scaled from the feet; collision is unchanged).
export const COW64_SCALE = 1.2;

// ---------------------------------------------------------------------------
// Textures (small canvases, N64-sized)

function canvasTex(w, h, draw) {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = THREE.RepeatWrapping;
  t.wrapT = THREE.ClampToEdgeWrapping;
  t.anisotropy = 4;
  return t;
}

// Seeded so the cow looks the same every time
function rng(seed) {
  let s = seed;
  return () => ((s = (s * 16807) % 2147483647) / 2147483647);
}

function furNoise(g, w, h, rand, base, light, dark, n = 900) {
  g.fillStyle = base;
  g.fillRect(0, 0, w, h);
  for (let i = 0; i < n; i++) {
    g.fillStyle = rand() < 0.5 ? light : dark;
    g.fillRect(rand() * w, rand() * h, 2, 2);
  }
}

/** A shaggy black patch: a blob with ragged tufts around its edge. */
function shagPatch(g, rand, cx, cy, rx, ry) {
  g.fillStyle = '#141414';
  g.beginPath();
  g.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
  g.fill();
  for (let i = 0; i < 60; i++) {
    const a = rand() * Math.PI * 2;
    const r = 0.8 + rand() * 0.35;
    const x = cx + Math.cos(a) * rx * r, y = cy + Math.sin(a) * ry * r;
    g.beginPath();
    g.moveTo(x, y);
    g.lineTo(x + Math.cos(a + 0.3) * 7, y + Math.sin(a + 0.3) * 7 + 3);
    g.lineTo(x + Math.cos(a - 0.3) * 6, y + Math.sin(a - 0.3) * 6 + 4);
    g.fill();
  }
}

// Sphere UVs (see ellipsoid()): u = 0.25 front, 0.5 left side, 0.75 back, 0/1 right side;
// canvas y = 0 at the top of the part.
function makeTextures() {
  const r = rng(7);
  const fur = canvasTex(64, 64, (g, w, h) => furNoise(g, w, h, r, '#f1eee6', '#ffffff', '#d9d4c8'));
  const body = canvasTex(256, 128, (g, w, h) => {
    furNoise(g, w, h, r, '#f1eee6', '#ffffff', '#d9d4c8', 3000);
    shagPatch(g, r, 0.25 * w, 0.74 * h, 30, 20); // lower belly, front
    shagPatch(g, r, 0.12 * w, 0.22 * h, 18, 14); // chest/shoulder on the cow's right
    shagPatch(g, r, 0.70 * w, 0.42 * h, 14, 18); // lower back, left
  });
  const hips = canvasTex(256, 64, (g, w, h) => {
    g.fillStyle = '#18181a';
    g.fillRect(0, 0, w, h);
    g.fillStyle = '#f2a9c4'; // pink satin panties at the front
    g.beginPath();
    g.ellipse(0.25 * w, 0.18 * h, 0.16 * w, 0.42 * h, 0, 0, Math.PI * 2);
    g.fill();
    g.fillStyle = '#f1eee6';
    g.fillRect(0, 0, w, 0.1 * h); // suit hem
  });
  const leggings = canvasTex(128, 64, (g, w, h) => {
    g.fillStyle = '#18181a';
    g.fillRect(0, 0, w, h);
    const rr = rng(11);
    for (let i = 0; i < 7; i++) {
      const x = rr() * w, y = 8 + rr() * (h - 16), s = 6 + rr() * 6;
      g.fillStyle = '#ecebe6';
      for (let k = 0; k < 9; k++) {
        g.beginPath();
        g.arc(x + (rr() - 0.5) * s, y + (rr() - 0.5) * s, s * (0.4 + rr() * 0.4), 0, Math.PI * 2);
        g.fill();
      }
    }
  });
  const terry = canvasTex(64, 64, (g, w, h) => furNoise(g, w, h, r, '#e7dcc4', '#f4ecd8', '#cfc2a6', 1400));
  const slipperFace = canvasTex(128, 64, (g, w, h) => {
    furNoise(g, w, h, r, '#ece6d6', '#fbf7ee', '#cfc6b4', 1500);
    g.strokeStyle = '#d23a6e';
    g.lineWidth = 3;
    g.beginPath();
    g.arc(0.5 * w, 0.38 * h, 0.16 * w, 0.15 * Math.PI, 0.85 * Math.PI); // embroidered smile
    g.stroke();
    g.fillStyle = '#e04b7d';
    for (const x of [0.38, 0.62]) {
      g.beginPath();
      g.ellipse(x * w, 0.2 * h, 6, 4, 0, 0, Math.PI * 2);
      g.fill();
    }
  });
  const horn = canvasTex(16, 64, (g, w, h) => {
    g.fillStyle = '#f4c51c';
    g.fillRect(0, 0, w, h);
    g.fillStyle = '#1a1a1a';
    for (const y of [0.15, 0.42, 0.7]) g.fillRect(0, y * h, w, 0.09 * h);
  });
  horn.wrapT = THREE.RepeatWrapping;
  return { fur, body, hips, leggings, terry, slipperFace, horn };
}

/** Fallback face, drawn in the mask's style, when the detailed model isn't available. */
function drawnFace() {
  const r = rng(3);
  return canvasTex(128, 128, (g, w, h) => {
    furNoise(g, w, h, r, '#f3f1ec', '#ffffff', '#d8d5ce', 2000);
    shagPatch(g, r, 0.78 * w, 0.32 * h, 22, 30);
    shagPatch(g, r, 0.2 * w, 0.18 * h, 16, 12);
    for (const x of [0.33, 0.67]) {
      g.fillStyle = '#2a1d16';
      g.beginPath();
      g.ellipse(x * w, 0.42 * h, 15, 10, 0, 0, Math.PI * 2);
      g.fill();
      g.fillStyle = '#d99a1e';
      g.beginPath();
      g.arc(x * w, 0.43 * h, 6, 0, Math.PI * 2);
      g.fill();
      g.fillStyle = '#000';
      g.beginPath();
      g.arc(x * w, 0.43 * h, 2.5, 0, Math.PI * 2);
      g.fill();
    }
    g.strokeStyle = '#3a2a22'; // scowling brows
    g.lineWidth = 5;
    g.beginPath();
    g.moveTo(0.18 * w, 0.27 * h); g.lineTo(0.45 * w, 0.35 * h);
    g.moveTo(0.82 * w, 0.27 * h); g.lineTo(0.55 * w, 0.35 * h);
    g.stroke();
  });
}

/**
 * Render the detailed model's mask (front view, unlit) into a texture, so the low-poly
 * head wears the real face. Returns { texture, aspect } or null.
 */
export function bakeFaceFromGltf(renderer, gltf) {
  const scene = gltf.scene;
  const masks = [];
  scene.traverse((o) => { if (o.isMesh && /^Mask_(scanned_face|lower_jaw)/.test(o.name)) masks.push(o); });
  if (!masks.length) return null;
  scene.updateMatrixWorld(true);
  const box = new THREE.Box3();
  for (const m of masks) box.expandByObject(m);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const pad = 1.04;
  const hw = (size.x / 2) * pad, hh = (size.y / 2) * pad;

  // Draw the real (skinned, quantized) meshes in their rest pose with unlit materials;
  // everything else in the model is hidden for the bake and restored afterwards.
  const saved = [];
  scene.traverse((o) => {
    if (!o.isMesh) return;
    saved.push([o, o.visible, o.material]);
    if (masks.includes(o)) {
      o.material = new THREE.MeshBasicMaterial({ map: o.material.map || null, color: o.material.map ? 0xffffff : o.material.color });
    } else {
      o.visible = false;
    }
  });
  const prevBackground = scene.background;
  scene.background = new THREE.Color(0xf1eee6);
  const cam = new THREE.OrthographicCamera(-hw, hw, hh, -hh, 0.001, 10);
  cam.position.set(center.x, center.y, box.max.z + 1);
  cam.lookAt(center.x, center.y, center.z);
  const W = 256, H = Math.round(256 * (hh / hw));
  const target = new THREE.WebGLRenderTarget(W, H, { colorSpace: THREE.SRGBColorSpace });
  const prevTarget = renderer.getRenderTarget();
  renderer.setRenderTarget(target);
  renderer.render(scene, cam);
  const pixels = new Uint8Array(W * H * 4);
  renderer.readRenderTargetPixels(target, 0, 0, W, H, pixels);
  for (let i = 0; i < pixels.length; i += 4) { // outside the mask: hood-coloured fur
    if (pixels[i + 3] < 200) { pixels[i] = 241; pixels[i + 1] = 238; pixels[i + 2] = 230; pixels[i + 3] = 255; }
  }
  renderer.setRenderTarget(prevTarget);
  target.dispose();
  scene.background = prevBackground;
  for (const [o, visible, material] of saved) {
    if (o.material !== material) o.material.dispose();
    o.visible = visible;
    o.material = material;
  }
  const tex = new THREE.DataTexture(pixels, W, H, THREE.RGBAFormat);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.magFilter = THREE.LinearFilter;
  tex.minFilter = THREE.LinearFilter;
  tex.generateMipmaps = false;
  tex.needsUpdate = true;
  return { texture: tex, aspect: hh / hw };
}

// ---------------------------------------------------------------------------
// Geometry helpers (all in a part's local frame)

const P = new THREE.Matrix4().set( // sphere pole axis (y) -> local X (up), z -> local Y (forward), x -> local Z
  0, 1, 0, 0,
  0, 0, 1, 0,
  1, 0, 0, 0,
  0, 0, 0, 1);

function ellipsoid(c, r, segW = 12, segH = 8, phi = [0, Math.PI * 2], theta = [0, Math.PI]) {
  const g = new THREE.SphereGeometry(1, segW, segH, phi[0], phi[1], theta[0], theta[1]);
  g.applyMatrix4(P);
  g.scale(r[0], r[1], r[2]);
  g.translate(c[0], c[1], c[2]);
  return g;
}

/** Tapered tube along +X from x0 to x1 (radii in Y and Z), optionally offset. */
function tube(x0, x1, r0, r1, seg = 8, off = [0, 0], squash = 1) {
  const g = new THREE.CylinderGeometry(r1, r0, x1 - x0, seg, 1, false);
  g.rotateZ(-Math.PI / 2); // +Y -> +X
  g.scale(1, 1, squash);
  g.translate((x0 + x1) / 2, off[0], off[1]);
  return g;
}

/** Cone from base point toward tip. */
function cone(base, tip, radius, seg = 7) {
  const a = new THREE.Vector3(...base), b = new THREE.Vector3(...tip);
  const len = a.distanceTo(b);
  const g = new THREE.ConeGeometry(radius, len, seg, 1);
  g.translate(0, len / 2, 0);
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
  g.applyQuaternion(q);
  g.translate(a.x, a.y, a.z);
  return g;
}

/** Planar UVs from local (Z, X): image left = the cow's right. */
function planarUV(g, zMin, zMax, xMin, xMax) {
  const pos = g.attributes.position, uv = g.attributes.uv;
  for (let i = 0; i < pos.count; i++) {
    uv.setXY(i, (pos.getZ(i) - zMin) / (zMax - zMin), (pos.getX(i) - xMin) / (xMax - xMin));
  }
  uv.needsUpdate = true;
  return g;
}

function lambert(map, color = 0xffffff, extra = {}) {
  return new THREE.MeshLambertMaterial({ map, color, ...extra });
}

// ---------------------------------------------------------------------------

export class LowPolyCow {
  /**
   * @param marioModel the MarioModel whose skeleton the cow rides on
   * @param face optional { texture, aspect } from bakeFaceFromGltf
   */
  constructor(marioModel, face = null) {
    this.mario = marioModel;
    this.meshes = [];
    this.triangleCount = 0;
    const T = makeTextures();
    const M = {
      fur: lambert(T.fur),
      body: lambert(T.body),
      hips: lambert(T.hips),
      legs: lambert(T.leggings),
      terry: lambert(T.terry),
      hoof: new THREE.MeshPhongMaterial({ color: 0x0c0c0e, shininess: 90, specular: 0x666666 }),
      pink: lambert(null, 0xf3a3c0),
      snout: lambert(null, 0xd8535c),
      nostril: lambert(null, 0x2a1214),
      horn: lambert(T.horn),
      wire: lambert(null, 0x2b2b2b),
      slipper: lambert(T.slipperFace),
      slipperBlack: lambert(null, 0x1d1d1f),
      sole: lambert(null, 0x2d2a28),
      tan: lambert(null, 0xc9a273),
      earPink: lambert(null, 0xe47aa0),
      face: lambert((face && face.texture) || drawnFace()),
    };
    this.materials = M;
    this.bakedFace = !!face;
    this.faceAspect = face ? face.aspect : 1.15;

    const parts = this.buildParts(M);
    for (const [index, build] of Object.entries(parts)) this.attach(Number(index), build);
    this.setActive(false);
  }

  /** Returns { animIndex: (mirror) => THREE.Group } */
  buildParts(M) {
    const mesh = (geom, mat) => new THREE.Mesh(geom, mat);
    const group = (...children) => { const g = new THREE.Group(); g.add(...children); return g; };
    const faceH = 252; // face plate height (local X)
    const faceW = faceH / this.faceAspect;

    const head = () => {
      // The mask: a front half-shell carrying the face, pushed forward around the
      // photographed snout (bottom centre of the face) to give it some depth.
      const faceCx = 120;
      const faceGeom = ellipsoid([faceCx, 30, 0], [faceH / 2, 120, faceW / 2], 18, 14, [0, Math.PI]);
      const fp = faceGeom.attributes.position;
      for (let i = 0; i < fp.count; i++) {
        const u = fp.getZ(i) / (faceW / 2), v = (fp.getX(i) - faceCx) / (faceH / 2);
        const d = Math.hypot(u / 0.42, (v + 0.72) / 0.32); // snout region
        if (d < 1 && fp.getY(i) > 30) fp.setY(i, fp.getY(i) + 38 * Math.cos((d * Math.PI) / 2));
      }
      faceGeom.computeVertexNormals();
      planarUV(faceGeom, -faceW / 2, faceW / 2, faceCx - faceH / 2, faceCx + faceH / 2);
      const g = group(
        mesh(ellipsoid([128, -6, 0], [128, 132, 136], 14, 10), M.fur), // hood
        mesh(faceGeom, M.face),
      );
      if (!this.bakedFace) { // the drawn fallback face has no snout of its own
        g.add(mesh(ellipsoid([62, 140, 0], [46, 42, 62], 10, 8), M.snout));
        g.add(mesh(ellipsoid([60, 178, 26], [12, 6, 10], 6, 4), M.nostril));
        g.add(mesh(ellipsoid([60, 178, -26], [12, 6, 10], 6, 4), M.nostril));
      }
      // the white tube holding the horns, lying along Z on top of the hood
      const hornTube = mesh(tube(-92, 92, 24, 24, 8), M.fur);
      hornTube.rotation.y = Math.PI / 2;
      hornTube.position.set(250, -20, 0);
      g.add(hornTube);
      // left horn (complete, curving up and out) and right horn (broken, with exposed wire)
      g.add(mesh(cone([250, -18, 86], [300, -14, 116], 21), M.horn));
      g.add(mesh(cone([300, -14, 116], [344, -10, 108], 13), M.horn));
      g.add(mesh(cone([250, -18, -86], [282, -15, -108], 21), M.horn));
      g.add(mesh(ellipsoid([282, -15, -108], [9, 9, 9], 6, 4), M.wire));
      for (const [y, z, tilt] of [[-10, -106, 0.9], [-20, -112, 0.6], [-14, -116, 1.2]]) {
        const wire = mesh(tube(0, 40, 2.2, 1.5, 4), M.wire);
        wire.rotation.z = tilt;
        wire.position.set(282, y, z);
        g.add(wire);
      }
      return g;
    };

    const torso = () => group(
      mesh(ellipsoid([4, 10, 0], [112, 104, 112], 14, 10), M.body),
      // udders with teats (pointing down/forward and outward)
      ...[-1, 1].flatMap((s) => [
        mesh(ellipsoid([44, 92, 46 * s], [42, 40, 42], 10, 8), M.pink),
        mesh(cone([18, 116, 40 * s], [-14, 150, 34 * s], 9, 6), M.pink),
        mesh(cone([30, 104, 80 * s], [12, 112, 116 * s], 8, 6), M.pink),
      ]),
    );

    const butt = () => group(mesh(ellipsoid([4, 6, 0], [70, 96, 108], 12, 8), M.hips));

    const upperArm = () => group(
      mesh(ellipsoid([4, 0, 0], [36, 36, 36], 8, 6), M.fur),
      mesh(tube(0, 70, 36, 30, 8), M.fur),
    );
    const forearm = () => group(
      mesh(tube(-6, 58, 30, 27, 8), M.fur),
      mesh(tube(52, 64, 29, 29, 8), M.fur), // cuff
    );
    // Mitten: terry cloth with a cloven black hoof at the tip and a cloth thumb
    const hand = () => group(
      mesh(ellipsoid([40, 4, -6], [50, 44, 40], 10, 8), M.terry),
      mesh(ellipsoid([86, 4, -20], [20, 24, 15], 8, 6), M.hoof),
      mesh(ellipsoid([86, 4, 10], [20, 24, 15], 8, 6), M.hoof),
      mesh(ellipsoid([30, -10, 34], [24, 16, 16], 6, 5), M.terry),
    );
    const thigh = () => group(mesh(tube(-10, 100, 52, 44, 9), M.legs), mesh(ellipsoid([0, 0, 0], [50, 50, 50], 8, 6), M.legs));
    const shin = () => group(mesh(tube(-6, 74, 44, 36, 9), M.legs));
    // Cow-face slipper: fluffy cream body, black upper, sole, little tan horns and black ears
    const foot = () => {
      const front = ellipsoid([62, 22, 0], [62, 40, 58], 10, 8);
      // map the face texture on the toe: project from the front (local X is the toe direction)
      const uv = front.attributes.uv, pos = front.attributes.position;
      for (let i = 0; i < pos.count; i++) uv.setXY(i, (pos.getZ(i) + 58) / 116, 1 - (pos.getY(i) + 18) / 80);
      return group(
        mesh(front, M.slipper),
        mesh(ellipsoid([-6, 10, 0], [56, 46, 54], 10, 8), M.slipperBlack),
        mesh(ellipsoid([32, 58, 0], [92, 9, 58], 10, 4), M.sole),
        mesh(cone([70, -16, 24], [72, -44, 34], 8, 6), M.tan),
        mesh(cone([70, -16, -24], [72, -44, -34], 8, 6), M.tan),
        mesh(ellipsoid([40, -14, 52], [16, 6, 18], 6, 4), M.slipperBlack),
        mesh(ellipsoid([40, -14, -52], [16, 6, 18], 6, 4), M.slipperBlack),
      );
    };

    return {
      1: butt, 2: torso, 3: head,
      5: upperArm, 6: forearm, 7: hand,
      9: upperArm, 10: forearm, 11: hand,
      13: thigh, 14: shin, 15: foot,
      17: thigh, 18: shin, 19: foot,
    };
  }

  /** Attach a part to every Mario node with that animation slot (hand-pose variants included). */
  attach(animIndex, build) {
    const mirror = [9, 10, 11, 17, 18, 19].includes(animIndex);
    for (const rt of this.mario.animatedParts) {
      if (rt.animIndex !== animIndex) continue;
      // Hands/right foot keep their punch/kick scale node: ride on it when present.
      const scaleChild = rt.children.find((c) => c && c.geo.type === 'scale');
      const host = scaleChild ? scaleChild.group : rt.group;
      const g = build();
      if (mirror) g.scale.z = -1;
      g.traverse((o) => {
        if (o.isMesh) {
          o.userData.cow64 = true;
          o.frustumCulled = false;
          this.triangleCount += (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3;
        }
      });
      g.userData.cow64 = true;
      host.add(g);
      this.meshes.push(g);
    }
  }

  /** Show the cow in place of Mario's own meshes (or restore Mario). */
  setActive(on) {
    this.active = on;
    this.mario.visualScale = on ? COW64_SCALE : 1;
    this.mario.root.traverse((o) => {
      if (o.isMesh) o.visible = o.userData.cow64 ? on : !on;
    });
  }
}
