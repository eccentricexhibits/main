// Port of src/game/mario_actions_airborne.c (object holding, shells, cannon,
// flying, hoot, wind and crazy box actions are omitted).

import { s16, sins, coss, atan2s, approach_s32, approach_f32, vec3f_copy } from '../engine/math_util.js';
import * as S from '../engine/surface_terrains.js';
import * as C from './constants.js';
import * as A from './anim_ids.js';
import {
    F32, play_sound, play_sound_if_no_flag, play_mario_sound, play_mario_jump_sound,
    play_mario_landing_sound, play_mario_heavy_landing_sound,
    set_mario_animation, is_anim_past_end, mario_set_forward_vel, set_mario_action,
    drop_and_set_mario_action, mario_floor_is_slippery, update_mario_sound_and_camera,
    set_camera_shake_from_hit, mario_check_object_grab, mario_grab_used_object, set_water_plunge_action,
    level_trigger_warp, WARP_OP_DEATH,
} from './mario.js';
import { mario_bonk_reflection, perform_air_step } from './mario_step.js';

const {
    INPUT_NONZERO_ANALOG, INPUT_A_PRESSED, INPUT_A_DOWN, INPUT_B_PRESSED, INPUT_Z_PRESSED, INPUT_SQUISHED,
    AIR_STEP_NONE, AIR_STEP_LANDED, AIR_STEP_HIT_WALL, AIR_STEP_GRABBED_LEDGE, AIR_STEP_GRABBED_CEILING,
    AIR_STEP_HIT_LAVA_WALL, AIR_STEP_CHECK_LEDGE_GRAB, AIR_STEP_CHECK_HANG,
    MARIO_CAP_ON_HEAD, MARIO_METAL_CAP, MARIO_UNKNOWN_18, MARIO_MARIO_SOUND_PLAYED, MARIO_ACTION_SOUND_PLAYED,
} = C;

export function play_flip_sounds(m, frame1, frame2, frame3) {
    const animFrame = m.marioObj.header.gfx.animInfo.animFrame;
    if (animFrame === frame1 || animFrame === frame2 || animFrame === frame3) {
        play_sound(m, 'SOUND_ACTION_SPIN');
    }
}

export function play_far_fall_sound(m) {
    const action = m.action;
    if (!(action & C.ACT_FLAG_INVULNERABLE) && action !== C.ACT_TWIRLING && action !== C.ACT_FLYING
        && !(m.flags & MARIO_UNKNOWN_18)) {
        if (m.peakHeight - m.pos[1] > 1150.0) {
            play_sound(m, 'SOUND_MARIO_WAAAOOOW');
            m.flags |= MARIO_UNKNOWN_18;
        }
    }
}

export function play_knockback_sound(m) {
    if (m.actionArg === 0 && (m.forwardVel <= -28.0 || m.forwardVel >= 28.0)) {
        play_sound_if_no_flag(m, 'SOUND_MARIO_DOH', MARIO_MARIO_SOUND_PLAYED);
    } else {
        play_sound_if_no_flag(m, 'SOUND_MARIO_UH', MARIO_MARIO_SOUND_PLAYED);
    }
}

export function lava_boost_on_wall(m) {
    m.faceAngle[1] = atan2s(m.wall.normal.z, m.wall.normal.x);

    if (m.forwardVel < 24.0) {
        m.forwardVel = 24.0;
    }

    if (!(m.flags & MARIO_METAL_CAP)) {
        m.hurtCounter = (m.hurtCounter + ((m.flags & MARIO_CAP_ON_HEAD) ? 12 : 18)) & 0xFF;
    }

    play_sound(m, 'SOUND_MARIO_ON_FIRE');
    update_mario_sound_and_camera(m);
    return drop_and_set_mario_action(m, C.ACT_LAVA_BOOST, 1);
}

export function check_fall_damage(m, hardFallAction) {
    let damageHeight;

    const fallHeight = m.peakHeight - m.pos[1];

    //! Never true
    if (m.actionState === C.ACT_GROUND_POUND) {
        damageHeight = 600.0;
    } else {
        damageHeight = 1150.0;
    }

    if (m.action !== C.ACT_TWIRLING && m.floor.type !== S.SURFACE_BURNING) {
        if (m.vel[1] < -55.0) {
            if (fallHeight > 3000.0) {
                m.hurtCounter = (m.hurtCounter + ((m.flags & MARIO_CAP_ON_HEAD) ? 16 : 24)) & 0xFF;
                set_camera_shake_from_hit(m, 'SHAKE_FALL_DAMAGE');
                play_sound(m, 'SOUND_MARIO_ATTACKED');
                return drop_and_set_mario_action(m, hardFallAction, 4);
            } else if (fallHeight > damageHeight && !mario_floor_is_slippery(m)) {
                m.hurtCounter = (m.hurtCounter + ((m.flags & MARIO_CAP_ON_HEAD) ? 8 : 12)) & 0xFF;
                m.squishTimer = 30;
                set_camera_shake_from_hit(m, 'SHAKE_FALL_DAMAGE');
                play_sound(m, 'SOUND_MARIO_ATTACKED');
            }
        }
    }

    return false;
}

export function check_kick_or_dive_in_air(m) {
    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, m.forwardVel > 28.0 ? C.ACT_DIVE : C.ACT_JUMP_KICK, 0);
    }
    return false;
}

export function should_get_stuck_in_ground(m) {
    const terrainType = m.area.terrainType & S.TERRAIN_MASK;
    const floor = m.floor;
    const flags = floor.flags;
    const type = floor.type;

    if (floor !== null && (terrainType === S.TERRAIN_SNOW || terrainType === S.TERRAIN_SAND)
        && type !== S.SURFACE_BURNING && S.SURFACE_IS_NOT_HARD(type)) {
        if (!(flags & 0x01) && m.peakHeight - m.pos[1] > 1000.0 && floor.normal.y >= F32(0.8660254)) {
            return true;
        }
    }

    return false;
}

export function check_fall_damage_or_get_stuck(m, hardFallAction) {
    if (should_get_stuck_in_ground(m)) {
        // ACT_FEET_STUCK_IN_GROUND is a cutscene action (not ported): only the
        // sound and particles are kept, then we fall through to normal landing.
        play_sound(m, 'SOUND_MARIO_OOOF2');
        m.particleFlags |= C.PARTICLE_MIST_CIRCLE;
    }

    return check_fall_damage(m, hardFallAction);
}

export function check_horizontal_wind(m) {
    const floor = m.floor;

    if (floor.type === S.SURFACE_HORIZONTAL_WIND) {
        const pushAngle = s16(floor.force << 8);

        m.slideVelX += 1.2 * sins(pushAngle);
        m.slideVelZ += 1.2 * coss(pushAngle);

        let speed = Math.sqrt(m.slideVelX * m.slideVelX + m.slideVelZ * m.slideVelZ);

        if (speed > 48.0) {
            m.slideVelX = m.slideVelX * 48.0 / speed;
            m.slideVelZ = m.slideVelZ * 48.0 / speed;
            speed = 32.0; //! This was meant to be 48?
        } else if (speed > 32.0) {
            speed = 32.0;
        }

        m.vel[0] = m.slideVelX;
        m.vel[2] = m.slideVelZ;
        m.slideYaw = atan2s(m.slideVelZ, m.slideVelX);
        m.forwardVel = speed * coss(m.faceAngle[1] - m.slideYaw);

        return true;
    }

    return false;
}

export function update_air_with_turn(m) {
    if (!check_horizontal_wind(m)) {
        const dragThreshold = m.action === C.ACT_LONG_JUMP ? 48.0 : 32.0;
        m.forwardVel = approach_f32(m.forwardVel, 0.0, 0.35, 0.35);

        if (m.input & INPUT_NONZERO_ANALOG) {
            const intendedDYaw = s16(m.intendedYaw - m.faceAngle[1]);
            const intendedMag = m.intendedMag / 32.0;

            m.forwardVel += 1.5 * coss(intendedDYaw) * intendedMag;
            m.faceAngle[1] = s16(m.faceAngle[1] + 512.0 * sins(intendedDYaw) * intendedMag);
        }

        //! Uncapped air speed. Net positive when moving forward.
        if (m.forwardVel > dragThreshold) {
            m.forwardVel -= 1.0;
        }
        if (m.forwardVel < -16.0) {
            m.forwardVel += 2.0;
        }

        m.vel[0] = m.slideVelX = m.forwardVel * sins(m.faceAngle[1]);
        m.vel[2] = m.slideVelZ = m.forwardVel * coss(m.faceAngle[1]);
    }
}

export function update_air_without_turn(m) {
    let sidewaysSpeed = 0.0;

    if (!check_horizontal_wind(m)) {
        const dragThreshold = m.action === C.ACT_LONG_JUMP ? 48.0 : 32.0;
        m.forwardVel = approach_f32(m.forwardVel, 0.0, 0.35, 0.35);

        if (m.input & INPUT_NONZERO_ANALOG) {
            const intendedDYaw = s16(m.intendedYaw - m.faceAngle[1]);
            const intendedMag = m.intendedMag / 32.0;

            m.forwardVel += intendedMag * coss(intendedDYaw) * 1.5;
            sidewaysSpeed = intendedMag * sins(intendedDYaw) * 10.0;
        }

        //! Uncapped air speed. Net positive when moving forward.
        if (m.forwardVel > dragThreshold) {
            m.forwardVel -= 1.0;
        }
        if (m.forwardVel < -16.0) {
            m.forwardVel += 2.0;
        }

        m.slideVelX = m.forwardVel * sins(m.faceAngle[1]);
        m.slideVelZ = m.forwardVel * coss(m.faceAngle[1]);

        m.slideVelX += sidewaysSpeed * sins(m.faceAngle[1] + 0x4000);
        m.slideVelZ += sidewaysSpeed * coss(m.faceAngle[1] + 0x4000);

        m.vel[0] = m.slideVelX;
        m.vel[2] = m.slideVelZ;
    }
}

export function update_lava_boost_or_twirling(m) {
    if (m.input & INPUT_NONZERO_ANALOG) {
        const intendedDYaw = s16(m.intendedYaw - m.faceAngle[1]);
        const intendedMag = m.intendedMag / 32.0;

        m.forwardVel += coss(intendedDYaw) * intendedMag;
        m.faceAngle[1] = s16(m.faceAngle[1] + sins(intendedDYaw) * intendedMag * 1024.0);

        if (m.forwardVel < 0.0) {
            m.faceAngle[1] = s16(m.faceAngle[1] + 0x8000);
            m.forwardVel *= -1.0;
        }

        if (m.forwardVel > 32.0) {
            m.forwardVel -= 2.0;
        }
    }

    m.vel[0] = m.slideVelX = m.forwardVel * sins(m.faceAngle[1]);
    m.vel[2] = m.slideVelZ = m.forwardVel * coss(m.faceAngle[1]);
}

export function common_air_action_step(m, landAction, animation, stepArg) {
    update_air_without_turn(m);

    const stepResult = perform_air_step(m, stepArg);
    switch (stepResult) {
        case AIR_STEP_NONE:
            set_mario_animation(m, animation);
            break;

        case AIR_STEP_LANDED:
            if (!check_fall_damage_or_get_stuck(m, C.ACT_HARD_BACKWARD_GROUND_KB)) {
                set_mario_action(m, landAction, 0);
            }
            break;

        case AIR_STEP_HIT_WALL:
            set_mario_animation(m, animation);

            if (m.forwardVel > 16.0) {
                mario_bonk_reflection(m, false);
                m.faceAngle[1] = s16(m.faceAngle[1] + 0x8000);

                if (m.wall !== null) {
                    set_mario_action(m, C.ACT_AIR_HIT_WALL, 0);
                } else {
                    if (m.vel[1] > 0.0) {
                        m.vel[1] = 0.0;
                    }

                    //! Hands-free holding.
                    if (m.forwardVel >= 38.0) {
                        m.particleFlags |= C.PARTICLE_VERTICAL_STAR;
                        set_mario_action(m, C.ACT_BACKWARD_AIR_KB, 0);
                    } else {
                        if (m.forwardVel > 8.0) {
                            mario_set_forward_vel(m, -8.0);
                        }
                        return set_mario_action(m, C.ACT_SOFT_BONK, 0);
                    }
                }
            } else {
                mario_set_forward_vel(m, 0.0);
            }
            break;

        case AIR_STEP_GRABBED_LEDGE:
            set_mario_animation(m, A.MARIO_ANIM_IDLE_ON_LEDGE);
            drop_and_set_mario_action(m, C.ACT_LEDGE_GRAB, 0);
            break;

        case AIR_STEP_GRABBED_CEILING:
            set_mario_action(m, C.ACT_START_HANGING, 0);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    return stepResult;
}

export function act_jump(m) {
    if (check_kick_or_dive_in_air(m)) {
        return true;
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 0);
    common_air_action_step(m, C.ACT_JUMP_LAND, A.MARIO_ANIM_SINGLE_JUMP,
        AIR_STEP_CHECK_LEDGE_GRAB | AIR_STEP_CHECK_HANG);
    return false;
}

export function act_double_jump(m) {
    const animation = (m.vel[1] >= 0.0)
        ? A.MARIO_ANIM_DOUBLE_JUMP_RISE
        : A.MARIO_ANIM_DOUBLE_JUMP_FALL;

    if (check_kick_or_dive_in_air(m)) {
        return true;
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 'SOUND_MARIO_HOOHOO');
    common_air_action_step(m, C.ACT_DOUBLE_JUMP_LAND, animation,
        AIR_STEP_CHECK_LEDGE_GRAB | AIR_STEP_CHECK_HANG);
    return false;
}

export function act_triple_jump(m) {
    // (gSpecialTripleJump is never set in this port.)

    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_DIVE, 0);
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 0);

    common_air_action_step(m, C.ACT_TRIPLE_JUMP_LAND, A.MARIO_ANIM_TRIPLE_JUMP, 0);
    play_flip_sounds(m, 2, 8, 20);
    return false;
}

export function act_backflip(m) {
    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 'SOUND_MARIO_YAH_WAH_HOO');
    common_air_action_step(m, C.ACT_BACKFLIP_LAND, A.MARIO_ANIM_BACKFLIP, 0);
    play_flip_sounds(m, 2, 3, 17);
    return false;
}

export function act_freefall(m) {
    let animation;

    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_DIVE, 0);
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    switch (m.actionArg) {
        case 0:
            animation = A.MARIO_ANIM_GENERAL_FALL;
            break;
        case 1:
            animation = A.MARIO_ANIM_FALL_FROM_SLIDE;
            break;
        case 2:
            animation = A.MARIO_ANIM_FALL_FROM_SLIDE_KICK;
            break;
        default:
            // (uninitialized in the original)
            animation = A.MARIO_ANIM_GENERAL_FALL;
            break;
    }

    common_air_action_step(m, C.ACT_FREEFALL_LAND, animation, AIR_STEP_CHECK_LEDGE_GRAB);
    return false;
}

export function act_side_flip(m) {
    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_DIVE, 0);
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 0);

    if (common_air_action_step(m, C.ACT_SIDE_FLIP_LAND, A.MARIO_ANIM_SLIDEFLIP, AIR_STEP_CHECK_LEDGE_GRAB)
        !== AIR_STEP_GRABBED_LEDGE) {
        m.marioObj.header.gfx.angle[1] = s16(m.marioObj.header.gfx.angle[1] + 0x8000);
    }

    if (m.marioObj.header.gfx.animInfo.animFrame === 6) play_sound(m, 'SOUND_ACTION_SIDE_FLIP_UNK');
    return false;
}

export function act_wall_kick_air(m) {
    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_DIVE, 0);
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_GROUND_POUND, 0);
    }

    play_mario_jump_sound(m);
    common_air_action_step(m, C.ACT_JUMP_LAND, A.MARIO_ANIM_SLIDEJUMP, AIR_STEP_CHECK_LEDGE_GRAB);
    return false;
}

export function act_long_jump(m) {
    let animation;
    if (!m.marioObj.oMarioLongJumpIsSlow) {
        animation = A.MARIO_ANIM_FAST_LONGJUMP;
    } else {
        animation = A.MARIO_ANIM_SLOW_LONGJUMP;
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 'SOUND_MARIO_YAHOO');

    if (m.floor.type === S.SURFACE_VERTICAL_WIND && m.actionState === 0) {
        play_sound(m, 'SOUND_MARIO_HERE_WE_GO');
        m.actionState = 1;
    }

    common_air_action_step(m, C.ACT_LONG_JUMP_LAND, animation, AIR_STEP_CHECK_LEDGE_GRAB);
    return false;
}

export function act_twirling(m) {
    const startTwirlYaw = m.twirlYaw;
    let yawVelTarget;

    if (m.input & INPUT_A_DOWN) {
        yawVelTarget = 0x2000;
    } else {
        yawVelTarget = 0x1800;
    }

    m.angleVel[1] = s16(approach_s32(m.angleVel[1], yawVelTarget, 0x200, 0x200));
    m.twirlYaw = s16(m.twirlYaw + m.angleVel[1]);

    set_mario_animation(m, m.actionArg === 0 ? A.MARIO_ANIM_START_TWIRL : A.MARIO_ANIM_TWIRL);
    if (is_anim_past_end(m)) {
        m.actionArg = 1;
    }

    if (startTwirlYaw > m.twirlYaw) {
        play_sound(m, 'SOUND_ACTION_TWIRL');
    }

    update_lava_boost_or_twirling(m);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_LANDED:
            set_mario_action(m, C.ACT_TWIRL_LAND, 0);
            break;

        case AIR_STEP_HIT_WALL:
            mario_bonk_reflection(m, false);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    m.marioObj.header.gfx.angle[1] = s16(m.marioObj.header.gfx.angle[1] + m.twirlYaw);
    return false;
}

export function act_dive(m) {
    if (m.actionArg === 0) {
        play_mario_sound(m, 'SOUND_ACTION_THROW', 'SOUND_MARIO_HOOHOO');
    } else {
        play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 0);
    }

    set_mario_animation(m, A.MARIO_ANIM_DIVE);
    if (mario_check_object_grab(m)) {
        mario_grab_used_object(m);
        m.marioBodyState.grabPos = C.GRAB_POS_LIGHT_OBJ;
        if (m.action !== C.ACT_DIVE) {
            return true;
        }
    }

    update_air_without_turn(m);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_NONE:
            if (m.vel[1] < 0.0 && m.faceAngle[0] > -0x2AAA) {
                m.faceAngle[0] -= 0x200;
                if (m.faceAngle[0] < -0x2AAA) {
                    m.faceAngle[0] = -0x2AAA;
                }
            }
            m.marioObj.header.gfx.angle[0] = s16(-m.faceAngle[0]);
            break;

        case AIR_STEP_LANDED:
            if (should_get_stuck_in_ground(m) && m.faceAngle[0] === -0x2AAA) {
                // ACT_HEAD_STUCK_IN_GROUND (cutscene) not ported: land normally.
                play_sound(m, 'SOUND_MARIO_OOOF2');
                m.particleFlags |= C.PARTICLE_MIST_CIRCLE;
            }
            if (!check_fall_damage(m, C.ACT_HARD_FORWARD_GROUND_KB)) {
                set_mario_action(m, C.ACT_DIVE_SLIDE, 0);
            }
            m.faceAngle[0] = 0;
            break;

        case AIR_STEP_HIT_WALL:
            mario_bonk_reflection(m, true);
            m.faceAngle[0] = 0;

            if (m.vel[1] > 0.0) {
                m.vel[1] = 0.0;
            }

            m.particleFlags |= C.PARTICLE_VERTICAL_STAR;
            drop_and_set_mario_action(m, C.ACT_BACKWARD_AIR_KB, 0);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    return false;
}

export function act_steep_jump(m) {
    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_DIVE, 0);
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 0);
    mario_set_forward_vel(m, 0.98 * m.forwardVel);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_LANDED:
            if (!check_fall_damage_or_get_stuck(m, C.ACT_HARD_BACKWARD_GROUND_KB)) {
                m.faceAngle[0] = 0;
                set_mario_action(m, m.forwardVel < 0.0 ? C.ACT_BEGIN_SLIDING : C.ACT_JUMP_LAND, 0);
            }
            break;

        case AIR_STEP_HIT_WALL:
            mario_set_forward_vel(m, 0.0);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    set_mario_animation(m, A.MARIO_ANIM_SINGLE_JUMP);
    m.marioObj.header.gfx.angle[1] = m.marioObj.oMarioSteepJumpYaw;
    return false;
}

export function act_ground_pound(m) {
    play_sound_if_no_flag(m, 'SOUND_ACTION_THROW', MARIO_ACTION_SOUND_PLAYED);

    if (m.actionState === 0) {
        if (m.actionTimer < 10) {
            const yOffset = 20 - 2 * m.actionTimer;
            if (m.pos[1] + yOffset + 160.0 < m.ceilHeight) {
                m.pos[1] += yOffset;
                m.peakHeight = m.pos[1];
                vec3f_copy(m.marioObj.header.gfx.pos, m.pos);
            }
        }

        m.vel[1] = -50.0;
        mario_set_forward_vel(m, 0.0);

        set_mario_animation(m, m.actionArg === 0 ? A.MARIO_ANIM_START_GROUND_POUND
            : A.MARIO_ANIM_TRIPLE_JUMP_GROUND_POUND);
        if (m.actionTimer === 0) {
            play_sound(m, 'SOUND_ACTION_SPIN');
        }

        m.actionTimer++;
        if (m.actionTimer >= m.marioObj.header.gfx.animInfo.curAnim.loopEnd + 4) {
            play_sound(m, 'SOUND_MARIO_GROUND_POUND_WAH');
            m.actionState = 1;
        }
    } else {
        set_mario_animation(m, A.MARIO_ANIM_GROUND_POUND);

        const stepResult = perform_air_step(m, 0);
        if (stepResult === AIR_STEP_LANDED) {
            if (should_get_stuck_in_ground(m)) {
                // ACT_BUTT_STUCK_IN_GROUND (cutscene) not ported: land normally.
                play_sound(m, 'SOUND_MARIO_OOOF2');
                m.particleFlags |= C.PARTICLE_MIST_CIRCLE;
            }
            play_mario_heavy_landing_sound(m, 'SOUND_ACTION_TERRAIN_HEAVY_LANDING');
            if (!check_fall_damage(m, C.ACT_HARD_BACKWARD_GROUND_KB)) {
                m.particleFlags |= C.PARTICLE_MIST_CIRCLE | C.PARTICLE_HORIZONTAL_STAR;
                set_mario_action(m, C.ACT_GROUND_POUND_LAND, 0);
            }
            set_camera_shake_from_hit(m, 'SHAKE_GROUND_POUND');
        } else if (stepResult === AIR_STEP_HIT_WALL) {
            mario_set_forward_vel(m, -16.0);
            if (m.vel[1] > 0.0) {
                m.vel[1] = 0.0;
            }

            m.particleFlags |= C.PARTICLE_VERTICAL_STAR;
            set_mario_action(m, C.ACT_BACKWARD_AIR_KB, 0);
        }
    }

    return false;
}

export function act_burning_jump(m) {
    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', m.actionArg === 0 ? 0 : -1);
    mario_set_forward_vel(m, m.forwardVel);

    if (perform_air_step(m, 0) === AIR_STEP_LANDED) {
        play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
        set_mario_action(m, C.ACT_BURNING_GROUND, 0);
    }

    set_mario_animation(m, m.actionArg === 0 ? A.MARIO_ANIM_SINGLE_JUMP : A.MARIO_ANIM_FIRE_LAVA_BURN);
    m.particleFlags |= C.PARTICLE_FIRE;
    play_sound(m, 'SOUND_MOVING_LAVA_BURN');

    m.marioObj.oMarioBurnTimer += 3;

    m.health -= 10;
    if (m.health < 0x100) {
        m.health = 0xFF;
    }
    return false;
}

export function act_burning_fall(m) {
    mario_set_forward_vel(m, m.forwardVel);

    if (perform_air_step(m, 0) === AIR_STEP_LANDED) {
        play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
        set_mario_action(m, C.ACT_BURNING_GROUND, 0);
    }

    set_mario_animation(m, A.MARIO_ANIM_GENERAL_FALL);
    m.particleFlags |= C.PARTICLE_FIRE;
    m.marioObj.oMarioBurnTimer += 3;

    m.health -= 10;
    if (m.health < 0x100) {
        m.health = 0xFF;
    }
    return false;
}

export function common_air_knockback_step(m, landAction, hardFallAction, animation, speed) {
    mario_set_forward_vel(m, speed);

    const stepResult = perform_air_step(m, 0);
    switch (stepResult) {
        case AIR_STEP_NONE:
            set_mario_animation(m, animation);
            break;

        case AIR_STEP_LANDED:
            if (!check_fall_damage_or_get_stuck(m, hardFallAction)) {
                if (m.action === C.ACT_THROWN_FORWARD || m.action === C.ACT_THROWN_BACKWARD) {
                    set_mario_action(m, landAction, m.hurtCounter);
                } else {
                    set_mario_action(m, landAction, m.actionArg);
                }
            }
            break;

        case AIR_STEP_HIT_WALL:
            set_mario_animation(m, A.MARIO_ANIM_BACKWARD_AIR_KB);
            mario_bonk_reflection(m, false);

            if (m.vel[1] > 0.0) {
                m.vel[1] = 0.0;
            }

            mario_set_forward_vel(m, -speed);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    return stepResult;
}

export function check_wall_kick(m) {
    if ((m.input & INPUT_A_PRESSED) && m.wallKickTimer !== 0 && m.prevAction === C.ACT_AIR_HIT_WALL) {
        m.faceAngle[1] = s16(m.faceAngle[1] + 0x8000);
        return set_mario_action(m, C.ACT_WALL_KICK_AIR, 0);
    }

    return false;
}

export function act_backward_air_kb(m) {
    if (check_wall_kick(m)) {
        return true;
    }

    play_knockback_sound(m);
    common_air_knockback_step(m, C.ACT_BACKWARD_GROUND_KB, C.ACT_HARD_BACKWARD_GROUND_KB, 0x0002, -16.0);
    return false;
}

export function act_forward_air_kb(m) {
    if (check_wall_kick(m)) {
        return true;
    }

    play_knockback_sound(m);
    common_air_knockback_step(m, C.ACT_FORWARD_GROUND_KB, C.ACT_HARD_FORWARD_GROUND_KB, 0x002D, 16.0);
    return false;
}

export function act_hard_backward_air_kb(m) {
    play_knockback_sound(m);
    common_air_knockback_step(m, C.ACT_HARD_BACKWARD_GROUND_KB, C.ACT_HARD_BACKWARD_GROUND_KB, 0x0002, -16.0);
    return false;
}

export function act_hard_forward_air_kb(m) {
    play_knockback_sound(m);
    common_air_knockback_step(m, C.ACT_HARD_FORWARD_GROUND_KB, C.ACT_HARD_FORWARD_GROUND_KB, 0x002D, 16.0);
    return false;
}

export function act_soft_bonk(m) {
    if (check_wall_kick(m)) {
        return true;
    }

    play_knockback_sound(m);

    common_air_knockback_step(m, C.ACT_FREEFALL_LAND, C.ACT_HARD_BACKWARD_GROUND_KB, 0x0056, m.forwardVel);
    return false;
}

export function act_air_hit_wall(m) {
    if (++m.actionTimer <= 2) {
        if (m.input & INPUT_A_PRESSED) {
            m.vel[1] = 52.0;
            m.faceAngle[1] = s16(m.faceAngle[1] + 0x8000);
            return set_mario_action(m, C.ACT_WALL_KICK_AIR, 0);
        }
    } else if (m.forwardVel >= 38.0) {
        m.wallKickTimer = 5;
        if (m.vel[1] > 0.0) {
            m.vel[1] = 0.0;
        }

        m.particleFlags |= C.PARTICLE_VERTICAL_STAR;
        return set_mario_action(m, C.ACT_BACKWARD_AIR_KB, 0);
    } else {
        m.wallKickTimer = 5;
        if (m.vel[1] > 0.0) {
            m.vel[1] = 0.0;
        }

        if (m.forwardVel > 8.0) {
            mario_set_forward_vel(m, -8.0);
        }
        return set_mario_action(m, C.ACT_SOFT_BONK, 0);
    }

    //! Missing return statement. The returned value is the result of the call
    // to set_mario_animation. In practice, this value is nonzero.
    // This results in this action "cancelling" into itself. It is supposed to
    // execute on two frames, but instead it executes twice on the same frame.
    // This results in firsties only being possible for a single frame, instead
    // of two.
    return set_mario_animation(m, A.MARIO_ANIM_START_WALLKICK) !== 0;
}

export function act_forward_rollout(m) {
    if (m.actionState === 0) {
        m.vel[1] = 30.0;
        m.actionState = 1;
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 0);

    update_air_without_turn(m);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_NONE:
            if (m.actionState === 1) {
                if (set_mario_animation(m, A.MARIO_ANIM_FORWARD_SPINNING) === 4) {
                    play_sound(m, 'SOUND_ACTION_SPIN');
                }
            } else {
                set_mario_animation(m, A.MARIO_ANIM_GENERAL_FALL);
            }
            break;

        case AIR_STEP_LANDED:
            set_mario_action(m, C.ACT_FREEFALL_LAND_STOP, 0);
            play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
            break;

        case AIR_STEP_HIT_WALL:
            mario_set_forward_vel(m, 0.0);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    if (m.actionState === 1 && is_anim_past_end(m)) {
        m.actionState = 2;
    }
    return false;
}

export function act_backward_rollout(m) {
    if (m.actionState === 0) {
        m.vel[1] = 30.0;
        m.actionState = 1;
    }

    play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 0);

    update_air_without_turn(m);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_NONE:
            if (m.actionState === 1) {
                if (set_mario_animation(m, A.MARIO_ANIM_BACKWARD_SPINNING) === 4) {
                    play_sound(m, 'SOUND_ACTION_SPIN');
                }
            } else {
                set_mario_animation(m, A.MARIO_ANIM_GENERAL_FALL);
            }
            break;

        case AIR_STEP_LANDED:
            set_mario_action(m, C.ACT_FREEFALL_LAND_STOP, 0);
            play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
            break;

        case AIR_STEP_HIT_WALL:
            mario_set_forward_vel(m, 0.0);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    if (m.actionState === 1 && m.marioObj.header.gfx.animInfo.animFrame === 2) {
        m.actionState = 2;
    }
    return false;
}

export function act_butt_slide_air(m) {
    if (++m.actionTimer > 30 && m.pos[1] - m.floorHeight > 500.0) {
        return set_mario_action(m, C.ACT_FREEFALL, 1);
    }

    update_air_with_turn(m);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_LANDED:
            if (m.actionState === 0 && m.vel[1] < 0.0 && m.floor.normal.y >= F32(0.9848077)) {
                m.vel[1] = -m.vel[1] / 2.0;
                m.actionState = 1;
            } else {
                set_mario_action(m, C.ACT_BUTT_SLIDE, 0);
            }
            play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
            break;

        case AIR_STEP_HIT_WALL:
            if (m.vel[1] > 0.0) {
                m.vel[1] = 0.0;
            }
            m.particleFlags |= C.PARTICLE_VERTICAL_STAR;
            set_mario_action(m, C.ACT_BACKWARD_AIR_KB, 0);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    set_mario_animation(m, A.MARIO_ANIM_SLIDE);
    return false;
}

export function act_lava_boost(m) {
    play_sound_if_no_flag(m, 'SOUND_MARIO_ON_FIRE', MARIO_MARIO_SOUND_PLAYED);

    if (!(m.input & INPUT_NONZERO_ANALOG)) {
        m.forwardVel = approach_f32(m.forwardVel, 0.0, 0.35, 0.35);
    }

    update_lava_boost_or_twirling(m);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_LANDED:
            if (m.floor.type === S.SURFACE_BURNING) {
                m.actionState = 0;
                if (!(m.flags & MARIO_METAL_CAP)) {
                    m.hurtCounter = (m.hurtCounter + ((m.flags & MARIO_CAP_ON_HEAD) ? 12 : 18)) & 0xFF;
                }
                m.vel[1] = 84.0;
                play_sound(m, 'SOUND_MARIO_ON_FIRE');
            } else {
                play_mario_heavy_landing_sound(m, 'SOUND_ACTION_TERRAIN_BODY_HIT_GROUND');
                if (m.actionState < 2 && m.vel[1] < 0.0) {
                    m.vel[1] = -m.vel[1] * 0.4;
                    mario_set_forward_vel(m, m.forwardVel * 0.5);
                    m.actionState++;
                } else {
                    set_mario_action(m, C.ACT_LAVA_BOOST_LAND, 0);
                }
            }
            break;

        case AIR_STEP_HIT_WALL:
            mario_bonk_reflection(m, false);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    set_mario_animation(m, A.MARIO_ANIM_FIRE_LAVA_BURN);
    if ((m.area.terrainType & S.TERRAIN_MASK) !== S.TERRAIN_SNOW && !(m.flags & MARIO_METAL_CAP)
        && m.vel[1] > 0.0) {
        m.particleFlags |= C.PARTICLE_FIRE;
        if (m.actionState === 0) {
            play_sound(m, 'SOUND_MOVING_LAVA_BURN');
        }
    }

    if (m.health < 0x100) {
        level_trigger_warp(m, WARP_OP_DEATH);
    }

    m.marioBodyState.eyeState = C.MARIO_EYES_DEAD;
    return false;
}

export function act_slide_kick(m) {
    if (m.actionState === 0 && m.actionTimer === 0) {
        play_mario_sound(m, 'SOUND_ACTION_TERRAIN_JUMP', 'SOUND_MARIO_HOOHOO');
        set_mario_animation(m, A.MARIO_ANIM_SLIDE_KICK);
    }

    if (++m.actionTimer > 30 && m.pos[1] - m.floorHeight > 500.0) {
        return set_mario_action(m, C.ACT_FREEFALL, 2);
    }

    update_air_without_turn(m);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_NONE:
            if (m.actionState === 0) {
                m.marioObj.header.gfx.angle[0] = atan2s(m.forwardVel, -m.vel[1]);
                if (m.marioObj.header.gfx.angle[0] > 0x1800) {
                    m.marioObj.header.gfx.angle[0] = 0x1800;
                }
            }
            break;

        case AIR_STEP_LANDED:
            if (m.actionState === 0 && m.vel[1] < 0.0) {
                m.vel[1] = -m.vel[1] / 2.0;
                m.actionState = 1;
                m.actionTimer = 0;
            } else {
                set_mario_action(m, C.ACT_SLIDE_KICK_SLIDE, 0);
            }
            play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
            break;

        case AIR_STEP_HIT_WALL:
            if (m.vel[1] > 0.0) {
                m.vel[1] = 0.0;
            }

            m.particleFlags |= C.PARTICLE_VERTICAL_STAR;

            set_mario_action(m, C.ACT_BACKWARD_AIR_KB, 0);
            break;

        case AIR_STEP_HIT_LAVA_WALL:
            lava_boost_on_wall(m);
            break;
    }

    return false;
}

export function act_jump_kick(m) {
    if (m.actionState === 0) {
        play_sound_if_no_flag(m, 'SOUND_MARIO_PUNCH_HOO', MARIO_ACTION_SOUND_PLAYED);
        m.marioObj.header.gfx.animInfo.animID = -1;
        set_mario_animation(m, A.MARIO_ANIM_AIR_KICK);
        m.actionState = 1;
    }

    const animFrame = m.marioObj.header.gfx.animInfo.animFrame;
    if (animFrame === 0) {
        m.marioBodyState.punchState = (2 << 6) | 6;
    }
    if (animFrame >= 0 && animFrame < 8) {
        m.flags |= C.MARIO_KICKING;
    }

    update_air_without_turn(m);

    switch (perform_air_step(m, 0)) {
        case AIR_STEP_LANDED:
            if (!check_fall_damage_or_get_stuck(m, C.ACT_HARD_BACKWARD_GROUND_KB)) {
                set_mario_action(m, C.ACT_FREEFALL_LAND, 0);
            }
            break;

        case AIR_STEP_HIT_WALL:
            mario_set_forward_vel(m, 0.0);
            break;
    }

    return false;
}

export function check_common_airborne_cancels(m) {
    if (m.pos[1] < m.waterLevel - 100) {
        return set_water_plunge_action(m);
    }

    // (INPUT_SQUISHED only happens with dynamic surfaces: never set.)
    // (SURFACE_VERTICAL_WIND -> ACT_VERTICAL_WIND not ported.)

    m.quicksandDepth = 0.0;
    return false;
}

export function mario_execute_airborne_action(m) {
    let cancel;

    if (check_common_airborne_cancels(m)) {
        return true;
    }

    play_far_fall_sound(m);

    /* clang-format off */
    switch (m.action) {
        case C.ACT_JUMP:                 cancel = act_jump(m);                 break;
        case C.ACT_DOUBLE_JUMP:          cancel = act_double_jump(m);          break;
        case C.ACT_FREEFALL:             cancel = act_freefall(m);             break;
        case C.ACT_SIDE_FLIP:            cancel = act_side_flip(m);            break;
        case C.ACT_WALL_KICK_AIR:        cancel = act_wall_kick_air(m);        break;
        case C.ACT_TWIRLING:             cancel = act_twirling(m);             break;
        case C.ACT_STEEP_JUMP:           cancel = act_steep_jump(m);           break;
        case C.ACT_BURNING_JUMP:         cancel = act_burning_jump(m);         break;
        case C.ACT_BURNING_FALL:         cancel = act_burning_fall(m);         break;
        case C.ACT_TRIPLE_JUMP:          cancel = act_triple_jump(m);          break;
        case C.ACT_BACKFLIP:             cancel = act_backflip(m);             break;
        case C.ACT_LONG_JUMP:            cancel = act_long_jump(m);            break;
        case C.ACT_DIVE:                 cancel = act_dive(m);                 break;
        case C.ACT_BACKWARD_AIR_KB:      cancel = act_backward_air_kb(m);      break;
        case C.ACT_FORWARD_AIR_KB:       cancel = act_forward_air_kb(m);       break;
        case C.ACT_HARD_FORWARD_AIR_KB:  cancel = act_hard_forward_air_kb(m);  break;
        case C.ACT_HARD_BACKWARD_AIR_KB: cancel = act_hard_backward_air_kb(m); break;
        case C.ACT_SOFT_BONK:            cancel = act_soft_bonk(m);            break;
        case C.ACT_AIR_HIT_WALL:         cancel = act_air_hit_wall(m);         break;
        case C.ACT_FORWARD_ROLLOUT:      cancel = act_forward_rollout(m);      break;
        case C.ACT_BUTT_SLIDE_AIR:       cancel = act_butt_slide_air(m);       break;
        case C.ACT_LAVA_BOOST:           cancel = act_lava_boost(m);           break;
        case C.ACT_BACKWARD_ROLLOUT:     cancel = act_backward_rollout(m);     break;
        case C.ACT_GROUND_POUND:         cancel = act_ground_pound(m);         break;
        case C.ACT_SLIDE_KICK:           cancel = act_slide_kick(m);           break;
        case C.ACT_JUMP_KICK:            cancel = act_jump_kick(m);            break;
        default:
            // Not ported (holding, shell, cannon, flying, ...): fall back to freefall.
            cancel = set_mario_action(m, C.ACT_FREEFALL, 0);
            break;
    }
    /* clang-format on */

    return cancel;
}
