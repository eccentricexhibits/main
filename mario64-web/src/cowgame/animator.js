// Animates the detailed cow from her own clips only, picked and paced by the
// controller's state, with procedural layers that sell her weight: leaning into
// speed, rolling into turns, wobbling on beams, belly/udder jiggle that lags behind
// her body, and squash on heavy landings.

import * as THREE from 'three';

export const COW_SCALE = 95;
const FADE = 0.15;
const IDLE_CYCLE = ['Idle', 'Idle', 'Look Around', 'Idle (alt)', 'Idle'];

const _q = new THREE.Quaternion();
const _e = new THREE.Euler();
const AX = new THREE.Vector3(1, 0, 0), AZ = new THREE.Vector3(0, 0, 1);

export class CowAnimator {
  constructor(gltf) {
    this.root = new THREE.Group(); // positioned/rotated by the game
    this.model = gltf.scene;
    this.model.scale.setScalar(COW_SCALE);
    this.root.add(this.model);
    this.model.traverse((o) => {
      if (o.isMesh) {
        o.frustumCulled = false;
        if (o.material && o.material.alphaTest > 0) o.material.alphaToCoverage = true;
      }
    });
    this.bones = [];
    this.model.traverse((o) => { if (o.isBone) this.bones.push(o); });
    this.byName = Object.fromEntries(this.bones.map((b) => [b.name, b]));
    this.rest = new Map(this.bones.map((b) => [b, { q: b.quaternion.clone(), p: b.position.clone() }]));
    this.clips = new Map(gltf.animations.map((c) => [c.name, this.sampler(c)]));

    this.source = null;
    this.time = 0;
    this.fade = null;
    this.idleIndex = 0;
    this.idleTime = 0;
    this.override = null; // { clip, from, to, rate, hold } forced by the game for a while
    this.clock = 0;
    // procedural state
    this.lean = 0;
    this.roll = 0;
    this.jiggle = 0;
    this.jiggleV = 0;
    this.squash = 0;
    this.squashV = 0;
    this.lastY = null;
    this.lastVy = 0;
  }

  sampler(clip) {
    const tracks = [];
    for (const track of clip.tracks) {
      const [name, prop] = track.name.split('.');
      const bone = this.byName[name];
      if (bone && (prop === 'quaternion' || prop === 'position')) tracks.push({ bone, prop, interp: track.createInterpolant() });
    }
    return { duration: clip.duration, tracks };
  }

  sample(name, t, out = new Map()) {
    const clip = this.clips.get(name);
    for (const b of this.bones) {
      const r = this.rest.get(b);
      out.set(b, { q: r.q.clone(), p: r.p.clone() });
    }
    if (!clip) return out;
    for (const tr of clip.tracks) {
      const v = tr.interp.evaluate(t);
      const o = out.get(tr.bone);
      if (tr.prop === 'quaternion') o.q.set(v[0], v[1], v[2], v[3]).normalize();
      else o.p.set(v[0], v[1], v[2]);
    }
    return out;
  }

  /** Play a clip segment once (e.g. a facepalm after falling in water), then hold. */
  play(clip, from, to, rate = 1, hold = 0.3) {
    this.override = { clip, from, to, rate, hold, t: from };
  }

  /** Choose the base pose from the controller state. Returns { key, clip, t } or a blend. */
  choose(ctl, dt) {
    const s = ctl.state;
    const v = Math.abs(ctl.speed);
    if (this.override) {
      const o = this.override;
      o.t += dt * o.rate;
      if (o.t >= o.to) { o.hold -= dt; if (o.hold <= 0) this.override = null; }
      return { key: 'ov:' + o.clip, clip: o.clip, t: Math.min(o.t, o.to) };
    }
    switch (s) {
      case 'ground':
        if (v < 25) {
          this.idleTime += dt;
          const name = IDLE_CYCLE[this.idleIndex % IDLE_CYCLE.length];
          return { key: 'idle:' + name, clip: name, loop: true, rate: 1, idle: true };
        }
        this.idleTime = 0;
        if (ctl.floor && ctl.floor.tag === 'beam') return { key: 'sneak', clip: 'Sneak', loop: true, rate: clamp(v / 70, 0.4, 2.2), loco: true };
        if (v < 230) return { key: 'walk', clip: ctl.tired ? 'Depressed Walk' : 'Walk', loop: true, rate: clamp(v / 115, 0.5, 2.2), loco: true };
        if (v < 520) return { key: 'run', clip: 'Run', loop: true, rate: clamp(v / 290, 0.8, 1.9), loco: true };
        return { key: 'sprint', clip: 'Run (alt)', loop: true, rate: clamp(v / 380, 1.2, 2.0), loco: true };
      case 'skid': return { key: 'skid', clip: 'Exasperated', t: 0.8 };
      case 'charge': return { key: 'charge', clip: 'Crouch and Sit', t: 0.8 + ctl.charge * 1.1 };
      case 'stumble':
        return this.lastLandStomp
          ? { key: 'stompLand', clip: 'Crouch and Sit', t: 1.7 }
          : { key: 'stumble', clip: 'Exasperated', loop: false, rate: 1.4, start: 0.2 };
      case 'cry': return { key: 'cry', clip: 'Crying', loop: false, rate: 1.1, start: 0.5 };
      case 'slide': return { key: 'slide', clip: 'Crouch and Sit', t: 4.6 };
      case 'stomp': return { key: 'stomp', clip: 'Crouch and Sit', t: 1.9 };
      case 'sit': return { key: 'sit', clip: 'Crouch and Sit', loop: false, rate: 1, start: 2.2, end: 5.2 };
      case 'sink':
      case 'air':
        if (s === 'air' && ctl.vel.y > 150) return { key: 'rise', clip: 'Jumping Jacks', t: 0.5 };
        return { key: 'flail', flail: true }; // arms flapping between out and up
      default: return { key: 'idle:Idle', clip: 'Idle', loop: true, rate: 1 };
    }
  }

  /**
   * @param dt frame time (s)
   * @param ctl the CowController
   * @param pos interpolated position, yaw interpolated facing
   */
  update(dt, ctl, pos, yaw) {
    this.clock += dt;
    this.root.position.copy(pos);
    this.root.rotation.set(0, yaw, 0);

    const c = this.choose(ctl, dt);
    if (c.key !== this.source) {
      const continuing = c.loco && this.lastLoco;
      this.fade = this.source ? { from: this.capture(), t: 0 } : null;
      if (!continuing) this.time = c.start || 0;
      this.source = c.key;
    }
    this.lastLoco = !!c.loco;

    let target;
    if (c.flail) {
      const w = 0.5 + 0.5 * Math.sin(this.clock * (ctl.state === 'sink' ? 22 : 15));
      const a = this.sample('Jumping Jacks', 0.25), b = this.sample('Jumping Jacks', 0.5);
      target = new Map();
      for (const bone of this.bones) {
        const pa = a.get(bone), pb = b.get(bone);
        target.set(bone, { q: pa.q.clone().slerp(pb.q, w), p: pa.p.clone().lerp(pb.p, w) });
      }
    } else if (c.t !== undefined) {
      target = this.sample(c.clip, c.t);
    } else {
      const clip = this.clips.get(c.clip);
      this.time += dt * (c.rate || 1);
      let t = this.time;
      if (c.loop) {
        if (c.idle && t >= clip.duration) { this.time = t = 0; this.idleIndex++; }
        t %= clip.duration;
      } else {
        t = Math.min(t, c.end || clip.duration - 0.001);
      }
      target = this.sample(c.clip, t);
    }

    // Cross-fade after a change of pose source
    let w = 1;
    if (this.fade) {
      this.fade.t += dt > 0 ? dt : FADE; // paused: show the target pose
      w = Math.min(1, this.fade.t / FADE);
      if (w >= 1) this.fade = null;
    }
    for (const b of this.bones) {
      const t = target.get(b);
      if (w < 1) {
        const f = this.fade.from.get(b);
        b.quaternion.copy(f.q).slerp(t.q, w);
        b.position.copy(f.p).lerp(t.p, w);
      } else {
        b.quaternion.copy(t.q);
        b.position.copy(t.p);
      }
    }
    this.procedural(dt, ctl, pos);
  }

  capture() {
    return new Map(this.bones.map((b) => [b, { q: b.quaternion.clone(), p: b.position.clone() }]));
  }

  procedural(dt, ctl, pos) {
    const k = 1 - Math.exp(-dt * 8);
    const T = ctl.T;
    // Lean into acceleration and speed; lean back while skidding
    let lean = clamp(ctl.accel / 4000, -0.12, 0.12) + clamp(ctl.speed / T.sprintSpeed, 0, 1) * 0.16;
    if (ctl.state === 'skid') lean = -0.3;
    if (ctl.state === 'air' || ctl.state === 'stomp' || ctl.state === 'sink') lean = 0;
    this.lean += (lean - this.lean) * k;
    // Roll into turns (more at speed)
    const roll = ctl.state === 'ground' ? clamp(-ctl.turnRate * ctl.speed / 3500, -0.22, 0.22) : 0;
    this.roll += (roll - this.roll) * k;
    const wob = ctl.wobble || 0;
    const wobbleRoll = Math.sin(this.clock * 7.5) * wob * 0.35 + Math.sin(this.clock * 3.1) * wob * 0.12;

    const hips = this.byName.Hips, spine = this.byName.Spine;
    if (spine) spine.quaternion.premultiply(_q.setFromAxisAngle(AX, this.lean));
    if (hips) hips.quaternion.premultiply(_q.setFromAxisAngle(AZ, this.roll + wobbleRoll));
    // Arms out for balance on beams
    for (const [name, s] of [['UpperArm_L', 1], ['UpperArm_R', -1]]) {
      const b = this.byName[name];
      if (b && wob > 0.05) b.quaternion.premultiply(_q.setFromAxisAngle(AZ, s * Math.min(1, wob * 1.6) * 0.9));
    }

    // Jiggle: a damped spring driven by her vertical acceleration
    const vy = this.lastY === null ? 0 : (pos.y - this.lastY) / Math.max(dt, 1e-4);
    const ay = (vy - this.lastVy) / Math.max(dt, 1e-4);
    this.lastY = pos.y;
    this.lastVy = vy;
    const drive = clamp(ay / 6000, -1.5, 1.5) + (ctl.state === 'ground' ? Math.sin(this.clock * 13) * Math.min(1, ctl.speed / 400) * 0.25 : 0);
    this.jiggleV += (-160 * this.jiggle - 9 * this.jiggleV - drive * 40) * dt;
    this.jiggle = clamp(this.jiggle + this.jiggleV * dt, -0.5, 0.5);
    for (const name of ['Udder_L', 'Udder_R']) {
      const b = this.byName[name];
      if (b) b.quaternion.premultiply(_q.setFromAxisAngle(AX, this.jiggle * 0.5));
    }
    const belly = this.byName.Belly;
    if (belly) belly.position.y += this.jiggle * 0.02;

    // Squash on landing, springing back
    this.squashV += (-220 * this.squash - 14 * this.squashV) * dt;
    this.squash = clamp(this.squash + this.squashV * dt, -0.12, 0.2);
    const sq = this.squash;
    this.model.scale.set(COW_SCALE * (1 + sq * 0.5), COW_SCALE * (1 - sq), COW_SCALE * (1 + sq * 0.5));
  }

  /** Called on landings with the impact speed. */
  land(impact, stomp) {
    this.lastLandStomp = stomp;
    this.squashV += Math.min(4, impact / 700) * (stomp ? 1.6 : 1);
    this.jiggleV -= Math.min(6, impact / 500);
  }
}

function clamp(v, lo, hi) {
  return v < lo ? lo : v > hi ? hi : v;
}
