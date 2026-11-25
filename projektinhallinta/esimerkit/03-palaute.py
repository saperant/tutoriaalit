"""Palautesilmukan pituus: erän koon U-käyrä.

40 ominaisuutta tehdään erissä, ja asiakas näkee tuloksen vasta erän
lopussa. Osa ominaisuuksista on ymmärretty väärin, ja korjaus on sitä
kalliimpi, mitä enemmän väärän oletuksen päälle on ehditty rakentaa.
"""

import random

OMINAISUUKSIA = 40
TYO = 5.0             # päivää ominaisuutta kohden
P_VAARIN = 0.25       # osuus, joka on ymmärretty väärin
KORJAUS = 2.0         # päivää, jos virhe huomataan heti
SEURANNAINEN = 0.5    # lisäpäivää jokaisesta päälle rakennetusta


# @alku malli
def uudelleentyo(era: int) -> float:
    """Uudelleentyön odotusarvo päivinä, kun palaute saadaan erän lopussa."""
    yhdelle_eralle = sum(
        P_VAARIN * (KORJAUS + SEURANNAINEN * (era - 1 - paikka))
        for paikka in range(era))
    return yhdelle_eralle * OMINAISUUKSIA / era


def kokonaistyo(era: int, kierroksen_hinta: float) -> float:
    kierroksia = OMINAISUUKSIA / era
    return (OMINAISUUKSIA * TYO + uudelleentyo(era)
            + kierroksia * kierroksen_hinta)
# @loppu malli


# @alku simulointi
def simuloi(era: int, rng: random.Random) -> float:
    """Yksi toteuma: arvotaan, mitkä ominaisuudet menivät väärin."""
    paivat = 0.0
    for paikka in range(OMINAISUUKSIA):
        if rng.random() < P_VAARIN:
            paalla = era - 1 - paikka % era
            paivat += KORJAUS + SEURANNAINEN * paalla
    return paivat
# @loppu simulointi


rng = random.Random(3)
print("erä  kierr.  uudelleentyö  palaute 2 pv  palaute 0,5 pv")
for era in (1, 2, 4, 5, 8, 10, 20, 40):
    simuloitu = sum(simuloi(era, rng) for _ in range(4000)) / 4000
    assert abs(simuloitu - uudelleentyo(era)) < 0.03 * uudelleentyo(era) + 1
    print(f"{era:3d}  {OMINAISUUKSIA // era:5d}  {uudelleentyo(era):9.1f} pv"
          f"  {kokonaistyo(era, 2.0):9.1f} pv"
          f"  {kokonaistyo(era, 0.5):10.1f} pv")

ERAT = (1, 2, 4, 5, 8, 10, 20, 40)
for hinta in (2.0, 0.5):
    tyot = {era: kokonaistyo(era, hinta) for era in ERAT}
    paras = min(tyot, key=tyot.__getitem__)
    print(f"palautekierros {hinta:3.1f} pv: paras erä {paras}")
