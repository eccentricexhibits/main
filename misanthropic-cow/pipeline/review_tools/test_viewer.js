// usage: node test_viewer.js <three.js node_modules dir> <screenshot dir>   (serve the viewer folder on :8765 first)
// 44B, the final model: one figure (the rounds and compare rows and the sidebar are gone).  Checks that the page opens
// on Idle (15.6 s) in daylight, that seeking works and the label names the Idle's beat, that every animation has both
// styles (the four mood clips gained brisk standard versions: Sit Cross-Legged 8.8 s standard, 11 s lumbering), and
// that clips play and blend; and that the loose-armed Idle (15.6 s) and Walk (1.12 s) are there.
const { chromium } = require('playwright');
const THREE_DIR = process.argv[2], OUT = process.argv[3] || '.';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 900, height: 1300 } });
  p.setDefaultTimeout(300000);           // software WebGL can stall the page for a while
  const errs = []; p.on('pageerror', e => errs.push('PAGE ' + e.message)); p.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) errs.push(m.text()); });
  await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: THREE_DIR + '/three/' + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  const shot = async (n) => { await p.waitForTimeout(2500); await (await p.$('#stage')).screenshot({ path: OUT + '/viewer_' + n + '.png', timeout: 240000 }); };
  await p.goto('http://localhost:8765/index.html');
  await p.waitForFunction(() => document.getElementById('status').hidden, null, { timeout: 600000 });
  console.log('clip:', await p.$eval('#clips button[aria-pressed="true"]', e => e.dataset.clip),
              '| Idle length:', await p.$eval('#scrub', e => e.max),
              '| light:', await p.$eval('#lights button[aria-pressed="true"]', e => e.dataset.light),
              '| rounds row:', !!(await p.$('#versions')), '| compare row:', !!(await p.$('#layout')), '| sidebar:', !!(await p.$('aside')));
  await shot('44b_idle');
  // Idle: seek to 11 s (the foot tap) and read the time and the beat back
  await p.click('#play');
  await p.$eval('#scrub', e => { e.value = '11.0'; e.dispatchEvent(new Event('input')); });
  await p.waitForTimeout(8000);           // software WebGL can drop to a frame a second; the readout updates on the next frame
  console.log('Idle time after seeking to 11 s:', await p.$eval('#time', e => e.textContent), '|', await p.$eval('#phaseNow', e => e.textContent));
  await p.click('#play');
  for (const c of ['Depressed Walk', 'Sit Cross-Legged', 'Crying', 'Exasperated']) {
    for (const st of ['std', 'alt']) {
      await p.click(`button[data-style="${st}"]`); await p.click(`button[data-clip="${c}"]`); await p.waitForTimeout(1500);
      console.log(`${c} ${st}:`, await p.$eval('#scrub', e => e.max), 's |', await p.$eval('#styleNote', e => e.textContent));
    }
  }
  await p.click('button[data-style="std"]');
  for (const c of ['Idle (loose)', 'Walk (loose)']) {       // the loose-armed versions (no lumbering version)
    await p.click(`button[data-clip="${c}"]`); await p.waitForTimeout(1500);
    console.log(`${c}:`, await p.$eval('#scrub', e => e.max), 's |', await p.$eval('#styleNote', e => e.textContent));
    await shot('44b_' + c.replace(/[ ()]/g, '_'));
  }
  for (const c of ['Sit Cross-Legged', 'Chicken Dance']) {
    await p.click(`button[data-clip="${c}"]`); await p.waitForTimeout(1500);
    await shot('44b_' + c.replace(/ /g, '_'));
  }
  console.log('errors:', errs.length ? errs : 'none');
  await b.close();
})();
