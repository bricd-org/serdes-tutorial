"""ch08_dfe.py -- figures for Chapter 8 (DFE and adaptation).

ch08_cancel : REF + 8 dB CTLE pulse, the 2-tap DFE feedback, and what is left
ch08_sslms  : sign-sign LMS adaptation of a 2-tap DFE (REF + 8 dB CTLE), and the pre-cursor pitfall
ch08_taps   : eye height vs number of DFE taps (Lab 5 numbers) and the eye before/after a 2-tap DFE
"""
from bricdstyle import *
from link import *

PEAK = 8
H = channel(REF_LEN)
hl, t = impulse(H * ctle(PEAK))
pl = pulse(hl)
i0 = int(np.argmax(pl))
k, cur, _ = cursors(pl, 1, 8)
h_pre, h0, post = cur[0], cur[1], cur[2:]
print("cursors", np.round(cur, 4))

# ------------------------------------------------------------------ ch08_cancel
tu = (np.arange(pl.size) - i0) / SPS
mm = (tu > -2) & (tu < 7)
fb = np.zeros_like(pl)
for j, wj in enumerate(post[:2], start=1):     # feedback held for one UI around cursor j
    fb[(tu >= j - 0.5) & (tu < j + 0.5)] = wj
res = pl - fb
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.25), gridspec_kw=dict(width_ratios=[1.25, 1]))
a1.plot(tu[mm], pl[mm], color=NAVY, lw=1.0, ls="--", label="pulse at DFE input")
a1.fill_between(tu[mm], 0, fb[mm], color=C2, alpha=0.25, lw=0, step=None)
a1.plot(tu[mm], fb[mm], color=C2, lw=1.2, label="DFE feedback $w_1, w_2$")
a1.plot(tu[mm], res[mm], color=C3, lw=1.5, label="after subtraction")
kk = np.arange(-1, 7)
a1.plot(kk, res[i0 + kk * SPS], "o", color=C3, ms=3.5, zorder=5)
note(a1, (1, 0.0), "$h_1, h_2 \\rightarrow 0$\nat the sampling instants", (2.3, 0.10), color=C3, fs=7)
note(a1, (-1, h_pre), "pre-cursor\nuntouched", (-1.9, 0.10), color=C4, fs=7)
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_xlim(-2, 7); a1.set_ylim(-0.03, 0.2)
a1.legend(loc="upper right", fontsize=7)
finish(a1, "Time from main cursor (UI)", "Pulse response (V)")
panel(a1, "a")
kk = np.arange(-1, 9)
after = cur.copy(); after[2:4] = 0
w = 0.36
for kx, b, a in zip(kk, cur, after):
    a2.bar(kx - w / 2, b, w, color=PALE, lw=0)
    col = GOLD if kx == 0 else (C4 if kx < 0 else (C3 if kx > 2 else C1))
    a2.bar(kx + w / 2, a, w, color=col, lw=0)
from matplotlib.patches import Patch
a2.legend(handles=[Patch(color=PALE, label="before DFE"), Patch(color=C3, label="after 2-tap DFE")],
          loc="upper right", fontsize=7)
for kx in (1, 2):
    a2.text(kx, cur[kx + 1] + 0.004, f"{cur[kx+1]:.3f}", ha="center", fontsize=6.5, color=MUTED)
a2.text(0, h0 + 0.004, f"{h0:.3f}", ha="center", fontsize=6.5, color=GOLDDK)
a2.set_xticks(kk); a2.set_xticklabels([f"{x:+d}" if x else "0" for x in kk])
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_ylim(0, 0.2)
finish(a2, "Cursor $k$ (UI)", "Cursor (V)")
panel(a2, "b")
savefig(fig, "ch08_cancel")

# ------------------------------------------------------------------ ch08_sslms
def sslms(y, a, ntap, mu, mu_d, d0, n):
    """Baud-rate DFE with sign-sign LMS. y: samples, a: true symbols (only for checking)."""
    wv = np.zeros(ntap); d = d0
    W = np.zeros((n, ntap)); D = np.zeros(n); errs = 0
    dec = np.zeros(n)
    for i in range(n):
        past = np.array([dec[i - j] if i - j >= 0 else 0.0 for j in range(1, ntap + 1)])
        z = y[i] - wv @ past
        dec[i] = 1.0 if z >= 0 else -1.0
        errs += dec[i] != a[i]
        e = z - d * dec[i]
        s = 1.0 if e >= 0 else -1.0
        wv += mu * s * past
        d += mu_d * s * dec[i]
        W[i] = wv; D[i] = d
    return W, D, errs

rng = np.random.default_rng(13)
bits = prbs_bits(13)
N = 6000
y = through(tx_wave(bits), hl)
ys = y[i0::SPS][:N] + rng.normal(0, 4e-3, N)        # sample at the main-cursor phase, 4 mV rms noise
asym = 2.0 * bits[:N] - 1
Wr, Dr, er = sslms(ys, asym, 2, 0.25e-3, 0.25e-3, 0.05, N)
print("REF SS-LMS final (mV)", np.round(1e3 * Wr[-1], 1), round(1e3 * Dr[-1], 1), "targets", np.round(1e3 * A_TX * post[:2], 1),
      round(1e3 * A_TX * h0, 1), "errors", er)
i90 = [int(np.argmax(np.abs(Wr[:, j] - A_TX * post[j]) < 2e-3)) for j in range(2)]
print("first within 2 mV at UI", i90)
# pitfall: the Worked Example 6.2 pulse, with and without its 0.2 pre-cursor
def example_samples(pre, n, sigma=10e-3, seed=3):
    r = np.random.default_rng(seed)
    a_ = 2.0 * prbs_bits(13)[:n + 10] - 1
    x = {-1: pre, 0: 0.85, 1: -0.2, 2: 0.1, 3: 0.05}
    yv = np.zeros(n)
    for i in range(n):
        yv[i] = A_TX * sum(v * a_[i + 4 - kk] for kk, v in x.items())
    return yv + r.normal(0, sigma, n), a_[4:4 + n]
NL = 6000
y1, a1_ = example_samples(0.0, NL); Wa, Da, ea = sslms(y1, a1_, 3, 2e-3, 2e-3, 0.3, NL)
y2, a2_ = example_samples(0.2, NL); Wb, Db, eb = sslms(y2, a2_, 3, 2e-3, 2e-3, 0.3, NL)
print("Example no-pre final", np.round(Wa[-1], 3), "with pre final", np.round(Wb[-1], 3), "errors", ea, eb)
print("with pre: w2 range after 2000 UI", Wb[2000:, 1].min(), Wb[2000:, 1].max(), " w1", Wb[2000:, 0].min(), Wb[2000:, 0].max())
print("no pre: w2 range after 2000 UI", Wa[2000:, 1].min(), Wa[2000:, 1].max())

fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.25))
ui = np.arange(N)
for j, col, lab in ((0, C1, "$w_1$"), (1, C3, "$w_2$")):
    a1.plot(ui, 1e3 * Wr[:, j], color=col, lw=1.0, label=lab)
    a1.axhline(1e3 * A_TX * post[j], color=col, ls="--", lw=0.8)
a1.plot(ui, 1e3 * Dr, color=C2, lw=1.0, label="data level $d_\\mathrm{lev}$")
a1.axhline(1e3 * A_TX * h0, color=C2, ls="--", lw=0.8)
a1.plot([], [], color=MUTED, ls="--", lw=0.8, label="targets $Ap_0, Ap_1, Ap_2$")
a1.set_xlim(0, N); a1.set_ylim(0, 110)
a1.legend(loc="center right", fontsize=7, bbox_to_anchor=(1.0, 0.62))
finish(a1, "Time (UI)", "Tap value (mV)")
a1.set_title("REF + 8 dB CTLE, 2-tap DFE", loc="left", fontsize=8)
panel(a1, "a")
ul = np.arange(NL)
for W_, col, lab in ((Wa, C3, "pre-cursor removed"), (Wb, C4, "pre-cursor 0.2 left in")):
    a2.plot(ul, 1e3 * W_[:, 1], color=col, lw=1.0, label=f"$w_2$, {lab}")
a2.axhline(1e3 * A_TX * 0.1, color=NAVY, ls="--", lw=0.8, label="target $Ax_2$ = 50 mV")
a2.set_xlim(0, NL); a2.set_ylim(-10, 140)
a2.legend(loc="upper right", fontsize=7)
finish(a2, "Time (UI)", "Tap value (mV)")
a2.set_title("Example pulse, 3-tap DFE", loc="left", fontsize=8)
panel(a2, "b")
savefig(fig, "ch08_sslms")

# ------------------------------------------------------------------ ch08_taps
bits7 = np.tile(prbs_bits(7), 40)
y7 = through(tx_wave(bits7), hl)
ntaps = [0, 1, 2, 3, 4, 5, 8]
ehs = []
for n in ntaps:
    rx = sdp.Receiver(y7, SPS, F_NYQ, LEVELS, shift=True)
    if n:
        rx.nrz_DFE(post[:n])
    hts, ph, S, A = eye_scan(rx.signal, bits7)
    ehs.append(hts[ph])
    if n == 0:
        eye0 = (rx.signal.copy(), ph)
    if n == 2:
        eye2 = (rx.signal.copy(), ph)
print("eye vs taps (mV)", np.round(1e3 * np.array(ehs), 1))
fig = plt.figure(figsize=(6.3, 2.25))
gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1, 1])
a1 = fig.add_subplot(gs[0]); a2 = fig.add_subplot(gs[1]); a3 = fig.add_subplot(gs[2], sharey=a2)
xs = np.arange(len(ntaps))
cols = [GOLD if n == 2 else PALE for n in ntaps]
cols[0] = MUTED
a1.bar(xs, 1e3 * np.array(ehs), 0.62, color=cols, lw=0)
for x_, v in zip(xs, ehs):
    a1.text(x_, 1e3 * v + 3, f"{1e3*v:.0f}", ha="center", fontsize=6.8, color=NAVY)
a1.set_xticks(xs); a1.set_xticklabels([str(n) for n in ntaps])
a1.set_ylim(0, 185)
a1.text(2, 1e3 * ehs[2] / 2, "Open-SERDES", ha="center", va="center", rotation=90, fontsize=7, color="white")
finish(a1, "Number of DFE taps", "Eye height (mV)")
panel(a1, "a")
for ax, (yy, ph), title in ((a2, eye0, f"8 dB CTLE: {1e3*ehs[0]:.0f} mV"), (a3, eye2, f"+ 2-tap DFE: {1e3*ehs[2]:.0f} mV")):
    eye_density(ax, yy, SPS, phase=ph % SPS, skip_ui=100, vlim=(-0.2, 0.2))
    ax.set_title(title, loc="left", fontsize=8)
a2.set_ylabel("Summer output (V)")
plt.setp(a3.get_yticklabels(), visible=False)
panel(a2, "b"); panel(a3, "c")
savefig(fig, "ch08_taps")
