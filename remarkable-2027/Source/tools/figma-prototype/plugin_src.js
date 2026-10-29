// Remarkable 2027 prototype builder (Figma plugin).
// Creates two pages, "Desktop prototype" and "Mobile prototype", with one frame per screen, one frame per pop-up,
// and clickable hotspots wired as prototype interactions. Screens are full-page images captured from the HTML mockup.
const DATA = __DATA__;
const IMAGES = __IMAGES__;

const GAP = 200;
const hashes = {};
const imageHash = file => hashes[file] || (hashes[file] = figma.createImage(figma.base64Decode(IMAGES[file])).hash);

function imageRect(parent, file, x, y, w, h) {
  const r = figma.createRectangle();
  r.name = 'Screenshot';
  r.resize(w, h); r.x = x; r.y = y;
  r.fills = [{type: 'IMAGE', scaleMode: 'FILL', imageHash: imageHash(file)}];
  parent.appendChild(r);
  r.locked = true;
  return r;
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

async function label(page, text, x, y, size) {
  try {
    await figma.loadFontAsync({family: 'Inter', style: 'Bold'});
    const t = figma.createText();
    t.fontName = {family: 'Inter', style: 'Bold'}; t.characters = text; t.fontSize = size;
    t.x = x; t.y = y; page.appendChild(t);
  } catch (e) { /* labels are optional */ }
}

async function buildDevice(d) {
  const title = d.id === 'desktop' ? 'Desktop' : 'Mobile';
  const page = figma.createPage();
  page.name = `${title} prototype`;
  await figma.setCurrentPageAsync(page);

  const frames = {};
  const pending = []; // [node, action]
  const used = new Set();
  for (const s of d.screens) for (const h of s.hotspots) if (h.action.type === 'overlay') used.add(h.action.to);
  for (const o of d.overlays) if (used.has(o.id)) for (const h of o.hotspots) if (h.action.type === 'overlay') used.add(h.action.to);

  await label(page, `Remarkable 2027 · ${title} (${d.w} px)`, 0, -260, d.id === 'desktop' ? 72 : 48);
  await label(page, 'Press Present (▶, top right) to click through the prototype.', 0, -150, 28);

  let x = 0, tallest = 0;
  for (const s of d.screens) {
    figma.notify(`Building ${title}: ${s.name}…`, {timeout: 1500});
    const f = figma.createFrame();
    f.name = `${title} / ${s.name}`;
    f.resize(d.w, s.h); f.x = x; f.y = 0;
    f.clipsContent = true;
    f.fills = [{type: 'SOLID', color: {r: 1, g: 1, b: 1}}];
    page.appendChild(f);
    for (const t of s.tiles) imageRect(f, t.file, 0, t.y, d.w, t.h);
    for (const h of s.hotspots) pending.push([hotspotRect(f, `Hotspot: ${h.label || h.action.to || h.action.type}`, h.x, h.y, h.w, h.h), h.action, f]);
    frames[s.id] = f;
    x += d.w + GAP; tallest = Math.max(tallest, s.h);
  }

  const oy0 = tallest + 400;
  await label(page, 'Pop-ups (opened from the screens above)', 0, oy0 - 110, 40);
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
      imageRect(f, o.file, ox, oy, o.w, o.h);
      const close = {type: 'CLOSE'};
      for (const [bx, by, bw, bh] of [[0, 0, d.w, oy], [0, oy + o.h, d.w, d.h - oy - o.h], [0, oy, ox, o.h], [ox + o.w, oy, d.w - ox - o.w, o.h]])
        if (bw > 0 && bh > 0) pending.push([hotspotRect(f, 'Hotspot: close (backdrop)', bx, by, bw, bh), {type: 'close'}, f]);
    } else {
      // Phone menu: pinned to the top; tapping below it closes the menu.
      f.fills = [];
      imageRect(f, o.file, 0, 0, o.w, o.h);
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

  page.flowStartingPoints = [{nodeId: frames.home.id, name: `${title}: start on Home`}];
  return {page, home: frames.home};
}

(async () => {
  try {
    const built = [];
    for (const d of DATA.devices) built.push(await buildDevice(d));
    await figma.setCurrentPageAsync(built[0].page);
    figma.viewport.scrollAndZoomIntoView([built[0].home]);
    figma.closePlugin('Remarkable 2027 prototype ready: open a prototype page and press Present (▶).');
  } catch (e) {
    figma.closePlugin('The prototype could not be built: ' + (e && e.message ? e.message : e));
  }
})();
