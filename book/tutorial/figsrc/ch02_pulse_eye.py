"""ch02_pulse_eye.py -- Chapter 2: pulse response, superposition, ISI vs tau, eye diagrams, BER."""
from bricdstyle import *
from link import *            # channel, pulse_of, cursors, prbs_bits, SPS, DT, UI, A_TX ...
from scipy.signal import lfilter
from scipy.stats import norm

A = A_TX                      # 0.5 V
rng = np.random.default_rng(2026)


def one_pole(x, tau_ui, sps=SPS):
    """Exact one-pole RC response (tau in UI) to a piecewise-constant waveform x."""
    a = np.exp(-1.0 / (tau_ui * sps))
    return lfilter([1 - a], [1, -a], x, zi=[x[0] * a])[0] if False else lfilter([1 - a], [1, -a], x - x[0]) + x[0]


# ------------------------------------------------------------------ 1) pulse response & cursors (10 dB channel)
L10 = LOSS_FAMILY[10]
t, p = pulse_of(channel(L10))
k, pk, i0 = cursors(p, 2, 6)
print("10 dB channel cursors k=-2..6:", np.round(pk, 4), " PDA:", round(pda_eye(pk, k), 4))
tu = (np.arange(p.size) - i0) / SPS                 # time in UI relative to main cursor
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.3), gridspec_kw=dict(width_ratios=[1.55, 1]))
rect = np.where((tu > -0.5) & (tu <= 0.5), 1.0, 0.0)
ax1.fill_between(tu, 0, rect, color=GTINT, lw=0, zorder=0)
ax1.plot(tu, rect, color=GOLD, lw=1.0, ls="--", label="TX pulse, 1 V × 1 UI (delay removed)")
ax1.plot(tu, p, color=C1, lw=1.6, label="pulse response $p(t)$")
for kk, v in zip(k, pk):
    c = GOLDDK if kk == 0 else (C4 if kk < 0 else C1)
    ax1.plot([kk, kk], [0, v], color=c, lw=0.8, ls=":")
    ax1.plot(kk, v, "o", color=c, ms=4.5, zorder=5)
for kk, txt, dx, dy in ((-1, "$p_{-1}$ (pre-cursor)", -0.12, 0.06), (0, "$p_0$ (main cursor)", 0.62, 0.0),
                        (1, "$p_1$", 0.12, 0.06), (2, "$p_2$", 0.1, 0.05), (3, "$p_3$", 0.1, 0.05)):
    v = pk[list(k).index(kk)]
    ax1.text(kk + dx, v + dy, txt, fontsize=7.2, color=GOLDDK if kk == 0 else (C4 if kk < 0 else C1),
             ha="right" if kk < 0 else "left")
ax1.annotate("post-cursor tail", xy=(4, 0.025), xytext=(4.3, 0.3), fontsize=6.8, color=C1,
             arrowprops=dict(arrowstyle="-|>", lw=0.6, color=C1, mutation_scale=6))
ax1.set_xlim(-3, 6.5); ax1.set_ylim(-0.05, 1.12); ax1.set_xticks(range(-3, 7))
finish(ax1, xlabel="Time relative to main cursor, $(t-t_s)/T_b$ (UI)", ylabel="Amplitude (V)",
       legend=True, loc="upper right")
panel(ax1, "a")
stem_cursors(ax2, k, pk)
ax2.set_ylim(-0.03, 0.65)
finish(ax2, xlabel="Cursor index $k$", ylabel="$p_k$ (V)")
panel(ax2, "b")
savefig(fig, "ch02_pulse_cursors")

# ------------------------------------------------------------------ 2) superposition
bits = np.array([1, 0, 1, 1, 0, 0, 0, 1, 0, 1])
a = 2 * bits - 1
nb = bits.size
pre, post = 2, 7                                    # UI of pulse kept before/after main cursor
tt = np.arange(-1.0 * SPS, (nb + 3) * SPS) / SPS    # time in UI; bit n has its main cursor at t = n
y = np.zeros_like(tt)
fig, (axp, axs) = plt.subplots(2, 1, figsize=(6.3, 3.35), sharex=True,
                               gridspec_kw=dict(height_ratios=[1, 1.15]))
for n, an in enumerate(a):
    pn = np.interp(tt - n, tu, p, left=0, right=0)
    y += A * an * pn
    col = C1 if an > 0 else C2
    axp.plot(tt, A * an * pn, color=col, lw=1.0, alpha=0.9)
    axp.plot(n, A * an * pk[list(k).index(0)], "o", color=col, ms=3)
    axp.text(n, 0.37 if an > 0 else -0.37, f"$a_{{{n}}}$={'+1' if an > 0 else chr(8722)+'1'}",
             ha="center", fontsize=6.3, color=col, va="center")
axp.axhline(0, color=MUTED, lw=0.6)
axp.set_ylim(-0.45, 0.45); axp.set_yticks([-0.3, 0, 0.3])
finish(axp, ylabel="$A\\,a_n\\,p(t-nT_b)$ (V)")
panel(axp, "a")
# TX waveform (delay removed: bit n occupies [n-0.5, n+0.5))
txw = np.where((tt >= -0.5) & (tt < nb - 0.5), A * a[np.clip(np.floor(tt + 0.5).astype(int), 0, nb - 1)], 0)
axs.plot(tt, txw, color=MUTED, lw=0.9, ls="--", label="TX symbols $A\\,a_n$")
axs.plot(tt, y, color=NAVY, lw=1.7, label="received $y(t)$ = sum of the pulses in (a)")
axs.axhline(0, color=C4, lw=0.7, ls=":")
ys = np.array([y[np.argmin(np.abs(tt - n))] for n in range(nb)])
for n in range(nb):
    axs.plot(n, ys[n], "o", ms=4.5, mfc=GOLDLT, mec=GOLDDK, zorder=5)
axs.plot([], [], "o", ms=4.5, mfc=GOLDLT, mec=GOLDDK, label="samples at $t_s + nT_b$")
note(axs, (7.05, ys[7]), f"lone 1 after 000:\nonly {1e3*ys[7]:.0f} mV", (9.9, -0.3), color=C4, fs=6.8)
note(axs, (3.05, ys[3]), f"1 after 1: {1e3*ys[3]:.0f} mV", (4.0, 0.36), color=GOLDDK, fs=6.8)
axs.text(nb + 2.9, 0.012, "threshold", fontsize=6.5, color=C4, ha="right", va="bottom")
axs.set_ylim(-0.55, 0.8); axs.set_xlim(-1, nb + 3)
axs.set_xticks(range(0, nb + 3))
axs.legend(loc="upper center", fontsize=6.6, ncol=3, bbox_to_anchor=(0.5, 1.03), handlelength=1.6,
           columnspacing=1.2)
finish(axs, xlabel="Time (UI), main cursor of bit $n$ at $t = n$", ylabel="Voltage (V)")
panel(axs, "b")
print("superposition samples (mV):", np.round(1e3 * ys))
savefig(fig, "ch02_superposition")

# ------------------------------------------------------------------ 3) ISI vs tau/UI (one-pole)
bits7 = np.tile(prbs_bits(7), 24)
x7 = np.repeat(A * (2.0 * bits7 - 1), SPS)
taus = (0.2, 0.5, 1.0)
fig, axs3 = plt.subplots(2, 3, figsize=(6.3, 3.3), gridspec_kw=dict(height_ratios=[0.8, 1.2]))
for j, tau in enumerate(taus):
    r = np.exp(-1 / tau)
    eh_pda = 1 - 2 * r                               # (EH / 2A) for a one-pole channel
    f3 = 1 / (2 * np.pi * tau * UI) / 1e9
    # pulse response (analytic) for a 1 V pulse starting at t=0
    tq = np.linspace(-0.5, 6, 800)
    pp = np.where(tq < 0, 0, np.where(tq < 1, 1 - np.exp(-np.maximum(tq, 0) / tau),
                                        (1 - r) * np.exp(-(tq - 1) / tau)))
    ax = axs3[0, j]
    ax.fill_between(tq, 0, ((tq >= 0) & (tq < 1)).astype(float), color=GTINT, lw=0)
    ax.plot(tq, pp, color=C1, lw=1.4)
    kk = np.arange(1, 7)
    ax.plot(kk, np.where(kk == 1, 1 - r, (1 - r) * r ** (kk - 1)), "o",
            color=C1, ms=3.2, mfc="white")
    ax.plot(1, 1 - r, "o", color=GOLDDK, ms=4)
    ax.set_title(f"τ = {tau:g} UI  ($f_{{3\\mathrm{{dB}}}}$ = {f3:.2f} GHz)", fontsize=7.8)
    ax.set_xlim(-0.5, 6); ax.set_ylim(-0.05, 1.12); ax.set_xticks(range(0, 7))
    ax.set_xlabel("Time (UI)", fontsize=7.5, labelpad=1)
    if j == 0:
        ax.set_ylabel("$p(t)$ (V)")
    panel(ax, "abc"[j])
    # eye
    yv = one_pole(x7, tau)
    # sample instant that maximizes the noise-free opening (search over one UI)
    nb7 = bits7.size
    best = (-9, 0)
    for d in range(0, 2 * SPS):
        idx = np.arange(30, nb7 - 3) * SPS + d
        bb = bits7[30:nb7 - 3]
        op = yv[idx][bb == 1].min() - yv[idx][bb == 0].max()
        if op > best[0]:
            best = (op, d)
    op, d = best
    dc = int(round((tau * np.log(2) + 0.5) * SPS))    # midpoint between crossings
    xo = (d - dc) / SPS                               # best instant relative to display centre
    ax = axs3[1, j]
    eye_density(ax, yv, SPS, phase=dc % SPS, skip_ui=30, vlim=(-0.62, 0.62), vbins=180)
    ax.annotate("", xy=(xo, op / 2), xytext=(xo, -op / 2),
                arrowprops=dict(arrowstyle="<->", color=GOLDDK if j < 2 else C4, lw=1.1,
                                shrinkA=0, shrinkB=0))
    ax.plot(xo, 0, "o", ms=3.5, color=GOLDDK if j < 2 else C4)
    ax.text(xo + 0.06, -0.1, f"EH = {1e3*op:.0f} mV", fontsize=7, color=GOLDDK if j < 2 else C4,
            va="center", ha="left", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    print(f"   best instant {xo:+.2f} UI from eye center")
    ax.set_xlabel("Time (UI)", fontsize=7.5, labelpad=1)
    ax.set_yticks([-0.5, 0, 0.5])
    if j == 0:
        ax.set_ylabel("Voltage (V)")
    else:
        ax.set_yticklabels([])
    print(f"tau={tau}: r={r:.4f}, EH/2A(PDA)={eh_pda:.4f}, eye from PRBS7 = {op*1e3:.1f} mV, f3dB={f3:.2f} GHz")
savefig(fig, "ch02_isi_tau")

# ------------------------------------------------------------------ 4) folding the waveform into an eye
tau = 0.45
yv = one_pole(x7, tau)
# phase: find best sample instant
best = (-9, 0)
for d in range(0, 2 * SPS):
    idx = np.arange(30, bits7.size - 3) * SPS + d
    bb = bits7[30:bits7.size - 3]
    op = yv[idx][bb == 1].min() - yv[idx][bb == 0].max()
    if op > best[0]:
        best = (op, d)
d = int(round((tau * np.log(2) + 0.5) * SPS))   # display centre = midpoint between crossings
start = 40 * SPS + d - SPS                          # window k spans [start + 2k*SPS, start + (2k+2)*SPS]
nwin = 6
cols = [C1, C2, C3, C4, C5, NAVY]
fig, (axa, axb) = plt.subplots(1, 2, figsize=(6.3, 2.15), gridspec_kw=dict(width_ratios=[2.2, 1]))
seg_t = np.arange(nwin * 2 * SPS + 1) / SPS
axa.plot(seg_t, yv[start:start + seg_t.size], color=MUTED, lw=0.5)
for w in range(nwin):
    i_a, i_b = w * 2 * SPS, (w + 1) * 2 * SPS + 1
    axa.axvspan(2 * w, 2 * w + 2, color=cols[w], alpha=0.07, lw=0)
    axa.plot(seg_t[i_a:i_b], yv[start + i_a:start + i_b], color=cols[w], lw=1.4)
    axa.text(2 * w + 1, 0.66, f"window {w+1}", ha="center", fontsize=6.5, color=cols[w])
    axa.axvline(2 * w, color=PALE, lw=0.6)
axa.set_xlim(0, 2 * nwin); axa.set_ylim(-0.7, 0.75); axa.set_xticks(range(0, 13, 2))
finish(axa, xlabel="Time (UI)", ylabel="Voltage (V)")
panel(axa, "a")
eye_lines(axb, yv, SPS, phase=d % SPS, skip_ui=30, ntraces=600, color=PALE, alpha=0.25, lw=0.5)
tt2 = np.arange(2 * SPS + 1) / SPS - 1
for w in range(nwin):
    axb.plot(tt2, yv[start + w * 2 * SPS:start + w * 2 * SPS + 2 * SPS + 1], color=cols[w], lw=1.3)
axb.set_ylim(-0.7, 0.75); axb.set_yticklabels([])
axb.set_xlabel("Time (UI)")
panel(axb, "b")
savefig(fig, "ch02_eye_fold")

# ------------------------------------------------------------------ 5) eye anatomy
rj_ui, sig_n = 0.03, 0.015
bitsA = np.tile(prbs_bits(7), 40)
nbA = bitsA.size
lev = A * (2.0 * bitsA - 1)
# TX waveform with Gaussian edge jitter placed at sub-sample resolution (area-correct ramps)
xA = np.repeat(lev, SPS).astype(float)
edges = np.nonzero(np.diff(bitsA))[0] + 1
for e in edges:
    te = (e + rng.normal(0, rj_ui)) * SPS          # edge position in samples
    i = int(np.floor(te)); fr = te - i
    lo, hi = lev[e - 1], lev[e]
    if i >= e * SPS:
        xA[e * SPS:i] = lo
    else:
        xA[i + 1:e * SPS] = hi
    xA[i] = lo * fr + hi * (1 - fr)
tg = np.arange(-4 * SPS, 4 * SPS + 1) / SPS       # symmetric (Gaussian) band-limited channel
hA = np.exp(-0.5 * (tg / 0.32) ** 2); hA /= hA.sum()
yA = np.convolve(xA, hA, mode="same")
nz = lfilter([1 - np.exp(-1 / (0.15 * SPS))], [1, -np.exp(-1 / (0.15 * SPS))], rng.normal(0, 1, yA.size))
yA = yA + sig_n * nz / np.std(nz)
sk = 60 * SPS
zc = np.nonzero(np.diff(np.sign(yA[sk:])))[0] + sk
ph_z = 2 * np.pi * (zc % SPS) / SPS
cph = (np.angle(np.mean(np.exp(1j * ph_z))) % (2 * np.pi)) / (2 * np.pi) * SPS
phase = int(round(cph + SPS / 2)) % SPS             # eye center = crossing + UI/2
cross_dev = (((zc - cph) / SPS + 0.5) % 1.0) - 0.5  # crossing deviation from nominal (UI)
def samples_at(off):
    i = np.arange(sk // SPS + 5, nbA - 20) * SPS + phase + off
    return yA[i]
def opening(off):
    v = samples_at(off); bb = v > 0
    return np.percentile(v[bb], 0.1) - np.percentile(v[~bb], 99.9), v, bb
ops = {o: opening(o)[0] for o in range(-12, 13)}
off = max(ops, key=ops.get); EH, samp, bb = opening(off)
xo = off / SPS
sj = np.std(cross_dev)
print(f"anatomy: EH = {EH*1e3:.0f} mV at {xo:+.3f} UI, crossing sigma = {sj:.3f} UI")
fig = plt.figure(figsize=(6.3, 3.45))
gs = fig.add_gridspec(2, 2, width_ratios=[4.2, 1], height_ratios=[3.2, 0.8], wspace=0.04, hspace=0.06)
ax = fig.add_subplot(gs[0, 0]); axr = fig.add_subplot(gs[0, 1], sharey=ax)
axj = fig.add_subplot(gs[1, 0], sharex=ax)
eye_density(ax, yA, SPS, phase=phase, skip_ui=60, vlim=(-0.6, 0.6), vbins=240, gamma=0.5)
ax.set_ylim(-0.86, 0.86)
ax.set_xlabel("")
plt.setp(ax.get_xticklabels(), visible=False)
# eye height
ax.annotate("", xy=(xo, EH / 2), xytext=(xo, -EH / 2),
            arrowprops=dict(arrowstyle="<->", color=GOLDDK, lw=1.3, shrinkA=0, shrinkB=0))
ax.text(xo + 0.05, 0.1, f"eye height\nEH ≈ {EH*1e3:.0f} mV", color=NAVY, fontsize=7.3,
        fontweight="bold", ha="left", va="bottom",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=GOLD, lw=0.6, alpha=0.92))
# eye width
xl, xr = -0.5 + np.percentile(cross_dev, 99.9), 0.5 + np.percentile(cross_dev, 0.1)
ax.annotate("", xy=(xl, 0), xytext=(xr, 0),
            arrowprops=dict(arrowstyle="<->", color=GOLDDK, lw=1.3, shrinkA=0, shrinkB=0))
ax.text(-0.27, -0.08, f"eye width\nEW ≈ {xr-xl:.2f} UI", color=NAVY, fontsize=7.3, fontweight="bold",
        ha="center", va="top", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=GOLD, lw=0.6, alpha=0.92))
# optimal sampling point
ax.plot(xo, 0, marker="*", ms=11, mfc=GOLDLT, mec=NAVY, mew=0.8, zorder=6)
note(ax, (xo + 0.02, -0.02), "optimal sampling point ($t_s$, threshold)", (0.08, -0.74), color=NAVY, fs=7)
# crossings
for xc in (-0.5, 0.5):
    ax.plot(xc, 0, "o", ms=9, mfc="none", mec=C4, mew=1.1, zorder=6)
note(ax, (0.52, 0.03), "crossing point", (0.6, 0.74), color=C4, fs=7)
# slope at the crossing (rising edge through (-0.5, 0)): dV/dt of the mean rising edge
ii = np.arange(sk // SPS + 5, nbA - 20) * SPS + phase - SPS // 2      # samples at the crossing
dv = (yA[ii + 2] - yA[ii - 2]) / (4 / SPS)
slope = np.median(dv[dv > 0])                       # V per UI of the rising edges at the crossing
print(f"  slope at crossing = {slope:.2f} V/UI = {slope/200*1e3:.2f} mV/ps")
xs = np.array([-0.6, -0.4])
ax.plot(xs, slope * (xs + 0.5), color=C2, lw=1.6, zorder=6)
note(ax, (-0.42, slope * 0.08), "slope dV/dt at the crossing: timing sensitivity", (-0.97, 0.74), color=C2, fs=7)
# levels
ax.set_ylabel("Voltage (V)"); ax.set_xlim(-1, 1); ax.set_yticks([-0.5, -0.25, 0, 0.25, 0.5])
# right marginal: voltage histogram at t_s
hb = np.linspace(-0.6, 0.6, 120)
axr.hist(samp[bb == 1], bins=hb, orientation="horizontal", color=C1, alpha=0.8)
axr.hist(samp[bb == 0], bins=hb, orientation="horizontal", color=C2, alpha=0.8)
axr.axhline(0, color=C4, lw=0.7, ls=":")
axr.text(0.5, 0.0, "noise + ISI:\nspread of\nlevels at $t_s$", transform=axr.get_yaxis_transform(),
         fontsize=6.5, color=NAVY, ha="center", va="center",
         bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="none"))
axr.text(0.97, 0.47, "‘1’", transform=axr.get_yaxis_transform(), fontsize=7, color=C1, ha="right")
axr.text(0.97, -0.47, "‘0’", transform=axr.get_yaxis_transform(), fontsize=7, color=C2,
         ha="right", va="top")
plt.setp(axr.get_yticklabels(), visible=False); axr.set_xticks([]); axr.grid(False)
axr.spines["left"].set_visible(False); axr.tick_params(axis="y", length=0)
# bottom marginal: crossing-time histogram
cr_abs = np.concatenate([cross_dev - 0.5, cross_dev + 0.5])
cr_abs = cr_abs[(cr_abs > -1) & (cr_abs < 1)]
axj.hist(cr_abs, bins=np.linspace(-1, 1, 161), color=C4, alpha=0.85)
axj.text(0.0, 0.45, "jitter: spread of crossing times", transform=axj.get_xaxis_transform(),
         fontsize=6.8, color=C4, ha="center")
axj.set_yticks([]); axj.grid(False); axj.spines["left"].set_visible(False)
axj.set_xlabel("Time relative to the eye center (UI)")
savefig(fig, "ch02_eye_anatomy")

# ------------------------------------------------------------------ 6) BER: Gaussian tails and BER vs SNR
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.3), gridspec_kw=dict(width_ratios=[1.15, 1]))
V, s = 1.0, 0.42
v = np.linspace(-2.4, 2.4, 800)
g1, g0 = norm.pdf(v, V, s), norm.pdf(v, -V, s)
ax1.plot(v, g0, color=C2, label="received ‘0’")
ax1.plot(v, g1, color=C1, label="received ‘1’")
ax1.fill_between(v, 0, g1, where=v < 0, color=C1, alpha=0.45)
ax1.fill_between(v, 0, g0, where=v > 0, color=C2, alpha=0.45)
ax1.axvline(0, color=C4, lw=0.9, ls="--")
ax1.text(0.05, 1.2, "threshold", color=C4, fontsize=6.8)
ax1.annotate("", xy=(0, 1.05), xytext=(V, 1.05), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=0.8))
ax1.text(V / 2, 1.1, "EH/2", fontsize=7, color=NAVY, ha="center")
ax1.annotate("", xy=(V, norm.pdf(s, 0, s) * 1), xytext=(V + s, norm.pdf(s, 0, s)),
             arrowprops=dict(arrowstyle="<->", color=NAVY, lw=0.7, shrinkA=0, shrinkB=0))
ax1.text(V + s + 0.05, norm.pdf(s, 0, s), "$\\sigma_n$", fontsize=7.5, color=NAVY, va="center")
note(ax1, (-0.17, 0.035), "P(error | 1)", (-2.3, 0.5), color=C1, fs=6.8)
note(ax1, (0.17, 0.035), "P(error | 0)", (1.45, 0.5), color=C2, fs=6.8)
ax1.set_xticks([-V, 0, V]); ax1.set_xticklabels(["−EH/2", "0", "+EH/2"])
ax1.set_ylim(0, 1.3); ax1.set_yticks([])
finish(ax1, xlabel="Sampled voltage at $t_s$", ylabel="Probability density", legend=True, loc="upper left")
panel(ax1, "a")
snr_db = np.linspace(6, 20, 400)
Q = 10 ** (snr_db / 20)
ax2.semilogy(snr_db, norm.sf(Q), color=C1)
for ber, c in ((1e-3, MUTED), (1e-6, MUTED), (1e-9, MUTED), (1e-12, GOLDDK), (1e-15, MUTED)):
    q = norm.isf(ber); sd = 20 * np.log10(q)
    ax2.plot(sd, ber, "o", color=c, ms=4 if c != GOLDDK else 5.5, zorder=5)
    ax2.text(sd - 0.25, ber * 0.25 if ber > 1e-14 else ber * 0.15, f"Q = {q:.2f}", fontsize=6.4,
             color=c, ha="right", va="top")
ax2.axhline(1e-12, color=GOLD, lw=0.8, ls="--")
ax2.text(6.2, 2e-12, "target BER 10$^{-12}$: Q = 7.03, SNR = 16.9 dB", fontsize=6.8, color=GOLDDK,
         va="bottom")
ax2.set_ylim(1e-17, 1); ax2.set_xlim(6, 20)
ax2.set_yticks([1, 1e-3, 1e-6, 1e-9, 1e-12, 1e-15])
finish(ax2, xlabel="SNR = $20\\log_{10}(\\mathrm{EH}/2\\sigma_n)$ (dB)", ylabel="BER")
panel(ax2, "b")
savefig(fig, "ch02_ber")
for ber in (1e-3, 1e-6, 1e-9, 1e-10, 1e-12, 1e-15):
    q = norm.isf(ber); print(f"BER {ber:.0e}: Q = {q:.3f}, 2Q = {2*q:.2f}, SNR = {20*np.log10(q):.2f} dB")

# ------------------------------------------------------------------ 7) bathtub teaser
fig, ax = plt.subplots(figsize=HALF)
xs = np.linspace(0, 1, 801)
for sj, col in ((0.02, C1), (0.04, C2)):
    ber = 0.5 * (norm.sf(xs / sj) + norm.sf((1 - xs) / sj))
    ax.semilogy(xs, np.maximum(ber, 1e-20), color=col, label=f"$\\sigma_j$ = {sj:g} UI ({sj*200:.0f} ps)")
    ok = xs[ber < 1e-12]
    print(f"bathtub sigma_j={sj}: opening at 1e-12 = {ok.max()-ok.min():.3f} UI")
    ax.annotate("", xy=(ok.min(), 1e-12), xytext=(ok.max(), 1e-12),
                arrowprops=dict(arrowstyle="<->", color=col, lw=0.8, shrinkA=0, shrinkB=0))
    ax.text(0.5, 1e-12 * (3e2 if sj == 0.02 else 3e-4), f"{ok.max()-ok.min():.2f} UI", color=col,
            fontsize=6.8, ha="center", va="center")
ax.axhline(1e-12, color=GOLD, lw=0.7, ls="--")
ax.set_ylim(1e-16, 1); ax.set_xlim(0, 1)
ax.set_yticks([1, 1e-4, 1e-8, 1e-12, 1e-16])
finish(ax, xlabel="Sampling instant within the UI (UI)", ylabel="BER", legend=True, loc="upper center")
ax.legend(loc="upper center", fontsize=6.3, bbox_to_anchor=(0.5, 1.02))
savefig(fig, "ch02_bathtub")
