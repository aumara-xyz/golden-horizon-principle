/* Gate 3-6 self-check harness.
   Extracts the inline math core and fixtures from public/observatory.html,
   syntax-checks every script block with `node --check`, then validates the
   inline theta / theta' / M(t) against the FULL-precision Gate-2 fixtures
   (reference/fixtures/*.json) at every grid point, per VALIDATION_PLAN.md.
   Exit code 0 = all tolerances met. */
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const html = readFileSync(join(root, 'public', 'observatory.html'), 'utf8');

function extract(id) {
  const open = html.indexOf(`<script id="${id}"`);
  if (open < 0) throw new Error(`missing script ${id}`);
  const start = html.indexOf('>', open) + 1;
  const end = html.indexOf('</script>', start);
  return html.slice(start, end);
}

const mathSrc = extract('zh-math');
const appSrc = extract('zh-app');
const fxEmbedded = JSON.parse(extract('zh-fixtures'));

/* --- 1. syntax check both script blocks --------------------------------- */
const tdir = mkdtempSync(join(tmpdir(), 'zh-check-'));
writeFileSync(join(tdir, 'math.js'), mathSrc);
writeFileSync(join(tdir, 'app.js'), appSrc);
for (const f of ['math.js', 'app.js']) {
  execFileSync(process.execPath, ['--check', join(tdir, f)]);
  console.log(`node --check ${f}: OK`);
}

/* --- 2. load the inline math core ---------------------------------------- */
(0, eval)(mathSrc);
const ZH = globalThis.ZH;
if (!ZH || typeof ZH.M !== 'function') throw new Error('ZH core did not load');

/* --- 3. validate against full-precision fixtures -------------------------- */
const TOL = {
  /* VALIDATION_PLAN targets, extended per-window (see MATHEMATICIAN_NOTE):
     theta W1 target < 1e-6 rad; W4 sits at the float64 phase frontier. */
  theta: { W1: 1e-6, W2: 1e-6, W3: 1e-6, W4: 1e-5 },
  thetaP: { W1: 1e-8, W2: 1e-8, W3: 1e-8, W4: 1e-8 },
  M: { W1: 1e-9, W2: 1e-8, W3: 1e-6, W4: 1e-3 },
  embedM: 1e-10   /* embedded 13-digit excerpt vs full fixture */
};
let fail = 0;
const rows = [];
for (const key of ['W1', 'W2', 'W3', 'W4']) {
  const fx = JSON.parse(readFileSync(join(root, 'reference', 'fixtures', `window_${key}.json`), 'utf8'));
  let dTheta = 0, dThetaP = 0, dM = 0, dEmbed = 0, dN = 0;
  fx.rows.forEach((row, i) => {
    const t = Number(row.t);
    dTheta = Math.max(dTheta, Math.abs(ZH.theta(t) - Number(row.theta)));
    dThetaP = Math.max(dThetaP, Math.abs(ZH.thetaPrime(t) - Number(row.theta_prime)));
    dM = Math.max(dM, Math.abs(ZH.M(t) - Number(row.M)));
    if (ZH.Nt(t) !== row.N) dN++;
    const emb = fxEmbedded.windows[key];
    dEmbed = Math.max(dEmbed, Math.abs(emb.M[i] - Number(row.M)),
      Math.abs(emb.Z[i] - Number(row.Z_ref)), Math.abs(emb.R[i] - Number(row.R_ref)));
  });
  const ok = dTheta <= TOL.theta[key] && dThetaP <= TOL.thetaP[key] &&
    dM <= TOL.M[key] && dEmbed <= TOL.embedM && dN === 0;
  if (!ok) fail++;
  rows.push({ key, pts: fx.rows.length, dTheta, dThetaP, dM, dEmbed, dN, ok });
}
console.log('\nwindow  pts  max|dTheta|   max|dTheta\'|  max|dM|      max|embed-full|  N-mismatch  verdict');
for (const r of rows) {
  console.log(
    `${r.key}      ${String(r.pts).padEnd(4)} ${r.dTheta.toExponential(3)}    ${r.dThetaP.toExponential(3)}     ` +
    `${r.dM.toExponential(3)}   ${r.dEmbed.toExponential(3)}       ${r.dN}           ${r.ok ? 'PASS' : 'FAIL'}`);
}

/* --- 4. cutoff-entry consistency inside W1 -------------------------------- */
for (const n of [4, 5]) {
  const tn = ZH.cutoffT(n);
  const below = ZH.Nt(tn - 1e-9), at = ZH.Nt(tn);
  const ok = below === n - 1 && at === n;
  console.log(`cutoff entry n=${n}: t_n=${tn.toFixed(9)}  N(t_n-)=${below}  N(t_n)=${at}  ${ok ? 'PASS' : 'FAIL'}`);
  if (!ok) fail++;
}

/* --- 5. audio-frequency derivative check (W1 + W2 grids) ------------------- */
let worstAbs = 0;
for (const key of ['W1', 'W2']) {
  const fx = JSON.parse(readFileSync(join(root, 'reference', 'fixtures', `window_${key}.json`), 'utf8'));
  const h = key === 'W1' ? 0.01 : 0.05;   /* balances O(h^2 theta''') truncation vs float64 noise/h */
  for (const row of fx.rows) {
    const t = Number(row.t), N = row.N;
    for (const n of [1, Math.max(1, Math.floor(N / 2)), N]) {
      const fd = (ZH.phin(n, t + h) - ZH.phin(n, t - h)) / (2 * h);
      const cf = ZH.omegan(n, t);
      worstAbs = Math.max(worstAbs, Math.abs(fd - cf));
    }
  }
}
const audioOk = worstAbs < 1e-8;   /* rad per unit t; pins "you hear the phase derivative" */
console.log(`audio-law derivative check (W1+W2): worst |central-diff - (theta'-ln n)| = ${worstAbs.toExponential(3)} rad/unit-t  ${audioOk ? 'PASS' : 'FAIL'}`);
if (!audioOk) fail++;

/* --- 6. crossing offsets at refined reference zeros ------------------------ */
console.log('\nrefined zero -> main-sum computed crossing offsets (finite-sum error, reported not gated):');
const sample = [0, 1, 10, 20, 30, 39];
for (const i of sample) {
  const z = fxEmbedded.zeros[i];
  const tc = ZH.bisectM(z.g - 0.6, z.g + 0.6, 90) ?? ZH.bisectM(z.g - 1.5, z.g + 1.5, 90);
  console.log(`  #${String(z.i).padEnd(6)} gamma=${z.gs.slice(0, 18).padEnd(20)} crossing=${tc === null ? 'none in ±1.5' : tc.toFixed(9)}  offset=${tc === null ? '—' : (tc - z.g).toExponential(3)}`);
}

console.log(fail === 0 ? '\nALL CHECKS PASS' : `\n${fail} CHECK GROUP(S) FAILED`);
process.exit(fail === 0 ? 0 : 1);
