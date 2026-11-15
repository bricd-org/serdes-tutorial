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
   shrinks to zero while a serial lane keeps its eye. After fig:ch1-parser. todo
2. `ratechain` · Follow the rates (Ex 1.2): pick serialization ratio and line rate → word clock, PLL, half-rate
   clock, UI, f_N (16 × 312.5 Mb/s → 5 Gb/s, 2.5 GHz, 200 ps). After fig:link-anatomy. todo
3. `fo4ui` · How many gate delays fit in a UI: bit rate slider; bars for CMOS FO4 (42/55 ps) vs HBT CML (~2 ps,
   loaded ×several); full/half/quarter rate (Fig 1.6, 9.2). After fig:ch1-speed. todo
4. `epb` · Energy per bit (Key eq 1.x): power and rate sliders, pJ/bit compared with published links. todo

**Ch 2 · Signals and systems**
5. ★ `nrzpsd` · NRZ spectrum: sinc² PSD, cumulative power; drag a cursor frequency → % power below it
   (77 % below f_N, 90 % below f_b, −3.9 dB at f_N). After fig:ch2-psd. todo
6. `lfsr` · Step an LFSR: 7-stage register animates bit by bit; choose PRBS7/9/15/31 taps; run-length histogram
   builds up (32, 16, 8 … runs); period 127. After fig:ch2-lfsr. todo
7. `onepole` · Bandwidth ↔ rise time: f3dB slider; Bode and step response; 10–90 % = 0.35/f3dB (140 ps = 0.7 UI
   at 2.5 GHz). After fig:ch2-onepole. todo
8. ★ `superpos` · Build the waveform from pulses: edit a bit pattern by clicking; each bit's shifted pulse drawn,
   sum shown with sample dots (334 mV vs 156 mV for the 10 dB line). After fig:ch2-superposition. todo
9. ★ `isieye` · One-pole ISI and the eye: τ slider (0.1–1.5 UI) → pulse, cursors, PRBS7 eye, measured opening vs
   2A(1 − 2e^(−Tb/τ)) (987/729/265 mV at τ = 0.2/0.5/1 UI). After fig:ch2-isi-tau. **done** (`isieye`)
10. `eyefold` · Fold the waveform: animate 2-UI windows dropping onto the eye; persistence slider. After
    fig:ch2-eye-fold. todo
11. `berq` · BER cliff: EH and σn sliders → Gaussian tails, Q, BER (Q = 7.03 ↔ 1e−12, 16.9 dB, ~3 decades/dB).
    After fig:ch2-ber. todo
12. `bathtub2` · Bathtub from edge jitter: RJ slider → BER vs phase, opening at 1e−12 (0.72/0.45 UI at 0.02/0.04 UI).
    After fig:ch2-bathtub. todo

**Ch 3 · The channel**
13. `tline` · When is a wire a transmission line: rise time and length → t_d vs t_r/6 rule; FR-4 delay
    (Ex 3.1). End of sec3.2.1. todo
14. `skin` · Skin depth and R(f): frequency slider; δ vs thickness; R_DC 7.7 Ω/m → 46 Ω/m at 2.5 GHz. After
    fig:ch3-skin. todo
15. ★ `lossbuild` · Build the channel loss: sliders for k_R, tanδ, ε_r, length, pad C → conductor (√f) and
    dielectric (f) loss in dB/in and total |S21| (REF −17.4 dB; 0.44 dB/in). Uses SL. After fig:ch3-loss. todo
16. ★ `bounce` · Lattice diagram: R_S, Z0, R_L sliders → animated bounce diagram and load voltage (25/50/100 Ω:
    0.889, 0.790, 0.8 V). After fig:ch3-bounce. todo
17. `padrl` · Pad C and return loss: C_p and bondwire L → |S11| vs f, 10 dB line, echo in the pulse response
    (2t_d = 6.7 UI). After fig:ch3-pad. todo
18. `viastub` · Via stub notch: stub length → quarter-wave null f = c/(4L√ε_eff) (6 mm → 6.2 GHz) over the NRZ
    lobe; pulse distortion. After fig:ch3-via. todo
19. `tdr` · TDR explorer: place an L bump and a C dip, rise-time slider (Fig 3.9). After fig:ch3-tdr. todo
20. ★ `s21pulse` · From S21 to the pulse: loss slider over the LOSS_FAMILY (5–30 dB) → |S21|, pulse, cursors,
    p1/p0 (46 % at 15 dB; REF 53.5 %, p0 = 0.340 V). Uses SL. After fig:ref-pulse. todo
21. `ifftpit` · IFFT pitfalls: df, f_max, window and missing DC → how the cursors change (Pitfall box). todo

**Ch 4 · Link budgets**
22. ★ `pda` · Peak distortion analysis: cursor bars with cumulative ISI; worst-case pattern built live;
    truncation slider (13 cursors hides 90 mV; −126 mV worst sample). After fig:ch4-pda. todo
23. ★ `isipdf` · ISI distribution by convolution: add cursors one at a time, watch each spike split; noise σ;
    log y (6 % of 1s below threshold unequalized). After fig:ch4-isipdf. todo
24. `stateye` · Statistical eye: noise σ, RJ, DJ sliders → BER contours 1e−3…1e−12, eye height/width at 1e−12
    (119 mV, 0.59 UI). After fig:ch4-stateye. todo
25. `waterfall` · Margin budget waterfall: drag each impairment (residual ISI, noise, offset, jitter, crosstalk)
    → linear vs RSS margin (76 vs 89 mV). After fig:ch4-waterfall. todo
26. `pam4` · NRZ or PAM4: line length → loss at 2.5 and 1.25 GHz, Δ vs 9.54 dB, crossover 1.37 m (23.8 dB).
    After fig:ch4-pam4. todo

**Ch 5 · Equalization fundamentals**
27. `zfnoise` · Inverse channel and noise: equalize-to frequency slider → flat product and noise gain
    (12.1 dB to f_N, 22.5 dB to 2f_N). After fig:ch5-inverse. todo
28. `cable` · Cable model: loss slider → zero-phase pulse, main cursor, PDA half-eye; eye closes ~14 dB.
    After fig:ch5-cable. todo
29. ★ `whoowns` · Who removes which cursor: toggle TX pre-tap, CTLE, DFE taps on the REF pulse; colour-coded
    pre/post/tail ownership; PDA eye after each. After fig:ch5-anatomy. todo

**Ch 6 · TX FFE**
30. ★ `ffe` · FFE playground: c−1, c0, c1 sliders under Σ|c| = 1 → TX waveform, pulse after REF, cursors, PDA
    eye (2-tap ZF [0.652, −0.349] → 163 mV open; 3-tap [−0.085, 0.596, −0.319]). After fig:ch6-ref. todo
31. `deemph` · De-emphasis in volts: dB slider → transition/run levels, PCIe presets (−3.5/−6 dB). After
    fig:ch6-deemph. todo
32. `ffefreq` · FFE frequency response: peaks at f_N, periodic in f_b; cascade with REF stays −17.4 dB at f_N.
    After fig:ch6-ffefreq. todo
33. `zfsolve` · Zero forcing step by step: pick which cursors to force → matrix, taps, new ISI at k = −2/+3.
    After fig:ch6-zf. todo

**Ch 7 · CTLE**
34. `rlc` · RLC peaking: ζ slider → impedance peak (16.6 dB at ζ = 0.2) and ringing step (2.7×). After fig:ch7-rlc. todo
35. ★ `ctlebode` · Degenerated pair designer: g_m, R_S, C_S, R_D, C_L → zero/poles, ideal vs realized boost at f_N
    (14 dB ideal, 10.9 dB realized for the Lab 4 values). After fig:ch7-bode. todo
36. ★ `ctleref` · CTLE on REF: peaking slider 0–20 dB → pulse, cursors, PRBS eye; best 14 dB (113 mV),
    over-equalization > 16 dB; shaded 0–12 dB range. Uses SL. After fig:ch7-ref. todo
37. `ctlefix` · Ideal vs realized boost (Ex 7.2): 10 dB promised, 7.0 dB realized; move f_p1 to 2f_N. After fig:ch7-we6. todo

**Ch 8 · DFE and adaptation**
38. ★ `dfe` · DFE step-through: bit by bit, decisions fed back, summer waveform; tap count; error propagation
    toggle (a wrong decision doubles ISI). After fig:ch8-cancel. todo
39. `tap1` · Tap-1 timing budget: clk-Q, summer settling, setup sliders vs 1 UI and 0.5 UI; unroll toggle
    (140 ps direct). After fig:ch8-timing. todo
40. ★ `sslms` · Sign-sign LMS live: μ, noise, pre-cursor sliders → taps converge to 91.6/27.6/11.8 mV, wander
    when p−1 is uncancelled. After fig:ch8-sslms. todo
41. `partition` · Equalizer partition vs loss: pick strategies → PDA eye vs loss (134 mV at REF). After fig:ch8-partition. todo

**Ch 9 · Transmitter**
42. `fo4rule` · 8-FO4 rule: FO4 and serialization ratio → max bit rate bars. After fig:ch9-fo4. todo
43. `muxtiming` · Half-rate 2:1 mux timing: clock duty cycle and data skew → output eye, DCD. After fig:ch9-mux. todo
44. ★ `term` · Termination choices: series/parallel/double, mismatch slider → launched level and echoes.
    After fig:ch9-term. todo
45. `cmlsst` · CML vs SST current: swing and de-emphasis → supply current and power (4×; 1.38× SST at 6 dB).
    After fig:ch9-current. todo
46. `ffecurr` · Tap currents: preset → I−1, I0, I1 summing to 20 mA, output levels. After fig:ch9-ffe. todo
47. `tcoil` · Pad C and T-coil: C_p → return loss (0.85 pF limit) and pole (10.1 → 14.3 GHz). After fig:ch9-pad. todo

**Ch 10 · Receiver front-end and samplers**
48. ★ `regen` · Latch regeneration: input ΔV, τ, A_int → exponential output on log axis; decision time
    (t1 40 ps, A 3, τ 13 ps). After fig:ch10-sa. todo
49. `aperture` · Sampling aperture: StrongARM vs CML weighting functions, centroid shift (23 ps). After fig:ch10-aperture. todo
50. ★ `meta` · Metastability: regeneration time and stage count → P(error) (4.2e−5 at 140 ps; HBT 110 ps → 1e−12).
    After fig:ch10-meta. todo
51. `offsetcal` · Offset calibration: Monte Carlo σ = 4.9 mV, DAC bits/range → trimmed spread, yield of
    4-sampler receivers (24 % untrimmed). After fig:ch10-offset. todo
52. `calloop` · Calibration loop animation: counter steps the DAC until toggling (LSB 0.91 mV). After fig:ch10-cal. todo
53. `sens` · Sampler sensitivity budget (Ex 10.3): noise, offset, hysteresis → minimum input. End of sec:ch10-noise. todo

**Ch 11 · Jitter**
54. `tie` · TIE, period and cycle-to-cycle jitter from edges (Ex 11.1): drag six edges. After fig:ch11-tie. todo
55. `slope` · Noise to jitter: σ_v and slew → σ_t (0.4 → 0.1 V_ppd = 4×). After fig:ch11-slope. todo
56. ★ `dualdirac` · RJ ⊗ DJ convolution and the dual-Dirac fit: DCD, ISI, RJ sliders → PDF on log axis, TJ(BER)
    (DJδδ 15.6 ps vs DJpp). After fig:ch11-hist. todo
57. ★ `bathtub` · Bathtub builder: DJδδ, σ_RJ → eye width at 1e−12 (0.71/0.59/0.45 UI at 1.32/3/5 ps). After
    fig:ch11-bathtub. todo
58. ★ `pnjitter` · Phase noise to jitter: drag the PN profile and integration limits → rms jitter (1.01 ps from
    10 kHz, 0.61 ps above …). After fig:ch11-pn. todo
59. `jbudget` · Jitter budget: each DJ/RJ term → TJ 58.6 ps, 0.71 UI eye. After fig:ch11-budget. todo

**Ch 12 · PLL**
60. `pfd` · PFD/CP waveforms: phase offset → UP/DN pulses, dead zone with T_rst. After fig:ch12-pfd. todo
61. ★ `pllloop` · Loop designer: I_CP, R, C1, C2, K_VCO, N → open-loop Bode, PM (60° at 1 MHz), closed-loop
    peaking, step response (ζ 0.5 → 30 % overshoot). After fig:ch12-loop. todo
62. ★ `pllnoise` · Optimum bandwidth: f_u slider → ref/CP (low-pass) and VCO (high-pass) contributions,
    integrated jitter (1.01 ps minimum near 3 MHz). After fig:ch12-noise. todo
63. `leeson` · Leeson's model: Q, amplitude, F → L(1 MHz) (−122 dBc/Hz vs quoted −100.8). After fig:ch12-leeson. todo
64. `ppf` · Polyphase filter: RC spread and frequency → I/Q amplitude and phase error, 1 vs 2 stages. After fig:ch12-poly. todo
65. `lock` · PLL acquisition animation: phase/frequency step, V_ctrl settling. todo

**Ch 13 · CDR**
66. `alex` · Alexander PD: drag the clock phase across a transition → early/late votes. After fig:ch13-alex. todo
67. ★ `bbgain` · Bang-bang gain linearized by jitter: σ_j slider → smoothed sign, slope √(2/π)/σ_j. After fig:ch13-bbchar. todo
68. ★ `jtol` · Jitter tolerance vs mask: K_P, K_I, latency → JTOL curve over the mask (dips at 1–2 MHz). After fig:ch13-jtol. todo
69. ★ `pi` · Phase interpolator: linear vs sin/cos weights, bits → phasor, INL (±4.1° vs ±0.55°). After fig:ch13-pi. todo
70. ★ `cdrsim` · Live PI-CDR: ppm offset, K_P, K_P/K_I, step count → PI code wrap, phase error, lock time
    (+200 ppm locks in 0.2 s). After fig:ch13-sim. todo

**Ch 14 · Architecture**
71. `clockplan` · Clock plan explorer: line rate → every clock in Fig 14.2 (2.5 GHz, 1.25 GHz, 625 MHz, 312.5 MHz). After fig:ch14-clock. todo
72. `budget10g` · Design for 10, guarantee 5: rate and length → PDA eye and timing budget (Fig 14.4). After fig:ch14-rate. todo
73. `bondwire` · Bond-wire length (Ex 14.2): L per mm and C_pad → resonance and return loss. End of sec14.5.3. todo
74. `power` · Power budget: currents per block → total power and pJ/bit (Fig 14.8). After fig:ch14-power. todo

**Ch 15 · Flow**
75. `mcruns` · How many Monte Carlo runs (key eq): yield target and confidence → N. End of sec:testbenches. todo
76. `bercount` · Bits needed to claim a BER: target BER, confidence, errors seen → N bits and test time
    (3/N rule at 95 %). End of sec:labtest. todo
77. `lumped` · Sections for a lumped line model: rise time and t_d → N sections. todo

**Ch 16 · Labs**: the labs run serdespy in Python, so instead of new demos each lab links back to the demo that
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

### Next steps

1. Check `isieye` at 375 px and in light mode.
2. Write `assets/js/serdes-link.js` (SL) and verify it against the REF numbers above.
3. Build the ★ demos in chapter order, then the rest. Mark each `done` here with the numbers it reproduces.
