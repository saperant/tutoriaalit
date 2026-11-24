"""Lineaarivaiheisten FIR-suodinten tyypit I-IV ja pakotetut nollat."""

import numpy as np
from scipy import signal

# @alku tyypit
rng = np.random.default_rng(3)
print("tyyppi  N   symmetria   |H(0)|  |H(fs/2)|  ryhmaviive")
for tyyppi, lkm, merkki in (("I", 9, 1), ("II", 8, 1),
                            ("III", 9, -1), ("IV", 8, -1)):
    puoli = rng.standard_normal(lkm // 2)
    keski = [] if lkm % 2 == 0 else [0.0 if merkki < 0 else 1.0]
    h = np.concatenate([puoli, keski, merkki * puoli[::-1]])
    H0, Hn = np.abs(np.polyval(h, [1.0, -1.0]))
    _, gd = signal.group_delay((h, [1.0]), w=[0.3, 1.1, 2.0])
    nimi = "parillinen" if merkki > 0 else "pariton"
    print(f"{tyyppi:5s} {lkm:3d}   {nimi:10s} {H0:7.3f} {Hn:9.3f}"
          f"   {np.round(gd, 3).tolist()}")
# @loppu tyypit

# @alku ylipaasto
try:
    signal.firwin(64, 1_000.0, pass_zero=False, fs=8_000.0)
except ValueError as virhe:
    # Viesti: "...must have zero response at the Nyquist frequency."
    print("firwin hylkaa:", type(virhe).__name__,
          "nolla Nyquistilla" if "Nyquist" in str(virhe) else "")
# @loppu ylipaasto
