"""Monte Carlo -toleranssianalyysi: monta jakajaa yhdessä netlistissä."""

import numpy as np

from spice import simuloi

# @alku netlist
N, TOL = 500, 0.05
rng = np.random.default_rng(2026)          # kiinteä siemen: toistettava
# Valmistajan 5 %:n vastukset: oletetaan tasajakauma toleranssin sisällä.
r1 = 10e3 * (1 + rng.uniform(-TOL, TOL, N))
r2 = 4.7e3 * (1 + rng.uniform(-TOL, TOL, N))
rivit = ["Monte Carlo: 500 jakajaa", "V1 syotto 0 DC 12"]
for k in range(N):
    rivit += [f"R1_{k} syotto u{k} {r1[k]:.3f}", f"R2_{k} u{k} 0 {r2[k]:.3f}"]
rivit += [".control", "op", "print " + " ".join(f"v(u{k})" for k in range(N)),
          ".endc", ".end"]
tulos = simuloi("\n".join(rivit))
u = np.array([tulos.arvot[f"v(u{k})"] for k in range(N)])
# @loppu netlist

# @alku tilasto
print(f"keskiarvo {u.mean():.3f} V, keskihajonta {1e3 * u.std():.1f} mV")
print(f"pienin {u.min():.3f} V, suurin {u.max():.3f} V")
print("huonoin tapaus (02-esarja.py): 3.580...4.103 V")
osuus = np.mean(np.abs(u - 3.837) < 0.1)
print(f"jakajista {100 * osuus:.0f} % on välillä 3.837 +- 0.1 V")
# @loppu tilasto
