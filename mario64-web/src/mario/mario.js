// Port of src/game/mario.c (plus the few helpers from interaction.c,
// level_update.c and object code that Mario's movement needs).
//
// Naming: functions keep their original C names (snake_case). Out-pointer
// parameters of the original are replaced by return values.

import {
    s16, s32, sins, coss, atan2s, vec3f_copy, vec3f_set, vec3s_set, vec3s_copy,
} from '../engine/math_util.js';
import { ANIM_FLAG_2, ANIM_FLAG_BACKWARD } from '../engine/graph_node.js';
import { createWallCollisionData, SURFACE_FLAG_DYNAMIC } from '../engine/surface.js';
import * as S from '../engine/surface_terrains.js';
import * as C from './constants.js';
import { mario_execute_stationary_action } from './actions_stationary.js';
import { mario_execute_moving_action } from './actions_moving.js';
import { mario_execute_airborne_action } from './actions_airborne.js';
import { mario_execute_automatic_action } from './actions_automatic.js';
import { mario_execute_object_action } from './actions_object.js';

const {
    INPUT_NONZERO_ANALOG, INPUT_A_PRESSED, INPUT_OFF_FLOOR, INPUT_ABOVE_SLIDE, INPUT_FIRST_PERSON,
    INPUT_UNKNOWN_5, INPUT_SQUISHED, INPUT_A_DOWN, INPUT_IN_POISON_GAS, INPUT_IN_WATER,
    INPUT_B_PRESSED, INPUT_Z_DOWN, INPUT_Z_PRESSED,
    A_BUTTON, B_BUTTON, Z_TRIG,
    MARIO_METAL_CAP, MARIO_ACTION_SOUND_PLAYED, MARIO_MARIO_SOUND_PLAYED, MARIO_UNKNOWN_08, MARIO_UNKNOWN_18,
    MARIO_WING_CAP, MARIO_VANISH_CAP, MARIO_METAL_SHOCK, MARIO_CAP_IN_HAND, MARIO_CAP_ON_HEAD, MARIO_TELEPORTING,
    MARIO_UNKNOWN_25, MARIO_SPECIAL_CAPS, MARIO_CAPS,
    MODEL_STATE_NOISE_ALPHA, MODEL_STATE_METAL,
    PARTICLE_SHALLOW_WATER_SPLASH, PARTICLE_SHALLOW_WATER_WAVE, PARTICLE_DIRT, PARTICLE_SNOW,
    ACT_GROUP_MASK, ACT_GROUP_STATIONARY, ACT_GROUP_MOVING, ACT_GROUP_AIRBORNE, ACT_GROUP_SUBMERGED,
    ACT_GROUP_CUTSCENE, ACT_GROUP_AUTOMATIC, ACT_GROUP_OBJECT,
    ACT_FLAG_AIR, ACT_FLAG_SWIMMING, ACT_FLAG_INTANGIBLE, ACT_FLAG_SHORT_HITBOX,
    ACT_PUNCHING, ACT_MOVE_PUNCHING,
    ACT_CRAWLING, ACT_WALKING, ACT_HOLD_WALKING, ACT_BEGIN_SLIDING, ACT_BUTT_SLIDE, ACT_STOMACH_SLIDE,
    ACT_HOLD_BEGIN_SLIDING, ACT_HOLD_BUTT_SLIDE, ACT_HOLD_STOMACH_SLIDE,
    ACT_DOUBLE_JUMP, ACT_TWIRLING, ACT_JUMP, ACT_BACKFLIP, ACT_TRIPLE_JUMP, ACT_FLYING_TRIPLE_JUMP,
    ACT_WATER_JUMP, ACT_HOLD_WATER_JUMP, ACT_BURNING_JUMP, ACT_RIDING_SHELL_JUMP, ACT_HOLD_JUMP,
    ACT_WALL_KICK_AIR, ACT_TOP_OF_POLE_JUMP, ACT_SIDE_FLIP, ACT_STEEP_JUMP, ACT_LAVA_BOOST, ACT_DIVE,
    ACT_LONG_JUMP, ACT_SLIDE_KICK, ACT_JUMP_KICK,
    ACT_METAL_WATER_JUMP, ACT_HOLD_METAL_WATER_JUMP,
    ACT_QUICKSAND_JUMP_LAND,
    ACT_JUMP_LAND, ACT_FREEFALL_LAND, ACT_SIDE_FLIP_LAND_STOP, ACT_DOUBLE_JUMP_LAND,
    ACT_FREEFALL,
    ACT_FIRST_PERSON, ACT_SLEEPING,
} = C;

export const GRAPH_RENDER_INVISIBLE = 1 << 4;

// Sound terrain ids (include/sounds.h)
export const SOUND_TERRAIN_DEFAULT = 0;
export const SOUND_TERRAIN_GRASS = 1;
export const SOUND_TERRAIN_WATER = 2;
export const SOUND_TERRAIN_STONE = 3;
export const SOUND_TERRAIN_SPOOKY = 4;
export const SOUND_TERRAIN_SNOW = 5;
export const SOUND_TERRAIN_ICE = 6;
export const SOUND_TERRAIN_SAND = 7;

// f32 literals used for floor normal comparisons
export const F32 = Math.fround;

/**************************************************
 *                  SOUND / STUBS                 *
 **************************************************/

/**
 * Replacement for play_sound(). `name` is the original SOUND_* constant name.
 * `extra` may contain { terrain } (the SOUND_TERRAIN_* addend that the original
 * adds to terrain sound ids) and/or { variant } (random variant offset).
 */
export function play_sound(m, name, extra) {
    if (m.sound) {
        m.sound(name, extra);
    }
}

/** play_sound(SOUND_X + m->terrainSoundAddend, ...) */
export function play_terrain_sound(m, name) {
    play_sound(m, name, { terrain: m.terrainSoundAddend >>> 16 });
}

/** Replacement for gAudioRandom (only used to pick sound variants). */
function audio_random(m) {
    m.audioRandom = (Math.imul(m.audioRandom + 0x3C6EF35F, 0x19660D) + 1) >>> 0;
    return m.audioRandom >>> 8;
}

/** Stubbed: camera mode changes are owned by the camera port. */
export function set_camera_mode(_m, _mode, _frames) {}
/** Stubbed: camera shake. */
export function set_camera_shake_from_hit(_m, _shake) {}

/** Objects do not exist in this port: holding/riding/grabbing are no-ops. */
export function mario_stop_riding_and_holding(_m) {}
export function mario_drop_held_object(_m) {}
export function mario_throw_held_object(_m) {}
export function mario_stop_riding_object(_m) {}
export function mario_grab_used_object(_m) {}
export function mario_check_object_grab(_m) { return false; }
export function mario_blow_off_cap(_m, _speed) {}

export const WARP_OP_WARP_FLOOR = 0x13;
export const WARP_OP_DEATH = 0x12;

/**
 * level_trigger_warp replacement: any death / warp-floor warp just requests a
 * respawn from the game loop (once, like sDelayedWarpOp). Returns the fade
 * duration the original would return.
 */
export function level_trigger_warp(m, warpOp) {
    if (!m.requestRespawn) {
        m.invincTimer = -1;
        m.requestRespawn = true;
        m.respawnReason = warpOp === WARP_OP_DEATH ? 'death' : 'warp_floor';
        if (warpOp === WARP_OP_DEATH) {
            play_sound(m, 'SOUND_MENU_BOWSER_LAUGH');
            return 48;
        }
        return 20;
    }
    return 0;
}

/**
 * Called wherever the original enters a death action (ACT_STANDING_DEATH,
 * ACT_DEATH_ON_BACK, ACT_QUICKSAND_DEATH, ...). Death cutscenes are not ported;
 * we request a respawn instead and keep Mario in his current action.
 */
export function request_death(m, deathAction) {
    if (!m.requestRespawn) {
        m.requestRespawn = true;
        m.respawnReason = 'death';
        m.deathAction = deathAction;
    }
    return true;
}

/**************************************************
 *                    ANIMATIONS                  *
 **************************************************/

function get_anim(m, animID) {
    const a = m.animations ? m.animations[animID] : null;
    if (a) return a;
    // Fallback header (keeps logic running if an animation is missing).
    return { flags: 0, animYTransDivisor: 0, startFrame: 0, loopStart: 0, loopEnd: 1 };
}

/** Checks if Mario's animation has reached its end point. */
export function is_anim_at_end(m) {
    const ai = m.marioObj.header.gfx.animInfo;
    return (ai.animFrame + 1) === ai.curAnim.loopEnd;
}

/** Checks if Mario's animation has surpassed 2 frames before its end point. */
export function is_anim_past_end(m) {
    const ai = m.marioObj.header.gfx.animInfo;
    return ai.animFrame >= (ai.curAnim.loopEnd - 2);
}

/** Sets Mario's animation without any acceleration, running at its default rate. */
export function set_mario_animation(m, targetAnimID) {
    const ai = m.marioObj.header.gfx.animInfo;
    const targetAnim = get_anim(m, targetAnimID);

    if (ai.animID !== targetAnimID) {
        ai.animID = targetAnimID;
        ai.curAnim = targetAnim;
        ai.animAccel = 0;
        ai.animYTrans = m.unkB0;

        if (targetAnim.flags & ANIM_FLAG_2) {
            ai.animFrame = targetAnim.startFrame;
        } else {
            if (targetAnim.flags & ANIM_FLAG_BACKWARD) {
                ai.animFrame = s16(targetAnim.startFrame + 1);
            } else {
                ai.animFrame = s16(targetAnim.startFrame - 1);
            }
        }
    }

    return ai.animFrame;
}

/** Sets Mario's animation where the animation is sped up or slowed down via acceleration. */
export function set_mario_anim_with_accel(m, targetAnimID, accel) {
    const ai = m.marioObj.header.gfx.animInfo;
    const targetAnim = get_anim(m, targetAnimID);
    accel |= 0;

    if (ai.animID !== targetAnimID) {
        ai.animID = targetAnimID;
        ai.curAnim = targetAnim;
        ai.animYTrans = m.unkB0;

        if (targetAnim.flags & ANIM_FLAG_2) {
            ai.animFrameAccelAssist = (targetAnim.startFrame << 0x10) | 0;
        } else {
            if (targetAnim.flags & ANIM_FLAG_BACKWARD) {
                ai.animFrameAccelAssist = ((targetAnim.startFrame << 0x10) + accel) | 0;
            } else {
                ai.animFrameAccelAssist = ((targetAnim.startFrame << 0x10) - accel) | 0;
            }
        }

        ai.animFrame = s16(ai.animFrameAccelAssist >> 0x10);
    }

    ai.animAccel = accel;

    return ai.animFrame;
}

/** Sets the animation to a specific "next" frame from the frame given. */
export function set_anim_to_frame(m, animFrame) {
    const ai = m.marioObj.header.gfx.animInfo;
    const curAnim = ai.curAnim;

    if (ai.animAccel !== 0) {
        if (curAnim.flags & ANIM_FLAG_BACKWARD) {
            ai.animFrameAccelAssist = ((animFrame << 0x10) + ai.animAccel) | 0;
        } else {
            ai.animFrameAccelAssist = ((animFrame << 0x10) - ai.animAccel) | 0;
        }
    } else {
        if (curAnim.flags & ANIM_FLAG_BACKWARD) {
            ai.animFrame = s16(animFrame + 1);
        } else {
            ai.animFrame = s16(animFrame - 1);
        }
    }
}

export function is_anim_past_frame(m, animFrame) {
    let isPastFrame;
    const acceleratedFrame = (animFrame << 0x10) | 0;
    const ai = m.marioObj.header.gfx.animInfo;
    const curAnim = ai.curAnim;

    if (ai.animAccel !== 0) {
        if (curAnim.flags & ANIM_FLAG_BACKWARD) {
            isPastFrame = (ai.animFrameAccelAssist > acceleratedFrame)
                && (acceleratedFrame >= ((ai.animFrameAccelAssist - ai.animAccel) | 0));
        } else {
            isPastFrame = (ai.animFrameAccelAssist < acceleratedFrame)
                && (acceleratedFrame <= ((ai.animFrameAccelAssist + ai.animAccel) | 0));
        }
    } else {
        if (curAnim.flags & ANIM_FLAG_BACKWARD) {
            isPastFrame = (ai.animFrame === (animFrame + 1));
        } else {
            isPastFrame = ((ai.animFrame + 1) === animFrame);
        }
    }

    return isPastFrame;
}

/**************************************************
 *                      AUDIO                     *
 **************************************************/

/** Plays a sound if Mario doesn't have the flag being checked. */
export function play_sound_if_no_flag(m, soundName, flags, extra) {
    if (!(m.flags & flags)) {
        play_sound(m, soundName, extra);
        m.flags |= flags;
    }
}

/** Plays a jump sound if one has not been played since the last action change. */
export function play_mario_jump_sound(m) {
    if (!(m.flags & MARIO_MARIO_SOUND_PLAYED)) {
        if (m.action === ACT_TRIPLE_JUMP) {
            play_sound(m, 'SOUND_MARIO_YAHOO_WAHA_YIPPEE', { variant: audio_random(m) % 5 });
        } else {
            play_sound(m, 'SOUND_MARIO_YAH_WAH_HOO', { variant: audio_random(m) % 3 });
        }
        m.flags |= MARIO_MARIO_SOUND_PLAYED;
    }
}

/** Adjusts the volume/pitch of sounds from Mario's speed (stubbed: exposed as a field). */
export function adjust_sound_for_speed(m) {
    const absForwardVel = s32(m.forwardVel > 0.0 ? m.forwardVel : -m.forwardVel);
    m.soundMovingSpeed = absForwardVel > 100 ? 100 : absForwardVel;
}

/** Spawns particles if the step sound says to, then plays a step sound or relevant other sound. */
export function play_sound_and_spawn_particles(m, soundName, waveParticleType) {
    const terrain = m.terrainSoundAddend >>> 16;
    if (terrain === SOUND_TERRAIN_WATER) {
        if (waveParticleType !== 0) {
            m.particleFlags |= PARTICLE_SHALLOW_WATER_SPLASH;
        } else {
            m.particleFlags |= PARTICLE_SHALLOW_WATER_WAVE;
        }
    } else {
        if (terrain === SOUND_TERRAIN_SAND) {
            m.particleFlags |= PARTICLE_DIRT;
        } else if (terrain === SOUND_TERRAIN_SNOW) {
            m.particleFlags |= PARTICLE_SNOW;
        }
    }

    if ((m.flags & MARIO_METAL_CAP) || soundName === 'SOUND_ACTION_UNSTUCK_FROM_GROUND'
        || soundName === 'SOUND_MARIO_PUNCH_HOO') {
        play_sound(m, soundName);
    } else {
        play_sound(m, soundName, { terrain });
    }
}

/** Plays an environmental sound if one has not been played since the last action change. */
export function play_mario_action_sound(m, soundName, waveParticleType) {
    if (!(m.flags & MARIO_ACTION_SOUND_PLAYED)) {
        play_sound_and_spawn_particles(m, soundName, waveParticleType);
        m.flags |= MARIO_ACTION_SOUND_PLAYED;
    }
}

export function play_mario_landing_sound(m, soundName) {
    play_sound_and_spawn_particles(m, (m.flags & MARIO_METAL_CAP) ? 'SOUND_ACTION_METAL_LANDING' : soundName, 1);
}

export function play_mario_landing_sound_once(m, soundName) {
    play_mario_action_sound(m, (m.flags & MARIO_METAL_CAP) ? 'SOUND_ACTION_METAL_LANDING' : soundName, 1);
}

export function play_mario_heavy_landing_sound(m, soundName) {
    play_sound_and_spawn_particles(m, (m.flags & MARIO_METAL_CAP) ? 'SOUND_ACTION_METAL_HEAVY_LANDING' : soundName, 1);
}

export function play_mario_heavy_landing_sound_once(m, soundName) {
    play_mario_action_sound(m, (m.flags & MARIO_METAL_CAP) ? 'SOUND_ACTION_METAL_HEAVY_LANDING' : soundName, 1);
}

/**
 * Plays action and Mario sounds relevant to what was passed into the function.
 * marioSound: a SOUND_MARIO_* name, 0 (= play the jump sound) or -1 (= none).
 */
export function play_mario_sound(m, actionSound, marioSound) {
    if (actionSound === 'SOUND_ACTION_TERRAIN_JUMP') {
        play_mario_action_sound(m, (m.flags & MARIO_METAL_CAP) ? 'SOUND_ACTION_METAL_JUMP' : 'SOUND_ACTION_TERRAIN_JUMP', 1);
    } else {
        play_sound_if_no_flag(m, actionSound, MARIO_ACTION_SOUND_PLAYED);
    }

    if (marioSound === 0) {
        play_mario_jump_sound(m);
    }

    if (marioSound !== -1 && marioSound !== 0) {
        play_sound_if_no_flag(m, marioSound, MARIO_MARIO_SOUND_PLAYED);
    }
}

/**************************************************
 *                     ACTIONS                    *
 **************************************************/

/** Sets Mario's other velocities from his forward speed. */
export function mario_set_forward_vel(m, forwardVel) {
    m.forwardVel = forwardVel;

    m.slideVelX = sins(m.faceAngle[1]) * m.forwardVel;
    m.slideVelZ = coss(m.faceAngle[1]) * m.forwardVel;

    m.vel[0] = m.slideVelX;
    m.vel[2] = m.slideVelZ;
}

/** Returns the slipperiness class of Mario's floor. */
export function mario_get_floor_class(m) {
    let floorClass;

    if ((m.area.terrainType & S.TERRAIN_MASK) === S.TERRAIN_SLIDE) {
        floorClass = S.SURFACE_CLASS_VERY_SLIPPERY;
    } else {
        floorClass = S.SURFACE_CLASS_DEFAULT;
    }

    if (m.floor !== null) {
        switch (m.floor.type) {
            case S.SURFACE_NOT_SLIPPERY:
            case S.SURFACE_HARD_NOT_SLIPPERY:
            case S.SURFACE_SWITCH:
                floorClass = S.SURFACE_CLASS_NOT_SLIPPERY;
                break;

            case S.SURFACE_SLIPPERY:
            case S.SURFACE_NOISE_SLIPPERY:
            case S.SURFACE_HARD_SLIPPERY:
            case S.SURFACE_NO_CAM_COL_SLIPPERY:
                floorClass = S.SURFACE_CLASS_SLIPPERY;
                break;

            case S.SURFACE_VERY_SLIPPERY:
            case S.SURFACE_ICE:
            case S.SURFACE_HARD_VERY_SLIPPERY:
            case S.SURFACE_NOISE_VERY_SLIPPERY_73:
            case S.SURFACE_NOISE_VERY_SLIPPERY_74:
            case S.SURFACE_NOISE_VERY_SLIPPERY:
            case S.SURFACE_NO_CAM_COL_VERY_SLIPPERY:
                floorClass = S.SURFACE_CLASS_VERY_SLIPPERY;
                break;
        }
    }

    // Crawling allows Mario to not slide on certain steeper surfaces.
    if (m.action === ACT_CRAWLING && m.floor.normal.y > 0.5 && floorClass === S.SURFACE_CLASS_DEFAULT) {
        floorClass = S.SURFACE_CLASS_NOT_SLIPPERY;
    }

    return floorClass;
}

// clang-format off
const sTerrainSounds = [
    // default,              hard,                 slippery,
    // very slippery,        noisy default,        noisy slippery
    [SOUND_TERRAIN_DEFAULT, SOUND_TERRAIN_STONE, SOUND_TERRAIN_GRASS,
        SOUND_TERRAIN_GRASS, SOUND_TERRAIN_GRASS, SOUND_TERRAIN_DEFAULT], // TERRAIN_GRASS
    [SOUND_TERRAIN_STONE, SOUND_TERRAIN_STONE, SOUND_TERRAIN_STONE,
        SOUND_TERRAIN_STONE, SOUND_TERRAIN_GRASS, SOUND_TERRAIN_GRASS], // TERRAIN_STONE
    [SOUND_TERRAIN_SNOW, SOUND_TERRAIN_ICE, SOUND_TERRAIN_SNOW,
        SOUND_TERRAIN_ICE, SOUND_TERRAIN_STONE, SOUND_TERRAIN_STONE], // TERRAIN_SNOW
    [SOUND_TERRAIN_SAND, SOUND_TERRAIN_STONE, SOUND_TERRAIN_SAND,
        SOUND_TERRAIN_SAND, SOUND_TERRAIN_STONE, SOUND_TERRAIN_STONE], // TERRAIN_SAND
    [SOUND_TERRAIN_SPOOKY, SOUND_TERRAIN_SPOOKY, SOUND_TERRAIN_SPOOKY,
        SOUND_TERRAIN_SPOOKY, SOUND_TERRAIN_STONE, SOUND_TERRAIN_STONE], // TERRAIN_SPOOKY
    [SOUND_TERRAIN_DEFAULT, SOUND_TERRAIN_STONE, SOUND_TERRAIN_GRASS,
        SOUND_TERRAIN_ICE, SOUND_TERRAIN_STONE, SOUND_TERRAIN_ICE], // TERRAIN_WATER
    [SOUND_TERRAIN_STONE, SOUND_TERRAIN_STONE, SOUND_TERRAIN_STONE,
        SOUND_TERRAIN_STONE, SOUND_TERRAIN_ICE, SOUND_TERRAIN_ICE], // TERRAIN_SLIDE
];

/** Computes the value that is added to terrain sounds (SOUND_TERRAIN_* << 16). */
export function mario_get_terrain_sound_addend(m) {
    let terrainType = m.area.terrainType & S.TERRAIN_MASK;
    let ret = SOUND_TERRAIN_DEFAULT << 16;

    if (m.floor !== null) {
        const floorType = m.floor.type;
        let floorSoundType;

        if (!m.area.isLLL && (m.floorHeight < (m.waterLevel - 10))) {
            // Water terrain sound, excluding LLL since it uses water in the volcano.
            ret = SOUND_TERRAIN_WATER << 16;
        } else if (S.SURFACE_IS_QUICKSAND(floorType)) {
            ret = SOUND_TERRAIN_SAND << 16;
        } else {
            switch (floorType) {
                default:
                    floorSoundType = 0;
                    break;

                case S.SURFACE_NOT_SLIPPERY:
                case S.SURFACE_HARD:
                case S.SURFACE_HARD_NOT_SLIPPERY:
                case S.SURFACE_SWITCH:
                    floorSoundType = 1;
                    break;

                case S.SURFACE_SLIPPERY:
                case S.SURFACE_HARD_SLIPPERY:
                case S.SURFACE_NO_CAM_COL_SLIPPERY:
                    floorSoundType = 2;
                    break;

                case S.SURFACE_VERY_SLIPPERY:
                case S.SURFACE_ICE:
                case S.SURFACE_HARD_VERY_SLIPPERY:
                case S.SURFACE_NOISE_VERY_SLIPPERY_73:
                case S.SURFACE_NOISE_VERY_SLIPPERY_74:
                case S.SURFACE_NOISE_VERY_SLIPPERY:
                case S.SURFACE_NO_CAM_COL_VERY_SLIPPERY:
                    floorSoundType = 3;
                    break;

                case S.SURFACE_NOISE_DEFAULT:
                    floorSoundType = 4;
                    break;

                case S.SURFACE_NOISE_SLIPPERY:
                    floorSoundType = 5;
                    break;
            }

            if (terrainType > 6) terrainType = 0; // (out of table in the original)
            ret = sTerrainSounds[terrainType][floorSoundType] << 16;
        }
    }

    return ret;
}

/** Collides with walls and returns the most recent wall. Modifies pos in place. */
export function resolve_and_return_wall_collisions(m, pos, offset, radius) {
    const collisionData = createWallCollisionData(pos[0], pos[1], pos[2], offset, radius);
    let wall = null;

    if (m.world.find_wall_collisions(collisionData)) {
        wall = collisionData.walls[collisionData.numWalls - 1];
    }

    pos[0] = collisionData.x;
    pos[1] = collisionData.y;
    pos[2] = collisionData.z;

    // This only returns the most recent wall and can also return NULL
    // there are no wall collisions.
    return wall;
}

/** Finds the ceiling from a vec3f horizontally and a height (with 80 vertical buffer). Returns { height, surface }. */
export function vec3f_find_ceil(m, pos, height) {
    return m.world.find_ceil(pos[0], height + 80.0, pos[2]);
}

/** find_floor wrapper: returns { height, surface }. */
export function find_floor(m, x, y, z) {
    return m.world.find_floor(x, y, z);
}

/** Determines if Mario is facing "downhill." */
export function mario_facing_downhill(m, turnYaw) {
    let faceAngleYaw = m.faceAngle[1];

    // This is never used in practice, as turnYaw is always passed as zero.
    if (turnYaw && m.forwardVel < 0.0) {
        faceAngleYaw = s16(faceAngleYaw + 0x8000);
    }

    faceAngleYaw = s16(m.floorAngle - faceAngleYaw);

    return (-0x4000 < faceAngleYaw) && (faceAngleYaw < 0x4000);
}

/** Determines if a surface is slippery based on the surface class. */
export function mario_floor_is_slippery(m) {
    let normY;

    if ((m.area.terrainType & S.TERRAIN_MASK) === S.TERRAIN_SLIDE
        && m.floor.normal.y < F32(0.9998477) //~cos(1 deg)
    ) {
        return true;
    }

    switch (mario_get_floor_class(m)) {
        case S.SURFACE_VERY_SLIPPERY:
            normY = F32(0.9848077); //~cos(10 deg)
            break;

        case S.SURFACE_SLIPPERY:
            normY = F32(0.9396926); //~cos(20 deg)
            break;

        default:
            normY = F32(0.7880108); //~cos(38 deg)
            break;

        case S.SURFACE_NOT_SLIPPERY:
            normY = 0.0;
            break;
    }

    return m.floor.normal.y <= normY;
}

/** Determines if a surface is a slope based on the surface class. */
export function mario_floor_is_slope(m) {
    let normY;

    if ((m.area.terrainType & S.TERRAIN_MASK) === S.TERRAIN_SLIDE
        && m.floor.normal.y < F32(0.9998477)) { // ~cos(1 deg)
        return true;
    }

    switch (mario_get_floor_class(m)) {
        case S.SURFACE_VERY_SLIPPERY:
            normY = F32(0.9961947); // ~cos(5 deg)
            break;

        case S.SURFACE_SLIPPERY:
            normY = F32(0.9848077); // ~cos(10 deg)
            break;

        default:
            normY = F32(0.9659258); // ~cos(15 deg)
            break;

        case S.SURFACE_NOT_SLIPPERY:
            normY = F32(0.9396926); // ~cos(20 deg)
            break;
    }

    return m.floor.normal.y <= normY;
}

/** Determines if a surface is steep based on the surface class. */
export function mario_floor_is_steep(m) {
    let normY;
    let result = false;

    // Interestingly, this function does not check for the slide terrain type.
    if (!mario_facing_downhill(m, false)) {
        switch (mario_get_floor_class(m)) {
            case S.SURFACE_VERY_SLIPPERY:
                normY = F32(0.9659258); // ~cos(15 deg)
                break;

            case S.SURFACE_SLIPPERY:
                normY = F32(0.9396926); // ~cos(20 deg)
                break;

            default:
                normY = F32(0.8660254); // ~cos(30 deg)
                break;

            case S.SURFACE_NOT_SLIPPERY:
                normY = F32(0.8660254); // ~cos(30 deg)
                break;
        }

        result = m.floor.normal.y <= normY;
    }

    return result;
}

/** Finds the floor height relative from Mario given polar displacement. */
export function find_floor_height_relative_polar(m, angleFromMario, distFromMario) {
    const y = sins(m.faceAngle[1] + angleFromMario) * distFromMario;
    const x = coss(m.faceAngle[1] + angleFromMario) * distFromMario;

    return m.world.find_floor(m.pos[0] + y, m.pos[1] + 100.0, m.pos[2] + x).height;
}

/** Returns the slope of the floor based off points around Mario. */
export function find_floor_slope(m, yawOffset) {
    let result;

    const x = sins(m.faceAngle[1] + yawOffset) * 5.0;
    const z = coss(m.faceAngle[1] + yawOffset) * 5.0;

    const forwardFloorY = m.world.find_floor(m.pos[0] + x, m.pos[1] + 100.0, m.pos[2] + z).height;
    const backwardFloorY = m.world.find_floor(m.pos[0] - x, m.pos[1] + 100.0, m.pos[2] - z).height;

    //! If Mario is near OOB, these floorY's can sometimes be -11000.
    const forwardYDelta = forwardFloorY - m.pos[1];
    const backwardYDelta = m.pos[1] - backwardFloorY;

    if (forwardYDelta * forwardYDelta < backwardYDelta * backwardYDelta) {
        result = atan2s(5.0, forwardYDelta);
    } else {
        result = atan2s(5.0, backwardYDelta);
    }

    return result;
}

/** Adjusts Mario's camera and sound based on his action status (camera parts stubbed). */
export function update_mario_sound_and_camera(m) {
    const action = m.action;
    if (action === ACT_FIRST_PERSON) {
        set_camera_mode(m, -1, 1);
    } else if (action === ACT_SLEEPING) {
        // raise_background_noise(2)
    }
}

/** Transitions Mario to a steep jump action. */
export function set_steep_jump_action(m) {
    m.marioObj.oMarioSteepJumpYaw = m.faceAngle[1];

    if (m.forwardVel > 0.0) {
        //! ((s16)0x8000) has undefined behavior.
        const angleTemp = s16(m.floorAngle + 0x8000);
        const faceAngleTemp = s16(m.faceAngle[1] - angleTemp);

        const y = sins(faceAngleTemp) * m.forwardVel;
        const x = coss(faceAngleTemp) * m.forwardVel * 0.75;

        m.forwardVel = Math.sqrt(y * y + x * x);
        m.faceAngle[1] = s16(atan2s(x, y) + angleTemp);
    }

    drop_and_set_mario_action(m, C.ACT_STEEP_JUMP, 0);
}

/** Sets Mario's vertical speed from his forward speed. */
function set_mario_y_vel_based_on_fspeed(m, initialVelY, multiplier) {
    // get_additive_y_vel_for_jumps is always 0 and a stubbed function.
    m.vel[1] = initialVelY + 0.0 + m.forwardVel * multiplier;

    if (m.squishTimer !== 0 || m.quicksandDepth > 1.0) {
        m.vel[1] *= 0.5;
    }
}

/** Transitions for a variety of airborne actions. */
function set_mario_action_airborne(m, action, actionArg) {
    let forwardVel;

    if ((m.squishTimer !== 0 || m.quicksandDepth >= 1.0)
        && (action === ACT_DOUBLE_JUMP || action === ACT_TWIRLING)) {
        action = ACT_JUMP;
    }

    switch (action) {
        case ACT_DOUBLE_JUMP:
            set_mario_y_vel_based_on_fspeed(m, 52.0, 0.25);
            m.forwardVel *= 0.8;
            break;

        case ACT_BACKFLIP:
            m.marioObj.header.gfx.animInfo.animID = -1;
            m.forwardVel = -16.0;
            set_mario_y_vel_based_on_fspeed(m, 62.0, 0.0);
            break;

        case ACT_TRIPLE_JUMP:
            set_mario_y_vel_based_on_fspeed(m, 69.0, 0.0);
            m.forwardVel *= 0.8;
            break;

        case ACT_FLYING_TRIPLE_JUMP:
            set_mario_y_vel_based_on_fspeed(m, 82.0, 0.0);
            break;

        case ACT_WATER_JUMP:
        case ACT_HOLD_WATER_JUMP:
            if (actionArg === 0) {
                set_mario_y_vel_based_on_fspeed(m, 42.0, 0.0);
            }
            break;

        case ACT_BURNING_JUMP:
            m.vel[1] = 31.5;
            m.forwardVel = 8.0;
            break;

        case ACT_RIDING_SHELL_JUMP:
            set_mario_y_vel_based_on_fspeed(m, 42.0, 0.25);
            break;

        case ACT_JUMP:
        case ACT_HOLD_JUMP:
            m.marioObj.header.gfx.animInfo.animID = -1;
            set_mario_y_vel_based_on_fspeed(m, 42.0, 0.25);
            m.forwardVel *= 0.8;
            break;

        case ACT_WALL_KICK_AIR:
        case ACT_TOP_OF_POLE_JUMP:
            set_mario_y_vel_based_on_fspeed(m, 62.0, 0.0);
            if (m.forwardVel < 24.0) {
                m.forwardVel = 24.0;
            }
            m.wallKickTimer = 0;
            break;

        case ACT_SIDE_FLIP:
            set_mario_y_vel_based_on_fspeed(m, 62.0, 0.0);
            m.forwardVel = 8.0;
            m.faceAngle[1] = m.intendedYaw;
            break;

        case ACT_STEEP_JUMP:
            m.marioObj.header.gfx.animInfo.animID = -1;
            set_mario_y_vel_based_on_fspeed(m, 42.0, 0.25);
            m.faceAngle[0] = -0x2000;
            break;

        case ACT_LAVA_BOOST:
            m.vel[1] = 84.0;
            if (actionArg === 0) {
                m.forwardVel = 0.0;
            }
            break;

        case ACT_DIVE:
            if ((forwardVel = m.forwardVel + 15.0) > 48.0) {
                forwardVel = 48.0;
            }
            mario_set_forward_vel(m, forwardVel);
            break;

        case ACT_LONG_JUMP:
            m.marioObj.header.gfx.animInfo.animID = -1;
            set_mario_y_vel_based_on_fspeed(m, 30.0, 0.0);
            m.marioObj.oMarioLongJumpIsSlow = m.forwardVel > 16.0 ? 0 : 1;

            //! (BLJ's) This properly handles long jumps from getting forward speed with
            //  too much velocity, but misses backwards longs allowing high negative speeds.
            if ((m.forwardVel *= 1.5) > 48.0) {
                m.forwardVel = 48.0;
            }
            break;

        case ACT_SLIDE_KICK:
            m.vel[1] = 12.0;
            if (m.forwardVel < 32.0) {
                m.forwardVel = 32.0;
            }
            break;

        case ACT_JUMP_KICK:
            m.vel[1] = 20.0;
            break;
    }

    m.peakHeight = m.pos[1];
    m.flags |= MARIO_UNKNOWN_08;

    return action;
}

/** Transitions for a variety of moving actions. */
function set_mario_action_moving(m, action, _actionArg) {
    const floorClass = mario_get_floor_class(m);
    const forwardVel = m.forwardVel;
    const mag = Math.min(m.intendedMag, 8.0);

    switch (action) {
        case ACT_WALKING:
            if (floorClass !== S.SURFACE_CLASS_VERY_SLIPPERY) {
                if (0.0 <= forwardVel && forwardVel < mag) {
                    m.forwardVel = mag;
                }
            }

            m.marioObj.oMarioWalkingPitch = 0;
            break;

        case ACT_HOLD_WALKING:
            if (0.0 <= forwardVel && forwardVel < mag / 2.0) {
                m.forwardVel = mag / 2.0;
            }
            break;

        case ACT_BEGIN_SLIDING:
            if (mario_facing_downhill(m, false)) {
                action = ACT_BUTT_SLIDE;
            } else {
                action = ACT_STOMACH_SLIDE;
            }
            break;

        case ACT_HOLD_BEGIN_SLIDING:
            if (mario_facing_downhill(m, false)) {
                action = ACT_HOLD_BUTT_SLIDE;
            } else {
                action = ACT_HOLD_STOMACH_SLIDE;
            }
            break;
    }

    return action;
}

/** Transition for certain submerged actions, which is actually just the metal jump actions. */
function set_mario_action_submerged(m, action, _actionArg) {
    if (action === ACT_METAL_WATER_JUMP || action === ACT_HOLD_METAL_WATER_JUMP) {
        m.vel[1] = 32.0;
    }
    return action;
}

/**
 * Puts Mario into a given action, putting Mario through the appropriate
 * specific function if needed.
 */
export function set_mario_action(m, action, actionArg) {
    switch (action & ACT_GROUP_MASK) {
        case ACT_GROUP_MOVING:
            action = set_mario_action_moving(m, action, actionArg);
            break;

        case ACT_GROUP_AIRBORNE:
            action = set_mario_action_airborne(m, action, actionArg);
            break;

        case ACT_GROUP_SUBMERGED:
            action = set_mario_action_submerged(m, action, actionArg);
            break;

        case ACT_GROUP_CUTSCENE:
            // (set_mario_action_cutscene: cutscene actions are not ported)
            break;
    }

    // Resets the sound played flags, meaning Mario can play those sound types again.
    m.flags &= ~(MARIO_ACTION_SOUND_PLAYED | MARIO_MARIO_SOUND_PLAYED);

    if (!(m.action & ACT_FLAG_AIR)) {
        m.flags &= ~MARIO_UNKNOWN_18;
    }

    // Initialize the action information.
    m.prevAction = m.action;
    m.action = action;
    m.actionArg = actionArg >>> 0;
    m.actionState = 0;
    m.actionTimer = 0;

    if (m.onActionChange) {
        m.onActionChange(action, m.prevAction);
    }

    return true;
}

/** Puts Mario into a specific jumping action from a landing action. */
export function set_jump_from_landing(m) {
    if (m.quicksandDepth >= 11.0) {
        return set_mario_action(m, ACT_QUICKSAND_JUMP_LAND, 0);
    }

    if (mario_floor_is_steep(m)) {
        set_steep_jump_action(m);
    } else {
        if ((m.doubleJumpTimer === 0) || (m.squishTimer !== 0)) {
            set_mario_action(m, ACT_JUMP, 0);
        } else {
            switch (m.prevAction) {
                case ACT_JUMP_LAND:
                    set_mario_action(m, ACT_DOUBLE_JUMP, 0);
                    break;

                case ACT_FREEFALL_LAND:
                    set_mario_action(m, ACT_DOUBLE_JUMP, 0);
                    break;

                case ACT_SIDE_FLIP_LAND_STOP:
                    set_mario_action(m, ACT_DOUBLE_JUMP, 0);
                    break;

                case ACT_DOUBLE_JUMP_LAND:
                    // If Mario has a wing cap, he ignores the typical speed
                    // requirement for a triple jump.
                    if (m.flags & MARIO_WING_CAP) {
                        set_mario_action(m, ACT_FLYING_TRIPLE_JUMP, 0);
                    } else if (m.forwardVel > 20.0) {
                        set_mario_action(m, ACT_TRIPLE_JUMP, 0);
                    } else {
                        set_mario_action(m, ACT_JUMP, 0);
                    }
                    break;

                default:
                    set_mario_action(m, ACT_JUMP, 0);
                    break;
            }
        }
    }

    m.doubleJumpTimer = 0;

    return true;
}

/**
 * Puts Mario in a given action, as long as it is not overruled by
 * either a quicksand or steep jump.
 */
export function set_jumping_action(m, action, actionArg) {
    if (m.quicksandDepth >= 11.0) {
        return set_mario_action(m, ACT_QUICKSAND_JUMP_LAND, 0);
    }

    if (mario_floor_is_steep(m)) {
        set_steep_jump_action(m);
    } else {
        set_mario_action(m, action, actionArg);
    }

    return true;
}

/** Drop anything Mario is holding and set a new action. */
export function drop_and_set_mario_action(m, action, actionArg) {
    mario_stop_riding_and_holding(m);
    return set_mario_action(m, action, actionArg);
}

/** Increment Mario's hurt counter and set a new action. */
export function hurt_and_set_mario_action(m, action, actionArg, hurtCounter) {
    m.hurtCounter = hurtCounter & 0xFF;
    return set_mario_action(m, action, actionArg);
}

/** Checks a variety of inputs for common transitions between many different actions. */
export function check_common_action_exits(m) {
    if (m.input & INPUT_A_PRESSED) {
        return set_mario_action(m, ACT_JUMP, 0);
    }
    if (m.input & INPUT_OFF_FLOOR) {
        return set_mario_action(m, ACT_FREEFALL, 0);
    }
    if (m.input & INPUT_NONZERO_ANALOG) {
        return set_mario_action(m, ACT_WALKING, 0);
    }
    if (m.input & INPUT_ABOVE_SLIDE) {
        return set_mario_action(m, ACT_BEGIN_SLIDING, 0);
    }

    return false;
}

/**
 * set_water_plunge_action: swimming is not ported. With the default world the
 * water level is FLOOR_LOWER_LIMIT, so this is never reached.
 */
export function set_water_plunge_action(m) {
    m.forwardVel = m.forwardVel / 4.0;
    m.vel[1] = m.vel[1] / 2.0;
    m.pos[1] = m.waterLevel - 100;
    m.faceAngle[2] = 0;
    vec3s_set(m.angleVel, 0, 0, 0);
    return set_mario_action(m, ACT_FREEFALL, 0);
}

/** Squish scale table. */
const sSquishScaleOverTime = [0x46, 0x32, 0x32, 0x3C, 0x46, 0x50, 0x50, 0x3C,
    0x28, 0x14, 0x14, 0x1E, 0x32, 0x3C, 0x3C, 0x28];

/** Applies the squish to Mario's model via scaling. */
export function squish_mario_model(m) {
    const scale = m.marioObj.header.gfx.scale;
    if (m.squishTimer !== 0xFF) {
        // If no longer squished, scale back to default.
        if (m.squishTimer === 0) {
            vec3f_set(scale, 1.0, 1.0, 1.0);
        } else if (m.squishTimer <= 16) {
            // If timer is less than 16, rubber-band Mario's size scale up and down.
            m.squishTimer -= 1;

            scale[1] = 1.0 - ((sSquishScaleOverTime[15 - m.squishTimer] * 0.6) / 100.0);
            scale[0] = ((sSquishScaleOverTime[15 - m.squishTimer] * 0.4) / 100.0) + 1.0;

            scale[2] = scale[0];
        } else {
            m.squishTimer -= 1;

            vec3f_set(scale, 1.4, 0.4, 1.4);
        }
    }
}

/** Update the button inputs for Mario. */
export function update_mario_button_inputs(m) {
    if (m.controller.buttonPressed & A_BUTTON) {
        m.input |= INPUT_A_PRESSED;
    }

    if (m.controller.buttonDown & A_BUTTON) {
        m.input |= INPUT_A_DOWN;
    }

    // Don't update for these buttons if squished.
    if (m.squishTimer === 0) {
        if (m.controller.buttonPressed & B_BUTTON) {
            m.input |= INPUT_B_PRESSED;
        }

        if (m.controller.buttonDown & Z_TRIG) {
            m.input |= INPUT_Z_DOWN;
        }

        if (m.controller.buttonPressed & Z_TRIG) {
            m.input |= INPUT_Z_PRESSED;
        }
    }

    if (m.input & INPUT_A_PRESSED) {
        m.framesSinceA = 0;
    } else if (m.framesSinceA < 0xFF) {
        m.framesSinceA++;
    }

    if (m.input & INPUT_B_PRESSED) {
        m.framesSinceB = 0;
    } else if (m.framesSinceB < 0xFF) {
        m.framesSinceB++;
    }
}

/** Updates the joystick intended magnitude. */
export function update_mario_joystick_inputs(m) {
    const controller = m.controller;
    const mag = ((controller.stickMag / 64.0) * (controller.stickMag / 64.0)) * 64.0;

    if (m.squishTimer === 0) {
        m.intendedMag = mag / 2.0;
    } else {
        m.intendedMag = mag / 8.0;
    }
    // Not in the original: lets a heavier character have a lower top speed.
    m.intendedMag *= m.speedScale;

    if (m.intendedMag > 0.0) {
        m.intendedYaw = s16(atan2s(-controller.stickY, controller.stickX) + m.area.camera.yaw);
        m.input |= INPUT_NONZERO_ANALOG;
    } else {
        m.intendedYaw = m.faceAngle[1];
    }
}

/** Resolves wall collisions, and updates a variety of inputs. */
export function update_mario_geometry_inputs(m) {
    m.world.f32_find_wall_collision(m.pos, 60.0, 50.0);
    m.world.f32_find_wall_collision(m.pos, 30.0, 24.0);

    let r = m.world.find_floor(m.pos[0], m.pos[1], m.pos[2]);
    m.floorHeight = r.height;
    m.floor = r.surface;

    // If Mario is OOB, move his position to his graphical position (which was not updated)
    // and check for the floor there.
    if (m.floor === null) {
        vec3f_copy(m.pos, m.marioObj.header.gfx.pos);
        r = m.world.find_floor(m.pos[0], m.pos[1], m.pos[2]);
        m.floorHeight = r.height;
        m.floor = r.surface;
    }

    const c = vec3f_find_ceil(m, m.pos, m.floorHeight);
    m.ceilHeight = c.height;
    m.ceil = c.surface;
    const gasLevel = m.world.find_poison_gas_level(m.pos[0], m.pos[2]);
    m.waterLevel = s16(m.world.find_water_level(m.pos[0], m.pos[2]));

    if (m.floor !== null) {
        m.floorAngle = atan2s(m.floor.normal.z, m.floor.normal.x);
        m.terrainSoundAddend = mario_get_terrain_sound_addend(m);

        if ((m.pos[1] > m.waterLevel - 40) && mario_floor_is_slippery(m)) {
            m.input |= INPUT_ABOVE_SLIDE;
        }

        if ((m.floor.flags & SURFACE_FLAG_DYNAMIC)
            || (m.ceil && (m.ceil.flags & SURFACE_FLAG_DYNAMIC))) {
            const ceilToFloorDist = m.ceilHeight - m.floorHeight;

            if ((0.0 <= ceilToFloorDist) && (ceilToFloorDist <= 150.0)) {
                m.input |= INPUT_SQUISHED;
            }
        }

        if (m.pos[1] > m.floorHeight + 100.0) {
            m.input |= INPUT_OFF_FLOOR;
        }

        if (m.pos[1] < (m.waterLevel - 10)) {
            m.input |= INPUT_IN_WATER;
        }

        if (m.pos[1] < (gasLevel - 100.0)) {
            m.input |= INPUT_IN_POISON_GAS;
        }
    } else {
        level_trigger_warp(m, WARP_OP_DEATH);
    }
}

/** Handles Mario's input flags as well as a couple timers. */
export function update_mario_inputs(m) {
    m.particleFlags = 0;
    m.input = 0;
    m.collidedObjInteractTypes = 0;
    m.flags &= 0xFFFFFF;

    update_mario_button_inputs(m);
    update_mario_joystick_inputs(m);
    update_mario_geometry_inputs(m);

    // (C-up first person mode is not ported: INPUT_FIRST_PERSON is never set.)

    if (!(m.input & (INPUT_NONZERO_ANALOG | INPUT_A_PRESSED))) {
        m.input |= INPUT_UNKNOWN_5;
    }

    // (INPUT_STOMPED comes from Bowser objects: never set.)

    if (m.wallKickTimer > 0) {
        m.wallKickTimer--;
    }

    if (m.doubleJumpTimer > 0) {
        m.doubleJumpTimer--;
    }
}

/** Both increments and decrements Mario's HP. */
export function update_mario_health(m) {
    if (m.health >= 0x100) {
        // When already healing or hurting Mario, Mario's HP is not changed any more here.
        if ((m.healCounter | m.hurtCounter) === 0) {
            if ((m.input & INPUT_IN_POISON_GAS) && !(m.action & ACT_FLAG_INTANGIBLE)) {
                if (!(m.flags & MARIO_METAL_CAP)) {
                    m.health -= 4;
                }
            } else {
                if ((m.action & ACT_FLAG_SWIMMING) && !(m.action & ACT_FLAG_INTANGIBLE)) {
                    const terrainIsSnow = (m.area.terrainType & S.TERRAIN_MASK) === S.TERRAIN_SNOW;
                    if ((m.pos[1] >= (m.waterLevel - 140)) && !terrainIsSnow) {
                        m.health += 0x1A;
                    } else {
                        m.health -= (terrainIsSnow ? 3 : 1);
                    }
                }
            }
        }

        if (m.healCounter > 0) {
            m.health += 0x40;
            m.healCounter--;
        }
        if (m.hurtCounter > 0) {
            m.health -= 0x40;
            m.hurtCounter--;
        }

        if (m.health > 0x880) {
            m.health = 0x880;
        }
        if (m.health < 0x100) {
            m.health = 0xFF;
        }
    }
    m.health = s16(m.health);
}

/** Updates some basic info for camera usage. */
export function update_mario_info_for_cam(m) {
    m.marioBodyState.action = m.action;
    m.statusForCamera.action = m.action;

    vec3s_copy(m.statusForCamera.faceAngle, m.faceAngle);

    if (!(m.flags & MARIO_UNKNOWN_25)) {
        vec3f_copy(m.statusForCamera.pos, m.pos);
    }
}

/** Resets Mario's model, done every time an action is executed. */
export function mario_reset_bodystate(m) {
    const bodyState = m.marioBodyState;

    bodyState.capState = C.MARIO_HAS_DEFAULT_CAP_OFF;
    bodyState.eyeState = C.MARIO_EYES_BLINK;
    bodyState.handState = C.MARIO_HAND_FISTS;
    bodyState.modelState = 0;
    bodyState.wingFlutter = 0;

    m.flags &= ~MARIO_METAL_SHOCK;
}

/** Adjusts Mario's graphical height for quicksand. */
export function sink_mario_in_quicksand(m) {
    const gfx = m.marioObj.header.gfx;

    if (gfx.throwMatrix) {
        gfx.throwMatrix[3][1] -= m.quicksandDepth;
    }

    gfx.pos[1] -= m.quicksandDepth;
}

/** Updates the cap flags mainly based on the cap timer (cap timers are not used in this port). */
export function update_and_return_cap_flags(m) {
    let flags = m.flags;
    if (m.capTimer > 0) {
        m.capTimer -= 1;
        if (m.capTimer === 0) {
            m.flags &= ~MARIO_SPECIAL_CAPS;
            if (!(m.flags & MARIO_CAPS)) {
                m.flags &= ~MARIO_CAP_ON_HEAD;
            }
        }
        // (cap flicker omitted)
        flags = m.flags;
    }
    return flags;
}

/** Updates the Mario's cap, rendering, and hitbox. */
export function mario_update_hitbox_and_cap_model(m) {
    const bodyState = m.marioBodyState;
    const flags = update_and_return_cap_flags(m);

    if (flags & MARIO_VANISH_CAP) {
        bodyState.modelState = MODEL_STATE_NOISE_ALPHA;
    }

    if (flags & MARIO_METAL_CAP) {
        bodyState.modelState |= MODEL_STATE_METAL;
    }

    if (flags & MARIO_METAL_SHOCK) {
        bodyState.modelState |= MODEL_STATE_METAL;
    }

    //! (Pause buffered hitstun)
    if ((m.invincTimer >= 3) && (m.globalTimer & 1)) {
        m.marioObj.header.gfx.node.flags |= GRAPH_RENDER_INVISIBLE;
    }

    if (flags & MARIO_CAP_IN_HAND) {
        if (flags & MARIO_WING_CAP) {
            bodyState.handState = C.MARIO_HAND_HOLDING_WING_CAP;
        } else {
            bodyState.handState = C.MARIO_HAND_HOLDING_CAP;
        }
    }

    if (flags & MARIO_CAP_ON_HEAD) {
        if (flags & MARIO_WING_CAP) {
            bodyState.capState = C.MARIO_HAS_WING_CAP_ON;
        } else {
            bodyState.capState = C.MARIO_HAS_DEFAULT_CAP_ON;
        }
    }

    // Short hitbox for crouching/crawling/etc.
    if (m.action & ACT_FLAG_SHORT_HITBOX) {
        m.marioObj.hitboxHeight = 100.0;
    } else {
        m.marioObj.hitboxHeight = 160.0;
    }

    if ((m.flags & MARIO_TELEPORTING) && (m.fadeWarpOpacity !== 0xFF)) {
        bodyState.modelState &= ~0xFF;
        bodyState.modelState |= (0x100 | m.fadeWarpOpacity);
    }
}

/**************************************************
 *     INTERACTION.C pieces that are not objects   *
 **************************************************/

/** check_kick_or_punch_wall (interaction.c) */
export function check_kick_or_punch_wall(m) {
    if (m.flags & (C.MARIO_PUNCHING | C.MARIO_KICKING | C.MARIO_TRIPPING)) {
        const detector = [0, 0, 0];
        detector[0] = m.pos[0] + 50.0 * sins(m.faceAngle[1]);
        detector[2] = m.pos[2] + 50.0 * coss(m.faceAngle[1]);
        detector[1] = m.pos[1];

        if (resolve_and_return_wall_collisions(m, detector, 80.0, 5.0) !== null) {
            if (m.action !== ACT_MOVE_PUNCHING || m.forwardVel >= 0.0) {
                if (m.action === ACT_PUNCHING) {
                    m.action = ACT_MOVE_PUNCHING;
                }

                mario_set_forward_vel(m, -48.0);
                play_sound(m, 'SOUND_ACTION_HIT_2');
                m.particleFlags |= C.PARTICLE_TRIANGLE;
            } else if (m.action & ACT_FLAG_AIR) {
                mario_set_forward_vel(m, -16.0);
                play_sound(m, 'SOUND_ACTION_HIT_2');
                m.particleFlags |= C.PARTICLE_TRIANGLE;
            }
        }
    }
}

/** mario_process_interactions without objects. */
export function mario_process_interactions(m) {
    if (m.invincTimer > 0) {
        m.invincTimer--;
    }

    //! If the kick/punch flags are set and an object collision changes Mario's
    // action, he will get the kick/punch wall speed anyway.
    check_kick_or_punch_wall(m);
    m.flags &= ~C.MARIO_PUNCHING & ~C.MARIO_KICKING & ~C.MARIO_TRIPPING;
}

/** check_death_barrier (interaction.c) */
export function check_death_barrier(m) {
    if (m.pos[1] < m.floorHeight + 2048.0) {
        if (level_trigger_warp(m, WARP_OP_WARP_FLOOR) === 20 && !(m.flags & MARIO_UNKNOWN_18)) {
            play_sound(m, 'SOUND_MARIO_WAAAOOOW');
        }
    }
}

/** check_lava_boost (interaction.c) */
export function check_lava_boost(m) {
    if (!(m.action & C.ACT_FLAG_RIDING_SHELL) && m.pos[1] < m.floorHeight + 10.0) {
        if (!(m.flags & MARIO_METAL_CAP)) {
            m.hurtCounter += (m.flags & MARIO_CAP_ON_HEAD) ? 12 : 18;
            m.hurtCounter &= 0xFF;
        }

        update_mario_sound_and_camera(m);
        drop_and_set_mario_action(m, ACT_LAVA_BOOST, 0);
    }
}

/** mario_handle_special_floors (interaction.c) */
export function mario_handle_special_floors(m) {
    if ((m.action & ACT_GROUP_MASK) === ACT_GROUP_CUTSCENE) {
        return;
    }

    if (m.floor !== null) {
        const floorType = m.floor.type;

        switch (floorType) {
            case S.SURFACE_DEATH_PLANE:
            case S.SURFACE_VERTICAL_WIND:
                check_death_barrier(m);
                break;

            case S.SURFACE_WARP:
                level_trigger_warp(m, WARP_OP_WARP_FLOOR);
                break;
        }

        if (!(m.action & ACT_FLAG_AIR) && !(m.action & ACT_FLAG_SWIMMING)) {
            switch (floorType) {
                case S.SURFACE_BURNING:
                    check_lava_boost(m);
                    break;
            }
        }
    }
}

/**************************************************
 *                  MAIN UPDATE                   *
 **************************************************/

function mario_execute_submerged_or_cutscene_action(m) {
    // Not ported. Fall back to freefall so the loop cannot hang.
    return set_mario_action(m, ACT_FREEFALL, 0);
}

/** Main function for executing Mario's behavior (execute_mario_action). */
export function execute_mario_action(m) {
    let inLoop = true;

    if (m.action) {
        m.marioObj.header.gfx.node.flags &= ~GRAPH_RENDER_INVISIBLE;
        mario_reset_bodystate(m);
        update_mario_inputs(m);
        mario_handle_special_floors(m);
        mario_process_interactions(m);

        // If Mario is OOB, stop executing actions.
        if (m.floor === null) {
            return 0;
        }

        // The function can loop through many action shifts in one frame.
        let guard = 0;
        while (inLoop) {
            switch (m.action & ACT_GROUP_MASK) {
                case ACT_GROUP_STATIONARY:
                    inLoop = mario_execute_stationary_action(m);
                    break;

                case ACT_GROUP_MOVING:
                    inLoop = mario_execute_moving_action(m);
                    break;

                case ACT_GROUP_AIRBORNE:
                    inLoop = mario_execute_airborne_action(m);
                    break;

                case ACT_GROUP_AUTOMATIC:
                    inLoop = mario_execute_automatic_action(m);
                    break;

                case ACT_GROUP_OBJECT:
                    inLoop = mario_execute_object_action(m);
                    break;

                case ACT_GROUP_SUBMERGED:
                case ACT_GROUP_CUTSCENE:
                default:
                    inLoop = mario_execute_submerged_or_cutscene_action(m);
                    break;
            }
            if (++guard > 32) {
                // Safety net against an action loop (the original would hang).
                break;
            }
        }

        sink_mario_in_quicksand(m);
        squish_mario_model(m);
        update_mario_health(m);
        update_mario_info_for_cam(m);
        mario_update_hitbox_and_cap_model(m);

        if (m.floor.type === S.SURFACE_HORIZONTAL_WIND || m.floor.type === S.SURFACE_VERTICAL_WIND) {
            play_sound(m, 'SOUND_ENV_WIND2');
        }

        return m.particleFlags;
    }

    return 0;
}
