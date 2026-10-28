// Melody vs. everything else in each verse: render the mix, render the melody parts soloed,
// subtract. Prints "melody minus rest" in dB (the user's preferred values are in HANDOFF.md).
// usage: node verse_balance.js [--k] <page url>     (--k = K-weighted, BS.1770 shelf + high-pass)
// Verse windows assume the song's opening tempo (156 BPM, constant until bar 57).
const { chromium } = require('playwright');
const args = process.argv.slice(2); const KW = args[0] === '--k'; const url = args[KW ? 1 : 0];
const W = [['verse 1', 7, 13, ['Violoncello']], ['verse 2', 21, 27, ['Viola', 'Horn 1·2 in F']],
           ['verse 3', 40, 46, ['Violoncello', 'Bassoon 1·2']]];
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url); await p.waitForFunction(() => S.banks.some(b => b.ready), null, { timeout: 90000 });
  const r = await p.evaluate(async ([KW, W]) => {
    const bar = b => (b - 1) * 4 * 60 / 156;
    const render = async ids => { S.ch.forEach((c, i) => c.solo = ids ? ids.includes(i) : false); const ab = await renderSong();
      return [ab.getChannelData(0).slice(), ab.getChannelData(1).slice(), ab.sampleRate]; };
    const [AL0, AR0, sr] = await render(null);
    const bq = (x, b0, b1, b2, a0, a1, a2) => { const y = new Float32Array(x.length); let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
      for (let i = 0; i < x.length; i++) { const v = (b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2) / a0; x2 = x1; x1 = x[i]; y2 = y1; y1 = v; y[i] = v; } return y; };
    const shelf = x => { const A = Math.pow(10, 4 / 40), w = 2 * Math.PI * 1500 / sr, c = Math.cos(w), al = Math.sin(w) / 2 * Math.SQRT2, s = 2 * Math.sqrt(A) * al;
      return bq(x, A * ((A + 1) + (A - 1) * c + s), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - s), (A + 1) - (A - 1) * c + s, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - s); };
    const hp = x => { const w = 2 * Math.PI * 38 / sr, c = Math.cos(w), al = Math.sin(w); return bq(x, (1 + c) / 2, -(1 + c), (1 + c) / 2, 1 + al, -2 * c, 1 - al); };
    const K = x => KW ? hp(shelf(x)) : x; const AL = K(AL0), AR = K(AR0); const out = [];
    for (const [name, b0, b1, labels] of W) {
      const ids = S.song.parts.filter(pt => labels.includes(trackLabel(pt))).map(pt => pt.index);
      const [ML0, MR0] = await render(ids); const ML = K(ML0), MR = K(MR0);
      let m = 0, o = 0; const i0 = Math.round(bar(b0) * sr), i1 = Math.round(bar(b1) * sr);
      for (let i = i0; i < i1; i++) { m += ML[i] ** 2 + MR[i] ** 2; o += (AL[i] - ML[i]) ** 2 + (AR[i] - MR[i]) ** 2; }
      out.push(`${name} (bars ${b0}-${b1 - 1}, ${labels.join('+')}): melody minus rest ${(10 * Math.log10(m / o)).toFixed(1)} dB`);
    }
    return out; }, [KW, W]);
  r.forEach(x => console.log(x)); await b.close(); })();
