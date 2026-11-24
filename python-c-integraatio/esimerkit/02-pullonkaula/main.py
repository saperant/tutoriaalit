"""Mittaa ensin: missä aika kuluu, ja riittääkö NumPy?

Anturidatasta lasketaan liukuva keskiarvo ja eksponentiaalinen
suodatin. Profiloija kertoo, kumpi on pullonkaula, ja vektorointi
ratkaisee vain toisen niistä.
"""

import cProfile
import pstats
import time
from collections.abc import Callable

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]


# @alku silmukat
def liukuva_keskiarvo(x: list[float], n: int) -> list[float]:
    """Keskiarvo n viimeisestä näytteestä (ikkuna liukuu)."""
    tulos = []
    summa = 0.0
    for i, arvo in enumerate(x):
        summa += arvo
        if i >= n:
            summa -= x[i - n]
        if i >= n - 1:
            tulos.append(summa / n)
    return tulos


def eksponentiaalinen(x: list[float], a: float) -> list[float]:
    """y[i] = a * y[i-1] + (1 - a) * x[i]: jokainen tulos riippuu
    edellisestä, joten laskua ei voi jakaa alkioittain."""
    tulos = []
    y = x[0]
    for arvo in x:
        y = a * y + (1.0 - a) * arvo
        tulos.append(y)
    return tulos
# @loppu silmukat


# @alku vektoroitu
def liukuva_keskiarvo_np(x: Taulukko, n: int) -> Taulukko:
    kertyma: Taulukko = np.cumsum(np.concatenate(([0.0], x)))
    return (kertyma[n:] - kertyma[:-n]) / n
# @loppu vektoroitu


def kasittele(data: Taulukko) -> float:
    """Tyypillinen putki: muunnos, suodatus ja yhteenveto."""
    lista: list[float] = data.tolist()
    suodatettu = eksponentiaalinen(lista, 0.9)
    return max(suodatettu)


def nopein(f: Callable[[], object], kerrat: int = 5) -> float:
    paras = float("inf")
    for _ in range(kerrat):
        alku = time.perf_counter()
        f()
        paras = min(paras, time.perf_counter() - alku)
    return paras


def main() -> None:
    rng = np.random.default_rng(1)
    data = rng.normal(20.0, 0.5, 200_000)
    lista: list[float] = data.tolist()

    # @alku profilointi
    profiili = cProfile.Profile()
    profiili.enable()
    kasittele(data)
    profiili.disable()
    tilasto = pstats.Stats(profiili)
    # stats: (tiedosto, rivi, funktio) -> (kutsut, ..., oma aika, ...)
    rivit = tilasto.stats.items()  # type: ignore[attr-defined]
    ajat: dict[str, float] = {avain[2]: arvot[2] for avain, arvot in rivit}
    print("eniten omaa aikaa:", max(ajat, key=lambda nimi: ajat[nimi]))
    # @loppu profilointi

    # @alku vertailu
    silmukka = liukuva_keskiarvo(lista, 50)
    vektori = liukuva_keskiarvo_np(data, 50)
    print("samat tulokset:", np.allclose(silmukka, vektori))
    t_silmukka = nopein(lambda: liukuva_keskiarvo(lista, 50))
    t_vektori = nopein(lambda: liukuva_keskiarvo_np(data, 50))
    print("NumPy yli 5 kertaa nopeampi:", t_silmukka > 5 * t_vektori)
    # @loppu vertailu
    y = eksponentiaalinen(lista, 0.9)
    print(f"suodatettu loppuarvo: {y[-1]:.2f}")


if __name__ == "__main__":
    main()
