"""ch16_lab4.py -- Lab 4 figure: CTLE responses, eye height vs peaking, best eye.
Same computations as tutorial/code/lab4_ctle.py."""
from bricdstyle import *
from link import *

FP1, FP2 = 2.5e9, 10e9
H = channel()
bits = np.tile(sdp.prbs7(1), 40)
x = tx_wave(bits)
peaks, eh, ew = np.arange(0, 21, 2), [], []
for pk in peaks:
    h_link, t = impulse(H * ctle(pk, FP1, FP2))
    hts, ph, S, A = eye_scan(through(x, h_link), bits)
    eh.append(hts[ph]); ew.append(np.sum(hts > 0) / SPS)
eh = 1e3 * np.array(eh)
best = peaks[int(np.argmax(eh))]
print("eye heights", np.round(eh, 1), "best", best)
h_link, t = impulse(H * ctle(best, FP1, FP2))
y = through(x, h_link)
hts, ph, S, A = eye_scan(y, bits)

fig, ax = plt.subplots(1, 3, figsize=(6.3, 2.2), gridspec_kw=dict(width_ratios=[1.15, 1.05, 1]))
a = ax[0]
for pk, col in zip((4, 8, best), (C1, C2, C3)):
    a.semilogx(F[1:] / 1e9, 20 * np.log10(np.abs(ctle(pk, FP1, FP2)[1:])), color=col, label=f"{pk} dB")
a.axvline(F_NYQ / 1e9, color=MUTED, ls="--", lw=0.8)
a.set_xlim(0.01, 100); a.set_ylim(-17, 2)
a.legend(loc="upper left", ncol=3, fontsize=6.8, handlelength=1.2, columnspacing=0.8)
finish(a, "Frequency (GHz)", "CTLE gain (dB)")
panel(a, "a")
b = ax[1]
b.plot(peaks, eh, "o-", color=C1, ms=3.5)
b.axhline(0, color=MUTED, lw=0.7)
b.axvspan(0, 12, color=BTINT, zorder=0)
b.text(6, -70, "Open-SERDES\nrange 0-12 dB", ha="center", fontsize=6.8, color=NAVY)
b.plot(best, eh.max(), "o", color=GOLD, ms=6, zorder=5)
note(b, (best, eh.max()), f"{eh.max():.1f} mV\nat {best} dB", (15.5, 20), ha="center")
b.set_xlim(-0.5, 20.5); b.set_ylim(-100, 145)
finish(b, "CTLE peaking (dB)", "Eye height (mV)")
panel(b, "b")
c = ax[2]
eye_density(c, 1e3 * y, SPS, phase=ph, n_ui=2, skip_ui=100, vlim=(-220, 220))
c.set_title(f"{best} dB: {1e3*hts[ph]:.1f} mV, {np.sum(hts>0)/SPS:.2f} UI", fontsize=8)
c.set_ylabel("Voltage (mV)")
panel(c, "c")
savefig(fig, "ch16_lab4")
