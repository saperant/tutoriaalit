"""LMS:n askelkoko: suppenemisnopeus, jaannosvirhe ja stabiilisuus."""

import numpy as np
from scipy import signal

# @alku koe
rng = np.random.default_rng(4)
lkm = 16
tuntematon = signal.firwin(lkm, 0.2)
x = rng.standard_normal(20_000)              # teho 1
kohina = 0.01 * rng.standard_normal(x.size)  # mittauskohina, -40 dB
d = signal.lfilter(tuntematon, [1.0], x) + kohina
raja = 2 / (lkm * 1.0)                       # karkea raja 2 / (N * teho)
print(f"raja 2/(N*teho) = {raja:.3f}")
print("   mu   MSE n=100-199  MSE lopussa  ylimaarainen  malli mu*N/2")
for mu in (0.002, 0.01, 0.04, 0.08, 0.15):
    w, v = np.zeros(lkm), np.zeros(lkm)
    e = np.zeros(x.size)
    with np.errstate(all="ignore"):
        for n in range(x.size):
            v = np.roll(v, 1)
            v[0] = x[n]
            e[n] = d[n] - w @ v
            w += mu * e[n] * v
        alku = np.mean(e[100:200] ** 2)
        loppu = np.mean(e[-5_000:] ** 2)
    if not np.isfinite(loppu) or loppu > 1.0:
        print(f"{mu:6.3f}   hajosi")
        continue
    ylim = loppu / 1e-4 - 1                   # suhteessa kohinan tehoon
    print(f"{mu:6.3f} {alku:13.2e} {loppu:12.2e} {ylim:12.2f}"
          f" {mu * lkm / 2:12.2f}")
# @loppu koe
