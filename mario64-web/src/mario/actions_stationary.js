// Port of src/game/mario_actions_stationary.c (object-holding actions omitted).

import { s16, sins } from '../engine/math_util.js';
import * as S from '../engine/surface_terrains.js';
import * as C from './constants.js';
import * as A from './anim_ids.js';
import {
    F32, play_sound, play_sound_if_no_flag, play_mario_landing_sound, play_mario_heavy_landing_sound,
    set_mario_animation, is_anim_at_end, is_anim_past_end, set_mario_action, drop_and_set_mario_action,
    set_jumping_action, set_jump_from_landing, check_common_action_exits, mario_set_forward_vel,
    find_floor_height_relative_polar, mario_drop_held_object, set_water_plunge_action,
    update_mario_sound_and_camera, request_death,
} from './mario.js';
import { mario_push_off_steep_floor, mario_update_quicksand, stationary_ground_step } from './mario_step.js';

const {
    INPUT_NONZERO_ANALOG, INPUT_A_PRESSED, INPUT_OFF_FLOOR, INPUT_ABOVE_SLIDE, INPUT_FIRST_PERSON,
    INPUT_SQUISHED, INPUT_IN_POISON_GAS, INPUT_IN_WATER, INPUT_STOMPED, INPUT_B_PRESSED, INPUT_Z_DOWN,
    INPUT_Z_PRESSED,
} = C;

export function check_common_idle_cancels(m) {
    mario_drop_held_object(m);
    if (m.floor.normal.y < F32(0.29237169)) {
        return mario_push_off_steep_floor(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_JUMP, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    if (m.input & INPUT_FIRST_PERSON) {
        return set_mario_action(m, C.ACT_FIRST_PERSON, 0);
    }

    if (m.input & INPUT_NONZERO_ANALOG) {
        m.faceAngle[1] = s16(m.intendedYaw);
        return set_mario_action(m, C.ACT_WALKING, 0);
    }

    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_PUNCHING, 0);
    }

    if (m.input & INPUT_Z_DOWN) {
        return set_mario_action(m, C.ACT_START_CROUCHING, 0);
    }

    return false;
}

export function act_idle(m) {
    if (m.quicksandDepth > 30.0) {
        return set_mario_action(m, C.ACT_IN_QUICKSAND, 0);
    }

    if (m.input & INPUT_IN_POISON_GAS) {
        return set_mario_action(m, C.ACT_COUGHING, 0);
    }

    if (!(m.actionArg & 1) && m.health < 0x300) {
        return set_mario_action(m, C.ACT_PANTING, 0);
    }

    if (check_common_idle_cancels(m)) {
        return true;
    }

    if (m.actionState === 3) {
        if ((m.area.terrainType & S.TERRAIN_MASK) === S.TERRAIN_SNOW) {
            return set_mario_action(m, C.ACT_SHIVERING, 0);
        } else {
            return set_mario_action(m, C.ACT_START_SLEEPING, 0);
        }
    }

    if (m.actionArg & 1) {
        set_mario_animation(m, A.MARIO_ANIM_STAND_AGAINST_WALL);
    } else {
        switch (m.actionState) {
            case 0:
                set_mario_animation(m, A.MARIO_ANIM_IDLE_HEAD_LEFT);
                break;

            case 1:
                set_mario_animation(m, A.MARIO_ANIM_IDLE_HEAD_RIGHT);
                break;

            case 2:
                set_mario_animation(m, A.MARIO_ANIM_IDLE_HEAD_CENTER);
                break;
        }

        if (is_anim_at_end(m)) {
            // Fall asleep after 10 head turning cycles.
            if (++m.actionState === 3) {
                const deltaYOfFloorBehindMario = m.pos[1] - find_floor_height_relative_polar(m, -0x8000, 60.0);
                if (deltaYOfFloorBehindMario < -24.0 || 24.0 < deltaYOfFloorBehindMario
                    || (m.floor.flags & S.SURFACE_FLAG_DYNAMIC)) {
                    m.actionState = 0;
                } else {
                    // If Mario hasn't turned his head 10 times yet, stay idle instead of going to sleep.
                    m.actionTimer++;
                    if (m.actionTimer < 10) {
                        m.actionState = 0;
                    }
                }
            }
        }
    }

    stationary_ground_step(m);

    return false;
}

export function play_anim_sound(m, actionState, animFrame, sound, extra) {
    if (m.actionState === actionState && m.marioObj.header.gfx.animInfo.animFrame === animFrame) {
        play_sound(m, sound, extra);
    }
}

export function act_start_sleeping(m) {
    let animFrame;

    if (check_common_idle_cancels(m)) {
        return true;
    }

    if (m.quicksandDepth > 30.0) {
        return set_mario_action(m, C.ACT_IN_QUICKSAND, 0);
    }

    if (m.actionState === 4) {
        return set_mario_action(m, C.ACT_SLEEPING, 0);
    }

    switch (m.actionState) {
        case 0:
            animFrame = set_mario_animation(m, A.MARIO_ANIM_START_SLEEP_IDLE);
            break;

        case 1:
            animFrame = set_mario_animation(m, A.MARIO_ANIM_START_SLEEP_SCRATCH);
            break;

        case 2:
            animFrame = set_mario_animation(m, A.MARIO_ANIM_START_SLEEP_YAWN);
            m.marioBodyState.eyeState = C.MARIO_EYES_HALF_CLOSED;
            break;

        case 3:
            animFrame = set_mario_animation(m, A.MARIO_ANIM_START_SLEEP_SITTING);
            m.marioBodyState.eyeState = C.MARIO_EYES_HALF_CLOSED;
            break;
    }

    play_anim_sound(m, 1, 41, 'SOUND_ACTION_PAT_BACK');
    play_anim_sound(m, 1, 49, 'SOUND_ACTION_PAT_BACK');
    play_anim_sound(m, 3, 15, 'SOUND_ACTION_TERRAIN_BODY_HIT_GROUND', { terrain: m.terrainSoundAddend >>> 16 });

    if (is_anim_at_end(m)) {
        m.actionState++;
    }

    if (m.actionState === 2 && animFrame === -1) {
        play_sound(m, 'SOUND_MARIO_YAWNING');
    }

    if (m.actionState === 1 && animFrame === -1) {
        play_sound(m, 'SOUND_MARIO_IMA_TIRED');
    }

    stationary_ground_step(m);
    return false;
}

export function act_sleeping(m) {
    let animFrame;
    if (m.input
        & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE
            | INPUT_FIRST_PERSON | INPUT_STOMPED | INPUT_B_PRESSED | INPUT_Z_PRESSED)) {
        return set_mario_action(m, C.ACT_WAKING_UP, m.actionState);
    }

    if (m.quicksandDepth > 30.0) {
        return set_mario_action(m, C.ACT_WAKING_UP, m.actionState);
    }

    if (m.pos[1] - find_floor_height_relative_polar(m, -0x8000, 60.0) > 24.0) {
        return set_mario_action(m, C.ACT_WAKING_UP, m.actionState);
    }

    m.marioBodyState.eyeState = C.MARIO_EYES_CLOSED;
    stationary_ground_step(m);
    switch (m.actionState) {
        case 0:
            animFrame = set_mario_animation(m, A.MARIO_ANIM_SLEEP_IDLE);

            if (animFrame === 2) {
                play_sound(m, 'SOUND_MARIO_SNORING1');
            }

            if (animFrame === 20) {
                play_sound(m, 'SOUND_MARIO_SNORING2');
            }

            if (is_anim_at_end(m)) {
                m.actionTimer++;
                if (m.actionTimer > 45) {
                    m.actionState++;
                }
            }
            break;

        case 1:
            if (set_mario_animation(m, A.MARIO_ANIM_SLEEP_START_LYING) === 18) {
                play_mario_heavy_landing_sound(m, 'SOUND_ACTION_TERRAIN_BODY_HIT_GROUND');
            }

            if (is_anim_at_end(m)) {
                m.actionState++;
            }
            break;

        case 2:
            animFrame = set_mario_animation(m, A.MARIO_ANIM_SLEEP_LYING);
            play_sound_if_no_flag(m, 'SOUND_MARIO_SNORING3', C.MARIO_ACTION_SOUND_PLAYED);
            break;
    }
    return false;
}

export function act_waking_up(m) {
    if (!m.actionTimer) {
        // stop_sound(...) is forwarded to the sound hook with { stop: true }
        play_sound(m, 'SOUND_MARIO_SNORING1', { stop: true });
        play_sound(m, 'SOUND_MARIO_SNORING2', { stop: true });
        play_sound(m, 'SOUND_MARIO_SNORING3', { stop: true });
    }

    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    m.actionTimer++;

    if (m.actionTimer > 20) {
        return set_mario_action(m, C.ACT_IDLE, 0);
    }

    stationary_ground_step(m);

    set_mario_animation(m, !m.actionArg ? A.MARIO_ANIM_WAKE_FROM_SLEEP : A.MARIO_ANIM_WAKE_FROM_LYING);

    return false;
}

export function act_shivering(m) {
    let animFrame;

    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    if (m.input
        & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE
            | INPUT_FIRST_PERSON | INPUT_STOMPED | INPUT_B_PRESSED | INPUT_Z_PRESSED)) {
        m.actionState = 2;
    }

    stationary_ground_step(m);
    switch (m.actionState) {
        case 0:
            animFrame = set_mario_animation(m, A.MARIO_ANIM_SHIVERING_WARMING_HAND);
            if (animFrame === 49) {
                m.particleFlags |= C.PARTICLE_BREATH;
                play_sound(m, 'SOUND_MARIO_PANTING_COLD');
            }
            if (animFrame === 7 || animFrame === 81) {
                play_sound(m, 'SOUND_ACTION_CLAP_HANDS_COLD');
            }
            if (is_anim_past_end(m)) {
                m.actionState = 1;
            }
            break;

        case 1:
            animFrame = set_mario_animation(m, A.MARIO_ANIM_SHIVERING);
            if (animFrame === 9 || animFrame === 25 || animFrame === 44) {
                play_sound(m, 'SOUND_ACTION_CLAP_HANDS_COLD');
            }
            break;

        case 2:
            set_mario_animation(m, A.MARIO_ANIM_SHIVERING_RETURN_TO_IDLE);
            if (is_anim_past_end(m)) {
                set_mario_action(m, C.ACT_IDLE, 0);
            }
            break;
    }
    return false;
}

export function act_coughing(m) {
    if (check_common_idle_cancels(m)) {
        return true;
    }

    stationary_ground_step(m);
    const animFrame = set_mario_animation(m, A.MARIO_ANIM_COUGHING);
    if (animFrame === 25 || animFrame === 35) {
        play_sound(m, 'SOUND_MARIO_COUGHING3');
    }

    if (animFrame === 50 || animFrame === 58) {
        play_sound(m, 'SOUND_MARIO_COUGHING2');
    }

    if (animFrame === 71 || animFrame === 80) {
        play_sound(m, 'SOUND_MARIO_COUGHING1');
    }

    return false;
}

export function act_standing_against_wall(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE)) {
        return check_common_action_exits(m);
    }

    if (m.input & INPUT_FIRST_PERSON) {
        return set_mario_action(m, C.ACT_FIRST_PERSON, 0);
    }

    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_PUNCHING, 0);
    }

    set_mario_animation(m, A.MARIO_ANIM_STAND_AGAINST_WALL);
    stationary_ground_step(m);
    return false;
}

export function act_in_quicksand(m) {
    if (m.quicksandDepth < 30.0) {
        return set_mario_action(m, C.ACT_IDLE, 0);
    }

    if (check_common_idle_cancels(m)) {
        return true;
    }

    if (m.quicksandDepth > 70.0) {
        set_mario_animation(m, A.MARIO_ANIM_DYING_IN_QUICKSAND);
    } else {
        set_mario_animation(m, A.MARIO_ANIM_IDLE_IN_QUICKSAND);
    }

    stationary_ground_step(m);
    return false;
}

export function act_crouching(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_BACKFLIP, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    if (m.input & INPUT_FIRST_PERSON) {
        return set_mario_action(m, C.ACT_STOP_CROUCHING, 0);
    }

    if (!(m.input & INPUT_Z_DOWN)) {
        return set_mario_action(m, C.ACT_STOP_CROUCHING, 0);
    }

    if (m.input & INPUT_NONZERO_ANALOG) {
        return set_mario_action(m, C.ACT_START_CRAWLING, 0);
    }

    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_PUNCHING, 9);
    }

    stationary_ground_step(m);
    set_mario_animation(m, A.MARIO_ANIM_CROUCHING);
    return false;
}

export function act_panting(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.health >= 0x500) {
        return set_mario_action(m, C.ACT_IDLE, 0);
    }

    if (check_common_idle_cancels(m)) {
        return true;
    }

    if (set_mario_animation(m, A.MARIO_ANIM_WALK_PANTING) === 1) {
        play_sound(m, 'SOUND_MARIO_PANTING', { variant: (m.globalTimer % 3) });
    }

    stationary_ground_step(m);
    m.marioBodyState.eyeState = C.MARIO_EYES_HALF_CLOSED;
    return false;
}

export function stopping_step(m, animID, action) {
    stationary_ground_step(m);
    set_mario_animation(m, animID);
    if (is_anim_at_end(m)) {
        set_mario_action(m, action, 0);
    }
}

export function act_braking_stop(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_PUNCHING, 0);
    }

    if (!(m.input & INPUT_FIRST_PERSON)
        && (m.input & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE))) {
        return check_common_action_exits(m);
    }

    stopping_step(m, A.MARIO_ANIM_STOP_SKID, C.ACT_IDLE);
    return false;
}

export function act_butt_slide_stop(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE)) {
        return check_common_action_exits(m);
    }

    stopping_step(m, A.MARIO_ANIM_STOP_SLIDE, C.ACT_IDLE);
    if (m.marioObj.header.gfx.animInfo.animFrame === 6) {
        play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
    }

    return false;
}

export function act_slide_kick_slide_stop(m) {
    if (m.input & INPUT_STOMPED) {
        return drop_and_set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return drop_and_set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    stopping_step(m, A.MARIO_ANIM_CROUCH_FROM_SLIDE_KICK, C.ACT_CROUCHING);
    return false;
}

export function act_start_crouching(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_BACKFLIP, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    stationary_ground_step(m);
    set_mario_animation(m, A.MARIO_ANIM_START_CROUCHING);
    if (is_anim_past_end(m)) {
        set_mario_action(m, C.ACT_CROUCHING, 0);
    }
    return false;
}

export function act_stop_crouching(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_BACKFLIP, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    stationary_ground_step(m);
    set_mario_animation(m, A.MARIO_ANIM_STOP_CROUCHING);
    if (is_anim_past_end(m)) {
        set_mario_action(m, C.ACT_IDLE, 0);
    }
    return false;
}

export function act_start_crawling(m) {
    if (m.input & INPUT_FIRST_PERSON) {
        return set_mario_action(m, C.ACT_STOP_CROUCHING, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    stationary_ground_step(m);
    set_mario_animation(m, A.MARIO_ANIM_START_CRAWLING);
    if (is_anim_past_end(m)) {
        set_mario_action(m, C.ACT_CRAWLING, 0);
    }

    return false;
}

export function act_stop_crawling(m) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    stationary_ground_step(m);
    set_mario_animation(m, A.MARIO_ANIM_STOP_CRAWLING);
    if (is_anim_past_end(m)) {
        set_mario_action(m, C.ACT_CROUCHING, 0);
    }
    return false;
}

export function act_shockwave_bounce(m) {
    // (INT_STATUS_MARIO_SHOCKWAVE / KNOCKBACK_DMG come from objects.)
    if (++m.actionTimer === 48) {
        return set_mario_action(m, C.ACT_IDLE, 0);
    }

    const sp1E = s16((m.actionTimer % 16) << 12);
    const sp18 = (((6 - ((m.actionTimer / 8) | 0)) * 8.0) + 4.0);
    mario_set_forward_vel(m, 0);
    m.vel[0] = 0.0;
    m.vel[1] = 0.0;
    m.vel[2] = 0.0;
    if (sins(sp1E) >= 0.0) {
        m.pos[1] = sins(sp1E) * sp18 + m.floorHeight;
    } else {
        m.pos[1] = m.floorHeight - sins(sp1E) * sp18;
    }

    const gfx = m.marioObj.header.gfx;
    gfx.pos[0] = m.pos[0];
    gfx.pos[1] = m.pos[1];
    gfx.pos[2] = m.pos[2];
    gfx.angle[0] = 0;
    gfx.angle[1] = m.faceAngle[1];
    gfx.angle[2] = 0;
    set_mario_animation(m, A.MARIO_ANIM_A_POSE);
    return false;
}

export function landing_step(m, arg1, action) {
    stationary_ground_step(m);
    set_mario_animation(m, arg1);
    if (is_anim_at_end(m)) {
        return set_mario_action(m, action, 0);
    }
    return false;
}

export function check_common_landing_cancels(m, action) {
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_FIRST_PERSON) {
        return set_mario_action(m, C.ACT_IDLE, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        if (!action) {
            return set_jump_from_landing(m);
        } else {
            return set_jumping_action(m, action, 0);
        }
    }

    if (m.input & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE)) {
        return check_common_action_exits(m);
    }

    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_PUNCHING, 0);
    }

    return false;
}

export function act_jump_land_stop(m) {
    if (check_common_landing_cancels(m, 0)) {
        return true;
    }

    landing_step(m, A.MARIO_ANIM_LAND_FROM_SINGLE_JUMP, C.ACT_IDLE);
    return false;
}

export function act_double_jump_land_stop(m) {
    if (check_common_landing_cancels(m, 0)) {
        return true;
    }

    landing_step(m, A.MARIO_ANIM_LAND_FROM_DOUBLE_JUMP, C.ACT_IDLE);
    return false;
}

export function act_side_flip_land_stop(m) {
    if (check_common_landing_cancels(m, 0)) {
        return true;
    }

    landing_step(m, A.MARIO_ANIM_SLIDEFLIP_LAND, C.ACT_IDLE);
    m.marioObj.header.gfx.angle[1] = s16(m.marioObj.header.gfx.angle[1] + 0x8000);
    return false;
}

export function act_freefall_land_stop(m) {
    if (check_common_landing_cancels(m, 0)) {
        return true;
    }

    landing_step(m, A.MARIO_ANIM_GENERAL_LAND, C.ACT_IDLE);
    return false;
}

export function act_triple_jump_land_stop(m) {
    if (check_common_landing_cancels(m, C.ACT_JUMP)) {
        return true;
    }

    landing_step(m, A.MARIO_ANIM_TRIPLE_JUMP_LAND, C.ACT_IDLE);
    return false;
}

export function act_backflip_land_stop(m) {
    if (!(m.input & INPUT_Z_DOWN) || m.marioObj.header.gfx.animInfo.animFrame >= 6) {
        m.input &= ~INPUT_A_PRESSED;
    }

    if (check_common_landing_cancels(m, C.ACT_BACKFLIP)) {
        return true;
    }

    landing_step(m, A.MARIO_ANIM_TRIPLE_JUMP_LAND, C.ACT_IDLE);
    return false;
}

export function act_lava_boost_land(m) {
    m.input &= ~(INPUT_FIRST_PERSON | INPUT_B_PRESSED);

    if (check_common_landing_cancels(m, 0)) {
        return true;
    }

    landing_step(m, A.MARIO_ANIM_STAND_UP_FROM_LAVA_BOOST, C.ACT_IDLE);
    return false;
}

export function act_long_jump_land_stop(m) {
    m.input &= ~INPUT_B_PRESSED;
    if (check_common_landing_cancels(m, C.ACT_JUMP)) {
        return true;
    }

    landing_step(m, !m.marioObj.oMarioLongJumpIsSlow ? A.MARIO_ANIM_CROUCH_FROM_FAST_LONGJUMP
        : A.MARIO_ANIM_CROUCH_FROM_SLOW_LONGJUMP,
    C.ACT_CROUCHING);
    return false;
}

export function act_twirl_land(m) {
    m.actionState = 1;
    if (m.input & INPUT_STOMPED) {
        return set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    stationary_ground_step(m);
    set_mario_animation(m, A.MARIO_ANIM_TWIRL_LAND);
    if (m.angleVel[1] > 0) {
        m.angleVel[1] -= 0x400;
        if (m.angleVel[1] < 0) {
            m.angleVel[1] = 0;
        }

        m.twirlYaw = s16(m.twirlYaw + m.angleVel[1]);
    }

    m.marioObj.header.gfx.angle[1] = s16(m.marioObj.header.gfx.angle[1] + m.twirlYaw);
    if (is_anim_at_end(m) && m.angleVel[1] === 0) {
        m.faceAngle[1] = s16(m.faceAngle[1] + m.twirlYaw);
        set_mario_action(m, C.ACT_IDLE, 0);
    }

    return false;
}

export function act_ground_pound_land(m) {
    m.actionState = 1;
    if (m.input & INPUT_STOMPED) {
        return drop_and_set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BUTT_SLIDE, 0);
    }

    landing_step(m, A.MARIO_ANIM_GROUND_POUND_LANDING, C.ACT_BUTT_SLIDE_STOP);
    return false;
}

export function act_first_person(m) {
    const sp1C = (m.input & (INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE | INPUT_STOMPED)) !== 0;

    if (m.actionState === 0) {
        m.actionState = 1;
    } else if (!(m.input & INPUT_FIRST_PERSON) || sp1C) {
        return set_mario_action(m, C.ACT_IDLE, 0);
    }

    stationary_ground_step(m);
    set_mario_animation(m, A.MARIO_ANIM_FIRST_PERSON);
    return false;
}

export function check_common_stationary_cancels(m) {
    if (m.pos[1] < m.waterLevel - 100) {
        update_mario_sound_and_camera(m);
        return set_water_plunge_action(m);
    }

    // (INPUT_SQUISHED only happens with dynamic surfaces: never set.)

    if (m.action !== C.ACT_UNKNOWN_0002020E) {
        if (m.health < 0x100) {
            update_mario_sound_and_camera(m);
            // return drop_and_set_mario_action(m, ACT_STANDING_DEATH, 0);
            request_death(m, C.ACT_STANDING_DEATH);
        }
    }
    return false;
}

export function mario_execute_stationary_action(m) {
    let cancel;

    if (check_common_stationary_cancels(m)) {
        return true;
    }

    if (mario_update_quicksand(m, 0.5)) {
        return true;
    }

    /* clang-format off */
    switch (m.action) {
        case C.ACT_IDLE:                    cancel = act_idle(m);                  break;
        case C.ACT_START_SLEEPING:          cancel = act_start_sleeping(m);        break;
        case C.ACT_SLEEPING:                cancel = act_sleeping(m);              break;
        case C.ACT_WAKING_UP:               cancel = act_waking_up(m);             break;
        case C.ACT_PANTING:                 cancel = act_panting(m);               break;
        case C.ACT_IN_QUICKSAND:            cancel = act_in_quicksand(m);          break;
        case C.ACT_STANDING_AGAINST_WALL:   cancel = act_standing_against_wall(m); break;
        case C.ACT_COUGHING:                cancel = act_coughing(m);              break;
        case C.ACT_SHIVERING:               cancel = act_shivering(m);             break;
        case C.ACT_CROUCHING:               cancel = act_crouching(m);             break;
        case C.ACT_START_CROUCHING:         cancel = act_start_crouching(m);       break;
        case C.ACT_STOP_CROUCHING:          cancel = act_stop_crouching(m);        break;
        case C.ACT_START_CRAWLING:          cancel = act_start_crawling(m);        break;
        case C.ACT_STOP_CRAWLING:           cancel = act_stop_crawling(m);         break;
        case C.ACT_SLIDE_KICK_SLIDE_STOP:   cancel = act_slide_kick_slide_stop(m); break;
        case C.ACT_SHOCKWAVE_BOUNCE:        cancel = act_shockwave_bounce(m);      break;
        case C.ACT_FIRST_PERSON:            cancel = act_first_person(m);          break;
        case C.ACT_JUMP_LAND_STOP:          cancel = act_jump_land_stop(m);        break;
        case C.ACT_DOUBLE_JUMP_LAND_STOP:   cancel = act_double_jump_land_stop(m); break;
        case C.ACT_FREEFALL_LAND_STOP:      cancel = act_freefall_land_stop(m);    break;
        case C.ACT_SIDE_FLIP_LAND_STOP:     cancel = act_side_flip_land_stop(m);   break;
        case C.ACT_LAVA_BOOST_LAND:         cancel = act_lava_boost_land(m);       break;
        case C.ACT_TWIRL_LAND:              cancel = act_twirl_land(m);            break;
        case C.ACT_TRIPLE_JUMP_LAND_STOP:   cancel = act_triple_jump_land_stop(m); break;
        case C.ACT_BACKFLIP_LAND_STOP:      cancel = act_backflip_land_stop(m);    break;
        case C.ACT_LONG_JUMP_LAND_STOP:     cancel = act_long_jump_land_stop(m);   break;
        case C.ACT_GROUND_POUND_LAND:       cancel = act_ground_pound_land(m);     break;
        case C.ACT_BRAKING_STOP:            cancel = act_braking_stop(m);          break;
        case C.ACT_BUTT_SLIDE_STOP:         cancel = act_butt_slide_stop(m);       break;
        default:
            // Not ported (object holding): fall back to idle.
            cancel = set_mario_action(m, C.ACT_IDLE, 0);
            break;
    }
    /* clang-format on */

    if (!cancel && (m.input & INPUT_IN_WATER)) {
        m.particleFlags |= C.PARTICLE_IDLE_WATER_WAVE;
    }

    return cancel;
}
