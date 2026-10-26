// A simple Lakitu-style follow camera. The camera is "dragged" behind Mario on a
// leash (so running sideways swings it around naturally), can be rotated by the
// player, and is pushed in front of walls so it never ends up inside the level.

import * as THREE from 'three';
import { atan2s } from '../engine/math_util.js';

const AIR_FLAG = 1 << 11; // ACT_FLAG_AIR

export class FollowCamera {
  constructor(camera, levelMesh) {
    this.camera = camera;
    this.level = levelMesh;
    this.dist = 950;
    this.pitch = 0.32;
    this.focus = new THREE.Vector3();
    this.pos = new THREE.Vector3();
    this.groundY = 0;
    this.ray = new THREE.Raycaster();
  }

  reset(marioPos, faceYaw) {
    const a = (faceYaw / 0x8000) * Math.PI;
    this.focus.set(marioPos[0], marioPos[1] + 125, marioPos[2]);
    this.groundY = marioPos[1];
    this.snap = true;
    // behind Mario: opposite of the direction he faces (sins(yaw) = x, coss(yaw) = z)
    this.pos.set(this.focus.x - Math.sin(a) * this.dist, 0, this.focus.z - Math.cos(a) * this.dist);
  }

  /** The yaw Mario's controls are relative to (camera->yaw in SM64). */
  get yaw() {
    return atan2s(this.pos.z - this.focus.z, this.pos.x - this.focus.x);
  }

  /**
   * @param m Mario state (for the action flags)
   * @param p interpolated position Mario is drawn at
   */
  update(m, input, dt, p) {
    const inAir = (m.action & AIR_FLAG) !== 0;
    if (!inAir) this.groundY = p[1];
    // Don't bob with every jump; follow vertical motion only when it leaves the band.
    let targetY = this.groundY;
    if (p[1] > this.groundY + 400) targetY = p[1] - 400;
    if (p[1] < this.groundY - 100) targetY = p[1] + 100;
    this.focus.x = p[0];
    this.focus.z = p[2];
    this.focus.y += (targetY + 125 - this.focus.y) * (this.snap ? 1 : 1 - Math.exp(-dt * 5));
    this.snap = false;

    // Manual control
    const turn = input.camX * dt * 2.4 + input.mouseX * 0.006;
    this.pitch = Math.max(-0.15, Math.min(1.2, this.pitch + input.camY * dt * 1.5 + input.mouseY * 0.004));
    this.dist = Math.max(500, Math.min(2200, this.dist * (1 + input.zoom * dt * 1.2 + input.wheel * 0.08)));

    // Leash: keep the current direction from Mario to the camera, rotated by input
    const ang = Math.atan2(this.pos.x - this.focus.x, this.pos.z - this.focus.z) - turn;
    const horiz = Math.cos(this.pitch) * this.dist;
    this.pos.x = this.focus.x + Math.sin(ang) * horiz;
    this.pos.z = this.focus.z + Math.cos(ang) * horiz;
    this.pos.y = this.focus.y + Math.sin(this.pitch) * this.dist;

    // Keep the camera out of walls: cast from the focus point to the camera
    const cam = this.camera;
    const dir = new THREE.Vector3().subVectors(this.pos, this.focus);
    const full = dir.length();
    dir.normalize();
    this.ray.set(this.focus, dir);
    this.ray.far = full;
    const hit = this.level ? this.ray.intersectObject(this.level, true)[0] : null;
    const eye = hit ? this.focus.clone().addScaledVector(dir, Math.max(80, hit.distance - 60)) : this.pos.clone();
    cam.position.copy(eye);
    cam.lookAt(this.focus);
  }
}
