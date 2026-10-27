"""ch07_ctle.py -- figures for Chapter 7 (CTLE).

ch07_rlc  : RLC-peaked load: boost vs damping zeta, and the ringing step response
ch07_bode : degenerated-pair CTLE: annotated Bode (Lab 4 example circuit) and the 0-12 dB family
ch07_ref  : CTLE on the REF channel: pulse responses and eye height vs peaking (Lab 4 sweep)
ch07_we6  : Worked Example 7.x: SG13G2 HBT CTLE, ideal vs realized boost, and the fixed design
"""
from bricdstyle import *
from link import *
import scipy.signal as sig
M = lambda v, d=1: f"{v:.{d}f}".replace("-", "\u2212")   # proper minus sign in labels

H = channel(REF_LEN)
fg = F / 1e9

# ------------------------------------------------------------------ ch07_rlc
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.15))
w = np.logspace(-1.3, 1.0, 1500)
tt = np.linspace(0, 40, 3000)
for z, col in zip((0.2, 0.3, 0.5, 0.707), (C4, C2, C1, C3)):
    num, den = np.array([1, 2 * z]) / (2 * z), [1, 2 * z, 1]   # Z/R with wn = 1
    _, Hz = sig.freqs(num, den, w)
    pkdb = 20 * np.log10(np.abs(Hz).max())
    a1.semilogx(w, 20 * np.log10(np.abs(Hz)), color=col, label=f"$\\zeta$ = {z:g}  ({pkdb:.1f} dB)")
    _, yst = sig.step((num, den), T=tt)
    a2.plot(tt / (2 * np.pi), yst, color=col, lw=1.2 if z != 0.2 else 1.5)
z = 0.2
env = np.exp(-z * tt)
a2.plot(tt / (2 * np.pi), 1 + 2.0 * env, color=C4, ls=":", lw=0.9)
a2.plot(tt / (2 * np.pi), 1 - 2.0 * env, color=C4, ls=":", lw=0.9)
a2.text(2.35, 1.55, "$\\propto e^{-\\zeta\\omega_n t}$", color=C4, fontsize=8)
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_xlim(w[0], w[-1]); a1.set_ylim(-14, 19)
a1.legend(loc="upper left", fontsize=7)
finish(a1, "Normalized frequency $\\omega/\\omega_n$", "$|Z_\\mathrm{load}|/R_S$ (dB)")
panel(a1, "a")
a2.set_xlim(0, 4); a2.set_ylim(-0.2, 3.2)
finish(a2, "Time ($t\\,\\omega_n/2\\pi$)", "Step response / final value")
panel(a2, "b")
savefig(fig, "ch07_rlc")

# ------------------------------------------------------------------ ch07_bode
gm, RS, CS, RD, CLd = 20e-3, 401.0, 0.795e-12, 50.0, 318e-15     # Lab 4 example circuit
def hdeg(f, gm, RS, CS, RD, CL):
    s = 2j * np.pi * f
    return gm * RD / (1 + gm * RS / 2) * (1 + s * RS * CS) / (1 + s * RS * CS / (1 + gm * RS / 2)) / (1 + s * RD * CL)
f = np.logspace(7.5, 11.3, 2000)
Hd = hdeg(f, gm, RS, CS, RD, CLd)
fz = 1 / (2 * np.pi * RS * CS); fp1 = (1 + gm * RS / 2) * fz; fp2 = 1 / (2 * np.pi * RD * CLd)
g0 = 20 * np.log10(gm * RD / (1 + gm * RS / 2)); ghf = 20 * np.log10(gm * RD)
print(f"Bode example: fz={fz/1e9:.3f} fp1={fp1/1e9:.3f} fp2={fp2/1e9:.2f} GHz DC={g0:.2f} HF={ghf:.2f} dB")
fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
# asymptotes
fa = np.logspace(7.5, 11.3, 400)
asym = g0 + 20 * np.log10(np.maximum(1, fa / fz)) - 20 * np.log10(np.maximum(1, fa / fp1)) - 20 * np.log10(np.maximum(1, fa / fp2))
a1.semilogx(fa / 1e9, asym, color=MUTED, ls="--", lw=0.9, label="asymptotes")
a1.semilogx(f / 1e9, 20 * np.log10(np.abs(Hd)), color=C1, lw=1.6, label="$|H_\\mathrm{CTLE}|$")
for fx, lab, y, dx, dy, ha in ((fz, "$\\omega_z$", g0, 0, -24, "center"), (fp1, "$\\omega_{p1}$", ghf, -3, 6, "right"), (fp2, "$\\omega_{p2}$", ghf, 3, 6, "left")):
    a1.plot(fx / 1e9, y, "o", color=GOLD, ms=4, zorder=5)
    a1.annotate(lab + f" {fx/1e9:.2g} GHz", (fx / 1e9, y), xytext=(dx, dy),
                textcoords="offset points", ha=ha, fontsize=7, color=GOLDDK)
iN = np.argmin(np.abs(f - 2.5e9)); gN = 20 * np.log10(np.abs(Hd[iN]))
a1.plot(2.5, gN, "o", color=C1, ms=4, zorder=5)
a1.annotate(f"{M(gN)} dB at $f_\\mathrm{{N}}$:\nboost {gN - g0:.1f} dB", (2.5, gN), xytext=(9, -18),
            fontsize=7, color=C1, ha="left", arrowprops=dict(arrowstyle="-|>", lw=0.7, color=C1, mutation_scale=7))
a1.axvline(2.5, color=MUTED, ls=":", lw=0.8)
a1.text(2.6, -24.5, "$f_\\mathrm{N}$", color=MUTED, fontsize=7.5)
a1.annotate("", xy=(0.12, ghf), xytext=(0.12, g0), arrowprops=dict(arrowstyle="<->", color=C4, lw=0.8))
a1.text(0.135, (g0 + ghf) / 2, f"ideal peaking\n= {ghf - g0:.0f} dB", fontsize=7, color=C4, va="center")
a1.text(0.035, g0 - 1.2, f"DC: {M(g0, 0)} dB", fontsize=7, color=NAVY, va="top")
a1.text(0.035, ghf + 1.0, f"$g_mR_D$ = {ghf:.0f} dB", fontsize=7, color=NAVY)
a1.axhline(ghf, color=GRID, lw=0.6, zorder=0)
a1.set_xlim(0.03, 200); a1.set_ylim(-26, 6)
a1.legend(loc="lower left", fontsize=7)
finish(a1, "Frequency (GHz)", "Gain (dB)")
panel(a1, "a")
i_n = np.argmin(np.abs(F - F_NYQ))
for pk, col in zip((0, 3, 6, 9, 12), (MUTED, C3, C1, C2, C4)):
    Hc = ctle(pk)
    boost = 20 * np.log10(abs(Hc[i_n]) / abs(Hc[0]))
    a2.semilogx(fg[1:], 20 * np.log10(np.abs(Hc[1:])), color=col, label=f"{pk} dB ({M(boost)} dB at $f_\\mathrm{{N}}$)")
    print("family", pk, "boost at fN", round(boost, 2), "peak/DC", round(20 * np.log10(np.abs(Hc).max() / abs(Hc[0])), 2))
a2.axvline(2.5, color=MUTED, ls=":", lw=0.8)
a2.set_xlim(0.03, 100); a2.set_ylim(-27, 3)
a2.legend(loc="lower left", fontsize=6.8, title="ideal peaking (realized boost)", title_fontsize=6.8)
finish(a2, "Frequency (GHz)", "Gain (dB)")
panel(a2, "b")
savefig(fig, "ch07_bode")

# ------------------------------------------------------------------ ch07_ref
bits = np.tile(prbs_bits(7), 40)
x = tx_wave(bits)
peaks = np.arange(0, 21, 2)
eh, p0s, ew = [], [], []
for pk in peaks:
    hl, _ = impulse(H * ctle(pk))
    hts, ph, S, A = eye_scan(through(x, hl), bits)
    eh.append(hts[ph]); ew.append(np.sum(hts > 0) / SPS)
    p0s.append(2 * A_TX * pulse(hl).max())
eh = np.array(eh); p0s = np.array(p0s)
print("sweep eye mV", np.round(1e3 * eh, 1)); print("sweep 2A p0 mV", np.round(1e3 * p0s, 1))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.3), gridspec_kw=dict(width_ratios=[1.1, 1]))
h0, _ = impulse(H); pref = pulse(h0); iref = int(np.argmax(pref))
for pk, col, lab in ((None, MUTED, "channel only"), (8, C1, "+ 8 dB CTLE"), (14, C3, "+ 14 dB (best alone)"), (20, C4, "+ 20 dB (over-peaked)")):
    pp = pref if pk is None else pulse(impulse(H * ctle(pk))[0])
    i0 = int(np.argmax(pp))
    tu = (np.arange(pp.size) - i0) / SPS
    mm = (tu > -2) & (tu < 6)
    a1.plot(tu[mm], pp[mm], color=col, label=lab, ls="--" if pk is None else "-", lw=1.0 if pk is None else 1.3)
    if pk == 20:
        k = np.arange(1, 4)
        a1.plot(k, pp[i0 + k * SPS], "o", color=col, ms=3)
note(a1, (2.0, -0.017), "$h_1, h_2 < 0$", (3.0, 0.08), color=C4, fs=7)
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_xlim(-2, 6); a1.set_ylim(-0.04, 0.37)
a1.legend(loc="upper right", fontsize=7)
finish(a1, "Time from main cursor (UI)", "Pulse response (V)")
panel(a1, "a")
a2.axvspan(0, 12, color=BGPALE, lw=0)
a2.text(6, 345, "Open-SERDES CTLE range", ha="center", fontsize=7, color=MUTED)
a2.plot(peaks, 1e3 * p0s, "s-", color=C2, ms=3.5, label="main cursor $2Ap_0$")
a2.plot(peaks, 1e3 * eh, "o-", color=C1, ms=3.5, label="eye height (PRBS7)")
ib = int(np.argmax(eh))
note(a2, (peaks[ib], 1e3 * eh[ib]), f"best: {peaks[ib]} dB, {1e3*eh[ib]:.0f} mV", (12.6, 35), color=C1, fs=7)
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xlim(0, 20); a2.set_ylim(-100, 370); a2.set_xticks(range(0, 21, 4))
a2.legend(loc="lower right", fontsize=7)
finish(a2, "CTLE ideal peaking (dB)", "Voltage (mV)")
panel(a2, "b")
savefig(fig, "ch07_ref")

# ------------------------------------------------------------------ ch07_we6 (HBT CTLE)
VT = 0.02585
gmh = 1e-3 / VT                                   # 1 mA per device (2 mA tail)
designs = {"WE6 as designed": (112, 1.8e-12), "fixed: $\\omega_{p1}$ at $2f_\\mathrm{N}$, lower $\\omega_z$": (317, 0.717e-12)}
RC, CLh = 200, 100e-15
f = np.logspace(8, 11, 1500)
fig, ax = plt.subplots(figsize=(6.3, 2.2))
for (name, (RE, CE)), col in zip(designs.items(), (C1, C3)):
    Hh = hdeg(f, gmh, RE, CE, RC, CLh)
    G0 = 20 * np.log10(abs(hdeg(0, gmh, RE, CE, RC, CLh)))
    GN = 20 * np.log10(abs(hdeg(2.5e9, gmh, RE, CE, RC, CLh)))
    fzh = 1 / (2 * np.pi * RE * CE); fp1h = (1 + gmh * RE / 2) * fzh; fp2h = 1 / (2 * np.pi * RC * CLh)
    print(f"{name}: RE={RE} CE={CE*1e12:.3f}p fz={fzh/1e9:.3f} fp1={fp1h/1e9:.3f} fp2={fp2h/1e9:.2f} "
          f"ideal={20*np.log10(1+gmh*RE/2):.2f} DC={G0:.2f} Nyq={GN:.2f} boost={GN-G0:.2f} "
          f"peak={20*np.log10(np.abs(Hh).max()):.2f}@{f[np.argmax(np.abs(Hh))]/1e9:.2f}GHz IRE/2={2e-3*RE/2*1e3:.0f}mV")
    asym = G0 + 20 * np.log10(np.maximum(1, f / fzh)) - 20 * np.log10(np.maximum(1, f / fp1h)) - 20 * np.log10(np.maximum(1, f / fp2h))
    ax.semilogx(f / 1e9, asym, color=col, ls="--", lw=0.8)
    ax.semilogx(f / 1e9, 20 * np.log10(np.abs(Hh)), color=col, lw=1.6,
                label=f"{name}: ideal {20*np.log10(1+gmh*RE/2):.0f} dB, realized {GN-G0:.1f} dB")
    ax.plot(2.5, GN, "o", color=col, ms=4, zorder=5)
    ax.annotate("", xy=(2.5 * (1.06 if col == C1 else 0.94), GN), xytext=(2.5 * (1.06 if col == C1 else 0.94), G0),
                arrowprops=dict(arrowstyle="<->", color=col, lw=0.8))
    ax.axhline(G0, xmax=0.36, color=col, lw=0.6, ls=":")
ax.axvline(2.5, color=MUTED, ls=":", lw=0.8)
ax.text(2.6, -1.3, "$f_\\mathrm{N}$", color=MUTED, fontsize=7.5)

ax.set_xlim(0.1, 100); ax.set_ylim(-2, 25.5)
ax.legend(loc="upper left", fontsize=7, title="dashed: pole-zero asymptotes (the \u201cideal\u201d picture)", title_fontsize=7, alignment="left")
finish(ax, "Frequency (GHz)", "Gain (dB)")
savefig(fig, "ch07_we6")
