"""ch04_pda.py -- Chapter 4 peak-distortion figures and the PDA-vs-PRBS-vs-statistical comparison.
Prints every number used in Section 4.2 (PDA, worst-case pattern, PRBS eyes).

Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch04_pda.py
"""
from bricdstyle import *
from link import *
from ch04_stateye import ffe_pulse, isi_pdf, FFE2

H = channel(REF_LEN)
t, p = pulse_of(H)
i0 = int(np.argmax(p))
k, pk, _ = cursors(p)                       # k = -2..10
print("PDA (13 cursors) =", round(pda_eye(pk, k), 4), "V")
kf, pkf, _ = cursors(p, n_pre=3, n_post=300)
print("PDA (k=-3..300)  =", round(pda_eye(pkf, kf), 4), "V; sum|p_k| k!=0 =",
      round(np.sum(np.abs(pkf)) - pkf[3], 4), "; H(0) =", round(np.sum(p) / SPS, 4))
cum_order = [kk for kk in k if kk != 0]
cum = np.cumsum([abs(pk[list(k).index(kk)]) for kk in cum_order])
print("cumulative ISI:", dict(zip(cum_order, np.round(cum, 4))))
pattern = {kk: (-int(np.sign(v)) if abs(v) > 1e-3 else 0) for kk, v in zip(k, pk) if kk != 0}
print("worst-case d_{n-k} for d_n=+1 (0 = don't care):", pattern)

# ---------------------------------------------------------------- Fig: PDA bars + worst-case waveform
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.6), gridspec_kw=dict(width_ratios=[1, 1.1]))
for kk, v in zip(k, pk):
    col = GOLD if kk == 0 else (C4 if kk < 0 else C1)
    ax1.bar(kk, abs(v), width=0.62, color=col, alpha=0.9 if kk == 0 else 0.75, zorder=2)
xs = np.array(cum_order, float)
ax1.plot(xs, cum, "o-", color=NAVY, lw=1.2, ms=2.8, zorder=4, label=r"cumulative ISI $\sum|p_k|$, $k\neq0$")
ax1.axhline(pk[2], color=GOLDDK, lw=0.9, ls="--", zorder=1)
ax1.text(10.4, pk[2] + 0.012, f"$p_0$ = {pk[2]:.3f}", color=GOLDDK, fontsize=7, ha="right")
icross = int(np.argmax(cum > pk[2]))
note(ax1, (xs[icross], cum[icross]), f"ISI exceeds $p_0$\nat $k$ = {int(xs[icross])}", (4.6, 0.20), color=NAVY)
ax1.text(10.4, cum[-1] + 0.02, f"{cum[-1]:.3f} by $k$ = 10\n(full tail: {np.sum(np.abs(pkf))-pkf[3]:.3f})",
         fontsize=6.8, color=NAVY, ha="right", va="bottom")
ax1.set_xlim(-2.6, 10.6); ax1.set_ylim(0, 0.72)
ax1.set_xticks(k); ax1.set_xticklabels([f"{kk:+d}" if kk else "0" for kk in k], fontsize=6.8)
finish(ax1, "Cursor index $k$", "|$p_k$| (V)")
ax1.legend(loc="upper left", fontsize=6.8)
panel(ax1, "a")
# (b) worst-case pattern: a lone 1 after a long run of 0s, followed by a 0
nb = 200
a = -np.ones(nb); n0 = 150; a[n0] = 1
y = np.zeros(nb * SPS + p.size)
for m in range(nb):
    y[m * SPS:m * SPS + p.size] += A_TX * a[m] * p
tx = np.repeat(A_TX * a, SPS)
ts_idx = n0 * SPS + i0
delay = i0 - SPS // 2
win = np.arange(ts_idx - 7 * SPS, ts_idx + 4 * SPS)
tu = (win - ts_idx) / SPS
ax2.plot(tu, tx[win - delay], color=PALE, lw=1.3, label="TX bits (shifted by the delay)")
ax2.plot(tu, y[win], color=NAVY, lw=1.6, label="RX waveform")
ax2.axhline(0, color=MUTED, lw=0.7, ls=":")
ax2.plot(0, y[ts_idx], "o", color=C4, ms=5, zorder=5)
print(f"worst-case '1' sample = {y[ts_idx]*1e3:.1f} mV (A(2p0 - H(0)) = {A_TX*(2*pk[2]-np.sum(p)/SPS)*1e3:.1f} mV)")
note(ax2, (0, y[ts_idx]), f"'1' sampled at {y[ts_idx]*1e3:.0f} mV:\nbelow threshold, an error", (0.75, 0.25), color=C4)
for m in range(-6, 4):
    ax2.text(m + 0.0, 0.56, "1" if m == 0 else "0", ha="center", fontsize=7,
             color=GOLDDK if m == 0 else MUTED, fontweight="bold" if m == 0 else "normal")
ax2.set_xlim(-6.6, 3.6); ax2.set_ylim(-0.6, 0.66)
finish(ax2, "Time from the sampling instant (UI)", "Voltage (V)")
ax2.legend(loc="upper left", fontsize=6.4, bbox_to_anchor=(0.0, 0.9))
panel(ax2, "b")
savefig(fig, "ch04_pda")

# ---------------------------------------------------------------- PRBS eyes vs PDA vs statistical
def eh_vs_phase(pp, idx, offs, targets=(1e-6, 1e-12), dv=0.05e-3):
    ks = np.array([kk for kk in range(-3, 151) if kk != 0])
    out = {"pda13": [], "pda": []}
    for tg in targets:
        out[tg] = []
    ks13 = np.array([kk for kk in range(-2, 11) if kk != 0])
    for o in offs:
        c0 = pp[idx + o]
        ck = pp[idx + o + ks * SPS]
        out["pda"].append(2 * A_TX * (c0 - np.sum(np.abs(ck))))
        out["pda13"].append(2 * A_TX * (c0 - np.sum(np.abs(pp[idx + o + ks13 * SPS]))))
        vmax = A_TX * np.sum(np.abs(ck)) * 1.2 + 0.01
        v = np.arange(-vmax, vmax + dv / 2, dv)
        cdf = np.cumsum(isi_pdf(ck, A_TX, v))
        for tg in targets:
            out[tg].append(2 * (A_TX * c0 + np.interp(tg, cdf, v)))
    return {kk: np.array(vv) for kk, vv in out.items()}


q = ffe_pulse(p, FFE2)
j0 = int(np.argmax(q))
offs = np.arange(-30, 31, 2)
res = {}
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.6), sharex=True)
for ax, (name, pp, idx, fir, lab) in zip(axs, (("REF", p, i0, None, "REF, no equalization"),
                                              ("FFE", q, j0, FFE2, "REF + 2-tap TX FFE"))):
    r = eh_vs_phase(pp, idx, offs)
    res[name] = r
    for order, col, ls in ((7, C2, "-"), (13, C3, "-")):
        bits = prbs_bits(order)
        bits = np.tile(bits, max(2, int(np.ceil(6000 / bits.size))))
        yy = rx_wave(bits, H, fir=fir)
        hts, ph, _, _ = eye_scan(yy, bits)
        ph_off = (np.arange(SPS) - (idx % SPS) + SPS // 2) % SPS - SPS // 2
        o_ = np.argsort(ph_off)
        o_ = o_[np.abs(ph_off[o_]) <= 26]
        ax.plot(ph_off[o_] / SPS, hts[o_] * 1e3, color=col, lw=1.2, ls=ls, label=f"PRBS{order} simulation")
        print(f"{name} PRBS{order} ({bits.size} bits): best eye {hts.max()*1e3:.1f} mV, width {np.sum(hts>0)/SPS:.2f} UI")
        res[name][f"prbs{order}"] = hts.max()
    ax.plot(offs / SPS, r[1e-6] * 1e3, color=C5, lw=1.1, ls="--", label="statistical, 1e-6")
    ax.plot(offs / SPS, r[1e-12] * 1e3, color=C1, lw=1.3, ls="--", label="statistical, 1e-12")
    ax.plot(offs / SPS, r["pda"] * 1e3, color=C4, lw=1.6, label="PDA, full tail")
    if name == "REF":
        ax.plot(offs / SPS, r["pda13"] * 1e3, color=C4, lw=0.9, ls=":", label="PDA, 13 cursors only")
    ax.axhline(0, color=MUTED, lw=0.7)
    ax.set_title(lab, fontsize=8)
    ib = int(np.argmax(r["pda"]))
    print(f"{name}: PDA full {r['pda'].max()*1e3:.1f} mV at {offs[ib]/SPS:+.3f} UI, PDA13 {r['pda13'].max()*1e3:.1f},"
          f" stat1e-6 {r[1e-6].max()*1e3:.1f}, stat1e-12 {r[1e-12].max()*1e3:.1f} mV;"
          f" PDA width {np.sum(r['pda']>0)*(offs[1]-offs[0])/SPS:.3f} UI, stat12 width {np.sum(r[1e-12]>0)*(offs[1]-offs[0])/SPS:.3f} UI")
axs[0].set_ylim(-320, 20); axs[1].set_ylim(-20, 190)
finish(axs[0], "Sampling phase from pulse peak (UI)", "Inner eye height (mV)")
finish(axs[1], "Sampling phase from pulse peak (UI)")
hd, lb = axs[0].get_legend_handles_labels()
fig.legend(hd, lb, loc="outside upper center", ncol=3, fontsize=6.8)
panel(axs[0], "a"); panel(axs[1], "b")
savefig(fig, "ch04_pda_prbs")
