// Headless physics test for the Mario port.
//
//   ROM=/path/to/sm64.us.z64 node tests/physics/run.mjs
//
// The ROM is only used to read Mario's animation headers (frame counts/flags),
// which the movement code depends on for timings. Without ROM the test is skipped.

import fs from 'node:fs';
import { buildTestWorld, LEDGE_H, RAMP_H, DEATH_Y } from './test_world.mjs';
import { loadMarioAnimHeaders } from './rom_anims.mjs';
import { createMario, actionName, A_BUTTON, B_BUTTON, Z_TRIG } from '../../src/mario/index.js';
import * as C from '../../src/mario/constants.js';
import { ANIM_NAMES } from '../../src/mario/anim_ids.js';
import { sins, coss, atan2s, gSineTable, gArctanTable } from '../../src/engine/math_util.js';

const ROM = process.env.ROM;
if (!ROM || !fs.existsSync(ROM)) {
    console.log('SKIP: set ROM=/path/to/sm64.us.z64 to run the physics tests');
    process.exit(0);
}

const VERBOSE = !!process.env.VERBOSE;
const animations = loadMarioAnimHeaders(ROM);
const world = buildTestWorld();

let failures = 0;
let passes = 0;
function check(name, cond, detail = '') {
    if (cond) {
        passes++;
        console.log(`  ok   ${name}${detail ? '  (' + detail + ')' : ''}`);
    } else {
        failures++;
        console.log(`  FAIL ${name}${detail ? '  (' + detail + ')' : ''}`);
    }
}

// Camera yaw such that pushing the stick up moves Mario toward `yaw`.
const camFor = (yaw) => ((yaw - 0x8000) << 16) >> 16;
const YAW_PZ = 0;        // +z
const YAW_PX = 0x4000;   // +x
const YAW_NX = -0x4000;  // -x

const sounds = [];

function newMario(pos, yaw) {
    const m = createMario({ world, animations, sound: (name, extra) => sounds.push(name) });
    m.reset(pos, yaw);
    m.log = [actionName(m.action)];
    m.onActionChange = (a) => {
        m.log.push(actionName(a));
    };
    m.frame = 0;
    return m;
}

/** Run frames; `fn(m, i)` returns { stickY, stickX, buttons, cameraYaw } or null to stop. */
function run(m, n, fn) {
    for (let i = 0; i < n; i++) {
        const inp = fn(m, i);
        if (inp === null) break;
        m.update(inp);
        m.frame++;
        if (VERBOSE) {
            console.log(`    f${m.frame} ${actionName(m.action)} pos=${m.pos.map((v) => v.toFixed(1))} fv=${m.forwardVel.toFixed(2)} vy=${m.vel[1].toFixed(1)} anim=${ANIM_NAMES[m.marioObj.header.gfx.animInfo.animID]}:${m.marioObj.header.gfx.animInfo.animFrame}`);
        }
    }
}

function compress(log) {
    const out = [];
    for (const a of log) if (out[out.length - 1] !== a) out.push(a);
    return out.map((s) => s.replace(/^ACT_/, '')).join(' > ');
}

function scenario(title, f) {
    console.log(`\n== ${title}`);
    f();
}

const hold = (cam, extra = {}) => ({ stickX: 0, stickY: 80, buttons: 0, cameraYaw: cam, ...extra });
const none = (cam = 0, extra = {}) => ({ stickX: 0, stickY: 0, buttons: 0, cameraYaw: cam, ...extra });

// ---------------------------------------------------------------------------
scenario('trig / atan2s sanity', () => {
    check('sins(0x4000) == 1', sins(0x4000) === 1);
    check('coss(0x8000) == -1', coss(0x8000) === -1);
    check('sine table size 0x1400', gSineTable.length === 0x1400);
    check('arctan table end == 0x2000', gArctanTable[0x400] === 0x2000);
    check('atan2s(1,0) == 0 (+z)', atan2s(1, 0) === 0);
    check('atan2s(0,1) == 0x4000 (+x)', atan2s(0, 1) === 0x4000);
    check('atan2s(-1,0) == -0x8000', atan2s(-1, 0) === -0x8000);
    check('atan2s(0,-1) == -0x4000', atan2s(0, -1) === -0x4000);
});

// ---------------------------------------------------------------------------
scenario('collision queries', () => {
    const f = world.find_floor(100, 50, 100);
    check('flat floor height 0', f.surface !== null && f.height === 0, `h=${f.height}`);
    const r = world.find_floor(2816, 1000, 0);
    check('ramp height at middle ~300', Math.abs(r.height - RAMP_H / 2) < 1.5, `h=${r.height.toFixed(2)} ny=${r.surface && r.surface.normal.y.toFixed(4)}`);
    const d = world.find_floor(-3800, 0, 0);
    check('death plane below hole', d.surface && d.surface.type === C.ACT_UNINITIALIZED + 0x0A && d.height === DEATH_Y, `h=${d.height}`);
    const pos = [-1480, 0, 1750];
    const n = world.f32_find_wall_collision(pos, 60, 50);
    check('wall pushes out to radius', n === 1 && Math.abs(pos[0] - (-1450)) < 1e-3, `x=${pos[0]}`);
    const c = world.find_ceil(750, 100, -2750);
    check('hangable ceiling found', c.surface !== null && c.height === 400, `h=${c.height}`);
    const oob = world.find_floor(9000, 0, 0);
    check('out of bounds floor is null / -11000', oob.surface === null && oob.height === -11000);
});

// ---------------------------------------------------------------------------
scenario('idle -> walking -> running speed', () => {
    const m = newMario([0, 0, -3500], YAW_PZ);
    run(m, 5, () => none());
    check('spawns idle', m.action === C.ACT_IDLE);
    let maxFv = 0;
    run(m, 75, () => hold(camFor(YAW_PZ)));
    maxFv = m.forwardVel;
    check('walking action', m.action === C.ACT_WALKING);
    check('forwardVel ~32 after 75 frames', Math.abs(m.forwardVel - 32) < 1.5, `fv=${m.forwardVel.toFixed(2)}`);
    check('running animation', m.marioObj.header.gfx.animInfo.animID === ANIM_NAMES.indexOf('MARIO_ANIM_RUNNING'));
    check('moved along +z only', Math.abs(m.pos[0]) < 1e-6 && m.pos[2] > -2000, `pos=${m.pos.map((v) => v.toFixed(1))}`);
    // release: braking / decelerating then idle
    run(m, 60, () => none(camFor(YAW_PZ)));
    check('stops to idle after releasing stick', m.action === C.ACT_IDLE, compress(m.log));
    console.log('  actions:', compress(m.log), ' maxFv', maxFv.toFixed(2));
});

// ---------------------------------------------------------------------------
scenario('single jump apex (standing, A held)', () => {
    const m = newMario([0, 0, -3500], YAW_PZ);
    run(m, 3, () => none());
    let apex = 0, frames = 0, vy0 = null;
    run(m, 60, (mm, i) => {
        if (i > 0 && mm.action !== C.ACT_JUMP) return null;
        return none(0, { buttons: A_BUTTON });
    });
    // collect apex during the jump with A held
    const m2 = newMario([0, 0, -3500], YAW_PZ);
    run(m2, 3, () => none());
    run(m2, 80, (mm, i) => {
        if (mm.action === C.ACT_JUMP) { apex = Math.max(apex, mm.pos[1]); frames++; if (vy0 === null) vy0 = mm.vel[1] + 4; }
        if (i > 1 && mm.action !== C.ACT_JUMP && mm.action !== C.ACT_IDLE) return null;
        return none(0, { buttons: A_BUTTON });
    });
    check('initial vy 42', vy0 === 42, `vy0=${vy0}`);
    check('apex ~242 (42+38+...+2)', Math.abs(apex - 242) < 1, `apex=${apex.toFixed(2)}`);
    check('airtime ~22 frames', frames >= 20 && frames <= 24, `frames=${frames}`);
    run(m2, 20, () => none());
    console.log('  actions:', compress(m2.log));
    check('lands: JUMP_LAND -> JUMP_LAND_STOP -> IDLE', compress(m2.log).includes('JUMP > JUMP_LAND > JUMP_LAND_STOP > IDLE'));

    // short hop: A released immediately -> vy /= 4 while > 20
    const m3 = newMario([0, 0, -3500], YAW_PZ);
    run(m3, 3, () => none());
    let apex3 = 0;
    run(m3, 40, (mm, i) => { apex3 = Math.max(apex3, mm.pos[1]); return none(0, { buttons: i === 0 ? A_BUTTON : 0 }); });
    check('releasing A gives a lower jump', apex3 < apex - 50, `apex=${apex3.toFixed(1)}`);
});

// ---------------------------------------------------------------------------
scenario('running jump / double / triple jump chain', () => {
    const m = newMario([0, 0, -3800], YAW_PZ);
    run(m, 45, () => hold(camFor(YAW_PZ)));
    const fvBefore = m.forwardVel;
    let pressed = false;
    const apexes = {};
    const vy0 = {};
    let lastAction = m.action;
    run(m, 200, (mm, i) => {
        const a = mm.action;
        if (a !== lastAction && (a === C.ACT_JUMP || a === C.ACT_DOUBLE_JUMP || a === C.ACT_TRIPLE_JUMP)) {
            vy0[actionName(a)] = mm.vel[1] + 4;
        }
        lastAction = a;
        if (a === C.ACT_JUMP || a === C.ACT_DOUBLE_JUMP || a === C.ACT_TRIPLE_JUMP) {
            apexes[actionName(a)] = Math.max(apexes[actionName(a)] || 0, mm.pos[1]);
        }
        if (a === C.ACT_TRIPLE_JUMP_LAND_STOP || a === C.ACT_IDLE) return null;
        let buttons = 0;
        if (i === 0) buttons = A_BUTTON;
        else if ((a === C.ACT_JUMP_LAND || a === C.ACT_DOUBLE_JUMP_LAND) && !pressed) { buttons = A_BUTTON; pressed = true; }
        else if (a === C.ACT_JUMP || a === C.ACT_DOUBLE_JUMP || a === C.ACT_TRIPLE_JUMP) {
            pressed = false;
            buttons = (mm.vel[1] > 0) ? A_BUTTON : 0;
        }
        return hold(camFor(YAW_PZ), { buttons });
    });
    const s = compress(m.log);
    console.log('  actions:', s);
    console.log('  fv before jump', fvBefore.toFixed(2), 'vy0', JSON.stringify(vy0), 'apex', JSON.stringify(Object.fromEntries(Object.entries(apexes).map(([k, v]) => [k, +v.toFixed(1)]))));
    check('JUMP > JUMP_LAND > DOUBLE_JUMP', s.includes('JUMP > JUMP_LAND > DOUBLE_JUMP'));
    check('DOUBLE_JUMP_LAND > TRIPLE_JUMP', s.includes('DOUBLE_JUMP_LAND > TRIPLE_JUMP'));
    check('triple jump lands', s.includes('TRIPLE_JUMP_LAND'));
    check('running jump vy0 = 42 + fv/4', vy0.ACT_JUMP !== undefined && Math.abs(vy0.ACT_JUMP - (42 + fvBefore / 4)) < 0.01, `vy0=${vy0.ACT_JUMP && vy0.ACT_JUMP.toFixed(2)}`);
    check('double jump vy0 in [52+5, 52+9]', vy0.ACT_DOUBLE_JUMP > 57 && vy0.ACT_DOUBLE_JUMP < 61, `vy0=${vy0.ACT_DOUBLE_JUMP && vy0.ACT_DOUBLE_JUMP.toFixed(2)}`);
    check('triple jump vy0 = 69', vy0.ACT_TRIPLE_JUMP === 69, `vy0=${vy0.ACT_TRIPLE_JUMP}`);
    check('triple jump highest', apexes.ACT_TRIPLE_JUMP > apexes.ACT_DOUBLE_JUMP && apexes.ACT_DOUBLE_JUMP > apexes.ACT_JUMP);
});

// ---------------------------------------------------------------------------
scenario('long jump', () => {
    const m = newMario([0, 0, -3800], YAW_PZ);
    run(m, 40, () => hold(camFor(YAW_PZ)));
    let startZ = null, endZ = null, vy0 = null, fv0 = null;
    run(m, 120, (mm, i) => {
        if (mm.action === C.ACT_LONG_JUMP && startZ === null) { startZ = mm.pos[2]; vy0 = mm.vel[1] + 2; fv0 = mm.forwardVel; }
        if (mm.action === C.ACT_LONG_JUMP_LAND && endZ === null) endZ = mm.pos[2];
        if (mm.action === C.ACT_LONG_JUMP_LAND_STOP || mm.action === C.ACT_CROUCHING) return null;
        // frame 0: Z (crouch slide), frame 1: Z + A (long jump)
        const buttons = (i === 0 ? Z_TRIG : 0) | (i === 1 ? Z_TRIG | A_BUTTON : 0) | (i > 1 && mm.vel[1] > 0 ? A_BUTTON : 0);
        return hold(camFor(YAW_PZ), { buttons });
    });
    console.log('  actions:', compress(m.log));
    check('CROUCH_SLIDE > LONG_JUMP > LONG_JUMP_LAND', compress(m.log).includes('CROUCH_SLIDE > LONG_JUMP > LONG_JUMP_LAND'));
    check('long jump vy0 = 30', vy0 === 30, `vy0=${vy0}`);
    check('long jump fv capped at 48', fv0 !== null && fv0 <= 48 && fv0 > 30, `fv0=${fv0 && fv0.toFixed(2)}`);
    check('long jump distance > 700', endZ - startZ > 700, `dist=${(endZ - startZ).toFixed(1)}`);
});

// ---------------------------------------------------------------------------
scenario('backflip', () => {
    const m = newMario([0, 0, -3500], YAW_PZ);
    run(m, 3, () => none());
    let apex = 0, startZ = m.pos[2], vy0 = null;
    run(m, 80, (mm, i) => {
        if (mm.action === C.ACT_BACKFLIP) { apex = Math.max(apex, mm.pos[1]); if (vy0 === null) vy0 = mm.vel[1] + 4; }
        if (mm.action === C.ACT_IDLE && i > 30) return null;
        let buttons = 0;
        if (i < 6) buttons = Z_TRIG;
        if (i === 6) buttons = Z_TRIG | A_BUTTON;
        if (i > 6 && mm.action === C.ACT_BACKFLIP) buttons = A_BUTTON;
        return none(0, { buttons });
    });
    console.log('  actions:', compress(m.log));
    check('START_CROUCHING > CROUCHING > BACKFLIP > BACKFLIP_LAND', compress(m.log).includes('CROUCHING > BACKFLIP > BACKFLIP_LAND'));
    check('backflip vy0 = 62', vy0 === 62, `vy0=${vy0}`);
    check('backflip apex ~512', Math.abs(apex - 512) < 10, `apex=${apex.toFixed(1)}`);
    check('moves backwards', m.pos[2] < startZ - 100, `dz=${(m.pos[2] - startZ).toFixed(1)}`);
});

// ---------------------------------------------------------------------------
scenario('side flip', () => {
    const m = newMario([0, 0, -3800], YAW_PZ);
    run(m, 30, () => hold(camFor(YAW_PZ)));
    let vy0 = null, yaw = null;
    run(m, 80, (mm, i) => {
        if (mm.action === C.ACT_SIDE_FLIP && vy0 === null) { vy0 = mm.vel[1] + 4; yaw = mm.faceAngle[1]; }
        if (mm.action === C.ACT_IDLE || mm.action === C.ACT_SIDE_FLIP_LAND_STOP) return null;
        // stick back (toward -z): turning around, then A
        const buttons = (mm.action === C.ACT_TURNING_AROUND && i > 1) ? A_BUTTON : (mm.action === C.ACT_SIDE_FLIP ? A_BUTTON : 0);
        return { stickX: 0, stickY: -80, buttons, cameraYaw: camFor(YAW_PZ) };
    });
    console.log('  actions:', compress(m.log));
    check('WALKING > TURNING_AROUND > SIDE_FLIP > SIDE_FLIP_LAND', compress(m.log).includes('TURNING_AROUND > SIDE_FLIP > SIDE_FLIP_LAND'));
    check('side flip vy0 = 62', vy0 === 62, `vy0=${vy0}`);
    check('side flip faces the stick direction (-z)', yaw === -0x8000, `yaw=${yaw}`);
});

// ---------------------------------------------------------------------------
scenario('dive (running B)', () => {
    const m = newMario([0, 0, -3800], YAW_PZ);
    run(m, 45, () => hold(camFor(YAW_PZ)));
    let fv0 = null;
    run(m, 90, (mm, i) => {
        if (mm.action === C.ACT_DIVE && fv0 === null) fv0 = mm.forwardVel;
        if (mm.action === C.ACT_IDLE && i > 5) return null;
        return hold(camFor(YAW_PZ), { buttons: i === 0 ? B_BUTTON : 0, stickY: i < 3 ? 80 : 0 });
    });
    console.log('  actions:', compress(m.log));
    check('DIVE > DIVE_SLIDE > STOMACH_SLIDE_STOP > IDLE', compress(m.log).includes('DIVE > DIVE_SLIDE > STOMACH_SLIDE_STOP > IDLE'));
    check('dive speed = min(fv + 15, 48)', fv0 !== null && fv0 > 40 && fv0 <= 48, `fv0=${fv0 && fv0.toFixed(2)}`);
});

// ---------------------------------------------------------------------------
scenario('ground pound', () => {
    const m = newMario([0, 0, -3500], YAW_PZ);
    run(m, 3, () => none());
    run(m, 80, (mm, i) => {
        if (mm.action === C.ACT_IDLE && i > 10) return null;
        let buttons = 0;
        if (i < 8) buttons = A_BUTTON;
        if (i === 8) buttons = Z_TRIG;
        return none(0, { buttons });
    });
    console.log('  actions:', compress(m.log));
    check('JUMP > GROUND_POUND > GROUND_POUND_LAND > BUTT_SLIDE_STOP > IDLE', compress(m.log).includes('JUMP > GROUND_POUND > GROUND_POUND_LAND > BUTT_SLIDE_STOP > IDLE'));
    check('ground pound particles heard/landed on floor', Math.abs(m.pos[1]) < 1e-6);
});

// ---------------------------------------------------------------------------
scenario('punch / kick sequence', () => {
    const m = newMario([0, 0, -3500], YAW_PZ);
    run(m, 3, () => none());
    let t = 0;
    run(m, 60, (mm, i) => {
        if (mm.action === C.ACT_IDLE && i > 5) return null;
        // press B every 4 frames
        return none(0, { buttons: (i % 4 === 0) ? B_BUTTON : 0 });
    });
    console.log('  actions:', compress(m.log));
    check('PUNCHING then back to IDLE', compress(m.log).includes('IDLE > PUNCHING > IDLE'));
});

// ---------------------------------------------------------------------------
scenario('wall kick off the tall box', () => {
    // Tall box +x face is at x = -1500 (z in [1500, 2000]). Run toward -x and jump into it.
    let result = null;
    for (let jumpDist = 60; jumpDist <= 400 && !result; jumpDist += 20) {
        const m = newMario([-500, 0, 1750], YAW_NX);
        let jumped = false, aWasDown = false, kickVy = null;
        run(m, 160, (mm, i) => {
            if (mm.action === C.ACT_WALL_KICK_AIR && kickVy === null) kickVy = mm.vel[1] + 4;
            if (kickVy !== null && mm.action !== C.ACT_WALL_KICK_AIR) return null;
            let buttons = 0;
            if (!jumped && mm.pos[0] - (-1500) < jumpDist && mm.action === C.ACT_WALKING) { buttons = A_BUTTON; jumped = true; }
            else if (mm.action === C.ACT_AIR_HIT_WALL || (mm.prevAction === C.ACT_AIR_HIT_WALL && mm.action === C.ACT_SOFT_BONK)) buttons = aWasDown ? 0 : A_BUTTON;
            else if (mm.action === C.ACT_WALL_KICK_AIR) buttons = A_BUTTON;
            aWasDown = !!(buttons & A_BUTTON);
            return hold(camFor(YAW_NX), { buttons });
        });
        if (kickVy !== null) result = { m, jumpDist, kickVy };
    }
    check('wall kick performed', !!result, result ? `jump at ${result.jumpDist} units` : '');
    if (result) {
        console.log('  actions:', compress(result.m.log));
        check('AIR_HIT_WALL > WALL_KICK_AIR', compress(result.m.log).includes('AIR_HIT_WALL > WALL_KICK_AIR') || compress(result.m.log).includes('SOFT_BONK > WALL_KICK_AIR'));
        check('wall kick vy0 = 62', result.kickVy === 62, `vy0=${result.kickVy}`);
        check('kicked away from wall (+x)', Math.abs(((result.m.faceAngle[1] - YAW_PX) << 16) >> 16) < 0x2000, `yaw=${result.m.faceAngle[1]}`);
    }
});

// ---------------------------------------------------------------------------
scenario('crouch slide', () => {
    const m = newMario([0, 0, -3800], YAW_PZ);
    run(m, 40, () => hold(camFor(YAW_PZ)));
    const fv0 = m.forwardVel;
    run(m, 60, (mm, i) => {
        if (mm.action === C.ACT_CROUCHING) return null;
        return none(camFor(YAW_PZ), { buttons: Z_TRIG });
    });
    console.log('  actions:', compress(m.log));
    check('WALKING > CROUCH_SLIDE > CROUCHING', compress(m.log).includes('WALKING > CROUCH_SLIDE > CROUCHING'), `fv0=${fv0.toFixed(1)}`);
    // slide kick
    const m2 = newMario([0, 0, -3800], YAW_PZ);
    run(m2, 40, () => hold(camFor(YAW_PZ)));
    run(m2, 80, (mm, i) => {
        if (mm.action === C.ACT_CROUCHING || mm.action === C.ACT_IDLE) return null;
        return hold(camFor(YAW_PZ), { buttons: (i === 0 ? Z_TRIG : 0) | (i === 2 ? Z_TRIG | B_BUTTON : 0) | (i > 2 ? 0 : Z_TRIG) });
    });
    console.log('  slide kick actions:', compress(m2.log));
    check('CROUCH_SLIDE > SLIDE_KICK > SLIDE_KICK_SLIDE', compress(m2.log).includes('CROUCH_SLIDE > SLIDE_KICK > SLIDE_KICK_SLIDE'));
});

// ---------------------------------------------------------------------------
scenario('ledge grab on the box top edge', () => {
    // Ledge box -x face at x = 1500, z in [1500, 2000], top at y = LEDGE_H. Approach toward +x.
    let result = null;
    const tries = [];
    for (let jumpDist = 40; jumpDist <= 500 && !result; jumpDist += 10) {
        const m = newMario([700, 0, 1750], YAW_PX);
        let jumped = false;
        run(m, 200, (mm, i) => {
            if (mm.action === C.ACT_IDLE && mm.pos[1] === LEDGE_H) return null;
            let buttons = 0;
            if (!jumped && 1500 - mm.pos[0] < jumpDist && mm.action === C.ACT_WALKING) { buttons = A_BUTTON; jumped = true; }
            else if (mm.action === C.ACT_JUMP) buttons = A_BUTTON;
            // climb: keep holding forward on the ledge
            return hold(camFor(YAW_PX), { buttons });
        });
        if (m.log.includes('ACT_LEDGE_GRAB')) result = { m, jumpDist };
        else tries.push(jumpDist);
    }
    check('ledge grab happened', !!result, result ? `jump at ${result.jumpDist} units` : '');
    if (result) {
        const m = result.m;
        console.log('  actions:', compress(m.log));
        check('LEDGE_GRAB > LEDGE_CLIMB_SLOW > IDLE on top', compress(m.log).includes('LEDGE_GRAB > LEDGE_CLIMB_SLOW_1 > LEDGE_CLIMB_SLOW_2 > IDLE') && m.pos[1] === LEDGE_H, `y=${m.pos[1]} x=${m.pos[0].toFixed(1)}`);
    }
    // fast climb with A
    const m2 = newMario([1400, LEDGE_H - 140, 1750], YAW_PX);
    m2.action = C.ACT_FREEFALL;
    let grabbed = false;
    run(m2, 80, (mm, i) => {
        if (mm.action === C.ACT_IDLE && mm.pos[1] === LEDGE_H) return null;
        if (mm.action === C.ACT_LEDGE_GRAB) grabbed = true;
        return { stickX: 0, stickY: 30, buttons: (mm.action === C.ACT_LEDGE_GRAB && mm.actionTimer === 3) ? A_BUTTON : 0, cameraYaw: camFor(YAW_PX) };
    });
    console.log('  fast climb actions:', compress(m2.log));
    check('LEDGE_GRAB > LEDGE_CLIMB_FAST > IDLE', compress(m2.log).includes('LEDGE_GRAB > LEDGE_CLIMB_FAST > IDLE') && m2.pos[1] === LEDGE_H);
});

// ---------------------------------------------------------------------------
scenario('steep slope slide', () => {
    // Ramp rises along +x (x in [2560, 3072]); stand Mario on it facing uphill.
    const m = newMario([2900, 1000, 0], YAW_PX);
    const y0 = m.pos[1];
    run(m, 150, (mm) => (mm.action === C.ACT_IDLE && mm.frame > 20 ? null : none()));
    console.log('  actions:', compress(m.log));
    check('starts on the ramp', y0 > 300, `y0=${y0.toFixed(1)}`);
    check('slides (STOMACH_SLIDE or BUTT_SLIDE)', m.log.includes('ACT_STOMACH_SLIDE') || m.log.includes('ACT_BUTT_SLIDE'));
    check('ends at the bottom, downhill (-x)', m.pos[1] === 0 && m.pos[0] < 2560, `pos=${m.pos.map((v) => v.toFixed(1))}`);
    // walking up the steep slope is not possible: jump on slope -> steep jump
    const m2 = newMario([2700, 1000, 0], YAW_PX);
    run(m2, 1, () => none());
    run(m2, 30, (mm, i) => hold(camFor(YAW_PX), { buttons: i === 0 ? A_BUTTON : 0 }));
    console.log('  jump on slope actions:', compress(m2.log));
    check('cannot walk up: slides back', m2.log.includes('ACT_STOMACH_SLIDE') || m2.log.includes('ACT_BUTT_SLIDE') || m2.log.includes('ACT_STEEP_JUMP') || m2.log.includes('ACT_FREEFALL'));
});

// ---------------------------------------------------------------------------
scenario('lava boost (SURFACE_BURNING)', () => {
    const m = newMario([-2816, 0, -256], YAW_PZ);
    let vyMax = 0;
    const h0 = m.health;
    run(m, 6, (mm) => { vyMax = Math.max(vyMax, mm.vel[1]); return none(); });
    check('lava boost triggered', m.log.includes('ACT_LAVA_BOOST'), compress(m.log));
    check('boost vy ~84', vyMax >= 70, `vyMax=${vyMax.toFixed(1)}`);
    run(m, 300, (mm) => (mm.requestRespawn ? null : none()));
    console.log('  actions:', compress(m.log), ' health', h0.toString(16), '->', m.health.toString(16));
    check('standing in lava repeatedly kills Mario -> requestRespawn', m.requestRespawn === true);

    // escape the lava with the stick
    const m2 = newMario([-2816, 0, -256], YAW_PZ);
    run(m2, 120, (mm) => hold(camFor(YAW_PZ)));
    console.log('  escape actions:', compress(m2.log), ' health', m2.health.toString(16));
    check('escapes with damage (health 0x880 -> 0x580)', !m2.requestRespawn && m2.health === 0x580 && m2.log.includes('ACT_LAVA_BOOST_LAND'), `health=0x${m2.health.toString(16)}`);
});

// ---------------------------------------------------------------------------
scenario('death plane below the cliff', () => {
    const m = newMario([-3400, 0, 0], YAW_NX);
    let frames = 0;
    run(m, 200, (mm) => { frames++; return mm.requestRespawn ? null : hold(camFor(YAW_NX)); });
    console.log('  actions:', compress(m.log), ' y', m.pos[1].toFixed(1), 'frames', frames);
    check('walks off and falls', m.log.includes('ACT_FREEFALL'));
    check('requestRespawn when nearing the death plane', m.requestRespawn === true && m.pos[1] < DEATH_Y + 2048 + 100);
});

// ---------------------------------------------------------------------------
scenario('fall damage', () => {
    const m = newMario([0, 0, 3000], YAW_PZ);
    m.pos[1] = 1400; m.action = C.ACT_FREEFALL; m.peakHeight = 1400;
    run(m, 60, (mm) => (mm.action === C.ACT_IDLE ? null : none()));
    console.log('  actions:', compress(m.log), ' health 0x' + m.health.toString(16));
    check('1400 unit fall: damaged (3 wedges = 0x880 - 8*0x40)', m.health === 0x880 - 8 * 0x40, `health=0x${m.health.toString(16)}`);
    const m2 = newMario([0, 0, 3000], YAW_PZ);
    m2.pos[1] = 3500; m2.action = C.ACT_FREEFALL; m2.peakHeight = 3500;
    run(m2, 150, (mm) => (mm.action === C.ACT_IDLE ? null : none()));
    console.log('  actions:', compress(m2.log), ' health 0x' + m2.health.toString(16));
    check('3500 unit fall: hard knockback', m2.log.includes('ACT_HARD_BACKWARD_GROUND_KB'));
});

// ---------------------------------------------------------------------------
scenario('hang from SURFACE_HANGABLE ceiling', () => {
    const m = newMario([750, 0, -2750], YAW_PZ);
    run(m, 2, () => none());
    run(m, 60, (mm, i) => (i > 40 ? null : none(0, { buttons: A_BUTTON })));
    console.log('  actions:', compress(m.log));
    check('START_HANGING > HANGING', compress(m.log).includes('JUMP > START_HANGING > HANGING'));
    run(m, 30, () => hold(camFor(YAW_PZ), { buttons: A_BUTTON }));
    check('HANG_MOVING with stick', m.log.includes('ACT_HANG_MOVING'));
    run(m, 30, () => none());
    console.log('  actions:', compress(m.log));
    check('releasing A drops', m.log.includes('ACT_FREEFALL'));
});

// ---------------------------------------------------------------------------
scenario('sleeping sequence', () => {
    const m = newMario([0, 0, -1000], YAW_PZ);
    run(m, 2000, (mm) => (mm.action === C.ACT_SLEEPING && mm.actionState === 2 ? null : none()));
    console.log('  actions:', compress(m.log), ' frames', m.frame);
    check('falls asleep', m.log.includes('ACT_SLEEPING'));
    run(m, 30, () => hold(camFor(YAW_PZ)));
    check('wakes up and walks', compress(m.log).includes('SLEEPING > WAKING_UP > IDLE') || compress(m.log).includes('SLEEPING > WAKING_UP'));
    console.log('  actions:', compress(m.log));
});

// ---------------------------------------------------------------------------
scenario('animation frame advance', () => {
    const m = newMario([0, 0, -1000], YAW_PZ);
    run(m, 1, () => none());
    const ai = m.marioObj.header.gfx.animInfo;
    check('idle anim set, frame 0 after first tick', ai.animID === ANIM_NAMES.indexOf('MARIO_ANIM_IDLE_HEAD_LEFT') && ai.animFrame === 0, `id=${ai.animID} frame=${ai.animFrame}`);
    run(m, 5, () => none());
    check('advances one frame per tick', ai.animFrame === 5, `frame=${ai.animFrame}`);
    check('marioBodyState populated', m.marioBodyState.capState === C.MARIO_HAS_DEFAULT_CAP_ON && m.marioBodyState.eyeState === C.MARIO_EYES_BLINK);
});

console.log(`\n${passes} passed, ${failures} failed`);
console.log(`sounds heard: ${[...new Set(sounds)].length} distinct (e.g. ${[...new Set(sounds)].slice(0, 8).join(', ')})`);
process.exit(failures ? 1 : 0);
