/* ==========================================================================
   2D panels: Z ribbon, phasor flower, term inspector, zero microscope.
   ========================================================================== */

function panelVisible(id) {
  return !document.getElementById(id).classList.contains('hidden');
}

var COL = { gold: '#e2b45a', blue: '#5b8ef2', purple: '#a06bff', dim: '#6b7890',
  faint: '#3a4459', ink: '#c6d1e2' };

function fitCanvas(cv) {
  var dpr = Math.min(2, window.devicePixelRatio || 1);
  var w = Math.floor(cv.clientWidth * dpr), h = Math.floor(cv.clientHeight * dpr);
  if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
  var ctx = cv.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
}

/* ---- Z ribbon ----------------------------------------------------------- */
function drawRibbon() {
  if (!panelVisible('ribbonPanel')) return;
  var cv = document.getElementById('ribbon');
  var ctx = fitCanvas(cv);
  var W = cv.clientWidth, H = cv.clientHeight;
  ctx.clearRect(0, 0, W, H);
  var t0 = ST.t, hw = halfWindow(t0), tLo = t0 - hw, tHi = t0 + hw;
  var fk = fixtureOverlap(tLo, tHi);
  var fw = fk ? FX.windows[fk] : null;

  /* y-scale from M samples and fixture values in range */
  var ymax = 0.5, k;
  for (k = 0; k < RIB_K; k++) ymax = Math.max(ymax, Math.abs(RIB.x[k]));
  if (fw && ST.layers.Z) {
    for (k = 0; k < fw.Z.length; k++) {
      var tf = fw.range[0] + k * fw.step;
      if (tf >= tLo && tf <= tHi) ymax = Math.max(ymax, Math.abs(fw.Z[k]));
    }
  }
  ymax *= 1.12;
  function X(t) { return (t - tLo) / (tHi - tLo) * W; }
  function Y(v) { return H / 2 - v / ymax * (H / 2 - 6); }

  ctx.strokeStyle = 'rgba(198,214,240,0.10)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, Y(0)); ctx.lineTo(W, Y(0)); ctx.stroke();

  /* fixture layers */
  /* fixture values are exact only AT grid points; the connecting line is a
     visual aid drawn faint (at high t the grid undersamples Z's oscillation) */
  function plotFixture(vals, color, dotColor) {
    ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.beginPath();
    var started = false, i, tf2;
    for (i = 0; i < vals.length; i++) {
      tf2 = fw.range[0] + i * fw.step;
      if (tf2 < tLo || tf2 > tHi) { started = false; continue; }
      var x = X(tf2), y = Y(vals[i]);
      if (!started) { ctx.moveTo(x, y); started = true; } else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.fillStyle = dotColor;
    for (i = 0; i < vals.length; i++) {
      tf2 = fw.range[0] + i * fw.step;
      if (tf2 < tLo || tf2 > tHi) continue;
      ctx.fillRect(X(tf2) - 1.25, Y(vals[i]) - 1.25, 2.5, 2.5);
    }
  }
  if (fw && ST.layers.R) plotFixture(fw.R, 'rgba(160,107,255,0.30)', 'rgba(160,107,255,0.9)');
  if (fw && ST.layers.Z) plotFixture(fw.Z, 'rgba(91,142,242,0.35)', 'rgba(120,166,255,0.95)');

  /* main sum */
  if (ST.layers.M && RIB.valid) {
    ctx.strokeStyle = COL.gold; ctx.lineWidth = 1.6; ctx.beginPath();
    for (k = 0; k < RIB_K; k++) {
      var x2 = X(t0 + RIB.u[k]), y2 = Y(RIB.x[k]);
      if (k === 0) ctx.moveTo(x2, y2); else ctx.lineTo(x2, y2);
    }
    ctx.stroke();
  }

  /* refined reference zeros in range */
  for (k = 0; k < FX.zeros.length; k++) {
    var g = FX.zeros[k].g;
    if (g >= tLo && g <= tHi) {
      ctx.strokeStyle = 'rgba(143,208,168,0.8)';
      ctx.beginPath(); ctx.moveTo(X(g), H - 12); ctx.lineTo(X(g), H); ctx.stroke();
    }
  }

  /* t0 marker */
  ctx.strokeStyle = 'rgba(226,180,90,0.5)';
  ctx.beginPath(); ctx.moveTo(X(t0), 0); ctx.lineTo(X(t0), H); ctx.stroke();

  ctx.fillStyle = COL.dim; ctx.font = '9px ui-monospace, monospace';
  ctx.fillText(fmtT(tLo), 4, H - 4);
  var lbl = fmtT(tHi);
  ctx.fillText(lbl, W - ctx.measureText(lbl).width - 4, H - 4);
  ctx.fillText('±' + fmtSig(ymax, 3), 4, 10);

  document.getElementById('ribbonNote').textContent = fw
    ? 'fixture ' + fk + ' overlays active (high-precision reference)'
    : 'no reference fixture in this window — main sum only';
}

/* ---- phasor flower ------------------------------------------------------ */
function drawFlower() {
  if (!panelVisible('flowerPanel')) return;
  var cv = document.getElementById('flower');
  var ctx = fitCanvas(cv);
  var W = cv.clientWidth, H = cv.clientHeight;
  ctx.clearRect(0, 0, W, H);
  var cx = W / 2, cy = H / 2;

  /* scale: fit the largest of a_1 and the partial-sum path */
  var maxR = 2, run = 0, ix = 0, iy = 0, k;
  var partial = [[0, 0]];
  for (k = 0; k < TERMS.N; k++) {
    ix += TERMS.a[k] * Math.cos(TERMS.phi0[k]);
    iy += TERMS.a[k] * Math.sin(TERMS.phi0[k]);
    partial.push([ix, iy]);
    maxR = Math.max(maxR, Math.hypot(ix, iy));
  }
  var S = (Math.min(W, H) / 2 - 14) / (maxR * 1.05);
  function PX(x) { return cx + x * S; }
  function PY(y) { return cy - y * S; }

  /* axes */
  ctx.strokeStyle = 'rgba(198,214,240,0.12)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, cy); ctx.lineTo(W, cy); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(cx, 0); ctx.lineTo(cx, H); ctx.stroke();
  ctx.fillStyle = COL.dim; ctx.font = '9px ui-monospace, monospace';
  ctx.fillText('Re — real part (sums to M(t))', W - 172, cy - 5);
  ctx.save(); ctx.translate(cx + 5, 12); ctx.fillText('Im — auxiliary coordinate', 0, 0); ctx.restore();

  /* unit circles a_1, a_2 */
  ctx.strokeStyle = 'rgba(198,214,240,0.05)';
  ctx.beginPath(); ctx.arc(cx, cy, 2 * S, 0, Math.PI * 2); ctx.stroke();

  /* spokes + projection drops */
  for (k = 0; k < TERMS.N; k++) {
    var px = TERMS.a[k] * Math.cos(TERMS.phi0[k]);
    var py = TERMS.a[k] * Math.sin(TERMS.phi0[k]);
    var pos = TERMS.c[k] >= 0;
    var col = pos ? 'rgba(91,142,242,' : 'rgba(160,107,255,';
    var alpha = Math.max(0.14, Math.min(0.85, TERMS.a[k] * 0.5));
    ctx.strokeStyle = col + alpha + ')';
    ctx.lineWidth = k + 1 === ST.sel ? 2.4 : 1;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(PX(px), PY(py)); ctx.stroke();
    ctx.strokeStyle = col + (alpha * 0.35) + ')';
    ctx.setLineDash([2, 3]);
    ctx.beginPath(); ctx.moveTo(PX(px), PY(py)); ctx.lineTo(PX(px), cy); ctx.stroke();
    ctx.setLineDash([]);
  }

  /* cumulative polygon in n-order */
  ctx.strokeStyle = 'rgba(226,180,90,0.85)'; ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(PX(0), PY(0));
  for (k = 1; k < partial.length; k++) ctx.lineTo(PX(partial[k][0]), PY(partial[k][1]));
  ctx.stroke();

  /* resultant */
  ctx.strokeStyle = COL.gold; ctx.lineWidth = 2.2;
  ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(PX(ix), PY(iy)); ctx.stroke();
  ctx.fillStyle = COL.gold;
  ctx.beginPath(); ctx.arc(PX(ix), PY(iy), 3, 0, Math.PI * 2); ctx.fill();
  /* real-axis projection of the resultant = M(t) */
  ctx.strokeStyle = 'rgba(226,180,90,0.5)'; ctx.setLineDash([3, 3]);
  ctx.beginPath(); ctx.moveTo(PX(ix), PY(iy)); ctx.lineTo(PX(ix), cy); ctx.stroke();
  ctx.setLineDash([]);

  var fi = fixtureInterp(ST.t);
  var el = document.getElementById('flowerNums');
  el.innerHTML =
    '<span class="k">t frozen at</span> <span class="v">' + fmtT(ST.t) + '</span> ' +
    '<span class="k">· N(t)</span> <span class="v">' + TERMS.N + '</span><br>' +
    '<span class="k">resultant Re = M(t)</span> <span class="g">' + fmtSig(ix, 6) + '</span> ' +
    '<span class="k">· Im (auxiliary)</span> <span class="v">' + fmtSig(iy, 4) + '</span><br>' +
    (fi
      ? '<span class="k">Z_ref (fixture ' + fi.win + ', interp)</span> <span class="v">' + fmtSig(fi.Z, 6) +
        '</span> <span class="k">· R_ref</span> <span class="v">' + fmtSig(fi.R, 4) +
        '</span> <span class="k">· |M &minus; Z_ref|</span> <span class="v">' + fmtSig(Math.abs(ix - fi.Z), 3) + '</span>'
      : '<span class="k">Z_ref: no fixture at this height (fixtures: W1-W4)</span>');
}

function flowerPick(evt) {
  var cv = document.getElementById('flower');
  var r = cv.getBoundingClientRect();
  var mx = evt.clientX - r.left, my = evt.clientY - r.top;
  var W = cv.clientWidth, H = cv.clientHeight, cx = W / 2, cy = H / 2;
  var maxR = 2, ix = 0, iy = 0, k;
  for (k = 0; k < TERMS.N; k++) {
    ix += TERMS.a[k] * Math.cos(TERMS.phi0[k]);
    iy += TERMS.a[k] * Math.sin(TERMS.phi0[k]);
    maxR = Math.max(maxR, Math.hypot(ix, iy));
  }
  var S = (Math.min(W, H) / 2 - 14) / (maxR * 1.05);
  var best = -1, bestD = 14;
  for (k = 0; k < TERMS.N; k++) {
    var px = cx + TERMS.a[k] * Math.cos(TERMS.phi0[k]) * S;
    var py = cy - TERMS.a[k] * Math.sin(TERMS.phi0[k]) * S;
    var d = Math.hypot(px - mx, py - my);
    if (d < bestD) { bestD = d; best = k + 1; }
  }
  if (best > 0) selectTerm(best);
}

/* ---- term inspector ----------------------------------------------------- */
function selectTerm(n) {
  ST.sel = n;
  showPanel('inspectorPanel', true);
  updateInspector();
}
function updateInspector() {
  var el = document.getElementById('inspectorBody');
  var n = ST.sel;
  if (!(n >= 1)) { el.textContent = 'click a helix or a phasor to select a term'; return; }
  var t = ST.t;
  var inSum = n <= TERMS.N;
  var phi = ZH.mod2pi(ZH.phin(n, t));
  el.innerHTML =
    '<span class="k">term n</span> <span class="g">' + n + '</span>' +
    (inSum ? '' : ' <span class="k">(not yet in the sum at this t)</span>') + '<br>' +
    '<span class="k">a_n = 2/&radic;n</span> <span class="v">' + fmtSig(ZH.an(n), 6) + '</span> <span class="k">(computed spectral)</span><br>' +
    '<span class="k">&phi;_n(t) mod 2&pi;</span> <span class="v">' + fmtSig(phi, 6) + ' rad</span><br>' +
    '<span class="k">c_n(t) = a_n cos &phi;_n</span> <span class="v">' + fmtSig(ZH.cn(n, t), 6) + '</span><br>' +
    '<span class="k">f_n = (&theta;&prime;&minus;ln n)/2&pi;</span> <span class="v">' + fmtSig(ZH.fn(n, t), 5) + ' cycles / unit t</span><br>' +
    '<span class="k">cutoff entry t_n = 2&pi;n&sup2;</span> <span class="v">' + fmtT(ZH.cutoffT(n)) + '</span> <span class="k">(a height, not a frequency)</span><br>' +
    '<span class="k">f_audio at v_t=' + fmtSig(ST.vt, 3) + '</span> <span class="v">' + fmtSig(ZH.fAudio(n, t, ST.vt), 5) + ' Hz</span>';
  var vb = document.getElementById('voiceBtn');
  var voiced = ST.voiced.indexOf(n) >= 0;
  vb.textContent = voiced ? 'unvoice term ' + n : 'voice term ' + n;
  vb.classList.toggle('on', voiced);
}

/* ---- zero microscope ---------------------------------------------------- */
var MICRO = { idx: -1, gamma: 0, tc: null, slope: 0 };

function microInit() {
  var sel = document.getElementById('microZeroSel');
  var opts = '';
  for (var i = 0; i < FX.zeros.length; i++) {
    var z = FX.zeros[i];
    opts += '<option value="' + i + '">#' + z.i + '  ·  γ ≈ ' + z.gs.slice(0, 18) + '</option>';
  }
  sel.innerHTML = opts;
  sel.addEventListener('change', function () { microSelect(+sel.value); });
}

function microSelect(i) {
  MICRO.idx = i;
  document.getElementById('microZeroSel').value = String(i);
  var z = FX.zeros[i];
  MICRO.gamma = z.g;
  MICRO.tc = ZH.bisectM(z.g - 0.6, z.g + 0.6, 90);
  if (MICRO.tc === null) {
    /* widen: some low-t crossings sit farther from gamma (large remainder) */
    MICRO.tc = ZH.bisectM(z.g - 1.5, z.g + 1.5, 90);
  }
  var h = 1e-5;
  MICRO.slope = MICRO.tc !== null ? (ZH.M(MICRO.tc + h) - ZH.M(MICRO.tc - h)) / (2 * h) : 0;
  glideTo(z.g);
  drawMicro();
}

function drawMicro() {
  if (MICRO.idx < 0) return;
  var z = FX.zeros[MICRO.idx];
  if (!panelVisible('microPanel')) return;
  var cvC = document.getElementById('microCurve');
  var ctx = fitCanvas(cvC);
  var W = cvC.clientWidth, H = cvC.clientHeight;
  ctx.clearRect(0, 0, W, H);
  var hw = 1.6, tLo = z.g - hw, tHi = z.g + hw, K = 360;
  var vals = new Float64Array(K), ymax = 0.3, k;
  for (k = 0; k < K; k++) {
    vals[k] = ZH.M(tLo + (tHi - tLo) * k / (K - 1));
    ymax = Math.max(ymax, Math.abs(vals[k]));
  }
  ymax *= 1.15;
  function X(t) { return (t - tLo) / (tHi - tLo) * W; }
  function Y(v) { return H / 2 - v / ymax * (H / 2 - 8); }
  ctx.strokeStyle = 'rgba(198,214,240,0.10)';
  ctx.beginPath(); ctx.moveTo(0, Y(0)); ctx.lineTo(W, Y(0)); ctx.stroke();
  ctx.strokeStyle = COL.gold; ctx.lineWidth = 1.5; ctx.beginPath();
  for (k = 0; k < K; k++) {
    var x = X(tLo + (tHi - tLo) * k / (K - 1)), y = Y(vals[k]);
    if (k === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
  /* reference gamma */
  ctx.strokeStyle = 'rgba(143,208,168,0.9)';
  ctx.beginPath(); ctx.moveTo(X(z.g), 6); ctx.lineTo(X(z.g), H - 6); ctx.stroke();
  ctx.fillStyle = 'rgba(143,208,168,0.9)'; ctx.font = '9px ui-monospace, monospace';
  ctx.fillText('γ (refined reference)', X(z.g) + 4, 14);
  /* our crossing */
  if (MICRO.tc !== null) {
    ctx.strokeStyle = 'rgba(226,180,90,0.8)'; ctx.setLineDash([3, 3]);
    ctx.beginPath(); ctx.moveTo(X(MICRO.tc), 6); ctx.lineTo(X(MICRO.tc), H - 6); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(226,180,90,0.8)';
    ctx.fillText('computed crossing (finite approximation)', Math.min(X(MICRO.tc) + 4, W - 210), H - 10);
  }
  ctx.fillStyle = COL.dim;
  ctx.fillText('M(t) over γ ± ' + hw, 6, H - 10);

  /* ---- bars: contributions frozen at gamma ---- */
  var cvB = document.getElementById('microBars');
  var ctxB = fitCanvas(cvB);
  var WB = cvB.clientWidth, HB = cvB.clientHeight;
  ctxB.clearRect(0, 0, WB, HB);
  var N = ZH.Nt(z.g), pos = [], neg = [], n;
  for (n = 1; n <= N; n++) {
    var c = ZH.cn(n, z.g);
    (c >= 0 ? pos : neg).push([n, c]);
  }
  pos.sort(function (a, b) { return b[1] - a[1]; });
  neg.sort(function (a, b) { return a[1] - b[1]; });
  var Mg = ZH.M(z.g);
  var Rg = 0 - Mg;   /* Z_ref(gamma) ~ 0 to ~1e-50 (refined list), so R = Z - M = -M */
  var sumPos = 0, sumNeg = 0;
  for (k = 0; k < pos.length; k++) sumPos += pos[k][1];
  for (k = 0; k < neg.length; k++) sumNeg += neg[k][1];
  var span = Math.max(sumPos, -sumNeg, 0.5) * 1.1;
  var mid = WB / 2;
  function XB(v) { return mid + v / span * (WB / 2 - 10); }
  /* waterfall: positives rightward from 0 (top row), negatives leftward (second row),
     then M and the closing remainder */
  var y0 = 26, bh = 26;
  ctxB.font = '9px ui-monospace, monospace';
  ctxB.fillStyle = COL.dim;
  ctxB.fillText('positive terms  Σ = +' + fmtSig(sumPos, 4), 6, y0 - 8);
  var acc = 0;
  for (k = 0; k < pos.length; k++) {
    ctxB.fillStyle = 'rgba(91,142,242,' + Math.max(0.25, Math.min(0.95, pos[k][1])) + ')';
    ctxB.fillRect(XB(acc), y0, Math.max(1, XB(acc + pos[k][1]) - XB(acc) - 0.5), bh);
    acc += pos[k][1];
  }
  ctxB.fillStyle = COL.dim;
  ctxB.fillText('negative terms  Σ = ' + fmtSig(sumNeg, 4), 6, y0 + bh + 16);
  acc = 0;
  for (k = 0; k < neg.length; k++) {
    ctxB.fillStyle = 'rgba(160,107,255,' + Math.max(0.25, Math.min(0.95, -neg[k][1])) + ')';
    ctxB.fillRect(XB(acc + neg[k][1]), y0 + bh + 22, Math.max(1, XB(acc) - XB(acc + neg[k][1]) - 0.5), bh);
    acc += neg[k][1];
  }
  var y2 = y0 + 2 * bh + 44;
  ctxB.fillStyle = COL.dim;
  ctxB.fillText('residual M(γ) + remainder → Z_ref(γ) ≈ 0', 6, y2 - 8);
  ctxB.fillStyle = COL.gold;
  ctxB.fillRect(Math.min(XB(0), XB(Mg)), y2, Math.max(1.5, Math.abs(XB(Mg) - XB(0))), 12);
  ctxB.fillStyle = 'rgba(143,208,168,0.8)';
  ctxB.fillRect(Math.min(XB(Mg), XB(Mg + Rg)), y2 + 14, Math.max(1.5, Math.abs(XB(Rg))), 12);
  ctxB.strokeStyle = 'rgba(198,214,240,0.25)';
  ctxB.beginPath(); ctxB.moveTo(XB(0), y0 - 4); ctxB.lineTo(XB(0), y2 + 30); ctxB.stroke();

  document.getElementById('microNums').innerHTML =
    '<span class="k">γ (refined)</span> <span class="g">' + esc(z.gs) + '</span><br>' +
    '<span class="k">table index</span> <span class="v">' + z.i + '</span> ' +
    '<span class="k">· refine offset vs table</span> <span class="v">' + esc(z.off) + '</span> ' +
    '<span class="k">· |Z(γ)| after refine</span> <span class="v">' + esc(z.az) + '</span><br>' +
    '<span class="k">Z&prime;(γ) reference slope</span> <span class="v">' + fmtSig(z.zp, 6) + '</span>' +
    (MICRO.tc !== null
      ? '<span class="k"> · our dM/dt at crossing</span> <span class="v">' + fmtSig(MICRO.slope, 6) + '</span>'
      : '') + '<br>' +
    '<span class="k">N(γ)</span> <span class="v">' + N + '</span> ' +
    '<span class="k">· M(γ) main sum</span> <span class="v">' + fmtSig(Mg, 6) + '</span> ' +
    '<span class="k">· remainder closing to Z_ref(γ)≈0:</span> <span class="v">' + fmtSig(Rg, 6) + '</span><br>' +
    (MICRO.tc !== null
      ? '<span class="k">computed crossing t</span> <span class="v">' + MICRO.tc.toFixed(9) + '</span> ' +
        '<span class="k">· offset from γ</span> <span class="g">' + fmtSig(MICRO.tc - z.g, 4) + '</span> ' +
        '<span class="k">(finite-sum error, disclosed)</span>'
      : '<span class="k">no main-sum sign change within γ ± 1.5 (finite approximation limit here)</span>');
}
