"""ch01_figs.py -- Chapter 1 plots: per-lane rate vs year, and the speed ladder."""
from bricdstyle import *
from matplotlib.lines import Line2D

# ------------------------------------------------------------------ 1) rate vs year
# (year, Gb/s per lane, label, modulation, label-x, label-y, ha)   NRZ = circle, PAM4/PAM3 = square
pcie = [(2003, 2.5, "1.0a", "NRZ", 2003.4, 2.1, "left"), (2007, 5, "2.0", "NRZ", 2006.6, 6.3, "right"),
        (2010, 8, "3.0", "NRZ", 2010.4, 6.6, "left"), (2017, 16, "4.0", "NRZ", 2017.4, 13.0, "left"),
        (2019, 32, "5.0", "NRZ", 2019.4, 34, "left"), (2022, 64, "6.0", "PAM", 2022.4, 55, "left"),
        (2025, 128, "7.0", "PAM", 2025.4, 108, "left")]
eth = [(2007, 10.3125, "10GBASE-KR", "NRZ", 2006.6, 12.5, "right"),
       (2014, 25.78125, "100GBASE-KR4", "NRZ", 2013.6, 31, "right"),
       (2018, 53.125, "50GBASE-KR", "PAM", 2017.6, 64, "right"),
       (2022, 106.25, "100GBASE-KR1", "PAM", 2021.6, 128, "right"),
       (2026, 212.5, "802.3dj", "PAM", 2025.6, 255, "right")]
usb = [(2000, 0.48, "USB 2.0", "NRZ", 2000.4, 0.48, "left"), (2008, 5, "3.0", "NRZ", 2008.4, 4.1, "left"),
       (2013, 10, "3.1", "NRZ", 2013.4, 8.5, "left"), (2019, 20, "USB4", "NRZ", 2019.4, 17, "left"),
       (2022, 40, "USB4 v2", "PAM", 2022.4, 34, "left")]
cb = (2018, 5.15625)

fig, ax = plt.subplots(figsize=(6.3, 2.65))
ax.axhspan(4.6, 5.45, color=GTINT, zorder=0)
ax.axhline(5, color=GOLD, lw=1.0, ls="--", zorder=1)
ax.text(2010.6, 4.25, "Open-SERDES target: 5 Gb/s NRZ", color=GOLDDK, fontsize=7.5, va="top",
        fontweight="bold")
for data, col in ((pcie, C1), (eth, C3), (usb, C5)):
    ax.plot([d[0] for d in data], [d[1] for d in data], color=col, lw=1.0, alpha=0.55, zorder=2)
    for (y, v, lab, mod, lx, ly, ha) in data:
        mk = "o" if mod == "NRZ" else "s"
        fc = "white" if lab == "802.3dj" else col
        ax.plot(y, v, mk, color=col, mfc=fc, ms=5, zorder=3)
        ax.text(lx, ly, lab, color=col, fontsize=6.5, ha=ha, va="center")
ax.plot(cb[0], cb[1], "D", color=GOLDDK, ms=5, zorder=4)
note(ax, cb, "802.3cb 5GBASE-KR\n(5.156 Gb/s, NRZ)", (2019.6, 2.5), color=GOLDDK, fs=6.8)
ax.set_yscale("log")
ax.set_ylim(0.3, 400); ax.set_xlim(1999, 2027.5)
ax.set_yticks([0.5, 1, 2, 5, 10, 20, 50, 100, 200])
ax.set_yticklabels(["0.5", "1", "2", "5", "10", "20", "50", "100", "200"])
ax.minorticks_off()
h = [Line2D([], [], color=C1, marker="o", lw=1, ms=4, label="PCIe"),
     Line2D([], [], color=C3, marker="o", lw=1, ms=4, label="Ethernet backplane (802.3)"),
     Line2D([], [], color=C5, marker="o", lw=1, ms=4, label="USB"),
     Line2D([], [], color=MUTED, marker="o", lw=0, ms=4, label="NRZ"),
     Line2D([], [], color=MUTED, marker="s", lw=0, ms=4, label="PAM4 / PAM3")]
ax.legend(handles=h, loc="upper left", ncol=1, fontsize=6.8)
finish(ax, xlabel="Year of specification", ylabel="Data rate per lane (Gb/s)")
savefig(fig, "ch01_rate_vs_year")

# ------------------------------------------------------------------ 2) speed ladder
items = [("1 UI at 5 Gb/s", 200, NAVY),
         ("130 nm CMOS: 4 FO4 (half-rate CMOS limit)", 4 * 45, C4),
         ("130 nm CMOS: 1 FO4 inverter delay", 45, C4),
         ("SG13G2 HBT CML gate (ring oscillator)", 2.0, C3),
         ("SG13G2 HBT: $1/(2\\pi f_T)$, $f_T$ = 300 GHz", 1e3 / (2 * np.pi * 300), C3)]
fig, ax = plt.subplots(figsize=(6.3, 1.95))
ypos = np.arange(len(items))[::-1]
for yy, (lab, v, col) in zip(ypos, items):
    ax.barh(yy, v, color=col, height=0.58, alpha=0.9 if col != C4 else 0.8)
    ax.text(v * 1.12, yy, f"{v:.2g} ps" if v < 10 else f"{v:.0f} ps", va="center",
            fontsize=7.5, color=col, fontweight="bold")
ax.set_yticks(ypos); ax.set_yticklabels([i[0] for i in items], fontsize=7.5)
ax.set_xscale("log"); ax.set_xlim(0.3, 900)
ax.axvline(200, color=NAVY, lw=0.8, ls=":")
ax.grid(True, axis="x", which="major"); ax.grid(False, axis="y")
ax.tick_params(axis="y", length=0)
finish(ax, xlabel="Time (ps, log scale)")
savefig(fig, "ch01_speed_ladder")
