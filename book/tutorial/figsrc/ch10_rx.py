"""ch10_rx.py -- figures for Chapter 10 (Receiver Front-End and Samplers).

ch10_sa       : behavioural StrongARM latch: output nodes in time, and exponential divergence (log scale)
ch10_aperture : sampling functions h(t) of a StrongARM and an HBT CML latch, cumulative weight, |H(f)|
ch10_meta     : metastability error probability vs available regeneration time (Evans' formula)
ch10_offset   : Pelgrom offset distribution before/after 5-bit calibration, and the |Vos| CDF vs spec
Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch10_rx.py
"""
from bricdstyle import *
from scipy.special import erfc, erf

M = lambda v, d=1: f"{v:.{d}f}".replace("-", "−")

# ------------------------------------------------------------------ ch10_sa  (WE numbers)
VDD, C, ID, VTP = 1.2, 20e-15, 200e-6, 0.4
gm_in = 1.5e-3                 # input-pair gm per side during integration
tau = 13e-12                   # C / gm of the cross-coupled pair (20 fF / 1.5 mS)
t1 = C * VTP / ID              # end of integration (PMOS turn on)  = 40 ps
Aint = gm_in * t1 / C          # integration gain = 3
VL = VDD / 2
print(f"SA: t_samp = {t1*1e12:.1f} ps, A_int = {Aint:.2f}, tau = {tau*1e12:.1f} ps")

def strongarm(dvin, T=0.3e-9, dt=0.05e-12, tclk_off=0.2e-9):
    """Behavioural StrongARM: integration (linear), then regeneration with saturation."""
    t = np.arange(-30e-12, T, dt)
    c = np.full(t.size, VDD); x = np.zeros(t.size)
    for i in range(1, t.size):
        ti = t[i]
        if ti <= 0 or ti > tclk_off:            # reset phase: precharge to VDD
            c[i] = c[i - 1] + (VDD - c[i - 1]) * dt / 8e-12
            x[i] = x[i - 1] * (1 - dt / 8e-12)
        elif ti <= t1:                          # integration: both nodes fall, difference grows linearly
            c[i] = c[i - 1] - ID / C * dt
            x[i] = x[i - 1] + gm_in * dvin / C * dt
        else:                                   # regeneration
            c[i] = c[i - 1] - (c[i - 1] - VDD / 2) * dt / 18e-12
            x[i] = x[i - 1] + x[i - 1] / tau * (1 - (x[i - 1] / VDD)**2) * dt
    vp = np.clip(c + x / 2, 0, VDD); vm = np.clip(c - x / 2, 0, VDD)
    return t, vp, vm, np.abs(x)

fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
for a in (a1,):
    a.axvspan(-30, 0, color=BGPALE, lw=0)
    a.axvspan(0, t1 * 1e12, color=GTINT, lw=0)
    a.axvspan(t1 * 1e12, 200, color=BTINT, lw=0)
for dv, ls, lab in ((10e-3, "-", "10 mV"), (0.1e-3, "--", "0.1 mV")):
    t, vp, vm, _ = strongarm(dv)
    a1.plot(t * 1e12, vp, color=C1, ls=ls, lw=1.4, label=f"out$^+$, $\\Delta V_{{in}}$ = {lab}")
    a1.plot(t * 1e12, vm, color=C4, ls=ls, lw=1.4, label=f"out$^-$, $\\Delta V_{{in}}$ = {lab}")
a1.text(-15, 0.12, "reset", ha="center", fontsize=6.8, color=MUTED, rotation=90)
a1.text(t1 * 1e12 / 2, 0.06, "integrate", ha="center", fontsize=6.8, color=GOLDDK)
a1.text(120, 0.06, "regenerate", ha="center", fontsize=6.8, color=C1)
a1.text(240, 0.06, "reset", ha="center", fontsize=6.8, color=MUTED)
a1.set_xlim(-30, 280); a1.set_ylim(-0.05, 1.62)
from matplotlib.lines import Line2D
hh = [Line2D([], [], color=C1, lw=1.4), Line2D([], [], color=C4, lw=1.4),
      Line2D([], [], color=MUTED, lw=1.2), Line2D([], [], color=MUTED, lw=1.2, ls="--")]
a1.legend(hh, ["out$^+$", "out$^-$", "$\Delta V_{in}$ = 10 mV", "0.1 mV"], loc="upper center", ncol=4,
          fontsize=6.4, handlelength=1.5, columnspacing=0.9)
finish(a1, "Time after the clock edge (ps)", "Output node voltage (V)")
panel(a1, "a")
for dv, col in ((100e-3, C3), (10e-3, C1), (1e-3, C5), (0.1e-3, C2), (0.01e-3, C4)):
    t, _, _, ax_ = strongarm(dv)
    a2.semilogy(t * 1e12, np.maximum(ax_, 1e-7), color=col, lw=1.3)
    td = t1 + tau * np.log(VL / (Aint * dv))
    lab = f"{dv*1e3:g} mV"
    a2.text(td * 1e12 + 3, 0.9e-1 if dv < 1e-3 else 0.9e-1, "", fontsize=6)
    i = np.argmin(np.abs(t - t1)); a2.text(t1 * 1e12 - 3, ax_[i], lab, ha="right", va="center", fontsize=6.5, color=col)
    if dv >= 1e-5:
        a2.plot(td * 1e12, VL, "o", color=col, ms=3.2, zorder=5)
a2.axhline(VL, color=NAVY, lw=0.8, ls="--"); a2.text(3, VL * 1.35, "$V_L$ = 0.6 V", ha="left", fontsize=7, color=NAVY)
a2.axvline(t1 * 1e12, color=GOLD, lw=0.8, ls=":")
a2.axvline(180, color=C4, lw=0.9, ls="--"); a2.text(183, 2e-6, "deadline\n(180 ps)", fontsize=6.8, color=C4)
a2.annotate("", xy=(140, 0.03), xytext=(110, 0.03), arrowprops=dict(arrowstyle="<->", lw=0.7, color=NAVY))
a2.text(125, 0.045, "\u03c4\u00b7ln 10 = 30 ps\nper decade", ha="center", fontsize=6.6, color=NAVY)
a2.set_xlim(0, 235); a2.set_ylim(1e-6, 3)
finish(a2, "Time after the clock edge (ps)", "$|V_{out}^+ - V_{out}^-|$ (V)")
panel(a2, "b")
savefig(fig, "ch10_sa")
for dv in (1e-3, 0.1e-3, 0.01e-3, 4e-6):
    print(f"SA: decision time for {dv*1e3:g} mV = {(t1 + tau*np.log(VL/(Aint*dv)))*1e12:.0f} ps")

# ------------------------------------------------------------------ ch10_aperture
dt = 0.05e-12
t = np.arange(-120e-12, 120e-12, dt)
# StrongARM: weight rises with the clock edge (6 ps) and falls linearly to zero at the end of integration
Tint, tr = 40e-12, 6e-12
h_sa = np.where((t >= 0) & (t <= Tint), (1 - np.exp(-t / tr)) * (1 - t / Tint), 0.0)
# CML latch: track stage remembers the input with tau_tr = R_L C; the clock edge (sigma 5 ps) ends tracking at t = 0
tau_tr, sig_e = 12e-12, 5e-12
h_cml = np.exp(np.minimum(t, 0) / tau_tr) * 0.5 * erfc(t / (np.sqrt(2) * sig_e))
h_cml[t < -100e-12] = 0
def stats(h):
    h = h / (h.sum() * dt)
    cum = np.cumsum(h) * dt
    t10, t50, t90 = (t[np.searchsorted(cum, q)] for q in (0.1, 0.5, 0.9))
    return h, cum, t10, t50, t90
fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
ff = np.linspace(0, 25e9, 600)
res = {}
for h0, col, name in ((h_sa, C2, "StrongARM"), (h_cml, C1, "HBT CML latch")):
    h, cum, t10, t50, t90 = stats(h0)
    res[name] = (t90 - t10)
    a1.plot(t * 1e12, h * 1e-12 * 1e2, color=col, lw=1.5, label=f"{name}: $w_{{80}}$ = {(t90-t10)*1e12:.0f} ps")
    a1.plot(t * 1e12, cum * 9.0, color=col, lw=0.9, ls="--")
    for tq in (t10, t90):
        a1.plot(tq * 1e12, np.interp(tq, t, cum) * 9.0, "o", color=col, ms=3)
    Hf = np.array([np.abs(np.sum(h * np.exp(-2j * np.pi * f0 * t)) * dt) for f0 in ff])
    f3 = ff[np.argmax(Hf < 1 / np.sqrt(2))]
    a2.plot(ff / 1e9, 20 * np.log10(Hf), color=col, lw=1.5, label=f"{name}: $f_{{3dB}}$ = {f3/1e9:.0f} GHz")
    print(f"aperture {name}: w80 = {(t90-t10)*1e12:.1f} ps ({(t90-t10)/200e-12:.2f} UI), centroid {t50*1e12:.1f} ps, "
          f"f3dB = {f3/1e9:.1f} GHz, |H(2.5G)| = {20*np.log10(np.interp(2.5e9, ff, Hf)):.2f} dB")
a1.text(-97, 5.2, "dashed: cumulative weight\n(right scale); dots: 10% and 90%", fontsize=6.4, color=MUTED, va="top")
a1.set_xlim(-100, 60); a1.set_ylim(0, 9.9)
a1.legend(loc="upper left", fontsize=6.6)
sec = a1.secondary_yaxis("right", functions=(lambda y: y / 9.0, lambda y: y * 9.0))
sec.set_ylabel("Cumulative weight", color=NAVY, fontsize=8)
finish(a1, "Time relative to the clock edge (ps)", "Sampling function $h(t)$ (%/ps)")
panel(a1, "a")
a2.axvline(2.5, color=GOLD, lw=0.9, ls="--"); a2.text(2.8, 0.12, "$f_N$", color=GOLDDK, fontsize=8)
a2.axhline(-3, color=MUTED, lw=0.6, ls=":")
a2.set_xlim(0, 25); a2.set_ylim(-6, 0.5)
a2.legend(loc="lower left", fontsize=6.6)
finish(a2, "Frequency (GHz)", "Aperture response $|H(f)|$ (dB)")
panel(a2, "b")
savefig(fig, "ch10_aperture")

# ------------------------------------------------------------------ ch10_meta  (WE numbers)
T = np.linspace(0, 260e-12, 600)
VLsa, A, dV = 0.6, 3.0, 0.2
pre_sa = 2 * VLsa / (A * dV)
p_sa = pre_sa * np.exp(-T / 13e-12)
p_sa2 = p_sa * np.exp(-2 * 200e-12 / 20e-12)
pre_cml = 2 * 0.2 / (A * dV)
p_cml = pre_cml * np.exp(-T / 4e-12)
p_cml_ideal = pre_cml * np.exp(-T / 1.8e-12)
fig, ax = plt.subplots(figsize=(6.3, 2.95))
ax.semilogy(T * 1e12, np.minimum(p_sa, 1), color=C2, lw=1.6, label="StrongARM alone ($\\tau$ = 13 ps)")
ax.semilogy(T * 1e12, np.minimum(p_sa2, 1), color=C2, lw=1.6, ls="--", label="StrongARM + 2 CMOS latches ($\\tau$ = 20 ps, 200 ps each)")
ax.semilogy(T * 1e12, np.minimum(p_cml, 1), color=C1, lw=1.6, label="HBT CML latch ($\\tau \\approx$ 4 ps with parasitics)")
ax.semilogy(T * 1e12, np.minimum(p_cml_ideal, 1), color=C1, lw=0.9, ls=":", label="HBT CML latch, ideal ($\\tau$ = 1.8 ps)")
ax.axhline(1e-12, color=C4, lw=0.9, ls="--"); ax.text(258, 2.2e-12, "BER target $10^{-12}$", ha="right", fontsize=7, color=C4)
Tw = 140e-12
for p, col in ((pre_sa * np.exp(-Tw / 13e-12), C2), (pre_sa * np.exp(-Tw / 13e-12 - 20), C2)):
    ax.plot(Tw * 1e12, p, "o", color=col, ms=4.5, zorder=6, mfc="white", mew=1.3)
ax.axvline(140, color=MUTED, lw=0.7, ls=":")
p1 = pre_sa * np.exp(-Tw / 13e-12); p2 = p1 * np.exp(-20)
ax.text(146, p1 * 2.5, "4.2$\\times10^{-5}$ per sample", fontsize=7, color=GOLDDK)
ax.annotate("8.7$\\times10^{-14}$ per sample", (141, p2 * 0.6), xytext=(178, 2e-19), fontsize=7, color=GOLDDK,
            arrowprops=dict(arrowstyle="-|>", lw=0.7, color=GOLDDK, mutation_scale=7))
ax.text(138, 3e-20, "WE: $T_{reg}$ = 140 ps", ha="right", fontsize=6.8, color=MUTED)
ax.set_xlim(0, 260); ax.set_ylim(1e-20, 3)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=6.6)
finish(ax, "Regeneration time available in the first latch, $T_{reg}$ (ps)", "$P_{meta}$ per sample")
savefig(fig, "ch10_meta")
print(f"meta: SA alone {p1:.2e}, SA+2 stages {p2:.2e}, CML(4ps) {pre_cml*np.exp(-Tw/4e-12):.1e}, CML@150ps {pre_cml*np.exp(-150e-12/4e-12):.1e}")

# ------------------------------------------------------------------ ch10_offset  (WE numbers)
AVT = 3.5e-3 * 1e-6                     # V*m  (3.5 mV.um, assumed for 130 nm)
W, Lg = 4e-6, 0.13e-6
sig = AVT / np.sqrt(W * Lg)
nbits = 5
rng = 3 * sig
lsb = 2 * rng / 2**nbits
print(f"offset: sigma = {sig*1e3:.2f} mV, range +-{rng*1e3:.1f} mV, LSB = {lsb*1e3:.3f} mV, residual +-{lsb/2*1e3:.2f} mV")
rs = np.random.default_rng(7)
N = 20000
vos = rs.normal(0, sig, N)
code = np.clip(np.round(vos / lsb), -2**(nbits - 1), 2**(nbits - 1) - 1)
vres = vos - code * lsb
fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
bins = np.arange(-20, 20.01, 0.5)
a1.hist(vos * 1e3, bins=bins, color=PALE, edgecolor=C1, lw=0.4, density=True, label="untrimmed")
a1.hist(vres * 1e3, bins=np.arange(-20, 20.01, 0.25), color=C3, alpha=0.85, density=True, label="after 5-bit trim")
a1.axvspan(-5, 5, color=GTINT, alpha=0.5, lw=0, zorder=0)
for s in (-1, 1):
    a1.axvline(s * rng * 1e3, color=NAVY, lw=0.8, ls=":")
a1.text(rng * 1e3 + 0.5, 0.055, "DAC range\n$\\pm3\\sigma$", fontsize=6.6, color=NAVY)
a1.text(-4.7, 0.127, "Ch. 4 spec $\\pm$5 mV", fontsize=6.6, color=GOLDDK, va="top")
note(a1, (0.6, 0.112), "trimmed: $\\pm$0.46 mV\n(bar off scale)", (5.6, 0.100), color=C3, fs=6.5)
a1.set_xlim(-20, 20); a1.set_ylim(0, 0.13)
a1.legend(loc="upper left", fontsize=6.4)
finish(a1, "Sampler input offset $V_{os}$ (mV)", "Probability density (1/mV)")
panel(a1, "a")
x = np.linspace(0, 20, 400)
cdf_before = erf(x / (np.sqrt(2) * sig * 1e3))
cdf_after = np.array([np.mean(np.abs(vres) * 1e3 <= xx) for xx in x])
a2.plot(x, cdf_before * 100, color=C1, lw=1.6, label="one sampler, untrimmed")
a2.plot(x, cdf_before**4 * 100, color=C4, lw=1.3, ls="--", label="all four samplers, untrimmed")
a2.plot(x, cdf_after * 100, color=C3, lw=1.6, label="after 5-bit trim")
a2.axvline(5, color=GOLDDK, lw=0.9, ls="--"); a2.axvline(1, color=MUTED, lw=0.7, ls=":")
p5 = erf(5 / (np.sqrt(2) * sig * 1e3))
a2.plot(5, p5 * 100, "o", color=C1, ms=4); a2.plot(5, p5**4 * 100, "o", color=C4, ms=4)
a2.text(5.6, p5 * 100 - 2, f"{p5*100:.0f}%", fontsize=7, color=C1, va="top")
a2.text(5.6, p5**4 * 100, f"{p5**4*100:.0f}%", fontsize=7, color=C4, va="center")
a2.text(1.4, 88, "1 mV", fontsize=6.8, color=MUTED)
a2.text(5.4, 8, "5 mV", fontsize=6.8, color=GOLDDK)
a2.set_xlim(0, 20); a2.set_ylim(0, 102)
a2.legend(loc="lower right", fontsize=6.6)
finish(a2, "Offset magnitude $|V_{os}|$ (mV)", "Fraction within $|V_{os}|$ (%)")
panel(a2, "b")
savefig(fig, "ch10_offset")
print(f"offset: P(|Vos|<5mV) = {p5:.3f}, all four = {p5**4:.3f}; after trim P(<1mV) = {np.mean(np.abs(vres)<1e-3):.4f}, P(<5mV) = {np.mean(np.abs(vres)<5e-3):.5f}")
print(f"offset: no-cal area for sigma 1 mV: WL = {(AVT/1e-3)**2*1e12:.1f} um^2 ({(AVT/1e-3)**2/(W*Lg):.0f}x)")

# ------------------------------------------------------------------ WE7 noise numbers
k, Tk = 1.380649e-23, 300.0
en50 = np.sqrt(4 * k * Tk * 50)
print(f"noise: 50-ohm diff. density {en50*1e9:.3f} nV/rtHz, over 11.8 GHz ENBW {en50*np.sqrt(11.8e9)*1e3:.3f} mV")
for Cx in (20e-15, 80e-15, 0.5e-12):
    print(f"noise: kT/C {Cx*1e15:.0f} fF -> {np.sqrt(k*Tk/Cx)*1e3:.3f} mV; differential {np.sqrt(2*k*Tk/Cx)*1e3:.3f} mV")
terms = dict(term=0.10, ctle=0.25, summer=0.32, sampler=1.0)
rss = np.sqrt(sum(v**2 for v in terms.values()))
print(f"noise: RSS = {rss:.3f} mV, 2Q*sigma = {14.07*rss:.1f} mV; Vsens = {14.07*1.0 + 5 + 2*lsb/2*1e3:.1f} mV")
print(f"margin: 131 - {14.07*rss:.1f} - 3.5 - 10 - 20 = {131 - 14.07*rss - 3.5 - 10 - 20:.1f} mV")
