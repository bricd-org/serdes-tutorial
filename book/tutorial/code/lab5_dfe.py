"""Lab 5 - DFE: taps from the post-cursors, eye after DFE, BER estimate.

A moderate 8 dB CTLE leaves post-cursor ISI that a DFE cancels. The DFE taps
are the post-cursors read off the pulse response (zero-forcing DFE). The DFE
itself is serdespy's behavioural model sdp.Receiver.nrz_DFE, which slices at
every UI and subtracts sum(tap_k * level[decision_{n-k}]) from the next UI.
The BER estimate is semi-analytic (common.ber_q): Gaussian noise of rms sigma
at the slicer, averaged over every simulated ISI pattern.
"""
from common import *

PEAK = 8                                   # CTLE peaking [dB] (lab 4 model)
H = channel()
bits = np.tile(sdp.prbs7(1), 40)
h_link, t = impulse(H * ctle(PEAK))        # channel x CTLE
y = through(tx_wave(bits), h_link)         # CTLE output waveform

# 1) Cursors of the CTLE-equalised pulse: h[-1], h[0], h[1..8]
cur = sdp.channel_coefficients(pulse(h_link), t, SPS, 1, 8, res=150,
                               title=f"Pulse response: channel + {PEAK} dB CTLE")
plt.gca().grid(False, axis="x")
plt.savefig("lab5_cursors.png"); plt.close("all")
h_pre, h0, post = cur[0], cur[1], cur[2:]
print(f"h-1 = {h_pre:.4f} V, h0 = {h0:.4f} V")
print("post-cursors h1..h8 =", np.round(post, 4))

# 2) Eye height vs number of DFE taps (taps = post-cursors, in volts per 1 V
#    pulse; serdespy multiplies them by the decided level, here +-0.5 V)
for n in (0, 1, 2, 3, 4, 5, 8):
    rx = sdp.Receiver(y, SPS, F_NYQ, LEVELS, shift=True)  # centre eye at 0
    if n:
        rx.nrz_DFE(post[:n])
    report_eye(f"CTLE {PEAK} dB + {n}-tap DFE", rx.signal, bits)

# 3) Final design: 3 DFE taps
N_TAPS = 3
taps = post[:N_TAPS]
print(f"Chosen DFE taps = {np.round(taps, 4)} V "
      f"(feedback per tap = +-{0.5*1e3*taps[0]:.1f}, +-{0.5*1e3*taps[1]:.1f}, "
      f"+-{0.5*1e3*taps[2]:.1f} mV)")
rx = sdp.Receiver(y, SPS, F_NYQ, LEVELS, shift=True)
hts0, ph0, _, _ = eye_scan(rx.signal, bits)
save_eye(rx.signal, ph0, f"Before DFE ({PEAK} dB CTLE)", "lab5_eye_before_dfe.png")
rx.nrz_DFE(taps)
hts, ph, S, A = eye_scan(rx.signal, bits)
save_eye(rx.signal, ph, f"After {N_TAPS}-tap DFE", "lab5_eye_after_dfe.png")
residual = h_pre**2 + np.sum(post[N_TAPS:]**2)
print(f"Residual ISI rms (h-1 and h{N_TAPS+1}..h8, +-0.5 V data) = "
      f"{1e3*0.5*np.sqrt(residual):.2f} mV")

# 4) Semi-analytic BER at the slicer for several noise levels
print(f"Eye height {1e3*hts[ph]:.1f} mV at phase {ph}/{SPS}; "
      f"mean signal level {1e3*np.mean(A[ph]*S[ph]):.1f} mV")
for sigma in (5e-3, 10e-3, 15e-3, 20e-3):
    ber = ber_q(S[ph], A[ph], sigma)
    q = hts[ph] / 2 / sigma
    print(f"  sigma = {1e3*sigma:4.1f} mV: worst-case Q = {q:5.2f}, "
          f"estimated BER = {ber:.2e}")

# 5) Decisions of a noise-free run: check with the serdespy PRBS checker
rx_bits = sdp.nrz_a2d(rx.signal, SPS, 0.0)[50:-5]   # slice every UI at 0 V
err = sdp.prbs_checker(7, sdp.prbs7(1), rx_bits)
print(f"PRBS checker (noise-free): {err[0]} errors in {rx_bits.size} bits")
