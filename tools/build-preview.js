// Bundle the preview into a single self-contained HTML file, so it can be
// opened straight off disk or hosted anywhere without a module server.
import { build } from 'esbuild';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const out = process.argv[2] || resolve(root, 'dist/preview.html');

const result = await build({
  entryPoints: [resolve(root, 'src/preview-main.js')],
  bundle: true,
  format: 'iife',
  target: 'es2020',
  write: false,
  legalComments: 'none',
});

const js = result.outputFiles[0].text;
const html = readFileSync(resolve(root, 'src/preview.html'), 'utf8');

const inlined = html.replace(
  '<script type="module" src="./preview-main.js"></script>',
  `<script>\n${js}\n</script>`
);

mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, inlined);
console.log(`wrote ${out}  (${(inlined.length / 1024).toFixed(0)} kB, self-contained)`);
