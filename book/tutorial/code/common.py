"""common.py - shared set-up for the Open-SERDES serdespy labs (5 Gb/s NRZ).

Channel = 50-ohm source | pad C | 1 m lossy FR-4 line | pad C | 50-ohm load,
built from serdespy's ABCD-matrix (chmodel) functions. Every lab starts with
`from common import *`.
"""
import numpy as np
if not hasattr(np, "complex_"):   # serdespy 1.0 uses np.complex_, which
    np.complex_ = np.complex128   # NumPy 2.x removed -> add it back (shim)
import matplotlib
matplotlib.use("Agg")             # no GUI windows: every figure goes to a PNG
import matplotlib.pyplot as plt
import scipy as sp
import scipy.signal, scipy.special
import serdespy as sdp

plt.rcParams.update({"figure.dpi": 150, "axes.grid": True, "grid.color": "#dddddd",
                     "axes.spines.top": False, "axes.spines.right": False})
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]   # series 1, 2, 3 (fixed order)

BIT_RATE = 5e9                    # [b/s]
UI = 1 / BIT_RATE                 # 200 ps
F_NYQ = BIT_RATE / 2              # 2.5 GHz (sdp.Transmitter expects THIS value)
SPS = 64                          # samples per UI (oversampling ratio)
DT = UI / SPS                     # 3.125 ps simulation time step
DF = 10e6                         # 10 MHz step -> 100 ns impulse-response window
F = np.arange(0, 1 / (2 * DT) + DF / 2, DF)   # 0..160 GHz, must start at DC
W = 2 * np.pi * F                 # [rad/s]
LEVELS = np.array([-0.5, 0.5])    # TX levels [V] for bits 0/1 (1 Vppd)

def channel(length=1.0, kr=60.0, rdc=7.0, tand=0.02, er=4.0, z0=50.0, c_pad=300e-15):
    """S21(f) of the synthetic channel. kr = skin-effect R [ohm/m] at 1 GHz."""
    v = 2.998e8 / np.sqrt(er)                     # propagation velocity [m/s]
    w0 = 2 * np.pi * 1e9                          # loss parameters given at 1 GHz
    R = np.sqrt(rdc**2 + (kr * (1 + 1j) * np.sqrt(W / w0))**2)  # ~sqrt(f) loss
    with np.errstate(divide="ignore", invalid="ignore"):        # causal dielectric:
        C = (1 / (z0 * v)) * (1j * W / w0)**(-2 * tand / np.pi)  # loss ~ f
    C[0] = C[1]                                   # 0**(-x) undefined at DC
    L, G = np.full(F.size, z0 / v), np.full(F.size, 1e-12)  # G>0 keeps DC finite
    line = sdp.rlgc(R, L, G, C, length, F)        # ABCD of the line
    src = sdp.impedance(np.full(F.size, z0))      # series source resistance
    pad = sdp.shunt_cap(c_pad, 1j * W)            # NB: pass s = j*omega
    load = sdp.admittance(np.full(F.size, 1 / z0))  # shunt termination
    abcd = sdp.series(np.array([src, pad, line, pad, load]))
    return 2 / abcd[:, 0, 0]                      # 2*Vout/Vsrc = S21 (DC ~ 1)

def ctle(peak_db, fp1=2.5e9, fp2=10e9):
    """CML CTLE: H(s) = (1/A)(1+s/wz)/((1+s/wp1)(1+s/wp2)), wz = wp1/A.
    High-frequency gain = 1 (0 dB); DC gain = -peak_db."""
    a = 10**(peak_db / 20)
    wz, wp1, wp2 = 2 * np.pi * fp1 / a, 2 * np.pi * fp1, 2 * np.pi * fp2
    num, den = np.array([1 / wz, 1]) / a, np.polymul([1 / wp1, 1], [1 / wp2, 1])
    return sp.signal.freqs(num, den, W)[1]        # evaluate on the same grid F

def impulse(H):
    """Impulse response h (per time step DT, sum(h) = H(0)) and time axis t."""
    return sdp.freq2impulse(H, F)

def pulse(h):
    """1-UI pulse response = impulse response convolved with SPS ones."""
    return sp.signal.fftconvolve(h, np.ones(SPS))[:h.size]

def tx_wave(bits, fir=None, jitter_ui=0.0):
    """Oversampled TX waveform via sdp.Transmitter (optional FIR and RJ)."""
    tx = sdp.Transmitter(bits, LEVELS, F_NYQ)     # 3rd arg: UI = 1/(2*F_NYQ)
    if fir is not None:
        tx.FIR(fir)                               # must come before oversample()
    tx.oversample(SPS)
    if jitter_ui > 0:
        tx.gaussian_jitter(stdev_div_UI=jitter_ui)
        return tx.signal
    return tx.signal_ideal

def through(x, h):
    """Causal convolution of waveform x with impulse response h."""
    return sp.signal.fftconvolve(x, h)[:x.size]

def eye_scan(y, bits, skip=100):
    """Noise-free inner eye height [V] at each of the SPS phases of a UI, using
    the known bits (aligned by cross-correlation). Returns heights, the best
    phase, and per-phase lists S[ph], A[ph] of samples and +-1 symbols."""
    a_all, hts, S, A = 2.0 * bits - 1, [], [], []
    for ph in range(SPS):
        s = y[ph::SPS]
        lag = np.argmax(sp.signal.correlate(s, a_all, method="fft")) - a_all.size + 1
        k = np.arange(max(lag, 0) + skip, min(s.size, a_all.size + lag) - 5)
        S.append(s[k]); A.append(a_all[k - lag])
        hts.append(S[-1][A[-1] > 0].min() - S[-1][A[-1] < 0].max())
    hts = np.array(hts)
    return hts, int(np.argmax(hts)), S, A

def report_eye(name, y, bits):
    hts, ph, S, A = eye_scan(y, bits)
    print(f"{name:26s} eye height {1e3 * hts[ph]:7.1f} mV, "
          f"eye width {np.sum(hts > 0) / SPS:.2f} UI")
    return hts, ph, S, A

def save_eye(y, phase, title, fname, ntraces=600, skip=100):
    """serdespy eye diagram, 2-UI window centred on `phase`, saved as PNG."""
    sdp.simple_eye(y[phase + skip * SPS:], 2 * SPS, ntraces, DT, title,
                   res=150, linewidth=0.3)
    plt.savefig(fname)
    plt.close("all")

def ber_q(s, a, sigma):
    """Semi-analytic BER: mean of Q(margin/sigma) over all simulated samples."""
    return np.mean(0.5 * sp.special.erfc(a * s / (sigma * np.sqrt(2))))
