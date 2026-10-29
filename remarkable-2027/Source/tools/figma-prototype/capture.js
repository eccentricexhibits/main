// Captures every screen and overlay of the Remarkable 2027 mockup, plus hotspot rectangles, for the Figma plugin.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = __dirname + '/data'; fs.rmSync(OUT,{recursive:true,force:true}); fs.mkdirSync(OUT,{recursive:true});
const BASE = 'http://localhost:8765/';
const DSF = 1.5, TILE = 2000, Q = 78;
const DEVICES = [{id:'desktop', w:1440, h:900}, {id:'mobile', w:390, h:844}];
const SCREENS = [
  {id:'home', name:'Home', url:'index.html'},
  {id:'agenda1', name:'Agenda (Day 1)', url:'agenda.html'},
  {id:'agenda2', name:'Agenda (Day 2)', url:'agenda.html?day=2'},
  {id:'speakers', name:'Speakers', url:'speakers.html'},
  {id:'faq', name:'FAQ', url:'faq.html'},
];
const spec = {devices:[]};
let imgN = 0;
const saveImg = (buf) => { const f = `img${++imgN}.jpg`; fs.writeFileSync(`${OUT}/${f}`, buf); return f; };

// Runs in the page: classify a clickable element into a prototype action.
const CLASSIFY = `(el, screen) => {
  const pageOf = (href) => {
    const u = new URL(href, location.href); const f = u.pathname.split('/').pop() || 'index.html';
    if (f === 'index.html') return 'home';
    if (f === 'agenda.html') return (u.searchParams.get('day') === '2' || /^#session-2-/.test(u.hash)) ? 'agenda2' : 'agenda1';
    if (f === 'speakers.html') return 'speakers';
    if (f === 'faq.html') return 'faq';
    return null;
  };
  if (el.matches('.skip-link')) return null;
  if (el.matches('a[href]')) {
    const href = el.getAttribute('href');
    if (href.startsWith('mailto:')) return {type:'url', url: href};
    if (href.startsWith('#')) {
      const t = href === '#top' ? document.body : document.getElementById(href.slice(1));
      if (!t) return null;
      return {type:'scroll', y: href === '#top' ? 0 : Math.max(0, t.getBoundingClientRect().top + scrollY - 20)};
    }
    const p = pageOf(href); if (!p) return null;
    return p === screen ? null : {type:'navigate', to: p};
  }
  if (el.matches('[data-register]')) return {type:'overlay', to: 'register-' + (el.dataset.register === 'choose' ? 'choose' : el.dataset.register === 'virtual' ? 'virtual' : 'inperson')};
  if (el.matches('[data-speaker]')) return {type:'overlay', to: 'speaker-' + el.dataset.speaker};
  if (el.matches('[role=tab]')) { const to = el.dataset.day === '1' ? 'agenda2' : 'agenda1'; return to === screen ? null : {type:'navigate', to}; }
  if (el.matches('.menu-toggle')) return {type:'overlay', to: 'menu'};
  return null;
}`;
const SELECTOR = 'a[href], button[data-register], button[data-speaker], [role=tab], .menu-toggle';

async function hotspots(page, screen, root, originX, originY) {
  return page.evaluate(({sel, cls, screen, root, ox, oy}) => {
    const classify = eval(cls); const scope = root ? document.querySelector(root) : document;
    const out = [];
    for (const el of scope.querySelectorAll(sel)) {
      const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
      if (r.width < 4 || r.height < 4 || cs.visibility === 'hidden' || cs.display === 'none') continue;
      const a = classify(el, screen); if (!a) continue;
      const fixed = root ? true : false;
      out.push({x: r.left - ox, y: r.top + (fixed ? 0 : scrollY) - oy, w: r.width, h: r.height, label: (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\\s+/g,' ').slice(0,40), action: a});
    }
    return out;
  }, {sel: SELECTOR, cls: CLASSIFY, screen, root, ox: originX, oy: originY});
}

// Runs in the page: collect every visible text block (grouped by its nearest non-inline container) with its
// styled runs, then hide the glyphs (-webkit-text-fill-color) so the screenshot carries no text. Symbol-only
// text (×, ↓, ▶, arrows) and rotated text stay in the image.
async function extractTexts(page, root, originX, originY) {
  return page.evaluate(({root, ox, oy}) => {
    const scope = root ? document.querySelector(root) : document.body;
    const SYMBOLS = /^[\s×↓↑▶←→]*$/;  // glyphs Karbon lacks stay in the image
    const groups = new Map();
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    const isInline = el => getComputedStyle(el).display.startsWith('inline') && getComputedStyle(el).display !== 'inline-block' && getComputedStyle(el).display !== 'inline-flex';
    const rotated = el => { for (let e = el; e && e !== document.body; e = e.parentElement) { if (getComputedStyle(e).writingMode !== 'horizontal-tb') return true; const t = getComputedStyle(e).transform; if (t && t !== 'none') { const m = t.match(/matrix\(([^)]+)\)/); if (m && Math.abs(parseFloat(m[1].split(',')[1])) > 0.01) return true; } } return false; };
    const keep = new Set();
    let n;
    while ((n = walker.nextNode())) {
      if (!n.data.trim()) continue;
      const el = n.parentElement; if (!el || el.closest('script,style,noscript,.skip-link,.sr-only')) continue;
      const det = el.closest('details'); if (det && !det.open && !el.closest('summary')) continue;  // closed answers
      if (el.checkVisibility && !el.checkVisibility({visibilityProperty: true, contentVisibilityAuto: true})) continue;
      const range = document.createRange(); range.selectNodeContents(n);
      let rects = [...range.getClientRects()].filter(r => r.width > 0 && r.height > 0);
      // Drop text clipped away by an overflow container (collapsed answers, off-screen gallery captions).
      for (let a = el; a && a !== document.documentElement; a = a.parentElement) {
        const acs = getComputedStyle(a);
        if (acs.overflowX !== 'visible' || acs.overflowY !== 'visible') {
          const ar = a.getBoundingClientRect();
          rects = rects.filter(r => { const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2; return cx >= ar.left && cx <= ar.right && cy >= ar.top && cy <= ar.bottom; });
        }
      }
      if (!rects.length) continue;
      const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
      let c = el; while (c.parentElement && isInline(c) && c !== scope) c = c.parentElement;
      if (SYMBOLS.test(n.data) || rotated(c)) { keep.add(el); continue; }
      if (!groups.has(c)) groups.set(c, []);
      groups.get(c).push({node: n, el, rects});
    }
    const out = [];
    const subgroups = [];
    for (const [c, items] of groups) {
      // Keep DOM order, then split where an inline element's margin or padding opens a visible gap on the line.
      const order = [];
      const tw0 = document.createTreeWalker(c, NodeFilter.SHOW_TEXT); let q; const byNode = new Map(items.map(i => [i.node, i]));
      while ((q = tw0.nextNode())) if (byNode.has(q)) order.push(byNode.get(q));
      let cur = [], piece = 0;
      for (const it of order) {
        const prev = cur[cur.length - 1];
        if (prev) {
          const pr = prev.rects[prev.rects.length - 1], nr = it.rects[0];
          const fs = parseFloat(getComputedStyle(it.el).fontSize);
          if (Math.abs(pr.top - nr.top) < fs * 0.6 && nr.left - pr.right > fs * 0.45) { subgroups.push([c, cur, piece > 0]); piece++; cur = []; }
        }
        cur.push(it);
      }
      if (cur.length) subgroups.push([c, cur, piece > 0]);
    }
    for (const [c, items, isSplit] of subgroups) {
      // Line breaks inside the container become \n.
      const ordered = [];
      const tw = document.createTreeWalker(c, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
      const set = new Set(items.map(i => i.node)); let m;
      let started = false;
      while ((m = tw.nextNode())) { if (m.nodeType === 3 && set.has(m)) { ordered.push(items.find(i => i.node === m)); started = true; } else if (m.nodeName === 'BR' && started) ordered.push({br: true}); }
      let text = ''; const runs = [];
      for (const it of ordered) {
        if (it.br) { text = text.replace(/ $/, '') + '\n'; if (runs.length) runs[runs.length - 1].end = text.length; continue; }
        let t = it.node.data.replace(/\s+/g, ' ');
        if (/[ \n]$/.test(text) || !text) t = t.replace(/^ /, '');
        if (!t) continue;
        const cs = getComputedStyle(it.el);
        const lh = cs.lineHeight === 'normal' ? null : parseFloat(cs.lineHeight);
        const col = cs.color.match(/[\d.]+/g).map(Number);
        runs.push({start: text.length, end: text.length + t.length, size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight, 10), ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing), lh, upper: cs.textTransform === 'uppercase', color: [col[0] / 255, col[1] / 255, col[2] / 255, col.length > 3 ? col[3] : 1]});
        text += t;
      }
      const trimmed = text.replace(/\s+$/, ''); if (!trimmed) continue;
      runs.forEach(r => { r.end = Math.min(r.end, trimmed.length); }); const live = runs.filter(r => r.end > r.start);
      const all = items.flatMap(i => i.rects);
      const first = all.reduce((a, b) => (b.top < a.top - 1 || (Math.abs(b.top - a.top) <= 1 && b.left < a.left)) ? b : a);
      const L0 = live[0].lh || first.height;
      const lines = Math.max(1, Math.round((Math.max(...all.map(r => r.bottom)) - Math.min(...all.map(r => r.top))) / L0));
      const ccs = getComputedStyle(c); const cr = c.getBoundingClientRect();
      const left = cr.left + parseFloat(ccs.paddingLeft) + parseFloat(ccs.borderLeftWidth);
      const width = cr.width - parseFloat(ccs.paddingLeft) - parseFloat(ccs.paddingRight) - parseFloat(ccs.borderLeftWidth) - parseFloat(ccs.borderRightWidth);
      const L = live[0].lh || first.height;
      const align = ccs.textAlign === 'center' ? 'CENTER' : (ccs.textAlign === 'right' || ccs.textAlign === 'end') ? 'RIGHT' : 'LEFT';
      const fixed = !root;
      const sy = fixed ? scrollY : 0;
      const minLeft = Math.min(...all.map(r => r.left)), maxRight = Math.max(...all.map(r => r.right));
      out.push({text: trimmed, runs: live, align, lines, lineHeightAuto: !live[0].lh,
        x: (lines > 1 && !isSplit ? (align === 'LEFT' ? left : align === 'CENTER' ? left - 2 : left - 4) : minLeft) - ox,
        y: first.top - (L - first.height) / 2 + sy - oy,
        w: lines > 1 ? (isSplit ? maxRight - minLeft + 4 : width + 4) : maxRight - minLeft});
    }
    // Hide the glyphs for the screenshot; keep symbols and rotated text visible.
    const st = document.createElement('style'); st.id = 'hide-text';
    st.textContent = '*{-webkit-text-fill-color:transparent!important;text-shadow:none!important} *::before,*::after{-webkit-text-fill-color:currentColor!important}';
    document.head.appendChild(st);
    for (const el of keep) el.style.setProperty('-webkit-text-fill-color', 'currentColor', 'important');
    return out;
  }, {root, ox: originX, oy: originY});
}

async function settle(page) {
  await page.addStyleTag({content:'.skip-link{display:none!important} *{animation:none!important;transition:none!important}'});
  await page.evaluate(() => document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager'));
  await page.evaluate(async () => { const s = innerHeight * .8; for (let y = 0; y < document.documentElement.scrollHeight; y += s) { scrollTo(0, y); await new Promise(r => setTimeout(r, 90)); } scrollTo(0, 0); await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode ? i.decode().catch(() => {}) : 0)); });
  await page.waitForTimeout(300);
}

(async () => {
  const b = await chromium.launch();
  for (const d of DEVICES) {
    const dev = {id: d.id, w: d.w, h: d.h, screens: [], overlays: []};
    const ctx = await b.newContext({viewport: {width: d.w, height: d.h}, deviceScaleFactor: DSF, reducedMotion: 'reduce'});
    for (const s of SCREENS) {
      const page = await ctx.newPage(); await page.goto(BASE + s.url, {waitUntil: 'networkidle'}); await settle(page);
      const H = await page.evaluate(() => document.documentElement.scrollHeight);
      const hs = await hotspots(page, s.id, null, 0, 0);
      const texts = await extractTexts(page, null, 0, 0); await page.waitForTimeout(150);
      const tiles = [];
      for (let y = 0; y < H; y += TILE) { const h = Math.min(TILE, H - y); tiles.push({y, h, file: saveImg(await page.screenshot({fullPage: true, clip: {x: 0, y, width: d.w, height: h}, type: 'jpeg', quality: Q}))}); }
      dev.screens.push({id: s.id, name: s.name, h: H, tiles, texts, hotspots: hs});
      await page.close();
    }
    // Registration dialogs and speaker profiles (centred pop-ups).
    const dialogs = [['register-choose', 'Registration (menu)', 'index.html', '.nav-register'], ['register-inperson', 'Registration (Register now)', 'index.html', '.hero-actions [data-register]'], ['register-virtual', 'Registration (virtual)', 'index.html', null]];
    for (let i = 0; i < 6; i++) dialogs.push([`speaker-${i}`, `Speaker profile ${i + 1}`, 'speakers.html', `[data-speaker="${i}"]`]);
    for (const [id, name, url, sel] of dialogs) {
      const page = await ctx.newPage(); await page.goto(BASE + url, {waitUntil: 'networkidle'}); await settle(page);
      if (sel) { if (d.id === 'mobile' && sel === '.nav-register') { await page.click('.menu-toggle'); } await page.click(sel); }
      else { const ok = await page.evaluate(() => { const b = document.createElement('button'); b.dataset.register = 'virtual'; document.body.appendChild(b); b.click(); return true; }); }
      await page.waitForTimeout(400);
      const box = await page.evaluate(() => { const r = document.getElementById('detail-dialog').getBoundingClientRect(); return {x: r.left, y: r.top, w: r.width, h: r.height}; });
      const hs = (await hotspots(page, 'dialog', '#detail-dialog', box.x, box.y)).filter(h => h.action.type !== 'scroll');
      const texts = await extractTexts(page, '#detail-dialog', box.x, box.y); await page.waitForTimeout(150);
      const file = saveImg(await page.locator('#detail-dialog').screenshot({type: 'jpeg', quality: Q}));
      const close = await page.evaluate(() => { const c = document.querySelector('.dialog-close').getBoundingClientRect(); const r = document.getElementById('detail-dialog').getBoundingClientRect(); return {x: c.left - r.left, y: c.top - r.top, w: c.width, h: c.height}; });
      hs.push({...close, label: 'Close', action: {type: 'close'}});
      dev.overlays.push({id, name, kind: 'dialog', w: box.w, h: box.h, file, texts, hotspots: hs});
      await page.close();
    }
    // Phone menu: the header and open menu, pinned to the top of the screen.
    if (d.id === 'mobile') {
      const page = await ctx.newPage(); await page.goto(BASE + 'index.html', {waitUntil: 'networkidle'}); await settle(page);
      await page.click('.menu-toggle'); await page.waitForTimeout(300);
      const bottom = await page.evaluate(() => Math.ceil(Math.max(document.getElementById('site-nav').getBoundingClientRect().bottom, document.querySelector('.site-header').getBoundingClientRect().bottom)));
      const hs0 = await hotspots(page, 'menu', '.site-header', 0, 0);
      const texts = await extractTexts(page, '.site-header', 0, 0); await page.waitForTimeout(150);
      const file = saveImg(await page.screenshot({clip: {x: 0, y: 0, width: d.w, height: bottom}, type: 'jpeg', quality: Q}));
      const hs = hs0.map(h => h.action.to === 'menu' ? {...h, label: 'Close menu', action: {type: 'close'}} : h);
      dev.overlays.push({id: 'menu', name: 'Menu (open)', kind: 'menu', w: d.w, h: bottom, file, texts, hotspots: hs});
      await page.close();
    }
    await ctx.close(); spec.devices.push(dev);
  }
  fs.writeFileSync(OUT + '/spec.json', JSON.stringify(spec, null, 1));
  for (const dv of spec.devices) { console.log(dv.id, dv.screens.map(s => `${s.id}:${s.h}px/${s.tiles.length}t/${s.hotspots.length}hs/${s.texts.length}tx`).join(' '), '| overlays', dv.overlays.map(o => `${o.id}:${Math.round(o.w)}x${Math.round(o.h)}/${o.hotspots.length}`).join(' ')); }
  await b.close();
})();
