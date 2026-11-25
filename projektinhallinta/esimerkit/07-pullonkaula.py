"""Pullonkaula: kolmivaiheinen linja kehitys -> katselmointi -> testaus.

Jokaisella vaiheella on päiväkapasiteetti, joka vaihtelee. Koko linjan
läpäisy on hitaimman vaiheen läpäisy, ja sen eteen kertyy jono.
"""

import random
import statistics
from dataclasses import dataclass


# @alku linja
@dataclass(frozen=True)
class Linja:
    kehitys: int = 5              # työtä päivässä keskimäärin
    katselmointi: int = 3
    testaus: int = 4
    jonoraja: int | None = None   # katselmointijonon enimmäispituus
    apu: bool = False             # jouten jäävät kehittäjät katselmoivat


def aja(linja: Linja, paivia: int = 250, siemen: int = 2
        ) -> tuple[float, float, float, float]:
    """Läpäisy/pv, jono keskimäärin, kiertoaika pv, kehityksen käyttöaste."""
    rng = random.Random(siemen)
    def tanaan(kapasiteetti: int) -> int:
        return kapasiteetti + rng.choice((-1, 0, 1))
    katselmoitavat: list[int] = []     # aloituspäivät jonossa
    testattavat: list[int] = []
    kierrot: list[int] = []
    jonot: list[int] = []
    tehty = mahdollinen = 0
    for paiva in range(paivia):
        kyky = tanaan(linja.kehitys)
        tilaa = kyky if linja.jonoraja is None else max(
            0, linja.jonoraja - len(katselmoitavat))
        uusia = min(kyky, tilaa)
        katselmoitavat += [paiva] * uusia
        tehty, mahdollinen = tehty + uusia, mahdollinen + kyky
        katselmoijat = tanaan(linja.katselmointi)
        if linja.apu:                  # kaksi kehittäjää vastaa yhtä
            katselmoijat += (kyky - uusia) // 2
        for _ in range(min(katselmoijat, len(katselmoitavat))):
            testattavat.append(katselmoitavat.pop(0))
        for _ in range(min(tanaan(linja.testaus), len(testattavat))):
            kierrot.append(paiva - testattavat.pop(0) + 1)
        jonot.append(len(katselmoitavat))
    return (len(kierrot) / paivia, statistics.mean(jonot),
            statistics.mean(kierrot), tehty / mahdollinen)
# @loppu linja


VAIHTOEHDOT = [
    ("lähtötilanne", Linja()),
    ("+2 kehittäjää", Linja(kehitys=7)),
    ("+1 katselmoija", Linja(katselmointi=4)),
    ("jonoraja 6", Linja(jonoraja=6)),
    ("jonoraja 6 ja apu", Linja(jonoraja=6, apu=True)),
]
print(f"{'vaihtoehto':<19}läpäisy/pv  jono ka.  kierto pv  kehitys käytössä")
for nimi, linja in VAIHTOEHDOT:
    lapaisy, jono, kierto, kaytto = aja(linja)
    print(f"{nimi:<19}{lapaisy:10.1f}  {jono:8.0f}  {kierto:9.1f}"
          f"  {kaytto:15.0%}")
