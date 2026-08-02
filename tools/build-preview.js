// Bundle the preview into a single self-contained HTML file, so it can be
// opened straight off disk or hosted anywhere without a module server.
//
//   node tools/build-preview.js
//   node tools/build-preview.js --src /path/to/old/src --out dist/preview-v1.html
//
// The --src form is how earlier cuts of the piece are rebuilt from git for
// side-by-side comparison; see tools/build-archive.sh.
import { build } from 'esbuild';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const src = resolve(root, arg('src', 'src'));
const out = resolve(root, arg('out', 'dist/preview.html'));
const banner = arg('banner', '');
const title = arg('title', '');

const result = await build({
  entryPoints: [resolve(src, 'preview-main.js')],
  bundle: true,
  format: 'iife',
  target: 'es2020',
  write: false,
  legalComments: 'none',
});

const js = result.outputFiles[0].text;
let html = readFileSync(resolve(src, 'preview.html'), 'utf8');

html = html.replace(
  '<script type="module" src="./preview-main.js"></script>',
  `<script>\n${js}\n</script>`
);

// Archived cuts need their own <title>, or several open tabs are
// indistinguishable from each other and from the current version.
if (title) {
  html = html.replace(/<title>[\s\S]*?<\/title>/, `<title>${title}</title>`);
}

// An optional banner marks archived cuts so they cannot be mistaken for the
// current one when several are open at once.
if (banner) {
  html = html.replace(
    '<body>',
    `<body>\n<div style="background:#3a1420;border-bottom:1px solid #6b2038;color:#ffb3cd;` +
      `padding:9px 26px;font:600 12px/1.4 system-ui,sans-serif;letter-spacing:.06em;` +
      `text-transform:uppercase">${banner}</div>`
  );
}

mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, html);
console.log(`wrote ${out}  (${(html.length / 1024).toFixed(0)} kB, self-contained)`);
