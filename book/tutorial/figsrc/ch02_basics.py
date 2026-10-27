"""ch02_basics.py -- Chapter 2: NRZ waveform, NRZ spectrum, PRBS7, one-pole LTI system."""
from bricdstyle import *
from link import prbs_bits
from scipy.integrate import quad
from scipy.ndimage import gaussian_filter1d

TB = 200e-12      # 1 UI
A = 0.5           # TX amplitude (V)

# ------------------------------------------------------------------ 1) NRZ waveform
bits = np.array([1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0])
sps = 200
a = 2 * bits - 1
x = np.repeat(A * a, sps).astype(float)
x = np.concatenate([np.full(sps, x[0]), x, np.full(sps, x[-1])])
x = gaussian_filter1d(x, 0.07 * sps, mode="nearest")[sps:-sps]       # finite edges
t = np.arange(x.size) / sps                                           # in UI
fig, ax = plt.subplots(figsize=(6.3, 1.8))
for k in range(bits.size + 1):
    ax.axvline(k, color=GRID, lw=0.7, zorder=0)
ax.plot(t, x, color=C1, lw=1.6)
ax.axhline(0, color=MUTED, lw=0.6, ls=":")
for k, (b, ak) in enumerate(zip(bits, a)):
    ax.text(k + 0.5, 0.78, str(b), ha="center", va="center", fontsize=8, color=NAVY, fontweight="bold")
    ax.text(k + 0.5, -0.78, ("+1" if ak > 0 else "\u22121"), ha="center", va="center", fontsize=7, color=MUTED)
    if k > 0 and bits[k] != bits[k - 1]:
        ax.plot(k, 0, "o", ms=4.2, mfc=GOLDLT, mec=GOLDDK, mew=0.8, zorder=5)
ax.text(-0.15, 0.78, "$b_k$", ha="right", va="center", fontsize=8, color=NAVY)
ax.text(-0.15, -0.78, "$a_k$", ha="right", va="center", fontsize=8, color=MUTED)
ax.annotate("", xy=(4, 0.1), xytext=(5, 0.1), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=0.8))
ax.text(4.5, 0.15, "1 UI = 200 ps", ha="center", va="bottom", fontsize=6.8, color=NAVY)
ax.annotate("", xy=(9, 0.3), xytext=(13, 0.3), arrowprops=dict(arrowstyle="<->", color=C4, lw=0.8))
ax.text(11, 0.24, "run of four 1s: no transitions", ha="center", va="top", fontsize=6.8, color=C4)
ax.plot([], [], "o", ms=4.2, mfc=GOLDLT, mec=GOLDDK, label="transition (edge)")
ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.22), fontsize=7, ncol=1)
ax.set_xlim(-0.9, bits.size); ax.set_ylim(-0.95, 0.95)
ax.set_xticks(range(0, 17, 2)); ax.set_yticks([-0.5, 0, 0.5])
ax.grid(False)
finish(ax, xlabel="Time (UI)", ylabel="Voltage (V)")
savefig(fig, "ch02_nrz_wave")

# ------------------------------------------------------------------ 2) NRZ spectrum
f = np.linspace(1e-4, 16, 3200)           # GHz
fb = 5.0
S = np.sinc(f / fb) ** 2                  # np.sinc(x) = sin(pi x)/(pi x)
SdB = 10 * np.log10(np.maximum(S, 1e-6))
frac = lambda fx: 2 * quad(lambda u: np.sinc(u) ** 2, 0, fx / fb, limit=200)[0]
ff = np.linspace(0, 16, 321)
cum = np.array([frac(v) for v in ff])
fN = fb / 2
print(f"power below fN: {frac(fN):.4f}, below fb: {frac(fb):.4f}, below 2fb: {frac(2*fb):.4f}, "
      f"S(fN) = {10*np.log10(np.sinc(0.5)**2):.2f} dB")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.2), gridspec_kw=dict(width_ratios=[1.25, 1]))
ax1.axvspan(0, fN, color=BTINT, zorder=0)
ax1.plot(f, SdB, color=C1)
ax1.axvline(fN, color=GOLD, ls="--", lw=1)
ax1.plot(fN, 10 * np.log10(np.sinc(0.5) ** 2), "o", color=GOLDDK, ms=4)
ax1.text(fN + 0.25, -3.0, "$f_N$ = 2.5 GHz: −3.9 dB", fontsize=7, color=GOLDDK, va="center")
for n in (1, 2, 3):
    ax1.annotate(f"null at {n*fb:.0f} GHz" if n == 1 else f"{n*fb:.0f} GHz", xy=(n * fb, -38),
                 xytext=(n * fb + (0.4 if n < 3 else -0.4), -33), fontsize=6.8, color=C4,
                 ha="left" if n < 3 else "right",
                 arrowprops=dict(arrowstyle="-|>", lw=0.6, color=C4, mutation_scale=6))
ax1.text(1.25, -45, "main lobe\nbelow $f_N$", ha="center", fontsize=6.8, color=BLUE)
ax1.set_xlim(0, 16); ax1.set_ylim(-50, 3)
finish(ax1, xlabel="Frequency (GHz)", ylabel="PSD, normalized (dB)")
panel(ax1, "a")
ax2.plot(ff, 100 * cum, color=C3)
for fx, lab, dy in ((fN, "$f_N$", -11), (fb, "$f_b$", -10)):
    v = 100 * frac(fx)
    ax2.plot(fx, v, "o", color=GOLDDK, ms=4)
    ax2.plot([fx, fx], [0, v], color=GOLD, lw=0.8, ls="--")
    ax2.text(fx + 0.35, v + dy, f"{v:.0f}% below {lab}", fontsize=7, color=GOLDDK)
ax2.set_xlim(0, 16); ax2.set_ylim(0, 102)
finish(ax2, xlabel="Frequency (GHz)", ylabel="Power below $f$ (%)")
panel(ax2, "b")
savefig(fig, "ch02_nrz_psd")

# ------------------------------------------------------------------ 3) PRBS7
b7 = prbs_bits(7)
N = b7.size
_s = "".join(map(str, b7)); b7 = np.roll(b7, -(((_s + _s).find("1" * 7) - 52) % N))  # long runs mid-plot
# rotate so the sequence starts right after the run of 7 ones ends (clean run counting)
def runs_circ(bb):
    i0 = int(np.argmax(bb != np.roll(bb, 1)))   # first index that starts a run
    r = np.roll(bb, -i0); out = []; c = 1
    for i in range(1, r.size + 1):
        if i < r.size and r[i] == r[i - 1]:
            c += 1
        else:
            out.append((int(r[i - 1]), c)); c = 1
    return out, i0
runs, _ = runs_circ(b7)
print("PRBS7 runs:", len(runs), "max ones run", max(c for v, c in runs if v == 1),
      "max zeros run", max(c for v, c in runs if v == 0))
fig = plt.figure(figsize=(6.3, 3.0))
gs = fig.add_gridspec(2, 3, height_ratios=[0.85, 1.6], width_ratios=[1, 1.15, 0.95])
axw = fig.add_subplot(gs[0, :])
tt = np.repeat(np.arange(N + 1), 2)[1:-1]
yy = np.repeat(b7, 2)
axw.fill_between(tt, 0, yy, color=BTINT, lw=0)
axw.plot(tt, yy, color=C1, lw=0.9)
s = "".join(map(str, b7))
i1 = (s + s).find("1" * 7); i0 = (s + s).find("0" * 6)
axw.axvspan(i1 % N, i1 % N + 7, color=C2, alpha=0.25, lw=0)
axw.text(i1 % N - 0.8, 1.22, "seven 1s", ha="right", fontsize=6.8, color=C2, va="center")
axw.axvspan(i0 % N, i0 % N + 6, color=C4, alpha=0.25, lw=0)
axw.text(i0 % N + 6.8, 1.22, "six 0s", ha="left", fontsize=6.8, color=C4, va="center")
axw.set_xlim(0, N); axw.set_ylim(-0.15, 1.45); axw.set_yticks([0, 1])
axw.set_xticks([0, 32, 64, 96, 127]); axw.grid(False)
finish(axw, xlabel="Bit index (one full period, 127 bits)", ylabel="$b_k$")
panel(axw, "a")
axh = fig.add_subplot(gs[1, 0])
L = np.arange(1, 8)
n1 = [sum(1 for v, c in runs if v == 1 and c == l) for l in L]
n0 = [sum(1 for v, c in runs if v == 0 and c == l) for l in L]
axh.bar(L - 0.19, n1, width=0.38, color=C1, label="runs of 1s")
axh.bar(L + 0.19, n0, width=0.38, color=C2, label="runs of 0s")
for l, v in zip(L, n1):
    axh.text(l - 0.21, v + 0.4, str(v), ha="center", fontsize=5.8, color=C1)
for l, v in zip(L, n0):
    axh.text(l + 0.23, v + 0.4, str(v), ha="center", fontsize=5.8, color=C2)
axh.set_xticks(L); axh.set_ylim(0, 19.5)
finish(axh, xlabel="Run length (bits)", ylabel="Number of runs", legend=True, loc="upper right")
panel(axh, "b")
axs = fig.add_subplot(gs[1, 1])
a7 = 2.0 * b7 - 1
Am = np.fft.fft(a7) / N
M = np.arange(0, 3 * N + 1)
fm = M * fb / N                                     # GHz
Pm = np.abs(Am[M % N]) ** 2 * np.sinc(M / N) ** 2
PdB = 10 * np.log10(np.maximum(Pm, 1e-12) / ((N + 1) / N ** 2))
keep = fm <= 12
axs.vlines(fm[keep], -45, PdB[keep], color=C1, lw=0.45, alpha=0.75)
fe = np.linspace(0.01, 12, 600)
axs.plot(fe, 10 * np.log10(np.maximum(np.sinc(fe / fb) ** 2, 1e-6)), color=GOLDDK, lw=1.0, ls="--")
axs.annotate("sinc$^2$ envelope", xy=(6.6, -13.6), xytext=(6.0, 1.5), fontsize=6.8, color=GOLDDK,
             arrowprops=dict(arrowstyle="-|>", lw=0.6, color=GOLDDK, mutation_scale=6))
axs.set_xlim(0, 12); axs.set_ylim(-45, 5)
finish(axs, xlabel="Frequency (GHz)", ylabel="Line power (dB)")
panel(axs, "c")
axz = fig.add_subplot(gs[1, 2])
z = fm <= 0.41
axz.vlines(fm[z] * 1e3, -30, PdB[z], color=C1, lw=1.0)
axz.plot(fm[z] * 1e3, PdB[z], "o", ms=2.4, color=C1)
axz.annotate("DC line: \u221221 dB", xy=(4, -21), xytext=(70, -25.5), fontsize=6.5, color=C4,
             bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"),
             arrowprops=dict(arrowstyle="-|>", lw=0.6, color=C4, mutation_scale=6))
axz.annotate("", xy=(39.4 * 4, 2.2), xytext=(39.4 * 5, 2.2),
             arrowprops=dict(arrowstyle="<->", lw=0.7, color=NAVY, shrinkA=0, shrinkB=0))
axz.text(39.4 * 4.5, 3.2, "$f_b$/127 = 39.4 MHz", fontsize=6.5, ha="center", color=NAVY)
axz.set_xlim(-15, 420); axz.set_ylim(-30, 7)
finish(axz, xlabel="Frequency (MHz), zoom")
panel(axz, "d")
savefig(fig, "ch02_prbs7")

# ------------------------------------------------------------------ 4) one-pole system
f3 = 2.5e9
tau = 1 / (2 * np.pi * f3)
fr = np.logspace(8, 11.3, 400)
H = 1 / (1 + 1j * fr / f3)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.15))
ax1.semilogx(fr / 1e9, 20 * np.log10(np.abs(H)), color=C1, label="$|H(f)|$")
asym = np.where(fr < f3, 0, -20 * np.log10(fr / f3))
ax1.semilogx(fr / 1e9, asym, color=MUTED, lw=0.8, ls="--", label="asymptotes")
ax1.plot(f3 / 1e9, -3.01, "o", color=GOLDDK, ms=4)
note(ax1, (f3 / 1e9, -3.01), "−3 dB at $f_{3\\mathrm{dB}}$ = 2.5 GHz", (0.13, -10), color=GOLDDK, fs=7)
ax1.text(30, -18.5, "−20 dB/decade", fontsize=7, color=MUTED, rotation=-28, ha="center")
ax1.set_xlim(0.1, 200); ax1.set_ylim(-40, 4)
finish(ax1, xlabel="Frequency (GHz)", ylabel="Magnitude (dB)", legend=True, loc="lower left")
panel(ax1, "a")
tp = np.linspace(-50, 600, 800) * 1e-12
step = np.where(tp > 0, 1 - np.exp(-np.maximum(tp, 0) / tau), 0)
ax2.plot(tp * 1e12, step, color=C1)
t10, t90 = tau * np.log(1 / 0.9), tau * np.log(10)
for lev, tx in ((0.1, t10), (0.9, t90)):
    ax2.axhline(lev, color=GRID, lw=0.8, ls="-")
    ax2.plot(tx * 1e12, lev, "o", color=GOLDDK, ms=4)
ax2.annotate("", xy=(t10 * 1e12, 0.52), xytext=(t90 * 1e12, 0.52),
             arrowprops=dict(arrowstyle="<->", color=GOLDDK, lw=0.8))
ax2.text((t10 + t90) / 2 * 1e12 + 8, 0.58, f"$t_r$ = {1e12*(t90-t10):.0f} ps\n= 0.35/$f_{{3\\mathrm{{dB}}}}$",
         fontsize=7, color=GOLDDK, ha="left")
ax2.annotate("", xy=(0, 1.1), xytext=(200, 1.1), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=0.8))
ax2.text(100, 1.13, "1 UI = 200 ps", fontsize=7, color=NAVY, ha="center", va="bottom")
ax2.text(560, 0.1, "10%", fontsize=6.5, color=MUTED, va="bottom", ha="right")
ax2.text(560, 0.9, "90%", fontsize=6.5, color=MUTED, va="top", ha="right")
ax2.set_xlim(-50, 600); ax2.set_ylim(-0.05, 1.27)
finish(ax2, xlabel="Time (ps)", ylabel="Step response (normalized)")
panel(ax2, "b")
print(f"tau = {tau*1e12:.1f} ps, t_r = {1e12*(t90-t10):.1f} ps")
savefig(fig, "ch02_onepole")
