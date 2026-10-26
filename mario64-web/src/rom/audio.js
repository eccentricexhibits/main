// Decodes Mario's voice clips from the ROM's sound banks.
// sound_data.ctl holds instrument definitions (pointing at samples + ADPCM codebooks),
// sound_data.tbl holds the VADPCM-compressed sample data. Formats follow
// tools/disassemble_sound.py and tools/aifc_decode.c from the decompilation.

const US_CTL = 0x57b720;
const US_TBL = 0x593560;

// SOUND_* name -> list of [bank, instrument slot] (one picked at random).
// Bank 0x08 = sfx_mario, bank 0x0A = sfx_mario_peach.
const VOICE_MAP = {
  SOUND_MARIO_YAH_WAH_HOO: [[8, 0], [8, 1], [8, 2]],
  SOUND_MARIO_HOOHOO: [[10, 1]],
  SOUND_MARIO_YAHOO: [[8, 4]],
  SOUND_MARIO_YAHOO_WAHA_YIPPEE: [[8, 4], [8, 24], [8, 25]],
  SOUND_MARIO_UH: [[8, 5]],
  SOUND_MARIO_HRMM: [[8, 6]],
  SOUND_MARIO_WAH2: [[8, 7]],
  SOUND_MARIO_WHOA: [[8, 8]],
  SOUND_MARIO_EEUH: [[8, 9]],
  SOUND_MARIO_ATTACKED: [[8, 10]],
  SOUND_MARIO_OOOF: [[8, 11]],
  SOUND_MARIO_OOOF2: [[8, 11]],
  SOUND_MARIO_HERE_WE_GO: [[8, 12]],
  SOUND_MARIO_YAWNING: [[8, 13]],
  SOUND_MARIO_SNORING1: [[8, 14]],
  SOUND_MARIO_SNORING2: [[8, 15]],
  SOUND_MARIO_SNORING3: [[8, 21]],
  SOUND_MARIO_DOH: [[8, 16]],
  SOUND_MARIO_HAHA: [[8, 3]],
  SOUND_MARIO_HAHA_2: [[8, 3]],
  SOUND_MARIO_TWIRL_BOUNCE: [[8, 20]],
  SOUND_MARIO_IMA_TIRED: [[8, 23]],
  SOUND_MARIO_WAAAOOOW: [[10, 0]],
  SOUND_MARIO_PANTING: [[10, 2]],
  SOUND_MARIO_PANTING_COLD: [[10, 2]],
  SOUND_MARIO_DYING: [[10, 4]],
  SOUND_MARIO_ON_FIRE: [[10, 5]],
  SOUND_MARIO_UH2: [[10, 6]],
  SOUND_MARIO_UH2_2: [[10, 6]],
  SOUND_MARIO_COUGHING1: [[10, 7]],
  SOUND_MARIO_COUGHING2: [[10, 7]],
  SOUND_MARIO_COUGHING3: [[10, 7]],
  SOUND_MARIO_PUNCH_YAH: [[10, 9]],
  SOUND_MARIO_PUNCH_HOO: [[10, 10]],
  SOUND_MARIO_PUNCH_WAH: [[8, 1]],
  SOUND_MARIO_GROUND_POUND_WAH: [[8, 7]],
  SOUND_MARIO_MAMA_MIA: [[10, 11]],
  SOUND_MARIO_OKEY_DOKEY: [[10, 12]],
  SOUND_MARIO_LETS_A_GO: [[8, 26]],
  SOUND_MARIO_HELLO: [[8, 18]],
  SOUND_MARIO_ITS_A_ME: [[10, 8]],
};

function seqFile(view, base) {
  const count = view.getUint16(base + 2);
  const entries = [];
  for (let i = 0; i < count; i++) {
    entries.push({ offset: base + view.getUint32(base + 4 + i * 8), length: view.getUint32(base + 8 + i * 8) });
  }
  return entries;
}

/** Expand a VADPCM codebook into the per-output-sample coefficient vectors (aifc_decode.c readcodebook). */
function expandBook(book, order, npredictors) {
  const table = [];
  for (let p = 0; p < npredictors; p++) {
    const t = Array.from({ length: 8 }, () => new Int32Array(order + 8));
    for (let j = 0; j < order; j++) {
      for (let k = 0; k < 8; k++) t[k][j] = book[p * order * 8 + j * 8 + k];
    }
    for (let k = 1; k < 8; k++) t[k][order] = t[k - 1][order - 1];
    t[0][order] = 2048;
    for (let k = 1; k < 8; k++) {
      let j = 0;
      for (; j < k; j++) t[j][k + order] = 0;
      for (; j < 8; j++) t[j][k + order] = t[j - k][order];
    }
    table.push(t);
  }
  return table;
}

function decodeVadpcm(bytes, table, order) {
  const frames = Math.floor(bytes.length / 9);
  const out = new Float32Array(frames * 16);
  const state = new Int32Array(16);
  const ix = new Int32Array(16);
  const inVec = new Int32Array(order + 8);
  for (let f = 0; f < frames; f++) {
    const p = f * 9;
    const scale = 1 << (bytes[p] >> 4);
    const coefs = table[bytes[p] & 0xf] || table[0];
    for (let i = 0; i < 16; i += 2) {
      const c = bytes[p + 1 + (i >> 1)];
      const hi = c >> 4, lo = c & 0xf;
      ix[i] = (hi <= 7 ? hi : hi - 16) * scale;
      ix[i + 1] = (lo <= 7 ? lo : lo - 16) * scale;
    }
    for (let j = 0; j < 2; j++) {
      for (let i = 0; i < 8; i++) inVec[i + order] = ix[j * 8 + i];
      for (let i = 0; i < order; i++) inVec[i] = j === 0 ? state[16 - order + i] : state[8 - order + i];
      for (let i = 0; i < 8; i++) {
        let acc = 0;
        const v = coefs[i];
        for (let k = 0; k < order + 8; k++) acc += v[k] * inVec[k];
        let s = Math.floor(acc / 2048);
        s = s > 32767 ? 32767 : s < -32768 ? -32768 : s;
        state[j * 8 + i] = s;
      }
    }
    for (let i = 0; i < 16; i++) out[f * 16 + i] = state[i] / 32768;
  }
  return out;
}

export class RomVoices {
  constructor(rom) {
    this.rom = rom;
    this.cache = new Map();
    const v = rom.view;
    this.ctl = seqFile(v, US_CTL);
    this.tbl = seqFile(v, US_TBL);
  }

  /** Decode one instrument's sample -> { pcm: Float32Array, rate } */
  decode(bank, slot) {
    const key = `${bank}:${slot}`;
    if (this.cache.has(key)) return this.cache.get(key);
    const v = this.rom.view;
    const entry = this.ctl[bank];
    const data = entry.offset + 16; // skip the 16-byte bank header
    const instAddr = v.getUint32(data + 4 + slot * 4);
    if (!instAddr) return null;
    const inst = data + instAddr;
    const sampleAddr = v.getUint32(inst + 16); // sound_med.sample_addr
    const tuning = v.getFloat32(inst + 20);
    const s = data + sampleAddr;
    const addr = v.getUint32(s + 4);
    const bookAddr = v.getUint32(s + 12);
    let size = v.getUint32(s + 16);
    if (size % 9) size -= size % 9;
    const order = v.getInt32(data + bookAddr);
    const npred = v.getInt32(data + bookAddr + 4);
    const book = new Int16Array(16 * order * npred);
    for (let i = 0; i < book.length; i++) book[i] = v.getInt16(data + bookAddr + 8 + i * 2);
    const bytes = this.rom.bytes.subarray(this.tbl[bank].offset + addr, this.tbl[bank].offset + addr + size);
    const result = { pcm: decodeVadpcm(bytes, expandBook(book, order, npred), order), rate: Math.round(32000 * tuning) };
    this.cache.set(key, result);
    return result;
  }

  variants(name) {
    return VOICE_MAP[name] || null;
  }
}
