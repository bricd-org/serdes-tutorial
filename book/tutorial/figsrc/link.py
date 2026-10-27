"""link.py -- shared 5 Gb/s NRZ link model for every tutorial figure (same numbers as the labs).

Identical channel/CTLE/pulse definitions to tutorial/code/common.py (Chapter 16 labs), plus a
few helpers used by figure scripts. Import with:  from link import *
Conventions (match the text!):
  * p(t) = response to ONE 1-UI pulse of amplitude 1 V; cursors p_k = p(t_s + k*Tb), p_0 = main.
  * TX levels are +-A with A = 0.5 V (1 Vppd); noise-free inner eye (PDA) = 2A(p0 - sum|p_k|).
  * REF channel = channel(REF_LEN) = 1 m synthetic FR-4 + 300 fF pads = -17.4 dB at 2.5 GHz.
  * LOSS_FAMILY maps loss at Nyquist (dB) -> line length (m) for trade-off plots.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from common import *          # noqa: F401,F403  (np, sp, sdp, plt, F, W, DT, SPS, UI, channel, ctle, ...)
import numpy as np
import scipy as sp
from scipy.optimize import brentq

REF_LEN = 1.0
A_TX = 0.5                    # TX amplitude [V] (+-A), 1 Vppd


def loss_db(H, f0=F_NYQ):
    """Insertion loss |H| in dB (negative number) at frequency f0."""
    return 20 * np.log10(np.abs(H[np.argmin(np.abs(F - f0))]))


def length_for_loss(target_db, **kw):
    """Line length [m] that gives `target_db` (positive dB) of loss at Nyquist."""
    return brentq(lambda L: -loss_db(channel(L, **kw)) - target_db, 0.01, 5.0, xtol=1e-4)


# pre-computed with length_for_loss (keeps scripts fast); re-run _make_family() if channel() changes
LOSS_FAMILY = {5: 0.285, 10: 0.572, 15: 0.862, 20: 1.152, 25: 1.441, 30: 1.731}


def _make_family():
    return {d: round(length_for_loss(d), 3) for d in (5, 10, 15, 20, 25, 30)}


def pulse_of(H):
    """(t, p): time axis [s] and 1-UI pulse response [V] for transfer function H on grid F."""
    h, t = impulse(H)
    return t, pulse(h)


def cursors(p, n_pre=2, n_post=10, idx0=None):
    """Sample pulse response every UI around the main cursor.
    idx0: sample index of the main cursor (default: pulse peak). Returns (k, pk, idx0)."""
    if idx0 is None:
        idx0 = int(np.argmax(p))
    k = np.arange(-n_pre, n_post + 1)
    return k, p[idx0 + k * SPS], idx0


def pda_eye(pk, k=None, A=A_TX):
    """Peak-distortion (worst-case) inner eye height [V] = 2A(p0 - sum_{k!=0}|p_k|)."""
    pk = np.asarray(pk)
    if k is None:
        i0 = int(np.argmax(pk))
    else:
        i0 = int(np.where(np.asarray(k) == 0)[0][0])
    return 2 * A * (pk[i0] - (np.sum(np.abs(pk)) - np.abs(pk[i0])))


def prbs_bits(order=13, n=None):
    """PRBS bit array (0/1) from serdespy (order in 7,13,20,22,24,31)."""
    gen = {7: sdp.prbs7, 13: sdp.prbs13, 20: sdp.prbs20, 22: sdp.prbs22, 24: sdp.prbs24, 31: sdp.prbs31}[order]
    b = np.asarray(gen(1), dtype=int)
    return b if n is None else b[:n]


def rx_wave(bits, H, fir=None, jitter_ui=0.0):
    """RX waveform for bit sequence through channel H (optional TX FIR / RJ)."""
    h, _ = impulse(H)
    return through(tx_wave(bits, fir=fir, jitter_ui=jitter_ui), h)


if __name__ == "__main__":
    print("REF loss @2.5GHz:", round(loss_db(channel(REF_LEN)), 2), "dB")
    print("family:", _make_family())
