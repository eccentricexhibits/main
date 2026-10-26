// Reads Mario's animation bank from the ROM.
// The bank is a DMA table: u32 count, u32 (unused) srcAddr, then count x {u32 offset, u32 size}.
// Each entry starts with a struct Animation header whose `values`/`index` pointers
// are offsets relative to the entry itself.

export function parseMarioAnimations(rom, base = rom.layout.marioAnims) {
  const v = rom.view;
  const count = v.getUint32(base);
  const anims = [];
  for (let i = 0; i < count; i++) {
    const entryOff = base + v.getUint32(base + 8 + i * 8);
    const size = v.getUint32(base + 12 + i * 8);
    const valuesOff = v.getUint32(entryOff + 0x0c);
    const indexOff = v.getUint32(entryOff + 0x10);
    // The index table holds (numParts + 1) * 3 (count, offset) pairs; its length is
    // implied by the layout: values follow the index in every entry of this bank.
    const indexLen = (Math.min(valuesOff, size) - indexOff) >> 1;
    const valuesLen = (size - valuesOff) >> 1;
    const index = new Uint16Array(indexLen);
    for (let j = 0; j < indexLen; j++) index[j] = v.getUint16(entryOff + indexOff + j * 2);
    const values = new Int16Array(valuesLen);
    for (let j = 0; j < valuesLen; j++) values[j] = v.getInt16(entryOff + valuesOff + j * 2);
    anims.push({
      id: i,
      flags: v.getInt16(entryOff),
      animYTransDivisor: v.getInt16(entryOff + 2),
      startFrame: v.getInt16(entryOff + 4),
      loopStart: v.getInt16(entryOff + 6),
      loopEnd: v.getInt16(entryOff + 8),
      unusedBoneCount: v.getInt16(entryOff + 10),
      index,
      values,
    });
  }
  return anims;
}

/** retrieve_animation_index() from the decomp: index pairs are (frameCount, offset). */
export function animValue(anim, frame, attr) {
  const count = anim.index[attr];
  const offset = anim.index[attr + 1];
  const f = frame < count ? frame : count - 1;
  return anim.values[offset + f];
}
