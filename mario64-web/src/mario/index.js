// Public entry point of the Mario physics port.
//
//   const m = createMario({ world, animations, sound });
//   m.reset([x, y, z], faceYaw);
//   m.update({ stickX, stickY, buttons, cameraYaw });   // one 30 Hz tick
//
// After update(), the MarioState fields (m.pos, m.vel, m.action, ...) and
// m.marioObj.header.gfx (pos / angle / animInfo / scale / throwMatrix) and
// m.marioBodyState have the same meaning as in the original game.

import { s16, vec3f_copy, vec3s_set } from '../engine/math_util.js';
import { geo_advance_object_animation } from '../engine/graph_node.js';
import * as C from './constants.js';
import { MARIO_ANIM_IDLE_HEAD_LEFT } from './anim_ids.js';
import { execute_mario_action, mario_reset_bodystate, update_mario_info_for_cam } from './mario.js';

export * from './constants.js';
export { MarioAnimID, ANIM_NAMES } from './anim_ids.js';

function createController() {
    return {
        rawStickX: 0,
        rawStickY: 0,
        stickX: 0,
        stickY: 0,
        stickMag: 0,
        buttonDown: 0,
        buttonPressed: 0,
    };
}

/** adjust_analog_stick (src/game/game_init.c): deadzone of 8, offset of 6, clamp magnitude to 64. */
export function adjust_analog_stick(controller) {
    controller.stickX = 0;
    controller.stickY = 0;

    if (controller.rawStickX <= -8) {
        controller.stickX = controller.rawStickX + 6;
    }

    if (controller.rawStickX >= 8) {
        controller.stickX = controller.rawStickX - 6;
    }

    if (controller.rawStickY <= -8) {
        controller.stickY = controller.rawStickY + 6;
    }

    if (controller.rawStickY >= 8) {
        controller.stickY = controller.rawStickY - 6;
    }

    controller.stickMag = Math.sqrt(controller.stickX * controller.stickX + controller.stickY * controller.stickY);

    if (controller.stickMag > 64) {
        controller.stickX *= 64 / controller.stickMag;
        controller.stickY *= 64 / controller.stickMag;
        controller.stickMag = 64;
    }
}

function clampRawStick(v) {
    v = Math.trunc(Number(v) || 0);
    if (v > 127) v = 127;
    if (v < -128) v = -128;
    return v;
}

/**
 * Create a MarioState.
 * @param {object} opts
 * @param {import('../engine/surface.js').CollisionWorld} opts.world
 * @param {Array<{flags,animYTransDivisor,startFrame,loopStart,loopEnd}>} opts.animations indexed by MarioAnimID
 * @param {(name: string, extra?: object) => void} [opts.sound] sound hook; name is the original SOUND_* constant name
 */
export function createMario({ world, animations, sound } = {}) {
    const m = {
        // ---- struct MarioState ----
        unk00: 0,
        input: 0,
        flags: 0,
        particleFlags: 0,
        action: 0,
        prevAction: 0,
        terrainSoundAddend: 0,
        actionState: 0,
        actionTimer: 0,
        actionArg: 0,
        intendedMag: 0,
        intendedYaw: 0,
        invincTimer: 0,
        framesSinceA: 0xFF,
        framesSinceB: 0xFF,
        wallKickTimer: 0,
        doubleJumpTimer: 0,
        faceAngle: [0, 0, 0],
        angleVel: [0, 0, 0],
        slideYaw: 0,
        twirlYaw: 0,
        pos: [0, 0, 0],
        vel: [0, 0, 0],
        forwardVel: 0,
        slideVelX: 0,
        slideVelZ: 0,
        wall: null,
        ceil: null,
        floor: null,
        ceilHeight: 0,
        floorHeight: 0,
        floorAngle: 0,
        waterLevel: -11000,
        interactObj: null,
        heldObj: null,
        usedObj: null,
        riddenObj: null,
        collidedObjInteractTypes: 0,
        numCoins: 0,
        numStars: 0,
        numKeys: 0,
        numLives: 4,
        health: 0x880,
        unkB0: 0xBD,
        hurtCounter: 0,
        healCounter: 0,
        squishTimer: 0,
        fadeWarpOpacity: 0,
        capTimer: 0,
        peakHeight: 0,
        quicksandDepth: 0,
        gettingBlownGravity: 0,

        // ---- linked structs ----
        marioObj: {
            header: {
                gfx: {
                    node: { flags: 0 },
                    pos: [0, 0, 0],
                    angle: [0, 0, 0],
                    scale: [1, 1, 1],
                    animInfo: {
                        animID: -1,
                        animYTrans: 0,
                        curAnim: null,
                        animFrame: 0,
                        animTimer: 0,
                        animFrameAccelAssist: 0,
                        animAccel: 0,
                    },
                    /** Floor-aligned transform (Mat4 [row][col]) set while crawling/sliding, else null. */
                    throwMatrix: null,
                },
            },
            oMarioWalkingPitch: 0,
            oMarioSteepJumpYaw: 0,
            oMarioLongJumpIsSlow: 0,
            oMarioBurnTimer: 0,
            hitboxHeight: 160,
            hitboxRadius: 37,
        },
        marioBodyState: {
            action: 0,
            capState: C.MARIO_HAS_DEFAULT_CAP_ON,
            eyeState: C.MARIO_EYES_BLINK,
            handState: C.MARIO_HAND_FISTS,
            wingFlutter: 0,
            modelState: 0,
            grabPos: C.GRAB_POS_NULL,
            punchState: 0,
            torsoAngle: [0, 0, 0],
            headAngle: [0, 0, 0],
            heldObjLastPosition: [0, 0, 0],
        },
        statusForCamera: {
            action: 0,
            faceAngle: [0, 0, 0],
            pos: [0, 0, 0],
            headRotation: [0, 0, 0],
            cameraEvent: 0,
        },
        controller: createController(),
        /** m->area: terrainType (TERRAIN_*), camera yaw used for intendedYaw. */
        area: {
            terrainType: 0,
            isLLL: false,
            camera: { yaw: 0, mode: 0, defMode: 0 },
        },

        // ---- port-specific ----
        world,
        animations: animations || [],
        sound: typeof sound === 'function' ? sound : null,
        requestRespawn: false,
        respawnReason: null,
        deathAction: 0,
        globalTimer: 0,
        areaUpdateCounter: 0,
        audioRandom: 0x12345678,
        soundMovingSpeed: 0,
        floorAlignMatrix: null,
        /** Optional hook: (newAction, prevAction) => void, called on every set_mario_action. */
        onActionChange: null,

        reset(pos, faceYaw = 0) {
            resetMario(m, pos, faceYaw);
        },

        update(input = {}) {
            updateMario(m, input);
        },
    };

    return m;
}

/** init_mario equivalent: spawn standing idle at pos. */
function resetMario(m, pos, faceYaw) {
    m.actionTimer = 0;
    m.actionState = 0;
    m.actionArg = 0;
    m.framesSinceA = 0xFF;
    m.framesSinceB = 0xFF;
    m.invincTimer = 0;
    m.flags = C.MARIO_NORMAL_CAP | C.MARIO_CAP_ON_HEAD;
    m.forwardVel = 0.0;
    m.squishTimer = 0;
    m.hurtCounter = 0;
    m.healCounter = 0;
    m.capTimer = 0;
    m.quicksandDepth = 0.0;
    m.wallKickTimer = 0;
    m.doubleJumpTimer = 0;
    m.slideVelX = 0;
    m.slideVelZ = 0;
    m.slideYaw = 0;
    m.twirlYaw = 0;
    m.input = 0;
    m.particleFlags = 0;
    m.health = 0x880;
    m.requestRespawn = false;
    m.respawnReason = null;
    m.deathAction = 0;
    m.heldObj = null;
    m.riddenObj = null;
    m.usedObj = null;
    m.wall = null;

    m.waterLevel = s16(m.world.find_water_level(pos[0], pos[2]));

    const gfx = m.marioObj.header.gfx;
    gfx.animInfo.animID = -1;
    gfx.animInfo.animAccel = 0;
    gfx.animInfo.animFrameAccelAssist = 0;
    const idle = m.animations[MARIO_ANIM_IDLE_HEAD_LEFT] || null;
    gfx.animInfo.curAnim = idle; // so a renderer has something to show before the first update
    gfx.animInfo.animFrame = idle ? idle.startFrame : 0;
    gfx.scale[0] = gfx.scale[1] = gfx.scale[2] = 1;
    gfx.node.flags = 0;
    gfx.throwMatrix = null;

    vec3s_set(m.faceAngle, 0, faceYaw, 0);
    vec3s_set(m.angleVel, 0, 0, 0);
    m.pos[0] = pos[0];
    m.pos[1] = pos[1];
    m.pos[2] = pos[2];
    m.vel[0] = m.vel[1] = m.vel[2] = 0;

    const f = m.world.find_floor(m.pos[0], m.pos[1], m.pos[2]);
    m.floorHeight = f.height;
    m.floor = f.surface;
    if (m.pos[1] < m.floorHeight) {
        m.pos[1] = m.floorHeight;
    }
    const c = m.world.find_ceil(m.pos[0], m.floorHeight + 80.0, m.pos[2]);
    m.ceilHeight = c.height;
    m.ceil = c.surface;
    m.peakHeight = m.pos[1];

    // (water spawn -> ACT_WATER_IDLE not ported)
    m.prevAction = 0;
    m.action = C.ACT_IDLE;

    mario_reset_bodystate(m);
    update_mario_info_for_cam(m);
    m.marioBodyState.punchState = 0;
    m.marioBodyState.torsoAngle[0] = m.marioBodyState.torsoAngle[1] = m.marioBodyState.torsoAngle[2] = 0;
    m.marioBodyState.headAngle[0] = m.marioBodyState.headAngle[1] = m.marioBodyState.headAngle[2] = 0;
    m.marioBodyState.capState = C.MARIO_HAS_DEFAULT_CAP_ON;
    m.marioObj.oMarioWalkingPitch = 0;
    m.marioObj.oMarioBurnTimer = 0;

    vec3f_copy(gfx.pos, m.pos);
    vec3s_set(gfx.angle, 0, m.faceAngle[1], 0);
}

/** One game tick (30 Hz). */
function updateMario(m, input) {
    // ---- controller (read_controller_inputs + adjust_analog_stick) ----
    const ctl = m.controller;
    const buttons = (input.buttons | 0) & 0xFFFF;
    ctl.rawStickX = clampRawStick(input.stickX);
    ctl.rawStickY = clampRawStick(input.stickY);
    ctl.buttonPressed = buttons & (buttons ^ ctl.buttonDown);
    ctl.buttonDown = buttons;
    adjust_analog_stick(ctl);

    if (input.cameraYaw !== undefined) {
        m.area.camera.yaw = s16(input.cameraYaw);
    }

    m.globalTimer = (m.globalTimer + 1) >>> 0;

    // The renderer clears throwMatrix after drawing the object each frame.
    m.marioObj.header.gfx.throwMatrix = null;

    execute_mario_action(m);

    m.flags >>>= 0;
    m.particleFlags >>>= 0;
    m.input &= 0xFFFF;

    // ---- rendering-time animation advance (geo_set_animation_globals) ----
    m.areaUpdateCounter = (m.areaUpdateCounter + 1) >>> 0;
    geo_advance_object_animation(m.marioObj.header.gfx.animInfo, m.areaUpdateCounter & 0xFFFF);
}
