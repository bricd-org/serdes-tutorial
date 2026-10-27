"""Lab 3 - Zero-forcing TX FFE (3 taps: pre, main, post) from the pulse response.

sdp.forcing_ffe solves the zero-forcing equations for the tap weights;
the taps are then rescaled so sum|c| = 1 (the driver cannot exceed its peak
swing) and applied with sdp.Transmitter.FIR. A 2-tap (main + post) version is
included for comparison.
"""
from common import *

H = channel()
h, t = impulse(H)
p = pulse(h)

# 1) Cursors h[-1], h[0], h[1] of the unequalised pulse response
cur = sdp.channel_coefficients(p, t, SPS, 1, 1, res=150)
plt.close("all")
print("Unequalised cursors h-1, h0, h1 =", np.round(cur, 4))

# 2) Zero-forcing taps: force h-1 and h+1 to zero (main tap returned as 1)
c3 = sdp.forcing_ffe(1, cur)              # [c-1, c0, c+1], c0 = 1
c3 = c3 / np.sum(np.abs(c3))              # peak-swing constraint sum|c| = 1
c2 = sdp.forcing_ffe(0, cur[1:])          # [c0, c+1]: classic de-emphasis
c2 = c2 / np.sum(np.abs(c2))
for name, c in (("3-tap", c3), ("2-tap", c2)):
    boost = 20 * np.log10(np.sum(np.abs(c)) / abs(np.sum(c)))  # Nyquist vs DC
    print(f"{name} TX FFE taps = {np.round(c, 4)}, "
          f"DC gain = {np.sum(c):.3f}, Nyquist/DC boost = {boost:.2f} dB")

# 3) Pulse response with the 3-tap FFE in front of the channel
p3 = sp.signal.fftconvolve(h, np.repeat(c3, SPS))[:h.size]
cur3 = sdp.channel_coefficients(p3, t, SPS, 2, 6, res=150,
                                title="Pulse response with 3-tap TX FFE")
plt.gca().grid(False, axis="x")
plt.savefig("lab3_cursors_ffe.png"); plt.close("all")
print("Cursors with 3-tap FFE h-2..h+6 =", np.round(cur3, 4), "(at new peak)")
k_zf = np.argmax(p) + SPS                 # ZF design phase (old peak + 1 UI)
print("Same, at the ZF design phase    =", np.round(p3[k_zf + SPS * np.arange(-2, 7)], 4))
print(f"Main cursor {cur[1]:.4f} V -> {cur3[2]:.4f} V "
      f"(the price of equalising at the TX)")

# 4) Frequency view: FFE response C(f) = sum_k c_k exp(-j 2 pi f k UI)
C3 = np.exp(-2j * np.pi * np.outer(F, np.arange(3)) * UI) @ c3
fig, ax = plt.subplots(figsize=(6, 3.6))
for Hx, lab, col in ((H, "Channel", COLORS[0]), (C3, "3-tap FFE", COLORS[1]),
                     (H * C3, "FFE x channel", COLORS[2])):
    ax.plot(F / 1e9, 20 * np.log10(np.abs(Hx)), color=col, lw=1.5, label=lab)
ax.axvline(F_NYQ / 1e9, color="grey", ls="--", lw=1)
ax.set(xlim=(0, 5), ylim=(-35, 2), xlabel="Frequency [GHz]",
       ylabel="Magnitude [dB]", title="TX FFE flattens the response to Nyquist")
ax.legend()
fig.tight_layout(); fig.savefig("lab3_freq.png"); plt.close(fig)

# 5) Time-domain eyes: no FFE, 2-tap, 3-tap (TX.FIR is called inside tx_wave)
bits = np.tile(sdp.prbs7(1), 40)
for name, c, png in ((None, None, None), ("2-tap", c2, None),
                     ("3-tap", c3, "lab3_eye_ffe3.png")):
    y = through(tx_wave(bits, fir=c), h)
    hts, ph, S, A = report_eye(f"Channel + {name or 'no'} FFE", y, bits)
    if png:
        save_eye(y, ph, "Eye with 3-tap ZF TX FFE", png)
