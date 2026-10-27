"""ch04_budget.py -- Chapter 4 margin waterfall (Section 4.4) and NRZ vs PAM4 (Section 4.5).
Prints the numbers used in the worked examples and tab:ch4-pam4.

Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch04_budget.py
"""
from bricdstyle import *
from link import *
from ch04_stateye import ffe_pulse, stat_eye, eye_metrics, FFE2
from scipy.ndimage import gaussian_filter1d

Q12 = 7.034
SIG, RJ, DJ = 1.5e-3, 2e-12, 20e-12        # assumptions stated in the text
VOS, VSENS = 5e-3, 20e-3

H = channel(REF_LEN)
t, p = pulse_of(H)
i0 = int(np.argmax(p))
q = ffe_pulse(p, FFE2)
j0 = int(np.argmax(q))
kw = dict(span_ui=0.3, vout=np.linspace(-0.2, 0.2, 1601))
eh_isi = eye_metrics(stat_eye(q, j0, **kw), 1e-12)[0]
eh_n = eye_metrics(stat_eye(q, j0, sigma_n=SIG, **kw), 1e-12)[0]
eh_nj = eye_metrics(stat_eye(q, j0, sigma_n=SIG, rj=RJ, dj=DJ, **kw), 1e-12)[0]
steps = [("TX swing\n2A", 2 * A_TX),
         ("channel\nloss", 2 * A_TX * p[i0]),
         ("FFE\nde-emph.", 2 * A_TX * q[j0]),
         ("residual\nISI", eh_isi),
         ("RX noise\n2Qσn", eh_isi - 2 * Q12 * SIG),
         ("jitter", eh_isi - 2 * Q12 * SIG - (eh_n - eh_nj)),
         ("offset\n2Vos", eh_isi - 2 * Q12 * SIG - (eh_n - eh_nj) - 2 * VOS),
         ("sampler\nsens.", eh_isi - 2 * Q12 * SIG - (eh_n - eh_nj) - 2 * VOS - VSENS)]
print("levels (mV):", [(s.replace(chr(10), ' '), round(v * 1e3, 1)) for s, v in steps])
print(f"stat EH 1e-12: ISI {eh_isi*1e3:.1f}, +noise {eh_n*1e3:.1f}, +noise+jitter {eh_nj*1e3:.1f} mV;"
      f" jitter cost {1e3*(eh_n-eh_nj):.1f} mV; noise cost (stat) {1e3*(eh_isi-eh_n):.1f} vs linear {2*Q12*SIG*1e3:.1f}")
stat_margin = eh_nj - 2 * VOS - VSENS
print(f"linear margin {steps[-1][1]*1e3:.1f} mV; statistical margin {stat_margin*1e3:.1f} mV")

# ---------------------------------------------------------------- waterfall
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.6), gridspec_kw=dict(width_ratios=[1, 2.5]))
def bars(ax, items, prev0, first_solid=True):
    prev = prev0
    for x, (lab, lev) in enumerate(items):
        if x == 0 and first_solid:
            ax.bar(x, lev * 1e3, width=0.62, color=C1, zorder=2)
            ax.text(x, lev * 1e3, f"{lev*1e3:.0f}", ha="center", va="bottom", fontsize=6.8, color=NAVY)
        else:
            ax.bar(x, (prev - lev) * 1e3, bottom=lev * 1e3, width=0.62, color=C4, alpha=0.8, zorder=2)
            ax.text(x, prev * 1e3, f"−{(prev-lev)*1e3:.0f}", ha="center", va="bottom", fontsize=6.8, color=C4)
            ax.plot([x - 1.31, x + 0.31], [prev * 1e3] * 2, color=MUTED, lw=0.6, ls=":", zorder=1)
        prev = lev
    ax.set_xticks(range(len(items))); ax.set_xticklabels([s for s, _ in items], fontsize=6.6)
    ax.grid(False, axis="x")
    return prev
bars(ax1, steps[:3], steps[0][1])
ax1.bar(3, steps[2][1] * 1e3, width=0.62, color=C1, alpha=0.55, zorder=2)
ax1.set_xticks(range(4)); ax1.set_xticklabels([s for s, _ in steps[:3]] + ["main\ncursor"], fontsize=6.6)
ax1.set_ylim(0, 1100)
finish(ax1, None, "Eye budget (mV)")
panel(ax1, "a")
items = [("main cursor\n2A·$q_0$", steps[2][1])] + steps[3:]
last = bars(ax2, items, steps[2][1])
n = len(items)
ax2.bar(n, last * 1e3, width=0.62, color=C3, zorder=2)
ax2.text(n, last * 1e3, f"{last*1e3:.0f}", ha="center", va="bottom", fontsize=7, color=C3, fontweight="bold")
ax2.axhline(stat_margin * 1e3, color=C3, lw=0.9, ls="--")
ax2.text(2.5, stat_margin * 1e3 - 5, f"statistical combination: margin {stat_margin*1e3:.0f} mV",
         fontsize=6.6, color=C3, ha="center", va="top")
ax2.set_xticks(range(n + 1)); ax2.set_xticklabels([s for s, _ in items] + ["margin"], fontsize=6.6)
ax2.set_xlim(-0.5, n + 0.5); ax2.set_ylim(0, 240)
finish(ax2, None, "mV")
panel(ax2, "b")
savefig(fig, "ch04_waterfall")

# ---------------------------------------------------------------- NRZ vs PAM4
Ls = np.linspace(0.05, 2.0, 40)
il25 = np.array([-loss_db(channel(L)) for L in Ls])
il125 = np.array([-loss_db(channel(L), 1.25e9) for L in Ls])
dl = il25 - il125
from scipy.interpolate import interp1d
Lx = brentq(lambda L: interp1d(Ls, dl, kind="cubic")(L) - 20 * np.log10(3), 0.3, 1.9)
ILx = float(interp1d(Ls, il25, kind="cubic")(Lx))
print(f"PAM4 crossover: L = {Lx:.3f} m, IL(2.5 GHz) = {ILx:.1f} dB; 20log10(3) = {20*np.log10(3):.2f} dB")
rows = [("REF", REF_LEN)] + [(f"{d} dB", LOSS_FAMILY[d]) for d in (5, 10, 15, 20, 25, 30)]
for name, L in rows:
    Hl = channel(L)
    a, b = -loss_db(Hl), -loss_db(Hl, 1.25e9)
    print(f"{name:6s} L={L:.3f} m: IL(2.5)={a:.2f} IL(1.25)={b:.2f} diff={a-b:.2f} -> {'PAM4?' if a-b > 9.54 else 'NRZ'}")

fig = plt.figure(figsize=(6.3, 2.6))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 2.3])
rng = np.random.default_rng(7)
for col, (lv, name, nsym) in enumerate(((np.array([-1, 1]), "NRZ, 5 Gb/s", 2), (np.array([-1, -1/3, 1/3, 1]), "PAM4, 2.5 GBd", 4))):
    ax = fig.add_subplot(gs[0, col])
    sym = lv[rng.integers(0, nsym, 600)] * A_TX
    sps = 32
    w = gaussian_filter1d(np.repeat(sym, sps), sps * 0.22, mode="wrap")
    eye_lines(ax, w, sps, phase=sps // 2, ntraces=300, alpha=0.08, color=NAVY)
    eh = 2 * A_TX / (nsym - 1)
    ax.annotate("", xy=(0, A_TX), xytext=(0, A_TX - eh), arrowprops=dict(arrowstyle="<->", lw=0.8, color=C4, mutation_scale=6))
    ax.text(0.07, A_TX - eh / 2, "2A" if nsym == 2 else "2A/3", fontsize=7, color=C4, va="center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    ax.set_ylim(-0.62, 0.62); ax.set_title(name, fontsize=7.5)
    ax.set_xlabel("Time (UI of its own)", fontsize=7)
    if col == 0:
        ax.set_ylabel("Voltage (V)")
    else:
        ax.set_yticklabels([])
    panel(ax, "ab"[col])
ax = fig.add_subplot(gs[0, 2])
ax.plot(Ls, il25, color=C1, lw=1.5, label="IL at 2.5 GHz (NRZ $f_N$)")
ax.plot(Ls, il125, color=C2, lw=1.5, label="IL at 1.25 GHz (PAM4 $f_N$)")
ax.plot(Ls, dl, color=NAVY, lw=1.6, ls="--", label="difference Δ")
ax.axhline(20 * np.log10(3), color=C4, lw=0.9, ls=":")
ax.text(0.03, 20 * np.log10(3) + 0.5, "9.54 dB", fontsize=6.6, color=C4, ha="left", va="bottom")
ax.fill_between(Ls, 0, dl, where=dl > 20 * np.log10(3), color=C4, alpha=0.12, lw=0)
ax.axvline(Lx, color=C4, lw=0.7, ls=":")
ax.text(Lx + 0.04, 0.8, f"PAM4 favored\nbeyond {Lx:.2f} m\n({ILx:.1f} dB at 2.5 GHz)", fontsize=6.3, color=C4, va="bottom", ha="left")
ax.plot(REF_LEN, -loss_db(H) + loss_db(H, 1.25e9), "o", color=GOLD, ms=5, zorder=5)
note(ax, (REF_LEN, -loss_db(H) + loss_db(H, 1.25e9)), f"REF: Δ = {-loss_db(H)+loss_db(H,1.25e9):.1f} dB", (0.08, 17.5), color=GOLDDK)
ax.set_xlim(0, 2.0); ax.set_ylim(0, 35)
finish(ax, "FR-4 line length (m)", "Loss (dB)")
ax.legend(loc="upper left", fontsize=6.4)
panel(ax, "c")
savefig(fig, "ch04_pam4")
