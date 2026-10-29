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
      const tiles = [];
      for (let y = 0; y < H; y += TILE) { const h = Math.min(TILE, H - y); tiles.push({y, h, file: saveImg(await page.screenshot({fullPage: true, clip: {x: 0, y, width: d.w, height: h}, type: 'jpeg', quality: Q}))}); }
      dev.screens.push({id: s.id, name: s.name, h: H, tiles, hotspots: await hotspots(page, s.id, null, 0, 0)});
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
      const file = saveImg(await page.locator('#detail-dialog').screenshot({type: 'jpeg', quality: Q}));
      const hs = (await hotspots(page, 'dialog', '#detail-dialog', box.x, box.y)).filter(h => h.action.type !== 'scroll');
      const close = await page.evaluate(() => { const c = document.querySelector('.dialog-close').getBoundingClientRect(); const r = document.getElementById('detail-dialog').getBoundingClientRect(); return {x: c.left - r.left, y: c.top - r.top, w: c.width, h: c.height}; });
      hs.push({...close, label: 'Close', action: {type: 'close'}});
      dev.overlays.push({id, name, kind: 'dialog', w: box.w, h: box.h, file, hotspots: hs});
      await page.close();
    }
    // Phone menu: the header and open menu, pinned to the top of the screen.
    if (d.id === 'mobile') {
      const page = await ctx.newPage(); await page.goto(BASE + 'index.html', {waitUntil: 'networkidle'}); await settle(page);
      await page.click('.menu-toggle'); await page.waitForTimeout(300);
      const bottom = await page.evaluate(() => Math.ceil(Math.max(document.getElementById('site-nav').getBoundingClientRect().bottom, document.querySelector('.site-header').getBoundingClientRect().bottom)));
      const file = saveImg(await page.screenshot({clip: {x: 0, y: 0, width: d.w, height: bottom}, type: 'jpeg', quality: Q}));
      const hs = (await hotspots(page, 'menu', '.site-header', 0, 0)).map(h => h.action.to === 'menu' ? {...h, label: 'Close menu', action: {type: 'close'}} : h);
      dev.overlays.push({id: 'menu', name: 'Menu (open)', kind: 'menu', w: d.w, h: bottom, file, hotspots: hs});
      await page.close();
    }
    await ctx.close(); spec.devices.push(dev);
  }
  fs.writeFileSync(OUT + '/spec.json', JSON.stringify(spec, null, 1));
  for (const dv of spec.devices) { console.log(dv.id, dv.screens.map(s => `${s.id}:${s.h}px/${s.tiles.length}t/${s.hotspots.length}hs`).join(' '), '| overlays', dv.overlays.map(o => `${o.id}:${Math.round(o.w)}x${Math.round(o.h)}/${o.hotspots.length}`).join(' ')); }
  await b.close();
})();
