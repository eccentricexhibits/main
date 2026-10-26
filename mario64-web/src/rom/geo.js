// Parser for SM64 geo layout scripts (the scene-graph bytecode that describes how a
// model's display lists are arranged into a hierarchy of bones, switches and scales).
// Mirrors src/engine/geo_layout.c from the decompilation.

const s16 = (v) => (v << 16) >> 16;
const degToAngle = (deg) => s16(Math.trunc((deg << 15) / 180));

function rd16(data, off) {
  return s16((data[off] << 8) | data[off + 1]);
}
function rd32(data, off) {
  return ((data[off] << 24) | (data[off + 1] << 16) | (data[off + 2] << 8) | data[off + 3]) >>> 0;
}

/**
 * Parse the geo layout at a segmented address into a plain node tree.
 * Every node: { type, children: [], ... }.
 */
export function parseGeoLayout(rom, startAddr) {
  const root = { type: 'root', children: [] };
  const parents = [root];
  const callStack = [];
  let last = root;
  let pos = startAddr >>> 0;

  const add = (node) => {
    node.children = [];
    parents[parents.length - 1].children.push(node);
    last = node;
    return node;
  };

  for (let guard = 0; guard < 100000; guard++) {
    const [data, off] = rom.resolve(pos);
    const cmd = data[off];
    const b1 = data[off + 1];
    switch (cmd) {
      case 0x00: // branch and link
        callStack.push(pos + 8);
        pos = rd32(data, off + 4);
        continue;
      case 0x01: // end
        return root;
      case 0x02: // branch (type 1 = call, 0 = jump)
        if (b1 === 1) callStack.push(pos + 8);
        pos = rd32(data, off + 4);
        continue;
      case 0x03: // return
        if (!callStack.length) return root;
        pos = callStack.pop();
        continue;
      case 0x04:
        parents.push(last);
        pos += 4;
        continue;
      case 0x05:
        parents.pop();
        pos += 4;
        continue;
      case 0x06: case 0x07: case 0x09: case 0x0c: case 0x17: case 0x1b: case 0x20:
        if (cmd === 0x0c) add({ type: 'zbuffer', enable: b1 });
        pos += 4;
        continue;
      case 0x08:
        add({ type: 'screenArea' });
        pos += 12;
        continue;
      case 0x0a:
        add({ type: 'frustum' });
        pos += b1 ? 12 : 8;
        continue;
      case 0x0b:
        add({ type: 'start' });
        pos += 4;
        continue;
      case 0x0d:
        add({ type: 'renderRange', min: rd16(data, off + 4), max: rd16(data, off + 6) });
        pos += 8;
        continue;
      case 0x0e:
        add({ type: 'switch', param: rd16(data, off + 2), fn: rd32(data, off + 4), selected: 0 });
        pos += 8;
        continue;
      case 0x0f:
        add({ type: 'camera' });
        pos += 20;
        continue;
      case 0x10: { // translate/rotate family
        const layer = b1 & 0x0f;
        const kind = (b1 & 0x70) >> 4;
        const hasDl = (b1 & 0x80) !== 0;
        let translation = [0, 0, 0];
        let rotation = [0, 0, 0];
        let size;
        if (kind === 0) {
          translation = [rd16(data, off + 4), rd16(data, off + 6), rd16(data, off + 8)];
          rotation = [rd16(data, off + 10), rd16(data, off + 12), rd16(data, off + 14)].map(degToAngle);
          size = 16;
        } else if (kind === 1) {
          translation = [rd16(data, off + 2), rd16(data, off + 4), rd16(data, off + 6)];
          size = 8;
        } else if (kind === 2) {
          rotation = [rd16(data, off + 2), rd16(data, off + 4), rd16(data, off + 6)].map(degToAngle);
          size = 8;
        } else {
          rotation = [0, degToAngle(rd16(data, off + 2)), 0];
          size = 4;
        }
        const dl = hasDl ? rd32(data, off + size) : 0;
        add({ type: 'translateRotate', layer, translation, rotation, dl, active: true });
        pos += size + (hasDl ? 4 : 0);
        continue;
      }
      case 0x11: case 0x12: case 0x14: { // translation / rotation / billboard nodes
        const hasDl = (b1 & 0x80) !== 0;
        const v = [rd16(data, off + 2), rd16(data, off + 4), rd16(data, off + 6)];
        const node = { layer: b1 & 0x0f, dl: hasDl ? rd32(data, off + 8) : 0 };
        if (cmd === 0x11) Object.assign(node, { type: 'translation', translation: v });
        else if (cmd === 0x12) Object.assign(node, { type: 'rotation', rotation: v.map(degToAngle) });
        else Object.assign(node, { type: 'billboard', translation: v });
        add(node);
        pos += hasDl ? 12 : 8;
        continue;
      }
      case 0x13:
        add({
          type: 'animatedPart',
          layer: b1,
          translation: [rd16(data, off + 2), rd16(data, off + 4), rd16(data, off + 6)],
          dl: rd32(data, off + 8),
        });
        pos += 12;
        continue;
      case 0x15:
        add({ type: 'displayList', layer: b1, dl: rd32(data, off + 4) });
        pos += 8;
        continue;
      case 0x16:
        add({ type: 'shadow', shadowType: rd16(data, off + 2), solidity: rd16(data, off + 4), scale: rd16(data, off + 6) });
        pos += 8;
        continue;
      case 0x18:
        add({ type: 'asm', param: rd16(data, off + 2), fn: rd32(data, off + 4) });
        pos += 8;
        continue;
      case 0x19:
        add({ type: 'background' });
        pos += 8;
        continue;
      case 0x1a: case 0x1e:
        pos += 8;
        continue;
      case 0x1f:
        pos += 16;
        continue;
      case 0x1c:
        add({ type: 'heldObject', param: b1, translation: [rd16(data, off + 2), rd16(data, off + 4), rd16(data, off + 6)], fn: rd32(data, off + 8) });
        pos += 12;
        continue;
      case 0x1d: {
        const hasDl = (b1 & 0x80) !== 0;
        add({ type: 'scale', layer: b1 & 0x0f, scale: rd32(data, off + 4) / 65536, dl: hasDl ? rd32(data, off + 8) : 0 });
        pos += hasDl ? 12 : 8;
        continue;
      }
      default:
        throw new Error(`Unknown geo command 0x${cmd.toString(16)} at 0x${pos.toString(16)}`);
    }
  }
  throw new Error('Geo layout did not terminate');
}
