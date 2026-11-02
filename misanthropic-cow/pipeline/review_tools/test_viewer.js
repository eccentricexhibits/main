// usage: node test_viewer.js <three.js node_modules dir> <screenshot dir>   (serve the viewer folder on :8765 first)
const { chromium } = require('playwright');
const THREE_DIR = process.argv[2], OUT = process.argv[3] || '.';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 900, height: 1300 } });
  const errs = []; p.on('pageerror', e => errs.push('PAGE ' + e.message)); p.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) errs.push(m.text()); });
  await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: THREE_DIR + '/three/' + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  const shot = async (n) => { await p.waitForTimeout(2500); await (await p.$('#stage')).screenshot({ path: OUT + '/viewer_' + n + '.png', timeout: 240000 }); };
  const pressed = sel => p.$eval(sel, e => e.getAttribute('aria-pressed') === 'true');
  const ready = () => p.waitForFunction(() => document.getElementById('status').hidden && !document.querySelector('#versions button').disabled, null, { timeout: 400000 });
  const rounds = () => p.$$eval('#versions button[data-round][aria-pressed="true"]', bs => bs.map(x => x.dataset.round).join(' '));
  const shown = sel => p.$eval(sel, e => getComputedStyle(e).display !== 'none');

  // opens on round 25 alone, with Idle selected and the Chicken Dance's controls hidden
  await p.goto('http://localhost:8765/index.html');
  await p.waitForFunction(() => document.querySelector('button[data-round="r32"]').getAttribute('aria-pressed') === 'true' && document.getElementById('status').hidden, null, { timeout: 400000 });
  console.log('opened on:', await rounds(), '|', await p.$eval('#verNote', e => e.textContent.slice(0, 40)));
  console.log('opening clip:', await p.$eval('#clips button[aria-pressed="true"]', e => e.dataset.clip),
    '| dance rows shown?', await shown('#phases'), await shown('#ticks'),
    '| layout disabled with one round?', await p.$eval('button[data-layout="side"]', e => e.disabled));

  // rounds 17 and 18 together, playing Idle side by side
  await p.click('button[data-round="r32"]'); await p.waitForTimeout(300);
  console.log('cannot remove the last round:', await rounds());
  await p.click('button[data-round="r18"]'); await ready();
  await p.click('button[data-round="r17"]'); await ready();
  console.log('all three picked:', await rounds());
  await p.click('button[data-round="r32"]'); await ready();
  console.log('round 32 taken away:', await rounds());
  console.log('17 + 18:', await p.$eval('#verNote', e => e.textContent), '| height lines on?', await pressed('#guides'));
  await shot('r17_r18_idle');

  // all three side by side, then overlaid, in the default pose
  await p.click('button[data-round="r32"]'); await ready();
  await p.click('#play'); await p.click('button[data-clip="__pose"]');
  console.log('three:', await rounds(), '|', await p.$eval('#verNote', e => e.textContent));
  await shot('side_three');
  // all four, then round 25 against round 26 (the hood fix)
  await p.click('button[data-round="r25"]'); await ready();
  console.log('four:', await rounds()); await shot('side_four');
  for (const k of ['r28', 'r29', 'r30', 'r31']) { await p.click(`button[data-round="${k}"]`); await ready(); }
  console.log('eight:', await rounds()); await shot('side_eight');
  for (const k of ['r28', 'r29', 'r30', 'r31']) { await p.click(`button[data-round="${k}"]`); await ready(); }
  await p.click('button[data-round="r17"]'); await ready(); await p.click('button[data-round="r18"]'); await ready();
  await p.click('button[data-view="side"]'); console.log('25 + 32:', await rounds()); await shot('r25_r32_side');
  await p.click('button[data-view="back"]'); await shot('r25_r32_back'); await p.click('button[data-view="front"]');
  await p.click('button[data-round="r17"]'); await ready(); await p.click('button[data-round="r18"]'); await ready();
  await p.click('button[data-round="r25"]'); await ready();
  console.log('back to three:', await rounds());
  await p.click('button[data-layout="overlay"]'); await ready();
  console.log('overlay:', await p.$eval('#verNote', e => e.textContent), '| label:', await p.$eval('#lab32', e => e.textContent));
  await shot('overlay_three');
  await p.click('button[data-round="r18"]'); await ready();
  console.log('overlay 17 + 32:', await p.$eval('#verNote', e => e.textContent));
  await p.click('button[data-layout="side"]'); await ready();

  // the Chicken Dance's own controls appear with it
  await p.click('button[data-clip="Chicken Dance"]');
  console.log('dance rows shown for the dance?', await shown('#phases'), await shown('#ticks'));
  await p.click('button[data-clip="__pose"]');

  // round 25 alone: arms raised, the lighting rigs and the backdrops
  await p.click('button[data-round="r17"]'); await ready();
  console.log('alone again:', await rounds(), '| arms disabled?', await p.$eval('#arms', e => e.disabled));
  await p.click('#arms');
  await p.waitForFunction(() => document.getElementById('arms').getAttribute('aria-pressed') === 'true' && document.getElementById('status').hidden, null, { timeout: 400000 });
  await shot('arms');
  console.log('label', await p.$eval('#lab32', e => e.textContent));
  for (const L of ['daylight', 'golden', 'night', 'stage', 'backlit']) { await p.click('button[data-light="' + L + '"]'); await shot(L); }
  await p.click('button[data-light="studio"]');
  await p.$eval('#lightTurn', e => { e.value = 90; e.dispatchEvent(new Event('input')); });
  await p.click('#shadows'); await shot('studio_turn_shadow');
  await p.click('button[data-bg="dark"]'); await shot('dark_bg');
  await p.click('#lightReset'); await p.click('#arms');
  await p.click('button[data-round="r18"]'); await ready(); await p.click('button[data-round="r32"]'); await ready();
  console.log('round 18 alone:', await rounds(), '| arms disabled?', await p.$eval('#arms', e => e.disabled));
  console.log('errors:', errs.slice(0, 8));
  await b.close();
})();
