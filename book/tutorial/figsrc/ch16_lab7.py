"""ch16_lab7.py -- Lab 7 figure: bang-bang PI-CDR locking to +200 ppm on the REF + CTLE waveform.
Imports the model from tutorial/code/lab7_bbcdr.py (same seeds and settings as the lab)."""
from bricdstyle import *
from link import *
from lab7_bbcdr import link_wave, simulate, lock_index, BASE

wave = link_wave(60000)
r = simulate(wave=wave, **BASE)
f = simulate(wave=wave, cdr=False, **BASE)
k = lock_index(r["err"])
trk = r["err"][k + 500:]
print(f"lock {r['t_us'][k]:.2f} us, rms {trk.std():.2f} ps, mean {trk.mean():+.1f} ps, "
      f"errors CDR {int(r['nerr'][-1])}, fixed {int(f['nerr'][-1])}")

fig = plt.figure(figsize=(6.3, 2.65))
gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1], width_ratios=[1, 1.1])
a = fig.add_subplot(gs[0, :]); b = fig.add_subplot(gs[1, 0]); c = fig.add_subplot(gs[1, 1])
a.plot(r["t_us"], r["ideal"], color=GOLD, lw=2.4, alpha=0.5, label="ideal code (data phase)")
a.plot(r["t_us"], r["code"], color=NAVY, lw=0.7, label="PI code")
a.set_xlim(0, r["t_us"][-1]); a.set_ylim(-2, 82); a.set_yticks([0, 16, 32, 48, 64])
a.legend(loc="upper left", ncol=2, fontsize=6.8)
a.text(r["t_us"][-1] * 0.99, 73, "+200 ppm: one PI rotation (2 UI) every 2.0 $\\mu$s",
       ha="right", fontsize=6.8, color=MUTED)
finish(a, "Time ($\\mu$s)", "PI code")
panel(a, "a")
b.plot(r["t_us"], r["err"], color=C3, lw=0.6)
b.axhline(trk.mean(), color=GOLDDK, lw=0.7, ls="--")
b.set_xlim(0, 1.5); b.set_ylim(-90, 30)
note(b, (r["t_us"][k], r["err"][k]), f"locked after\n{r['t_us'][k]:.2f} $\\mu$s", (0.45, -60))
b.text(1.45, 12, f"{trk.std():.1f} ps rms, offset {trk.mean():+.1f} ps", ha="right", fontsize=6.8, color=C3)
finish(b, "Time ($\\mu$s), first 1.5 $\\mu$s", "Clock $-$ data phase (ps)")
panel(b, "b")
c.plot(f["t_us"], f["nerr"], color=C4, label="fixed clock")
c.plot(r["t_us"], r["nerr"], color=C1, lw=1.8, label="with CDR")
c.set_xlim(0, r["t_us"][-1]); c.set_ylim(-60, 1750)
c.text(r["t_us"][-1] * 0.98, f["nerr"][-1] + 60, f"{int(f['nerr'][-1])} errors", ha="right", va="bottom", fontsize=6.8, color=C4)
c.text(r["t_us"][-1] * 0.98, 90, f"{int(r['nerr'][-1])} errors", ha="right", fontsize=6.8, color=C1)
c.legend(loc="upper left", fontsize=6.8)
finish(c, "Time ($\\mu$s)", "Cumulative bit errors")
panel(c, "c")
savefig(fig, "ch16_lab7")
