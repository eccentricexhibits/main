// Bundles the game and the animation viewer into single self-contained HTML files
// (code, CSS and Three.js inlined) that can be opened straight from disk via file://.
// Usage: npm install && npm run build   ->  dist/mario64-playground.html, dist/mario64-viewer.html

import { build } from 'esbuild';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');

const PAGES = [
  { html: 'index.html', entry: 'src/main.js', out: 'mario64-playground.html' },
  { html: 'viewer.html', entry: 'src/viewer.js', out: 'mario64-viewer.html' },
  { html: 'cow.html', entry: 'src/cowgame/main.js', out: 'leave-me-alone.html' },
];
// Links between the pages point at the bundled file names.
const LINKS = { 'href="viewer.html"': 'href="mario64-viewer.html"', 'href="index.html"': 'href="mario64-playground.html"', 'href="cow.html"': 'href="leave-me-alone.html"' };

// Browsers refuse fetch() from file:// pages, so the cow model is embedded as base64
// and handed to the loader as a blob: URL.
const cowAssetPlugin = {
  name: 'embed-cow',
  setup(b) {
    b.onResolve({ filter: /cowAsset\.js$/ }, (args) => ({ path: path.join(args.resolveDir, args.path), namespace: 'cow-asset' }));
    b.onLoad({ filter: /.*/, namespace: 'cow-asset' }, async () => {
      const glb = await readFile(path.join(root, 'assets/misanthropic_cow.glb'));
      return {
        contents: `const b64 = ${JSON.stringify(glb.toString('base64'))};
const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
export const COW_URL = URL.createObjectURL(new Blob([bytes], { type: 'model/gltf-binary' }));`,
        loader: 'js',
      };
    });
  },
};

async function bundle(entry) {
  const result = await build({
    plugins: [cowAssetPlugin],
    entryPoints: [path.join(root, entry)],
    bundle: true,
    format: 'esm',
    minify: true,
    write: false,
    alias: { three: path.join(root, 'vendor/three.module.min.js') },
    legalComments: 'inline',
  });
  // An inline script must not contain a literal closing script tag.
  return result.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');
}

await mkdir(dist, { recursive: true });
const css = await readFile(path.join(root, 'style.css'), 'utf8');

for (const page of PAGES) {
  let html = await readFile(path.join(root, page.html), 'utf8');
  const js = await bundle(page.entry);
  html = html
    .replace(/<script type="importmap">[\s\S]*?<\/script>\n?/, '')
    .replace('<link rel="stylesheet" href="style.css">', () => `<style>\n${css}</style>`)
    .replace(/<script type="module" src="[^"]+"><\/script>/, () => `<script type="module">\n${js}</script>`);
  for (const [from, to] of Object.entries(LINKS)) html = html.split(from).join(to);
  await writeFile(path.join(dist, page.out), html);
  console.log(`dist/${page.out}  ${(html.length / 1024).toFixed(0)} KB`);
}
