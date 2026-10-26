// Keyboard, gamepad and touch input, folded into an N64-style controller state:
// an analog stick in [-80, 80] and the A / B / Z buttons, plus camera controls.

export const BTN_A = 1, BTN_B = 2, BTN_Z = 4, BTN_START = 8;

const KEYMAP = {
  KeyW: 'up', ArrowUp: 'up', KeyS: 'down', ArrowDown: 'down',
  KeyA: 'left', KeyD: 'right',
  ArrowLeft: 'camLeft', ArrowRight: 'camRight', KeyQ: 'camLeft', KeyE: 'camRight',
  KeyR: 'camIn', KeyF: 'camOut',
  Space: 'a', KeyK: 'a', KeyJ: 'b', KeyX: 'b', KeyL: 'z', KeyZ: 'z', ShiftLeft: 'z', ShiftRight: 'z',
  ControlLeft: 'walk', ControlRight: 'walk', KeyC: 'walk',
  Escape: 'start', Enter: 'start', KeyP: 'start',
};

export class Input {
  constructor(canvas) {
    this.keys = new Set();
    this.mouseDelta = { x: 0, y: 0 };
    this.touch = { stick: { x: 0, y: 0 }, buttons: 0 };
    this.lastPad = null;

    addEventListener('keydown', (e) => {
      const k = KEYMAP[e.code];
      if (!k) return;
      if (!e.repeat) this.keys.add(k);
      e.preventDefault();
    });
    addEventListener('keyup', (e) => {
      const k = KEYMAP[e.code];
      if (k) this.keys.delete(k);
    });
    addEventListener('blur', () => this.keys.clear());

    // Drag (mouse or one finger on empty space) rotates the camera
    let drag = null;
    canvas.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'mouse' && e.button !== 0 && e.button !== 2) return;
      drag = { id: e.pointerId, x: e.clientX, y: e.clientY };
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (!drag || drag.id !== e.pointerId) return;
      this.mouseDelta.x += e.clientX - drag.x;
      this.mouseDelta.y += e.clientY - drag.y;
      drag.x = e.clientX;
      drag.y = e.clientY;
    });
    const end = (e) => { if (drag && drag.id === e.pointerId) drag = null; };
    canvas.addEventListener('pointerup', end);
    canvas.addEventListener('pointercancel', end);
    canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    this.wheel = 0;
    canvas.addEventListener('wheel', (e) => { this.wheel += Math.sign(e.deltaY); e.preventDefault(); }, { passive: false });
  }

  /** Attach on-screen controls (shown on touch devices). */
  attachTouch(root) {
    const stick = root.querySelector('.stick');
    const knob = root.querySelector('.knob');
    let id = null, cx = 0, cy = 0;
    const R = 60;
    const move = (e) => {
      let dx = e.clientX - cx, dy = e.clientY - cy;
      const len = Math.hypot(dx, dy);
      if (len > R) { dx *= R / len; dy *= R / len; }
      knob.style.transform = `translate(${dx}px, ${dy}px)`;
      this.touch.stick = { x: (dx / R) * 80, y: (-dy / R) * 80 };
    };
    stick.addEventListener('pointerdown', (e) => {
      id = e.pointerId;
      const r = stick.getBoundingClientRect();
      cx = r.left + r.width / 2;
      cy = r.top + r.height / 2;
      stick.setPointerCapture(id);
      move(e);
      e.stopPropagation();
    });
    stick.addEventListener('pointermove', (e) => { if (e.pointerId === id) move(e); });
    const release = (e) => {
      if (e.pointerId !== id) return;
      id = null;
      knob.style.transform = '';
      this.touch.stick = { x: 0, y: 0 };
    };
    stick.addEventListener('pointerup', release);
    stick.addEventListener('pointercancel', release);

    for (const btn of root.querySelectorAll('.tbtn')) {
      const bit = { a: BTN_A, b: BTN_B, z: BTN_Z }[btn.dataset.btn];
      btn.addEventListener('pointerdown', (e) => { this.touch.buttons |= bit; btn.setPointerCapture(e.pointerId); e.stopPropagation(); });
      const up = () => { this.touch.buttons &= ~bit; };
      btn.addEventListener('pointerup', up);
      btn.addEventListener('pointercancel', up);
    }
  }

  /**
   * Sample the controller. Returns { stickX, stickY, buttons, camX, camY, zoom }.
   */
  poll() {
    let sx = 0, sy = 0, buttons = 0, camX = 0, camY = 0, zoom = 0;
    const k = this.keys;
    if (k.has('left')) sx -= 1;
    if (k.has('right')) sx += 1;
    if (k.has('up')) sy += 1;
    if (k.has('down')) sy -= 1;
    if (sx || sy) {
      const len = Math.hypot(sx, sy);
      const mag = k.has('walk') ? 32 : 80;
      sx = (sx / len) * mag;
      sy = (sy / len) * mag;
    }
    if (k.has('a')) buttons |= BTN_A;
    if (k.has('b')) buttons |= BTN_B;
    if (k.has('z')) buttons |= BTN_Z;
    if (k.has('start')) buttons |= BTN_START;
    if (k.has('camLeft')) camX -= 1;
    if (k.has('camRight')) camX += 1;
    if (k.has('camIn')) zoom -= 1;
    if (k.has('camOut')) zoom += 1;

    // Gamepad (standard mapping)
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (const p of pads) {
      if (!p || !p.connected) continue;
      const dz = (v) => (Math.abs(v) < 0.12 ? 0 : v);
      const lx = dz(p.axes[0] || 0), ly = dz(p.axes[1] || 0);
      if (lx || ly) { sx = lx * 80; sy = -ly * 80; }
      camX += dz(p.axes[2] || 0) * 1.5;
      camY += dz(p.axes[3] || 0) * 1.5;
      const pressed = (i) => p.buttons[i] && p.buttons[i].pressed;
      if (pressed(0)) buttons |= BTN_A;
      if (pressed(1) || pressed(2)) buttons |= BTN_B;
      if (pressed(6) || pressed(7) || pressed(4)) buttons |= BTN_Z;
      if (pressed(9)) buttons |= BTN_START;
      if (pressed(14)) camX -= 1;
      if (pressed(15)) camX += 1;
      if (pressed(12)) zoom -= 1;
      if (pressed(13)) zoom += 1;
      this.lastPad = p.id;
      break;
    }

    if (this.touch.stick.x || this.touch.stick.y) { sx = this.touch.stick.x; sy = this.touch.stick.y; }
    buttons |= this.touch.buttons;

    const md = this.mouseDelta;
    const out = { stickX: Math.round(sx), stickY: Math.round(sy), buttons, camX, camY, zoom, mouseX: md.x, mouseY: md.y, wheel: this.wheel };
    md.x = md.y = 0;
    this.wheel = 0;
    return out;
  }
}
