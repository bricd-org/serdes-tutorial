"""ch16_lab5.py -- Lab 5 figure: eye height vs DFE taps, eye before and after a 3-tap DFE.
Same computations as tutorial/code/lab5_dfe.py."""
from bricdstyle import *
from link import *

PEAK = 8
H = channel()
bits = np.tile(sdp.prbs7(1), 40)
h_link, t = impulse(H * ctle(PEAK))
y = through(tx_wave(bits), h_link)
cur = sdp.channel_coefficients(pulse(h_link), t, SPS, 1, 8, res=50); plt.close("all")
post = cur[2:]
ntaps, eh = (0, 1, 2, 3, 4, 5, 8), []
for n in ntaps:
    rx = sdp.Receiver(y, SPS, F_NYQ, LEVELS, shift=True)
    if n:
        rx.nrz_DFE(post[:n])
    hts, ph, S, A = eye_scan(rx.signal, bits)
    eh.append(1e3 * hts[ph])
print("eye vs taps", np.round(eh, 1))
rx = sdp.Receiver(y, SPS, F_NYQ, LEVELS, shift=True)
hts0, ph0, _, _ = eye_scan(rx.signal, bits)
y0 = rx.signal.copy()
rx.nrz_DFE(post[:3])
hts, ph, S, A = eye_scan(rx.signal, bits)
ber = ber_q(S[ph], A[ph], 10e-3)
print(f"3-tap: {1e3*hts[ph]:.1f} mV; BER(10 mV) = {ber:.2e}")

fig, ax = plt.subplots(1, 3, figsize=(6.3, 2.2), gridspec_kw=dict(width_ratios=[1.1, 1, 1]))
a = ax[0]
xs = np.arange(len(ntaps))
cols = [GOLD if n == 3 else (C3 if n == 2 else C1) for n in ntaps]
a.bar(xs, eh, color=cols, width=0.62)
for xx, v in zip(xs, eh):
    a.text(xx, v + 3, f"{v:.0f}", ha="center", fontsize=6.8, color=NAVY)
a.set_xticks(xs); a.set_xticklabels([str(n) for n in ntaps])
a.set_ylim(0, 185)
a.text(2, 50, "chip", ha="center", va="center", rotation=90, fontsize=7, color="white")
a.text(3, 50, "this lab", ha="center", va="center", rotation=90, fontsize=7, color="white")
finish(a, "Number of DFE taps", "Eye height (mV)")
panel(a, "a")
for b, sig, p_, hh, let, tit in ((ax[1], y0, ph0, hts0, "b", f"{PEAK} dB CTLE, no DFE"),
                                 (ax[2], rx.signal, ph, hts, "c", "+ 3-tap DFE")):
    eye_density(b, 1e3 * sig, SPS, phase=p_, n_ui=2, skip_ui=100, vlim=(-200, 200))
    b.set_title(f"{tit}: {1e3*hh[p_]:.1f} mV", fontsize=8)
    panel(b, let)
ax[1].set_ylabel("Voltage (mV)"); ax[2].set_yticklabels([])
ax[2].text(0, -185, f"BER at $\\sigma$ = 10 mV: {ber:.1e}", ha="center", fontsize=7, color=NAVY,
           bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
savefig(fig, "ch16_lab5")
