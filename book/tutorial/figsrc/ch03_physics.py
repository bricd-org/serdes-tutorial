"""ch03_physics.py -- Chapter 3 figures on line physics: skin depth, loss per inch,
pad/bondwire return loss and echoes, via-stub notch, TDR.  Prints every number quoted
in the Chapter 3 worked examples.

Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch03_physics.py
"""
from bricdstyle import *
from link import *

C0, MU0 = 2.998e8, 4e-7 * np.pi
RHO_CU, RHO_AL = 1.72e-8, 2.65e-8
ER, TAND, Z0 = 4.0, 0.02, 50.0
W_TR, T_TR = 127e-6, 17.5e-6          # 5-mil wide, 0.5-oz (17.5 um) copper stripline
INCH = 0.0254
NP2DB = 20 / np.log(10)              # 8.686 dB per neper


def skin_depth(f, rho=RHO_CU):
    return np.sqrt(rho / (np.pi * f * MU0))


def r_line(f):
    """Per-unit-length R of the stripline: DC value blended with skin-effect R_s/P."""
    rdc = RHO_CU / (W_TR * T_TR)
    rac = (RHO_CU / skin_depth(f)) / (2 * (W_TR + T_TR))
    return np.sqrt(rdc**2 + rac**2), rdc, rac


def alpha_r(f):                       # dB/in
    return r_line(f)[0] / (2 * Z0) * NP2DB * INCH


def alpha_d(f, er=ER, tand=TAND):     # dB/in
    return np.pi * f * np.sqrt(er) * tand / C0 * NP2DB * INCH


# ---------------------------------------------------------------- numbers for the text
fN = 2.5e9
v = C0 / np.sqrt(ER)
print(f"v = {v:.4e} m/s, delay = {1e12/v*INCH:.1f} ps/in = {1e12/v*1e-3:.3f} ps/mm")
for tr in (30e-12, 50e-12):
    print(f"t_r = {tr*1e12:.0f} ps: critical length t_r/(6 t_pd) = {tr*v/6*1e3:.2f} mm")
print(f"lambda/10 at 2.5 GHz = {v/fN/10*1e3:.1f} mm, at 7.5 GHz = {v/7.5e9/10*1e3:.1f} mm")
L_ref, C_ref = Z0 / v, 1 / (Z0 * v)
print(f"REF L = {L_ref*1e9:.1f} nH/m, C = {C_ref*1e12:.1f} pF/m, f_LC(Rdc=7) = {7/(2*np.pi*L_ref)/1e6:.2f} MHz")
print(f"REF 1 m delay = {1/v*1e9:.3f} ns = {1/v/UI:.1f} UI")
print(f"skin depth Cu 2.5 GHz = {skin_depth(fN)*1e6:.3f} um, 5 GHz = {skin_depth(5e9)*1e6:.3f} um,"
      f" Al 2.5 GHz = {skin_depth(fN, RHO_AL)*1e6:.3f} um")
R, rdc, rac = r_line(fN)
print(f"R_DC = {rdc:.2f} ohm/m, R_s(2.5G) = {RHO_CU/skin_depth(fN)*1e3:.2f} mohm/sq, R_AC = {rac:.1f} ohm/m")
fs = RHO_CU / (np.pi * MU0 * (T_TR / 2)**2)
print(f"skin onset (delta = t/2) f_s = {fs/1e6:.0f} MHz")
ar, ad = alpha_r(fN), alpha_d(fN)
print(f"alpha_R = {ar:.4f} dB/in, alpha_D = {ad:.4f} dB/in ({ad/INCH:.2f} dB/m), total = {ar+ad:.4f} dB/in")
print(f"reach for 10 dB: line only {10/(ar+ad):.1f} in = {10/(ar+ad)*INCH*100:.0f} cm;"
      f" with 3 dB discretes {7/(ar+ad):.1f} in = {7/(ar+ad)*INCH*100:.0f} cm")
fx = brentq(lambda f: alpha_r(f) - alpha_d(f), 1e7, 1e10)
print(f"alpha_R = alpha_D crossover at {fx/1e9:.2f} GHz")
# REF model per inch (link.py parameters: kr = 60 ohm/m at 1 GHz)
ar_ref = 60 * np.sqrt(fN / 1e9) / (2 * Z0) * NP2DB * INCH
ad_ref = alpha_d(fN)
print(f"REF model: alpha_R = {ar_ref:.3f}, alpha_D = {ad_ref:.3f}, total = {ar_ref+ad_ref:.3f} dB/in"
      f" = {(ar_ref+ad_ref)/INCH:.2f} dB/m")
for cp in (0, 300e-15):
    print(f"channel(1.0, c_pad={cp*1e15:.0f} fF): {loss_db(channel(1.0, c_pad=cp)):.2f} dB at 2.5 GHz")
print(f"LOSS_FAMILY[10] = {LOSS_FAMILY[10]} m = {LOSS_FAMILY[10]/INCH:.1f} in")
# low-loss laminate
ad_ll = alpha_d(fN, er=3.7, tand=0.004)
print(f"low-loss laminate (3.7, 0.004): alpha_D = {ad_ll:.3f}, total = {ad_ll+ar:.3f} dB/in")


def gamma_c(f, c, r=Z0):
    x = 2 * np.pi * f * r * c
    return x / np.sqrt(4 + x**2)


def gamma_l(f, l):
    x = 2 * np.pi * f * l / (2 * Z0)
    return x / np.sqrt(1 + x**2)


for c in (300e-15, 1e-12):
    g = gamma_c(fN, c)
    print(f"pad {c*1e15:.0f} fF: |G|(2.5G) = {g:.4f}, RL = {-20*np.log10(g):.2f} dB;"
          f" at 5 GHz RL = {-20*np.log10(gamma_c(5e9, c)):.2f} dB")
print(f"pad pole 1/(2 pi 25 ohm 300 fF) = {1/(2*np.pi*25*300e-15)/1e9:.1f} GHz")
for rl in (10, 15):
    g = 10**(-rl / 20)
    cmax = 2 * g / np.sqrt(1 - g**2) / (2 * np.pi * fN * Z0)
    print(f"C_max for RL >= {rl} dB at 2.5 GHz: {cmax*1e12:.3f} pF")
lb = 2.5e-9
xb = 2 * np.pi * fN * lb / (2 * Z0)
print(f"bondwire 2.5 nH: wL = {2*np.pi*fN*lb:.1f} ohm, x = {xb:.3f}, |S21| = {1/np.sqrt(1+xb**2):.4f}"
      f" ({20*np.log10(1/np.sqrt(1+xb**2)):.2f} dB), |S11| = {gamma_l(fN, lb):.4f},"
      f" RL = {-20*np.log10(gamma_l(fN, lb)):.2f} dB")
print(f"  matching C for sqrt(L/C)=50: {lb/Z0**2*1e12:.2f} pF, cutoff 1/(pi sqrt(LC)) ="
      f" {1/(np.pi*np.sqrt(lb*lb/Z0**2))/1e9:.2f} GHz")
for lr in (40, 60):
    g = (lr - Z0) / (lr + Z0)
    print(f"R_T = {lr} ohm: Gamma = {g:+.3f}, RL = {-20*np.log10(abs(g)):.1f} dB")
for ls in (1.5e-3, 3e-3, 5e-3):
    print(f"via stub {ls*1e3:.1f} mm: f_null = v/(4l) = {v/(4*ls)/1e9:.2f} GHz")
print(f"stub length for null at 3 fN = 7.5 GHz: {v/(4*7.5e9)*1e3:.2f} mm")
# lattice example
rs, rl_, vs = 25.0, 100.0, 1.0
gs, gl = (rs - Z0) / (rs + Z0), (rl_ - Z0) / (rl_ + Z0)
vi = vs * Z0 / (rs + Z0)
vl, acc = [], 0
for n in range(4):
    acc += vi * (gs * gl)**n * (1 + gl)
    vl.append(acc)
print(f"lattice RS=25, RL=100: GS={gs:.3f}, GL={gl:.3f}, Vi={vi:.4f}, VL steps =",
      np.round(vl, 4), "final", rl_ / (rs + rl_))

# ---------------------------------------------------------------- Fig: skin depth + R(f)
f = np.logspace(6, 10.3, 400)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.25))
ax1.loglog(f / 1e9, skin_depth(f) * 1e6, color=C1, label="copper")
ax1.loglog(f / 1e9, skin_depth(f, RHO_AL) * 1e6, color=C2, ls="--", label="aluminum")
ax1.axhline(T_TR / 2 * 1e6, color=MUTED, lw=0.8, ls=":")
ax1.text(19, T_TR / 2 * 1e6 * 1.12, "half of 0.5-oz PCB Cu (8.75 µm)", fontsize=6.6, color=MUTED, ha="right")
ax1.axhline(1.5, color=MUTED, lw=0.8, ls=":")
ax1.text(1.3e-3, 1.5 * 0.72, "half of SG13G2 TopMetal2 (1.5 µm)", fontsize=6.8, color=MUTED)
ax1.plot(2.5, skin_depth(fN) * 1e6, "o", color=GOLD, ms=5, zorder=5)
note(ax1, (2.5, skin_depth(fN) * 1e6), "1.32 µm at 2.5 GHz", (0.004, 0.55), color=GOLDDK)
ax1.set_xlim(1e-3, 20); ax1.set_ylim(0.3, 100)
finish(ax1, "Frequency (GHz)", "Skin depth δ (µm)", legend=True, loc="upper right")
panel(ax1, "a")
R_all, rdc_, _ = r_line(f)
ax2.loglog(f / 1e9, R_all, color=C1, label="R(f), 5-mil trace")
ax2.loglog(f / 1e9, rdc_ * np.ones_like(f), color=MUTED, lw=0.8, ls=":")
ax2.loglog(f / 1e9, rac * np.sqrt(f / fN), color=C4, lw=0.9, ls="--", label="~√f asymptote")
ax2.axvline(fs / 1e9, color=MUTED, lw=0.7, ls=":")
ax2.text(fs / 1e9 * 1.15, 2.2, f"onset\n≈ {fs/1e6:.0f} MHz", fontsize=6.8, color=MUTED)
ax2.text(1.2e-3, rdc_ * 1.15, f"$R_{{DC}}$ = {rdc_:.1f} Ω/m", fontsize=6.8, color=MUTED)
ax2.plot(2.5, R, "o", color=GOLD, ms=5, zorder=5)
note(ax2, (2.5, R), f"{R:.0f} Ω/m", (0.25, 60), color=GOLDDK)
ax2.set_xlim(1e-3, 20); ax2.set_ylim(1.5, 200)
finish(ax2, "Frequency (GHz)", "Resistance (Ω/m)", legend=True, loc="upper left")
panel(ax2, "b")
savefig(fig, "ch03_skin")

# ---------------------------------------------------------------- Fig: loss per inch
f = np.linspace(0.01e9, 10e9, 500)
fig, ax = plt.subplots(figsize=(6.3, 2.45))
ax.plot(f / 1e9, alpha_r(f), color=C1, ls="--", label=r"conductor $\alpha_R$ (~√f)")
ax.plot(f / 1e9, alpha_d(f), color=C2, ls="-.", label=r"dielectric $\alpha_D$ (~f·tanδ)")
ax.plot(f / 1e9, alpha_r(f) + alpha_d(f), color=NAVY, lw=1.8, label="total, FR-4 stripline")
ax.plot(f / 1e9, alpha_r(f) + alpha_d(f, 3.7, 0.004), color=C3, lw=1.0, label=r"total, low-loss laminate ($\tan\delta$ = 0.004)")
ref_tot = 60 * np.sqrt(f / 1e9) / (2 * Z0) * NP2DB * INCH + alpha_d(f)
ax.plot(f / 1e9, ref_tot, color=C4, lw=1.0, ls=":", label="total, REF model (rougher conductor)")
for fx_, lab in ((1.25, "$f_N$ PAM4\n1.25 GHz"), (2.5, "$f_N$ NRZ\n2.5 GHz")):
    ax.axvline(fx_, color=MUTED, lw=0.7, ls=":")
    ax.text(fx_ + 0.08, 0.93, lab, fontsize=6.8, color=MUTED, va="top")
tot = ar + ad
ax.plot(2.5, tot, "o", color=GOLD, ms=5, zorder=5)
note(ax, (2.5, tot), f"{tot:.2f} dB/in\n({ad:.3f} + {ar:.3f})", (3.6, 0.2), color=GOLDDK)
ax.plot(2.5, ar_ref + ad_ref, "o", color=C4, ms=4, zorder=5)
note(ax, (2.5, ar_ref + ad_ref), f"{ar_ref+ad_ref:.2f} dB/in", (3.4, 0.62), color=C4)
ax.set_xlim(0, 10); ax.set_ylim(0, 1.5)
finish(ax, "Frequency (GHz)", "Loss (dB/in)", legend=True, loc="upper left")
ax.legend(loc="upper left", ncol=2, columnspacing=1.2)
savefig(fig, "ch03_loss")

# ---------------------------------------------------------------- Fig: pad return loss + echoes
f = np.linspace(1e6, 10e9, 600)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FULL2)
for c, col in zip((150e-15, 300e-15, 600e-15, 1e-12), (C3, C1, C2, C4)):
    ax1.plot(f / 1e9, 20 * np.log10(gamma_c(f, c)), color=col, label=f"$C_p$ = {c*1e15:.0f} fF")
ax1.plot(f / 1e9, 20 * np.log10(gamma_l(f, 2.5e-9)), color=NAVY, ls="--", lw=1.1, label="2.5 nH bondwire")
ax1.axhline(-10, color=MUTED, lw=0.8, ls=":")
ax1.text(0.15, -9.0, "RL = 10 dB", fontsize=6.8, color=MUTED, ha="left")
ax1.axvline(2.5, color=MUTED, lw=0.7, ls=":")
g3 = 20 * np.log10(gamma_c(fN, 300e-15))
ax1.plot(2.5, g3, "o", color=GOLD, ms=4.5, zorder=5)
note(ax1, (2.5, g3), f"{g3:.1f} dB", (3.6, -27), color=GOLDDK)
ax1.set_xlim(0, 10); ax1.set_ylim(-40, 0)
finish(ax1, "Frequency (GHz)", "|S11| (dB)", legend=True, loc="lower right")
ax1.legend(loc="lower right", fontsize=6.5)
panel(ax1, "a")
Ls = 0.10
td = Ls / v
for c, col, lab in ((0.0, MUTED, "no pads"), (300e-15, C1, "300 fF pads"), (1e-12, C4, "1 pF pads")):
    t, p = pulse_of(channel(Ls, c_pad=c))
    i0 = int(np.argmax(p))
    tu = (np.arange(p.size) - i0) / SPS
    print(f"10 cm, pad {c*1e15:.0f} fF: p0 = {p.max():.3f}")
    ax2.plot(tu, p, color=col, lw=1.1 if c else 0.9, ls="-" if c else "--", label=lab)
ax2.axvline(2 * td / UI, color=GOLDDK, lw=0.7, ls=":")
ax2.text(2 * td / UI + 0.2, 0.07, f"echo at $2t_d$\n= {2*td/UI:.1f} UI", fontsize=6.8, color=GOLDDK, va="top")
ax2.set_xlim(-2, 12); ax2.set_ylim(-0.06, 0.09)
ax2.text(-1.8, -0.045, f"10 cm line; main pulse\n≈ {p.max():.2f} V (off scale)", fontsize=6.8, color=MUTED, va="center")
finish(ax2, "Time from main cursor (UI)", "Pulse response (V)", legend=True, loc="lower right")
ax2.legend(loc="lower right", fontsize=6.5)
panel(ax2, "b")
savefig(fig, "ch03_pad")

# ---------------------------------------------------------------- Fig: via stub notch
f = np.linspace(1e6, 20e9, 1500)
w = 2 * np.pi * f
fig, ax = plt.subplots(figsize=HALF)
ax.axvspan(0, 5, color=BGPALE, zorder=0)
ax.text(2.5, -27.0, "NRZ main lobe\n0–5 GHz", fontsize=6.6, color=MUTED, ha="center")
for ls, col in ((2e-3, C3), (4e-3, C1), (6e-3, C4)):
    alpha = np.pi * f * np.sqrt(ER) * TAND / C0 + 0.5 * np.sqrt(f / 1e9) / (2 * Z0)
    gam = alpha + 1j * w / v
    y = np.tanh(gam * ls) / Z0                 # open stub input admittance
    s21 = 2 / (2 + y * Z0)
    ax.plot(f / 1e9, 20 * np.log10(np.abs(s21)), color=col, label=f"{ls*1e3:.0f} mm stub")
    fn = v / (4 * ls) / 1e9
    left = fn > 15
    ax.text(fn + (-0.5 if left else 0.5), -28.5, f"{fn:.1f} GHz", fontsize=6.5, color=col, ha="right" if left else "left")
ax.set_xlim(0, 20); ax.set_ylim(-30, 1)
finish(ax, "Frequency (GHz)", "|S21| (dB)")
ax.legend(loc="lower left", fontsize=6.5, bbox_to_anchor=(0.0, 0.22))
savefig(fig, "ch03_via")

# ---------------------------------------------------------------- Fig: TDR
fmax, df = 400e9, 25e6
ff = np.arange(0, fmax + df / 2, df)
ww = 2 * np.pi * ff
def tline(tau, z=Z0):
    th = ww * tau
    return np.array([[np.cos(th), 1j * z * np.sin(th)], [1j * np.sin(th) / z, np.cos(th)]]).transpose(2, 0, 1)
one, zero = np.ones_like(ww), np.zeros_like(ww)
ser = lambda Z: np.array([[one, Z], [zero, one]]).transpose(2, 0, 1)
shu = lambda Y: np.array([[one, zero], [Y, one]]).transpose(2, 0, 1)
L_d, C_d = 1.0e-9, 0.5e-12
net = tline(0.20e-9) @ ser(1j * ww * L_d) @ tline(0.25e-9) @ shu(1j * ww * C_d) @ tline(0.25e-9)
zl = Z0
zin = (net[:, 0, 0] * zl + net[:, 0, 1]) / (net[:, 1, 0] * zl + net[:, 1, 1])
gam_in = (zin - Z0) / (zin + Z0)
gam_in[0] = 0
dt = 1 / (2 * fmax)
fig, ax = plt.subplots(figsize=(6.3, 2.5))
for tr, col, lw_ in ((25e-12, NAVY, 1.5), (100e-12, C2, 1.2)):
    sig = tr / 2.563
    hg = np.exp(-2 * np.pi**2 * sig**2 * ff**2)
    rho_imp = np.fft.irfft(gam_in * hg)
    rho = np.cumsum(rho_imp)                    # step response of the reflection
    t = np.arange(rho.size) * dt
    z = Z0 * (1 + rho) / (1 - rho)
    ax.plot(t * 1e9, z, color=col, lw=lw_, label=f"step rise time {tr*1e12:.0f} ps")
    if tr < 50e-12:
        iL = np.argmax(z[t < 0.65e-9]); iC = np.argmin(z[(t > 0.65e-9) & (t < 1.2e-9)]) + np.sum(t <= 0.65e-9)
        zL, zC = z[iL], z[iC]
        print(f"TDR tr={tr*1e12:.0f} ps: L peak {zL:.1f} ohm at {t[iL]*1e9:.3f} ns, C dip {zC:.1f} ohm at {t[iC]*1e9:.3f} ns")
    else:
        print(f"TDR tr={tr*1e12:.0f} ps: L peak {z[t<0.65e-9].max():.1f}, C dip {z[(t>0.65e-9)&(t<1.2e-9)].min():.1f}")
ax.axhline(Z0, color=MUTED, lw=0.7, ls=":")
note(ax, (t[iL] * 1e9, zL), "series L = 1 nH\n(connector pin, bondwire):\nbump up", (0.50, 88), color=NAVY)
note(ax, (t[iC] * 1e9, zC), "shunt C = 0.5 pF\n(pad, via barrel):\ndip down", (1.12, 30), color=NAVY)
ax.text(1.5, 58, "matched end at 1.4 ns: flat at 50 Ω", fontsize=7, color=MUTED)
ax.set_xlim(0, 2.0); ax.set_ylim(15, 105)
finish(ax, "Round-trip time (ns)", "Apparent impedance (Ω)", legend=True, loc="lower left")
sec = ax.secondary_xaxis("top", functions=(lambda tt: tt * 1e-9 * v / 2 * 1e3, lambda xx: xx * 1e-3 * 2 / v * 1e9))
sec.set_xlabel("Distance from the TDR port, $x = v\\,t/2$ (mm)", color=NAVY)
sec.tick_params(colors=MUTED)
savefig(fig, "ch03_tdr")
