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


# ------------------------------------------------------------------ 3) rate vs reach of electrical links
# (reach m, Gb/s per lane, label, label dx, label dy in points, ha). Reach as specified: IEEE 802.3 clauses for
# KR/CR/CX4, UCIe-A/-S channel reach; SATA internal cable and USB4 40 Gb/s passive cable: typical maximum length.
pkg = [(0.002, 32, "UCIe advanced package", 6, -1, "left"), (0.025, 32, "UCIe standard package", 6, 7, "left")]
pcb = [(1.0, 10.3125, "10GBASE-KR", -7, 0, "right"), (1.0, 25.78125, "100GBASE-KR4", -7, 0, "right")]
cab = [(1.0, 6.0, "SATA 3", 7, 1, "left"), (0.8, 20.0, "USB4 (per lane)", -7, 0, "right"),
       (15.0, 3.125, "10GBASE-CX4", 0, -9, "center"), (5.0, 25.78125, "100GBASE-CR4", 7, 0, "left"),
       (3.0, 53.125, "50GBASE-CR", 7, 0, "left"), (2.0, 106.25, "100GBASE-CR1", 0, -9, "center")]

fig, ax = plt.subplots(figsize=(6.3, 3.0))
xr = np.logspace(-3.2, 1.6, 50)
for prod, yl in ((1, 150), (10, 150), (100, 150), (1000, 150)):
    ax.plot(xr, prod / xr, color=PALE, lw=0.9, ls="--", zorder=1)
    ax.text(prod / yl * 0.84, yl, f"{prod:g} Gb/s·m", color=MUTED, fontsize=6.5, rotation=-39, ha="right", va="top")
for data, col, mk in ((pkg, C5, "^"), (pcb, C1, "o"), (cab, C3, "s")):
    for (x, v, lab, dx, dy, ha) in data:
        ax.plot(x, v, mk, color=col, ms=5.5, zorder=3)
        ax.annotate(lab, (x, v), xytext=(dx, dy), textcoords="offset points", color=col, fontsize=6.6,
                    ha=ha, va="center")
ax.plot(1.0, 5.0, "D", color=GOLD, mec=GOLDDK, ms=6.5, zorder=4)
ax.annotate("Open-SERDES: 5 Gb/s\nover the 1 m REF channel", (1.0, 5.0), xytext=(-7, -9), textcoords="offset points",
            color=GOLDDK, fontsize=6.8, fontweight="bold", ha="right", va="center")
ax.text(36, 160, "longer or faster:\noptical fiber", color=NAVY, fontsize=6.8, ha="right", va="center")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(8e-4, 40); ax.set_ylim(1.5, 200)
ax.set_xticks([1e-3, 1e-2, 0.1, 1, 10]); ax.set_xticklabels(["1 mm", "1 cm", "10 cm", "1 m", "10 m"])
ax.set_yticks([2, 5, 10, 20, 50, 100, 200]); ax.set_yticklabels(["2", "5", "10", "20", "50", "100", "200"])
ax.minorticks_off()
h = [Line2D([], [], color=C5, marker="^", lw=0, ms=5, label="in a package (chiplet links)"),
     Line2D([], [], color=C1, marker="o", lw=0, ms=5, label="PCB backplane, two connectors"),
     Line2D([], [], color=C3, marker="s", lw=0, ms=5, label="copper cable (twinax, SATA, USB)"),
     Line2D([], [], color=PALE, ls="--", lw=0.9, label="constant rate × reach")]
ax.legend(handles=h, loc="lower left", fontsize=6.8)
finish(ax, xlabel="Reach (log scale)", ylabel="Data rate per lane (Gb/s)")
savefig(fig, "ch01_reach")


# ------------------------------------------------------------------ 4) a backplane link, drawn
from matplotlib.patches import Rectangle, FancyBboxPatch
fig, ax = plt.subplots(figsize=(6.3, 2.75))
ax.set_xlim(0, 100); ax.set_ylim(-9.5, 44); ax.axis("off")
# backplane, connectors and the two line cards (side view)
ax.add_patch(Rectangle((5, 3), 90, 6, fc=BGPALE, ec=SLATE, lw=0.8, hatch="////", zorder=1))
for x0 in (16, 78):
    ax.add_patch(Rectangle((x0, 9), 6, 4.5, fc=NAVY, ec=NAVY, zorder=3))
for x0 in (18.2, 79.6):
    ax.add_patch(Rectangle((x0, 13.5), 1.8, 27, fc=GTINT, ec=GOLDDK, lw=0.8, zorder=2))
# chips: TX on the left card, RX on the right card
ax.add_patch(FancyBboxPatch((20.2, 30.5), 5.2, 4.2, boxstyle="round,pad=0.25", fc=SLATE, ec=NAVY, lw=0.8, zorder=4))
ax.add_patch(FancyBboxPatch((74.2, 30.5), 5.2, 4.2, boxstyle="round,pad=0.25", fc=SLATE, ec=NAVY, lw=0.8, zorder=4))
ax.text(22.8, 32.6, "TX", color="white", fontsize=7.5, fontweight="bold", ha="center", va="center", zorder=5)
ax.text(76.8, 32.6, "RX", color="white", fontsize=7.5, fontweight="bold", ha="center", va="center", zorder=5)
# the path one bit takes (gold)
path = [(22.8, 30.2), (21.0, 28.5), (21.0, 12.0), (19.0, 10.0), (19.0, 6.0), (81.0, 6.0), (81.0, 10.0),
        (79.0, 12.0), (79.0, 28.5), (76.8, 30.2)]
ax.plot([p[0] for p in path], [p[1] for p in path], color=GOLD, lw=2.2, solid_capstyle="round",
        solid_joinstyle="round", zorder=6)
ax.annotate("", xy=(76.8, 30.4), xytext=(78.6, 28.9),
            arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=2.2, mutation_scale=10), zorder=7)
for x in (19.0, 81.0):
    ax.plot([x, x], [6.0, 3.4], color=C4, lw=1.6, solid_capstyle="butt", zorder=6)     # via stubs
# labels
kw = dict(fontsize=6.8, color=NAVY, va="center")
note(ax, (22.8, 34.9), "die in a package, bond\nwires or bumps to the card", (30, 39.5), fs=6.8)
note(ax, (21.0, 22), "line-card trace", (30, 22), fs=6.8)
note(ax, (19.6, 38), "line card", (8, 38), fs=6.8, ha="right")
note(ax, (16.2, 11.2), "connector", (6, 16), fs=6.8, ha="right")
note(ax, (19.0, 4.0), "via stub", (9, -2.5), fs=6.8, color=C4, ha="right")
note(ax, (50, 6.0), "backplane trace on an inner layer", (50, 16), fs=6.8, ha="center")
note(ax, (79.0, 22), "line-card trace", (70, 22), fs=6.8, ha="right")
note(ax, (76.8, 34.9), "receiver: equalize, recover\nthe clock, decide every bit", (70, 39.5), fs=6.8, ha="right")
ax.text(50, 30, "The job: 5 Gb/s per lane with a bit-error rate of\n10$^{-12}$ or less, across a channel that loses\n"
        "17.4 dB at 2.5 GHz (the 1 m REF channel)", fontsize=6.8, color=NAVY, ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.5", fc=GTINT, ec=GOLD, lw=0.8))
ax.annotate("", xy=(5, -4.2), xytext=(95, -4.2), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.8))
ax.text(50, -6.8, "10GBASE-KR asks for up to about 1 m of PCB and two connectors; Open-SERDES stands in for it with the 1 m REF channel",
        fontsize=6.6, color=MUTED, ha="center", va="center")
savefig(fig, "ch01_backplane")
