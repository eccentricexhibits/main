// Interactive pieces of the cow course. Most of them react to her weight.

import * as THREE from 'three';
import { LevelBuilder } from '../game/level.js';
import { Body } from './collision.js';

/** Build meshes + local collision triangles for a set of boxes in object space. */
function boxes(list) {
  const L = new LevelBuilder();
  for (const [x0, y0, z0, x1, y1, z1, opts] of list) L.box(x0, y0, z0, x1, y1, z1, opts || {});
  return { group: L.buildMeshes(), tris: L.tris };
}

function standingOn(cow, body) {
  return cow.grounded && cow.floor && cow.floor.body === body;
}

class Thing {
  constructor(game, x, y, z) {
    this.game = game;
    this.object = new THREE.Group();
    this.object.position.set(x, y, z);
    this.home = new THREE.Vector3(x, y, z);
    game.scene.add(this.object);
  }

  addBody(tris, opts = {}) {
    this.body = this.game.world.addBody(new Body(this.object, tris, { owner: this, ...opts }));
    return this.body;
  }

  update() {}
}

/** Debris burst used by everything that breaks. */
export function debris(game, pos, color, count = 14, size = 26) {
  const mat = new THREE.MeshLambertMaterial({ color });
  for (let i = 0; i < count; i++) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(size * (0.4 + Math.random()), size * 0.3, size * (0.4 + Math.random())), mat);
    m.position.copy(pos).add(new THREE.Vector3((Math.random() - 0.5) * 80, Math.random() * 60, (Math.random() - 0.5) * 80));
    const v = new THREE.Vector3((Math.random() - 0.5) * 500, 300 + Math.random() * 500, (Math.random() - 0.5) * 500);
    const spin = new THREE.Vector3(Math.random() * 10, Math.random() * 10, Math.random() * 10);
    game.scene.add(m);
    game.effects.push({ t: 1.4, update(dt) {
      v.y -= 2400 * dt;
      m.position.addScaledVector(v, dt);
      m.rotation.x += spin.x * dt; m.rotation.y += spin.y * dt;
      this.t -= dt;
      if (this.t <= 0) { game.scene.remove(m); m.geometry.dispose(); return false; }
      return true;
    } });
  }
}

/** A rickety plank: cracks under her, then drops. Comes back once she's gone. */
export class CrumblePlank extends Thing {
  constructor(game, x, y, z, w = 260, d = 110) {
    super(game, x, y, z);
    const { group, tris } = boxes([[-w / 2, -24, -d / 2, w / 2, 0, d / 2, { top: 'plank', side: 'plank' }]]);
    this.mesh = group;
    this.object.add(group);
    this.addBody(tris);
    this.load = 0;
    this.falling = 0;
    this.gone = 0;
  }

  update(dt) {
    const cow = this.game.cow;
    if (this.gone > 0) {
      this.gone -= dt;
      if (this.gone <= 0) { // reset once she isn't right there
        if (cow.pos.distanceTo(this.home) < 300) { this.gone = 0.5; return; }
        this.object.position.copy(this.home);
        this.object.rotation.set(0, 0, 0);
        this.object.visible = true;
        this.body.enabled = true;
        this.load = 0;
        this.falling = 0;
      }
      return;
    }
    if (this.falling > 0) {
      this.falling += dt;
      this.object.position.y -= 900 * this.falling * dt;
      this.object.rotation.z += dt * 1.5;
      if (this.falling > 1.5) { this.object.visible = false; this.gone = 4; }
      return;
    }
    if (standingOn(cow, this.body)) {
      if (this.load === 0) this.game.sfx.creak();
      this.load += dt;
    } else if (this.load > 0) {
      this.load = Math.max(0.0001, this.load - dt * 0.3);
    }
    if (this.load > 0.4) { // shake
      this.mesh.position.set((Math.random() - 0.5) * 6, (Math.random() - 0.5) * 3, 0);
    }
    if (this.load > 0.9) {
      this.falling = 0.001;
      this.body.enabled = false;
      this.mesh.position.set(0, 0, 0);
      this.game.sfx.crack();
    }
  }
}

/** A floating raft that sinks while she stands on it and bobs back up afterwards. */
export class SinkingRaft extends Thing {
  constructor(game, x, z, waterY, size = 230) {
    super(game, x, waterY + 22, z);
    const h = size / 2;
    const { group, tris } = boxes([[-h, -40, -h, h, 0, h, { top: 'plank', side: 'wood' }]]);
    this.object.add(group);
    this.addBody(tris);
    this.top = waterY + 22;
    this.sink = 0;
    this.phase = Math.random() * 6;
  }

  update(dt, t) {
    const on = standingOn(this.game.cow, this.body);
    this.sink = on ? Math.min(200, this.sink + 60 * dt) : Math.max(0, this.sink - 80 * dt);
    this.object.position.y = this.top - this.sink + Math.sin(t * 1.7 + this.phase) * 4;
    this.object.rotation.x = Math.sin(t * 1.3 + this.phase) * 0.02;
    this.object.rotation.z = Math.cos(t * 1.1 + this.phase) * 0.02;
    this.game.world.updateBody(this.body);
  }
}

/** Only something as heavy as her can push one of these down. Latches when pressed. */
export class PressurePlate extends Thing {
  constructor(game, x, y, z, onPress) {
    super(game, x, y, z);
    const { group, tris } = boxes([[-90, 0, -90, 90, 14, 90, { top: 'pad', side: 'stone' }]]);
    this.mesh = group;
    this.object.add(group);
    this.addBody(tris);
    this.pressed = false;
    this.onPress = onPress;
  }

  update(dt) {
    if (!this.pressed && standingOn(this.game.cow, this.body)) {
      this.pressed = true;
      this.game.sfx.clunk();
      this.onPress && this.onPress(this);
    }
    const targetY = this.pressed ? this.home.y - 11 : this.home.y;
    if (Math.abs(this.object.position.y - targetY) > 0.1) {
      this.object.position.y += (targetY - this.object.position.y) * Math.min(1, dt * 10);
      this.game.world.updateBody(this.body);
    }
  }
}

/** A heavy gate that slides up into the hedge once opened. */
export class Gate extends Thing {
  constructor(game, x, y, z, w = 1400, h = 320) {
    super(game, x, y, z);
    const { group, tris } = boxes([[-w / 2, 0, -24, w / 2, h, 24, { top: 'stone', side: 'brick' }]]);
    this.object.add(group);
    this.addBody(tris);
    this.opening = false;
    this.h = h;
  }

  open() {
    if (this.opening) return;
    this.opening = true;
    this.game.sfx.rumble();
  }

  update(dt) {
    if (!this.opening || this.object.position.y > this.home.y + this.h + 10) return;
    this.object.position.y += 180 * dt;
    this.game.world.updateBody(this.body);
  }
}

/** Something that breaks: a flimsy fence (stampede through it) or a crate (stampede or stomp). */
export class Breakable extends Thing {
  constructor(game, x, y, z, size, opts = {}) {
    super(game, x, y, z);
    const [w, h, d] = size;
    const { group, tris } = boxes([[-w / 2, 0, -d / 2, w / 2, h, d / 2, { top: opts.tex || 'crate', side: opts.tex || 'crate' }]]);
    this.object.add(group);
    this.addBody(tris);
    this.smashable = true;
    this.stompable = !!opts.stompable;
    this.color = opts.color || 0xb07a3c;
    this.contents = opts.contents || null;
    this.size = size;
    this.broken = false;
  }

  smash() {
    if (this.broken) return;
    this.broken = true;
    this.body.enabled = false;
    this.object.visible = false;
    const c = this.object.position.clone();
    c.y += this.size[1] / 2;
    debris(this.game, c, this.color, Math.min(28, 8 + Math.round(this.size[0] / 60)));
    this.game.sfx.smash();
    if (this.contents) this.contents(this);
  }
}

/** A cracked slab over a pit: only a stomp breaks it. */
export class CrackedFloor extends Thing {
  constructor(game, x, y, z, w, d) {
    super(game, x, y, z);
    const { group, tris } = boxes([[-w / 2, -30, -d / 2, w / 2, 0, d / 2, { top: 'crack', side: 'stone' }]]);
    this.object.add(group);
    this.addBody(tris);
    this.stompable = true;
    this.w = w;
    this.d = d;
  }

  smash() {
    if (!this.body.enabled) return;
    this.body.enabled = false;
    this.object.visible = false;
    debris(this.game, this.object.position, 0x9d9a90, 24, 40);
    this.game.sfx.smash();
  }
}

/** A springboard. Landing bounces her a little; a stomp launches her. */
export class Spring extends Thing {
  constructor(game, x, y, z, r = 120) {
    super(game, x, y, z);
    const { group, tris } = boxes([
      [-r, 0, -r, r, 24, r, { top: 'spring', side: 'stone', type: 'spring' }],
    ]);
    // the top surface carries the 'spring' tag
    for (const t of tris) t.type = 'spring';
    this.mesh = group;
    this.object.add(group);
    this.addBody(tris);
    this.boing = 0;
  }

  bounce() {
    this.boing = 1;
  }

  update(dt, t) {
    if (this.boing > 0) {
      this.boing = Math.max(0, this.boing - dt * 2.5);
      this.mesh.scale.y = 1 - Math.sin(this.boing * Math.PI * 3) * this.boing * 0.4;
    }
  }
}

/** A ringing phone. She'd like it to stop. Walk into it to silence it. */
export class Phone extends Thing {
  constructor(game, x, y, z, follow = null) {
    super(game, x, y, z);
    const red = new THREE.MeshLambertMaterial({ color: 0xd7262e });
    const dark = new THREE.MeshLambertMaterial({ color: 0x222222 });
    const base = new THREE.Mesh(new THREE.BoxGeometry(56, 26, 46), red);
    base.position.y = 13;
    const handset = new THREE.Mesh(new THREE.CapsuleGeometry(9, 50, 4, 8), red);
    handset.rotation.z = Math.PI / 2;
    handset.position.y = 34;
    const dial = new THREE.Mesh(new THREE.CylinderGeometry(13, 13, 4, 12), dark);
    dial.rotation.x = Math.PI / 2 - 0.5;
    dial.position.set(0, 18, 24);
    this.mesh = new THREE.Group();
    this.mesh.add(base, handset, dial);
    this.mesh.scale.setScalar(1.3);
    this.object.add(this.mesh);
    this.follow = follow; // { object, offset } to ride on a raft
    this.silenced = false;
    this.ringClock = Math.random() * 3;
  }

  update(dt, t) {
    if (this.follow) {
      this.object.position.copy(this.follow.object.position).add(this.follow.offset);
    }
    if (this.silenced) return;
    this.ringClock += dt;
    const ringing = this.ringClock % 3 < 1.2;
    this.mesh.position.x = ringing ? Math.sin(t * 70) * 3 : 0;
    this.mesh.rotation.y = t * 0.6;
    const cow = this.game.cow;
    const p = this.object.position;
    const d = cow.pos.distanceTo(p);
    if (ringing && Math.floor(this.ringClock * 8) !== Math.floor((this.ringClock - dt) * 8) && d < 1600) {
      this.game.sfx.ring(1 - d / 1600);
    }
    // her body spans ~160 units upward from her feet
    const dy = p.y - cow.pos.y;
    if (Math.hypot(cow.pos.x - p.x, cow.pos.z - p.z) < 105 && dy > -60 && dy < 170) this.silence();
  }

  silence() {
    if (this.silenced) return;
    this.silenced = true;
    this.mesh.rotation.set(0, 0, Math.PI / 2); // knocked over
    this.mesh.position.set(0, -8, 0);
    this.game.onPhoneSilenced(this);
  }
}

function signTexture(text, bg, fg) {
  const c = document.createElement('canvas');
  c.width = 256; c.height = 128;
  const g = c.getContext('2d');
  g.fillStyle = bg; g.fillRect(0, 0, 256, 128);
  g.strokeStyle = fg; g.lineWidth = 8; g.strokeRect(6, 6, 244, 116);
  g.fillStyle = fg;
  g.font = 'bold 34px system-ui, sans-serif';
  g.textAlign = 'center';
  const lines = text.split('\n');
  lines.forEach((l, i) => g.fillText(l, 128, 64 + (i - (lines.length - 1) / 2) * 40 + 12));
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** A DO NOT DISTURB sign: checkpoint. */
export class Checkpoint extends Thing {
  constructor(game, x, y, z, yaw = 0) {
    super(game, x, y, z);
    const post = new THREE.Mesh(new THREE.BoxGeometry(12, 170, 12), new THREE.MeshLambertMaterial({ color: 0x6b4a2a }));
    post.position.y = 85;
    this.offTex = signTexture('DO NOT\nDISTURB', '#f2efe6', '#c23b2e');
    this.onTex = signTexture('DO NOT\nDISTURB', '#c23b2e', '#ffffff');
    this.board = new THREE.Mesh(new THREE.PlaneGeometry(130, 65), new THREE.MeshLambertMaterial({ map: this.offTex, side: THREE.DoubleSide }));
    this.board.position.y = 175;
    this.object.add(post, this.board);
    this.object.rotation.y = yaw;
    this.yaw = yaw;
    this.active = false;
  }

  update() {
    const cow = this.game.cow;
    if (!this.active && cow.grounded && cow.pos.distanceTo(this.object.position) < 260) {
      this.active = true;
      this.board.material.map = this.onTex;
      this.board.material.needsUpdate = true;
      this.game.setCheckpoint(this);
    }
  }
}

/** Her couch. Reaching it ends the level. */
export class Couch extends Thing {
  constructor(game, x, y, z, yaw = 0) {
    super(game, x, y, z);
    const { group, tris } = boxes([
      [-120, 0, -45, 120, 50, 50, { top: 'couch', side: 'couch' }], // seat
      [-120, 0, -80, 120, 125, -45, { top: 'couch', side: 'couch' }], // back
      [-150, 0, -80, -120, 80, 50, { top: 'couch', side: 'couch' }], // arms
      [120, 0, -80, 150, 80, 50, { top: 'couch', side: 'couch' }],
    ]);
    this.object.add(group);
    this.object.rotation.y = yaw;
    this.yaw = yaw;
    this.seatY = y + 50;
    void tris; // the couch is a trigger, not a platform
  }

  update() {
    const cow = this.game.cow;
    if (this.game.finished) return;
    const local = this.object.worldToLocal(cow.pos.clone());
    if (Math.abs(local.x) < 180 && local.z > -60 && local.z < 200 && Math.abs(local.y) < 120 && cow.grounded) {
      this.game.finish(this);
    }
  }
}

/** Shows a hint the first time she walks into a zone. */
export class Hint {
  constructor(game, x0, z0, x1, z1, text) {
    Object.assign(this, { game, x0: Math.min(x0, x1), x1: Math.max(x0, x1), z0: Math.min(z0, z1), z1: Math.max(z0, z1), text, shown: false });
  }

  update() {
    const p = this.game.cow.pos;
    if (!this.shown && p.x > this.x0 && p.x < this.x1 && p.z > this.z0 && p.z < this.z1) {
      this.shown = true;
      this.game.hint(this.text);
    }
  }
}
