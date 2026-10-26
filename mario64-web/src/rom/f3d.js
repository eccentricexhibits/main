// A small interpreter for the Fast3D (F3D) display-list microcode SM64 uses.
// It does not rasterize anything: it walks display lists, tracks the RSP/RDP state
// that matters for a model (vertex buffer, lights, combiner, texture tiles, geometry
// mode) and emits triangle batches grouped by material, ready to upload to WebGL.

export const G_LIGHTING = 0x00020000;
export const G_TEXTURE_GEN = 0x00040000;
export const G_CULL_FRONT = 0x00001000;
export const G_CULL_BACK = 0x00002000;

export function createF3DState() {
  return {
    vtx: new Array(16).fill(null),
    geometryMode: G_LIGHTING | G_CULL_BACK,
    combine: [0, 0],
    numLights: 1,
    lights: [
      { color: [255, 255, 255], dir: [0x28, 0x28, 0x28] },
      { color: [127, 127, 127], dir: [0, 0, 0] },
      { color: [0, 0, 0], dir: [0, 0, 0] },
    ],
    texImage: { addr: 0, fmt: 0, siz: 2, width: 1 },
    tiles: Array.from({ length: 8 }, () => ({
      fmt: 0, siz: 2, line: 0, tmem: 0, cms: 0, cmt: 0, masks: 0, maskt: 0, shifts: 0, shiftt: 0,
      uls: 0, ult: 0, lrs: 0, lrt: 0,
    })),
    tmemLoads: new Map(), // tmem address -> { addr, siz }
    texture: { on: false, s: 0xffff, t: 0xffff, tile: 0 },
    envColor: [255, 255, 255, 255],
    primColor: [255, 255, 255, 255],
    otherModeL: 0,
  };
}

export function cloneF3DState(s) {
  return {
    ...s,
    vtx: s.vtx.slice(),
    combine: s.combine.slice(),
    lights: s.lights.map((l) => ({ color: l.color.slice(), dir: l.dir.slice() })),
    texImage: { ...s.texImage },
    tiles: s.tiles.map((t) => ({ ...t })),
    tmemLoads: new Map(s.tmemLoads),
    texture: { ...s.texture },
    envColor: s.envColor.slice(),
    primColor: s.primColor.slice(),
  };
}

function rd32(d, o) {
  return ((d[o] << 24) | (d[o + 1] << 16) | (d[o + 2] << 8) | d[o + 3]) >>> 0;
}
const s16 = (d, o) => (((d[o] << 8) | d[o + 1]) << 16) >> 16;
const s8 = (v) => (v << 24) >> 24;

// ---------------------------------------------------------------------------
// Texture decoding (N64 texel formats -> RGBA8)

function decodeTexture(rom, addr, fmt, siz, width, height) {
  const [data, off] = rom.resolve(addr);
  const out = new Uint8Array(width * height * 4);
  const n = width * height;
  for (let i = 0; i < n; i++) {
    let r, g, b, a;
    if (siz === 2) { // 16-bit
      const v = (data[off + i * 2] << 8) | data[off + i * 2 + 1];
      if (fmt === 0) { // RGBA5551
        r = ((v >> 11) & 0x1f) * 255 / 31;
        g = ((v >> 6) & 0x1f) * 255 / 31;
        b = ((v >> 1) & 0x1f) * 255 / 31;
        a = (v & 1) ? 255 : 0;
      } else { // IA88
        r = g = b = v >> 8;
        a = v & 0xff;
      }
    } else if (siz === 3) { // RGBA32
      r = data[off + i * 4]; g = data[off + i * 4 + 1]; b = data[off + i * 4 + 2]; a = data[off + i * 4 + 3];
    } else if (siz === 1) { // 8-bit
      const v = data[off + i];
      if (fmt === 3) { // IA44
        r = g = b = (v >> 4) * 17;
        a = (v & 0xf) * 17;
      } else { // I8
        r = g = b = a = v;
      }
    } else { // 4-bit
      const byte = data[off + (i >> 1)];
      const v = (i & 1) ? byte & 0xf : byte >> 4;
      if (fmt === 3) { // IA31
        r = g = b = ((v >> 1) * 255) / 7;
        a = (v & 1) ? 255 : 0;
      } else { // I4
        r = g = b = a = v * 17;
      }
    }
    out[i * 4] = r; out[i * 4 + 1] = g; out[i * 4 + 2] = b; out[i * 4 + 3] = a;
  }
  return out;
}

// ---------------------------------------------------------------------------

/**
 * Collects triangles into per-material batches.
 */
export class BatchSink {
  constructor(rom) {
    this.rom = rom;
    this.batches = new Map();
    this.textures = new Map(); // key -> { width, height, rgba, cms, cmt }
  }

  materialFor(state) {
    const lighting = (state.geometryMode & G_LIGHTING) !== 0;
    let tex = null;
    if (state.texture.on) {
      const tile = state.tiles[state.texture.tile];
      const load = state.tmemLoads.get(tile.tmem);
      if (load) {
        const width = tile.masks ? 1 << tile.masks : ((tile.lrs - tile.uls) >> 2) + 1;
        const height = tile.maskt ? 1 << tile.maskt : ((tile.lrt - tile.ult) >> 2) + 1;
        const key = `${load.addr.toString(16)}:${tile.fmt}:${tile.siz}:${width}x${height}:${tile.cms}:${tile.cmt}`;
        if (!this.textures.has(key)) {
          this.textures.set(key, {
            key, width, height, cms: tile.cms, cmt: tile.cmt, addr: load.addr,
            rgba: decodeTexture(this.rom, load.addr, tile.fmt, tile.siz, width, height),
          });
        }
        tex = {
          key, width, height, uls: tile.uls / 4, ult: tile.ult / 4,
          scaleS: state.texture.s / 65536, scaleT: state.texture.t / 65536,
          // G_TEXTURE_GEN maps the normal's [-1, 1] range onto texScale/64 texels
          genScale: [state.texture.s / 64 / width, state.texture.t / 64 / height],
        };
      }
    }
    const amb = state.lights[state.numLights].color;
    const diff = state.lights[0];
    const material = {
      combine: state.combine.slice(),
      lighting,
      texgen: (state.geometryMode & G_TEXTURE_GEN) !== 0,
      cullBack: (state.geometryMode & G_CULL_BACK) !== 0,
      ambient: amb.slice(),
      diffuse: diff.color.slice(),
      lightDir: diff.dir.slice(),
      envColor: state.envColor.slice(),
      primColor: state.primColor.slice(),
      texKey: tex ? tex.key : null,
      texGenScale: tex ? tex.genScale : [1, 1],
    };
    const key = JSON.stringify(material);
    return { key, material, tex };
  }

  addTriangle(state, i0, i1, i2) {
    const { key, material, tex } = this.materialFor(state);
    let batch = this.batches.get(key);
    if (!batch) {
      batch = { material, positions: [], normals: [], colors: [], uvs: [] };
      this.batches.set(key, batch);
    }
    for (const i of [i0, i1, i2]) {
      const v = state.vtx[i];
      if (!v) throw new Error(`Triangle references unloaded vertex ${i}`);
      batch.positions.push(v.x, v.y, v.z);
      if (material.lighting) {
        batch.normals.push(s8(v.r) / 127, s8(v.g) / 127, s8(v.b) / 127);
        batch.colors.push(1, 1, 1, v.a / 255);
      } else {
        batch.normals.push(0, 1, 0);
        batch.colors.push(v.r / 255, v.g / 255, v.b / 255, v.a / 255);
      }
      if (tex) {
        // S/T are S10.5 texel coordinates; +0.5 maps N64 texel centres onto GL ones.
        const s = (v.s * tex.scaleS) / 32 - tex.uls;
        const t = (v.t * tex.scaleT) / 32 - tex.ult;
        batch.uvs.push((s + 0.5) / tex.width, (t + 0.5) / tex.height);
      } else {
        batch.uvs.push(0, 0);
      }
    }
  }

  takeBatches() {
    const list = [...this.batches.values()];
    this.batches = new Map();
    return list;
  }
}

/**
 * Execute a display list at a segmented address, mutating `state` and pushing
 * triangles into `sink`.
 */
export function runDisplayList(rom, addr, state, sink, depth = 0) {
  if (depth > 16) throw new Error('Display list nesting too deep');
  let pos = addr >>> 0;
  for (let guard = 0; guard < 200000; guard++) {
    const [d, o] = rom.resolve(pos);
    const w0 = rd32(d, o);
    const w1 = rd32(d, o + 4);
    const cmd = w0 >>> 24;
    pos += 8;
    switch (cmd) {
      case 0x04: { // G_VTX
        const b1 = (w0 >>> 16) & 0xff;
        const n = (b1 >> 4) + 1;
        const v0 = b1 & 0xf;
        const [vd, vo] = rom.resolve(w1);
        for (let i = 0; i < n; i++) {
          const p = vo + i * 16;
          state.vtx[v0 + i] = {
            x: s16(vd, p), y: s16(vd, p + 2), z: s16(vd, p + 4),
            s: s16(vd, p + 8), t: s16(vd, p + 10),
            r: vd[p + 12], g: vd[p + 13], b: vd[p + 14], a: vd[p + 15],
          };
        }
        break;
      }
      case 0xbf: // G_TRI1
        sink.addTriangle(state, ((w1 >>> 16) & 0xff) / 10, ((w1 >>> 8) & 0xff) / 10, (w1 & 0xff) / 10);
        break;
      case 0x06: // G_DL
        if (((w0 >>> 16) & 0xff) === 1) { pos = w1; break; } // branch, no return
        runDisplayList(rom, w1, state, sink, depth + 1);
        break;
      case 0xb8: // G_ENDDL
        return;
      case 0x03: { // G_MOVEMEM
        const index = (w0 >>> 16) & 0xff;
        if (index >= 0x86 && index <= 0x94) { // G_MV_L0..L7
          const li = (index - 0x86) >> 1;
          const [ld, lo] = rom.resolve(w1);
          const light = state.lights[li] || (state.lights[li] = { color: [0, 0, 0], dir: [0, 0, 0] });
          light.color = [ld[lo], ld[lo + 1], ld[lo + 2]];
          light.dir = [s8(ld[lo + 8]), s8(ld[lo + 9]), s8(ld[lo + 10])];
        }
        break;
      }
      case 0xbc: { // G_MOVEWORD
        const index = w0 & 0xff;
        if (index === 0x02) state.numLights = Math.max(1, ((w1 & 0x7fffffff) >> 5) - 1); // G_MW_NUMLIGHT
        break;
      }
      case 0xb7: state.geometryMode |= w1; break; // G_SETGEOMETRYMODE
      case 0xb6: state.geometryMode &= ~w1; break; // G_CLEARGEOMETRYMODE
      case 0xbb: // G_TEXTURE
        state.texture = { on: (w0 & 0xff) !== 0, tile: (w0 >>> 8) & 7, s: w1 >>> 16, t: w1 & 0xffff };
        break;
      case 0xfc: state.combine = [w0 & 0xffffff, w1]; break; // G_SETCOMBINE
      case 0xfd: // G_SETTIMG
        state.texImage = { fmt: (w0 >>> 21) & 7, siz: (w0 >>> 19) & 3, width: (w0 & 0xfff) + 1, addr: w1 };
        break;
      case 0xf5: { // G_SETTILE
        const t = state.tiles[(w1 >>> 24) & 7];
        Object.assign(t, {
          fmt: (w0 >>> 21) & 7, siz: (w0 >>> 19) & 3, line: (w0 >>> 9) & 0x1ff, tmem: w0 & 0x1ff,
          cmt: (w1 >>> 18) & 3, maskt: (w1 >>> 14) & 0xf, shiftt: (w1 >>> 10) & 0xf,
          cms: (w1 >>> 8) & 3, masks: (w1 >>> 4) & 0xf, shifts: w1 & 0xf,
        });
        break;
      }
      case 0xf2: { // G_SETTILESIZE
        const t = state.tiles[(w1 >>> 24) & 7];
        t.uls = (w0 >>> 12) & 0xfff; t.ult = w0 & 0xfff;
        t.lrs = (w1 >>> 12) & 0xfff; t.lrt = w1 & 0xfff;
        break;
      }
      case 0xf3: // G_LOADBLOCK
      case 0xf4: { // G_LOADTILE
        const t = state.tiles[(w1 >>> 24) & 7];
        state.tmemLoads.set(t.tmem, { addr: state.texImage.addr, siz: state.texImage.siz });
        break;
      }
      case 0xfb: state.envColor = [w1 >>> 24, (w1 >>> 16) & 0xff, (w1 >>> 8) & 0xff, w1 & 0xff]; break;
      case 0xfa: state.primColor = [w1 >>> 24, (w1 >>> 16) & 0xff, (w1 >>> 8) & 0xff, w1 & 0xff]; break;
      case 0xb9: state.otherModeL = w1; break;
      default:
        break; // syncs, othermode H, matrices etc. are irrelevant for model extraction
    }
  }
  throw new Error('Display list did not terminate');
}
