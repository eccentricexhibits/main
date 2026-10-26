// Port of geo_update_animation_frame (src/engine/graph_node.c) and the
// frame-advance part of geo_set_animation_globals (src/game/rendering_graph_node.c).

import { s16 } from './math_util.js';

export const ANIM_FLAG_NOLOOP = 1 << 0;
export const ANIM_FLAG_BACKWARD = 1 << 1;
export const ANIM_FLAG_2 = 1 << 2;
export const ANIM_FLAG_HOR_TRANS = 1 << 3;
export const ANIM_FLAG_VERT_TRANS = 1 << 4;
export const ANIM_FLAG_5 = 1 << 5;
export const ANIM_FLAG_6 = 1 << 6;
export const ANIM_FLAG_7 = 1 << 7;

const GET_HIGH_S16_OF_32 = (v) => s16(v >> 16);
const SET_HIGH_S16_OF_32 = (v, x) => ((v & 0xFFFF) | (x << 16)) | 0;

/**
 * Update the animation frame of an object. The animation flags determine
 * whether it plays forwards or backwards, and whether it stops or loops at
 * the end etc.
 *
 * `animInfo` is a struct AnimInfo-like object. Returns
 * { frame, accelAssist } (the C version writes accelAssist through a pointer).
 */
export function geo_update_animation_frame(animInfo, areaUpdateCounter) {
    let result;
    const anim = animInfo.curAnim;

    if (animInfo.animTimer === areaUpdateCounter || (anim.flags & ANIM_FLAG_2)) {
        return { frame: animInfo.animFrame, accelAssist: animInfo.animFrameAccelAssist };
    }

    if (anim.flags & ANIM_FLAG_BACKWARD) {
        if (animInfo.animAccel !== 0) {
            result = (animInfo.animFrameAccelAssist - animInfo.animAccel) | 0;
        } else {
            result = ((animInfo.animFrame - 1) << 16) | 0;
        }

        if (GET_HIGH_S16_OF_32(result) < anim.loopStart) {
            if (anim.flags & ANIM_FLAG_NOLOOP) {
                result = SET_HIGH_S16_OF_32(result, anim.loopStart);
            } else {
                result = SET_HIGH_S16_OF_32(result, anim.loopEnd - 1);
            }
        }
    } else {
        if (animInfo.animAccel !== 0) {
            result = (animInfo.animFrameAccelAssist + animInfo.animAccel) | 0;
        } else {
            result = ((animInfo.animFrame + 1) << 16) | 0;
        }

        if (GET_HIGH_S16_OF_32(result) >= anim.loopEnd) {
            if (anim.flags & ANIM_FLAG_NOLOOP) {
                result = SET_HIGH_S16_OF_32(result, anim.loopEnd - 1);
            } else {
                result = SET_HIGH_S16_OF_32(result, anim.loopStart);
            }
        }
    }

    return { frame: GET_HIGH_S16_OF_32(result), accelAssist: result };
}

/**
 * The animation-frame part of geo_set_animation_globals, which the original runs
 * once per frame while rendering the object (after the object's logic ran).
 */
export function geo_advance_object_animation(animInfo, areaUpdateCounter) {
    if (animInfo.curAnim == null) {
        return;
    }
    const r = geo_update_animation_frame(animInfo, areaUpdateCounter);
    animInfo.animFrame = r.frame;
    animInfo.animFrameAccelAssist = r.accelAssist;
    animInfo.animTimer = areaUpdateCounter & 0xFFFF;
}
