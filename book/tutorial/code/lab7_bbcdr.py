"""Lab 7 - Behavioral half-rate bang-bang PI-CDR on a real equalized waveform.

serdespy has no CDR, so this lab builds one around the Lab 4 link (REF channel +
14 dB CTLE, 5 ps rms TX random jitter). The receiver clock runs `ppm` faster
than the data and starts `phi0` UI away from the eye center. Per UI there is one
data sample D and one edge sample E half a UI earlier (the four half-rate
samplers D0 E0 D1 E1 at 0/90/180/270 degrees of the 2.5 GHz clock). The loop:
  * Alexander phase detector: transition and E == previous D -> clock early (+1)
  * one update per 8 UI (625 MHz, the 1:8 demux point): majority vote v
  * latency of D_LAT extra updates, digital P+I filter (units = PI steps):
        f += KI*v ;  acc += KP*v + f ;  PI code = round(acc) mod 64
  * 64-step PI per 2.5 GHz period (2 UI): one step = 6.25 ps = 1/32 UI
Bit errors are counted against the transmitted PRBS, with and without the CDR.
"""
from common import *

N_PI, UPD = 64, 8                         # PI steps per 2 UI, UI per loop update
LSB = 2.0 / N_PI                          # one PI step in UI (6.25 ps)
BASE = dict(kp=1 / 8, ki=1 / 8 / 128, d_lat=1)   # Open-SERDES baseline (Ch. 13)


def link_wave(n_bits, peak_db=14, rj_ui=0.025, seed=7):
    """PRBS7 through REF + CTLE. Returns bits, waveform and the sample index of
    the center of bit 0 (best noise-free phase, found as in common.eye_scan)."""
    np.random.seed(seed)
    bits = np.tile(sdp.prbs7(1), n_bits // 127 + 1)[:n_bits]
    h_link, _ = impulse(channel() * ctle(peak_db))
    y = through(tx_wave(bits, jitter_ui=rj_ui), h_link)
    y0 = through(tx_wave(bits[:5080]), h_link)            # noise-free copy
    hts, ph, _, _ = eye_scan(y0, bits[:5080])
    a = 2.0 * bits[:5080] - 1
    s = y0[ph::SPS]
    lag = np.argmax(sp.signal.correlate(s, a, method="fft")) - a.size + 1
    return bits, y, ph + lag * SPS, hts[ph]


def sample(y, t):
    """Linear interpolation of the waveform at fractional sample times t."""
    i = np.floor(t).astype(int)
    f = t - i
    return y[i] * (1 - f) + y[i + 1] * f


def simulate(n_bits=60000, ppm=200.0, phi0=0.37, kp=1 / 8, ki=1 / 8 / 128, d_lat=1,
             sigma=5e-3, sj_pp=0.0, sj_f=1e6, cdr=True, wave=None, seed=11):
    """Run the CDR. Returns a dict of per-update traces and error counts."""
    bits, y, t0, eh = wave if wave is not None else link_wave(n_bits)
    rng = np.random.default_rng(seed)
    n_upd = n_bits // UPD - 40                            # stay inside the waveform
    acc = freg = 0.0
    pipe = [0.0] * (d_lat + 1)
    d_prev = None
    out = {k: np.zeros(n_upd) for k in ("code", "ideal", "err", "freg", "nerr")}
    nerr = 0
    for k in range(n_upd):
        n = k * UPD + np.arange(UPD)                      # RX bit indices of this update
        phi_d = phi0 + ppm * 1e-6 * n + 0.5 * sj_pp * np.sin(2 * np.pi * sj_f * n * UI)
        phi_c = np.round(acc) * LSB                       # PI phase (UI)
        t_d = t0 + SPS * (n - phi_d + phi_c)              # data-sampler instants
        d = sample(y, t_d) + sigma * rng.standard_normal(UPD) > 0
        e = sample(y, t_d - SPS / 2) + sigma * rng.standard_normal(UPD) > 0
        prev = np.concatenate(([d[0] if d_prev is None else d_prev], d[:-1]))
        trans = prev != d                                 # a transition before each bit
        votes = np.where(e == prev, 1, -1) * trans        # +1: clock early -> later
        d_prev = d[-1]
        m = np.round((t_d - t0) / SPS).astype(int)       # TX bit actually sampled
        nerr += np.sum(d != bits[m].astype(bool))
        pipe.append(np.sign(votes.sum()))                 # majority vote of the block
        v = pipe.pop(0)                                   # ... seen d_lat updates later
        if cdr:
            freg += ki * v                                # integral path (frequency)
            acc += kp * v + freg                          # proportional path + phase
        out["code"][k] = np.round(acc) % N_PI
        out["ideal"][k] = (phi_d.mean() / LSB) % N_PI
        out["err"][k] = (phi_c - phi_d.mean()) * UI * 1e12   # clock - data phase (ps)
        out["freg"][k] = freg * LSB / UPD * 1e6           # integral register (ppm)
        out["nerr"][k] = nerr
    out["t_us"] = np.arange(n_upd) * UPD * UI * 1e6
    out["eye_mV"] = 1e3 * eh
    return out


def lock_index(err_ps, tol_ps=10.0, hold=50):
    """First update after which the phase error stays within tol of its final
    mean (the static lock offset) for `hold` updates."""
    dev = np.abs(err_ps - err_ps[-2000:].mean())
    ok = np.convolve(dev < tol_ps, np.ones(hold), "valid") >= hold
    return int(np.argmax(ok)) if ok.any() else None


if __name__ == "__main__":
    wave = link_wave(60000)
    print(f"Link: REF + 14 dB CTLE, 5 ps RJ; noise-free eye {wave[3]*1e3:.1f} mV")
    r = simulate(wave=wave, **BASE)
    k = lock_index(r["err"])
    trk = r["err"][k + 500:]
    print(f"CDR on : lock after {r['t_us'][k]:.2f} us; tracking error {trk.std():.2f} ps rms, "
          f"{np.ptp(trk):.1f} ps pp, mean {trk.mean():+.1f} ps vs eye center")
    print(f"         integral register {r['freg'][-500:].mean():.0f} ppm (true +200); "
          f"bit errors {int(r['nerr'][k])} before lock, "
          f"{int(r['nerr'][-1] - r['nerr'][k])} after, in {len(r['t_us'])*UPD} bits")
    f = simulate(wave=wave, cdr=False, **BASE)
    print(f"CDR off: {int(f['nerr'][-1])} bit errors (BER {f['nerr'][-1]/(len(f['t_us'])*UPD):.1e})")
    for kp, d in ((1 / 8, 0), (1 / 8, 3), (1 / 2, 1), (1.0, 1)):
        q = simulate(wave=wave, kp=kp, ki=kp / 128, d_lat=d)
        e = q["err"][3000:]
        print(f"  KP = {kp:5.3f} LSB, D = {d}: wander {e.std():.2f} ps rms, {np.ptp(e):.1f} ps pp")

    fig, ax = plt.subplots(3, 1, figsize=(6, 6.4), sharex=True)
    ax[0].plot(r["t_us"], r["ideal"], color=COLORS[1], lw=2, alpha=0.5, label="ideal code")
    ax[0].plot(r["t_us"], r["code"], color=COLORS[0], lw=0.7, label="PI code")
    ax[0].set(ylabel="PI code", title="Bang-bang PI-CDR, +200 ppm")
    ax[0].legend(loc="upper right")
    ax[1].plot(r["t_us"], r["err"], color=COLORS[2], lw=0.6)
    ax[1].set(ylabel="Phase error [ps]", ylim=(-90, 90))
    ax[2].plot(f["t_us"], f["nerr"], color=COLORS[1], lw=1.5, label="fixed clock")
    ax[2].plot(r["t_us"], r["nerr"], color=COLORS[0], lw=1.5, label="with CDR")
    ax[2].set(xlabel="Time [us]", ylabel="Cumulative errors")
    ax[2].legend(loc="upper left")
    fig.tight_layout(); fig.savefig("lab7_cdr.png"); plt.close(fig)
