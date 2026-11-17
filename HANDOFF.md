# HANDOFF: Open-SERDES Tutorial

State and next steps for whoever picks this up (human or agent). Update it at the end of every task.
This file is excluded from the Jekyll site (`_config.yml` → `exclude`).

## How the site is built (read first)

- The LaTeX book in `book/` is the source of truth. `tools/build_site.py` (needs TeX Live, pandoc ≥ 3,
  poppler) regenerates `chapters/`, `appendices/`, `parts/`, `preface.html`, `references.html`.
  **Never hand-edit those pages**: the next build overwrites them.
- pandoc is not installed on the maintainer's Mac, so the generated pages are usually not rebuilt locally.
- Preview: Jekyll in Docker (`ruby:3.3`), e.g. `docker run --rm -p 4007:4007 -v "$PWD":/site -v serdes-gems:/usr/local/bundle -w /site ruby:3.3 sh -c 'bundle install && bundle exec jekyll serve --host 0.0.0.0 --port 4007'`
  → http://localhost:4007/serdes-tutorial/ . Revert `Gemfile.lock` after a Docker build.
- Work on a branch, merge into `main` with a merge commit (see `git log`); a push to `main` deploys the public site.

## Interactive demos (started 15 Nov 2026)

The user asked for interactive demos in every chapter, "as many as possible", to break down the complex
concepts, in the style of the BRICD Open-BioAFE tutorial (https://www.thebricd.org/biomedical-ic-design/,
local repo `~/BRICD/biomedical-ic-design`, which has 14 of them).

### Framework (same pattern as Open-BioAFE)

- `assets/css/demos.css`: navy panel (`.bd`), sliders, segmented buttons, scopes, readouts, captions.
- `assets/js/demos.js`: `window.BD` plot helpers (canvas frame with lin/log axes, line, hline, vline, dot,
  eng formatting, radix-2 FFT, Gaussian RNG, seeded RNG, `bind` sliders, `seg` buttons, `toggle`, `observe`).
- `assets/js/serdes-link.js`: `window.SL`, the link engine shared by the channel/EQ demos. A JS port of
  `book/tutorial/code/common.py` (`channel()`, `ctle()`, impulse and 1-UI pulse response, cursors, PDA eye,
  PRBS, erfc/Q). **It must reproduce the book**: REF = −17.4 dB at 2.5 GHz, p0 = 0.340 V at 6.82 ns,
  p1/p0 = 53.5 %, p−1 = 0.049, cumulative ISI 0.501 V by k = 10 (+0.093 V tail), 2-tap ZF taps
  [0.652, −0.349]. Check these in the browser console before relying on it.
- `_includes/demos/assets.html` loads the CSS/JS; each demo is `_includes/demos/<name>.html`: one `.bd`
  block plus one IIFE, no external libraries, readouts with `aria-live`, works at 375 px and in dark mode.
  Captions are set from JS, so use HTML `<sub>/<sup>`, not `\( \)` maths (KaTeX renders only at load).
- **Placement survives rebuilds**: `tools/insert_demos.py` holds the registry (`DEMOS`: page slug, demo name,
  anchor) and inserts `{% endraw %}{% include demos/NAME.html %}{% raw %}` between `<!-- demo:NAME -->`
  markers after the anchor's figure (`after: "fig:..."`) or at the end of a section (`end: "sec:..."`).
  It strips old markers first, so it is idempotent. `build_site.py` calls it at the end of `main()`;
  run it by hand after adding a demo: `python3 tools/insert_demos.py`.
- Every demo must reproduce the numbers its chapter quotes at its default settings (the numbers are listed
  below). The LaTeX/PDF stays unchanged; demos are web-only.

### Proposed demos (status: `todo`, `wip`, `done`)

Priority: ★ = build first (the hardest concepts, or reused by later demos).

**Ch 1 · Why serial links?**
1. `skew` · Parallel bus vs serial link (Worked Ex 1.1): bit rate, lane count, skew σ → valid window of a bus
   shrinks to zero while a serial lane keeps its eye. After fig:ch1-parser. **done** (10 mm → 67 ps: 2.1 % at
   312.5 Mb/s, 33.5 % at 5 Gb/s; 16 lanes)
2. `ratechain` · Follow the rates (Ex 1.2): pick serialization ratio and line rate → word clock, PLL, half-rate
   clock, UI, f_N (16 × 312.5 Mb/s → 5 Gb/s, 2.5 GHz, 200 ps). After fig:link-anatomy. **covered by `clockplan`**,
   also placed there
3. `fo4ui` · How many gate delays fit in a UI: bit rate slider; bars for CMOS FO4 (42/55 ps) vs HBT CML (~2 ps,
   loaded ×several); full/half/quarter rate (Fig 1.6, 9.2). After fig:ch1-speed. **covered by `fo4rule`**
4. `epb` · Energy per bit (Key eq 1.x): power and rate sliders, pJ/bit compared with published links. **done**
   after fig:ch1-glance (50 mW at 5 Gb/s = 10.0 pJ/b; iso-pJ/b lines; published-link points not added)

**Ch 2 · Signals and systems**
5. ★ `nrzpsd` · NRZ spectrum: sinc² PSD, cumulative power; drag a cursor frequency → % power below it
   (77 % below f_N, 90 % below f_b, −3.9 dB at f_N). After fig:ch2-psd. **done** (77.4 %, 90.3 %, −3.9 dB)
6. `lfsr` · Step an LFSR: 7-stage register animates bit by bit; choose PRBS7/9/15/31 taps; run-length histogram
   builds up (32, 16, 8 … runs); period 127. Placed after fig:ch2-prbs. **done** (period 127, 64/63, longest run 7)
7. `onepole` · Bandwidth ↔ rise time: f3dB slider; Bode and step response; 10–90 % = 0.35/f3dB (140 ps = 0.7 UI
   at 2.5 GHz). After fig:ch2-onepole. **done** (140 ps = 0.70 UI, −3.0 dB at f_N, 913 mV worst eye)
8. ★ `superpos` · Build the waveform from pulses: edit a bit pattern by clicking; each bit's shifted pulse drawn,
   sum shown with sample dots (334 mV vs 156 mV for the 10 dB line). After fig:ch2-superposition. **done** (14
   clickable bits, 10 dB line or REF; the book's 334/156 mV come from its own pattern, not reproduced exactly)
9. ★ `isieye` · One-pole ISI and the eye: τ slider (0.1–1.5 UI) → pulse, cursors, PRBS7 eye, measured opening vs
   2A(1 − 2e^(−Tb/τ)) (987/729/265 mV at τ = 0.2/0.5/1 UI). After fig:ch2-isi-tau. **done** (`isieye`)
10. `eyefold` · Fold the waveform: animate 2-UI windows dropping onto the eye; persistence slider. After
    fig:ch2-eye-fold. **done** (τ 0.45 UI, PRBS7, 1–126 windows, animate; eye 783 mV)
11. `berq` · BER cliff: EH and σn sliders → Gaussian tails, Q, BER (Q = 7.03 ↔ 1e−12, 16.9 dB, ~3 decades/dB).
    After fig:ch2-ber. **done** (Q 7.03, 16.9 dB, 1.0e−12, 3.28 min between errors at 5 Gb/s)
12. `bathtub2` · Bathtub from edge jitter: RJ slider → BER vs phase, opening at 1e−12 (0.72/0.45 UI at 0.02/0.04 UI).
    After fig:ch2-bathtub. **done** (transition density 0.5: 0.72 / 0.45 UI at 0.02 / 0.04 UI rms)

**Ch 3 · The channel**
13. `tline` · When is a wire a transmission line: rise time and length → t_d vs t_r/6 rule; FR-4 delay
    (Ex 3.1). End of sec3.2.1. **done** (6.67 ps/mm, 1.25 mm at 50 ps, 334 nH/m, 133 pF/m)
14. `skin` · Skin depth and R(f): frequency slider; δ vs thickness; R_DC 7.7 Ω/m → 46 Ω/m at 2.5 GHz. After
    fig:ch3-skin. **done** (7.7 → 45.8 Ω/m, onset 56.9 MHz; perimeter-skin model)
15. ★ `lossbuild` · Build the channel loss: sliders for k_R, tanδ, ε_r, length, pad C → conductor (√f) and
    dielectric (f) loss in dB/in and total |S21| (REF −17.4 dB; 0.44 dB/in). Uses SL. After fig:ch3-loss. **done**
    (REF 0.438 dB/in; presets smooth 5-mil stripline k_R 29 → 0.332, low-loss tanδ 0.0045 → 0.153, as Fig 3.4)
16. ★ `bounce` · Lattice diagram: R_S, Z0, R_L sliders → animated bounce diagram and load voltage (25/50/100 Ω:
    0.889, 0.790, 0.8 V). After fig:ch3-bounce. **done** (0.667 launched, 0.889 first step, 0.800 final)
17. `padrl` · Pad C and return loss: C_p and bondwire L → |S11| vs f, 10 dB line, echo in the pulse response
    (2t_d = 6.7 UI). After fig:ch3-pad. **done as `padbond`** (return loss of wire, pad and both; 0.63 pF → 12.4 dB;
    the pulse-echo part is not modelled)
18. `viastub` · Via stub notch: stub length → quarter-wave null f = c/(4L√ε_eff) (6 mm → 6.2 GHz) over the NRZ
    lobe. After fig:ch3-via. **done** (6.2 GHz at 6 mm, ε_eff 4; 5/10/25 Gb/s presets)
19. `tdr` · TDR explorer: place an L bump and a C dip, rise-time slider (Fig 3.9). After fig:ch3-tdr. todo
20. ★ `s21pulse` · From S21 to the pulse: loss slider over the LOSS_FAMILY (5–30 dB) → |S21|, pulse, cursors,
    p1/p0 (46 % at 15 dB; REF 53.5 %, p0 = 0.340 V). Uses SL. After fig:ref-pulse. **done** (REF −17.4 dB, 6.82 ns,
    0.049/0.340, 53.5 %, PDA −161 mV; 10 dB line 0.020/0.556; length and pad-C sliders)
21. `ifftpit` · IFFT pitfalls: df, f_max, window and missing DC → how the cursors change (Pitfall box). todo

**Ch 4 · Link budgets**
22. ★ `pda` · Peak distortion analysis: cursor bars with cumulative ISI; worst-case pattern built live;
    truncation slider (13 cursors hides 90 mV; −126 mV worst sample). After fig:ch4-pda. **done** (Σ 0.501 V,
    −161 mV, full tail −255 mV, 94 mV hidden; with 2-tap FFE main 209 mV, PDA 150 mV / 125 mV full)
23. ★ `isipdf` · ISI distribution by convolution: add cursors one at a time, watch each spike split; noise σ;
    log y (6 % of 1s below threshold unequalized). After fig:ch4-isipdf. **done** (6.1 % below, −126 mV worst;
    FFE: ends at 60 mV at 1e−12 vs PDA 63 mV; spikes drawn while ≤ 32 patterns and no noise)
24. `stateye` · Statistical eye: noise σ, RJ, DJ sliders → BER contours 1e−3…1e−12, eye height/width at 1e−12
    (119 mV, 0.59 UI). After fig:ch4-stateye. todo
25. `waterfall` · Margin budget waterfall: drag each impairment (residual ISI, noise, offset, jitter, crosstalk)
    → linear vs RSS margin (76 vs 89 mV). After fig:ch4-waterfall. **done as `margin`** (76.4 mV linear at the book
    values; 82.3 mV with Ex 10.3's 1.08 mV; statistical 89 mV quoted, not recomputed)
26. `pam4` · NRZ or PAM4: line length → loss at 2.5 and 1.25 GHz, Δ vs 9.54 dB, crossover 1.37 m (23.8 dB).
    After fig:ch4-pam4. **done** (REF Δ 7.0 dB, NRZ by 2.6 dB, crossover 1.37 m / 23.8 dB)

**Ch 5 · Equalization fundamentals**
27. `zfnoise` · Inverse channel and noise: equalize-to frequency slider → flat product and noise gain
    (12.1 dB to f_N, 22.5 dB to 2f_N). After fig:ch5-inverse. **done** (Eq 5.1 on REF: 12.1 / 22.4 dB)
28. `cable` · Cable model: loss slider → zero-phase pulse, main cursor, PDA half-eye; eye closes ~14 dB.
    After fig:ch5-cable. **done** (Eq 5.3/5.4 Lorentzian: 15 dB → k_d l 691 ps, 0.470, 0.153, 0.043, Σ 0.527)
29. ★ `whoowns` · Who removes which cursor: toggle TX pre-tap, CTLE, DFE taps on the REF pulse; colour-coded
    pre/post/tail ownership; PDA eye after each. After fig:ch5-anatomy. **done** (toggles c−1 −0.08, c1 −0.20,
    CTLE 8 dB, 2-tap DFE; PDA over 63 cursors: −242 → 31 (DFE) → 78 (CTLE+DFE) → 83 mV (+pre-tap))

**Ch 6 · TX FFE**
30. ★ `ffe` · FFE playground: c−1, c0, c1 sliders under Σ|c| = 1 → TX waveform, pulse after REF, cursors, PDA
    eye (2-tap ZF [0.652, −0.349] → 163 mV open; 3-tap [−0.085, 0.596, −0.319]). After fig:ch6-ref. **done**
    (163 / 145 mV PRBS7 eyes, −78 mV without FFE, presets −3.5/−6 dB; ZF taps solved live the Lab 3 way)
31. `deemph` · De-emphasis in volts: dB slider → transition/run levels, PCIe presets (−3.5/−6 dB). After
    fig:ch6-deemph. **done inside `ffefreq`** (−6 dB: 0.751/−0.249, ±500/±251 mV; −3.5 dB: ±334 mV)
32. `ffefreq` · FFE frequency response: peaks at f_N, periodic in f_b; cascade with REF stays −17.4 dB at f_N.
    After fig:ch6-ffefreq. **done** (cascade −17.4 dB at f_N for every setting)
33. `zfsolve` · Zero forcing step by step: pick which cursors to force → matrix, taps, new ISI at k = −2/+3.
    After fig:ch6-zf. **done** on REF (0–2 pre, 1–4 post taps; Lab 3 taps reproduced; matrix not displayed)

**Ch 7 · CTLE**
34. `rlc` · RLC peaking: ζ slider → impedance peak (16.6 dB at ζ = 0.2) and ringing step (2.7×). After fig:ch7-rlc.
    **done** (16.6 dB, 2.74×)
35. ★ `ctlebode` · Degenerated pair designer: g_m, R_S, C_S, R_D, C_L → zero/poles, ideal vs realized boost at f_N
    (14 dB ideal, 10.9 dB realized for the Lab 4 values). After fig:ch7-bode. **done** (Ex 7.1: 14/10.9 dB; Ex 7.2:
    DC 7.8, |H(f_N)| 14.8, realized 7.0 dB, peak 4.3 GHz; fixed: 17.1 ideal, 10.0 realized)
36. ★ `ctleref` · CTLE on REF: peaking slider 0–20 dB → pulse, cursors, PRBS eye; best 14 dB (113 mV),
    over-equalization > 16 dB; shaded 0–12 dB range. Uses SL. After fig:ch7-ref. **done** (14 dB: 113 mV,
    main cursor −7.6 dB vs 0 dB, p1 < 0 above 16 dB; eye-vs-peaking curve)
37. `ctlefix` · Ideal vs realized boost (Ex 7.2): 10 dB promised, 7.0 dB realized; move f_p1 to 2f_N. After fig:ch7-we6.
    **covered by `ctlebode`** (presets Ex 7.2 and Ex 7.2 fixed)

**Ch 8 · DFE and adaptation**
38. ★ `dfe` · DFE step-through: bit by bit, decisions fed back, summer waveform; tap count; error propagation
    toggle (a wrong decision doubles ISI). After fig:ch8-cancel. **done** as `dfe` (REF + 8 dB CTLE: data level
    91.6 mV, taps 27.6/11.8 mV, eye 60 → 129 mV with 2 taps; no step-through or error propagation yet)
39. `tap1` · Tap-1 timing budget: clk-Q, summer settling, setup sliders vs 1 UI and 0.5 UI; unroll toggle
    (140 ps direct). After fig:ch8-timing. **done** (Ex 8.2: 30+10+60+20+20 = 140 ps, 60 ps slack; unrolled 80 ps)
40. ★ `sslms` · Sign-sign LMS live: μ, noise, pre-cursor sliders → taps converge to 91.6/27.6/11.8 mV, wander
    when p−1 is uncancelled. After fig:ch8-sslms. **done** (Worked Ex 8.3 set-up: PRBS13, 4 mV, μ 0.25 mV, start
    d_lev 50 mV; w1 within 2 mV after 277 UI (book ~310), no decision errors; extra pre-cursor slider shows the wander)
41. `partition` · Equalizer partition vs loss: pick strategies → PDA eye vs loss (134 mV at REF). After fig:ch8-partition. todo

**Ch 9 · Transmitter**
42. `fo4rule` · 8-FO4 rule: FO4 and serialization ratio → max bit rate bars. After fig:ch9-fo4. **done**, also
    placed in Ch 1 after fig:ch1-speed in place of `fo4ui` (42 ps: 2.98 GHz clock, UI = 4.8 FO4, half-rate +19 %;
    55 ps: −9 %)
43. `muxtiming` · Half-rate 2:1 mux timing: clock duty cycle and data skew → output eye, DCD. After fig:ch9-mux. todo
44. ★ `term` · Termination choices: series/parallel/double, mismatch slider → launched level and echoes.
    After fig:ch9-term. todo
45. `cmlsst` · CML vs SST current: swing and de-emphasis → supply current and power (4×; 1.38× SST at 6 dB).
    After fig:ch9-current. **done** (Eq 9.3: 20 mA/50 mW vs 6 mW at 1 V_ppd, 16 mA/40 mW vs 4.8 mW at 0.8 V;
    the 1.38× SST de-emphasis penalty is not modelled yet)
46. `ffecurr` · Tap currents: preset → I−1, I0, I1 summing to 20 mA, output levels. After fig:ch9-ffe. **done** (Ex 9.4:
    −6 dB = 24 + 8 cells, 15/5 mA, 1.0/0.5 V_ppd; 32 cells of 0.625 mA, quantized)
47. `tcoil` · Pad C and T-coil: C_p → return loss (0.85 pF limit) and pole (10.1 → 14.3 GHz). After fig:ch9-pad. **done**
    (Eq 9.6 at 0.63 pF: L1 = L2 0.59 nH, M 0.20 nH, C_B 79 fF, 10.1 → 14.3 GHz; T-coil response idealized)

**Ch 10 · Receiver front-end and samplers**
48. ★ `regen` · Latch regeneration: input ΔV, τ, A_int → exponential output on log axis; decision time
    (t1 40 ps, A 3, τ 13 ps). **done inside `latch`** (109 ps at 1 mV, 169 ps at 10 µV)
49. `aperture` · Sampling aperture: StrongARM vs CML weighting functions, centroid shift (23 ps). After fig:ch10-aperture. todo
50. ★ `meta` · Metastability: regeneration time and stage count → P(error) (4.2e−5 at 140 ps; HBT 110 ps → 1e−12).
    After fig:ch10-meta. **done as `latch`** (4.2e−5; 8.7e−14 with two extra stages; HBT CML 4.2e−16)
51. `offsetcal` · Offset calibration: Monte Carlo σ = 4.9 mV, DAC bits/range → trimmed spread, yield of
    4-sampler receivers (24 % untrimmed). After fig:ch10-offset. **done** (spec ±5.1 mV: 70 % / 24 % raw, ~100 %
    trimmed; LSB 2·3σ/32 = 0.92 mV as in Fig 10.9)
52. `calloop` · Calibration loop animation: counter steps the DAC until toggling (LSB 0.91 mV). After fig:ch10-cal. todo
53. `sens` · Sampler sensitivity budget (Ex 10.3): noise, offset, hysteresis → minimum input. End of sec:ch10-noise.
    **done inside `margin`** (also placed there: V_sens = 14.1 + 5 + 0.9 = 20 mV)

**Ch 11 · Jitter**
54. `tie` · TIE, period and cycle-to-cycle jitter from edges (Ex 11.1): drag six edges. After fig:ch11-tie. **done**
    (Ex 11.1: 2.00 pp / 0.69 / 1.42 / 3.00 ps; plus locked and free-running random clocks; edges not draggable)
55. `slope` · Noise to jitter: σ_v and slew → σ_t (0.4 → 0.1 V_ppd = 4×). After fig:ch11-slope. **done**
    (3.14 mV/ps at 0.4 V_ppd; 300 noisy edges measured against σ_v/SR)
56. ★ `dualdirac` · RJ ⊗ DJ convolution and the dual-Dirac fit: DCD, ISI, RJ sliders → PDF on log axis, TJ(BER)
    (DJδδ 15.6 ps vs DJpp). After fig:ch11-hist. **done** (DCD/sinusoidal/uniform DJ ⊗ RJ, exact tail sums;
    fit b = 0.5Q((t−μ)/σ) over 1e−4…1e−12: DCD returns DJpp and σ exactly, sinusoidal 17.5 of 20 ps; does not
    reproduce the book's 15.6 ps case, whose DCD+ISI mix is not specified)
57. ★ `bathtub` · Bathtub builder: DJδδ, σ_RJ → eye width at 1e−12 (0.71/0.59/0.45 UI at 1.32/3/5 ps). After
    fig:ch11-bathtub. **done** (TJ 58.6 ps; 0.71/0.59/0.45 UI at σ 1.32/3/5 ps, DJδδ 40 ps)
58. ★ `pnjitter` · Phase noise to jitter: drag the PN profile and integration limits → rms jitter (1.01 ps from
    10 kHz, 0.61 ps above …). After fig:ch11-pn. **done by reusing `pllnoise`** (it has the integration-limit slider)
59. `jbudget` · Jitter budget: each DJ/RJ term → TJ 58.6 ps, 0.71 UI eye. After fig:ch11-budget. **done** (Table 11.1
    rows: DJ 8+6+6+20 = 40, RJ RSS 1.32, TJ 58.6 ps = 0.293 UI, eye 141 ps)

**Ch 12 · PLL**
60. `pfd` · PFD/CP waveforms: phase offset → UP/DN pulses, dead zone with T_rst. After fig:ch12-pfd. **done**
    (Ex 12.1 values: 1 ns → 200 fC, 3.8 mV on C1, 10 µA average)
61. ★ `pllloop` · Loop designer: I_CP, R, C1, C2, K_VCO, N → open-loop Bode, PM (60° at 1 MHz), closed-loop
    peaking, step response (ζ 0.5 → 30 % overshoot). After fig:ch12-loop. **done** (Ex 12.1 exactly: 1.00 MHz,
    60.0°, 1.56 MHz, 1.7 dB, f_n 537 kHz, ζ 1.00; Ex 12.2 preset 3.00 MHz, 4.69 MHz; time-domain step response)
62. ★ `pllnoise` · Optimum bandwidth: f_u slider → ref/CP (low-pass) and VCO (high-pass) contributions,
    integrated jitter (1.01 ps minimum near 3 MHz). After fig:ch12-noise. **done** (60° loops of Eq 12.2,
    VCO −100.8 dBc/Hz·(1 MHz/f)², floor −110: 1.73/1.27/1.03/1.00/1.13 ps at 0.5/1/2/3/6 MHz vs book
    1.91/1.34/1.06/1.01/1.14; 3 MHz split 0.69/0.72 ps (book 0.71/0.72); the 0.5 MHz gap suggests the book's
    VCO model has more close-in noise; integration-limit slider included, so `pnjitter` can reuse this)
63. `leeson` · Leeson's model: Q, amplitude, F → L(1 MHz) (−122 dBc/Hz vs quoted −100.8). After fig:ch12-leeson. **done**
    (R_p 1.06 kΩ, P_sig = V²/2R_p, −122.3 dBc/Hz, 21.5 dB excess)
64. `ppf` · Polyphase filter: RC spread and frequency → I/Q amplitude and phase error, 1 vs 2 stages. After fig:ch12-poly. todo
65. `lock` · PLL acquisition animation: phase/frequency step, V_ctrl settling. todo

**Ch 13 · CDR**
66. `alex` · Alexander PD: drag the clock phase across a transition → early/late votes. After fig:ch13-alex. **done**
    (S1/S2/S3 truth, no-transition abstain, jitter → 1000-edge vote counts)
67. ★ `bbgain` · Bang-bang gain linearized by jitter: σ_j slider → smoothed sign, slope √(2/π)/σ_j. After fig:ch13-bbchar.
    **done** (edge histogram split early/late, erf characteristic, tangent, linear range)
68. ★ `jtol` · Jitter tolerance vs mask: K_P, K_I, latency → JTOL curve over the mask (dips at 1–2 MHz). After fig:ch13-jtol.
    **done** (Eq 13.4 estimate TM + 2S/ω, S = 2.44e6 UI/s at K_P 1/8, mask, first-order linear CDR, and the book's
    simulated points 3.0/1.08/0.51/0.32 UI as gold dots; a real JTOL sweep by simulation is still todo)
69. ★ `pi` · Phase interpolator: linear vs sin/cos weights, bits → phasor, INL (±4.1° vs ±0.55°). After fig:ch13-pi.
    **done** (18.43° at α = 1/4, ±4.07° = 4.52 ps linear, ±0.55° with 6-bit sin/cos; phasor drawing not yet eyeballed)
70. ★ `cdrsim` · Live PI-CDR: ppm offset, K_P, K_P/K_I, step count → PI code wrap, phase error, lock time
    (+200 ppm locks in 0.2 s). After fig:ch13-sim. **done** (Section 13.6 model: 8-vote majority, P+I, D = 1, RJ
    1.32 ps, ±10 ps DDJ, start 74 ps off: lock 0.15 µs (book 0.19), 2.5 ps rms (book 2.5–2.6), integral 202 ppm;
    integer K_P 10.1 ps rms (book 10.7); no-integral preset slips above the 488 ppm slew limit). Note: in the
    extracted book text the µ of µs is lost in places ("0.2 s" means 0.2 µs).

**Ch 14 · Architecture**
71. `clockplan` · Clock plan explorer: line rate → every clock in Fig 14.2 (2.5 GHz, 1.25 GHz, 625 MHz, 312.5 MHz). After fig:ch14-clock.
    **done** (N = 50 at 5 Gb/s, 100 at 10 Gb/s; flags the CDR loop clock reaching 1.25 GHz and fractional N)
72. `budget10g` · Design for 10, guarantee 5: rate and length → PDA eye and timing budget (Fig 14.4). After fig:ch14-rate. todo
73. `bondwire` · Bond-wire length (Ex 14.2): L per mm and C_pad → resonance and return loss. End of sec14.5.3.
    **done as `padbond`** (1/2.5/3 mm → 16.2/8.7/7.4 dB; 1 mm at 5 GHz 10.5 dB; 2.5 nH + 1 pF artificial line)
74. `power` · Power budget: currents per block → total power and pJ/bit (Fig 14.8). After fig:ch14-power. **done**
    (Ex 14.3: 216 mW, 43.2 pJ/b; SST 172 mW, 34.4 pJ/b; Purdue 219 pJ/b; per-block table rows not itemized)

**Ch 15 · Flow**
75. `mcruns` · How many Monte Carlo runs (key eq): yield target and confidence → N. End of sec:testbenches. **done**
    (Δσ/σ ≈ 1/√(2N): 200 runs 4.9 ± 0.25 mV, 50 runs 10 %; 200 repeated sets confirm it)
76. `bercount` · Bits needed to claim a BER: target BER, confidence, errors seen → N bits and test time
    (3/N rule at 95 %). End of sec:labtest. **done** (Poisson bound: 3.00e12 bits, 10 min at 1e−12/95 %; k errors)
77. `lumped` · Sections for a lumped line model: rise time and t_d → N sections. todo

**Ch 16 · Labs** (**done** as `labmap`, a try-it box at the end of Lab 0 linking all 11 demos; links checked): the labs run serdespy in Python, so instead of new demos each lab links back to the demo that
previews it (Lab 1 → `s21pulse`, Lab 2 → `isieye`, Lab 3 → `ffe`, Lab 4 → `ctleref`, Lab 5 → `dfe`,
Lab 6 → `bathtub`, Lab 7 → `cdrsim`). 78. `linkall` capstone: full link (REF length, FFE, CTLE, DFE taps,
noise, jitter) → stat eye and margin, the whole book on one panel. todo

**Appendix A (formula sheet)**: 79. `calc` · a small calculator for UI/f_N, Q↔BER, dB↔ratio, skin depth. todo

### Progress log

- 15 Nov 2026: proposals above; framework (`demos.css`, `demos.js`, `assets.html`, `tools/insert_demos.py`,
  build hook) and the first demo (`isieye`, Ch 2, after Fig 2.8). Verified in the browser: presets give
  987/729/265 mV (formula 987/729/264), renders in dark mode at desktop width; not yet checked at 375 px or
  in light mode. Weekly usage was at 97 %, so work stopped there.
- Preview: `preview_start serdes` (entry in `~/SkillSurf/.claude/launch.json`, Docker container
  `serdes-jekyll`, gems volume `serdes-gems`, port 4007) → http://localhost:4007/serdes-tutorial/
- 15 Nov (later): `nrzpsd`, `berq` (Ch 2) and `bounce` (Ch 3) done and checked in the browser; the user
  asked to merge into main, so the branch was merged and pushed (site deployed).
- 15 Nov (later): `bathtub` (Ch 11) done; fixed a start-up console error in `bounce` (a slider event fired
  before `pres` was set). Merged and pushed. Weekly usage reached 99 %.
- 15 Nov (later): `pi` (Ch 13) done, merged and pushed. 6 demos live: isieye, nrzpsd, berq, bounce, bathtub, pi.
- 15 Nov (later): `onepole` (Ch 2) and `slope` (Ch 11) done, merged and pushed: 8 demos live.
- 15 Nov (later): `lfsr` (Ch 2) and `viastub` (Ch 3) done, merged and pushed: 10 demos live.
- 17 Nov: `assets/js/serdes-link.js` (SL) written and verified against the book: REF −17.38 dB, peak 6.82 ns,
  cursors 0.0486/0.3396/0.1817/0.0909 … 0.0085, Σ13 = 0.501, tail 0.094 (book 0.093), full PDA −0.255;
  10 dB line 0.020/0.556/0.160/0.063; PRBS7 eyes −77.7 mV (Lab 2), 162.8 mV 2-tap (Lab 3), 113.3 mV at 14 dB
  CTLE (Lab 4); ZF taps the Lab 3 way (`zfTaps`, only the cursors h−npre…h+npost, like sdp.forcing_ffe).
  `eyeScan`/`eyeTraces` treat one PRBS period as periodic (circular convolution), 4 ms per scan.
  Demos on SL: `s21pulse` (Ch 3), `pda` (Ch 4), `ffe` (Ch 6), `ctleref` (Ch 7), `dfe` (Ch 8). 15 demos live.
- 17 Nov (later): `isipdf` (Ch 4), `sslms` (Ch 8), `dualdirac` (Ch 11), `bbgain` (Ch 13): 19 demos live.
  Fixed `ffe` logging a start-up error (slider set before its helper was defined). Lesson: in every demo, define
  helpers before any `dispatchEvent` at start-up, and keep bit-history offsets ≥ the longest cursor span.
- 17 Nov (later): `latch` (Ch 10), `pllloop` and `pllnoise` (Ch 12): 22 demos live.
- 17 Nov (later): `jtol` and `cdrsim` (Ch 13): 24 demos live.
- 17 Nov (later): `superpos` (Ch 2), `lossbuild` (Ch 3), `whoowns` (Ch 5), and `pllnoise` reused in Ch 11:
  27 demo placements (26 distinct demos) live.
- 17 Nov (later): `skew` (Ch 1), `cmlsst` (Ch 9), `clockplan` (Ch 14), `bercount` (Ch 15): every chapter 1–15 now
  has at least one demo; 31 placements (30 distinct demos). Checked all 15 demo pages at 375 px: no horizontal
  overflow; PDA panel readable at phone width. Light mode not checked separately (the panels have fixed navy colours).
- Lab 5 check: SL's ideal-DFE eye gives 60 → 108/129/~142/~152 mV for 1–4 taps vs the book's 60 → 110.7/129.7/
  143.2/153.6 (serdespy's DFE samples at a fixed phase; SL searches the phase in 2-sample steps).
- Visual check while the browser pane is hidden: screenshots fail, so a page snippet POSTs the canvases to a
  local receiver (`python3 -I shotsrv.py <dir>` on 127.0.0.1:4099, kept in the session scratchpad) and the PNG
  is read back. Recreate it if needed: it base64-decodes `name|dataURL` bodies.
- Open question: Ch 2 text says the 10 dB line's PDA eye is 230 mV; with 13 cursors SL gives 204 mV. Check
  which cursor count the book used before quoting either.

### Next steps

State on 17 Nov (third window): 64 placements; was 32 (31 includes incl. `labmap`), every chapter 1–16 covered, all merged
into `main` (deployed). Each `done` entry above lists the book numbers it reproduces.

0. Values for the rest are already extracted in this pass: Ex 8.2 tap-1 budget (clk-Q 25–35, tap 10, 3τ = 60 with
   250 Ω·80 fF, setup 20, margin 20 → 135–145 ps; unrolled fits 100 ps), Ex 9.4 tap currents (I_T 20 mA, 32 cells of
   0.625 mA; −6 dB → 15/5 mA), Ex 11.3 budget (DJ 8+6+6+20 = 40 ps, RJ √(1.0²+0.7²+0.5²) = 1.32 ps, TJ 58.6 ps),
   Ex 14.3 power (CML 77 mA × 2.5 V = 192 mW + 25 mW = 216 mW, 43.2 pJ/b; SST −44 mW; 0.8 V_ppd −10 mW; Purdue
   219 pJ/b), Ex 3.1 (t_r 50 ps → t_r·v/6 = 1.25 mm, 6.67 ps/mm, 334 nH/m, 133 pF/m). `tap1`, `ffecurr` and `power` are done;
   `jbudget` and `tline` too.
1. Remaining ★ demos: `stateye` (Ch 4, needs a jitter-aware statistical eye in SL), `ctlebode` (Ch 7 degenerated
   pair g_m/R_S/C_S/R_D/C_L → 14 dB ideal, 10.9 dB realized), `term` (Ch 9), `dfe` step-through with error
   propagation (Ch 8).
2. Then the plain `todo` entries, cheapest first: `fo4ui`/`ratechain`/`epb` (Ch 1), `eyefold`/`bathtub2` (Ch 2),
   `tline`/`skin`/`padrl`/`tdr` (Ch 3), `waterfall`/`pam4` (Ch 4), `zfnoise`/`cable` (Ch 5), `deemph`/`ffefreq`/
   `zfsolve` (Ch 6), `rlc`/`ctlefix` (Ch 7), `tap1`/`partition` (Ch 8), `fo4rule`/`muxtiming`/`ffecurr`/`tcoil`
   (Ch 9), `aperture`/`offsetcal`/`calloop`/`sens` (Ch 10), `tie`/`jbudget` (Ch 11), `pfd`/`leeson`/`ppf`/`lock`
   (Ch 12), `alex` (Ch 13), `budget10g`/`bondwire`/`power` (Ch 14), `mcruns`/`lumped` (Ch 15), `linkall` capstone,
   `calc` (App A).
3. Open questions: Ch 2's 230 mV PDA for the 10 dB line (SL gives 204 mV with 13 cursors); `pllnoise` is 10 % low at
   f_u = 0.5 MHz (book's VCO model may have more close-in noise); `dualdirac` does not reproduce Fig 11.4's 15.6 ps
   case; `cmlsst` lacks the 1.38× SST de-emphasis penalty; a JTOL sweep by simulation would replace the estimate.
4. Workflow per batch: write includes → add to `DEMOS` in `tools/insert_demos.py` → `python3 tools/insert_demos.py`
   → check numbers in the browser console and a canvas snapshot → mark `done` here → commit on `interactive-demos`,
   merge `--no-ff` into `main`, push (the user approved merging demo batches). Watch for two bugs met twice: a
   `dispatchEvent` at start-up before a helper `var` is defined, and bit-history offsets shorter than the cursor span.
