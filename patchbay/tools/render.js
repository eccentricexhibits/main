// Render a Patchbay page's song to WAV through its own Export button (headless Chromium).
// usage: node render.js <page url> <out.wav>
// Serve a folder holding the song's Patchbay.html plus a `sounds` folder (or symlink) with the
// generaluser-gs-{0,1,2}.b64.txt parts:  python3 -m http.server 8765 --bind 127.0.0.1
const { chromium } = require('playwright');
const [url, out] = process.argv.slice(2);
(async () => { const b = await chromium.launch(); const errs = [];
  const p = await b.newPage({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(url); await p.waitForFunction(() => S.banks.some(b => b.ready), null, { timeout: 90000 });
  console.log(await p.evaluate(() => S.song.name + ' | ' + $('#songInfo').textContent));
  // Big arrangements (the lush version: 52 parts, 20k notes) take over 8 minutes headless.
  const dl = p.waitForEvent('download', { timeout: 1800000 }); await p.click('#btnExport');
  await (await dl).saveAs(out); console.log('exported', out);
  console.log(errs.join('\n') || 'no errors'); await b.close(); })();
