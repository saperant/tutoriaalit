"""Pyöristystapojen harha ja virheen hajonta mitattuna."""

from collections.abc import Callable

import numpy as np
import numpy.typing as npt

Kokonaiset = npt.NDArray[np.int64]
Tapa = Callable[["Kokonaiset"], "Kokonaiset"]
K = 4                                    # pudotettavat bitit
YKSI = 2**K                              # yksi tulos-LSB alkuperäisinä


def kok(a: object) -> Kokonaiset:
    return np.asarray(a, dtype=np.int64)


# @alku tavat
def lattia(x: Kokonaiset) -> Kokonaiset:
    return kok(x >> K)                   # NumPy: aritmeettinen siirto


def kohti_nollaa(x: Kokonaiset) -> Kokonaiset:
    return kok(np.sign(x) * (np.abs(x) >> K))


def ylos(x: Kokonaiset) -> Kokonaiset:
    return kok((x + YKSI // 2) >> K)


def parilliseen(x: Kokonaiset) -> Kokonaiset:
    q = x >> K
    jaannos = x & (YKSI - 1)
    pyorista = (jaannos > YKSI // 2) | ((jaannos == YKSI // 2) & (q & 1 == 1))
    return kok(q + pyorista)
# @loppu tavat


# @alku mittaus
# Kaikki 13-bittiset arvot kerran: pudotetut bitit tasajakautuneita.
x = np.arange(-(2**12), 2**12, dtype=np.int64)
print(f"{'tapa':12} {'harha (LSB)':>12} {'RMS (LSB)':>10}")
for nimi, tapa in [("lattia", lattia), ("kohti nollaa", kohti_nollaa),
                   ("ylös", ylos), ("parilliseen", parilliseen)]:
    virhe = tapa(x) - x / YKSI           # tuloksen LSB-yksiköissä
    print(f"{nimi:12} {virhe.mean():>+12.4f} "
          f"{np.sqrt(np.mean(virhe**2)):>10.4f}")
# @loppu mittaus

# @alku kertyminen
# Liukuva keskiarvo y += (x - y) / 16 kohti arvoa 1000 alhaalta ja
# ylhäältä: pieni ero pyöristyy nollaksi, ja y jää kuolleelle alueelle.
def keskiarvo(tapa: Tapa, alku: int, murtobitit: int,
              askelia: int = 500) -> list[int]:
    """Tila y on murtobitit (0 tai K) bittiä tarkempi kuin syöte."""
    tavoite = kok([1000 << murtobitit])
    y, sarja = kok([alku << murtobitit]), []
    for _ in range(askelia):
        y = y + tapa(tavoite - y)
        # Tulos pyöristetään takaisin syötteen tarkkuuteen.
        sarja.append(int(ylos(y)[0]) if murtobitit == K else int(y[0]))
    return sarja


for nimi, tapa, murtobitit in [("lattia", lattia, 0),
                               ("parilliseen", parilliseen, 0),
                               ("lattia, tila +4 b.", lattia, 4)]:
    loput = [keskiarvo(tapa, alku, murtobitit)[-1] for alku in (0, 2000)]
    print(f"{nimi:18} alhaalta {loput[0]}, ylhäältä {loput[1]}"
          " (tavoite 1000)")
# @loppu kertyminen
