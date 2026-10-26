// MIO0 is Nintendo's LZ-style compression used for most SM64 asset banks.
// Header: "MIO0", u32 decompressed size, u32 offset of compressed (back-reference) data,
// u32 offset of uncompressed (literal) data. Layout bits start at 0x10, MSB first:
// 1 = copy one literal byte, 0 = copy a back-reference (u16: 4-bit length-3, 12-bit distance-1).

export function mio0Decompress(src) {
  const view = new DataView(src.buffer, src.byteOffset, src.byteLength);
  if (view.getUint32(0) !== 0x4d494f30) throw new Error('Not MIO0 data');
  const size = view.getUint32(4);
  let compPos = view.getUint32(8);
  let rawPos = view.getUint32(12);
  let layoutPos = 0x10;
  const out = new Uint8Array(size);
  let outPos = 0;
  let bits = 0;
  let bitCount = 0;

  while (outPos < size) {
    if (bitCount === 0) {
      bits = view.getUint32(layoutPos);
      layoutPos += 4;
      bitCount = 32;
    }
    if (bits & 0x80000000) {
      out[outPos++] = src[rawPos++];
    } else {
      const v = view.getUint16(compPos);
      compPos += 2;
      const length = (v >> 12) + 3;
      let from = outPos - ((v & 0xfff) + 1);
      for (let i = 0; i < length && outPos < size; i++) out[outPos++] = out[from++];
    }
    bits <<= 1;
    bitCount--;
  }
  return out;
}
