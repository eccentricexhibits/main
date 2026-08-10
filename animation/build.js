#!/usr/bin/env node
/*
 * Inlines the engine (and, for the mock-up, the Karbon brand faces) into
 * self-contained single-file HTML deliverables.
 *
 *   node animation/build.js
 */
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const dir = __dirname;
const engine = fs.readFileSync(path.join(dir, 'arrow-field.js'), 'utf8');

function fontDataUri(file) {
  const b64 = fs.readFileSync(path.join(root, file)).toString('base64');
  return `data:font/otf;base64,${b64}`;
}

const substitutions = {
  '/* __ENGINE__ */': engine,
  '__KARBON_REGULAR__': () => fontDataUri('Karbon-Regular.otf'),
  '__KARBON_SEMIBOLD__': () => fontDataUri('Karbon-Semibold.otf'),
};

function build(template, output) {
  const source = path.join(dir, 'templates', template);
  if (!fs.existsSync(source)) return;
  let html = fs.readFileSync(source, 'utf8');
  for (const [token, value] of Object.entries(substitutions)) {
    if (!html.includes(token)) continue;
    html = html.split(token).join(typeof value === 'function' ? value() : value);
  }
  const target = path.join(dir, output);
  fs.writeFileSync(target, html);
  console.log(`${output}  ${(fs.statSync(target).size / 1024).toFixed(0)} KB`);
}

build('render.html', 'arrow-animation-render.html');
build('mockup.html', 'arrow-animation-mockup.html');
