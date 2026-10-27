"""ch15_flow_infographic.py -- 'The Open-SERDES design flow' overview infographic (Ch 15)."""
from bricdstyle import *
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch

STAGES = [
    ("Specs", "link budget,\nblock targets", "Ch 4, 14"),
    ("System model", "serdespy, Python\nstat. eye", "Ch 16 labs"),
    ("Schematic + sim", "Xschem, ngspice\nXyce, VACASK", "testbenches"),
    ("Layout", "KLayout, Magic\nLibreLane (digital)", "CML symmetry"),
    ("Extraction + EM", "KLayout-PEX, Magic\nopenEMS / Palace", "post-layout"),
    ("Sign-off", "DRC / LVS (KLayout,\nNetgen), CACE", "every corner"),
    ("Tape-out", "IHP SG13G2\nshuttle", "GDSII"),
    ("Lab test", "eye, BER bathtub,\nJTOL, phase noise", "measured data"),
]

fig = plt.figure(figsize=(6.3, 3.35), layout="none")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 53); ax.axis("off")
ax.add_patch(FancyBboxPatch((0.5, 0.5), 99, 52, boxstyle="round,pad=0,rounding_size=1.5",
                            fc=BGPALE, ec="none"))
ax.text(3, 49.2, "THE OPEN-SERDES DESIGN FLOW", fontsize=10.5, fontweight="bold", color=NAVY, va="center")
ax.text(97, 49.2, "idea  →  silicon  →  measured link", fontsize=7.5, color=GOLDDK,
        va="center", ha="right", fontweight="bold")

W, H = 21.0, 15.0
xs = [3.5, 27.5, 51.5, 75.5]
rows = [27.5, 8.5]           # y of card bottom: row 1 (stages 1-4), row 2 (stages 8..5, snake)
pos = {}
for i in range(4):
    pos[i] = (xs[i], rows[0])
for j, i in enumerate(range(4, 8)):
    pos[i] = (xs[3 - j], rows[1])

for i, (title, tools, tag) in enumerate(STAGES):
    x, y = pos[i]
    hl = i in (1, 7)
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0,rounding_size=1.2",
                                fc=NAVY if hl else "white", ec=NAVY, lw=0.9))
    tc = "white" if hl else NAVY
    ax.add_patch(Circle((x + 3.2, y + H - 3.2), 2.1, fc=GOLD, ec="none"))
    ax.text(x + 3.2, y + H - 3.25, str(i + 1), color="white", fontsize=8, fontweight="bold",
            ha="center", va="center")
    ax.text(x + 6.3, y + H - 3.2, title, color=tc, fontsize=7.8, fontweight="bold", va="center")
    ax.text(x + 1.6, y + 6.1, tools, color=PALE if hl else SLATE, fontsize=6.4, va="center",
            linespacing=1.25)
    ax.text(x + W - 1.4, y + 1.7, tag, color=GOLDLT if hl else GOLDDK, fontsize=5.9, ha="right",
            va="center", style="italic")

def arrow(p, q, style="-|>", color=GOLDDK, ls="-", rad=0.0, lw=1.2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=8, color=color, lw=lw,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))

# forward path (snake)
for i in range(3):
    x, y = pos[i]; arrow((x + W + 0.2, y + H / 2), (pos[i + 1][0] - 0.2, y + H / 2))
x, y = pos[3]; arrow((x + W / 2, y - 0.2), (x + W / 2, pos[4][1] + H + 0.2))
for i in range(4, 7):
    x, y = pos[i]; arrow((x - 0.2, y + H / 2), (pos[i + 1][0] + W + 0.2, y + H / 2))

# feedback bus to the system model (dashed blue): ticks up from stages 5, 6, 8 -> bus -> stage 2
by = 25.5
fb = dict(color=BLUE, lw=0.9, ls=(0, (3, 2)))
taps = [pos[7][0] + W / 2, pos[5][0] + 3.5, pos[4][0] + W - 4]
for tx in taps:
    ax.plot([tx, tx], [rows[1] + H + 0.2, by], **fb)
ax.plot([min(taps), max(taps)], [by, by], **fb)
mx = pos[1][0] + W / 2
arrow((mx, by), (mx, rows[0] - 0.2), color=BLUE, lw=0.9, ls=(0, (3, 2)))
ax.text(71, by, " measured numbers replace assumptions ", color=BLUE,
        fontsize=6.2, style="italic", ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.15", fc=BGPALE, ec="none"))

# footer band
ax.add_patch(FancyBboxPatch((3.5, 1.6), 93, 4.6, boxstyle="round,pad=0,rounding_size=1",
                            fc=GTINT, ec="none"))
ax.text(50, 3.9, "All tools ship in the IIC-OSIC-TOOLS container  ·  open PDK: IHP SG13G2  ·  "
        "template: JKU AMS chip template", color=BROWN, fontsize=6.6, ha="center", va="center",
        fontweight="bold")
savefig(fig, "ch15_flow_infographic", png=True)
