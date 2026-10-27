"""ch14_budget.py -- the voltage and timing budgets of Chapters 4 and 11 side by side (Chapter 14)."""
from bricdstyle import *

# voltage: REF + 2-tap de-emphasis, statistical eye at 1e-12 = 131 mV (Ch. 4, linear budget)
V = [("noise $2Q\\sigma_n$", 14.07 * 1.5, C4), ("jitter", 3.5, C5), ("offset $2V_{os}$", 10.0, C2),
     ("sensitivity", 20.0, GOLDDK)]
EH = 131.0
mV = EH - sum(v for _, v, _ in V)
# timing: UI = 200 ps; DJ terms (Ch. 11) and 2Q*RJ
T = [("TX DCD/DDJ", 8, C2), ("residual ISI", 6, C3), ("RX clock path", 6, C5), ("CDR dither", 20, GOLDDK),
     ("RJ $\\times 2Q$", 14.07 * np.sqrt(1.0**2 + 0.7**2 + 0.5**2), C4)]
mT = 200 - sum(v for _, v, _ in T)
print(f"voltage margin {mV:.1f} mV; timing eye {mT:.1f} ps (TJ {200-mT:.1f} ps)")

fig, (a, b) = plt.subplots(2, 1, figsize=(6.3, 2.1))
for ax, items, total, rest, unit, lab in ((a, V, EH, mV, "mV", "margin"), (b, T, 200, mT, "ps", "open eye at $10^{-12}$")):
    x0 = 0
    for name, v, c in items:
        ax.barh(0, v, left=x0, color=c, height=0.55, edgecolor="white", lw=0.8)
        if v > 0.07 * total:
            ax.text(x0 + v / 2, 0, f"{v:.1f}", ha="center", va="center", fontsize=6.8, color="white")
        ax.barh([], [], color=c, label=name)
        x0 += v
    ax.barh(0, rest, left=x0, color=BTINT, height=0.55, edgecolor=C1, lw=0.8)
    ax.text(x0 + rest / 2, 0, f"{lab}: {rest:.1f} {unit}", ha="center", va="center", fontsize=7.2,
            color=NAVY, fontweight="bold")
    ax.set_xlim(0, total); ax.set_ylim(-0.4, 0.4); ax.set_yticks([])
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=n) for n, _, c in items], ncol=len(items), loc="lower left",
              bbox_to_anchor=(0.0, 0.93), fontsize=6.6, handlelength=1.0, columnspacing=1.0, borderaxespad=0)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
finish(a, f"Voltage (mV) out of the {EH:.0f} mV statistical eye of REF + 2-tap de-emphasis")
finish(b, "Time (ps) out of one 200 ps UI")
panel(a, "a", x=-0.01, y=0.93); panel(b, "b", x=-0.01, y=0.93)
savefig(fig, "ch14_budget")
