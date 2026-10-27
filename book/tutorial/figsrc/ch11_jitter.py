"""ch11_jitter.py -- figures and checked numbers for Chapter 11 (Jitter).

Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch11_jitter.py
Writes ch11_tie, ch11_slope, ch11_hist, ch11_bathtub, ch11_pn, ch11_budget (tutorial/figs/).
"""
from bricdstyle import *
from scipy.special import erfc, erfcinv
from scipy.stats import norm

UI = 200e-12
F0 = 2.5e9                      # half-rate clock
T0 = 1 / F0                     # 400 ps
Qf = lambda x: 0.5 * erfc(x / np.sqrt(2))
Q12 = np.sqrt(2) * erfcinv(2e-12)
print(f"Q(1e-12) = {Q12:.3f}, 2Q = {2*Q12:.3f}")

# ------------------------------------------------------------------ worked example 11.1 (definitions)
edges = np.array([0, 401.0, 799.5, 1201.5, 1600.0, 2000.8])
tie = edges - 400 * np.arange(len(edges))
per = np.diff(edges) - 400
cc = np.diff(np.diff(edges))
rms = lambda x: np.sqrt(np.mean(np.asarray(x) ** 2))
print("WE11.1 TIE", tie, "rms", round(rms(tie), 2), "pp", tie.max() - tie.min())
print("        Jper", per, "rms", round(rms(per), 2))
print("        Jcc ", cc, "rms", round(rms(cc), 2))

# ------------------------------------------------------------------ phase-noise model (team VCO)
L1M = 10 ** (-100.8 / 10)                    # -100.8 dBc/Hz at 1 MHz
kappa = 1e6 / F0 * np.sqrt(L1M)              # sqrt(s)
sig_per = kappa * np.sqrt(T0)
print(f"kappa = {kappa:.3e} sqrt(s); period jitter = {sig_per*1e15:.0f} fs; 1us accumulation = {kappa*np.sqrt(1e-6)*1e12:.2f} ps")
for fc in [0.5e6, 1e6, 2e6, 3e6, 5e6]:
    print(f"   first-order VCO-limited jitter fc={fc/1e6:.1f} MHz: {kappa/np.sqrt(4*np.pi*fc)*1e12:.2f} ps")

# ================================================================== Fig: TIE definitions
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.3), gridspec_kw=dict(width_ratios=[1.55, 1]))
T = 1.0
tie_d = np.array([0.0, 0.13, -0.10, 0.16, -0.05, 0.11])      # exaggerated, in periods
n = len(tie_d)
def sq(edges_r, y0, hi=0.32):
    xs, ys = [-0.15], [y0]
    for e in edges_r:
        xs += [e, e, e + 0.5, e + 0.5]; ys += [y0, y0 + hi, y0 + hi, y0]
    xs += [edges_r[-1] + 0.75]; ys += [y0]
    return xs, ys
ideal = np.arange(n) * T
real = ideal + tie_d
xi, yi = sq(ideal, 1.0)
xr, yr = sq(real, 0.25)
a.plot(xi, yi, color=MUTED, lw=1.1)
a.plot(xr, yr, color=C1, lw=1.4)
for k in range(n):
    a.plot([ideal[k], ideal[k]], [0.2, 1.0], color=MUTED, lw=0.6, ls=":", zorder=0)
    if abs(tie_d[k]) > 0.01:
        a.annotate("", xy=(real[k], 0.41), xytext=(ideal[k], 0.41),
                   arrowprops=dict(arrowstyle="-|>", lw=0.9, color=C4, mutation_scale=6, shrinkA=0, shrinkB=0))
    a.text(ideal[k] + tie_d[k] / 2, 0.66, f"TIE$_{k}$", fontsize=6.5, color=C4, ha="center")
a.annotate("", xy=(real[3], 0.12), xytext=(real[2], 0.12),
           arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=NAVY, mutation_scale=6, shrinkA=0, shrinkB=0))
a.text((real[2] + real[3]) / 2, 0.04, "$T_2 = T + J_{\\mathrm{per},2}$", ha="center", va="top", fontsize=7, color=NAVY)
a.text(-0.12, 1.42, "ideal clock, period $T$", fontsize=7.5, color=MUTED)
a.text(real[-1] + 0.78, 0.40, "jittered\nclock", fontsize=7.5, color=C1, va="center")
a.set_xlim(-0.2, n + 0.35); a.set_ylim(-0.2, 1.55)
a.set_yticks([]); a.set_xticks(ideal); a.set_xticklabels([f"{k}$T$" for k in range(n)])
a.spines["left"].set_visible(False); a.grid(False)
a.set_xlabel("Time (edge offsets exaggerated)")
panel(a, "a")
# (b) TIE vs time: free-running random walk vs PLL-locked
rng = np.random.default_rng(3)
ncyc = 20000
w = rng.standard_normal(ncyc) * sig_per
free = np.cumsum(w)
fc = 3e6; aa = 2 * np.pi * fc * T0
pll = np.zeros(ncyc)
for k in range(1, ncyc):
    pll[k] = (1 - aa) * pll[k - 1] + w[k]
t_us = np.arange(ncyc) * T0 * 1e6
b.plot(t_us, free * 1e12, color=C4, lw=0.9, label="free-running VCO")
b.plot(t_us, pll * 1e12, color=C1, lw=0.9, label="locked in a 3 MHz PLL")
env = kappa * np.sqrt(np.arange(ncyc) * T0) * 1e12
b.fill_between(t_us, -env, env, color=C4, alpha=0.08, lw=0)
b.plot(t_us, env, color=C4, lw=0.6, ls="--"); b.plot(t_us, -env, color=C4, lw=0.6, ls="--")
b.text(7.8, -env[-1] * 0.80, "$\\pm\\kappa\\, t^{1/2}$", color=C4, fontsize=7.5, ha="right")
finish(b, xlabel="Time ($\\mu$s)", ylabel="TIE (ps)")
b.legend(loc="upper left", fontsize=6.8)
b.set_xlim(0, t_us[-1]); b.set_ylim(-14, 14)
panel(b, "b")
print(f"free-running TIE rms at end of sim: {env[-1]:.2f} ps; PLL TIE rms {np.std(pll[5000:])*1e12:.2f} ps (theory {kappa/np.sqrt(4*np.pi*fc)*1e12:.2f})")
savefig(fig, "ch11_tie")

# ================================================================== Fig: voltage noise -> timing via slope
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.15), gridspec_kw=dict(width_ratios=[1.05, 1]))
tt = np.linspace(-45, 45, 400)                    # ps
tau = 25.0
A = 0.2
sv = 0.030                                        # exaggerated noise, V
for k in range(70):
    v = A * np.tanh(tt / tau) + sv * rng.standard_normal() + 0.004 * rng.standard_normal(tt.size).cumsum() * 0
    a.plot(tt, v * 1e3, color=NAVY, alpha=0.08, lw=0.7)
a.plot(tt, A * np.tanh(tt / tau) * 1e3, color=GOLD, lw=1.6)
slope = A / tau                                   # V/ps at the crossing
a.axhline(0, color=C4, lw=0.8, ls="--")
a.text(43, -22, "threshold", color=C4, fontsize=7, ha="right")
# voltage pdf at t=0 (left side) and timing pdf (bottom)
vv = np.linspace(-110, 110, 200)
pv = norm.pdf(vv, 0, sv * 1e3)
a.fill_betweenx(vv, -45, -45 + pv / pv.max() * 9, color=C2, alpha=0.45, lw=0)
a.text(-35, 40, "$\\sigma_v$", color=C2, fontsize=8)
st = sv / slope                                   # ps
tp = np.linspace(-6 * st, 6 * st, 200)
pt = norm.pdf(tp, 0, st)
a.fill_between(tp, -230, -230 + pt / pt.max() * 45, color=C1, alpha=0.45, lw=0)
a.text(st * 3.2, -200, "$\\sigma_t = \\sigma_v / \\mathrm{SR}$", color=C1, fontsize=8)
note(a, (8, slope * 8 * 1e3), "slope SR", (14, 40), color=GOLDDK)
a.set_ylim(-235, 235); a.set_xlim(-45, 45)
finish(a, xlabel="Time (ps)", ylabel="Signal (mV)")
panel(a, "a")
sr = np.logspace(-0.5, 1.2, 100)                  # mV/ps
for s, c in zip([0.5, 1.0, 2.0], [C3, C1, C4]):
    b.loglog(sr, s / sr, color=c, label=f"$\\sigma_v$ = {s:g} mV rms")
for x, lab, dy in [(3.14, "CML clock\n0.4 V$_{ppd}$ at 2.5 GHz", 0.05), (0.785, "same clock\nat 0.1 V$_{ppd}$", 0.05)]:
    b.axvline(x, color=MUTED, lw=0.7, ls=":")
    b.text(x * 1.07, dy, lab, fontsize=6.5, color=MUTED, va="center")
finish(b, xlabel="Slew rate at the threshold (mV/ps)", ylabel="Timing jitter $\\sigma_t$ (ps rms)")
b.legend(loc="upper right", fontsize=6.8)
b.set_ylim(0.03, 4)
panel(b, "b")
savefig(fig, "ch11_slope")
print("slope figure: 1 mV / 3.14 mV/ps =", round(1 / 3.14, 3), "ps; 1 mV / 0.785 =", round(1 / 0.785, 2), "ps")

# ================================================================== Fig: RJ, DJ, TJ histograms
dt = 0.02
x = np.arange(-40, 40 + dt, dt)                   # ps
sig = 2.0
rj = norm.pdf(x, 0, sig)
# DJ = DCD (two impulses at +-4 ps) convolved with ISI-type DDJ (edge offsets +-3, +-2, +-1 ps from three earlier bits)
def diracs(vals):
    d = np.zeros_like(x)
    for v in vals:
        d[np.argmin(np.abs(x - v))] += 1 / (len(vals) * dt)
    return d
dj = diracs([-4, 4])
for amp in (3, 2, 1):
    dj = np.convolve(dj, diracs([-amp, amp]), mode="same") * dt
dj_show = np.convolve(dj, norm.pdf(x, 0, 0.25), mode="same") * dt
dj /= dj.sum() * dt
tj = np.convolve(dj, rj, mode="same") * dt
tj /= tj.sum() * dt
# dual-Dirac fit of the TJ tails on a Q-scale (BER 1e-4..1e-12)
cdf = np.cumsum(tj) * dt
ql = -norm.ppf(np.clip(cdf, 1e-300, 1))           # left tail Q
sel = (ql > norm.isf(1e-4)) & (ql < norm.isf(1e-12))
pfit = np.polyfit(ql[sel], x[sel], 1)             # x = mu_L - sigma*Q
mu_L, sig_fit = pfit[1], -pfit[0]
DJdd = 2 * abs(mu_L)
print(f"hist: DJpp = 20 ps, fitted DJ(dd) = {DJdd:.2f} ps, fitted sigma = {sig_fit:.2f} ps (true {sig})")
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.2), sharey=True)
titles = ["Random jitter (RJ)", "Deterministic jitter (DJ)", "Total jitter = RJ $\\ast$ DJ"]
for ax, p, c, ttl in zip(axs, [rj, dj_show, tj], [C1, C2, NAVY], titles):
    ax.fill_between(x, 1e-12, np.maximum(p, 1e-12), color=c, alpha=0.25, lw=0)
    ax.semilogy(x, np.maximum(p, 1e-14), color=c, lw=1.2)
    ax.set_ylim(1e-9, 1); ax.set_xlim(-35, 35)
    ax.set_title(ttl, fontsize=8)
    ax.set_xlabel("Edge position (ps)")
axs[0].set_ylabel("Probability density (1/ps)")
axs[0].text(0, 3e-9, "unbounded:\n$\\sigma$ = 2 ps", ha="center", fontsize=7, color=C1)
axs[1].annotate("", xy=(10, 1.5e-5), xytext=(-10, 1.5e-5),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=GOLDDK, mutation_scale=6))
axs[1].text(0, 2.5e-6, "bounded:\nDJ$_{pp}$ = 20 ps", ha="center", fontsize=7, color=GOLDDK)
axs[1].text(0, 3e-9, "DCD $\\pm$4 ps $\\ast$ ISI (DDJ)\nfrom 3 earlier bits, $\\pm$6 ps", ha="center", fontsize=6.8, color=GOLDDK)
# dual-Dirac model overlay
dd = 0.5 * norm.pdf(x, -DJdd / 2, sig_fit) + 0.5 * norm.pdf(x, DJdd / 2, sig_fit)
axs[2].semilogy(x, dd, color=GOLD, lw=1.0, ls="--", label="dual-Dirac fit")
axs[2].legend(loc="upper right", fontsize=6.5)
axs[2].text(0, 3e-9, f"tails fit: DJ$_{{\\delta\\delta}}$ = {DJdd:.1f} ps,\n$\\sigma$ = {sig_fit:.1f} ps", ha="center", fontsize=6.8, color=NAVY)
for k, ax in enumerate(axs):
    panel(ax, "abc"[k])
savefig(fig, "ch11_hist")

# ================================================================== Fig: dual-Dirac PDF + bathtub
DJ = 40.0
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.25))
xx = np.linspace(-30, 230, 3000)
s_show = 3.0
for c0 in (0, 200):
    p = 0.5 * norm.pdf(xx, c0 - DJ / 2, s_show) + 0.5 * norm.pdf(xx, c0 + DJ / 2, s_show)
    a.fill_between(xx, 0, p, color=C1, alpha=0.25, lw=0)
    a.plot(xx, p, color=C1, lw=1.1)
    for s in (-1, 1):
        a.annotate("", xy=(c0 + s * DJ / 2, 0.075), xytext=(c0 + s * DJ / 2, 0.0),
                   arrowprops=dict(arrowstyle="-|>", lw=1.0, color=GOLDDK, mutation_scale=7))
a.annotate("", xy=(DJ / 2, 0.085), xytext=(-DJ / 2, 0.085),
           arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=GOLDDK, mutation_scale=6))
a.text(0, 0.092, "DJ$_{\\delta\\delta}$", ha="center", fontsize=7.5, color=GOLDDK)
a.text(100, 0.06, "left and right\ncrossings of the eye", ha="center", fontsize=7.2, color=MUTED)
a.text(100, 0.02, f"Gaussian RJ, $\\sigma$ = {s_show:g} ps,\nat each Dirac", ha="center", fontsize=7.2, color=C1)
a.set_ylim(0, 0.105); a.set_xlim(-40, 240)
finish(a, xlabel="Edge position (ps)", ylabel="Probability density (1/ps)")
panel(a, "a")
xs = np.linspace(0, 200, 4001)
for s, c in [(1.32, C3), (3.0, C1), (5.0, C4)]:
    ber = Qf((xs - DJ / 2) / s) + Qf((200 - xs - DJ / 2) / s)
    ber = np.clip(ber, 1e-18, 0.5)
    b.semilogy(xs / 200, ber, color=c, lw=1.3, label=f"$\\sigma_\\mathrm{{RJ}}$ = {s:g} ps")
    ew = 200 - (DJ + 2 * Q12 * s)
    print(f"bathtub sigma={s}: TJ={DJ+2*Q12*s:.1f} ps, EW={ew:.1f} ps = {ew/200:.3f} UI")
b.axhline(1e-12, color=MUTED, lw=0.8, ls="--")
b.text(0.5, 3e-12, "BER = 10$^{-12}$", ha="center", fontsize=7, color=MUTED)
ew = 200 - (DJ + 2 * Q12 * 1.32)
b.annotate("", xy=((100 + ew / 2) / 200, 1e-12), xytext=((100 - ew / 2) / 200, 1e-12),
           arrowprops=dict(arrowstyle="<|-|>", lw=0.9, color=C3, mutation_scale=6))
b.text(0.5, 2e-14, f"eye width {ew/200:.2f} UI", ha="center", fontsize=7, color=C3)
b.set_ylim(1e-16, 1); b.set_xlim(0, 1)
finish(b, xlabel="Sampling instant (UI)", ylabel="BER")
b.legend(loc="center", fontsize=6.8, bbox_to_anchor=(0.5, 0.62))
panel(b, "b")
savefig(fig, "ch11_bathtub")

# ================================================================== Fig: phase noise profile + integrated jitter
f = np.logspace(3, np.log10(1.25e9), 6000)
s = 1j * 2 * np.pi * f
L_vco = L1M * (1e6 / f) ** 2 * (1 + 1e5 / f) + 10 ** (-155 / 10)
L_in = 10 ** (-110 / 10) * np.ones_like(f)
# third-order CP-PLL, 60 deg PM, f_u = 3 MHz (Chapter 12 design), K_VCO = 2pi*150 MHz/V, N = 50
def pll_lg(fu, Icp=600e-6, N=50, Kv=2 * np.pi * 150e6, pm=60):
    tp = np.tan(np.radians(pm)); Kc = 2 * tp ** 2 + 2 * tp * np.sqrt(tp ** 2 + 1)
    wu = 2 * np.pi * fu; wz = wu / np.sqrt(1 + Kc); wp = wu * np.sqrt(1 + Kc)
    C2 = Icp * Kv / (2 * np.pi * N * wu ** 2) * np.sqrt((wu ** 2 + wz ** 2) / (wu ** 2 + wp ** 2))
    C1 = Kc * C2; R = 1 / (wz * C1)
    Z = (1 + s * R * C1) / (s * (C1 + C2) * (1 + s * R * C1 * C2 / (C1 + C2)))
    return Icp / (2 * np.pi) * Kv / s * Z / N
LG = pll_lg(3e6)
H = LG / (1 + LG); E = 1 / (1 + LG)
L_out = L_vco * np.abs(E) ** 2 + L_in * np.abs(H) ** 2
def cum_from(Lf):          # sigma_t integrated from each f up to f0/2
    seg = 0.5 * (Lf[1:] + Lf[:-1]) * np.diff(f)
    c = np.concatenate([np.cumsum(seg[::-1])[::-1], [0]])
    return np.sqrt(2 * c) / (2 * np.pi * F0)
cj_out = cum_from(L_out)
cj_vco = cum_from(L_vco)
i10k = np.argmin(np.abs(f - 1e4)); i4 = np.argmin(np.abs(f - 4e6)); i1 = np.argmin(np.abs(f - 1e6))
print(f"PLL out (fu=3 MHz): jitter 10k-1.25G = {cj_out[i10k]*1e12:.2f} ps, above 4 MHz = {cj_out[i4]*1e12:.2f} ps, above 1 MHz = {cj_out[i1]*1e12:.2f} ps")
print(f"free VCO above 1 MHz = {cj_vco[i1]*1e12:.2f} ps, above 4 MHz = {cj_vco[i4]*1e12:.2f} ps")
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.35))
a.semilogx(f, 10 * np.log10(L_vco), color=C4, lw=1.1, label="free-running VCO")
a.semilogx(f, 10 * np.log10(L_in), color=C2, lw=1.1, ls="--", label="in-band floor (ref + CP) $\\times N^2$")
a.semilogx(f, 10 * np.log10(L_out), color=NAVY, lw=1.6, label="PLL output ($f_u$ = 3 MHz)")
a.plot(1e6, -100.8, "o", color=C4, ms=4)
a.text(1.25e6, -98, "$-$100.8 dBc/Hz\nat 1 MHz", fontsize=6.8, color=C4, va="bottom")
a.axvspan(4e6, 1.25e9, color=GOLDLT, alpha=0.16, lw=0)
a.text(3e7, -158, "not tracked by\na 4 MHz CDR", fontsize=6.8, color=GOLDDK, ha="center")
a.set_ylim(-165, -55); a.set_xlim(1e3, 1.25e9)
finish(a, xlabel="Offset frequency (Hz)", ylabel="Phase noise L(f) (dBc/Hz)")
a.legend(loc="upper right", fontsize=6.3)
panel(a, "a")
b.semilogx(f, cj_out * 1e12, color=NAVY, lw=1.6, label="PLL output")
b.semilogx(f, cj_vco * 1e12, color=C4, lw=1.1, label="free-running VCO")
for fx, val, lab in [(1e4, cj_out[i10k], "10 kHz"), (4e6, cj_out[i4], "4 MHz")]:
    b.plot(fx, val * 1e12, "o", color=GOLDDK, ms=4)
    b.text(fx * 1.3, val * 1e12 + 0.12, f"{val*1e12:.2f} ps", fontsize=7, color=GOLDDK)
b.axvspan(4e6, 1.25e9, color=GOLDLT, alpha=0.16, lw=0)
b.set_ylim(0, 3.0); b.set_xlim(1e3, 1.25e9)
finish(b, xlabel="Lower integration limit $f_1$ (Hz)", ylabel="rms jitter from $f_1$ to $f_0/2$ (ps)")
b.legend(loc="upper right", fontsize=6.8)
panel(b, "b")
savefig(fig, "ch11_pn")

# ================================================================== Fig: jitter budget (horizontal waterfall)
items = [("TX: half-rate mux DCD + driver DDJ", 8.0, "DJ", C2),
         ("Channel: residual ISI after EQ (DDJ)", 6.0, "DJ", C2),
         ("RX clock path: I/Q error, duty cycle, PI INL", 6.0, "DJ", C2),
         ("CDR: PI quantization + bang-bang dither", 20.0, "DJ", C2)]
rj_items = [("TX clock (PLL + buffers), untracked", 1.0), ("RX clock (PLL + PI + buffers), untracked", 0.7),
            ("Samplers: aperture and noise", 0.5)]
sig_tot = np.sqrt(sum(v ** 2 for _, v in rj_items))
DJtot = sum(v for _, v, _, _ in items)
TJ = DJtot + 2 * Q12 * sig_tot
print(f"budget: DJ={DJtot} ps, sigma={sig_tot:.3f} ps, 2Q sigma={2*Q12*sig_tot:.1f} ps, TJ={TJ:.1f} ps = {TJ/200:.3f} UI; sigma max for 60 ps = {(60-DJtot)/(2*Q12):.2f} ps")
fig, ax = plt.subplots(figsize=(6.3, 2.35))
rows = [(lab, v, c) for lab, v, _, c in items] + [(f"RJ: 2Q$\\sigma$ with $\\sigma$ = {sig_tot:.2f} ps (RSS of 1.0, 0.7, 0.5 ps)", 2 * Q12 * sig_tot, C1)]
left = 0
for i, (lab, v, c) in enumerate(rows):
    y = len(rows) - i + 1
    ax.barh(y, v, left=left, color=c, alpha=0.85, height=0.62, edgecolor="white")
    ax.text(left + v + 2, y, f"{lab}:  {v:.1f} ps", va="center", fontsize=7, color=NAVY)
    left += v
ax.barh(1, TJ, color=NAVY, height=0.62)
ax.barh(1, 200 - TJ, left=TJ, color=C3, alpha=0.35, height=0.62)
ax.text(TJ / 2, 1, f"TJ = {TJ:.1f} ps", va="center", ha="center", fontsize=7.5, color="white", fontweight="bold")
ax.text(140, 1, f"eye width left at 10$^{{-12}}$: {200-TJ:.1f} ps = {(200-TJ)/200:.2f} UI",
        va="center", ha="center", fontsize=7.5, color=NAVY)
ax.plot([60, 60], [0.55, 1.45], color=C4, lw=1.2, ls="--")
ax.text(61.5, 1.0, "0.3 UI\nlimit", color=C4, fontsize=6.5, va="center")
ax.set_xlim(0, 200); ax.set_ylim(0.5, 7.1)
ax.set_yticks([]); ax.spines["left"].set_visible(False)
sec = ax.secondary_xaxis("top", functions=(lambda v: v / 200, lambda u: u * 200))
sec.set_xlabel("UI", fontsize=7.5); sec.tick_params(labelsize=7)
ax.grid(axis="y", visible=False)
finish(ax, xlabel="Time within one UI (ps)")
savefig(fig, "ch11_budget")
