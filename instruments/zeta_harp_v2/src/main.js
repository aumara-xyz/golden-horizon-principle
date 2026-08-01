/* ==========================================================================
   Orchestration: navigation, events, opening sequence, fence, main loop.
   ========================================================================== */

var T_MIN = 100, T_MAX = 1e8;

function sliderToT(v) { return Math.pow(10, 2 + 6 * v / 10000); }
function tToSlider(t) { return Math.round((Math.log10(t) - 2) / 6 * 10000); }
function clampT(t) { return Math.max(T_MIN, Math.min(T_MAX, t)); }
function glideTo(t) { ST.tTarget = clampT(t); }

function showPanel(id, on) {
  var el = document.getElementById(id);
  if (on === undefined) on = el.classList.contains('hidden');
  el.classList.toggle('hidden', !on);
  return on;
}

/* ---------------- events: ignition + crossings --------------------------- */
var EV = { labelUntil: 0 };
function showEvent(html, seconds) {
  var el = document.getElementById('eventLabel');
  el.innerHTML = html;
  el.style.opacity = 1;
  EV.labelUntil = performance.now() + (seconds || 2) * 1000;
}
function eventTick(now) {
  if (EV.labelUntil && now > EV.labelUntil) {
    document.getElementById('eventLabel').style.opacity = 0;
    EV.labelUntil = 0;
  }
}
function detectEvents(tPrev, tNow) {
  var Nprev = ZH.Nt(tPrev), Nnow = TERMS.N;
  var dT = Math.abs(tNow - tPrev), hw = halfWindow(tNow);
  if (Nnow > Nprev && Nnow - Nprev <= 3 && dT < hw) {
    for (var n = Nprev + 1; n <= Nnow; n++) {
      var zPos = (ZH.cutoffT(n) - tNow) * zScale(tNow);
      GLR.spawnRing(ZH.an(n) * RSCALE, Math.max(-SCENE_HALF, Math.min(SCENE_HALF, zPos)), 'birth');
      var head = ST.mode === 'temple' ? 'string birth — term ' : 'cutoff entry — term ';
      showEvent(head + n + ' enters the sum' +
        '<div class="sub2">computed spectral amplitude 2/&radic;' + n + ' = ' + fmtSig(ZH.an(n), 5) +
        ' · cutoff-entry height 2&pi;&middot;' + n + '&sup2; = ' + fmtT(ZH.cutoffT(n)) + '</div>', 2);
      chime(n);
    }
  }
  /* main-sum sign change while moving slowly */
  if (dT > 0 && dT < 0.5 * hw) {
    var mPrev = ST.lastM, mNow = Mnow();
    if (mPrev !== undefined && mPrev !== 0 && (mPrev > 0) !== (mNow > 0)) {
      var lo = Math.min(tPrev, tNow), hi = Math.max(tPrev, tNow);
      var tc = ZH.bisectM(lo, hi, 60);
      if (tc !== null) {
        GLR.spawnRing(0.5, 0, 'cross');
        var nearest = null, bd = 0.5;
        for (var i = 0; i < FX.zeros.length; i++) {
          var d = Math.abs(FX.zeros[i].g - tc);
          if (d < bd) { bd = d; nearest = FX.zeros[i]; }
        }
        if (nearest) {
          showEvent('computed crossing at t &asymp; ' + tc.toFixed(6) +
            '<div class="sub2">refined reference zero &gamma; &asymp; ' + esc(nearest.gs.slice(0, 22)) +
            ' nearby · offset ' + fmtSig(tc - nearest.g, 3) + ' (finite-sum error)</div>', 2.5);
        } else {
          showEvent('computed crossing (finite approximation) at t &asymp; ' + tc.toFixed(6) +
            '<div class="sub2">sign change of the main sum M(t) — not a certified zero</div>', 2.2);
        }
      }
    }
  }
  ST.lastM = Mnow();
}

/* ---------------- HUD ----------------------------------------------------- */
var sliderEl = document.getElementById('tslider');
var draggingSlider = false;
function updateHUD() {
  document.getElementById('tReadout').textContent = fmtT(ST.t);
  document.getElementById('nReadout').textContent = TERMS.N;
  document.getElementById('mReadout').textContent = fmtSig(Mnow(), 5);
  var nNext = TERMS.N + 1, tNext = ZH.cutoffT(nNext);
  document.getElementById('nextTermReadout').textContent = nNext;
  document.getElementById('nextTReadout').textContent = fmtT(tNext);
  document.getElementById('countdownReadout').textContent = fmtSig(tNext - ST.t, 4);
  var hw = halfWindow(ST.t);
  var fk = fixtureOverlap(ST.t - hw, ST.t + hw);
  document.getElementById('fixtureHere').textContent = fk
    ? 'reference fixture ' + fk + ' overlaps this window — open the ribbon [R] for Z_ref / R_ref'
    : 'no reference fixture at this height — main sum only (fixtures at 130 / 10⁴ / 10⁶ / 10⁸)';
  if (!draggingSlider) sliderEl.value = tToSlider(ST.t);
}

/* ---------------- fence ---------------------------------------------------- */
function fillFenceStatic() {
  var rt = document.getElementById('fenceRTable');
  var vt2 = document.getElementById('fenceVTable');
  var keys = Object.keys(FX.windows);
  for (var i = 0; i < keys.length; i++) {
    var w = FX.windows[keys[i]], maxR = 0, rms = 0, maxM = 0, k;
    for (k = 0; k < w.Z.length; k++) {
      var Mfix = w.M[k];
      maxR = Math.max(maxR, Math.abs(w.R[k]));
      rms += w.R[k] * w.R[k];
      maxM = Math.max(maxM, Math.abs(Mfix));
    }
    rms = Math.sqrt(rms / w.Z.length);
    var tr = document.createElement('tr');
    tr.innerHTML = '<td>' + keys[i] + '</td><td>[' + fmtT(w.range[0]) + ', ' + fmtT(w.range[1]) + ']</td>' +
      '<td>' + fmtSig(maxR, 4) + '</td><td>' + fmtSig(rms, 4) + '</td><td>' + fmtSig(maxM, 4) + '</td>';
    rt.appendChild(tr);

    /* in-page self-check: inline M vs embedded fixture M */
    var maxDiff = 0;
    for (k = 0; k < w.M.length; k++) {
      var tg = w.range[0] + k * w.step;
      maxDiff = Math.max(maxDiff, Math.abs(ZH.M(tg) - w.M[k]));
    }
    var tv = document.createElement('tr');
    tv.innerHTML = '<td>' + keys[i] + '</td><td>' + w.M.length + '</td><td>' + fmtSig(maxDiff, 3) + '</td>';
    vt2.appendChild(tv);
  }
  document.getElementById('fenceRNote').textContent =
    'R_ref is defined by subtraction from the high-precision reference, not by the ' +
    'Riemann-Siegel correction series. Near 10^8 (window W4) float64 phase rounding ' +
    '(~1e-7 rad) additionally limits the drawn phases; W4 is shown as the honest edge ' +
    'of this instrument’s range.';
}
function fillFenceLive() {
  document.getElementById('fenceDisclosures').innerHTML =
    'scale_t (scene length per unit height) = ' + fmtSig(zScale(ST.t), 4) +
    ' &nbsp;=&nbsp; ' + SCENE_HALF + ' / half-window(' + fmtSig(halfWindow(ST.t), 3) + ')<br>' +
    'radius scale (scene length per unit amplitude) = ' + RSCALE + '<br>' +
    'v_t (time dilation) = ' + fmtSig(ST.vt, 4) + ' height-units per second, one global value<br>' +
    'master gain = slider ' + fmtSig(ST.gain, 3) + ' &times; ' + AUD.MASTER_SCALE +
    ' (linear); voiced-term gain = a_n &times; slider &times; 0.12<br>' +
    'cutoff-entry chime: a UI event cue at the entering term’s f_audio, clamped up to 55 Hz ' +
    'for audibility — it is not part of the sonification law<br>' +
    'ribbon/helix phases beyond the exact-evaluation window use the local expansion ' +
    'φ₀ + ωu + ½θ″u² + ⅙θ‴u³ (error ≪ 10⁻³ rad at all displayed heights)';
}

/* ---------------- input ---------------------------------------------------- */
var keys = {};
function bindInput() {
  var cv = GLR.canvas;
  var down = false, moved = 0, lx = 0, ly = 0, btn = 0;
  cv.addEventListener('mousedown', function (e) {
    down = true; moved = 0; lx = e.clientX; ly = e.clientY; btn = e.button;
  });
  window.addEventListener('mousemove', function (e) {
    if (!down) return;
    var dx = e.clientX - lx, dy = e.clientY - ly;
    lx = e.clientX; ly = e.clientY; moved += Math.abs(dx) + Math.abs(dy);
    if (btn === 2 || e.ctrlKey) {
      GLR.CAM.dist = Math.max(2.5, Math.min(120, GLR.CAM.dist * (1 + dy * 0.004)));
    } else {
      GLR.CAM.yaw += dx * 0.0045; GLR.CAM.pitch += dy * 0.0035;
      GLR.CAM.vyaw = dx * 0.0009; GLR.CAM.vpitch = dy * 0.0007;
    }
  });
  window.addEventListener('mouseup', function (e) {
    if (down && moved < 5 && btn === 0) {
      var n = GLR.pickTerm(e.clientX, e.clientY);
      if (n > 0) selectTerm(n);
    }
    down = false;
  });
  cv.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  cv.addEventListener('wheel', function (e) {
    e.preventDefault();
    if (e.shiftKey) {
      var lt = Math.log10(ST.t) + e.deltaY * 0.0006;
      ST.t = clampT(Math.pow(10, lt)); ST.tTarget = null;
    } else {
      ST.t = clampT(ST.t + e.deltaY * halfWindow(ST.t) * 0.0022); ST.tTarget = null;
    }
  }, { passive: false });

  window.addEventListener('keydown', function (e) {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT')) return;
    keys[e.key.toLowerCase()] = true;
    var k = e.key.toLowerCase();
    if (k === ' ') {
      e.preventDefault();
      ST.frozen = !ST.frozen;
      if (ST.frozen) showPanel('flowerPanel', true);
    }
    else if (k === 'f') showPanel('flowerPanel');
    else if (k === 'r') showPanel('ribbonPanel');
    else if (k === 'z') { if (showPanel('microPanel')) { if (MICRO.idx < 0) microSelect(0); else drawMicro(); } }
    else if (k === 'u') showPanel('audioPanel');
    else if (k === 'i') { if (showPanel('fencePanel')) fillFenceLive(); }
    else if (k === 'a') ST.cruise = !ST.cruise;
    else if (k === 'escape') {
      ['flowerPanel', 'ribbonPanel', 'microPanel', 'audioPanel', 'fencePanel', 'inspectorPanel']
        .forEach(function (id) { showPanel(id, false); });
    }
  });
  window.addEventListener('keyup', function (e) { keys[e.key.toLowerCase()] = false; });

  sliderEl.addEventListener('input', function () {
    draggingSlider = true;
    ST.t = sliderToT(+sliderEl.value); ST.tTarget = null;
  });
  sliderEl.addEventListener('change', function () { draggingSlider = false; });
  document.querySelectorAll('#presets button').forEach(function (b) {
    b.addEventListener('click', function () { glideTo(+b.dataset.t); });
  });
  document.querySelectorAll('[data-close]').forEach(function (b) {
    b.addEventListener('click', function () { showPanel(b.dataset.close, false); });
  });
  ['lyrM', 'lyrZ', 'lyrR'].forEach(function (id) {
    var el = document.getElementById(id), key = id.slice(3);
    el.addEventListener('click', function () {
      ST.layers[key] = !ST.layers[key];
      el.classList.toggle('off', !ST.layers[key]);
    });
  });
  document.getElementById('flower').addEventListener('click', flowerPick);
  document.getElementById('modeBtn').addEventListener('click', toggleMode);
  document.getElementById('skipBtn').addEventListener('click', endOpening);

  /* audio controls */
  document.getElementById('audioBtn').addEventListener('click', function () {
    if (!ST.audioOn) {
      audioEnsure(function () {
        if (AUD.ctx && AUD.ctx.state === 'suspended') AUD.ctx.resume();
        ST.audioOn = true; ST.playing = true;
        document.getElementById('audioBtn').textContent = 'audio off';
        document.getElementById('audioState').textContent =
          'live — playback advances t at v_t per second (freeze [space] to hold the chord)';
        audioPushTerms(true);
      });
    } else {
      ST.audioOn = false; ST.playing = false;
      document.getElementById('audioBtn').textContent = 'enable audio';
      document.getElementById('audioState').textContent = 'off — audio starts only on your gesture';
      audioUpdateRates();
    }
  });
  var vtS = document.getElementById('vtSlider'), gS = document.getElementById('gainSlider');
  function vtLabel() {
    document.getElementById('vtReadout').textContent = fmtSig(ST.vt, 4) + ' height/s';
    document.getElementById('gainReadout').textContent = fmtSig(ST.gain * AUD.MASTER_SCALE, 3) + ' linear';
  }
  vtS.addEventListener('input', function () { ST.vt = Math.pow(10, 3 * vtS.value / 1000); vtLabel(); });
  gS.addEventListener('input', function () { ST.gain = gS.value / 100; vtLabel(); });
  ST.vt = Math.pow(10, 3 * vtS.value / 1000); ST.gain = gS.value / 100; vtLabel();
  document.getElementById('reverbChk').addEventListener('change', function (e2) {
    ST.artistic.reverb = e2.target.checked; setBadge();
  });
  document.getElementById('quantChk').addEventListener('change', function (e2) {
    ST.artistic.quant = e2.target.checked; setBadge(); audioUpdateRates();
  });
  document.getElementById('voiceBtn').addEventListener('click', function () {
    if (!(ST.sel >= 1)) return;
    if (!AUD.started) audioEnsure(function () { voiceTerm(ST.sel); });
    else voiceTerm(ST.sel);
  });
}

function toggleMode() {
  ST.mode = ST.mode === 'obs' ? 'temple' : 'obs';
  var temple = ST.mode === 'temple';
  document.getElementById('mastTitle').innerHTML = temple
    ? 'Zeta Harp // Resonance Temple' : 'Riemann-Siegel Phase Observatory';
  document.getElementById('mastSub').textContent = temple
    ? 'a temple strung with one formula — each string a term of the main sum, each string birth a cutoff entry'
    : "the main sum of Hardy's Z, drawn as phase trajectories";
  document.getElementById('modeBtn').textContent = temple ? 'observatory mode' : 'installation mode';
}

/* ---------------- opening sequence ----------------------------------------- */
var OP = { on: true, s: 0, cross: null, phase: -1 };
function setupOpening() {
  OP.br = fixtureBestCrossingBracket('W3');
  OP.cross = OP.br ? OP.br.tAt : 1000010;
  ST.t = 1000000.0;
  GLR.CAM.dist = 6.5; GLR.CAM.pitch = 0.10; GLR.CAM.yaw = 0.4;
  document.getElementById('fade').style.opacity = 1;
  ['nav', 'keysHint', 'topbar'].forEach(function (id) {
    var el = document.getElementById(id);
    el.style.opacity = 0; el.style.transition = 'opacity 1.6s'; el.style.pointerEvents = 'none';
  });
}
function openingTick(now, dt) {
  OP.s += dt;              /* frame-accumulated: robust to rAF throttling */
  var s = OP.s;
  function line(id, on) { document.getElementById(id).style.opacity = on ? 1 : 0; }
  if (s > 0.3) document.getElementById('fade').style.opacity = 0;
  line('op1', s > 0.6 && s < 5.2);
  line('op2', s > 5.6 && s < 9.0);
  GLR.CAM.yaw += dt * 0.045;
  if (s < 9.5) {
    /* drift inside the field near t = 10^6 */
  } else if (s < 15.0) {
    /* travel to the reference crossing, decelerating */
    var f = (s - 9.5) / 5.5, ease = 1 - Math.pow(1 - f, 3);
    ST.t = 1000000.0 + (OP.cross - 1000000.0) * ease;
    GLR.CAM.dist = 6.5 + 2.5 * ease;
  } else if (s < 18.6) {
    if (OP.phase < 1) {
      OP.phase = 1;
      ST.t = OP.cross; ST.frozen = true;
      computeTerms(ST.t); computeRibbon(ST.t);
      var M0 = Mnow();
      var err = OP.br ? Math.abs(M0 - OP.br.zAt) : Math.abs(M0);
      document.getElementById('op3').innerHTML = OP.br
        ? ('Z_ref changes sign in [' + OP.br.tLo.toFixed(1) + ', ' + OP.br.tHi.toFixed(1) +
           '] — a computed reference crossing (fixture W3)<br>frozen at the grid point t = ' +
           OP.cross.toFixed(1) + ': the projections nearly cancel &nbsp;·&nbsp; Z_ref = ' +
           fmtSig(OP.br.zAt, 3) + ' (high-precision) &nbsp;·&nbsp; M(t) = ' + fmtSig(M0, 3) +
           ' &nbsp;·&nbsp; |M &minus; Z_ref| = ' + fmtSig(err, 3) + ' (the omitted remainder here)')
        : ('frozen at t = ' + OP.cross.toFixed(1));
      line('op3', true);
    }
  } else if (s < 22.5) {
    if (OP.phase < 2) {
      OP.phase = 2; line('op3', false); ST.frozen = false;
      document.getElementById('opTitle').style.transition = 'opacity 2.4s';
      line('opTitle', true);
    }
    GLR.CAM.dist = Math.min(34, GLR.CAM.dist * (1 + dt * 0.55));
    GLR.CAM.pitch += dt * 0.02;
  } else {
    endOpening();
  }
}
function endOpening() {
  if (!OP.on) return;
  OP.on = false; ST.opening = false;
  document.getElementById('opening').remove();
  document.getElementById('skipBtn').remove();
  document.getElementById('fade').style.opacity = 0;
  ST.frozen = false;
  GLR.CAM.dist = Math.max(GLR.CAM.dist, 20);
  ['nav', 'keysHint', 'topbar'].forEach(function (id) {
    var el = document.getElementById(id);
    el.style.opacity = 1; el.style.pointerEvents = '';
  });
  showPanel('ribbonPanel', true);
}

/* ---------------- main loop ------------------------------------------------ */
var lastFrame = performance.now(), frameCount = 0, audioAcc = 0, lastComputedT = null;
function frame(now) {
  var dt = Math.min(0.05, (now - lastFrame) / 1000);
  lastFrame = now;
  frameCount++;
  var tPrev = lastComputedT !== null ? lastComputedT : ST.t;

  if (OP.on) openingTick(now, dt);
  else {
    if (!ST.frozen) {
      var hw = halfWindow(ST.t), spd = hw * 1.6 * (keys.shift ? 8 : 1);
      if (keys.w || keys.arrowup) { ST.t = clampT(ST.t + spd * dt); ST.tTarget = null; }
      if (keys.s || keys.arrowdown) { ST.t = clampT(ST.t - spd * dt); ST.tTarget = null; }
      if (ST.cruise) { ST.t = clampT(ST.t + hw * 0.22 * dt); GLR.CAM.yaw += dt * 0.03; }
      if (ST.audioOn && ST.playing && !keys.w && !keys.s && !ST.cruise && ST.tTarget === null) {
        ST.t = clampT(ST.t + ST.vt * dt);   /* Truth Audio playback: t(tau) = t0 + v_t tau */
      }
      if (ST.tTarget !== null) {
        var lt = Math.log10(ST.t), ltT = Math.log10(ST.tTarget);
        lt += (ltT - lt) * Math.min(1, dt * 2.0);
        ST.t = Math.pow(10, lt);
        if (Math.abs(ltT - lt) < 1e-7) { ST.t = ST.tTarget; ST.tTarget = null; }
      }
    }
  }

  if (ST.t !== lastComputedT || !RIB.valid) {
    computeTerms(ST.t);
    computeRibbon(ST.t);
    if (!OP.on && lastComputedT !== null) detectEvents(tPrev, ST.t);
    lastComputedT = ST.t;
  }

  GLR.draw(dt);
  var flowerVisible = panelVisible('flowerPanel');
  if (flowerVisible && (ST.frozen || frameCount % 4 === 0)) drawFlower();
  if (panelVisible('ribbonPanel')) drawRibbon();
  if (frameCount % 3 === 0 && !OP.on) updateHUD();
  eventTick(now);

  audioAcc += dt;
  if (audioAcc > 0.05) { audioAcc = 0; if (AUD.started) audioUpdateRates(); }

  requestAnimationFrame(frame);
}

/* ---------------- boot ------------------------------------------------------ */
(function boot() {
  computeTerms(ST.t);
  computeRibbon(ST.t);
  ST.lastM = Mnow();
  microInit();
  fillFenceStatic();
  fillFenceLive();
  bindInput();
  setupOpening();
  /* read-only debug handle (used by the check harness notes; no behavior) */
  window.ZH_DEBUG = { ST: ST, OP: OP, TERMS: TERMS, CAM: GLR.CAM, frame: frame,
    endOpening: endOpening, microSelect: microSelect, glideTo: glideTo,
    selectTerm: selectTerm, showPanel: showPanel, toggleMode: toggleMode,
    fillFenceLive: fillFenceLive, drawMicro: drawMicro };
  requestAnimationFrame(function (n) { lastFrame = n; requestAnimationFrame(frame); });
})();
