"""ch16_lab6.py -- Lab 6 figure: bathtub (estimated and counted) and counted vs estimated BER.
Same computations, in the same order and with the same seed, as tutorial/code/lab6_jitter_ber.py."""
from bricdstyle import *
from link import *

np.random.seed(2026)
PEAK, N_TAPS, RJ_UI = 8, 3, 0.025
H = channel()
h_link, t = impulse(H * ctle(PEAK))
cur = sdp.channel_coefficients(pulse(h_link), t, SPS, 1, N_TAPS, res=50); plt.close("all")
taps = cur[2:]
bits = np.tile(sdp.prbs7(1), 800)
y = through(tx_wave(bits, jitter_ui=RJ_UI), h_link)
rx = sdp.Receiver(y, SPS, F_NYQ, LEVELS, shift=True)
rx.nrz_DFE(taps)
hts, ph, S, A = eye_scan(rx.signal, bits)
skip = 50
sig_list, counted, est = (10e-3, 15e-3, 20e-3, 25e-3), [], []
for sigma in sig_list:
    rx.noise(sigma); rx.nrz_DFE(taps)
    d = sdp.nrz_a2d(rx.signal, SPS, 0.0)[skip:-5]
    counted.append(sdp.prbs_checker(7, sdp.prbs7(1), d)[0] / d.size)
    est.append(ber_q(S[0], A[0], sigma))
nbits = d.size
offs = np.arange(-SPS // 2, SPS // 2)
bt = {s: np.array([ber_q(S[o % SPS], A[o % SPS], s) for o in offs]) for s in (5e-3, 20e-3)}
cnt_o, cnt_b = [], []
for o in range(-24, 25, 4):
    r = sdp.Receiver(rx.signal_org[SPS + o:], SPS, F_NYQ, LEVELS, shift=False)
    r.noise(20e-3); r.nrz_DFE(taps)
    d = sdp.nrz_a2d(r.signal, SPS, 0.0)[skip:-5]
    res = sdp.prbs_checker(7, sdp.prbs7(1), d)
    if res and res[0] > 0:
        cnt_o.append(o / SPS); cnt_b.append(res[0] / d.size)
print("counted", ["%.2e" % c for c in counted], "est", ["%.2e" % e for e in est])
print("bathtub 5 mV: 1e-12 opening %.2f UI" % (np.sum(bt[5e-3] < 1e-12) / SPS))

fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.2), gridspec_kw=dict(width_ratios=[1.45, 1]))
for (s, bb), col in zip(bt.items(), (C1, C2)):
    a.semilogy(offs / SPS, np.maximum(bb, 1e-30), color=col, label=f"estimate, $\\sigma$ = {1e3*s:.0f} mV")
a.semilogy(cnt_o, cnt_b, "o", color=C3, ms=4, label="counted, 20 mV")
a.axhline(1e-12, color=C4, ls="--", lw=0.8)
a.text(0.47, 3e-12, "$10^{-12}$", color=C4, fontsize=7, ha="right", va="bottom")
w = np.sum(bt[5e-3] < 1e-12) / SPS
a.annotate("", xy=(-w / 2, 1e-13), xytext=(w / 2, 1e-13),
           arrowprops=dict(arrowstyle="<->", color=C1, lw=0.8, shrinkA=0, shrinkB=0))
a.text(0, 2.5e-15, f"{w:.2f} UI at $10^{{-12}}$", ha="center", fontsize=7, color=C1)
a.set_xlim(-0.5, 0.5); a.set_ylim(1e-16, 1)
a.legend(loc="center", fontsize=6.8)
finish(a, "Sampling offset from eye center (UI)", "BER")
panel(a, "a")
xs = np.arange(len(sig_list))
b.semilogy(xs, est, "s-", color=C1, ms=4, label="estimate (ber_q)")
cz = np.array(counted)
b.semilogy(xs[cz > 0], cz[cz > 0], "o", color=C3, ms=5, label="counted")
b.semilogy([0], [3 / nbits], "v", color=C3, ms=5, mfc="white")
b.text(0.12, 3 / nbits, "0 errors:\nBER < 3/N", fontsize=6.5, color=C3, va="center")
b.set_xticks(xs); b.set_xticklabels([f"{1e3*s:.0f}" for s in sig_list])
b.set_ylim(1e-13, 1e-2); b.set_xlim(-0.4, 3.4)
b.legend(loc="lower right", fontsize=6.8)
finish(b, "RX noise $\\sigma$ (mV)", "BER at eye center")
panel(b, "b")
savefig(fig, "ch16_lab6")
