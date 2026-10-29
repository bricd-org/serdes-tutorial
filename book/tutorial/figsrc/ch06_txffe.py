"""ch06_txffe.py -- figures for Chapter 6 (Transmit FFE).

ch06_deemph  : TX and RX waveforms with and without 6 dB de-emphasis (2-tap FFE)
ch06_ffefreq : 2-tap FFE magnitude for several de-emphasis settings, and its product with REF
ch06_zf      : 3-tap zero-forcing example (Worked Example 6.2): cursors before and after
ch06_ref     : REF pulse and eye: no FFE, 2-tap and 3-tap zero-forcing FFE (Lab 3 numbers)
"""
from bricdstyle import *
from link import *

H = channel(REF_LEN)
h, t = impulse(H)
p = pulse(h)
i0 = int(np.argmax(p))
delay = i0 - SPS // 2                       # pulse peak sits mid-bit after this delay

def taps2(de_db):
    g = 10 ** (-de_db / 20)
    c1 = (1 - g) / 2
    return np.array([1 - c1, -c1])

# ------------------------------------------------------------------ ch06_deemph
pat = np.array([0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0])
bits = np.tile(pat, 30)
c6 = taps2(6.0)
x0 = tx_wave(bits)
x6 = tx_wave(bits, fir=c6)
y0 = through(x0, h)
y6 = through(x6, h)
n0 = 20 * pat.size                          # show one period in steady state
nb = pat.size
tt = np.arange(nb * SPS) / SPS
fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
a1.plot(tt, x0[n0 * SPS:(n0 + nb) * SPS], color=MUTED, lw=0.9, ls="--", label="no FFE")
a1.plot(tt, x6[n0 * SPS:(n0 + nb) * SPS], color=C1, lw=1.3, label="6 dB de-emphasis")
for b in range(nb):
    a1.text(b + 0.5, 0.64, str(pat[b]), ha="center", fontsize=6.5, color=MUTED)
note(a1, (6.5, 0.5), "transition bit: full swing $\\pm A$", (0.3, 0.90), color=C1, fs=7, ha="left")
note(a1, (18.5, 0.25), "repeated bits: $\\pm A/2$", (13.2, 0.90), color=C1, fs=7, ha="left")
a1.set_xlim(0, nb); a1.set_ylim(-0.62, 1.02)
a1.set_xticks(range(0, nb + 1, 4))
finish(a1, "Time (UI)", "TX output (V)")
panel(a1, "a")
s0 = slice(n0 * SPS + delay, (n0 + nb) * SPS + delay)
a2.plot(tt, y0[s0], color=MUTED, lw=1.0, ls="--", label="no FFE")
a2.plot(tt, y6[s0], color=C1, lw=1.3, label="6 dB de-emphasis")
a2.plot(np.arange(nb) + 0.5, y6[n0 * SPS + delay + SPS // 2::SPS][:nb], "o", color=C1, ms=2.5)
a2.axhline(0, color=MUTED, lw=0.6)
note(a2, (4.5, y0[n0 * SPS + delay + 4 * SPS + SPS // 2]), "without FFE a long run\ncharges far past the\ntransition levels", (0.3, 0.42),
     color=MUTED, fs=7)
a2.set_xlim(0, nb); a2.set_ylim(-0.55, 0.55)
a2.set_xticks(range(0, nb + 1, 4))
a2.legend(loc="lower right", fontsize=7, ncol=2)
finish(a2, "Time (UI)", "RX input (V)")
panel(a2, "b")
savefig(fig, "ch06_deemph")

# ------------------------------------------------------------------ ch06_ffefreq
fg = F / 1e9
m = F <= 5.0e9
fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
for de, col in zip((0, 3.5, 6.0, 9.5), (MUTED, C3, C1, C2)):
    c = taps2(de)
    Hf = c[0] + c[1] * np.exp(-2j * np.pi * F * UI)
    lab = "no FFE" if de == 0 else f"{de:g} dB ($c_1$={c[1]:.3f})"
    a1.plot(fg[m], 20 * np.log10(np.abs(Hf[m])), color=col, label=lab)
    a2.plot(fg[m], 20 * np.log10(np.abs(Hf[m] * H[m])), color=col, label="channel only" if de == 0 else f"{de:g} dB")
a1.axvline(2.5, color=MUTED, ls="--", lw=0.8); a2.axvline(2.5, color=MUTED, ls="--", lw=0.8)
a1.text(2.55, -11.4, "$f_\\mathrm{N}$", color=MUTED, fontsize=7.5)
a1.text(4.95, -11.4, "$f_\\mathrm{b}$", color=MUTED, fontsize=7.5, ha="right")
a1.set_xlim(0, 5); a1.set_ylim(-12, 1.5)
a1.legend(loc="lower center", fontsize=6.8, ncol=2)
finish(a1, "Frequency (GHz)", "$|H_\\mathrm{FFE}(f)|$ (dB)")
panel(a1, "a")
a2.set_xlim(0, 5); a2.set_ylim(-32, 1)
a2.legend(loc="lower left", fontsize=7)
finish(a2, "Frequency (GHz)", "Channel $\\times$ FFE (dB)")
panel(a2, "b")
savefig(fig, "ch06_ffefreq")

# ------------------------------------------------------------------ ch06_zf (Worked Example 6.2)
x = {-1: 0.2, 0: 0.85, 1: -0.2, 2: 0.1, 3: 0.05}
X = lambda k: x.get(k, 0.0)
M = np.array([[X(i - j) for j in (-1, 0, 1)] for i in (-1, 0, 1)])
a = np.linalg.solve(M, [0, 1, 0])
an = a / np.abs(a).sum()
kk = np.arange(-2, 5)
before = np.array([X(k) for k in kk])
after = np.array([sum(an[j + 1] * X(k - j) for j in (-1, 0, 1)) for k in kk])
fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2, sharey=True)
stem_cursors(a1, kk, before, fmt="{:.2f}")
a1.set_ylim(-0.3, 1.0)
finish(a1, "Cursor $k$ (UI)", "Cursor value $x_k$")
a1.set_title("Unequalized pulse", loc="left")
panel(a1, "a")
a2.axvspan(-1.5, 1.5, color=GTINT, lw=0, zorder=0)
a2.text(0, 0.92, "forced window", ha="center", fontsize=7, color=GOLDDK)
stem_cursors(a2, kk, after, fmt="{:.3f}")
for k_ in (-2, 2, 3):
    i = list(kk).index(k_)
    a2.plot(k_, after[i], "o", ms=9, mfc="none", mec=C4, mew=0.9)
note(a2, (3.15, 0.07), "ISI pushed\noutside the window", (3.0, 0.42), color=C4, fs=7, ha="center")
finish(a2, "Cursor $k$ (UI)")
a2.set_title("After normalized 3-tap ZF FFE", loc="left")
panel(a2, "b")
savefig(fig, "ch06_zf")
print("ZF taps", a, an, "after", np.round(after, 3))

# ------------------------------------------------------------------ ch06_ref
c3 = sdp.forcing_ffe(1, p[i0 + SPS * np.arange(-1, 2)]); c3 = c3 / np.abs(c3).sum()
c2 = sdp.forcing_ffe(0, p[i0 + SPS * np.arange(0, 2)]); c2 = c2 / np.abs(c2).sum()
print("taps", np.round(c3, 4), np.round(c2, 4))
bits = np.tile(prbs_bits(7), 40)
res = {}
for name, c in (("none", None), ("2tap", c2), ("3tap", c3)):
    y = through(tx_wave(bits, fir=c), h)
    hts, ph, S, A = eye_scan(y, bits)
    res[name] = (y, ph, hts)
    print(name, "eye", round(1e3 * hts[ph], 1), "mV", np.sum(hts > 0) / SPS, "UI")
# quantized 2-tap taps (driver built from 16 or 32 equal slices)
for nseg in (8, 16, 32):
    n1 = int(round(abs(c2[1]) * nseg))
    cq = np.array([nseg - n1, -n1]) / nseg
    y = through(tx_wave(bits, fir=cq), h)
    hts, ph, S, A = eye_scan(y, bits)
    print("quantized", nseg, cq, round(1e3 * hts[ph], 1))
# grid-searched 3-tap (PDA optimum) for comparison
cg = np.array([-0.04, 0.61, -0.35])
y = through(tx_wave(bits, fir=cg), h)
hts, ph, S, A = eye_scan(y, bits)
print("grid 3tap", round(1e3 * hts[ph], 1), np.sum(hts > 0) / SPS)

fig = plt.figure(figsize=(6.3, 2.45))
gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1, 1])
a1 = fig.add_subplot(gs[0]); a2 = fig.add_subplot(gs[1]); a3 = fig.add_subplot(gs[2], sharey=a2)
tu = (np.arange(p.size) - i0) / SPS
mm = (tu > -2) & (tu < 6)
for c, col, lab, npre in ((None, MUTED, "no FFE", 0), (c2, C1, "2-tap", 0), (c3, C2, "3-tap ZF", 1)):
    pp = p if c is None else sum(cj * np.roll(p, (j - npre) * SPS) for j, cj in enumerate(c))
    a1.plot(tu[mm], pp[mm], color=col, label=lab, lw=1.3 if c is not None else 1.0,
            ls="--" if c is None else "-")
    if c is not None:
        j0 = i0 + SPS * (1 if npre == 0 else 1)   # ZF design phase: old peak + (delay of main tap)
        j0 = i0 + SPS * npre if npre else i0
        kk = np.arange(-2, 6)
        a1.plot(tu[j0 + kk * SPS], pp[j0 + kk * SPS], "o", color=col, ms=2.8)
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_xlim(-2, 6); a1.set_ylim(-0.05, 0.37)
a1.legend(loc="upper right", fontsize=7)
finish(a1, "Time (UI)", "Pulse response (V)")
panel(a1, "a")
for ax, key, title in ((a2, "none", "No FFE"), (a3, "2tap", "2-tap FFE")):
    y, ph, hts = res[key]
    eye_density(ax, y, SPS, phase=ph, skip_ui=100, vlim=(-0.55, 0.55))
    ax.set_title(f"{title}: {1e3 * hts[ph]:.0f} mV".replace("-", "\u2212"), loc="left", fontsize=8)
a2.set_ylabel("RX input (V)")
plt.setp(a3.get_yticklabels(), visible=False)
panel(a2, "b"); panel(a3, "c")
savefig(fig, "ch06_ref")
