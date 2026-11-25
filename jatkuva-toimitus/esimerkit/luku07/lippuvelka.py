"""Lippurekisteri: mitkä liput pitäisi jo poistaa?

Jokaisella lipulla on omistaja ja luontipäivä. Lippu, joka on ollut
kokonaan päällä tai pois yli kuukauden, on velkaa: koodissa on haara,
jota ei enää valita.
"""

from datetime import date

from toimitus.liput import Lippu, poistettavat

TANAAN = date(2026, 6, 1)
REKISTERI = [
    Lippu("uusi-kassa", "maksutiimi", date(2026, 3, 2), osuus=100),
    Lippu("uusi-haku", "hakutiimi", date(2026, 5, 18), osuus=25),
    Lippu("tumma-teema", "kayttoliittyma", date(2025, 11, 3), osuus=100),
    Lippu("vanha-vienti", "raportit", date(2025, 9, 1), osuus=0),
    Lippu("raskas-raportti", "raportit", date(2026, 1, 12), osuus=100,
          pysyva=True),        # kuormansäätö: saa jäädä
    Lippu("kevatkampanja", "markkinointi", date(2026, 5, 25), osuus=100),
]

velka = poistettavat(REKISTERI, TANAAN)
print(f"lippuja {len(REKISTERI)}, poistettavia {len(velka)}")
for lippu in velka:
    ika = (TANAAN - lippu.luotu).days
    tila = "päällä kaikilla" if lippu.osuus == 100 else "pois kaikilta"
    print(f"  {lippu.nimi:<16}{tila:<17}{ika:>4} pv  {lippu.omistaja}")

# Jokainen lippu kaksinkertaistaa mahdolliset yhdistelmät.
print(f"lippuyhdistelmiä nyt {2 ** len(REKISTERI)}, "
      f"siivouksen jälkeen {2 ** (len(REKISTERI) - len(velka))}")
