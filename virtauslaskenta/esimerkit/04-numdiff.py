"""Vastavirtakaavion numeerinen diffuusio mitattuna.

Kapea kumpu kulkee jaksollisella alueella. Tarkassa ratkaisussa sen
leveys ei muutu; vastavirtakaaviossa varianssi kasvaa kuin
diffuusioyhtälössä, jonka kerroin on u h (1 - C) / 2."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]

# @alku mittaus
N = 200
H = 1.0 / N
NOPEUS = 1.0
LEVEYS = 0.04         # kummun keskihajonta alussa


def varianssi(c: Taulukko) -> float:
    """Jakauman varianssi huipun ympärillä jaksollisella alueella."""
    x: Taulukko = (np.arange(N, dtype=np.float64) + 0.5) * H
    huippu = float(x[int(np.argmax(c))])
    etaisyys = (x - huippu + 0.5) % 1.0 - 0.5
    return float(np.sum(c * etaisyys**2) / np.sum(c))


def mitattu_diffuusio(courant: float, matka: float = 0.5) -> float:
    """Varianssin kasvu on 2 D t: D saadaan alun ja lopun erotuksesta."""
    x: Taulukko = (np.arange(N, dtype=np.float64) + 0.5) * H
    c: Taulukko = np.exp(-0.5 * ((x - 0.25) / LEVEYS) ** 2)
    alku = varianssi(c)
    askelia = round(matka / (courant * H))
    for _ in range(askelia):
        c = c - courant * (c - np.roll(c, 1))
    aika = askelia * courant * H / NOPEUS
    return (varianssi(c) - alku) / (2.0 * aika)
# @loppu mittaus


# @alku taulukko
print("Courant  mitattu D   u h (1 - C) / 2   leveys lopussa / alussa")
for courant in (0.25, 0.5, 0.75, 1.0):
    d = mitattu_diffuusio(courant)
    ennuste = NOPEUS * H * (1.0 - courant) / 2.0
    lopussa = (LEVEYS**2 + 2.0 * d * 0.5) ** 0.5 / LEVEYS
    d = d if abs(d) > 1e-12 else 0.0       # pyöristysvirheen taso nollaksi
    print(f"{courant:7.2f} {d:10.2e} {ennuste:17.2e} {lopussa:14.2f}")
# @loppu taulukko
