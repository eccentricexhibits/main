// Captures the Remarkable 2027 mockup as editable layers for the Figma plugin.
// For every screen and pop-up it records, in paint order: boxes (fills, gradients, borders, radii, shadows, blur,
// blend modes), images (cropped to what is shown), masked vector symbols (the Vector plus) and text runs, plus the
// geometry and target of every clickable element. Run with the local server on :8765, then `python3 build.py`.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = __dirname + '/data'; fs.rmSync(OUT, {recursive: true, force: true}); fs.mkdirSync(OUT, {recursive: true});
const BASE = 'http://localhost:8765/';
const KARBON = JSON.parse(fs.readFileSync(__dirname + '/karbon-cmap.json'));
const DEVICES = [{id: 'desktop', w: 1440, h: 900}, {id: 'mobile', w: 390, h: 844}];
const SCREENS = [
  {id: 'home', name: 'Home', url: 'index.html'},
  {id: 'agenda1', name: 'Agenda (Day 1)', url: 'agenda.html'},
  {id: 'agenda2', name: 'Agenda (Day 2)', url: 'agenda.html?day=2'},
  {id: 'speakers', name: 'Speakers', url: 'speakers.html'},
  {id: 'faq', name: 'FAQ', url: 'faq.html'},
];
const spec = {devices: [], images: {}, svgs: {}};

// ---------- In-page helpers (serialised into the page) ----------
const PAGE_LIB = String.raw`
window.__lib = (() => {
  const num = v => parseFloat(v) || 0;
  const splitTop = s => { const out = []; let d = 0, cur = ''; for (const ch of s) { if (ch === '(') d++; if (ch === ')') d--; if (ch === ',' && d === 0) { out.push(cur.trim()); cur = ''; } else cur += ch; } if (cur.trim()) out.push(cur.trim()); return out; };
  const color = s => { if (!s || s === 'transparent') return [0, 0, 0, 0]; const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return [p[0] / 255, p[1] / 255, p[2] / 255, p.length > 3 ? p[3] : 1]; };
  const visible = c => c && c[3] > 0.001;
  // Stops: "rgb(...) 10%" | "transparent 87%" | "rgb(...)"
  const stops = parts => { const st = parts.map(p => { const m = p.match(/^(rgba?\([^)]*\)|transparent)\s*(-?[\d.]+%)?/); return m ? {c: color(m[1]), p: m[2] != null ? num(m[2]) / 100 : null} : null; }).filter(Boolean);
    if (!st.length) return st; if (st[0].p == null) st[0].p = 0; if (st[st.length - 1].p == null) st[st.length - 1].p = 1;
    for (let i = 1; i < st.length - 1; i++) if (st[i].p == null) { let j = i; while (st[j].p == null) j++; const a = st[i - 1].p, b = st[j].p; for (let k = i; k < j; k++) st[k].p = a + (b - a) * (k - i + 1) / (j - i + 1); }
    return st; };
  // Figma gradientTransform maps the node's normalised space to gradient space (stops run along x).
  function linear(def, w, h) {
    const parts = splitTop(def); let ang = 180;
    const kw = {'to top': 0, 'to right': 90, 'to bottom': 180, 'to left': 270, 'to top right': 45, 'to right top': 45, 'to bottom right': 135, 'to right bottom': 135, 'to bottom left': 225, 'to left bottom': 225, 'to top left': 315, 'to left top': 315};
    if (/deg$/.test(parts[0])) { ang = num(parts.shift()); } else if (parts[0] in kw) { ang = kw[parts.shift()]; }
    const r = ang * Math.PI / 180, dx = Math.sin(r), dy = -Math.cos(r);
    const L = Math.abs(w * dx) + Math.abs(h * dy);
    const S = [w / 2 - dx * L / 2, h / 2 - dy * L / 2], D = [dx * L, dy * L], L2 = L * L;
    const T = [[w * D[0] / L2, h * D[1] / L2, -(S[0] * D[0] + S[1] * D[1]) / L2],
               [-w * D[1] / L2, h * D[0] / L2, -(-S[0] * D[1] + S[1] * D[0]) / L2 + 0.5]];
    return {type: 'linear', T, stops: stops(parts)};
  }
  function radial(def, w, h) {
    const parts = splitTop(def); let shape = parts[0]; let rx = w / 2, ry = h / 2, cx = w / 2, cy = h / 2;
    if (!/^(rgba?|transparent)/.test(shape)) {
      parts.shift();
      const [size, pos] = shape.split(' at ');
      const sz = (size || '').replace(/ellipse|circle/g, '').trim().split(/\s+/).filter(Boolean);
      const len = (v, ref) => /%$/.test(v) ? num(v) / 100 * ref : num(v);
      if (sz.length >= 2) { rx = len(sz[0], w); ry = len(sz[1], h); } else if (sz.length === 1 && /px|%/.test(sz[0])) { rx = ry = len(sz[0], w); }
      else { rx = Math.hypot(w, h) / 2; ry = rx; }
      if (pos) { const p = pos.trim().split(/\s+/); const k = {left: '0%', center: '50%', right: '100%', top: '0%', bottom: '100%'}; cx = len(k[p[0]] || p[0], w); cy = len(k[p[1] || 'center'] || p[1], h); }
    }
    const T = [[w / (2 * rx), 0, 0.5 - cx / (2 * rx)], [0, h / (2 * ry), 0.5 - cy / (2 * ry)]];
    return {type: 'radial', T, stops: stops(parts)};
  }
  function radii(cs, w, h) { const r = k => { const v = cs[k]; if (!v) return 0; const a = v.split(' ')[0]; return /%$/.test(a) ? num(a) / 100 * Math.min(w, h) : num(a); };
    return ['borderTopLeftRadius', 'borderTopRightRadius', 'borderBottomRightRadius', 'borderBottomLeftRadius'].map(k => Math.min(r(k), w / 2, h / 2)); }
  function shadows(s) { if (!s || s === 'none') return []; return splitTop(s).map(l => { const c = color(l); const rest = l.replace(/rgba?\([^)]*\)/, '').trim(); const inset = /inset/.test(rest); const n = rest.replace('inset', '').trim().split(/\s+/).map(num); return {c, x: n[0] || 0, y: n[1] || 0, blur: n[2] || 0, spread: n[3] || 0, inset}; }).filter(s => s.c && s.c[3] > 0); }
  return {num, splitTop, color, visible, linear, radial, radii, shadows};
})();`;

async function settle(page) {
  await page.addStyleTag({content: '.skip-link{display:none!important} *{animation:none!important;transition:none!important}'});
  await page.evaluate(() => document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager'));
  await page.evaluate(async () => { const s = innerHeight * .8; for (let y = 0; y < document.documentElement.scrollHeight; y += s) { scrollTo(0, y); await new Promise(r => setTimeout(r, 90)); } scrollTo(0, 0); await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode ? i.decode().catch(() => {}) : 0)); });
  await page.addScriptTag({content: PAGE_LIB});
  // In-flow pseudo-elements with text (the ribbon "·" separators) become real spans so their text can be measured.
  await page.evaluate(() => {
    const st = document.createElement('style'); st.textContent = '[data-px-before]::before,[data-px-after]::after{content:none!important}'; document.head.appendChild(st);
    for (const el of document.querySelectorAll('body *')) for (const which of ['before', 'after']) {
      const cs = getComputedStyle(el, '::' + which); const m = (cs.content || '').match(/^"(.+)"$/s);
      if (!m || cs.position === 'absolute' || cs.position === 'fixed' || cs.display === 'none') continue;
      const s = document.createElement('span');
      for (const p of ['display', 'color', 'font-family', 'font-size', 'font-weight', 'letter-spacing', 'line-height', 'margin-left', 'margin-right', 'padding-left', 'padding-right', 'vertical-align', 'text-transform']) s.style.setProperty(p, cs.getPropertyValue(p));
      s.textContent = m[1].replace(/\\([0-9a-f]{1,6}) ?/gi, (x, h) => String.fromCodePoint(parseInt(h, 16)));
      el.setAttribute('data-px-' + which, ''); if (which === 'before') el.insertBefore(s, el.firstChild); else el.appendChild(s);
    }
  });
  await page.waitForTimeout(250);
}

// Collects layers in paint order. root: selector of a pop-up root (coordinates relative to it), or null for the page.
async function layers(page, root, karbon, noClip) {
  return page.evaluate(async ({root, karbon, noClip}) => {
    const L = window.__lib; const KS = new Set(karbon);
    const scope = root ? document.querySelector(root) : document.body;
    const sr = scope.getBoundingClientRect();
    const ox = root ? sr.left : 0, oy = root ? sr.top : -scrollY;
    const out = []; const imgs = []; const svgs = new Set();
    const rel = r => ({x: r.left - ox, y: r.top - oy, w: r.width, h: r.height});
    const isect = (a, b) => { const x = Math.max(a.x, b.x), y = Math.max(a.y, b.y), r = Math.min(a.x + a.w, b.x + b.w), bt = Math.min(a.y + a.h, b.y + b.h); return r > x && bt > y ? {x, y, w: r - x, h: bt - y} : null; };
    const rotOf = cs => { const t = cs.transform; if (!t || t === 'none') return {a: 0, tx: 0, ty: 0}; const m = t.match(/matrix\(([^)]+)\)/); if (!m) return {a: 0, tx: 0, ty: 0}; const v = m[1].split(',').map(Number); return {a: Math.atan2(v[1], v[0]), tx: v[4], ty: v[5], sx: Math.hypot(v[0], v[1]), sy: Math.hypot(v[2], v[3])}; };

    // ---- text blocks (grouped by nearest non-inline container; split at visible gaps) ----
    const textsByContainer = new Map();
    {
      const isInline = el => { const d = getComputedStyle(el).display; return d === 'inline' || d === 'contents'; };
      const groups = new Map(); const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT); let n;
      while ((n = walker.nextNode())) {
        if (!n.data.trim()) continue;
        const el = n.parentElement; if (!el || el.closest('script,style,noscript,.skip-link,.sr-only')) continue;
        if (!root && el.closest('dialog')) continue;
        const det = el.closest('details'); if (det && !det.open && !el.closest('summary')) continue;
        if (el.checkVisibility && !el.checkVisibility({visibilityProperty: true, contentVisibilityAuto: true, opacityProperty: true})) continue;
        const range = document.createRange(); range.selectNodeContents(n);
        let rects = [...range.getClientRects()].filter(r => r.width > 0 && r.height > 0);
        for (let a = el; a && a !== document.documentElement; a = a.parentElement) { const acs = getComputedStyle(a); if (acs.overflowX !== 'visible' || acs.overflowY !== 'visible') { const ar = a.getBoundingClientRect(); rects = rects.filter(r => { const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2; return cx >= ar.left && cx <= ar.right && cy >= ar.top && cy <= ar.bottom; }); } }
        if (!rects.length) continue;
        let c = el; while (c.parentElement && isInline(c) && c !== scope) c = c.parentElement;
        if (!groups.has(c)) groups.set(c, []); groups.get(c).push({node: n, el, rects});
      }
      for (const [c, items] of groups) {
        const order = []; const tw0 = document.createTreeWalker(c, NodeFilter.SHOW_TEXT); let q; const byNode = new Map(items.map(i => [i.node, i]));
        while ((q = tw0.nextNode())) if (byNode.has(q)) order.push(byNode.get(q));
        const pieces = []; let cur = [];
        for (const it of order) { const prev = cur[cur.length - 1]; if (prev) { const pr = prev.rects[prev.rects.length - 1], nr = it.rects[0]; const fs = L.num(getComputedStyle(it.el).fontSize); if (Math.abs(pr.top - nr.top) < fs * 0.6 && nr.left - pr.right > fs * 0.45) { pieces.push(cur); cur = []; } } cur.push(it); }
        if (cur.length) pieces.push(cur);
        const ccs = getComputedStyle(c); const cr = c.getBoundingClientRect();
        const vertical = ccs.writingMode !== 'horizontal-tb';
        pieces.forEach((its, pi) => {
          const set = new Set(its.map(i => i.node)); const ordered = []; const tw = document.createTreeWalker(c, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT); let m, started = false;
          while ((m = tw.nextNode())) { if (m.nodeType === 3 && set.has(m)) { ordered.push(its.find(i => i.node === m)); started = true; } else if (m.nodeName === 'BR' && started) ordered.push({br: true}); }
          let text = ''; const runs = [];
          for (const it of ordered) {
            if (it.br) { text = text.replace(/ $/, '') + '\n'; if (runs.length) runs[runs.length - 1].end = text.length; continue; }
            let t = it.node.data.replace(/\s+/g, ' '); if (/[ \n]$/.test(text) || !text) t = t.replace(/^ /, ''); if (!t) continue;
            const cs = getComputedStyle(it.el); const lh = cs.lineHeight === 'normal' ? null : L.num(cs.lineHeight); const col = L.color(cs.color);
            const base = {size: L.num(cs.fontSize), weight: parseInt(cs.fontWeight, 10), ls: cs.letterSpacing === 'normal' ? 0 : L.num(cs.letterSpacing), lh, upper: cs.textTransform === 'uppercase', color: col};
            // Split into Karbon / fallback runs by glyph coverage.
            let i0 = 0; const chars = [...t]; let pos = text.length;
            const sym = ch => !KS.has(ch.codePointAt(0)) && ch !== ' ';
            for (let i = 1; i <= chars.length; i++) { if (i === chars.length || sym(chars[i]) !== sym(chars[i0])) { const seg = chars.slice(i0, i).join(''); runs.push({...base, start: pos, end: pos + seg.length, fallback: sym(chars[i0])}); pos += seg.length; i0 = i; } }
            text += t;
          }
          const trimmed = text.replace(/\s+$/, ''); if (!trimmed) return;
          runs.forEach(r => { r.end = Math.min(r.end, trimmed.length); }); const live = runs.filter(r => r.end > r.start); if (!live.length) return;
          const all = its.flatMap(i => i.rects);
          const first = all.reduce((a, b) => (b.top < a.top - 1 || (Math.abs(b.top - a.top) <= 1 && b.left < a.left)) ? b : a);
          const Lh = live[0].lh || first.height;
          const minL = Math.min(...all.map(r => r.left)), maxR = Math.max(...all.map(r => r.right)), minT = Math.min(...all.map(r => r.top)), maxB = Math.max(...all.map(r => r.bottom));
          const lines = vertical ? 1 : Math.max(1, Math.round((maxB - minT) / Lh));
          const left = cr.left + L.num(ccs.paddingLeft) + L.num(ccs.borderLeftWidth);
          const width = cr.width - L.num(ccs.paddingLeft) - L.num(ccs.paddingRight) - L.num(ccs.borderLeftWidth) - L.num(ccs.borderRightWidth);
          const align = ccs.textAlign === 'center' ? 'CENTER' : (ccs.textAlign === 'right' || ccs.textAlign === 'end') ? 'RIGHT' : 'LEFT';
          const split = pi > 0;
          let op = 1; for (let a = c; a && a !== document.documentElement; a = a.parentElement) op *= L.num(getComputedStyle(a).opacity) || (getComputedStyle(a).opacity === '0' ? 0 : 1);
          const sh = L.shadows(getComputedStyle(its[0].el).textShadow);
          const node = {t: 'text', text: trimmed, runs: live, align, lines, opacity: op, shadows: sh};
          if (vertical) { node.rotation = ccs.writingMode === 'vertical-lr' ? 90 : -90; node.x = maxR - ox; node.y = minT - oy; node.w = maxB - minT; }
          else { node.x = (lines > 1 && !split ? (align === 'LEFT' ? left : align === 'CENTER' ? left - 2 : left - 4) : minL) - ox; node.y = first.top - (Lh - first.height) / 2 - oy; node.w = lines > 1 ? (split ? maxR - minL + 4 : width + 4) : maxR - minL; }
          if (!textsByContainer.has(c)) textsByContainer.set(c, []); textsByContainer.get(c).push(node);
        });
      }
    }

    // ---- images: crop to the displayed region and re-encode via canvas ----
    async function imageNode(src, box, crop, radius, opacity, blend, name) {
      const img = await new Promise(res => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = src; }); if (!img) return null;
      const scale = Math.min(2, crop.sw / box.w, crop.sh / box.h) || 1;
      const k = Math.min(Math.max(1, scale), 4096 / Math.max(box.w, box.h));  // Figma's image limit is 4096 px
      const cw = Math.max(1, Math.round(box.w * k)), ch = Math.max(1, Math.round(box.h * k));
      const cv = document.createElement('canvas'); cv.width = cw; cv.height = ch; cv.getContext('2d').drawImage(img, crop.sx, crop.sy, crop.sw, crop.sh, 0, 0, cw, ch);
      const png = /\.png(\?|$)/i.test(src) || /\.svg/i.test(src);
      const data = cv.toDataURL(png ? 'image/png' : 'image/jpeg', 0.84);
      imgs.push(data);
      return {t: 'image', ...box, r: radius, img: imgs.length - 1, opacity, blend, name};
    }
    const cropFor = (nw, nh, box, fit, posX, posY) => {
      if (fit === 'fill') return {sx: 0, sy: 0, sw: nw, sh: nh};
      const s = fit === 'contain' ? Math.min(box.w / nw, box.h / nh) : Math.max(box.w / nw, box.h / nh);
      const sw = box.w / s, sh = box.h / s;
      return {sx: (nw - sw) * posX, sy: (nh - sh) * posY, sw, sh};
    };
    const pct = (v, ref) => { if (v === 'left' || v === 'top') return 0; if (v === 'center') return 0.5; if (v === 'right' || v === 'bottom') return 1; if (/%$/.test(v)) return L.num(v) / 100; return ref ? L.num(v) / ref : 0.5; };

    // ---- one element or pseudo-element box ----
    async function emitBox(cs, rect, ctx, name, isImg, el) {
      const first = out.length;
      try { await emitBoxInner(cs, rect, ctx, name, isImg, el); } finally { for (let i = first; i < out.length; i++) out[i].sec = ctx.sec; }
    }
    async function emitBoxInner(cs, rect, ctx, name, isImg, el) {
      let box = rect; const clip = ctx.clip;
      const vis = clip ? isect(box, clip) : box; if (!vis) return;
      const op = ctx.op * (L.num(cs.opacity) || (cs.opacity === '0' ? 0 : 1)); if (op <= 0.001) return;
      { const t0 = rotOf(cs); if (t0.sx != null && (t0.sx < 0.01 || t0.sy < 0.01)) return; }  // scaled to nothing (hover underlines)
      const blend = cs.mixBlendMode && cs.mixBlendMode !== 'normal' ? cs.mixBlendMode.toUpperCase().replace('-', '_') : null;
      const rot = rotOf(cs); const rad = L.radii(cs, box.w, box.h);
      const geom = b => rot.a ? {...b, rotation: -rot.a * 180 / Math.PI} : b;
      // Backgrounds: one rectangle per layer (bottom first), on the layer's clip box.
      const bw = ['Top', 'Right', 'Bottom', 'Left'].map(s => L.num(cs['border' + s + 'Width']));
      const pad = {x: box.x + bw[3], y: box.y + bw[0], w: box.w - bw[1] - bw[3], h: box.h - bw[0] - bw[2]};
      const clipBox = k => k === 'padding-box' ? pad : k === 'content-box' ? {x: pad.x + L.num(cs.paddingLeft), y: pad.y + L.num(cs.paddingTop), w: pad.w - L.num(cs.paddingLeft) - L.num(cs.paddingRight), h: pad.h - L.num(cs.paddingTop) - L.num(cs.paddingBottom)} : box;
      const radFor = b => b === box ? rad : rad.map(r => Math.max(0, r - Math.max(...bw)));
      const clips = L.splitTop(cs.backgroundClip || 'border-box');
      const layersBG = cs.backgroundImage && cs.backgroundImage !== 'none' ? L.splitTop(cs.backgroundImage) : [];
      const shadows = L.shadows(cs.boxShadow); const blurM = (cs.backdropFilter || '').match(/blur\(([\d.]+)px\)/);
      let effectsUsed = false;
      const effects = () => { if (effectsUsed) return []; effectsUsed = true; const e = shadows.map(s => ({type: s.inset ? 'inner' : 'drop', ...s})); if (blurM) e.push({type: 'blur', r: L.num(blurM[1])}); return e; };
      const bgc = L.color(cs.backgroundColor);
      const mask = cs.webkitMaskImage || cs.maskImage;
      const mu = mask && mask !== 'none' && mask.match(/url\("?([^")]+)"?\)/);
      const colorClip = clips[clips.length - 1] || 'border-box';
      const parts = [];
      if (L.visible(bgc) && !mu) parts.push({b: clipBox(colorClip), fill: {type: 'solid', c: bgc}});
      for (let i = layersBG.length - 1; i >= 0; i--) {
        const def = layersBG[i]; const b = clipBox(clips[i] || clips[clips.length - 1] || 'border-box');
        const g = def.match(/^(repeating-)?(linear|radial)-gradient\((.*)\)$/s);
        if (g) { parts.push({b, fill: g[2] === 'linear' ? L.linear(g[3], b.w, b.h) : L.radial(g[3], b.w, b.h), css: def}); continue; }
        const u = def.match(/^url\("?([^")]+)"?\)$/);
        if (u) {
          const img = await new Promise(res => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = u[1]; }); if (!img) continue;
          const size = L.splitTop(cs.backgroundSize)[i] || 'auto'; const posx = (L.splitTop(cs.backgroundPositionX)[i] || '0%'), posy = (L.splitTop(cs.backgroundPositionY)[i] || '0%');
          let dw = img.naturalWidth, dh = img.naturalHeight;
          if (size === 'cover' || size === 'contain') { const s = size === 'cover' ? Math.max(b.w / dw, b.h / dh) : Math.min(b.w / dw, b.h / dh); dw *= s; dh *= s; }
          const dx = b.x + (b.w - dw) * pct(posx), dy = b.y + (b.h - dh) * pct(posy);
          let draw = {x: dx, y: dy, w: dw, h: dh}; const shown = isect(isect(draw, b) || draw, clip || draw); if (!shown) continue;
          const sx = (shown.x - dx) / dw * img.naturalWidth, sy = (shown.y - dy) / dh * img.naturalHeight;
          parts.push({b: shown, imageSrc: u[1], crop: {sx, sy, sw: shown.w / dw * img.naturalWidth, sh: shown.h / dh * img.naturalHeight}});
        }
      }
      for (const p of parts) {
        const b = clip ? isect(p.b, clip) : p.b; if (!b) continue;
        if (p.imageSrc) { const n = await imageNode(p.imageSrc, b, p.crop, [0, 0, 0, 0], op, blend, name + ' (image)'); if (n) out.push(n); continue; }
        out.push(geom({t: 'rect', ...b, r: radFor(p.b), fill: p.fill, css: p.css, opacity: op, blend, effects: effects(), name}));
      }
      // Borders: uniform → stroke on a transparent rectangle; otherwise one thin rectangle per side.
      const bc = ['Top', 'Right', 'Bottom', 'Left'].map(s => cs['border' + s + 'Style'] !== 'none' ? L.color(cs['border' + s + 'Color']) : null);
      const uniform = bw.every(w => w === bw[0]) && bc.every(c => c && L.visible(c) && c.join() === bc[0].join());
      if (bw[0] > 0 && uniform) out.push(geom({t: 'rect', ...box, r: rad, stroke: {w: bw[0], c: bc[0]}, opacity: op, blend, effects: effects(), name: name + ' (border)'}));
      else bw.forEach((w, i) => { if (!(w > 0) || !bc[i] || !L.visible(bc[i])) return; const s = [{x: box.x, y: box.y, w: box.w, h: w}, {x: box.x + box.w - w, y: box.y, w, h: box.h}, {x: box.x, y: box.y + box.h - w, w: box.w, h: w}, {x: box.x, y: box.y, w, h: box.h}][i]; const v = clip ? isect(s, clip) : s; if (v) out.push({t: 'rect', ...v, r: [0, 0, 0, 0], fill: {type: 'solid', c: bc[i]}, opacity: op, name: name + ' (line)'}); });
      if (shadows.length && !effectsUsed) out.push(geom({t: 'rect', ...box, r: rad, fill: {type: 'solid', c: [1, 1, 1, 0]}, opacity: op, effects: effects(), name: name + ' (shadow)'}));
      // Masked vector symbols (the Vector plus and plus cluster).
      if (mu && L.visible(bgc)) {
        const svgText = await (await fetch(mu[1])).text(); const vb = (svgText.match(/viewBox="([^"]+)"/) || [])[1]; const [, , vw, vh] = vb ? vb.split(/\s+/).map(Number) : [0, 0, box.w, box.h];
        const s = Math.min(box.w / vw, box.h / vh); const dw = vw * s, dh = vh * s;
        const mpx = (cs.webkitMaskPositionX || cs.maskPositionX || '50%'), mpy = (cs.webkitMaskPositionY || cs.maskPositionY || '50%');
        svgs.add(mu[1]);
        out.push(geom({t: 'svg', src: mu[1], x: box.x + (box.w - dw) * pct(mpx.split(' ')[0]), y: box.y + (box.h - dh) * pct(mpy.split(' ')[0]), w: dw, h: dh, c: bgc, opacity: op, blend, name: name + ' (symbol)'}));
      }
      if (isImg && el) {
        const nw = el.naturalWidth, nh = el.naturalHeight; if (!nw) return;
        const ip = (cs.objectPosition || '50% 50%').split(' ');
        const crop = cropFor(nw, nh, box, cs.objectFit === 'none' ? 'fill' : (cs.objectFit || 'fill'), pct(ip[0]), pct(ip[1] || '50%'));
        let shown = box, c2 = crop;
        if (clip) { const v = isect(box, clip); if (!v) return; if (v.w < box.w - 0.5 || v.h < box.h - 0.5) { c2 = {sx: crop.sx + (v.x - box.x) / box.w * crop.sw, sy: crop.sy + (v.y - box.y) / box.h * crop.sh, sw: v.w / box.w * crop.sw, sh: v.h / box.h * crop.sh}; shown = v; } }
        let r = rad; if (ctx.clipRadius && Math.abs(ctx.clipRadius.box.w - box.w) < 2 && Math.abs(ctx.clipRadius.box.h - box.h) < 2) r = ctx.clipRadius.r;
        const n = await imageNode(el.currentSrc || el.src, shown, c2, r, op, blend, name); if (n) out.push(n);
      }
    }

    // Absolutely positioned pseudo-element geometry from its resolved style and containing block.
    function pseudoRect(el, cs) {
      let cb = el; while (cb && cb !== document.body && getComputedStyle(cb).position === 'static' && getComputedStyle(cb).transform === 'none') cb = cb.parentElement;
      const r = cb.getBoundingClientRect(); const ccs = getComputedStyle(cb);
      const w = L.num(cs.width) + L.num(cs.paddingLeft) + L.num(cs.paddingRight) + L.num(cs.borderLeftWidth) + L.num(cs.borderRightWidth);
      const h = L.num(cs.height) + L.num(cs.paddingTop) + L.num(cs.paddingBottom) + L.num(cs.borderTopWidth) + L.num(cs.borderBottomWidth);
      const x = cs.position === 'fixed' ? L.num(cs.left) : r.left + L.num(ccs.borderLeftWidth) + L.num(cs.left) + L.num(cs.marginLeft);
      const y = cs.position === 'fixed' ? L.num(cs.top) : r.top + L.num(ccs.borderTopWidth) + L.num(cs.top) + L.num(cs.marginTop);
      const rot = rotOf(cs);
      if (!rot.a) return {x: x + rot.tx - ox, y: y + rot.ty - oy, w, h};
      // Rotated about its centre: Figma positions a rotated layer by its (rotated) top-left corner.
      const cx = x + w / 2 + rot.tx - ox, cy = y + h / 2 + rot.ty - oy, ca = Math.cos(rot.a), sa = Math.sin(rot.a);
      return {x: cx + (-w / 2) * ca - (-h / 2) * sa, y: cy + (-w / 2) * sa + (-h / 2) * ca, w, h};
    }

    const zOf = cs => cs.position !== 'static' && cs.zIndex !== 'auto' ? parseInt(cs.zIndex, 10) : null;
    async function walk(el, ctx) {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || el.matches('script,style,noscript,.skip-link,.sr-only,template')) return;
      if (!root && el.tagName === 'DIALOG') return;
      if (el.parentElement && el.parentElement.tagName === 'DETAILS' && !el.parentElement.open && el.tagName !== 'SUMMARY') return;
      const hidden = cs.visibility === 'hidden';
      const br = el.getBoundingClientRect();
      const rot = rotOf(cs);
      let rect = rel(br);
      if (rot.a) { const w = el.offsetWidth, h = el.offsetHeight; const cx = rect.x + rect.w / 2, cy = rect.y + rect.h / 2; const ca = Math.cos(rot.a), sa = Math.sin(rot.a); rect = {x: cx + (-w / 2) * ca - (-h / 2) * sa, y: cy + (-w / 2) * sa + (-h / 2) * ca, w, h}; }
      const name = (el.id ? '#' + el.id : el.classList[0] ? '.' + el.classList[0] : el.tagName.toLowerCase());
      // Page sections become groups in Figma: children of #app (header, footer) and of <main>.
      if (!root && el.parentElement && (el.parentElement.id === 'app' || el.parentElement.tagName === 'MAIN') && el.tagName !== 'MAIN') {
        const h = el.querySelector('h1,h2');
        ctx = {...ctx, sec: el.matches('header') ? 'Header' : el.matches('footer') ? 'Footer' : el.matches('.event-ribbon') ? 'Ribbon' : el.matches('.funders') ? 'Funders' : (h ? h.innerText.trim().replace(/\s+/g, ' ').slice(0, 40) : (el.classList[0] || el.tagName.toLowerCase()))};
      }
      if (!hidden && rect.w > 0 && rect.h > 0) await emitBox(cs, rect, ctx, name, el.tagName === 'IMG', el);
      // Child context: clipping and opacity.
      const c2 = {...ctx, op: ctx.op * (L.num(cs.opacity) || (cs.opacity === '0' ? 0 : 1))};
      if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') { const b = rel(br); c2.clip = ctx.clip ? isect(ctx.clip, b) : b; c2.clipRadius = {box: b, r: L.radii(cs, b.w, b.h)}; if (!c2.clip) return; }
      if (c2.op <= 0.001) return;
      const entries = [];
      const pseudo = which => { const pcs = getComputedStyle(el, '::' + which); if (!pcs.content || pcs.content === 'none' || pcs.content === 'normal' || pcs.display === 'none') return; if (pcs.position !== 'absolute' && pcs.position !== 'fixed') return; entries.push({pseudo: which, cs: pcs, z: zOf(pcs), positioned: true}); };
      pseudo('before');
      const texts = textsByContainer.get(el); if (texts) entries.push({texts, z: null, positioned: false, flow: true});
      for (const ch of el.children) { const ccs = getComputedStyle(ch); entries.push({el: ch, z: zOf(ccs), positioned: ccs.position !== 'static'}); }
      pseudo('after');
      entries.forEach((e, i) => e.i = i);
      const bucket = e => e.z != null && e.z < 0 ? 0 : !e.positioned ? 1 : (e.z == null || e.z === 0) ? 2 : 3;
      entries.sort((a, b) => bucket(a) - bucket(b) || (bucket(a) !== 1 && bucket(a) !== 2 ? (a.z - b.z) : 0) || a.i - b.i);
      for (const e of entries) {
        if (e.pseudo) { if (!hidden) await emitBox(e.cs, pseudoRect(el, e.cs), c2, name + '::' + e.pseudo, false, null); }
        else if (e.texts) { if (!hidden) for (const t of e.texts) out.push({...t, sec: c2.sec}); }
        else await walk(e.el, c2);
      }
    }
    await walk(scope, {op: 1, sec: root ? 'Pop-up' : 'Page', clip: root && !noClip ? {x: 0, y: 0, w: sr.width, h: sr.height} : null});
    return {layers: out, images: imgs, svgs: [...svgs]};
  }, {root, karbon, noClip: !!noClip});
}

const CLASSIFY = `(el, screen) => {
  const pageOf = (href) => { const u = new URL(href, location.href); const f = u.pathname.split('/').pop() || 'index.html';
    if (f === 'index.html') return 'home'; if (f === 'agenda.html') return (u.searchParams.get('day') === '2' || /^#session-2-/.test(u.hash)) ? 'agenda2' : 'agenda1';
    if (f === 'speakers.html') return 'speakers'; if (f === 'faq.html') return 'faq'; return null; };
  if (el.matches('.skip-link')) return null;
  if (el.matches('a[href]')) { const href = el.getAttribute('href');
    if (href.startsWith('mailto:')) return {type:'url', url: href};
    if (href.startsWith('#')) { const t = href === '#top' ? document.body : document.getElementById(href.slice(1)); if (!t) return null; return {type:'scroll', y: href === '#top' ? 0 : Math.max(0, t.getBoundingClientRect().top + scrollY - 20)}; }
    const p = pageOf(href); if (!p) return null; return p === screen ? null : {type:'navigate', to: p}; }
  if (el.matches('[data-register]')) return {type:'overlay', to: 'register-' + (el.dataset.register === 'choose' ? 'choose' : el.dataset.register === 'virtual' ? 'virtual' : 'inperson')};
  if (el.matches('[data-speaker]')) return {type:'overlay', to: 'speaker-' + el.dataset.speaker};
  if (el.matches('[role=tab]')) { const to = el.dataset.day === '1' ? 'agenda2' : 'agenda1'; return to === screen ? null : {type:'navigate', to}; }
  if (el.matches('.menu-toggle')) return {type:'overlay', to: 'menu'};
  return null;
}`;
const SELECTOR = 'a[href], button[data-register], button[data-speaker], [role=tab], .menu-toggle';
async function hotspots(page, screen, root, originX, originY) {
  return page.evaluate(({sel, cls, screen, root, ox, oy}) => {
    const classify = eval(cls); const scope = root ? document.querySelector(root) : document; const out = [];
    for (const el of scope.querySelectorAll(sel)) {
      const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
      if (r.width < 4 || r.height < 4 || cs.visibility === 'hidden' || cs.display === 'none') continue;
      const a = classify(el, screen); if (!a) continue;
      out.push({x: r.left - ox, y: r.top + (root ? 0 : scrollY) - oy, w: r.width, h: r.height, label: (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40), action: a});
    }
    return out;
  }, {sel: SELECTOR, cls: CLASSIFY, screen, root, ox: originX, oy: originY});
}

let imgCount = 0;
const imgIndex = new Map();
function storeImages(result) {
  // Dedupe identical crops across screens; write each once.
  const map = result.images.map(data => {
    if (imgIndex.has(data)) return imgIndex.get(data);
    const [, mime, b64] = data.match(/^data:image\/(\w+);base64,(.*)$/);
    const f = `img${++imgCount}.${mime === 'png' ? 'png' : 'jpg'}`; fs.writeFileSync(`${OUT}/${f}`, Buffer.from(b64, 'base64'));
    imgIndex.set(data, f); return f;
  });
  for (const l of result.layers) if (l.t === 'image') l.img = map[l.img];
  return result.layers;
}
async function storeSvgs(page, list) {
  for (const u of list) { const key = u.split('/').pop(); if (!spec.svgs[key]) spec.svgs[key] = await page.evaluate(async u => (await fetch(u)).text(), u); }
}
const fixSvgRefs = ls => { for (const l of ls) if (l.t === 'svg') l.src = l.src.split('/').pop(); return ls; };

(async () => {
  const b = await chromium.launch();
  for (const d of DEVICES) {
    const dev = {id: d.id, w: d.w, h: d.h, screens: [], overlays: []};
    const ctx = await b.newContext({viewport: {width: d.w, height: d.h}, deviceScaleFactor: 1, reducedMotion: 'reduce'});
    for (const s of SCREENS) {
      const page = await ctx.newPage(); await page.goto(BASE + s.url, {waitUntil: 'networkidle'}); await settle(page);
      const H = await page.evaluate(() => document.documentElement.scrollHeight);
      const r = await layers(page, null, KARBON); await storeSvgs(page, r.svgs);
      const bg = await page.evaluate(() => window.__lib.color(getComputedStyle(document.body).backgroundColor));
      dev.screens.push({id: s.id, name: s.name, h: H, bg, layers: fixSvgRefs(storeImages(r)), hotspots: await hotspots(page, s.id, null, 0, 0)});
      await page.close();
    }
    const dialogs = [['register-choose', 'Registration (menu)', 'index.html', '.nav-register'], ['register-inperson', 'Registration (Register now)', 'index.html', '.hero-actions [data-register]']];
    for (let i = 0; i < 6; i++) dialogs.push([`speaker-${i}`, `Speaker profile ${i + 1}`, 'speakers.html', `[data-speaker="${i}"]`]);
    for (const [id, name, url, sel] of dialogs) {
      const page = await ctx.newPage(); await page.goto(BASE + url, {waitUntil: 'networkidle'}); await settle(page);
      if (d.id === 'mobile' && sel === '.nav-register') await page.click('.menu-toggle');
      await page.click(sel); await page.waitForTimeout(400);
      const box = await page.evaluate(() => { const r = document.getElementById('detail-dialog').getBoundingClientRect(); return {x: r.left, y: r.top, w: r.width, h: r.height}; });
      const r = await layers(page, '#detail-dialog', KARBON); await storeSvgs(page, r.svgs);
      const hs = (await hotspots(page, 'dialog', '#detail-dialog', box.x, box.y)).filter(h => h.action.type !== 'scroll');
      const close = await page.evaluate(() => { const c = document.querySelector('.dialog-close').getBoundingClientRect(); const r = document.getElementById('detail-dialog').getBoundingClientRect(); return {x: c.left - r.left, y: c.top - r.top, w: c.width, h: c.height}; });
      hs.push({...close, label: 'Close', action: {type: 'close'}});
      dev.overlays.push({id, name, kind: 'dialog', w: box.w, h: box.h, layers: fixSvgRefs(storeImages(r)), hotspots: hs});
      await page.close();
    }
    if (d.id === 'mobile') {
      const page = await ctx.newPage(); await page.goto(BASE + 'index.html', {waitUntil: 'networkidle'}); await settle(page);
      await page.click('.menu-toggle'); await page.waitForTimeout(300);
      const bottom = await page.evaluate(() => Math.ceil(Math.max(document.getElementById('site-nav').getBoundingClientRect().bottom, document.querySelector('.site-header').getBoundingClientRect().bottom)));
      const r = await layers(page, '.site-header', KARBON, true); await storeSvgs(page, r.svgs);
      const hs = (await hotspots(page, 'menu', '.site-header', 0, 0)).map(h => h.action.to === 'menu' ? {...h, label: 'Close menu', action: {type: 'close'}} : h);
      dev.overlays.push({id: 'menu', name: 'Menu (open)', kind: 'menu', w: d.w, h: bottom, layers: fixSvgRefs(storeImages(r)), hotspots: hs});
      await page.close();
    }
    await ctx.close(); spec.devices.push(dev);
  }
  fs.writeFileSync(OUT + '/spec.json', JSON.stringify(spec));
  const count = (ls, t) => ls.filter(l => l.t === t).length;
  for (const dv of spec.devices) console.log(dv.id, dv.screens.map(s => `${s.id}: ${count(s.layers, 'rect')}r ${count(s.layers, 'image')}i ${count(s.layers, 'svg')}s ${count(s.layers, 'text')}t`).join(' | '));
  console.log('overlays', spec.devices.map(dv => dv.overlays.map(o => `${dv.id}/${o.id}:${o.layers.length}`).join(' ')).join(' '));
  console.log('images', imgCount, 'svgs', Object.keys(spec.svgs).join(','));
  await b.close();
})();
