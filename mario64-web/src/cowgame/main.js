// "Leave Me Alone": a weighty platformer for The Misanthropic Cow.
// No ROM needed: she moves with her own physics and animates with her own clips.

import * as THREE from 'three';
import { GLTFLoader } from '../../vendor/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from '../../vendor/addons/libs/meshopt_decoder.module.js';
import { COW_URL } from '../game/cowAsset.js';
import { setupLighting } from '../render/lighting.js';
import { FollowCamera } from '../game/camera.js';
import { Input, BTN_A, BTN_B, BTN_Z, BTN_START } from '../game/input.js';
import { World } from './collision.js';
import { CowController } from './controller.js';
import { CowAnimator } from './animator.js';
import { buildCourse, populateCourse } from './level.js';
import { CowSfx } from './sfx.js';
import { Breakable, CrackedFloor, Spring, debris } from './objects.js';

const STEP = 1 / 60;
const $ = (id) => document.getElementById(id);

const canvas = $('game');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9fcdf0);
scene.fog = new THREE.Fog(0x9fcdf0, 5000, 14000);
setupLighting(renderer, scene);
const camera = new THREE.PerspectiveCamera(50, 1, 20, 30000);
function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

async function loadCow() {
  const loader = new GLTFLoader();
  loader.setMeshoptDecoder(MeshoptDecoder);
  return loader.loadAsync(COW_URL);
}

function makeShadow() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(0,0,0,0.9)');
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4 }));
  m.renderOrder = 1;
  return m;
}

async function start() {
  let gltf;
  try {
    gltf = await loadCow();
  } catch (e) {
    $('loading').innerHTML = '<h1>Cow not found</h1><p>This game needs <code>assets/misanthropic_cow.glb</code>. ' +
      'Use the standalone build, or copy the model into <code>assets/</code>.</p>';
    console.error(e);
    return;
  }

  const sfx = new CowSfx();
  const course = buildCourse();
  scene.add(course.mesh);
  const world = new World(course.tris);
  world.water = course.water;

  const game = {
    scene, world, sfx, effects: [], objects: [],
    phones: 0, phonesTotal: 0, breakdowns: 0, time: 0, finished: false, paused: false,
    checkpoint: { pos: course.spawn.pos, yaw: course.spawn.yaw },
    shake: 0,
  };

  const anim = new CowAnimator(gltf);
  scene.add(anim.root);
  const shadow = makeShadow();
  scene.add(shadow);

  // --- events from the controller -------------------------------------------
  const onEvent = (name, data = {}) => {
    switch (name) {
      case 'jump': sfx.grunt(); break;
      case 'land': {
        anim.land(data.impact, data.stomp);
        if (data.stomp) {
          sfx.stomp();
          game.shake = 0.6;
          shockwave(data.pos, data.floor);
        } else if (data.impact > 600) {
          sfx.thud(data.impact);
          if (data.impact > 1400) game.shake = Math.min(0.5, data.impact / 5000);
        }
        break;
      }
      case 'spring': {
        sfx.boing(data.stomp);
        const owner = data.floor.body && data.floor.body.owner;
        if (owner instanceof Spring) owner.bounce();
        if (data.stomp) game.shake = 0.3;
        break;
      }
      case 'breakdown':
        game.breakdowns++;
        sfx.sob();
        hint('That was a long way down. She needs a minute.');
        break;
      case 'bonk': sfx.thud(1800); game.shake = 0.35; break;
      case 'smash': game.shake = 0.3; break;
      case 'skid': sfx.skid(); break;
      case 'wobbleFall': sfx.grunt(); hint('Too fast for the beam! Hold Ctrl to tiptoe.'); break;
      case 'headBonk': sfx.thud(800); break;
      case 'stompStart': sfx.osc('sine', 300, 600, 0.15, 0.1); break;
      case 'splash': sfx.splash(); splashFx(data.pos, data.y); break;
      case 'drowned':
      case 'fellOut':
        respawn(true);
        break;
      default: break;
    }
  };

  const cow = new CowController(world, onEvent);
  game.cow = cow;

  function shockwave(pos, floor) {
    const ring = new THREE.Mesh(new THREE.RingGeometry(40, 60, 32).rotateX(-Math.PI / 2),
      new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7, depthWrite: false }));
    ring.position.set(pos.x, pos.y + 4, pos.z);
    scene.add(ring);
    game.effects.push({ t: 0.5, update(dt) {
      this.t -= dt;
      const s = 1 + (0.5 - this.t) * 10;
      ring.scale.set(s, 1, s);
      ring.material.opacity = Math.max(0, this.t * 1.4);
      if (this.t <= 0) { scene.remove(ring); return false; }
      return true;
    } });
    for (const o of game.objects) {
      if (!o.stompable || !o.body || !o.body.enabled) continue;
      const onIt = floor && floor.body === o.body;
      const near = o instanceof Breakable && o.object.position.distanceTo(pos) < 260;
      if (onIt || near) o.smash();
    }
  }

  function splashFx(pos, y) {
    debris(game, new THREE.Vector3(pos.x, y, pos.z), 0x9fd3ff, 18, 18);
  }

  // --- game API used by objects ----------------------------------------------
  let hintTimer = 0;
  function hint(text) {
    $('hint').textContent = text;
    $('hint').hidden = false;
    hintTimer = 5.5;
  }
  game.hint = hint;
  game.setCheckpoint = (cp) => {
    const p = cp.object.position;
    if (p.z < game.checkpoint.pos[2]) { // only checkpoints further along the course
      game.checkpoint = { pos: [p.x + 150, p.y, p.z], yaw: course.spawn.yaw };
      if (game.started) sfx.checkpoint();
    }
  };
  game.onPhoneSilenced = () => {
    game.phones++;
    sfx.silence();
  };
  game.finish = (couch) => {
    game.finished = true;
    game.couch = couch;
    const seat = couch.object.localToWorld(new THREE.Vector3(0, 0, 18));
    cow.reset([seat.x, couch.object.position.y + 18, seat.z], couch.yaw, false);
    cow.setState('sit');
    prevPos.copy(cow.pos);
    prevYaw = cow.yaw;
    sfx.finish();
    setTimeout(() => sfx.sigh(), 1400);
    $('finish').hidden = false;
    $('finishStats').innerHTML =
      `Time ${formatTime(game.time)} · Phones silenced ${game.phones}/${game.phonesTotal} · ` +
      `Breakdowns ${game.breakdowns}`;
  };

  game.objects = populateCourse(game);
  const followCam = new FollowCamera(camera, course.mesh);
  followCam.dist = 680; // close enough to see how heavy she moves
  const input = new Input(canvas);
  if (matchMedia('(pointer: coarse)').matches) {
    $('touch').hidden = false;
    input.attachTouch($('touch'));
  }

  const prevPos = new THREE.Vector3();
  let prevYaw = 0;
  function respawn(sigh) {
    const cp = game.checkpoint;
    cow.reset(cp.pos, cp.yaw);
    prevPos.copy(cow.pos);
    prevYaw = cow.yaw;
    followCam.reset(cp.pos, Math.round((cp.yaw / Math.PI) * 0x8000)); // camera takes SM64 angle units
    if (sigh) {
      anim.play('Exasperated', 3.0, 5.2, 1.3, 0.2); // facepalm
      sfx.sigh();
    }
  }

  function restart() {
    location.reload();
  }
  function setPaused(p) {
    game.paused = p;
    $('pause').hidden = !p;
  }
  $('resume').addEventListener('click', () => setPaused(false));
  $('restart').addEventListener('click', restart);
  $('again').addEventListener('click', restart);
  $('hideHelp').addEventListener('click', (e) => { e.preventDefault(); $('help').hidden = true; });

  function formatTime(t) {
    return `${Math.floor(t / 60)}'${String(Math.floor(t % 60)).padStart(2, '0')}"${Math.floor((t * 10) % 10)}`;
  }

  // --- main loop ---------------------------------------------------------------
  respawn(false);
  game.started = true;
  $('loading').hidden = true;
  $('hud').hidden = false;
  $('help').hidden = false;

  let acc = 0, last = performance.now(), prevButtons = 0, stepDist = 0, simTime = 0;
  const camFwd = new THREE.Vector3();
  function frame(now) {
    const dt = Math.min((now - last) / 1000, 0.1);
    last = now;
    const inp = input.poll();
    const pressed = inp.buttons & ~prevButtons;
    prevButtons = inp.buttons;
    if (pressed & BTN_START && !game.finished) setPaused(!game.paused);

    if (!game.paused) {
      // stick -> world direction relative to the camera
      camera.getWorldDirection(camFwd);
      camFwd.y = 0;
      camFwd.normalize();
      const sx = inp.stickX / 80, sy = inp.stickY / 80;
      const mx = camFwd.x * sy - camFwd.z * sx;
      const mz = camFwd.z * sy + camFwd.x * sx;
      const control = game.finished ? { mx: 0, mz: 0 } : { mx, mz };
      const ci = {
        ...control,
        jump: !game.finished && !!(inp.buttons & BTN_A),
        crouch: !game.finished && !!(inp.buttons & BTN_Z),
        sprint: !!(inp.buttons & BTN_B),
        sneak: input.keys.has('walk'),
      };
      acc += dt;
      while (acc >= STEP) {
        acc -= STEP;
        simTime += STEP;
        prevPos.copy(cow.pos);
        prevYaw = cow.yaw;
        for (const o of game.objects) o.update(STEP, simTime);
        cow.tired = game.breakdowns >= 3;
        cow.step(STEP, ci);
        if (!game.finished) game.time += STEP;
        // footsteps
        if (cow.grounded && cow.state === 'ground' && cow.speed > 30) {
          stepDist += cow.speed * STEP;
          const stride = cow.speed > 450 ? 150 : 115;
          if (stepDist > stride) { stepDist = 0; sfx.step(cow.speed > 450 ? 1.3 : 0.8); }
        }
      }
      game.effects = game.effects.filter((e) => e.update(dt));
    }

    const alpha = game.paused ? 1 : acc / STEP;
    const pos = prevPos.clone().lerp(cow.pos, alpha);
    let dyaw = cow.yaw - prevYaw;
    while (dyaw > Math.PI) dyaw -= Math.PI * 2;
    while (dyaw < -Math.PI) dyaw += Math.PI * 2;
    anim.update(game.paused ? 0 : dt, cow, pos, prevYaw + dyaw * alpha);

    // blob shadow on the floor below her
    const f = world.findFloor(pos.x, pos.y + 10, pos.z, 0);
    if (f) {
      const h = pos.y - f.y;
      shadow.visible = h < 1500;
      const s = 150 * Math.max(0.45, 1 - h / 1200);
      shadow.scale.set(s, 1, s);
      shadow.position.set(pos.x, f.y + 2, pos.z);
      shadow.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(...f.normal));
      shadow.material.opacity = Math.max(0.2, 1 - h / 1200) * 0.6;
    } else shadow.visible = false;

    if (game.finished) {
      // a fixed shot of her on the couch
      const eye = game.couch.object.localToWorld(new THREE.Vector3(60, 200, 400));
      camera.position.lerp(eye, 1 - Math.exp(-dt * 3));
      camera.lookAt(pos.x, pos.y - 10, pos.z); // aim low so she sits in the upper half, above the card
    } else {
      const camInput = game.paused ? { camX: 0, camY: 0, zoom: 0, mouseX: 0, mouseY: 0, wheel: 0 } : inp;
      followCam.update({ action: cow.grounded ? 0 : 1 << 11 }, camInput, dt, [pos.x, pos.y, pos.z]);
    }
    if (game.shake > 0) {
      game.shake = Math.max(0, game.shake - dt);
      const a = game.shake * 18;
      camera.position.add(new THREE.Vector3((Math.random() - 0.5) * a, (Math.random() - 0.5) * a, (Math.random() - 0.5) * a));
    }

    // HUD
    $('phones').textContent = `${game.phones}/${game.phonesTotal}`;
    $('timer').textContent = formatTime(game.time);
    $('breakdowns').textContent = game.breakdowns ? `Breakdowns: ${game.breakdowns}` : '';
    const meter = $('meter');
    if (cow.wobble > 0.02 || cow.state === 'charge') {
      meter.hidden = false;
      const v = cow.state === 'charge' ? cow.charge : cow.wobble;
      $('meterLabel').textContent = cow.state === 'charge' ? 'Crouch' : 'Balance';
      $('meterFill').style.width = `${Math.round(Math.min(1, v) * 100)}%`;
      $('meterFill').style.background = cow.state === 'charge' ? '#ffd23a' : v > 0.7 ? '#ff4b3e' : '#ffd23a';
    } else meter.hidden = true;
    if (hintTimer > 0 && (hintTimer -= dt) <= 0) $('hint').hidden = true;

    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  // Deterministic stepping for automated tests: run the simulation for `seconds`
  // with a fixed input (bypasses rendering).
  const simulate = (ci, seconds) => {
    const full = { mx: 0, mz: 0, jump: false, crouch: false, sprint: false, sneak: false, ...ci };
    for (let i = 0; i < Math.round(seconds / STEP); i++) {
      simTime += STEP;
      prevPos.copy(cow.pos);
      prevYaw = cow.yaw;
      for (const o of game.objects) o.update(STEP, simTime);
      cow.step(STEP, full);
    }
  };
  window.__cowgame = { game, cow, anim, world, followCam, simulate, respawn };
}

start();
