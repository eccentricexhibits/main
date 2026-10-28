// Level of some parts (soloed) against the full mix, second by second.
// usage: node solo_level.js <page url> '<regex on track label>' [from_s] [to_s]
const { chromium } = require('playwright');
const [url, re, from = 0, to = 1e9] = process.argv.slice(2);
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url); await p.waitForFunction(() => S.banks.some(b => b.ready), null, { timeout: 90000 });
  console.log(await p.evaluate(async ([re, from, to]) => {
    const rms = ab => { const L = ab.getChannelData(0), sr = ab.sampleRate, out = [];
      for (let s = 0; s < Math.floor(L.length / sr); s++) { let ss = 0; for (let i = s * sr; i < (s + 1) * sr; i++) ss += L[i] * L[i]; out.push(10 * Math.log10(ss / sr + 1e-12)); } return out; };
    const ids = S.song.parts.filter(pt => new RegExp(re).test(trackLabel(pt))).map(pt => pt.index);
    S.ch.forEach((c, i) => c.solo = ids.includes(i)); const solo = rms(await renderSong());
    S.ch.forEach(c => c.solo = false); const all = rms(await renderSong());
    return 'parts: ' + ids.map(i => trackLabel(S.song.parts[i])).join(', ') + '\nsec: solo / mix / gap\n' +
      solo.map((d, i) => d > -70 && i >= from && i <= to ? `${i}:${d.toFixed(0)}/${all[i].toFixed(0)}/${(all[i] - d).toFixed(0)}` : null).filter(Boolean).join(' ');
  }, [re, +from, +to])); await b.close(); })();
