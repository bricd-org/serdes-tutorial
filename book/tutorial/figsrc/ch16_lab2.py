"""ch16_lab2.py -- Lab 2 figure: PRBS7 waveform before/after REF and the closed RX eye.
Same computations as tutorial/code/lab2_prbs_eye.py."""
from bricdstyle import *
from link import *

bits = np.tile(sdp.prbs7(1), 40)
tx = sdp.Transmitter(bits, LEVELS, F_NYQ)
tx.oversample(SPS)
x = tx.signal_ideal
h, t = impulse(channel())
y = through(x, h)
hts, ph, S, A = eye_scan(y, bits)
print(f"RX eye {1e3*hts[ph]:.1f} mV, width {np.sum(hts>0)/SPS:.2f} UI, phase {ph}")
delay = np.argmax(pulse(h)) - SPS // 2
n = 40 * SPS
tt = np.arange(n) * DT * 1e9

fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.2), gridspec_kw=dict(width_ratios=[1.6, 1]))
a.plot(tt, 1e3 * x[200 * SPS:200 * SPS + n], color=C2, lw=1.0, label="TX ($\\pm$500 mV)")
a.plot(tt, 1e3 * y[200 * SPS + delay:200 * SPS + delay + n], color=C1, lw=1.4, label="RX, delay removed")
a.axhline(0, color=MUTED, lw=0.6)
a.set_xlim(0, tt[-1]); a.set_ylim(-620, 760)
a.legend(loc="upper left", ncol=2)
finish(a, "Time (ns), 40 bits of PRBS7", "Voltage (mV)")
panel(a, "a")
eye_density(b, 1e3 * y, SPS, phase=ph, n_ui=2, skip_ui=100, vlim=(-300, 300))
b.axhline(0, color=GOLD, lw=0.6, ls=":")
b.text(0, 285, f"eye {1e3*hts[ph]:.1f} mV: closed", ha="center", va="top", fontsize=7.5, color=C4,
       bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
b.set_ylabel("Voltage (mV)")
panel(b, "b")
savefig(fig, "ch16_lab2")
