// Standalone animation browser: every one of Mario's 209 animations, straight from the ROM.
import * as THREE from 'three';
import { parseMarioAnimations } from './rom/anims.js';
import { MarioModel } from './render/marioModel.js';
import { pickRomFile } from './game/romPicker.js';
import { CowModel, loadCowGltf } from './render/cowModel.js';
import { LowPolyCow, bakeFaceFromGltf } from './render/lowPolyCow.js';
import { COW_URL } from './game/cowAsset.js';
import { setupLighting } from './render/lighting.js';

const canvas = document.getElementById('view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87b8e8);
const camera = new THREE.PerspectiveCamera(45, 1, 10, 20000);
renderer.outputColorSpace = THREE.SRGBColorSpace;
setupLighting(renderer, scene);

const floor = new THREE.Mesh(
  new THREE.CircleGeometry(400, 48).rotateX(-Math.PI / 2),
  new THREE.MeshBasicMaterial({ color: 0x5aa04a }));
scene.add(floor);

let yaw = 0.6, pitch = 0.25, dist = 520;
window.__setYaw = (y, p, d) => { yaw = y; if (p !== undefined) pitch = p; if (d !== undefined) dist = d; }; // used by automated screenshots
function placeCamera() {
  const target = new THREE.Vector3(0, 80, 0);
  camera.position.set(
    target.x + Math.sin(yaw) * Math.cos(pitch) * dist,
    target.y + Math.sin(pitch) * dist,
    target.z + Math.cos(yaw) * Math.cos(pitch) * dist);
  camera.lookAt(target);
}
let dragging = null;
canvas.addEventListener('pointerdown', (e) => { dragging = { x: e.clientX, y: e.clientY }; canvas.setPointerCapture(e.pointerId); });
canvas.addEventListener('pointerup', () => { dragging = null; });
canvas.addEventListener('pointermove', (e) => {
  if (!dragging) return;
  yaw -= (e.clientX - dragging.x) * 0.01;
  pitch = Math.max(-0.2, Math.min(1.4, pitch + (e.clientY - dragging.y) * 0.01));
  dragging = { x: e.clientX, y: e.clientY };
});
canvas.addEventListener('wheel', (e) => { dist = Math.max(150, Math.min(2000, dist * (e.deltaY > 0 ? 1.1 : 0.9))); e.preventDefault(); }, { passive: false });

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

const ui = {
  select: document.getElementById('animSelect'),
  slider: document.getElementById('frameSlider'),
  info: document.getElementById('animInfo'),
  play: document.getElementById('playPause'),
  eyes: document.getElementById('eyeSelect'),
  hands: document.getElementById('handSelect'),
  cap: document.getElementById('capToggle'),
};

async function start(rom) {
  const animations = parseMarioAnimations(rom);
  const model = new MarioModel(rom, animations);
  scene.add(model.root);
  let cow = null;
  let face = null;
  try {
    const gltf = await loadCowGltf(COW_URL);
    face = bakeFaceFromGltf(renderer, gltf);
    cow = new CowModel(gltf, model);
    cow.useNativeClips = false;
    scene.add(cow.root);
    for (const name of cow.clipNames) {
      const opt = document.createElement('option');
      opt.value = opt.textContent = name;
      document.getElementById('clipSelect').append(opt);
    }
  } catch (e) {
    console.error('Cow model unavailable', e);
  }
  const charSelect = document.getElementById('charSelect');
  const clipSelect = document.getElementById('clipSelect');
  const applyChar = () => {
    const asCow = charSelect.value === 'cow' && !!cow;
    if (cow) cow.root.visible = asCow;
    model.root.visible = !asCow;
    cow64.setActive(charSelect.value === 'cow64');
    document.getElementById('clipRow').hidden = !asCow;
  };
  const cow64 = new LowPolyCow(model, face);
  if (!cow) charSelect.querySelector('option[value=cow]').disabled = true;
  charSelect.addEventListener('change', applyChar);
  clipSelect.addEventListener('change', () => { if (cow) cow.override = clipSelect.value || null; });
  applyChar();
  let names = [];
  try { names = (await import('./mario/anim_ids.js')).ANIM_NAMES || []; } catch { /* names are optional */ }

  animations.forEach((a, i) => {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = `${i.toString(16).toUpperCase().padStart(2, '0')} ${(names[i] || 'anim').replace(/^MARIO_ANIM_/, '')}`;
    ui.select.append(opt);
  });

  const m = {
    marioObj: { header: { gfx: { pos: [0, 0, 0], angle: [0, 0, 0], animInfo: { animID: 0, animFrame: 0, animYTrans: 189 } } } },
    marioBodyState: { action: 0, capState: 0, eyeState: 0, handState: 0, punchState: 0, torsoAngle: [0, 0, 0], headAngle: [0, 0, 0], modelState: 0, wingFlutter: 0 },
    areaUpdateCounter: 0,
  };
  const ai = m.marioObj.header.gfx.animInfo;
  let playing = true;

  function setAnim(id) {
    id = (id + animations.length) % animations.length;
    const a = animations[id];
    ai.animID = id;
    ai.animFrame = a.startFrame;
    ui.select.value = id;
    ui.slider.min = 0;
    ui.slider.max = Math.max(1, a.loopEnd - 1);
    const flags = [];
    if (a.flags & 1) flags.push('no-loop');
    if (a.flags & 2) flags.push('backward');
    ui.info.textContent = `${a.loopEnd} frames · loop from ${a.loopStart}${flags.length ? ' · ' + flags.join(', ') : ''}`;
  }

  ui.select.addEventListener('change', () => setAnim(+ui.select.value));
  document.getElementById('prevAnim').addEventListener('click', () => setAnim(ai.animID - 1));
  document.getElementById('nextAnim').addEventListener('click', () => setAnim(ai.animID + 1));
  ui.play.addEventListener('click', () => { playing = !playing; ui.play.textContent = playing ? 'Pause' : 'Play'; });
  ui.slider.addEventListener('input', () => { ai.animFrame = +ui.slider.value; });
  const syncBody = () => {
    m.marioBodyState.eyeState = +ui.eyes.value;
    m.marioBodyState.handState = +ui.hands.value;
    m.marioBodyState.capState = ui.cap.checked ? 0 : 1;
  };
  [ui.eyes, ui.hands, ui.cap].forEach((el) => el.addEventListener('change', syncBody));
  addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') setAnim(ai.animID + 1);
    if (e.key === 'ArrowLeft') setAnim(ai.animID - 1);
    if (e.key === ' ') ui.play.click();
  });

  const params = new URLSearchParams(location.search);
  setAnim(params.has('anim') ? parseInt(params.get('anim'), 16) : 0xc3);
  document.getElementById('panel').hidden = false;

  let acc = 0, last = performance.now();
  function frame(now) {
    const dt = Math.min(now - last, 100) / 1000;
    acc += dt * 1000;
    last = now;
    while (acc >= 1000 / 30) {
      acc -= 1000 / 30;
      m.areaUpdateCounter++;
      if (playing) {
        const a = animations[ai.animID];
        ai.animFrame++;
        if (ai.animFrame >= a.loopEnd) ai.animFrame = (a.flags & 1) ? a.loopEnd - 1 : a.loopStart;
        ui.slider.value = ai.animFrame;
      }
    }
    if (cow && cow.root.visible) cow.update(m, null, 1, playing ? dt : 0);
    else model.update(m);
    placeCamera();
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  window.__viewer = { model, cow, cow64, animations, m, setAnim };
}

pickRomFile(start);
