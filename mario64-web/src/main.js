// Game entry point: ROM -> Mario model + animations, ported SM64 physics, a small
// playground level, a follow camera and a red-coin challenge.

import * as THREE from 'three';
import { parseMarioAnimations } from './rom/anims.js';
import { MarioModel } from './render/marioModel.js';
import { RedCoinModel, StarModel } from './render/objects.js';
import { CowModel, loadCowGltf } from './render/cowModel.js';
import { LowPolyCow, bakeFaceFromGltf } from './render/lowPolyCow.js';
import { setupLighting } from './render/lighting.js';
import { COW_URL } from './game/cowAsset.js';
import { pickRomFile, forgetRom } from './game/romPicker.js';
import { buildPlayground } from './game/level.js';
import { FollowCamera } from './game/camera.js';
import { Input, BTN_A, BTN_B, BTN_Z, BTN_START } from './game/input.js';
import { CollisionWorld } from './engine/surface.js';
import { createMario } from './mario/index.js';
import { A_BUTTON, B_BUTTON, Z_TRIG } from './mario/constants.js';
import { actionName } from './game/actionNames.js';
import { Sfx } from './game/sfx.js';

const TICK = 1 / 30;
// The cow is heavier than Mario: a lower top speed keeps its run cycle believable.
const COW_SPEED_SCALE = 0.78;

const settings = loadSettings();
function loadSettings() {
  try {
    return { character: 'cow64', voice: false, ...JSON.parse(localStorage.getItem('mario64-web-settings') || '{}') };
  } catch {
    return { character: 'cow64', voice: false };
  }
}
function saveSettings() {
  try { localStorage.setItem('mario64-web-settings', JSON.stringify(settings)); } catch { /* storage unavailable */ }
}

const canvas = document.getElementById('game');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = skyTexture();
scene.fog = new THREE.Fog(0xb9dcf7, 7000, 18000);
const camera = new THREE.PerspectiveCamera(45, 1, 20, 30000);
setupLighting(renderer, scene);

function skyTexture() {
  const c = document.createElement('canvas');
  c.width = 2; c.height = 256;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 0, 256);
  grad.addColorStop(0, '#3f86d8');
  grad.addColorStop(0.6, '#8ec5f2');
  grad.addColorStop(1, '#d9eefc');
  g.fillStyle = grad;
  g.fillRect(0, 0, 2, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

const $ = (id) => document.getElementById(id);
const ui = {
  hud: $('hud'), coins: $('coins'), timer: $('timer'), power: $('power'), action: $('actionName'),
  toast: $('toast'), help: $('help'), pause: $('pause'), touch: $('touch'),
};

function makeShadow() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(0,0,0,1)');
  grad.addColorStop(0.75, 'rgba(0,0,0,0.9)');
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4 }));
  mesh.renderOrder = 1;
  return mesh;
}

async function start(rom) {
  const animations = parseMarioAnimations(rom);
  const model = new MarioModel(rom, animations);
  scene.add(model.root);

  // Two cows: the detailed model (own skeleton, retargeted animation) and "Cow 64", a
  // low-poly Mario-proportioned version riding Mario's skeleton. Cow 64 wears the
  // detailed model's mask, baked to a texture, when that model is available.
  let cow = null;
  let face = null;
  try {
    const gltf = await loadCowGltf(COW_URL);
    face = bakeFaceFromGltf(renderer, gltf);
    cow = new CowModel(gltf, model);
    scene.add(cow.root);
  } catch (e) {
    console.error('Could not load the detailed cow model', e);
  }
  const cow64 = new LowPolyCow(model, face);

  const level = buildPlayground();
  scene.add(level.mesh);
  const world = new CollisionWorld(level.tris);
  const sfx = new Sfx(rom);

  const m = createMario({ world, animations, sound: (name, extra) => sfx.play(name, extra) });
  const followCam = new FollowCamera(camera, level.mesh);
  const input = new Input(canvas);
  if (matchMedia('(pointer: coarse)').matches) {
    ui.touch.hidden = false;
    input.attachTouch(ui.touch);
  }

  const shadow = makeShadow();
  scene.add(shadow);

  function applySettings() {
    if (settings.character === 'cow' && !cow) settings.character = 'cow64';
    const asCow = settings.character === 'cow';
    if (cow) cow.root.visible = asCow;
    model.root.visible = !asCow;
    cow64.setActive(settings.character === 'cow64');
    m.speedScale = asCow ? COW_SPEED_SCALE : 1;
    sfx.voiceEnabled = settings.voice;
    $('characterSelect').value = settings.character;
    $('voiceToggle').checked = settings.voice;
    $('characterSelect').querySelector('option[value=cow]').disabled = !cow;
  }
  $('characterSelect').addEventListener('change', (e) => { settings.character = e.target.value; saveSettings(); applySettings(); });
  $('voiceToggle').addEventListener('change', (e) => { settings.voice = e.target.checked; saveSettings(); applySettings(); });
  applySettings();
  const usingCow = () => cow && cow.root.visible;

  const coins = level.redCoins.map((p) => {
    const model = new RedCoinModel(rom);
    scene.add(model.root);
    return { model, mesh: model.root, pos: p, got: false };
  });
  const starModel = new StarModel(rom);
  const star = starModel.root;
  star.visible = false;
  scene.add(star);

  const game = { time: 0, coins: 0, done: false, paused: false, counter: 0 };
  let prevSnap = null;

  function snapshot() {
    const gfx = m.marioObj.header.gfx;
    return { pos: gfx.pos.slice(), angle: gfx.angle.slice(), animID: gfx.animInfo.animID, animFrame: gfx.animInfo.animFrame };
  }

  function respawn() {
    m.reset(level.spawn.pos, level.spawn.yaw);
    followCam.reset(level.spawn.pos, level.spawn.yaw);
    prevSnap = null;
  }

  function restart() {
    game.time = 0; game.coins = 0; game.done = false;
    coins.forEach((c) => { c.got = false; c.mesh.visible = true; });
    if (cow) cow.override = null;
    star.visible = false;
    ui.toast.hidden = true;
    respawn();
  }

  let toastTimer = 0;
  function toast(text, seconds = 2) {
    ui.toast.textContent = text;
    ui.toast.hidden = false;
    toastTimer = seconds;
  }

  function setPaused(p) {
    game.paused = p;
    ui.pause.hidden = !p;
  }
  $('resume').addEventListener('click', () => setPaused(false));
  $('restart').addEventListener('click', () => { restart(); setPaused(false); });
  $('forgetRom').addEventListener('click', async (e) => { e.preventDefault(); await forgetRom(); location.reload(); });
  $('hideHelp').addEventListener('click', (e) => { e.preventDefault(); ui.help.hidden = true; });

  let prevButtons = 0;
  function tick(inp) {
    const pressedNow = inp.buttons & ~prevButtons;
    prevButtons = inp.buttons;
    if (pressedNow & BTN_START) setPaused(!game.paused);
    if (game.paused) return;

    let buttons = 0;
    if (inp.buttons & BTN_A) buttons |= A_BUTTON;
    if (inp.buttons & BTN_B) buttons |= B_BUTTON;
    if (inp.buttons & BTN_Z) buttons |= Z_TRIG;

    prevSnap = snapshot();
    if (cow && cow.override && (inp.stickX || inp.stickY || buttons)) cow.override = null; // end the victory dance
    m.update({ stickX: inp.stickX, stickY: inp.stickY, buttons, cameraYaw: followCam.yaw });
    game.counter++;
    if (m.requestRespawn) {
      sfx.play('SOUND_MARIO_WAAAOOOW');
      respawn();
      return;
    }
    if (!game.done) game.time += TICK;

    // Red coins & star
    const cx = m.pos[0], cy = m.pos[1] + 80, cz = m.pos[2];
    for (const c of coins) {
      if (c.got) continue;
      if (Math.hypot(c.pos[0] - cx, c.pos[1] - cy, c.pos[2] - cz) < 130) {
        c.got = true;
        c.mesh.visible = false;
        game.coins++;
        sfx.coin(game.coins);
        if (game.coins === coins.length) {
          star.visible = true;
          toast('A star appeared on the tower!', 3);
        }
      }
    }
    if (star.visible && !game.done) {
      const s = level.starPos;
      if (Math.hypot(s[0] - cx, s[1] - cy, s[2] - cz) < 160) {
        game.done = true;
        star.visible = false;
        sfx.star();
        if (cow) cow.override = 'Chicken Dance';
        toast(`STAR GET!  ${formatTime(game.time)}`, 1e9);
      }
    }
  }

  function formatTime(t) {
    const min = Math.floor(t / 60);
    const sec = Math.floor(t % 60);
    const tenth = Math.floor((t * 10) % 10);
    return `${min}'${sec.toString().padStart(2, '0')}"${tenth}`;
  }

  function updateHud() {
    ui.coins.textContent = game.coins;
    ui.timer.textContent = formatTime(game.time);
    const wedges = Math.max(0, Math.min(8, m.health >> 8));
    const color = wedges > 4 ? '#3cc8ff' : wedges > 2 ? '#ffd23a' : '#ff4b3e';
    ui.power.style.background = `conic-gradient(${color} ${wedges * 45}deg, rgba(0,0,0,.45) 0)`;
    ui.action.textContent = actionName(m.action);
  }

  restart();
  ui.hud.hidden = false;
  ui.help.hidden = false;

  let acc = 0, last = performance.now();
  function frame(now) {
    const dt = Math.min((now - last) / 1000, 0.1);
    last = now;
    acc += dt;
    const inp = input.poll();
    while (acc >= TICK) {
      acc -= TICK;
      tick(inp);
    }
    const alpha = game.paused ? 1 : acc / TICK;

    if (usingCow()) cow.update(m, prevSnap, alpha, game.paused ? 0 : dt);
    else model.update(m, prevSnap, alpha);
    const gp = model.root.matrix.elements;
    // shadow on the floor under Mario, fading with height
    if (m.floor) {
      const h = gp[13] - m.floorHeight;
      shadow.visible = h < 1500;
      const s = (usingCow() ? 135 : settings.character === 'cow64' ? 125 : 100) * Math.max(0.5, 1 - h / 1500);
      shadow.scale.set(s, 1, s);
      shadow.position.set(gp[12], m.floorHeight + 2, gp[14]);
      const n = m.floor.normal;
      shadow.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(n.x, n.y, n.z));
      shadow.material.opacity = (0xb4 / 255) * Math.max(0.2, 1 - h / 1500);
    } else {
      shadow.visible = false;
    }

    if (toastTimer > 0 && (toastTimer -= dt) <= 0) ui.toast.hidden = true;

    followCam.update(m, game.paused ? { camX: 0, camY: 0, zoom: 0, mouseX: 0, mouseY: 0, wheel: 0 } : inp, dt,
      [gp[12], gp[13], gp[14]]);
    camera.updateMatrixWorld();
    const spin = Math.floor(now / (1000 / 30));
    for (const c of coins) if (!c.got) c.model.update(c.pos, camera, spin);
    if (star.visible) starModel.update(level.starPos, (spin * 0x800) & 0xffff);
    updateHud();
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  window.__game = { m, model, cow, cow64, world, level, game, followCam, sfx };
}

pickRomFile(start);
