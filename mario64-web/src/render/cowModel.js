// The Misanthropic Cow as the player character.
//
// The cow comes with its own skeleton and clips (idle, walk, run, sneak, ...), but
// not with platformer moves. For those we retarget Mario's animations from the ROM
// at runtime: a hidden Mario model is posed from the physics state every frame, and
// each of his body parts' rotations (relative to his A-pose) is applied to the
// matching cow bone. Locomotion and idling use the cow's own clips instead.

import * as THREE from 'three';
import { GLTFLoader } from '../../vendor/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from '../../vendor/addons/libs/meshopt_decoder.module.js';
import * as A from '../mario/anim_ids.js';

export const COW_SCALE = 95; // metres -> SM64 units: the 1.70 m cow stands ~161 units, like Mario
const CROSSFADE = 0.14; // seconds
const LOW_HEALTH = 0x300;

// cow bone <- Mario animated part. 'dir' bones are re-aimed along Mario's limb before
// applying his motion (the cow's arms hang lower than Mario's A-pose); 'rot' bones copy
// the rotation change directly. Left/right are swapped automatically if needed.
const MAP = [
  ['Hips', 1, 'rot'],
  ['Spine', 2, 'dir', 3],
  ['Head', 3, 'rot'],
  ['UpperArm_L', 5, 'dir', 6], ['Forearm_L', 6, 'dir', 7], ['Hand_L', 7, 'rot'],
  ['UpperArm_R', 9, 'dir', 10], ['Forearm_R', 10, 'dir', 11], ['Hand_R', 11, 'rot'],
  ['Thigh_L', 13, 'dir', 14], ['Shin_L', 14, 'dir', 15], ['Foot_L', 15, 'rot'],
  ['Thigh_R', 17, 'dir', 18], ['Shin_R', 18, 'dir', 19], ['Foot_R', 19, 'rot'],
];
const BONE_CHILD = { Spine: 'Chest', UpperArm_L: 'Forearm_L', Forearm_L: 'Hand_L', UpperArm_R: 'Forearm_R', Forearm_R: 'Hand_R', Thigh_L: 'Shin_L', Shin_L: 'Foot_L', Thigh_R: 'Shin_R', Shin_R: 'Foot_R' };
// Skinning helpers that carry half of their partner's rotation (as in the cow's own clips).
const HALF = { Elbow_L: 'Forearm_L', Elbow_R: 'Forearm_R', UpperArmRoot_L: 'UpperArm_L', UpperArmRoot_R: 'UpperArm_R' };

const IDLE_ANIMS = new Set([A.MARIO_ANIM_IDLE_HEAD_LEFT, A.MARIO_ANIM_IDLE_HEAD_RIGHT, A.MARIO_ANIM_IDLE_HEAD_CENTER]);

export async function loadCowGltf(url) {
  const loader = new GLTFLoader();
  loader.setMeshoptDecoder(MeshoptDecoder);
  return loader.loadAsync(url);
}

const _m = new THREE.Matrix4();
const _inv = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const _q2 = new THREE.Quaternion();
const _p = new THREE.Vector3();
const _s = new THREE.Vector3();
const IDENT = new THREE.Quaternion();

export class CowModel {
  /**
   * @param gltf loaded cow asset
   * @param mario a MarioModel (not added to the scene) used as the animation source
   */
  constructor(gltf, mario) {
    this.mario = mario;
    this.root = new THREE.Group();
    this.root.name = 'Cow';
    this.root.matrixAutoUpdate = false;
    this.scene = gltf.scene;
    this.scene.scale.setScalar(COW_SCALE);
    this.root.add(this.scene);
    this.scene.traverse((o) => {
      if (o.isMesh) {
        o.frustumCulled = false;
        const mat = o.material;
        if (mat && mat.alphaTest > 0) mat.alphaToCoverage = true;
      }
    });

    // Bones in parent-before-child order
    this.bones = [];
    this.scene.traverse((o) => { if (o.isBone) this.bones.push(o); });
    this.byName = Object.fromEntries(this.bones.map((b) => [b.name, b]));
    this.rest = new Map(this.bones.map((b) => [b, { q: b.quaternion.clone(), p: b.position.clone() }]));
    this.scene.updateMatrixWorld(true);
    this.restWorldQ = new Map();
    this.restWorldPos = new Map();
    for (const b of this.bones) {
      b.matrixWorld.decompose(_p, _q, _s);
      this.restWorldQ.set(b, _q.clone());
      this.restWorldPos.set(b, _p.clone());
    }
    const hips = this.byName.Hips;
    this.hipsParentQ = new THREE.Quaternion();
    if (hips.parent) hips.parent.matrixWorld.decompose(_p, this.hipsParentQ, _s);

    this.clips = new Map(gltf.animations.map((clip) => [clip.name, this.makeSampler(clip)]));
    this.calibrate();

    this.source = null;
    this.clipTime = 0;
    this.fade = null; // { from: Map(bone -> {q,p}), t }
    this.idleCycle = 0;
    this.override = null; // clip forced by the game (e.g. a victory dance)
    this.useNativeClips = true; // false: always show Mario's animation retargeted
  }

  makeSampler(clip) {
    const tracks = [];
    for (const track of clip.tracks) {
      const [name, prop] = track.name.split('.');
      const bone = this.byName[name];
      if (!bone || (prop !== 'quaternion' && prop !== 'position')) continue;
      tracks.push({ bone, prop, interp: track.createInterpolant() });
    }
    return { duration: clip.duration, tracks };
  }

  /** Pose the hidden Mario in his A-pose and record each part's reference transform. */
  calibrate() {
    const m0 = {
      marioObj: { header: { gfx: { pos: [0, 0, 0], angle: [0, 0, 0], scale: [1, 1, 1], throwMatrix: null,
        animInfo: { animID: A.MARIO_ANIM_A_POSE, animFrame: 0, animYTrans: 189 } } } },
      marioBodyState: { action: 0, capState: 0, eyeState: 0, handState: 0, punchState: 0, torsoAngle: [0, 0, 0], headAngle: [0, 0, 0], modelState: 0, wingFlutter: 0 },
    };
    const ref = this.sampleMario(m0);
    this.refQ = ref.q;
    this.refP = ref.p;

    // Mario faces +Z like the cow; his part 5 is the arm on +X (the cow's _L side) unless swapped.
    const swap = ref.p[5].x < ref.p[9].x;
    const lr = (i) => (swap ? ({ 5: 9, 6: 10, 7: 11, 9: 5, 10: 6, 11: 7, 13: 17, 14: 18, 15: 19, 17: 13, 18: 14, 19: 15 }[i] ?? i) : i);
    this.map = MAP.map(([name, part, mode, childPart]) => {
      const bone = this.byName[name];
      const p = lr(part);
      let align = new THREE.Quaternion();
      if (mode === 'dir') {
        const marioDir = ref.p[lr(childPart)].clone().sub(ref.p[p]).normalize();
        const cowDir = this.restWorldPos.get(this.byName[BONE_CHILD[name]]).clone().sub(this.restWorldPos.get(bone)).normalize();
        align = new THREE.Quaternion().setFromUnitVectors(cowDir, marioDir);
      }
      return { bone, part: p, align };
    });
    this.mapByBone = new Map(this.map.map((e) => [e.bone, e]));
    // Hips height ratio, to scale Mario's root motion (crouches, flips) to the cow's body.
    this.hipRatio = this.restWorldPos.get(this.byName.Hips).y / ref.p[1].y;
  }

  /** Pose the hidden Mario for state m and return each part's rotation/position in his object space. */
  sampleMario(m, prev = null, alpha = 1) {
    const mario = this.mario;
    mario.update(m, prev, alpha);
    mario.root.updateMatrixWorld(true);
    _inv.copy(mario.root.matrixWorld).invert();
    const q = [], p = [];
    for (const part of mario.posedParts) {
      _m.multiplyMatrices(_inv, part.group.matrixWorld);
      const pos = new THREE.Vector3(), quat = new THREE.Quaternion(), scl = new THREE.Vector3();
      _m.decompose(pos, quat, scl);
      q.push(quat);
      p.push(pos);
    }
    return { q, p };
  }

  /** Which of the cow's own clips (if any) replaces Mario's animation right now. */
  chooseClip(m) {
    if (this.override) return { name: this.override, rate: 1 };
    if (!this.useNativeClips) return null;
    const animID = m.marioObj.header.gfx.animInfo.animID;
    const v = Math.abs(m.forwardVel);
    const tired = m.health < LOW_HEALTH;
    if (IDLE_ANIMS.has(animID)) {
      const cycle = ['Idle', 'Idle', 'Look Around', 'Idle (alt)'];
      return { name: tired ? 'Exasperated' : cycle[this.idleCycle % cycle.length], rate: 1, idle: true };
    }
    if (animID === A.MARIO_ANIM_WALK_PANTING) return { name: 'Exasperated', rate: 1 };
    if (animID === A.MARIO_ANIM_TIPTOE || animID === A.MARIO_ANIM_START_TIPTOE) {
      return { name: 'Sneak', rate: clamp(v / 3.5, 0.5, 2.5), loco: true };
    }
    if (animID === A.MARIO_ANIM_WALKING) {
      return tired ? { name: 'Depressed Walk', rate: clamp(v / 6, 0.5, 2.5), loco: true }
        : { name: 'Walk', rate: clamp(v / 7.5, 0.5, 2.6), loco: true };
    }
    if (animID === A.MARIO_ANIM_RUNNING) return { name: 'Run', rate: clamp(v / 13, 0.6, 2.4), loco: true };
    return null;
  }

  /**
   * @param m Mario state from the physics
   * @param prev / alpha interpolation snapshot (same as MarioModel.update)
   * @param dt seconds since the last rendered frame
   */
  get clipNames() {
    return [...this.clips.keys()];
  }

  update(m, prev, alpha, dt) {
    // The hidden Mario provides the object transform and, when needed, the pose.
    const marioPose = this.sampleMario(m, prev, alpha);
    this.root.matrix.copy(this.mario.root.matrix);
    this.root.matrixWorldNeedsUpdate = true;

    const choice = this.chooseClip(m);
    const key = choice ? choice.name : 'mario';
    if (key !== this.source) {
      const continuing = choice && choice.loco && this.lastWasLoco; // keep phase between gaits
      this.fade = { from: this.capturePose(), t: 0 };
      if (!continuing) this.clipTime = 0;
      this.source = key;
    }
    this.lastWasLoco = !!(choice && choice.loco);

    const target = new Map();
    if (choice) {
      const clip = this.clips.get(choice.name);
      this.clipTime += dt * choice.rate;
      if (choice.idle && this.clipTime >= clip.duration) {
        this.clipTime = 0;
        this.idleCycle++;
      }
      this.sampleClip(clip, this.clipTime % clip.duration, target);
    } else {
      this.retarget(marioPose, target);
    }

    // Cross-fade from the previously displayed pose after a source change
    let w = 1;
    if (this.fade) {
      this.fade.t += dt > 0 ? dt : CROSSFADE; // paused (dt = 0): snap instead of freezing mid-fade
      w = Math.min(1, this.fade.t / CROSSFADE);
      if (w >= 1) this.fade = null;
    }
    for (const b of this.bones) {
      const t = target.get(b) || this.rest.get(b);
      if (w < 1) {
        const f = this.fade.from.get(b);
        b.quaternion.copy(f.q).slerp(t.q, w);
        b.position.copy(f.p).lerp(t.p, w);
      } else {
        b.quaternion.copy(t.q);
        b.position.copy(t.p);
      }
    }
  }

  capturePose() {
    return new Map(this.bones.map((b) => [b, { q: b.quaternion.clone(), p: b.position.clone() }]));
  }

  sampleClip(clip, time, out) {
    for (const b of this.bones) out.set(b, { q: this.rest.get(b).q.clone(), p: this.rest.get(b).p.clone() });
    for (const tr of clip.tracks) {
      const v = tr.interp.evaluate(time);
      const o = out.get(tr.bone);
      if (tr.prop === 'quaternion') o.q.set(v[0], v[1], v[2], v[3]).normalize();
      else o.p.set(v[0], v[1], v[2]);
    }
  }

  retarget(pose, out) {
    const worldQ = new Map();
    for (const b of this.bones) {
      const rest = this.rest.get(b);
      const parentQ = b === this.byName.Hips ? this.hipsParentQ : (worldQ.get(b.parent) || IDENT);
      const entry = this.mapByBone.get(b);
      let local;
      if (entry) {
        // world = (Mario's rotation change from his A-pose) * align * rest
        _q.copy(this.refQ[entry.part]).invert();
        _q2.copy(pose.q[entry.part]).multiply(_q);
        const world = _q2.clone().multiply(entry.align).multiply(this.restWorldQ.get(b));
        local = parentQ.clone().invert().multiply(world);
      } else {
        local = rest.q.clone();
      }
      worldQ.set(b, parentQ.clone().multiply(local));
      out.set(b, { q: local, p: rest.p.clone() });
    }
    for (const [helper, partner] of Object.entries(HALF)) {
      const h = this.byName[helper], pb = this.byName[partner];
      if (h && pb) out.get(h).q.copy(IDENT).slerp(out.get(pb).q, 0.5);
    }
    // Root motion (crouching, flips, ledge climbs), scaled to the cow's hip height
    const hips = this.byName.Hips;
    const d = pose.p[1].clone().sub(this.refP[1]).multiplyScalar(this.hipRatio / COW_SCALE);
    out.get(hips).p.add(d);
  }
}

function clamp(v, lo, hi) {
  return v < lo ? lo : v > hi ? hi : v;
}
