"""Lab 2 - PRBS-7 NRZ through the channel: eye diagram before and after.

sdp.prbs7 makes the bit pattern, sdp.Transmitter turns it into an oversampled
NRZ waveform (64 samples/UI), and the waveform is convolved with the channel
impulse response. sdp.simple_eye draws the eyes; eye height and width are
measured with common.eye_scan (serdespy has no eye-measurement routine).
"""
from common import *

prbs = sdp.prbs7(1)                       # one period: 127 bits, seed = 1
bits = np.tile(prbs, 40)                  # 5080 bits = 1.016 us of data
print(f"PRBS-7 period = {prbs.size} bits, ones = {prbs.sum()}, "
      f"simulated bits = {bits.size}")

# TX: ideal (zero rise-time) NRZ waveform, +-0.5 V levels
tx = sdp.Transmitter(bits, LEVELS, F_NYQ)  # NB: 3rd argument = Nyquist frequency
tx.oversample(SPS)
x = tx.signal_ideal
print(f"Transmitter UI = {tx.UI*1e12:.1f} ps, samples = {x.size}")

# Channel: y = x * h (causal convolution)
H = channel()
h, t = impulse(H)
y = through(x, h)

# Eye measurements (noise-free, inner eye over the simulated pattern)
hts_tx, ph_tx, _, _ = report_eye("TX output", x, bits)
hts_rx, ph_rx, S, A = report_eye("Channel output", y, bits)
print(f"Channel output: best sampling phase = {ph_rx}/{SPS} of a UI, "
      f"mean '1' level = {S[ph_rx][A[ph_rx] > 0].mean()*1e3:.1f} mV, "
      f"mean '0' level = {S[ph_rx][A[ph_rx] < 0].mean()*1e3:.1f} mV")

# Eye diagrams (2-UI window, centred on the best sampling phase)
save_eye(x, SPS // 2, "TX eye, 5 Gb/s PRBS-7", "lab2_eye_tx.png")  # flat: use mid-bit
save_eye(y, ph_rx, "Eye after 1 m channel (17.4 dB @ 2.5 GHz)", "lab2_eye_rx.png")

# Short waveform snippet: TX vs RX (shifted by the channel delay)
delay = np.argmax(pulse(h)) - SPS // 2    # pulse peak ~ centre of the bit
n = 40 * SPS
tt = np.arange(n) * DT * 1e9
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(tt, x[200 * SPS:200 * SPS + n], color=COLORS[1], lw=1.2, label="TX")
ax.plot(tt, y[200 * SPS + delay:200 * SPS + delay + n], color=COLORS[0], lw=1.5,
        label="RX (delay removed)")
ax.set(xlabel="Time [ns]", ylabel="Voltage [V]", title="40 bits of PRBS-7")
ax.legend(loc="upper right")
fig.tight_layout(); fig.savefig("lab2_waveforms.png"); plt.close(fig)
print(f"Channel delay (pulse peak - UI/2) = {delay*DT*1e9:.3f} ns")
