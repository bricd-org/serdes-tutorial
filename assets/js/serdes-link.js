/* serdes-link.js: the Open-SERDES link model in the browser (window.SL), for the interactive demos.
   A port of book/tutorial/code/common.py (the serdespy labs), with the same conventions:
   - 5 Gb/s NRZ, UI = 200 ps, SPS = 64 samples per UI, DT = 3.125 ps;
   - channel() = 50-ohm source | pad C | lossy FR-4 RLGC line | pad C | 50-ohm load, S21 = 2/A (DC ~ 1);
   - ctle(peak) = (1/A)(1 + s/wz)/((1 + s/wp1)(1 + s/wp2)), wz = wp1/A, 0 dB at high frequency;
   - impulse h per DT with sum(h) = H(0); pulse = h convolved with SPS ones (1 V, 1 UI);
   - cursors p_k = p(idx0 + k SPS) from the peak; PDA eye = 2A(p0 - sum|p_k|).
   The FFT grid is N = 16384 points (df = 19.53 MHz, 51.2 ns window) instead of the labs' 10 MHz grid;
   the REF numbers agree with the book to the digits it quotes. Needs demos.js (BD.fft). MIT licence. */
(function () {
  if (window.SL) return;
  var SPS = 64, UI = 200e-12, DT = UI / SPS, N = 16384, NF = N / 2 + 1, DF = 1 / (N * DT), A_TX = 0.5;
  var F = new Float64Array(NF); for (var i = 0; i < NF; i++) F[i] = i * DF;
  var cache = {};

  /* S21 of the synthetic channel (same parameters and defaults as common.py) */
  function channel(o) {
    o = o || {};
    var L = o.length != null ? o.length : 1.0, kr = o.kr != null ? o.kr : 60, rdc = o.rdc != null ? o.rdc : 7,
        tand = o.tand != null ? o.tand : 0.02, er = o.er != null ? o.er : 4, z0 = o.z0 != null ? o.z0 : 50,
        cp = o.cpad != null ? o.cpad : 300e-15;
    var key = [L, kr, rdc, tand, er, z0, cp].join(',');
    if (cache[key]) return cache[key];
    var v = 2.998e8 / Math.sqrt(er), w0 = 2 * Math.PI * 1e9, Lp = z0 / v, G = 1e-12, x = 2 * tand / Math.PI;
    var re = new Float64Array(NF), im = new Float64Array(NF);
    for (var k = 0; k < NF; k++) {
      var w = 2 * Math.PI * F[k], wn = Math.max(k, 1) * 2 * Math.PI * DF / w0;      // C[0] = C[1]
      // R = sqrt(rdc^2 + (kr(1+j)sqrt(w/w0))^2) = sqrt(rdc^2 + j 2 kr^2 w/w0)
      var ra = rdc * rdc, rb = 2 * kr * kr * w / w0, rr = Math.hypot(ra, rb);
      var Rr = Math.sqrt((rr + ra) / 2), Ri = Math.sqrt(Math.max(0, (rr - ra) / 2));
      // C = (1/(z0 v)) (j w/w0)^(-x)
      var cm = Math.pow(wn, -x) / (z0 * v), Cr = cm * Math.cos(-x * Math.PI / 2), Ci = cm * Math.sin(-x * Math.PI / 2);
      // Z = R + jwL, Y = G + jwC
      var Zr = Rr, Zi = Ri + w * Lp, Yr = G - w * Ci, Yi = w * Cr;
      // gamma = sqrt(Z Y), Zc = sqrt(Z / Y)
      var pr = Zr * Yr - Zi * Yi, pi = Zr * Yi + Zi * Yr, pm = Math.hypot(pr, pi);
      var gr = Math.sqrt((pm + pr) / 2), gi = (pi >= 0 ? 1 : -1) * Math.sqrt(Math.max(0, (pm - pr) / 2));
      var yd = Yr * Yr + Yi * Yi, qr = (Zr * Yr + Zi * Yi) / yd, qi = (Zi * Yr - Zr * Yi) / yd, qm = Math.hypot(qr, qi);
      var zr = Math.sqrt((qm + qr) / 2), zi = (qi >= 0 ? 1 : -1) * Math.sqrt(Math.max(0, (qm - qr) / 2));
      var a = gr * L, b = gi * L, ch = Math.cosh(a), sh = Math.sinh(a), cb = Math.cos(b), sb = Math.sin(b);
      var coR = ch * cb, coI = sh * sb, siR = sh * cb, siI = ch * sb;            // cosh, sinh of gamma L
      var Bl_r = zr * siR - zi * siI, Bl_i = zr * siI + zi * siR;                  // B = Zc sinh
      var zd = zr * zr + zi * zi, Cl_r = (siR * zr + siI * zi) / zd, Cl_i = (siI * zr - siR * zi) / zd;  // C = sinh / Zc
      // M1 = src * pad = [[1 + z0 sC, z0], [sC, 1]] with sC = j w cp
      var sc = w * cp, M1A_r = 1, M1A_i = z0 * sc, M1B = z0;
      // M2 = M1 * line
      var M2A_r = M1A_r * coR - M1A_i * coI + M1B * Cl_r, M2A_i = M1A_r * coI + M1A_i * coR + M1B * Cl_i;
      var M2B_r = M1A_r * Bl_r - M1A_i * Bl_i + M1B * coR, M2B_i = M1A_r * Bl_i + M1A_i * Bl_r + M1B * coI;
      // A_total = M2A + M2B (sC + 1/z0)
      var At_r = M2A_r + M2B_r / z0 - M2B_i * sc, At_i = M2A_i + M2B_i / z0 + M2B_r * sc;
      var ad = At_r * At_r + At_i * At_i; re[k] = 2 * At_r / ad; im[k] = -2 * At_i / ad;
    }
    var H = { re: re, im: im };
    cache[key] = H; return H;
  }
  /* CML CTLE of common.py: 0 dB at high frequency, DC gain = -peak dB */
  function ctle(peak, fp1, fp2) {
    fp1 = fp1 || 2.5e9; fp2 = fp2 || 10e9;
    var a = Math.pow(10, peak / 20), re = new Float64Array(NF), im = new Float64Array(NF);
    for (var k = 0; k < NF; k++) {
      var fz = fp1 / a, f = F[k];
      // (1/a)(1 + j f/fz) / ((1 + j f/fp1)(1 + j f/fp2))
      var nr = 1 / a, ni = f / fz / a, d1r = 1, d1i = f / fp1, d2r = 1, d2i = f / fp2;
      var dr = d1r * d2r - d1i * d2i, di = d1r * d2i + d1i * d2r, dd = dr * dr + di * di;
      re[k] = (nr * dr + ni * di) / dd; im[k] = (ni * dr - nr * di) / dd;
    }
    return { re: re, im: im };
  }
  function mul(A, B) {
    var re = new Float64Array(NF), im = new Float64Array(NF);
    for (var k = 0; k < NF; k++) { re[k] = A.re[k] * B.re[k] - A.im[k] * B.im[k]; im[k] = A.re[k] * B.im[k] + A.im[k] * B.re[k]; }
    return { re: re, im: im };
  }
  function magDb(H, f) { var k = Math.round(f / DF); return 10 * Math.log10(H.re[k] * H.re[k] + H.im[k] * H.im[k]); }
  /* impulse response per DT (sum = H(0)), as serdespy.freq2impulse: real(ifft(hermitian H)) */
  function impulse(H) {
    var re = new Float64Array(N), im = new Float64Array(N);
    for (var k = 0; k < NF; k++) { re[k] = H.re[k]; im[k] = -H.im[k]; }            // conj for an inverse FFT via the forward one
    im[N / 2] = 0;
    for (k = 1; k < N / 2; k++) { re[N - k] = H.re[k]; im[N - k] = H.im[k]; }
    BD.fft(re, im);
    for (k = 0; k < N; k++) re[k] /= N;
    return re;
  }
  /* 1 V, 1 UI pulse response = running sum of SPS impulse samples */
  function pulse(h) {
    var p = new Float64Array(h.length), s = 0;
    for (var n = 0; n < h.length; n++) { s += h[n]; if (n >= SPS) s -= h[n - SPS]; p[n] = s; }
    return p;
  }
  function pulseOf(H) { return pulse(impulse(H)); }
  function argmax(p) { var m = 0; for (var i = 1; i < p.length; i++) if (p[i] > p[m]) m = i; return m; }
  /* cursors around the peak (or idx0): returns {k, v, idx0} */
  function cursors(p, npre, npost, idx0) {
    if (idx0 == null) idx0 = argmax(p);
    var k = [], v = [];
    for (var j = -npre; j <= npost; j++) { var n = idx0 + j * SPS; k.push(j); v.push(n >= 0 && n < p.length ? p[n] : 0); }
    return { k: k, v: v, idx0: idx0 };
  }
  /* PDA inner eye 2A(p0 - sum_{k != 0} |p_k|) */
  function pda(c, A) {
    A = A == null ? A_TX : A; var i0 = c.k.indexOf(0), s = 0;
    for (var i = 0; i < c.v.length; i++) if (i !== i0) s += Math.abs(c.v[i]);
    return 2 * A * (c.v[i0] - s);
  }
  /* TX FFE applied to a pulse: taps [c_-npre ... c_0 ... ], tap j delays by (j - npre) UI */
  function ffe(p, taps, npre) {
    var out = new Float64Array(p.length);
    for (var j = 0; j < taps.length; j++) { var sh = (j - npre) * SPS, c = taps[j];
      for (var n = 0; n < p.length; n++) { var m = n - sh; if (m >= 0 && m < p.length) out[n] += c * p[m]; } }
    return out;
  }
  /* PRBS bits (0/1) from an LFSR, same taps as the book's Figure 2.3 */
  function prbs(n, count) {
    var t = { 7: [7, 6], 9: [9, 5], 13: [13, 12, 2, 1], 15: [15, 14], 31: [31, 28] }[n], s = [], out = [];
    for (var i = 0; i < n; i++) s.push(1);
    for (i = 0; i < count; i++) { var fb = 0; t.forEach(function (tp) { fb ^= s[tp - 1]; }); out.push(s[n - 1]); s.pop(); s.unshift(fb); }
    return out;
  }
  /* receiver samples for a bit list from a pulse's cursors (superposition); returns the sample of each bit */
  function samples(bits, c, A) {
    A = A == null ? A_TX : A; var out = [], i0 = c.k.indexOf(0);
    for (var n = 0; n < bits.length; n++) { var y = 0;
      for (var i = 0; i < c.k.length; i++) { var m = n - c.k[i]; if (m >= 0 && m < bits.length) y += A * (2 * bits[m] - 1) * c.v[i]; }
      out.push(y); }
    return out;
  }
  /* one period of a PRBS (0/1) repeated forever through pulse p: the samples at phase offset ph (samples
     from the peak) are a circular convolution, so fold the cursors modulo the period first */
  function periodicSamples(p, bits, ph, idx0, A) {
    var P = bits.length, w = new Float64Array(P), y = new Float64Array(P);
    for (var n = idx0 + ph, k = 0; n < p.length; n += SPS, k++) w[k % P] += p[n];
    for (n = idx0 + ph - SPS, k = -1; n >= 0; n -= SPS, k--) w[((k % P) + P) % P] += p[n];
    for (var m = 0; m < P; m++) { var s = 0; for (var r = 0; r < P; r++) { var b = bits[(m - r + P) % P]; s += b ? w[r] : -w[r]; } y[m] = A * s; }
    return y;
  }
  /* noise-free inner eye of a periodic pattern at every phase of the UI (like eye_scan in common.py) */
  function eyeScan(p, bits, A) {
    A = A == null ? A_TX : A; var idx0 = argmax(p), hs = [], best = -1e9, bph = 0;
    for (var ph = -SPS / 2; ph < SPS / 2; ph++) {
      var y = periodicSamples(p, bits, ph, idx0, A), lo = 1e9, hi = -1e9;
      for (var m = 0; m < bits.length; m++) { if (bits[m]) lo = Math.min(lo, y[m]); else hi = Math.max(hi, y[m]); }
      hs.push(lo - hi); if (lo - hi > best) { best = lo - hi; bph = ph; }
    }
    return { heights: hs, best: best, phase: bph, idx0: idx0 };
  }
  /* eye-diagram traces: one 2-UI trace per bit, centred on phase offset c (from the peak); step = samples per point */
  function eyeTraces(p, bits, c, A, step) {
    A = A == null ? A_TX : A; step = step || 2; var idx0 = argmax(p), cols = [];
    for (var ph = c - SPS; ph <= c + SPS; ph += step) cols.push(periodicSamples(p, bits, ph, idx0, A));
    var tr = []; for (var m = 0; m < bits.length; m++) { var t = new Float64Array(cols.length); for (var j = 0; j < cols.length; j++) t[j] = cols[j][m]; tr.push(t); }
    return tr;
  }
  /* zero-forcing taps the way Lab 3 gets them (sdp.forcing_ffe on the cursors around p0 only), scaled to sum|c| = 1 */
  function zfTaps(c, npre, npost) {
    var P = function (k) { var i = c.k.indexOf(k); return i < 0 ? 0 : c.v[i]; }, n = npre + npost + 1, M = [], b = [];
    var cur = []; for (var k = -npre; k <= npost; k++) cur.push(P(k));       // only the n cursors h_-npre..h_npost
    var Q = function (k) { var i = k + npre; return i >= 0 && i < n ? cur[i] : 0; };
    for (var r = 0; r < n; r++) { M.push([]); for (var j = 0; j < n; j++) M[r].push(Q(r - j)); b.push(r === npre ? 1 : 0); }
    for (var i = 0; i < n; i++) { var piv = i; for (j = i + 1; j < n; j++) if (Math.abs(M[j][i]) > Math.abs(M[piv][i])) piv = j;
      var t = M[i]; M[i] = M[piv]; M[piv] = t; t = b[i]; b[i] = b[piv]; b[piv] = t;
      for (j = 0; j < n; j++) if (j !== i) { var f = M[j][i] / M[i][i]; for (var kk = i; kk < n; kk++) M[j][kk] -= f * M[i][kk]; b[j] -= f * b[i]; } }
    var x = b.map(function (v, ii) { return v / M[ii][ii]; }), s = x.reduce(function (a, v) { return a + Math.abs(v); }, 0);
    return x.map(function (v) { return v / s; });
  }
  /* drawing helpers on a BD frame f */
  function drawEye(f, tr, col) {                  // traces span -1..+1 UI on the x axis
    var g = f.d.g; f.clipIn(); g.strokeStyle = col || 'rgba(127,184,240,.16)'; g.lineWidth = 1;
    tr.forEach(function (t) { var n = t.length; g.beginPath();
      for (var j = 0; j < n; j++) { var x = f.X(-1 + 2 * j / (n - 1)), y = f.Y(t[j]); if (j) g.lineTo(x, y); else g.moveTo(x, y); } g.stroke(); });
    f.clipOut();
  }
  function drawCursors(f, c, scale) {             // stems at k UI: pre red, main gold, post teal
    var g = f.d.g; scale = scale || 1; f.clipIn();
    c.k.forEach(function (k, i) { var v = c.v[i] * scale, col = k < 0 ? '#f08a6a' : k === 0 ? '#e0b85a' : '#7fd0b8';
      g.strokeStyle = col; g.lineWidth = k === 0 ? 2 : 1.4; g.beginPath(); g.moveTo(f.X(k), f.Y(0)); g.lineTo(f.X(k), f.Y(v)); g.stroke();
      g.fillStyle = col; g.beginPath(); g.arc(f.X(k), f.Y(v), k === 0 ? 4 : 3, 0, 7); g.fill(); });
    f.clipOut();
  }
  function erfc(x) { var z = Math.abs(x), t = 1 / (1 + 0.5 * z);
    var r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
    return x >= 0 ? r : 2 - r; }
  /* LOSS_FAMILY of link.py: loss at Nyquist (dB) -> line length (m) */
  var LOSS_FAMILY = { 5: 0.285, 10: 0.572, 15: 0.862, 20: 1.152, 25: 1.441, 30: 1.731 };
  function lengthForLoss(db) {                   // interpolate the family (linear in length), REF = 1 m
    var ks = [0, 5, 10, 15, 20, 25, 30], ls = [0, 0.285, 0.572, 0.862, 1.152, 1.441, 1.731];
    for (var i = 1; i < ks.length; i++) if (db <= ks[i]) return ls[i - 1] + (ls[i] - ls[i - 1]) * (db - ks[i - 1]) / (ks[i] - ks[i - 1]);
    return ls[ls.length - 1];
  }
  window.SL = { SPS: SPS, UI: UI, DT: DT, N: N, NF: NF, DF: DF, F: F, A_TX: A_TX, F_NYQ: 2.5e9, REF_LEN: 1.0,
                channel: channel, ctle: ctle, mul: mul, magDb: magDb, impulse: impulse, pulse: pulse, pulseOf: pulseOf,
                argmax: argmax, cursors: cursors, pda: pda, ffe: ffe, prbs: prbs, samples: samples, erfc: erfc,
                periodicSamples: periodicSamples, eyeScan: eyeScan, eyeTraces: eyeTraces, zfTaps: zfTaps,
                drawEye: drawEye, drawCursors: drawCursors,
                LOSS_FAMILY: LOSS_FAMILY, lengthForLoss: lengthForLoss };
})();
