// usage: node test_viewer.js <three.js node_modules dir> <screenshot dir>   (serve the viewer folder on :8765 first)
const { chromium } = require('playwright');
const THREE_DIR = process.argv[2], OUT = process.argv[3] || '.';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 900, height: 1300 } });
  const errs = []; p.on('pageerror', e => errs.push('PAGE ' + e.message)); p.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) errs.push(m.text()); });
  await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: THREE_DIR + '/three/' + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await p.goto('http://localhost:8765/index.html');
  await p.waitForFunction(() => document.querySelector('button[data-ver="r24"]').getAttribute('aria-pressed') === 'true' && document.getElementById('status').hidden, null, { timeout: 400000 });
  console.log('opened:', await p.$eval('#verNote', e => e.textContent.slice(0, 50)), 'arms disabled?', await p.$eval('#arms', e => e.disabled));
  await p.click('#play'); await p.click('button[data-clip="__pose"]');
  const shot = async (n) => { await p.waitForTimeout(2500); await (await p.$('#stage')).screenshot({ path: OUT + '/viewer_' + n + '.png', timeout: 240000 }); };
  await p.click('#arms');
  await p.waitForFunction(() => document.getElementById('arms').getAttribute('aria-pressed') === 'true' && document.getElementById('status').hidden, null, { timeout: 400000 });
  await shot('arms');
  console.log('label', await p.$eval('#lab24', e => e.textContent));
  for (const L of ['daylight', 'golden', 'night', 'stage', 'backlit']) { await p.click('button[data-light="' + L + '"]'); await shot(L); }
  await p.click('button[data-light="studio"]');
  await p.$eval('#lightTurn', e => { e.value = 90; e.dispatchEvent(new Event('input')); });
  await p.click('#shadows'); await shot('studio_turn_shadow');
  await p.click('button[data-bg="dark"]'); await shot('dark_bg');
  await p.click('#arms'); await p.click('button[data-ver="side"]');
  await p.waitForFunction(() => document.querySelector('button[data-ver="side"]').getAttribute('aria-pressed') === 'true', null, { timeout: 60000 });
  await p.click('#lightReset'); await shot('side');
  await p.click('button[data-ver="r18"]'); await p.waitForTimeout(500);
  console.log('arms disabled in r18:', await p.$eval('#arms', e => e.disabled));
  console.log('errors:', errs.slice(0, 8));
  await b.close();
})();
