// usage: node test_viewer.js <three.js node_modules dir> <screenshot dir>   (serve the viewer folder on :8765 first)
// Round 42: the viewer holds rounds 41 and 42.  Checks that it opens on round 42 with Idle (20 s), plays clips, shows
// round 41 beside it, that Idle runs past round 41's 8 s and that the label names the Idle's beat.
const { chromium } = require('playwright');
const THREE_DIR = process.argv[2], OUT = process.argv[3] || '.';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 900, height: 1300 } });
  const errs = []; p.on('pageerror', e => errs.push('PAGE ' + e.message)); p.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) errs.push(m.text()); });
  await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: THREE_DIR + '/three/' + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  const shot = async (n) => { await p.waitForTimeout(2500); await (await p.$('#stage')).screenshot({ path: OUT + '/viewer_' + n + '.png', timeout: 240000 }); };
  const ready = () => p.waitForFunction(() => document.getElementById('status').hidden && !document.querySelector('#versions button').disabled, null, { timeout: 600000 });
  const rounds = () => p.$$eval('#versions button[data-round][aria-pressed="true"]', bs => bs.map(x => x.dataset.round).join(' '));
  await p.goto('http://localhost:8765/index.html');
  await p.waitForFunction(() => document.querySelector('button[data-round="r42"]').getAttribute('aria-pressed') === 'true' && document.getElementById('status').hidden, null, { timeout: 600000 });
  console.log('opened on:', await rounds(), '| clip:', await p.$eval('#clips button[aria-pressed="true"]', e => e.dataset.clip),
              '| Idle length:', await p.$eval('#scrub', e => e.max));
  await shot('r42_idle');
  await p.click('button[data-round="r41"]'); await ready();
  console.log('with 41:', await rounds(), '|', await p.$eval('#verNote', e => e.textContent));
  // Idle past 8 s: seek to 11 s (the hoof check) and read the time and the beat back
  await p.click('#play');
  await p.$eval('#scrub', e => { e.value = '11.0'; e.dispatchEvent(new Event('input')); });
  await p.waitForTimeout(3000);           // software WebGL draws slowly; the readout updates on the next frame
  console.log('Idle time after seeking to 11 s:', await p.$eval('#time', e => e.textContent), '|', await p.$eval('#phaseNow', e => e.textContent));
  await shot('r41_r42_idle_11s');
  for (const c of ['Exasperated', 'Chicken Dance']) {
    await p.click(`button[data-clip="${c}"]`); await p.waitForTimeout(1500);
    await shot('r41_r42_' + c.replace(/ /g, '_'));
  }
  console.log('errors:', errs.length ? errs : 'none');
  await b.close();
})();
