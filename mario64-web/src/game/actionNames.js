// Readable names for Mario's action ids (for the HUD / debugging).
import * as C from '../mario/constants.js';

const NAMES = new Map();
for (const [k, v] of Object.entries(C)) {
  if (k.startsWith('ACT_') && !k.startsWith('ACT_FLAG_') && !k.startsWith('ACT_GROUP_') && !k.endsWith('_MASK') && typeof v === 'number' && !NAMES.has(v >>> 0)) {
    NAMES.set(v >>> 0, k.slice(4).toLowerCase().replace(/_/g, ' '));
  }
}

export function actionName(action) {
  return NAMES.get(action >>> 0) || `0x${(action >>> 0).toString(16)}`;
}
