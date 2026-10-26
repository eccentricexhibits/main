// Loads Mario's animation headers from a US SM64 ROM (big-endian .z64).
// The ROM is only read at test time (path from the ROM env var); nothing is copied.

import fs from 'node:fs';

export const MARIO_ANIM_TABLE_ROM_OFFSET = 0x4EC000;

/**
 * Returns an array indexed by MarioAnimID of
 * { flags, animYTransDivisor, startFrame, loopStart, loopEnd, unusedBoneCount, length }.
 */
export function loadMarioAnimHeaders(romPath) {
    const rom = fs.readFileSync(romPath);
    if (rom.readUInt32BE(0) !== 0x80371240) {
        throw new Error('ROM is not a big-endian .z64 image');
    }
    const base = MARIO_ANIM_TABLE_ROM_OFFSET;
    const count = rom.readUInt32BE(base);
    const anims = [];
    for (let i = 0; i < count; i++) {
        const off = rom.readUInt32BE(base + 8 + i * 8);
        const p = base + off;
        anims.push({
            flags: rom.readInt16BE(p + 0),
            animYTransDivisor: rom.readInt16BE(p + 2),
            startFrame: rom.readInt16BE(p + 4),
            loopStart: rom.readInt16BE(p + 6),
            loopEnd: rom.readInt16BE(p + 8),
            unusedBoneCount: rom.readInt16BE(p + 10),
            length: rom.readUInt32BE(p + 20),
        });
    }
    return anims;
}
