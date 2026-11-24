"""Korkea-asteinen IIR: yksi polynomi vai toisen asteen lohkot."""

import numpy as np
from scipy import signal

# @alku navat
# Kapea alipaasto: navat ovat lahella pistetta z = 1.
fs = 48_000.0
sos = signal.butter(8, 150.0, output="sos", fs=fs)
b, a = signal.sos2tf(sos)


def suurin_napa(a: np.ndarray) -> float:
    return float(np.abs(np.roots(a)).max())


a32 = a.astype(np.float32).astype(np.float64)     # kertoimet float32:na
sos32 = sos.astype(np.float32).astype(np.float64)
print("suurin |napa|")
print(f"  lohkoista, float64   {max(suurin_napa(s[3:]) for s in sos):.4f}")
print(f"  lohkoista, float32   {max(suurin_napa(s[3:]) for s in sos32):.4f}")
# Polynomin juuret ovat itsessaan herkkia, joten vain kaksi desimaalia.
print(f"  polynomista, float32 {suurin_napa(a32):.2f}")
# @loppu navat

# @alku vaste
x = np.zeros(48_000)
x[0] = 1.0
viite = signal.sosfilt(sos, x)
ajot = {"polynomi float64": signal.lfilter(b, a, x),
        "polynomi float32": signal.lfilter(b.astype(np.float32), a32, x),
        "lohkot float32": signal.sosfilt(sos32, x)}
with np.errstate(all="ignore"):
    for nimi, y in ajot.items():
        virhe = np.max(np.abs(y - viite)) / np.max(np.abs(viite))
        tulos = f"{virhe:.1e}" if np.isfinite(virhe) else "hajosi (inf)"
        print(f"impulssivaste, {nimi:16s} virhe {tulos}")
# @loppu vaste
