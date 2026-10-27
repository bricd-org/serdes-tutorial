"""ch08_partition.py -- equalization partition study (Table tab:eq-partition and fig ch08_partition).

Method (kept deliberately simple, and stated in the text):
  * channel(LOSS_FAMILY[d]) for d = 5..30 dB loss at 2.5 GHz, plus REF (17.4 dB).
  * CTLE = ctle(pk) from link.py (fp1 = 2.5 GHz, fp2 = 10 GHz, HF gain 0 dB), pk swept in 1 dB steps.
  * TX FFE = taps [c-1, c0, c1] with c0 = 1 - |c-1| - |c1| (peak-swing constraint), grid search
    c-1 in 0..-0.20, c1 in 0..-0.50 (step 0.02); 2-tap: c-1 = 0.
  * DFE = ideal: removes the first N post-cursors exactly.
  * Metric = PDA eye 2A(q0 - sum|qk|) over k = -4..+40 of the equalized cursors q, A = 0.5 V,
    maximized over the sampling phase (+-0.5 UI around the pulse peak) and over the free settings.
  * Normalized eye = PDA eye / (2A p0), p0 = main cursor of the UNequalized pulse.
"""
from bricdstyle import *
from link import *

KPRE, KPOST = 4, 40
kidx = np.arange(-KPRE, KPOST + 1)
CM1 = np.arange(0, -0.201, -0.02)
CP1 = np.arange(0, -0.501, -0.02)


def cursor_sets(p):
    """Cursor vectors (k = -KPRE-1 .. KPOST+1) for every sampling phase within +-0.5 UI of the peak."""
    ipk = int(np.argmax(p))
    ks = np.arange(-KPRE - 1, KPOST + 2)
    return np.stack([p[ipk + d + ks * SPS] for d in range(-SPS // 2, SPS // 2)])   # (64, nk+2)


def best_eye(P, ndfe, taps="none", cm1=CM1, cp1=CP1):
    """P: (phases, nk+2) cursor sets with one extra cursor each side. Returns (eye, (c-1,c1))."""
    if taps == "none":
        grid = [(0.0, 0.0)]
    elif taps == "2":
        grid = [(0.0, c) for c in cp1]
    else:
        grid = [(a, c) for a in cm1 for c in cp1]
    best = (-9.0, None)
    for a, c in grid:
        c0 = 1 - abs(a) - abs(c)
        # q_k = a p_{k+1} + c0 p_k + c p_{k-1}
        Q = a * P[:, 2:] + c0 * P[:, 1:-1] + c * P[:, :-2]          # k = -KPRE..KPOST
        main = Q[:, KPRE]
        isi = np.abs(Q).sum(1) - np.abs(main) - np.abs(Q[:, KPRE + 1:KPRE + 1 + ndfe]).sum(1)
        e = 2 * A_TX * (main - isi)
        i = int(np.argmax(e))
        if e[i] > best[0]:
            best = (e[i], (a, c))
    return best


CM_OS = np.arange(0, -0.101, -0.02)        # practical TX limits: |c-1| <= 0.1,
CP_OS = np.arange(0, -0.2501, -0.01)       # |c1| <= 0.25 (6 dB de-emphasis, the PCIe Gen2 maximum)


def optimize(Pc, pks, ndfe, taps="none", cm1=CM1, cp1=CP1, need_open_pre=False):
    """Best post-EQ PDA eye over CTLE settings pks and TX grid. If need_open_pre, the eye
    BEFORE the DFE (TX + CTLE only) must also be open."""
    best = (-9.0, None, None)
    for pk in pks:
        P = Pc[pk]
        grid = [(0.0, 0.0)] if taps == "none" else ([(0.0, c) for c in cp1] if taps == "2" else
                                                     [(a, c) for a in cm1 for c in cp1])
        for a, c in grid:
            e = best_eye(P, ndfe, "3", [a], [c])[0]
            if need_open_pre and best_eye(P, 0, "3", [a], [c])[0] <= 0:
                continue
            if e > best[0]:
                best = (e, (a, c), pk)
    return best


LOSSES = [5, 10, 15, 17.4, 20, 25, 30]
STRATS = [("none", "No equalization"), ("tx2", "TX 2-tap FFE"), ("ctle", "CTLE"),
          ("ctle_dfe2", "CTLE + 2-tap DFE"), ("all", "TX 3-tap + CTLE + 2-tap DFE"),
          ("os", "\\OS{} partition$^{\\ast}$"), ("max", "\\OS{} limits, 5-tap DFE$^{\\ast}$")]
res = {s: {} for s, _ in STRATS}
for L in LOSSES:
    H = channel(REF_LEN if L == 17.4 else LOSS_FAMILY[L])
    t, p_raw = pulse_of(H)
    p0_raw = p_raw.max()
    Pc = {pk: cursor_sets(pulse_of(H * ctle(pk))[1]) for pk in range(0, 21)}
    Pc[-1] = cursor_sets(p_raw)                    # -1 = no CTLE at all
    allpk = [-1] + list(range(0, 21))
    out = {"none": optimize(Pc, [-1], 0), "tx2": optimize(Pc, [-1], 0, "2"),
           "ctle": optimize(Pc, allpk, 0), "ctle_dfe2": optimize(Pc, allpk, 2),
           "all": optimize(Pc, allpk, 2, "3"),
           "os": optimize(Pc, [-1] + list(range(0, 13)), 2, "3", CM_OS, CP_OS, True),
           "max": optimize(Pc, [-1] + list(range(0, 13)), 5, "3", CM_OS, CP_OS, True)}
    print(f"--- {L} dB   (2A p0 raw = {1e3*2*A_TX*p0_raw:.1f} mV)")
    for s, name in STRATS:
        e, tp, pk = out[s]
        res[s][L] = (e, e / (2 * A_TX * p0_raw), tp, pk)
        de = "" if tp is None else f"c-1={tp[0]:.2f} c1={tp[1]:.2f} ({20*np.log10(1/max(1e-9, 1-2*abs(tp[1])-2*abs(tp[0]))):.1f} dB DE)"
        print(f"  {name:40s} {1e3*e:7.1f} mV  norm {e/(2*A_TX*p0_raw):6.3f}  CTLE {pk} dB  {de}")

# LaTeX rows for the table (10/15/REF/20/25 dB)
print("\nLaTeX rows:")
def fmt(e, n):
    if e <= 0:
        return f"\\closed{{{1e3*e:.0f}}}"
    return f"{1e3*e:.0f} & {n:.2f}"
for s, name in STRATS:
    cells = " & ".join(fmt(*res[s][L][:2]) for L in (10, 15, 17.4, 20, 25))
    print(f"{name} & {cells} \\\\")

# figure: PDA eye vs loss for each strategy
fig, ax = plt.subplots(figsize=(6.3, 2.5))
style = {"none": (MUTED, "--", "o"), "tx2": (C2, "-", "^"), "ctle": (C1, "-", "s"),
         "ctle_dfe2": (C5, "-", "D"), "all": (GOLD, ":", "v"), "os": (C3, "-", "o"), "max": (NAVY, "--", "x")}
Ls = [5, 10, 15, 17.4, 20, 25, 30]
for s, name in STRATS:
    col, ls, mk = style[s]
    yv = np.array([1e3 * res[s][L][0] for L in Ls])
    yv = np.where(yv > 0, yv, np.nan)                  # closed eyes cannot be drawn on a log axis
    ax.plot(Ls, yv, color=col, ls=ls, marker=mk, ms=3.8,
            lw=2.0 if s == "os" else 1.2, label=name.replace("\\OS{}", "Open-SERDES").replace("$^{\\ast}$", "*"))
ax.set_yscale("log")
ax.axvline(17.4, color=GOLDDK, ls=":", lw=0.9)
ax.text(17.6, 880, "REF 17.4 dB", color=GOLDDK, fontsize=7, va="top")
ax.text(11.2, 60, "no EQ: closed\nabove 13 dB", color=MUTED, fontsize=7, ha="left", va="center")
ax.set_xlim(4, 31); ax.set_ylim(10, 1000)
ax.set_yticks([10, 20, 50, 100, 200, 500, 1000]); ax.set_yticklabels(["10", "20", "50", "100", "200", "500", "1000"])
ax.legend(loc="lower left", fontsize=7, ncol=1)
finish(ax, "Channel loss at 2.5 GHz (dB)", "PDA eye height (mV)")
savefig(fig, "ch08_partition")
