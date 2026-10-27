"""ch04_stateye.py -- statistical-eye engine + Chapter 4 figures (ISI PDF, stat eye, bathtub).

Reusable API (Chapter 16 may import it:  from ch04_stateye import stat_eye, isi_pdf):
    isi_pdf(cursors, A, v)                 -> PMF of the ISI sum on voltage grid v
    stat_eye(p, idx0, ...)                 -> dict with phase axis, threshold axis, BER map, PDF map
    eye_metrics(se, target)                -> eye height / width at a BER target
Method (Casper 2002, Sanders 2004): at each sampling phase the ISI is the sum of
independent two-point variables +-A*p_k, so its PDF is the convolution of the two-point
PDFs; Gaussian noise is one more convolution; sampling jitter is a convolution along time.

Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch04_stateye.py
"""
import numpy as np
from scipy.special import erfc
from bricdstyle import *
from link import *

FFE2 = np.array([0.6515, -0.3485])   # 2-tap ZF TX de-emphasis for REF (Lab 3), sum|c| = 1


def ffe_pulse(p, taps, sps=SPS):
    """Pulse response with a TX FIR [c0, c1, ...] (main tap first, post taps after)."""
    q = np.zeros_like(p)
    for n, c in enumerate(taps):
        q[n * sps:] += c * p[:p.size - n * sps]
    return q


def isi_pdf(cursors, A, v):
    """PMF of sum_k a_k*A*c_k (a_k = +-1 equiprobable) on the uniform grid v (must be wide
    enough). Each delta is split linearly between neighbouring bins, so the mean is exact."""
    dv = v[1] - v[0]
    pmf = np.zeros(v.size)
    pmf[np.argmin(np.abs(v))] = 1.0
    for c in cursors:
        s = A * abs(c) / dv
        n = int(np.floor(s)); f = s - n
        up = (1 - f) * np.roll(pmf, n) + f * np.roll(pmf, n + 1)
        dn = (1 - f) * np.roll(pmf, -n) + f * np.roll(pmf, -n - 1)
        pmf = 0.5 * (up + dn)
    return pmf


def gauss_kernel(sigma, dv, nsig=12):
    if sigma <= 0:
        return np.array([1.0])
    x = np.arange(-int(np.ceil(nsig * sigma / dv)), int(np.ceil(nsig * sigma / dv)) + 1) * dv
    g = np.exp(-0.5 * (x / sigma) ** 2)
    return g / g.sum()


def jitter_kernel(rj, dj, dt, nsig=8):
    """Dual-Dirac + Gaussian jitter PDF sampled on time step dt (seconds)."""
    half = dj / 2
    span = half + nsig * max(rj, dt)
    x = np.arange(-int(np.ceil(span / dt)), int(np.ceil(span / dt)) + 1) * dt
    if rj <= 0:
        w = np.zeros(x.size)
        for m in (-half, half):
            w[np.argmin(np.abs(x - m))] += 0.5
        return w
    w = 0.5 * (np.exp(-0.5 * ((x - half) / rj) ** 2) + np.exp(-0.5 * ((x + half) / rj) ** 2))
    return w / w.sum()


def stat_eye(p, idx0, A=A_TX, sigma_n=0.0, rj=0.0, dj=0.0, n_pre=3, n_post=150,
             up=4, span_ui=0.75, dv=0.05e-3, vout=np.linspace(-0.25, 0.25, 401)):
    """Statistical eye of pulse response p (1 V, 1 UI; samples of DT) around index idx0.
    Phases cover +-span_ui UI in steps of DT/up. Returns dict(t_ui, v, ber, pdf)."""
    nph = int(round(span_ui * SPS * up))
    off = np.arange(-nph, nph + 1) / up                    # offset from idx0 in samples
    grid = np.arange(p.size)
    ks = np.array([k for k in range(-n_pre, n_post + 1) if k != 0])
    vmax = A * np.sum(np.abs(p[idx0 + ks * SPS])) * 1.6 + 12 * sigma_n + 0.05
    v = np.arange(-vmax, vmax + dv / 2, dv)
    g = gauss_kernel(sigma_n, dv)
    ber = np.empty((off.size, vout.size)); pdf = np.empty((off.size, vout.size))
    c0s = np.empty(off.size)
    for i, o in enumerate(off):
        c0 = np.interp(idx0 + o, grid, p)
        ck = np.interp(idx0 + o + ks * SPS, grid, p)
        pmf = isi_pdf(ck, A, v)
        if g.size > 1:
            pmf = np.convolve(pmf, g, mode="same")
        cdf = np.cumsum(pmf)
        F = lambda x: np.interp(x, v, cdf, left=0.0, right=1.0)
        ber[i] = 0.5 * (F(vout - A * c0) + F(-vout - A * c0))   # P(y1<v)/2 + P(y0>v)/2
        dens = pmf / dv
        pdf[i] = 0.5 * (np.interp(vout - A * c0, v, dens, 0, 0) + np.interp(vout + A * c0, v, dens, 0, 0))
        c0s[i] = c0
    if rj > 0 or dj > 0:                                  # sampling-time jitter: convolve in t
        w = jitter_kernel(rj, dj, DT / up)
        pad = w.size // 2
        bp = np.pad(ber, ((pad, pad), (0, 0)), mode="edge")
        ber = np.stack([np.convolve(bp[:, j], w, mode="valid") for j in range(vout.size)], axis=1)
        pp = np.pad(pdf, ((pad, pad), (0, 0)), mode="edge")
        pdf = np.stack([np.convolve(pp[:, j], w, mode="valid") for j in range(vout.size)], axis=1)
    return dict(t_ui=off / SPS, v=vout, ber=ber, pdf=pdf, c0=c0s)


def eye_metrics(se, target=1e-12):
    """Eye height [V] at the best phase and eye width [UI] at v = 0, for BER < target."""
    ok = se["ber"] < target
    v, t = se["v"], se["t_ui"]
    dv = v[1] - v[0]
    heights = np.array([ok[i].sum() * dv for i in range(t.size)])   # contiguous for one eye
    ib = int(np.argmax(heights))
    j0 = np.argmin(np.abs(v))
    width = ok[:, j0].sum() * (t[1] - t[0])
    return heights[ib], width, ib


def q_of(ber):
    from scipy.special import erfcinv
    return np.sqrt(2) * erfcinv(2 * ber)


if __name__ == "__main__":
    H = channel(REF_LEN)
    t, p = pulse_of(H)
    i0 = int(np.argmax(p))
    q = ffe_pulse(p, FFE2)
    j0 = int(np.argmax(q))
    print(f"REF p0 = {p[i0]:.4f} at {t[i0]*1e9:.3f} ns; FFE pulse peak {q[j0]:.4f} at {t[j0]*1e9:.3f} ns"
          f" (shift {(j0-i0)} samples)")
    kq, qk, _ = cursors(q, n_pre=3, n_post=10, idx0=j0)
    print("FFE cursors k=-3..10:", np.round(qk, 4))
    SIG, RJ, DJ = 1.5e-3, 2e-12, 20e-12
    print(f"2Q sigma_n = {2*7.034*SIG*1e3:.1f} mV")

    # ---------- ISI PDF figure
    kk, pk_ref, _ = cursors(p, n_pre=3, n_post=150)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.55), gridspec_kw=dict(width_ratios=[1, 1.15]))
    v = np.arange(-0.4, 0.4, 0.25e-3)
    rows = [((1,), "$p_1$ only"), ((1, 2), "$p_1, p_2$"), ((-1, 1, 2, 3), "$p_{-1}, p_1, p_2, p_3$")]
    for r, (sel, lab) in enumerate(rows):
        c = [pk_ref[list(kk).index(s)] for s in sel]
        vals = np.array([0.0])
        for ci in c:
            vals = np.concatenate([vals + A_TX * ci, vals - A_TX * ci])
        base = 2.0 - r
        uniq, cnt = np.unique(np.round(vals, 4), return_counts=True)
        for u_, n_ in zip(uniq, cnt):
            ax1.vlines(u_ * 1e3, base, base + 0.42 * n_ / cnt.max(), color=C1, lw=1.6)
        ax1.axhline(base, color=MUTED, lw=0.6)
        ax1.text(-195, base + 0.55, lab + f"  ({len(vals)} patterns)", fontsize=7, color=NAVY)
    ax1.set_xlim(-200, 200); ax1.set_ylim(-0.1, 3.0); ax1.set_yticks([])
    ax1.grid(False, axis="y")
    finish(ax1, "ISI voltage (mV)")
    ax1.set_ylabel("Probability", color=NAVY)
    panel(ax1, "a")
    # (b) PDF of the received '1' sample, log scale: REF and REF + FFE
    vv = np.arange(-0.35, 0.45, 0.05e-3)
    for pp, idx, col, lab in ((p, i0, C4, "REF, no EQ"), (q, j0, C3, "REF + 2-tap FFE")):
        ks = np.array([k for k in range(-3, 151) if k != 0])
        ck = pp[idx + ks * SPS]
        pmf = np.convolve(isi_pdf(ck, A_TX, vv - vv.mean()), gauss_kernel(SIG, 0.05e-3), "same")
        dens = pmf / 0.05e-3
        x = vv - vv.mean() + A_TX * pp[idx]
        ax2.semilogy(x * 1e3, np.maximum(dens, 1e-30), color=col, lw=1.3, label=lab)
        worst = A_TX * (pp[idx] - np.sum(np.abs(ck)))
        ax2.axvline(worst * 1e3, color=col, lw=0.8, ls="--")
        cdf = np.cumsum(pmf)
        x12 = np.interp(1e-12, cdf, x)
        print(f"{lab}: A*c0 = {A_TX*pp[idx]*1e3:.1f} mV, PDA worst '1' = {worst*1e3:.1f} mV,"
              f" 1e-12 quantile (with noise) = {x12*1e3:.1f} mV, P(y1<0) = {np.interp(0, x, cdf):.2e}")
    ax2.axvline(0, color=NAVY, lw=0.8)
    ax2.text(3, 3e-15, "decision\nthreshold", fontsize=6.8, color=NAVY)
    ax2.text(-262, 2e-26, "dashed: PDA\nworst case", fontsize=6.8, color=MUTED)
    ax2.set_xlim(-280, 320); ax2.set_ylim(1e-30, 1e3)
    ax2.set_yticks([1e-30, 1e-24, 1e-18, 1e-12, 1e-6, 1])
    finish(ax2, "Received sample for a '1' (mV)", "PDF (1/V)")
    ax2.legend(loc="upper left", fontsize=6.8)
    panel(ax2, "b")
    savefig(fig, "ch04_isipdf")

    # ---------- statistical eye + bathtub (REF + 2-tap FFE)
    se0 = stat_eye(q, j0)                                   # ISI only
    se1 = stat_eye(q, j0, sigma_n=SIG)                      # + noise
    se2 = stat_eye(q, j0, sigma_n=SIG, rj=RJ, dj=DJ)        # + noise + jitter
    se3 = stat_eye(q, j0, rj=RJ, dj=DJ)                     # ISI + jitter (no noise)
    res = {}
    for name, se in (("ISI only", se0), ("ISI+noise", se1), ("ISI+jitter", se3), ("ISI+noise+jitter", se2)):
        for tg in (1e-3, 1e-6, 1e-9, 1e-12):
            eh, ew, ib = eye_metrics(se, tg)
            res[(name, tg)] = (eh, ew, se["t_ui"][ib])
        print(f"{name:18s}: EH(1e-12) = {res[(name,1e-12)][0]*1e3:6.1f} mV at t = {res[(name,1e-12)][2]:+.3f} UI,"
              f" EW(1e-12) = {res[(name,1e-12)][1]:.3f} UI; EH(1e-6) = {res[(name,1e-6)][0]*1e3:.1f}")
    # PDA of the FFE pulse vs phase (full tail)
    ks = np.array([k for k in range(-3, 151) if k != 0])
    grid = np.arange(q.size)
    offs = se0["t_ui"] * SPS
    pda = np.array([2 * A_TX * (np.interp(j0 + o, grid, q) - np.sum(np.abs(np.interp(j0 + o + ks * SPS, grid, q)))) for o in offs])
    print(f"PDA (full tail) best = {pda.max()*1e3:.1f} mV at t = {se0['t_ui'][np.argmax(pda)]:+.3f} UI, width = {np.sum(pda>0)*(offs[1]-offs[0])/SPS:.3f} UI")
    np.savez("/tmp/claude-0/-home-claude/c042d0d1-5418-50a5-bd99-52014980c43e/scratchpad/p2/stat.npz",
             eh=[res[(n, 1e-12)][0] for n in ("ISI only", "ISI+noise", "ISI+jitter", "ISI+noise+jitter")],
             c0=se0["c0"][np.argmax(pda)], pda=pda.max())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.75), gridspec_kw=dict(width_ratios=[1.35, 1]))
    se = se2
    lg = np.log10(np.maximum(se["pdf"], 1e-12))
    T, V = np.meshgrid(se["t_ui"], se["v"] * 1e3, indexing="ij")
    ax1.pcolormesh(T, V, lg, cmap=EYE_CMAP, shading="auto", vmin=-1, vmax=lg.max(), rasterized=True)
    lb = np.log10(np.maximum(se["ber"], 1e-300))
    levels = [-12, -9, -6, -3]
    cs = ax1.contour(T, V, lb, levels=levels, colors=[C4, C2, C3, C1], linewidths=1.0)
    ax1.clabel(cs, fmt={-12: "1e-12", -9: "1e-9", -6: "1e-6", -3: "1e-3"}, fontsize=6.3, inline=True)
    eh12, ew12, ib = eye_metrics(se, 1e-12)
    tb = se["t_ui"][ib]
    ax1.annotate("", xy=(tb, eh12 / 2 * 1e3), xytext=(tb, -eh12 / 2 * 1e3),
                 arrowprops=dict(arrowstyle="<->", lw=0.8, color=NAVY, mutation_scale=6))
    ax1.text(tb + 0.03, 8, f"{eh12*1e3:.0f} mV\n@1e-12", fontsize=6.8, color=NAVY)
    ax1.set_xlim(-0.6, 0.6); ax1.set_ylim(-200, 200)
    ax1.grid(False)
    finish(ax1, "Sampling phase from pulse peak (UI)", "Threshold (mV)")
    panel(ax1, "a")
    j = np.argmin(np.abs(se0["t_ui"] - tb))
    for s_, col, lab in ((se0, MUTED, "ISI only"), (se1, C1, "+ noise"), (se2, C4, "+ jitter")):
        e_, _, jj = eye_metrics(s_, 1e-12)
        ax2.semilogy(s_["v"] * 1e3, np.maximum(s_["ber"][jj], 1e-30), color=col, lw=1.2,
                     label=f"{lab}  {e_*1e3:.0f} mV")
    ax2.axhline(1e-12, color=MUTED, lw=0.7, ls=":")
    ax2.text(-29, 3e-12, "BER = 1e-12", fontsize=6.8, color=MUTED)
    ax2.set_xlim(-85, 85); ax2.set_ylim(1e-20, 1)
    ax2.set_yticks([1e-20, 1e-16, 1e-12, 1e-8, 1e-4, 1])
    finish(ax2, "Threshold (mV)", "BER")
    ax2.legend(loc="upper center", fontsize=6.2, title="EH at 1e-12", title_fontsize=6.4, handlelength=1.2)
    panel(ax2, "b")
    savefig(fig, "ch04_stateye")
