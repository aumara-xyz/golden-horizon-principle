/* ==========================================================================
   Truth Audio — MATH_SPEC section 9.
   f_audio_n = v_t * (theta'(t) - ln n) / 2pi, one global v_t, one global gain.
   Direct main-sum render: up to AUD.DIRECT_MAX sample-exact term phasors in an
   AudioWorklet; terms beyond that are band-summed (disclosed). Voiced terms
   ride separate oscillators. Artistic controls (reverb / quantize) leave
   Truth Mode and flip the badge.
   ========================================================================== */

var AUD = {
  ctx: null, master: null, node: null, wet: null, conv: null,
  started: false, usingWorklet: false,
  DIRECT_MAX: 512, BANDS: 8, VOICE_MAX: 8, MASTER_SCALE: 0.045,
  voiced: {},           /* n -> {osc, g} */
  spFallback: null, spState: null,
  lastTermSig: ''
};

/* Each term is a complex phasor advanced by a per-sample rotation
   e^{i dphi_n} (dphi_n = omega_n * v_t / sampleRate) — the sample-exact
   integral of the Truth Audio law, renormalized once per block. */
var WORKLET_CODE =
  "class ZHSum extends AudioWorkletProcessor {\n" +
  "  constructor(){ super();\n" +
  "    this.n=0; this.a=[]; this.cr=[]; this.ci=[]; this.dc=[]; this.ds=[];\n" +
  "    this.gain=0; this.target=0;\n" +
  "    this.port.onmessage = (e)=>{ const m=e.data;\n" +
  "      if(m.type==='terms'){\n" +
  "        this.n=m.a.length; this.a=m.a;\n" +
  "        this.dc=m.dph.map(Math.cos); this.ds=m.dph.map(Math.sin);\n" +
  "        this.cr=m.ph.map(Math.cos); this.ci=m.ph.map(Math.sin);\n" +
  "        this.target=m.gain;\n" +
  "      } else if(m.type==='u'){\n" +
  "        this.dc=m.dph.map(Math.cos); this.ds=m.dph.map(Math.sin);\n" +
  "        this.target=m.gain;\n" +
  "      }\n" +
  "    };\n" +
  "  }\n" +
  "  process(inputs, outputs){\n" +
  "    const out=outputs[0][0]; const n=this.n;\n" +
  "    const a=this.a, cr=this.cr, ci=this.ci, dc=this.dc, ds=this.ds;\n" +
  "    for(let i=0;i<out.length;i++){\n" +
  "      let s=0;\n" +
  "      for(let k=0;k<n;k++){\n" +
  "        const r=cr[k]*dc[k]-ci[k]*ds[k];\n" +
  "        ci[k]=cr[k]*ds[k]+ci[k]*dc[k]; cr[k]=r;\n" +
  "        s+=a[k]*r;\n" +
  "      }\n" +
  "      this.gain+=(this.target-this.gain)*0.0008;\n" +
  "      out[i]=s*this.gain;\n" +
  "    }\n" +
  "    for(let k=0;k<n;k++){\n" +
  "      const m2=cr[k]*cr[k]+ci[k]*ci[k];\n" +
  "      if(m2>0){ const inv=1/Math.sqrt(m2); cr[k]*=inv; ci[k]*=inv; }\n" +
  "    }\n" +
  "    if(outputs[0].length>1) outputs[0][1].set(out);\n" +
  "    return true;\n" +
  "  }\n" +
  "}\n" +
  "registerProcessor('zh-sum', ZHSum);\n";

function audioEnsure(cb) {
  if (AUD.started) { cb && cb(); return; }
  var Ctx = window.AudioContext || window.webkitAudioContext;
  if (!Ctx) return;
  AUD.ctx = new Ctx();
  AUD.master = AUD.ctx.createGain();
  AUD.master.gain.value = 1;
  AUD.master.connect(AUD.ctx.destination);
  /* reverb path (silent until artistic mode) */
  AUD.conv = AUD.ctx.createConvolver();
  AUD.conv.buffer = makeIR(AUD.ctx, 2.0);
  AUD.wet = AUD.ctx.createGain(); AUD.wet.gain.value = 0;
  AUD.master.connect(AUD.conv); AUD.conv.connect(AUD.wet); AUD.wet.connect(AUD.ctx.destination);
  AUD.started = true;
  if (AUD.ctx.audioWorklet && typeof Blob !== 'undefined') {
    var url = URL.createObjectURL(new Blob([WORKLET_CODE], { type: 'application/javascript' }));
    AUD.ctx.audioWorklet.addModule(url).then(function () {
      AUD.node = new AudioWorkletNode(AUD.ctx, 'zh-sum', { outputChannelCount: [2] });
      AUD.node.connect(AUD.master);
      AUD.usingWorklet = true;
      audioPushTerms(true);
      cb && cb();
    }).catch(function () { audioFallback(); cb && cb(); });
  } else { audioFallback(); cb && cb(); }
}

function audioFallback() {
  /* ScriptProcessor fallback: same law, main-thread rendered */
  var sp = AUD.ctx.createScriptProcessor(2048, 0, 2);
  AUD.spState = { a: [], ph: [], dph: [], gain: 0, target: 0 };
  var st = AUD.spState;
  sp.onaudioprocess = function (e) {
    var L = e.outputBuffer.getChannelData(0), R = e.outputBuffer.getChannelData(1);
    var n = st.a.length;
    for (var i = 0; i < L.length; i++) {
      var s = 0;
      for (var k = 0; k < n; k++) { st.ph[k] += st.dph[k]; s += st.a[k] * Math.cos(st.ph[k]); }
      st.gain += (st.target - st.gain) * 0.0008;
      L[i] = s * st.gain; R[i] = L[i];
    }
    for (var k2 = 0; k2 < n; k2++) st.ph[k2] %= 6.283185307179586;
  };
  sp.connect(AUD.master);
  AUD.spFallback = sp;
  audioPushTerms(true);
}

function makeIR(ctx, seconds) {
  var sr = ctx.sampleRate, len = Math.floor(sr * seconds);
  var buf = ctx.createBuffer(2, len, sr);
  for (var ch = 0; ch < 2; ch++) {
    var d = buf.getChannelData(ch);
    for (var i = 0; i < len; i++)
      d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.4) * 0.5;
  }
  return buf;
}

/* Build the direct-render term set at the current t: min(N, DIRECT_MAX)
   sample-exact terms + band-summed remainder. Returns counts for honesty. */
function audioTermSet() {
  var t = ST.t, N = TERMS.N, sr = AUD.ctx ? AUD.ctx.sampleRate : 48000;
  var D = Math.min(N, AUD.DIRECT_MAX);
  var a = [], dph = [], ph = [];
  var scale = ST.playingGain();
  for (var n = 1; n <= D; n++) {
    a.push(TERMS.a[n - 1]);
    dph.push(TERMS.omega[n - 1] * ST.vt / sr);
    ph.push(TERMS.phi0[n - 1]);
  }
  var B = 0;
  if (N > D) {
    var lo = D + 1;
    for (var b = 0; b < AUD.BANDS; b++) {
      var hi = Math.min(N, Math.floor(D * Math.pow(N / D, (b + 1) / AUD.BANDS)));
      if (hi < lo) continue;
      var e = 0, wsum = 0, osum = 0;
      for (var m = lo; m <= hi; m++) {
        var am = 2 / Math.sqrt(m);
        e += am * am;
        wsum += am;
        osum += am * TERMS.omega[m - 1];
      }
      if (wsum <= 0) { lo = hi + 1; continue; }
      a.push(Math.sqrt(e));                     /* energy-preserving band amplitude */
      dph.push((osum / wsum) * ST.vt / sr);     /* amplitude-weighted mean rate */
      ph.push(Math.random() * Math.PI * 2);
      B++;
      lo = hi + 1;
    }
  }
  return { a: a, dph: dph, ph: ph, D: D, B: B, N: N };
}

ST.playingGain = function () {
  return (ST.audioOn && (ST.playing || ST.frozen)) ? ST.gain * AUD.MASTER_SCALE : 0;
};

function audioPushTerms(withPhases) {
  if (!AUD.started) return;
  var set = audioTermSet();
  var msg = { type: 'terms', a: set.a, dph: set.dph, ph: set.ph, gain: ST.playingGain() };
  if (AUD.usingWorklet && AUD.node) AUD.node.port.postMessage(msg);
  else if (AUD.spState) {
    AUD.spState.a = set.a; AUD.spState.dph = set.dph; AUD.spState.target = msg.gain;
    if (withPhases) AUD.spState.ph = set.ph.slice();
  }
  setHonesty(set);
  return set;
}

function audioUpdateRates() {
  if (!AUD.started) return;
  var set = audioTermSet();
  var sig = set.N + '/' + set.D + '/' + set.B;
  if (sig !== AUD.lastTermSig) { AUD.lastTermSig = sig; audioPushTerms(true); }
  else {
    var msg = { type: 'u', dph: set.dph, gain: ST.playingGain() };
    if (AUD.usingWorklet && AUD.node) AUD.node.port.postMessage(msg);
    else if (AUD.spState) { AUD.spState.dph = set.dph; AUD.spState.target = msg.gain; }
    setHonesty(set);
  }
  /* voiced oscillators follow the law live */
  for (var n in AUD.voiced) {
    var v = AUD.voiced[n], f = ZH.fAudio(+n, ST.t, ST.vt);
    if (ST.artistic.quant) f = quantize(f);
    if (f > 8 && f < 12000) {
      v.osc.frequency.setTargetAtTime(f, AUD.ctx.currentTime, 0.05);
      v.g.gain.setTargetAtTime(ZH.an(+n) * ST.gain * 0.12, AUD.ctx.currentTime, 0.05);
    } else {
      v.g.gain.setTargetAtTime(0, AUD.ctx.currentTime, 0.05); /* out of audible band at this v_t */
    }
  }
}

function quantize(f) {
  /* ARTISTIC ONLY: snap to A-minor pentatonic; never active in Truth Mode */
  if (f <= 20) return f;
  var degrees = [0, 3, 5, 7, 10];
  var semis = 12 * Math.log(f / 55) / Math.LN2;
  var oct = Math.floor(semis / 12), pos = semis - 12 * oct, best = degrees[0], bd = 99;
  for (var i = 0; i < degrees.length; i++) {
    var d = Math.abs(degrees[i] - pos);
    if (d < bd) { bd = d; best = degrees[i]; }
  }
  return 55 * Math.pow(2, (12 * oct + best) / 12);
}

function voiceTerm(n) {
  var i = ST.voiced.indexOf(n);
  if (i >= 0) {
    ST.voiced.splice(i, 1);
    if (AUD.voiced[n]) {
      AUD.voiced[n].g.gain.setTargetAtTime(0, AUD.ctx.currentTime, 0.08);
      var vn = AUD.voiced[n]; delete AUD.voiced[n];
      setTimeout(function () { try { vn.osc.stop(); } catch (e2) {} }, 600);
    }
  } else {
    if (ST.voiced.length >= AUD.VOICE_MAX) return;
    ST.voiced.push(n);
    if (AUD.started) {
      var osc = AUD.ctx.createOscillator(), g = AUD.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = Math.max(8, ZH.fAudio(n, ST.t, ST.vt));
      g.gain.value = 0;
      osc.connect(g); g.connect(AUD.master);
      osc.start();
      AUD.voiced[n] = { osc: osc, g: g };
    }
  }
  updateInspector();
  audioUpdateRates();
}

function chime(n) {
  if (!AUD.started || !ST.audioOn) return;
  var f = ZH.fAudio(n, ST.t, ST.vt);
  f = Math.max(55, Math.abs(f));          /* event cue: clamped for audibility (UI sound, not the sonification) */
  var osc = AUD.ctx.createOscillator(), g = AUD.ctx.createGain();
  osc.type = 'sine'; osc.frequency.value = f;
  var t0 = AUD.ctx.currentTime;
  g.gain.setValueAtTime(0, t0);
  g.gain.linearRampToValueAtTime(ST.gain * 0.18, t0 + 0.02);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.6);
  osc.connect(g); g.connect(AUD.master);
  osc.start(t0); osc.stop(t0 + 1.7);
}

function setHonesty(set) {
  var el = document.getElementById('honesty');
  if (!el) return;
  el.textContent = set.N + ' terms in the sum · ' + set.D + ' rendered sample-exact · ' +
    ST.voiced.length + ' individually voiced · ' +
    (set.B > 0 ? (set.N - set.D) + ' band-summed into ' + set.B + ' bands' : 'none band-summed');
}

function setBadge() {
  var b = document.getElementById('truthBadge');
  var art = ST.artistic.reverb || ST.artistic.quant;
  if (art) {
    b.className = 'badge artistic';
    b.textContent = 'ARTISTIC SONIFICATION — NOT A PRIVILEGED MATHEMATICAL MAPPING';
  } else {
    b.className = 'badge truth';
    b.textContent = 'TRUTH MODE — no per-string tuning, no remapping';
  }
  if (AUD.started && AUD.wet)
    AUD.wet.gain.setTargetAtTime(ST.artistic.reverb ? 0.4 : 0, AUD.ctx.currentTime, 0.2);
}
