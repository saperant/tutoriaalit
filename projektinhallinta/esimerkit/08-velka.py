"""Teknisen velan korkomalli: oikotie nopeuttaa nyt ja hidastaa myöhemmin.

Tiimin kapasiteetti on 100 yksikköä sprintissä. Oikotiellä ominaisuuksia
syntyy 30 % nopeammin, mutta jokainen oikotiellä tehty yksikkö kasvattaa
velkaa. Velka maksaa korkoa: osa jokaisen sprintin kapasiteetista kuluu
sen kiertämiseen. Maksamaton velka myös kasvaa, koska sen päälle
rakennetaan uutta.
"""

from collections.abc import Callable
from dataclasses import dataclass

KAPASITEETTI = 100.0
OIKOTIEN_NOPEUS = 1.3      # ominaisuuksia kapasiteettiyksikköä kohden
VELKAA_YKSIKOSTA = 0.6     # velan kasvu oikotiellä tehdystä yksiköstä
KORKO = 0.04               # osuus velasta, joka kuluu sprintissä
KASVU = 0.03               # maksamattoman velan kasvu sprintissä
LYHENNYS = 0.5             # lyhennykseen käytetty osuus kapasiteetista


@dataclass(frozen=True)
class Paatos:
    oikotie: bool
    lyhenna: bool


Strategia = Callable[[int, float], Paatos]   # (sprintti, velka) -> päätös


# @alku malli
def aja(strategia: Strategia, sprintteja: int = 40
        ) -> tuple[list[float], float]:
    """Kertyneet ominaisuudet sprinteittäin ja velka lopussa."""
    velka = valmista = 0.0
    kertyma = []
    for sprintti in range(1, sprintteja + 1):
        paatos = strategia(sprintti, velka)
        kaytossa = max(0.0, KAPASITEETTI - KORKO * velka)   # korko ensin
        if paatos.lyhenna:
            lyhennys = min(velka, LYHENNYS * kaytossa)
            velka -= lyhennys
            kaytossa -= lyhennys
        if paatos.oikotie:
            valmista += OIKOTIEN_NOPEUS * kaytossa
            velka += VELKAA_YKSIKOSTA * kaytossa
        else:
            valmista += kaytossa
        velka *= 1 + KASVU
        kertyma.append(valmista)
    return kertyma, velka
# @loppu malli


# @alku strategiat
STRATEGIAT: dict[str, Strategia] = {
    "ei oikoteitä": lambda s, velka: Paatos(False, False),
    "aina oikotie": lambda s, velka: Paatos(True, False),
    "oikotie 8 sprinttiä, ei lyhennystä":
        lambda s, velka: Paatos(s <= 8, False),
    "oikotie 8 sprinttiä, sitten lyhennys":
        lambda s, velka: Paatos(s <= 8, s > 8),
}
# @loppu strategiat

RAJAT = (8, 16, 24, 40)
print(f"{'strategia':<38}" + "".join(f"{f'spr. {r}':>8}" for r in RAJAT)
      + "   velka")
perus, _ = aja(STRATEGIAT["ei oikoteitä"])
for nimi, strategia in STRATEGIAT.items():
    kertyma, velka = aja(strategia)
    print(f"{nimi:<38}" + "".join(f"{kertyma[r - 1]:>8.0f}" for r in RAJAT)
          + f"{velka:>8.0f}")
    takana = next((s for s in range(1, 41) if kertyma[s - 1] < perus[s - 1]),
                  None)
    if takana:
        print(f"{'':<4}jää jälkeen velattomasta sprintissä {takana}")
