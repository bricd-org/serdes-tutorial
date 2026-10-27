"""ch05_eqfund.py -- figures for Chapter 5 (Equalization Fundamentals).

ch05_inverse : REF |S21|, its ideal (zero-forcing) inverse, and the noise the inverse amplifies
ch05_cable   : Liu's zero-phase cable model: Lorentzian pulse, main cursor and PDA eye vs loss
ch05_anatomy : REF pulse response coloured by which equalizer removes which cursors
"""
from bricdstyle import *
from link import *

H = channel(REF_LEN)
fg = F / 1e9
m5 = F <= 5.0e9
Hdb = 20 * np.log10(np.abs(H))

# ------------------------------------------------------------------ ch05_inverse
fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
a1.axvspan(2.5, 5, color=BGPALE, lw=0)
a1.plot(fg[m5], Hdb[m5], color=C1, label="channel $|H_\\mathrm{ch}|$")
a1.plot(fg[m5], -Hdb[m5], color=C2, label="ideal inverse $1/|H_\\mathrm{ch}|$")
a1.plot(fg[m5], 0 * fg[m5], color=C3, lw=2.0, label="product (flat)")
a1.axvline(2.5, color=MUTED, ls="--", lw=0.8)
i_n = np.argmin(np.abs(F - F_NYQ))
a1.plot(2.5, Hdb[i_n], "o", color=C1, ms=4)
a1.plot(2.5, -Hdb[i_n], "o", color=C2, ms=4)
a1.text(2.65, Hdb[i_n] + 2.5, f"\u2212{-Hdb[i_n]:.1f} dB", color=C1, fontsize=7.5, va="bottom")
a1.text(2.65, -Hdb[i_n] - 2.5, f"+{-Hdb[i_n]:.1f} dB", color=C2, fontsize=7.5, va="top")
a1.text(2.45, -27, "$f_\\mathrm{N}$", color=MUTED, ha="right", fontsize=7.5)
a1.set_xlim(0, 5); a1.set_ylim(-33, 33)
a1.legend(loc="upper left", fontsize=7)
finish(a1, "Frequency (GHz)", "Magnitude (dB)")
panel(a1, "a")

# noise: white noise in, PSD gain |Heq|^2 and the cumulative rms noise gain vs equalized bandwidth
g2 = 1 / np.abs(H) ** 2
cum = np.cumsum(g2) / np.arange(1, g2.size + 1)
a2.fill_between(fg[m5], 0, 10 * np.log10(g2[m5]), color=C4, alpha=0.12, lw=0)
a2.plot(fg[m5], 10 * np.log10(g2[m5]), color=C4, label="noise PSD gain $|H_\\mathrm{eq}|^2$")
a2.plot(fg[m5], 10 * np.log10(cum[m5]), color=NAVY, label="rms noise gain if EQ stops at $B$")
for B, dx in ((2.5, -0.15), (5.0, -0.15)):
    i = np.argmin(np.abs(F - B * 1e9))
    v = 10 * np.log10(cum[i])
    a2.plot(B, v, "o", color=NAVY, ms=4)
    a2.text(B + dx, v + 1.5, f"{v:.1f} dB", color=NAVY, fontsize=7.5, ha="right")
a2.axvline(2.5, color=MUTED, ls="--", lw=0.8)
a2.set_xlim(0, 5); a2.set_ylim(0, 65)
a2.legend(loc="upper left", fontsize=7)
finish(a2, "Frequency or EQ bandwidth $B$ (GHz)", "Noise gain (dB)")
panel(a2, "b")
savefig(fig, "ch05_inverse")
for B in (2.5e9, 5e9):
    print("rms noise gain to", B, 10 * np.log10(cum[np.argmin(np.abs(F - B))]))

# ------------------------------------------------------------------ ch05_cable
def cable_pulse(t, kdl, V0=1.0):
    return V0 / np.pi * (np.arctan(2 * np.pi * t / kdl) - np.arctan(2 * np.pi * (t - UI) / kdl))

fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2, gridspec_kw=dict(width_ratios=[1.15, 1]))
tt = np.linspace(-4, 5, 1200)                # in UI, pulse occupies 0..1
for Ldb, col in zip((5, 10, 15, 20), (C3, C1, C2, C4)):
    kdl = Ldb / (8.686 * F_NYQ)
    a1.plot(tt, cable_pulse(tt * UI, kdl), color=col, label=f"{Ldb} dB")
    if Ldb == 15:
        kk = np.arange(-3, 4)
        ys = cable_pulse((0.5 + kk) * UI, kdl)
        a1.plot(0.5 + kk, ys, "o", color=col, ms=3.5, zorder=5)
a1.plot([0, 0, 1, 1], [0, 1, 1, 0], color=MUTED, lw=0.8, ls=":")
a1.text(1.05, 0.95, "TX pulse", fontsize=7, color=MUTED)
note(a1, (-0.5, 0.153), "pre = post\n(zero phase)", (-3.9, 0.55), color=C2, fs=7)
a1.set_xlim(-4, 5); a1.set_ylim(-0.05, 1.08)
a1.legend(loc="upper right", fontsize=7, title="loss at $f_\\mathrm{N}$", title_fontsize=7)
finish(a1, "Time (UI)", "$y(t)/V_0$")
panel(a1, "a")

L = np.linspace(0.5, 25, 300)
kdl = L / (8.686 * F_NYQ)
ymax = 2 / np.pi * np.arctan(np.pi * UI / kdl)
eye = []
for k_ in kdl:
    c = cable_pulse((0.5 + np.arange(-60, 61)) * UI, k_)
    eye.append(c[60] - (np.abs(c).sum() - c[60]))
eye = np.array(eye)
a2.plot(L, ymax, color=C1, label="main cursor $y_\\max/V_0$")
a2.plot(L, eye, color=C4, label="PDA half-eye / $V_0$")
a2.axhline(0, color=MUTED, lw=0.7)
L0 = np.interp(0, -eye, L)
a2.plot(15, 2 / np.pi * np.arctan(np.pi * UI / (15 / (8.686 * F_NYQ))), "o", color=C1, ms=4)
note(a2, (15, 0.470), "15 dB: 0.47", (17.0, 0.68), color=C1, fs=7)
note(a2, (L0, 0), f"eye closes\nat {L0:.0f} dB", (17.0, 0.16), color=C4, fs=7)
a2.set_xlim(0, 25); a2.set_ylim(-0.45, 1.05)
a2.legend(loc="upper right", fontsize=7)
finish(a2, "Loss at $f_\\mathrm{N}$ (dB)", "Normalized amplitude")
panel(a2, "b")
savefig(fig, "ch05_cable")
print("cable eye closes at", L0)

# ------------------------------------------------------------------ ch05_anatomy
t, p = pulse_of(H)
i0 = int(np.argmax(p))
tu = (np.arange(p.size) - i0) / SPS
fig, ax = plt.subplots(figsize=(6.3, 2.45))
zones = [(-2.5, -0.5, C4, "pre-cursor\nTX pre-tap,\nCTLE"),
         (-0.5, 0.5, GOLD, "main\ncursor"),
         (0.5, 2.5, C1, "first post-cursors\nDFE taps, TX post-tap"),
         (2.5, 10.5, C3, "long tail\nCTLE (and TX post-tap)")]
for x0, x1, col, txt in zones:
    ax.axvspan(x0, x1, color=col, alpha=0.08, lw=0)
    ax.text((x0 + x1) / 2, 0.455, txt, ha="center", va="top", fontsize=7, color=col)
m = (tu > -2.5) & (tu < 10.5)
ax.plot(tu[m], p[m], color=NAVY, lw=1.3)
k, pk, _ = cursors(p, 1, 10)
for kk, v in zip(k, pk):
    c = GOLD if kk == 0 else (C4 if kk < 0 else (C1 if kk <= 2 else C3))
    ax.vlines(kk, 0, v, color=c, lw=2.0)
    ax.plot(kk, v, "o", color=c, ms=3.8)
for kk in (-1, 0, 1, 2, 3):
    v = pk[list(k).index(kk)]
    ax.text(kk + 0.12, v + 0.004, f"{v:.3f}", fontsize=6.5, color=MUTED, va="bottom")
ax.axhline(0, color=MUTED, lw=0.7)
ax.set_xlim(-2.5, 10.5); ax.set_ylim(-0.02, 0.46)
ax.set_xticks(range(-2, 11))
finish(ax, "Time from main cursor (UI)", "Pulse response (V)")
savefig(fig, "ch05_anatomy")
