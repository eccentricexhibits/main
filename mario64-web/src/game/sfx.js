// Sound effects. Coin/star jingles are synthesized; Mario's voice clips are decoded
// from the ROM's sound bank (see ../rom/audio.js).
import { RomVoices } from '../rom/audio.js';

export class Sfx {
  constructor(rom) {
    this.rom = rom;
    this.ctx = null;
    this.muted = false;
    this.buffers = new Map();
    this.voiceSource = null;
    try {
      this.voices = new RomVoices(rom);
    } catch (e) {
      console.warn('Voice clips unavailable', e);
      this.voices = null;
    }
    const unlock = () => {
      this.ensure();
      removeEventListener('keydown', unlock);
      removeEventListener('pointerdown', unlock);
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
    this.master.gain.value = 0.5;
    this.master.connect(this.ctx.destination);
    return this.ctx;
  }

  tone(freq, start, dur, type = 'square', vol = 0.15) {
    const ctx = this.ensure();
    if (!ctx || this.muted) return;
    const t = ctx.currentTime + start;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, t);
    g.gain.setValueAtTime(vol, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.connect(g).connect(this.master);
    o.start(t);
    o.stop(t + dur + 0.02);
  }

  /** Red coin jingle: rises with each coin collected. */
  coin(n) {
    const base = 523.25 * Math.pow(2, (n - 1) / 12 * 2);
    this.tone(base, 0, 0.12);
    this.tone(base * 1.5, 0.08, 0.25);
  }

  star() {
    [523.25, 659.25, 783.99, 1046.5, 783.99, 1046.5].forEach((f, i) => this.tone(f, i * 0.11, 0.3, 'triangle', 0.2));
  }

  /** Called by the physics port with SM64 SOUND_* names. */
  play(name, extra) {
    if (this.muted || !this.ctx) return;
    const variants = this.voices && this.voices.variants(name);
    if (!variants) return;
    const v = extra && Number.isInteger(extra.variant) && variants[extra.variant];
    this.playVoice(v || variants[Math.floor(Math.random() * variants.length)]);
  }

  /** Mario has one voice channel: a new clip cuts off the previous one, like the original. */
  playVoice([bank, slot]) {
    const key = `${bank}:${slot}`;
    let buffer = this.buffers.get(key);
    if (!buffer) {
      const clip = this.voices.decode(bank, slot);
      if (!clip) return;
      buffer = this.ctx.createBuffer(1, clip.pcm.length, clip.rate);
      buffer.copyToChannel(clip.pcm, 0);
      this.buffers.set(key, buffer);
    }
    if (this.voiceSource) {
      try { this.voiceSource.stop(); } catch { /* already finished */ }
    }
    const src = this.ctx.createBufferSource();
    src.buffer = buffer;
    const g = this.ctx.createGain();
    g.gain.value = 0.8;
    src.connect(g).connect(this.master);
    src.start();
    this.voiceSource = src;
  }
}
