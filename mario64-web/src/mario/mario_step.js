// Port of src/game/mario_step.c

import { s16, sins, coss, atan2s, vec3f_copy, vec3f_set, vec3s_set } from '../engine/math_util.js';
import * as S from '../engine/surface_terrains.js';
import * as C from './constants.js';
import {
    play_sound, mario_set_forward_vel, set_mario_action, drop_and_set_mario_action,
    resolve_and_return_wall_collisions, vec3f_find_ceil, mario_get_terrain_sound_addend,
    update_mario_sound_and_camera, request_death,
} from './mario.js';

const sMovingSandSpeeds = [12, 8, 4, 0];

export function mario_bonk_reflection(m, negateSpeed) {
    if (m.wall !== null) {
        const wallAngle = atan2s(m.wall.normal.z, m.wall.normal.x);
        m.faceAngle[1] = s16(wallAngle - s16(m.faceAngle[1] - wallAngle));

        play_sound(m, (m.flags & C.MARIO_METAL_CAP) ? 'SOUND_ACTION_METAL_BONK' : 'SOUND_ACTION_BONK');
    } else {
        play_sound(m, 'SOUND_ACTION_HIT');
    }

    if (negateSpeed) {
        mario_set_forward_vel(m, -m.forwardVel);
    } else {
        m.faceAngle[1] = s16(m.faceAngle[1] + 0x8000);
    }
}

export function mario_update_quicksand(m, sinkingSpeed) {
    if (m.action & C.ACT_FLAG_RIDING_SHELL) {
        m.quicksandDepth = 0.0;
    } else {
        if (m.quicksandDepth < 1.1) {
            m.quicksandDepth = 1.1;
        }

        switch (m.floor.type) {
            case S.SURFACE_SHALLOW_QUICKSAND:
                if ((m.quicksandDepth += sinkingSpeed) >= 10.0) {
                    m.quicksandDepth = 10.0;
                }
                break;

            case S.SURFACE_SHALLOW_MOVING_QUICKSAND:
                if ((m.quicksandDepth += sinkingSpeed) >= 25.0) {
                    m.quicksandDepth = 25.0;
                }
                break;

            case S.SURFACE_QUICKSAND:
            case S.SURFACE_MOVING_QUICKSAND:
                if ((m.quicksandDepth += sinkingSpeed) >= 60.0) {
                    m.quicksandDepth = 60.0;
                }
                break;

            case S.SURFACE_DEEP_QUICKSAND:
            case S.SURFACE_DEEP_MOVING_QUICKSAND:
                if ((m.quicksandDepth += sinkingSpeed) >= 160.0) {
                    update_mario_sound_and_camera(m);
                    // drop_and_set_mario_action(m, ACT_QUICKSAND_DEATH, 0)
                    m.quicksandDepth = 160.0;
                    request_death(m, C.ACT_QUICKSAND_DEATH);
                    return false;
                }
                break;

            case S.SURFACE_INSTANT_QUICKSAND:
            case S.SURFACE_INSTANT_MOVING_QUICKSAND:
                update_mario_sound_and_camera(m);
                // drop_and_set_mario_action(m, ACT_QUICKSAND_DEATH, 0)
                request_death(m, C.ACT_QUICKSAND_DEATH);
                return false;

            default:
                m.quicksandDepth = 0.0;
                break;
        }
    }

    return false;
}

export function mario_push_off_steep_floor(m, action, actionArg) {
    const floorDYaw = s16(m.floorAngle - m.faceAngle[1]);

    if (floorDYaw > -0x4000 && floorDYaw < 0x4000) {
        m.forwardVel = 16.0;
        m.faceAngle[1] = m.floorAngle;
    } else {
        m.forwardVel = -16.0;
        m.faceAngle[1] = s16(m.floorAngle + 0x8000);
    }

    return set_mario_action(m, action, actionArg);
}

export function mario_update_moving_sand(m) {
    const floor = m.floor;
    const floorType = floor.type;

    if (floorType === S.SURFACE_DEEP_MOVING_QUICKSAND || floorType === S.SURFACE_SHALLOW_MOVING_QUICKSAND
        || floorType === S.SURFACE_MOVING_QUICKSAND || floorType === S.SURFACE_INSTANT_MOVING_QUICKSAND) {
        const pushAngle = s16(floor.force << 8);
        const pushSpeed = sMovingSandSpeeds[(floor.force >> 8) & 3];

        m.vel[0] += pushSpeed * sins(pushAngle);
        m.vel[2] += pushSpeed * coss(pushAngle);

        return true;
    }

    return false;
}

export function mario_update_windy_ground(m) {
    const floor = m.floor;

    if (floor.type === S.SURFACE_HORIZONTAL_WIND) {
        let pushSpeed;
        const pushAngle = s16(floor.force << 8);

        if (m.action & C.ACT_FLAG_MOVING) {
            const pushDYaw = s16(m.faceAngle[1] - pushAngle);

            pushSpeed = m.forwardVel > 0.0 ? -m.forwardVel * 0.5 : -8.0;

            if (pushDYaw > -0x4000 && pushDYaw < 0x4000) {
                pushSpeed *= -1.0;
            }

            pushSpeed *= coss(pushDYaw);
        } else {
            pushSpeed = 3.2 + (m.globalTimer % 4);
        }

        m.vel[0] += pushSpeed * sins(pushAngle);
        m.vel[2] += pushSpeed * coss(pushAngle);

        return true;
    }

    return false;
}

export function stop_and_set_height_to_floor(m) {
    const marioObj = m.marioObj;

    mario_set_forward_vel(m, 0.0);
    m.vel[1] = 0.0;

    //! This is responsible for some downwarps.
    m.pos[1] = m.floorHeight;

    vec3f_copy(marioObj.header.gfx.pos, m.pos);
    vec3s_set(marioObj.header.gfx.angle, 0, m.faceAngle[1], 0);
}

export function stationary_ground_step(m) {
    const marioObj = m.marioObj;
    let stepResult = C.GROUND_STEP_NONE;

    mario_set_forward_vel(m, 0.0);

    let takeStep = mario_update_moving_sand(m);
    takeStep = mario_update_windy_ground(m) || takeStep;
    if (takeStep) {
        stepResult = perform_ground_step(m);
    } else {
        //! This is responsible for several stationary downwarps.
        m.pos[1] = m.floorHeight;

        vec3f_copy(marioObj.header.gfx.pos, m.pos);
        vec3s_set(marioObj.header.gfx.angle, 0, m.faceAngle[1], 0);
    }

    return stepResult;
}

function perform_ground_quarter_step(m, nextPos) {
    /* lowerWall = */ resolve_and_return_wall_collisions(m, nextPos, 30.0, 24.0);
    const upperWall = resolve_and_return_wall_collisions(m, nextPos, 60.0, 50.0);

    const f = m.world.find_floor(nextPos[0], nextPos[1], nextPos[2]);
    let floorHeight = f.height;
    let floor = f.surface;
    const ceilHeight = vec3f_find_ceil(m, nextPos, floorHeight).height;

    m.wall = upperWall;

    if (floor === null) {
        return C.GROUND_STEP_HIT_WALL_STOP_QSTEPS;
    }

    // (Riding shell water pseudo floor omitted: no shells.)

    if (nextPos[1] > floorHeight + 100.0) {
        if (nextPos[1] + 160.0 >= ceilHeight) {
            return C.GROUND_STEP_HIT_WALL_STOP_QSTEPS;
        }

        vec3f_copy(m.pos, nextPos);
        m.floor = floor;
        m.floorHeight = floorHeight;
        return C.GROUND_STEP_LEFT_GROUND;
    }

    if (floorHeight + 160.0 >= ceilHeight) {
        return C.GROUND_STEP_HIT_WALL_STOP_QSTEPS;
    }

    vec3f_set(m.pos, nextPos[0], floorHeight, nextPos[2]);
    m.floor = floor;
    m.floorHeight = floorHeight;

    if (upperWall !== null) {
        const wallDYaw = s16(atan2s(upperWall.normal.z, upperWall.normal.x) - m.faceAngle[1]);

        if (wallDYaw >= 0x2AAA && wallDYaw <= 0x5555) {
            return C.GROUND_STEP_NONE;
        }
        if (wallDYaw <= -0x2AAA && wallDYaw >= -0x5555) {
            return C.GROUND_STEP_NONE;
        }

        return C.GROUND_STEP_HIT_WALL_CONTINUE_QSTEPS;
    }

    return C.GROUND_STEP_NONE;
}

export function perform_ground_step(m) {
    let stepResult;
    const intendedPos = [0, 0, 0];

    for (let i = 0; i < 4; i++) {
        intendedPos[0] = m.pos[0] + m.floor.normal.y * (m.vel[0] / 4.0);
        intendedPos[2] = m.pos[2] + m.floor.normal.y * (m.vel[2] / 4.0);
        intendedPos[1] = m.pos[1];

        stepResult = perform_ground_quarter_step(m, intendedPos);
        if (stepResult === C.GROUND_STEP_LEFT_GROUND || stepResult === C.GROUND_STEP_HIT_WALL_STOP_QSTEPS) {
            break;
        }
    }

    m.terrainSoundAddend = mario_get_terrain_sound_addend(m);
    vec3f_copy(m.marioObj.header.gfx.pos, m.pos);
    vec3s_set(m.marioObj.header.gfx.angle, 0, m.faceAngle[1], 0);

    if (stepResult === C.GROUND_STEP_HIT_WALL_CONTINUE_QSTEPS) {
        stepResult = C.GROUND_STEP_HIT_WALL;
    }
    return stepResult;
}

export function check_ledge_grab(m, wall, intendedPos, nextPos) {
    if (m.vel[1] > 0) {
        return false;
    }

    const displacementX = nextPos[0] - intendedPos[0];
    const displacementZ = nextPos[2] - intendedPos[2];

    // Only ledge grab if the wall displaced Mario in the opposite direction of
    // his velocity.
    if (displacementX * m.vel[0] + displacementZ * m.vel[2] > 0.0) {
        return false;
    }

    //! Since the search for floors starts at y + 160, we will sometimes grab
    // a higher ledge than expected (glitchy ledge grab)
    const ledgePos = [0, 0, 0];
    ledgePos[0] = nextPos[0] - wall.normal.x * 60.0;
    ledgePos[2] = nextPos[2] - wall.normal.z * 60.0;
    const lf = m.world.find_floor(ledgePos[0], nextPos[1] + 160.0, ledgePos[2]);
    ledgePos[1] = lf.height;
    const ledgeFloor = lf.surface;

    if (ledgePos[1] - nextPos[1] <= 100.0) {
        return false;
    }

    vec3f_copy(m.pos, ledgePos);
    m.floor = ledgeFloor;
    m.floorHeight = ledgePos[1];

    m.floorAngle = atan2s(ledgeFloor.normal.z, ledgeFloor.normal.x);

    m.faceAngle[0] = 0;
    m.faceAngle[1] = s16(atan2s(wall.normal.z, wall.normal.x) + 0x8000);
    return true;
}

export function perform_air_quarter_step(m, intendedPos, stepArg) {
    const nextPos = [intendedPos[0], intendedPos[1], intendedPos[2]];

    const upperWall = resolve_and_return_wall_collisions(m, nextPos, 150.0, 50.0);
    const lowerWall = resolve_and_return_wall_collisions(m, nextPos, 30.0, 50.0);

    const f = m.world.find_floor(nextPos[0], nextPos[1], nextPos[2]);
    let floorHeight = f.height;
    let floor = f.surface;
    const ceilHeight = vec3f_find_ceil(m, nextPos, floorHeight).height;

    m.wall = null;

    //! The water pseudo floor is not referenced when your intended qstep is
    // out of bounds, so it won't detect you as landing.

    if (floor === null) {
        if (nextPos[1] <= m.floorHeight) {
            m.pos[1] = m.floorHeight;
            return C.AIR_STEP_LANDED;
        }

        m.pos[1] = nextPos[1];
        return C.AIR_STEP_HIT_WALL;
    }

    // (Riding shell water pseudo floor omitted: no shells.)

    //! This check uses f32, but findFloor uses short (overflow jumps)
    if (nextPos[1] <= floorHeight) {
        if (ceilHeight - floorHeight > 160.0) {
            m.pos[0] = nextPos[0];
            m.pos[2] = nextPos[2];
            m.floor = floor;
            m.floorHeight = floorHeight;
        }

        //! When ceilHeight - floorHeight <= 160, the step result says that
        // Mario landed, but his movement is cancelled and his referenced floor
        // isn't updated (pedro spots)
        m.pos[1] = floorHeight;
        return C.AIR_STEP_LANDED;
    }

    if (nextPos[1] + 160.0 > ceilHeight) {
        if (m.vel[1] >= 0.0) {
            m.vel[1] = 0.0;

            //! Uses referenced ceiling instead of ceil (ceiling hang upwarp)
            if ((stepArg & C.AIR_STEP_CHECK_HANG) && m.ceil !== null
                && m.ceil.type === S.SURFACE_HANGABLE) {
                return C.AIR_STEP_GRABBED_CEILING;
            }

            return C.AIR_STEP_NONE;
        }

        //! Potential subframe downwarp->upwarp?
        if (nextPos[1] <= m.floorHeight) {
            m.pos[1] = m.floorHeight;
            return C.AIR_STEP_LANDED;
        }

        m.pos[1] = nextPos[1];
        return C.AIR_STEP_HIT_WALL;
    }

    //! When the wall is not completely vertical or there is a slight wall
    // misalignment, you can activate these conditions in unexpected situations
    if ((stepArg & C.AIR_STEP_CHECK_LEDGE_GRAB) && upperWall === null && lowerWall !== null) {
        if (check_ledge_grab(m, lowerWall, intendedPos, nextPos)) {
            return C.AIR_STEP_GRABBED_LEDGE;
        }

        vec3f_copy(m.pos, nextPos);
        m.floor = floor;
        m.floorHeight = floorHeight;
        return C.AIR_STEP_NONE;
    }

    vec3f_copy(m.pos, nextPos);
    m.floor = floor;
    m.floorHeight = floorHeight;

    if (upperWall !== null || lowerWall !== null) {
        m.wall = upperWall !== null ? upperWall : lowerWall;
        const wallDYaw = s16(atan2s(m.wall.normal.z, m.wall.normal.x) - m.faceAngle[1]);

        if (m.wall.type === S.SURFACE_BURNING) {
            return C.AIR_STEP_HIT_LAVA_WALL;
        }

        if (wallDYaw < -0x6000 || wallDYaw > 0x6000) {
            m.flags |= C.MARIO_UNKNOWN_30;
            return C.AIR_STEP_HIT_WALL;
        }
    }

    return C.AIR_STEP_NONE;
}

export function apply_twirl_gravity(m) {
    let heaviness = 1.0;

    if (m.angleVel[1] > 1024) {
        heaviness = 1024.0 / m.angleVel[1];
    }

    const terminalVelocity = -75.0 * heaviness;

    m.vel[1] -= 4.0 * heaviness;
    if (m.vel[1] < terminalVelocity) {
        m.vel[1] = terminalVelocity;
    }
}

export function should_strengthen_gravity_for_jump_ascent(m) {
    if (!(m.flags & C.MARIO_UNKNOWN_08)) {
        return false;
    }

    if (m.action & (C.ACT_FLAG_INTANGIBLE | C.ACT_FLAG_INVULNERABLE)) {
        return false;
    }

    if (!(m.input & C.INPUT_A_DOWN) && m.vel[1] > 20.0) {
        return (m.action & C.ACT_FLAG_CONTROL_JUMP_HEIGHT) !== 0;
    }

    return false;
}

export function apply_gravity(m) {
    if (m.action === C.ACT_TWIRLING && m.vel[1] < 0.0) {
        apply_twirl_gravity(m);
    } else if (m.action === C.ACT_SHOT_FROM_CANNON) {
        m.vel[1] -= 1.0;
        if (m.vel[1] < -75.0) {
            m.vel[1] = -75.0;
        }
    } else if (m.action === C.ACT_LONG_JUMP || m.action === C.ACT_SLIDE_KICK
        || m.action === C.ACT_BBH_ENTER_SPIN) {
        m.vel[1] -= 2.0;
        if (m.vel[1] < -75.0) {
            m.vel[1] = -75.0;
        }
    } else if (m.action === C.ACT_LAVA_BOOST || m.action === C.ACT_FALL_AFTER_STAR_GRAB) {
        m.vel[1] -= 3.2;
        if (m.vel[1] < -65.0) {
            m.vel[1] = -65.0;
        }
    } else if (m.action === C.ACT_GETTING_BLOWN) {
        m.vel[1] -= m.gettingBlownGravity;
        if (m.vel[1] < -75.0) {
            m.vel[1] = -75.0;
        }
    } else if (should_strengthen_gravity_for_jump_ascent(m)) {
        m.vel[1] /= 4.0;
    } else if (m.action & C.ACT_FLAG_METAL_WATER) {
        m.vel[1] -= 1.6;
        if (m.vel[1] < -16.0) {
            m.vel[1] = -16.0;
        }
    } else if ((m.flags & C.MARIO_WING_CAP) && m.vel[1] < 0.0 && (m.input & C.INPUT_A_DOWN)) {
        m.marioBodyState.wingFlutter = 1;

        m.vel[1] -= 2.0;
        if (m.vel[1] < -37.5) {
            if ((m.vel[1] += 4.0) > -37.5) {
                m.vel[1] = -37.5;
            }
        }
    } else {
        m.vel[1] -= 4.0;
        if (m.vel[1] < -75.0) {
            m.vel[1] = -75.0;
        }
    }
}

export function apply_vertical_wind(m) {
    if (m.action !== C.ACT_GROUND_POUND) {
        const offsetY = m.pos[1] - -1500.0;

        if (m.floor.type === S.SURFACE_VERTICAL_WIND && -3000.0 < offsetY && offsetY < 2000.0) {
            let maxVelY;
            if (offsetY >= 0.0) {
                maxVelY = 10000.0 / (offsetY + 200.0);
            } else {
                maxVelY = 50.0;
            }

            if (m.vel[1] < maxVelY) {
                if ((m.vel[1] += maxVelY / 8.0) > maxVelY) {
                    m.vel[1] = maxVelY;
                }
            }
        }
    }
}

export function perform_air_step(m, stepArg) {
    const intendedPos = [0, 0, 0];
    let stepResult = C.AIR_STEP_NONE;

    m.wall = null;

    for (let i = 0; i < 4; i++) {
        intendedPos[0] = m.pos[0] + m.vel[0] / 4.0;
        intendedPos[1] = m.pos[1] + m.vel[1] / 4.0;
        intendedPos[2] = m.pos[2] + m.vel[2] / 4.0;

        const quarterStepResult = perform_air_quarter_step(m, intendedPos, stepArg);

        //! On one qf, hit OOB/ceil/wall to store the 2 return value, and continue
        // getting 0s until your last qf. Graze a wall on your last qf, and it will
        // return the stored 2 with a sharply angled reference wall. (some gwks)

        if (quarterStepResult !== C.AIR_STEP_NONE) {
            stepResult = quarterStepResult;
        }

        if (quarterStepResult === C.AIR_STEP_LANDED || quarterStepResult === C.AIR_STEP_GRABBED_LEDGE
            || quarterStepResult === C.AIR_STEP_GRABBED_CEILING
            || quarterStepResult === C.AIR_STEP_HIT_LAVA_WALL) {
            break;
        }
    }

    if (m.vel[1] >= 0.0) {
        m.peakHeight = m.pos[1];
    }

    m.terrainSoundAddend = mario_get_terrain_sound_addend(m);

    if (m.action !== C.ACT_FLYING) {
        apply_gravity(m);
    }
    apply_vertical_wind(m);

    vec3f_copy(m.marioObj.header.gfx.pos, m.pos);
    vec3s_set(m.marioObj.header.gfx.angle, 0, m.faceAngle[1], 0);

    return stepResult;
}

export function set_vel_from_pitch_and_yaw(m) {
    m.vel[0] = m.forwardVel * coss(m.faceAngle[0]) * sins(m.faceAngle[1]);
    m.vel[1] = m.forwardVel * sins(m.faceAngle[0]);
    m.vel[2] = m.forwardVel * coss(m.faceAngle[0]) * coss(m.faceAngle[1]);
}

export function set_vel_from_yaw(m) {
    m.vel[0] = m.slideVelX = m.forwardVel * sins(m.faceAngle[1]);
    m.vel[1] = 0.0;
    m.vel[2] = m.slideVelZ = m.forwardVel * coss(m.faceAngle[1]);
}

export { drop_and_set_mario_action };
