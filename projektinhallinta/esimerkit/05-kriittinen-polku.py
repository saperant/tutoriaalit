"""Kriittinen polku (CPM) ja miksi rinnakkaiset polut myöhästyttävät.

Tehtäväverkko käydään läpi topologisessa järjestyksessä eteenpäin
(aikaisin alku) ja taaksepäin (myöhäisin loppu). Pelivara on niiden
erotus, ja kriittisellä polulla pelivaraa ei ole.
"""

import random

# nimi: (kesto päivinä, edeltäjät). Järjestys on topologinen.
VERKKO: dict[str, tuple[float, tuple[str, ...]]] = {
    "määrittely": (5, ()),
    "tietokanta": (9, ("määrittely",)),
    "rajapinta": (10, ("määrittely",)),
    "käyttöliittymä": (15, ("määrittely",)),
    "integraatio": (6, ("tietokanta", "rajapinta")),
    "testaus": (5, ("integraatio", "käyttöliittymä")),
    "käyttöönotto": (3, ("testaus",)),
}


# @alku cpm
def cpm(kestot: dict[str, float]) -> tuple[float, dict[str, float]]:
    """Palauttaa projektin keston ja jokaisen tehtävän pelivaran."""
    loppu: dict[str, float] = {}
    for nimi, (_, edeltajat) in VERKKO.items():           # eteenpäin
        alku = max((loppu[e] for e in edeltajat), default=0.0)
        loppu[nimi] = alku + kestot[nimi]
    kesto = max(loppu.values())
    myohaisin = {nimi: kesto for nimi in VERKKO}
    for nimi in reversed(VERKKO):                         # taaksepäin
        for e in VERKKO[nimi][1]:
            myohaisin[e] = min(myohaisin[e], myohaisin[nimi] - kestot[nimi])
    return kesto, {n: myohaisin[n] - loppu[n] for n in VERKKO}
# @loppu cpm


arviot = {nimi: kesto for nimi, (kesto, _) in VERKKO.items()}
kesto, pelivarat = cpm(arviot)
print(f"projektin kesto {kesto:.0f} pv")
for nimi, vara in pelivarat.items():
    merkki = "kriittinen" if vara == 0 else f"pelivara {vara:.0f} pv"
    print(f"  {nimi:<15} {arviot[nimi]:3.0f} pv  {merkki}")

# @alku epavarmuus
# Jokainen kesto vaihtelee välillä 0,8-1,6 kertaa arvio (kolmiojakauma).
rng = random.Random(9)
TOISTOJA = 20_000
summa = 0.0
kriittisena = dict.fromkeys(VERKKO, 0)
for _ in range(TOISTOJA):
    toteuma = {n: rng.triangular(0.8 * k, 1.6 * k, k)
               for n, k in arviot.items()}
    kesto_nyt, varat = cpm(toteuma)
    summa += kesto_nyt
    for nimi, vara in varat.items():
        kriittisena[nimi] += vara < 1e-9
# @loppu epavarmuus

keskikerroin = (0.8 + 1.0 + 1.6) / 3
print("kriittinen polku keskimääräisin kestoin "
      f"{kesto * keskikerroin:.1f} pv")
print(f"simuloitu keskimääräinen kesto          {summa / TOISTOJA:.1f} pv")
print("kriittisellä polulla osuus toistoista:")
for nimi, n in kriittisena.items():
    print(f"  {nimi:<15} {n / TOISTOJA:5.0%}")
