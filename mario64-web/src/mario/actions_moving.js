// Port of src/game/mario_actions_moving.c (object-holding and shell-riding
// actions are omitted: there are no objects in this port).

import { s16, s32, sins, coss, atan2s, approach_s32, approach_f32, vec3f_copy, mtxf_new, mtxf_align_terrain_triangle } from '../engine/math_util.js';
import * as S from '../engine/surface_terrains.js';
import * as C from './constants.js';
import * as A from './anim_ids.js';
import {
    F32, play_sound, play_terrain_sound, play_sound_if_no_flag, play_sound_and_spawn_particles,
    play_mario_landing_sound, play_mario_landing_sound_once, play_mario_heavy_landing_sound_once,
    adjust_sound_for_speed, is_anim_past_frame, is_anim_at_end, set_mario_animation, set_mario_anim_with_accel,
    mario_set_forward_vel, set_mario_action, set_jump_from_landing, set_jumping_action, drop_and_set_mario_action,
    mario_get_floor_class, mario_facing_downhill, mario_floor_is_slippery, mario_floor_is_slope,
    find_floor_slope, mario_drop_held_object, mario_check_object_grab, mario_grab_used_object,
    set_water_plunge_action, request_death, check_common_action_exits, play_mario_jump_sound,
} from './mario.js';
import {
    mario_bonk_reflection, mario_update_quicksand, mario_push_off_steep_floor, mario_update_moving_sand,
    mario_update_windy_ground, perform_ground_step,
} from './mario_step.js';
import { mario_update_punch_sequence } from './actions_object.js';

const {
    INPUT_NONZERO_ANALOG, INPUT_A_PRESSED, INPUT_OFF_FLOOR, INPUT_ABOVE_SLIDE, INPUT_FIRST_PERSON,
    INPUT_UNKNOWN_5, INPUT_SQUISHED, INPUT_A_DOWN, INPUT_IN_WATER, INPUT_STOMPED,
    INPUT_B_PRESSED, INPUT_Z_DOWN, INPUT_Z_PRESSED,
    GROUND_STEP_LEFT_GROUND, GROUND_STEP_NONE, GROUND_STEP_HIT_WALL,
} = C;

function LandingAction(numFrames, unk02, verySteepAction, endAction, aPressedAction, offFloorAction, slideAction) {
    return { numFrames, unk02, verySteepAction, endAction, aPressedAction, offFloorAction, slideAction };
}

const sJumpLandAction = LandingAction(
    4, 5, C.ACT_FREEFALL, C.ACT_JUMP_LAND_STOP, C.ACT_DOUBLE_JUMP, C.ACT_FREEFALL, C.ACT_BEGIN_SLIDING);

const sFreefallLandAction = LandingAction(
    4, 5, C.ACT_FREEFALL, C.ACT_FREEFALL_LAND_STOP, C.ACT_DOUBLE_JUMP, C.ACT_FREEFALL, C.ACT_BEGIN_SLIDING);

const sSideFlipLandAction = LandingAction(
    4, 5, C.ACT_FREEFALL, C.ACT_SIDE_FLIP_LAND_STOP, C.ACT_DOUBLE_JUMP, C.ACT_FREEFALL, C.ACT_BEGIN_SLIDING);

const sLongJumpLandAction = LandingAction(
    6, 5, C.ACT_FREEFALL, C.ACT_LONG_JUMP_LAND_STOP, C.ACT_LONG_JUMP, C.ACT_FREEFALL, C.ACT_BEGIN_SLIDING);

const sDoubleJumpLandAction = LandingAction(
    4, 5, C.ACT_FREEFALL, C.ACT_DOUBLE_JUMP_LAND_STOP, C.ACT_JUMP, C.ACT_FREEFALL, C.ACT_BEGIN_SLIDING);

const sTripleJumpLandAction = LandingAction(
    4, 0, C.ACT_FREEFALL, C.ACT_TRIPLE_JUMP_LAND_STOP, C.ACT_UNINITIALIZED, C.ACT_FREEFALL, C.ACT_BEGIN_SLIDING);

const sBackflipLandAction = LandingAction(
    4, 0, C.ACT_FREEFALL, C.ACT_BACKFLIP_LAND_STOP, C.ACT_BACKFLIP, C.ACT_FREEFALL, C.ACT_BEGIN_SLIDING);

export function tilt_body_running(m) {
    let pitch = find_floor_slope(m, 0);
    pitch = s16(pitch * m.forwardVel / 40.0);
    return s16(-pitch);
}

export function play_step_sound(m, frame1, frame2) {
    if (is_anim_past_frame(m, frame1) || is_anim_past_frame(m, frame2)) {
        const animID = m.marioObj.header.gfx.animInfo.animID;
        if (m.flags & C.MARIO_METAL_CAP) {
            if (animID === A.MARIO_ANIM_TIPTOE) {
                play_sound_and_spawn_particles(m, 'SOUND_ACTION_METAL_STEP_TIPTOE', 0);
            } else {
                play_sound_and_spawn_particles(m, 'SOUND_ACTION_METAL_STEP', 0);
            }
        } else if (m.quicksandDepth > 50.0) {
            play_sound(m, 'SOUND_ACTION_QUICKSAND_STEP');
        } else if (animID === A.MARIO_ANIM_TIPTOE) {
            play_sound_and_spawn_particles(m, 'SOUND_ACTION_TERRAIN_STEP_TIPTOE', 0);
        } else {
            play_sound_and_spawn_particles(m, 'SOUND_ACTION_TERRAIN_STEP', 0);
        }
    }
}

export function align_with_floor(m) {
    m.pos[1] = m.floorHeight;
    if (!m.floorAlignMatrix) {
        m.floorAlignMatrix = mtxf_new();
    }
    mtxf_align_terrain_triangle(m.floorAlignMatrix, m.pos, m.faceAngle[1], 40.0,
        (x, y, z) => m.world.find_floor(x, y, z).height);
    m.marioObj.header.gfx.throwMatrix = m.floorAlignMatrix;
}

export function begin_walking_action(m, forwardVel, action, actionArg) {
    m.faceAngle[1] = m.intendedYaw;
    mario_set_forward_vel(m, forwardVel);
    return set_mario_action(m, action, actionArg);
}

export function check_ledge_climb_down(m) {
    if (m.forwardVel < 10.0) {
        const wallCols = { x: m.pos[0], y: m.pos[1], z: m.pos[2], radius: 10.0, offsetY: -10.0, numWalls: 0, walls: [null, null, null, null] };

        if (m.world.find_wall_collisions(wallCols) !== 0) {
            const f = m.world.find_floor(wallCols.x, wallCols.y, wallCols.z);
            const floorHeight = f.height;
            if (f.surface !== null && (wallCols.y - floorHeight > 160.0)) {
                const wall = wallCols.walls[wallCols.numWalls - 1];
                const wallAngle = atan2s(wall.normal.z, wall.normal.x);
                const wallDYaw = s16(wallAngle - m.faceAngle[1]);

                if (wallDYaw > -0x4000 && wallDYaw < 0x4000) {
                    m.pos[0] = wallCols.x - 20.0 * wall.normal.x;
                    m.pos[2] = wallCols.z - 20.0 * wall.normal.z;

                    m.faceAngle[0] = 0;
                    m.faceAngle[1] = s16(wallAngle + 0x8000);

                    set_mario_action(m, C.ACT_LEDGE_CLIMB_DOWN, 0);
                    set_mario_animation(m, A.MARIO_ANIM_CLIMB_DOWN_LEDGE);
                }
            }
        }
    }
}

export function slide_bonk(m, fastAction, slowAction) {
    if (m.forwardVel > 16.0) {
        mario_bonk_reflection(m, true);
        drop_and_set_mario_action(m, fastAction, 0);
    } else {
        mario_set_forward_vel(m, 0.0);
        set_mario_action(m, slowAction, 0);
    }
}

export function set_triple_jump_action(m, _action, _actionArg) {
    if (m.flags & C.MARIO_WING_CAP) {
        return set_mario_action(m, C.ACT_FLYING_TRIPLE_JUMP, 0);
    } else if (m.forwardVel > 20.0) {
        return set_mario_action(m, C.ACT_TRIPLE_JUMP, 0);
    } else {
        return set_mario_action(m, C.ACT_JUMP, 0);
    }
}

export function update_sliding_angle(m, accel, lossFactor) {
    const floor = m.floor;
    const slopeAngle = atan2s(floor.normal.z, floor.normal.x);
    const steepness = Math.sqrt(floor.normal.x * floor.normal.x + floor.normal.z * floor.normal.z);

    m.slideVelX += accel * steepness * sins(slopeAngle);
    m.slideVelZ += accel * steepness * coss(slopeAngle);

    m.slideVelX *= lossFactor;
    m.slideVelZ *= lossFactor;

    m.slideYaw = atan2s(m.slideVelZ, m.slideVelX);

    const facingDYaw = s16(m.faceAngle[1] - m.slideYaw);
    let newFacingDYaw = facingDYaw;

    //! -0x4000 not handled - can slide down a slope while facing perpendicular to it
    if (newFacingDYaw > 0 && newFacingDYaw <= 0x4000) {
        if ((newFacingDYaw -= 0x200) < 0) {
            newFacingDYaw = 0;
        }
    } else if (newFacingDYaw > -0x4000 && newFacingDYaw < 0) {
        if ((newFacingDYaw += 0x200) > 0) {
            newFacingDYaw = 0;
        }
    } else if (newFacingDYaw > 0x4000 && newFacingDYaw < 0x8000) {
        if ((newFacingDYaw += 0x200) > 0x8000) {
            newFacingDYaw = 0x8000;
        }
    } else if (newFacingDYaw > -0x8000 && newFacingDYaw < -0x4000) {
        if ((newFacingDYaw -= 0x200) < -0x8000) {
            newFacingDYaw = -0x8000;
        }
    }

    m.faceAngle[1] = s16(m.slideYaw + newFacingDYaw);

    m.vel[0] = m.slideVelX;
    m.vel[1] = 0.0;
    m.vel[2] = m.slideVelZ;

    mario_update_moving_sand(m);
    mario_update_windy_ground(m);

    //! Speed is capped a frame late (butt slide HSG)
    m.forwardVel = Math.sqrt(m.slideVelX * m.slideVelX + m.slideVelZ * m.slideVelZ);
    if (m.forwardVel > 100.0) {
        m.slideVelX = m.slideVelX * 100.0 / m.forwardVel;
        m.slideVelZ = m.slideVelZ * 100.0 / m.forwardVel;
    }

    if (newFacingDYaw < -0x4000 || newFacingDYaw > 0x4000) {
        m.forwardVel *= -1.0;
    }
}

export function update_sliding(m, stopSpeed) {
    let lossFactor;
    let accel;
    let stopped = false;

    const intendedDYaw = s16(m.intendedYaw - m.slideYaw);
    let forward = coss(intendedDYaw);
    const sideward = sins(intendedDYaw);

    //! 10k glitch
    if (forward < 0.0 && m.forwardVel >= 0.0) {
        forward *= 0.5 + 0.5 * m.forwardVel / 100.0;
    }

    switch (mario_get_floor_class(m)) {
        case S.SURFACE_CLASS_VERY_SLIPPERY:
            accel = 10.0;
            lossFactor = m.intendedMag / 32.0 * forward * 0.02 + 0.98;
            break;

        case S.SURFACE_CLASS_SLIPPERY:
            accel = 8.0;
            lossFactor = m.intendedMag / 32.0 * forward * 0.02 + 0.96;
            break;

        default:
            accel = 7.0;
            lossFactor = m.intendedMag / 32.0 * forward * 0.02 + 0.92;
            break;

        case S.SURFACE_CLASS_NOT_SLIPPERY:
            accel = 5.0;
            lossFactor = m.intendedMag / 32.0 * forward * 0.02 + 0.92;
            break;
    }

    const oldSpeed = Math.sqrt(m.slideVelX * m.slideVelX + m.slideVelZ * m.slideVelZ);

    //! This is attempting to use trig derivatives to rotate Mario's speed.
    // It is slightly off/asymmetric since it uses the new X speed, but the old
    // Z speed.
    m.slideVelX += m.slideVelZ * (m.intendedMag / 32.0) * sideward * 0.05;
    m.slideVelZ -= m.slideVelX * (m.intendedMag / 32.0) * sideward * 0.05;

    const newSpeed = Math.sqrt(m.slideVelX * m.slideVelX + m.slideVelZ * m.slideVelZ);

    if (oldSpeed > 0.0 && newSpeed > 0.0) {
        m.slideVelX = m.slideVelX * oldSpeed / newSpeed;
        m.slideVelZ = m.slideVelZ * oldSpeed / newSpeed;
    }

    update_sliding_angle(m, accel, lossFactor);

    if (!mario_floor_is_slope(m) && m.forwardVel * m.forwardVel < stopSpeed * stopSpeed) {
        mario_set_forward_vel(m, 0.0);
        stopped = true;
    }

    return stopped;
}

export function apply_slope_accel(m) {
    let slopeAccel;

    const floor = m.floor;
    const steepness = Math.sqrt(floor.normal.x * floor.normal.x + floor.normal.z * floor.normal.z);

    const floorDYaw = s16(m.floorAngle - m.faceAngle[1]);

    if (mario_floor_is_slope(m)) {
        let slopeClass = 0;

        if (m.action !== C.ACT_SOFT_BACKWARD_GROUND_KB && m.action !== C.ACT_SOFT_FORWARD_GROUND_KB) {
            slopeClass = mario_get_floor_class(m);
        }

        switch (slopeClass) {
            case S.SURFACE_CLASS_VERY_SLIPPERY:
                slopeAccel = 5.3;
                break;
            case S.SURFACE_CLASS_SLIPPERY:
                slopeAccel = 2.7;
                break;
            default:
                slopeAccel = 1.7;
                break;
            case S.SURFACE_CLASS_NOT_SLIPPERY:
                slopeAccel = 0.0;
                break;
        }

        if (floorDYaw > -0x4000 && floorDYaw < 0x4000) {
            m.forwardVel += slopeAccel * steepness;
        } else {
            m.forwardVel -= slopeAccel * steepness;
        }
    }

    m.slideYaw = m.faceAngle[1];

    m.slideVelX = m.forwardVel * sins(m.faceAngle[1]);
    m.slideVelZ = m.forwardVel * coss(m.faceAngle[1]);

    m.vel[0] = m.slideVelX;
    m.vel[1] = 0.0;
    m.vel[2] = m.slideVelZ;

    mario_update_moving_sand(m);
    mario_update_windy_ground(m);
}

export function apply_landing_accel(m, frictionFactor) {
    let stopped = false;

    apply_slope_accel(m);

    if (!mario_floor_is_slope(m)) {
        m.forwardVel *= frictionFactor;
        if (m.forwardVel * m.forwardVel < 1.0) {
            mario_set_forward_vel(m, 0.0);
            stopped = true;
        }
    }

    return stopped;
}

export function apply_slope_decel(m, decelCoef) {
    let decel;
    let stopped = false;

    switch (mario_get_floor_class(m)) {
        case S.SURFACE_CLASS_VERY_SLIPPERY:
            decel = decelCoef * 0.2;
            break;
        case S.SURFACE_CLASS_SLIPPERY:
            decel = decelCoef * 0.7;
            break;
        default:
            decel = decelCoef * 2.0;
            break;
        case S.SURFACE_CLASS_NOT_SLIPPERY:
            decel = decelCoef * 3.0;
            break;
    }

    if ((m.forwardVel = approach_f32(m.forwardVel, 0.0, decel, decel)) === 0.0) {
        stopped = true;
    }

    apply_slope_accel(m);
    return stopped;
}

export function update_decelerating_speed(m) {
    let stopped = false;

    if ((m.forwardVel = approach_f32(m.forwardVel, 0.0, 1.0, 1.0)) === 0.0) {
        stopped = true;
    }

    mario_set_forward_vel(m, m.forwardVel);
    mario_update_moving_sand(m);
    mario_update_windy_ground(m);

    return stopped;
}

export function update_walking_speed(m) {
    let maxTargetSpeed;
    let targetSpeed;

    if (m.floor !== null && m.floor.type === S.SURFACE_SLOW) {
        maxTargetSpeed = 24.0;
    } else {
        maxTargetSpeed = 32.0;
    }

    targetSpeed = m.intendedMag < maxTargetSpeed ? m.intendedMag : maxTargetSpeed;

    if (m.quicksandDepth > 10.0) {
        targetSpeed *= 6.25 / m.quicksandDepth;
    }

    if (m.forwardVel <= 0.0) {
        m.forwardVel += 1.1;
    } else if (m.forwardVel <= targetSpeed) {
        m.forwardVel += 1.1 - m.forwardVel / 43.0;
    } else if (m.floor.normal.y >= F32(0.95)) {
        m.forwardVel -= 1.0;
    }

    if (m.forwardVel > 48.0) {
        m.forwardVel = 48.0;
    }

    m.faceAngle[1] = s16(m.intendedYaw - approach_s32(s16(m.intendedYaw - m.faceAngle[1]), 0, 0x800, 0x800));
    apply_slope_accel(m);
}

export function should_begin_sliding(m) {
    if (m.input & INPUT_ABOVE_SLIDE) {
        const slideLevel = (m.area.terrainType & S.TERRAIN_MASK) === S.TERRAIN_SLIDE;
        const movingBackward = m.forwardVel <= -1.0;

        if (slideLevel || movingBackward || mario_facing_downhill(m, false)) {
            return true;
        }
    }

    return false;
}

export function analog_stick_held_back(m) {
    const intendedDYaw = s16(m.intendedYaw - m.faceAngle[1]);
    return intendedDYaw < -0x471C || intendedDYaw > 0x471C;
}

export function check_ground_dive_or_punch(m) {
    if (m.input & INPUT_B_PRESSED) {
        //! Speed kick (shoutouts to SimpleFlips)
        if (m.forwardVel >= 29.0 && m.controller.stickMag > 48.0) {
            m.vel[1] = 20.0;
            return set_mario_action(m, C.ACT_DIVE, 1);
        }

        return set_mario_action(m, C.ACT_MOVE_PUNCHING, 0);
    }

    return false;
}

export function begin_braking_action(m) {
    mario_drop_held_object(m);

    if (m.actionState === 1) {
        m.faceAngle[1] = s16(m.actionArg);
        return set_mario_action(m, C.ACT_STANDING_AGAINST_WALL, 0);
    }

    if (m.forwardVel >= 16.0 && m.floor.normal.y >= F32(0.17364818)) {
        return set_mario_action(m, C.ACT_BRAKING, 0);
    }

    return set_mario_action(m, C.ACT_DECELERATING, 0);
}

export function anim_and_audio_for_walk(m) {
    let val14;
    const marioObj = m.marioObj;
    let val0C = true;
    let targetPitch = 0;
    let val04;

    val04 = m.intendedMag > m.forwardVel ? m.intendedMag : m.forwardVel;

    if (val04 < 4.0) {
        val04 = 4.0;
    }

    if (m.quicksandDepth > 50.0) {
        val14 = s32(val04 / 4.0 * 0x10000);
        set_mario_anim_with_accel(m, A.MARIO_ANIM_MOVE_IN_QUICKSAND, val14);
        play_step_sound(m, 19, 93);
        m.actionTimer = 0;
    } else {
        while (val0C) {
            switch (m.actionTimer) {
                case 0:
                    if (val04 > 8.0) {
                        m.actionTimer = 2;
                    } else {
                        //! (Speed Crash) If Mario's speed is more than 2^17.
                        if ((val14 = s32(val04 / 4.0 * 0x10000)) < 0x1000) {
                            val14 = 0x1000;
                        }
                        set_mario_anim_with_accel(m, A.MARIO_ANIM_START_TIPTOE, val14);
                        play_step_sound(m, 7, 22);
                        if (is_anim_past_frame(m, 23)) {
                            m.actionTimer = 2;
                        }

                        val0C = false;
                    }
                    break;

                case 1:
                    if (val04 > 8.0) {
                        m.actionTimer = 2;
                    } else {
                        //! (Speed Crash) If Mario's speed is more than 2^17.
                        if ((val14 = s32(val04 * 0x10000)) < 0x1000) {
                            val14 = 0x1000;
                        }
                        set_mario_anim_with_accel(m, A.MARIO_ANIM_TIPTOE, val14);
                        play_step_sound(m, 14, 72);

                        val0C = false;
                    }
                    break;

                case 2:
                    if (val04 < 5.0) {
                        m.actionTimer = 1;
                    } else if (val04 > 22.0) {
                        m.actionTimer = 3;
                    } else {
                        //! (Speed Crash) If Mario's speed is more than 2^17.
                        val14 = s32(val04 / 4.0 * 0x10000);
                        set_mario_anim_with_accel(m, A.MARIO_ANIM_WALKING, val14);
                        play_step_sound(m, 10, 49);

                        val0C = false;
                    }
                    break;

                case 3:
                    if (val04 < 18.0) {
                        m.actionTimer = 2;
                    } else {
                        //! (Speed Crash) If Mario's speed is more than 2^17.
                        val14 = s32(val04 / 4.0 * 0x10000);
                        set_mario_anim_with_accel(m, A.MARIO_ANIM_RUNNING, val14);
                        play_step_sound(m, 9, 45);
                        targetPitch = tilt_body_running(m);

                        val0C = false;
                    }
                    break;

                default:
                    // (Unreachable in the original.)
                    m.actionTimer = 0;
                    break;
            }
        }
    }

    marioObj.oMarioWalkingPitch = s16(approach_s32(marioObj.oMarioWalkingPitch, targetPitch, 0x800, 0x800));
    marioObj.header.gfx.angle[0] = marioObj.oMarioWalkingPitch;
}

export function push_or_sidle_wall(m, startPos) {
    let wallAngle;
    let dWallAngle;
    const dx = m.pos[0] - startPos[0];
    const dz = m.pos[2] - startPos[2];
    const movedDistance = Math.sqrt(dx * dx + dz * dz);
    //! (Speed Crash) If a wall is after moving 16384 distance, this crashes.
    const val04 = s32(movedDistance * 2.0 * 0x10000);

    if (m.forwardVel > 6.0) {
        mario_set_forward_vel(m, 6.0);
    }

    if (m.wall !== null) {
        wallAngle = atan2s(m.wall.normal.z, m.wall.normal.x);
        dWallAngle = s16(wallAngle - m.faceAngle[1]);
    }

    if (m.wall === null || dWallAngle <= -0x71C8 || dWallAngle >= 0x71C8) {
        m.flags |= C.MARIO_UNKNOWN_31;
        set_mario_animation(m, A.MARIO_ANIM_PUSHING);
        play_step_sound(m, 6, 18);
    } else {
        if (dWallAngle < 0) {
            set_mario_anim_with_accel(m, A.MARIO_ANIM_SIDESTEP_RIGHT, val04);
        } else {
            set_mario_anim_with_accel(m, A.MARIO_ANIM_SIDESTEP_LEFT, val04);
        }

        if (m.marioObj.header.gfx.animInfo.animFrame < 20) {
            play_terrain_sound(m, 'SOUND_MOVING_TERRAIN_SLIDE');
            m.particleFlags |= C.PARTICLE_DUST;
        }

        m.actionState = 1;
        m.actionArg = (wallAngle + 0x8000) >>> 0;
        m.marioObj.header.gfx.angle[1] = s16(wallAngle + 0x8000);
        m.marioObj.header.gfx.angle[2] = find_floor_slope(m, 0x4000);
    }
}

export function tilt_body_walking(m, startYaw) {
    const val0C = m.marioBodyState;
    const animID = m.marioObj.header.gfx.animInfo.animID;

    if (animID === A.MARIO_ANIM_WALKING || animID === A.MARIO_ANIM_RUNNING) {
        const dYaw = s16(m.faceAngle[1] - startYaw);
        //! (Speed Crash) These casts can cause a crash if (dYaw * forwardVel / 12) or
        //! (forwardVel * 170) exceed or equal 2^31.
        let val02 = s16(-s16(dYaw * m.forwardVel / 12.0));
        let val00 = s16(m.forwardVel * 170.0);

        if (val02 > 0x1555) {
            val02 = 0x1555;
        }
        if (val02 < -0x1555) {
            val02 = -0x1555;
        }

        if (val00 > 0x1555) {
            val00 = 0x1555;
        }
        if (val00 < 0) {
            val00 = 0;
        }

        val0C.torsoAngle[2] = s16(approach_s32(val0C.torsoAngle[2], val02, 0x400, 0x400));
        val0C.torsoAngle[0] = s16(approach_s32(val0C.torsoAngle[0], val00, 0x400, 0x400));
    } else {
        val0C.torsoAngle[2] = 0;
        val0C.torsoAngle[0] = 0;
    }
}

export function act_walking(m) {
    const startPos = [0, 0, 0];
    const startYaw = m.faceAngle[1];

    mario_drop_held_object(m);

    if (should_begin_sliding(m)) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    if (m.input & INPUT_FIRST_PERSON) {
        return begin_braking_action(m);
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jump_from_landing(m);
    }

    if (check_ground_dive_or_punch(m)) {
        return true;
    }

    if (m.input & INPUT_UNKNOWN_5) {
        return begin_braking_action(m);
    }

    if (analog_stick_held_back(m) && m.forwardVel >= 16.0) {
        return set_mario_action(m, C.ACT_TURNING_AROUND, 0);
    }

    if (m.input & INPUT_Z_PRESSED) {
        return set_mario_action(m, C.ACT_CROUCH_SLIDE, 0);
    }

    m.actionState = 0;

    vec3f_copy(startPos, m.pos);
    update_walking_speed(m);

    switch (perform_ground_step(m)) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, C.ACT_FREEFALL, 0);
            set_mario_animation(m, A.MARIO_ANIM_GENERAL_FALL);
            break;

        case GROUND_STEP_NONE:
            anim_and_audio_for_walk(m);
            if (m.intendedMag - m.forwardVel > 16.0) {
                m.particleFlags |= C.PARTICLE_DUST;
            }
            break;

        case GROUND_STEP_HIT_WALL:
            push_or_sidle_wall(m, startPos);
            m.actionTimer = 0;
            break;
    }

    check_ledge_climb_down(m);
    tilt_body_walking(m, startYaw);
    return false;
}

export function act_move_punching(m) {
    if (should_begin_sliding(m)) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    if (m.actionState === 0 && (m.input & INPUT_A_DOWN)) {
        return set_mario_action(m, C.ACT_JUMP_KICK, 0);
    }

    m.actionState = 1;

    mario_update_punch_sequence(m);

    if (m.forwardVel >= 0.0) {
        apply_slope_decel(m, 0.5);
    } else {
        if ((m.forwardVel += 8.0) >= 0.0) {
            m.forwardVel = 0.0;
        }
        apply_slope_accel(m);
    }

    switch (perform_ground_step(m)) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, C.ACT_FREEFALL, 0);
            break;

        case GROUND_STEP_NONE:
            m.particleFlags |= C.PARTICLE_DUST;
            break;
    }

    return false;
}

export function act_turning_around(m) {
    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_SIDE_FLIP, 0);
    }

    if (m.input & INPUT_UNKNOWN_5) {
        return set_mario_action(m, C.ACT_BRAKING, 0);
    }

    if (!analog_stick_held_back(m)) {
        return set_mario_action(m, C.ACT_WALKING, 0);
    }

    if (apply_slope_decel(m, 2.0)) {
        return begin_walking_action(m, 8.0, C.ACT_FINISH_TURNING_AROUND, 0);
    }

    play_terrain_sound(m, 'SOUND_MOVING_TERRAIN_SLIDE');

    adjust_sound_for_speed(m);

    switch (perform_ground_step(m)) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, C.ACT_FREEFALL, 0);
            break;

        case GROUND_STEP_NONE:
            m.particleFlags |= C.PARTICLE_DUST;
            break;
    }

    if (m.forwardVel >= 18.0) {
        set_mario_animation(m, A.MARIO_ANIM_TURNING_PART1);
    } else {
        set_mario_animation(m, A.MARIO_ANIM_TURNING_PART2);
        if (is_anim_at_end(m)) {
            if (m.forwardVel > 0.0) {
                begin_walking_action(m, -m.forwardVel, C.ACT_WALKING, 0);
            } else {
                begin_walking_action(m, 8.0, C.ACT_WALKING, 0);
            }
        }
    }

    return false;
}

export function act_finish_turning_around(m) {
    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_SIDE_FLIP, 0);
    }

    update_walking_speed(m);
    set_mario_animation(m, A.MARIO_ANIM_TURNING_PART2);

    if (perform_ground_step(m) === GROUND_STEP_LEFT_GROUND) {
        set_mario_action(m, C.ACT_FREEFALL, 0);
    }

    if (is_anim_at_end(m)) {
        set_mario_action(m, C.ACT_WALKING, 0);
    }

    m.marioObj.header.gfx.angle[1] = s16(m.marioObj.header.gfx.angle[1] + 0x8000);
    return false;
}

export function act_braking(m) {
    if (!(m.input & INPUT_FIRST_PERSON)
        && (m.input & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED | INPUT_OFF_FLOOR | INPUT_ABOVE_SLIDE))) {
        return check_common_action_exits(m);
    }

    if (apply_slope_decel(m, 2.0)) {
        return set_mario_action(m, C.ACT_BRAKING_STOP, 0);
    }

    if (m.input & INPUT_B_PRESSED) {
        return set_mario_action(m, C.ACT_MOVE_PUNCHING, 0);
    }

    switch (perform_ground_step(m)) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, C.ACT_FREEFALL, 0);
            break;

        case GROUND_STEP_NONE:
            m.particleFlags |= C.PARTICLE_DUST;
            break;

        case GROUND_STEP_HIT_WALL:
            slide_bonk(m, C.ACT_BACKWARD_GROUND_KB, C.ACT_BRAKING_STOP);
            break;
    }

    play_terrain_sound(m, 'SOUND_MOVING_TERRAIN_SLIDE');
    adjust_sound_for_speed(m);
    set_mario_animation(m, A.MARIO_ANIM_SKID_ON_GROUND);
    return false;
}

export function act_decelerating(m) {
    let val0C;
    const slopeClass = mario_get_floor_class(m);

    if (!(m.input & INPUT_FIRST_PERSON)) {
        if (should_begin_sliding(m)) {
            return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
        }

        if (m.input & INPUT_A_PRESSED) {
            return set_jump_from_landing(m);
        }

        if (check_ground_dive_or_punch(m)) {
            return true;
        }

        if (m.input & INPUT_NONZERO_ANALOG) {
            return set_mario_action(m, C.ACT_WALKING, 0);
        }

        if (m.input & INPUT_Z_PRESSED) {
            return set_mario_action(m, C.ACT_CROUCH_SLIDE, 0);
        }
    }

    if (update_decelerating_speed(m)) {
        return set_mario_action(m, C.ACT_IDLE, 0);
    }

    switch (perform_ground_step(m)) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, C.ACT_FREEFALL, 0);
            break;

        case GROUND_STEP_HIT_WALL:
            if (slopeClass === S.SURFACE_CLASS_VERY_SLIPPERY) {
                mario_bonk_reflection(m, true);
            } else {
                mario_set_forward_vel(m, 0.0);
            }
            break;
    }

    if (slopeClass === S.SURFACE_CLASS_VERY_SLIPPERY) {
        set_mario_animation(m, A.MARIO_ANIM_IDLE_HEAD_LEFT);
        play_terrain_sound(m, 'SOUND_MOVING_TERRAIN_SLIDE');
        adjust_sound_for_speed(m);
        m.particleFlags |= C.PARTICLE_DUST;
    } else {
        // (Speed Crash) Crashes if speed exceeds 2^17.
        if ((val0C = s32(m.forwardVel / 4.0 * 0x10000)) < 0x1000) {
            val0C = 0x1000;
        }

        set_mario_anim_with_accel(m, A.MARIO_ANIM_WALKING, val0C);
        play_step_sound(m, 10, 49);
    }

    return false;
}

export function act_crawling(m) {
    if (should_begin_sliding(m)) {
        return set_mario_action(m, C.ACT_BEGIN_SLIDING, 0);
    }

    if (m.input & INPUT_FIRST_PERSON) {
        return set_mario_action(m, C.ACT_STOP_CRAWLING, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_JUMP, 0);
    }

    if (check_ground_dive_or_punch(m)) {
        return true;
    }

    if (m.input & INPUT_UNKNOWN_5) {
        return set_mario_action(m, C.ACT_STOP_CRAWLING, 0);
    }

    if (!(m.input & INPUT_Z_DOWN)) {
        return set_mario_action(m, C.ACT_STOP_CRAWLING, 0);
    }

    m.intendedMag *= 0.1;

    update_walking_speed(m);

    switch (perform_ground_step(m)) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, C.ACT_FREEFALL, 0);
            break;

        case GROUND_STEP_HIT_WALL:
            if (m.forwardVel > 10.0) {
                mario_set_forward_vel(m, 10.0);
            }
        //! Possibly unintended missing break
        // fallthrough
        case GROUND_STEP_NONE:
            align_with_floor(m);
            break;
    }

    const val04 = s32(m.intendedMag * 2.0 * 0x10000);
    set_mario_anim_with_accel(m, A.MARIO_ANIM_CRAWLING, val04);
    play_step_sound(m, 26, 79);
    return false;
}

export function act_burning_ground(m) {
    if (m.input & INPUT_A_PRESSED) {
        return set_mario_action(m, C.ACT_BURNING_JUMP, 0);
    }

    m.marioObj.oMarioBurnTimer += 2;
    if (m.marioObj.oMarioBurnTimer > 160) {
        return set_mario_action(m, C.ACT_WALKING, 0);
    }

    if (m.waterLevel - m.floorHeight > 50.0) {
        play_sound(m, 'SOUND_GENERAL_FLAME_OUT');
        return set_mario_action(m, C.ACT_WALKING, 0);
    }

    if (m.forwardVel < 8.0) {
        m.forwardVel = 8.0;
    }
    if (m.forwardVel > 48.0) {
        m.forwardVel = 48.0;
    }

    m.forwardVel = approach_f32(m.forwardVel, 32.0, 4.0, 1.0);

    if (m.input & INPUT_NONZERO_ANALOG) {
        m.faceAngle[1] = s16(m.intendedYaw - approach_s32(s16(m.intendedYaw - m.faceAngle[1]), 0, 0x600, 0x600));
    }

    apply_slope_accel(m);

    if (perform_ground_step(m) === GROUND_STEP_LEFT_GROUND) {
        set_mario_action(m, C.ACT_BURNING_FALL, 0);
    }

    set_mario_anim_with_accel(m, A.MARIO_ANIM_RUNNING, s32(m.forwardVel / 2.0 * 0x10000));
    play_step_sound(m, 9, 45);

    m.particleFlags |= C.PARTICLE_FIRE;
    play_sound(m, 'SOUND_MOVING_LAVA_BURN');

    m.health -= 10;
    if (m.health < 0x100) {
        // set_mario_action(m, ACT_STANDING_DEATH, 0);
        request_death(m, C.ACT_STANDING_DEATH);
    }

    m.marioBodyState.eyeState = C.MARIO_EYES_DEAD;
    return false;
}

export function tilt_body_butt_slide(m) {
    const intendedDYaw = s16(m.intendedYaw - m.faceAngle[1]);
    m.marioBodyState.torsoAngle[0] = s16(s32(5461.3335 * m.intendedMag / 32.0 * coss(intendedDYaw)));
    m.marioBodyState.torsoAngle[2] = s16(s32(-(5461.3335 * m.intendedMag / 32.0 * sins(intendedDYaw))));
}

export function common_slide_action(m, endAction, airAction, animation) {
    play_terrain_sound(m, 'SOUND_MOVING_TERRAIN_SLIDE');
    adjust_sound_for_speed(m);

    switch (perform_ground_step(m)) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, airAction, 0);
            if (m.forwardVel < -50.0 || 50.0 < m.forwardVel) {
                play_sound(m, 'SOUND_MARIO_HOOHOO');
            }
            break;

        case GROUND_STEP_NONE:
            set_mario_animation(m, animation);
            align_with_floor(m);
            m.particleFlags |= C.PARTICLE_DUST;
            break;

        case GROUND_STEP_HIT_WALL:
            if (!mario_floor_is_slippery(m)) {
                if (m.forwardVel > 16.0) {
                    m.particleFlags |= C.PARTICLE_VERTICAL_STAR;
                }
                slide_bonk(m, C.ACT_GROUND_BONK, endAction);
            } else if (m.wall !== null) {
                const wallAngle = atan2s(m.wall.normal.z, m.wall.normal.x);
                let slideSpeed = Math.sqrt(m.slideVelX * m.slideVelX + m.slideVelZ * m.slideVelZ);

                if ((slideSpeed *= 0.9) < 4.0) {
                    slideSpeed = 4.0;
                }

                m.slideYaw = s16(wallAngle - s16(m.slideYaw - wallAngle) + 0x8000);

                m.vel[0] = m.slideVelX = slideSpeed * sins(m.slideYaw);
                m.vel[2] = m.slideVelZ = slideSpeed * coss(m.slideYaw);
            }

            align_with_floor(m);
            break;
    }
}

export function common_slide_action_with_jump(m, stopAction, jumpAction, airAction, animation) {
    if (m.actionTimer === 5) {
        if (m.input & INPUT_A_PRESSED) {
            return set_jumping_action(m, jumpAction, 0);
        }
    } else {
        m.actionTimer++;
    }

    if (update_sliding(m, 4.0)) {
        return set_mario_action(m, stopAction, 0);
    }

    common_slide_action(m, stopAction, airAction, animation);
    return false;
}

export function act_butt_slide(m) {
    const cancel = common_slide_action_with_jump(m, C.ACT_BUTT_SLIDE_STOP, C.ACT_JUMP, C.ACT_BUTT_SLIDE_AIR,
        A.MARIO_ANIM_SLIDE);
    tilt_body_butt_slide(m);
    return cancel;
}

export function act_crouch_slide(m) {
    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, C.ACT_BUTT_SLIDE, 0);
    }

    if (m.actionTimer < 30) {
        m.actionTimer++;
        if (m.input & INPUT_A_PRESSED) {
            if (m.forwardVel > 10.0) {
                return set_jumping_action(m, C.ACT_LONG_JUMP, 0);
            }
        }
    }

    if (m.input & INPUT_B_PRESSED) {
        if (m.forwardVel >= 10.0) {
            return set_mario_action(m, C.ACT_SLIDE_KICK, 0);
        } else {
            return set_mario_action(m, C.ACT_MOVE_PUNCHING, 0x0009);
        }
    }

    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_JUMP, 0);
    }

    if (m.input & INPUT_FIRST_PERSON) {
        return set_mario_action(m, C.ACT_BRAKING, 0);
    }

    return common_slide_action_with_jump(m, C.ACT_CROUCHING, C.ACT_JUMP, C.ACT_FREEFALL,
        A.MARIO_ANIM_START_CROUCHING);
}

export function act_slide_kick_slide(m) {
    if (m.input & INPUT_A_PRESSED) {
        return set_jumping_action(m, C.ACT_FORWARD_ROLLOUT, 0);
    }

    set_mario_animation(m, A.MARIO_ANIM_SLIDE_KICK);
    if (is_anim_at_end(m) && m.forwardVel < 1.0) {
        return set_mario_action(m, C.ACT_SLIDE_KICK_SLIDE_STOP, 0);
    }

    update_sliding(m, 1.0);
    switch (perform_ground_step(m)) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, C.ACT_FREEFALL, 2);
            break;

        case GROUND_STEP_HIT_WALL:
            mario_bonk_reflection(m, true);
            m.particleFlags |= C.PARTICLE_VERTICAL_STAR;
            set_mario_action(m, C.ACT_BACKWARD_GROUND_KB, 0);
            break;
    }

    play_terrain_sound(m, 'SOUND_MOVING_TERRAIN_SLIDE');
    m.particleFlags |= C.PARTICLE_DUST;
    return false;
}

export function stomach_slide_action(m, stopAction, airAction, animation) {
    if (m.actionTimer === 5) {
        if (!(m.input & INPUT_ABOVE_SLIDE) && (m.input & (INPUT_A_PRESSED | INPUT_B_PRESSED))) {
            return drop_and_set_mario_action(
                m, m.forwardVel >= 0.0 ? C.ACT_FORWARD_ROLLOUT : C.ACT_BACKWARD_ROLLOUT, 0);
        }
    } else {
        m.actionTimer++;
    }

    if (update_sliding(m, 4.0)) {
        return set_mario_action(m, stopAction, 0);
    }

    common_slide_action(m, stopAction, airAction, animation);
    return false;
}

export function act_stomach_slide(m) {
    return stomach_slide_action(m, C.ACT_STOMACH_SLIDE_STOP, C.ACT_FREEFALL, A.MARIO_ANIM_SLIDE_DIVE);
}

export function act_dive_slide(m) {
    if (!(m.input & INPUT_ABOVE_SLIDE) && (m.input & (INPUT_A_PRESSED | INPUT_B_PRESSED))) {
        return set_mario_action(m, m.forwardVel > 0.0 ? C.ACT_FORWARD_ROLLOUT : C.ACT_BACKWARD_ROLLOUT, 0);
    }

    play_mario_landing_sound_once(m, 'SOUND_ACTION_TERRAIN_BODY_HIT_GROUND');

    //! If the dive slide ends on the same frame that we pick up on object,
    // Mario will not be in the dive slide action for the call to
    // mario_check_object_grab.
    if (update_sliding(m, 8.0) && is_anim_at_end(m)) {
        mario_set_forward_vel(m, 0.0);
        set_mario_action(m, C.ACT_STOMACH_SLIDE_STOP, 0);
    }

    if (mario_check_object_grab(m)) {
        mario_grab_used_object(m);
        m.marioBodyState.grabPos = C.GRAB_POS_LIGHT_OBJ;
        return true;
    }

    common_slide_action(m, C.ACT_STOMACH_SLIDE_STOP, C.ACT_FREEFALL, A.MARIO_ANIM_DIVE);
    return false;
}

export function common_ground_knockback_action(m, animation, arg2, arg3, arg4) {
    if (arg3) {
        play_mario_heavy_landing_sound_once(m, 'SOUND_ACTION_TERRAIN_BODY_HIT_GROUND');
    }

    if (arg4 > 0) {
        play_sound_if_no_flag(m, 'SOUND_MARIO_ATTACKED', C.MARIO_MARIO_SOUND_PLAYED);
    } else {
        play_sound_if_no_flag(m, 'SOUND_MARIO_OOOF2', C.MARIO_MARIO_SOUND_PLAYED);
    }

    if (m.forwardVel > 32.0) {
        m.forwardVel = 32.0;
    }
    if (m.forwardVel < -32.0) {
        m.forwardVel = -32.0;
    }

    const animFrame = set_mario_animation(m, animation);
    if (animFrame < arg2) {
        apply_landing_accel(m, 0.9);
    } else if (m.forwardVel >= 0.0) {
        mario_set_forward_vel(m, 0.1);
    } else {
        mario_set_forward_vel(m, -0.1);
    }

    if (perform_ground_step(m) === GROUND_STEP_LEFT_GROUND) {
        if (m.forwardVel >= 0.0) {
            set_mario_action(m, C.ACT_FORWARD_AIR_KB, arg4);
        } else {
            set_mario_action(m, C.ACT_BACKWARD_AIR_KB, arg4);
        }
    } else if (is_anim_at_end(m)) {
        if (m.health < 0x100) {
            // set_mario_action(m, ACT_STANDING_DEATH, 0);
            request_death(m, C.ACT_STANDING_DEATH);
        } else {
            if (arg4 > 0) {
                m.invincTimer = 30;
            }
            set_mario_action(m, C.ACT_IDLE, 0);
        }
    }

    return animFrame;
}

export function act_hard_backward_ground_kb(m) {
    const animFrame = common_ground_knockback_action(m, A.MARIO_ANIM_FALL_OVER_BACKWARDS, 43, true, m.actionArg);
    if (animFrame === 43 && m.health < 0x100) {
        // set_mario_action(m, ACT_DEATH_ON_BACK, 0);
        request_death(m, C.ACT_DEATH_ON_BACK);
    }

    if (animFrame === 69) {
        play_mario_landing_sound_once(m, 'SOUND_ACTION_TERRAIN_LANDING');
    }

    return false;
}

export function act_hard_forward_ground_kb(m) {
    const animFrame = common_ground_knockback_action(m, A.MARIO_ANIM_LAND_ON_STOMACH, 21, true, m.actionArg);
    if (animFrame === 23 && m.health < 0x100) {
        // set_mario_action(m, ACT_DEATH_ON_STOMACH, 0);
        request_death(m, C.ACT_DEATH_ON_STOMACH);
    }

    return false;
}

export function act_backward_ground_kb(m) {
    common_ground_knockback_action(m, A.MARIO_ANIM_BACKWARD_KB, 22, true, m.actionArg);
    return false;
}

export function act_forward_ground_kb(m) {
    common_ground_knockback_action(m, A.MARIO_ANIM_FORWARD_KB, 20, true, m.actionArg);
    return false;
}

export function act_soft_backward_ground_kb(m) {
    common_ground_knockback_action(m, A.MARIO_ANIM_SOFT_BACK_KB, 100, false, m.actionArg);
    return false;
}

export function act_soft_forward_ground_kb(m) {
    common_ground_knockback_action(m, A.MARIO_ANIM_SOFT_FRONT_KB, 100, false, m.actionArg);
    return false;
}

export function act_ground_bonk(m) {
    const animFrame = common_ground_knockback_action(m, A.MARIO_ANIM_GROUND_BONK, 32, true, m.actionArg);
    if (animFrame === 32) {
        play_mario_landing_sound(m, 'SOUND_ACTION_TERRAIN_LANDING');
    }
    return false;
}

export function common_landing_action(m, animation, airAction) {
    if (m.input & INPUT_NONZERO_ANALOG) {
        apply_landing_accel(m, 0.98);
    } else if (m.forwardVel >= 16.0) {
        apply_slope_decel(m, 2.0);
    } else {
        m.vel[1] = 0.0;
    }

    const stepResult = perform_ground_step(m);
    switch (stepResult) {
        case GROUND_STEP_LEFT_GROUND:
            set_mario_action(m, airAction, 0);
            break;

        case GROUND_STEP_HIT_WALL:
            set_mario_animation(m, A.MARIO_ANIM_PUSHING);
            break;
    }

    if (m.forwardVel > 16.0) {
        m.particleFlags |= C.PARTICLE_DUST;
    }

    set_mario_animation(m, animation);
    play_mario_landing_sound_once(m, 'SOUND_ACTION_TERRAIN_LANDING');

    if (m.floor.type >= S.SURFACE_SHALLOW_QUICKSAND && m.floor.type <= S.SURFACE_MOVING_QUICKSAND) {
        m.quicksandDepth += (4 - m.actionTimer) * 3.5 - 0.5;
    }

    return stepResult;
}

export function common_landing_cancels(m, landingAction, setAPressAction) {
    //! Everything here, including floor steepness, is checked before checking
    // if Mario is actually on the floor. This leads to e.g. remote sliding.

    if (m.floor.normal.y < F32(0.2923717)) {
        return mario_push_off_steep_floor(m, landingAction.verySteepAction, 0);
    }

    m.doubleJumpTimer = landingAction.unk02;

    if (should_begin_sliding(m)) {
        return set_mario_action(m, landingAction.slideAction, 0);
    }

    if (m.input & INPUT_FIRST_PERSON) {
        return set_mario_action(m, landingAction.endAction, 0);
    }

    if (++m.actionTimer >= landingAction.numFrames) {
        return set_mario_action(m, landingAction.endAction, 0);
    }

    if (m.input & INPUT_A_PRESSED) {
        return setAPressAction(m, landingAction.aPressedAction, 0);
    }

    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, landingAction.offFloorAction, 0);
    }

    return false;
}

export function act_jump_land(m) {
    if (common_landing_cancels(m, sJumpLandAction, set_jumping_action)) {
        return true;
    }

    common_landing_action(m, A.MARIO_ANIM_LAND_FROM_SINGLE_JUMP, C.ACT_FREEFALL);
    return false;
}

export function act_freefall_land(m) {
    if (common_landing_cancels(m, sFreefallLandAction, set_jumping_action)) {
        return true;
    }

    common_landing_action(m, A.MARIO_ANIM_GENERAL_LAND, C.ACT_FREEFALL);
    return false;
}

export function act_side_flip_land(m) {
    if (common_landing_cancels(m, sSideFlipLandAction, set_jumping_action)) {
        return true;
    }

    if (common_landing_action(m, A.MARIO_ANIM_SLIDEFLIP_LAND, C.ACT_FREEFALL) !== GROUND_STEP_HIT_WALL) {
        m.marioObj.header.gfx.angle[1] = s16(m.marioObj.header.gfx.angle[1] + 0x8000);
    }
    return false;
}

export function act_long_jump_land(m) {
    if (!(m.input & INPUT_Z_DOWN)) {
        m.input &= ~INPUT_A_PRESSED;
    }

    if (common_landing_cancels(m, sLongJumpLandAction, set_jumping_action)) {
        return true;
    }

    if (!(m.input & INPUT_NONZERO_ANALOG)) {
        play_sound_if_no_flag(m, 'SOUND_MARIO_UH2_2', C.MARIO_MARIO_SOUND_PLAYED);
    }

    common_landing_action(m,
        !m.marioObj.oMarioLongJumpIsSlow ? A.MARIO_ANIM_CROUCH_FROM_FAST_LONGJUMP
            : A.MARIO_ANIM_CROUCH_FROM_SLOW_LONGJUMP,
        C.ACT_FREEFALL);
    return false;
}

export function act_double_jump_land(m) {
    if (common_landing_cancels(m, sDoubleJumpLandAction, set_triple_jump_action)) {
        return true;
    }
    common_landing_action(m, A.MARIO_ANIM_LAND_FROM_DOUBLE_JUMP, C.ACT_FREEFALL);
    return false;
}

export function act_triple_jump_land(m) {
    m.input &= ~INPUT_A_PRESSED;

    if (common_landing_cancels(m, sTripleJumpLandAction, set_jumping_action)) {
        return true;
    }

    if (!(m.input & INPUT_NONZERO_ANALOG)) {
        play_sound_if_no_flag(m, 'SOUND_MARIO_HAHA', C.MARIO_MARIO_SOUND_PLAYED);
    }

    common_landing_action(m, A.MARIO_ANIM_TRIPLE_JUMP_LAND, C.ACT_FREEFALL);
    return false;
}

export function act_backflip_land(m) {
    if (!(m.input & INPUT_Z_DOWN)) {
        m.input &= ~INPUT_A_PRESSED;
    }

    if (common_landing_cancels(m, sBackflipLandAction, set_jumping_action)) {
        return true;
    }

    if (!(m.input & INPUT_NONZERO_ANALOG)) {
        play_sound_if_no_flag(m, 'SOUND_MARIO_HAHA', C.MARIO_MARIO_SOUND_PLAYED);
    }

    common_landing_action(m, A.MARIO_ANIM_TRIPLE_JUMP_LAND, C.ACT_FREEFALL);
    return false;
}

export function quicksand_jump_land_action(m, animation1, animation2, endAction, airAction) {
    if (m.actionTimer++ < 6) {
        m.quicksandDepth -= (7 - m.actionTimer) * 0.8;
        if (m.quicksandDepth < 1.0) {
            m.quicksandDepth = 1.1;
        }

        play_mario_jump_sound(m);
        set_mario_animation(m, animation1);
    } else {
        if (m.actionTimer >= 13) {
            return set_mario_action(m, endAction, 0);
        }

        set_mario_animation(m, animation2);
    }

    apply_landing_accel(m, 0.95);
    if (perform_ground_step(m) === GROUND_STEP_LEFT_GROUND) {
        set_mario_action(m, airAction, 0);
    }

    return false;
}

export function act_quicksand_jump_land(m) {
    return quicksand_jump_land_action(m, A.MARIO_ANIM_SINGLE_JUMP, A.MARIO_ANIM_LAND_FROM_SINGLE_JUMP,
        C.ACT_JUMP_LAND_STOP, C.ACT_FREEFALL);
}

export function check_common_moving_cancels(m) {
    if (m.pos[1] < m.waterLevel - 100) {
        return set_water_plunge_action(m);
    }

    // (INPUT_STOMPED / INPUT_SQUISHED come from objects: never set.)
    if (!(m.action & C.ACT_FLAG_INVULNERABLE) && (m.input & INPUT_STOMPED)) {
        return drop_and_set_mario_action(m, C.ACT_SHOCKWAVE_BOUNCE, 0);
    }

    if (!(m.action & C.ACT_FLAG_INVULNERABLE)) {
        if (m.health < 0x100) {
            // return drop_and_set_mario_action(m, ACT_STANDING_DEATH, 0);
            request_death(m, C.ACT_STANDING_DEATH);
        }
    }

    return false;
}

export function mario_execute_moving_action(m) {
    let cancel;

    if (check_common_moving_cancels(m)) {
        return true;
    }

    if (mario_update_quicksand(m, 0.25)) {
        return true;
    }

    /* clang-format off */
    switch (m.action) {
        case C.ACT_WALKING:                  cancel = act_walking(m);                  break;
        case C.ACT_TURNING_AROUND:           cancel = act_turning_around(m);           break;
        case C.ACT_FINISH_TURNING_AROUND:    cancel = act_finish_turning_around(m);    break;
        case C.ACT_BRAKING:                  cancel = act_braking(m);                  break;
        case C.ACT_CRAWLING:                 cancel = act_crawling(m);                 break;
        case C.ACT_BURNING_GROUND:           cancel = act_burning_ground(m);           break;
        case C.ACT_DECELERATING:             cancel = act_decelerating(m);             break;
        case C.ACT_BUTT_SLIDE:               cancel = act_butt_slide(m);               break;
        case C.ACT_STOMACH_SLIDE:            cancel = act_stomach_slide(m);            break;
        case C.ACT_DIVE_SLIDE:               cancel = act_dive_slide(m);               break;
        case C.ACT_MOVE_PUNCHING:            cancel = act_move_punching(m);            break;
        case C.ACT_CROUCH_SLIDE:             cancel = act_crouch_slide(m);             break;
        case C.ACT_SLIDE_KICK_SLIDE:         cancel = act_slide_kick_slide(m);         break;
        case C.ACT_HARD_BACKWARD_GROUND_KB:  cancel = act_hard_backward_ground_kb(m);  break;
        case C.ACT_HARD_FORWARD_GROUND_KB:   cancel = act_hard_forward_ground_kb(m);   break;
        case C.ACT_BACKWARD_GROUND_KB:       cancel = act_backward_ground_kb(m);       break;
        case C.ACT_FORWARD_GROUND_KB:        cancel = act_forward_ground_kb(m);        break;
        case C.ACT_SOFT_BACKWARD_GROUND_KB:  cancel = act_soft_backward_ground_kb(m);  break;
        case C.ACT_SOFT_FORWARD_GROUND_KB:   cancel = act_soft_forward_ground_kb(m);   break;
        case C.ACT_GROUND_BONK:              cancel = act_ground_bonk(m);              break;
        case C.ACT_JUMP_LAND:                cancel = act_jump_land(m);                break;
        case C.ACT_FREEFALL_LAND:            cancel = act_freefall_land(m);            break;
        case C.ACT_DOUBLE_JUMP_LAND:         cancel = act_double_jump_land(m);         break;
        case C.ACT_SIDE_FLIP_LAND:           cancel = act_side_flip_land(m);           break;
        case C.ACT_TRIPLE_JUMP_LAND:         cancel = act_triple_jump_land(m);         break;
        case C.ACT_BACKFLIP_LAND:            cancel = act_backflip_land(m);            break;
        case C.ACT_QUICKSAND_JUMP_LAND:      cancel = act_quicksand_jump_land(m);      break;
        case C.ACT_LONG_JUMP_LAND:           cancel = act_long_jump_land(m);           break;
        default:
            // Not ported (object holding / shell riding): fall back to walking.
            cancel = set_mario_action(m, C.ACT_WALKING, 0);
            break;
    }
    /* clang-format on */

    if (!cancel && (m.input & INPUT_IN_WATER)) {
        m.particleFlags |= C.PARTICLE_WAVE_TRAIL;
        m.particleFlags &= ~C.PARTICLE_DUST;
    }

    return cancel;
}
