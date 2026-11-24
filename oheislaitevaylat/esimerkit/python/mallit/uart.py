"""UART: asynkroninen sarjalinja bittitasolla.

Lähetin ja vastaanotin eivät jaa kelloa. Vastaanotin tahdistuu
jokaisen kehyksen START-bitin laskevaan reunaan ja näytteistää bitit
omalla kellollaan, tavallisesti 16-kertaisella ylinäytteistyksellä.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

Pariteetti = Literal["N", "E", "O"]  # ei, parillinen, pariton


# @alku kehys
@dataclass(frozen=True)
class Kehysmuoto:
    databitit: int = 8
    pariteetti: Pariteetti = "N"
    stopbitit: int = 1

    def __str__(self) -> str:
        return f"{self.databitit}{self.pariteetti}{self.stopbitit}"

    @property
    def pituus(self) -> int:
        """Kehyksen bittimäärä START-bitistä viimeiseen STOP-bittiin."""
        return (1 + self.databitit + (self.pariteetti != "N")
                + self.stopbitit)


def kehyksen_bitit(tavu: int, muoto: Kehysmuoto) -> list[int]:
    """START (0), databitit vähiten merkitsevä ensin, pariteetti ja
    STOP (1)."""
    data = [(tavu >> i) & 1 for i in range(muoto.databitit)]
    bitit = [0, *data]
    if muoto.pariteetti != "N":
        ykkosia = sum(data) % 2
        bitit.append(ykkosia if muoto.pariteetti == "E" else 1 - ykkosia)
    return bitit + [1] * muoto.stopbitit
# @loppu kehys


# @alku linja
def linja(tavut: Iterable[int], muoto: Kehysmuoto,
          bitin_pituus: float = 16.0, lepo: int = 2) -> list[int]:
    """Lähettimen linja vastaanottimen näytteinä. bitin_pituus on
    lähettimen bitin kesto vastaanottimen näytejaksoina: 16 tarkoittaa
    samaa nopeutta, 16 * 1.03 lähetintä, joka on 3 % hitaampi."""
    bitit = [1] * lepo
    for tavu in tavut:
        bitit += kehyksen_bitit(tavu, muoto)
    bitit += [1] * lepo
    naytteita = int(len(bitit) * bitin_pituus)
    return [bitit[min(int(t / bitin_pituus), len(bitit) - 1)]
            for t in range(naytteita)]
# @loppu linja


# @alku vastaanotto
@dataclass(frozen=True)
class Vastaanotettu:
    tavu: int
    virhe: str | None = None  # "pariteetti" tai "kehys"


def vastaanota(naytteet: list[int], muoto: Kehysmuoto,
               ylinaytteistys: int = 16) -> list[Vastaanotettu]:
    """Etsii START-bitin laskevan reunan, tarkistaa sen keskeltä ja
    näytteistää loput bitit niiden oletetusta keskikohdasta."""
    tulos = []
    t = 1
    while t < len(naytteet):
        if not (naytteet[t - 1] == 1 and naytteet[t] == 0):
            t += 1
            continue
        keskella = t + ylinaytteistys // 2
        if keskella >= len(naytteet) or naytteet[keskella] != 0:
            t += 1  # häiriöpiikki, ei START-bittiä
            continue
        hetket = [keskella + k * ylinaytteistys
                  for k in range(1, muoto.pituus)]
        if hetket[-1] >= len(naytteet):
            break
        bitit = [naytteet[h] for h in hetket]
        data = bitit[:muoto.databitit]
        tavu = sum(b << i for i, b in enumerate(data))
        virhe = None
        if muoto.pariteetti != "N":
            odotettu = kehyksen_bitit(tavu, muoto)[1 + muoto.databitit]
            if bitit[muoto.databitit] != odotettu:
                virhe = "pariteetti"
        if 0 in bitit[len(bitit) - muoto.stopbitit:]:
            virhe = "kehys"  # STOP-bitin paikalla oli 0
        tulos.append(Vastaanotettu(tavu, virhe))
        t = hetket[-1]  # uusi START voi alkaa STOP-bitin jälkeen
    return tulos
# @loppu vastaanotto
