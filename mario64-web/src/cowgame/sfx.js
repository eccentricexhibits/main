// Synthesized sounds for the cow game: heavy thuds, creaks, crashes, grumbles and
// a lot of phones ringing. No samples, so nothing to ship.

export class CowSfx {
  constructor() {
    this.ctx = null;
    const unlock = () => {
      this.ensure();
      if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume();
    };
    addEventListener('keydown', unlock);
    addEventListener('pointerdown', unlock);
  }

  ensure() {
    if (this.ctx) return this.ctx;
    const Ctx = globalThis.AudioContext || globalThis.webkitAudioContext;
    if (!Ctx) return null;
    this.ctx = new Ctx();
    this.master = this.ctx.createGain();
    this.master.gain.value = 0.55;
    this.master.connect(this.ctx.destination);
    const len = this.ctx.sampleRate;
    this.noiseBuf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
    const d = this.noiseBuf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    return this.ctx;
  }

  get ready() {
    return this.ctx && this.ctx.state === 'running';
  }

  env(node, t, attack, dur, peak) {
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(peak, t + attack);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    node.connect(g).connect(this.master);
    return g;
  }

  osc(type, f0, f1, dur, peak = 0.3, delay = 0) {
    if (!this.ready) return;
    const t = this.ctx.currentTime + delay;
    const o = this.ctx.createOscillator();
    o.type = type;
    o.frequency.setValueAtTime(f0, t);
    o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
    this.env(o, t, 0.005, dur, peak);
    o.start(t);
    o.stop(t + dur + 0.05);
  }

  noise(dur, freq, peak = 0.3, q = 1, type = 'lowpass', delay = 0, f1 = null) {
    if (!this.ready) return;
    const t = this.ctx.currentTime + delay;
    const src = this.ctx.createBufferSource();
    src.buffer = this.noiseBuf;
    const f = this.ctx.createBiquadFilter();
    f.type = type;
    f.frequency.setValueAtTime(freq, t);
    if (f1) f.frequency.exponentialRampToValueAtTime(f1, t + dur);
    f.Q.value = q;
    src.connect(f);
    this.env(f, t, 0.004, dur, peak);
    src.start(t, Math.random() * 0.5);
    src.stop(t + dur + 0.05);
  }

  step(weight = 1) { this.osc('sine', 110, 50, 0.12, 0.18 * weight); this.noise(0.07, 400, 0.05 * weight); }
  thud(impact) {
    const k = Math.min(1, impact / 2500);
    this.osc('sine', 120, 35, 0.25 + k * 0.3, 0.3 + k * 0.4);
    this.noise(0.2 + k * 0.3, 300, 0.15 + k * 0.3);
  }
  stomp() { this.osc('sine', 90, 25, 0.7, 0.9); this.noise(0.6, 600, 0.6, 1, 'lowpass', 0, 80); }
  grunt() { // a weary "hmph"
    this.osc('sawtooth', 150, 95, 0.22, 0.08);
    this.noise(0.18, 700, 0.06, 4, 'bandpass');
  }
  sigh() { this.noise(0.9, 900, 0.12, 2, 'bandpass', 0, 300); }
  sob() { for (let i = 0; i < 4; i++) this.osc('triangle', 420 - i * 15, 300, 0.25, 0.07, i * 0.35); }
  skid() { this.noise(0.45, 2500, 0.12, 1, 'bandpass', 0, 600); }
  creak() { this.osc('sawtooth', 70, 110, 0.35, 0.06); }
  crack() { this.noise(0.25, 3000, 0.35, 1, 'highpass'); this.osc('square', 200, 60, 0.15, 0.1); }
  smash() { this.noise(0.5, 1800, 0.45, 0.7, 'bandpass', 0, 300); this.osc('sine', 100, 40, 0.3, 0.3); }
  splash() { this.noise(0.7, 1200, 0.4, 0.8, 'lowpass', 0, 300); }
  boing(big) { this.osc('sine', big ? 180 : 240, big ? 900 : 600, big ? 0.5 : 0.3, 0.3); }
  clunk() { this.osc('square', 140, 70, 0.12, 0.2); this.noise(0.1, 800, 0.2); }
  rumble() { this.noise(1.5, 200, 0.4, 1); this.osc('sine', 50, 40, 1.5, 0.25); }
  ring(vol) { this.osc('square', 1320, 1320, 0.05, 0.04 * vol); this.osc('square', 1660, 1660, 0.05, 0.03 * vol, 0.03); }
  silence() { this.osc('square', 300, 80, 0.12, 0.15); this.osc('triangle', 660, 660, 0.12, 0.12, 0.12); this.osc('triangle', 990, 990, 0.2, 0.12, 0.22); }
  checkpoint() { [523, 659, 784].forEach((f, i) => this.osc('triangle', f, f, 0.18, 0.12, i * 0.08)); }
  finish() { [392, 330, 262, 196].forEach((f, i) => this.osc('triangle', f, f * 0.98, 0.5, 0.15, i * 0.35)); }
}
