"""Projektin aikataulu standardikirjaston datetime-modulilla."""

import math
from datetime import date, timedelta

VIIKONPAIVAT = ["ma", "ti", "ke", "to", "pe", "la", "su"]


def lisaa_tyopaivia(alku: date, tyopaivia: int) -> date:
    """Palauttaa päivän, joka on annetun määrän arkipäiviä alun
    jälkeen. Viikonloput ohitetaan, pyhäpäiviä ei huomioida."""
    paiva = alku
    while tyopaivia > 0:
        paiva += timedelta(days=1)
        if paiva.weekday() < 5:          # 0 = maanantai, 6 = sunnuntai
            tyopaivia -= 1
    return paiva


aloitus = date(2026, 3, 2)
tehtavat = [("Määrittely", 3), ("Toteutus", 8), ("Testaus", 4)]
paiva = aloitus
for nimi, kesto in tehtavat:
    paiva = lisaa_tyopaivia(paiva, kesto)
    viikonpaiva = VIIKONPAIVAT[paiva.weekday()]
    print(f"{nimi:<12}{kesto:>3} pv  valmis {viikonpaiva} "
          f"{paiva:%d.%m.%Y}")

kalenteripaivia = (paiva - aloitus).days
print(f"Kesto {kalenteripaivia} kalenteripäivää eli "
      f"{math.ceil(kalenteripaivia / 7)} viikkoa (pyöristys ylös)")
print(date.fromisoformat("2026-03-02") == aloitus)
