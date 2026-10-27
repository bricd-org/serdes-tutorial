"""ch09_tx.py -- figures for Chapter 9 (The Transmitter).

ch09_fo4     : max bit rate with CMOS-distributed clocks (8-FO4 rule) per serializer architecture
ch09_current : driver supply current and power vs differential swing (CML vs voltage-mode/SST)
ch09_pad     : pad-capacitance budget: |S11| at Nyquist vs Cp, and pad-node bandwidth with/without T-coil
Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch09_tx.py
"""
from bricdstyle import *
from link import *

M = lambda v, d=1: f"{v:.{d}f}".replace("-", "−")
Z0 = 50.0

# ------------------------------------------------------------------ ch09_fo4
FO4_TT, FO4_SS = 42e-12, 55e-12          # 130 nm estimates (measure in ngspice!)
arch = ["full rate\n(1 bit/clock)", "half rate\n(2 bits/clock)", "quarter rate\n(4 bits/clock)", "eighth rate\n(8 bits/clock)"]
nbit = np.array([1, 2, 4, 8])
fmax_tt = nbit / (8 * FO4_TT) / 1e9
fmax_ss = nbit / (8 * FO4_SS) / 1e9
for a, t, s in zip(arch, fmax_tt, fmax_ss):
    print("FO4:", a.split("\n")[0], f"TT {t:.2f}  SS {s:.2f} Gb/s")
fig, ax = plt.subplots(figsize=(6.3, 2.15))
x = np.arange(4)
ax.bar(x - 0.18, fmax_tt, 0.34, color=C1, label="typical corner, FO4 = 42 ps")
ax.bar(x + 0.18, fmax_ss, 0.34, color=PALE, edgecolor=C1, lw=0.7, hatch="////", label="slow corner, FO4 = 55 ps")
for xi, t, s in zip(x, fmax_tt, fmax_ss):
    ax.text(xi - 0.18, t * 1.07, f"{t:.1f}", ha="center", va="bottom", fontsize=7, color=C1)
    ax.text(xi + 0.18, s * 1.07, f"{s:.1f}", ha="center", va="bottom", fontsize=7, color=MUTED)
ax.axhline(5, color=C4, lw=1.1, ls="--")
ax.text(-0.56, 5.35, "5 Gb/s target", color=C4, fontsize=7.5, ha="left", va="bottom")
ax.set_yscale("log"); ax.set_ylim(1, 60)
ax.set_yticks([1, 2, 5, 10, 20, 50]); ax.set_yticklabels(["1", "2", "5", "10", "20", "50"])
ax.set_xticks(x); ax.set_xticklabels(arch, fontsize=7.5)
ax.set_xlim(-0.6, 3.6)
ax.text(1.0, 8.6, "19% margin (TT),\nfails at SS", color=C4, fontsize=7, ha="center", va="bottom")
ax.text(0.0, 6.6, "fails", color=C4, fontsize=7, ha="center", va="bottom")
ax.legend(loc="upper left", fontsize=7)
finish(ax, None, "Max. bit rate with\nCMOS clocks (Gb/s)")
ax.grid(axis="x", visible=False)
savefig(fig, "ch09_fo4")

# ------------------------------------------------------------------ ch09_current
V = np.linspace(0, 1.2, 200)
I_cml = V / Z0 * 1e3
I_vmse = V / (2 * Z0) * 1e3
I_vmd = V / (4 * Z0) * 1e3
# SST with 6 dB 2-tap de-emphasis (c0 = 0.75, c1 = -0.25): supply current per symbol type
def sst_current(Vs, c0=0.75):
    """Supply current [A] of an ideal segmented SST driver, differential 100-ohm load.
    Transition bit: all slices agree. Repeated bit: fraction c0 drive the data, 1-c0 the inverse."""
    I_tr = Vs / (4 * Z0)
    Rup_p, Rup_m = Z0 / c0, Z0 / (1 - c0)              # pull-up resistances (side +, side -)
    i = (c0 - (1 - c0)) * Vs / (4 * Z0)                 # loop current through 2*Z0 + 2*Z0
    vp = c0 * Vs - Z0 * i; vm = (1 - c0) * Vs + Z0 * i
    I_rep = (Vs - vp) / Rup_p + (Vs - vm) / Rup_m
    return I_tr, I_rep
itr, irep = sst_current(1.0)
avg_ratio = 0.5 * (itr + irep) / itr
print(f"SST 6 dB EQ: repeated/transition current = {irep/itr:.3f}, 50%-transition average = {avg_ratio:.3f}x")
I_sst_eq = I_vmd * avg_ratio
fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
for a in (a1, a2):
    a.axvspan(0.8, 1.0, color=GTINT, lw=0)
a1.plot(V, I_cml, color=C1, lw=1.6, label="CML: $V_{d,pp}/Z_0$")
a1.plot(V, I_vmse, color=C5, lw=1.2, ls="--", label="VM, single-ended term.: $V_{d,pp}/2Z_0$")
a1.plot(V, I_sst_eq, color=C2, lw=1.0, ls=":", label=f"SST + 6 dB de-emph. (avg, {avg_ratio:.2f}$\\times$)")
a1.plot(V, I_vmd, color=C3, lw=1.6, label="SST / VM, diff. term.: $V_{d,pp}/4Z_0$")
for v in (0.8, 1.0):
    a1.plot(v, v / Z0 * 1e3, "o", color=C1, ms=4)
    a1.plot(v, v / (4 * Z0) * 1e3, "o", color=C3, ms=4)
a1.text(0.77, 17.0, "16 mA", ha="right", fontsize=7, color=C1)
a1.text(1.03, 19.4, "20 mA", ha="left", va="top", fontsize=7, color=C1)
a1.text(0.77, 1.0, "4 mA", ha="right", fontsize=7, color=C3)
a1.text(1.03, 4.4, "5 mA", ha="left", va="top", fontsize=7, color=C3)
a1.annotate("", xy=(0.9, 4.9), xytext=(0.9, 17.4), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=0.8))
a1.text(0.92, 11.5, "4$\\times$", fontsize=8, color=NAVY, fontweight="bold")
a1.set_xlim(0, 1.2); a1.set_ylim(0, 35)
a1.legend(loc="upper left", fontsize=6.3, handlelength=1.6)
finish(a1, "Differential swing $V_{d,pp}$ (V)", "Driver supply current (mA)")
panel(a1, "a")
P_cml25 = 2.5 * I_cml
P_sst12 = 1.2 * I_vmd
P_sst_ideal = V * I_vmd
a2.plot(V, P_cml25, color=C1, lw=1.6, label="HBT CML from 2.5 V")
a2.plot(V, P_sst12, color=C3, lw=1.6, label="SST, regulated from 1.2 V")
a2.plot(V, P_sst_ideal, color=C3, lw=1.0, ls="--", label="SST, ideal supply $V_s = V_{d,pp}$")
for v in (0.8, 1.0):
    a2.plot(v, 2.5 * v / Z0 * 1e3, "o", color=C1, ms=4)
a2.text(0.77, 42, "40 mW", ha="right", fontsize=7, color=C1)
a2.text(1.03, 48.5, "50 mW", ha="left", va="top", fontsize=7, color=C1)
a2.text(1.03, 9.5, "6 mW", ha="left", va="center", fontsize=7, color=C3)
a2.set_xlim(0, 1.2); a2.set_ylim(0, 80)
a2.legend(loc="upper left", fontsize=6.5)
finish(a2, "Differential swing $V_{d,pp}$ (V)", "Output-stage power (mW)")
panel(a2, "b")
savefig(fig, "ch09_current")

# ------------------------------------------------------------------ ch09_pad
def s11_rc(f, Cp):
    x = 2 * np.pi * f * Z0 * Cp
    return x / np.sqrt(4 + x * x)

def tcoil(f, C, R=50.0, Rs=50.0, k=1 / 3, Rcoil=0.0):
    """Symmetric bridged T-coil (Galal-Razavi design, zeta = 0.707): source Rs at node P, C at the
    centre tap X, termination R at node T. Returns (V_X normalised to DC, S11 at P)."""
    L = R**2 * C / (2 * (1 + k)); Mm = k * L; CB = C * (1 - k) / (4 * (1 + k))
    vx, s11 = [], []
    for ff in np.atleast_1d(f):
        s = 2j * np.pi * ff
        A = np.zeros((5, 5), complex); b = np.zeros(5, complex)
        A[0, 0] = 1 / Rs + s * CB; A[0, 2] = -s * CB; A[0, 3] = 1; b[0] = 1.0
        A[1, 1] = s * C; A[1, 3] = -1; A[1, 4] = 1
        A[2, 2] = 1 / R + s * CB; A[2, 0] = -s * CB; A[2, 4] = -1
        A[3, 0] = 1; A[3, 1] = -1; A[3, 3] = -(s * L + Rcoil); A[3, 4] = -s * Mm
        A[4, 1] = 1; A[4, 2] = -1; A[4, 3] = -s * Mm; A[4, 4] = -(s * L + Rcoil)
        xs = np.linalg.solve(A, b)
        vp = xs[0]; zin = vp / (1 - vp / Rs)
        vx.append(xs[1]); s11.append((zin - Rs) / (zin + Rs))
    vx = np.array(vx); return vx / (Rs * R / (Rs + R)), np.array(s11)

fN = 2.5e9
Cs = np.linspace(0.02e-12, 1.5e-12, 150)
s11_fn = 20 * np.log10(s11_rc(fN, Cs))
s11_tc = np.array([20 * np.log10(abs(tcoil(fN, c, Rcoil=3.0)[1][0])) for c in Cs])
cmax10 = 0.6667 / (2 * np.pi * fN * Z0); cmax15 = 2 * 0.1778 / np.sqrt(1 - 0.1778**2) / (2 * np.pi * fN * Z0)
print(f"pad: Cp max for RL 10 dB = {cmax10*1e12:.3f} pF, 15 dB = {cmax15*1e12:.3f} pF")
print(f"pad: WE3 0.63 pF -> |S11|(fN) = {20*np.log10(s11_rc(fN,0.63e-12)):.2f} dB, f3dB = {1/(np.pi*Z0*0.63e-12)/1e9:.2f} GHz")
f = np.linspace(0.05e9, 25e9, 1200)
h_tc, s_tc = tcoil(f, 0.63e-12)
f3_tc = f[np.argmax(np.abs(h_tc) < 1 / np.sqrt(2))]
_, s_tc3 = tcoil(np.array([fN, 5e9]), 0.63e-12, Rcoil=3.0)
print(f"pad: T-coil 0.63 pF: f3dB(VX) = {f3_tc/1e9:.2f} GHz; |S11| with 3-ohm coils at 2.5/5 GHz = "
      f"{20*np.log10(abs(s_tc3[0])):.1f} / {20*np.log10(abs(s_tc3[1])):.1f} dB")
L = 50**2 * 0.63e-12 / (2 * 4 / 3)
print(f"pad: T-coil L1=L2={L*1e9:.3f} nH, M={L/3*1e9:.3f} nH, CB={0.63e-12/8*1e15:.1f} fF, total {50**2*0.63e-12*1e9:.3f} nH")

fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
a1.axhspan(-10, 0, color="#F6E3E0", lw=0)
a1.plot(Cs * 1e12, s11_fn, color=C1, lw=1.6, label="pad, ESD, driver on one node")
a1.plot(Cs * 1e12, s11_tc, color=C3, lw=1.6, label="with T-coil (3 $\\Omega$ per coil)")
a1.axhline(-10, color=C4, lw=0.9, ls="--"); a1.axhline(-15, color=MUTED, lw=0.7, ls=":")
a1.text(0.04, -9.3, "RL = 10 dB", color=C4, fontsize=7)
a1.text(0.04, -14.3, "15 dB", color=MUTED, fontsize=7)
for c, lab, xt, yt in ((0.30, "REF model, 0.30 pF", 0.40, -22.0), (0.63, "example: 0.63 pF", 0.80, -17.0)):
    y = 20 * np.log10(s11_rc(fN, c * 1e-12))
    a1.plot(c, y, "o", color=GOLD, ms=4.5, zorder=5)
    a1.annotate(lab, (c, y), xytext=(xt, yt), fontsize=6.8, color=NAVY, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=NAVY, shrinkA=0, shrinkB=2))
a1.plot(cmax10 * 1e12, -10, "v", color=C4, ms=5)
a1.text(cmax10 * 1e12 + 0.05, -12.4, f"{cmax10*1e12:.2f} pF", color=C4, fontsize=7)
a1.set_xlim(0, 1.5); a1.set_ylim(-40, 0)
a1.legend(loc="lower right", fontsize=6.6)
finish(a1, "Total pad capacitance $C_p$ (pF)", "$|S_{11}|$ at 2.5 GHz (dB)")
panel(a1, "a")
for c, col, ls in ((0.30e-12, C1, ":"), (0.63e-12, C1, "-"), (1.0e-12, C4, "--")):
    h = 1 / np.sqrt(1 + (2 * np.pi * f * (Z0 / 2) * c)**2)
    a2.plot(f / 1e9, 20 * np.log10(h), color=col, ls=ls, lw=1.3, label=f"RC, {c*1e12:.2f} pF ($f_{{3dB}}$ = {1/(np.pi*Z0*c)/1e9:.1f} GHz)")
a2.plot(f / 1e9, 20 * np.log10(np.abs(h_tc)), color=C3, lw=1.6, label=f"T-coil, 0.63 pF ($f_{{3dB}}$ = {f3_tc/1e9:.1f} GHz)")
a2.axhline(-3, color=MUTED, lw=0.6, ls=":")
a2.axvline(2.5, color=GOLD, lw=0.9, ls="--"); a2.text(2.8, 0.25, "$f_N$", color=GOLDDK, fontsize=8)
a2.set_xlim(0, 25); a2.set_ylim(-13, 1)
a2.legend(loc="lower left", fontsize=6.4)
finish(a2, "Frequency (GHz)", "Pad-node response (dB)")
panel(a2, "b")
savefig(fig, "ch09_pad")

# extra numbers used in the text: REF channel with heavier pads
for cp in (300e-15, 630e-15):
    Hc = channel(REF_LEN, c_pad=cp)
    _, p = pulse_of(Hc); k, pk, _ = cursors(p)
    q = np.convolve(pk, [0.751, -0.249])[:pk.size]
    print(f"REF with c_pad={cp*1e15:.0f} fF: loss {loss_db(Hc):.2f} dB, p0 {pk[2]:.4f}, FFE-only PDA {1e3*pda_eye(q, k):.1f} mV")
