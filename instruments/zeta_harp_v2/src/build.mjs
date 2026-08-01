/* Assemble public/observatory.html from src/ parts + compact fixture excerpts.
   Usage: node src/build.mjs   (run from instruments/zeta_harp_v2/) */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const fixDir = join(root, 'reference', 'fixtures');

function sig(x, d) { return Number(Number(x).toPrecision(d)); }

/* --- compact fixture excerpts ------------------------------------------- */
const windows = {};
for (const key of ['W1', 'W2', 'W3', 'W4']) {
  const f = JSON.parse(readFileSync(join(fixDir, `window_${key}.json`), 'utf8'));
  const M = [], Z = [], R = [];
  for (const row of f.rows) {
    M.push(sig(row.M, 13));
    Z.push(sig(row.Z_ref, 13));
    R.push(sig(row.R_ref, 13));
  }
  windows[key] = {
    range: [Number(f.t_range[0]), Number(f.t_range[1])],
    step: Number(f.step),
    M, Z, R
  };
}
const zf = JSON.parse(readFileSync(join(fixDir, 'zeros_reference.json'), 'utf8'));
const zeros = zf.rows.map(r => ({
  i: r.table_index,
  g: Number(r.gamma_refined),
  gs: r.gamma_refined.slice(0, 30),
  zp: sig(r.Z_prime_at_gamma, 10),
  az: r.abs_Z_at_gamma,
  off: r.refine_offset
}));

const fixtures = JSON.stringify({
  note: 'Compact excerpts of the frozen Gate-2 fixtures (13 sig digits). ' +
    'Full-precision originals + SHA-256 manifest: instruments/zeta_harp_v2/reference/fixtures/. ' +
    'Zero list: Odlyzko-derived, mpmath-refined, NOT certified.',
  windows, zeros
});

/* --- assemble ------------------------------------------------------------ */
const css = readFileSync(join(here, 'style.css'), 'utf8');
const math = readFileSync(join(here, 'math.js'), 'utf8');
const fence = readFileSync(join(here, 'fence.html'), 'utf8');
const app = ['app_state.js', 'render3d.js', 'panels.js', 'audio.js', 'main.js']
  .map(f => readFileSync(join(here, f), 'utf8')).join('\n');
const appWrapped = "(function(){\n'use strict';\n" + app + "\n})();\n";

let html = readFileSync(join(here, 'shell.html'), 'utf8');
html = html.split('%CSS%').join(css);
html = html.split('%FENCE%').join(fence);
html = html.split('%FIXTURES%').join(fixtures);
html = html.split('%MATH%').join(math);
html = html.split('%APP%').join(appWrapped);

const out = join(root, 'public', 'observatory.html');
writeFileSync(out, html);
console.log('wrote', out, (html.length / 1024).toFixed(1) + ' KiB');
