"""Lab 1 - Channel: frequency response, impulse response, pulse response, cursors.

Builds the synthetic 1 m FR-4 channel (see common.channel), plots |H(f)| with
the 2.5 GHz Nyquist marker, converts it to an impulse response with
sdp.freq2impulse and measures the pulse-response cursors with
sdp.channel_coefficients.
"""
from common import *

H = channel()                                  # complex S21 on the grid F
H_db = 20 * np.log10(np.abs(H))
i_nyq = np.argmin(np.abs(F - F_NYQ))
print(f"Frequency grid: {F.size} points, df = {DF/1e6:.0f} MHz, "
      f"fmax = {F[-1]/1e9:.0f} GHz -> dt = {DT*1e12:.3f} ps")
print(f"|H| at DC = {H_db[0]:.2f} dB, at 1.25 GHz = "
      f"{H_db[np.argmin(np.abs(F - 1.25e9))]:.2f} dB, "
      f"at Nyquist 2.5 GHz = {H_db[i_nyq]:.2f} dB, at 5 GHz = "
      f"{H_db[np.argmin(np.abs(F - 5e9))]:.2f} dB")

# 1) Bode magnitude plot (0-10 GHz is the interesting part for 5 Gb/s)
fig, ax = plt.subplots(figsize=(6, 3.6))
ax.plot(F / 1e9, H_db, color=COLORS[0], lw=1.5, label="Channel |S21|")
ax.axvline(F_NYQ / 1e9, color="grey", ls="--", lw=1, label="Nyquist 2.5 GHz")
ax.plot(F_NYQ / 1e9, H_db[i_nyq], "o", ms=6, color=COLORS[0])
ax.annotate(f"{H_db[i_nyq]:.1f} dB", (F_NYQ / 1e9, H_db[i_nyq]),
            xytext=(8, 8), textcoords="offset points")
ax.set(xlim=(0, 10), ylim=(-45, 2), xlabel="Frequency [GHz]",
       ylabel="Magnitude [dB]", title="Synthetic 1 m FR-4 channel")
ax.legend()
fig.tight_layout(); fig.savefig("lab1_bode.png"); plt.close(fig)

# 2) Impulse response: IFFT of the Hermitian-extended H (serdespy)
h, t = impulse(H)                              # h is per-sample: sum(h) = H(0)
print(f"Impulse response: {h.size} samples, dt = {t[1]*1e12:.3f} ps, "
      f"sum(h) = {h.sum():.4f}, peak at t = {t[np.argmax(h)]*1e9:.3f} ns")

# 3) Pulse response = response to one 200 ps wide, 1 V pulse
p = pulse(h)
k0 = np.argmax(p)
print(f"Pulse peak (main cursor) at t = {t[k0]*1e9:.3f} ns")
fig, ax = plt.subplots(figsize=(6, 3.6))
ax.plot(t * 1e9, h / h.max(), color=COLORS[1], lw=1.2, label="Impulse (normalised)")
ax.plot(t * 1e9, p, color=COLORS[0], lw=1.5, label="1-UI pulse response [V]")
ax.set(xlim=(t[k0] * 1e9 - 1.5, t[k0] * 1e9 + 4), xlabel="Time [ns]",
       ylabel="Amplitude", title="Impulse and pulse response")
ax.legend()
fig.tight_layout(); fig.savefig("lab1_impulse_pulse.png"); plt.close(fig)

# 4) Cursor values sampled every UI from the peak (serdespy makes the figure)
n_pre, n_post = 2, 10
cur = sdp.channel_coefficients(p, t, SPS, n_pre, n_post, res=150,
                               title="Pulse response and cursors")
plt.gca().grid(False, axis="x")                # serdespy already draws UI lines
plt.savefig("lab1_cursors.png"); plt.close("all")
for i, c in enumerate(cur):
    print(f"  h[{i - n_pre:+d}] = {c:+.4f} V")
isi = np.sum(np.abs(cur)) - cur[n_pre]
print(f"Main cursor h0 = {cur[n_pre]:.4f} V, sum|ISI| (h-2..h+10) = {isi:.4f} V,"
      f" h1/h0 = {cur[n_pre + 1] / cur[n_pre]:.3f}")
print(f"Peak-distortion eye (1 V swing, {n_pre}+{n_post} cursors) = "
      f"{cur[n_pre] - isi:+.4f} V  (negative = closed)")
