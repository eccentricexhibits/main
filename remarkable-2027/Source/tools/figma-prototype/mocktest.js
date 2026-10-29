// Runs code.js against a minimal mock of the Figma plugin API and checks what it builds.
const fs = require('fs'); const zlib = require('zlib');
let nid = 0; const all = {}; const errors = []; const pages = []; let closedMsg = null;
function node(type) {
  const n = {id: `${++nid}:1`, type, children: [], parent: null, x: 0, y: 0, width: 100, height: 100, fills: [], reactions: [], name: '',
    resize(w, h) { if (!(w > 0 && h > 0)) errors.push(`bad resize ${w}x${h} on ${n.name}`); n.width = w; n.height = h; },
    appendChild(c) { c.parent = n; n.children.push(c); },
    remove() { if (n.parent) n.parent.children = n.parent.children.filter(c => c !== n); delete all[n.id]; },
    async setReactionsAsync(r) { n.reactions = r; }};
  all[n.id] = n; return n;
}
const images = {}; const texts = []; const fontsLoaded = new Set();
global.figma = {
  createPage() { const p = node('PAGE'); p.flowStartingPoints = []; pages.push(p); return p; },
  async setCurrentPageAsync(p) { figma.currentPage = p; },
  createFrame() { return node('FRAME'); }, createRectangle() { return node('RECTANGLE'); }, createText() { const t = node('TEXT'); t.characters = ''; const chk = (a, b) => { if (!(a >= 0 && b <= t.characters.length && a < b)) errors.push(`bad text range ${a}-${b} of ${t.characters.length}: ${t.characters.slice(0, 30)}`); if (!fontsLoaded.has(JSON.stringify(t.fontName))) errors.push('font not loaded'); };
    for (const k of ['setRangeFontName', 'setRangeFontSize', 'setRangeLetterSpacing', 'setRangeLineHeight', 'setRangeTextCase', 'setRangeFills']) t[k] = (a, b, v) => { chk(a, b); if (k === 'setRangeFontName' && !fontsLoaded.has(JSON.stringify(v))) errors.push('range font not loaded ' + JSON.stringify(v)); };
    texts.push(t); return t; },
  async loadFontAsync(f) { if (process.env.NO_KARBON && f.family === 'Karbon') throw new Error('missing'); fontsLoaded.add(JSON.stringify(f)); },
  base64Decode(s) { return Buffer.from(s, 'base64'); },
  createImage(bytes) {
    // JPEG dimensions from SOF marker; Figma downscales images over 4096 px.
    let i = 2; let w = 0, h = 0; while (i < bytes.length) { if (bytes[i] !== 0xFF) break; const m = bytes[i + 1]; const len = bytes.readUInt16BE(i + 2); if (m >= 0xC0 && m <= 0xC2) { h = bytes.readUInt16BE(i + 5); w = bytes.readUInt16BE(i + 7); break; } i += 2 + len; }
    if (w > 4096 || h > 4096) errors.push(`image too large ${w}x${h}`);
    const hash = 'h' + Object.keys(images).length; images[hash] = {w, h}; return {hash};
  },
  notify() {}, viewport: {scrollAndZoomIntoView() {}}, closePlugin(m) { closedMsg = m; },
};
eval(fs.readFileSync(process.argv[2], 'utf8'));
setTimeout(() => {
  const frameOf = n => { while (n && !(n.parent && n.parent.type === 'PAGE')) n = n.parent; return n; };
  let hot = 0, byNav = {};
  for (const n of Object.values(all)) for (const r of n.reactions || []) for (const a of r.actions) {
    hot++; byNav[a.navigation || a.type] = (byNav[a.navigation || a.type] || 0) + 1;
    if (a.type === 'NODE') {
      const d = all[a.destinationId]; if (!d) { errors.push(`missing destination for ${n.name}`); continue; }
      if (a.navigation === 'SCROLL_TO' && frameOf(d) !== frameOf(n)) errors.push(`scroll target outside frame: ${n.name}`);
      if (a.navigation !== 'SCROLL_TO' && !(d.parent && d.parent.type === 'PAGE')) errors.push(`destination not top-level: ${n.name}`);
      if (frameOf(d).parent !== frameOf(n).parent) errors.push(`cross-page link: ${n.name}`);
    }
    // hotspot inside its frame bounds
    const f = frameOf(n); if (n.x < -1 || n.y < -1 || n.x + n.width > f.width + 1 || n.y + n.height > f.height + 1) errors.push(`hotspot outside frame: ${n.name} in ${f.name} (${Math.round(n.x)},${Math.round(n.y)},${Math.round(n.width)}x${Math.round(n.height)} vs ${f.width}x${f.height})`);
  }
  for (const p of pages) { for (const s of p.flowStartingPoints) if (!all[s.nodeId]) errors.push('bad flow start');
    console.log(p.name, '| frames:', p.children.filter(c => c.type === 'FRAME').map(c => c.name.split(' / ')[1]).join(', ')); }
  console.log('interactions', hot, byNav, '| images', Object.keys(images).length);
  console.log('text layers', texts.length, '| fonts', [...new Set(texts.map(x => x.fontName.family))].join(','));
  console.log('closePlugin:', closedMsg);
  console.log(errors.length ? 'ERRORS:\n' + [...new Set(errors)].join('\n') : 'no errors');
}, 500);
