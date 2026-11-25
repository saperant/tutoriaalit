"""Pieni virtaussimulaattori: tiimi, työjono ja keskeneräisen työn raja.

Töitä saapuu satunnaisesti. Tiimi aloittaa työn, kun keskeneräisiä on
alle rajan, ja jakaa aikansa tasan keskeneräisten kesken. Jokainen
samanaikainen työ yli yhden henkeä kohden vie osan ajasta vaihtoihin.
Muut esimerkit ja kuvat tuovat tämän moduulin.
"""

import math
import random
from dataclasses import dataclass, field

TEKIJOITA = 4
KESKIKOKO = 4.0        # henkilötyöpäivää työtä kohden
VAIHTOHAVIO = 0.15     # tehon lasku jokaisesta lisätyöstä henkeä kohden
POHJATEHO = 0.75       # vaihtoihin kuluu enintään neljännes ajasta
ASKEL = 0.25           # simulaation aika-askel päivinä


# @alku tietomalli
@dataclass
class Tyo:
    saapui: float
    jaljella: float                    # henkilötyöpäivää
    aloitettu: float = math.nan
    valmis: float = math.nan

    @property
    def lapimenoaika(self) -> float:   # asiakkaan näkemä: tilaus -> valmis
        return self.valmis - self.saapui

    @property
    def kiertoaika(self) -> float:     # tiimin näkemä: aloitus -> valmis
        return self.valmis - self.aloitettu


@dataclass
class Tulos:
    valmiit: list[Tyo] = field(default_factory=list)
    # Päivittäin: (saapuneita, aloitettuja, valmiita) kertyminä.
    kertymat: list[tuple[int, int, int]] = field(default_factory=list)
# @loppu tietomalli


# @alku teho
def kapasiteetti(keskeneraisia: int) -> float:
    """Tiimin teho henkilötyöpäivinä päivässä keskeneräisten määrällä."""
    if keskeneraisia <= TEKIJOITA:
        return float(keskeneraisia)        # loput odottavat töitä
    per_henki = keskeneraisia / TEKIJOITA
    teho = 1 / (1 + VAIHTOHAVIO * (per_henki - 1))
    return TEKIJOITA * max(POHJATEHO, teho)
# @loppu teho


# @alku simulointi
def simuloi(wip_raja: int | None, paivia: int = 1000, siemen: int = 1,
            saapuu_paivassa: float = 0.7) -> Tulos:
    rng = random.Random(siemen)
    tulos = Tulos()
    jono: list[Tyo] = []
    kesken: list[Tyo] = []
    saapuneita = aloitettuja = 0
    seuraava = rng.expovariate(saapuu_paivassa)
    for askel in range(int(paivia / ASKEL)):
        nyt = askel * ASKEL
        while seuraava <= nyt:                       # uudet tilaukset
            koko = KESKIKOKO * rng.lognormvariate(-0.18, 0.6)
            jono.append(Tyo(seuraava, koko))
            saapuneita += 1
            seuraava += rng.expovariate(saapuu_paivassa)
        while jono and (wip_raja is None or len(kesken) < wip_raja):
            tyo = jono.pop(0)                        # veto: aloita vanhin
            tyo.aloitettu = nyt
            kesken.append(tyo)
            aloitettuja += 1
        if kesken:
            osuus = kapasiteetti(len(kesken)) * ASKEL / len(kesken)
            for tyo in kesken:
                tyo.jaljella -= osuus
            for tyo in [t for t in kesken if t.jaljella <= 0]:
                tyo.valmis = nyt + ASKEL
                kesken.remove(tyo)
                tulos.valmiit.append(tyo)
        if askel % int(1 / ASKEL) == 0:
            tulos.kertymat.append((saapuneita, aloitettuja,
                                   len(tulos.valmiit)))
    return tulos
# @loppu simulointi


if __name__ == "__main__":
    # Tarkistus: yksi työ kerrallaan ei kärsi vaihdoista.
    for n in (1, 4, 8, 16):
        print(f"{n:2d} keskeneräistä: teho {kapasiteetti(n):.2f} htp/pv")
