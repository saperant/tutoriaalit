"""Siirtolinjan heijastukset: heijastuskertoimista askel kerrallaan."""

import numpy as np

from spice import lopeta, simuloi, vertaa

# @alku heijastus
Z0, U, TD, t0 = 50.0, 2.0, 5e-9, 1e-9


def gamma(Z: float) -> float:
    """Heijastuskerroin: (Z - Z0) / (Z + Z0). Auki 1, oikosulku -1."""
    return (Z - Z0) / (Z + Z0)


def kuorman_jannite(R_s: float, R_L: float, k: int) -> float:
    """Kuorman jännite k:nnen aallon saavuttua (k = 1, 3, 5, ...).
    Linjaan lähtee aalto U Z0 / (R_s + Z0); se heijastuu kuormasta
    kertoimella G_L ja lähteestä kertoimella G_s."""
    aalto = U * Z0 / (R_s + Z0)
    G_L, G_s = gamma(R_L), gamma(R_s)
    u = 0.0
    for _ in range(0, k, 2):           # saapuva aalto ja sen heijastus
        u += aalto * (1 + G_L)
        aalto *= G_L * G_s
    return u
# @loppu heijastus


data = simuloi("07-heijastus.cir").data["heijastus"]
t = data[:, 0]
# wrdata kirjoittaa jokaiselle suureelle oman aika-arvosarakkeen:
# sarakkeet 1, 3 ja 5 ovat v(b1), v(b2) ja v(b3).
tapaukset = [("50/auki", 50.0, 1e9, 1), ("10/auki", 10.0, 1e9, 3),
             ("10/50", 10.0, 50.0, 5)]
for nimi, R_s, R_L, sarake in tapaukset:
    # Näyte kunkin aallon keskeltä: kuorma muuttuu hetkinä t0 + k TD.
    for aalto in (1, 3, 5):
        hetki = t0 + (aalto + 1) * TD
        u_sim = float(np.interp(hetki, t, data[:, sarake]))
        vertaa(f"{nimi} k={aalto}", u_sim,
               kuorman_jannite(R_s, R_L, aalto), "V", 0.01)
lopeta()
