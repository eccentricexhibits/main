// Remarkable 2027 prototype builder (Figma plugin).
// Builds two pages, "Desktop prototype" and "Mobile prototype". Every screen and pop-up is rebuilt from native Figma
// layers captured from the HTML mockup: rectangles (solid and gradient fills, borders, corner radii, shadows,
// background blur, blend modes), images, Vector plus symbols as vectors, and Karbon text (Inter if Karbon is not
// installed). Layers are grouped by page section, and clickable hotspots are wired as prototype interactions.
const DATA = __DATA__;
const IMAGES = __IMAGES__;
const SVGS = __SVGS__;

const GAP = 200;
const hashes = {};
const imageHash = file => hashes[file] || (hashes[file] = figma.createImage(figma.base64Decode(IMAGES[file])).hash);
const rgb = c => ({r: c[0], g: c[1], b: c[2]});

// ---------- fonts ----------
const KARBON = {400: 'Regular', 500: 'Medium', 600: 'Semibold', 700: 'Bold'};
const INTER = {400: 'Regular', 500: 'Medium', 600: 'Semi Bold', 700: 'Bold'};
let family = 'Karbon';
async function loadFonts() {
  for (const style of Object.values(INTER)) await figma.loadFontAsync({family: 'Inter', style});
  try { for (const style of Object.values(KARBON)) await figma.loadFontAsync({family: 'Karbon', style}); }
  catch (e) { family = 'Inter'; }
}
function fontFor(weight, fallback) {
  const w = [400, 500, 600, 700].reduce((a, b) => Math.abs(b - weight) < Math.abs(a - weight) ? b : a);
  const fam = fallback ? 'Inter' : family;
  return {family: fam, style: (fam === 'Karbon' ? KARBON : INTER)[w]};
}

// ---------- geometry ----------
// Places a node at (x, y), rotated clockwise on screen by -rotation degrees about its top-left corner.
function place(n, l, ox, oy) {
  const x = l.x + ox, y = l.y + oy;
  if (l.rotation) { const a = -l.rotation * Math.PI / 180; n.relativeTransform = [[Math.cos(a), -Math.sin(a), x], [Math.sin(a), Math.cos(a), y]]; }
  else { n.x = x; n.y = y; }
}
function paint(f) {
  if (!f) return [];
  if (f.type === 'solid') return [{type: 'SOLID', color: rgb(f.c), opacity: f.c[3]}];
  const stops = f.stops.map(s => ({position: Math.min(1, Math.max(0, s.p)), color: {r: s.c[0], g: s.c[1], b: s.c[2], a: s.c[3]}}));
  for (let i = 1; i < stops.length; i++) if (stops[i].position < stops[i - 1].position) stops[i].position = stops[i - 1].position;
  return [{type: f.type === 'linear' ? 'GRADIENT_LINEAR' : 'GRADIENT_RADIAL', gradientTransform: f.T, gradientStops: stops}];
}
function effects(list) {
  return (list || []).map(e => e.type === 'blur' ? {type: 'BACKGROUND_BLUR', radius: e.r, visible: true}
    : {type: e.type === 'inner' ? 'INNER_SHADOW' : 'DROP_SHADOW', color: {r: e.c[0], g: e.c[1], b: e.c[2], a: e.c[3]}, offset: {x: e.x, y: e.y}, radius: e.blur, spread: e.spread, visible: true, blendMode: 'NORMAL', ...(e.type === 'inner' ? {} : {showShadowBehindNode: false})});
}
function common(n, l) {
  n.name = l.name || n.name;
  if (l.opacity != null && l.opacity < 1) n.opacity = l.opacity;
  if (l.blend) { try { n.blendMode = l.blend; } catch (e) { /* unsupported blend mode */ } }
}

// ---------- layer builders ----------
function buildRect(l, ox, oy) {
  const n = figma.createRectangle();
  n.resize(Math.max(0.01, l.w), Math.max(0.01, l.h));
  place(n, l, ox, oy);
  const r = l.r || [0, 0, 0, 0];
  n.topLeftRadius = r[0]; n.topRightRadius = r[1]; n.bottomRightRadius = r[2]; n.bottomLeftRadius = r[3];
  n.fills = l.t === 'image' ? [{type: 'IMAGE', scaleMode: 'FILL', imageHash: imageHash(l.img)}] : paint(l.fill);
  if (l.stroke) { n.strokes = [{type: 'SOLID', color: rgb(l.stroke.c), opacity: l.stroke.c[3]}]; n.strokeWeight = l.stroke.w; n.strokeAlign = 'INSIDE'; }
  if (l.effects && l.effects.length) n.effects = effects(l.effects);
  common(n, l);
  return n;
}
function buildSvg(l, ox, oy) {
  const n = figma.createNodeFromSvg(SVGS[l.src]);
  n.fills = []; n.clipsContent = false;
  if (n.width > 0) n.rescale(l.w / n.width);
  for (const v of n.findAll(c => 'fills' in c && c.type !== 'FRAME')) v.fills = [{type: 'SOLID', color: rgb(l.c), opacity: l.c[3]}];
  place(n, l, ox, oy);
  common(n, l);
  return n;
}
function buildText(l, ox, oy) {
  const n = figma.createText();
  const r0 = l.runs[0];
  n.fontName = fontFor(r0.weight, r0.fallback);
  n.characters = l.text;
  n.textAlignHorizontal = l.align;
  for (const r of l.runs) {
    n.setRangeFontName(r.start, r.end, fontFor(r.weight, r.fallback));
    n.setRangeFontSize(r.start, r.end, r.size);
    n.setRangeLetterSpacing(r.start, r.end, {value: r.ls, unit: 'PIXELS'});
    n.setRangeLineHeight(r.start, r.end, r.lh ? {value: r.lh, unit: 'PIXELS'} : {unit: 'AUTO'});
    n.setRangeTextCase(r.start, r.end, r.upper ? 'UPPER' : 'ORIGINAL');
    n.setRangeFills(r.start, r.end, [{type: 'SOLID', color: rgb(r.color), opacity: r.color[3]}]);
  }
  if (l.lines > 1) { n.resize(Math.max(1, l.w), n.height); n.textAutoResize = 'HEIGHT'; }
  else n.textAutoResize = 'WIDTH_AND_HEIGHT';
  if (l.shadows && l.shadows.length) n.effects = effects(l.shadows.map(s => ({...s, type: 'drop'})));
  place(n, l, ox, oy);
  common(n, l);
  n.name = l.text.replace(/\s+/g, ' ').slice(0, 40);
  return n;
}
function buildLayers(parent, layers, ox, oy) {
  const bySection = new Map(); // section name -> nodes, in paint order
  for (const l of layers) {
    let n = null;
    try { n = l.t === 'text' ? buildText(l, ox, oy) : l.t === 'svg' ? buildSvg(l, ox, oy) : buildRect(l, ox, oy); }
    catch (e) { console.warn('Skipped a layer:', l.name, e && e.message); continue; }
    parent.appendChild(n);
    const k = l.sec || 'Layers';
    if (!bySection.has(k)) bySection.set(k, []);
    bySection.get(k).push(n);
  }
  for (const [name, nodes] of bySection) {
    if (nodes.length < 2) continue;
    try { const g = figma.group(nodes, parent); g.name = name; } catch (e) { /* grouping is optional */ }
  }
}

function hotspotRect(parent, name, x, y, w, h) {
  const r = figma.createRectangle();
  r.name = name;
  r.resize(Math.max(1, w), Math.max(1, h)); r.x = x; r.y = y;
  r.fills = [{type: 'SOLID', color: {r: 1, g: 1, b: 1}, opacity: 0}];
  parent.appendChild(r);
  return r;
}
async function setClick(node, action) {
  const reactions = [{trigger: {type: 'ON_CLICK'}, actions: [action]}];
  if (node.setReactionsAsync) await node.setReactionsAsync(reactions); else node.reactions = reactions;
}
function label(page, text, x, y, size) {
  const t = figma.createText();
  t.fontName = {family: 'Inter', style: 'Bold'}; t.characters = text; t.fontSize = size;
  t.x = x; t.y = y; page.appendChild(t);
}

async function buildDevice(d) {
  const title = d.id === 'desktop' ? 'Desktop' : 'Mobile';
  const page = figma.createPage();
  page.name = `${title} prototype`;
  await figma.setCurrentPageAsync(page);

  const frames = {};
  const pending = []; // [node, action, frame]
  const used = new Set();
  for (const s of d.screens) for (const h of s.hotspots) if (h.action.type === 'overlay') used.add(h.action.to);
  for (const o of d.overlays) if (used.has(o.id)) for (const h of o.hotspots) if (h.action.type === 'overlay') used.add(h.action.to);

  label(page, `Remarkable 2027 · ${title} (${d.w} px)`, 0, -260, d.id === 'desktop' ? 72 : 48);
  label(page, 'Press Present (▶, top right) to click through the prototype.', 0, -150, 28);

  let x = 0, tallest = 0;
  for (const s of d.screens) {
    figma.notify(`Building ${title}: ${s.name}…`, {timeout: 1500});
    const f = figma.createFrame();
    f.name = `${title} / ${s.name}`;
    f.resize(d.w, s.h); f.x = x; f.y = 0;
    f.clipsContent = true;
    f.fills = [{type: 'SOLID', color: rgb(s.bg || [1, 1, 1, 1])}];
    page.appendChild(f);
    buildLayers(f, s.layers, 0, 0);
    const hs = [];
    for (const h of s.hotspots) { const r = hotspotRect(f, `Hotspot: ${h.label || h.action.to || h.action.type}`, h.x, h.y, h.w, h.h); hs.push(r); pending.push([r, h.action, f]); }
    frames[s.id] = f;
    x += d.w + GAP; tallest = Math.max(tallest, s.h);
  }

  const oy0 = tallest + 400;
  label(page, 'Pop-ups (opened from the screens above)', 0, oy0 - 110, 40);
  x = 0;
  for (const o of d.overlays) {
    if (!used.has(o.id)) continue;
    const f = figma.createFrame();
    f.name = `${title} / Pop-up: ${o.name}`;
    f.resize(d.w, d.h); f.x = x; f.y = oy0;
    f.clipsContent = true;
    page.appendChild(f);
    let ox = 0, oy = 0;
    if (o.kind === 'dialog') {
      // Dimmed backdrop; clicking outside the dialog closes it.
      f.fills = [{type: 'SOLID', color: {r: 0.035, g: 0.024, b: 0.055}, opacity: 0.6}];
      ox = Math.round((d.w - o.w) / 2); oy = Math.max(0, Math.round((d.h - o.h) / 2));
      for (const [bx, by, bw, bh] of [[0, 0, d.w, oy], [0, oy + o.h, d.w, d.h - oy - o.h], [0, oy, ox, o.h], [ox + o.w, oy, d.w - ox - o.w, o.h]])
        if (bw > 0 && bh > 0) pending.push([hotspotRect(f, 'Hotspot: close (backdrop)', bx, by, bw, bh), {type: 'close'}, f]);
      const inner = figma.createFrame();
      inner.name = o.name; inner.resize(o.w, o.h); inner.x = ox; inner.y = oy; inner.fills = []; inner.clipsContent = true;
      f.appendChild(inner);
      buildLayers(inner, o.layers, 0, 0);
    } else {
      // Phone menu: pinned to the top; tapping below it closes the menu.
      f.fills = [];
      buildLayers(f, o.layers, 0, 0);
      pending.push([hotspotRect(f, 'Hotspot: close (backdrop)', 0, o.h, d.w, d.h - o.h), {type: 'close'}, f]);
    }
    for (const h of o.hotspots) {
      if (h.y < -1 || h.y + h.h > o.h + 1) continue; // scrolled out of the pop-up's visible area
      pending.push([hotspotRect(f, `Hotspot: ${h.label || h.action.type}`, h.x + ox, h.y + oy, h.w, h.h), h.action, f]);
    }
    frames[o.id] = f;
    x += d.w + GAP;
  }

  for (const [node, a, frame] of pending) {
    let action = null;
    if (a.type === 'navigate' || a.type === 'overlay') {
      const dest = frames[a.to];
      if (dest) action = {type: 'NODE', destinationId: dest.id, navigation: a.type === 'overlay' ? 'OVERLAY' : 'NAVIGATE', transition: null, preserveScrollPosition: false};
    } else if (a.type === 'scroll') {
      const anchor = hotspotRect(frame, 'Anchor', 0, a.y, 1, 1);
      action = {type: 'NODE', destinationId: anchor.id, navigation: 'SCROLL_TO', transition: null, preserveScrollPosition: false};
    } else if (a.type === 'url') {
      action = {type: 'URL', url: a.url};
    } else if (a.type === 'close') {
      action = {type: 'CLOSE'};
    }
    if (action) await setClick(node, action); else node.remove();
  }
  // Keep each frame's hotspots together in one group at the top of the layer list.
  for (const f of Object.values(frames)) {
    const hs = f.children.filter(c => c.type === 'RECTANGLE' && /^(Hotspot|Anchor)/.test(c.name));
    if (hs.length > 1) { try { const g = figma.group(hs, f); g.name = 'Hotspots (prototype links)'; } catch (e) { /* optional */ } }
  }

  page.flowStartingPoints = [{nodeId: frames.home.id, name: `${title}: start on Home`}];
  return {page, home: frames.home};
}

(async () => {
  try {
    await loadFonts();
    if (family !== 'Karbon') figma.notify('Karbon is not installed on this computer, so the text uses Inter. Install Karbon and run the plugin again to match the design.', {timeout: 8000});
    const built = [];
    for (const d of DATA.devices) built.push(await buildDevice(d));
    await figma.setCurrentPageAsync(built[0].page);
    figma.viewport.scrollAndZoomIntoView([built[0].home]);
    figma.closePlugin(`Remarkable 2027 prototype ready (text in ${family}): open a prototype page and press Present (▶).`);
  } catch (e) {
    figma.closePlugin('The prototype could not be built: ' + (e && e.message ? e.message : e));
  }
})();
