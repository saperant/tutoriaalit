"""Asteittainen käyttöönotto lipulla: 1 %, 10 %, 50 %, 100 %.

Käyttäjät jaetaan lokeroihin tiivisteellä. Tarkistetaan, että jako on
tasainen, pysyvä ja riippumaton muista lipuista, ja että hätäkatkaisu
sulkee ominaisuuden kaikilta.
"""

from dataclasses import replace
from datetime import date

from toimitus.liput import Lippu, paalla

KAYTTAJAT = [f"kayttaja-{nro}" for nro in range(10_000)]
lippu = Lippu("uusi-kassa", "maksutiimi", date(2026, 3, 2),
              sallitut=frozenset({"testaaja-1", "testaaja-2"}))

# @alku portaat
edelliset: set[str] = set()
print(f"{'osuus':>6}{'päällä':>8}{'pysyivät':>10}")
for osuus in (0, 1, 10, 50, 100):
    porras = replace(lippu, osuus=osuus)
    mukana = {k for k in KAYTTAJAT if paalla(porras, k)}
    pysyi = "kyllä" if edelliset <= mukana else "EI"
    print(f"{osuus:>5}%{len(mukana):>8}{pysyi:>10}")
    edelliset = mukana
# @loppu portaat

print("testaaja-1, osuus 0 %:",
      "päällä" if paalla(lippu, "testaaja-1") else "pois")

# Kaksi lippua 50 %:ssa: jos jako olisi sama, samat käyttäjät saisivat
# aina molemmat uutuudet ja toiset eivät kumpaakaan.
toinen = Lippu("uusi-haku", "hakutiimi", date(2026, 3, 9), osuus=50)
puolet = replace(lippu, osuus=50)
molemmat = sum(paalla(puolet, k) and paalla(toinen, k) for k in KAYTTAJAT)
print(f"kaksi lippua 50 %:ssa, molemmat päällä: "
      f"{molemmat / len(KAYTTAJAT):.0%} käyttäjistä")

katkaistu = replace(lippu, osuus=100, hatakatkaisu=True)
print("hätäkatkaisun jälkeen päällä:",
      sum(paalla(katkaistu, k) for k in KAYTTAJAT + ["testaaja-1"]))
