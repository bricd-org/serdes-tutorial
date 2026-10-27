"""ch16_lab3.py -- Lab 3 figure: ZF TX FFE in frequency and the 2-tap / 3-tap eyes.
Same computations as tutorial/code/lab3_tx_ffe.py."""
from bricdstyle import *
from link import *

H = channel()
h, t = impulse(H)
p = pulse(h)
cur = sdp.channel_coefficients(p, t, SPS, 1, 1, res=50); plt.close("all")
c3 = sdp.forcing_ffe(1, cur); c3 = c3 / np.sum(np.abs(c3))
c2 = sdp.forcing_ffe(0, cur[1:]); c2 = c2 / np.sum(np.abs(c2))
print("c3 =", np.round(c3, 4), " c2 =", np.round(c2, 4))
Cf = np.exp(-2j * np.pi * np.outer(F, np.arange(3)) * UI) @ c3
bits = np.tile(sdp.prbs7(1), 40)
res = {}
for name, c in (("2-tap", c2), ("3-tap", c3)):
    y = through(tx_wave(bits, fir=c), h)
    hts, ph, S, A = eye_scan(y, bits)
    res[name] = (y, ph, hts[ph], np.sum(hts > 0) / SPS)
    print(f"{name}: {1e3*hts[ph]:.1f} mV, {np.sum(hts>0)/SPS:.2f} UI")

fig, ax = plt.subplots(1, 3, figsize=(6.3, 2.2), gridspec_kw=dict(width_ratios=[1.25, 1, 1]))
a = ax[0]
for Hx, lab, col in ((H, "channel", C1), (Cf, "3-tap FFE", C2), (H * Cf, "FFE $\\times$ channel", C3)):
    a.plot(F / 1e9, 20 * np.log10(np.abs(Hx)), color=col, label=lab)
a.axvline(F_NYQ / 1e9, color=MUTED, ls="--", lw=0.8)
a.set_xlim(0, 5); a.set_ylim(-35, 3)
a.legend(loc="lower left", fontsize=6.8)
finish(a, "Frequency (GHz)", "Magnitude (dB)")
panel(a, "a")
for b, name, let in ((ax[1], "2-tap", "b"), (ax[2], "3-tap", "c")):
    y, ph, eh, ew = res[name]
    eye_density(b, 1e3 * y, SPS, phase=ph, n_ui=2, skip_ui=100, vlim=(-260, 260))
    b.set_title(f"{name}: {1e3*eh:.1f} mV, {ew:.2f} UI", fontsize=8)
    if let == "b":
        b.set_ylabel("Voltage (mV)")
    else:
        b.set_yticklabels([])
    panel(b, let)
savefig(fig, "ch16_lab3")
