"""ch14_power.py -- first-cut Open-SERDES power budget (Chapter 14) and energy per bit.
Block powers come from Chapters 9, 10, 12 and 13 (checklists and specnotes); see tab in 14_arch.tex."""
from bricdstyle import *

FB = 5e9
# (block, domain, mW)
BLOCKS = [
    ("3-tap CML driver (20 mA, 2.5 V)", "TX", 50.0),
    ("Pre-drivers (x3)", "TX", 10.0),
    ("CML 2:1 muxes (x3) + latches", "TX", 21.0),
    ("CML 4:2, TX clock buffers, /2", "TX", 20.0),
    ("CMOS 16:4 serializer", "TX", 3.0),
    ("CTLE + buffer", "RX", 12.5),
    ("DFE summers + tap DACs", "RX", 15.0),
    ("4 CML samplers (M-S)", "RX", 30.0),
    ("Sampler clock buffers", "RX", 10.0),
    ("Offset DACs (x4)", "RX", 0.6),
    ("CMOS 1:16 deserializer", "RX", 5.0),
    ("PLL (team design)", "Clock", 12.73),
    ("PPF + I/Q buffers, distribution", "Clock", 15.0),
    ("Phase interpolators (x2)", "Clock", 8.0),
    ("CDR loop filter (digital)", "Digital", 2.0),
    ("PRBS gen. + checker", "Digital", 1.0),
    ("SPI + config registers", "Digital", 0.2),
]
COL = {"TX": C1, "RX": C3, "Clock": C2, "Digital": GOLDDK}
tot = sum(p for _, _, p in BLOCKS)
for d in COL:
    s = sum(p for _, dd, p in BLOCKS if dd == d)
    print(f"{d:8s} {s:7.2f} mW  ({100*s/tot:4.1f} %)")
print(f"TOTAL    {tot:7.2f} mW  -> {tot*1e-3/FB*1e12:.1f} pJ/b")
sst = tot - 44.0
print(f"with SST driver (-44 mW): {sst:.1f} mW -> {sst*1e-3/FB*1e12:.1f} pJ/b")
purdue = 438e-3 / 2e9 * 1e12
print(f"Purdue OpenSerDes: {purdue:.0f} pJ/b")

fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 3.0), gridspec_kw=dict(width_ratios=[2.2, 1]))
order = BLOCKS[::-1]
ys = np.arange(len(order))
a.barh(ys, [p for _, _, p in order], color=[COL[d] for _, d, _ in order], height=0.68)
for y_, (n, d, p) in zip(ys, order):
    a.text(p + 0.8, y_, f"{p:g}", va="center", fontsize=6.6, color=NAVY)
a.set_yticks(ys); a.set_yticklabels([n for n, _, _ in order], fontsize=6.6)
a.set_xlim(0, 60); a.grid(axis="y", visible=False)
from matplotlib.patches import Patch
hand = [Patch(color=c, label=f"{d}: {sum(p for _, dd, p in BLOCKS if dd == d):.0f} mW") for d, c in COL.items()]
a.legend(handles=hand, loc="lower right", fontsize=6.8, title=f"total {tot:.0f} mW = {tot/5:.1f} pJ/b",
         title_fontsize=7.2)
finish(a, "Power (mW), first-cut estimate")
panel(a, "a", x=-0.42)
names = ["Open-\nSerDes\nSKY130", "Open-\nSERDES\nfirst cut", "with\nSST\ndriver"]
vals = [purdue, tot / 5, sst / 5]
b.bar(range(3), vals, color=[MUTED, C1, C3], width=0.6)
for i, v in enumerate(vals):
    b.text(i, v + 4, f"{v:.0f}", ha="center", fontsize=7, color=NAVY)
b.set_xticks(range(3)); b.set_xticklabels(names, fontsize=6.4)
b.set_ylim(0, 250); b.grid(axis="x", visible=False)
finish(b, None, "Energy per bit (pJ/b)")
panel(b, "b")
savefig(fig, "ch14_power")
