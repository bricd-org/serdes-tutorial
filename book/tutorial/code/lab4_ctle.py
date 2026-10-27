"""Lab 4 - CTLE design: one zero, two poles, sweep the peaking.

serdespy has no CTLE object: as in its example 2_ctle.py, the CTLE is a
transfer function evaluated with scipy.signal.freqs on the channel's frequency
grid, cascaded with the channel and turned into an impulse response with
sdp.freq2impulse. Model (source-degenerated CML pair, see common.ctle):
    H(s) = (1/A) (1 + s/wz) / ((1 + s/wp1)(1 + s/wp2)),  wz = wp1/A
High-frequency gain is 0 dB, DC gain is -A dB, so eye heights compare fairly.
"""
from common import *

FP1, FP2 = 2.5e9, 10e9                    # pole 1 at Nyquist, output pole 10 GHz
H = channel()
bits = np.tile(sdp.prbs7(1), 40)
x = tx_wave(bits)

# 1) Sweep the peaking and measure the eye at the CTLE output
peaks, eh, ew = np.arange(0, 21, 2), [], []
for pk in peaks:
    h_link, t = impulse(H * ctle(pk, FP1, FP2))   # channel x CTLE
    hts, ph, S, A = eye_scan(through(x, h_link), bits)
    eh.append(hts[ph]); ew.append(np.sum(hts > 0) / SPS)
    print(f"peaking {pk:2d} dB (fz = {FP1/10**(pk/20)/1e9:.3f} GHz): "
          f"eye height {1e3*eh[-1]:7.1f} mV, width {ew[-1]:.2f} UI")
best = peaks[int(np.argmax(eh))]
print(f"Best peaking = {best} dB")

# 2) CTLE magnitude responses
fig, ax = plt.subplots(figsize=(6, 3.6))
for pk, col in zip((4, 8, best), COLORS):
    ax.semilogx(F / 1e9, 20 * np.log10(np.abs(ctle(pk, FP1, FP2))), color=col,
                lw=1.5, label=f"{pk} dB peaking")
ax.axvline(F_NYQ / 1e9, color="grey", ls="--", lw=1, label="Nyquist")
ax.set(xlim=(0.01, 100), ylim=(-25, 3), xlabel="Frequency [GHz]",
       ylabel="Magnitude [dB]", title="CTLE responses (HF gain = 0 dB)")
ax.legend(loc="lower right")
fig.tight_layout(); fig.savefig("lab4_ctle_bode.png"); plt.close(fig)

# 3) Eye height vs peaking (one series, one axis)
fig, ax = plt.subplots(figsize=(6, 3.2))
ax.plot(peaks, 1e3 * np.array(eh), "o-", color=COLORS[0], lw=1.5, ms=6)
ax.axhline(0, color="grey", lw=1)
ax.set(xlabel="CTLE peaking [dB]", ylabel="Eye height [mV]",
       title="Eye height at CTLE output vs peaking")
fig.tight_layout(); fig.savefig("lab4_eye_vs_peaking.png"); plt.close(fig)

# 4) Best CTLE: response at Nyquist, cursors, and eye
Hc = ctle(best, FP1, FP2)
i_nyq = np.argmin(np.abs(F - F_NYQ))
print(f"Nominal peaking A = wp1/wz = {best} dB; actual peak/DC = "
      f"{20*np.log10(np.abs(Hc).max()/abs(Hc[0])):.2f} dB at "
      f"{F[np.argmax(np.abs(Hc))]/1e9:.2f} GHz (the 2nd pole eats some)")
print(f"CTLE gain at DC {20*np.log10(abs(Hc[0])):.2f} dB, at Nyquist "
      f"{20*np.log10(abs(Hc[i_nyq])):.2f} dB; channel x CTLE at Nyquist "
      f"{20*np.log10(abs(H[i_nyq]*Hc[i_nyq])):.2f} dB (DC {20*np.log10(abs(H[0]*Hc[0])):.2f} dB)")
h_link, t = impulse(H * Hc)
cur = sdp.channel_coefficients(pulse(h_link), t, SPS, 1, 5, res=150,
                               title=f"Pulse response, channel + {best} dB CTLE")
plt.close("all")
print("Cursors h-1..h+5 with best CTLE =", np.round(cur, 4))
y = through(x, h_link)
hts, ph, S, A = report_eye(f"Channel + {best} dB CTLE", y, bits)
save_eye(y, ph, f"Eye after channel + {best} dB CTLE", "lab4_eye_ctle.png")

# 5) What it means for the circuit: degenerated pair with gm, RS, CS, RD, CL
gm, a = 20e-3, 10**(best / 20)            # example: gm = 20 mS per side
RS = 2 * (a - 1) / gm                     # A = 1 + gm*RS/2
CS = 1 / (RS * 2 * np.pi * FP1 / a)       # wz = 1/(RS*CS)
RD, CL = 1 / gm, 1 / (2 * np.pi * FP2 / gm)   # gm*RD = 1, wp2 = 1/(RD*CL)
print(f"Circuit (gm = 20 mS): RS = {RS:.0f} ohm, CS = {CS*1e12:.3f} pF, "
      f"RD = {RD:.0f} ohm, CL = {CL*1e15:.0f} fF")
