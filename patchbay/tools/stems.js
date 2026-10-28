// Level of groups of parts (soloed) in bar windows, plus the mix: RMS and the band under 120 Hz, in dB.
// usage: node stems.js <page url> <bpm> '{"group": "regex on track label"}' '[["name", first bar, bar after last]]'
// Bar windows assume a constant tempo; use trim.py for a short, fast excerpt.
const { chromium } = require('playwright');
const [url, bpm, G, W] = process.argv.slice(2); const groups = JSON.parse(G), wins = JSON.parse(W);
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url); await p.waitForFunction(() => S.banks.some(b => b.ready), null, { timeout: 90000 });
  const r = await p.evaluate(async ([bpm, groups, wins]) => {
    const bar = b => (b - 1) * 4 * 60 / bpm;
    const meas = async ids => { S.ch.forEach((c, i) => c.solo = ids ? ids.includes(i) : false); const ab = await renderSong();
      const L = ab.getChannelData(0), R = ab.getChannelData(1), sr = ab.sampleRate;
      // high-pass ~60 Hz + shelf approx skipped: plain RMS, plus a sub-band (<120 Hz) measure via one-pole lowpass
      return wins.map(([n, b0, b1]) => { let s = 0, lo = 0, y = 0; const i0 = Math.round(bar(b0) * sr), i1 = Math.min(L.length, Math.round(bar(b1) * sr)); const a = Math.exp(-2 * Math.PI * 120 / sr);
        for (let i = i0; i < i1; i++) { const x = (L[i] + R[i]) / 2; s += L[i] * L[i] + R[i] * R[i]; y = (1 - a) * x + a * y; lo += y * y * 2; }
        const n_ = i1 - i0; return [(10 * Math.log10(s / n_ + 1e-12)).toFixed(1), (10 * Math.log10(lo / n_ + 1e-12)).toFixed(1)]; }); };
    const out = { MIX: await meas(null) };
    for (const [g, re] of Object.entries(groups)) { const ids = S.song.parts.filter(pt => new RegExp(re).test(trackLabel(pt))).map(pt => pt.index); out[g + '(' + ids.length + ')'] = await meas(ids); }
    return out; }, [+bpm, groups, wins]);
  console.log('group'.padEnd(22) + wins.map(w => (w[0] + ' rms/sub').padStart(16)).join(''));
  for (const [g, v] of Object.entries(r)) console.log(g.padEnd(22) + v.map(([a, l]) => (a + '/' + l).padStart(16)).join(''));
  await b.close(); })();
