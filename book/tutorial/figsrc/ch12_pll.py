"""ch12_pll.py -- figures and checked numbers for Chapter 12 (PLL, LC VCO, quadrature).

Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch12_pll.py
Writes ch12_resp, ch12_loop, ch12_noise, ch12_leeson, ch12_poly (tutorial/figs/).
"""
from bricdstyle import *
from scipy import signal

pi = np.pi
F0 = 2.5e9
kB, Tk = 1.380649e-23, 300.0

# ------------------------------------------------------------------ zeta table (2nd-order type-II)
print("zeta  w3dB/wn  peaking(dB)")
w = np.logspace(-2, 2, 200001)
for z in [0.5, 0.707, 1.0, 2.0, 4.0, 4.5]:
    H = (2j * z * w + 1) / (-w ** 2 + 2j * z * w + 1)
    m = 20 * np.log10(np.abs(H))
    w3 = w[np.where(m > -3.0103)[0][-1]]
    form = np.sqrt(1 + 2 * z ** 2 + np.sqrt((1 + 2 * z ** 2) ** 2 + 1))
    print(f"{z:5.3f} {w3:7.3f} (formula {form:6.3f})  {m.max():5.2f}")

# ------------------------------------------------------------------ loop-filter design (max phase margin)
def design(fu, Icp, N=50, Kv=2 * pi * 150e6, pm=60.0):
    t = np.tan(np.radians(pm)); Kc = 2 * t ** 2 + 2 * t * np.sqrt(t ** 2 + 1)
    wu = 2 * pi * fu; wz = wu / np.sqrt(1 + Kc); wp = wu * np.sqrt(1 + Kc)
    C2 = Icp * Kv / (2 * pi * N * wu ** 2) * np.sqrt((wu ** 2 + wz ** 2) / (wu ** 2 + wp ** 2))
    C1 = Kc * C2; R = 1 / (wz * C1)
    return dict(Kc=Kc, fz=wz / 2 / pi, fp=wp / 2 / pi, C1=C1, C2=C2, R=R, Icp=Icp, N=N, Kv=Kv, fu=fu)

def loopgain(d, f):
    s = 1j * 2 * pi * f
    Z = (1 + s * d["R"] * d["C1"]) / (s * (d["C1"] + d["C2"]) * (1 + s * d["R"] * d["C1"] * d["C2"] / (d["C1"] + d["C2"])))
    return d["Icp"] / (2 * pi) * d["Kv"] / s * Z / d["N"], Z

f = np.logspace(3, np.log10(1.25e9), 20000)
we = design(1e6, 200e-6)
LG, Z = loopgain(we, f)
H = LG / (1 + LG)
Hdb = 20 * np.log10(np.abs(H))
iu = np.argmin(np.abs(np.abs(LG) - 1))
wn = np.sqrt(we["Icp"] * we["Kv"] / (2 * pi * we["N"] * we["C1"]))
zeta = we["R"] / 2 * np.sqrt(we["Icp"] * we["Kv"] * we["C1"] / (2 * pi * we["N"]))
print(f"WE12: Kc={we['Kc']:.2f} fz={we['fz']/1e3:.0f} kHz fp3={we['fp']/1e6:.2f} MHz C2={we['C2']*1e12:.2f} pF "
      f"C1={we['C1']*1e12:.1f} pF R={we['R']/1e3:.2f} kOhm")
print(f"      2nd-order: fn={wn/2/pi/1e3:.0f} kHz zeta={zeta:.2f}; sim fu={f[iu]/1e6:.3f} MHz PM={180+np.angle(LG[iu],deg=True):.1f} deg;"
      f" f3dB={f[np.where(Hdb > -3)[0][-1]]/1e6:.2f} MHz peaking={Hdb.max():.2f} dB")
print(f"      4kTR = {np.sqrt(4*kB*Tk*we['R'])*1e9:.1f} nV/rtHz; C1 area at 1.5 fF/um2 = {we['C1']/1.5e-15/1e6:.4f} mm2;"
      f" fref/fu = {50e6/1e6:.0f}")
d3 = design(3e6, 600e-6)
LG3, _ = loopgain(d3, f); H3 = LG3 / (1 + LG3); H3db = 20 * np.log10(np.abs(H3))
print(f"3 MHz design (Icp=600uA): C2={d3['C2']*1e12:.2f} pF C1={d3['C1']*1e12:.1f} pF R={d3['R']/1e3:.2f} kOhm "
      f"f3dB={f[np.where(H3db > -3)[0][-1]]/1e6:.2f} MHz peaking={H3db.max():.2f} dB")
d3b = design(3e6, 200e-6)
print(f"3 MHz design (Icp=200uA): C2={d3b['C2']*1e12:.2f} pF C1={d3b['C1']*1e12:.1f} pF R={d3b['R']/1e3:.1f} kOhm")

# ================================================================== Fig: 2nd-order response family
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.15))
wx = np.logspace(-1.3, 1.6, 800)
tt = np.linspace(0, 12, 1200)
for z, c in zip([0.5, 0.707, 1.0, 2.0], [C4, C2, C1, C3]):
    Hn = (2j * z * wx + 1) / (-wx ** 2 + 2j * z * wx + 1)
    a.semilogx(wx, 20 * np.log10(np.abs(Hn)), color=c, label=f"$\\zeta$ = {z:g}")
    sys = signal.lti([2 * z, 1], [1, 2 * z, 1])
    _, y = signal.step(sys, T=tt)
    b.plot(tt, y, color=c, label=f"$\\zeta$ = {z:g}")
a.axhline(-3, color=MUTED, lw=0.7, ls="--")
a.text(0.06, -2.4, "$-$3 dB", fontsize=7, color=MUTED)
a.set_ylim(-20, 6); a.set_xlim(wx[0], wx[-1])
finish(a, xlabel="Normalized frequency $\\omega/\\omega_n$", ylabel="$|H(j\\omega)|/N$ (dB)")
a.legend(loc="lower left", fontsize=6.8)
panel(a, "a")
b.axhline(1, color=MUTED, lw=0.7, ls="--")
finish(b, xlabel="Normalized time $\\omega_n t$", ylabel="Output phase / input step")
b.set_xlim(0, 12); b.set_ylim(0, 1.45)
b.legend(loc="lower right", fontsize=6.8)
panel(b, "b")
savefig(fig, "ch12_resp")

# ================================================================== Fig: WE loop gain and closed loop
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.15))
a.semilogx(f, 20 * np.log10(np.abs(LG)), color=C1, lw=1.4)
a.set_ylim(-40, 80); a.set_xlim(1e4, 1e8)
a.axhline(0, color=MUTED, lw=0.7)
a2 = a.twinx()
a2.semilogx(f, np.angle(LG, deg=True), color=C2, lw=1.2, ls="--")
a2.set_ylim(-200, -60); a2.spines["right"].set_visible(True); a2.grid(False)
a2.set_ylabel("Phase of $LG$ (deg)", color=C2); a2.tick_params(axis="y", colors=C2)
a2.axhline(-180, color=C4, lw=0.6, ls=":")
for fx, lab in [(we["fz"], "$f_z$"), (we["fu"], "$f_u$"), (we["fp"], "$f_{p3}$")]:
    a.axvline(fx, color=MUTED, lw=0.6, ls=":")
    a.text(fx * 1.08, 70, lab, fontsize=7.5, color=NAVY)
a2.annotate("", xy=(1e6, -120), xytext=(1e6, -180),
            arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=C4, mutation_scale=6, shrinkA=0, shrinkB=0))
a2.text(1.15e6, -165, "PM = 60$^\\circ$", fontsize=7, color=C4, bbox=dict(fc="white", ec="none", pad=0.6))
finish(a, xlabel="Frequency (Hz)", ylabel="$|LG(j\\omega)|$ (dB)")
a.text(1.3e4, -33, "$|LG|$", color=C1, fontsize=7.5); a.text(2.2e7, -33, "phase", color=C2, fontsize=7.5)
panel(a, "a")
# second-order approximation with same wn, zeta
s = 1j * 2 * pi * f
H2 = (2 * zeta * wn * s + wn ** 2) / (s ** 2 + 2 * zeta * wn * s + wn ** 2)
b.semilogx(f, Hdb, color=NAVY, lw=1.5, label="third-order loop (R, C$_1$, C$_2$)")
b.semilogx(f, 20 * np.log10(np.abs(H2)), color=C2, lw=1.1, ls="--", label=f"second-order fit ($\\zeta$ = {zeta:.2f})")
b.axhline(-3, color=MUTED, lw=0.7, ls=":")
f3 = f[np.where(Hdb > -3)[0][-1]]
b.plot(f3, -3, "o", color=GOLDDK, ms=4)
b.text(f3 * 1.25, -2.0, f"$f_{{-3\\mathrm{{dB}}}}$ = {f3/1e6:.2f} MHz", fontsize=7, color=GOLDDK)
b.text(2.2e4, 3.0, f"peaking {Hdb.max():.1f} dB", fontsize=7, color=NAVY)
b.set_ylim(-30, 6); b.set_xlim(1e4, 1e8)
finish(b, xlabel="Frequency (Hz)", ylabel="$|H(j\\omega)|/N$ (dB)")
b.legend(loc="lower left", fontsize=6.6)
panel(b, "b")
savefig(fig, "ch12_loop")

# ================================================================== Fig: noise transfer and bandwidth optimum
L1M = 10 ** (-100.8 / 10)
Lvco = L1M * (1e6 / f) ** 2 * (1 + 1e5 / f) + 10 ** (-155 / 10)
Lin = 10 ** (-110 / 10)
def integ(S):
    return np.sqrt(2 * np.trapezoid(S, f)) / (2 * pi * F0)
fus = np.logspace(np.log10(0.3e6), np.log10(10e6), 30)
jv, ji, jt, jt_good = [], [], [], []
for fu in fus:
    d = design(fu, 200e-6)
    lg, _ = loopgain(d, f)
    Hc = lg / (1 + lg); Ec = 1 / (1 + lg)
    v = integ(Lvco * np.abs(Ec) ** 2); r = integ(Lin * np.abs(Hc) ** 2)
    vg = integ(Lvco * 10 ** (-22 / 10) * np.abs(Ec) ** 2)
    jv.append(v); ji.append(r); jt.append(np.hypot(v, r)); jt_good.append(np.hypot(vg, r))
jv, ji, jt, jt_good = map(np.array, (jv, ji, jt, jt_good))
k = np.argmin(jt)
print(f"bandwidth optimum: fu={fus[k]/1e6:.2f} MHz total={jt[k]*1e12:.2f} ps (vco {jv[k]*1e12:.2f}, inband {ji[k]*1e12:.2f})")
for fu in [0.5e6, 1e6, 2e6, 3e6, 6e6]:
    d = design(fu, 200e-6); lg, _ = loopgain(d, f)
    v = integ(Lvco * np.abs(1 / (1 + lg)) ** 2); r = integ(Lin * np.abs(lg / (1 + lg)) ** 2)
    print(f"   fu={fu/1e6:.1f}: VCO {v*1e12:.2f} in-band {r*1e12:.2f} total {np.hypot(v,r)*1e12:.2f} ps")
print(f"if VCO 22 dB better: min total {jt_good.min()*1e12:.2f} ps at fu={fus[np.argmin(jt_good)]/1e6:.2f} MHz; at 3 MHz {np.interp(3e6,fus,jt_good)*1e12:.2f}")
# loop-filter resistor noise (band-pass) for the 1 MHz and 3 MHz designs
for d in (we, d3):
    lg, _ = loopgain(d, f)
    SvR = 4 * kB * Tk * d["R"]
    Sphi = SvR * (d["Kv"] / (2 * pi * f)) ** 2 * np.abs(1 / (1 + lg)) ** 2   # rad^2/Hz (double-sided->single)
    # Sphi is the one-sided phase PSD; L = Sphi/2, sigma_phi^2 = int Sphi df
    sig = np.sqrt(np.trapezoid(Sphi, f)) / (2 * pi * F0)
    print(f"   R noise ({d['fu']/1e6:.0f} MHz, R={d['R']/1e3:.1f}k): {sig*1e12:.2f} ps")

fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.15))
for fu, ls in [(1e6, "--"), (3e6, "-")]:
    d = design(fu, 200e-6); lg, _ = loopgain(d, f)
    a.semilogx(f, 20 * np.log10(np.abs(lg / (1 + lg))), color=C2, ls=ls, lw=1.3)
    a.semilogx(f, 20 * np.log10(np.abs(1 / (1 + lg))), color=C4, ls=ls, lw=1.3)
a.text(1.5e4, 2.2, "reference, CP: low-pass ($\\times N$)", fontsize=7, color=C2)
a.text(1.5e4, -8, "VCO: high-pass", fontsize=7, color=C4)
a.plot([], [], color=MUTED, ls="--", label="$f_u$ = 1 MHz"); a.plot([], [], color=MUTED, ls="-", label="$f_u$ = 3 MHz")
a.legend(loc="lower right", fontsize=6.8)
a.set_ylim(-45, 8); a.set_xlim(1e4, 1e8)
finish(a, xlabel="Offset frequency (Hz)", ylabel="Noise transfer (dB)")
panel(a, "a")
b.semilogx(fus / 1e6, jv * 1e12, color=C4, lw=1.2, label="VCO term ($\\propto f_u^{-1/2}$)")
b.semilogx(fus / 1e6, ji * 1e12, color=C2, lw=1.2, label="in-band term ($\\propto f_u^{1/2}$)")
b.semilogx(fus / 1e6, jt * 1e12, color=NAVY, lw=1.8, label="total (RSS)")
b.semilogx(fus / 1e6, jt_good * 1e12, color=MUTED, lw=1.0, ls=":", label="total if VCO is 22 dB quieter")
b.plot(fus[k] / 1e6, jt[k] * 1e12, "o", color=GOLDDK, ms=4.5)
b.text(fus[k] / 1e6, jt[k] * 1e12 + 0.18, f"optimum\n{fus[k]/1e6:.1f} MHz, {jt[k]*1e12:.2f} ps", fontsize=6.8, color=GOLDDK, ha="center")
b.set_ylim(0, 2.6); b.set_xlim(0.3, 10)
b.set_xticks([0.3, 1, 3, 10]); b.set_xticklabels(["0.3", "1", "3", "10"])
finish(b, xlabel="Loop bandwidth $f_u$ (MHz)", ylabel="Integrated jitter (ps rms)")
b.legend(loc="upper right", fontsize=6.3)
panel(b, "b")
savefig(fig, "ch12_noise")

# ================================================================== Fig: Leeson
Lind, Q = 4e-9, 16.8
w0 = 2 * pi * F0
Ctot = 1 / (w0 ** 2 * Lind); Rp = Q * w0 * Lind
print(f"tank: C = {Ctot*1e12:.3f} pF, Rp = {Rp:.0f} Ohm, gm_min = {2/Rp*1e3:.2f} mS")
print(f"   at 2.4 GHz with 4 nH: C = {1/((2*pi*2.4e9)**2*Lind)*1e12:.3f} pF; C ratio 2.4->2.5 = {(2.5/2.4)**2:.3f}")
def leeson(df, V=0.6, Qt=Q, F=2.0, fc3=1e5):
    Rpt = Qt * w0 * Lind
    P = V ** 2 / (2 * Rpt)
    return 10 * np.log10(2 * F * kB * Tk / P * (1 + (F0 / (2 * Qt * df)) ** 2) * (1 + fc3 / df))
print(f"Leeson at 1 MHz (Q 16.8, 0.6 V, F=2): {leeson(1e6):.1f} dBc/Hz")
for Pv in [5e-3, 12.73e-3]:
    for Lx in [-100.8, leeson(1e6)]:
        print(f"   FoM (L={Lx:.1f}, P={Pv*1e3:.2f} mW) = {-Lx + 20*np.log10(F0/1e6) - 10*np.log10(Pv/1e-3):.1f} dB")
Vneed = 0.6 / 10 ** ((-100.8 - leeson(1e6)) / 20)
print(f"swing needed for -100.8 with F=2: {Vneed*1e3:.0f} mV")
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.15))
df = np.logspace(4, 8, 400)
a.semilogx(df, leeson(df), color=NAVY, lw=1.5, label="Leeson: $Q$ = 16.8, 0.6 V, $F$ = 2")
a.semilogx(df, leeson(df, F=2 * 10 ** 2.19), color=C4, lw=1.0, ls="--", label="same, 22 dB excess noise")
a.plot(1e6, -100.8, "o", color=C4, ms=5)
a.text(1.3e6, -99, "team PLL: $-$100.8 dBc/Hz", fontsize=6.8, color=C4)
a.plot(1e6, leeson(1e6), "o", color=NAVY, ms=4)
a.text(1.3e6, leeson(1e6) + 1.5, f"{leeson(1e6):.0f} dBc/Hz", fontsize=6.8, color=NAVY)
a.text(1.3e4, -132, "1/$f^3$ (flicker)", fontsize=6.8, color=MUTED)
a.text(1.3e4, -142, "1/$f^2$ (thermal, shaped by $Q$)", fontsize=6.8, color=MUTED)
a.text(2.0e7, -138, "floor", fontsize=6.8, color=MUTED)
a.axvline(1e5, color=GRID, lw=0.8); a.axvline(F0 / (2 * Q), color=GRID, lw=0.8)
a.set_ylim(-165, -60); a.set_xlim(1e4, 1e8)
finish(a, xlabel="Offset frequency (Hz)", ylabel="Phase noise (dBc/Hz)")
a.legend(loc="upper right", fontsize=6.3)
panel(a, "a")
Vs = np.linspace(0.05, 1.2, 200)
for Qt, c in [(10, C2), (16.8, NAVY), (25, C3)]:
    b.plot(Vs, [leeson(1e6, V=v, Qt=Qt) for v in Vs], color=c, lw=1.3, label=f"$Q$ = {Qt:g}")
b.axhline(-100.8, color=C4, lw=0.9, ls="--")
b.text(0.62, -99.5, "team PLL value at 1 MHz", fontsize=6.8, color=C4)
b.set_ylim(-140, -95); b.set_xlim(0, 1.2)
finish(b, xlabel="Tank amplitude (V peak, differential)", ylabel="$\\mathcal{L}$(1 MHz) from Leeson (dBc/Hz)".replace("$\\mathcal{L}$", "L"))
b.legend(loc="center right", fontsize=6.8)
panel(b, "b")
savefig(fig, "ch12_leeson")

# ================================================================== Fig: polyphase filter
def poly_out(fq, taus_R, taus_C, Rm=None, Cm=None, CL=0.0):
    """Nodal solve of a cascade of RC polyphase stages, input (1,0,-1,0).
    Rm, Cm: arrays (nst,4) of relative values. Returns the 4 output phasors."""
    nst = len(taus_R)
    wq = 2 * pi * fq
    n_unk = 4 * nst
    Y = np.zeros((n_unk, n_unk), complex); I = np.zeros(n_unk, complex)
    vin = np.array([1, 0, -1, 0], complex)
    def idx(st, i): return 4 * (st - 1) + i       # stage st output node i (st>=1)
    for st in range(nst):
        for i in range(4):
            R = taus_R[st] * (1 if Rm is None else Rm[st, i])
            C = taus_C[st] * (1 if Cm is None else Cm[st, i])
            yR, yC = 1 / R, 1j * wq * C
            o = idx(st + 1, i)
            for (src, y) in [(i, yR), ((i - 1) % 4, yC)]:   # R from same phase, C from previous phase
                Y[o, o] += y
                if st == 0:
                    I[o] += y * vin[src]
                else:
                    sidx = idx(st, src)
                    Y[o, sidx] -= y; Y[sidx, sidx] += y; Y[sidx, o] -= y
        if CL and st == nst - 1:
            for i in range(4):
                Y[idx(st + 1, i), idx(st + 1, i)] += 1j * wq * CL
    V = np.linalg.solve(Y, I)
    return V[-4:]
def iq_err(V):
    ph = np.angle(V[1] / V[0], deg=True)       # nominal +-90
    amp = 20 * np.log10(np.abs(V[0]) / np.abs(V[1]))
    return abs(ph) - 90, amp
R0 = 500.0
fq = np.linspace(1.5e9, 4.0e9, 300)
one = [iq_err(poly_out(x, [R0], [1 / (2 * pi * 2.5e9 * R0)])) for x in fq]
fp1, fp2 = 2.5e9 / 1.25, 2.5e9 * 1.25
two = [iq_err(poly_out(x, [R0, R0], [1 / (2 * pi * fp1 * R0), 1 / (2 * pi * fp2 * R0)])) for x in fq]
one, two = np.array(one), np.array(two)
print(f"poly: ideal 1-stage phase error max {np.abs(one[:,0]).max():.3f} deg; amp imbalance at 2.0/3.0 GHz: "
      f"{np.interp(2.0e9,fq,one[:,1]):.2f}/{np.interp(3.0e9,fq,one[:,1]):.2f} dB; 2-stage {np.interp(2.0e9,fq,two[:,1]):.2f}/{np.interp(3.0e9,fq,two[:,1]):.2f} dB")
rng = np.random.default_rng(7)
mc1, mc2 = [], []
for _ in range(3000):
    Rm = 1 + 0.01 * rng.standard_normal((2, 4)); Cm = 1 + 0.01 * rng.standard_normal((2, 4))
    mc1.append(iq_err(poly_out(2.5e9, [R0], [1 / (2 * pi * 2.5e9 * R0)], Rm[:1], Cm[:1]))[0])
    mc2.append(iq_err(poly_out(2.5e9, [R0, R0], [1 / (2 * pi * fp1 * R0), 1 / (2 * pi * fp2 * R0)], Rm, Cm))[0])
mc1, mc2 = np.array(mc1), np.array(mc2)
V2 = poly_out(2.5e9, [R0, R0], [1 / (2 * pi * fp1 * R0), 1 / (2 * pi * fp2 * R0)])
V1 = poly_out(2.5e9, [R0], [1 / (2 * pi * 2.5e9 * R0)])
print(f"poly output amplitude (input diff amplitude 2): 1-stage {np.abs(V1[0]):.3f}, 2-stage {np.abs(V2[0]):.3f}; loss 2-stage {20*np.log10(np.abs(V2[0])):.1f} dB rel. single-ended input")
print(f"poly MC 1% mismatch: sigma phase err 1-stage {mc1.std():.2f} deg, 2-stage {mc2.std():.2f} deg "
      f"(= {mc1.std()*400/360:.2f}/{mc2.std()*400/360:.2f} ps); 3-sigma 2-stage {3*mc2.std():.2f} deg")
# with RC +-20 % process shift: amplitude imbalance at 2.5 GHz
for sh in (0.8, 1.2):
    v1 = iq_err(poly_out(2.5e9, [R0], [sh / (2 * pi * 2.5e9 * R0)]))[1]
    v2 = iq_err(poly_out(2.5e9, [R0, R0], [sh / (2 * pi * fp1 * R0), sh / (2 * pi * fp2 * R0)]))[1]
    print(f"   RC x{sh}: imbalance 1-stage {v1:.2f} dB, 2-stage {v2:.2f} dB")
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.15))
a.plot(fq / 1e9, np.abs(one[:, 1]), color=C4, lw=1.3, label="1 stage ($f_p$ = 2.5 GHz)")
a.plot(fq / 1e9, np.abs(two[:, 1]), color=C1, lw=1.5, label="2 stages (2.0, 3.1 GHz)")
a.axvspan(2.5 / 1.2, 2.5 / 0.8, color=GOLDLT, alpha=0.2, lw=0)
a.text(2.6, 2.45, "2.5 GHz with\n$RC$ $\\pm$20%", fontsize=6.8, color=GOLDDK, ha="center")
a.set_ylim(0, 4.0); a.set_xlim(1.5, 4.0)
finish(a, xlabel="Clock frequency (GHz)", ylabel="I/Q amplitude imbalance (dB)")
a.legend(loc="upper center", fontsize=6.6)
panel(a, "a")
bins = np.linspace(-2.5, 2.5, 61)
b.hist(mc1, bins=bins, color=C4, alpha=0.45, label=f"1 stage, $\\sigma$ = {mc1.std():.2f}$^\\circ$")
b.hist(mc2, bins=bins, color=C1, alpha=0.6, label=f"2 stages, $\\sigma$ = {mc2.std():.2f}$^\\circ$")
finish(b, xlabel="Quadrature phase error at 2.5 GHz (deg)", ylabel="Count (3000 runs)")
b.legend(loc="upper left", fontsize=6.6)
b.text(1.3, b.get_ylim()[1] * 0.55, "1% random\nR and C\nmismatch\n\n1$^\\circ$ = 1.11 ps", fontsize=6.8, color=MUTED)
panel(b, "b")
savefig(fig, "ch12_poly")
