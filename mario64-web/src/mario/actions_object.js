// Port of src/game/mario_actions_object.c. Only the attack actions are kept
// (punching / kicking sequence, stomach slide stop); there are no objects to
// pick up, throw, or hit, so attacks only animate (and still bounce off walls
// via check_kick_or_punch_wall).

import * as C from './constants.js';
import * as A from './anim_ids.js';
import {
    play_sound, play_mario_action_sound, set_mario_animation, is_anim_at_end, is_anim_past_end,
    set_mario_action, drop_and_set_mario_action, check_common_action_exits, mario_set_forward_vel,
    mario_check_object_grab, set_water_plunge_action, request_death,
} from './mario.js';
import { stationary_ground_step, perform_ground_step, mario_update_quicksand } from './mario_step.js';

const {
    INPUT_NONZERO_ANALOG, INPUT_A_PRESSED, INPUT_OFF_FLOOR, INPUT_ABOVE_SLIDE, INPUT_A_DOWN,
    INPUT_STOMPED, INPUT_B_PRESSED, INPUT_IN_WATER,
} = C;

/** Used by act_punching() to determine Mario's forward velocity during each animation frame. */
const sPunchingForwardVelocities = [0, 1, 1, 2, 3, 5, 7, 10];

export function animated_stationary_ground_step(m, animation, endAction) {
    stationary_ground_step(m);
    set_mario_animation(m, animation);
    if (is_anim_at_end(m)) {
        set_mario_action(m, endAction, 0);
    }
}

export function mario_update_punch_sequence(m) {
    let endAction, crouchEndAction;
    let animFrame;

    if (m.action & C.ACT_FLAG_MOVING) {
        endAction = C.ACT_WALKING, crouchEndAction = C.ACT_CROUCH_SLIDE;
    } else {
        endAction = C.ACT_IDLE, crouchEndAction = C.ACT_CROUCHING;
    }

    switch (m.actionArg) {
        case 0:
            play_sound(m, 'SOUND_MARIO_PUNCH_YAH');
        // fallthrough
        case 1:
            set_mario_animation(m, A.MARIO_ANIM_FIRST_PUNCH);
            if (is_anim_past_end(m)) {
                m.actionArg = 2;
            } else {
                m.actionArg = 1;
            }

            if (m.marioObj.header.gfx.animInfo.animFrame >= 2) {
                if (mario_check_object_grab(m)) {
                    return true;
                }

                m.flags |= C.MARIO_PUNCHING;
            }

            if (m.actionArg === 2) {
                m.marioBodyState.punchState = (0 << 6) | 4;
            }
            break;

        case 2:
            set_mario_animation(m, A.MARIO_ANIM_FIRST_PUNCH_FAST);

            if (m.marioObj.header.gfx.animInfo.animFrame <= 0) {
                m.flags |= C.MARIO_PUNCHING;
            }

            if (m.input & INPUT_B_PRESSED) {
                m.actionArg = 3;
            }

            if (is_anim_at_end(m)) {
                set_mario_action(m, endAction, 0);
            }
            break;

        case 3:
            play_sound(m, 'SOUND_MARIO_PUNCH_WAH');
        // fallthrough
        case 4:
            set_mario_animation(m, A.MARIO_ANIM_SECOND_PUNCH);
            if (is_anim_past_end(m)) {
                m.actionArg = 5;
            } else {
                m.actionArg = 4;
            }

            if (m.marioObj.header.gfx.animInfo.animFrame > 0) {
                m.flags |= C.MARIO_PUNCHING;
            }

            if (m.actionArg === 5) {
                m.marioBodyState.punchState = (1 << 6) | 4;
            }
            break;

        case 5:
            set_mario_animation(m, A.MARIO_ANIM_SECOND_PUNCH_FAST);
            if (m.marioObj.header.gfx.animInfo.animFrame <= 0) {
                m.flags |= C.MARIO_PUNCHING;
            }

            if (m.input & INPUT_B_PRESSED) {
                m.actionArg = 6;
            }

            if (is_anim_at_end(m)) {
                set_mario_action(m, endAction, 0);
            }
            break;

        case 6:
            play_mario_action_sound(m, 'SOUND_MARIO_PUNCH_HOO', 1);
            animFrame = set_mario_animation(m, A.MARIO_ANIM_GROUND_KICK);
            if (animFrame === 0) {
                m.marioBodyState.punchState = (2 << 6) | 6;
            }

            if (animFrame >= 0 && animFrame < 8) {
                m.flags |= C.MARIO_KICKING;
            }

            if (is_anim_at_end(m)) {
                set_mario_action(m, endAction, 0);
            }
            break;

        case 9:
            play_mario_action_sound(m, 'SOUND_MARIO_PUNCH_HOO', 1);
            set_mario_animation(m, A.MARIO_ANIM_BREAKDANCE);
            animFrame = m.marioObj.header.gfx.animInfo.animFrame;

            if (animFrame >= 2 && animFrame < 8) {
                m.flags |= C.MARIO_TRIPPING;
            }

            if (is_anim_at_end(m)) {
                set_mario_action(m, crouchEndAction, 0);
            }
            break;
    }

    return false;
}

export function act_punching(m) {
    if (m.input & INPUT_STOMPED) {
        return drop_and_set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE)) {
        return check_common_action_exits(m);
    }

    if (m.actionState === 0 && (m.input & INPUT_A_DOWN)) {
        return set_mario_action(m, C.ACT_JUMP_KICK, 0);
    }

    m.actionState = 1;
    if (m.actionArg === 0) {
        m.actionTimer = 7;
    }

    mario_set_forward_vel(m, sPunchingForwardVelocities[m.actionTimer]);
    if (m.actionTimer > 0) {
        m.actionTimer--;
    }

    mario_update_punch_sequence(m);
    perform_ground_step(m);
    return false;
}

export function act_stomach_slide_stop(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    animated_stationary_ground_step(m, A.MARIO_ANIM_SLOW_LAND_FROM_DIVE, C.ACT_IDLE);
    return false;
}

export function check_common_object_cancels(m) {
    const waterSurface = m.waterLevel - 100;
    if (m.pos[1] < waterSurface) {
        return set_water_plunge_action(m);
    }

    if (m.health < 0x100) {
        // return drop_and_set_mario_action(m, ACT_STANDING_DEATH, 0);
        request_death(m, C.ACT_STANDING_DEATH);
    }

    return false;
}

export function mario_execute_object_action(m) {
    let cancel;

    if (check_common_object_cancels(m)) {
        return true;
    }

    if (mario_update_quicksand(m, 0.5)) {
        return true;
    }

    switch (m.action) {
        case C.ACT_PUNCHING:           cancel = act_punching(m);           break;
        case C.ACT_STOMACH_SLIDE_STOP: cancel = act_stomach_slide_stop(m); break;
        default:
            // Not ported (picking up / throwing / Bowser): fall back to idle.
            cancel = set_mario_action(m, C.ACT_IDLE, 0);
            break;
    }

    if (!cancel && (m.input & INPUT_IN_WATER)) {
        m.particleFlags |= C.PARTICLE_IDLE_WATER_WAVE;
    }

    return cancel;
}
