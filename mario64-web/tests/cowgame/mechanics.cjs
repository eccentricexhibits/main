// Mechanics tests for Leave Me Alone. Serve the project root on :8642 (with the cow model in
// assets/), then: node tests/cowgame/mechanics.cjs   (needs the playwright package).
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 400, height: 300 } });
  page.on('pageerror', e => console.log('pageerror: ' + e.message + '\n' + (e.stack || '').split('\n').slice(0, 4).join('\n')));
  await page.goto('http://localhost:8642/cow.html');
  await page.waitForFunction(() => window.__cowgame, null, { timeout: 60000 });
  const results = await page.evaluate(() => {
    const G = window.__cowgame; const { cow, game, simulate } = G;
    game.paused = true;
    const out = [];
    const S = (ci, t) => simulate(ci, t);
    const st = () => `pos=(${cow.pos.toArray().map(Math.round)}) state=${cow.state} speed=${Math.round(cow.speed)}`;
    const check = (name, ok, extra = '') => out.push(`${ok ? 'PASS' : 'FAIL'} ${name} ${extra} | ${st()}`);
    const fwd = { mz: -1 };
    const reset = (p, yaw = Math.PI) => { cow.reset(p, yaw); S({}, 0.05); };
    const find = (cls) => game.objects.filter((o) => o.constructor.name === cls);

    // 1 top speed + acceleration time
    reset([0, 0, 850]); let t = 0; while (cow.speed < 370 && t < 3) { S(fwd, 1 / 60); t += 1 / 60; }
    check('reaches run speed', cow.speed >= 370, `in ${t.toFixed(2)}s`);
    // 2 hurdle: running jump clears a 70-high hurdle
    reset([0, 0, 250]); for (let i = 0; i < 300 && cow.pos.z > -100; i++) S(fwd, 1 / 60); S({ ...fwd, jump: true }, 0.3); S(fwd, 0.6);
    check('running hop clears hurdle', cow.pos.z < -230 && cow.state === 'ground');
    // 3 a plain hop can't reach the 230 box, a crouch-jump can
    reset([400, 0, -1050]); S({ jump: true }, 0.6); S({}, 0.5);
    check('plain hop does not reach 230 box', cow.pos.y < 10);
    reset([400, 0, -1050]); S({ crouch: true }, 0.55); S({ crouch: true, jump: true, mz: -0.6 }, 0.5); S({ jump: true, mz: -0.6 }, 0.3); S({}, 0.6);
    check('crouch-jump reaches 230 box', Math.abs(cow.pos.y - 230) < 2, `phones=${game.phones}`);
    // 4 fence: running bumps, stampede smashes
    const fence = find('Breakable').find((b) => b.size[0] === 1400);
    reset([0, 0, -1400]); S(fwd, 2.0);
    check('running does not break fence', !fence.broken && cow.pos.z > -2000);
    reset([0, 0, -1300]); S({ ...fwd, sprint: true }, 2.5);
    check('stampede smashes fence', fence.broken && cow.pos.z < -2050);
    // 5 bridge: keep moving and it holds; stand still and it drops
    reset([0, 0, -2550]); S(fwd, 3.2);
    check('crossing the bridge while moving', cow.pos.z < -3500 && cow.pos.y > -5 && cow.state !== 'sink');
    for (const p of find('CrumblePlank')) { p.gone = 0.001; } S({}, 0.1); // make sure planks are back
    reset([0, 0, -2550]); S(fwd, 0.7); S({}, 2.0);
    check('standing still on the bridge sinks her', cow.state === 'sink' || cow.pos.y < -60);
    // 6 cracked floor + spring + plateau
    reset([0, 0, -4470]); S({ jump: true }, 0.2); S({ jump: true, crouch: true }, 0.1); S({}, 0.6);
    const crack = find('CrackedFloor')[0];
    check('stomp breaks cracked floor', !crack.body.enabled);
    S({}, 0.5); // falls onto the spring and bounces
    const bounced = cow.state === 'air';
    let maxY = -999; for (let i = 0; i < 40; i++) { S({}, 1 / 60); maxY = Math.max(maxY, cow.pos.y); }
    check('spring bounce is small without stomp', bounced && maxY < 200, `maxY=${Math.round(maxY)}`);
    // after another small bounce, stomp onto the spring on the way down
    S({}, 0.3); S({ crouch: true }, 0.1); S({}, 0.4); S({ mz: -1 }, 1.0);
    check('stomp-spring launches onto the plateau', cow.pos.y > 440 && cow.pos.z < -4600);
    // 7 beam: running wobbles off, tiptoeing crosses
    reset([0, 450, -5150]); S(fwd, 3.0);
    check('running on the beam falls off', cow.pos.y < 400);
    reset([0, 450, -5150]); S({ ...fwd, sneak: true }, 9);
    check('tiptoeing across the beam', cow.pos.z < -6300 && cow.pos.y > 440, `phones=${game.phones}`);
    // 8 slope: steep slide down
    reset([0, 450, -6950]); let slid = false; for (let i = 0; i < 150; i++) { S({ mz: i < 30 ? -0.5 : 0 }, 1 / 60); slid = slid || cow.state === 'slide'; }
    check('slides down the slope', slid && cow.pos.y < 5 && cow.pos.z < -7350);
    // 9 raft sinks under her
    const raft = find('SinkingRaft')[0];
    reset([raft.object.position.x, raft.object.position.y + 50, raft.object.position.z]); S({}, 0.3);
    const onRaft = cow.floor && cow.floor.body === raft.body;
    S({}, 2.0);
    check('raft sinks with her on it', onRaft && (cow.state === 'sink' || raft.sink > 100), `sink=${Math.round(raft.sink)}`);
    // 10 plates open the gate
    const gate = find('Gate')[0]; const plates = find('PressurePlate');
    reset([plates[0].object.position.x, 30, plates[0].object.position.z]); S({}, 0.3);
    check('one plate does not open the gate', plates[0].pressed && !gate.opening);
    reset([plates[1].object.position.x, 30, plates[1].object.position.z]); S({}, 0.3);
    S({}, 2.5);
    check('both plates open the gate', gate.opening && gate.object.position.y > 300);
    // 11 terraces need crouch-jumps
    reset([0, 0, -9800]); S({ mz: -0.4 }, 0.6); S({ jump: true, mz: -0.4 }, 0.5); S({}, 0.5);
    check('plain hop does not climb a terrace', cow.pos.y < 5);
    reset([0, 0, -9840]); S({ crouch: true }, 0.55); S({ crouch: true, jump: true, mz: -0.5 }, 0.45); S({ jump: true, mz: -0.5 }, 0.35); S({}, 0.5);
    check('crouch-jump climbs a terrace', Math.abs(cow.pos.y - 200) < 2);
    // 12 falls: stumble and cry
    cow.reset([0, 500, 100], Math.PI, false); S({}, 0.7);
    const stumbled = cow.state === 'stumble';
    cow.reset([0, 1100, 100], Math.PI, false); S({}, 0.9);
    check('medium fall stumbles, big fall makes her cry', stumbled && cow.state === 'cry', `breakdowns=${game.breakdowns}`);
    // 13 couch
    reset([0, 600, -10550]); S({ mz: -0.5 }, 1.5);
    check('reaching the couch finishes', game.finished && cow.state === 'sit');
    return out;
  });
  console.log(results.join('\n'));
  await browser.close();
})();
