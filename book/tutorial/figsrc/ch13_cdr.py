"""ch13_cdr.py -- figures and checked numbers for Chapter 13 (CDR).

Run ch13_sim.py first (it writes ch13_pi_data.npz), then:
  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch13_cdr.py
Writes ch13_jtran, ch13_bbchar, ch13_jtol, ch13_inl (tutorial/figs/).
"""
from bricdstyle import *
from scipy.special import erf

pi = np.pi
Tb = 200e-12
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ analog (VCO-based) BB-CDR, per-bit model
def bbcdr(n, amps, Tui, R=200.0, C=1e-9, Icp=100e-6, Kvco=150e6, TD=0.5, rj=0.01, seed=0, prop_only=False):
    """Vectorized over SJ amplitudes (UIpp). Half-rate VCO: one clock cycle = 2 UI.
    Returns phi_in, phi_out (n x na) in UI."""
    rng = np.random.default_rng(seed)
    na = len(amps)
    po = np.zeros(na); vc = np.zeros(na)
    PI = np.zeros((n, na)); PO = np.zeros((n, na))
    dV = Icp * Tb / C
    for k in range(n):
        pin = 0.5 * amps * np.sin(2 * pi * k / Tui)
        e = pin - po
        if rng.random() < TD:
            s = np.sign(e + rj * rng.standard_normal())
        else:
            s = np.zeros(na)
        if not prop_only:
            vc += s * dV
        po += Kvco * (s * Icp * R + vc) * Tb * 2.0
        PI[k] = pin; PO[k] = po
    return PI, PO

def S_of(R, Icp=100e-6, Kvco=150e6, TD=0.5):
    return TD * Kvco * Icp * R * 2.0          # UI/s (half-rate: 2 UI per VCO cycle)

for R in (100, 200):
    print(f"analog BB-CDR R={R}: dphi_P = {150e6*100e-6*R*Tb*2:.1e} UI/bit, S = {S_of(R):.2e} UI/s, "
          f"JTOL(1 MHz) ~ TM + 2S/w = {0.4 + 2*S_of(R)/(2*pi*1e6):.2f} UIpp, (0.5 MHz) {0.4 + 2*S_of(R)/(2*pi*0.5e6):.2f}, "
          f"FD must land within TD*dphi = {0.5*150e6*100e-6*R*Tb*2*1e6:.0f} ppm, xi = RC/Tb = {R*1e-9/Tb:.0f}")
# measured 90 nm example (10 Gb/s, full rate)
S_bb = 0.5 * 1e9 * 300e-6 * 10          # UI/s, full-rate clock: 1 cycle = 1 UI
for app in (0.125, 0.25, 0.5):
    print(f"Slew check: A = {app} UIpp -> f-3dB = S/(4 A_pk) = {S_bb/(4*app/2)/1e6:.1f} MHz")

# ================================================================== Fig: jitter transfer (linear + BB)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.15))
f = np.logspace(4, 8, 600)
z = 4.5
fn = 4e6 / 9.111
s = 1j * f / fn
Hl = (2 * z * s + 1) / (s ** 2 + 2 * z * s + 1)
a.semilogx(f, 20 * np.log10(np.abs(Hl)), color=NAVY, lw=1.6, label="$|H|$: jitter the CDR tracks")
a.semilogx(f, 20 * np.log10(np.abs(1 - Hl)), color=C4, lw=1.4, ls="--", label="$|1-H|$: jitter left at the sampler")
a.axhline(-3, color=MUTED, lw=0.6, ls=":")
a.axvline(4e6, color=MUTED, lw=0.6, ls=":")
a.text(4.4e6, -43, "$f_{-3\\mathrm{dB}}$ = 4 MHz", fontsize=7, color=MUTED)
a.text(1.5e4, -18, "$-$40 dB/dec", fontsize=7, color=C4)
a.text(1.6e5, -12, "$-$20 dB/dec", fontsize=7, color=C4)
a.set_ylim(-45, 16); a.set_xlim(1e4, 1e8)
finish(a, xlabel="Jitter frequency (Hz)", ylabel="Transfer (dB)")
a.legend(loc="upper left", fontsize=6.3)
panel(a, "a")
# BB transfer by simulation (R = 200 Ohm design)
fj = np.logspace(np.log10(0.3e6), np.log10(40e6), 16)
amps = np.array([0.1, 0.2, 0.4, 0.8])
gains = np.zeros((len(fj), len(amps)))
for i, fx in enumerate(fj):
    Tui = 5e9 / fx
    nper = 6
    n = int((nper + 1) * Tui)
    PI, PO = bbcdr(n, amps, Tui, seed=i)
    k0 = int(Tui)
    ref = np.exp(-2j * pi * np.arange(k0, n) / Tui)
    gains[i] = np.abs((PO[k0:] * ref[:, None]).sum(0)) / np.abs((PI[k0:] * ref[:, None]).sum(0))
for j, (A, c) in enumerate(zip(amps, [C3, C1, C2, C4])):
    b.semilogx(fj, 20 * np.log10(gains[:, j]), "-o", color=c, ms=2.8, lw=1.2, label=f"{A:g} UI$_{{pp}}$")
    fpred = S_of(200) / (4 * A / 2)
    b.plot(fpred, -3, "v", color=c, ms=5)
    g = 20 * np.log10(gains[:, j]); kk = np.where(g < -3)[0][0]
    fint = 10 ** np.interp(-3, [g[kk], g[kk - 1]], [np.log10(fj[kk]), np.log10(fj[kk - 1])])
    print(f"BB JTRAN A={A}: predicted f-3dB {fpred/1e6:.2f} MHz, simulated {fint/1e6:.2f} MHz (ratio {fint/fpred:.2f}), peak {g.max():.2f} dB")
b.axhline(-3, color=MUTED, lw=0.6, ls=":")
b.text(3.3e5, -24, "$\\blacktriangledown$ = $\\pi S/(2A_{pk})$ prediction", fontsize=6.8, color=MUTED)
b.set_ylim(-26, 4); b.set_xlim(3e5, 4e7)
finish(b, xlabel="Jitter frequency (Hz)", ylabel="Jitter transfer (dB)")
b.legend(loc="lower left", fontsize=6.6, title="SJ amplitude", title_fontsize=6.6, bbox_to_anchor=(0, 0.1))
panel(b, "b")
savefig(fig, "ch13_jtran")

# ================================================================== Fig: PD characteristics + slewing
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.15))
dphi = np.linspace(-0.5, 0.5, 1001)
a.plot(dphi, dphi / 0.5, color=MUTED, lw=1.0, ls="--", label="linear (Hogge), ideal")
a.plot(dphi, np.sign(dphi), color=NAVY, lw=1.6, label="bang-bang, no jitter")
for sg, c in [(0.01, C1), (0.03, C3), (0.1, C2)]:
    a.plot(dphi, erf(dphi / (np.sqrt(2) * sg)), color=c, lw=1.2, label=f"bang-bang, $\\sigma_j$ = {sg:g} UI")
a.set_xlim(-0.5, 0.5); a.set_ylim(-1.15, 1.15)
note(a, (0.03, erf(0.03 / (np.sqrt(2) * 0.03))), "slope $\\sqrt{2/\\pi}/\\sigma_j$", (0.12, 0.25), color=C3)
finish(a, xlabel="Phase error $\\Delta\\phi$ (UI)", ylabel="Average PD output / TD")
a.legend(loc="lower right", fontsize=6.2)
panel(a, "a")
fs = 5e6; Tui = 5e9 / fs
n = int(2.2 * Tui)
PI, PO = bbcdr(n, np.array([0.4]), Tui, prop_only=True, seed=3)
tt = np.arange(n) * Tb * 1e9
b.plot(tt, PI[:, 0], color=GOLD, lw=1.8, label="input phase $\\phi_{in}$ (0.4 UI$_{pp}$, 5 MHz)")
b.plot(tt, PO[:, 0], color=NAVY, lw=1.2, label="recovered clock phase $\\phi_{out}$")
b.plot(tt, PI[:, 0] - PO[:, 0], color=C4, lw=0.8, label="error $\\phi_{in}-\\phi_{out}$")
Sx = S_of(200)
b.text(40, 0.27, f"slope $\\pm S$ = $\\pm${Sx/1e6:.0f}$\\times$10$^6$ UI/s", fontsize=7, color=NAVY)
b.set_xlim(0, tt[-1]); b.set_ylim(-0.5, 0.36)
finish(b, xlabel="Time (ns)", ylabel="Phase (UI)")
b.legend(loc="lower center", fontsize=6.0, ncol=2)
panel(b, "b")
savefig(fig, "ch13_bbchar")
print(f"slewing: predicted phi_out,p = S*T/4 = {Sx/fs/4:.3f} UI vs input 0.2 UI peak; sim pk {PO[int(Tui):,0].max():.3f}")

# ================================================================== Fig: JTOL
def mask(fx):
    fx = np.asarray(fx, float)
    return np.where(fx < 4.9e6, 1e6 / fx, 0.2)
fm = np.logspace(np.log10(0.5e6), np.log10(50e6), 200)
fsim = np.array([0.3e6, 0.5e6, 1e6, 2e6, 4.9e6, 10e6, 30e6])
TM = 0.4
amps = np.logspace(-1.0, 1.7, 70)
res = {}
for R in (100, 200):
    out = []
    for i, fx in enumerate(fsim):
        Tui = 5e9 / fx; n = int(3.2 * Tui); k0 = int(Tui)
        PI, PO = bbcdr(n, amps, Tui, R=R, seed=10 + i)
        ok = np.abs(PI[k0:] - PO[k0:]).max(0) < TM / 2
        out.append(amps[np.argmax(~ok) - 1] if (~ok).any() else amps[-1])
    res[R] = np.array(out)
    print(f"analog BB-CDR R={R} JTOL sim:", " ".join(f"{fx/1e6:g}M:{v:.2f}" for fx, v in zip(fsim, res[R])))
pid = np.load(os.path.join(HERE, "ch13_pi_data.npz"))
fig, ax = plt.subplots(figsize=(6.3, 2.45))
fl = np.logspace(np.log10(5e4), np.log10(1e8), 400)
sl = 1j * fl / fn
Hl = (2 * z * sl + 1) / (sl ** 2 + 2 * z * sl + 1)
ax.loglog(fl, TM / np.abs(1 - Hl), color=MUTED, lw=1.0, ls=":", label="linear CDR, 4 MHz: TM/|1$-H$|")
ax.loglog(fm, mask(fm), color=NAVY, lw=2.2, drawstyle="default", label="JTOL mask (USB 3 Gen 1-style)")
ax.fill_between(fm, 1e-2, mask(fm), color=NAVY, alpha=0.06, lw=0)
for R, c in [(100, C4), (200, C3)]:
    ax.loglog(fl, TM + 2 * S_of(R) / (2 * pi * fl), color=c, lw=1.0, ls="--")
    ax.loglog(fsim, res[R], "o", color=c, ms=4, label=f"analog BB-CDR, $R$ = {R} $\\Omega$ (sim; dashed: TM + 2S/$\\omega$)")
ax.loglog(pid["fj"], pid["jt"], "-s", color=C1, ms=3.2, lw=1.3, label="Open-SERDES PI-CDR (sim)")
ax.set_xlim(1e5, 1e8); ax.set_ylim(0.1, 30)
ax.plot(1e6, 1.0, "o", mfc="white", mec=NAVY, ms=4.5)
finish(ax, xlabel="Sinusoidal jitter frequency (Hz)", ylabel="Tolerated SJ (UI$_{pp}$)")
ax.legend(loc="upper right", fontsize=6.6)
savefig(fig, "ch13_jtol")

# ================================================================== Fig: PI INL (linear weights vs corrected weights)
nq = 16
k = np.arange(0, 64 + 1)
def pi_phase(alpha):
    return np.degrees(np.arctan2(alpha, 1 - alpha))
inl_lin = []; inl_cor = []; amp_lin = []
for kk in k:
    qd, r = divmod(kk, nq)
    al = r / nq
    th_l = 90 * qd + pi_phase(al)
    # corrected: weights from a sine/cosine table quantized to 1/64 of full scale
    th_t = np.radians(90 * r / nq)
    wI, wQ = np.round(64 * np.cos(th_t)) / 64, np.round(64 * np.sin(th_t)) / 64
    th_c = 90 * qd + np.degrees(np.arctan2(wQ, wI))
    inl_lin.append(th_l - 360 * kk / 64); inl_cor.append(th_c - 360 * kk / 64)
    amp_lin.append(np.hypot(al, 1 - al))
inl_lin, inl_cor = np.array(inl_lin), np.array(inl_cor)
print(f"PI INL linear weights: max {np.abs(inl_lin).max():.2f} deg = {np.abs(inl_lin).max()*400/360:.2f} ps; "
      f"corrected (6-bit trig weights): {np.abs(inl_cor).max():.2f} deg = {np.abs(inl_cor).max()*400/360:.2f} ps; "
      f"min amplitude {min(amp_lin):.3f}")
alc = np.linspace(0, 1, 401)
cont = pi_phase(alc) - 90 * alc
print(f"continuous linear-weight INL max {cont.max():.2f} deg at alpha={alc[np.argmax(cont)]:.3f}")
fig, ax = plt.subplots(figsize=(3.3, 2.35))
ax.plot(k, inl_lin, "-o", color=C4, ms=2.2, lw=1.0, label="linear weights $\\alpha = k/16$")
ax.plot(k, inl_cor, "-o", color=C1, ms=2.2, lw=1.0, label="sine/cosine weights (6-bit)")
ax.axhline(0, color=MUTED, lw=0.6)
ax.set_xlim(0, 64); ax.set_xticks([0, 16, 32, 48, 64]); ax.set_ylim(-8, 6)
sec = ax.secondary_yaxis("right", functions=(lambda d: d * 400 / 360, lambda p: p * 360 / 400))
sec.set_ylabel("INL (ps)", fontsize=7.5); sec.tick_params(labelsize=7)
finish(ax, xlabel="PI code $k$ (16 per quadrant)", ylabel="INL (degrees)")
ax.legend(loc="lower left", fontsize=6.0, ncol=1)
savefig(fig, "ch13_inl")
