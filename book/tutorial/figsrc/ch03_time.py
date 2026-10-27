"""ch03_time.py -- Chapter 3 figures from frequency to time and the REF channel:
causality, impulse vs pulse response, LOSS_FAMILY pulses, REF |S21| and REF pulse/cursors.
Prints the numbers used in Sections 3.6-3.7 (and tab:ref-cursors).

Run:  cd tutorial/figsrc && /home/claude/research/venv/bin/python ch03_time.py
"""
from bricdstyle import *
from link import *

H = channel(REF_LEN)
h, t = impulse(H)
p = pulse(h)
i0 = int(np.argmax(p))
td = REF_LEN * np.sqrt(4.0) / 2.998e8
k, pk, _ = cursors(p)
print(f"REF: loss {loss_db(H):.2f} dB @2.5G, {loss_db(H,1.25e9):.2f} @1.25G, {loss_db(H,5e9):.2f} @5G,"
      f" DC {loss_db(H,0):.2f} dB; line only {loss_db(channel(REF_LEN, c_pad=0)):.2f} dB")
print(f"t_d = {td*1e9:.3f} ns; impulse peak {t[np.argmax(h)]*1e9:.3f} ns; pulse peak {t[i0]*1e9:.3f} ns")
print("cursors k=-2..10:", " ".join(f"{v:.4f}" for v in pk))
print(f"p1/p0 = {pk[3]/pk[2]:.3f}; sum|ISI| = {np.sum(np.abs(pk))-pk[2]:.4f}; PDA = {pda_eye(pk,k):+.4f} V")
kk, pkk, _ = cursors(p, n_pre=2, n_post=300)
print(f"tail sum k>10: {np.sum(pkk[kk>10]):.4f}; energy fraction of p in main UI: n/a")
print(f"sum(h) = {h.sum():.4f} (= H(0)); impulse peak x Tb = {h.max()*SPS:.3f} V")
# fraction of pulse 'area' in main cursor UI
area = p.sum() / SPS
print(f"pulse area / Tb = {area:.4f} (= H(0))")

# ---------------------------------------------------------------- Fig: causality (HALF)
Hm = np.abs(H) * np.exp(-2j * np.pi * F * t[np.argmax(h)])   # same |H|, linear phase only
hm, _ = impulse(Hm)
t_on = t[np.argmax(h > 0.01 * h.max())]                       # first arrival of the causal model
print(f"causal onset (1% of peak) = {t_on*1e9:.3f} ns; l/v = {td*1e9:.3f} ns")
fig, ax = plt.subplots(figsize=HALF)
ax.axvspan(5.9, t_on * 1e9, color=BGPALE, zorder=0)
ax.plot(t * 1e9, hm * SPS, color=C4, lw=1.1, label="|H| only + pure delay")
ax.plot(t * 1e9, h * SPS, color=NAVY, lw=1.5, label="REF (causal model)")
ax.axvline(t_on * 1e9, color=GOLDDK, lw=0.8, ls="--")
ax.text(t_on * 1e9 - 0.03, 0.47, "first\narrival", color=GOLDDK, fontsize=6.8, ha="right", va="top")
ax.text(5.95, 0.22, "causal model\nis exactly\nzero here", fontsize=6.6, color=MUTED, va="center")
note(ax, (6.25, 0.035), "non-causal\nprecursor", (6.05, 0.12), color=C4)
ax.set_xlim(5.9, 7.6); ax.set_ylim(-0.06, 0.5)
finish(ax, "Time (ns)", "$h(t)\\cdot T_b$ (V)")
ax.legend(loc="upper right", fontsize=6.2, bbox_to_anchor=(1.02, 0.9))
savefig(fig, "ch03_causal")
pre = np.sum(np.abs(hm[t < t_on])) / np.sum(np.abs(hm))
print(f"non-causal model: fraction of |h| before first arrival = {pre:.3f}")

# ---------------------------------------------------------------- Fig: impulse vs pulse (HALF)
fig, ax = plt.subplots(figsize=HALF)
ax.plot(t * 1e9, h * SPS, color=C2, lw=1.1, label="impulse $h(t)\\cdot T_b$")
ax.plot(t * 1e9, p, color=NAVY, lw=1.6, label="1-UI pulse $p(t)$")
ax.plot(t[i0] * 1e9, p[i0], "o", color=GOLD, ms=4.5, zorder=5)
note(ax, (t[i0] * 1e9, p[i0]), f"$p_0$ = {p[i0]:.3f} V", (7.4, 0.42), color=GOLDDK)
ax.annotate("", xy=(t[i0] * 1e9 + 0.2, 0.02), xytext=(t[i0] * 1e9, 0.02),
            arrowprops=dict(arrowstyle="|-|", lw=0.7, color=MUTED, mutation_scale=2))
ax.text(t[i0] * 1e9 + 0.1, -0.06, "1 UI", fontsize=6.6, color=MUTED, ha="center")
ax.set_xlim(6.2, 9.0); ax.set_ylim(-0.08, 0.5)
finish(ax, "Time (ns)", "Amplitude (V)")
ax.legend(loc="upper right", fontsize=6.2, bbox_to_anchor=(1.02, 1.0))
savefig(fig, "ch03_imp_pulse")

# ---------------------------------------------------------------- Fig: loss family pulses
fig, ax = plt.subplots(figsize=(6.3, 2.45))
fam = [5, 10, 15, 20, 25]
for d, col in zip(fam, (C3, C1, C5, C2, C4)):
    L = LOSS_FAMILY[d]
    tt, pp = pulse_of(channel(L))
    j0 = int(np.argmax(pp))
    tu = (np.arange(pp.size) - j0) / SPS
    _, ck, _ = cursors(pp, n_pre=1, n_post=10)
    lab = f"{d} dB ({L*100:.0f} cm)" + (", ≈ REF" if d == 15 else "")
    ax.plot(tu, pp, color=col, lw=1.4, label=f"{d} dB, {L*100:.0f} cm")
    ax.plot(0, pp[j0], "o", color=col, ms=4)
    ax.plot(np.arange(1, 11), ck[2:], "o", color=col, ms=2.5, mfc="white", mew=0.8)
    print(f"family {d} dB L={L} m: p0={ck[1]:.4f}, p1={ck[2]:.4f}, p1/p0={ck[2]/ck[1]:.3f}, p5={ck[6]:.4f}, delay={tt[j0]*1e9:.2f} ns")
ax.set_xlim(-3, 12); ax.set_ylim(-0.03, 0.82)
ax.set_xticks(range(-3, 13))
note(ax, (0.05, 0.76), "main cursor $p_0$ falls\nfrom 0.77 to 0.22 V", (1.4, 0.70), color=NAVY)
note(ax, (4.0, 0.075), "tail (post-cursors) grows\nrelative to $p_0$", (5.3, 0.30), color=NAVY)
finish(ax, "Time from main cursor (UI)", "Pulse response (V)", legend=True, loc="upper right")
ax.legend(loc="upper right", title="loss at 2.5 GHz, length", title_fontsize=7)
savefig(fig, "ch03_family")

# ---------------------------------------------------------------- Fig: REF |S21| (HALF)
fig, ax = plt.subplots(figsize=HALF)
sel = F <= 10.05e9
ax.plot(F[sel] / 1e9, 20 * np.log10(np.abs(H[sel])), color=NAVY, lw=1.6, label="REF (with 300 fF pads)")
H0 = channel(REF_LEN, c_pad=0)
ax.plot(F[sel] / 1e9, 20 * np.log10(np.abs(H0[sel])), color=C1, lw=0.9, ls="--", label="line only")
for fx, off in ((1.25, (2.2, -4.0)), (2.5, (3.6, -12.0)), (5.0, (6.2, -24.0))):
    y = loss_db(H, fx * 1e9)
    ax.plot(fx, y, "o", color=GOLD if fx == 2.5 else MUTED, ms=4.5 if fx == 2.5 else 3.5, zorder=5)
    note(ax, (fx, y), f"{y:.1f} dB", off, color=GOLDDK if fx == 2.5 else MUTED)
ax.axvline(2.5, color=MUTED, lw=0.7, ls=":")
ax.set_xlim(0, 10); ax.set_ylim(-56, 2)
finish(ax, "Frequency (GHz)", "|S21| (dB)")
ax.legend(loc="lower left", fontsize=6.4)
savefig(fig, "ch03_ref_s21")

# ---------------------------------------------------------------- Fig: REF pulse + cursors (FULL)
fig, ax = plt.subplots(figsize=(6.3, 2.5))
tu = (np.arange(p.size) - i0) / SPS
for kx in range(-3, 12):
    ax.axvline(kx, color=GRID, lw=0.6, zorder=0)
ax.plot(tu, p, color=PALE, lw=2.4, zorder=1, label="pulse response $p(t)$")
stem_cursors(ax, k, pk)
ax.grid(False, axis="x")
ax.set_xlim(-3.3, 11.3); ax.set_ylim(-0.03, 0.40)
ax.set_xticks(range(-3, 12)); ax.set_xticklabels([f"{x:+d}" if x else "0" for x in range(-3, 12)])
ax.text(-3.1, 0.37, "pre-cursor", color=C4, fontsize=7.5)
ax.text(-3.1, 0.345, "main cursor", color=GOLDDK, fontsize=7.5)
ax.text(-3.1, 0.32, "post-cursors", color=C1, fontsize=7.5)
ax.annotate("", xy=(1, pk[3]), xytext=(1, pk[2]),
            arrowprops=dict(arrowstyle="<->", lw=0.7, color=NAVY, mutation_scale=6))
ax.text(1.15, (pk[2] + pk[3]) / 2 + 0.03, f"$p_1/p_0$ = {pk[3]/pk[2]:.3f}", fontsize=7.5, color=NAVY)
ax.text(6.5, 0.17, "sampled every UI at $t_s + k T_b$;\n$t_s$ = pulse peak, "
        f"{t[i0]*1e9:.2f} ns after launch", fontsize=7.5, color=MUTED)
finish(ax, "Cursor index $k$ (UI from main cursor)", "Amplitude (V)")
savefig(fig, "ch03_ref_pulse")
