"""Haavoittuvuusilmoituksen käsittely valmistajan puolella: mitkä
julkaisulinjat korjataan, mihin mennessä ja mitä kustakin tiedotetaan."""

from dataclasses import dataclass
from datetime import date, timedelta

Versio = tuple[int, int, int]


# @alku tiedot
# Korjausaika vakavuuden mukaan päivinä ilmoituksen vastaanotosta.
# Tiimi päättää ajat itse ja julkaisee ne (SECURITY.md).
KORJAUSAIKA = {"kriittinen": 7, "korkea": 30, "keskitaso": 90}


@dataclass(frozen=True)
class Linja:
    """Ylläpidetty julkaisulinja ja sen uusin julkaisu."""
    uusin: Versio
    tuki_paattyy: date


@dataclass(frozen=True)
class Ilmoitus:
    tunniste: str
    vastaanotettu: date
    vakavuus: str
    alkaen: Versio          # ensimmäinen haavoittuva versio


LINJAT = [
    Linja((1, 8, 12), date(2027, 6, 30)),     # pitkän tuen linja
    Linja((2, 4, 7), date(2026, 6, 30)),
    Linja((2, 6, 1), date(2028, 6, 30)),
    Linja((3, 0, 2), date(2029, 6, 30)),
]
ILMOITUS = Ilmoitus("ESIM-2026-0007", date(2026, 11, 2), "korkea",
                    alkaen=(2, 0, 0))
# @loppu tiedot


def teksti(v: Versio) -> str:
    return ".".join(map(str, v))


# @alku suunnitelma
def suunnitelma(i: Ilmoitus, linjat: list[Linja], tanaan: date) -> list[str]:
    maaraaika = i.vastaanotettu + timedelta(days=KORJAUSAIKA[i.vakavuus])
    rivit = []
    for linja in linjat:
        nimi = f"{linja.uusin[0]}.{linja.uusin[1]}"
        if linja.uusin < i.alkaen:
            # Haavoittuva koodi tuli vasta myöhempään versioon.
            rivit.append(f"{nimi}: ei koske (VEX: not_affected, "
                         "haavoittuvaa koodia ei ole)")
        elif linja.tuki_paattyy < tanaan:
            rivit.append(f"{nimi}: tuki päättynyt, tiedotteessa "
                         "kehotus päivittää")
        else:
            korjattu = (*linja.uusin[:2], linja.uusin[2] + 1)
            rivit.append(f"{nimi}: korjaus versioon {teksti(korjattu)} "
                         f"viimeistään {maaraaika.isoformat()}")
    return rivit
# @loppu suunnitelma


if __name__ == "__main__":
    print(f"{ILMOITUS.tunniste} ({ILMOITUS.vakavuus}), "
          f"haavoittuva versiosta {teksti(ILMOITUS.alkaen)} alkaen")
    for rivi in suunnitelma(ILMOITUS, LINJAT, tanaan=date(2026, 11, 3)):
        print(" ", rivi)
