"""Lab 6 - TX jitter + RX noise: count bit errors and sweep a bathtub curve.

Link = lab 5 (8 dB CTLE + 3-tap DFE). TX random jitter comes from
sdp.Transmitter.gaussian_jitter, RX noise from sdp.Receiver.noise, decisions
from sdp.Receiver.nrz_DFE + sdp.nrz_a2d, and errors are counted with
sdp.prbs_checker. The counted BER is compared with the semi-analytic estimate
(common.ber_q), which also extends the bathtub far below 1e-5.
"""
from common import *

np.random.seed(2026)                       # repeatable jitter and noise
PEAK, N_TAPS, RJ_UI = 8, 3, 0.025          # RJ = 2.5 % UI = 5 ps rms
H = channel()
h_link, t = impulse(H * ctle(PEAK))
cur = sdp.channel_coefficients(pulse(h_link), t, SPS, 1, N_TAPS, res=72)
plt.close("all")
taps = cur[2:]                             # zero-forcing DFE taps h1..h3
bits = np.tile(sdp.prbs7(1), 800)          # 101 600 bits
y = through(tx_wave(bits, jitter_ui=RJ_UI), h_link)   # TX RJ -> channel -> CTLE
print(f"{bits.size} bits, TX RJ = {RJ_UI*UI*1e12:.1f} ps rms, "
      f"DFE taps = {np.round(taps, 4)}")

# 1) Noise-free DFE eye with TX jitter (per-phase samples feed the bathtub)
rx = sdp.Receiver(y, SPS, F_NYQ, LEVELS, shift=True)  # sampling phase -> index 0
rx.nrz_DFE(taps)
hts, ph, S, A = report_eye("With 5 ps TX RJ, no noise", rx.signal, bits)

# 2) Count errors at the eye centre vs RX noise; compare with the estimate
skip = 50                                  # ignore the start-up transient
for sigma in (10e-3, 15e-3, 20e-3, 25e-3):
    rx.noise(sigma)                        # resets to pre-DFE signal + AWGN
    rx.nrz_DFE(taps)                       # real decisions: error propagation
    d = sdp.nrz_a2d(rx.signal, SPS, 0.0)[skip:-5]
    n_err = sdp.prbs_checker(7, sdp.prbs7(1), d)[0]
    est = ber_q(S[0], A[0], sigma)
    print(f"sigma = {1e3*sigma:4.1f} mV: counted {n_err:3d} errors / {d.size} "
          f"-> BER = {n_err/d.size:.2e}; estimate = {est:.2e} "
          f"(= {est*d.size:.2f} errors expected)")
    if sigma == 15e-3:
        save_eye(rx.signal, 0, "5 ps RJ + 15 mV rms noise, after DFE",
                 "lab6_eye_jitter_noise.png")

# 3) Bathtub: BER vs sampling offset. Estimate at every phase; count at some.
offs = np.arange(-SPS // 2, SPS // 2)
bt = {s: np.array([ber_q(S[o % SPS], A[o % SPS], s) for o in offs])
      for s in (5e-3, 20e-3)}
cnt_o, cnt_b = [], []
for o in range(-24, 25, 4):                # re-sample with DFE at offset o
    r = sdp.Receiver(rx.signal_org[SPS + o:], SPS, F_NYQ, LEVELS, shift=False)
    r.noise(20e-3); r.nrz_DFE(taps)
    d = sdp.nrz_a2d(r.signal, SPS, 0.0)[skip:-5]
    res = sdp.prbs_checker(7, sdp.prbs7(1), d)
    if res and res[0] > 0:                 # False if the checker cannot lock
        cnt_o.append(o / SPS); cnt_b.append(res[0] / d.size)
for s, b in bt.items():
    print(f"sigma = {1e3*s:.0f} mV: horizontal opening at BER 1e-12 = "
          f"{np.sum(b < 1e-12)/SPS:.2f} UI, at 1e-5 = {np.sum(b < 1e-5)/SPS:.2f} UI,"
          f" BER at centre = {b[SPS//2]:.1e}")
print("counted (20 mV):", ", ".join(f"{o:+.3f} UI: {b:.1e}" for o, b in zip(cnt_o, cnt_b)))

fig, ax = plt.subplots(figsize=(6, 3.8))
for (s, b), col in zip(bt.items(), COLORS):
    ax.semilogy(offs / SPS, np.maximum(b, 1e-30), color=col, lw=1.5,
                label=f"estimate, sigma = {1e3*s:.0f} mV")
ax.semilogy(cnt_o, cnt_b, "o", ms=6, color=COLORS[2], label="counted, 20 mV")
ax.axhline(1e-12, color="grey", ls="--", lw=1)
ax.set(xlim=(-0.5, 0.5), ylim=(1e-16, 1), ylabel="BER",
       xlabel="Sampling offset from eye centre [UI]",
       title="Bathtub: 5 ps RJ, CTLE 8 dB + 3-tap DFE")
ax.legend(loc="center")                    # empty area between the curves
fig.tight_layout(); fig.savefig("lab6_bathtub.png"); plt.close(fig)
