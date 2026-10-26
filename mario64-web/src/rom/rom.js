// Loads a user-supplied Super Mario 64 (US) ROM and exposes the pieces of it we use.
// Nothing from the ROM is bundled with this project; everything is read at runtime
// from the file the player selects, inside their own browser.

import { mio0Decompress } from './mio0.js';

export const SM64_US_SHA1 = '9bef1128717f958171a4afac3ed78ee2bb4e86ce';

// ROM locations for the US release (from the level script that loads group0).
const US_LAYOUT = {
  group0Mio0: [0x114750, 0x1279b0], // segment 0x04: Mario's display lists, vertices, textures
  group0Geo: [0x1279b0, 0x12a7e0], // segment 0x17: Mario's geo layout
  common1Mio0: [0x201410, 0x218da0], // segment 0x03: coins, stars and other common objects
  common1Geo: [0x218da0, 0x219e00], // segment 0x16: their geo layouts
  marioGeo: 0x17002dd4,
  starGeo: 0x16000ea0,
  redCoinGeo: 0x160002c4,
  marioAnims: 0x4ec000,
};

/**
 * N64 ROM dumps come in three byte orders. Normalize to big-endian (.z64).
 */
export function normalizeByteOrder(bytes) {
  const b0 = bytes[0], b1 = bytes[1], b2 = bytes[2], b3 = bytes[3];
  if (b0 === 0x80 && b1 === 0x37 && b2 === 0x12 && b3 === 0x40) return bytes; // .z64
  const out = new Uint8Array(bytes.length);
  if (b0 === 0x37 && b1 === 0x80 && b2 === 0x40 && b3 === 0x12) { // .v64 (16-bit swapped)
    for (let i = 0; i < bytes.length; i += 2) {
      out[i] = bytes[i + 1];
      out[i + 1] = bytes[i];
    }
    return out;
  }
  if (b0 === 0x40 && b1 === 0x12 && b2 === 0x37 && b3 === 0x80) { // .n64 (32-bit little-endian)
    for (let i = 0; i < bytes.length; i += 4) {
      out[i] = bytes[i + 3];
      out[i + 1] = bytes[i + 2];
      out[i + 2] = bytes[i + 1];
      out[i + 3] = bytes[i];
    }
    return out;
  }
  throw new Error('This does not look like an N64 ROM.');
}

async function sha1Hex(bytes) {
  const subtle = globalThis.crypto && globalThis.crypto.subtle;
  if (!subtle) return null; // non-secure context; skip verification
  const digest = await subtle.digest('SHA-1', bytes);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, '0')).join('');
}

export class Rom {
  constructor(bytes) {
    this.bytes = bytes;
    this.view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    this.layout = US_LAYOUT;
    this.segments = new Map();
  }

  slice(start, end) {
    return this.bytes.subarray(start, end);
  }

  setSegment(seg, data) {
    this.segments.set(seg, data);
  }

  /** Resolve a segmented address (0xSSOOOOOO) to [Uint8Array, offset]. */
  resolve(addr) {
    const seg = (addr >>> 24) & 0xff;
    const data = this.segments.get(seg);
    if (!data) throw new Error(`Segment 0x${seg.toString(16)} not loaded (address 0x${(addr >>> 0).toString(16)})`);
    return [data, addr & 0xffffff];
  }

  loadSegments() {
    const L = this.layout;
    this.setSegment(0x04, mio0Decompress(this.slice(...L.group0Mio0)));
    this.setSegment(0x17, this.slice(...L.group0Geo));
    this.setSegment(0x03, mio0Decompress(this.slice(...L.common1Mio0)));
    this.setSegment(0x16, this.slice(...L.common1Geo));
  }
}

/**
 * @param {ArrayBuffer|Uint8Array} input
 * @returns {Promise<Rom>}
 */
export async function loadRom(input) {
  const raw = input instanceof Uint8Array ? input : new Uint8Array(input);
  if (raw.length < 0x800000) throw new Error('File is too small to be a Super Mario 64 ROM.');
  const bytes = normalizeByteOrder(raw);
  const name = new TextDecoder('ascii').decode(bytes.subarray(0x20, 0x34)).trim();
  if (!/SUPER MARIO 64/i.test(name)) {
    throw new Error(`This ROM's internal name is "${name}", not SUPER MARIO 64.`);
  }
  const hash = await sha1Hex(bytes);
  if (hash && hash !== SM64_US_SHA1) {
    const region = String.fromCharCode(bytes[0x3e]);
    throw new Error(
      `Unsupported ROM version (region "${region}", SHA-1 ${hash}). ` +
        'Only the unmodified US release (SHA-1 9bef1128…ce) is supported.');
  }
  const rom = new Rom(bytes);
  rom.loadSegments();
  return rom;
}
