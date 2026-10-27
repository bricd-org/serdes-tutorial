"""ch16_lab1.py -- Lab 1 figure (Chapter 16): REF channel |S21| and pulse response with cursors.
Same computations as tutorial/code/lab1_channel.py."""
from bricdstyle import *
from link import *

H = channel()
H_db = 20 * np.log10(np.abs(H))
i_nyq = np.argmin(np.abs(F - F_NYQ))
h, t = impulse(H)
p = pulse(h)
k0 = np.argmax(p)
n_pre, n_post = 2, 10
cur = sdp.channel_coefficients(p, t, SPS, n_pre, n_post, res=50)   # same call as the lab
plt.close("all")
isi = np.sum(np.abs(cur)) - cur[n_pre]
print(f"|H| at Nyquist {H_db[i_nyq]:.2f} dB; p0 = {cur[n_pre]:.4f}; PDA = {cur[n_pre]-isi:+.4f} V")

fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.2), gridspec_kw=dict(width_ratios=[1, 1.25]))
a.plot(F / 1e9, H_db, color=C1)
a.axvline(F_NYQ / 1e9, color=MUTED, ls="--", lw=0.8)
a.plot(F_NYQ / 1e9, H_db[i_nyq], "o", color=GOLD, ms=5, zorder=5)
note(a, (F_NYQ / 1e9, H_db[i_nyq]), f"{H_db[i_nyq]:.2f} dB at\nNyquist (2.5 GHz)", (4.3, -9))
a.set_xlim(0, 10); a.set_ylim(-45, 2)
finish(a, "Frequency (GHz)", "$|S_{21}|$ (dB)")
panel(a, "a")

k = np.arange(-n_pre, n_post + 1)
tu = (t - t[k0]) / UI
m = (tu > -2.6) & (tu < 10.6)
b.plot(tu[m], p[m], color=PALE, lw=1.6, zorder=1)
stem_cursors(b, k, cur, fmt="{:.3f}")
for txt in b.texts:            # keep only the first four labels readable
    if txt.get_position()[0] > 2.5 or txt.get_position()[0] < -1.5:
        txt.set_visible(False)
b.set_xlim(-2.6, 10.6); b.set_ylim(-0.03, 0.40)
b.text(10.4, 0.37, f"$\\Sigma|p_k|_{{k\\neq0}}$ = {isi:.3f} V\nPDA eye = {cur[n_pre]-isi:+.3f} V (closed)",
       ha="right", va="top", fontsize=7.5, color=C4)
finish(b, "Time from pulse peak (UI)", "Pulse response (V)")
panel(b, "b")
savefig(fig, "ch16_lab1")
