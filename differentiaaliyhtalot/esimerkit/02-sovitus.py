"""Mallin parametrin sovitus mittauksiin: jäähtymisvakio k."""

import numpy as np
from scipy.optimize import curve_fit

# @alku mittaukset
# Kahvin lämpötila mitataan viiden minuutin välein. Mittauksissa on
# kohinaa (keskihajonta 0,5 C); kohina tuotetaan kiinteällä siemenellä.
T_YMP, T_ALKU, K_TOSI = 21.0, 90.0, 0.045
aika = np.arange(0.0, 35.0, 5.0)
rng = np.random.default_rng(2026)
mitattu = (
    T_YMP
    + (T_ALKU - T_YMP) * np.exp(-K_TOSI * aika)
    + rng.normal(0.0, 0.5, aika.size)
)
print("mitattu:", " ".join(f"{m:.1f}" for m in mitattu))
# @loppu mittaukset


# @alku sovitus
# 1) Epälineaarinen pienimmän neliösumman sovitus suoraan malliin.
def malli(t: np.ndarray, k: float, alku: float) -> np.ndarray:
    tulos: np.ndarray = T_YMP + (alku - T_YMP) * np.exp(-k * t)
    return tulos


(k, alku), kov = curve_fit(malli, aika, mitattu, p0=(0.1, 80.0))
print(
    f"curve_fit: k = {k:.4f} +- {np.sqrt(kov[0, 0]):.4f} 1/min, "
    f"T0 = {alku:.1f} C"
)

# 2) Linearisointi: ln(T - T_y) = ln(T0 - T_y) - k t on suora.
kulma, _vakio = np.polyfit(aika, np.log(mitattu - T_YMP), 1)
print(f"suora logaritmeista: k = {-kulma:.4f} 1/min")
# @loppu sovitus
