"""Stabiilisuus napojen sijainnista ja kertoimien herkkyys."""

import numpy as np
from scipy import signal

# @alku stabiilius
suotimet = {
    "EMA alfa=0.1": ([0.1], [1.0, -0.9]),
    "resonaattori": ([1.0], [1.0, -1.8, 0.95]),
    "summain": ([1.0], [1.0, -1.0]),
    "epävakaa": ([1.0], [1.0, -2.1, 1.2]),
}
for nimi, (b, a) in suotimet.items():
    navat = np.roots(a)
    r = float(np.max(np.abs(navat)))
    h = signal.lfilter(b, a, np.r_[1.0, np.zeros(499)])
    tila = "stabiili" if r < 1 else ("rajalla" if r == 1 else "epästabiili")
    print(f"{nimi:<13} max|p| {r:6.4f} {tila:<11}"
          f" |h[499]| {abs(h[-1]):9.2e}")
# @loppu stabiilius

# @alku herkkyys
# Kapea 6. asteen alipäästö; kertoimet pyöristetään neljään desimaaliin,
# kuten kiinteän pilkun toteutuksessa.
b6, a6 = signal.butter(6, 0.05)
pyor = np.round(a6, 4)
print(f"suurin kertoimen muutos {np.max(np.abs(pyor - a6)):.1e}")
print(f"suora muoto: max|p| {np.max(np.abs(np.roots(a6))):.4f}"
      f" -> {np.max(np.abs(np.roots(pyor))):.4f}")
sos = signal.butter(6, 0.05, output="sos")      # kolme 2. asteen lohkoa
pahin = max(np.max(np.abs(np.roots(np.round(rivi[3:], 4)))) for rivi in sos)
print(f"{len(sos)} toisen asteen lohkoa: max|p| -> {pahin:.4f}")
# @loppu herkkyys
