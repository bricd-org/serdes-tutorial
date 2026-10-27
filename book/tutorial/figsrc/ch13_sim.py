"""ch13_sim.py -- behavioural model of the Open-SERDES PI-based bang-bang CDR (Chapter 13).

Phase model, one loop update per 8 UI (625 MHz, the 1:8 point of the deserializer), all phases in UI.
  * half-rate Alexander BBPD: one early/late decision per data transition (TD = 0.5)
  * majority vote of the decisions in one update -> v in {-1, 0, +1}
  * latency D extra updates, digital P+I loop filter:  f += Ki*v ;  acc += Kp*v + f
  * PI code = round(acc), 64 steps per 2 UI (6.25 ps); clock phase = code * LSB
Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch13_sim.py
Writes ch13_sim.pdf and ch13_pi_data.npz (JTOL / JTRAN points used by ch13_cdr.py).
"""
from bricdstyle import *
from scipy.stats import norm

UIps = 200.0
BASE = dict(nsteps=64, Kp=0.125, Ki=0.125 / 128, D=1, nb=8)     # Open-SERDES baseline (625 MHz loop)
TUPD = BASE["nb"] * 200e-12


def run(n_upd, nsteps=64, Kp=0.25, Ki=0.25 / 32, D=1, nb=16, ppm=0.0, phi0=0.0, sj_pp=0.0, sj_f=0.0,
        rj=0.0066, ddj=0.1, seed=1, record=True):
    """Scalar simulation. Returns dict of time series (per update)."""
    rng = np.random.default_rng(seed)
    lsb = 2.0 / nsteps
    acc = 0.0; freg = 0.0; pipe = [0.0] * (D + 1)
    b = np.arange(nb)
    out = {k: np.zeros(n_upd) for k in ("code", "err", "freg", "phd")}
    for k in range(n_upd):
        code = np.round(acc)
        tb = k * nb + b
        phd = phi0 + ppm * 1e-6 * tb + 0.5 * sj_pp * np.sin(2 * np.pi * sj_f * tb)
        e = (phd - code * lsb + 0.5) % 1.0 - 0.5
        trans = rng.random(nb) < 0.5
        j = rj * rng.standard_normal(nb) + ddj * (rng.random(nb) - 0.5)
        v = np.sign((np.sign(e + j) * trans).sum())
        pipe.append(v); u = pipe.pop(0)
        freg += Ki * u
        acc += Kp * u + freg
        out["code"][k] = code % nsteps; out["err"][k] = e.mean(); out["freg"][k] = freg; out["phd"][k] = phd.mean()
    return out


def jtol(fj, nsteps=64, Kp=0.25, Ki=0.25 / 32, D=1, nb=16, TM=0.4, rj=0.0066, ddj=0.1, seed=0,
         amps=np.logspace(-1.3, 2.3, 90)):
    """Largest sinusoidal-jitter amplitude (UIpp) at fj [Hz] for which |phase error| < TM/2 (vectorized)."""
    na = len(amps); rng = np.random.default_rng(seed); lsb = 2.0 / nsteps
    Tui = 5e9 / fj
    n0 = int(np.ceil(Tui / nb)); n_upd = 4 * n0
    acc = np.zeros(na); freg = np.zeros(na); pipe = [np.zeros(na) for _ in range(D + 1)]
    maxe = np.zeros(na); b = np.arange(nb)
    for k in range(n_upd):
        phc = np.round(acc) * lsb
        tb = k * nb + b
        e = 0.5 * amps[:, None] * np.sin(2 * np.pi * tb[None, :] / Tui) - phc[:, None]
        trans = rng.random(nb) < 0.5
        j = rj * rng.standard_normal(nb) + ddj * (rng.random(nb) - 0.5)
        v = np.sign((np.sign(e + j[None, :]) * trans[None, :]).sum(axis=1))
        pipe.append(v); u = pipe.pop(0)
        freg += Ki * u; acc += Kp * u + freg
        if k >= n0:
            maxe = np.maximum(maxe, np.abs(e).max(axis=1))
    ok = maxe < TM / 2
    if not ok[0]:
        return amps[0]
    return amps[np.argmax(~ok) - 1] if (~ok).any() else amps[-1]


def jtran(fj, a_pp, nsteps=64, Kp=0.25, Ki=0.25 / 32, D=1, nb=16, rj=0.0066, ddj=0.1, seed=2, nper=8):
    """|phi_clk/phi_data| at fj for SJ amplitude a_pp (UIpp), by lock-in over nper periods."""
    Tui = 5e9 / fj
    n_upd = int(np.ceil((nper + 1) * Tui / nb))
    r = run(n_upd, nsteps, Kp, Ki, D, nb, sj_pp=a_pp, sj_f=1 / Tui, rj=rj, ddj=ddj, seed=seed)
    k0 = int(np.ceil(Tui / nb))
    t = (np.arange(n_upd) * nb + nb / 2)[k0:]
    phc = (r["phd"] - r["err"])[k0:]
    ref = np.exp(-2j * np.pi * t / Tui)
    return np.abs(np.sum(phc * ref)) / np.abs(np.sum(r["phd"][k0:] * ref))


def stats(cfg, n=150000, seed=3):
    r = run(n, ppm=200, phi0=0.3, seed=seed, **cfg)
    es = r["err"][30000:] * UIps
    q = np.quantile(es, [1e-5, 1 - 1e-5])
    return es.std(), q[1] - q[0]


if __name__ == "__main__":
    lsb_ps = 400 / 64
    Tp = TUPD * 1e12
    S = BASE["Kp"] * lsb_ps / UIps / TUPD
    print(f"baseline: T_upd = {Tp:.0f} ps, Kp = {BASE['Kp']*lsb_ps:.3f} ps/update, slew S = {S:.3g} UI/s, "
          f"prop-only range = {BASE['Kp']*lsb_ps/Tp*1e6:.0f} ppm; max code rate 1 LSB/update = {lsb_ps/Tp*1e6:.0f} ppm; Kp/Ki = {BASE['Kp']/BASE['Ki']:.0f}")
    for ppm in (200, 300):
        print(f"   {ppm} ppm -> {ppm*1e-6*Tp/lsb_ps:.4f} LSB/update, wrap every {64/(ppm*1e-6*Tp/lsb_ps):.0f} updates "
              f"= {64/(ppm*1e-6*Tp/lsb_ps)*Tp*1e-6:.2f} us, PI rotation rate {ppm*1e-6*5e9/2/1e3:.0f} kHz")
    # ---------------------------------------------------------------- lock + track +200 ppm
    n = 6000
    r = run(n, ppm=200, phi0=0.37, seed=5, **BASE)
    t_us = np.arange(n) * TUPD * 1e6
    fppm = r["freg"] * lsb_ps / (TUPD * 1e12) * 1e6
    lock = np.argmax(np.convolve(np.abs(r["err"]) < 0.05, np.ones(50), "same") >= 50)
    print(f"lock: phase error < 0.05 UI from update {lock} ({lock*TUPD*1e6:.2f} us); freg final mean {fppm[-1000:].mean():.0f} ppm")
    fig = plt.figure(figsize=(6.3, 3.1))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1])
    a = fig.add_subplot(gs[0, :]); b = fig.add_subplot(gs[1, 0]); c = fig.add_subplot(gs[1, 1])
    ideal = (r["phd"] / (2.0 / 64)) % 64
    a.plot(t_us, ideal, color=GOLD, lw=2.4, alpha=0.5, label="ideal code (data phase)")
    a.plot(t_us, r["code"], color=NAVY, lw=0.8, label="PI code")
    a.set_xlim(0, t_us[-1]); a.set_ylim(-2, 80); a.set_yticks([0, 16, 32, 48, 64])
    finish(a, xlabel="Time ($\\mu$s)", ylabel="PI code (0..63)")
    a.legend(loc="upper left", fontsize=6.8, ncol=2)
    rate = 200e-6 * TUPD * 1e12 / lsb_ps
    a.text(9.5, 72, f"+200 ppm: the code wraps every {64/rate*TUPD*1e6:.1f} $\\mu$s (2 UI of drift)", fontsize=6.8, color=MUTED, ha="right")
    panel(a, "a")
    b.plot(t_us, fppm, color=C1, lw=0.9)
    b.axhline(200, color=GOLDDK, lw=0.8, ls="--")
    b.text(5.0, 140, "true offset +200 ppm", fontsize=7, color=GOLDDK)
    b.set_xlim(0, t_us[-1]); b.set_ylim(-50, 420)
    finish(b, xlabel="Time ($\\mu$s)", ylabel="Integral register (ppm)")
    panel(b, "b")
    c.plot(t_us, r["err"] * UIps, color=C3, lw=0.7)
    c.set_xlim(0, 1.5); c.set_ylim(-30, 80)
    c.annotate("lock in\n0.2 $\\mu$s", xy=(0.19, 5), xytext=(0.45, 45), fontsize=7, color=NAVY,
               arrowprops=dict(arrowstyle="-|>", lw=0.7, color=NAVY, mutation_scale=6))
    finish(c, xlabel="Time ($\\mu$s), first 1.5 $\\mu$s", ylabel="Phase error (ps)")
    sd = r["err"][1500:].std() * UIps
    c.text(0.8, 22, f"tracking: {sd:.1f} ps rms", fontsize=7, color=C3)
    panel(c, "c")
    savefig(fig, "ch13_sim")
    print(f"tracking error rms (after {1500*TUPD*1e6:.1f} us) = {sd:.2f} ps")

    # ---------------------------------------------------------------- step-size / loop-clock table
    cfgs = [("64 steps, integer step Kp = 1 LSB", dict(nsteps=64, Kp=1.0, Ki=1.0 / 32, D=1, nb=16)),
            ("64 steps, Kp = 1/4 LSB", dict(nsteps=64, Kp=0.25, Ki=0.25 / 32, D=1, nb=16)),
            ("128 steps, Kp = 1/2 LSB", dict(nsteps=128, Kp=0.5, Ki=0.5 / 32, D=1, nb=16)),
            ("64 steps, 625 MHz loop, Kp = 1/8 LSB (baseline)", BASE),
            ("128 steps, 625 MHz loop, Kp = 1/4 LSB", dict(nsteps=128, Kp=0.25, Ki=0.25 / 128, D=1, nb=8))]
    fm = [0.5e6, 1e6, 2e6, 4.9e6]; mk = [2.0, 1.0, 0.5, 0.2]
    for lab, cfg in cfgs:
        rms, pp = stats(cfg)
        jt = [jtol(f, **cfg) for f in fm]
        marg = min(j / m for j, m in zip(jt, mk))
        Sx = cfg["Kp"] * (400 / cfg["nsteps"]) / UIps / (cfg["nb"] * 200e-12)
        print(f"{lab:40s} S={Sx:.2e} UI/s  wander rms {rms:.2f} ps  pp(1e-5) {pp:.1f} ps  JTOL margin {marg:.2f}  ({' '.join(f'{j:.2f}' for j in jt)})")

    # ---------------------------------------------------------------- JTOL and JTRAN of the baseline (saved for ch13_cdr.py)
    fj = np.array([0.1e6, 0.2e6, 0.3e6, 0.5e6, 0.7e6, 1e6, 1.5e6, 2e6, 3e6, 4.9e6, 7e6, 10e6, 20e6, 50e6])
    jt = np.array([jtol(f, **BASE) for f in fj])
    print("PI-CDR JTOL:", " ".join(f"{f/1e6:g}M:{j:.2f}" for f, j in zip(fj, jt)))
    ft = np.logspace(5, 7.7, 12)
    tr = {a: np.array([jtran(f, a, **BASE) for f in ft]) for a in (0.05, 0.2)}
    for a, v in tr.items():
        db = 20 * np.log10(v)
        k3 = np.where(db < -3)[0]
        f3 = ft[k3[0]] if len(k3) else np.nan
        print(f"PI-CDR JTRAN A={a} UIpp: peak {db.max():.1f} dB, f-3dB ~ {f3/1e6:.1f} MHz;", " ".join(f"{x:.1f}" for x in db))
    np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch13_pi_data.npz"),
             fj=fj, jt=jt, ft=ft, tr005=tr[0.05], tr02=tr[0.2])
