// "Leave Me Alone": a linear obstacle course from the back yard to her couch.
// Each section is built around one thing her weight (or clumsiness) does.
// Layout runs from z = +600 toward -11000 inside hedge walls at x = +-700.

import * as THREE from 'three';
import { LevelBuilder } from '../game/level.js';
import {
  CrumblePlank, SinkingRaft, PressurePlate, Gate, Breakable, CrackedFloor, Spring,
  Phone, Checkpoint, Couch, Hint,
} from './objects.js';

const W = 700; // corridor half-width
const WATER_Y = -60;

export function buildCourse(game) {
  const L = new LevelBuilder();
  const ground = (z0, z1, top = 0, opts = {}) => L.box(-W, -400, Math.min(z0, z1), W, top, Math.max(z0, z1), opts);
  const water = [];
  const pool = (z0, z1) => {
    L.box(-W, -500, Math.min(z0, z1), W, -400, Math.max(z0, z1), { top: 'dirt', side: 'dirt' });
    water.push({ minX: -W, maxX: W, minZ: Math.min(z0, z1), maxZ: Math.max(z0, z1), y: WATER_Y });
  };

  // Hedges (always ~260 above the ground beside them) and end walls
  for (const [z0, z1, top] of [[1260, -4600, 260], [-4600, -7400, 710], [-7400, -9900, 260], [-9900, -11010, 860]]) {
    L.box(-W - 60, -500, z1, -W, top, z0, { top: 'hedge', side: 'hedge' });
    L.box(W, -500, z1, W + 60, top, z0, { top: 'hedge', side: 'hedge' });
  }
  L.box(-W, -400, 1200, W, 260, 1260, { top: 'hedge', side: 'hedge' });
  L.box(-W, -400, -11010, W, 900, -10950, { top: 'hedge', side: 'hedge' });

  // S0 back yard: hurdles and boxes (one needs a crouch-jump)
  ground(1200, -2600);
  L.box(-450, 0, -210, 450, 70, -190, { top: 'plank', side: 'plank' });
  L.box(-450, 0, -610, 450, 70, -590, { top: 'plank', side: 'plank' });
  L.box(250, 0, -1000, 550, 110, -850, { top: 'wood', side: 'wood' });
  L.box(250, 0, -1250, 550, 230, -1100, { top: 'wood', side: 'wood' });

  // S2 creek (crumbling bridge) and far bank
  pool(-2600, -3500);
  ground(-3500, -4400);
  // S3 pit under a cracked slab, with a spring at the bottom, right below the plateau
  ground(-4580, -4600);
  L.box(-W, -400, -4580, -200, 0, -4400, {});
  L.box(200, -400, -4580, W, 0, -4400, {});
  L.box(-200, -400, -4580, 200, -180, -4400, { top: 'dirt', side: 'dirt' });
  L.box(-W, -400, -5200, W, 450, -4600, { top: 'grass', side: 'brick' });
  // S4 balance beam over the water
  pool(-5200, -6300);
  L.box(-35, 380, -6300, 35, 450, -5200, { top: 'wood', side: 'wood', type: 'beam' });
  L.box(-W, -400, -7000, W, 450, -6300, { top: 'grass', side: 'brick' });
  // S5 slippery slope down to the pond
  L.ramp(-W, -7400, W, -7000, -400, 0, 450, 'z+', { top: 'slide', side: 'brick' });
  ground(-7400, -7700);
  pool(-7700, -9000);
  // S6 gate yard
  ground(-9000, -9900);
  L.box(-600, 0, -9400, -400, 110, -9300, { top: 'wood', side: 'wood' });
  // S7 terraces up to the porch
  L.box(-W, -400, -10150, W, 200, -9900, { top: 'grass', side: 'brick' });
  L.box(-W, -400, -10400, W, 400, -10150, { top: 'grass', side: 'brick' });
  L.box(-W, -400, -10950, W, 600, -10400, { top: 'wood', side: 'brick' });

  const mesh = L.buildMeshes();

  // Water surfaces
  const waterMat = new THREE.MeshLambertMaterial({ color: 0x3f8fd0, transparent: true, opacity: 0.72, depthWrite: false });
  for (const w of water) {
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(w.maxX - w.minX, w.maxZ - w.minZ).rotateX(-Math.PI / 2), waterMat);
    plane.position.set((w.minX + w.maxX) / 2, w.y, (w.minZ + w.maxZ) / 2);
    plane.raycast = () => {};
    mesh.add(plane);
  }
  // Decorative trees outside the hedges
  const canopy = new THREE.MeshLambertMaterial({ color: 0x2f8f3a, flatShading: true });
  const trunk = new THREE.MeshLambertMaterial({ color: 0x6b4a2a });
  for (let z = 400; z > -11000; z -= 700) {
    for (const side of [-1, 1]) {
      const x = side * (1000 + Math.random() * 500);
      const t = new THREE.Mesh(new THREE.CylinderGeometry(25, 35, 300, 6), trunk);
      t.position.set(x, 150, z + Math.random() * 300);
      const c = new THREE.Mesh(new THREE.ConeGeometry(220, 520, 7), canopy);
      c.position.set(t.position.x, 520, t.position.z);
      t.raycast = c.raycast = () => {};
      mesh.add(t, c);
    }
  }
  const outside = new THREE.Mesh(new THREE.PlaneGeometry(9000, 16000).rotateX(-Math.PI / 2), new THREE.MeshLambertMaterial({ color: 0x4f9a3a }));
  outside.position.set(0, -2, -5200);
  outside.raycast = () => {};
  mesh.add(outside);

  return { mesh, tris: L.tris, water, spawn: { pos: [0, 0, 850], yaw: Math.PI } };
}

/** Place the interactive objects. Needs game.world / game.scene ready. */
export function populateCourse(game) {
  const o = [];
  const add = (thing) => { o.push(thing); return thing; };

  // S0
  add(new Checkpoint(game, -400, 0, 700));
  add(new Phone(game, 400, 230, -1175));
  add(new Breakable(game, -300, 0, -900, [110, 110, 110], { stompable: true }));
  add(new Checkpoint(game, -450, 0, -1300));
  // S1 stampede through the fence
  add(new Breakable(game, 0, 0, -2000, [1400, 300, 40], { tex: 'plank', color: 0xa8763f }));
  add(new Phone(game, 0, 0, -2300));
  // S2 crumbling bridge
  for (let i = 0; i < 7; i++) add(new CrumblePlank(game, 0, 0, -2660 - i * 125));
  add(new Phone(game, 350, 0, -3750));
  add(new Checkpoint(game, -350, 0, -3700));
  // S3 cracked slab, spring, plateau
  add(new CrackedFloor(game, 0, 0, -4490, 400, 180));
  add(new Spring(game, 0, -180, -4490, 100));
  add(new Breakable(game, 300, 450, -4900, [120, 120, 120], {
    stompable: true,
    contents: (crate) => add(new Phone(game, crate.object.position.x, 450, crate.object.position.z)),
  }));
  add(new Checkpoint(game, -300, 450, -4750));
  // S4 beam
  add(new Phone(game, 0, 450, -5750));
  add(new Checkpoint(game, -300, 450, -6450));
  // S5 pond with sinking rafts
  add(new Checkpoint(game, -300, 0, -7560));
  const rafts = [[-110, -7880], [120, -8180], [-120, -8480], [100, -8780]].map(([x, z]) => add(new SinkingRaft(game, x, z, WATER_Y, 200)));
  add(new Phone(game, 0, 0, 0, { object: rafts[2].object, offset: new THREE.Vector3(0, 0, 0) }));
  // S6 gate opened by two pressure plates
  const gate = add(new Gate(game, 0, 0, -9500));
  const plates = [];
  const check = () => { if (plates.every((p) => p.pressed)) gate.open(); };
  plates.push(add(new PressurePlate(game, -420, 0, -9250, check)));
  plates.push(add(new PressurePlate(game, 420, 0, -9250, check)));
  add(new Phone(game, -500, 110, -9350));
  add(new Checkpoint(game, 300, 0, -9100));
  // S7 terraces and the couch
  add(new Phone(game, -400, 200, -10050));
  add(new Checkpoint(game, -300, 600, -10500));
  add(new Couch(game, 0, 600, -10800, 0));

  // Hints
  const hints = [
    [-200, 1200, 'She\'s heavy. WASD to lumber about, Space to hop.\nHold Shift, then Space, for a crouch-jump.'],
    [-1700, -1400, 'Hold J to stampede. That fence looks flimsy.'],
    [-2650, -2450, 'Rickety planks. Don\'t dawdle.'],
    [-4300, -3950, 'Shift in mid-air: STOMP. Cracked floors give way.\nStomp onto a spring to launch.'],
    [-5260, -5050, 'A narrow beam. Hold Ctrl to tiptoe, or she\'ll wobble off.'],
    [-7010, -6850, 'That slope looks slippery.'],
    [-7750, -7600, 'Rafts sink under her weight. Keep hopping.'],
    [-9150, -9000, 'Only something heavy can push these plates down.'],
    [-9900, -9700, 'Crouch-jump up the terraces.'],
  ];
  for (const [z0, z1, text] of hints) add(new Hint(game, -W, z0, W, z1, text));
  game.phonesTotal = o.filter((t) => t instanceof Phone).length + 1; // +1 inside the crate
  return o;
}
