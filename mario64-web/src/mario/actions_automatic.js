// Port of src/game/mario_actions_automatic.c: ledge grab / climb and ceiling
// hanging. Poles, cannon, grabbed and tornado actions are omitted.

import { s16, sins, coss, approach_s32, vec3f_copy, vec3s_set } from '../engine/math_util.js';
import * as S from '../engine/surface_terrains.js';
import * as C from './constants.js';
import * as A from './anim_ids.js';
import {
    F32, play_sound, play_sound_if_no_flag, play_mario_landing_sound,
    set_mario_animation, is_anim_at_end, is_anim_past_end, set_mario_action, check_common_action_exits,
    find_floor_height_relative_polar, resolve_and_return_wall_collisions, vec3f_find_ceil, set_water_plunge_action,
} from './mario.js';
import { stop_and_set_height_to_floor } from './mario_step.js';

const {
    INPUT_NONZERO_ANALOG, INPUT_A_PRESSED, INPUT_OFF_FLOOR, INPUT_ABOVE_SLIDE, INPUT_UNKNOWN_5,
    INPUT_A_DOWN, INPUT_STOMPED, INPUT_Z_PRESSED,
} = C;

const HANG_NONE = 0;
const HANG_HIT_CEIL_OR_OOB = 1;
const HANG_LEFT_CEIL = 2;

export function perform_hanging_step(m, nextPos) {
    m.wall = resolve_and_return_wall_collisions(m, nextPos, 50.0, 50.0);
    const f = m.world.find_floor(nextPos[0], nextPos[1], nextPos[2]);
    const floorHeight = f.height;
    const floor = f.surface;
    const c = vec3f_find_ceil(m, nextPos, floorHeight);
    const ceilHeight = c.height;
    const ceil = c.surface;

    if (floor === null) {
        return HANG_HIT_CEIL_OR_OOB;
    }
    if (ceil === null) {
        return HANG_LEFT_CEIL;
    }
    if (ceilHeight - floorHeight <= 160.0) {
        return HANG_HIT_CEIL_OR_OOB;
    }
    if (ceil.type !== S.SURFACE_HANGABLE) {
        return HANG_LEFT_CEIL;
    }

    const ceilOffset = ceilHeight - (nextPos[1] + 160.0);
    if (ceilOffset < -30.0) {
        return HANG_HIT_CEIL_OR_OOB;
    }
    if (ceilOffset > 30.0) {
        return HANG_LEFT_CEIL;
    }

    nextPos[1] = m.ceilHeight - 160.0;
    vec3f_copy(m.pos, nextPos);

    m.floor = floor;
    m.floorHeight = floorHeight;
    m.ceil = ceil;
    m.ceilHeight = ceilHeight;

    return HANG_NONE;
}

export function update_hang_moving(m) {
    const nextPos = [0, 0, 0];
    const maxSpeed = 4.0;

    m.forwardVel += 1.0;
    if (m.forwardVel > maxSpeed) {
        m.forwardVel = maxSpeed;
    }

    m.faceAngle[1] = s16(m.intendedYaw - approach_s32(s16(m.intendedYaw - m.faceAngle[1]), 0, 0x800, 0x800));

    m.slideYaw = m.faceAngle[1];
    m.slideVelX = m.forwardVel * sins(m.faceAngle[1]);
    m.slideVelZ = m.forwardVel * coss(m.faceAngle[1]);

    m.vel[0] = m.slideVelX;
    m.vel[1] = 0.0;
    m.vel[2] = m.slideVelZ;

    nextPos[0] = m.pos[0] - m.ceil.normal.y * m.vel[0];
    nextPos[2] = m.pos[2] - m.ceil.normal.y * m.vel[2];
    nextPos[1] = m.pos[1];

    const stepResult = perform_hanging_step(m, nextPos);

    vec3f_copy(m.marioObj.header.gfx.pos, m.pos);
    vec3s_set(m.marioObj.header.gfx.angle, 0, m.faceAngle[1], 0);
    return stepResult;
}

export function update_hang_stationary(m) {
    m.forwardVel = 0.0;
    m.slideVelX = 0.0;
    m.slideVelZ = 0.0;

    m.pos[1] = m.ceilHeight - 160.0;
    m.vel[0] = 0.0;
    m.vel[1] = 0.0;
    m.vel[2] = 0.0;
    vec3f_copy(m.marioObj.header.gfx.pos, m.pos);
}

export function act_start_hanging(m) {
    m.actionTimer++;

    if ((m.input & INPUT_NONZERO_ANALOG) && m.actionTimer >= 31) {
        return set_mario_action(m, C.ACT_HANGING, 0);
    }

    if (!(m.input & INPUT_A_DOWN)) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    //! Crash if Mario's referenced ceiling is NULL (same for other hanging actions)
    if (m.ceil === null || m.ceil.type !== S.SURFACE_HANGABLE) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    set_mario_animation(m, A.MARIO_ANIM_HANG_ON_CEILING);
    play_sound_if_no_flag(m, 'SOUND_ACTION_HANGING_STEP', C.MARIO_ACTION_SOUND_PLAYED);
    update_hang_stationary(m);

    if (is_anim_at_end(m)) {
        set_mario_action(m, C.ACT_HANGING, 0);
    }

    return false;
}

export function act_hanging(m) {
    if (m.input & INPUT_NONZERO_ANALOG) {
        return set_mario_action(m, C.ACT_HANG_MOVING, m.actionArg);
    }

    if (!(m.input & INPUT_A_DOWN)) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    if (m.ceil === null || m.ceil.type !== S.SURFACE_HANGABLE) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.actionArg & 1) {
        set_mario_animation(m, A.MARIO_ANIM_HANDSTAND_LEFT);
    } else {
        set_mario_animation(m, A.MARIO_ANIM_HANDSTAND_RIGHT);
    }

    update_hang_stationary(m);

    return false;
}

export function act_hang_moving(m) {
    if (!(m.input & INPUT_A_DOWN)) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    if (m.ceil === null || m.ceil.type !== S.SURFACE_HANGABLE) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.actionArg & 1) {
        set_mario_animation(m, A.MARIO_ANIM_MOVE_ON_WIRE_NET_RIGHT);
    } else {
        set_mario_animation(m, A.MARIO_ANIM_MOVE_ON_WIRE_NET_LEFT);
    }

    if (m.marioObj.header.gfx.animInfo.animFrame === 12) {
        play_sound(m, 'SOUND_ACTION_HANGING_STEP');
    }

    if (is_anim_past_end(m)) {
        m.actionArg ^= 1;
        if (m.input & INPUT_UNKNOWN_5) {
            return set_mario_action(m, C.ACT_HANGING, m.actionArg);
        }
    }

    if (update_hang_moving(m) === HANG_LEFT_CEIL) {
        set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    return false;
}

export function let_go_of_ledge(m) {
    m.vel[1] = 0.0;
    m.forwardVel = -8.0;
    m.pos[0] -= 60.0 * sins(m.faceAngle[1]);
    m.pos[2] -= 60.0 * coss(m.faceAngle[1]);

    const floorHeight = m.world.find_floor(m.pos[0], m.pos[1], m.pos[2]).height;
    if (floorHeight < m.pos[1] - 100.0) {
        m.pos[1] -= 100.0;
    } else {
        m.pos[1] = floorHeight;
    }

    return set_mario_action(m, C.ACT_SOFT_BONK, 0);
}

export function climb_up_ledge(m) {
    set_mario_animation(m, A.MARIO_ANIM_IDLE_HEAD_LEFT);
    m.pos[0] += 14.0 * sins(m.faceAngle[1]);
    m.pos[2] += 14.0 * coss(m.faceAngle[1]);
    vec3f_copy(m.marioObj.header.gfx.pos, m.pos);
}

export function update_ledge_climb_camera(m) {
    let sp4;

    if (m.actionTimer < 14) {
        sp4 = m.actionTimer;
    } else {
        sp4 = 14.0;
    }
    m.statusForCamera.pos[0] = m.pos[0] + sp4 * sins(m.faceAngle[1]);
    m.statusForCamera.pos[2] = m.pos[2] + sp4 * coss(m.faceAngle[1]);
    m.statusForCamera.pos[1] = m.pos[1];
    m.actionTimer++;
    m.flags |= C.MARIO_UNKNOWN_25;
}

export function update_ledge_climb(m, animation, endAction) {
    stop_and_set_height_to_floor(m);

    set_mario_animation(m, animation);
    if (is_anim_at_end(m)) {
        set_mario_action(m, endAction, 0);
        if (endAction === C.ACT_IDLE) {
            climb_up_ledge(m);
        }
    }
}

export function act_ledge_grab(m) {
    const intendedDYaw = s16(m.intendedYaw - m.faceAngle[1]);
    const hasSpaceForMario = (m.ceilHeight - m.floorHeight >= 160.0);

    if (m.actionTimer < 10) {
        m.actionTimer++;
    }

    if (m.floor.normal.y < F32(0.9063078)) {
        return let_go_of_ledge(m);
    }

    if (m.input & (INPUT_Z_PRESSED | INPUT_OFF_FLOOR)) {
        return let_go_of_ledge(m);
    }

    if ((m.input & INPUT_A_PRESSED) && hasSpaceForMario) {
        return set_mario_action(m, C.ACT_LEDGE_CLIMB_FAST, 0);
    }

    if (m.input & INPUT_STOMPED) {
        return let_go_of_ledge(m);
    }
    if (m.actionTimer === 10 && (m.input & INPUT_NONZERO_ANALOG)) {
        if (intendedDYaw >= -0x4000 && intendedDYaw <= 0x4000) {
            if (hasSpaceForMario) {
                return set_mario_action(m, C.ACT_LEDGE_CLIMB_SLOW_1, 0);
            }
        } else {
            return let_go_of_ledge(m);
        }
    }

    const heightAboveFloor = m.pos[1] - find_floor_height_relative_polar(m, -0x8000, 30.0);
    if (hasSpaceForMario && heightAboveFloor < 100.0) {
        return set_mario_action(m, C.ACT_LEDGE_CLIMB_FAST, 0);
    }

    if (m.actionArg === 0) {
        play_sound_if_no_flag(m, 'SOUND_MARIO_WHOA', C.MARIO_MARIO_SOUND_PLAYED);
    }

    stop_and_set_height_to_floor(m);
    set_mario_animation(m, A.MARIO_ANIM_IDLE_ON_LEDGE);

    return false;
}

export function act_ledge_climb_slow(m) {
    if (m.input & INPUT_OFF_FLOOR) {
        return let_go_of_ledge(m);
    }

    if (m.actionTimer >= 28
        && (m.input & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE))) {
        climb_up_ledge(m);
        return check_common_action_exits(m);
    }

    if (m.actionTimer === 10) {
        play_sound_if_no_flag(m, 'SOUND_MARIO_EEUH', C.MARIO_MARIO_SOUND_PLAYED);
    }

    update_ledge_climb(m, A.MARIO_ANIM_SLOW_LEDGE_GRAB, C.ACT_IDLE);

    update_ledge_climb_camera(m);
    if (m.marioObj.header.gfx.animInfo.animFrame === 17) {
        m.action = C.ACT_LEDGE_CLIMB_SLOW_2;
    }

    return false;
}

export function act_ledge_climb_down(m) {
    if (m.input & INPUT_OFF_FLOOR) {
        return let_go_of_ledge(m);
    }

    play_sound_if_no_flag(m, 'SOUND_MARIO_WHOA', C.MARIO_MARIO_SOUND_PLAYED);

    update_ledge_climb(m, A.MARIO_ANIM_CLIMB_DOWN_LEDGE, C.ACT_LEDGE_GRAB);
    m.actionArg = 1;

    return false;
}

export function act_ledge_climb_fast(m) {
    if (m.input & INPUT_OFF_FLOOR) {
        return let_go_of_ledge(m);
    }

    play_sound_if_no_flag(m, 'SOUND_MARIO_UH2', C.MARIO_MARIO_SOUND_PLAYED);

    update_ledge_climb(m, A.MARIO_ANIM_FAST_LEDGE_GRAB, C.ACT_IDLE);

    if (m.marioObj.header.gfx.animInfo.animFrame === 8) {
        play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
    }
    update_ledge_climb_camera(m);

    return false;
}

export function check_common_automatic_cancels(m) {
    if (m.pos[1] < m.waterLevel - 100) {
        return set_water_plunge_action(m);
    }

    return false;
}

export function mario_execute_automatic_action(m) {
    let cancel;

    if (check_common_automatic_cancels(m)) {
        return true;
    }

    m.quicksandDepth = 0.0;

    switch (m.action) {
        case C.ACT_START_HANGING:      cancel = act_start_hanging(m);    break;
        case C.ACT_HANGING:            cancel = act_hanging(m);          break;
        case C.ACT_HANG_MOVING:        cancel = act_hang_moving(m);      break;
        case C.ACT_LEDGE_GRAB:         cancel = act_ledge_grab(m);       break;
        case C.ACT_LEDGE_CLIMB_SLOW_1: cancel = act_ledge_climb_slow(m); break;
        case C.ACT_LEDGE_CLIMB_SLOW_2: cancel = act_ledge_climb_slow(m); break;
        case C.ACT_LEDGE_CLIMB_DOWN:   cancel = act_ledge_climb_down(m); break;
        case C.ACT_LEDGE_CLIMB_FAST:   cancel = act_ledge_climb_fast(m); break;
        default:
            // Not ported (poles, cannon, grabbed, tornado): fall back to freefall.
            cancel = set_mario_action(m, C.ACT_FREEFALL, 0);
            break;
    }

    return cancel;
}
