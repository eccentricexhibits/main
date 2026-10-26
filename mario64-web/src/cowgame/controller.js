// The Misanthropic Cow's movement. She is heavy: slow to get going and slow to stop,
// she turns in wide arcs at speed, skids when you reverse, hops low and falls fast.
// Her weight is also her toolkit: a ground stomp, a crouch-charged jump, and a
// stampede sprint that smashes flimsy things and bounces her off solid ones.
// Clumsiness: big landings make her stumble (or sit down and cry), and on narrow
// beams she wobbles unless she tiptoes.

import * as THREE from 'three';

export const TUNING = {
  radius: 42,
  height: 160,
  walkSpeed: 160, // tiptoe / light stick
  runSpeed: 380,
  sprintSpeed: 640,
  accelRun: 520,
  accelSprint: 300,
  decel: 900,
  skidDecel: 1500,
  turnRateSlow: 7.0, // rad/s when nearly still
  turnRateFast: 1.6, // rad/s at full stampede
  gravityUp: 2600, // while rising with jump held
  gravityDown: 3900, // falling (or jump released): she drops like a sack
  terminal: 3000,
  jumpV: 790, // ~120 units, three quarters of her height
  chargeJumpV: 1170, // ~260 units after a full crouch
  chargeTime: 0.45,
  airAccel: 420,
  airTurn: 2.2,
  stompHover: 0.2,
  stompV: 3000,
  stumbleImpact: 1650,
  cryImpact: 2500, // a fall of roughly 800 units
  coyote: 0.1,
  buffer: 0.12,
  slideNY: 0.75, // floors steeper than this can't be stood on
  springMin: 1050,
  springStomp: 2000,
  bonkSpeed: 520,
  smashSpeed: 560,
};

const WALL_HEIGHTS = [35, 85, 135];
const _v = new THREE.Vector3();
const _inv = new THREE.Matrix4();

function angleDiff(a, b) {
  let d = b - a;
  while (d > Math.PI) d -= Math.PI * 2;
  while (d < -Math.PI) d += Math.PI * 2;
  return d;
}

export class CowController {
  constructor(world, onEvent = () => {}) {
    this.world = world;
    this.T = TUNING;
    this.onEvent = onEvent;
    this.pos = new THREE.Vector3();
    this.vel = new THREE.Vector3(); // used in the air
    this.reset([0, 0, 0], 0);
  }

  reset(pos, yaw, snap = true) {
    this.pos.set(pos[0], pos[1], pos[2]);
    this.vel.set(0, 0, 0);
    this.yaw = yaw; // facing: 0 = +Z
    this.speed = 0; // forward ground speed
    this.state = 'ground';
    this.stateTime = 0;
    this.timer = 0;
    this.floor = null;
    this.grounded = true;
    this.coyote = 0;
    this.jumpBuffer = 0;
    this.charge = 0;
    this.wobble = 0;
    this.stomping = false;
    this.turnRate = 0; // for animation lean
    this.accel = 0;
    this.prev = { jump: false, crouch: false };
    if (snap) this.snapToFloor();
    else { this.grounded = false; this.state = 'air'; }
  }

  get forward() {
    return _v.set(Math.sin(this.yaw), 0, Math.cos(this.yaw));
  }

  setState(s, timer = 0) {
    this.state = s;
    this.stateTime = 0;
    this.timer = timer;
  }

  snapToFloor() {
    const f = this.world.findFloor(this.pos.x, this.pos.y + 100, this.pos.z, 0);
    if (f) { this.pos.y = f.y; this.floor = f; }
  }

  /**
   * @param dt seconds (fixed step)
   * @param input { mx, mz: world-space stick (length 0..1), jump, crouch, sprint, sneak }
   */
  step(dt, input) {
    const T = this.T;
    const jumpPressed = input.jump && !this.prev.jump;
    const crouchPressed = input.crouch && !this.prev.crouch;
    this.prev = { jump: input.jump, crouch: input.crouch };
    if (jumpPressed) this.jumpBuffer = T.buffer;
    else this.jumpBuffer = Math.max(0, this.jumpBuffer - dt);
    this.stateTime += dt;
    if (this.timer > 0) this.timer -= dt;

    const mag = Math.min(1, Math.hypot(input.mx, input.mz));
    const wantYaw = mag > 0.1 ? Math.atan2(input.mx, input.mz) : this.yaw;
    const prevSpeed = this.speed;

    this.rideFloor();

    switch (this.state) {
      case 'ground': this.stepGround(dt, input, mag, wantYaw, crouchPressed); break;
      case 'skid': this.stepSkid(dt, mag, wantYaw); break;
      case 'charge': this.stepCharge(dt, input, mag, wantYaw); break;
      case 'stumble': this.stepRecover(dt, 'ground'); break;
      case 'cry': this.stepRecover(dt, 'ground'); break;
      case 'slide': this.stepSlide(dt, input, mag, wantYaw); break;
      case 'air': this.stepAir(dt, input, mag, wantYaw, crouchPressed); break;
      case 'stomp': this.stepStomp(dt); break;
      case 'sink': this.stepSink(dt); break;
      case 'sit': this.speed = 0; break;
      default: break;
    }
    this.accel = (this.speed - prevSpeed) / dt;

    // Water: she can't swim
    const water = this.world.waterAt(this.pos.x, this.pos.z);
    if (water !== null && this.pos.y < water - 50 && this.state !== 'sink') {
      this.setState('sink', 1.4);
      this.vel.set(0, -80, 0);
      this.speed = 0;
      this.onEvent('splash', { pos: this.pos.clone(), y: water });
    }
    if (this.pos.y < -2500 && this.state !== 'sink') this.onEvent('fellOut');
  }

  /** Carry her along with a moving platform she stands on. */
  rideFloor() {
    const b = this.grounded && this.floor && this.floor.body;
    if (!b || !b.enabled) return;
    _inv.copy(b.prevMatrix).invert();
    const p = this.pos.clone().applyMatrix4(_inv).applyMatrix4(b.matrix);
    this.pos.copy(p);
  }

  /** Move horizontally by (dx, dz), resolve walls. Returns the wall contact, if any. */
  moveHoriz(dx, dz) {
    this.pos.x += dx;
    this.pos.z += dz;
    // on the ground she steps up low ledges; in the air every ledge is a wall
    return this.world.pushWalls(this.pos, this.T.radius, WALL_HEIGHTS, this.grounded ? 40 : 5);
  }

  /** Highest floor under her footprint (centre plus four points around it). */
  footFloor(stepUp) {
    const p = this.pos;
    let best = this.world.findFloor(p.x, p.y, p.z, stepUp);
    const r = this.T.radius * 0.6;
    for (const [dx, dz] of [[r, 0], [-r, 0], [0, r], [0, -r]]) {
      const f = this.world.findFloor(p.x + dx, p.y, p.z + dz, stepUp);
      if (f && (!best || f.y > best.y)) best = f;
    }
    return best;
  }

  groundCheck(maxDrop = 50) {
    const f = this.footFloor(45);
    if (f && f.y > this.pos.y - maxDrop) {
      this.pos.y = f.y;
      this.floor = f;
      this.grounded = true;
      return f;
    }
    this.floor = f;
    this.grounded = false;
    return null;
  }

  takeOff(vy) {
    const f = this.forward;
    this.vel.set(f.x * this.speed, vy, f.z * this.speed);
    this.grounded = false;
    this.stomping = false;
    this.springRise = false;
    this.setState('air');
  }

  stepGround(dt, input, mag, wantYaw, crouchPressed) {
    const T = this.T;
    if (crouchPressed) {
      if (this.speed < 140) { this.setState('charge'); this.charge = 0; return; }
      this.setState('skid'); // crouching at speed: dig the hooves in
      return;
    }
    if (this.jumpBuffer > 0) {
      this.jumpBuffer = 0;
      this.onEvent('jump');
      this.takeOff(T.jumpV + this.speed * 0.08);
      return;
    }

    // Steering: she turns quickly when slow and in wide arcs at speed
    const diff = angleDiff(this.yaw, wantYaw);
    if (mag > 0.1 && Math.abs(diff) > 2.3 && this.speed > 260) {
      this.setState('skid');
      this.onEvent('skid');
      return;
    }
    const speedFrac = Math.min(1, this.speed / T.sprintSpeed);
    const rate = T.turnRateSlow + (T.turnRateFast - T.turnRateSlow) * speedFrac;
    const turn = mag > 0.1 ? Math.max(-rate * dt, Math.min(rate * dt, diff)) : 0;
    this.yaw += turn;
    this.turnRate = turn / dt;

    let target = 0;
    if (mag > 0.1) {
      const top = input.sneak ? T.walkSpeed : input.sprint ? T.sprintSpeed : T.runSpeed;
      target = top * (input.sneak ? 1 : mag) * Math.max(0.35, Math.cos(Math.min(Math.abs(diff), 1.2)));
    }
    if (this.speed < target) {
      const accel = this.speed > T.runSpeed ? T.accelSprint : T.accelRun;
      this.speed = Math.min(target, this.speed + accel * dt);
    } else {
      this.speed = Math.max(target, this.speed - T.decel * dt * (target > 0 ? 0.6 : 1));
    }

    // Slopes: heavy going uphill, gathers speed downhill, slides on steep ones
    const n = this.floor ? this.floor.normal : [0, 1, 0];
    if (n[1] < 0.995) {
      const f = this.forward;
      const downhill = f.x * n[0] + f.z * n[2]; // >0 when facing downhill
      this.speed = Math.max(0, this.speed + downhill * 900 * dt);
    }

    // Narrow beams: wobble builds with speed and turning, settles when tiptoeing
    if (this.floor && this.floor.tag === 'beam') {
      const rush = (this.speed / 200) ** 2 * 1.2 + Math.abs(this.turnRate) * 0.35;
      this.wobble = Math.max(0, this.wobble + (rush - 0.8) * dt);
      if (this.wobble > 1) {
        this.wobble = 0;
        const side = Math.random() < 0.5 ? -1 : 1;
        const f = this.forward;
        this.speed = 0;
        this.takeOff(220);
        this.vel.x += f.z * side * 260;
        this.vel.z -= f.x * side * 260;
        this.onEvent('wobbleFall');
        return;
      }
    } else {
      this.wobble = Math.max(0, this.wobble - dt * 2);
    }

    const f = this.forward;
    const hit = this.moveHoriz(f.x * this.speed * dt, f.z * this.speed * dt);
    if (hit) this.wallContact(hit);
    if (this.state !== 'ground') return;

    const floor = this.groundCheck();
    if (!floor) {
      this.coyote = T.coyote;
      this.takeOff(0);
      return;
    }
    if (floor.normal[1] < T.slideNY) this.setState('slide');
  }

  /** Hitting a wall on the ground: smash flimsy things, bounce off solid ones at speed. */
  wallContact(hit) {
    const T = this.T;
    const f = this.forward;
    const into = -(f.x * hit.normal[0] + f.z * hit.normal[2]);
    const owner = hit.body && hit.body.owner;
    if (owner && owner.smashable && this.speed >= T.smashSpeed && into > 0.4) {
      owner.smash(this);
      this.speed *= 0.75;
      this.onEvent('smash', { owner });
      return;
    }
    if (this.speed > T.bonkSpeed && into > 0.6) {
      this.speed = -200;
      this.setState('stumble', 0.75);
      this.onEvent('bonk');
      return;
    }
    this.speed *= 1 - into * 0.5; // scrape along the wall
  }

  stepSkid(dt, mag, wantYaw) {
    this.speed = Math.max(0, this.speed - this.T.skidDecel * dt);
    const f = this.forward;
    this.moveHoriz(f.x * this.speed * dt, f.z * this.speed * dt);
    if (!this.groundCheck()) { this.takeOff(0); return; }
    if (this.jumpBuffer > 0 && this.speed > 150) { // hop out of a skid
      this.jumpBuffer = 0;
      this.onEvent('jump');
      this.takeOff(this.T.jumpV);
      return;
    }
    if (this.speed <= 30) {
      if (mag > 0.1) this.yaw = wantYaw; // finally turned round
      this.speed = 0;
      this.setState('ground');
    }
  }

  stepCharge(dt, input, mag, wantYaw) {
    const T = this.T;
    this.speed = Math.max(0, this.speed - T.decel * 2 * dt);
    if (mag > 0.1) this.yaw += Math.max(-2 * dt, Math.min(2 * dt, angleDiff(this.yaw, wantYaw)));
    this.charge = Math.min(1, this.charge + dt / T.chargeTime);
    if (this.jumpBuffer > 0) {
      this.jumpBuffer = 0;
      this.onEvent('jump', { charged: this.charge });
      // a crouch-jump with the stick held leaps that way
      if (mag > 0.1) this.yaw = wantYaw;
      this.speed = mag > 0.1 ? 120 + 80 * mag : 0;
      this.takeOff(T.jumpV + (T.chargeJumpV - T.jumpV) * this.charge);
      return;
    }
    if (!input.crouch) this.setState('ground');
    if (!this.groundCheck()) this.takeOff(0);
  }

  stepRecover(dt, next) {
    this.speed *= Math.max(0, 1 - 6 * dt);
    const f = this.forward;
    this.moveHoriz(f.x * this.speed * dt, f.z * this.speed * dt);
    if (!this.groundCheck()) { this.takeOff(0); return; }
    if (this.timer <= 0) { this.speed = 0; this.setState(next); }
  }

  stepSlide(dt, input, mag, wantYaw) {
    const n = this.floor ? this.floor.normal : [0, 1, 0];
    // gravity along the slope, little steering, some friction
    const gx = n[0], gz = n[2];
    const gl = Math.hypot(gx, gz) || 1;
    const vh = new THREE.Vector2(Math.sin(this.yaw) * this.speed, Math.cos(this.yaw) * this.speed);
    vh.x += (gx / gl) * 1400 * (1 - n[1]) * dt + input.mx * 120 * dt;
    vh.y += (gz / gl) * 1400 * (1 - n[1]) * dt + input.mz * 120 * dt;
    vh.multiplyScalar(1 - 0.4 * dt);
    this.speed = vh.length();
    if (this.speed > 1) this.yaw = Math.atan2(vh.x, vh.y);
    this.moveHoriz(vh.x * dt, vh.y * dt);
    if (this.jumpBuffer > 0) {
      this.jumpBuffer = 0;
      this.onEvent('jump');
      this.takeOff(this.T.jumpV * 0.8);
      return;
    }
    const floor = this.groundCheck(80);
    if (!floor) { this.takeOff(0); return; }
    if (floor.normal[1] >= this.T.slideNY) this.setState('ground');
  }

  stepAir(dt, input, mag, wantYaw, crouchPressed) {
    const T = this.T;
    if (this.coyote > 0) {
      this.coyote -= dt;
      if (this.jumpBuffer > 0 && this.vel.y <= 0) {
        this.jumpBuffer = 0;
        this.coyote = 0;
        this.onEvent('jump');
        this.vel.y = T.jumpV;
      }
    }
    if (crouchPressed && this.stateTime > 0.08) {
      this.setState('stomp');
      this.stomping = true;
      this.vel.set(0, 0, 0);
      this.onEvent('stompStart');
      return;
    }
    const rising = this.vel.y > 0 && (input.jump || this.springRise);
    this.vel.y = Math.max(-T.terminal, this.vel.y - (rising ? T.gravityUp : T.gravityDown) * dt);

    // Weak air control: nudge the momentum, never add much speed
    const vh = new THREE.Vector2(this.vel.x, this.vel.z);
    const before = vh.length();
    if (mag > 0.1) {
      vh.x += input.mx * T.airAccel * dt;
      vh.y += input.mz * T.airAccel * dt;
      const cap = Math.max(before, T.runSpeed * 0.55);
      if (vh.length() > cap) vh.setLength(cap);
      this.yaw += Math.max(-T.airTurn * dt, Math.min(T.airTurn * dt, angleDiff(this.yaw, wantYaw)));
    }
    this.vel.x = vh.x;
    this.vel.z = vh.y;
    this.airMove(dt);
  }

  stepStomp(dt) {
    if (this.stateTime < this.T.stompHover) {
      this.vel.set(0, 40, 0);
    } else {
      this.vel.set(0, -this.T.stompV, 0);
    }
    this.airMove(dt);
  }

  airMove(dt) {
    const hit = this.moveHoriz(this.vel.x * dt, this.vel.z * dt);
    if (hit && this.vel.y <= 0) {
      // falling against a wall loses the momentum going into it; while rising she keeps
      // pressing forward, so she pops over a ledge as soon as she clears it
      const d = this.vel.x * hit.normal[0] + this.vel.z * hit.normal[2];
      if (d < 0) { this.vel.x -= d * hit.normal[0]; this.vel.z -= d * hit.normal[2]; }
    }
    const newY = this.pos.y + this.vel.y * dt;
    if (this.vel.y > 0) {
      const ceil = this.world.findCeil(this.pos.x, this.pos.y + this.T.height * 0.5, this.pos.z);
      if (ceil && newY + this.T.height > ceil.y) {
        this.vel.y = 0;
        this.onEvent('headBonk');
        return;
      }
      this.pos.y = newY;
      return;
    }
    const floor = this.footFloor(10);
    if (floor && newY <= floor.y) {
      this.pos.y = floor.y;
      this.floor = floor;
      this.land(-this.vel.y, floor);
    } else {
      this.pos.y = newY;
    }
  }

  land(impact, floor) {
    const T = this.T;
    const stomp = this.stomping;
    this.stomping = false;
    this.springRise = false;
    if (floor.tag === 'spring') {
      const vy = stomp ? T.springStomp : Math.max(T.springMin, impact * 0.9);
      this.vel.y = vy;
      if (stomp) { // a stomp-launch carries her forward a little, toward where she faces
        const f = this.forward;
        this.vel.x = f.x * 160;
        this.vel.z = f.z * 160;
      }
      this.springRise = true; // a launch rises the full height even without holding jump
      this.setState('air');
      this.onEvent('spring', { stomp, floor });
      return;
    }
    // keep the horizontal momentum as forward speed
    const vh = Math.hypot(this.vel.x, this.vel.z);
    if (vh > 40) this.yaw = Math.atan2(this.vel.x, this.vel.z);
    this.speed = vh;
    this.grounded = true;
    this.onEvent('land', { impact, stomp, floor, pos: this.pos.clone() });
    if (stomp) {
      this.speed = 0;
      this.setState('stumble', 0.35);
    } else if (impact > T.cryImpact) {
      this.speed = 0;
      this.setState('cry', 2.6);
      this.onEvent('breakdown');
    } else if (impact > T.stumbleImpact) {
      this.speed *= 0.3;
      this.setState('stumble', 0.8);
    } else if (floor.normal[1] < T.slideNY) {
      this.setState('slide');
    } else {
      this.setState('ground');
    }
  }

  stepSink(dt) {
    this.pos.y += this.vel.y * dt;
    if (this.timer <= 0) this.onEvent('drowned');
  }
}
