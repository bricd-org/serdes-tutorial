"""ch14_rate.py -- how far does the 5 Gb/s architecture stretch? (Chapter 14, sec:ch14-10g)

(a) Worst-case (PDA) eye after the Open-SERDES partition against the length of the REF FR-4 line,
    for 5, 8 and 10 Gb/s NRZ and for 10 Gb/s PAM4 (5 GBd).
    Same channel(), ctle() and partition search as common.py and ch08_partition.py, with the symbol
    rate as a parameter: TX 3-tap FFE within the Open-SERDES limits (|c-1| <= 0.1, |c1| <= 0.25),
    CTLE 0..12 dB with its poles scaled to the new Nyquist frequency (fp1 = fN, fp2 = 4 fN),
    2-tap DFE (ideal), eye open before the DFE, best sampling phase. PAM4 sub-eye uses levels
    +-A, +-A/3: eye = 2A(p0/3 - residual ISI).
(b) The timing budget of fig. ch14_budget in fractions of a UI: 5 Gb/s today, the same terms scaled
    naively to a 100 ps UI, and the 10 Gb/s targets of tab:specs.
Prints the numbers used in sec:ch14-10g.
"""
from bricdstyle import *
import scipy as sp
import scipy.signal
if not hasattr(np, "complex_"):
    np.complex_ = np.complex128
import serdespy as sdp

A = 0.5
KPRE, KPOST = 4, 40
CM = np.arange(0, -0.101, -0.02)
CP = np.arange(0, -0.2501, -0.01)


class Grid:
    def __init__(self, baud, sps=32, df=10e6):
        self.ui, self.sps = 1 / baud, sps
        dt = self.ui / sps
        self.F = np.arange(0, 1 / (2 * dt) + df / 2, df)
        self.W = 2 * np.pi * self.F
        self.fn = baud / 2

    def channel(self, length, kr=60.0, rdc=7.0, tand=0.02, er=4.0, z0=50.0, c_pad=300e-15):
        F, W = self.F, self.W
        v, w0 = 2.998e8 / np.sqrt(er), 2 * np.pi * 1e9
        R = np.sqrt(rdc**2 + (kr * (1 + 1j) * np.sqrt(W / w0))**2)
        with np.errstate(divide="ignore", invalid="ignore"):
            C = (1 / (z0 * v)) * (1j * W / w0)**(-2 * tand / np.pi)
        C[0] = C[1]
        line = sdp.rlgc(R, np.full(F.size, z0 / v), np.full(F.size, 1e-12), C, length, F)
        abcd = sdp.series(np.array([sdp.impedance(np.full(F.size, z0)), sdp.shunt_cap(c_pad, 1j * W), line,
                                    sdp.shunt_cap(c_pad, 1j * W), sdp.admittance(np.full(F.size, 1 / z0))]))
        return 2 / abcd[:, 0, 0]

    def ctle(self, pk):
        a = 10**(pk / 20)
        wp1, wp2 = 2 * np.pi * self.fn, 2 * np.pi * 4 * self.fn
        num, den = np.array([a / wp1, 1]) / a, np.polymul([1 / wp1, 1], [1 / wp2, 1])
        return sp.signal.freqs(num, den, self.W)[1]

    def loss(self, H):
        return 20 * np.log10(abs(H[np.argmin(abs(self.F - self.fn))]))

    def csets(self, H):
        h, _ = sdp.freq2impulse(H, self.F)
        p = sp.signal.fftconvolve(h, np.ones(self.sps))[:h.size]
        i, ks = int(np.argmax(p)), np.arange(-KPRE - 1, KPOST + 2)
        return np.stack([p[i + d + ks * self.sps] for d in range(-self.sps // 2, self.sps // 2)])


def best_eye(g, H, pam4=False, ndfe=2):
    sets = [g.csets(H)] + [g.csets(H * g.ctle(pk)) for pk in range(0, 13)]
    best = -9.0
    for P in sets:
        for a in CM:
            for c in CP:
                c0 = 1 - abs(a) - abs(c)
                Q = a * P[:, 2:] + c0 * P[:, 1:-1] + c * P[:, :-2]
                m = Q[:, KPRE] / (3 if pam4 else 1)
                tot = np.abs(Q).sum(1) - np.abs(Q[:, KPRE])
                isi = tot - np.abs(Q[:, KPRE + 1:KPRE + 1 + ndfe]).sum(1)
                e = np.where(m - tot > 0, 2 * A * (m - isi), -9.0)
                best = max(best, e.max())
    return best


CASES = [("5 Gb/s NRZ", 5e9, False, C1), ("8 Gb/s NRZ", 8e9, False, C3),
         ("10 Gb/s NRZ", 10e9, False, C4), ("10 Gb/s PAM4 (5 GBd)", 5e9, True, C2)]
LENS = np.round(np.arange(0.25, 1.0001, 0.0625), 4)
res = {}
for name, baud, pam4, _ in CASES:
    g = Grid(baud)
    ys, ls = [], []
    for L in LENS:
        H = g.channel(L)
        ys.append(best_eye(g, H, pam4)); ls.append(g.loss(H))
    res[name] = (np.array(ys), np.array(ls))
    print(name, " ".join(f"{L:.2f}m:{1e3*y:.0f}mV({l:.1f}dB)" for L, y, l in zip(LENS, ys, ls)), flush=True)

# voltage terms that the eye must cover (fig. ch14_budget a): noise, jitter, offset, sensitivity
TERMS = 14.07 * 1.5 + 3.5 + 10.0 + 20.0
NEED = TERMS + 50.0

# timing budget, fractions of one UI
Q2 = 14.07
RJ5 = np.sqrt(1.0**2 + 0.7**2 + 0.5**2)
ROWS = [("5 Gb/s today\n(UI = 200 ps)", 200, [8, 6, 6, 20, Q2 * RJ5]),
        ("10 Gb/s, same circuits\n(UI = 100 ps)", 100, [8, 3, 6, 10, Q2 * RJ5]),
        ("10 Gb/s targets", 100, [4, 3, 3, 8, Q2 * 0.85])]
TNAMES = [("TX DCD/DDJ", C2), ("residual ISI", C3), ("RX clock path", C5), ("CDR dither", GOLDDK),
          ("RJ $\\times 2Q$", C4)]
for lab, ui, v in ROWS:
    print(f"{lab.splitlines()[0]:24s} TJ = {sum(v):5.1f} ps = {sum(v)/ui:.3f} UI")

fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.75), gridspec_kw=dict(width_ratios=[1.15, 1]))
a.axhspan(0, NEED, color=BGPALE, zorder=0)
a.axhline(NEED, color=MUTED, lw=0.7, ls="--")
a.text(0.26, NEED - 8, f"below {NEED:.0f} mV:\nmargin < 50 mV", fontsize=6.2, color=MUTED, ha="left", va="top")
for name, baud, pam4, col in CASES:
    y, _ = res[name]
    a.plot(LENS, 1e3 * y, marker="o", ms=2.6, lw=1.2, color=col, label=name, ls="--" if pam4 else "-")
for L, lab in ((1.0, "REF\n1 m"), (0.5, "REF-10\n0.5 m")):
    a.axvline(L, color=GOLDDK, lw=0.7, ls=":")
    a.text(L - 0.01, 640, lab, fontsize=6.3, color=GOLDDK, ha="right", va="top")
a.set_xlim(0.24, 1.01); a.set_ylim(0, 650)
finish(a, "Length of the REF FR-4 line (m)", "Worst-case (PDA) eye (mV)", legend=True, loc="upper right")
a.legend(fontsize=6.2, loc="upper right", bbox_to_anchor=(0.995, 0.86), handlelength=1.8)

from matplotlib.patches import Patch
for i, (lab, ui, v) in enumerate(ROWS):
    x0 = 0.0
    for (n, c), t in zip(TNAMES, v):
        b.barh(-i, t / ui, left=x0, color=c, height=0.56, edgecolor="white", lw=0.8)
        x0 += t / ui
    b.barh(-i, 1 - x0, left=x0, color=BTINT, height=0.56, edgecolor=C1, lw=0.8)
    b.text(x0 + (1 - x0) / 2, -i, f"eye\n{1 - x0:.2f} UI", ha="center", va="center", fontsize=6.5,
           color=NAVY, fontweight="bold")
    b.text(x0 - 0.01, -i + 0.38, f"TJ {x0:.2f} UI", ha="right", va="bottom", fontsize=6.0, color=NAVY)
b.axvline(0.3, color=C4, lw=0.8, ls="--")
b.text(0.31, -2.62, "0.3 UI target", fontsize=6.0, color=C4, va="top")
b.set_yticks([0, -1, -2]); b.set_yticklabels([r[0] for r in ROWS], fontsize=6.4)
b.set_xlim(0, 1); b.set_ylim(-2.85, 0.75)
b.legend(handles=[Patch(color=c, label=n) for n, c in TNAMES], ncol=3, loc="lower left",
         bbox_to_anchor=(-0.02, 1.0), fontsize=5.9, handlelength=1.0, columnspacing=0.8, borderaxespad=0)
b.grid(axis="y", visible=False)
finish(b, "Fraction of one UI")
panel(a, "a"); panel(b, "b", x=-0.55, y=1.04)
fig.tight_layout(w_pad=1.2)
savefig(fig, "ch14_rate")
